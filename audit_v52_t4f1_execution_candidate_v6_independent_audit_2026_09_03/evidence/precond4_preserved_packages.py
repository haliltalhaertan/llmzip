#!/usr/bin/env python3
"""Precondition 4: are the preserved V4/V5 audit packages and the V6 implementer
preflight package still authentic? Recompute every hash their own manifests assert."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

REPO = Path("/home/user/llmzip")
def sh(*a): return subprocess.run(a, capture_output=True, text=True, cwd=REPO).stdout.strip()
def blob_sha(commit, path):
    out = subprocess.run(["git", "cat-file", "blob", f"{commit}:{path}"],
                         capture_output=True, cwd=REPO)
    return hashlib.sha256(out.stdout).hexdigest() if out.returncode == 0 else None

report = {}

# --- declared audit commits exist and carry the declared manifest digests ---------
for label, commit, manifest, declared in [
    ("v4_audit", "641568d8b78af97eb69c9dc4e0434e7b6564a26c", None, None),
    ("v5_audit", "6243ba6d9fe1c3d059d78369d8fed3534d7921d0",
     "audit_v52_t4f1_execution_candidate_v5_independent_audit_2026_09_02/INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json",
     "0b7879e366d58f68022bc12826e820a23e7c2a1f4bf29c456fea70f7faf4af81"),
]:
    entry = {"commit_present": sh("git", "cat-file", "-t", commit) == "commit",
             "commit_subject": sh("git", "log", "-1", "--format=%s", commit)}
    if manifest:
        actual = blob_sha(commit, manifest)
        entry.update(manifest_sha256=actual, manifest_matches_declared=(actual == declared))
    report[label] = entry

for label, c in [("cochair_review", "776c45f333b262754aa0020e8043db54942d1bea"),
                 ("cochair_approval", "4bd32782c4148d15a632fb822dae8cab358892c6")]:
    report[label] = {"commit_present": sh("git", "cat-file", "-t", c) == "commit",
                     "subject": sh("git", "log", "-1", "--format=%s", c)}

# --- V5 audit manifest self-consistency at its own commit -------------------------
V5C = "6243ba6d9fe1c3d059d78369d8fed3534d7921d0"
V5NS = "audit_v52_t4f1_execution_candidate_v5_independent_audit_2026_09_02"
man = json.loads(subprocess.run(["git", "cat-file", "blob",
      f"{V5C}:{V5NS}/INDEPENDENT_V5_EXECUTION_AUDIT_HASHES.json"],
      capture_output=True, cwd=REPO).stdout)
def walk(o, out, pfx=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) == 64 and all(ch in "0123456789abcdef" for ch in v):
                out[f"{pfx}{k}"] = v
            else: walk(v, out, f"{pfx}{k}.")
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, out, f"{pfx}[{i}].")
entries = []
files = man.get("files")
if isinstance(files, dict):
    for name, rec in files.items():
        entries.append((name, rec["sha256"] if isinstance(rec, dict) else rec))
elif isinstance(files, list):
    for it in files:
        entries.append((it.get("name") or it.get("path"), it["sha256"]))
ok = bad = 0; mismatches = []
for name, declared in entries:
    actual = blob_sha(V5C, f"{V5NS}/{name}") or blob_sha(V5C, name)
    if actual == declared: ok += 1
    else: bad += 1; mismatches.append({"name": name, "declared": declared, "actual": actual})
report["v5_audit_manifest_self_consistency"] = {
    "entries_checked": len(entries), "verified": ok, "mismatched": bad, "mismatches": mismatches,
    "manifest_top_keys": sorted(man.keys())}

# --- V6 implementer preflight package ---------------------------------------------
pf = REPO / "task4f1_execution_candidate_v6_preflight_2026_09_03" / "PREFLIGHT_HASHES.json"
report["v6_implementer_preflight"] = {
    "path_exists": pf.is_file(),
    "sha256": hashlib.sha256(pf.read_bytes()).hexdigest() if pf.is_file() else None,
    "matches_declared": (hashlib.sha256(pf.read_bytes()).hexdigest() ==
        "4f6abc15917ea5d8ae7d06f69c7b223234d9a8123b0a1713bd1ec0dac63b73ad") if pf.is_file() else False,
}
# --- V4/V5/V6 candidate namespaces untouched by this audit -------------------------
report["candidate_namespaces_unmodified_working_tree"] = sh(
    "git", "status", "--porcelain",
    "task4f1_execution_candidate_v4_2026_09_01",
    "task4f1_execution_candidate_v5_2026_09_02",
    "task4f1_execution_candidate_v6_2026_09_03",
    "docs/v52/task4f1") == ""

Path(sys.argv[1]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps(report, indent=2, sort_keys=True))
