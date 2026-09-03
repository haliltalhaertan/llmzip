#!/usr/bin/env python3
"""Build INDEPENDENT_V6_EXECUTION_AUDIT_HASHES.json: hashes every recursive audit
output except itself, and binds the exact V6 anchors this audit was scoped to."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

REPO = Path("/home/user/llmzip")
NS = REPO / "audit_v52_t4f1_execution_candidate_v6_independent_audit_2026_09_03"
CAND = REPO / "task4f1_execution_candidate_v6_2026_09_03"
SELF = "INDEPENDENT_V6_EXECUTION_AUDIT_HASHES.json"

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()

files = {}
for p in sorted(NS.rglob("*")):
    if p.is_file() and "__pycache__" not in p.parts:
        rel = p.relative_to(NS).as_posix()
        if rel == SELF: continue
        files[rel] = {"bytes": p.stat().st_size, "sha256": sha(p)}

def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, cwd=REPO).stdout.strip()

man = {
  "schema": "V52_T4F1_V6_INDEPENDENT_DELTA_AUDIT_HASHES_V1",
  "role": "cold-start independent implementation auditor",
  "audit_date_utc": "2026-09-03",
  "audit_namespace": NS.name,
  "audit_branch": "audit/v52-t4f1-v6-independent-2026-09-03",
  "audited_repository_commit": "6dee50da1452869e6049c109100f3c3fb5abb0fb",
  "instruction_set": "prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V6_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-03.md",
  "self_excluded_file": SELF,
  "recursive_output_count": len(files),
  "files": files,
  "verdict": "BLOCKED - DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1",
  "gate_claim_status": "NOT ESTABLISHED; not yet falsified on the V6 bytes as shipped",
  "delta_route_justified": True,
  "audited_candidate_anchors": {
    "namespace": CAND.name,
    "recursive_file_count": sum(1 for p in CAND.rglob("*") if p.is_file()),
    "implementation_sha256": sha(CAND / "v52_t4f1_beam_retrieval.py"),
    "PAYLOAD_HASHES.json": sha(CAND / "PAYLOAD_HASHES.json"),
    "CANDIDATE_EXECUTION_SEAL.json": sha(CAND / "CANDIDATE_EXECUTION_SEAL.json"),
    "NORMATIVE_SOURCE_MAP.json": sha(CAND / "NORMATIVE_SOURCE_MAP.json"),
    "candidate_package_preflight.py": sha(CAND / "candidate_package_preflight.py"),
    "EXECUTION_SPEC.md": sha(CAND / "EXECUTION_SPEC.md"),
    "detached_attestation_sha256": sha(REPO / "docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json"),
  },
  "upstream_anchors_independently_verified": {
    "beam_commit": "3e12035532eb85768f1a7cd779832b650c4b2ef9",
    "beam_tree_manifest_sha256": "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318",
    "beam_selected_blobs_verified": "205/205",
    "cohort_sha256": "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a",
    "cohort_shape": "2000 rows / 1712 eligible / 96 archives; excludes 1M::5, 1M::26, 1M::33, 1M::34",
  },
  "preserved_read_only": {
    "accepted_v4_runner_sha256": "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8",
    "v4_audit_commit": "641568d8b78af97eb69c9dc4e0434e7b6564a26c",
    "v5_audit_commit": "6243ba6d9fe1c3d059d78369d8fed3534d7921d0",
    "v5_audit_manifest_sha256": "0b7879e366d58f68022bc12826e820a23e7c2a1f4bf29c456fea70f7faf4af81",
    "cochair_review_commit": "776c45f333b262754aa0020e8043db54942d1bea",
    "cochair_approval_commit": "4bd32782c4148d15a632fb822dae8cab358892c6",
  },
  "implementer_evidence_read_only": {
    "namespace": "task4f1_execution_candidate_v6_preflight_2026_09_03",
    "PREFLIGHT_HASHES.json": sha(REPO / "task4f1_execution_candidate_v6_preflight_2026_09_03/PREFLIGHT_HASHES.json"),
    "use": "coverage assessment only; not evidence for any conclusion",
  },
  "gate6_citation_boundary": [
    "B1/B2/B3 implementation gates", "aggregation correctness",
    "authorization verifier behaviour beyond statically checked fail-closed constants",
    "leakage analysis of the retrieval path",
  ],
  "outcome_boundary": json.loads((NS / "evidence/OUTCOME_BOUNDARY_TALLY.json").read_text()),
  "blocking_findings": [
    "All three exempt classes are wider than their declared rationales (C1, C2, C3, C4)",
    "Missing load-bearing concepts: REAL_CANARY_QUERY and TIERS",
    "Gate claim not established: normalisation destroys pattern boundaries (A1-A3); eight further evasion classes survive (B1, B3-B8); five concepts covering the numerical core are unenforced (D1-D7)",
    "Detached attestation is byte-unbound, unswept, and its path is redirectable into the candidate (B8, F5)",
  ],
  "non_blocking_observations": [
    "No superseded literal survives in the shipped bytes under an independent robust search: 0 survivors",
    "No numerical-semantic drift in the shipped bytes: 30/30 declared values match the runner constants",
    "Independent sweep of shipped bytes: 0 tokens invisible to the gate",
    "Runner byte-identical and AST-identical to the accepted V4 runner",
  ],
  "environment": {
    "python": "3.12.13 (built from python.org source tarball)",
    "numpy": "2.3.2", "scipy": "1.16.1", "scikit-learn": "1.7.1", "psutil": "7.0.0",
    "single_thread_controls": True, "PYTHONDONTWRITEBYTECODE": "1",
  },
  "authority_note": ("V6 was prepared under Continuity Lead authority alone and exceeds the standing "
                     "co-chair approval 4bd32782, which covered V5 only."),
}
(NS / SELF).write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
print(f"{len(files)} outputs hashed")
print("manifest sha256:", sha(NS / SELF))
