#!/usr/bin/env python3
"""Independent re-derivation of the V6 sweep.

The gate normalises (strips ALL whitespace, casefolds) and THEN applies patterns
carrying hex lookarounds. Stripping whitespace destroys the very boundaries the
lookarounds rely on. This sweeper re-derives the token set the gate CLAIMS to
police, using boundaries that survive normalisation, and reports what the gate
actually sees versus what is really there.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

CAND = Path("/home/user/llmzip/task4f1_execution_candidate_v6_2026_09_03")

GATE_PATTERNS = (
    re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])"),
    re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])"),
    re.compile(r"v52_t4f[0-9][a-z0-9_]*"),
)
# Same shapes, but anchored on real lexical boundaries in the RAW text.
TRUE_PATTERNS = (
    re.compile(r"(?<![0-9A-Za-z])[0-9a-fA-F]{64}(?![0-9A-Za-z])"),
    re.compile(r"(?<![0-9A-Za-z])[0-9a-fA-F]{40}(?![0-9A-Za-z])"),
    re.compile(r"v52_t4f[0-9][a-z0-9_]*", re.I),
)

def normalise(t: str) -> str:
    return re.sub(r"\s+", "", t).casefold()

def gate_view(text: str) -> set[str]:
    h = normalise(text)
    out = set()
    for p in GATE_PATTERNS:
        out.update(p.findall(h))
    return out

def true_view(text: str) -> set[str]:
    out = set()
    for p in TRUE_PATTERNS:
        out.update(m.casefold() for m in p.findall(text))
    # also catch digests wrapped across lines, the way the gate intends to
    h = normalise(text)
    for p in TRUE_PATTERNS[:2]:
        out.update(m.casefold() for m in p.findall(h))
    return out

manifest = json.loads((CAND / "PAYLOAD_HASHES.json").read_text())
bound = sorted({i["name"] for i in manifest["files"]} | {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"})

source_map = json.loads((CAND / "NORMATIVE_SOURCE_MAP.json").read_text())
attribution = {}
for f in source_map["fields"]:
    permitted = {f["authoritative_path"], *(m["path"] for m in f.get("mirrors", []))}
    for lit in f.get("scannable_literals", []):
        attribution[normalise(lit)] = (f["concept"], permitted)

report = {"files": {}, "invisible_tokens": [], "summary": {}}
total_invisible = 0
for name in bound:
    p = CAND / name
    try:
        raw = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        report["files"][name] = {"unreadable": True}
        continue
    # the gate substitutes a re-serialised map with fields/deprecated_literals removed
    if name == "NORMATIVE_SOURCE_MAP.json":
        reg = dict(source_map); reg.pop("fields", None); reg.pop("deprecated_literals", None)
        text = json.dumps(reg, indent=2, sort_keys=True)
    else:
        text = raw
    g, t = gate_view(text), true_view(text)
    missed = sorted(t - g)
    report["files"][name] = {"gate_sees": len(g), "actually_present": len(t), "invisible_to_gate": missed}
    for tok in missed:
        total_invisible += 1
        known = attribution.get(tok)
        report["invisible_tokens"].append({
            "file": name, "token": tok,
            "attributed_concept": known[0] if known else None,
            "permitted_here": (name in known[1]) if known else False,
        })

report["summary"] = {
    "bound_payloads": len(bound),
    "tokens_invisible_to_gate": total_invisible,
    "invisible_and_unattributed": sum(1 for r in report["invisible_tokens"] if r["attributed_concept"] is None),
    "invisible_and_at_non_permitted_path": sum(
        1 for r in report["invisible_tokens"] if r["attributed_concept"] and not r["permitted_here"]),
}
Path(sys.argv[1]).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps(report["summary"], indent=2))
for r in report["invisible_tokens"]:
    print(f"  INVISIBLE {r['file']:32} {r['token'][:24]}...  concept={r['attributed_concept']} permitted_here={r['permitted_here']}")
