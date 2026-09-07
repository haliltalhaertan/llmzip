"""Independent sweep of the v3 test suite for conditions that cannot fail (CRITERION 2).

This is the auditor's OWN sweep. It is deliberately BROADER than the preparer's self-sweep, which
covers exactly one shape (a `check()` condition that is a boolean expression containing a literal
`True`). Shapes looked for here:

  V1  check(name, <BoolOp with a literal True among its values>)   - the preparer's named shape
  V2  check(name, True) / check(name, <any truthy literal>)        - a bare constant condition
  V3  check(name, <condition that constant-folds to a constant>)   - e.g. a comparison of literals
  V4  check(name, not <literal False>) and similar unary forms
  V5  expect_violation(..., needle="") or needle omitted           - "" is a substring of every
                                                                     message, so the message
                                                                     assertion is vacuous
  V6  check(...) called with fewer than two arguments
  V7  any `or True` / `and True` anywhere in the file, inside a check() or not

It also reports how many check() and expect_violation() calls exist, and cross-checks the
preparer's own sweep predicate against this file so the two can be compared directly.

Usage: python vacuity_sweep.py <path-to-test-file> [more test files...]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def const_fold(node):
    """Return (is_constant, value) if the expression is statically decidable, else (False, None)."""
    try:
        return True, ast.literal_eval(node)
    except Exception:                                             # noqa: BLE001
        pass
    if isinstance(node, ast.Compare):
        try:
            return True, bool(eval(compile(ast.Expression(node), "<c>", "eval"), {"__builtins__": {}}, {}))
        except Exception:                                         # noqa: BLE001
            return False, None
    return False, None


def sweep(path: Path):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    findings = []
    n_check = n_expect = 0
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Name):
            continue
        if n.func.id == "check":
            n_check += 1
            if len(n.args) < 2:
                findings.append(("V6", n.lineno, "check() called with fewer than 2 positional args",
                                 ast.get_source_segment(src, n)))
                continue
            cond = n.args[1]
            seg = (ast.get_source_segment(src, cond) or "").replace("\n", " ")[:130]
            if isinstance(cond, ast.BoolOp) and any(
                    isinstance(v, ast.Constant) and v.value is True for v in cond.values):
                findings.append(("V1", n.lineno, "boolean expression with a literal True operand", seg))
            elif isinstance(cond, ast.Constant):
                findings.append(("V2", n.lineno,
                                 f"bare constant condition {cond.value!r} - always "
                                 f"{'passes' if cond.value else 'fails'}", seg))
            elif isinstance(cond, ast.UnaryOp) and isinstance(cond.op, ast.Not) \
                    and isinstance(cond.operand, ast.Constant):
                findings.append(("V4", n.lineno, f"not {cond.operand.value!r} - constant", seg))
            else:
                folded, val = const_fold(cond)
                if folded:
                    findings.append(("V3", n.lineno, f"condition constant-folds to {val!r}", seg))
        elif n.func.id == "expect_violation":
            n_expect += 1
            needle = None
            if len(n.args) >= 3:
                needle = n.args[2]
            for kw in n.keywords:
                if kw.arg == "needle":
                    needle = kw.value
            if needle is None:
                findings.append(("V5", n.lineno, "expect_violation with NO needle - the message is "
                                                 "not asserted at all",
                                 (ast.get_source_segment(src, n) or "").replace("\n", " ")[:130]))
            elif isinstance(needle, ast.Constant) and needle.value == "":
                findings.append(("V5", n.lineno, "expect_violation with an EMPTY needle - '' is a "
                                                 "substring of every message",
                                 (ast.get_source_segment(src, n) or "").replace("\n", " ")[:130]))

    # V7 - textual scan for `or True` / `and True` anywhere, independent of the AST shape.
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.split("#", 1)[0]
        if " or True" in stripped or " and True" in stripped:
            findings.append(("V7", i, "literal `or True` / `and True` in code", stripped.strip()[:130]))
    return findings, n_check, n_expect, src, tree


def preparer_predicate(src: str):
    """Re-run the preparer's own sweep predicate over the given source, for direct comparison."""
    hits = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "check" \
                and len(n.args) >= 2:
            cond = n.args[1]
            if isinstance(cond, ast.Constant) and cond.value is True:
                continue
            if isinstance(cond, ast.BoolOp) and any(
                    isinstance(v, ast.Constant) and v.value is True for v in cond.values):
                hits.append(n.lineno)
    return hits


for arg in sys.argv[1:]:
    p = Path(arg).resolve()
    findings, n_check, n_expect, src, tree = sweep(p)
    print("=" * 100)
    print(f"FILE: {p}")
    print(f"  check() calls: {n_check}    expect_violation() calls: {n_expect}    "
          f"total assertions: {n_check + n_expect}")
    print(f"  preparer's own sweep predicate over this file reports lines: "
          f"{preparer_predicate(src) or 'NONE'}")
    print()
    if not findings:
        print("  auditor's sweep: NO findings in any of the shapes V1-V7.")
    else:
        for kind, line, why, seg in sorted(findings, key=lambda r: (r[0], r[1])):
            print(f"  [{kind}] line {line}: {why}")
            print(f"         {seg}")
    print()
raise SystemExit(0)
