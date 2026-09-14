"""Independent byte-hash recomputation: ITQ/Haar objective comparison package (P2)."""
import hashlib
import json
from pathlib import Path

PKG = Path("C:/Users/MDP/dev/llmzip-work/verify/itq_haar/research/v52/itq_haar_objective_comparison_2026_09_12")
CLAIM = "70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f"
LOG = Path("C:/Users/MDP/dev/llmzip-work/reports/logs/local_verify_p2.log")
P1_CROSS = {
    "source/itq_feasibility_synthetic.py": "18ddc99dfe57e93f949ea55b2e1c9cae402c9204d1db99bb82d0a2014a30973d",
    "source/PLAN.json": "e56ea0d6858e06211fa9eb82d6d255724a3d0e23016b77d28f8d8ff10923c53f",
    "source/RESULTS.json": "0c2cf96553dbf448d22def0538c8993ada038d1fdac52665f759c08e5a304214",
}

lines = []


def emit(s=""):
    lines.append(s)
    print(s)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


emit("== P2 CHECK 1: sha256 of FILE_HASHES.json vs claimed manifest hash ==")
a = sha(PKG / "FILE_HASHES.json")
emit(f"claimed = {CLAIM}")
emit(f"actual  = {a}")
emit("RESULT: " + ("PASS MATCH" if a == CLAIM else "FAIL MISMATCH"))
emit()

emit("== P2 CHECK 2: recompute all declared file hashes (sha256 + bytes) ==")
man = json.loads((PKG / "FILE_HASHES.json").read_bytes())
files = man["files"]
emit(f"manifest keys={sorted(man.keys())} self_excluded={man['self_excluded']!r} declared_files={len(files)}")
matched = 0
mism = []
absent = []
for rel, e in sorted(files.items()):
    f = PKG / rel
    if not f.is_file():
        absent.append(rel)
        emit(f"ABSENT {rel}")
        continue
    aa = sha(f)
    sz = f.stat().st_size
    if aa == e["sha256"] and sz == e["bytes"]:
        matched += 1
    else:
        mism.append((rel, e["sha256"], aa, e["bytes"], sz))
        emit(f"MISMATCH {rel} expected_sha={e['sha256']} actual_sha={aa} expected_bytes={e['bytes']} actual_bytes={sz}")
emit(f"entries={len(files)} matched={matched} mismatched={len(mism)} absent={len(absent)}")
emit()
emit("-- per-entry results (OK lines) --")
for rel, e in sorted(files.items()):
    f = PKG / rel
    if f.is_file() and sha(f) == e["sha256"]:
        emit(f"OK  {e['sha256']}  {rel}")
emit()

emit("== P2 CHECK 3: inventory coverage (byte manifest vs package dir) ==")
allfiles = sorted(p.relative_to(PKG).as_posix() for p in PKG.rglob("*") if p.is_file())
declared = set(files)
extra = [x for x in allfiles if x not in declared and x != "FILE_HASHES.json"]
missing = [d for d in sorted(declared) if d not in set(allfiles)]
emit(f"files_on_disk={len(allfiles)} declared={len(declared)} other_than_manifest={len(allfiles) - 1}")
emit(f"missing_on_disk={missing}")
emit(f"extra_not_declared={extra}")
emit("RESULT: " + ("PASS" if not missing and not extra else "FAIL"))
emit()

emit("== P2 CHECK 4: cross-links to P1 namespace bytes ==")
for rel, exp in P1_CROSS.items():
    act = sha(PKG / rel)
    emit(f"{rel}: p1_expected={exp} actual={act} " + ("MATCH" if act == exp else "MISMATCH"))
emit()

emit("== P2 CHECK 5: declared duplicate-content groups ==")


def pair(x, y):
    s1 = sha(PKG / x)
    s2 = sha(PKG / y)
    emit(f"{x} vs {y}: {s1} {s2} " + ("IDENTICAL" if s1 == s2 else "DIFFER"))


pair("replay/objectives.csv", "review_agent/objectives.csv")
pair("replay/RESULTS.json", "review_agent/RESULTS.json")
pair("replay/ENVIRONMENT.json", "review_agent/ENVIRONMENT.json")

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
print()
print("full log written to", LOG)
print("log sha256 =", sha(LOG))
