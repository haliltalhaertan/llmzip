#!/usr/bin/env python3
"""Build task1_RESULTS_extended.json — the frozen Task1 RESULTS.json schema, extended additively.

Preserves every frozen field value; fills D1_gt / zero_mass / D4 for LongMemEval and the whole
locomo block, from the certified regeneration. Every added value carries its source label and the
certification references. LOCAL SESSION — NOT PUSHED.
"""
import json
from pathlib import Path

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
frozen = json.loads((WORK / "harness" / "ref" / "task1_RESULTS.json").read_text())
ext_lme = json.loads((WORK / "regen" / "lme" / "task1_extension_lme.json").read_text())
loc = json.loads((WORK / "regen" / "locomo" / "task1_locoMo_stats.json").read_text())
cert = json.loads((WORK / "regen" / "lme" / "certification_report.json").read_text())
cert_sign = json.loads((WORK / "regen" / "lme" / "code_certification_sign.json").read_text())
itq_path = WORK / "regen" / "lme" / "code_certification_itq.json"
cert_itq = json.loads(itq_path.read_text()) if itq_path.exists() else None

SRC = ("Computed from a certified re-execution of the byte-frozen V52 Task 4C3 producer "
       "(sha256 8dce37b1...) on the canonical dataset (d6f21ea9...); certification: all published "
       "heterogeneity fields reproduce at 0.0 deviation (470/470 questions) and all frozen packed "
       "sign codes are bit-identical (470/470 questions, 231606 documents).")

out = dict(frozen)
out["status"] = ("EXTENDED (LOCAL SESSION, NOT PUSHED) - frozen published statistics preserved; "
                 "missing components computed from certified regeneration")
out["extension"] = {
    "labels": ["[LOCAL SESSION - NOT PUSHED]", "[CERTIFIED REGENERATION]",
               "Strict >0 / zero-mass resolved by measurement (no substitution)."],
    "method": SRC,
    "certification": {
        "statistics_level_max_relative_deviation": 0.0,
        "code_level_sign_doc_packed_bit_exact": cert_sign["sign_doc_packed_bit_exact"],
        "code_level_sign_query_packed_bit_exact": cert_sign["sign_query_packed_bit_exact"],
        "code_level_itq": ({"per_seed_exact": cert_itq["per_seed_exact"], "all_seeds_exact": cert_itq["all_seeds_exact"]}
                           if cert_itq else "PENDING"),
    },
    "artifacts": {
        "extension_lme": "regen/lme/task1_extension_lme.json (+ .csv 470 rows)",
        "certification": "regen/lme/certification_report.json",
        "code_certification_sign": "regen/lme/code_certification_sign.json",
        "code_certification_itq": "regen/lme/code_certification_itq.json" if cert_itq else "(pending)",
        "locomo_stats": "regen/locomo/task1_locoMo_stats.json",
    },
    "independent_recomputation": ("Muse session 01a0970e-db02 (independent executor, frozen functions "
                                  "imported verbatim): all LME means exact; sds and per-archive D4 "
                                  "agree to the last ulp; LoCoMo equal to the last ulp. A later "
                                  "second-party re-execution on a different stack (Muse 01a09725-8449, "
                                  "python 3.14.4 / numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1) "
                                  "reproduced LoCoMo structurally bit-exact and numerically to "
                                  "<=3e-15 absolute. See regen/muse_independent/ and "
                                  "reports/muse_locomo_reval_2026-09-12.md."),
    "intentional_frozen_leaf_updates": [
        {"path": "longmemeval/D1_gt_reason", "from": frozen["longmemeval"].get("D1_gt_reason"),
         "to": None, "why": "reason-for-null string cleared because D1_gt is now computed "
         "(frozen schema: the reason field explains a null value; the null is now filled)"},
        {"path": "longmemeval/D4_reason", "from": frozen["longmemeval"].get("D4_reason"),
         "to": None, "why": "reason-for-null string cleared because D4 is now computed"},
        {"path": "locomo/status", "from": frozen.get("locomo", {}).get("status"),
         "to": "COMPUTED (LOCAL SESSION) - per-conversation native representation regenerated "
               "with counts 10/10 exact vs the frozen transfer proof",
         "why": "LoCoMo diagnostics family now computed from the certified regeneration"},
    ],
}

lme = out["longmemeval"]
lme["D1_gt"] = ext_lme["D1_gt"]
lme["D1_gt_reason"] = None
lme["D1_gt_note"] = "Equal to D1_ge bit-for-bit in every archive: zero_mass == 0.0 everywhere."
lme["zero_mass"] = ext_lme["zero_mass"]
lme["D4"] = {"off_mass": ext_lme["D4_off_mass"], "median_abs": ext_lme["D4_median_abs"],
             "p95_abs": ext_lme["D4_p95_abs"]}
lme["D4_reason"] = None
lme["D4_note"] = "Computed on active coordinates (variance>0; all 96 active in all 470 archives)."
lme["extension_source"] = SRC
# fill per-archive new fields (traceability: consumers may read either this file or the extension JSONs)
ext_by_qid = {r["question_id"]: r for r in ext_lme["archives"]}
filled = 0
for row in lme.get("archives", []):
    qid = row.get("archive_id") or row.get("question_id")
    e = ext_by_qid.get(qid)
    if not e:
        continue
    row["sign_entropy_gt"] = e["sign_entropy_gt"]
    row["zero_mass"] = e["zero_mass"]
    row["correlation_proxy"] = {
        "off_mass": e["corr_off_mass"], "median_abs": e["corr_median_abs"], "p95_abs": e["corr_p95_abs"],
    }
    row["extension_source"] = SRC
    filled += 1
out["extension"]["longmemeval_archives_filled"] = filled

out["locomo"] = {
    "status": "COMPUTED (LOCAL SESSION) - per-conversation native representation regenerated with "
              "counts 10/10 exact vs the frozen transfer proof",
    "archive_count": loc["archive_count"], "dimensions": loc["dimensions"],
    "D1_ge": loc["D1_ge"], "D1_gt": loc["D1_gt"], "zero_mass": loc["zero_mass"],
    "D2_cv_sigma": loc["D2_cv_sigma"],
    "D3_top_variance_fraction": {"16": loc["D3_top16"], "32": loc["D3_top32"], "48": loc["D3_top48"]},
    "D3_ordered_prefix_fraction": {"32": loc["D3_first32"]},
    "D4": {"off_mass": loc["D4_off_mass"], "median_abs": loc["D4_median_abs"], "p95_abs": loc["D4_p95_abs"]},
    "archives": loc["archives"],
    "extension_source": ("Regenerated from the byte-frozen T4D script (== seal sealed_compute_script_sha256) "
                          "on raw locomo10.json (79fa87e9...) + audit layer (manifest 90a4e94c..., 20/20 files)."),
}

out["interpretation"] = frozen["interpretation"] + [
    "Extension values come from a certified regeneration: all previously published functional checks "
    "reproduce and the consumed sign codes are bit-identical; this is not frozen-byte recovery and not "
    "an independent audit.",
    "zero_mass == 0.0 in all 470 LongMemEval and all 10 LoCoMo archives, so the strict >0 form equals "
    "the >=0 form by measurement.",
]

outp = WORK / "regen" / "task1_RESULTS_extended.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print("wrote", outp)
print("itq present:", cert_itq is not None)
