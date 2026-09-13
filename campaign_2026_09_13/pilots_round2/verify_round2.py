#!/usr/bin/env python3
"""Round-2 self-consistency checks for EDITION-2 bundle. Stdlib only.
Run from bundle root: python3 verify_round2.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]   # <worktree-or-bundle-root>/pilots/axis_attack_2026-09-12/round2/
R2 = ROOT / "pilots" / "axis_attack_2026-09-12" / "round2"
fails = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print(("PASS" if ok else "FAIL"), "-", name, ("| " + str(detail)) if detail else "")
    if not ok:
        fails.append(name)


def load_manifest(mf):
    lines = [l for l in mf.read_text(encoding="utf-8").splitlines() if l.strip()]
    bad = []
    for ln in lines:
        want, rel = ln.split("  ", 1)
        f = ROOT / rel
        if not f.exists():
            bad.append(rel + " (missing)")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != want:
            bad.append(rel + " (hash)")
    return len(lines), bad


# 1) round-2 manifest
n, bad = load_manifest(R2 / "HASHES_AXIS_PILOT_R2.txt")
check(f"manifest HASHES_AXIS_PILOT_R2.txt: all {n} entries verify", not bad, "; ".join(bad[:3]))

# 2) report checks
rep = (R2 / "ROUND2_REPORT.md").read_text(encoding="utf-8")
check("report: labels present", "[LOCAL EXPLORATORY PILOT — ROUND 2]" in rep)
check("report: review section filled (no PENDING)", "## 6. Independent review verdicts" in rep and "[PENDING" not in rep)
check("report: key numbers present", "63 / 250 / 157" in rep and "+3.39 pp" in rep and "diff 0.0" in rep)

# 3) R2B
b = json.loads((R2 / "wsl_details" / "r2b_details.json").read_text(encoding="utf-8"))
check("R2B: split 239/231", b["split"]["n_train"] == 239 and b["split"]["n_test"] == 231)
check("R2B: gate max abs diff <= 1e-15", b["gate_native"]["max_abs_diff"] <= 1e-15, b["gate_native"]["max_abs_diff"])
check("R2B: drop64 test FR", abs(b["arms"]["drop64"]["test_FR"] - 0.48378066378066376) < 1e-12, b["arms"]["drop64"]["test_FR"])
check("R2B: drop64 gap vs random +3.3943 pp", abs(b["arms"]["drop64"]["gap_vs_random_pp"] - 3.3943001443) < 1e-6)
check("R2B: drop64 W/T/L 63/124/44", b["best_learned"]["WTL_vs_random_mean_tol1e-12"] == [63, 124, 44])
check("R2B: random64 mean", abs(b["random_mean"]["64"]["test"] - 0.4498376623376623) < 1e-12)

# 4) R2C
c = json.loads((R2 / "wsl_details" / "r2c_details.json").read_text(encoding="utf-8"))
check("R2C: gate native exact 0.0", c["gate"]["native_diff"] == 0.0 and c["gate"]["native"] == 0.23654714666441054)
check("R2C: haar diff >= -1e-13", c["gate"]["haar_diff"] >= -1e-13, c["gate"]["haar_diff"])
bm = c["block_means"]
check("R2C: monotone MATCHED > RANDPAIR > ANTIMATCHED",
      bm["MATCHED"] > bm["RANDPAIR"] > bm["ANTIMATCHED"], f"{bm['MATCHED']:.6f} > {bm['RANDPAIR']:.6f} > {bm['ANTIMATCHED']:.6f}")
check("R2C: BOT_k48 value", abs(c["arms"]["BOT_k48"]["fractional_R3"] - 0.18112226499522918) < 1e-12)

# 5) R2A
a = json.loads((R2 / "wsl_details" / "r2a_per_q.json").read_text(encoding="utf-8"))
w = a["WTL_overall"]
check("R2A: W/T/L 63/250/157",
      (w.get("W"), w.get("T"), w.get("L")) == (63, 250, 157) or [w.get("W"), w.get("T"), w.get("L")] == [63, 250, 157],
      w)
check("R2A: gate diffs all 0.0", all(v == 0.0 for v in a["gate_diffs"].values()), a["gate_diffs"])

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): " + "; ".join(fails))
    sys.exit(1)
print("RESULT: ALL ROUND-2 CHECKS PASS")
