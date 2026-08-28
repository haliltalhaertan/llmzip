#!/usr/bin/env python3
"""Independent raw-table reproduction for V52 Task 4C3.

Usage:
  python audit_v52_t4c3/reproduce_raw_table_audit.py \
      --trial V52_T4C3_trial_results.csv \
      --qlevel V52_T4C3_question_level.csv
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

ROT = [43001, 43002, 43003, 43004, 43005]
ITQ = [101, 202, 303, 404, 505]
BLOCKS = [2, 4, 8, 16, 32, 96]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", type=Path, required=True)
    ap.add_argument("--qlevel", type=Path, required=True)
    a = ap.parse_args()

    t = pd.read_csv(a.trial)
    q = pd.read_csv(a.qlevel)

    assert len(t) == 385400, len(t)
    assert t.question_id.nunique() == 470
    assert q.question_id.nunique() == 470
    assert set(t.trial.unique()) == set(range(20))
    assert set(t.loc[t.method=="BLOCK_ORTHO_SIGN96","seed"].dropna().astype(int)) == set(ROT)
    assert set(t.loc[t.method=="ITQ96_CENTERED","seed"].dropna().astype(int)) == set(ITQ)
    assert set(t.loc[t.method=="BLOCK_ORTHO_SIGN96","block_size"].dropna().astype(int)) == set(BLOCKS)

    key = ["question_id","method","block_size","seed","trial"]
    assert not t.duplicated(key).any()
    assert (t.groupby("question_id").size() == 820).all()

    # Independently check metric semantics from gold cardinality.
    z = t.merge(q[["question_id","gold_count"]], on="question_id", validate="many_to_one")
    hits_float = z.fractional_r3 * z.gold_count
    hits = np.rint(hits_float).astype(int)
    assert np.max(np.abs(hits_float - hits)) < 1e-12
    assert np.array_equal(z.any_r3.astype(bool).to_numpy(), (hits > 0))
    assert np.array_equal(z.all_r3.astype(bool).to_numpy(), (hits == z.gold_count.to_numpy()))

    # Collapse nuisance within question/method/block/seed.
    c = (t.groupby(["question_id","method","block_size","seed"], dropna=False, as_index=False)
           [["any_r3","all_r3","fractional_r3"]].mean())

    def agg(method, block=None):
        x = c[c.method == method]
        if block is not None:
            x = x[x.block_size == block]
        xq = x.groupby("question_id")[["any_r3","all_r3","fractional_r3"]].mean()
        return xq.mean().to_dict(), xq

    native, native_q = agg("NATIVE_SIGN96")
    signed, _ = agg("SIGNED_PERM_CONTROL96")
    itq, _ = agg("ITQ96_CENTERED")
    blocks = {b: agg("BLOCK_ORTHO_SIGN96", b)[0] for b in BLOCKS}

    b96 = c[(c.method=="BLOCK_ORTHO_SIGN96") & (c.block_size==96)]
    seedvals = b96.groupby("seed")[["any_r3","all_r3","fractional_r3"]].mean()
    haar_q = b96.groupby("question_id")[["any_r3","all_r3","fractional_r3"]].mean()
    d96 = (haar_q.fractional_r3.mean() - native_q.fractional_r3.mean()) * 100.0

    paired = (native_q.fractional_r3 - haar_q.fractional_r3) * 100.0
    eps = 1e-12
    w = int((paired > eps).sum())
    tie = int((paired.abs() <= eps).sum())
    loss = int((paired < -eps).sum())
    positive = paired[paired > 0].sort_values(ascending=False)
    remaining = {}
    for k in (10,25,50):
        remaining[str(k)] = float(paired.drop(index=positive.head(k).index).mean())

    expected = {
        "native_fractional": 0.5419751773049645,
        "haar96_fractional": 0.3827166666666667,
        "d96_pp": -15.925851063829777,
    }
    assert abs(native["fractional_r3"] - expected["native_fractional"]) < 1e-14
    assert abs(haar_q.fractional_r3.mean() - expected["haar96_fractional"]) < 1e-14
    assert abs(d96 - expected["d96_pp"]) < 1e-12
    assert (seedvals.fractional_r3 < native["fractional_r3"]).all()
    assert abs(signed["fractional_r3"] - native["fractional_r3"]) < 1e-14

    out = {
        "rows": len(t),
        "questions": int(t.question_id.nunique()),
        "native": native,
        "signed_perm": signed,
        "itq": itq,
        "blocks": blocks,
        "haar96_seed_values": {str(int(k)): float(v) for k,v in seedvals.fractional_r3.items()},
        "haar96_fractional": float(haar_q.fractional_r3.mean()),
        "D96_pp": float(d96),
        "all_5_haar96_below_native": bool((seedvals.fractional_r3 < native["fractional_r3"]).all()),
        "native_minus_haar_question_W_T_L": [w, tie, loss],
        "median_native_minus_haar_pp": float(paired.median()),
        "remaining_mean_native_advantage_after_top_positive_removed_pp": remaining,
        "verdict": "STRONG AXIS-STRUCTURE EFFECT — FULL ORTHOGONAL MIXING HURTS SIGN RETRIEVAL",
    }
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
