import json, hashlib, os, sys

root = sys.argv[1]
os.chdir(root)
m = json.load(open("PAYLOAD_HASHES.json"))
print("status", m.get("status"), "base", m.get("base_commit"))
for k, v in m.items():
    if k != "files":
        print("META", k, "=", repr(v)[:300])
files = m["files"]
if isinstance(files, dict):
    entries = [{"path": k, "sha256": v} for k, v in files.items()]
else:
    entries = files
print("manifest entries:", len(entries))
bad = []
listed = set()
for e in entries:
    p = e["path"] if isinstance(e, dict) else e
    h = e.get("sha256") if isinstance(e, dict) else None
    listed.add(p)
    if not os.path.exists(p):
        bad.append((p, "MISSING"))
        continue
    a = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if h and a != h:
        bad.append((p, "MISMATCH", h, a))
print("mismatches:", bad)
onfs = set()
sep = os.sep
for r, d, f in os.walk("."):
    for x in f:
        rel = os.path.relpath(os.path.join(r, x), ".")
        onfs.add(rel.replace(sep, "/"))
print("on-disk not listed:", sorted(onfs - listed))
print("listed not on disk:", sorted(listed - onfs))
