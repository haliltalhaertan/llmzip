#!/usr/bin/env python3
"""Same 96 bits, different questions: does the threshold position matter?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The production code asks every centered coordinate "are you >= 0?", i.e. the
threshold is the archive mean.  The proposal is to keep one bit per
coordinate but move each coordinate's decision boundary to a more useful
place.  Nothing is gained for free: a threshold at +0.40 separates +0.12 from
+0.80 but stops separating -0.80 from +0.12.  The question is whether the
trade is worth making.

Stage 1 (this script) asks the cheap prior question: does the position matter
at all, and in which direction?  If zero is already optimal there is nothing
to learn.

  quantile arms   every coordinate's threshold at its own q-th quantile,
                  q in 0.1 ... 0.9.  q ~ 0.5 is the balanced-bit code.
  zero            the production threshold, as the baseline
  random          thresholds drawn from the coordinate's own distribution,
                  as a control -- if random matches zero, position is inert

Rules kept identical to production so only the threshold moves:
  * thresholds are per ARCHIVE and per COORDINATE (96 numbers), never per
    document -- a bit must mean the same thing in every row
  * documents and the query are encoded with the SAME thresholds
  * thresholds are fitted from the archive's document coordinates only;
    no query and no gold label is touched
  * scoring is unchanged: Hamming over packed bits (`sym`), and the same
    code scored against an exact query (`float_q`) to separate the two
    effects this session found are distinct

The threshold vector replaces the mean vector the pipeline already stores,
so at equal accounting it is not extra memory; if both were kept it would be.
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

QS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
KS = (1, 3, 10)
RNG = np.random.default_rng(20260916)


def hamming_scores(Db, qb):
    """Production scorer: negative Hamming over packed bits."""
    return (-np.count_nonzero(Db != qb[None, :], axis=1)).astype(np.float64)


def float_q_scores(Db, q, thr):
    """Same bits, exact query: cosine(q - thr, +-1 reconstruction)."""
    R = np.where(Db, 1.0, -1.0)
    v = q - thr
    n = float(np.linalg.norm(v))
    if n == 0 or not np.isfinite(n):
        return np.full(R.shape[0], -np.inf)
    return (R @ v) / (np.linalg.norm(R, axis=1) * n)


def arms_for(C):
    """threshold vectors, all fitted from documents alone."""
    out = {"zero": np.zeros(C.shape[1])}
    for q in QS:
        out[f"q{q:.1f}"] = np.quantile(C, q, axis=0)
    lo, hi = C.min(axis=0), C.max(axis=0)
    out["random"] = lo + RNG.random(C.shape[1]) * (hi - lo)
    return out


def one_archive(C, queries, golds, acc):
    C = np.asarray(C, dtype=np.float64)
    for name, thr in arms_for(C).items():
        Db = C >= thr[None, :]
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            qb = q >= thr
            for mode, sc in (("sym", hamming_scores(Db, qb)),
                             ("float_q", float_q_scores(Db, q, thr))):
                for k in KS:
                    acc[(name, mode, k)].append(H.hit_at_k(sc, g, k))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "realtalk"
    names = list(arms_for(np.zeros((2, 96))).keys())
    acc = {(n, m, k): [] for n in names
           for m in ("sym", "float_q") for k in KS}

    if which == "lme":
        for f in sorted(glob.glob(H.LME_GLOB)):
            d = pickle.loads(open(f, "rb").read())
            one_archive(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                        [np.asarray(d["gold"]).ravel().astype(int)], acc)
    elif which == "realtalk":
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
                one_archive(o["C"], qs, gs, acc)
            print(f"  realtalk {os.path.basename(f)} n={len(qs)}", flush=True)
    else:
        from collections import defaultdict
        arch = pickle.load(open(H.ARCH_PKL, "rb"))
        Q = pickle.load(open(H.Q_PKL, "rb"))
        by = defaultdict(list)
        for qid, v in Q.items():
            by[v["char"]].append(qid)
        for ch in sorted(by):
            ids = sorted(by[ch])
            one_archive(arch[ch]["C"],
                        [np.asarray(Q[q]["qC"], float) for q in ids],
                        [np.asarray(Q[q]["gold"]).ravel().astype(int)
                         for q in ids], acc)
            print(f"  perltqa {ch} n={len(ids)}", flush=True)
        del arch, Q

    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": which,
           "question": "does moving the per-coordinate threshold help",
           "thresholds": "per archive, per coordinate; docs and query share "
                         "them; fitted from document coordinates only",
           "n_queries": len(acc[("zero", "sym", 10)]),
           "hit_percent": {
               f"{n}_{m}_hit{k}": float(np.mean(acc[(n, m, k)]) * 100)
               for n in names for m in ("sym", "float_q") for k in KS}}
    with open(os.path.join(HERE, f"THRESHOLD_{which}.json"), "w") as fh:
        json.dump(res, fh, indent=2)

    hp = res["hit_percent"]
    base_s, base_f = hp["zero_sym_hit10"], hp["zero_float_q_hit10"]
    print(f"\n=== {which}  (n={res['n_queries']}) ===")
    print(f"  {'esik':>8s}{'sym':>9s}{'fark':>8s}{'float_q':>10s}{'fark':>8s}")
    for n in names:
        s, f = hp[f"{n}_sym_hit10"], hp[f"{n}_float_q_hit10"]
        print(f"  {n:>8s}{s:9.2f}{s - base_s:+8.2f}{f:10.2f}{f - base_f:+8.2f}")
    print(f"\nwrote THRESHOLD_{which}.json")


if __name__ == "__main__":
    main()
