"""Read-only check: does the COMMITTED producer rule reproduce the bound LoCoMo cohort?

This answers the second of the two claims kept apart in LOCOMO_SELECTION_RULE_NOTE_2026-09-08.md -
why those 1535 questions - and it does NOT strengthen the first, that the mapping is verified.

The rule is transcribed from `research/v52/locomo_sign_mechanism_replication.py` on branch
codex/v52-locomo-reproduction-audit-2026-09-07 @ 692f599eedeb7e7a649443f24ff507e8c4d1c17d. It is
TRANSCRIBED rather than imported on purpose: importing the producer module would execute its code and
pull in its representation machinery, which is not authorized here.

Read-only. No representation is fitted, nothing is retrieved, ranked, evaluated or bootstrapped, no
new corpus scan beyond this check is started, and NO question, answer or dialogue text is printed,
logged or written - only ids, counts and set sizes.

Usage: python verify_selection_rule.py <locomo10.json> <audit-dir> <bound-mapping.json> [json-out]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SOURCE_SHA256 = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
SOURCE_BYTES = 2805274
COHORT_CATEGORIES = {1, 2, 3, 4}          # EXPECTED_CATEGORY_COUNTS keys
EXPECTED_AFTER_CATEGORY = 1540            # EXPECTED_QUESTIONS
EXPECTED_CORRECTIONS = 156                # EXPECTED_CORRECTIONS
DIA = re.compile(r"D\d+:\d+")

src_path, audit_dir, map_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
out_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None


def norm_evidence(value):
    """Transcribed from the committed `norm_evidence`."""
    if value is None:
        return []
    if isinstance(value, str):
        found = DIA.findall(value)
        return found if found else [value]
    if isinstance(value, (list, tuple)):
        out = []
        for item in value:
            if isinstance(item, str):
                found = DIA.findall(item)
                out.extend(found if found else [item])
            elif isinstance(item, dict):
                did = item.get("dia_id") or item.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


h = hashlib.sha256()
with src_path.open("rb") as f:
    for block in iter(lambda: f.read(8 << 20), b""):
        h.update(block)
if h.hexdigest() != SOURCE_SHA256 or src_path.stat().st_size != SOURCE_BYTES:
    raise SystemExit("ABORT: source identity mismatch")
print(f"source identity VERIFIED: {SOURCE_SHA256}\n")

corrections = {}
for f in sorted(audit_dir.glob("errors_conv_*.json")):
    rows = json.loads(f.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        continue
    for row in rows:
        qid = row.get("question_id")
        if qid:
            corrections[str(qid)] = {"has_correct_evidence": "correct_evidence" in row,
                                     "correct_evidence": norm_evidence(row.get("correct_evidence")),
                                     "error_type": row.get("error_type")}

raw = json.loads(src_path.read_text(encoding="utf-8"))
after_category, predicted, dropped_empty_gold = 0, set(), []
for index, item in enumerate(raw):
    conv = item.get("conversation") or {}
    ids = []
    for sk in sorted((k for k in conv if k.startswith("session_") and not k.endswith("_date_time")),
                     key=lambda k: int(k.split("_")[1])):
        for msg in conv.get(sk) or []:
            did = str(msg.get("dia_id", ""))
            if did:
                ids.append(did)
    id_to_row = {x: i for i, x in enumerate(ids)}
    for position, question in enumerate(item.get("qa") or []):
        category = question.get("category")
        category = int(category) if category is not None else None
        if category not in COHORT_CATEGORIES:
            continue                                             # step 1
        after_category += 1
        qid = str(question.get("question_id") or f"locomo_{index}_qa{position}")
        correction = corrections.get(qid)
        evidence = (list(correction["correct_evidence"]) if correction["has_correct_evidence"]
                    else norm_evidence(question.get("evidence"))) if correction \
            else norm_evidence(question.get("evidence"))          # step 2
        gold = list(dict.fromkeys(id_to_row[e] for e in evidence if e in id_to_row))
        if not gold:                                              # step 3
            dropped_empty_gold.append(
                {"question_id": qid, "had_correction": bool(correction),
                 "error_type": correction["error_type"] if correction else None,
                 "corrected_evidence_count": len(correction["correct_evidence"]) if correction else None})
            continue
        predicted.add(qid)

bound = set(json.loads(map_path.read_text(encoding="utf-8"))["expected_question_to_cluster"])
checks, failed = [], []


def check(label, cond, detail=""):
    checks.append({"check": label, "pass": bool(cond), "detail": str(detail)})
    print(("ok    " if cond else "FAIL  ") + f"{label}   {detail}"[:150])
    if not cond:
        failed.append(label)


check("the audit corrections load to the frozen count",
      len(corrections) == EXPECTED_CORRECTIONS, f"{len(corrections)} vs {EXPECTED_CORRECTIONS}")
check("step 1, category in {1,2,3,4}, gives the frozen intermediate count",
      after_category == EXPECTED_AFTER_CATEGORY, f"{after_category} vs {EXPECTED_AFTER_CATEGORY}")
check("step 3 drops exactly the questions whose CORRECTED evidence resolves to no archive row",
      len(dropped_empty_gold) == after_category - len(bound),
      f"{len(dropped_empty_gold)} dropped: {[d['question_id'] for d in dropped_empty_gold]}")
check("the committed three-step rule reproduces the bound cohort EXACTLY",
      predicted == bound,
      f"predicted {len(predicted)}, bound {len(bound)}, "
      f"only-predicted {sorted(predicted - bound)[:3]}, only-bound {sorted(bound - predicted)[:3]}")
residual = [d for d in dropped_empty_gold if d["question_id"] == "locomo_6_qa11"]
check("the previously unexplained position is explained by step 2, the audit corrections",
      bool(residual) and residual[0]["had_correction"] and residual[0]["corrected_evidence_count"] == 0,
      f"{residual[0] if residual else 'not found'}")

print()
verdict = ("SELECTION RULE REPRODUCED FROM COMMITTED CODE" if not failed
           else "SELECTION RULE NOT REPRODUCED")
print(verdict)
print("This is claim 2 - why those 1535. It does NOT strengthen claim 1, that the mapping is verified, "
      "and the ingestion deliberately does NOT implement this rule.")

if out_path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "task": "read-only reproduction of the committed LoCoMo selection rule",
        "verdict": verdict,
        "rule_source": ("research/v52/locomo_sign_mechanism_replication.py @ "
                        "692f599eedeb7e7a649443f24ff507e8c4d1c17d, TRANSCRIBED not imported"),
        "steps": ["1. keep category in {1,2,3,4} - excludes category 5",
                  "2. apply the 156 audit corrections; correct_evidence REPLACES raw evidence when present",
                  "3. resolve evidence against the conversation's archive rows; drop when the gold set is empty"],
        "counts": {"after_category_step": after_category, "dropped_for_empty_gold": len(dropped_empty_gold),
                   "predicted": len(predicted), "bound": len(bound)},
        "dropped_for_empty_gold": dropped_empty_gold,
        "checks": checks,
        "claim_separation": ("claim 1 - the mapping is verified - is established in "
                             "DATA_IDENTITY_REPORT_2026-09-08.md and is NOT strengthened by this file; "
                             "claim 2 is what this file establishes"),
        "ingestion_does_not_implement_this": ("corpus_ingest.py resolves the BOUND cohort id by id and "
                                              "never derives a cohort; reimplementing this rule would be "
                                              "a second rule that could drift"),
        "content_emitted": "none - ids, counts and set sizes only",
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {out_path}")

raise SystemExit(1 if failed else 0)
