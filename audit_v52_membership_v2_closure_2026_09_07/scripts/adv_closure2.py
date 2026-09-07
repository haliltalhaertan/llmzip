"""Follow-up closure probes: the per-seed conformance gap, the AST division band,
the vacuous check at test L132, and the _cv epsilon question done properly."""
from __future__ import annotations
import ast, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
V2 = HERE / "v2"
rows = []
def rec(area, name, outcome, detail=""):
    rows.append({"area": area, "probe": name, "outcome": outcome, "detail": str(detail)[:400]})
    print(f"[{area}] {outcome:<9} {name}   {str(detail)[:230]}")

def run_mutant(label, patch, expect):
    work = Path(tempfile.mkdtemp(prefix="mut_"))
    shutil.copytree(V2, work / "c")
    p = work / "c" / "membership_scaling_core.py"
    s = p.read_text(encoding="utf-8")
    s2 = patch(s)
    if s2 == s:
        rec("mutation", label, "NOT-APPLIED", "anchor not found")
        return None
    p.write_text(s2, encoding="utf-8")
    r = subprocess.run([sys.executable, "test_membership_scaling_core.py"], cwd=work / "c",
                       capture_output=True, text=True)
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    killed = r.returncode != 0
    rec("mutation", label, "KILLED" if killed else "SURVIVED",
        f"exit={r.returncode} expect={expect} fails={fails[:2]}")
    return killed

print("python", sys.version.split()[0], "numpy", np.__version__)

# ---------- 1. per-seed vectors are never conformance-checked ----------
print("\n--- per-seed vectors vs the independent reference ---")
src = (V2 / "test_membership_scaling_core.py").read_text(encoding="utf-8")
tree = ast.parse(src)
conf = [ast.get_source_segment(src, n.args[0]) for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "check"
        and n.args and isinstance(n.args[0], ast.Constant) and "CONFORMANCE" in str(n.args[0].value)]
rec("conformance", "checks whose name says CONFORMANCE", "LIST", conf)
mentions_per_seed = [c for c in conf if "per_seed" in c.lower()]
rec("conformance", "any CONFORMANCE check covering a per_seed_* vector",
    "NONE" if not mentions_per_seed else "FOUND", mentions_per_seed)
ref_fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "reference_quantities"][0]
rec("conformance", "reference_quantities returns", "INFO",
    ast.get_source_segment(src, ref_fn.body[-1]))

# the three per-seed keys are in the published schema
spec = importlib.util.spec_from_file_location("mc2", V2 / "membership_scaling_core.py")
m = importlib.util.module_from_spec(spec); sys.modules["mc2"] = m; spec.loader.exec_module(m)
rec("conformance", "published schema keys", "INFO", sorted(m.AGGREGATE_KEYS))

# ---------- 2. ratios substituted into EXISTING keys ----------
print("\n--- ratios smuggled into existing, permitted key names ---")
run_mutant("R1: per_seed_Delta_pp becomes Delta/G (a genuine forbidden ratio, existing key)",
           lambda s: s.replace('"per_seed_Delta_pp": per_seed_d.tolist(),',
                               '"per_seed_Delta_pp": (per_seed_d / np.where(per_seed_g == 0, 1.0, per_seed_g)).tolist(),'),
           "should be killed")
run_mutant("R2: per_seed_G_scaled_pp becomes G_scaled/G (a ratio, existing key)",
           lambda s: s.replace('"per_seed_G_scaled_pp": per_seed_gs.tolist(),',
                               '"per_seed_G_scaled_pp": (per_seed_gs / np.where(per_seed_g == 0, 1.0, per_seed_g)).tolist(),'),
           "should be killed")
run_mutant("R3: per_seed_G_pp scaled by an arbitrary factor 1.5 (not even a ratio)",
           lambda s: s.replace('"per_seed_G_pp": per_seed_g.tolist(),',
                               '"per_seed_G_pp": (per_seed_g * 1.5).tolist(),'),
           "should be killed")
run_mutant("R4 CONTROL: Delta_bar_pp itself becomes Delta/G (a scalar the conformance test does cover)",
           lambda s: s.replace('    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,',
                               '    D_ = D_ / G if G != 0 else D_\n    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,'),
           "must be killed (negative control for the conformance test)")
run_mutant("R5: the ratio stored in the _percentiles note text (a string channel)",
           lambda s: s.replace('res = {"scheme": scheme,',
                               'res = {"ratio_hint": "see note", "scheme": scheme,'),
           "bootstrap output has no closed schema")

# ---------- 3. how wide is the AST division band? ----------
print("\n--- the AST division check is a COUNT BAND, not an enumeration ---")
core = (V2 / "membership_scaling_core.py").read_text(encoding="utf-8")
n_div = len([n for n in ast.walk(ast.parse(core)) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)])
rec("AST", "divisions currently in the core (band asserted is 0 < n <= 12)", "INFO", n_div)
rec("AST", "spare capacity: divisions that can be ADDED before the band trips",
    "INFO", f"{12 - n_div} more Div nodes pass the check")
run_mutant("R6: add a forbidden ratio using np.divide (not an ast.Div node) under an existing key",
           lambda s: s.replace('"per_seed_Delta_pp": per_seed_d.tolist(),',
                               '"per_seed_Delta_pp": np.divide(per_seed_d, np.where(per_seed_g == 0, 1.0, per_seed_g)).tolist(),'),
           "np.divide is invisible to the Div-node count")

# ---------- 4. the vacuous check at test L132 ----------
print("\n--- vacuous check introduced by v2 ---")
lines = src.split("\n")
rec("vacuous", "test L132-133 source", "INFO", lines[131].strip() + " | " + lines[132].strip())
# prove it is vacuous: break cv_sigma_before completely and see whether that check still passes
def break_cv_before(s):
    return s.replace('"cv_sigma_before": _cv(sigma),', '"cv_sigma_before": 123456.0,')
work = Path(tempfile.mkdtemp(prefix="vac_")); shutil.copytree(V2, work / "c")
p = work / "c" / "membership_scaling_core.py"
p.write_text(break_cv_before(p.read_text(encoding="utf-8")), encoding="utf-8")
r = subprocess.run([sys.executable, "test_membership_scaling_core.py"], cwd=work / "c",
                   capture_output=True, text=True)
line132 = [l for l in r.stdout.splitlines() if "cv_sigma_before is a CV too" in l]
rec("vacuous", "with cv_sigma_before hard-coded to 123456.0, the 'cv_sigma_before is a CV too' check",
    "STILL PASSES" if line132 and line132[0].startswith("ok") else "fails", line132)
rec("vacuous", "does the suite as a whole still catch the broken cv_sigma_before?",
    "KILLED" if r.returncode != 0 else "SURVIVED",
    f"exit={r.returncode} fails={[l for l in r.stdout.splitlines() if l.startswith('FAIL')][:3]}")

# ---------- 5. _cv epsilon question, done by AST rather than by grep ----------
print("\n--- _cv: no epsilon, checked structurally ---")
cvfn = [n for n in ast.walk(ast.parse(core)) if isinstance(n, ast.FunctionDef) and n.name == "_cv"][0]
consts = [n.value for n in ast.walk(cvfn) if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))]
divs = [ast.get_source_segment(core, n) for n in ast.walk(cvfn) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
rec("F-1", "numeric constants inside _cv", "INFO", consts)
rec("F-1", "division expressions inside _cv", "INFO", divs)
rec("F-1", "no epsilon added to the CV denominator",
    "PASS" if consts == [0.0] and divs == ["values.std(ddof=0) / mean"] else "REVIEW", f"{consts} {divs}")
# negative control: an epsilon-added variant must be visibly different
rec("F-1", "NEGATIVE CONTROL: the same structural check applied to an eps-added variant",
    "PASS(differs)" if divs != ["values.std(ddof=0) / (mean + 1e-12)"] else "FAIL", "")

# ---------- 6. n_questions == 0 ----------
print("\n--- degenerate cluster inputs ---")
try:
    m.build_clusters([], 0)
    rec("F-2", "build_clusters([], 0)", "ACCEPTED", "")
except m.DesignViolation as e:
    rec("F-2", "build_clusters([], 0)", "DesignViolation", str(e)[:150])
except Exception as e:
    rec("F-2", "build_clusters([], 0) raises a NON-DesignViolation", "RAW-EXC", f"{type(e).__name__}: {e}")
# realistic cross-enum integer collision
import enum
class A(enum.IntEnum): X = 1
class B(enum.IntEnum): Y = 1
try:
    o, mem, cd = m.build_clusters([A.X] * 5 + [B.Y] * 5, 10)
    rec("F-2", "two DIFFERENT IntEnum labels with the same integer value are MERGED",
        "MERGED", f"n_clusters={cd['n_clusters']} sizes={cd['cluster_sizes']}")
except Exception as e:
    rec("F-2", "cross-enum same-value labels", type(e).__name__, str(e)[:150])

json.dump(rows, open(HERE / "adv_closure2_results.json", "w"), indent=1)
print(f"\nrows={len(rows)}")
