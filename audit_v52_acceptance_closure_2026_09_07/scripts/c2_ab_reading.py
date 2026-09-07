"""C2 — does the A/B ruling follow from the preregistration text?

Three separable questions, each answered from bytes:
  (a) does section 7 support A as the natural reading?
  (b) is the converse claim true - does section 7 nowhere describe collapsing
      arms across seeds before forming the ratio?
  (c) is the decision's reasoning section outcome-free, as it asserts?

The auditor's own reading is recorded in the report; this script supplies only
the byte facts that reading rests on, plus negative controls.
"""
import json, re, subprocess, sys
from pathlib import Path

MAIN = "ed2b2f74347da6be68beae2c22d5c3d22992f1a3"
RESEARCH = "0c9916bd7786d7ddb332f5b6da3d96d61a6223f0"
OUT = Path(sys.argv[1])


def show(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True,
                          check=True).stdout.decode("utf8")


prereg = show(RESEARCH, "research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md")
decision = show(MAIN, "docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md")

# ---- isolate section 7 of the preregistration --------------------------------
s7 = prereg.split("\n## 7. Primary estimand")[1].split("\n## 8.")[0]
s9 = prereg.split("\n## 9. What each outcome")[1].split("\n## 10.")[0]

R = {"section_7_bytes": len(s7), "section_9_bytes": len(s9)}

# (a) the three textual facts the ruling rests on -----------------------------
R["textual_facts"] = {
    "fact_1_governing_per_seed_clause": {
        "claim": "frac_arm is defined per rotation seed; the formulas sit under that clause",
        "clause_text_present": "For each dataset independently, per rotation seed, paired at the question level:" in s7,
        "clause_precedes_formulas": (s7.index("per rotation seed") < s7.index("frac_full  =")),
        "clause_is_bold_in_source": "**per rotation seed**" in s7,
        "clause_is_bold_in_decision_quote": "**per rotation seed**" in decision,
    },
    "fact_2_bands_on_seed_panel_mean": {
        "claim": "the bands are applied to the seed-panel mean",
        "text_present": "bands on the seed-panel mean, applied per arm" in s7,
        "nearest_defined_quantity_before_it": "frac_arm" if s7.rindex("frac_arm", 0, s7.index("seed-panel mean")) else None,
        "any_other_quantity_defined_in_s7": sorted(set(re.findall(r"`(frac_full|frac_block|frac_arm|frac|I_frac|delta_full|delta_block)`", s7))),
    },
    "fact_3_per_seed_dispersion_of_denominators": {
        "claim": "denominators must be reported with their per-seed dispersion, so a per-seed denominator exists",
        "text_present": "must be reported with their per-seed dispersion" in s7,
        "denominators_measured_inside": "Both denominators are measured **inside this experiment**" in s7,
    },
}

# (b) the converse claim: does section 7 anywhere describe collapsing across seeds?
COLLAPSE_PAT = re.compile(
    r"(mean|average|averag|aggregate|pool|collaps|combin)[a-z]*\s+(the\s+)?(arms?|across\s+seeds?|"
    r"over\s+seeds?|seed[- ]mean)|seed[- ]mean\s+(gain|loss)|before\s+forming\s+the\s+ratio", re.I)
R["converse_claim"] = {
    "claim": "section 7 nowhere describes averaging each arm across seeds before forming the ratio",
    "matches_in_section_7": [m.group(0) for m in COLLAPSE_PAT.finditer(s7)],
    "matches_in_whole_preregistration": [m.group(0) for m in COLLAPSE_PAT.finditer(prereg)],
    "phrase_seed_panel_mean_occurrences_in_prereg": len(re.findall(r"seed-panel mean", prereg)),
    "phrase_seed_mean_occurrences_in_prereg": len(re.findall(r"seed-mean", prereg)),
    "section_8_reporting_requirement": [ln.strip() for ln in prereg.split("\n")
                                        if "seed-panel mean" in ln],
}

# (c) is the decision's reasoning outcome-free? --------------------------------
sec2 = decision.split("\n## 2. Decision — A versus B")[1].split("\n## 3.")[0]
reasoning = sec2.split("### 2.4")[0]           # 2.1 What section 7 says + 2.2 + 2.3 Ruling
correction = "### 2.4" + sec2.split("### 2.4")[1]
NUM = re.compile(r"(?<![\w.])\d+\.\d+")
R["outcome_free_check"] = {
    "assertion_in_document": "no outcome value appears in this section's reasoning" in decision,
    "decimal_numbers_in_2_1_to_2_3": sorted(set(NUM.findall(reasoning))),
    "decimal_numbers_in_2_4_correction": sorted(set(NUM.findall(correction)))[:12],
    "band_numbers_elided_from_the_s7_quote": ("0.70" not in reasoning and "0.20" not in reasoning),
    "quote_uses_an_elision_marker": "applied per arm: …" in reasoning,
    "auditor_note": ("2.1-2.3, the derivation, carry no outcome value. 2.4 is inside section 2 and "
                     "does carry the A/B values; it is labelled a presentational correction demanded "
                     "by the Head Researcher and is not part of the derivation."),
}

# ---- NEGATIVE CONTROLS -------------------------------------------------------
nc = {}
# NC1: the collapse-pattern must fire on text that DOES describe definition B
b_text = ("Average each arm across the seed panel, then form the ratio of the seed-mean gain to the "
          "seed-mean loss before forming the ratio.")
nc["NC_C2_collapse_pattern_can_fire"] = {
    "synthetic_text_describing_B": b_text,
    "fires": [m.group(0) for m in COLLAPSE_PAT.finditer(b_text)],
    "control_passes_iff_nonempty": True,
}
# NC2: the outcome-value detector must fire on a synthetic reasoning section
nc["NC_C2_number_detector_can_fire"] = {
    "synthetic": "A is the natural reading because A = 0.7271861342884777 and B = 0.7261069075901362.",
    "fires": NUM.findall("A is the natural reading because A = 0.7271861342884777 and B = 0.7261069075901362."),
    "control_passes_iff_nonempty": True,
}
# NC3: fact-presence checks must fail for a clause that is not in section 7
nc["NC_C2_fact_check_can_fail"] = {
    "fake_clause": "For each dataset independently, per archive, paired at the question level:",
    "present": "For each dataset independently, per archive, paired at the question level:" in s7,
    "control_passes_iff_false": True,
}
R["negative_controls"] = nc

OUT.write_text(json.dumps(R, indent=2))
print(json.dumps(R, indent=2))
