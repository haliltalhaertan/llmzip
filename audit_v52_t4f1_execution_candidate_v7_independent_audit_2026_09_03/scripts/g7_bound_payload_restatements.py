#!/usr/bin/env python3
"""Gate 7: census of values restated INSIDE the V7 package, and whether anything reconciles them.

Tests the seal's consistency_claim directly: "no bound document can state a requirement,
so there is nothing restated and nothing to reconcile."
"""
from __future__ import annotations
import ast, hashlib, json, re, sys
from pathlib import Path

C = Path("/home/user/llmzip/task4f1_execution_candidate_v7_2026_09_03")
runner_src = (C / "v52_t4f1_beam_retrieval.py").read_text(encoding="utf-8")
checker_src = (C / "candidate_package_preflight.py").read_text(encoding="utf-8")
lock_text = (C / "DEPENDENCY_LOCK.txt").read_text(encoding="utf-8")
template = json.loads((C / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
seal = json.loads((C / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
manifest = json.loads((C / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))

t = ast.parse(runner_src)
K = {}
for n in t.body:
    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
        if n.targets[0].id.isupper():
            try: K[n.targets[0].id] = ast.literal_eval(n.value)
            except Exception: pass

lock_kv = dict(re.findall(r"^([A-Za-z_][\w-]*)==([\w.]+)$", lock_text, re.M))
lock_env = dict(re.findall(r"^([A-Z_]+)=(\d+)$", lock_text, re.M))

R = []
def rec(concept, a_site, a_val, b_site, b_val, reconciler, bound_pair):
    R.append({"concept": concept,
              "site_a": a_site, "value_a": a_val,
              "site_b": b_site, "value_b": b_val,
              "agrees": a_val == b_val,
              "reconciled_by": reconciler,
              "both_sites_bound": bound_pair})

# 1) dependency lock versions vs runner ENVIRONMENT_LOCK  (BOTH BOUND)
name_map = {"Python": "python", "numpy": "numpy", "scipy": "scipy",
            "scikit-learn": "scikit_learn", "psutil": "psutil"}
for lk, rk in name_map.items():
    rec(f"env_version::{rk}", "DEPENDENCY_LOCK.txt", lock_kv.get(lk),
        "runner ENVIRONMENT_LOCK", K["ENVIRONMENT_LOCK"][rk],
        "NOTHING - the runner only digests the lock; it never parses it", True)

# 2) thread controls vs runner THREAD_LOCK  (BOTH BOUND)
for tk, tv in K["THREAD_LOCK"].items():
    rec(f"thread_control::{tk}", "DEPENDENCY_LOCK.txt", lock_env.get(tk),
        "runner THREAD_LOCK", tv,
        "NOTHING - the runner only digests the lock; it never parses it", True)

# 3) archive count: template vs runner  (BOTH BOUND)
rec("required_archive_count", "RUN_AUTHORIZATION_TEMPLATE.json", template["required_archive_count"],
    "runner EXPECTED_ARCHIVES", K["EXPECTED_ARCHIVES"],
    "runner verify_run_authorization compares the authorization field to EXPECTED_ARCHIVES", True)

# 4) accepted runner digest: checker constant vs actual runner vs seal
runner_sha = hashlib.sha256((C / "v52_t4f1_beam_retrieval.py").read_bytes()).hexdigest()
m = re.search(r'V4_ACCEPTED_RUNNER_SHA256 = "([0-9a-f]{64})"', checker_src)
rec("accepted_runner_sha256", "candidate_package_preflight.py", m.group(1),
    "actual runner bytes", runner_sha, "checker line 57 compares them", True)
rec("accepted_runner_sha256", "CANDIDATE_EXECUTION_SEAL.json implementation.sha256",
    seal["implementation"]["sha256"], "actual runner bytes", runner_sha,
    "NOTHING inside the package - the seal is unbound and its digest is not checked here", False)

# 5) dependency lock digest: runner constant vs seal vs actual
lock_sha = hashlib.sha256((C / "DEPENDENCY_LOCK.txt").read_bytes()).hexdigest()
rec("dependency_lock_sha256", "runner EXPECTED_DEPENDENCY_LOCK_SHA256",
    K["EXPECTED_DEPENDENCY_LOCK_SHA256"], "actual lock bytes", lock_sha,
    "runner verify_bound_file at --mode preflight/run/finalize", True)
rec("dependency_lock_sha256", "CANDIDATE_EXECUTION_SEAL.json environment.sha256",
    seal["environment"]["sha256"], "actual lock bytes", lock_sha,
    "NOTHING inside the package", False)

# 6) HMAC env var name: runner vs checker vs seal
mm = re.search(r'AUTH_HMAC_ENV = "([A-Z0-9_]+)"', checker_src)
rec("auth_hmac_env_name", "candidate_package_preflight.py", mm.group(1),
    "runner AUTH_HMAC_ENV", K["AUTH_HMAC_ENV"], "checker line 120 compares seal to its own copy", True)
rec("auth_hmac_env_name", "CANDIDATE_EXECUTION_SEAL.json authorization_control",
    seal["authorization_control"]["key_environment_variable"], "runner AUTH_HMAC_ENV",
    K["AUTH_HMAC_ENV"], "checker line 120", False)

# 7) signed field list: runner tuple vs seal list
rec("auth_signed_fields", "CANDIDATE_EXECUTION_SEAL.json signed_fields",
    list(seal["authorization_control"]["signed_fields"]), "runner AUTH_SIGNED_FIELDS",
    list(K["AUTH_SIGNED_FIELDS"]), "NOTHING - the checker never compares these", False)

# 8) seal schema literal restated in the checker
ms = re.search(r'seal\["schema"\] != "([A-Z0-9_]+)"', checker_src)
rec("seal_schema", "candidate_package_preflight.py", ms.group(1),
    "CANDIDATE_EXECUTION_SEAL.json schema", seal["schema"], "checker line 78", True)

# 9) submission-status literal restated in the checker (twice) and the seal
rec("submission_status", "candidate_package_preflight.py",
    "PREPARED_NOT_INDEPENDENTLY_AUDITED", "CANDIDATE_EXECUTION_SEAL.json",
    seal["status_at_audit_submission"], "checker lines 61 and 80", True)

# 10) the four bound names restated in the checker AND in the inventory
rec("bound_payload_name_set", "candidate_package_preflight.py EXPECTED_BOUND_PAYLOAD",
    sorted(re.findall(r'"([^"]+)",\s*#', checker_src))[:4],
    "PAYLOAD_HASHES.json files[].name", sorted(i["name"] for i in manifest["files"]),
    "checker line 49 set equality", True)

# stale narrative labels inside the shipped package
stale = []
for field, text in [("package_version_note", seal.get("package_version_note", "")),
                    ("self_audit_prohibited", seal.get("self_audit_prohibited", "")),
                    ("stop_rule", seal.get("stop_rule", ""))]:
    for tag in ("V4", "V5", "V6"):
        if re.search(rf"\b{tag}\b", text):
            stale.append({"file": "CANDIDATE_EXECUTION_SEAL.json", "field": field,
                          "mentions": tag, "text": text[:220]})

out = {
  "claim_under_test": seal["consistency_claim"],
  "restatement_pairs": len(R),
  "pairs_with_both_sites_bound": sum(1 for r in R if r["both_sites_bound"]),
  "pairs_reconciled_by_nothing": [r["concept"] for r in R if r["reconciled_by"].startswith("NOTHING")],
  "disagreements": [r for r in R if not r["agrees"]],
  "disagreement_count": sum(1 for r in R if not r["agrees"]),
  "restatements": R,
  "stale_version_labels_in_shipped_package": stale,
  "dependency_lock_first_line": lock_text.splitlines()[0],
  "dependency_lock_task_label_matches_runner_task": "4F1" in lock_text.splitlines()[0],
  "runner_TASK": K["TASK"],
  "template_note_claims_every_value_is_placeholder": "Every value here is a placeholder" in template["note"],
  "template_non_placeholder_values": {k: v for k, v in template.items()
                                      if not (isinstance(v, str) and ("REPLACE" in v or "NOT_" in v))},
}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("restatement pairs        :", out["restatement_pairs"])
print("both sites BOUND         :", out["pairs_with_both_sites_bound"])
print("reconciled by NOTHING    :", len(out["pairs_reconciled_by_nothing"]))
print("   ", out["pairs_reconciled_by_nothing"])
print("disagreements            :", out["disagreement_count"])
print("lock first line          :", out["dependency_lock_first_line"])
print("runner TASK              :", out["runner_TASK"])
print("template 'all placeholder' claim:", out["template_note_claims_every_value_is_placeholder"])
print("template non-placeholder values :", out["template_non_placeholder_values"])
print("stale version labels     :", [(s["field"], s["mentions"]) for s in stale])
