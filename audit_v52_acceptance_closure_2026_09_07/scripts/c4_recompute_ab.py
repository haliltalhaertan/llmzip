"""C4 — recompute definition A and definition B for all four benchmark/arm
combinations from the PERSISTED PER-QUESTION ROWS (not from the summary JSONs),
and compare to the acceptance decision document's table to full precision.

Inputs are extracted from raw git blobs by the caller into a work directory:
  locomo.csv.gz, lme.csv.gz   (per-question rows @ research 0c9916bd)
  locomo_summary.json, lme_summary.json  (used ONLY as a cross-check, never as
                                          the source of A or B)

Definitions, read off preregistration section 7 and the sealed runner:
  per (arm, seed) mean m[arm,s] = mean over questions of fractional_R3
  arm grand mean      M[arm]    = mean over the 10 seeds of m[arm,s]
  A = mean_s  ( m[SCALED_X,s] - m[X_FRESH,s] ) / ( M[NATIVE] - m[X_FRESH,s] )
  B = ( M[SCALED_X] - M[X_FRESH] ) / ( M[NATIVE] - M[X_FRESH] )

Negative controls are included and MUST fail; a check that cannot fail is not
evidence.
"""
import gzip, json, csv, sys, math
from pathlib import Path
from collections import defaultdict

WORK = Path(sys.argv[1])
OUT = Path(sys.argv[2])

SEEDS = [59001, 59002, 59003, 59004, 59005, 59006, 59007, 59008, 59009, 59010]
ARMS = ["NATIVE", "SCALED_NATIVE", "FULLHAAR_FRESH", "SCALED_FULLHAAR",
        "BLOCK32_FRESH", "SCALED_BLOCK32"]


def load_arm_seed_means(path):
    """Return m[(arm,seed)] and row/question counts, straight from the CSV."""
    sums = defaultdict(float)
    counts = defaultdict(int)
    qids = set()
    nrows = 0
    with gzip.open(path, "rt", newline="") as fh:
        for row in csv.DictReader(fh):
            nrows += 1
            arm = row["arm"]
            s = int(row["rotation_seed"])
            v = float(row["fractional_R3"])
            sums[(arm, s)] += v
            counts[(arm, s)] += 1
            qids.add(row["question_id"])
    m = {k: sums[k] / counts[k] for k in sums}
    return m, counts, nrows, len(qids)


def frac(native, unscaled, scaled):
    return (scaled - unscaled) / (native - unscaled)


def compute(m, seeds=SEEDS):
    M = {arm: sum(m[(arm, s)] for s in seeds) / len(seeds) for arm in ARMS}
    res = {}
    for label, fresh, scaled in (("full", "FULLHAAR_FRESH", "SCALED_FULLHAAR"),
                                 ("block", "BLOCK32_FRESH", "SCALED_BLOCK32")):
        per_seed = [frac(M["NATIVE"], m[(fresh, s)], m[(scaled, s)]) for s in seeds]
        A = sum(per_seed) / len(per_seed)
        B = frac(M["NATIVE"], M[fresh], M[scaled])
        res[label] = {"A": A, "B": B, "A_minus_B": A - B, "per_seed_A": per_seed}
    res["_arm_means"] = M
    return res


# ---- the decision document's table, transcribed verbatim from its bytes -----
DOC_TABLE = {
    ("LoCoMo", "full"):      ("0.7271861342884777", "0.7261069075901362", "+0.0010792266983414844"),
    ("LoCoMo", "block"):     ("0.4454425786787960", "0.6516429195680419", "-0.2062003408892458"),
    ("LongMemEval", "full"): ("0.6569781664714960", "0.6563342970957214", "+0.0006438693757745"),
    ("LongMemEval", "block"):("0.3165111621882831", "0.3084585844542308", "+0.0080525777340523"),
}

report = {"python": sys.version, "gates": {}, "negative_controls": {}}
tables = {}

for bench, csvname, sumname in (("LoCoMo", "locomo.csv.gz", "locomo_summary.json"),
                                ("LongMemEval", "lme.csv.gz", "lme_summary.json")):
    m, counts, nrows, nq = load_arm_seed_means(WORK / csvname)
    r = compute(m)
    summary = json.loads((WORK / sumname).read_text())
    tables[bench] = {
        "rows": nrows,
        "questions": nq,
        "cells": len(counts),
        "cell_sizes": sorted(set(counts.values())),
        "arm_means_recomputed": r["_arm_means"],
        "arm_means_in_summary": summary["primary"]["arm_means"],
        "native_seed_invariant": len(set(repr(m[("NATIVE", s)]) for s in SEEDS)) == 1,
        "full": {k: v for k, v in r["full"].items()},
        "block": {k: v for k, v in r["block"].items()},
        "summary_frac_full_B": summary["primary"]["frac_full"],
        "summary_frac_block_B": summary["primary"]["frac_block"],
        "summary_frac_full_per_seed": summary["primary"]["frac_full_per_seed"],
        "summary_frac_block_per_seed": summary["primary"]["frac_block_per_seed"],
    }

# ---- compare against the document, to full precision ------------------------
comparisons = []
for (bench, arm), (dA, dB, dD) in DOC_TABLE.items():
    got = tables[bench][arm]
    cA, cB = got["A"], got["B"]
    cD = cA - cB
    comparisons.append({
        "benchmark": bench, "arm": arm,
        "doc_A": dA, "recomputed_A": repr(cA),
        "doc_B": dB, "recomputed_B": repr(cB),
        "doc_A_minus_B": dD, "recomputed_A_minus_B": repr(cD),
        "A_exact_string_match": dA == repr(cA) or float(dA) == cA,
        "B_exact_string_match": dB == repr(cB) or float(dB) == cB,
        "A_bitwise_equal": float(dA) == cA,
        "B_bitwise_equal": float(dB) == cB,
        "A_ulp_gap": abs(float(dA) - cA),
        "B_ulp_gap": abs(float(dB) - cB),
        "diff_bitwise_equal": float(dD) == cD,
        "diff_gap": abs(float(dD) - cD),
        "doc_diff_equals_doc_A_minus_doc_B": float(dD) == (float(dA) - float(dB)),
        "doc_diff_minus_docAminusdocB": float(dD) - (float(dA) - float(dB)),
    })

report["tables"] = tables
report["comparisons"] = comparisons

# ---- NEGATIVE CONTROLS: each must FAIL ---------------------------------------
nc = report["negative_controls"]

# NC1: perturb one per-question value in the LoCoMo scaled-full arm by 1e-9 and
#      show the A comparison stops matching.
m2, _, _, _ = load_arm_seed_means(WORK / "locomo.csv.gz")
m2[("SCALED_FULLHAAR", 59001)] += 1e-9
r2 = compute(m2)
nc["NC1_perturbed_input_breaks_A_match"] = {
    "perturbation": "m[SCALED_FULLHAAR,59001] += 1e-9",
    "A_after": repr(r2["full"]["A"]),
    "still_matches_doc": float(DOC_TABLE[("LoCoMo", "full")][0]) == r2["full"]["A"],
    "control_passes_iff_false": True,
}

# NC2: swap definition A for definition B in the comparison and show the
#      LoCoMo block cell (where A and B diverge by 0.206) stops matching.
nc["NC2_definition_swap_detected"] = {
    "doc_A_locomo_block": DOC_TABLE[("LoCoMo", "block")][0],
    "value_if_B_were_substituted": repr(tables["LoCoMo"]["block"]["B"]),
    "would_match": float(DOC_TABLE[("LoCoMo", "block")][0]) == tables["LoCoMo"]["block"]["B"],
    "control_passes_iff_false": True,
}

# NC3: recompute A using only 9 of the 10 seeds and show it stops matching.
r3 = compute(m, seeds=SEEDS[:9])
nc["NC3_wrong_seed_panel_detected"] = {
    "A_nine_seeds": repr(r3["full"]["A"]),
    "would_match": float(DOC_TABLE[("LoCoMo", "full")][0]) == r3["full"]["A"],
    "control_passes_iff_false": True,
}

# NC4: a deliberately wrong document value must be flagged as non-matching.
nc["NC4_wrong_doc_value_detected"] = {
    "fake_doc_A": "0.7271861342884778",
    "matches_recomputed": float("0.7271861342884778") == tables["LoCoMo"]["full"]["A"],
    "control_passes_iff_false": True,
}

OUT.write_text(json.dumps(report, indent=2))

# ---- console summary ---------------------------------------------------------
print("python:", sys.version.split()[0])
for bench in ("LoCoMo", "LongMemEval"):
    t = tables[bench]
    print(f"\n[{bench}] rows={t['rows']} questions={t['questions']} "
          f"cells={t['cells']} cell_sizes={t['cell_sizes']} "
          f"native_seed_invariant={t['native_seed_invariant']}")
    for arm in ("full", "block"):
        print(f"   {arm:5s} A={t[arm]['A']!r}  B={t[arm]['B']!r}")
        print(f"         summary_B={t['summary_frac_'+arm+'_B']!r}  "
              f"B_matches_summary={t[arm]['B']==t['summary_frac_'+arm+'_B']}")
        sA = sum(t['summary_frac_'+arm+'_per_seed'])/10
        print(f"         A_from_summary_per_seed={sA!r}  A_matches={t[arm]['A']==sA}")

print("\n--- comparison to decision document table ---")
for c in comparisons:
    print(f"{c['benchmark']:12s} {c['arm']:5s} "
          f"A_bit={c['A_bitwise_equal']} (gap {c['A_ulp_gap']:.3e})  "
          f"B_bit={c['B_bitwise_equal']} (gap {c['B_ulp_gap']:.3e})  "
          f"diff_bit={c['diff_bitwise_equal']} (gap {c['diff_gap']:.3e})  "
          f"docdiff==docA-docB: {c['doc_diff_equals_doc_A_minus_doc_B']} "
          f"(off by {c['doc_diff_minus_docAminusdocB']:.3e})")

print("\n--- negative controls (each must be False under 'would/still match') ---")
for k, v in nc.items():
    print(" ", k, json.dumps({kk: vv for kk, vv in v.items() if kk != 'control_passes_iff_false'}))
