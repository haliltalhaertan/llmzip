#!/usr/bin/env python3
"""Does the 12-byte code lose exactly where the answer hinges on a RARE term?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_bm25.py` established that plain BM25 matches or beats the whole pipeline
on the frozen metric, significantly on two of three benchmarks.  That is a
result without an explanation.  An external run proposes one: a truncated SVD
keeps the directions along which the archive varies MOST, and a term that
appears in three documents out of nine hundred contributes almost nothing to
that variance.  So the projection should discard rare terms preferentially --
and rare terms are exactly what pins an answer to one specific turn.

The prediction is sharp and falsifiable: split queries by how rare the rarest
term shared between the question and its gold evidence is.  If the mechanism
is right, the code should hold its own where the hinge term is COMMON and lose
badly where it is RARE.  If the gap is flat across buckets, the explanation is
wrong and the BM25 result still has no mechanism.

Bucketing is by document frequency of that hinge term within its own archive,
with the cut points fixed here and reported, not chosen after seeing the
split:

    none      the question shares no term with any gold document
    common    df > 10 % of the archive
    medium    2 % < df <= 10 %
    rare      df <= 2 %

Arms are the production `sym`, this session's `qscale`, and `bm25`, all on
FR@3 with the frozen tie convention.  Per-bucket counts are printed so a
bucket that is too small to read is visible as such.
"""
import glob
import json
import math
import os
import pickle
import re
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
import run_bm25 as M  # noqa: E402  (BM25 implementation and loaders)
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

BUCKETS = ["none", "common", "medium", "rare"]
RNG = np.random.default_rng(20260916)
B_REPS = 20000


def bucket_qonly(qtext, texts):
    """GOLD-FREE control bucketing.

    The main bucketing below uses the rarest term shared between the question
    and its gold, which is CIRCULAR for BM25: its score IS the IDF-weighted
    overlap, so "gold shares a rare term" and "BM25 ranks gold highly" are
    close to the same statement.  This variant looks only at the QUESTION's
    own rarest in-archive term and never touches gold, so if the pattern
    survives here the mechanism is not an artifact of the split.
    """
    n = len(texts)
    dfs = Counter()
    for t in texts:
        dfs.update(set(M.toks(t)))
    seen = [dfs[w] for w in set(M.toks(qtext)) if w in dfs]
    if not seen:
        return "none"
    frac = min(seen) / max(n, 1)
    if frac > 0.10:
        return "common"
    if frac > 0.02:
        return "medium"
    return "rare"


def bucket_of(qtext, gold_rows, texts):
    """Rarest term shared between the question and ANY gold document."""
    n = len(texts)
    qt = set(M.toks(qtext))
    dfs = Counter()
    for t in texts:
        dfs.update(set(M.toks(t)))
    best = None
    for g in gold_rows:
        for w in set(M.toks(texts[int(g)])) & qt:
            c = dfs.get(w, n)
            if best is None or c < best:
                best = c
    if best is None:
        return "none", None
    frac = best / max(n, 1)
    if frac > 0.10:
        return "common", frac
    if frac > 0.02:
        return "medium", frac
    return "rare", frac


def boot(d, cluster):
    keys = np.unique(cluster)
    groups = [np.nonzero(cluster == x)[0] for x in keys]
    sums = np.array([d[g].sum() for g in groups])
    cnts = np.array([len(g) for g in groups], float)
    idx = RNG.integers(0, len(keys), size=(B_REPS, len(keys)))
    b = (sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)) * 100
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main():
    which = sys.argv[1:] or ["lme", "perltqa", "locomo"]
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "buckets": "df of the rarest question/gold shared term, "
                      "cut at 10 % and 2 % of the archive, fixed in advance",
           "benchmarks": {}}

    for name in which:
        rows = {"sym": [], "qscale": [], "bm25": []}
        buck, buck_q, cl = [], [], []

        def collect(C, texts, questions, golds, qvecs, tag, acc_, cluster_):
            C = np.asarray(C, float)
            st = B.fit_archive(C)
            R = np.where(C >= 0, 1.0, -1.0)
            std = np.asarray(st["std"], float)
            bm = M.BM25(texts)
            for j, qt in enumerate(questions):
                q = np.asarray(qvecs[j], float).reshape(-1)
                g = np.asarray(golds[j]).ravel().astype(int)
                s_sym = (-np.count_nonzero((C >= 0) != (q >= 0)[None, :],
                                           axis=1)).astype(np.float64)
                rows["sym"].append(B.exact_frac(s_sym, g, True))
                rows["qscale"].append(B.exact_frac(R @ (q / std), g, True))
                rows["bm25"].append(B.exact_frac(bm.score(qt), g, True))
                b, _ = bucket_of(qt, g, texts)
                buck.append(b)
                buck_q.append(bucket_qonly(qt, texts))
                cl.append(tag)

        real_score, M.score = M.score, collect
        try:
            {"lme": M.run_lme, "perltqa": M.run_perltqa,
             "locomo": M.run_locomo}[name](defaultdict(list), [], 10**9)
        finally:
            M.score = real_score

        buck_q = np.asarray(buck_q)
        buck = np.asarray(buck)
        cl = np.asarray(cl)
        sym = np.asarray(rows["sym"])
        qs = np.asarray(rows["qscale"])
        bm = np.asarray(rows["bm25"])
        rec = {"n_queries": int(len(buck)), "by_bucket": {}}
        print(f"\n=== {name}  n={len(buck)} ===")
        print(f"  {'kova':>8s}{'sorgu':>7s}{'sym':>8s}{'qscale':>8s}"
              f"{'bm25':>8s}{'sym-bm25':>10s}{'kume CI95':>22s}")
        for tagname, BK in (("GOLD-BAGIMLI (dongusel olabilir)", buck),
                            ("SADECE-SORU (gold'a bakmaz)", buck_q)):
          print(f"  -- {tagname} --")
          for b in BUCKETS:
            m = BK == b
            if not m.any():
                continue
            d = sym[m] - bm[m]
            lo, hi = boot(d, cl[m])
            sig = "SIG" if (lo > 0 or hi < 0) else "ns"
            rec["by_bucket"].setdefault(tagname, {})[b] = {
                "n": int(m.sum()),
                "sym": float(sym[m].mean() * 100),
                "qscale": float(qs[m].mean() * 100),
                "bm25": float(bm[m].mean() * 100),
                "sym_minus_bm25": float(d.mean() * 100),
                "ci95": [lo, hi], "significant": sig == "SIG"}
            v = rec["by_bucket"][tagname][b]
            print(f"  {b:>8s}{v['n']:>7d}{v['sym']:8.2f}{v['qscale']:8.2f}"
                  f"{v['bm25']:8.2f}{v['sym_minus_bm25']:+10.2f}"
                  f"{f'[{lo:+.2f}, {hi:+.2f}]':>19s} {sig}")
        res["benchmarks"][name] = rec
        print(flush=True)

    with open(os.path.join(HERE, "RARETERM.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote RARETERM.json")


if __name__ == "__main__":
    main()
