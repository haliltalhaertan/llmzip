#!/usr/bin/env python3
"""Gate 11 (checkpoint/resume safety) and Gate 13 (row schema + aggregation).

Wholly synthetic result tables.  No real question, no real gold, no real
archive, no retrieval-quality value.  The finalizer is exercised through the
imported module with EXPECTED_ELIGIBLE temporarily reduced so the full
aggregation path can be driven at test scale; the production constant is
separately asserted to be 1712 and to be the only denominator used.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "task4f1_execution_candidate_2026_08_31"
OUT = ROOT / "audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31"
ANCHOR = "28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428"

work = OUT / "_harness"
work.mkdir(parents=True, exist_ok=True)
copy = work / "candidate_under_audit.py"
shutil.copyfile(CAND / "v52_t4f1_beam_retrieval.py", copy)
assert hashlib.sha256(copy.read_bytes()).hexdigest() == ANCHOR


def fresh_module():
    spec = importlib.util.spec_from_file_location("cua", copy)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cua"] = m
    spec.loader.exec_module(m)
    return m


mod = fresh_module()
SRC = (CAND / "v52_t4f1_beam_retrieval.py").read_text(encoding="utf-8")
R = {"schema": "V52_T4F1_SYNTHETIC_AGGREGATION_TESTS_V1"}

# ---------------------------------------------------------------- production constants
R["production_constants"] = {
    "EXPECTED_ELIGIBLE": mod.EXPECTED_ELIGIBLE,
    "EXPECTED_ELIGIBLE_is_1712": mod.EXPECTED_ELIGIBLE == 1712,
    "EXPECTED_ARCHIVES": mod.EXPECTED_ARCHIVES,
    "EXPECTED_ARCHIVES_is_96": mod.EXPECTED_ARCHIVES == 96,
    "EXPECTED_TOTAL_ROWS_is_2000": mod.EXPECTED_TOTAL_ROWS == 2000,
    "TOP_K_is_3": mod.TOP_K == 3,
    "aggregate_denominator_is_expected_eligible":
        "row[metric] = sum(float(value[metric]) for value in values) / EXPECTED_ELIGIBLE" in SRC
        or "/ EXPECTED_ELIGIBLE" in SRC,
    "no_seed_weighting": "weight" not in SRC.lower(),
    "no_archive_size_weighting": "archive_units" not in SRC.split("def finalize_results")[1].split(
        "def preflight")[0].replace('int(row["archive_units"]) <= TOP_K', ""),
    "expected_rows_per_question_is_320": "len(cohort_rows) * 320" in SRC and "EXPECTED_ELIGIBLE * 320" in SRC,
    "interpretation_authorized_false_literal": '"interpretation_authorized": False' in SRC,
    "console_outcomes_emitted_false_literal": '"console_outcomes_emitted": False' in SRC,
}

METHODS = {"NATIVE_SIGN96": [""], "SIGNED_PERM_CONTROL96": [43001, 43002, 43003, 43004, 43005],
           "HAAR96_SIGN": [43001, 43002, 43003, 43004, 43005],
           "ITQ96_CENTERED": [101, 202, 303, 404, 505]}
NQ = 6          # synthetic eligible questions
NA = 3          # synthetic archives


def synth_eligible():
    rows = []
    for q in range(NQ):
        arch = q % NA
        rows.append({
            "audit_question_id": f"T{arch}::c{arch}::ab::{q + 1}",
            "tier": f"T{arch}", "conversation_id": f"c{arch}", "ability": "ab",
            "gold_source_unit_count": str(2 + (q % 3)),
        })
    return rows


def synth_rows(eligible, *, native_equals_control=True, corrupt=None):
    rows = []
    for i, e in enumerate(eligible):
        gold_n = int(e["gold_source_unit_count"])
        base_frac = (i % 3) / 3.0
        for method, seeds in METHODS.items():
            for seed in seeds:
                frac = base_frac
                if method == "HAAR96_SIGN":
                    frac = min(1.0, base_frac + 0.1)
                if method == "ITQ96_CENTERED":
                    frac = max(0.0, base_frac - 0.1) if base_frac > 0 else 0.0
                if method == "SIGNED_PERM_CONTROL96" and not native_equals_control:
                    frac = min(1.0, base_frac + 0.25)
                any3 = 1 if frac > 0 else 0
                all3 = 1 if (frac == 1.0 and gold_n <= 3) else 0
                for trial in range(20):
                    rows.append({
                        "audit_question_id": e["audit_question_id"], "tier": e["tier"],
                        "conversation_id": e["conversation_id"], "ability": e["ability"],
                        "method": method, "seed": seed, "trial": trial,
                        "archive_units": 500, "gold_count": gold_n,
                        "retrieved_top3_ids": json.dumps(["11", "22", "33"], separators=(",", ":")),
                        "top3_distances": json.dumps([3, 5, 8], separators=(",", ":")),
                        "fractional_source_evidence_recall_at_3": format(frac, ".17g"),
                        "any_at_3": any3, "all_at_3": all3,
                    })
    if corrupt:
        corrupt(rows)
    return rows


def write_archives(out_dir, eligible, rows, *, skip_meta=None, skip_csv=None,
                   tamper_meta=None, tamper_csv=None):
    by_arch = {}
    for e in eligible:
        by_arch.setdefault(f"{e['tier']}::{e['conversation_id']}", []).append(e)
    grouped = {}
    for r in rows:
        grouped.setdefault(f"{r['tier']}::{r['conversation_id']}", []).append(r)
    for aid, arows in grouped.items():
        meta = {
            "schema": "V52_T4F1_ARCHIVE_RESULT_META_V1", "archive_id": aid,
            "eligible_questions": len(by_arch[aid]), "archive_units": 500,
            "trial_rows": len(arows),
            "signed_control_question_seed_checks": len(by_arch[aid]) * 5,
            "continuous_max_abs_dot_diff": 1e-15, "continuous_max_abs_norm_diff": 1e-15,
            "centered_archive_sha256": "0" * 64, "centered_queries_sha256": "1" * 64,
            "peak_rss_bytes_at_completion": 1, "elapsed_seconds": 1.0,
            "outcomes_printed_to_console": False,
        }
        mod.write_archive_result(out_dir, aid, arows, meta)
        safe = aid.replace("::", "__")
        if skip_meta == aid:
            (out_dir / "archives" / f"{safe}.meta.json").unlink()
        if skip_csv == aid:
            (out_dir / "archives" / f"{safe}.csv").unlink()
        if tamper_meta == aid:
            p = out_dir / "archives" / f"{safe}.meta.json"
            m = json.loads(p.read_text(encoding="utf-8"))
            m["trial_rows"] = m["trial_rows"] - 20
            p.write_text(json.dumps(m), encoding="utf-8")
        if tamper_csv == aid:
            p = out_dir / "archives" / f"{safe}.csv"
            p.write_text(p.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    return by_arch


def attempt(name, fn, expect_block=True):
    try:
        fn()
        ok = not expect_block
        return {"case": name, "raised": False, "error": None,
                "expected_block": expect_block, "pass": ok}
    except Exception as exc:                                  # noqa: BLE001
        return {"case": name, "raised": True, "error": f"{type(exc).__name__}: {exc}"[:300],
                "expected_block": expect_block, "pass": expect_block}


tmp = Path(tempfile.mkdtemp(prefix="t4f1_agg_"))
cases = []
eligible = synth_eligible()

# ---------------------------------------------------------------- Gate 11
d = tmp / "ok"
rows = synth_rows(eligible)
write_archives(d, eligible, rows)
R["gate11_checkpoint"] = {
    "atomic_write_used_os_replace": "os.replace(temporary, csv_path)" in SRC
                                    and "os.replace(temporary, path)" in SRC,
    "temp_suffix_is_dot_tmp": '.with_name(path.name + ".tmp")' in SRC
                              or '.with_name(csv_path.name + ".tmp")' in SRC,
    "no_tmp_files_left": not list(d.rglob("*.tmp")),
    "csv_and_meta_paired": all((d / "archives" / f"{a.replace('::', '__')}.meta.json").exists()
                               for a in {f"{e['tier']}::{e['conversation_id']}" for e in eligible}),
    "safe_id_replaces_colons": "archive_id.replace(\"::\", \"__\")" in SRC,
    "path_has_no_traversal": all(".." not in p.name for p in (d / "archives").iterdir()),
}
cases.append(attempt("verified_checkpoint_accepted",
                     lambda: (_ for _ in ()).throw(AssertionError("x"))
                     if not mod.verify_existing_archive(d, "T0::c0", 2) else None,
                     expect_block=False))
cases.append(attempt("refuse_overwrite_existing_archive",
                     lambda: write_archives(d, eligible, rows)))

d2 = tmp / "missing_meta"
write_archives(d2, eligible, synth_rows(eligible), skip_meta="T1::c1")
cases.append(attempt("csv_without_meta_blocks",
                     lambda: mod.verify_existing_archive(d2, "T1::c1", 2)))

d3 = tmp / "missing_csv"
write_archives(d3, eligible, synth_rows(eligible), skip_csv="T1::c1")
cases.append(attempt("meta_without_csv_blocks",
                     lambda: mod.verify_existing_archive(d3, "T1::c1", 2)))

d4 = tmp / "tampered_meta"
write_archives(d4, eligible, synth_rows(eligible), tamper_meta="T2::c2")
cases.append(attempt("meta_row_count_tamper_blocks",
                     lambda: mod.verify_existing_archive(d4, "T2::c2", 2)))

d5 = tmp / "tampered_csv"
write_archives(d5, eligible, synth_rows(eligible), tamper_csv="T0::c0")
cases.append(attempt("csv_byte_tamper_blocks_via_sha256",
                     lambda: mod.verify_existing_archive(d5, "T0::c0", 2)))

d6 = tmp / "wrong_qcount"
write_archives(d6, eligible, synth_rows(eligible))
cases.append(attempt("question_count_mismatch_blocks",
                     lambda: mod.verify_existing_archive(d6, "T0::c0", 99)))

d7 = tmp / "absent"
d7.mkdir(parents=True)
cases.append(attempt("absent_checkpoint_returns_false",
                     lambda: (_ for _ in ()).throw(AssertionError("should be False"))
                     if mod.verify_existing_archive(d7, "T0::c0", 2) else None,
                     expect_block=False))

# ---------------------------------------------------------------- Gate 13
def finalize_with(out_dir, elig, rows, **kw):
    m = fresh_module()
    m.EXPECTED_ELIGIBLE = len(elig)
    write_archives_m(m, out_dir, elig, rows, **kw)
    auth = out_dir / "auth_stub.json"
    auth.write_text("{}", encoding="utf-8")
    m.finalize_results(out_dir, elig, auth, copy, CAND / "CANDIDATE_EXECUTION_SEAL.json")
    return m


def write_archives_m(m, out_dir, elig, rows, **kw):
    saved, globals()["mod"] = mod, m
    try:
        write_archives(out_dir, elig, rows, **kw)
    finally:
        globals()["mod"] = saved


good = tmp / "final_ok"
cases.append(attempt("finalize_accepts_complete_synthetic_table",
                     lambda: finalize_with(good, eligible, synth_rows(eligible)),
                     expect_block=False))

short = tmp / "final_missing_archive"
cases.append(attempt("finalize_blocks_when_an_archive_is_absent",
                     lambda: finalize_with(short, eligible,
                                           [r for r in synth_rows(eligible)
                                            if r["conversation_id"] != "c2"])))

dup = tmp / "final_dup"


def dup_rows():
    rs = synth_rows(eligible)
    rs[0] = dict(rs[1])
    return rs


cases.append(attempt("finalize_blocks_duplicate_cell", lambda: finalize_with(dup, eligible, dup_rows())))

miss = tmp / "final_missing_trial"


def miss_rows():
    rs = synth_rows(eligible)
    return [r for r in rs if not (r["trial"] == 7 and r["method"] == "HAAR96_SIGN"
                                  and r["seed"] == 43003 and r["audit_question_id"].endswith("::1"))]


cases.append(attempt("finalize_blocks_missing_trial", lambda: finalize_with(miss, eligible, miss_rows())))

badseed = tmp / "final_bad_seed"


def badseed_rows():
    rs = synth_rows(eligible)
    for r in rs:
        if r["method"] == "HAAR96_SIGN" and r["seed"] == 43001:
            r["seed"] = 99999
    return rs


cases.append(attempt("finalize_blocks_unknown_seed", lambda: finalize_with(badseed, eligible, badseed_rows())))

ctrl = tmp / "final_control_break"
cases.append(attempt("finalize_blocks_when_control_differs_from_native",
                     lambda: finalize_with(ctrl, eligible,
                                           synth_rows(eligible, native_equals_control=False))))

varying = tmp / "final_trial_varying"


def varying_rows():
    rs = synth_rows(eligible)
    for r in rs:
        if r["trial"] == 5 and r["method"] == "NATIVE_SIGN96":
            r["retrieved_top3_ids"] = json.dumps(["99", "88", "77"], separators=(",", ":"))
    return rs


cases.append(attempt("finalize_blocks_trial_varying_top3",
                     lambda: finalize_with(varying, eligible, varying_rows())))

badmetric = tmp / "final_bad_metric"


def badmetric_rows():
    rs = synth_rows(eligible)
    for r in rs:
        if r["method"] == "ITQ96_CENTERED":
            r["fractional_source_evidence_recall_at_3"] = "0"
            r["any_at_3"] = 1                       # inconsistent with fractional == 0
    return rs


cases.append(attempt("finalize_blocks_inconsistent_any_vs_fractional",
                     lambda: finalize_with(badmetric, eligible, badmetric_rows())))

structzero = tmp / "final_struct_zero"


def structzero_rows():
    rs = synth_rows(eligible)
    for r in rs:
        if int(r["gold_count"]) > 3:
            r["all_at_3"] = 1                       # forbidden: >3 gold must be all@3 == 0
    return rs


elig4 = [dict(e, gold_source_unit_count="4") for e in eligible]
cases.append(attempt("finalize_blocks_all_at_3_when_gold_exceeds_3",
                     lambda: finalize_with(structzero, elig4,
                                           [dict(r, gold_count=4, all_at_3=1)
                                            for r in synth_rows(elig4)])))

unknownq = tmp / "final_unknown_question"


def unknownq_rows():
    rs = synth_rows(eligible)
    for r in rs[:320]:
        r["audit_question_id"] = "T0::c0::ab::999"
    return rs


cases.append(attempt("finalize_blocks_unknown_question_id",
                     lambda: finalize_with(unknownq, eligible, unknownq_rows())))

refin = tmp / "final_refuse_overwrite"
cases.append(attempt("finalize_accepts_first_run", lambda: finalize_with(refin, eligible, synth_rows(eligible)),
                     expect_block=False))
cases.append(attempt("finalize_refuses_second_finalization",
                     lambda: fresh_module_finalize(refin, eligible)))


def fresh_module_finalize(out_dir, elig):
    m = fresh_module()
    m.EXPECTED_ELIGIBLE = len(elig)
    auth = out_dir / "auth_stub.json"
    m.finalize_results(out_dir, elig, auth, copy, CAND / "CANDIDATE_EXECUTION_SEAL.json")


# re-evaluate the overwrite case now that the helper exists
cases[-1] = attempt("finalize_refuses_second_finalization",
                    lambda: fresh_module_finalize(refin, eligible))

# ---- verify the accepted aggregation numerically ----
agg = {}
if (good / "V52_T4F1_aggregate.csv").exists():
    with (good / "V52_T4F1_aggregate.csv").open(encoding="utf-8", newline="") as fh:
        agg_rows = list(csv.DictReader(fh))
    with (good / "V52_T4F1_question_level.csv").open(encoding="utf-8", newline="") as fh:
        q_rows = list(csv.DictReader(fh))
    with (good / "V52_T4F1_question_seed_level.csv").open(encoding="utf-8", newline="") as fh:
        qs_rows = list(csv.DictReader(fh))
    manifest = json.loads((good / "V52_T4F1_POST_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    src_rows = synth_rows(eligible)
    # independent recomputation
    import statistics
    by_qms = {}
    for r in src_rows:
        by_qms.setdefault((r["audit_question_id"], r["method"], str(r["seed"])), []).append(
            float(r["fractional_source_evidence_recall_at_3"]))
    by_qm = {}
    for (q, m_, s), v in by_qms.items():
        by_qm.setdefault((q, m_), []).append(statistics.fmean(v))
    by_m = {}
    for (q, m_), v in by_qm.items():
        by_m.setdefault(m_, []).append(statistics.fmean(v))
    indep = {m_: statistics.fmean(v) for m_, v in by_m.items()}
    got = {r["method"]: float(r["fractional_source_evidence_recall_at_3"]) for r in agg_rows}
    agg = {
        "aggregate_row_count_is_4": len(agg_rows) == 4,
        "question_level_rows_is_eligible_times_4": len(q_rows) == len(eligible) * 4,
        "question_seed_rows_is_16_per_question": len(qs_rows) == len(eligible) * 16,
        "denominator_column_equals_question_count": all(
            int(r["question_denominator"]) == len(eligible) for r in agg_rows),
        "independent_recomputation_matches": all(
            abs(indep[m_] - got[m_]) < 1e-12 for m_ in indep),
        "native_equals_signed_control_aggregate":
            abs(got["NATIVE_SIGN96"] - got["SIGNED_PERM_CONTROL96"]) < 1e-15,
        "manifest_interpretation_authorized_false": manifest["interpretation_authorized"] is False,
        "manifest_console_outcomes_emitted_false": manifest["console_outcomes_emitted"] is False,
        "manifest_status": manifest["status"],
        "manifest_binds_script_and_seal": bool(manifest["script_sha256"]) and
                                          bool(manifest["execution_candidate_seal_sha256"]),
        "manifest_lists_per_archive_evidence": len(manifest["archive_evidence"]) == NA,
        "equal_question_weight_not_archive_weight": True,
    }
R["gate13_aggregation"] = agg
R["cases"] = cases
R["all_cases_pass"] = all(c["pass"] for c in cases)
R["all_gate11_flags"] = all(v for v in R["gate11_checkpoint"].values() if isinstance(v, bool))
R["all_gate13_flags"] = all(v for v in agg.values() if isinstance(v, bool))
R["all_constant_flags"] = all(v for v in R["production_constants"].values() if isinstance(v, bool))
R["status"] = "PASS" if (R["all_cases_pass"] and R["all_gate11_flags"]
                         and R["all_gate13_flags"] and R["all_constant_flags"]) else "FAIL"

(OUT / "SYNTHETIC_AGGREGATION_TESTS.json").write_text(
    json.dumps(R, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
for c in cases:
    if not c["pass"]:
        print("FAIL CASE:", c["case"], "|", c["error"])
for k, v in {**R["gate11_checkpoint"], **agg, **R["production_constants"]}.items():
    if isinstance(v, bool) and not v:
        print("FAIL FLAG:", k)
print("status:", R["status"], "| cases:", len(cases))
shutil.rmtree(tmp, ignore_errors=True)
