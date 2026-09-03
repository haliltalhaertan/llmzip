#!/usr/bin/env python3
"""Gate 3.3/3.7 + Gate 7: which concepts can the sweep actually police?

A concept is policed only if some part of its value is shaped like one of the three
token patterns AND that shape is declared in scannable_literals. Everything else is
declared but unenforced: the gate can neither detect its relocation nor its drift.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

CAND = Path("/home/user/llmzip/task4f1_execution_candidate_v6_2026_09_03")
smap = json.loads((CAND / "NORMATIVE_SOURCE_MAP.json").read_text())
PATTERNS = (re.compile(r"^[0-9a-f]{64}$"), re.compile(r"^[0-9a-f]{40}$"),
            re.compile(r"^v52_t4f[0-9][a-z0-9_]*$"))

def token_shaped(s: str) -> bool:
    return any(p.match(s.casefold()) for p in PATTERNS)

def atoms(v):
    """Flatten a declared value into the scalar literals a reader would have to trust."""
    if isinstance(v, dict):
        for x in v.values(): yield from atoms(x)
    elif isinstance(v, list):
        for x in v: yield from atoms(x)
    else:
        yield v

rows, policed, unpoliced = [], [], []
for f in smap["fields"]:
    vals = [a for a in atoms(f.get("value")) if a is not None]
    shaped = [str(a) for a in vals if isinstance(a, str) and token_shaped(a)]
    declared = f.get("scannable_literals", [])
    unshaped = [a for a in vals if not (isinstance(a, str) and token_shaped(a))]
    covered = sorted({s.casefold() for s in shaped} & {d.casefold() for d in declared})
    shaped_but_undeclared = sorted({s.casefold() for s in shaped} - {d.casefold() for d in declared})
    row = {
        "concept": f["concept"],
        "mirrors_declared": len(f.get("mirrors", [])),
        "value_atoms": len(vals),
        "atoms_token_shaped": len(shaped),
        "atoms_NOT_token_shaped": len(unshaped),
        "scannable_literals_declared": len(declared),
        "shaped_atoms_covered_by_sweep": covered,
        "shaped_atoms_MISSING_from_scannable_literals": shaped_but_undeclared,
        "unenforceable_atoms": [str(a)[:60] for a in unshaped],
        "policed_by_sweep": bool(covered),
    }
    rows.append(row)
    (policed if row["policed_by_sweep"] else unpoliced).append(f["concept"])

summary = {
    "concepts_total": len(rows),
    "concepts_policed_by_sweep": len(policed),
    "concepts_NOT_policed_by_sweep": len(unpoliced),
    "unpoliced_concepts": unpoliced,
    "value_atoms_total": sum(r["value_atoms"] for r in rows),
    "value_atoms_token_shaped": sum(r["atoms_token_shaped"] for r in rows),
    "value_atoms_outside_every_token_shape": sum(r["atoms_NOT_token_shaped"] for r in rows),
    "shaped_atoms_missing_from_scannable_literals":
        sorted({t for r in rows for t in r["shaped_atoms_MISSING_from_scannable_literals"]}),
    "gate_verifies_scannable_literals_match_declared_value": False,
    "gate_verifies_declared_mirror_actually_contains_value": False,
}
Path(sys.argv[1]).write_text(json.dumps({"summary": summary, "concepts": rows}, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, indent=2))
print("\nUnpoliced concepts and the values that ride on them:")
for r in rows:
    if not r["policed_by_sweep"]:
        print(f"  {r['concept']:34} {r['atoms_NOT_token_shaped']:2d} unenforceable atoms  e.g. {r['unenforceable_atoms'][:4]}")
