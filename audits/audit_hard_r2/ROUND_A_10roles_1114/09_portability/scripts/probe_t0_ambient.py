"""T0: as-shipped t1() executed from cleanroom copy location (AMBIENT paths).
Labels ambient: this run READS /mnt/c/... outside the package by design of the
as-shipped script. It proves on-machine behavior, NOT portability.
"""
import importlib.util
import json
import os
import sys
import time

OWN = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/09_portability"
PKG = os.path.join(OWN, "cleanroom", "coordinator", "decision_tests_pkg.py")

spec = importlib.util.spec_from_file_location("dt_pkg", PKG)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

t0 = time.time()
out = mod.t1()
dt = time.time() - t0

# Record which RT/lib paths the as-shipped code resolved (static confirmation)
print("W =", mod.W)
print("elapsed_s =", round(dt, 2))
print("strongest =", out["strongest_bm25"])
print("C1 =", out["verdict"]["C1_gate_plus2pp_fr3"])

json.dump(out, open(os.path.join(OWN, "outputs", "T0_ambient_T1.json"), "w"), indent=1)
print("WROTE outputs/T0_ambient_T1.json")
print("NOTE: ambient run — RT and lib resolved to absolute /mnt/c/... paths outside package.")
