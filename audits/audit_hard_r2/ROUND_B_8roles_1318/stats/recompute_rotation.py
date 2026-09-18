"""Round-2 stats audit: recompute rotation-damage vs archive-size correlation (task E).

READ-ONLY on sources; writes only to this stats dir.
Source: top10_comparison_r1/math_r1/quant/per_query.jsonl (RealTalk, qscale, FULL vs RAND_20260916).
Claim audited: REPORT.md/FINAL_STATE.md "Pearson r(archive size, damage) = -0.78",
  "small (N<700) -6.56 pp / large (N>=1000) -23.13 pp".
"""
import json, math
from collections import defaultdict

SRC = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/quant/per_query.jsonl"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/stats/rotation_recompute.json"

ARCH_N = {"RT01": 662, "RT02": 476, "RT03": 453, "RT04": 422, "RT05": 410,
          "RT06": 1548, "RT07": 1511, "RT08": 1162, "RT09": 1044, "RT10": 1256}

hit = defaultdict(dict)
with open(SRC, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("benchmark") != "RealTalk" or r.get("scorer") != "qscale":
            continue
        if r.get("arm") not in ("FULL", "RAND_20260916"):
            continue
        a = r["archive_id"]
        hit[a].setdefault(r["arm"], []).append(float(r["hit10"]))

rows = []
for a in sorted(hit):
    assert set(hit[a]) == {"FULL", "RAND_20260916"}, a
    f = sum(hit[a]["FULL"]) / len(hit[a]["FULL"])
    d = sum(hit[a]["RAND_20260916"]) / len(hit[a]["RAND_20260916"])
    rows.append({"arch": a, "N": ARCH_N[a], "n_q": len(hit[a]["FULL"]),
                 "full_pct": 100 * f, "rand_pct": 100 * d, "delta_pp": 100 * (d - f)})

import numpy as np
from scipy import stats as st

N = np.array([r["N"] for r in rows], float)
D = np.array([r["delta_pp"] for r in rows], float)
n = len(rows)
r_pear, p_pear = st.pearsonr(N, D)
r_spea, p_spea = st.spearmanr(N, D)
# Fisher-z 95% CI for Pearson
z = math.atanh(max(-0.999999, min(0.999999, r_pear)))
se_z = 1 / math.sqrt(n - 3)
ci = [math.tanh(z - 1.96 * se_z), math.tanh(z + 1.96 * se_z)]
# t-statistic check: t = r*sqrt((n-2)/(1-r^2))
t_stat = r_pear * math.sqrt((n - 2) / (1 - r_pear ** 2))
# leave-one-out range
loo = []
for i in range(n):
    rr, _ = st.pearsonr(np.delete(N, i), np.delete(D, i))
    loo.append({"dropped": rows[i]["arch"], "r": rr})
small = [r["delta_pp"] for r in rows if r["N"] < 700]
large = [r["delta_pp"] for r in rows if r["N"] >= 1000]
mid = [r for r in rows if 700 <= r["N"] < 1000]

out = {
    "n_archives": n,
    "per_archive": [{**r, "full_pct": round(r["full_pct"], 2),
                     "rand_pct": round(r["rand_pct"], 2),
                     "delta_pp": round(r["delta_pp"], 2)} for r in rows],
    "pearson_r": round(float(r_pear), 4),
    "pearson_p_two_sided": float(p_pear),
    "pearson_t_stat_df8": round(float(t_stat), 3),
    "pearson_95CI_fisher": [round(ci[0], 3), round(ci[1], 3)],
    "spearman_rho": round(float(r_spea), 4),
    "spearman_p": float(p_spea),
    "leave_one_out_r": [{**e, "r": round(float(e["r"]), 3)} for e in loo],
    "loo_min": round(float(min(e["r"] for e in loo)), 3),
    "loo_max": round(float(max(e["r"] for e in loo)), 3),
    "small_Nlt700_mean_delta": round(float(sum(small) / len(small)), 2),
    "large_Nge1000_mean_delta": round(float(sum(large) / len(large)), 2),
    "n_small": len(small), "n_large": len(large),
    "archives_in_gap_700_1000": [r["arch"] for r in mid],
    "claim_r": -0.78, "claim_small": -6.56, "claim_large": -23.13,
}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1))
