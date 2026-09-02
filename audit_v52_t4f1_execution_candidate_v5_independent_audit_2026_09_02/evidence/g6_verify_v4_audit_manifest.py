#!/usr/bin/env python3
"""Delta precondition 4 / Gate 6: verify the V4 independent-audit package and its manifest
remain authentic at the declared commit. Re-derives every hash from the checked-out bytes."""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
HASHES = ROOT / "INDEPENDENT_V4_EXECUTION_AUDIT_HASHES.json"
doc = json.loads(HASHES.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# locate the mapping of relative path -> sha256 wherever the document keeps it
def collect(node, out, prefix=""):
    if isinstance(node, dict):
        if "sha256" in node and isinstance(node.get("sha256"), str) and (
                "path" in node or "name" in node or "file" in node):
            out[node.get("path") or node.get("name") or node.get("file")] = node["sha256"]
            return
        for k, v in node.items():
            if isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v) \
               and ("/" in k or k.endswith((".json", ".md", ".csv", ".txt", ".py"))):
                out[k] = v
            else:
                collect(v, out, prefix + "/" + str(k))
    elif isinstance(node, list):
        for item in node:
            collect(item, out, prefix)


declared = {}
collect(doc, declared)
declared.pop("INDEPENDENT_V4_EXECUTION_AUDIT_HASHES.json", None)

on_disk = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(ROOT.rglob("*")) if p.is_file()}
on_disk_wo_self = {k: v for k, v in on_disk.items() if k != "INDEPENDENT_V4_EXECUTION_AUDIT_HASHES.json"}

match, mismatch, missing = [], [], []
for path, want in sorted(declared.items()):
    got = on_disk.get(path)
    if got is None:
        missing.append(path)
    elif got == want:
        match.append(path)
    else:
        mismatch.append({"path": path, "declared": want, "actual": got})

undeclared = sorted(set(on_disk_wo_self) - set(declared))
print(json.dumps({
    "v4_audit_namespace": ROOT.name,
    "hashes_file_self_sha256": sha(HASHES),
    "declared_entry_count": len(declared),
    "files_on_disk_excluding_hashes_file": len(on_disk_wo_self),
    "match": len(match), "mismatch": mismatch, "missing": missing,
    "undeclared_on_disk": undeclared,
    "reverse_coverage_complete": not undeclared,
    "manifest_authentic": not mismatch and not missing and not undeclared,
    "declared_paths": sorted(declared),
    "top_level_keys": sorted(doc.keys()),
}, indent=2))
