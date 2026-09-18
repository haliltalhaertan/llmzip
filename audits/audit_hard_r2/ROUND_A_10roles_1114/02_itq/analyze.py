"""02_itq analysis: read-only over own per-archive rows + RESULTS_ORIG."""
import csv
import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = [20260916, 20260917, 20260918, 7, 42]


def load(tag):
    with open(os.path.join(HERE, "per_archive_rows_%s.csv" % tag)) as f:
        return list(csv.DictReader(f))


def mean(rows, arm, scorer, metric="hit10_pct"):
    sel = [r for r in rows if r["arm"] == arm and r["scorer"] == scorer]
    n = sum(int(r["n"]) for r in sel)
    return sum(float(r[metric]) * int(r["n"]) for r in sel) / n


def paired_counts(rows, a, b, scorer, metric="hit10_pct"):
    """Per-archive sign of (a-b); returns (neg, zero, pos)."""
    da = {(r["archive"]): float(r[metric]) for r in rows
          if r["arm"] == a and r["scorer"] == scorer}
    db = {(r["archive"]): float(r[metric]) for r in rows
          if r["arm"] == b and r["scorer"] == scorer}
    assert set(da) == set(db)
    diffs = [da[k] - db[k] for k in da]
    return (sum(1 for d in diffs if d < 0), sum(1 for d in diffs if d == 0),
            sum(1 for d in diffs if d > 0), diffs)


out = {"seeds": SEEDS, "benches": {}}
orig = json.load(open(os.path.join(HERE, "RESULTS_ORIG.json")))

for tag, bkey in (("rt", "RealTalk"), ("pqsub5", "PerLTQA")):
    rows = load(tag)
    E = {"n_rows": len(rows),
         "archives": sorted(set(r["archive"] for r in rows)),
         "n_queries": sum(int(r["n"]) for r in rows if r["arm"] == "FULL" and r["scorer"] == "qscale")}
    # explicit verification of published single-fit contrasts on RT full cohort
    if tag == "rt":
        full_q = mean(rows, "FULL", "qscale")
        itq16 = mean(rows, "ITQ_20260916", "qscale")
        pub = orig["benchmarks"]["RealTalk"]["summary"]
        E["verify_vs_published"] = {
            "FULL_qscale_mine": full_q,
            "FULL_qscale_publ": pub["FULL/qscale"]["hit10_pct"],
            "ITQ16_qscale_mine": itq16,
            "ITQ16_qscale_publ": pub["ITQ_C/qscale"]["hit10_pct"],
            "ITQ16-FULL_mine": itq16 - full_q,
            "ITQ16-FULL_publ_-16.88": pub["ITQ_C/qscale"]["hit10_pct"] - pub["FULL/qscale"]["hit10_pct"],
        }
        for s in [20260916, 20260917, 20260918]:
            E["verify_vs_published"]["ITQ16-RAND%d_mine" % s] = itq16 - mean(rows, "RAND_%d" % s, "qscale")
    # paired ITQ_s - RAND_s per seed, both scorers
    E["paired"] = {}
    for s in SEEDS:
        for scorer in ("sym", "qscale"):
            neg, zer, pos, diffs = paired_counts(rows, "ITQ_%d" % s, "RAND_%d" % s, scorer)
            E["paired"]["seed%d/%s_ITQ-RAND" % (s, scorer)] = {
                "cohort_diff_pp": mean(rows, "ITQ_%d" % s, scorer) - mean(rows, "RAND_%d" % s, scorer),
                "per_archive_neg_zero_pos": [neg, zer, pos],
                "per_archive_diffs_pp": [round(d, 4) for d in diffs],
            }
    # init sensitivity: spread across ITQ inits vs across RANDs
    E["spread_qscale_hit10"] = {
        "ITQ_min": min(mean(rows, "ITQ_%d" % s, "qscale") for s in SEEDS),
        "ITQ_max": max(mean(rows, "ITQ_%d" % s, "qscale") for s in SEEDS),
        "RAND_min": min(mean(rows, "RAND_%d" % s, "qscale") for s in SEEDS),
        "RAND_max": max(mean(rows, "RAND_%d" % s, "qscale") for s in SEEDS),
    }
    # quantization objective vs retrieval: loss reduction but retrieval change
    lr = []
    for r in rows:
        if r["arm"].startswith("ITQ_") and r["scorer"] == "qscale" and r["loss_init"]:
            l0, l1 = float(r["loss_init"]), float(r["loss_final"])
            h0, h1 = float(r["haar_init"]), float(r["haar_final"])
            lr.append((l0, l1, h0, h1))
    l0 = np.array([x[0] for x in lr])
    l1 = np.array([x[1] for x in lr])
    # haar==frob identity: haar is mean, frob is sum over same entries
    E["objective"] = {
        "n_fits": len(lr),
        "all_decreased": bool(np.all(l1 <= l0)),
        "mean_rel_reduction": float(((l0 - l1) / l0).mean()),
        "min_rel_reduction": float(((l0 - l1) / l0).min()),
    }
    out["benches"][tag] = E
    print("== %s n=%d ==" % (tag, E["n_queries"]))
    if tag == "rt":
        for k, v in E["verify_vs_published"].items():
            print("  %-28s %s" % (k, v))
    for s in SEEDS:
        for scorer in ("sym", "qscale"):
            p = E["paired"]["seed%d/%s_ITQ-RAND" % (s, scorer)]
            print("  seed %d %-6s ITQ-RAND=%+.4f pp arch(-/0/+)=%s" % (
                s, scorer, p["cohort_diff_pp"], p["per_archive_neg_zero_pos"]))
    print("  spread:", E["spread_qscale_hit10"])
    print("  objective:", E["objective"])

with open(os.path.join(HERE, "evidence_itq.json"), "w") as f:
    json.dump(out, f, indent=2)
print("wrote evidence_itq.json")
