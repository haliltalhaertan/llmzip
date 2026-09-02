#!/usr/bin/env python3
"""Delta precondition 3: verify the materialized pinned BEAM corpus against the committed
pinned-tree manifest by reconstructing each Git blob SHA1 from the raw file bytes.
Outcome-free: hashes bytes only; opens no probing question for retrieval and ranks nothing."""
import hashlib, json, sys
from pathlib import Path

MANIFEST = Path(sys.argv[1]).resolve()
CORPUS = Path(sys.argv[2]).resolve()
doc = json.loads(MANIFEST.read_text(encoding="utf-8"))

def blob_sha1(path: Path, size: int) -> str:
    h = hashlib.sha1()
    h.update(b"blob " + str(size).encode() + b"\0")
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

ok, size_mismatch, id_mismatch, absent = 0, [], [], []
total_bytes = 0
for entry in doc["selected"]:
    p = CORPUS / entry["path"]
    if not p.is_file():
        absent.append(entry["path"]); continue
    actual_size = p.stat().st_size
    total_bytes += actual_size
    if actual_size != entry["size"]:
        size_mismatch.append({"path": entry["path"], "declared": entry["size"], "actual": actual_size})
        continue
    got = blob_sha1(p, actual_size)
    if got != entry["git_blob_sha1"]:
        id_mismatch.append({"path": entry["path"], "declared": entry["git_blob_sha1"], "actual": got})
    else:
        ok += 1

print(json.dumps({
    "manifest_path": str(MANIFEST),
    "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
    "declared_commit": doc["commit"],
    "declared_repository": doc["repository"],
    "declared_selected_blob_count": doc["selected_blob_count"],
    "declared_selected_total_bytes": doc["selected_total_bytes"],
    "observed_total_bytes": total_bytes,
    "blob_id_and_size_match": ok,
    "size_mismatch": size_mismatch,
    "blob_id_mismatch": id_mismatch,
    "absent_from_materialized_corpus": absent,
    "corpus_matches_pinned_manifest": ok == doc["selected_blob_count"]
                                      and not size_mismatch and not id_mismatch and not absent,
}, indent=2))
