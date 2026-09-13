"""Independent byte-hash recomputation: preseal diagnostics namespace (P1).

Checks:
 1. sha256(HASHES.txt) vs claimed manifest hash.
 2. Recompute every hash listed in HASHES.txt (self-excluded inventory).
 3. Coverage: every namespace file except HASHES.txt declared, no extras.
 4. Recompute task2/HASHES.txt and task3/HASHES.json declared hashes.
 5. Cross-check resolved paths stay inside the namespace.
"""
import hashlib
import json
from pathlib import Path

NS = Path("C:/Users/MDP/dev/llmzip-work/verify/preseal/research/v52/preseal_diagnostics_2026_09_12")
CLAIM = "5bf22716a82139ce59b35def4a10488904288fdda4ab8032e7ba62c49341780b"
LOG = Path("C:/Users/MDP/dev/llmzip-work/reports/logs/local_verify_p1.log")

lines = []


def emit(s=""):
    lines.append(s)
    print(s)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_sums(p: Path):
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        h, rest = line.split(None, 1)
        rest = rest.strip()
        if rest.startswith("*"):
            rest = rest[1:]
        out.append((rest, h))
    return out


# ---- CHECK 1
emit("== P1 CHECK 1: sha256 of HASHES.txt vs claimed manifest hash ==")
actual = sha(NS / "HASHES.txt")
emit(f"claimed = {CLAIM}")
emit(f"actual  = {actual}")
emit("RESULT: " + ("PASS MATCH" if actual == CLAIM else "FAIL MISMATCH"))
emit()

# ---- CHECK 2
emit("== P1 CHECK 2: recompute all hashes declared in HASHES.txt ==")
entries = parse_sums(NS / "HASHES.txt")
seen = set()
dupes = []
matched = 0
mism = []
absent = []
for r, h in entries:
    if r in seen:
        dupes.append(r)
    seen.add(r)
    f = NS / r
    if not f.is_file():
        absent.append((r, h))
        emit(f"ABSENT {r} expected={h}")
        continue
    a = sha(f)
    if a == h:
        matched += 1
    else:
        mism.append((r, h, a))
        emit(f"MISMATCH {r} expected={h} actual={a}")
for d in sorted(set(dupes)):
    emit(f"DUPLICATE {d}")
emit(f"entries={len(entries)} matched={matched} mismatched={len(mism)} absent={len(absent)} duplicate_entries={len(dupes)}")
emit()
emit("-- per-entry results (OK lines) --")
for r, h in entries:
    f = NS / r
    if f.is_file() and sha(f) == h:
        emit(f"OK  {h}  {r}")
emit()

# ---- CHECK 3
emit("== P1 CHECK 3: HASHES.txt coverage semantics (all namespace files except itself) ==")
allfiles = {p.relative_to(NS).as_posix() for p in NS.rglob("*") if p.is_file()}
expected = allfiles - {"HASHES.txt"}
declared = {r for r, _ in entries}
missing = sorted(expected - declared)
extra = sorted(declared - expected)
emit(f"files_in_namespace={len(allfiles)} (including HASHES.txt)")
emit(f"expected_declared={len(expected)} actual_declared={len(declared)}")
emit(f"missing_from_manifest={missing}")
emit(f"extra_in_manifest={extra}")
emit("RESULT: " + ("PASS complete self-excluded inventory" if not missing and not extra else "FAIL incomplete inventory"))
emit()

# ---- CHECK 4
def check_manifest(path: Path, kind: str):
    emit(f"== P1 CHECK 4: {path.relative_to(NS).as_posix()} ({kind}) ==")
    if kind == "txt":
        items = parse_sums(path)
    else:
        data = json.loads(path.read_bytes())
        emit("meta: " + json.dumps({k: v for k, v in data.items() if k != "files"}, sort_keys=True))
        items = [(k, v["sha256"]) for k, v in data["files"].items()]
    bases = [NS, path.parent]
    base = None
    for cand in bases:
        if all((cand / r).is_file() for r, _ in items):
            base = cand
            break
    if base is None:
        base = NS
        emit("NOTE: no single base resolves all entries; resolving per entry")
    emit(f"base={base}")
    m = 0
    mism2 = []
    absent2 = []
    resolved = {}
    for r, h in items:
        f = base / r
        if not f.is_file():
            alts = [b for b in bases if (b / r).is_file()]
            if alts:
                f = alts[0]
            else:
                absent2.append((r, h))
                emit(f"ABSENT {r} expected={h}")
                continue
        rp = f.resolve()
        resolved[r] = rp
        if NS.resolve() not in rp.parents and rp != NS.resolve():
            emit(f"OUTSIDE-NAMESPACE {r} -> {rp}")
        a = sha(rp)
        if a == h:
            m += 1
        else:
            mism2.append((r, h, a))
            emit(f"MISMATCH {r} expected={h} actual={a}")
    emit(f"entries={len(items)} matched={m} mismatched={len(mism2)} absent={len(absent2)}")
    emit("-- per-entry results (OK lines) --")
    for r, h in items:
        rp = resolved.get(r)
        if rp is not None and sha(rp) == h:
            emit(f"OK  {h}  {r}")
    emit()


check_manifest(NS / "task2" / "HASHES.txt", "txt")
check_manifest(NS / "task3" / "HASHES.json", "json")

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
print()
print("full log written to", LOG)
print("log sha256 =", sha(LOG))
