#!/usr/bin/env python3
"""Do SIGN96 and standardized float fail on DIFFERENT questions?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

An external reviewer reports a per-question "oracle selector" upper bound --
what you would score if, for each question, an oracle that already knew the
answer picked whichever of the two arms did better -- at 90.21 / 86.07 /
54.98 on LME / PerLTQA / RealTalk, and 51 RealTalk questions where SIGN96
strictly beats float.  This recomputes both from our own per-query rows.

The oracle number is NOT an achievable system score and not a fusion of two
result lists; it is a ceiling on ARM SELECTION, computed with the labels.
Its only use is to say whether the two arms fail on the same questions.  If
the oracle equals max(sym, float_std) the arms are nested and there is
nothing to exploit; the further above both it sits, the more complementary
they are.

Also reported, because the ceiling alone is misleading:
  * the reverse oracle (an adversary picking the WORSE arm) -- the floor
  * how often each arm strictly wins
  * what a fixed choice of the better arm PER BENCHMARK already gets,
    which is the cheap baseline any selector must beat
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

K = 10
A, B = "sym", "float_std"


def main():
    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "arms": [A, B], "k": K,
           "oracle_is_not_a_system_score": (
               "computed with the gold labels; it is the ceiling on choosing "
               "between two arms per question, not a reachable result and not "
               "a fusion of two ranked lists"),
           "benchmarks": {}}
    for name, fn in (("perltqa", H.run_perltqa), ("lme", H.run_lme),
                     ("realtalk", H.run_realtalk)):
        rows, cluster = fn()
        a = np.asarray([r[f"hit{K}_{A}"] for r in rows], dtype=float)
        b = np.asarray([r[f"hit{K}_{B}"] for r in rows], dtype=float)
        best = np.maximum(a, b)
        worst = np.minimum(a, b)
        fixed = max(a.mean(), b.mean())          # better arm, chosen once
        d = a - b
        out["benchmarks"][name] = {
            "n_queries": len(rows),
            f"{A}_pct": float(a.mean() * 100),
            f"{B}_pct": float(b.mean() * 100),
            "oracle_pct": float(best.mean() * 100),
            "anti_oracle_pct": float(worst.mean() * 100),
            "fixed_better_arm_pct": float(fixed * 100),
            "oracle_headroom_over_fixed_pp": float(best.mean() * 100 - fixed * 100),
            f"queries_{A}_strictly_better": int(np.count_nonzero(d > 0)),
            f"queries_{B}_strictly_better": int(np.count_nonzero(d < 0)),
            "queries_equal": int(np.count_nonzero(d == 0)),
        }
        v = out["benchmarks"][name]
        print(f"{name:9s} n={v['n_queries']:5d}  "
              f"{A} {v[f'{A}_pct']:6.2f}  {B} {v[f'{B}_pct']:6.2f}  "
              f"-> oracle {v['oracle_pct']:6.2f}  "
              f"(taban {v['anti_oracle_pct']:6.2f})   "
              f"{A} kazanan {v[f'queries_{A}_strictly_better']:4d} / "
              f"{B} kazanan {v[f'queries_{B}_strictly_better']:4d}",
              flush=True)

    with open(os.path.join(HERE, "AUDIT_ORACLE.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\nwrote AUDIT_ORACLE.json")


if __name__ == "__main__":
    main()
