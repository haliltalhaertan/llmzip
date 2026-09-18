#!/usr/bin/env python3
"""Per-coordinate LEARNED thresholds: 96 better-placed decision boundaries.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Stage 1 (`run_threshold.py`) moved every coordinate's threshold by the same
quantile and found zero already best -- a sharp peak, with the median 1.4 pp
behind on RealTalk and random thresholds 24 pp behind.  That rules out
uniform shifts.  It does NOT rule out this proposal, which is per-coordinate:
some axes may want to move up and others down.

The criterion, as proposed: pick each coordinate's threshold from the
archive's own geometry, so that it separates pairs of documents that are FAR
apart in the full float space without splitting pairs that are NEAR.  A
threshold t splits a pair (a, b) on coordinate j exactly when
min(a_j, b_j) < t <= max(a_j, b_j), so for each coordinate

    score(t) = #(far pairs straddled by t) - LAMBDA * #(near pairs straddled)

is a piecewise-constant function computable exactly by a sweep over the
archive's own coordinate values.  We take the argmax.

What this is NOT allowed to touch, and does not:
  * no query vector and no gold label enters the fit -- only document
    coordinates and distances between documents
  * thresholds are per ARCHIVE and per COORDINATE, never per document
  * documents and query are encoded with the same thresholds
  * scoring is the production one, unchanged: Hamming over packed bits

Arms:
  zero        production baseline (threshold = archive mean)
  learn_L*    learned thresholds at several LAMBDA values
  shuffled    the learned threshold VALUES randomly permuted across
              coordinates -- the control that matters.  It keeps the
              distribution of thresholds and destroys only the pairing with
              the coordinate, so if `learn` beats `shuffled` the gain is the
              placement and not the spread.

LAMBDA is a tuning knob and there is no held-out set for it here, so any
`learn` arm that wins is an upper bound on what an honestly-tuned version
would get.  This is a screen, not a result.
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

LAMBDAS = (0.5, 1.0, 2.0)
N_PAIRS = 4000
KS = (1, 3, 10)
RNG = np.random.default_rng(20260916)


def sample_pairs(C):
    """near pairs = mutual top-cosine neighbours; far pairs = random."""
    n = C.shape[0]
    Cn = C / np.maximum(np.linalg.norm(C, axis=1, keepdims=True), 1e-12)
    m = min(n, 400)                       # cap the similarity matrix
    sel = RNG.choice(n, m, replace=False) if n > m else np.arange(n)
    S = Cn[sel] @ Cn[sel].T
    np.fill_diagonal(S, -np.inf)
    k = min(5, m - 1)
    nb = np.argpartition(-S, k, axis=1)[:, :k]
    near = np.stack([np.repeat(sel, k), sel[nb.ravel()]], axis=1)
    if len(near) > N_PAIRS:
        near = near[RNG.choice(len(near), N_PAIRS, replace=False)]
    # far: random pairs, then keep the least similar half
    a = RNG.integers(0, n, 2 * N_PAIRS)
    b = RNG.integers(0, n, 2 * N_PAIRS)
    ok = a != b
    a, b = a[ok], b[ok]
    sim = np.einsum("ij,ij->i", Cn[a], Cn[b])
    keep = np.argsort(sim)[:N_PAIRS]
    far = np.stack([a[keep], b[keep]], axis=1)
    return near, far


def straddle_counts(vals, pairs, cand):
    """how many pairs each candidate threshold straddles, on one coordinate."""
    lo = np.minimum(vals[pairs[:, 0]], vals[pairs[:, 1]])
    hi = np.maximum(vals[pairs[:, 0]], vals[pairs[:, 1]])
    lo.sort()
    hi.sort()
    # straddled iff lo < t <= hi
    return (np.searchsorted(lo, cand, side="left")
            - np.searchsorted(hi, cand, side="left"))


def learn_thresholds(C, near, far, lam):
    thr = np.zeros(C.shape[1])
    for j in range(C.shape[1]):
        vals = C[:, j]
        cand = np.unique(vals)
        if len(cand) < 2:
            continue
        sc = (straddle_counts(vals, far, cand).astype(np.float64)
              - lam * straddle_counts(vals, near, cand))
        thr[j] = cand[int(np.argmax(sc))]
    return thr


def hamming(Db, qb):
    return (-np.count_nonzero(Db != qb[None, :], axis=1)).astype(np.float64)


def one_archive(C, queries, golds, acc):
    C = np.asarray(C, dtype=np.float64)
    near, far = sample_pairs(C)
    arms = {"zero": np.zeros(C.shape[1])}
    for lam in LAMBDAS:
        t = learn_thresholds(C, near, far, lam)
        arms[f"learn_L{lam}"] = t
        if lam == 1.0:
            arms["shuffled"] = RNG.permutation(t)
    for name, thr in arms.items():
        Db = C >= thr[None, :]
        for j, qv in enumerate(queries):
            q = np.asarray(qv, dtype=np.float64).reshape(-1)
            g = np.asarray(golds[j]).ravel().astype(int)
            sc = hamming(Db, q >= thr)
            for k in KS:
                acc[(name, k)].append(H.hit_at_k(sc, g, k))
    return arms


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "realtalk"
    names = ["zero"] + [f"learn_L{l}" for l in LAMBDAS] + ["shuffled"]
    acc = {(n, k): [] for n in names for k in KS}
    moved = []

    if which == "lme":
        files = sorted(glob.glob(H.LME_GLOB))
        for i, f in enumerate(files):
            d = pickle.loads(open(f, "rb").read())
            a = one_archive(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                            [np.asarray(d["gold"]).ravel().astype(int)], acc)
            moved.append(float(np.mean(np.abs(a["learn_L1.0"]))))
            if (i + 1) % 100 == 0:
                print(f"  lme {i+1}/{len(files)}", flush=True)
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
                a = one_archive(o["C"], qs, gs, acc)
                moved.append(float(np.mean(np.abs(a["learn_L1.0"]))))
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
            a = one_archive(arch[ch]["C"],
                            [np.asarray(Q[q]["qC"], float) for q in ids],
                            [np.asarray(Q[q]["gold"]).ravel().astype(int)
                             for q in ids], acc)
            moved.append(float(np.mean(np.abs(a["learn_L1.0"]))))
            print(f"  perltqa {ch} n={len(ids)}", flush=True)
        del arch, Q

    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": which,
           "lambda_not_held_out": ("LAMBDA is chosen by looking at the same "
                                   "queries, so any winning learn arm is an "
                                   "upper bound, not an honest estimate"),
           "n_queries": len(acc[("zero", 10)]),
           "mean_abs_learned_threshold": float(np.mean(moved)),
           "hit_percent": {f"{n}_hit{k}": float(np.mean(acc[(n, k)]) * 100)
                           for n in names for k in KS}}
    with open(os.path.join(HERE, f"LEARNTHR_{which}.json"), "w") as fh:
        json.dump(res, fh, indent=2)

    hp = res["hit_percent"]
    base = hp["zero_hit10"]
    print(f"\n=== {which}  (n={res['n_queries']}) ===")
    print(f"  esiklerin ortalama buyuklugu: "
          f"{res['mean_abs_learned_threshold']:.4f}")
    print(f"  {'kol':>12s}{'hit@1':>9s}{'hit@3':>9s}{'hit@10':>9s}{'fark':>8s}")
    for n in names:
        print(f"  {n:>12s}{hp[f'{n}_hit1']:9.2f}{hp[f'{n}_hit3']:9.2f}"
              f"{hp[f'{n}_hit10']:9.2f}{hp[f'{n}_hit10'] - base:+8.2f}")
    print(f"\nwrote LEARNTHR_{which}.json")


if __name__ == "__main__":
    main()
