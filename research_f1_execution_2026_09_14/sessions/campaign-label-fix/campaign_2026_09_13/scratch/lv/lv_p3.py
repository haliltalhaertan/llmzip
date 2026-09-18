"""Independent byte-hash recomputation: G3 remediation delivery package (P3)."""
import hashlib
import json
from pathlib import Path

PKG = Path("C:/Users/MDP/dev/llmzip-work/verify/g3/drafts/v52/membership_g3_remediation_2026_09_11")
CLAIM = "9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d"
LOG = Path("C:/Users/MDP/dev/llmzip-work/reports/logs/local_verify_p3.log")

lines = []


def emit(s=""):
    lines.append(s)
    print(s)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


emit("== P3 CHECK 1: sha256 of FILE_HASHES.json vs claimed manifest hash ==")
a = sha(PKG / "FILE_HASHES.json")
emit(f"claimed = {CLAIM}")
emit(f"actual  = {a}")
emit("RESULT: " + ("PASS MATCH" if a == CLAIM else "FAIL MISMATCH"))
emit()

emit("== P3 CHECK 2: recompute all declared file hashes (sha256 + bytes) ==")
man = json.loads((PKG / "FILE_HASHES.json").read_bytes())
emit("meta: " + json.dumps({k: v for k, v in man.items() if k != "files"}, sort_keys=True))
entries = man["files"]
declared_list = [e["path"] for e in entries]
dupes = sorted({d for d in declared_list if declared_list.count(d) > 1})
emit(f"declared_files={len(declared_list)} duplicate_paths={dupes}")
emit(f"declared_in_sorted_order={declared_list == sorted(declared_list)}")
matched = 0
mism = []
absent = []
for e in entries:
    f = PKG / e["path"]
    if not f.is_file():
        absent.append(e["path"])
        emit(f"ABSENT {e['path']}")
        continue
    aa = sha(f)
    sz = f.stat().st_size
    if aa == e["sha256"] and sz == e["bytes"]:
        matched += 1
    else:
        mism.append((e["path"], e["sha256"], aa, e["bytes"], sz))
        emit(f"MISMATCH {e['path']} expected_sha={e['sha256']} actual_sha={aa} expected_bytes={e['bytes']} actual_bytes={sz}")
emit(f"entries={len(entries)} matched={matched} mismatched={len(mism)} absent={len(absent)}")
emit()
emit("-- per-entry results (OK lines) --")
for e in entries:
    f = PKG / e["path"]
    if f.is_file() and sha(f) == e["sha256"]:
        emit(f"OK  {e['sha256']}  {e['path']}")
emit()

emit("== P3 CHECK 3: inventory coverage (byte manifest vs package dir) ==")
allfiles = sorted(p.relative_to(PKG).as_posix() for p in PKG.rglob("*") if p.is_file())
declared = set(declared_list)
extra = [x for x in allfiles if x not in declared and x != "FILE_HASHES.json"]
missing = [d for d in sorted(declared) if d not in set(allfiles)]
emit(f"files_on_disk={len(allfiles)} declared={len(declared)}")
emit(f"missing_on_disk={missing}")
emit(f"extra_not_declared={extra}")
emit("RESULT: " + ("PASS" if not missing and not extra else "FAIL"))

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
print()
print("full log written to", LOG)
print("log sha256 =", sha(LOG))
