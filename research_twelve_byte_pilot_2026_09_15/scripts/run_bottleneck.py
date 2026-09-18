#!/usr/bin/env python3
"""Where does the loss live: the SVD96 projection, or the features themselves?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Rebuilds the canonical LongMemEval representation from raw items with the
frozen adapter (`fit_archive_representation`, identical vectorizer settings),
then scores gold Hit@k in four spaces:

  Z        full sparse feature space, NO projection  (~10^5 columns)
  svd384   normalize(TruncatedSVD(384)(Z)), centered
  svd192   normalize(TruncatedSVD(192)(Z)), centered
  svd96    normalize(TruncatedSVD(96)(Z)),  centered  <- the production space

svd96 must reproduce the cached `float` arm; that is the fidelity check.
If Z >> svd96 the projection is the bottleneck and a wider code can pay.
If Z ~= svd96 the features/retrieval unit are the bottleneck and no number
of bits or dimensions helps.

Usage: python run_bottleneck.py [n_items] [seed]
"""
import glob
import json
import os
import random
import sys
import time

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

SRC = H.SRC
ITEMS = os.path.join(SRC, "regen", "lme", "items", "*.json")
ADAPTER = os.path.join(SRC, "github-publish-static", "adapters",
                       "longmemeval_v52_adapter.py")
SVD_RANDOM_STATE = 5101          # as in v52_t4c2_centering_geometry.py

# !!! SEED DEFECT (found 2026-09-15, after this script's results were
# published): the producer uses random_state=5101 for the LSA32 stage and
# 5204 for the FINAL SVD96 (v52_t4f1_beam_retrieval.py:51-54,
# v52_t4c2_centering_geometry.py:37).  This script used 5101 for the final
# SVD96, so it did NOT build the production representation.  audit_seed.py
# shows 5204 reproduces the frozen cache bit-exactly (12/12 archives) while
# 5101 differs on 21.71 % of bits.  The seed is left as-is so the committed
# results still match the code that produced them; re-run under 5204 before
# citing anything here.
WIDTHS = (384, 192, 96)
KS = (1, 3, 5, 10, 20, 50, 100)
ARMS = ["Z"] + [f"svd{w}" for w in WIDTHS]


def load_adapter():
    import importlib.util
    spec = importlib.util.spec_from_file_location("lme_adapter", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def centered_cosine(Y, QY):
    mu = Y.mean(axis=0, keepdims=True)
    C = Y - mu
    q = (QY - mu).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = np.linalg.norm(q)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (dn * qn)


def sparse_cosine(Z, Zq):
    s = np.asarray((Z @ Zq.T).todense()).ravel()
    dn = np.sqrt(np.asarray(Z.multiply(Z).sum(axis=1)).ravel())
    qn = float(np.sqrt(Zq.multiply(Zq).sum()))
    with np.errstate(divide="ignore", invalid="ignore"):
        return s / (dn * qn)


def one_item(adapter, path):
    item = json.loads(open(path, encoding="utf-8").read())
    memories, gold_ids, issues = adapter.build_archive(item)
    if issues:
        raise RuntimeError(f"archive issues {issues[:2]}")
    texts = adapter.fit_input_payload(memories)
    id_to_row = {m["memory_id"]: i for i, m in enumerate(memories)}
    gold = np.asarray([id_to_row[g] for g in gold_ids], dtype=int)
    assert len(gold) > 0
    wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    q = str(item["question"])
    Qw = normalize(wv.transform([q]))
    Qc = normalize(cv.transform([q]))
    Ql = normalize(base_svd.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    out = {"Z": sparse_cosine(Z, Zq)}
    n = Z.shape[0]
    for w in WIDTHS:
        if w >= min(n, Z.shape[1]):
            out[f"svd{w}"] = None
            continue
        sv = TruncatedSVD(n_components=w, random_state=SVD_RANDOM_STATE)
        Y = normalize(sv.fit_transform(Z))
        QY = normalize(sv.transform(Zq))
        out[f"svd{w}"] = centered_cosine(Y, QY)
    return out, gold, n


def main():
    n_items = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260915
    shard = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nshard = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    files = sorted(glob.glob(ITEMS))
    assert len(files) == 470, len(files)
    if n_items and n_items < len(files):
        files = sorted(random.Random(seed).sample(files, n_items))
    if nshard > 1:
        files = files[shard::nshard]
    adapter = load_adapter()
    facts = {a: [] for a in ARMS}
    pools, skipped, t0 = [], [], time.perf_counter()
    for i, f in enumerate(files):
        try:
            sc, gold, n = one_item(adapter, f)
        except Exception as e:  # noqa: BLE001 keep failures visible
            skipped.append({"file": os.path.basename(f), "error": repr(e)})
            continue
        pools.append(n)
        for a in ARMS:
            if sc.get(a) is None:
                facts[a].append(None)
            else:
                f_a = _facts(sc[a], gold)
                # fidelity: the curve must agree with the independent
                # hit_at_k implementation at k=10
                assert abs(_hit(f_a, 10)
                           - H.hit_at_k(sc[a], gold, 10)) < 1e-12
                facts[a].append(f_a)
        if (i + 1) % 25 == 0:
            el = time.perf_counter() - t0
            print(f"  {i + 1}/{len(files)}  {el:.0f}s  "
                  f"({el / (i + 1):.2f}s/item)", flush=True)
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": "lme", "n_items_requested": len(files),
           "n_items_scored": len(pools), "seed": seed,
           "pool_mean": float(np.mean(pools)) if pools else None,
           "skipped": skipped, "arms": ARMS,
           "fidelity_note": "svd96 must track the cached float arm "
                            "(hit@10 = 82.55% on the full 470)",
           "hit_percent": {}, "k_needed": {}}
    for a in ARMS:
        ff = [x for x in facts[a] if x is not None]
        res["hit_percent"][a] = {
            str(k): float(np.mean([_hit(f, k) for f in ff]) * 100.0)
            for k in KS}
        res["k_needed"][a] = {}
        for t in (0.90, 0.95):
            kk = None
            for k in range(1, int(max(pools)) + 1):
                if np.mean([_hit(f, k) for f in ff]) >= t:
                    kk = k
                    break
            res["k_needed"][a][str(t)] = kk
    res["elapsed_seconds"] = time.perf_counter() - t0
    res["pools"] = [int(p) for p in pools]
    res["facts"] = {a: [list(x) if x is not None else None for x in facts[a]]
                    for a in ARMS}
    out_name = ("BOTTLENECK.json" if nshard == 1
                else f"BOTTLENECK_shard{shard}of{nshard}.json")
    with open(out_name, "w") as fh:
        json.dump(res, fh, indent=2)
    for a in ARMS:
        print(f"{a:8s} hit@10={res['hit_percent'][a]['10']:6.2f}  "
              f"K@90%={res['k_needed'][a]['0.9']}  "
              f"K@95%={res['k_needed'][a]['0.95']}", flush=True)
    print("wrote BOTTLENECK.json", flush=True)


def _facts(scores, gold):
    import run_ksweep as KS_
    return KS_.bucket_facts(scores, gold)


def _hit(f, k):
    import run_ksweep as KS_
    return KS_.hit_from_facts(*f, k)


if __name__ == "__main__":
    main()
