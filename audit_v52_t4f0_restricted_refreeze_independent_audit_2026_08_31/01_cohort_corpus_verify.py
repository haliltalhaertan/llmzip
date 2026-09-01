# V52 T4F0 RESTRICTED-REFREEZE INDEPENDENT AUDIT â€” 01_cohort_corpus_verify.py
# Audit-only. Verifies:
#  (1) cohort CSV internal invariants (2000/1712/exclusions/cardinality/composition)
#  (2) corpus byte-identity: remediation corpus vs pinned-commit clone (SHA256, per file)
#  (3) eligibility recomputed from RAW pinned corpus, row-by-row vs CSV
# No retrieval quality, no ranking, no Native/Haar outcome.
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

CAND = Path(sys.argv[1])          # candidate namespace
CORPUS = Path(sys.argv[2])        # remediation corpus root (contains chats/)
CLONE = Path(sys.argv[3])         # pinned BEAM clone (commit-verified)
RAW = Path(sys.argv[4])           # raw git-blob extraction dir
OUT = Path(sys.argv[5])           # audit output dir

EXPECTED_COHORT_SHA = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"
EXCLUDED = {"1M::5", "1M::26", "1M::33", "1M::34"}
TIERS = ["100K", "500K", "1M", "10M"]


def sha256_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def flatten_source_ids(value):
    vals = []
    def walk(x):
        if isinstance(x, bool):
            raise TypeError("bool")
        if isinstance(x, int):
            vals.append(int(x)); return
        if isinstance(x, list):
            for y in x:
                walk(y)
            return
        if isinstance(x, dict):
            for y in x.values():
                walk(y)
            return
        raise TypeError(type(x).__name__)
    walk(value)
    return list(dict.fromkeys(vals))


def iter_messages(obj):
    if isinstance(obj, dict):
        if {"role", "id", "content"}.issubset(obj.keys()):
            yield obj; return
        for v in obj.values():
            yield from iter_messages(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_messages(v)


result = {"cohort_checks": {}, "corpus_identity": {}, "recomputed_vs_csv": {}}

# ---------------------------------------------------------------- (1) cohort CSV
cohort_path = CAND / "estimand_primary_cohort.csv"
assert sha256_file(cohort_path) == EXPECTED_COHORT_SHA, "cohort digest mismatch"
rows = list(csv.DictReader(cohort_path.open(encoding="utf-8", newline="")))
elig = [r for r in rows if r["primary_evidence_cohort_eligible"] == "True"]
result["cohort_checks"] = {
    "rows": len(rows),
    "eligible": len(elig),
    "eligible_unique_ids": len({r["audit_question_id"] for r in elig}),
    "rows_unique_ids": len({r["audit_question_id"] for r in rows}),
    "eligible_all_exact": all(r["audit_category"] == "EXACT_SOURCE_IDS" for r in elig),
    "eligible_none_abstention": all(r["ability"] != "abstention" for r in elig),
    "eligible_none_excluded_archive": all(
        f"{r['tier']}::{r['conversation_id']}" not in EXCLUDED for r in elig
    ),
    "eligible_all_gold_gt0": all(int(r["gold_source_unit_count"]) > 0 for r in elig),
    "excluded_archive_rows": sorted(
        {f"{r['tier']}::{r['conversation_id']}" for r in rows
         if f"{r['tier']}::{r['conversation_id']}" in EXCLUDED}
    ),
    "cardinality_gt3": sum(1 for r in elig if int(r["gold_source_unit_count"]) > 3),
    "structurally_impossible_all3": sum(
        1 for r in elig if r["all_at_3_structurally_possible"] == "False"
    ),
    "schema_has_no_answer_or_rubric_columns": not (
        {"question", "ideal_answer", "ideal_response", "answer", "rubric",
         "evaluator_output", "outcome"} & set(rows[0].keys())
    ),
}
# eligibility_reason census
result["cohort_checks"]["eligibility_reason_counts"] = dict(
    Counter(r["eligibility_reason"] for r in rows)
)
# cardinality distribution vs summary
card = Counter(int(r["gold_source_unit_count"]) for r in elig)
summary = json.loads((CAND / "estimand_summary.json").read_text(encoding="utf-8"))
dist_match = all(card[int(k)] == v for k, v in summary["gold_cardinality"]["distribution"].items())
result["cohort_checks"]["cardinality_distribution_matches_summary"] = dist_match
# composition table sums
comp = list(csv.DictReader((CAND / "tier_ability_composition.csv").open(encoding="utf-8", newline="")))
result["cohort_checks"]["composition_rows_sum"] = sum(int(r["eligible_questions"]) for r in comp)
comp_map = {f"{r['tier']}.{r['ability']}": int(r["eligible_questions"]) for r in comp}
sum_map = summary["eligible_by_tier_ability"]
result["cohort_checks"]["composition_matches_summary"] = comp_map == sum_map
# CSV gold_source_ids vs gold_source_unit_count
mismatch_cnt = 0
for r in rows:
    ids = json.loads(r["gold_source_ids"])
    if len(set(ids)) != int(r["gold_source_unit_count"]):
        mismatch_cnt += 1
result["cohort_checks"]["gold_ids_vs_count_mismatches"] = mismatch_cnt

# ------------------------------------------------------------ (2) corpus identity
clone_files = {}
for tier in TIERS:
    for p in sorted((CLONE / "chats" / tier).rglob("*")):
        if p.is_file():
            rel = p.relative_to(CLONE).as_posix()
            clone_files[rel] = sha256_file(p)
corpus_files = {}
raw_files = {}
croot = CORPUS / "chats"
for tier in TIERS:
    for p in sorted((croot / tier).rglob("*")):
        if p.is_file():
            rel = p.relative_to(CORPUS).as_posix()
            corpus_files[rel] = sha256_file(p)
    for p in sorted((RAW / "chats" / tier).rglob("*")):
        if p.is_file():
            rel = p.relative_to(RAW).as_posix()
            raw_files[rel] = sha256_file(p)
result["corpus_identity"] = {
    "raw_blob_files": len(raw_files),
    "corpus_files": len(corpus_files),
    "corpus_files_all_byte_identical_to_pinned_raw_blobs": all(
        raw_files.get(k) == v for k, v in corpus_files.items()
    ),
    "corpus_files_missing_in_raw": sorted(set(corpus_files) - set(raw_files))[:10],
    "corpus_files_differing_from_raw": sorted(
        k for k, v in corpus_files.items() if raw_files.get(k) != v
    )[:10],
}

# ------------------------------------------- (3) eligibility recomputed from raw
# (full recomputation uses the commit-verified pinned clone; the remediation
#  corpus only carries the 4 self-test chat.json files - identity-checked above)
rows_by_id = {r["audit_question_id"]: r for r in rows}
recomputed = {}
per_conv = {}
for tier in TIERS:
    for cdir in sorted((p for p in (CLONE / "chats" / tier).iterdir() if p.is_dir()), key=lambda p: (0, int(p.name), '') if p.name.isdigit() else (1, 0, p.name)):
        chat = json.loads((cdir / "chat.json").read_text(encoding="utf-8"))
        idc = Counter(m.get("id") for m in iter_messages(chat))
        per_conv[(tier, cdir.name)] = {
            "unique_archive": all(v == 1 for v in idc.values()),
            "id_counts": idc,
        }
mismatch = []
matched = 0
for tier in TIERS:
    for cdir in sorted((p for p in (CLONE / "chats" / tier).iterdir() if p.is_dir()), key=lambda p: (0, int(p.name), '') if p.name.isdigit() else (1, 0, p.name)):
        q_path = cdir / "probing_questions" / "probing_questions.json"
        qs = json.loads(q_path.read_text(encoding="utf-8"))
        info = per_conv[(tier, cdir.name)]
        idc = info["id_counts"]
        for ability, qlist in qs.items():
            for i, q in enumerate(qlist, start=1):
                qid = f"{tier}::{cdir.name}::{ability}::{i}"
                if ability == "abstention":
                    cat, gold = "ABSTENTION_NO_POSITIVE_EVIDENCE", []
                elif "source_chat_ids" not in q or not q.get("source_chat_ids"):
                    coarse = bool(q.get("conversation_reference") or q.get("conversation_references"))
                    cat, gold = ("COARSE_SOURCE" if coarse else "SOURCE_AMBIGUOUS_OR_MISSING"), []
                else:
                    try:
                        gold = flatten_source_ids(q["source_chat_ids"])
                    except Exception:
                        gold, cat = [], "MALFORMED_CONTRADICTORY"
                    else:
                        if not gold:
                            cat = "SOURCE_AMBIGUOUS_OR_MISSING"
                        elif all(idc.get(g, 0) == 1 for g in gold):
                            cat = "EXACT_SOURCE_IDS"
                        elif all(idc.get(g, 0) >= 1 for g in gold):
                            cat = "SOURCE_AMBIGUOUS_OR_MISSING"  # multi-mapped
                        else:
                            cat = "SOURCE_AMBIGUOUS_OR_MISSING"  # unmatched
                is_elig = (cat == "EXACT_SOURCE_IDS") and info["unique_archive"]
                row = rows_by_id.get(qid)
                if row is None:
                    mismatch.append({"qid": qid, "issue": "MISSING_IN_CSV"})
                    continue
                ok = (
                    row["primary_evidence_cohort_eligible"] == str(is_elig)
                    and row["audit_category"] == cat
                    and int(row["gold_source_unit_count"]) == len(set(gold))
                    and json.loads(row["gold_source_ids"]) == gold
                )
                if ok:
                    matched += 1
                else:
                    mismatch.append({
                        "qid": qid,
                        "csv_elig": row["primary_evidence_cohort_eligible"],
                        "rec_elig": is_elig,
                        "csv_cat": row["audit_category"],
                        "rec_cat": cat,
                        "csv_gold_n": row["gold_source_unit_count"],
                        "rec_gold_n": len(set(gold)),
                    })
result["recomputed_vs_csv"] = {
    "questions_recomputed": 2000,
    "matched": matched,
    "mismatch_count": len(mismatch),
    "mismatch_examples": mismatch[:20],
}

(OUT / "audit_cohort_corpus_verify.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(result, indent=2, ensure_ascii=False)[:4000])



