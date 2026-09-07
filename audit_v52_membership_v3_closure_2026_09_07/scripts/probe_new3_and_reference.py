"""Direct probes for CRITERION 3 (NEW-3) and for the independence of the conformance reference.

Part 1 - build_clusters boundary behaviour, called directly by the auditor rather than read from
the preparer's test names. For each input it records the exception TYPE, so a named DesignViolation
can be told apart from a library exception leaking from a deeper frame, and the frame the exception
was actually raised in.

Part 2 - independence of the conformance reference. The claim under audit is that
`reference_quantities` in the v3 test suite is an independent reimplementation. This part parses
the test file's AST and enumerates every Name/Attribute the function body touches, to show whether
it reads anything from the core module object `m`.

No corpus, no model, no network, no real data.
Usage: python probe_new3_and_reference.py <candidate_dir>
"""
from __future__ import annotations

import ast
import importlib.util
import sys
import traceback
from pathlib import Path

CAND = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("v3core", CAND / "membership_scaling_core.py")
m = importlib.util.module_from_spec(spec)
sys.modules["v3core"] = m
spec.loader.exec_module(m)

print("=" * 100)
print("PART 1 - build_clusters boundary probes (CRITERION 3 / NEW-3)")
print("=" * 100)

CASES = [
    ("build_clusters([], 0)                     the exact NEW-3 case", [], 0),
    ("build_clusters([], -1)                    negative count, empty labels", [], -1),
    ("build_clusters([], -7)                    negative count, empty labels", [], -7),
    ("build_clusters([], 3)                     empty labels, POSITIVE count", [], 3),
    ("build_clusters(['A','B'], 0)              non-empty labels, zero count", ["A", "B"], 0),
    ("build_clusters(['A','B'], -2)             non-empty labels, negative count", ["A", "B"], -2),
    ("build_clusters(['A'], 1)                  the minimal VALID case", ["A"], 1),
    ("build_clusters(['A','B'], 2)              a valid two-singleton case", ["A", "B"], 2),
    ("build_clusters(['A','A'], 2)              a valid one-cluster case", ["A", "A"], 2),
]

rows = []
for label, labels, n in CASES:
    try:
        out = m.build_clusters(labels, n)
        rows.append((label, "RETURNED", f"n_clusters={out[2]['n_clusters']} covered={out[2]['questions_covered_at_construction']}"))
    except m.DesignViolation as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        rows.append((label, "DesignViolation", f"{str(e)[:78]!r} raised at {Path(tb[-1].filename).name}:{tb[-1].lineno}"))
    except Exception as e:                                        # noqa: BLE001 - that is the point
        tb = traceback.extract_tb(sys.exc_info()[2])
        rows.append((label, f"*** {type(e).__name__} (NOT a named violation) ***",
                     f"{str(e)[:78]!r} raised at {Path(tb[-1].filename).name}:{tb[-1].lineno}"))
for label, kind, detail in rows:
    print(f"{label}\n    -> {kind}\n       {detail}")

print()
print("Additional probe: a non-iterable first argument, which reaches list() before the guard.")
for label, arg, n in (("build_clusters(None, 0)", None, 0), ("build_clusters(3, 0)", 3, 0)):
    try:
        m.build_clusters(arg, n)
        print(f"{label} -> RETURNED (no exception)")
    except m.DesignViolation as e:
        print(f"{label} -> DesignViolation {str(e)[:70]!r}")
    except Exception as e:                                        # noqa: BLE001
        tb = traceback.extract_tb(sys.exc_info()[2])
        print(f"{label} -> *** {type(e).__name__} (NOT a named violation) *** {str(e)[:60]!r} "
              f"at {Path(tb[-1].filename).name}:{tb[-1].lineno}")

print()
print("Probe: the public path that reaches build_clusters with n_questions = 0.")
import numpy as np  # noqa: E402
try:
    m.cluster_bootstrap(np.zeros((0, 10)), np.zeros((0, 10)), [], seed=1, replicates=2)
    print("cluster_bootstrap on an EMPTY g -> RETURNED (no exception)")
except m.DesignViolation as e:
    print(f"cluster_bootstrap on an EMPTY g -> DesignViolation {str(e)[:80]!r}")
except Exception as e:                                            # noqa: BLE001
    print(f"cluster_bootstrap on an EMPTY g -> *** {type(e).__name__} *** {str(e)[:80]!r}")

print()
print("=" * 100)
print("PART 2 - is the conformance reference independent of the core? (CRITERION 1)")
print("=" * 100)
tsrc = (CAND / "test_membership_scaling_core.py").read_text(encoding="utf-8")
tree = ast.parse(tsrc)
fn = next(n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "reference_quantities")
names, attrs, calls = set(), set(), set()
for n in ast.walk(fn):
    if isinstance(n, ast.Name):
        names.add(n.id)
    if isinstance(n, ast.Attribute):
        base = n.value
        attrs.add((base.id if isinstance(base, ast.Name) else type(base).__name__) + "." + n.attr)
    if isinstance(n, ast.Call):
        f = n.func
        calls.add(f.id if isinstance(f, ast.Name) else
                  (getattr(f, "attr", type(f).__name__)))
print(f"reference_quantities: lines {fn.lineno}-{fn.end_lineno}")
print(f"  free/local Names touched : {sorted(names)}")
print(f"  attribute accesses       : {sorted(attrs) if attrs else '(none)'}")
print(f"  functions called         : {sorted(calls)}")
core_touch = sorted(a for a in attrs if a.startswith("m.")) + sorted(n for n in names if n == "m")
print(f"  references to the core module object `m` : {core_touch if core_touch else 'NONE'}")
print(f"  imports numpy?           : {'np' in names}")
print()
print("VERDICT (mechanical): the reference is independent of the core iff the line above is NONE "
      "and it calls no core function.")

print()
print("Cross-check: the fixture the reference is fed vs the fixture the core is fed.")
for n in ast.walk(tree):
    if isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("ref", "agg_c", "g_c", "frac", "recs_c")
                                         for t in n.targets):
        print(f"  line {n.lineno}: {ast.get_source_segment(tsrc, n)[:150]}")
raise SystemExit(0)
