#!/usr/bin/env python3
"""
Gate K/L/M — independent reconstruction of every seed-level R@3 and rho
DIRECTLY from the persisted per-question records.

Deliberately does NOT read:
  - *_boundary_summary.json
  - *_boundary_seed_results.csv
Only the per-question CSV.GZ is opened, plus the two frozen anchors quoted
from the preregistration text (which are inputs to the estimand, not outputs).

Written cold by the independent auditor. No prior session values consulted.
"""
import csv, gzip, json, math, sys, statistics
from collections import defaultdict

V52 = "research/v52"

# Anchors as written in the PREREGISTRATION (§3), transcribed by the auditor.
FROZEN = {
    "LoCoMo": {
        "native": 0.23654714666441054,
        "full_haar": 0.13770827054136,
        "n": 1535,
        "pq": f"{V52}/locomo_boundary_outputs/locomo_boundary_per_question.csv.gz",
    },
    "LongMemEval": {
        "native": 0.5419751773049646,
        "full_haar": 0.38271666666667,
        "n": 470,
        "pq": f"{V52}/longmemeval_boundary_outputs/longmemeval_boundary_per_question.csv.gz",
    },
}
BOUNDARIES = [16, 24, 32, 48, 64]
ROT_SEEDS = list(range(58001, 58011))
PART_SEEDS = list(range(68001, 68011))
THRESH = 0.25

def load(path):
    with gzip.open(path, "rt", newline="") as fh:
        return list(csv.DictReader(fh))

def analyse(ds):
    cfg = FROZEN[ds]
    rows = load(cfg["pq"])
    out = {"dataset": ds, "n_rows": len(rows)}

    # ---- structural checks (Gate J) ----
    arms = sorted({r["arm"] for r in rows})
    seeds = sorted({int(r["rotation_seed"]) for r in rows})
    qids = sorted({r["question_id"] for r in rows})
    out["arms"] = arms
    out["rotation_seeds"] = seeds
    out["n_unique_questions"] = len(qids)

    # exactly one record per (question, arm, seed)
    cell = defaultdict(int)
    for r in rows:
        cell[(r["question_id"], r["arm"], int(r["rotation_seed"]))] += 1
    out["max_records_per_cell"] = max(cell.values())
    out["min_records_per_cell"] = min(cell.values())
    out["n_cells"] = len(cell)
    out["expected_cells"] = len(qids) * len(arms) * len(seeds)
    out["complete_coverage"] = (out["n_cells"] == out["expected_cells"]
                                and out["max_records_per_cell"] == 1)
    out["cohort_matches_prereg"] = (len(qids) == cfg["n"])

    # partition_seed must be present exactly on RANDOM32 and absent elsewhere
    ps_by_arm = defaultdict(set)
    for r in rows:
        ps_by_arm[r["arm"]].add(r["partition_seed"])
    out["partition_seed_by_arm"] = {a: sorted(v) for a, v in ps_by_arm.items()}

    # pairing rule 5800i <-> 6800i (prereg §7)
    pairing_ok = True
    for r in rows:
        if r["arm"] == "RANDOM32":
            if int(r["partition_seed"]) != int(r["rotation_seed"]) + 10000:
                pairing_ok = False
                break
    out["paired_seed_rule_ok"] = pairing_ok

    # ---- native reconstruction (Gate F) ----
    # native_fractional_R3 must be identical for a question across all arms/seeds
    nat_per_q = defaultdict(set)
    for r in rows:
        nat_per_q[r["question_id"]].add(r["native_fractional_R3"])
    out["native_constant_per_question"] = all(len(v) == 1 for v in nat_per_q.values())
    native_vals = [float(next(iter(v))) for v in nat_per_q.values()]
    native_rec = sum(native_vals) / len(native_vals)
    out["native_R3_reconstructed"] = native_rec
    out["native_R3_frozen"] = cfg["native"]
    out["native_abs_error"] = abs(native_rec - cfg["native"])

    L_full = cfg["native"] - cfg["full_haar"]
    out["L_full_from_frozen_anchors"] = L_full

    # ---- seed-level R@3 and rho (Gate K) ----
    acc = defaultdict(list)
    for r in rows:
        acc[(r["arm"], int(r["rotation_seed"]))].append(float(r["fractional_R3"]))

    per_seed, arm_stats = {}, {}
    for arm in arms:
        seed_R3, seed_rho = [], []
        for s in ROT_SEEDS:
            vals = acc[(arm, s)]
            R = sum(vals) / len(vals)
            rho = (cfg["native"] - R) / L_full
            per_seed[f"{arm}|{s}"] = {"R3": R, "rho": rho, "n": len(vals)}
            seed_R3.append(R); seed_rho.append(rho)
        mean_R3 = sum(seed_R3) / len(seed_R3)
        mean_rho = (cfg["native"] - mean_R3) / L_full
        arm_stats[arm] = {
            "mean_R3": mean_R3,
            "rho": mean_rho,
            "mean_of_per_seed_rho": sum(seed_rho) / len(seed_rho),
            "sample_sd_R3": statistics.stdev(seed_R3),
            "se_R3": statistics.stdev(seed_R3) / math.sqrt(len(seed_R3)),
            "sample_sd_rho": statistics.stdev(seed_rho),
            "se_rho": statistics.stdev(seed_rho) / math.sqrt(len(seed_rho)),
            "rho_min": min(seed_rho),
            "rho_max": max(seed_rho),
            "per_seed_R3": seed_R3,
            "per_seed_rho": seed_rho,
            # L_b changes sign  <=>  R_b > R_native  <=>  rho < 0
            "sign_inverting_rotation_seeds": [ROT_SEEDS[i] for i, v in enumerate(seed_rho) if v < 0],
            # individually above the sufficiency threshold
            "threshold_exceeding_rotation_seeds": [ROT_SEEDS[i] for i, v in enumerate(seed_rho) if v > THRESH],
        }
    out["arm_stats"] = arm_stats
    out["per_seed"] = per_seed

    # ---- sufficiency set (Gate L) ----
    out["S_dataset"] = [b for b in BOUNDARIES if arm_stats[f"B{b}"]["rho"] <= THRESH]
    out["rho32"] = arm_stats["B32"]["rho"]
    out["P1_rho32_pass"] = bool(arm_stats["B32"]["rho"] <= THRESH)
    out["rho_random32"] = arm_stats["RANDOM32"]["rho"]
    d32 = arm_stats["RANDOM32"]["rho"] - arm_stats["B32"]["rho"]
    out["Delta32"] = d32
    out["P2"] = ("SPECTRAL_POSITION_CONFIRMED" if d32 >= 0.25 else
                 "GENERIC_BLOCK_NOT_REJECTED" if d32 <= 0.05 else
                 "MIXED_PARTIAL")
    return out

res = {ds: analyse(ds) for ds in FROZEN}

S_L = set(res["LoCoMo"]["S_dataset"])
S_M = set(res["LongMemEval"]["S_dataset"])
S_common = sorted(S_L & S_M)
p1 = res["LoCoMo"]["P1_rho32_pass"] and res["LongMemEval"]["P1_rho32_pass"]
p2 = (res["LoCoMo"]["P2"] == "SPECTRAL_POSITION_CONFIRMED"
      and res["LongMemEval"]["P2"] == "SPECTRAL_POSITION_CONFIRMED")

# prereg §11, applied mechanically in written order
if p1 and p2 and S_common == [32]:
    verdict = "L1 [PC32-LOCALIZED SUFFICIENCY LEAD - ON TESTED GRID]"
elif p1 and p2 and 32 in S_common and 1 < len(S_common) < 5:
    verdict = "L2 [BROAD CONTIGUOUS SUFFICIENCY PLATEAU - NO UNIQUE PC32]"
elif p1 and p2 and S_common == BOUNDARIES:
    verdict = "L3 [NO BOUNDARY LOCALIZATION]"
elif p2 and S_common and 32 not in S_common:
    verdict = "L4 [BOUNDARY SHIFT]"
elif not S_common:
    verdict = "L5 [NO SHARED SUFFICIENT BOUNDARY - DATASET HETEROGENEITY]"
else:
    verdict = "UNCLASSIFIED"

res["_cross_dataset"] = {
    "S_LoCoMo": sorted(S_L),
    "S_LongMemEval": sorted(S_M),
    "S_common": S_common,
    "P1_both_pass": p1,
    "P2_both_confirmed": p2,
    "mechanical_verdict": verdict,
    "heterogeneity_flag": (sorted(S_L) != sorted(S_M)),
}
json.dump(res, open(sys.argv[1], "w"), indent=2)

c = res["_cross_dataset"]
for ds in ("LoCoMo", "LongMemEval"):
    r = res[ds]
    print(f"\n=== {ds} ===  rows={r['n_rows']} q={r['n_unique_questions']} "
          f"cells_complete={r['complete_coverage']} native_err={r['native_abs_error']:.3e}")
    for a in ["B16", "B24", "B32", "B48", "B64", "RANDOM32"]:
        s = r["arm_stats"][a]
        print(f"  {a:9s} R3={s['mean_R3']:.15f} rho={s['rho']:.15f} "
              f"se_rho={s['se_rho']:.6f} [{s['rho_min']:.4f},{s['rho_max']:.4f}] "
              f"over={s['threshold_exceeding_rotation_seeds']} inv={s['sign_inverting_rotation_seeds']}")
    print(f"  S_{ds}={r['S_dataset']} P1={r['P1_rho32_pass']} Delta32={r['Delta32']:.15f} P2={r['P2']}")
print("\n=== CROSS ===")
for k, v in c.items():
    print(f"  {k} = {v}")
