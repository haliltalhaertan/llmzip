#!/usr/bin/env python3
"""V52 Task 4F1 execution-candidate independent audit.

Gate 1 (namespace/byte closure), Gate 3 (corpus git-blob identity),
Gate 4 (cohort + source-ID join).  Outcome-free: no ranking, no metric.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "task4f1_execution_candidate_2026_08_31"
SEALED = ROOT / "audit_v52_t4f0_restricted_refreeze_2026_08_31"
MANIFEST = ROOT / "audit_v52_t4f0_codex_2026_08_31" / "pinned_tree_manifest.json"
CORPUS = ROOT.parent / "BEAM_pinned_3e12035532eb85768f1a7cd779832b650c4b2ef9"
OUT = ROOT / "audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31"

ANCHORS = {
    "v52_t4f1_beam_retrieval.py": ("28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428", 52673),
    "PAYLOAD_HASHES.json": ("278dbf80d6388a7dcd2605791283442615d5a951b2ef1e1ce1b6c92b4dd392b7", None),
    "CANDIDATE_EXECUTION_SEAL.json": ("a1277e4665936ea691505a2d386c1d6a4824c2ebc5e5e56d6a94aba1f58876cd", None),
}
UPSTREAM = {
    "restricted_final_seal": (SEALED / "CANDIDATE_SEAL.json", "596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c"),
    "cohort": (SEALED / "estimand_primary_cohort.csv", "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"),
    "protocol": (SEALED / "REFREEZE_PROTOCOL.md", "f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1"),
    "dependency_lock": (CAND / "DEPENDENCY_LOCK.txt", "86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e"),
    "pinned_tree_manifest": (MANIFEST, "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318"),
    "preflight_evidence": (ROOT / "task4f1_execution_candidate_preflight_2026_08_31" / "IMPLEMENTATION_PREFLIGHT.json",
                           "138f291ee53a70c0c4f37d4797e683acd1db77d5f362db676b5517e0d8f91f49"),
}
EXCLUDED = {"1M::5", "1M::26", "1M::33", "1M::34"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def canonical_raw_id(value):
    if isinstance(value, bool):
        raise ValueError("bool id")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value.isdigit():
        return str(int(value))
    raise ValueError(f"non-canonical {value!r}")


def iter_messages(value):
    if isinstance(value, dict):
        if {"role", "id", "content"}.issubset(value):
            yield value
            return
        for child in value.values():
            yield from iter_messages(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_messages(child)


report = {"schema": "V52_T4F1_INDEPENDENT_CLOSURE_CORPUS_COHORT_V1"}

# ---------------- Gate 1: namespace + byte closure ----------------
observed = {}
for path in sorted(CAND.rglob("*")):
    if path.is_file():
        observed[path.relative_to(CAND).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha256(path)}

inventory = json.loads((CAND / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
declared = {item["name"]: item for item in inventory["files"]}
seal = json.loads((CAND / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))

payload_rows = []
for name, item in sorted(declared.items()):
    got = observed.get(name)
    payload_rows.append({
        "name": name,
        "declared_bytes": item["bytes"],
        "declared_sha256": item["sha256"],
        "observed_bytes": None if got is None else got["bytes"],
        "observed_sha256": None if got is None else got["sha256"],
        "match": got is not None and got["bytes"] == item["bytes"] and got["sha256"] == item["sha256"],
    })

bound_names = set(declared) | {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"}
unbound = sorted(set(observed) - bound_names)

anchor_rows = []
for name, (want_hash, want_bytes) in ANCHORS.items():
    got = observed.get(name)
    anchor_rows.append({
        "name": name, "expected_sha256": want_hash, "observed_sha256": None if got is None else got["sha256"],
        "expected_bytes": want_bytes, "observed_bytes": None if got is None else got["bytes"],
        "match": got is not None and got["sha256"] == want_hash and (want_bytes is None or got["bytes"] == want_bytes),
    })

upstream_rows = []
for label, (path, want) in UPSTREAM.items():
    got = sha256(path) if path.is_file() else None
    upstream_rows.append({"label": label, "path": str(path.relative_to(ROOT.parent)), "expected_sha256": want,
                          "observed_sha256": got, "match": got == want})

# seal internal bindings
seal_bind = {
    "implementation_sha256_matches_file": seal["implementation"]["sha256"] == observed["v52_t4f1_beam_retrieval.py"]["sha256"],
    "implementation_bytes_matches_file": seal["implementation"]["bytes"] == observed["v52_t4f1_beam_retrieval.py"]["bytes"],
    "payload_inventory_sha256_matches_file": seal["payload_inventory"]["sha256"] == observed["PAYLOAD_HASHES.json"]["sha256"],
    "payload_inventory_bytes_matches_file": seal["payload_inventory"]["bytes"] == observed["PAYLOAD_HASHES.json"]["bytes"],
    "declared_file_count_6": inventory["file_count_excluding_inventory_and_seal"] == 6 == len(declared),
    "seal_file_count_agrees": seal["payload_inventory"]["file_count_excluding_inventory_and_seal"] == 6,
    "seal_env_lock_sha256": seal["environment"]["sha256"] == observed["DEPENDENCY_LOCK.txt"]["sha256"],
    "seal_parent_commit": seal["parent_llmzip_commit"] == "d3c7aa09c9553cd5ac100e668923abab602e4257",
    "seal_beam_commit": seal["pinned_beam_commit"] == "3e12035532eb85768f1a7cd779832b650c4b2ef9",
    "seal_run_blocked": seal["authorization"]["task_4f1_run"] == "BLOCKED",
    "seal_prereg_blocked": seal["authorization"]["task_4f1_preregistration"] == "BLOCKED",
    "seal_outcome_forbidden": seal["authorization"]["retrieval_quality_outcome_access"] == "FORBIDDEN",
    "seal_upstream_seal_sha": seal["sealed_task4f0_boundary"]["final_seal_sha256"] == UPSTREAM["restricted_final_seal"][1],
    "seal_upstream_cohort_sha": seal["sealed_task4f0_boundary"]["cohort_sha256"] == UPSTREAM["cohort"][1],
    "seal_upstream_protocol_sha": seal["sealed_task4f0_boundary"]["protocol_sha256"] == UPSTREAM["protocol"][1],
    "seal_manifest_sha": seal["pinned_beam_tree_manifest"]["sha256"] == UPSTREAM["pinned_tree_manifest"][1],
    "seal_excluded_archives": set(seal["sealed_task4f0_boundary"]["excluded_archives"]) == EXCLUDED,
    "seal_eligible_1712": seal["sealed_task4f0_boundary"]["eligible_questions"] == 1712,
    "seal_archives_96": seal["sealed_task4f0_boundary"]["archive_count"] == 96,
}

# template cannot authorize
template = json.loads((CAND / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
template_block = {
    "schema_is_template_only": template["schema"] == "V52_T4F1_RUN_AUTHORIZATION_V1_TEMPLATE_ONLY",
    "schema_not_runner_schema": template["schema"] != "V52_T4F1_RUN_AUTHORIZATION_V1",
    "status_not_authorized": template["status"] != "AUTHORIZED_FOR_TASK_4F1_EXECUTION",
    "outcome_access_forbidden": template["retrieval_quality_outcome_access"] != "AUTHORIZED",
    "script_hash_placeholder": template["execution_script_sha256"] == "REPLACE_ONLY_AFTER_INDEPENDENT_AUDIT",
    "seal_hash_placeholder": template["execution_candidate_seal_sha256"] == "REPLACE_ONLY_AFTER_INDEPENDENT_AUDIT",
    "namespace_placeholder": template["output_namespace_basename"] == "REPLACE_ONLY_AFTER_PREREGISTRATION",
}

report["gate1_namespace_byte_closure"] = {
    "observed_file_count": len(observed),
    "declared_payload_count": len(declared),
    "payloads": payload_rows,
    "all_payloads_match": all(r["match"] for r in payload_rows),
    "unbound_files": unbound,
    "no_unbound_payload": not unbound,
    "anchors": anchor_rows,
    "all_anchors_match": all(r["match"] for r in anchor_rows),
    "upstream_anchors": upstream_rows,
    "all_upstream_match": all(r["match"] for r in upstream_rows),
    "seal_bindings": seal_bind,
    "all_seal_bindings_ok": all(seal_bind.values()),
    "run_authorization_template_cannot_authorize": template_block,
    "template_blocked": all(template_block.values()),
}

# ---------------- Gate 4: cohort ----------------
cohort_path = SEALED / "estimand_primary_cohort.csv"
with cohort_path.open("r", encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader(fh))

eligible = []
semantics_violations = []
for row in rows:
    flag = row["primary_evidence_cohort_eligible"]
    if flag not in ("True", "False"):
        semantics_violations.append((row["audit_question_id"], "bool"))
        continue
    if flag != "True":
        continue
    archive_id = f"{row['tier']}::{row['conversation_id']}"
    gold = json.loads(row["gold_source_ids"])
    problems = []
    if row["audit_category"] != "EXACT_SOURCE_IDS":
        problems.append("category")
    if row["ability"] == "abstention":
        problems.append("abstention")
    if archive_id in EXCLUDED:
        problems.append("excluded_archive")
    if not isinstance(gold, list) or not gold:
        problems.append("gold_empty")
    elif len(gold) != int(row["gold_source_unit_count"]):
        problems.append("gold_cardinality")
    if problems:
        semantics_violations.append((row["audit_question_id"], problems))
    row["_gold"] = gold
    row["_archive"] = archive_id
    eligible.append(row)

ids = [r["audit_question_id"] for r in rows]
archives = sorted({r["_archive"] for r in eligible})

report["gate4_cohort"] = {
    "total_rows": len(rows),
    "total_rows_is_2000": len(rows) == 2000,
    "unique_audit_question_ids": len(set(ids)) == len(ids),
    "eligible_rows": len(eligible),
    "eligible_is_1712": len(eligible) == 1712,
    "archive_count": len(archives),
    "archive_count_is_96": len(archives) == 96,
    "excluded_archives_present_in_eligible": sorted(set(archives) & EXCLUDED),
    "excluded_archives_absent": not (set(archives) & EXCLUDED),
    "semantics_violations": semantics_violations[:20],
    "semantics_violation_count": len(semantics_violations),
    "gold_cardinality_histogram": dict(sorted(Counter(len(r["_gold"]) for r in eligible).items())),
    "eligible_over_top3_gold": sum(1 for r in eligible if len(r["_gold"]) > 3),
    "tier_histogram": dict(sorted(Counter(r["tier"] for r in eligible).items())),
}

# ---------------- Gate 3: corpus blob identity ----------------
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
selected = {item["path"]: item for item in manifest["selected"]}
blob_rows = []
mismatch = []
for archive_id in archives:
    tier, conv = archive_id.split("::", 1)
    for rel in (f"chats/{tier}/{conv}/chat.json",
                f"chats/{tier}/{conv}/probing_questions/probing_questions.json"):
        disk = CORPUS / rel
        entry = selected.get(rel)
        if entry is None:
            mismatch.append({"path": rel, "reason": "absent_from_manifest"})
            continue
        if not disk.is_file():
            mismatch.append({"path": rel, "reason": "missing_on_disk"})
            continue
        payload = disk.read_bytes()
        blob = git_blob_sha1(payload)
        ok = blob == entry["git_blob_sha1"] and len(payload) == entry["size"]
        if not ok:
            mismatch.append({"path": rel, "reason": "blob_or_size_mismatch",
                             "observed_blob": blob, "expected_blob": entry["git_blob_sha1"],
                             "observed_size": len(payload), "expected_size": entry["size"]})
        blob_rows.append(ok)

report["gate3_corpus_blob_identity"] = {
    "manifest_commit": manifest.get("commit"),
    "manifest_commit_matches": manifest.get("commit") == "3e12035532eb85768f1a7cd779832b650c4b2ef9",
    "manifest_selected_entries": len(selected),
    "files_expected": len(archives) * 2,
    "files_verified": sum(blob_rows),
    "all_192_match": sum(blob_rows) == 192 and len(archives) * 2 == 192 and not mismatch,
    "mismatches": mismatch[:20],
    "mismatch_count": len(mismatch),
}

# ---------------- Gate 4b: gold -> archive raw-id join ----------------
by_archive = {}
for r in eligible:
    by_archive.setdefault(r["_archive"], []).append(r)

join_failures = []
dup_id_archives = []
question_index_failures = []
archive_units = {}
for archive_id, rws in sorted(by_archive.items()):
    tier, conv = archive_id.split("::", 1)
    raw = json.loads((CORPUS / f"chats/{tier}/{conv}/chat.json").read_text(encoding="utf-8"))
    raw_ids = []
    for msg in iter_messages(raw):
        raw_ids.append(canonical_raw_id(msg.get("id")))
    archive_units[archive_id] = len(raw_ids)
    if len(set(raw_ids)) != len(raw_ids):
        dup_id_archives.append(archive_id)
    id_counts = Counter(raw_ids)
    id_set = set(raw_ids)
    questions = json.loads((CORPUS / f"chats/{tier}/{conv}/probing_questions/probing_questions.json").read_text(encoding="utf-8"))
    for r in rws:
        gold = {canonical_raw_id(v) for v in r["_gold"]}
        if len(gold) != int(r["gold_source_unit_count"]):
            join_failures.append({"qid": r["audit_question_id"], "reason": "gold_set_collapse"})
        missing = sorted(gold - id_set)
        if missing:
            join_failures.append({"qid": r["audit_question_id"], "reason": "gold_not_in_archive", "missing": missing})
        multi = sorted(g for g in gold if id_counts[g] != 1)
        if multi:
            join_failures.append({"qid": r["audit_question_id"], "reason": "gold_joins_more_than_once", "ids": multi})
        # question index join (structure only; question text length recorded, never content)
        parts = r["audit_question_id"].split("::")
        if len(parts) != 4 or parts[0] != r["tier"] or parts[1] != r["conversation_id"] or parts[2] != r["ability"]:
            question_index_failures.append({"qid": r["audit_question_id"], "reason": "id_schema"})
            continue
        idx = int(parts[3]) - 1
        recs = questions.get(r["ability"])
        if recs is None or not 0 <= idx < len(recs):
            question_index_failures.append({"qid": r["audit_question_id"], "reason": "index_out_of_range",
                                            "index": idx, "available": None if recs is None else len(recs)})
            continue
        q = recs[idx].get("question")
        if not isinstance(q, str) or not q:
            question_index_failures.append({"qid": r["audit_question_id"], "reason": "question_text_invalid"})

report["gate4b_gold_join_and_question_index"] = {
    "archives_joined": len(by_archive),
    "archives_with_duplicate_raw_ids": dup_id_archives,
    "unique_raw_ids_all_archives": not dup_id_archives,
    "join_failures": join_failures[:20],
    "join_failure_count": len(join_failures),
    "every_gold_id_joins_exactly_once": not join_failures,
    "question_index_failures": question_index_failures[:20],
    "question_index_failure_count": len(question_index_failures),
    "all_question_indices_resolve": not question_index_failures,
    "min_archive_units": min(archive_units.values()),
    "max_archive_units": max(archive_units.values()),
    "archives_below_mixed96_precondition": sorted(a for a, n in archive_units.items() if n < 98),
    "archive_units_100K_12": archive_units.get("100K::12"),
}
report["no_ranking_performed"] = True
report["no_retrieval_quality_computed"] = True
report["question_text_never_emitted"] = True

out = OUT / "audit_closure_corpus_cohort.json"
out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k.startswith("gate")}, indent=2, sort_keys=True)[:1]
      if False else "written", out.name)
for key in sorted(k for k in report if k.startswith("gate")):
    sub = report[key]
    flags = {k: v for k, v in sub.items() if isinstance(v, bool)}
    print(key, "->", "PASS" if all(flags.values()) else "FAIL", flags)
sys.exit(0)
