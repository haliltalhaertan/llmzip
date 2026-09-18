"""Own-code manifest spot check (integrity audit, read-only).
Samples 30 entries from FILE_MANIFEST.json (seed fixed) and verifies sha256
of worktree bytes. Manifest note: sha256 is of ORIGINAL uncompressed bytes;
entries whose `stored` ends with .gz are gunzipped before hashing.
No clone is made (per expanded responsibility: read-only git show / worktree reads).
"""
import json, hashlib, gzip, random, os, sys

PKG = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
MAN = os.path.join(PKG, "FILE_MANIFEST.json")

m = json.load(open(MAN))
files = m["files"]
rng = random.Random(20260917)
sample = rng.sample(files, 30)

ok = bad = missing = 0
for e in sample:
    p, want, stored = e["path"], e["sha256"], e["stored"]
    disk = os.path.join(PKG, stored)
    if not os.path.exists(disk):
        print(f"MISSING {p} (stored={stored})")
        missing += 1
        continue
    with open(disk, "rb") as f:
        raw = f.read()
    if stored.endswith(".gz"):
        raw = gzip.decompress(raw)
    got = hashlib.sha256(raw).hexdigest()
    if got == want:
        ok += 1
    else:
        bad += 1
        print(f"MISMATCH {p} want={want[:16]}.. got={got[:16]}.. bytes={e['bytes']}")
print(f"sample=30 ok={ok} mismatch={bad} missing={missing} manifest_n={len(files)}")
