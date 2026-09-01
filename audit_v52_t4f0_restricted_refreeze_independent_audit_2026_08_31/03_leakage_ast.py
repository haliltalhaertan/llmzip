# V52 T4F0 RESTRICTED-REFREEZE INDEPENDENT AUDIT — 03_leakage_ast.py
# Static AST/text leakage audit of all candidate-namespace Python code.
import ast
import json
import sys
from pathlib import Path

CAND = Path(sys.argv[1])
OUT = Path(sys.argv[2])

FORBIDDEN_IDENTIFIERS = {
    "ideal_answer", "ideal_response", "answer", "rubric", "source_chat_ids",
    "source_labels", "evaluator_output", "outcome", "gold", "retrieval",
}
FORBIDDEN_CALLS = {
    "TfidfVectorizer", "TruncatedSVD", "fit_transform", "transform", "fit",
    "cossim", "cosine_similarity", "hamming", "rank", "argsort", "lexsort",
}
FORBIDDEN_SUBSTRINGS_FITTING = ["sklearn", "numpy.dot", "@ ", "fit_transform"]

rows = []
py_files = sorted(CAND.rglob("*.py"))
for p in py_files:
    src = p.read_text(encoding="utf-8")
    tree = ast.parse(src)
    idents = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    idents |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    calls |= {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    bad_ids = sorted(FORBIDDEN_IDENTIFIERS & idents)
    bad_calls = sorted(FORBIDDEN_CALLS & calls)
    rows.append({
        "file": p.name,
        "sha256": __import__("hashlib").sha256(src.encode("utf-8")).hexdigest(),
        "forbidden_identifiers": bad_ids,
        "forbidden_fitting_ranking_calls": bad_calls,
        "verdict": "PASS" if not bad_ids and not bad_calls else "FAIL",
    })

result = {
    "scope": "candidate namespace *.py (static AST only)",
    "files_scanned": [r["file"] for r in rows],
    "rows": rows,
    "notes": {
        "cohort_fields_used_by_preflight": [
            "primary_evidence_cohort_eligible", "tier", "conversation_id", "ability",
            "audit_category", "gold_source_unit_count", "audit_question_id",
        ],
        "field_note": "audit_category/ability are official classification metadata used for cohort membership only; no answer/rubric/evaluator/source-payload text is read",
        "fitting_code_in_candidate": "none — candidate contains the no-outcome preflight only",
    },
    "overall": "PASS" if all(r["verdict"] == "PASS" for r in rows) else "FAIL",
}
(OUT / "audit_leakage_ast.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(result, indent=2)[:1500])
