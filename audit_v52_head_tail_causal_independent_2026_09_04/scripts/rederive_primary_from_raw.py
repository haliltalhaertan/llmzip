"""G4b/G5/G6: rebuild the primary numbers from the committed per-seed CSVs (NOT from the
summary JSON's own fields), cross-check against the independently-written subset_r3.csv, re-apply
the preregistered band rule, and compute the five-draw dispersion.

Usage:  python rederive_primary_from_raw.py <path to research/v52 at the audit commit>
e.g.    git archive 7799502b research/v52 | tar -x -C /tmp/t && \
        python rederive_primary_from_raw.py /tmp/t/research/v52
"""
import csv, json, statistics, sys
from pathlib import Path

T = Path(sys.argv[1] if len(sys.argv) > 1 else "research/v52")

def rows(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

BENCHES = [
    ("LoCoMo",      "locomo_head_tail_outputs",      "locomo_head_tail",      0.23654714666441054, 0.13770827054136),
    ("LongMemEval", "longmemeval_head_tail_outputs", "longmemeval_head_tail", 0.5419751773049646,  0.38271666666667),
]

for bench, d, pre, nat, fh in BENCHES:
    sr   = rows(T / d / f"{pre}_seed_results.csv")
    sub  = rows(T / d / f"{pre}_subset_r3.csv")
    summ = json.loads((T / d / f"{pre}_summary.json").read_text())
    seeds = [int(r["seed"]) for r in sr]
    vals  = [float(r["Fractional_R3"]) for r in sr]
    full  = {int(r["seed"]): float(r["Fractional_R3"]) for r in sub if r["subset"] == "Full96"}

    print(f"===== {bench} =====")
    print("  seeds:", seeds, "== preregistered 56001..56005:", seeds == [56001, 56002, 56003, 56004, 56005])
    for s, v in zip(seeds, vals):
        js = float(summ["primary"]["seed_R3"][str(s)])
        print(f"  seed {s}: seed_results={v!r}  summaryJSON={js!r}  match={v == js}"
              f"  | subset_r3.Full96={full[s]!r}  maxdiff={abs(v - full[s]):.3e}")

    mean   = sum(vals) / len(vals)
    L_full = nat - fh
    L_2    = nat - mean
    rho    = L_2 / L_full
    P      = summ["primary"]
    print(f"  REBUILT mean(seed R@3) = {mean!r}   declared {P['head_tail_haar_mean_R3']!r}  match={mean == P['head_tail_haar_mean_R3']}")
    print(f"  REBUILT L_full = {L_full!r}  declared {P['L_full']!r}  match={L_full == P['L_full']}")
    print(f"  REBUILT L_2    = {L_2!r}  declared {P['L_2']!r}  match={L_2 == P['L_2']}")
    print(f"  REBUILT rho_2  = {rho!r}  declared {P['rho_2']!r}  match={rho == P['rho_2']}")

    band = ("[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]" if rho <= 0.25 else
            "[THREE-BAND OR FINER STRUCTURE REQUIRED LEAD]" if rho >= 0.75 else
            "[MIXED TWO-SUBSPACE / FINER-STRUCTURE REGIME]")
    print(f"  REBUILT regime = {band}  declared {P['regime']}  match={band == P['regime']}")

    per = [(nat - v) / L_full for v in vals]
    sd  = statistics.stdev(vals)
    sem = sd / len(vals) ** 0.5
    sem_rho = sem / L_full
    print(f"  G6 per-seed rho_2: min={min(per):.6f} max={max(per):.6f} range={max(per) - min(per):.6f}")
    print(f"  G6 per-seed R@3 sd={sd:.6g}  sem={sem:.6g}")
    print(f"  G6 sem(rho_2)={sem_rho:.6f} -> rho_2 = {rho:.4f} +/- {sem_rho:.4f} (1 s.e.); "
          f"95% CI ~ [{rho - 2.776 * sem_rho:.4f}, {rho + 2.776 * sem_rho:.4f}] (t, 4 d.f.)")
    print(f"  G6 seeds inverting the sign of L_2 (intervention beat native): "
          f"{[s for s, v in zip(seeds, vals) if v > nat]}")
    print(f"  G6 distance of rho_2 from the 0.25 boundary: {(0.25 - rho) / sem_rho:.2f} s.e.")
    print(f"  G6 all individual seeds inside the <=0.25 band: {all(x <= 0.25 for x in per)}")
