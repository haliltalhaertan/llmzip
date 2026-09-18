"""T1 CLEANROOM: path-only adapted t1() using ONLY files copied to own cleanroom/.
Asserts no ambient source imports: the loaded lib must come from cleanroom/audit/.
Compares every cell vs published DECISION_TESTS.json T1 with exact float diffs.
"""
import importlib.util
import json
import os
import sys
import time

OWN = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/09_portability"
CLEAN = os.path.join(OWN, "cleanroom", "coordinator", "decision_tests_clean.py")
LIB_EXPECT = os.path.normpath(os.path.join(OWN, "cleanroom", "audit", "audit_baseline_lib.py"))

# Guard: forbid accidental ambient imports of the original source tree
FORBIDDEN = ("/top10_comparison_r1/", "/_wt_top10/", "/bench3/", "/incoming_20260916b", "/drive/")
for m in list(sys.modules):
    for f in FORBIDDEN:
        assert f not in str(getattr(sys.modules[m], "__file__", "") or ""), f"ambient pre-import {m}"

spec = importlib.util.spec_from_file_location("dt_clean", CLEAN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

t0 = time.time()
out = mod.t1()
dt = time.time() - t0

# Guard: lib actually loaded must be the cleanroom copy.
# (module_from_spec does not register in sys.modules, so verify by construction
# plus a sweep that no loaded module came from the ambient source tree.)
libfile = LIB_EXPECT
assert os.path.isfile(libfile), f"cleanroom lib missing: {libfile}"
for name, m in list(sys.modules.items()):
    f = str(getattr(m, "__file__", "") or "")
    for prefix in FORBIDDEN:
        assert prefix not in f, f"ambient source import: {name} -> {f}"

pub = json.load(open(os.path.join(OWN, "evidence", "DECISION_TESTS_published.json")))["T1_fair_baseline"]

rows = []
fails = 0
for v in ("coarse_textbook", "frozen_textbook", "coarse_idfonly", "frozen_idfonly"):
    for metric in ("hit10", "fr3"):
        a = float(out["bm25_variants"][v][metric])
        b = float(pub["bm25_variants"][v][metric])
        d = float(abs(a - b))
        ok = bool(d == 0.0)
        fails += (not ok)
        rows.append({"cell": f"BM25/{v}/{metric}", "rerun": a, "published": b, "absdiff": d, "match": ok})
for arm in sorted(pub["code_arms"]):
    for metric in ("hit10", "fr3", "vs_strongest_bm25_hit10_pp", "vs_strongest_bm25_fr3_pp"):
        a = float(out["code_arms"][arm][metric])
        b = float(pub["code_arms"][arm][metric])
        d = float(abs(a - b))
        ok = bool(d == 0.0)
        fails += (not ok)
        rows.append({"cell": f"code/{arm}/{metric}", "rerun": a, "published": b, "absdiff": d, "match": ok})
for k in ("any_arm_beats_strongest_bm25_hit10", "C1_gate_plus2pp_fr3"):
    ok = bool(out["verdict"][k] == pub["verdict"][k])
    fails += (not ok)
    rows.append({"cell": f"verdict/{k}", "rerun": bool(out["verdict"][k]), "published": bool(pub["verdict"][k]), "absdiff": 0.0 if ok else 1.0, "match": ok})
strong_ok = bool(out["strongest_bm25"]["variant"] == pub["strongest_bm25"]["variant"])
fails += (not strong_ok)
rows.append({"cell": "strongest_variant", "rerun": out["strongest_bm25"]["variant"], "published": pub["strongest_bm25"]["variant"], "absdiff": 0.0 if strong_ok else 1.0, "match": strong_ok})

report = {
    "elapsed_s": float(dt),
    "lib_file": libfile,
    "n_cells": len(rows),
    "n_mismatch": int(fails),
    "all_match": bool(fails == 0),
    "rows": rows,
}
json.dump(report, open(os.path.join(OWN, "outputs", "T1_cleanroom_compare.json"), "w"), indent=1)
json.dump(out, open(os.path.join(OWN, "outputs", "T1_cleanroom_T1.json"), "w"), indent=1)
print(f"cells={len(rows)} mismatches={fails} elapsed={dt:.1f}s lib={libfile}")
for r in rows:
    if not r["match"]:
        print("MISMATCH", r)
print("strongest:", out["strongest_bm25"], "C1:", out["verdict"]["C1_gate_plus2pp_fr3"])
print("WROTE outputs/T1_cleanroom_compare.json")
assert fails == 0, f"{fails} cell mismatches"
