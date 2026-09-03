#!/usr/bin/env python3
"""Gate 3.4: does the relocated, unbound narrative still agree with the runner?

The runner's module constants are treated as the single authority. Each document is
searched for statements about the same concept and compared. Outcome-free: only
protocol constants are compared, never a retrieval result.
"""
from __future__ import annotations
import ast, hashlib, json, re, sys
from pathlib import Path

R = Path("/home/user/llmzip")
RUNNER = R / "task4f1_execution_candidate_v7_2026_09_03" / "v52_t4f1_beam_retrieval.py"

tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
K = {}
for n in tree.body:
    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
        nm = n.targets[0].id
        if nm.isupper():
            try: K[nm] = ast.literal_eval(n.value)
            except Exception: pass

import re as _re
_m = _re.search(r"NUISANCE_TRIALS\s*=\s*tuple\(range\((\d+)\)\)", RUNNER.read_text(encoding="utf-8"))
NUISANCE_N = int(_m.group(1)) if _m else None
K["NUISANCE_TRIALS_N"] = NUISANCE_N

DOCS = {
    "unbound_spec":  R / "docs/v52/task4f1/V7_EXECUTION_SPEC_NON_NORMATIVE.md",
    "unbound_readme": R / "docs/v52/task4f1/V7_CANDIDATE_README_NON_NORMATIVE.md",
    "prereg_draft":  R / "docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md",
    "v7_seal":       R / "task4f1_execution_candidate_v7_2026_09_03/CANDIDATE_EXECUTION_SEAL.json",
    "v7_template":   R / "task4f1_execution_candidate_v7_2026_09_03/RUN_AUTHORIZATION_TEMPLATE.json",
    "v7_lock":       R / "task4f1_execution_candidate_v7_2026_09_03/DEPENDENCY_LOCK.txt",
    "v7_checker":    R / "task4f1_execution_candidate_v7_2026_09_03/candidate_package_preflight.py",
    "ops_state":     R / "ops/CURRENT_STATE.json",
}

# concept -> (authoritative value, regex that finds a stated value for that concept)
CONCEPTS = {
    "latent_seed":        (K["LATENT_SEED"],  r"SVD32\s*\(`?(\d{3,5})`?\)"),
    "mixed_seed":         (K["MIXED_SEED"],   r"SVD96\s*\(`?(\d{3,5})`?\)"),
    "haar_seed_first":    (K["HAAR_SEEDS"][0], r"seed[s]?\s+`?(\d{5})`?,\s*\d{5}"),
    "itq_iterations":     (K["ITQ_ITERATIONS"], r"exactly\s+(\d+)\s+iterations"),
    "nuisance_trial_max_index": (NUISANCE_N - 1, r"trial=0\.\.(\d+)"),
    "nuisance_trial_count":     (NUISANCE_N, r"emits the (\d+) required identical trial rows"),
    "expected_archives":  (K["EXPECTED_ARCHIVES"], r"exactly\s+(\d+)\s+archive checkpoints"),
    "expected_eligible":  (K["EXPECTED_ELIGIBLE"], r"(\d[\d,]{3,})\s+questions"),
    "invariance_tol":     (K["INVARIANCE_TOLERANCE"], r"within\s+`?(1e-\d+)`?"),
    "top_k":              (K["TOP_K"], r"top-(?:three|(\d))"),
    "mixed_dim":          (K["MIXED_DIM"], r"permutation\((\d+)\)"),
}

def _ser(v):
    if isinstance(v, bytes): return v.decode("ascii", "replace")
    if isinstance(v, (tuple, frozenset, set)): return sorted(_ser(x) for x in v)
    return v

report = {"runner_constants": {k: _ser(v) for k, v in K.items() if not isinstance(v, dict)},
          "documents": {}, "contradictions": [], "restatements": []}

for label, path in DOCS.items():
    if not path.is_file():
        report["documents"][label] = {"present": False}
        continue
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    entry = {"present": True, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
             "bound_in_v7_payload": label in ("v7_template", "v7_lock", "v7_checker"),
             "hash_covered_anywhere": label in ("v7_template", "v7_lock", "v7_checker", "v7_seal"),
             "says_non_normative_in_body": "non-normative" in text.lower(),
             "stated": {}}
    for cname, (auth, rx) in CONCEPTS.items():
        m = re.search(rx, text)
        if not m:
            continue
        got = m.group(1)
        if got is None:
            continue
        norm = got.replace(",", "")
        try:
            got_v = float(norm) if ("e-" in norm or "." in norm) else int(norm)
        except ValueError:
            got_v = norm
        agrees = (got_v == auth)
        entry["stated"][cname] = {"stated_value": got_v, "authoritative_value": auth, "agrees": agrees}
        report["restatements"].append({"document": label, "concept": cname,
                                       "stated": got_v, "authoritative": auth, "agrees": agrees,
                                       "hash_covered": entry["hash_covered_anywhere"]})
        if not agrees:
            report["contradictions"].append({"document": label, "concept": cname,
                                             "stated": got_v, "authoritative": auth})
    report["documents"][label] = entry

report["restatement_count"] = len(report["restatements"])
report["contradiction_count"] = len(report["contradictions"])
report["restatements_in_uncovered_documents"] = [
    r for r in report["restatements"] if not r["hash_covered"]]
report["uncovered_restatement_count"] = len(report["restatements_in_uncovered_documents"])

Path(sys.argv[1]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("restatements found      :", report["restatement_count"])
print("of which hash-uncovered :", report["uncovered_restatement_count"])
print("live contradictions     :", report["contradiction_count"])
for r in report["restatements"]:
    flag = "OK " if r["agrees"] else "!! "
    cov = "covered  " if r["hash_covered"] else "UNCOVERED"
    print(f"  {flag}{cov} {r['document']:16s} {r['concept']:18s} stated={r['stated']!r} auth={r['authoritative']!r}")
for label, e in report["documents"].items():
    if e.get("present"):
        print(f"  body-says-non-normative[{label:16s}] = {e['says_non_normative_in_body']}   hash_covered={e['hash_covered_anywhere']}")
