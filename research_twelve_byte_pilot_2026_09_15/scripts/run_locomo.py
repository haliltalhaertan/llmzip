#!/usr/bin/env python3
"""LoCoMo: the fourth benchmark, scored on the same six arms as the other three.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

LoCoMo has cached, hash-pinned representations under regen/locomo/ (10
archives, C / QC / qas / id_to_row) built by the frozen recipe.  This scores
them with the SAME code path run_hit10.py uses for the other three, so the
numbers sit in the same table.

TWO CAVEATS THAT MUST TRAVEL WITH EVERY NUMBER HERE:

1. GOLD IS CONTESTED.  These caches carry `raw_evidence` only.  The historical
   producer applied 156 audit corrections (`correct_evidence`), and reconciling
   the two is an OPEN Head-Researcher obligation blocking Task 4F1.  Questions
   whose audited evidence differs are therefore scored against the RAW gold
   here.  This is a labelled choice, not a resolution.

2. NO HISTORICAL FLOAT ANCHOR EXISTS.  `theory_benchmark_test_v1/
   audit_locomo_provenance/REPORT.md` establishes that the circulating LoCoMo
   "SIGN - float = +12 pp" was never recomputed from data and is retracted
   pending a primary source.  The float columns below are FRESH measurements,
   not replications of a frozen baseline.

Benchmarks are never pooled; LoCoMo is reported as its own row.
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

GLOB = os.path.join(H.SRC, "regen", "locomo", "locomo_*.pkl")


def main():
    files = sorted(glob.glob(GLOB))
    assert len(files) == 10, len(files)
    rows_all = []
    n_q = n_skip = 0
    pools = []
    for f in files:
        d = pickle.load(open(f, "rb"))
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        i2r = d["id_to_row"]
        golds, keep = [], []
        for j, qa in enumerate(d["qas"]):
            rows = sorted({int(i2r[x]) for x in qa["raw_evidence"] if x in i2r})
            if not rows:
                n_skip += 1
                continue
            golds.append(np.asarray(rows, dtype=int))
            keep.append(j)
        if not keep:
            continue
        Q = QC[np.asarray(keep, dtype=int)]
        # score_archive self-checks frac@3 against the frozen lib_b8 scorer
        rows_all.extend(H.score_archive(C, Q, golds))
        n_q += len(keep)
        pools.append(C.shape[0])

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": "locomo",
           "gold": "raw_evidence only; the 156 audited corrections are an OPEN "
                   "Head-Researcher obligation and are NOT applied here",
           "float_anchor": "no historical LoCoMo float baseline exists in the "
                           "frozen artifacts; float columns are fresh",
           "n_archives": len(files), "n_queries": n_q,
           "queries_skipped_no_retrievable_gold": n_skip,
           "pool_mean": float(np.mean(pools)),
           "hit_percent": {}, "frac_percent": {}}
    for k in H.KS:
        out["hit_percent"][str(k)] = {
            a: float(np.mean([r[f"hit{k}_{a}"] for r in rows_all]) * 100)
            for a in H.ARMS}
        out["frac_percent"][str(k)] = {
            a: float(np.mean([r[f"frac{k}_{a}"] for r in rows_all]) * 100)
            for a in H.ARMS}
    with open(os.path.join(HERE, "LOCOMO.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"LoCoMo: {out['n_archives']} arşiv, {out['n_queries']} sorgu "
          f"(atlanan {n_skip}), havuz~{out['pool_mean']:.0f}\n")
    print(f"{'kol':12s}" + "".join(f"  hit@{k:<5d}" for k in H.KS))
    for a in H.ARMS:
        print(f"{a:12s}" + "".join(
            f"  {out['hit_percent'][str(k)][a]:7.2f}" for k in H.KS))
    print("\nwrote LOCOMO.json")


if __name__ == "__main__":
    main()
