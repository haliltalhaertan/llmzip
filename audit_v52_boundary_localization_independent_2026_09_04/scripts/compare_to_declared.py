#!/usr/bin/env python3
"""Compare the auditor's per-question reconstruction against the declared
summary JSONs and the per-seed CSVs. Reconstruction is the reference."""
import csv, json
R = json.load(open("audit_v52_boundary_localization_independent_2026_09_04/evidence/reconstruction.json"))
P = {"LoCoMo": "research/v52/locomo_boundary_outputs/locomo_boundary_summary.json",
     "LongMemEval": "research/v52/longmemeval_boundary_outputs/longmemeval_boundary_summary.json"}
C = {"LoCoMo": "research/v52/locomo_boundary_outputs/locomo_boundary_seed_results.csv",
     "LongMemEval": "research/v52/longmemeval_boundary_outputs/longmemeval_boundary_seed_results.csv"}
FIELDS = ["mean_R3","rho","sample_sd_R3","se_R3","sample_sd_rho","se_rho","rho_min","rho_max"]
worst = 0.0; report = {}
for ds in ("LoCoMo","LongMemEval"):
    s = json.load(open(P[ds])); rec = R[ds]; d = {}
    for arm, dec in s["primary"]["arm_stats"].items():
        mine = rec["arm_stats"][arm]
        for f in FIELDS:
            e = abs(dec[f]-mine[f]); worst = max(worst,e); d[f"{arm}.{f}"] = e
        d[f"{arm}.sign_inverting_match"] = (dec["sign_inverting_rotation_seeds"]
                                            == mine["sign_inverting_rotation_seeds"])
    for f in ("S_dataset","P1_rho32_pass","P2"):
        d[f"{f}_match"] = (s["primary"][f] == rec[f] if f!="S_dataset"
                           else list(s["primary"][f]) == list(rec[f]))
    d["Delta32_err"] = abs(s["primary"]["Delta32"]-rec["Delta32"]); worst=max(worst,d["Delta32_err"])
    d["declared_rows_match"] = (s["controls"]["per_question_actual_rows"] == rec["n_rows"])
    # per-seed CSV cross-check
    rows = list(csv.DictReader(open(C[ds])))
    d["seed_csv_rows"] = len(rows)
    cols = rows[0].keys(); d["seed_csv_columns"] = list(cols)
    rcol = next((c for c in cols if "R3" in c or "r3" in c.lower()), None)
    acol = next((c for c in cols if "arm" in c.lower()), None)
    scol = next((c for c in cols if "seed" in c.lower() and "part" not in c.lower()), None)
    mx = 0.0; n = 0
    if rcol and acol and scol:
        for r in rows:
            key = f"{r[acol]}|{int(r[scol])}"
            if key in rec["per_seed"]:
                mx = max(mx, abs(float(r[rcol]) - rec["per_seed"][key]["R3"])); n += 1
    d["seed_csv_matched_cells"] = n
    d["seed_csv_max_abs_R3_err"] = mx; worst = max(worst, mx)
    report[ds] = d
report["_worst_abs_error_overall"] = worst
json.dump(report, open("audit_v52_boundary_localization_independent_2026_09_04/evidence/declared_vs_reconstructed.json","w"), indent=2)
for ds in ("LoCoMo","LongMemEval"):
    d = report[ds]
    num = {k:v for k,v in d.items() if isinstance(v,float)}
    print(f"\n=== {ds} === max numeric deviation = {max(num.values()):.3e}")
    print("  non-matching booleans:", [k for k,v in d.items() if v is False] or "none")
    print(f"  per-seed CSV: {d['seed_csv_rows']} rows, {d['seed_csv_matched_cells']} cells matched, "
          f"max |dR3| = {d['seed_csv_max_abs_R3_err']:.3e}")
    print("  columns:", d["seed_csv_columns"])
print(f"\nWORST ABSOLUTE DEVIATION ACROSS EVERYTHING: {worst:.3e}")
