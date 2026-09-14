"""Verify complete package inventory, excluding only this manifest itself.

--write is a packaging operation; ordinary verification is read-only.
Use a disposable package copy for fresh numerical replay output: new output
is deliberately an extra file relative to the original frozen inventory.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FILE_HASHES.json"

def inventory():
    return {p.relative_to(ROOT).as_posix(): {
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "bytes": p.stat().st_size,
    } for p in sorted(ROOT.rglob("*")) if p.is_file() and p != MANIFEST}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        with MANIFEST.open("x", encoding="utf-8", newline="\n") as f:
            json.dump({"self_excluded": "FILE_HASHES.json", "files": inventory()}, f, indent=2)
            f.write("\n")
    expected = json.loads(MANIFEST.read_bytes())
    if expected != {"self_excluded": "FILE_HASHES.json", "files": inventory()}:
        raise SystemExit("PACKAGE: FAIL - missing, extra or changed file")
    print(f"PACKAGE: PASS - {len(expected['files'])} files")
    print("manifest_sha256=" + hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
