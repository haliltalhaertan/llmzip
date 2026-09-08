"""Probe F -- does the harness check what it claims?

  F1  guarded_suite.py: negative control. A synthetic suite that opens a .json OUTSIDE
      the guard root must be denied and must make the launcher exit non-zero.
  F2  guarded_suite.py: positive control. A synthetic suite that opens a .json INSIDE
      the root must be observed and allowed.
  F3  validate_candidate.py refuses an EXISTING output directory.
  F4  validate_candidate.py detects a tampered payload (on a temp COPY of the package).
  F5  compute_results / identity-before-parse: the accepted-manifest stamp is required.

Synthetic only. Nothing under the candidate namespace is modified: F4 works on a copy.

Usage: python -B probe_f_harness.py <worktree root> <python exe>
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
PYEXE = sys.argv[2]
NS = "drafts/v52/membership_runner_ingest_codex_v5_2026_09_08"
PKG = WT / NS
TMP = Path(tempfile.mkdtemp(prefix="probe_f_")).resolve()
PASS = FAIL = 0
env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1",
           OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
           NUMEXPR_NUM_THREADS="1")


def truth(tag, cond, note=""):
    global PASS, FAIL
    PASS += bool(cond)
    FAIL += (not cond)
    print(("PASS " if cond else "FAIL ") + tag + (("\n      " + str(note)[:400]) if note else ""))


print("=" * 100)
print("F1/F2  guarded_suite.py negative and positive controls")
print("=" * 100)
outside = TMP / "outside_synthetic_data.json"
outside.write_text('{"synthetic": true}', encoding="utf-8")

neg = TMP / "suite_neg.py"
neg.write_text(
    "from pathlib import Path\n"
    "print('SUITE NEG START')\n"
    "print(Path(%r).read_text())\n"
    "print('SUITE NEG REACHED END')\n" % str(outside), encoding="utf-8")
p = subprocess.run([PYEXE, "-B", str(PKG / "guarded_suite.py"), str(neg)],
                   capture_output=True, text=True, env=env, cwd=str(WT))
truth("F1 a .json read OUTSIDE the guard root is DENIED and the launcher exits non-zero",
      p.returncode != 0 and "REACHED END" not in p.stdout
      and "PermissionError" in (p.stdout + p.stderr),
      "exit=%s | %s" % (p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1][:200]))
print("      guard line: %s" % next((l for l in p.stdout.splitlines()
                                     if "PYTHON_IO_GUARD" in l), "(none)"))

pos = TMP / "suite_pos.py"
pos.write_text(
    "import json, tempfile\n"
    "from pathlib import Path\n"
    "p = Path(tempfile.mkdtemp()) / 'inside.json'\n"
    "p.write_text('{}')\n"
    "print('read ->', p.read_text())\n"
    "print('SUITE POS REACHED END')\n", encoding="utf-8")
p2 = subprocess.run([PYEXE, "-B", str(PKG / "guarded_suite.py"), str(pos)],
                    capture_output=True, text=True, env=env, cwd=str(WT))
guard_line = next((l for l in p2.stdout.splitlines() if "PYTHON_IO_GUARD" in l), "")
obs = json.loads(guard_line.split(" ", 1)[1]) if guard_line else {}
truth("F2 a .json read INSIDE the guard root is observed and allowed",
      p2.returncode == 0 and "SUITE POS REACHED END" in p2.stdout
      and obs.get("observed_data_events", 0) > 0 and obs.get("denied_data_events") == 0, obs)

print()
print("=" * 100)
print("F3/F4  validate_candidate.py")
print("=" * 100)
existing = TMP / "already_here"
existing.mkdir()
p3 = subprocess.run([PYEXE, "-B", str(PKG / "validate_candidate.py"), "--output", str(existing)],
                    capture_output=True, text=True, env=env, cwd=str(WT))
truth("F3 the writer REFUSES an existing output folder",
      p3.returncode != 0 and "FileExistsError" in (p3.stdout + p3.stderr),
      (p3.stdout + p3.stderr).strip().splitlines()[-1][:200])

copy_root = TMP / "wtcopy"
shutil.copytree(WT / "drafts", copy_root / "drafts")
tampered = copy_root / NS / "errors.py"
tampered.write_text(tampered.read_text(encoding="utf-8") + "\n# tamper\n", encoding="utf-8")
p4 = subprocess.run([PYEXE, "-B", str(copy_root / NS / "validate_candidate.py")],
                    capture_output=True, text=True, env=env, cwd=str(copy_root))
truth("F4 the no-argument payload verification DETECTS a one-line tamper",
      p4.returncode != 0 and "AssertionError" in (p4.stdout + p4.stderr),
      (p4.stdout + p4.stderr).strip().splitlines()[-1][:200])

print()
print("=" * 100)
print("F5  compute_results requires a mapping stamped by the accepted-resolution path")
print("=" * 100)
sys.path[:0] = [str(PKG), str(WT / "drafts/v52/membership_impl_v3_2026_09_07")]
import membership_runner_v4 as R                                              # noqa: E402
import inspect                                                               # noqa: E402
print("      compute_results signature:", inspect.signature(R.compute_results))
src = inspect.getsource(R.compute_results)
truth("F5 compute_results checks the accepted-manifest stamp before parsing",
      "_accepted_manifest_sha256" in src, [l.strip()[:110] for l in src.splitlines()
                                           if "_accepted_manifest_sha256" in l])

print()
print("SUMMARY  PASS=%d FAIL=%d" % (PASS, FAIL))
print("TEMP:", TMP)
