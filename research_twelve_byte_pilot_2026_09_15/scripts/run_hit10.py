#!/usr/bin/env python3
"""Re-read of the frozen r1 score matrices under a top-10 candidate metric.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

No new representation, no new fit rule, no new arm.  Encoding, state fitting
and all six scoring functions are imported unchanged from the frozen
`lib_b8.py`; only the metric applied to the resulting score vector is new.

Metrics per query, all under the SAME uniform-random-within-tie convention
that `lib_b8.exact_frac` already uses:

  hit@k    expected P(at least one gold document lands in the top k)
  frac@k   expected (#gold in top k) / (#gold)   == exact_frac generalised

Self-check: `frac_at_k(.., k=3)` must reproduce `lib_b8.exact_frac` exactly
(K=3 there) on every query.  Any mismatch aborts the run.
"""
import glob
import json
import math
import os
import pickle
import sys
import time
from collections import defaultdict

import numpy as np

SRC = r"C:\Users\MDP\dev\llmzip-work"
B8DIR = os.path.join(SRC, "parallel_ideas_r1", "b8")
sys.path.insert(0, B8DIR)
import lib_b8 as B  # noqa: E402

ARCH_PKL = os.path.join(SRC, "bench3", "runs", "b3b_perltqa",
                        "cache_arch_eval.pkl")
Q_PKL = os.path.join(SRC, "bench3", "runs", "b3b_perltqa", "cache_q_eval.pkl")
LME_GLOB = os.path.join(SRC, "regen", "lme", "cache_repr", "*.pkl")
RT_GLOB = os.path.join(SRC, "bench3", "runs", "b3a_realtalk", "rt_repr",
                       "RT*.pkl")
EXCL_RT = os.path.join(SRC, "theory_benchmark_test_v1", "realtalk",
                       "excluded_ids.json")

ARMS = ["sym", "asym", "b8", "sign88", "float", "float_std"]
KS = (1, 3, 5, 10, 20)
BOOT_SEED = 20260915
BOOT_B = 2000


def _levels(scores):
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    return s, np.unique(s)[::-1]


def frac_at_k(scores, gold, k):
    """Expected (#gold in top k)/(#gold); mirrors exact_frac with free k."""
    s, levels = _levels(scores)
    g = np.asarray(gold).ravel().astype(int)
    m = int(len(g))
    assert m > 0
    gset = set(int(x) for x in g)
    better = 0
    exp = 0.0
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        bsz = len(idx)
        if bsz == 0:
            continue
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + bsz <= k:
            exp += gb
        else:
            exp += (k - better) * gb / bsz
            break
        better += bsz
    return exp / m


def hit_at_k(scores, gold, k):
    """Expected P(>=1 gold in top k) under uniform within-tie shuffling."""
    s, levels = _levels(scores)
    gset = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    assert len(gset) > 0
    better = 0
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        bsz = len(idx)
        if bsz == 0:
            continue
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + bsz <= k:
            if gb > 0:
                return 1.0
            better += bsz
        else:
            take = k - better
            if gb == 0:
                return 0.0
            if take > bsz - gb:
                return 1.0
            p_none = math.comb(bsz - gb, take) / math.comb(bsz, take)
            return 1.0 - p_none
    return 0.0


def arm_scores(C, st, payload_b8, payload_s96, S96, q):
    """The six frozen arms, identical call sites to b8/run.py score_archive."""
    sc_sym = (-np.count_nonzero(
        np.unpackbits(payload_s96, axis=1, bitorder="big")[:, :96].astype(bool)
        != (q >= 0)[None, :], axis=1)).astype(np.float64)
    return {
        "sym": sc_sym,
        "asym": B.cosine_from_code(S96, q),
        "b8": B.b8_scores(payload_b8, st, q),
        "sign88": B.sign88_scores(payload_b8, st, q),
        "float": B.float_raw_scores(C, q),
        "float_std": B.float_std_scores(C, q, st["std"]),
    }


def score_archive(C, queries, golds):
    C = np.asarray(C, dtype=np.float64)
    n = C.shape[0]
    st = B.fit_archive(C)
    payload_b8 = B.encode_docs(C, st)
    payload_s96 = np.packbits((C >= 0), axis=1,
                              bitorder="big").astype(np.uint8)
    assert payload_b8.shape == (n, 12) and payload_s96.shape == (n, 12)
    s96 = np.where(np.unpackbits(payload_s96, axis=1,
                                 bitorder="big")[:, :96].astype(bool),
                   1.0, -1.0)
    rows = []
    for j, qv in enumerate(queries):
        q = np.asarray(qv, dtype=np.float64).reshape(-1)
        g = np.asarray(golds[j]).ravel().astype(int)
        sc = arm_scores(C, st, payload_b8, payload_s96, s96, q)
        row = {"gold_size": int(len(g)), "N": int(n)}
        for a in ARMS:
            # frozen-metric self-check: k=3 must equal lib_b8.exact_frac
            ref = B.exact_frac(sc[a], g, True)
            mine = frac_at_k(sc[a], g, 3)
            if abs(ref - mine) > 1e-12:
                raise AssertionError(
                    f"frac_at_k(k=3) != exact_frac for arm {a}: "
                    f"{mine!r} vs {ref!r}")
            for k in KS:
                row[f"hit{k}_{a}"] = hit_at_k(sc[a], g, k)
                row[f"frac{k}_{a}"] = frac_at_k(sc[a], g, k)
        rows.append(row)
    return rows


def bootstrap_ci(contrast, cluster, seed=BOOT_SEED, bb=BOOT_B):
    contrast = np.asarray(contrast, float)
    cluster = np.asarray(cluster)
    rng = np.random.default_rng(seed)
    by_cl = {c: contrast[cluster == c] for c in np.unique(cluster)}
    cs = list(by_cl)
    reps = np.empty(bb)
    for i in range(bb):
        samp = [by_cl[c] for c in rng.choice(cs, size=len(cs), replace=True)]
        reps[i] = float(np.concatenate(samp).mean())
    return {"point_pp": float(contrast.mean()) * 100.0,
            "ci95_pp": [float(np.percentile(reps, 2.5)) * 100.0,
                        float(np.percentile(reps, 97.5)) * 100.0],
            "n": int(len(contrast)), "n_clusters": int(len(cs))}


def run_perltqa():
    arch = pickle.load(open(ARCH_PKL, "rb"))
    q_all = pickle.load(open(Q_PKL, "rb"))
    by_char = defaultdict(list)
    for qid, q in q_all.items():
        by_char[q["char"]].append(qid)
    chars = sorted(by_char)
    assert len(chars) == 30 and len(q_all) == 8265, (len(chars), len(q_all))
    rows, cluster = [], []
    for ai, char in enumerate(chars):
        ql = sorted(by_char[char])
        c = np.asarray(arch[char]["C"], dtype=np.float64)
        qc = [np.asarray(q_all[q]["qC"], dtype=np.float64) for q in ql]
        gl = [np.asarray(q_all[q]["gold"]).ravel().astype(int) for q in ql]
        rr = score_archive(c, qc, gl)
        rows.extend(rr)
        cluster.extend([char] * len(rr))
        print(f"  perltqa {ai + 1}/30 {char} n={len(ql)}", flush=True)
    return rows, cluster


def run_lme():
    files = sorted(glob.glob(LME_GLOB))
    assert len(files) == 470, len(files)
    rows, cluster = [], []
    for i, f in enumerate(files):
        d = pickle.loads(open(f, "rb").read())
        c = np.asarray(d["C"], float)
        q = np.asarray(d["qC"], float).reshape(-1)
        g = np.asarray(d["gold"]).ravel().astype(int)
        rr = score_archive(c, [q], [g])
        rows.extend(rr)
        cluster.extend([d["question_id"]] * len(rr))
        if (i + 1) % 100 == 0:
            print(f"  lme {i + 1}/470", flush=True)
    return rows, cluster


def run_realtalk():
    files = sorted(glob.glob(RT_GLOB))
    assert len(files) == 10, len(files)
    excluded = set(json.load(open(EXCL_RT))["excluded_ids"])
    rows, cluster = [], []
    for f in files:
        o = pickle.loads(open(f, "rb").read())
        c = np.asarray(o["C"], float)
        qc_all = np.asarray(o["QC"], float)
        qs, gs = [], []
        for qi, qid in enumerate(o["qids"]):
            gold = [int(x) for x in o["gold_rows"][qi]]
            if not gold or qid in excluded:
                continue
            qs.append(qc_all[qi])
            gs.append(np.asarray(gold))
        if not qs:
            continue
        rr = score_archive(c, qs, gs)
        rows.extend(rr)
        cluster.extend([os.path.basename(f)] * len(rr))
        print(f"  realtalk {os.path.basename(f)} n={len(qs)}", flush=True)
    assert len(rows) == 705, len(rows)
    return rows, cluster


def aggregate(name, rows, cluster):
    out = {"n": len(rows), "n_clusters": int(len(set(cluster))),
           "mean_gold_size": float(np.mean([r["gold_size"] for r in rows])),
           "mean_N": float(np.mean([r["N"] for r in rows])),
           "frac_queries_with_N_le_10": float(
               np.mean([r["N"] <= 10 for r in rows]))}
    for k in KS:
        out[f"hit{k}_percent"] = {
            a: float(np.mean([r[f"hit{k}_{a}"] for r in rows]) * 100.0)
            for a in ARMS}
        out[f"frac{k}_percent"] = {
            a: float(np.mean([r[f"frac{k}_{a}"] for r in rows]) * 100.0)
            for a in ARMS}
    # contrasts on the new headline metric
    out["hit10_contrasts"] = {}
    for a, b in (("asym", "sym"), ("b8", "sym"), ("sign88", "sym"),
                 ("b8", "sign88"), ("float_std", "sym"), ("float", "sym")):
        d = [r[f"hit10_{a}"] - r[f"hit10_{b}"] for r in rows]
        out["hit10_contrasts"][f"{a}-{b}"] = bootstrap_ci(d, cluster)
    return out


def main():
    t0 = time.perf_counter()
    summary = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                          "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
               "what_this_is": ("re-read of the frozen parallel_ideas_r1 arms "
                                "under hit@k / frac@k; encoding and scoring "
                                "imported unchanged from lib_b8"),
               "arms": ARMS, "ks": list(KS),
               "tie_convention": "uniform random within equal-score bucket",
               "self_check": "frac_at_k(k=3) == lib_b8.exact_frac, all queries",
               "benchmarks": {}}
    for name, fn in (("perltqa", run_perltqa), ("lme", run_lme),
                     ("realtalk", run_realtalk)):
        print(f"=== {name} ===", flush=True)
        rows, cluster = fn()
        summary["benchmarks"][name] = aggregate(name, rows, cluster)
        print(f"  -> hit10 " + "  ".join(
            f"{a}={summary['benchmarks'][name]['hit10_percent'][a]:.2f}"
            for a in ARMS), flush=True)
    summary["elapsed_seconds"] = time.perf_counter() - t0
    with open("HIT10.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("wrote HIT10.json", flush=True)


if __name__ == "__main__":
    main()
