"""Negative and positive controls for locomo_denominator_dispersion.py. A check that cannot fail is
not evidence; every guard below is exercised in the direction that must be REJECTED."""
from __future__ import annotations
import importlib.util, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ldd", HERE / "locomo_denominator_dispersion.py")
m = importlib.util.module_from_spec(spec); sys.modules["ldd"] = m; spec.loader.exec_module(m)

fails = 0
def check(name, ok, detail=""):
    global fails
    print(("ok    " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok: fails += 1
def expect_raise(name, fn, needle=""):
    try:
        fn(); check(name, False, "no exception")
    except RuntimeError as e:
        check(name, needle in str(e), str(e)[:70])

# breakdown algebra
n, a = 0.5, 0.4
h = m.breakdown_denominator(n, a)
check("breakdown point puts rho exactly at the gate", abs(m.rho(n, a, h) - m.GATE) < 1e-15)
check("rho rises as H rises toward native (direction)", m.rho(n, a, 0.30) < m.rho(n, a, 0.35))
m.directional_control(); check("directional control passes on correct rho", True)
# a deliberately inverted rho must trip the directional control
orig = m.rho
m.rho = lambda n_, a_, f_: -(orig(n_, a_, f_))
expect_raise("directional control REJECTS an inverted rho", m.directional_control, "directional")
m.rho = orig

# analyse() on a synthetic panel with KNOWN dispersion, against a synthetic boundary summary
def boundary(native, arms, frozen=m.INHERITED_FULL_HAAR):
    return {"primary": {"native_R3": native, "frozen_full_haar_R3": frozen,
                        "arm_stats": {k: {"mean_R3": v, "rho": m.rho(native, v, frozen)} for k, v in arms.items()}}}
native = 0.23654714666441054
panel = {s: m.INHERITED_FULL_HAAR + (i - 4.5) * 0.002 for i, s in enumerate(range(59001, 59011))}   # sd known
sd = (sum(((i - 4.5) * 0.002) ** 2 for i in range(10)) / 9) ** 0.5
res = m.analyse(panel, boundary(native, {"B32": 0.2284, "B48": 0.2066}))
check("sample sd re-derived exactly", abs(res["fresh_panel"]["sample_sd"] - sd) < 1e-15)
check("se of a FIVE-seed mean = sd/sqrt(5)", abs(res["fresh_panel"]["se_of_five_seed_mean"] - sd / math.sqrt(5)) < 1e-15)
check("B32 sufficient, B48 excluded on this synthetic", res["arms"]["B32"]["verdict"] == "sufficient" and res["arms"]["B48"]["verdict"] == "not sufficient")
check("B48 breakdown needs a NEGATIVE shift (denominator must fall)", res["arms"]["B48"]["shift_needed_abs"] < 0)
check("B32 breakdown needs a POSITIVE shift (denominator must rise)", res["arms"]["B32"]["shift_needed_abs"] > 0)
check("tightest arm is B48", res["tightest_arm"] == "B48")
# negative control: a huge synthetic dispersion must put the B48 breakdown INSIDE the interval
wide = {s: m.INHERITED_FULL_HAAR + (i - 4.5) * 0.008 for i, s in enumerate(range(59001, 59011))}
res_w = m.analyse(wide, boundary(native, {"B32": 0.2284, "B48": 0.2066}))
check("with 4x dispersion the B48 breakdown falls INSIDE the 95% interval (check can fail)", res_w["arms"]["B48"]["breakdown_outside_95pct_interval"] is False)
check("...while B32 stays outside", res_w["arms"]["B32"]["breakdown_outside_95pct_interval"] is True)
# guards
expect_raise("analyse REJECTS a boundary summary with a different frozen denominator",
             lambda: m.analyse(panel, boundary(native, {"B32": 0.2284}, frozen=0.14)), "different frozen")
bad = boundary(native, {"B32": 0.2284}); bad["primary"]["arm_stats"]["B32"]["rho"] += 1e-6
expect_raise("analyse REJECTS a recorded rho that does not re-derive", lambda: m.analyse(panel, bad), "rho mismatch")
# real bytes: the committed per-question file must yield exactly ten seeds x 1535 questions
real = m.fresh_panel_from_rows(m.PER_QUESTION)
check("committed per-question rows: seeds 59001..59010, 1535 questions each", sorted(real) == list(range(59001, 59011)))
import json
summ = json.loads((m.R / "locomo_scale_outputs" / "locomo_scale_summary.json").read_text(encoding="utf-8"))
check("fresh panel mean re-derived from rows matches the committed summary to 1e-12",
      abs(sum(real.values()) / 10 - summ["primary"]["arm_means"]["FULLHAAR_FRESH"]) < 1e-12)

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
raise SystemExit(1 if fails else 0)
