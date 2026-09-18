#!/usr/bin/env python3
"""Where in the pipeline does retrieval actually break? One rung at a time.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The chain from text to bit has five operations.  Rather than guess which one
costs, this scores retrieval at EVERY rung with the same metric, so the loss
can be attributed step by step:

  S1_Z        raw TF-IDF features, ~10^5 columns          sparse cosine
  S2_svd      after TruncatedSVD(96), before normalising  cosine
  S3_norm     after row normalisation                     cosine
  S4_center   after subtracting the archive mean          cosine  (= float arm)
  S5_sign_fq  sign of S4, scored against an EXACT query   cosine on +-1
  S6_sign     sign of S4, query also binarised            Hamming (= sym arm)

One prediction is worth stating before the numbers, because it is a check on
the harness rather than a finding: cosine is invariant to positive row
scaling, so S3 must equal S2 EXACTLY.  Normalisation cannot change cosine
ranking by itself.  If S3 differs from S2 the code is wrong.  What
normalisation actually does is change what the MEAN is, and therefore change
S4 -- its effect is real but it acts one rung later.

Rebuilt from raw text with the production seeds (LSA32 5101, SVD96 5204), so
S6 should land on the frozen `sym` value.
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
import run_bottleneck as BN  # noqa: E402

SVD_SEED = 5204
KS = (1, 3, 10)
RUNGS = ["S1_Z", "S2_svd", "S3_norm", "S4_center", "S5_sign_fq", "S6_sign"]


def cos_dense(M, q):
    qn = float(np.linalg.norm(q))
    if qn == 0 or not np.isfinite(qn):
        return np.full(M.shape[0], -np.inf)
    d = np.linalg.norm(M, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (M @ q) / (d * qn)
    return np.nan_to_num(s, nan=-np.inf, posinf=-np.inf, neginf=-np.inf)


def cos_sparse(Z, zq):
    s = np.asarray((Z @ zq.T).todense()).ravel()
    dn = np.sqrt(np.asarray(Z.multiply(Z).sum(axis=1)).ravel())
    qn = float(np.sqrt(zq.multiply(zq).sum()))
    with np.errstate(divide="ignore", invalid="ignore"):
        s = s / (dn * qn)
    return np.nan_to_num(s, nan=-np.inf, posinf=-np.inf, neginf=-np.inf)


def main():
    n_items = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    files = sorted(glob.glob(BN.ITEMS))
    assert len(files) == 470, len(files)
    if n_items < len(files):
        files = sorted(random.Random(20260916).sample(files, n_items))
    adapter = BN.load_adapter()
    acc = {(r, k): [] for r in RUNGS for k in KS}
    s2_vs_s3 = 0.0
    t0 = time.perf_counter()

    for i, f in enumerate(files):
        item = json.loads(open(f, encoding="utf-8").read())
        memories, gold_ids, issues = adapter.build_archive(item)
        if issues:
            continue
        texts = adapter.fit_input_payload(memories)
        id_to_row = {m["memory_id"]: j for j, m in enumerate(memories)}
        g = np.asarray([id_to_row[x] for x in gold_ids], dtype=int)
        if len(g) == 0:
            continue
        wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(texts)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        q = str(item["question"])
        Qw = normalize(wv.transform([q]))
        Qc = normalize(cv.transform([q]))
        Ql = normalize(base_svd.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")

        sv = TruncatedSVD(n_components=96, random_state=SVD_SEED)
        Y0 = sv.fit_transform(Z)                 # S2
        Q0 = sv.transform(Zq).reshape(-1)
        Y = normalize(Y0)                        # S3
        Qn = Q0 / max(np.linalg.norm(Q0), 1e-12)
        mu = Y.mean(axis=0, keepdims=True)
        C = Y - mu                               # S4
        Qc4 = Qn - mu.reshape(-1)
        R = np.where(C >= 0, 1.0, -1.0)          # S5 / S6

        scores = {
            "S1_Z": cos_sparse(Z, Zq),
            "S2_svd": cos_dense(Y0, Q0),
            "S3_norm": cos_dense(Y, Qn),
            "S4_center": cos_dense(C, Qc4),
            "S5_sign_fq": cos_dense(R, Qc4),
            "S6_sign": (-np.count_nonzero(
                (C >= 0) != (Qc4 >= 0)[None, :], axis=1)).astype(np.float64),
        }
        s2_vs_s3 = max(s2_vs_s3,
                       float(np.abs(scores["S2_svd"] - scores["S3_norm"]).max()))
        for r in RUNGS:
            for k in KS:
                acc[(r, k)].append(H.hit_at_k(scores[r], g, k))
        if (i + 1) % 20 == 0:
            el = time.perf_counter() - t0
            print(f"  {i+1}/{len(files)}  {el:.0f}s", flush=True)

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": "lme", "n_archives": len(acc[("S6_sign", 10)]),
           "seeds": {"LSA32": 5101, "SVD96": SVD_SEED},
           "harness_check_S2_equals_S3": {
               "max_abs_score_difference": s2_vs_s3,
               "why": "cosine is invariant to positive row scaling"},
           "hit_percent": {f"{r}_hit{k}": float(np.mean(acc[(r, k)]) * 100)
                           for r in RUNGS for k in KS},
           "per_query_hit10": {r: [float(x) for x in acc[(r, 10)]]
                               for r in RUNGS}}
    with open(os.path.join(HERE, "LADDER.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    hp = out["hit_percent"]
    print(f"\n=== merdiven, {out['n_archives']} LongMemEval arsivi ===")
    print(f"  S2 == S3 kontrolu: en buyuk fark {s2_vs_s3:.3e}")
    print(f"\n  {'asama':>12s}{'hit@1':>8s}{'hit@3':>8s}{'hit@10':>8s}"
          f"{'bir onceki adimdan fark':>26s}")
    prev = None
    for r in RUNGS:
        v = hp[f"{r}_hit10"]
        d = "" if prev is None else f"{v - prev:+.2f}"
        print(f"  {r:>12s}{hp[f'{r}_hit1']:8.2f}{hp[f'{r}_hit3']:8.2f}"
              f"{v:8.2f}{d:>26s}")
        prev = v
    print("\nwrote LADDER.json")


if __name__ == "__main__":
    main()
