"""Read-only draft/source/inventory check; --write creates the initial manifest.

Checks artifact identity only. Does not run a model, validate cost measurements,
grant approval, access corpus data or change any experiment authorization.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FILE_HASHES.json"

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def inventory():
    return {p.relative_to(ROOT).as_posix(): {"sha256": sha(p.read_bytes()),
            "bytes": p.stat().st_size}
            for p in sorted(ROOT.rglob("*")) if p.is_file() and p != MANIFEST}

def require(ok, message):
    if not ok:
        raise SystemExit("DRAFT_IDENTITY: FAIL - " + message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    binding = json.loads((ROOT / "SOURCE_BINDINGS.json").read_bytes())
    for item in binding["sources"]:
        p = (ROOT / item["local_path"]).resolve()
        require(ROOT in p.parents, "source outside package")
        raw = p.read_bytes()
        require(sha(raw) == item["sha256"] and len(raw) == item["bytes"], item["local_path"])
    source = binding["sources"][0]
    require(source["sha256"] == "1832f4b368024edba4a7f5d2d3f925e9c9b1c53367f1a4ed54b7586b2ec8cc26", "budget pin")
    sidecar = (ROOT / binding["sources"][1]["local_path"]).read_text(encoding="utf-8")
    require(source["sha256"] in sidecar, "budget sidecar")
    draft = (ROOT / "MEASUREMENT_CONTRACT_TR.md").read_bytes()
    review = (ROOT / "INDEPENDENT_DESIGN_DELTA_REVIEW.md").read_text(encoding="utf-8")
    require(sha(draft) in review.lower(), "delta review does not identify current draft bytes")
    require(len(re.findall(r"^## [1-5]\. ", draft.decode(), re.M)) == 5, "five-question structure")
    if args.write:
        with MANIFEST.open("x", encoding="utf-8", newline="\n") as f:
            json.dump({"self_excluded": "FILE_HASHES.json", "files": inventory()}, f, indent=2)
            f.write("\n")
    expected = json.loads(MANIFEST.read_bytes())
    require(expected == {"self_excluded": "FILE_HASHES.json", "files": inventory()}, "missing/extra/changed file")
    print(f"DRAFT_IDENTITY: PASS ({len(expected['files'])} files; not scientific approval)")
    print("draft_sha256=" + sha(draft))
    print("manifest_sha256=" + sha(MANIFEST.read_bytes()))
