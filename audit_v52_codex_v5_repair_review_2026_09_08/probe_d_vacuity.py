"""Probe D -- item 2: are the candidate's own checks capable of failing?

Two independent methods.

  D-A  STATIC SWEEP: every check(...) call in both candidate suites is parsed; its
       condition is evaluated for compile-time constancy (literal-only expression,
       comparison of two distinct literals, `and True`, iteration over an empty
       literal, etc.).

  D-B  MUTATION TEST: the candidate package is copied into a fresh temp tree, ONE
       defect is reintroduced per mutant, and both suites are re-run IN AN ISOLATED
       SUBPROCESS against the mutant tree. A check that cannot fail will not notice.
       No candidate file is modified: everything happens on a temp copy.

Usage: python -B probe_d_vacuity.py <worktree drafts/v52 dir> <python exe>
"""
from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

V52 = Path(sys.argv[1]).resolve()
PYEXE = sys.argv[2]
PKGNAME = "membership_runner_ingest_codex_v5_2026_09_08"
PKG = V52 / PKGNAME
SUITES = ["test_runner_ingest_v4.py", "test_codex_v5.py"]

print("=" * 100)
print("D-A  STATIC SWEEP for checks that cannot fail")
print("=" * 100)


def constant_ish(node):
    """True if the expression can be decided without running any candidate code."""
    for sub in ast.walk(node):
        if isinstance(sub, (ast.Call, ast.Name, ast.Attribute, ast.Subscript)):
            return False
    return True


def empty_iteration(node):
    hits = []
    for sub in ast.walk(node):
        if isinstance(sub, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            for gen in sub.generators:
                it = gen.iter
                if isinstance(it, (ast.List, ast.Tuple, ast.Set)) and not it.elts:
                    hits.append(ast.unparse(sub))
                if isinstance(it, ast.ListComp) and isinstance(it.generators[0].iter,
                                                               (ast.List, ast.Tuple)) \
                        and not it.generators[0].iter.elts:
                    hits.append(ast.unparse(sub))
    return hits


def literal_only_compare(node):
    """`A.value != B.value` style comparisons of two fixed module constants."""
    if not isinstance(node, ast.Compare):
        return False
    parts = [node.left] + node.comparators
    return all(isinstance(p, (ast.Attribute, ast.Constant)) for p in parts) and \
        all(not isinstance(p, ast.Call) for p in parts)


total = 0
flagged = []
for suite in SUITES:
    tree = ast.parse((PKG / suite).read_text(encoding="utf-8"), filename=suite)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "check" and len(node.args) >= 2):
            continue
        total += 1
        label, cond = node.args[0], node.args[1]
        lab = ast.unparse(label)[:70]
        why = []
        if constant_ish(cond):
            why.append("condition contains no call/name/attribute -- decided at parse time")
        for e in empty_iteration(cond):
            why.append("comprehension over an EMPTY literal: " + e[:80])
        src = ast.unparse(cond)
        if src.rstrip().endswith(" and True") or src.rstrip() == "True":
            why.append("conjunct with a literal True")
        if why:
            flagged.append((suite, node.lineno, lab, why))

print("check() calls parsed:", total)
if flagged:
    for suite, ln, lab, why in flagged:
        print("  FLAG %s:%d  %s" % (suite, ln, lab))
        for w in why:
            print("        - " + w)
else:
    print("  no check() call is decided at parse time; none iterates an empty literal")

# The weaker category: a check whose condition compares two module constants.
print()
print("  weak-but-not-vacuous (compares fixed module constants only):")
weak = 0
for suite in SUITES:
    tree = ast.parse((PKG / suite).read_text(encoding="utf-8"), filename=suite)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "check" and len(node.args) >= 2
                and literal_only_compare(node.args[1])):
            weak += 1
            print("    %s:%d  %s   ->   %s" % (suite, node.lineno,
                                               ast.unparse(node.args[0])[:60],
                                               ast.unparse(node.args[1])[:90]))
print("  weak count:", weak)

print()
print("=" * 100)
print("D-B  MUTATION TEST -- reintroduce one defect at a time on a TEMP COPY")
print("=" * 100)

MUTANTS = [
    ("M1 require_identifier_kind back to isinstance-only",
     "membership_runner_v4.py",
     "    if type(value) is IdentifierKind and any(value is member for member in IdentifierKind):",
     "    if isinstance(value, IdentifierKind):"),
    ("M2 errors._safe accepts ANY Enum and echoes .value",
     "errors.py",
     "    if type(value) is IdentifierKind:",
     "    if isinstance(value, Enum):\n        return value.value\n    if type(value) is IdentifierKind:"),
    ("M3 errors.message drops the closed field-NAME set",
     "errors.py",
     "    if any(type(k) is not str or k not in FIELD_NAMES for k in fields):\n        raise UnsafeErrorField(\"an error field name is not in the closed field set\")\n",
     ""),
    ("M4 errors._safe accepts numeric SUBCLASSES again",
     "errors.py",
     "    if value is None or type(value) in (bool, int, float):",
     "    import numbers as _n\n    if value is None or isinstance(value, (bool, _n.Real)):"),
    ("M5 _normalise_evidence silently DROPS a malformed item",
     "corpus_ingest_v4.py",
     "            else:\n                errors.raise_violation(DesignViolation, errors.Code.EVIDENCE_ITEM_MALFORMED,\n                                       item_position=position, items=len(value),\n                                       item_is_str=False, item_is_mapping=False)",
     "            else:\n                continue"),
    ("M6 safe_report.describe prints the raw type name again",
     "safe_report.py",
     "    category = type(value).__name__ if type(value) in (\n        str, bytes, bytearray, int, float, bool, type(None), dict, list, tuple, set, frozenset) else \"object\"",
     "    category = type(value).__name__"),
    ("M7 safe_report.digest calls repr() on custom objects again",
     "safe_report.py",
     "    if not _builtin_tree(value):\n        return hashlib.sha256(b\"<opaque object>\").hexdigest()[:DIGEST_CHARS]\n",
     ""),
    ("M8 errors.message accepts any Code-lookalike (isinstance)",
     "errors.py",
     "    if type(code) is not Code or not any(code is member for member in Code):",
     "    if not isinstance(code, Code):"),
]

env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1",
           OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
           NUMEXPR_NUM_THREADS="1")


def run_suites(root):
    out = {}
    for suite in SUITES:
        p = subprocess.run([PYEXE, "-B", str(root / PKGNAME / suite)],
                           capture_output=True, text=True, cwd=str(root / PKGNAME), env=env)
        out[suite] = (p.returncode, (p.stdout + p.stderr))
    return out


base_root = Path(tempfile.mkdtemp(prefix="probe_d_base_")) / "v52"
shutil.copytree(V52, base_root)
base = run_suites(base_root)
print("BASELINE (unmutated copy):")
for s, (rc, txt) in base.items():
    tail = [l for l in txt.strip().splitlines() if l.strip()][-1:]
    print("   %-28s exit=%d  %s" % (s, rc, tail[0][:90] if tail else ""))
print()

results = []
for tag, target, old, new in MUTANTS:
    root = Path(tempfile.mkdtemp(prefix="probe_d_mut_")) / "v52"
    shutil.copytree(V52, root)
    f = root / PKGNAME / target
    src = f.read_text(encoding="utf-8")
    if src.count(old) != 1:
        print("SKIP %s -- anchor found %d times in %s" % (tag, src.count(old), target))
        results.append((tag, None, None, "anchor-miss"))
        continue
    f.write_text(src.replace(old, new), encoding="utf-8")
    res = run_suites(root)
    caught = [s for s, (rc, _) in res.items() if rc != 0]
    print("%-58s caught_by=%s" % (tag, caught if caught else "*** NOTHING -- undetected ***"))
    for s, (rc, txt) in res.items():
        if rc != 0:
            fail_lines = [l for l in txt.splitlines()
                          if "Assertion" in l or "assert" in l.lower() or "FAIL" in l][-2:]
            for l in fail_lines:
                print("        %s: %s" % (s, l.strip()[:130]))
    results.append((tag, res[SUITES[0]][0], res[SUITES[1]][0], caught))
    shutil.rmtree(root.parent, ignore_errors=True)

shutil.rmtree(base_root.parent, ignore_errors=True)
print()
undetected = [t for t, a, b, c in results if c == [] or c == "anchor-miss"]
print("MUTANTS UNDETECTED BY THE CANDIDATE'S OWN SUITES:", undetected if undetected else "NONE")
