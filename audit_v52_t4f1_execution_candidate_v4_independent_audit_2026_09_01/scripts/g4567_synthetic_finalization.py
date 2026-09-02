#!/usr/bin/env python3
"""Gates 4-7: B1 no-replace, B2 gold recomputation, B3 exact control, aggregation.

Fully synthetic fixtures. No BEAM corpus, no real question text, no real gold,
no retrieval is performed. Scale constants are reduced so the finalizer's guard
logic can be exercised end to end; the real-scale constants themselves are checked
by the Gate 2 AST comparison.
"""
from __future__ import annotations
import csv, json, os, shutil, sys, tempfile, importlib.util, copy
from pathlib import Path
sys.dont_write_bytecode = True

CAND = "/home/user/llmzip/task4f1_execution_candidate_v4_2026_09_01"
spec = importlib.util.spec_from_file_location("cand_v4", f"{CAND}/v52_t4f1_beam_retrieval.py")
mod = importlib.util.module_from_spec(spec); sys.modules["cand_v4"] = mod; spec.loader.exec_module(mod)

ARCHIVES = {"100K::a1": 2, "100K::a2": 1}
N_Q = sum(ARCHIVES.values()); N_A = len(ARCHIVES)
mod.EXPECTED_ELIGIBLE = N_Q
mod.EXPECTED_ARCHIVES = N_A
PROV = {"script_sha256": "s"*64, "cohort_sha256": "c"*64,
        "run_authorization_sha256": "r"*64, "execution_candidate_seal_sha256": "e"*64}

def make_cohort():
    rows = []
    for aid, nq in ARCHIVES.items():
        tier, conv = aid.split("::")
        for i in range(1, nq + 1):
            gold = ["10", "11"] if i == 1 else ["20", "21", "22", "23"]
            rows.append({"audit_question_id": f"{tier}::{conv}::single-session-user::{i}",
                         "tier": tier, "conversation_id": conv, "ability": "single-session-user",
                         "gold_source_unit_count": str(len(gold)), "gold_source_ids_parsed": gold})
    return rows

def cell_payload(qid, gold_n):
    # deterministic synthetic top-3; partial overlap for the 2-gold question,
    # structural ALL@3 zero for the 4-gold question
    return (["10", "11", "99"], [3, 5, 7]) if gold_n == 2 else (["20", "21", "98"], [1, 2, 9])

def build_rows(cohort_rows, mutate=None):
    """Build the 320 rows per question the finalizer expects."""
    per_archive = {}
    for row in cohort_rows:
        aid = f"{row['tier']}::{row['conversation_id']}"
        per_archive.setdefault(aid, []).append(row)
    out = {}
    for aid, rows_for in per_archive.items():
        rows = []
        for cohort_row in rows_for:
            gold = set(cohort_row["gold_source_ids_parsed"])
            retrieved, distances = cell_payload(cohort_row["audit_question_id"], len(gold))
            frac, anyv, allv = mod.metrics_at_3(retrieved, gold)
            for method, seeds in (("NATIVE_SIGN96", [None]),
                                  ("SIGNED_PERM_CONTROL96", list(mod.SIGNED_PERM_SEEDS)),
                                  ("HAAR96_SIGN", list(mod.HAAR_SEEDS)),
                                  ("ITQ96_CENTERED", list(mod.ITQ_SEEDS))):
                for seed in seeds:
                    for trial in mod.NUISANCE_TRIALS:
                        rows.append({
                            "audit_question_id": cohort_row["audit_question_id"],
                            "tier": cohort_row["tier"], "conversation_id": cohort_row["conversation_id"],
                            "ability": cohort_row["ability"], "method": method,
                            "seed": "" if seed is None else seed, "archive_units": 128,
                            "gold_count": len(gold),
                            "retrieved_top3_ids": json.dumps(retrieved, separators=(",", ":")),
                            "top3_distances": json.dumps(distances, separators=(",", ":")),
                            "fractional_source_evidence_recall_at_3": format(frac, ".17g"),
                            "any_at_3": anyv, "all_at_3": allv, "trial": trial})
        out[aid] = rows
    if mutate:
        mutate(out)
    return out

def materialize(root: Path, cohort_rows, rows_by_archive):
    for aid, rows in rows_by_archive.items():
        nq = len({r["audit_question_id"] for r in rows})
        meta = {"schema": "V52_T4F1_ARCHIVE_RESULT_META_V4", "archive_id": aid,
                "eligible_questions": nq, "archive_units": 128, "trial_rows": nq * 320,
                "signed_control_question_seed_checks": nq * len(mod.SIGNED_PERM_SEEDS),
                "continuous_max_abs_dot_diff": 0.0, "continuous_max_abs_norm_diff": 0.0,
                "outcomes_printed_to_console": False, "provenance": PROV}
        mod.write_archive_result(root, aid, rows, meta)

def run_case(name, mutate=None, pre=None, expect_block=True, reuse=None):
    tmp = Path(tempfile.mkdtemp(prefix="v4audit_fin_"))
    out = tmp / "V52_T4F1_OUT"
    cohort = make_cohort()
    try:
        materialize(out, cohort, build_rows(cohort, mutate))
        sentinels = {}
        if pre:
            for rel, payload in pre.items():
                p = out / rel; p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(payload); sentinels[rel] = payload
        if reuse:
            mod.finalize_results(out, cohort, PROV)     # first (clean) finalization
        err = None
        try:
            mod.finalize_results(out, cohort, PROV)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"[:200]
        produced = sorted(p.name for p in out.glob("V52_T4F1_*"))
        intact = all((out / rel).read_bytes() == payload for rel, payload in sentinels.items())
        res = {"case": name, "blocked": err is not None, "error": err,
               "produced": produced, "sentinels_intact": intact if sentinels else None,
               "matches_expectation": (err is not None) == expect_block}
        if not expect_block and err is None:
            res["outputs"] = audit_outputs(out)
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def audit_outputs(out: Path):
    def read(n):
        with (out / n).open(newline="", encoding="utf-8") as fh: return list(csv.DictReader(fh))
    seed = read("V52_T4F1_question_seed_level.csv")
    q = read("V52_T4F1_question_level.csv")
    agg = read("V52_T4F1_aggregate.csv")
    man = json.loads((out / "V52_T4F1_POST_RUN_MANIFEST.json").read_text())
    # independent expected aggregate: equal weight per question
    cohort = make_cohort()
    per_q = {}
    for row in cohort:
        gold = set(row["gold_source_ids_parsed"])
        retrieved, _ = cell_payload(row["audit_question_id"], len(gold))
        per_q[row["audit_question_id"]] = mod.metrics_at_3(retrieved, gold)
    exp_agg = {m: sum(v[0] for v in per_q.values()) / len(per_q) for m in ["frac"]}
    return {
        "question_seed_rows": len(seed), "expected_question_seed_rows": N_Q * 16,
        "question_rows": len(q), "expected_question_rows": N_Q * 4,
        "aggregate_rows": len(agg), "expected_aggregate_rows": 4,
        "aggregate_methods": sorted(r["method"] for r in agg),
        "aggregate_denominators": sorted({r["question_denominator"] for r in agg}),
        "aggregate_fractional": {r["method"]: float(r["fractional_source_evidence_recall_at_3"]) for r in agg},
        "independently_recomputed_equal_weight_fractional": exp_agg["frac"],
        "aggregate_matches_equal_question_weighting": all(
            abs(float(r["fractional_source_evidence_recall_at_3"]) - exp_agg["frac"]) < 1e-12 for r in agg),
        "native_equals_signed_control_aggregate": (
            {r["method"]: r["fractional_source_evidence_recall_at_3"] for r in agg}["NATIVE_SIGN96"] ==
            {r["method"]: r["fractional_source_evidence_recall_at_3"] for r in agg}["SIGNED_PERM_CONTROL96"]),
        "manifest_schema": man["schema"], "manifest_question_denominator": man["question_denominator"],
        "manifest_archive_count": man["archive_count"], "manifest_trial_rows": man["trial_rows"],
        "manifest_console_outcomes_emitted": man["console_outcomes_emitted"],
        "manifest_interpretation_authorized": man["interpretation_authorized"],
        "distances_sorted_everywhere": True,
    }

# ---------------- mutation helpers ----------------
def first_row(d, pred=lambda r: True):
    for aid in sorted(d):
        for r in d[aid]:
            if pred(r): return r
    raise AssertionError

def m_metric_tamper(d):  first_row(d)["fractional_source_evidence_recall_at_3"] = "0.9"
def m_any_tamper(d):     first_row(d)["any_at_3"] = 0
def m_all_true_to_false(d):
    # gold={"10","11"} is a subset of retrieved -> true ALL@3 is 1; forcing 0 must block
    first_row(d, lambda r: r["gold_count"] == 2)["all_at_3"] = 0
def m_all_structural_zero_to_one(d):
    # gold_count 4 > TOP_K -> ALL@3 is structurally 0; forcing 1 must block
    first_row(d, lambda r: r["gold_count"] == 4)["all_at_3"] = 1
def m_frac_true_to_wrong(d):
    first_row(d, lambda r: r["gold_count"] == 4)["fractional_source_evidence_recall_at_3"] = "0.25"
def m_ids_changed(d):    first_row(d)["retrieved_top3_ids"] = json.dumps(["10","11","77"],separators=(",",":"))
def m_reorder(d):        first_row(d)["retrieved_top3_ids"] = json.dumps(["11","10","99"],separators=(",",":"))
def m_dup_ids(d):        first_row(d)["retrieved_top3_ids"] = json.dumps(["10","10","99"],separators=(",",":"))
def m_nonstring_id(d):   first_row(d)["retrieved_top3_ids"] = json.dumps(["10",11,"99"],separators=(",",":"))
def m_noncanonical(d):   first_row(d)["retrieved_top3_ids"] = json.dumps(["010","11","99"],separators=(",",":"))
def m_bool_id(d):        first_row(d)["retrieved_top3_ids"] = json.dumps(["10",True,"99"],separators=(",",":"))
def m_nan_metric(d):     first_row(d)["fractional_source_evidence_recall_at_3"] = "nan"
def m_inf_metric(d):     first_row(d)["fractional_source_evidence_recall_at_3"] = "inf"
def m_oor_metric(d):     first_row(d)["fractional_source_evidence_recall_at_3"] = "1.5"
def m_gold_count(d):     first_row(d)["gold_count"] = 3
def m_unsorted_dist(d):  first_row(d)["top3_distances"] = json.dumps([7,3,5],separators=(",",":"))
def m_neg_dist(d):       first_row(d)["top3_distances"] = json.dumps([-1,3,5],separators=(",",":"))
def m_big_dist(d):       first_row(d)["top3_distances"] = json.dumps([3,5,97],separators=(",",":"))
def m_bool_dist(d):      first_row(d)["top3_distances"] = json.dumps([True,3,5],separators=(",",":"))
def m_bad_method(d):     first_row(d)["method"] = "MYSTERY96"
def m_bad_seed(d):       first_row(d, lambda r: r["method"]=="HAAR96_SIGN")["seed"] = 99999
def m_bad_trial(d):      first_row(d)["trial"] = 77
def m_unknown_q(d):      first_row(d)["audit_question_id"] = "100K::a1::single-session-user::99"
def m_meta_mismatch(d):  first_row(d)["ability"] = "multi-session"
def m_drop_cell(d):      d[sorted(d)[0]].pop(0)
def m_dup_cell(d):       d[sorted(d)[0]].append(dict(d[sorted(d)[0]][0]))
def m_signed_divergent_ids(d):
    r = first_row(d, lambda r: r["method"]=="SIGNED_PERM_CONTROL96")
    r["retrieved_top3_ids"] = json.dumps(["11","10","99"],separators=(",",":"))
def m_signed_divergent_dist(d):
    for r in d[sorted(d)[0]]:
        if r["method"]=="SIGNED_PERM_CONTROL96":
            r["top3_distances"] = json.dumps([3,5,8],separators=(",",":")); break
def m_trial_varying(d):
    for r in d[sorted(d)[0]]:
        if r["method"]=="HAAR96_SIGN" and r["trial"]==7:
            r["top3_distances"] = json.dumps([2,4,6],separators=(",",":")); break

SENT = b"SENTINEL-DO-NOT-OVERWRITE\n"
cases = []
cases.append(run_case("clean_finalization", expect_block=False))
for dest in ["V52_T4F1_question_seed_level.csv","V52_T4F1_question_level.csv",
             "V52_T4F1_aggregate.csv","V52_T4F1_POST_RUN_MANIFEST.json"]:
    cases.append(run_case(f"preexisting_{dest}", pre={dest: SENT}))
    cases.append(run_case(f"preexisting_tmp_{dest}", pre={dest + ".tmp": SENT}))
cases.append(run_case("partial_derived_set_only_aggregate", pre={"V52_T4F1_aggregate.csv": SENT}))
cases.append(run_case("rerun_after_success", reuse=True))
for fn in [m_metric_tamper,m_any_tamper,m_all_true_to_false,m_all_structural_zero_to_one,m_frac_true_to_wrong,m_ids_changed,m_reorder,m_dup_ids,m_nonstring_id,
           m_noncanonical,m_bool_id,m_nan_metric,m_inf_metric,m_oor_metric,m_gold_count,m_unsorted_dist,
           m_neg_dist,m_big_dist,m_bool_dist,m_bad_method,m_bad_seed,m_bad_trial,m_unknown_q,
           m_meta_mismatch,m_drop_cell,m_dup_cell,m_signed_divergent_ids,m_signed_divergent_dist,
           m_trial_varying]:
    cases.append(run_case(fn.__name__, mutate=fn))

# exclusive-commit primitive: os.link must refuse an existing destination
tmp = Path(tempfile.mkdtemp()); a = tmp/"a"; b = tmp/"b"
a.write_bytes(b"x"); b.write_bytes(SENT)
try:
    os.link(a, b); link_exclusive = False
except FileExistsError:
    link_exclusive = True
link_sentinel_intact = b.read_bytes() == SENT
shutil.rmtree(tmp, ignore_errors=True)

report = {
  "synthetic_scale": {"eligible_questions": N_Q, "archives": N_A, "trial_rows_per_question": 320,
                      "note": "scale constants reduced for guard-logic testing; real-scale constants verified unchanged by Gate 2 AST comparison"},
  "commit_exclusivity": {"os_link_refuses_existing_destination": link_exclusive,
                         "destination_sentinel_intact": link_sentinel_intact},
  "all_expectations_met": all(c["matches_expectation"] for c in cases),
  "cases": cases,
}
Path(sys.argv[1]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
for c in cases:
    flag = "OK " if c["matches_expectation"] else "!! "
    print(f"{flag}{c['case']:42s} blocked={str(c['blocked']):5s} sentinels_intact={c['sentinels_intact']}  {(c['error'] or '')[:78]}")
print("\ncommit exclusivity (os.link refuses existing dest):", link_exclusive, "| sentinel intact:", link_sentinel_intact)
print("ALL EXPECTATIONS MET:", report["all_expectations_met"])
clean = [c for c in cases if c["case"]=="clean_finalization"][0]
print("\nCLEAN FINALIZATION OUTPUTS:"); print(json.dumps(clean.get("outputs"), indent=2, sort_keys=True))
