#!/usr/bin/env python3
"""Verify that the committed continuity handoff still binds its declared V52 anchors.

This checker never imports or executes an outcome-capable candidate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ops" / "CURRENT_STATE.json"
LEDGER_PATH = ROOT / "docs" / "CONTINUITY_LEDGER.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    if state.get("schema") != "LLMZIP_CONTINUITY_STATE_V1":
        failures.append("unexpected state schema")
    if state.get("task_state", {}).get("task_4f1_run") != "BLOCKED":
        failures.append("Task 4F1 run is not blocked")
    if state.get("task_state", {}).get("retrieval_quality_outcome_access") != "FORBIDDEN":
        failures.append("retrieval outcome access is not forbidden")
    hard_stops = "\n".join(state.get("hard_stops", []))
    for required in ("--mode run", "--mode finalize", "V52_T4F1_AUTH_HMAC_KEY_HEX"):
        if required not in hard_stops:
            failures.append(f"hard stop missing: {required}")
    for label, anchor in state.get("anchors", {}).items():
        path = ROOT / anchor["path"]
        if not path.is_file():
            failures.append(f"{label}: missing {anchor['path']}")
            continue
        actual = sha256(path)
        if actual != anchor["sha256"]:
            failures.append(f"{label}: SHA256 mismatch ({actual})")
    ledger = LEDGER_PATH.read_text(encoding="utf-8")
    entry = state.get("ledger_entry")
    if not entry or entry not in ledger:
        failures.append("current ledger entry is absent")
    tag = state.get("predecessor_anchor", {}).get("handoff_tag")
    if not tag or tag not in ledger:
        failures.append("predecessor handoff tag is absent from ledger")
    if failures:
        print("CONTINUITY_STATE: BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("CONTINUITY_STATE: PASS")
    print(f"state_id={state['state_id']}")
    print(f"next_single_action={state['task_state']['next_single_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
