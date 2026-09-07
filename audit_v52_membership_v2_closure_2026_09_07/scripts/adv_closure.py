"""Independent adversarial closure probes against v2 core.
Cold-start closure check, audit/v52-membership-v2-closure-2026-09-07.
Synthetic data only. No corpus, no model, no seal, no run/finalize.
"""
from __future__ import annotations
import importlib.util, math, sys, json, numbers
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mc2", HERE / "v2" / "membership_scaling_core.py")
m = importlib.util.module_from_spec(spec); sys.modules["mc2"] = m; spec.loader.exec_module(m)

rows = []
def rec(area, name, outcome, detail=""):
    rows.append({"area": area, "probe": name, "outcome": outcome, "detail": str(detail)[:300]})
    print(f"[{area}] {outcome:<9} {name}   {str(detail)[:170]}")

def probe(area, name, fn, want):
    """want in {'reject','accept'}; returns the value on accept."""
    try:
        v = fn()
    except m.DesignViolation as e:
        rec(area, name, "REJECTED" if want == "reject" else "REJECTED*", type(e).__name__ + ": " + str(e)[:150])
        return None
    except Exception as e:
        rec(area, name, "RAW-EXC", type(e).__name__ + ": " + str(e)[:150])
        return None
    rec(area, name, "ACCEPTED" if want == "accept" else "ACCEPTED*", repr(v)[:200])
    return v

print("python", sys.version.split()[0], "numpy", np.__version__)

# ============================ F-1: CV ============================
print("\n--- F-1 coefficient of variation ---")
rng = np.random.default_rng(4242)
C = rng.standard_normal((200, 96)) * (0.9 ** np.arange(96)); C = C - C.mean(axis=0)
D, d = m.scale_matrix(C)
post = (C @ D).std(axis=0, ddof=0)
pre = C.std(axis=0, ddof=0)
ok_after = abs(d["cv_sigma_after"] - post.std(ddof=0) / post.mean()) < 1e-15
ok_before = abs(d["cv_sigma_before"] - pre.std(ddof=0) / pre.mean()) < 1e-15
rec("F-1", "cv_sigma_after == spread/mean of post sigma (recomputed independently)",
    "PASS" if ok_after else "FAIL", f"{d['cv_sigma_after']!r}")
rec("F-1", "cv_sigma_before == spread/mean of pre sigma (recomputed independently)",
    "PASS" if ok_before else "FAIL", f"{d['cv_sigma_before']!r}")
# NEGATIVE CONTROL: the same assertion must fail against the SD (the v1 quantity)
neg = abs(d["sd_sigma_after"] - post.std(ddof=0) / post.mean()) < 1e-15
rec("F-1", "NEGATIVE CONTROL: sd_sigma_after is NOT the CV (assertion must fail)",
    "PASS(control failed as required)" if not neg else "FAIL(control passed)",
    f"sd={d['sd_sigma_after']!r} cv={d['cv_sigma_after']!r}")
rec("F-1", "sd_sigma_after equals the v1-reported quantity (SD of post sigma)",
    "PASS" if abs(d["sd_sigma_after"] - float(post.std(ddof=0))) < 1e-15 else "FAIL", d["sd_sigma_after"])

# zero-mean case, no epsilon
Dz, dz = m.scale_matrix(np.zeros((7, 96)))
rec("F-1", "zero-mean sigma -> NaN (not 0, not inf, no epsilon)",
    "PASS" if (math.isnan(dz["cv_sigma_after"]) and math.isnan(dz["cv_sigma_before"])) else "FAIL",
    f"before={dz['cv_sigma_before']} after={dz['cv_sigma_after']}")
# grep the source for any epsilon in the CV denominator
src = (HERE / "v2" / "membership_scaling_core.py").read_text(encoding="utf-8")
cvsrc = src.split("def _cv")[1].split("def scale_matrix")[0]
rec("F-1", "no epsilon literal inside _cv body",
    "PASS" if ("1e-" not in cvsrc and "eps" not in cvsrc.lower()) else "FAIL", repr(cvsrc[:0]))
# a mixed archive where only SOME coords are dead: cv != sd (the case v1 got wrong)
Cm = C.copy(); Cm[:, -20:] = 0.0
_, dm = m.scale_matrix(Cm)
rec("F-1", "on the reviewer's 20-dead-coordinate fixture cv and sd genuinely differ",
    "PASS" if abs(dm["cv_sigma_after"] - dm["sd_sigma_after"]) > 1e-6 else "FAIL",
    f"cv={dm['cv_sigma_after']:.6f} sd={dm['sd_sigma_after']:.6f}")

# ============================ F-2: cluster labels ============================
print("\n--- F-2 cluster label validation (break attempts) ---")
N = 10
def bc(labels, n=N):
    return lambda: m.build_clusters(labels, n)

probe("F-2", "numpy int64 array as the whole label vector", bc(np.arange(10) // 3), "accept")
probe("F-2", "numpy int32 scalars", bc([np.int32(i // 3) for i in range(10)]), "accept")
probe("F-2", "numpy uint8 scalars", bc([np.uint8(i // 3) for i in range(10)]), "accept")
probe("F-2", "numpy str_ scalars", bc([np.str_("c%d" % (i // 3)) for i in range(10)]), "accept")
probe("F-2", "numpy float64 array of whole numbers (1.0, 2.0)", bc(np.array([1.0] * 5 + [2.0] * 5)), "reject")
probe("F-2", "python floats 1.0/2.0", bc([1.0] * 5 + [2.0] * 5), "reject")
probe("F-2", "np.float64 NaN", bc([np.float64("nan")] + ["B"] * 9), "reject")
probe("F-2", "python float nan", bc([float("nan")] + ["B"] * 9), "reject")
probe("F-2", "None", bc([None] + ["B"] * 9), "reject")
probe("F-2", "np.nan mixed among ints", bc([1, 1, np.nan] + [2] * 7), "reject")
probe("F-2", "EMPTY STRING label", bc([""] * 3 + ["B"] * 7), "?")
probe("F-2", "whitespace-only label", bc(["  "] * 3 + ["B"] * 7), "?")
probe("F-2", "the literal string 'nan'", bc(["nan"] * 3 + ["B"] * 7), "?")
probe("F-2", "the literal string 'None'", bc(["None"] * 3 + ["B"] * 7), "?")
probe("F-2", "unicode look-alikes: latin 'a' vs cyrillic '\\u0430'", bc(["a"] * 5 + ["а"] * 5), "?")
probe("F-2", "NFC/NFD look-alikes: 'e\\u0301' vs '\\u00e9'", bc(["é"] * 5 + ["é"] * 5), "?")
probe("F-2", "very large python ints (2**200)", bc([2 ** 200] * 5 + [2 ** 200 + 1] * 5), "accept")
probe("F-2", "np.int64 max", bc([np.int64(2 ** 63 - 1)] * 5 + [np.int64(2 ** 63 - 2)] * 5), "accept")
probe("F-2", "a SINGLE cluster", bc(["only"] * 10), "accept")
probe("F-2", "one cluster PER QUESTION", bc([f"q{i}" for i in range(10)]), "accept")
probe("F-2", "bool True", bc([True] + ["B"] * 9), "reject")
probe("F-2", "np.bool_ True", bc([np.bool_(True)] + ["B"] * 9), "reject")
probe("F-2", "tuple label", bc([(1, 2)] + ["B"] * 9), "reject")
probe("F-2", "bytes label", bc([b"A"] * 5 + [b"B"] * 5), "reject")
probe("F-2", "list label (unhashable)", bc([[1]] + ["B"] * 9), "reject")
probe("F-2", "0-d numpy array label", bc([np.array(1)] + [np.array(2)] * 9), "?")
probe("F-2", "1-element numpy array label", bc([np.array([1])] + [np.array([2])] * 9), "reject")
probe("F-2", "length mismatch (9 labels, 10 questions)", bc(["A"] * 9), "reject")
probe("F-2", "length mismatch (11 labels, 10 questions)", bc(["A"] * 11), "reject")
probe("F-2", "empty label list, 0 questions", lambda: m.build_clusters([], 0), "?")
probe("F-2", "generator of labels", lambda: m.build_clusters((("c%d" % (i // 3)) for i in range(10)), 10), "accept")
probe("F-2", "decimal.Decimal labels", bc(__import__("decimal").Decimal(1) * np.array([1]) if False else
                                           [__import__("decimal").Decimal(1)] * 5 + [__import__("decimal").Decimal(2)] * 5), "reject")
probe("F-2", "enum.IntEnum labels (an Integral subclass)",
      bc(list(__import__("enum").IntEnum("E", "A B")) * 5), "?")

# NEGATIVE CONTROL for the whole F-2 battery: the v1 core must ACCEPT what v2 rejects
spec1 = importlib.util.spec_from_file_location("mc1", HERE / "v1" / "membership_scaling_core.py")
m1 = importlib.util.module_from_spec(spec1); sys.modules["mc1"] = m1; spec1.loader.exec_module(m1)
g1 = np.ones((10, 4));
try:
    r1 = m1.cluster_bootstrap(g1, g1, [1, "1"] + [2] * 8, seed=1, replicates=50)
    rec("F-2", "NEGATIVE CONTROL: v1 silently ACCEPTS the mixed-type label vector",
        "PASS(control reproduces the v1 defect)", f"n_clusters={r1.get('n_clusters')}")
except Exception as e:
    rec("F-2", "NEGATIVE CONTROL: v1 mixed-type", "UNEXPECTED", f"{type(e).__name__}: {e}")
try:
    r1b = m1.cluster_bootstrap(g1, g1, [float("nan")] * 2 + [1] * 8, seed=1, replicates=50)
    rec("F-2", "NEGATIVE CONTROL: v1 silently ACCEPTS a NaN label (question loss)",
        "PASS(control reproduces the v1 defect)", f"n_clusters={r1b.get('n_clusters')}")
except Exception as e:
    rec("F-2", "NEGATIVE CONTROL: v1 NaN label", f"raised {type(e).__name__}", str(e)[:120])

# ---- exactly-one-cluster membership, proved by exhaustive check on many random label vectors ----
print("\n--- F-2 partition property, randomized ---")
bad = 0
rg = np.random.default_rng(9)
for t in range(300):
    n = int(rg.integers(1, 40))
    k = int(rg.integers(1, n + 1))
    labs = [f"c{int(x)}" for x in rg.integers(0, k, size=n)]
    ordered, members, cd = m.build_clusters(labs, n)
    allidx = np.sort(np.concatenate([members[c] for c in ordered]))
    if not np.array_equal(allidx, np.arange(n)) or cd["questions_covered_at_construction"] != n:
        bad += 1
rec("F-2", "300 random label vectors: every question in exactly one cluster",
    "PASS" if bad == 0 else "FAIL", f"{bad} violations")

# does cluster_bootstrap lose slots?
print("\n--- F-2 no slot loss in the bootstrap ---")
labs = ["A"] * 2 + ["B"] * 3 + ["C"] * 5
vals = np.arange(10, dtype=float)[:, None] * np.ones((1, 4))
res = m.cluster_bootstrap(vals, vals, labs, seed=3, replicates=200)
rec("F-2", "'clusters not drawn' is reported and distinct from loss",
    "PASS" if (res["mean_clusters_not_drawn_per_replicate"] > 0 and res["questions_lost_to_invalid_labels"] == 0
               and "not_drawn_is_not_loss" in res) else "FAIL",
    f"not_drawn={res['mean_clusters_not_drawn_per_replicate']:.3f}")

# ============================ M16: is the partition guard reachable? ============================
print("\n--- M16 reachability of the partition coverage proof ---")
srcb = src.split("def build_clusters")[1].split("\ndef ")[0]
# The loop appends index i exactly once per i, so covered == len(labels) == n_questions always.
# Empirically try to reach it via any public entry point with pathological but VALID labels.
reached = []
for labs_try in ([f"c{i%3}" for i in range(10)], [0] * 10, [i for i in range(10)],
                 [np.int64(1)] * 10, [2 ** 300] * 5 + [2 ** 300 + 1] * 5):
    try:
        m.build_clusters(labs_try, len(labs_try))
    except m.DesignViolation as e:
        if "partition" in str(e) or "does not partition" in str(e):
            reached.append(str(e))
rec("M16", "partition/coverage guard reachable through the public API on valid labels",
    "NOT REACHED" if not reached else "REACHED", reached[:2])
# structural argument, checked mechanically: exactly one append per index
import ast as _ast
fn = [n for n in _ast.walk(_ast.parse(src)) if isinstance(n, _ast.FunctionDef) and n.name == "build_clusters"][0]
appends = [n for n in _ast.walk(fn) if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)
           and n.func.attr == "append" and isinstance(n.func.value, _ast.Subscript)]
rec("M16", "AST: exactly one members[k].append(i) site, inside the single enumerate loop",
    "PASS" if len(appends) == 1 else "FAIL", f"{len(appends)} append sites")
# Can a custom Integral collapse two labels to one key? int(x) is the key.
class Weird(numbers.Integral):
    def __init__(self, v): self.v = v
    def __int__(self): return 0            # every label maps to key 0
    def __index__(self): return 0
    def __hash__(self): return hash(self.v)
    def __eq__(self, o): return isinstance(o, Weird) and o.v == self.v
    for _n in ("__abs__","__add__","__and__","__ceil__","__floor__","__floordiv__","__invert__",
               "__lshift__","__mod__","__mul__","__neg__","__or__","__pos__","__pow__","__radd__",
               "__rand__","__rfloordiv__","__rlshift__","__rmod__","__rmul__","__ror__","__round__",
               "__rpow__","__rrshift__","__rshift__","__rtruediv__","__rxor__","__truediv__",
               "__trunc__","__xor__","__lt__","__le__"):
        locals()[_n] = (lambda *a, **k: NotImplemented)
try:
    o, mem2, cd2 = m.build_clusters([Weird(i) for i in range(10)], 10)
    rec("M16", "key-collapsing Integral subclass: coverage still holds?",
        "ACCEPTED", f"n_clusters={cd2['n_clusters']} covered={cd2['questions_covered_at_construction']}")
except m.DesignViolation as e:
    rec("M16", "key-collapsing Integral subclass", "REJECTED", str(e)[:180])
except Exception as e:
    rec("M16", "key-collapsing Integral subclass", "RAW-EXC", f"{type(e).__name__}: {e}")

# ============================ Assurance: add a ratio under an unanticipated name ============================
print("\n--- assurance: a ratio smuggled under a name the suite does not anticipate ---")
import subprocess, tempfile, shutil, os, re
work = Path(tempfile.mkdtemp(prefix="ratio_"))
shutil.copytree(HERE / "v2", work / "cand")
core_p = work / "cand" / "membership_scaling_core.py"
s = core_p.read_text(encoding="utf-8")
NEW = 'q77x'   # a neutral name no test, docstring or word scan mentions
assert NEW not in s
old_ret = '''    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,'''
assert old_ret in s
s2 = s.replace(old_ret,
   '''    _q77x = (D_ / G) if G != 0.0 else float("nan")
    return {"q77x": _q77x, "G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,''')
core_p.write_text(s2, encoding="utf-8")
r = subprocess.run([sys.executable, "test_membership_scaling_core.py"], cwd=work / "cand",
                   capture_output=True, text=True)
failing = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
rec("assurance", "a genuine Delta/G ratio added under the unanticipated key 'q77x' DIES",
    "KILLED" if r.returncode != 0 else "SURVIVED", f"exit={r.returncode}; {failing[:3]}")
# and one hidden inside a nested dict value rather than as a top-level key
shutil.rmtree(work / "cand"); shutil.copytree(HERE / "v2", work / "cand")
s3 = s.replace('"per_seed_Delta_pp": per_seed_d.tolist(),',
               '"per_seed_Delta_pp": (per_seed_d / np.where(per_seed_g == 0, 1.0, per_seed_g)).tolist(),')
core_p.write_text(s3, encoding="utf-8")
r2 = subprocess.run([sys.executable, "test_membership_scaling_core.py"], cwd=work / "cand",
                    capture_output=True, text=True)
f2 = [l for l in r2.stdout.splitlines() if l.startswith("FAIL")]
rec("assurance", "a ratio hidden INSIDE an existing key's value (per_seed_Delta becomes Delta/G)",
    "KILLED" if r2.returncode != 0 else "SURVIVED", f"exit={r2.returncode}; {f2[:3]}")
# negative control: an unmutated copy must pass
shutil.rmtree(work / "cand"); shutil.copytree(HERE / "v2", work / "cand")
r3 = subprocess.run([sys.executable, "test_membership_scaling_core.py"], cwd=work / "cand",
                    capture_output=True, text=True)
rec("assurance", "NEGATIVE CONTROL: the unmutated copy passes", "PASS" if r3.returncode == 0 else "FAIL",
    f"exit={r3.returncode}")

# ============================ vacuous-check hunt in the v2 suite ============================
print("\n--- vacuous checks in the v2 suite ---")
tsrc = (HERE / "v2" / "test_membership_scaling_core.py").read_text(encoding="utf-8")
ttree = _ast.parse(tsrc)
vac = []
for node in _ast.walk(ttree):
    if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name) and node.func.id == "check":
        if len(node.args) >= 2:
            a = node.args[1]
            if isinstance(a, _ast.BoolOp) and isinstance(a.op, _ast.Or) and any(
                    isinstance(v, _ast.Constant) and v.value is True for v in a.values):
                vac.append((node.lineno, _ast.get_source_segment(tsrc, node.args[0])))
            if isinstance(a, _ast.Constant) and a.value is True:
                vac.append((node.lineno, "literal True: " + str(_ast.get_source_segment(tsrc, node.args[0]))))
        if isinstance(node.args[0], _ast.Constant):
            pass
rec("vacuous", "check(...) calls whose condition is unconditionally true",
    "FOUND" if vac else "NONE", vac)

# ============================ regression on core behaviours ============================
print("\n--- regression ---")
NQ, NK = 13, 10
rg2 = np.random.default_rng(1)
frac = {a: rg2.uniform(0.05, 0.95, size=(NQ, NK)) for a in m.ARMS}
qids = [f"q{i}" for i in range(NQ)]
recs = [{"question_id": qids[q], "rotation_seed": m.ROTATION_SEEDS[k], "arm": a,
         "fractional_R3": float(frac[a][q, k])} for q in range(NQ) for k in range(NK) for a in m.ARMS]
g, gs = m.paired_matrices(recs, qids)
agg = m.aggregate(g, gs)
refG = float(((frac["B32_FRESH"] - frac["RANDOM32_FRESH"]) * 100).mean(axis=0).mean())
refGS = float(((frac["SCALED_B32"] - frac["SCALED_RANDOM32"]) * 100).mean(axis=0).mean())
rec("regression", "G_bar and Delta_bar match a from-scratch reference",
    "PASS" if abs(agg["G_bar_pp"] - refG) < 1e-12 and abs(agg["Delta_bar_pp"] - (refGS - refG)) < 1e-12 else "FAIL",
    f"{agg['G_bar_pp']:.9f}")
rec("regression", "output schema is exactly AGGREGATE_KEYS",
    "PASS" if set(agg) == set(m.AGGREGATE_KEYS) else "FAIL", sorted(set(agg) ^ set(m.AGGREGATE_KEYS)))
qb = m.question_bootstrap(g, gs, seed=99, replicates=200)
qb2 = m.question_bootstrap(g, gs, seed=99, replicates=200)
rec("regression", "question_bootstrap is deterministic in the seed",
    "PASS" if qb["Delta_bar_pp"] == qb2["Delta_bar_pp"] else "FAIL")
cb = m.cluster_bootstrap(g, gs, [f"c{i%4}" for i in range(NQ)], seed=99, replicates=200)
cb2 = m.cluster_bootstrap(g, gs, [f"c{i%4}" for i in range(NQ)], seed=99, replicates=200)
rec("regression", "cluster_bootstrap is deterministic in the seed",
    "PASS" if cb["Delta_bar_pp"] == cb2["Delta_bar_pp"] else "FAIL")
# eps fallback: sigma exactly eps still divides (N-5 razor edge preserved)
Ce = np.zeros((2, 96)); Ce[0, 0] = m.EPS_SIGMA; Ce[1, 0] = -m.EPS_SIGMA
De, de = m.scale_matrix(Ce)
rec("regression", "N-5 razor edge preserved: sigma exactly eps takes the DIVIDE branch",
    "PASS" if abs(np.diag(De)[0] - 1.0 / m.EPS_SIGMA) < 1 else "OBSERVE", f"d0={np.diag(De)[0]:.4g}")
# F-3 duplicate ids
dup = list(recs)
probe("regression", "F-3 duplicate question ids rejected by name",
      lambda: m.validate_per_question_records(recs, qids[:-1] + [qids[0]]), "reject")
# safe_write_json still refuses overwrite
import tempfile as _tf
with _tf.TemporaryDirectory() as td:
    p = Path(td) / "a.json"; m.safe_write_json(p, {"x": 1})
    probe("regression", "safe_write_json refuses overwrite", lambda: m.safe_write_json(p, {"x": 2}), "reject")
# real-data gate: default closed, module global read at call time
probe("regression", "real-data gate closed by default", m.require_real_data_authorization, "reject")

# ============================ README claim check ============================
print("\n--- README claims ---")
rd = (HERE / "v2" / "README_IMPL_V2.md").read_text(encoding="utf-8")
low = rd.lower()
for phrase, why in [("word scan", "does the README still lean on the word scan?"),
                    ("not a proof", "does it disclaim AST-as-proof?"),
                    ("conformance", "does it name the conformance test as the primary guarantee?")]:
    rec("README", f"mentions {phrase!r}", "YES" if phrase in low else "NO", why)

json.dump(rows, open(HERE / "adv_closure_results.json", "w"), indent=1)
print(f"\nrows={len(rows)}")
