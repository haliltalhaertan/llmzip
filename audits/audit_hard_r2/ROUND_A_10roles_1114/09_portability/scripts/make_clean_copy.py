"""Make path-only cleanroom copy of decision_tests.py (T1 only). Logs exact diff."""
import difflib
import os

OWN = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/09_portability"
SRC = os.path.join(OWN, "cleanroom", "coordinator", "decision_tests_pkg.py")
DST = os.path.join(OWN, "cleanroom", "coordinator", "decision_tests_clean.py")

src = open(SRC, encoding="utf-8").read()

old_rt = '    RT = f"{W}/top10_comparison_r1/data"'
new_rt = '    RT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")  # CLEANROOM path-only: in-package data/'
assert src.count(old_rt) == 1, "RT line not found exactly once"

old_lib1 = '        importlib.util.spec_from_file_location("lib", f"{W}/top10_comparison_r1/audit/audit_baseline_lib.py"))'
new_lib1 = '        importlib.util.spec_from_file_location("lib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit", "audit_baseline_lib.py")))  # CLEANROOM path-only: in-package audit lib'
assert src.count(old_lib1) == 1, "lib1 line not found exactly once"

old_lib2 = '        "lib", f"{W}/top10_comparison_r1/audit/audit_baseline_lib.py").loader.exec_module(lib)'
new_lib2 = '        "lib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit", "audit_baseline_lib.py")).loader.exec_module(lib)  # CLEANROOM path-only'
assert src.count(old_lib2) == 1, "lib2 line not found exactly once"

dst = src.replace(old_rt, new_rt).replace(old_lib1, new_lib1).replace(old_lib2, new_lib2)
open(DST, "w", encoding="utf-8").write(dst)

diff = "".join(difflib.unified_diff(
    src.splitlines(True), dst.splitlines(True),
    fromfile="decision_tests_pkg.py (as-shipped)",
    tofile="decision_tests_clean.py (cleanroom path-only)"))
open(os.path.join(OWN, "outputs", "T1_path_patch.diff"), "w", encoding="utf-8").write(diff)
print(diff)
print("WROTE", DST)
