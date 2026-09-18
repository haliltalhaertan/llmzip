#!/usr/bin/env python3
"""Independently checking the three load-bearing audit findings.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

An external adversarial audit returned three findings that, if true, change
what the scaled-query result means.  Two of them are about the FROZEN scorer
and the frozen protocol, so they are checked here rather than accepted:

  F1  PROTOCOL.md makes ASYM-SIGN96 the primary BASELINE and SYM-SIGN96 only
      the symmetric CONTROL, so qscale was compared against the weakest of
      four existing 12-byte arms.  Recompute qscale against asym, b8 and
      sign88, cluster-bootstrapped.

  F2  The gain does not transfer to FR@3, the frozen estimand: claimed
      +4.34 SIG on PerLTQA, +0.06 ns on LongMemEval, -0.14 ns on RealTalk.

  F3  `lib_b8.ndcg3_expected` is not the expectation it claims.  A gold inside
      a tie bucket of size B starting at rank `pos` lands uniformly in one of
      B slots, so its expected discount is sum(disc[pos:pos+take]) / B.  The
      frozen code (lib_b8.py:63) divides by `take`, which over-credits by
      B/take whenever the bucket is larger than the slots it can fill.  This
      is checked by brute-force Monte Carlo over explicit permutations, not by
      reading the code.

F3 matters beyond this pilot: the bias is exactly zero without ties, so it
inflates the TIED arms (Hamming) and leaves the float arms untouched, and
`ndcg3_expected` is called from the frozen Task B entrypoint.
"""
import glob
import json
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

RNG = np.random.default_rng(20260916)
MC = 40000
B_REPS = 20000
ARMS = ["sym", "asym", "b8", "sign88", "qscale", "float_std"]


# ---------------------------------------------------------------- F3
def ndcg3_correct(scores, gold, K=3):
    """Same as lib_b8.ndcg3_expected but dividing by the BUCKET size."""
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    m = len(gset)
    disc = np.array([1.0 / np.log2(2 + p) for p in range(K)])
    idcg = float(disc[:min(K, m)].sum())
    exp_dcg, pos = 0.0, 0
    for lv in np.unique(s)[::-1]:
        if pos >= K:
            break
        idx = np.nonzero(s == lv)[0]
        Bn = len(idx)
        take = min(Bn, K - pos)
        gb = sum(1 for i in idx if int(i) in gset)
        exp_dcg += gb * float(disc[pos:pos + take].sum()) / Bn
        pos += Bn
    return exp_dcg / idcg


def ndcg3_mc(scores, gold, K=3, reps=MC):
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    m = len(gset)
    disc = np.array([1.0 / np.log2(2 + p) for p in range(K)])
    idcg = float(disc[:min(K, m)].sum())
    n = len(s)
    tot = 0.0
    for _ in range(reps):
        order = np.lexsort((RNG.random(n), -s))
        tot += sum(disc[p] for p in range(K)
                   if int(order[p]) in gset)
    return tot / reps / idcg


def check_f3():
    """Brute-force check on synthetic score vectors with heavy ties."""
    cases, worst, nbad = [], 0.0, 0
    for trial in range(300):
        n = int(RNG.integers(6, 14))
        lv = RNG.integers(0, 4, size=n).astype(float)     # heavy ties
        ng = int(RNG.integers(1, 4))
        gold = RNG.choice(n, size=ng, replace=False)
        mc = ndcg3_mc(lv, gold, reps=4000)
        frozen = B.ndcg3_expected(lv, gold)
        fixed = ndcg3_correct(lv, gold)
        d_frozen, d_fixed = abs(frozen - mc), abs(fixed - mc)
        worst = max(worst, d_frozen)
        if d_frozen > 0.02:
            nbad += 1
        cases.append({"n": n, "mc": mc, "frozen": frozen, "fixed": fixed,
                      "err_frozen": d_frozen, "err_fixed": d_fixed})
    return {
        "n_cases": len(cases),
        "mc_reps_per_case": 4000,
        "mean_abs_err_frozen": float(np.mean([c["err_frozen"] for c in cases])),
        "mean_abs_err_fixed": float(np.mean([c["err_fixed"] for c in cases])),
        "max_abs_err_frozen": float(worst),
        "max_abs_err_fixed": float(max(c["err_fixed"] for c in cases)),
        "cases_frozen_off_by_gt_0.02": nbad,
        "verdict": ("frozen ndcg3_expected is biased; dividing by the bucket "
                    "size reproduces the Monte-Carlo expectation")
        if np.mean([c["err_frozen"] for c in cases]) >
           10 * np.mean([c["err_fixed"] for c in cases])
        else "no material difference found",
    }


# ---------------------------------------------------------------- F1 / F2
def arm_scores(C, st, R, packed, payload_b8, q):
    qb = (np.asarray(q, dtype=np.float64) >= 0)
    sym = (-np.count_nonzero(
        np.unpackbits(packed, axis=1, bitorder="big")[:, :96].astype(bool)
        != qb[None, :], axis=1)).astype(np.float64)
    std = np.asarray(st["std"], dtype=np.float64)
    return {"sym": sym,
            "asym": B.cosine_from_code(R, q),
            "b8": B.b8_scores(payload_b8, st, q),
            "sign88": B.sign88_scores(payload_b8, st, q),
            "qscale": R @ (np.asarray(q, float).reshape(-1) / std),
            "float_std": B.float_std_scores(C, q, st["std"])}


def collect(name):
    out = defaultdict(lambda: defaultdict(list))
    cluster = []

    def do(C, queries, golds, tag):
        C = np.asarray(C, dtype=np.float64)
        st = B.fit_archive(C)
        packed = np.packbits((C >= 0), axis=1, bitorder="big").astype(np.uint8)
        payload_b8 = B.encode_docs(C, st)
        R = np.where(np.unpackbits(packed, axis=1,
                                   bitorder="big")[:, :96].astype(bool),
                     1.0, -1.0)
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            sc = arm_scores(C, st, R, packed, payload_b8, q)
            for a, s in sc.items():
                out["hit10"][a].append(H.hit_at_k(s, g, 10))
                out["fr3"][a].append(B.exact_frac(s, g, True))
                out["ndcg3_frozen"][a].append(B.ndcg3_expected(s, g))
                out["ndcg3_fixed"][a].append(ndcg3_correct(s, g))
            cluster.append(tag)

    if name == "lme":
        for f in sorted(glob.glob(H.LME_GLOB)):
            d = pickle.loads(open(f, "rb").read())
            do(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
               [np.asarray(d["gold"]).ravel().astype(int)],
               os.path.basename(f))
    elif name == "realtalk":
        excluded = set(json.load(open(H.EXCL_RT))["excluded_ids"])
        for f in sorted(glob.glob(H.RT_GLOB)):
            o = pickle.loads(open(f, "rb").read())
            qc = np.asarray(o["QC"], float)
            qs, gs = [], []
            for qi, qid in enumerate(o["qids"]):
                gold = [int(x) for x in o["gold_rows"][qi]]
                if gold and qid not in excluded:
                    qs.append(qc[qi])
                    gs.append(np.asarray(gold))
            if qs:
                do(o["C"], qs, gs, os.path.basename(f))
    else:
        arch = pickle.load(open(H.ARCH_PKL, "rb"))
        Q = pickle.load(open(H.Q_PKL, "rb"))
        by = defaultdict(list)
        for qid, v in Q.items():
            by[v["char"]].append(qid)
        for ch in sorted(by):
            ids = sorted(by[ch])
            do(arch[ch]["C"], [np.asarray(Q[q]["qC"], float) for q in ids],
               [np.asarray(Q[q]["gold"]).ravel().astype(int) for q in ids], ch)
        del arch, Q
    return out, np.asarray(cluster)


def boot_cluster(d, cluster):
    keys = np.unique(cluster)
    groups = [np.nonzero(cluster == k)[0] for k in keys]
    sums = np.array([d[g].sum() for g in groups])
    cnts = np.array([len(g) for g in groups], dtype=float)
    idx = RNG.integers(0, len(keys), size=(B_REPS, len(keys)))
    b = (sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)) * 100
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "F3_ndcg_bias": check_f3(), "benchmarks": {}}
    f3 = res["F3_ndcg_bias"]
    print("=== F3: lib_b8.ndcg3_expected Monte-Carlo dogrulamasi ===")
    print(f"  {f3['n_cases']} sentetik vaka x {f3['mc_reps_per_case']} permutasyon")
    print(f"  donmus kod  ortalama hata {f3['mean_abs_err_frozen']:.4f}  "
          f"en buyuk {f3['max_abs_err_frozen']:.4f}")
    print(f"  duzeltilmis ortalama hata {f3['mean_abs_err_fixed']:.6f}  "
          f"en buyuk {f3['max_abs_err_fixed']:.6f}")
    print(f"  0.02'den fazla sapan vaka: "
          f"{f3['cases_frozen_off_by_gt_0.02']}/{f3['n_cases']}")
    print(f"  -> {f3['verdict']}\n", flush=True)

    for name in ("perltqa", "lme", "realtalk"):
        out, cluster = collect(name)
        rec = {"n_queries": len(cluster),
               "n_archives": int(len(np.unique(cluster))),
               "levels": {}, "contrasts": {}}
        for metric in ("hit10", "fr3", "ndcg3_frozen", "ndcg3_fixed"):
            rec["levels"][metric] = {
                a: float(np.mean(out[metric][a]) * 100) for a in ARMS}
        for metric in ("hit10", "fr3"):
            for base in ("sym", "asym", "b8", "sign88"):
                d = (np.asarray(out[metric]["qscale"])
                     - np.asarray(out[metric][base]))
                lo, hi = boot_cluster(d, cluster)
                rec["contrasts"][f"{metric}:qscale-{base}"] = {
                    "delta_pp": float(d.mean() * 100), "ci95": [lo, hi],
                    "significant": bool(lo > 0 or hi < 0)}
        res["benchmarks"][name] = rec
        print(f"=== {name}  {rec['n_queries']} sorgu / {rec['n_archives']} arsiv ===")
        print(f"  {'kol':>10s}{'hit@10':>9s}{'FR@3':>9s}"
              f"{'nDCG@3 donmus':>15s}{'nDCG@3 dogru':>14s}")
        for a in ARMS:
            print(f"  {a:>10s}{rec['levels']['hit10'][a]:9.2f}"
                  f"{rec['levels']['fr3'][a]:9.2f}"
                  f"{rec['levels']['ndcg3_frozen'][a]:15.2f}"
                  f"{rec['levels']['ndcg3_fixed'][a]:14.2f}")
        print(f"  {'kontrast':>22s}{'fark':>9s}{'kume CI95':>22s}{'':>4s}")
        for key, c in rec["contrasts"].items():
            tag = "SIG" if c["significant"] else "ns"
            lo, hi = c["ci95"]
            ci = f"[{lo:+.2f}, {hi:+.2f}]"
            print(f"  {key:>22s}{c['delta_pp']:+9.2f}{ci:>22s}{tag:>4s}")
        print(flush=True)

    with open(os.path.join(HERE, "VERIFY_AUDIT.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote VERIFY_AUDIT.json")


if __name__ == "__main__":
    main()
