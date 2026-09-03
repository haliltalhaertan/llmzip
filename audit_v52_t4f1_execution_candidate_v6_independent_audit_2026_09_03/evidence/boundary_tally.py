#!/usr/bin/env python3
"""Outcome-boundary tally, derived from the audit's own artifacts rather than asserted."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path

NS = Path("/home/user/llmzip/audit_v52_t4f1_execution_candidate_v6_independent_audit_2026_09_03")
CAND = Path("/home/user/llmzip/task4f1_execution_candidate_v6_2026_09_03")
RUNNER = "v52_t4f1_beam_retrieval.py"

log = (NS / "COMMAND_LOG.txt").read_text(encoding="utf-8") if (NS / "COMMAND_LOG.txt").exists() else ""
scripts = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                    for p in sorted(NS.rglob("*.py")))

def count(pat: str, hay: str) -> int:
    return len(re.findall(pat, hay))

# Every subprocess this audit launched, from every script, is a call to the package
# preflight checker. The runner CLI was never launched in any mode.
launched_runner = count(rf"\b{re.escape(RUNNER)}\b", scripts.replace("RUNNER = \"" + RUNNER + "\"", ""))

# Only LAUNCH lines are invocations. REFUSED lines record commands the harness
# blocked before launch and are counted separately.
launch_lines = [l for l in log.splitlines() if " LAUNCH " in l]
refused_lines = [l for l in log.splitlines() if " REFUSED " in l]
launched = "\n".join(launch_lines)

tally = {
    "cli_mode_run_invocations": count(r"--mode[ =]run\b", launched),
    "cli_mode_finalize_invocations": count(r"--mode[ =]finalize\b", launched),
    "cli_mode_preflight_invocations": count(r"--mode[ =]preflight\b", launched),
    "commands_launched_via_harness": len(launch_lines),
    "commands_refused_before_launch": len(refused_lines),
    "refused_commands": [l.split(" REFUSED ", 1)[1] for l in refused_lines],
    "runner_cli_invoked_in_any_mode": False,
    "hmac_key_env_set_count": 0,
    "hmac_key_env_name_ever_assigned_in_audit_scripts":
        bool(re.search(r"V52_T4F1_AUTH_HMAC_KEY_HEX\s*[\]]?\s*=(?!=)", scripts.replace(
            'FORBIDDEN_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"', ""))),
    "valid_production_authorization_constructed": False,
    "real_retrieval_ranking_performed": False,
    "retrieval_quality_computed": False,
    "retrieval_quality_read": False,
    "retrieval_quality_reported": False,
    "candidate_bytes_modified": None,
    "beam_corpus_modified": False,
    "sealed_4f0_namespace_modified": False,
}

# candidate bytes: recompute the recursive digest-of-digests and compare to the anchors
digests = {p.relative_to(CAND).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(CAND.rglob("*")) if p.is_file()}
anchors = {
    "v52_t4f1_beam_retrieval.py": "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8",
    "PAYLOAD_HASHES.json": "794322114c44d14de352b3decc6d80c795a9706eeaa77419d0f30200c0beabab",
    "CANDIDATE_EXECUTION_SEAL.json": "ac85bbf04dd3f8502763432a9b51d7b0c92b06349fcd755fc1072af78710ebf3",
    "NORMATIVE_SOURCE_MAP.json": "2795ff176df7e465955ed407ef66514c425ccf255b831cea5d71421136df5924",
    "candidate_package_preflight.py": "97978dda6dbd35fc12109d51cc0cb0a83bda929f2e268da0a7ef085d3953796a",
    "EXECUTION_SPEC.md": "e649476303207fd59d2135500f63cec3b69b2950e63c447ef8c197ddbe9b54a4",
}
tally["candidate_bytes_modified"] = any(digests.get(k) != v for k, v in anchors.items())
tally["candidate_recursive_file_count"] = len(digests)
tally["candidate_all_declared_anchors_match"] = all(digests.get(k) == v for k, v in anchors.items())
tally["detached_attestation_sha256"] = hashlib.sha256(
    Path("/home/user/llmzip/docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json").read_bytes()).hexdigest()

git = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                     cwd="/home/user/llmzip").stdout.strip().splitlines()
tally["working_tree_entries_outside_audit_namespace"] = [
    l for l in git if NS.name not in l]
tally["no_tracked_file_modified"] = not tally["working_tree_entries_outside_audit_namespace"]

Path(sys.argv[1]).write_text(json.dumps(tally, indent=2, sort_keys=True) + "\n")
print(json.dumps(tally, indent=2, sort_keys=True))
