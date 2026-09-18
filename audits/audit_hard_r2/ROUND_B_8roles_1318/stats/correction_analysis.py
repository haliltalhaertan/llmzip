"""Round-2 stats audit: project-wide multiple-comparison correction table (task B).

READ-ONLY on sources; writes only to this stats dir.
Collects every stored excludes_zero=True contrast, converts 95% CI -> z -> p,
and tests survival at Bonferroni alphas for family sizes 15 / 50 / 267.
SE-from-CI uses normal approx SE=(hi-lo)/3.92; labelled APPROX where pairing ignored.
"""
import json, math
from scipy.stats import norm

PKG = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/stats/correction_table.json"
rows = []


def add(name, est, lo, hi, n=None, clusters=None, note=""):
    se = (hi - lo) / 3.92 if hi > lo else float("nan")
    z = abs(est) / se if se and se > 0 else 0.0
    p = 2 * norm.sf(z)
    rows.append({"claim": name, "est_pp": round(est, 2),
                 "CI95": [round(lo, 2), round(hi, 2)],
                 "z_approx": round(z, 2), "p_approx": p,
                 "n": n, "clusters": clusters, "note": note})


def walk_contrasts(o, prefix, n=None, clusters=None):
    if isinstance(o, dict):
        if "mean_diff_pp" in o and ("ci95_lo_pp" in o):
            add(prefix, o["mean_diff_pp"], o["ci95_lo_pp"], o["ci95_hi_pp"],
                o.get("n", n), o.get("clusters", clusters))
        elif "vs_BM25_alone_pp" in o:
            add(prefix, o["vs_BM25_alone_pp"], o["ci_lo"], o["ci_hi"], n, clusters)
        for k, v in o.items():
            if k.startswith("_"):
                continue
            walk_contrasts(v, prefix + "/" + str(k), n or o.get("n_queries"),
                           clusters or o.get("n_clusters"))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk_contrasts(v, prefix + "[%d]" % i, n, clusters)


# 1. quant ITQ/random/median vs FULL (RealTalk qscale Hit@10 focus + the ITQ-vs-random diff)
q = json.load(open(PKG + "/math_r1/quant/RESULTS.json", encoding="utf-8"))
c = q["benchmarks"]["RealTalk"]["contrasts_vs_FULL_pp"]
for arm in ("RAND_20260916-FULL/qscale", "RAND_20260917-FULL/qscale",
            "RAND_20260918-FULL/qscale", "MED-FULL/qscale"):
    try:
        o = c[arm]["hit10"]
        add("quant/RealTalk/%s/Hit@10" % arm.replace("/", "_"), o["mean_diff_pp"],
            o["ci95_lo_pp"], o["ci95_hi_pp"], 705, 10)
    except KeyError as e:
        print("missing", arm, e)
# ITQ-minus-random: worker quant/REPORT.md CIs vs each of 3 seeds (top-level REPORT
# quotes -2.27 = ITQ minus 3-seed MEAN with NO CI; worker CIs are seed-specific)
for est, lo, hi, seed in ((-2.41, -4.74, -0.14, 16), (-2.55, -4.73, -0.54, 17),
                          (-1.84, -3.70, -0.28, 18)):
    add("quant/RealTalk/ITQ-minus-RANDseed%d/qscale/Hit@10" % seed, est, lo, hi,
        705, 10, "worker REPORT.md; top-level -2.27 quoted WITHOUT any CI")

# 2. repr mechanism + rare band + ablation perltqa + T2 lo/hi handled separately
for fn, pre in (("coordinator/repr_fr3_mechanism.json", "repr"),
                ("coordinator/rare_band_decisive.json", "rarebad"),
                ("coordinator/repr_results.json", "repr_res")):
    try:
        walk_contrasts(json.load(open(PKG + "/" + fn, encoding="utf-8")), pre)
    except Exception as e:
        print("skip", fn, e)

# 3. ablation perltqa channel contrasts: find explicit contrast dicts
ab = json.load(open(PKG + "/ablation_r2/perltqa/RESULTS.json", encoding="utf-8"))
walk_contrasts(ab, "abl_perltqa")

dec = json.load(open(PKG + "/coordinator/DECISION_TESTS.json", encoding="utf-8"))
walk_contrasts(dec.get("T2_rerank", {}), "T2")

# 4. channel ablations: CIs live in worker REPORT.md tables, not JSON -> transcribed
abl_rows = [
    # PerLTQA (n=8265, 30 clusters): arm-FULL
    ("abl_PQ/NO_LSA-qscale/FR@3", -1.23, -2.16, -0.30, 8265, 30),
    ("abl_PQ/NO_CHAR-sym/Hit@10", 1.39, 0.35, 2.48, 8265, 30),
    ("abl_PQ/NO_CHAR-sym/FR@3", 3.13, 1.96, 4.27, 8265, 30),
    ("abl_PQ/NO_CHAR-qscale/Hit@10", 0.83, 0.14, 1.49, 8265, 30),
    ("abl_PQ/NO_CHAR-qscale/FR@3", 2.26, 1.60, 2.96, 8265, 30),
    ("abl_PQ/WORD_ONLY-sym/Hit@10", 2.13, 0.86, 3.48, 8265, 30),
    ("abl_PQ/WORD_ONLY-sym/FR@3", 2.40, 1.13, 3.69, 8265, 30),
    ("abl_PQ/WORD_ONLY-qscale/Hit@10", 1.37, 0.50, 2.21, 8265, 30),
    ("abl_PQ/WORD_ONLY-qscale/FR@3", 2.09, 1.24, 2.94, 8265, 30),
    # RealTalk (n=705, 10 clusters): arm-FULL
    ("abl_RT/NO_LSA-qscale/Hit@10", 2.41, -0.28, 5.15, 705, 10),
    ("abl_RT/NO_LSA-qscale/FR@3", 3.44, -0.56, 7.56, 705, 10),
    ("abl_RT/NO_CHAR-qscale/Hit@10", -5.82, -8.85, -2.76, 705, 10),
    ("abl_RT/WORD_ONLY-qscale/Hit@10", -3.40, -5.36, -1.63, 705, 10),
    # RRF first-stage (REPORT S4, n=705 RealTalk; +3.12 quoted SIG with NO CI)
    ("firststage/RRF-CODE/pool100", 5.67, 3.23, 8.20, 705, 10),
]
for nm, e, lo, hi, n, cl in abl_rows:
    add(nm, e, lo, hi, n, cl, "transcribed from worker REPORT.md table" if nm.startswith("abl_") else "")

fams = {"T2_only_15": 15, "per_experiment_50": 50, "project_combos_267": 267}
for r in rows:
    r["survives"] = {k: bool(r["p_approx"] < 0.05 / m) for k, m in fams.items()}

sig = [r for r in rows if True]
json.dump({"family_alphas": {k: 0.05 / m for k, m in fams.items()},
           "contrasts": rows}, open(OUT, "w"), indent=1)
print("total contrasts collected:", len(rows))
for r in rows:
    if "T2" in r["claim"] or "ITQ-minus" in r["claim"] or "rare" in r["claim"] or "SHIFT" in r["claim"].upper() or "WORD" in r["claim"].upper() or "NO_" in r["claim"]:
        print("%-72s est=%+7.2f p=%.2g surv15=%s surv50=%s surv267=%s %s" %
              (r["claim"][-72:], r["est_pp"], r["p_approx"],
               r["survives"]["T2_only_15"], r["survives"]["per_experiment_50"],
               r["survives"]["project_combos_267"], r["note"]))
