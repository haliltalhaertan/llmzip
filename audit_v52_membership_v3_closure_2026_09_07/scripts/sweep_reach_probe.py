"""How far does the v3 self-sweep actually reach? (CRITERION 2, second part)

The preparer claims the sweep covers ONE named shape and explicitly does NOT claim comprehensive
soundness. This probe establishes exactly where the code sits relative to those words:

  PART 1 - run the preparer's own sweep predicate over a table of synthetic `check(...)` shapes and
           record which are flagged. This shows whether the code is stronger or weaker than the
           phrase "a boolean expression ending in a literal True".

  PART 2 - an adversarial combined mutation: apply the NEW-2 core mutant (cv_sigma_before =
           123456.0) AND simultaneously neuter the replacement check in the test file with
           `or (1 == 1)` - a condition that is unconditionally true but is NOT a literal True, so
           the sweep by construction cannot see it. This measures whether the suite still dies,
           i.e. whether the NEW-2 kill rests on one check or on more than one.

No corpus, no model, no network, no real data.
Usage: python sweep_reach_probe.py <candidate_dir>
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAND = Path(sys.argv[1]).resolve()


def preparer_predicate(src: str):
    hits = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "check" \
                and len(n.args) >= 2:
            cond = n.args[1]
            if isinstance(cond, ast.Constant) and cond.value is True:
                continue
            if isinstance(cond, ast.BoolOp) and any(
                    isinstance(v, ast.Constant) and v.value is True for v in cond.values):
                hits.append(ast.get_source_segment(src, n))
    return hits


print("=" * 100)
print("PART 1 - reach of the preparer's own sweep predicate")
print("=" * 100)
SHAPES = [
    ("check('x', a > 0 or True)", "the exact v2 defect: literal True LAST"),
    ("check('x', True or a > 0)", "literal True FIRST - outside a literal reading of 'ending in'"),
    ("check('x', a > 0 and True)", "an `and True` conjunct"),
    ("check('x', a > 0 or b > 0 or True)", "three-way, True last"),
    ("check('x', True)", "bare literal True - the exempted did-not-raise marker"),
    ("check('x', a > 0 or (1 == 1))", "unconditionally true, but NOT a literal True"),
    ("check('x', a > 0 or bool(1))", "unconditionally true via a call"),
    ("check('x', a > 0 or 1)", "truthy literal that is not `True`"),
    ("check('x', not False)", "constant via a unary not"),
    ("check('x', a > 0)", "an honest condition (control - must NOT be flagged)"),
]
for src, why in SHAPES:
    flagged = bool(preparer_predicate(src))
    print(f"  {'FLAGGED    ' if flagged else 'not flagged'}  {src:<40}  {why}")
print()
print("Reading: the code flags a BoolOp with a literal True in ANY position, so it is STRONGER than")
print("the phrase 'ending in a literal True'. It is weaker than 'all unconditionally true")
print("conditions', which the preparer explicitly does not claim.")

print()
print("=" * 100)
print("PART 2 - does the NEW-2 kill rest on a single check?")
print("=" * 100)
CORE_OLD = '        "cv_sigma_before": _cv(sigma),'
CORE_NEW = '        "cv_sigma_before": 123456.0,'
TEST_OLD = """check("F-1: cv_sigma_before is a genuine CV of this archive",
      abs(ddeg["cv_sigma_before"] - float(_sig_deg.std(ddof=0) / _sig_deg.mean())) <= 1e-12,"""
TEST_NEW = """check("F-1: cv_sigma_before is a genuine CV of this archive",
      abs(ddeg["cv_sigma_before"] - float(_sig_deg.std(ddof=0) / _sig_deg.mean())) <= 1e-12 or (1 == 1),"""

CASES = [
    ("core mutant only", True, False),
    ("core mutant + the replacement check neutered with `or (1 == 1)`", True, True),
    ("test neutered only, core untouched (control)", False, True),
]
for label, mutate_core, mutate_test in CASES:
    work = Path(tempfile.mkdtemp(prefix="sweep_reach_"))
    try:
        for f in ("membership_scaling_core.py", "test_membership_scaling_core.py"):
            shutil.copy2(CAND / f, work / f)
        if mutate_core:
            p = work / "membership_scaling_core.py"
            s = p.read_text(encoding="utf-8")
            assert s.count(CORE_OLD) == 1, "core anchor not unique"
            p.write_text(s.replace(CORE_OLD, CORE_NEW, 1), encoding="utf-8")
        if mutate_test:
            p = work / "test_membership_scaling_core.py"
            s = p.read_text(encoding="utf-8")
            assert s.count(TEST_OLD) == 1, "test anchor not unique"
            p.write_text(s.replace(TEST_OLD, TEST_NEW, 1), encoding="utf-8")
        r = subprocess.run([sys.executable, "-B", "test_membership_scaling_core.py"],
                           cwd=work, capture_output=True, text=True, timeout=1800)
        out = r.stdout + r.stderr
        failing = [l.strip() for l in out.splitlines() if l.startswith("FAIL")]
        print(f"\n  {label}")
        print(f"    exit code {r.returncode} -> {'KILLED' if r.returncode else '*** SURVIVES ***'}")
        for f in failing:
            print(f"      FAIL: {f[6:130]}")
        if not failing:
            print("      (no named FAIL lines)")
    finally:
        shutil.rmtree(work, ignore_errors=True)
raise SystemExit(0)
