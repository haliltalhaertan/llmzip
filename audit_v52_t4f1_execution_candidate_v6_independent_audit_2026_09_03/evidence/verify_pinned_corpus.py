#!/usr/bin/env python3
"""Verify the materialized BEAM working tree against the committed pinned-tree manifest.

Recomputes each selected blob's git SHA-1 and size from the bytes on disk. No corpus
content is read into the report; only identity is checked.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

BEAM = Path("/tmp/claude-0/-home-user-llmzip/d56815f4-8a56-5a41-b42c-9e65664693e2/scratchpad/BEAM")
MAN = Path("/home/user/llmzip/audit_v52_t4f0_codex_2026_08_31/pinned_tree_manifest.json")

man = json.loads(MAN.read_text())
manifest_sha = hashlib.sha256(MAN.read_bytes()).hexdigest()

def git_blob_sha1(p: Path) -> str:
    data = p.read_bytes()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()

missing, mismatched, ok = [], [], 0
total_bytes = 0
for e in man["selected"]:
    p = BEAM / e["path"]
    if not p.is_file():
        missing.append(e["path"]); continue
    size = p.stat().st_size
    sha1 = git_blob_sha1(p)
    if size != e["size"] or sha1 != e["git_blob_sha1"]:
        mismatched.append({"path": e["path"], "expected_sha1": e["git_blob_sha1"], "actual_sha1": sha1,
                           "expected_size": e["size"], "actual_size": size})
    else:
        ok += 1; total_bytes += size

report = {
    "manifest_path": str(MAN.relative_to("/home/user/llmzip")),
    "manifest_sha256": manifest_sha,
    "manifest_sha256_matches_declared_anchor":
        manifest_sha == "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318",
    "declared_commit": man["commit"],
    "materialized_commit": (BEAM / ".git" / "HEAD").exists() and
        __import__("subprocess").run(["git", "-C", str(BEAM), "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip(),
    "selected_blob_count_declared": man["selected_blob_count"],
    "selected_blobs_verified": ok,
    "selected_blobs_missing": missing,
    "selected_blobs_mismatched": mismatched,
    "selected_total_bytes_declared": man["selected_total_bytes"],
    "selected_total_bytes_observed": total_bytes,
    "corpus_matches_pinned_manifest": (not missing and not mismatched and ok == man["selected_blob_count"]),
}
Path(sys.argv[1]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
for k, v in report.items():
    print(f"{k}: {v if not isinstance(v, list) else f'{len(v)} entries'}")
