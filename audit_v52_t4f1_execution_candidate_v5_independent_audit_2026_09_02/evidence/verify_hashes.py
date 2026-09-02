#!/usr/bin/env python3
"""Self-verification of INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json against the bytes on disk."""
import hashlib, json, sys
from pathlib import Path

AUD = Path(sys.argv[1]).resolve()
SELF = "INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json"
doc = json.loads((AUD / SELF).read_text(encoding="utf-8"))


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


on_disk = {p.relative_to(AUD).as_posix(): p for p in sorted(AUD.rglob("*")) if p.is_file()}
match, mismatch, missing = [], [], []
for rel, meta in sorted(doc["files"].items()):
    p = on_disk.get(rel)
    if p is None:
        missing.append(rel); continue
    got, size = sha(p), p.stat().st_size
    if got == meta["sha256"] and size == meta["bytes"]:
        match.append(rel)
    else:
        mismatch.append({"path": rel, "declared": meta, "actual": {"bytes": size, "sha256": got}})
undeclared = sorted(set(on_disk) - set(doc["files"]) - {SELF})
print(json.dumps({
    "hashes_file": SELF,
    "hashes_file_self_sha256": sha(AUD / SELF),
    "declared_recursive_output_count": doc["recursive_output_count"],
    "declared_entries": len(doc["files"]),
    "files_on_disk_total": len(on_disk),
    "match": len(match), "mismatch": mismatch, "missing": missing,
    "undeclared_on_disk": undeclared,
    "reverse_coverage_complete": not undeclared,
    "self_verification": f"{len(match)}/{len(doc['files'])} declared entries match on disk; "
                         f"{len(mismatch)} mismatch; {len(missing)} missing",
    "verified": not mismatch and not missing and not undeclared
               and len(doc["files"]) == doc["recursive_output_count"],
    "verdict_in_hashes_file": doc["verdict"],
}, indent=2))
