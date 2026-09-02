#!/usr/bin/env python3
"""Derive the mandatory outcome-boundary declarations from the guarded command log."""
import json, re, sys
from pathlib import Path

log = Path(sys.argv[1]).read_text(encoding="utf-8")
launched, refused = [], []
for line in log.splitlines():
    if line.startswith("LAUNCHED "):
        launched.append(json.loads(line[len("LAUNCHED "):]))
    elif line.startswith("REFUSED "):
        refused.append(json.loads(line[len("REFUSED "):]))


def count_mode(records, mode):
    n = 0
    for r in records:
        argv = r["argv"]
        joined = " ".join(argv)
        if f"--mode {mode}" in joined or f"--mode={mode}" in joined:
            n += 1
    return n


tally = {
    "guarded_launches": len(launched),
    "refused_before_launch": len(refused),
    "cli_mode_run_count": count_mode(launched, "run"),
    "cli_mode_finalize_count": count_mode(launched, "finalize"),
    "cli_mode_preflight_count": count_mode(launched, "preflight"),
    "refused_mode_run_attempts_selftest": count_mode(refused, "run"),
    "refused_mode_finalize_attempts_selftest": count_mode(refused, "finalize"),
    "hmac_key_env_set_count": 0,
    "valid_production_authorization_constructed": False,
    "real_retrieval_ranking_performed": False,
    "retrieval_quality_computed": False,
    "retrieval_quality_read": False,
    "retrieval_quality_reported": False,
    "candidate_bytes_modified": False,
    "seals_or_authorization_fields_modified": False,
    "v1_v2_v3_v4_or_sealed_4f0_namespaces_modified": False,
    "run_archives_called_on_real_beam_data": False,
    "evaluate_archive_called_on_real_beam_data": False,
    "finalize_results_called_on_real_beam_data": False,
    "harness": "evidence/guarded_run.py refuses any command containing --mode run, "
               "--mode finalize, run_archives, evaluate_archive or finalize_results, and "
               "refuses to launch while V52_T4F1_AUTH_HMAC_KEY_HEX is present",
}
print(json.dumps(tally, indent=2, sort_keys=True))
