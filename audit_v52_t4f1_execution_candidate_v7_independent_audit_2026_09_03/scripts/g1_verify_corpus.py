#!/usr/bin/env python3
"""Gate 1 support: verify the materialized BEAM tree against the committed pinned-tree manifest.

Outcome-free: reconstructs Git blob SHA1 from raw bytes and compares to the manifest.
Reads no probing question, computes no retrieval quality.
"""
import hashlib, json, sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
corpus_root = Path(sys.argv[2])
out_path = Path(sys.argv[3])

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

def git_blob_sha1(payload: bytes) -> str:
    header = b"blob " + str(len(payload)).encode() + b"\x00"
    return hashlib.sha1(header + payload).hexdigest()

checked = matched = missing = mismatched = 0
failures = []
for item in manifest["selected"]:
    p = corpus_root / item["path"]
    checked += 1
    if not p.is_file():
        missing += 1
        failures.append({"path": item["path"], "reason": "MISSING"})
        continue
    raw = p.read_bytes()
    got_sha1 = git_blob_sha1(raw)
    if got_sha1 == item["git_blob_sha1"] and len(raw) == item["size"]:
        matched += 1
    else:
        mismatched += 1
        failures.append({"path": item["path"], "reason": "MISMATCH",
                         "expected_sha1": item["git_blob_sha1"], "got_sha1": got_sha1,
                         "expected_size": item["size"], "got_size": len(raw)})

result = {
    "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    "manifest_commit": manifest["commit"],
    "selected_blob_count_declared": manifest["selected_blob_count"],
    "checked": checked, "matched": matched,
    "missing": missing, "mismatched": mismatched,
    "all_selected_blobs_verified": (matched == checked and checked == manifest["selected_blob_count"]),
    "failures": failures[:20],
}
out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "failures"}, indent=2, sort_keys=True))
