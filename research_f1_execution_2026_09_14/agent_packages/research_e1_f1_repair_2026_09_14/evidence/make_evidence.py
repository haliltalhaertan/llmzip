# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
#!/usr/bin/env python3
"""make_evidence.py — build evidence/per_query_rows.* + evidence/results.json.

SYNTHETIC-ONLY generator (real caches absent; see CACHE_INVENTORY.md). Uses
f1_competition.query_row / benchmark_summary / cluster_bootstrap so the
evidence files exercise the exact contract code path, including the row schema
a real-data executor would persist (qid, benchmark, cluster/section, delta,
gold_n, per-arm means, primary + sensitivity + min-gold-control gaps).
Deterministic: all RNG seeded.
"""
import csv
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import f1_competition as F

EV = HERE  # rows/results live directly in evidence/

C_FIX = [[2, -1, 1, -3], [-1, 2, -2, 1], [1, 1, -1, -1],
         [-2, -2, 2, 2], [0, 3, -3, 0]]
Q_FIX = [1, -2, 3, -1]

rows = [
    F.query_row(C_FIX, Q_FIX, [0, 2], 0.5, k=2, qid="FIX:Q1",
                benchmark="FIXTURE", cluster="archA"),
    F.query_row(C_FIX, Q_FIX, [4], -0.25, k=2, qid="FIX:Q2",
                benchmark="FIXTURE", cluster="archA"),
    F.query_row(C_FIX, Q_FIX, [1, 3], 0.1, k=2, qid="FIX:Q3",
                benchmark="FIXTURE", cluster="archB", section="demo"),
]

# Larger synthetic 96-D benchmark (k=64, overlapping TOP/BOT like the contract)
rng = random.Random(96013)
synth = []
for c in range(4):
    n = 12
    C = [[rng.gauss(0, 1.5) for _ in range(96)] for _ in range(n)]
    for i in range(6):
        q = [rng.gauss(0, 1) for _ in range(96)]
        ng = rng.choice([1, 1, 2, 3])
        gold = rng.sample(range(n), ng)
        delta = rng.gauss(0.05 * (len(gold) - 1), 1.0)
        synth.append(F.query_row(C, q, gold, delta, k=64,
                                 qid="SYN:c%d:q%d" % (c, i),
                                 benchmark="SYNTH", cluster="syn_c%d" % c))
rows.extend(synth)

with open(os.path.join(EV, "per_query_rows.json"), "w") as f:
    json.dump({"label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
                        "[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
               "origin": "SYNTHETIC fixtures only — real-cache rerun BLOCKED "
                         "(see ../CACHE_INVENTORY.md)",
               "schema": "qid, benchmark, cluster, section, delta, gold_n, "
                         "strict_top/tie_top/strict_bot/tie_bot (+_ng "
                         "sensitivity), strict_gap/tie_gap (+_ng), "
                         "min_strict_gap/min_tie_gap (FORBIDDEN-variant "
                         "control, never a metric)",
               "rows": rows}, f, indent=1, sort_keys=True)

cols = ["qid", "benchmark", "cluster", "section", "delta", "gold_n",
        "strict_top", "tie_top", "strict_bot", "tie_bot",
        "strict_gap", "tie_gap",
        "strict_top_ng", "tie_top_ng", "strict_bot_ng", "tie_bot_ng",
        "strict_gap_ng", "tie_gap_ng",
        "min_strict_gap", "min_tie_gap"]
with open(os.path.join(EV, "per_query_rows.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)

fix = [r for r in rows if r["benchmark"] == "FIXTURE"]
syn = [r for r in rows if r["benchmark"] == "SYNTH"]
boot = F.cluster_bootstrap(syn, seed=96013, n_boot=2000)

results = {
    "label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] "
             "[DISCLOSE-BEFORE-USE]",
    "three_reference_comparison": {
        "note": "Lead (buggy min-gold) and auditor (corrected per-gold) values "
                "are CLAIM re-extracted live from branch bytes (see verify_f1.py "
                "checks D1-D6, all PASS). Mine (real data) is UNAVAILABLE: "
                "caches absent, no network — exact inputs that would be needed "
                "are listed in CACHE_INVENTORY.md.",
        "LME": {"lead_min_gold_strict": 0.09965709814218833,
                "lead_min_gold_tie": 0.0989586520264074,
                "auditor_per_gold_strict": 0.14168629605302735,
                "auditor_per_gold_tie": 0.14045379360271315,
                "mine_real_data": "UNAVAILABLE-UNDER-MISSING-CACHES"},
        "REALTALK": {"lead_min_gold_strict": 0.06118332620206951,
                     "lead_min_gold_tie": 0.0871527005507532,
                     "auditor_per_gold_strict": 0.097939128891117,
                     "auditor_per_gold_tie": 0.12281952421315011,
                     "mine_real_data": "UNAVAILABLE-UNDER-MISSING-CACHES"},
        "PERLTQA": {"lead_min_gold_strict": 0.27738722348615524,
                    "lead_min_gold_tie": 0.285059265942642,
                    "auditor_per_gold_strict": 0.25416826537535475,
                    "auditor_per_gold_tie": 0.2797878341571222,
                    "mine_real_data": "UNAVAILABLE-UNDER-MISSING-CACHES"},
        "LOCOMO": {"lead_min_gold_strict": 0.09370604039357276,
                   "lead_min_gold_tie": 0.09533237242284638,
                   "auditor_per_gold_strict": 0.09491957131277647,
                   "auditor_per_gold_tie": 0.10376015063205302,
                   "mine_real_data": "UNAVAILABLE-UNDER-MISSING-CACHES"}},
    "synthetic_demonstration": {
        "fixture_summary": F.benchmark_summary(fix),
        "fixture_bug_effect": [
            {"qid": r["qid"],
             "correct": [r["strict_gap"], r["tie_gap"]],
             "min_gold": [r["min_strict_gap"], r["min_tie_gap"]]}
            for r in fix],
        "synth_summary_primary": F.benchmark_summary(syn),
        "synth_summary_nongold_sensitivity": F.benchmark_summary(
            syn, "strict_gap_ng", "tie_gap_ng"),
        "synth_summary_mingold_control": F.benchmark_summary(
            syn, "min_strict_gap", "min_tie_gap"),
        "synth_bootstrap_descriptive_posthoc": boot},
    "agreement_statement": "On hand-computed fixtures my implementation matches "
                           "the SPEC arithmetic exactly (verify_f1.py A1-A9, "
                           "all PASS); auditor-vs-mine agreement on REAL data "
                           "is UNTESTED (caches absent) — any future mismatch "
                           "on real data is a major finding per the task, not "
                           "to be explained away.",
}
with open(os.path.join(EV, "results.json"), "w") as f:
    json.dump(results, f, indent=1, sort_keys=True)
print("wrote %d rows; synth rho strict=%r tie=%r" % (
    len(rows), results["synthetic_demonstration"]["synth_summary_primary"]["rho_strict"],
    results["synthetic_demonstration"]["synth_summary_primary"]["rho_tie"]))
print("bootstrap strict interval=%s tie interval=%s" % (
    boot["strict_gap"]["interval_95"], boot["tie_gap"]["interval_95"]))
