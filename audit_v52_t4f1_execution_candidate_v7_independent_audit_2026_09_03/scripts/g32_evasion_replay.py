#!/usr/bin/env python3
"""Gate 3.2: replay the V6 evasion classes against V7 and classify the MECHANISM.

For each class the same payload is applied at three sites:
  (a) a re-added narrative file (EXECUTION_SPEC.md)  -> tests the set-equality check
  (b) an existing BOUND functional file              -> tests content freezing
  (c) the UNBOUND seal / relocated docs/ narrative   -> tests what is no longer covered
Outcome is classified as:
  BLOCKED_BY_SET_EQUALITY | BLOCKED_BY_HASH | NOT_APPLICABLE_NO_SUCH_BOUND_FILE | SURVIVES
"""
from __future__ import annotations
import hashlib, json, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safe_harness as H

REAL = Path("/home/user/llmzip/task4f1_execution_candidate_v7_2026_09_03")
WORK = Path(sys.argv[1]); PY = sys.argv[2]; OUT = Path(sys.argv[3])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

DEPRECATED = "d3c7aa09c9553cd5ac100e668923abab602e4257"  # a real anchor, used as the smuggled literal

PAYLOADS = {
    "line_wrapping":      DEPRECATED[:32] + "\n" + DEPRECATED[32:],
    "uppercase_hex":      DEPRECATED.upper(),
    "hex_adjacent_words": f"probe{DEPRECATED}and",
    "zero_width":         DEPRECATED[:20] + "​" + DEPRECATED[20:],
    "markup_interleave":  DEPRECATED[:20] + "<!-- x -->" + DEPRECATED[20:],
    "base64_reencode":    __import__("base64").b64encode(bytes.fromhex(DEPRECATED)).decode(),
    "decimal_reencode":   str(int(DEPRECATED, 16)),
    "split_json_keys":    None,   # handled structurally
    "non_utf8":           None,   # handled structurally
}

def reseal(root: Path) -> None:
    m = json.loads((root / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if rel in ("PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"):
            continue
        files.append({"bytes": p.stat().st_size, "name": rel, "sha256": sha(p)})
    m["files"] = files; m["file_count_excluding_inventory_and_seal"] = len(files)
    (root / "PAYLOAD_HASHES.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    s = json.loads((root / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    s["payload_inventory"]["sha256"] = sha(root / "PAYLOAD_HASHES.json")
    s["payload_inventory"]["bytes"] = (root / "PAYLOAD_HASHES.json").stat().st_size
    (root / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(s, indent=2, sort_keys=True) + "\n", encoding="utf-8")

RES = []
def trial(cls: str, site: str, apply_fn, do_reseal: bool):
    root = WORK / f"{cls}__{site}"
    if root.exists(): shutil.rmtree(root)
    shutil.copytree(REAL, root)
    detail = apply_fn(root) or ""
    if do_reseal: reseal(root)
    rec = H.run([PY, "-B", "candidate_package_preflight.py"], cwd=str(root))
    rc = rec.get("returncode", 1)
    err = (rec.get("stderr") or "")
    if rc != 0:
        if "BOUND PAYLOAD IS NOT FUNCTIONAL-ONLY" in err:
            mech = "BLOCKED_BY_SET_EQUALITY"
        elif "payload closure mismatch" in err:
            mech = "BLOCKED_BY_SET_EQUALITY"
        elif "payload mismatch" in err or "inventory binding" in err:
            mech = "BLOCKED_BY_HASH"
        else:
            mech = "BLOCKED_OTHER"
    else:
        mech = "SURVIVES"
    RES.append({"evasion_class": cls, "site": site, "resealed": do_reseal,
                "detail": detail, "checker_returncode": rc, "mechanism": mech,
                "checker_error": err.strip().splitlines()[-1][:200] if err.strip() else ""})
    shutil.rmtree(root, ignore_errors=True)

for cls, payload in PAYLOADS.items():
    # ---- site (a): re-add a narrative file carrying the evasion ----
    def add_narrative(root: Path, p=payload, c=cls):
        if c == "non_utf8":
            (root / "EXECUTION_SPEC.md").write_bytes(b"spec \xff\xfe " + DEPRECATED.encode())
        elif c == "split_json_keys":
            (root / "EXECUTION_SPEC.md").write_text(
                json.dumps({"a": DEPRECATED[:20], "b": DEPRECATED[20:]}), encoding="utf-8")
        else:
            (root / "EXECUTION_SPEC.md").write_text(f"# spec\nvalue {p}\n", encoding="utf-8")
        return "narrative file re-added to the package carrying the evasion payload"
    trial(cls, "a_readded_narrative_file", add_narrative, False)
    trial(cls, "a_readded_narrative_file_resealed", add_narrative, True)

    # ---- site (b): same payload inside an EXISTING bound functional file ----
    def into_bound_lock(root: Path, p=payload, c=cls):
        tgt = root / "DEPENDENCY_LOCK.txt"
        if c == "non_utf8":
            tgt.write_bytes(tgt.read_bytes() + b"\nsmuggled \xff\xfe " + DEPRECATED.encode())
        elif c == "split_json_keys":
            tgt.write_text(tgt.read_text(encoding="utf-8") + f"\na={DEPRECATED[:20]}\nb={DEPRECATED[20:]}\n", encoding="utf-8")
        else:
            tgt.write_text(tgt.read_text(encoding="utf-8") + f"\nsmuggled {p}\n", encoding="utf-8")
        return "evasion payload appended to a BOUND functional file"
    trial(cls, "b_bound_functional_file", into_bound_lock, False)
    trial(cls, "b_bound_functional_file_resealed", into_bound_lock, True)

    # ---- site (c): same payload inside the UNBOUND seal ----
    def into_seal(root: Path, p=payload, c=cls):
        s = json.loads((root / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
        if c == "split_json_keys":
            s["smuggled_a"] = DEPRECATED[:20]; s["smuggled_b"] = DEPRECATED[20:]
        else:
            s["smuggled_note"] = f"value {p if p else DEPRECATED}"
        (root / "CANDIDATE_EXECUTION_SEAL.json").write_text(
            json.dumps(s, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return "evasion payload placed in the UNBOUND seal (excluded from the inventory)"
    trial(cls, "c_unbound_seal", into_seal, False)

OUT.write_text(json.dumps({
    "deprecated_literal_used": DEPRECATED,
    "trial_count": len(RES),
    "survivors": [r for r in RES if r["mechanism"] == "SURVIVES"],
    "survivor_count": sum(1 for r in RES if r["mechanism"] == "SURVIVES"),
    "results": RES,
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

from collections import Counter
print("mechanism tally:", dict(Counter(r["mechanism"] for r in RES)))
print()
for r in RES:
    mark = "!!" if r["mechanism"] == "SURVIVES" else "  "
    print(f"{mark} {r['evasion_class']:20s} {r['site']:36s} {r['mechanism']}")
