#!/usr/bin/env python3
"""Verify committed frozen artifacts byte-for-byte against pinned SHA256 values.

The verifier is intentionally conservative. A hash mismatch is blocking. Large or
Drive-only artifacts are reported as EXTERNAL-PIN when their bytes are not present in
the Git checkout; their expected hashes remain visible so a cold auditor can verify
materialized copies independently.

Usage:
    python3 tools/verify_frozen_artifacts.py
    python3 tools/verify_frozen_artifacts.py --list
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Post-run manifests currently committed to Git.
MANIFESTS = [
    ROOT / "docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json",
]

# Cross-file bindings for committed Task 4C2 chain anchors.
BINDINGS = [
    (
        ROOT / "docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json",
        "pre_run_seal_sha256",
        "docs/v52/task4c2/V52_T4C2_PRE_RUN_SEAL.json",
    ),
    (
        ROOT / "docs/v52/task4c2/V52_T4C2_PRE_RUN_SEAL.json",
        "script_sha256",
        "docs/v52/task4c2/v52_t4c2_centering_geometry.py",
    ),
]

# Large Task 4C2 artifacts intentionally kept in Drive.
DRIVE_ONLY = {
    "V52_T4C2_trial_results.csv",
    "V52_T4C2_BINARY_GEOMETRY.zip",
}

# Exact-byte frozen adapters are now in Git. This former provenance gap is CLOSED.
ADAPTERS = {
    "adapters/longmemeval_v52_adapter.py":
        "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722",
    "adapters/longmemeval_v52_adapter_v2.py":
        "643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218",
}

# Task 4C3 was accepted after an independent audit. Its canonical raw bytes remain
# Drive-first. If exact copies are later committed at these paths, this verifier will
# automatically promote them from EXTERNAL-PIN to byte-level verification.
TASK4C3_EXTERNAL = {
    "docs/v52/task4c3/V52_T4C3_PRE_RUN_SEAL.json":
        "c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97",
    "docs/v52/task4c3/v52_t4c3_coordinate_axis_probe.py":
        "8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996",
    "docs/v52/task4c3/V52_T4C3_POST_RUN_MANIFEST.json":
        "7bfeae589ffdf86012c04eec02017918cae92c3fa20a699c8d342f4baa39c00c",
}

DATASET_EXTERNAL = {
    "data/longmemeval_s_cleaned.json":
        "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442",
}


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def dig(obj, dotted: str):
    for part in dotted.split("."):
        obj = obj[part]
    return obj


def verify_pinned_group(title: str, pins: dict[str, str], *, external_ok: bool, show_all: bool):
    ok = mismatch = external = 0
    problems: list[str] = []
    print(f"\n== {title} ==")
    for rel, expected in sorted(pins.items()):
        path = ROOT / rel
        if not path.exists():
            if external_ok:
                external += 1
                print(f"  EXTERNAL-PIN {rel}\n    expected {expected}")
            else:
                problems.append(f"ABSENT     {rel}\n    expected {expected}")
                print(f"  ABSENT     {rel}")
            continue
        got = sha256_file(path)
        if got == expected:
            ok += 1
            if show_all or not external_ok:
                print(f"  OK         {rel}")
        else:
            mismatch += 1
            problems.append(f"MISMATCH   {rel}\n    got      {got}\n    expected {expected}")
            print(f"  MISMATCH   {rel}")
    return ok, mismatch, external, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print every checked path")
    args = ap.parse_args()

    ok = mismatch = drive_only = absent = external = 0
    problems: list[str] = []

    for man in MANIFESTS:
        if not man.exists():
            absent += 1
            problems.append(f"MANIFEST ABSENT  {man.relative_to(ROOT)}")
            continue
        hashes = json.loads(man.read_text(encoding="utf-8"))["output_hashes"]
        base = man.parent
        print(f"\n== {man.relative_to(ROOT)} -- {len(hashes)} declared artifacts ==")
        for name, expected in sorted(hashes.items()):
            path = base / name
            if not path.exists():
                if name in DRIVE_ONLY:
                    drive_only += 1
                    if args.list:
                        print(f"  DRIVE-ONLY {name}")
                else:
                    absent += 1
                    print(f"  ABSENT     {name}  (compact -- should be committed)")
                continue
            got = sha256_file(path)
            if got == expected:
                ok += 1
                if args.list:
                    print(f"  OK         {name}")
            else:
                mismatch += 1
                problems.append(
                    f"MISMATCH   {name}\n    got      {got}\n    expected {expected}"
                )
                print(f"  MISMATCH   {name}")

    a_ok, a_bad, a_ext, a_prob = verify_pinned_group(
        "frozen LongMemEval adapters — CLOSED GAP", ADAPTERS,
        external_ok=False, show_all=args.list,
    )
    ok += a_ok
    mismatch += a_bad
    external += a_ext
    problems.extend(a_prob)

    print("\n== Task 4C2 cross-manifest bindings ==")
    for man, key, rel in BINDINGS:
        target = ROOT / rel
        if not man.exists() or not target.exists():
            absent += 1
            print(f"  SKIP       {key} -> {rel} (not present)")
            continue
        expected = dig(json.loads(man.read_text(encoding="utf-8")), key)
        got = sha256_file(target)
        if got == expected:
            ok += 1
            print(f"  OK         {key} -> {rel}")
        else:
            mismatch += 1
            problems.append(f"MISMATCH   {key} -> {rel}\n    got      {got}\n    expected {expected}")
            print(f"  MISMATCH   {key} -> {rel}")

    c_ok, c_bad, c_ext, c_prob = verify_pinned_group(
        "Task 4C3 accepted frozen anchors", TASK4C3_EXTERNAL,
        external_ok=True, show_all=args.list,
    )
    ok += c_ok
    mismatch += c_bad
    external += c_ext
    problems.extend(c_prob)

    d_ok, d_bad, d_ext, d_prob = verify_pinned_group(
        "canonical LongMemEval dataset", DATASET_EXTERNAL,
        external_ok=True, show_all=args.list,
    )
    ok += d_ok
    mismatch += d_bad
    external += d_ext
    problems.extend(d_prob)

    print(
        f"\nmatch={ok}  mismatch={mismatch}  drive-only={drive_only}  "
        f"external-pins={external}  absent={absent}"
    )

    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print("  " + p)

    if mismatch:
        print(
            "\nCHAIN-OF-CUSTODY DEFECT. Do not interpret affected results until resolved.\n"
            "Never repair a frozen artifact by regenerating or reformatting it; restore\n"
            "the canonical bytes and verify the published SHA256."
        )
        return 1

    print("\nNo committed frozen-artifact hash mismatch detected.")
    if external:
        print("External pins still require independent byte materialization for full re-hash coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
