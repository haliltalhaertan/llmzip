#!/usr/bin/env python3
"""Verify every committed frozen artifact byte-for-byte against its manifest SHA256.

Chain-of-custody gate for the llmzip research repo. Frozen artifacts (pre-run seals,
post-run manifests, preregistrations, sealed compute scripts, frozen diagnostics) must
be carried byte-for-byte. Re-serializing a JSON seal preserves its meaning but changes
its hash and breaks verification -- that defect has occurred once already, on
V52_T4C2_PRE_RUN_SEAL.json.

Usage:
    python3 tools/verify_frozen_artifacts.py            # verify, exit 1 on mismatch
    python3 tools/verify_frozen_artifacts.py --list     # show every checked path

Exit codes: 0 all committed artifacts match; 1 at least one MISMATCH.
Artifacts absent from Git because they are intentionally Drive-only are reported as
DRIVE-ONLY and never fail the run -- see DATASETS_AND_LARGE_ARTIFACTS.md.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Post-run manifests that declare {filename: sha256} under "output_hashes".
MANIFESTS = [
    ROOT / "docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json",
]

# Cross-manifest bindings: hashes one frozen file asserts about another.
# (manifest path, dotted key path, expected filename) -- verified when the file is present.
BINDINGS = [
    (ROOT / "docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json",
     "pre_run_seal_sha256", "docs/v52/task4c2/V52_T4C2_PRE_RUN_SEAL.json"),
    (ROOT / "docs/v52/task4c2/V52_T4C2_PRE_RUN_SEAL.json",
     "script_sha256", "docs/v52/task4c2/v52_t4c2_centering_geometry.py"),
]

# Known intentionally Drive-only artifacts (too heavy for ordinary Git text history).
DRIVE_ONLY = {
    "V52_T4C2_trial_results.csv",
    "V52_T4C2_BINARY_GEOMETRY.zip",
}

# Frozen adapters pinned by SHA256 in BOTH the 4C1 and 4C2 pre-run seals.
# Their raw bytes have not yet been materialized from the File Library. The moment they
# land in the repo this check turns them from an open gap into a verified binding.
ADAPTERS = {
    "adapters/longmemeval_v52_adapter.py":
        "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722",
    "adapters/longmemeval_v52_adapter_v2.py":
        "643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218",
}


def sha256_file(p: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def dig(obj, dotted: str):
    for part in dotted.split("."):
        obj = obj[part]
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print every checked path, not just problems")
    args = ap.parse_args()

    ok = mismatch = drive_only = absent = 0
    problems: list[str] = []

    for man in MANIFESTS:
        if not man.exists():
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

    print("\n== frozen adapters (pinned by 4C1 + 4C2 seals) ==")
    for rel, expected in sorted(ADAPTERS.items()):
        path = ROOT / rel
        if not path.exists():
            absent += 1
            print(f"  NOT YET IN GIT  {rel}\n    pinned {expected}")
            continue
        got = sha256_file(path)
        if got == expected:
            ok += 1
            print(f"  OK              {rel}")
        else:
            mismatch += 1
            problems.append(f"MISMATCH   {rel}\n    got      {got}\n    expected {expected}")
            print(f"  MISMATCH        {rel}")

    print("\n== cross-manifest bindings ==")
    for man, key, rel in BINDINGS:
        target = ROOT / rel
        if not man.exists() or not target.exists():
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

    print(f"\nmatch={ok}  mismatch={mismatch}  drive-only={drive_only}  absent={absent}")
    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print("  " + p)
    if mismatch:
        print(
            "\nCHAIN-OF-CUSTODY DEFECT. Do not interpret results until resolved.\n"
            "A mismatch is a packaging defect until the canonical Drive copy is\n"
            "independently checked. Never fix it by regenerating or reformatting the\n"
            "file -- restore the frozen bytes."
        )
        return 1
    print("\nAll committed frozen artifacts verified byte-for-byte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
