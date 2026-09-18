#!/usr/bin/env python3
"""[LOCAL AUDIT] Task B — independent aggregation from committed per-question T4C2 artifact."""
import csv, json, statistics

QLEVEL = "/home/mdp/muse-work/llmzip-audit/docs/v52/task4c2/V52_T4C2_question_level.csv"
AGG = "/home/mdp/muse-work/llmzip-audit/docs/v52/task4c2/V52_T4C2_aggregate.csv"

rows = list(csv.DictReader(open(QLEVEL)))
n = len(rows)
print(f"n_questions = {n}")
assert n == 470, n

def col(name):
    return [float(r[name]) for r in rows]

fU = col("float96_uncentered_fractional_r3")
fC = col("float96_centered_fractional_r3")
Sg = col("sign96_centered_fractional_r3")
It = col("itq96_centered_fractional_r3")

def mean(x): return sum(x)/len(x)

mU, mC, mS, mI = mean(fU), mean(fC), mean(Sg), mean(It)
print(f"mean float(Y) uncentered = {mU!r}  ({100*mU:.6f}%)")
print(f"mean float(C) centered   = {mC!r}  ({100*mC:.6f}%)")
print(f"mean sign(C)  native     = {mS!r}  ({100*mS:.6f}%)")
print(f"mean ITQ(C)              = {mI!r}  ({100*mI:.6f}%)")

# Anchor gates
NATIVE_ANCHOR = 0.5419751773049645
print(f"|native - anchor| = {abs(mS - NATIVE_ANCHOR):.3e}")
print(f"float(Y) vs 44.16% anchor: {100*mU:.6f}% -> reproduces 44.16%? {abs(100*mU-44.16)<0.005}")
print(f"float(C) vs 44.16% anchor: {100*mC:.6f}% -> reproduces 44.16%? {abs(100*mC-44.16)<0.005}")

# Cross-check against committed aggregate CSV
agg = {r["method"]: float(r["Fractional_R3"]) for r in csv.DictReader(open(AGG))}
print("aggregate-CSV cross-check:",
      {k: f"{abs(v - {'FLOAT96_UNCENTERED': mU, 'FLOAT96_CENTERED': mC, 'SIGN96_CENTERED': mS, 'ITQ96_CENTERED': mI}[k]):.2e}" for k, v in agg.items()})

# Decomposition (pp)
centering = (mC - mU) * 100
binar = (mS - mC) * 100
total_uncentered_base = (mS - mU) * 100
cross_fY_sY = None  # sign(Y) not stored; cannot compute
print(f"[float(Y)->float(C)] centering gain    = {centering:+.6f} pp")
print(f"[float(C)->sign(C)]  binarization gain = {binar:+.6f} pp")
print(f"[float(Y)->sign(C)]  total             = {total_uncentered_base:+.6f} pp")
print(f"centering share of total = {100*centering/total_uncentered_base:.2f}%")

# W/T/L + medians for both steps
def wtl(a, b):
    import numpy as np
    d = (np.array(a) - np.array(b)) * 100.0
    eps = 1e-12
    return int((d > eps).sum()), int((abs(d) <= eps).sum()), int((d < -eps).sum()), float(np.median(d))

print("W/T/L sign-vs-floatC:", wtl(Sg, fC), "(frozen: 122/304/44, median 0.0)")
print("W/T/L floatC-vs-floatU:", wtl(fC, fU), "(frozen: 7/458/5, median 0.0)")

# check precomputed pp columns consistent
d1 = col("sign_minus_centered_float_fractional_pp")
d2 = col("centered_minus_uncentered_float_fractional_pp")
import numpy as np
print("max|precomputed - recomputed| sign-floatC pp col:",
      float(np.max(np.abs(np.array(d1) - (np.array(Sg)-np.array(fC))*100))))
print("max|precomputed - recomputed| floatC-floatU pp col:",
      float(np.max(np.abs(np.array(d2) - (np.array(fC)-np.array(fU))*100))))

# D96 printed-precision nit: recompute from anchor constants
haar = 0.3827166666666667
D = (haar - NATIVE_ANCHOR) * 100
print(f"D96 from constants = {D!r}  (script: -15.925851063829777; checkpoint: -15.925851063830)")

out = {
    "n": n,
    "mean_floatY_uncentered": mU, "mean_floatC_centered": mC,
    "mean_signC_native": mS, "mean_itq": mI,
    "native_minus_anchor_abs": abs(mS - NATIVE_ANCHOR),
    "centering_gain_pp": centering, "binarization_gain_pp": binar,
    "total_vs_uncentered_pp": total_uncentered_base,
    "wtl_sign_vs_floatC": wtl(Sg, fC), "wtl_floatC_vs_floatU": wtl(fC, fU),
    "D96_from_constants": D,
}
json.dump(out, open("/tmp/audit1/taskB_numbers.json", "w"), indent=2)
print("wrote /tmp/audit1/taskB_numbers.json")
