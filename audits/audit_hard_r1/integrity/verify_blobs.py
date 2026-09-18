"""Own-code worktree-vs-git-blob check (read-only, no clone).
For 10 sampled manifest entries + 4 key docs, compare worktree disk bytes
(as stored, i.e. .gz where gzipped) against `git show e672192:<path>` blobs.
"""
import subprocess, random, json, os

R = "/mnt/c/Users/MDP/dev/llmzip-work"
MAIN = "/mnt/c/Users/MDP/dev/llmzip"
PKG = os.path.join(R, "_wt_top10/research_top10_comparison_2026_09_16")
BR = "findings/top10-comparison-2026-09-15"
PREFIX = "research_top10_comparison_2026_09_16"

man = json.load(open(os.path.join(PKG, "FILE_MANIFEST.json")))
sample = random.Random(777).sample(man["files"], 10)
paths = [(PREFIX + "/" + e["stored"]) for e in sample]
paths += [PREFIX + "/REPORT.md", PREFIX + "/FINAL_STATE.md",
          PREFIX + "/coordinator/decision_tests.py",
          PREFIX + "/decision_r1/cost/REFEREE.md"]

ok = bad = missing_blob = 0
for gp in paths:
    disk = os.path.join(MAIN + "-work" if False else R, "")  # placeholder
    # disk path: worktree file
    rel = gp[len(PREFIX) + 1:]
    disk = os.path.join(PKG, rel)
    if not os.path.exists(disk):
        print(f"DISK-MISSING {rel}"); bad += 1; continue
    with open(disk, "rb") as f:
        diskbytes = f.read()
    q = subprocess.run(["git", "-C", MAIN, "show", f"{BR}:{gp}"],
                       capture_output=True)
    if q.returncode != 0:
        print(f"NO-BLOB {gp}: {q.stderr.decode()[:120]}")
        missing_blob += 1
        continue
    if q.stdout == diskbytes:
        ok += 1
    else:
        bad += 1
        print(f"BLOB-DIFF {gp} disk={len(diskbytes)} blob={len(q.stdout)}")
print(f"n={len(paths)} match={ok} diff={bad} no_blob={missing_blob}")
