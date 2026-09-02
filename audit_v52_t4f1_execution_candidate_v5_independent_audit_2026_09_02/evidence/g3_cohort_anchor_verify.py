#!/usr/bin/env python3
"""Delta precondition 3: re-derive the cohort anchor structure from the sealed CSV bytes.
Reads only identity/eligibility columns. No ranking, no metric, no gold-set scoring."""
import csv, hashlib, json, sys
from pathlib import Path

P = Path(sys.argv[1]).resolve()
rows = list(csv.DictReader(P.read_text(encoding="utf-8").splitlines()))
fields = list(rows[0].keys()) if rows else []

elig_col = next((c for c in fields if c.lower() in
                 ("eligible", "is_eligible", "eligible_flag", "in_estimand", "primary_evidence_cohort_eligible")), None)


def truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "t")


def archive_of(r):
    for a, b in (("tier", "conversation_id"), ("tier", "conversation"), ("tier", "conv_id")):
        if a in r and b in r:
            return f"{r[a]}::{r[b]}"
    for c in fields:
        if c.lower() in ("archive_id", "archive"):
            return r[c]
    qid = r.get("audit_question_id", "")
    parts = qid.split("::")
    return "::".join(parts[:2]) if len(parts) >= 2 else ""


eligible = [r for r in rows if (truthy(r[elig_col]) if elig_col else True)]
archives = sorted({archive_of(r) for r in eligible})
all_archives = sorted({archive_of(r) for r in rows})
excluded = sorted(set(all_archives) - set(archives))

print(json.dumps({
    "cohort_path": str(P),
    "cohort_sha256": hashlib.sha256(P.read_bytes()).hexdigest(),
    "columns": fields,
    "eligibility_column": elig_col,
    "total_rows": len(rows),
    "eligible_rows": len(eligible),
    "archives_over_eligible_rows": len(archives),
    "archives_over_all_rows": len(all_archives),
    "excluded_archives": excluded,
    "matches_declared_anchor": (
        len(rows) == 2000 and len(eligible) == 1712 and len(archives) == 96
        and excluded == sorted(["1M::5", "1M::26", "1M::33", "1M::34"])
    ),
}, indent=2))
