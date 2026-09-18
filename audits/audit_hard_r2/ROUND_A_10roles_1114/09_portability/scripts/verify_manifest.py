"""Manifest vs workdir vs Git-blob verification (bounded sample for hashes).
Leaves original manifests unchanged (reads PUB manifest, compares to COPY only).
"""
import gzip
import hashlib
import json
import os
import subprocess

OWN = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/09_portability"
PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
REF = "findings/top10-comparison-2026-09-15"
REPO = "/mnt/c/Users/MDP/dev/llmzip"
out = {}

man = json.load(open(os.path.join(OWN, "evidence", "FILE_MANIFEST_copy.json")))
entries = man["files"]
out["manifest_entries"] = len(entries)
out["manifest_excluded"] = man.get("excluded")
out["manifest_label"] = man.get("_label")
out["manifest_note"] = man.get("note")

def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr[:500]}"
    return r.stdout

# Mechanical set comparison (no hashing = cheap, full coverage)
git_paths = [l for l in git("ls-tree", "-r", "--name-only", REF, "--",
                            "research_top10_comparison_2026_09_16").splitlines() if l]
git_rel = [p.split("/", 1)[1] for p in git_paths]
out["git_tracked_under_package"] = len(git_rel)

workdir_all = []
for root, dirs, files in os.walk(PUB):
    if "__pycache__" in root or ".pytest_cache" in root:
        continue
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
    for f in files:
        workdir_all.append(os.path.relpath(os.path.join(root, f), PUB))
out["workdir_files_excl_cache"] = len(workdir_all)

man_paths = [e["path"] for e in entries]
man_set, git_set, wd_set = set(man_paths), set(git_rel), set(workdir_all)
out["manifest_minus_git"] = sorted(man_set - git_set)[:30]
out["manifest_minus_git_count"] = len(man_set - git_set)
out["git_minus_manifest_count"] = len(git_set - man_set)
out["git_minus_manifest_sample"] = sorted(git_set - man_set)[:30]
out["workdir_minus_git_count"] = len(wd_set - git_set)
out["workdir_minus_git_sample"] = sorted(wd_set - git_set)[:20]
out["git_minus_workdir_count"] = len(git_set - wd_set)
out["git_minus_workdir_sample"] = sorted(git_set - wd_set)[:20]

# Bounded hash verification: 12 files spanning T1 path + scripts + JSONs
sample = [
    "coordinator/decision_tests.py",
    "coordinator/LADDER.json",
    "coordinator/DECISION_TESTS.json",
    "audit/audit_baseline_lib.py",
    "data/RT01.json",
    "data/RT10.json",
    "data/manifest.json",
    "coordinator/ladder.py",
    "coordinator/t3_perltqa_kltn.py",
    "ablation_r2/perltqa/t3_ladder.py",
    "PROTOCOL.md",
    "REPORT.md",
]
man_by_path = {e["path"]: e for e in entries}
rows = []
for rel in sample:
    e = man_by_path.get(rel)
    wp = os.path.join(PUB, rel)
    wb = open(wp, "rb").read()
    wsha = hashlib.sha256(wb).hexdigest()
    gb = subprocess.run(["git", "-C", REPO, "show", f"{REF}:research_top10_comparison_2026_09_16/{rel}"],
                        capture_output=True).stdout
    grows = []
    grows.append({"check": "workdir_sha_vs_manifest", "manifest": e["sha256"] if e else None,
                  "workdir": wsha, "match": bool(e) and e["sha256"] == wsha})
    grows.append({"check": "git_blob_vs_workdir_bytes", "git_bytes": len(gb), "workdir_bytes": len(wb),
                  "match": gb == wb})
    rows.append({"path": rel, "in_manifest": bool(e), "checks": grows})
out["sample_rows"] = rows
out["sample_all_match"] = all(c["match"] for r in rows for c in r["checks"])

# Gzip-stored entries: verify 2 of the 5 (decompress git blob, hash, compare to manifest)
for rel_gz_manifest, stored in [
    ("ablation_r2/perltqa/per_query.jsonl", "ablation_r2/perltqa/per_query.jsonl.gz"),
]:
    e = man_by_path.get(rel_gz_manifest)
    if e:
        gb = subprocess.run(["git", "-C", REPO, "show", f"{REF}:research_top10_comparison_2026_09_16/{stored}"],
                            capture_output=True).stdout
        dec = gzip.decompress(gb)
        out["gzip_check"] = {"manifest_path": rel_gz_manifest, "stored": stored,
                             "manifest_sha": e["sha256"], "decompressed_sha": hashlib.sha256(dec).hexdigest(),
                             "match": hashlib.sha256(dec).hexdigest() == e["sha256"],
                             "manifest_bytes": e["bytes"], "decompressed_bytes": len(dec)}

# ZIP scope: any top10 ZIP at research root?
import glob
out["research_root_zips"] = sorted(glob.glob("/mnt/c/Users/MDP/dev/llmzip-work/*.zip"))
out["top10_zip_present"] = any("top10" in z.lower() or "top-10" in z.lower() for z in out["research_root_zips"])

json.dump(out, open(os.path.join(OWN, "outputs", "manifest_verify.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("sample_rows",)}, indent=1)[:3000])
print("sample_all_match =", out["sample_all_match"])
for r in rows:
    print(r["path"], [(c["check"], c["match"]) for c in r["checks"]])
print("WROTE outputs/manifest_verify.json")
