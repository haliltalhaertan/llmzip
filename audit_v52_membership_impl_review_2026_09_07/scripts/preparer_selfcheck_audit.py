"""Audit of the PREPARER's own test suite: which of its checks can never fail?

A check whose asserted condition is a literal, a tautology, or a comparison that is true for every
possible value is not evidence. This script finds them statically, and separately reports how the
preparer's "forbidden token" self-check is scoped.

Usage: python preparer_selfcheck_audit.py <candidate_dir> [json-out]
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

CAND = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

TEST = CAND / "test_membership_scaling_core.py"
CORE = CAND / "membership_scaling_core.py"
tsrc = TEST.read_text(encoding="utf-8")
tlines = tsrc.splitlines()
tree = ast.parse(tsrc)

vacuous = []
for n in ast.walk(tree):
    if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "check"):
        continue
    if len(n.args) < 2:
        continue
    cond = n.args[1]
    why = None
    if isinstance(cond, ast.Constant) and cond.value is True:
        why = "the asserted condition is the literal True"
    elif isinstance(cond, ast.Compare) and len(cond.ops) == 1 and isinstance(cond.ops[0], ast.In) \
            and isinstance(cond.comparators[0], ast.Tuple):
        vals = {c.value for c in cond.comparators[0].elts
                if isinstance(c, ast.Constant)}
        if vals == {True, False}:
            why = "membership in (True, False) is true for every boolean, so nothing is asserted"
    if why:
        name = ast.literal_eval(n.args[0]) if isinstance(n.args[0], ast.Constant) else "<dynamic>"
        line = tlines[n.lineno - 1].strip()
        # Fair distinction: `m.f(...); check(name, True)` is assertion-by-non-raising -- the
        # preceding call carries the test and the literal True is only a reporting device.
        carried = line.split("check(")[0].strip().startswith("m.")
        vacuous.append({"line": n.lineno, "check_name": name, "reason": why,
                        "carried_by_a_preceding_call_that_would_raise": carried,
                        "asserts_nothing_at_all": not carried,
                        "source": line[:120]})

# How many checks are there, and how many are negative (expect_violation) vs positive?
n_check = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Name) and n.func.id == "check")
n_expect = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Name) and n.func.id == "expect_violation")

# Scope of the preparer's forbidden-token scan.
csrc = CORE.read_text(encoding="utf-8")
doc = ast.get_docstring(ast.parse(csrc)) or ""
scanned_body = csrc.split('"""', 2)[2]
scope = {
    "scan_expression": "src.lower().split('\\\"\\\"\\\"', 2)[2]",
    "module_docstring_chars_excluded_from_the_scan": len(doc),
    "chars_actually_scanned": len(scanned_body),
    "tokens_scanned": ["rho", "verdict", "accounts for most", "indeterminate",
                       "relative scale unsuitable"],
    "forbidden_strings_present_in_the_excluded_docstring":
        sorted(t for t in ["rho", "verdict", "accounts for most", "indeterminate",
                           "relative scale unsuitable", "ratio"] if t in doc.lower()),
    "function_docstrings_ARE_inside_the_scanned_region": "def scale_matrix" in scanned_body,
}

print(f"preparer's suite: {n_check} check() calls + {n_expect} expect_violation() calls")
print(f"vacuous checks found: {len(vacuous)}")
for v in vacuous:
    tag = "CARRIED BY A PRECEDING CALL" if v["carried_by_a_preceding_call_that_would_raise"] else "ASSERTS NOTHING"
    print(f"  L{v['line']} [{tag}]: {v['check_name']}")
    print(f"        reason: {v['reason']}")
    print(f"        source: {v['source']}")
print("\nforbidden-token self-check scope:")
for k, v in scope.items():
    print(f"  {k}: {v}")

payload = {"n_check_calls": n_check, "n_expect_violation_calls": n_expect,
           "vacuous_checks": vacuous, "forbidden_token_scan_scope": scope}
if OUT:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
