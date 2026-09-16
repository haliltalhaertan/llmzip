#!/usr/bin/env python3
"""Did the learned thresholds fail, or did the objective we gave them fail?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_learnthr.py` showed learned per-coordinate thresholds lose 2.81 pp on
RealTalk.  Three criticisms of how that was reported are correct and are
answered here.

1. "Shuffled beats learned, so placement is useless" was overclaimed: it
   rested on ONE shuffle and a 0.57 pp gap, with no spread.  Here the shuffle
   control is repeated N_SHUF times and reported as mean +- sd, so the gap can
   be read against its own noise.  Note also that moving a threshold to
   another coordinate changes its size relative to that coordinate's scale,
   not only its "placement" -- the control is not purely positional.

2. Calling stage 1 "uniform shifts" was wrong.  `np.quantile(C, q, axis=0)`
   already gives EVERY coordinate its own threshold; what is held constant is
   the quantile LEVEL, not the value.  Stage 1 was therefore also a
   per-coordinate threshold experiment.

3. The most instructive missing control, and the point of this script: did
   the learned thresholds actually improve the objective they were optimised
   for?  That separates two very different failures.

     objective improved, retrieval fell  -> the optimiser worked and the
       PROXY is wrong: preserving document-to-document neighbourhoods is not
       the same goal as finding the evidence for a question
     objective did not improve           -> look at the optimiser, not the
       proxy; zero was available as a candidate and should have been chosen

Reported per archive, then averaged:
  * J = sum_j [ #far straddled - LAMBDA * #near straddled ], the exact
    quantity the search maximises, evaluated at zero / learned / shuffled
  * the same thing in CODE space, which is what retrieval actually sees:
    mean Hamming distance for near pairs, for far pairs, and the separation
    between them
"""
import glob
import json
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
import run_learnthr as L  # noqa: E402

LAM = 1.0
N_SHUF = 20
KS = (1, 3, 10)
RNG = np.random.default_rng(20260916)


def objective(C, thr, near, far, lam=LAM):
    """the exact quantity learn_thresholds maximises, summed over coords."""
    tot = 0.0
    for j in range(C.shape[1]):
        vals = C[:, j]
        t = np.array([thr[j]])
        f = L.straddle_counts(vals, far, t)[0]
        n = L.straddle_counts(vals, near, t)[0]
        tot += f - lam * n
    return float(tot)


def code_separation(C, thr, near, far):
    """what retrieval sees: Hamming distance on near vs far pairs."""
    B = C >= thr[None, :]
    dn = np.count_nonzero(B[near[:, 0]] != B[near[:, 1]], axis=1).mean()
    df = np.count_nonzero(B[far[:, 0]] != B[far[:, 1]], axis=1).mean()
    return float(dn), float(df), float(df - dn)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "realtalk"
    rows = []
    hit = {a: [] for a in ("zero", "learn", "shuf")}

    def handle(C, queries, golds):
        C = np.asarray(C, dtype=np.float64)
        near, far = L.sample_pairs(C)
        zero = np.zeros(C.shape[1])
        learn = L.learn_thresholds(C, near, far, LAM)
        shufs = [RNG.permutation(learn) for _ in range(N_SHUF)]

        r = {"N": int(C.shape[0]),
             "J_zero": objective(C, zero, near, far),
             "J_learn": objective(C, learn, near, far),
             "J_shuf_mean": float(np.mean(
                 [objective(C, s, near, far) for s in shufs[:5]]))}
        for tag, t in (("zero", zero), ("learn", learn)):
            dn, df, sep = code_separation(C, t, near, far)
            r[f"ham_near_{tag}"], r[f"ham_far_{tag}"] = dn, df
            r[f"ham_sep_{tag}"] = sep
        # retrieval, with the shuffle control repeated
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            for tag, t in (("zero", zero), ("learn", learn)):
                B = C >= t[None, :]
                sc = L.hamming(B, q >= t)
                hit[tag].append(H.hit_at_k(sc, g, 10))
            sh = []
            for s in shufs:
                B = C >= s[None, :]
                sh.append(H.hit_at_k(L.hamming(B, q >= s), g, 10))
            hit["shuf"].append(sh)
        rows.append(r)

    if which == "realtalk":
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
                handle(o["C"], qs, gs)
            print(f"  {os.path.basename(f)} n={len(qs)}", flush=True)
    else:
        for i, f in enumerate(sorted(glob.glob(H.LME_GLOB))):
            d = pickle.loads(open(f, "rb").read())
            handle(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                   [np.asarray(d["gold"]).ravel().astype(int)])
            if (i + 1) % 100 == 0:
                print(f"  lme {i+1}", flush=True)

    sh = np.asarray(hit["shuf"])                 # n_queries x N_SHUF
    per_shuf = sh.mean(axis=0) * 100
    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": which, "lambda": LAM, "n_shuffles": N_SHUF,
           "n_queries": len(hit["zero"]),
           "objective_J": {
               "zero": float(np.mean([r["J_zero"] for r in rows])),
               "learned": float(np.mean([r["J_learn"] for r in rows])),
               "shuffled": float(np.mean([r["J_shuf_mean"] for r in rows])),
               "archives_where_learned_beats_zero": int(sum(
                   1 for r in rows if r["J_learn"] > r["J_zero"])),
               "n_archives": len(rows)},
           "hamming_separation": {
               "near_zero": float(np.mean([r["ham_near_zero"] for r in rows])),
               "far_zero": float(np.mean([r["ham_far_zero"] for r in rows])),
               "sep_zero": float(np.mean([r["ham_sep_zero"] for r in rows])),
               "near_learn": float(np.mean([r["ham_near_learn"] for r in rows])),
               "far_learn": float(np.mean([r["ham_far_learn"] for r in rows])),
               "sep_learn": float(np.mean([r["ham_sep_learn"] for r in rows]))},
           "hit10_percent": {
               "zero": float(np.mean(hit["zero"]) * 100),
               "learned": float(np.mean(hit["learn"]) * 100),
               "shuffled_mean": float(per_shuf.mean()),
               "shuffled_sd": float(per_shuf.std(ddof=1)),
               "shuffled_min": float(per_shuf.min()),
               "shuffled_max": float(per_shuf.max()),
               "shuffles_worse_than_learned": int(
                   np.count_nonzero(per_shuf < np.mean(hit["learn"]) * 100))}}
    with open(os.path.join(HERE, f"LEARNTHR_DIAG_{which}.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    J, S, Hh = out["objective_J"], out["hamming_separation"], out["hit10_percent"]
    print(f"\n=== {which}  n={out['n_queries']} ===")
    print("\n1. ALGORITMA KENDI HEDEFINI TUTTURDU MU?")
    print(f"   J(zero)      {J['zero']:12.1f}")
    print(f"   J(ogrenilmis){J['learned']:12.1f}   "
          f"fark {J['learned']-J['zero']:+.1f}")
    print(f"   J(karistirilmis){J['shuffled']:9.1f}")
    print(f"   ogrenilmis > zero olan arsiv: "
          f"{J['archives_where_learned_beats_zero']}/{J['n_archives']}")
    print("\n2. KOD UZAYINDA AYRISMA (uzak - yakin Hamming)")
    print(f"   zero        yakin {S['near_zero']:5.2f}  uzak {S['far_zero']:5.2f}"
          f"  ayrisma {S['sep_zero']:5.2f}")
    print(f"   ogrenilmis  yakin {S['near_learn']:5.2f}  uzak {S['far_learn']:5.2f}"
          f"  ayrisma {S['sep_learn']:5.2f}")
    print("\n3. ARAMA BASARISI")
    print(f"   zero          {Hh['zero']:6.2f}")
    print(f"   ogrenilmis    {Hh['learned']:6.2f}   "
          f"fark {Hh['learned']-Hh['zero']:+.2f}")
    print(f"   karistirilmis {Hh['shuffled_mean']:6.2f} +- {Hh['shuffled_sd']:.2f}"
          f"   (min {Hh['shuffled_min']:.2f}, max {Hh['shuffled_max']:.2f})")
    print(f"   ogrenilmisin altinda kalan karistirma: "
          f"{Hh['shuffles_worse_than_learned']}/{N_SHUF}")
    print(f"\nwrote LEARNTHR_DIAG_{which}.json")


if __name__ == "__main__":
    main()
