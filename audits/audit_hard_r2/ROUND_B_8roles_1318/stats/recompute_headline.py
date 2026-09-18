"""Round-2 stats audit: headline-gap uncertainty + per-question-data existence (task C).

READ-ONLY on sources; writes only to this stats dir.
Claims audited:
  H1: 65.67 (fair BM25) vs 57.87 (48B qscale) = -7.80pp Hit@10, RealTalk n=705 (DECISION_TESTS.md T1).
  H2: sym 54.18 vs float 43.69 at k=384 = +10.49pp "sign adds ~10pp" (FINAL_STATE.md).
  H3: ladder steps +5.67 / +2.55 with no CI (LADDER_REALTALK.md).
Checks: (a) is any CI stored? (b) is per-question paired data stored anywhere?
(c) archive-level (n=10) paired analysis from LADDER_CACHE.jsonl as the strongest
    reproducible check; binomial SEs as labelled approximations.
"""
import json, math, os
import numpy as np
from scipy import stats as st

PKG = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
WT = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/stats/headline_recompute.json"
out = {}

# (a) stored CIs?
dec = json.load(open(os.path.join(PKG, "coordinator/DECISION_TESTS.json"), encoding="utf-8"))
t1 = dec["T1_fair_baseline"]
has_ci = any("ci" in json.dumps(v).lower() for v in t1.values())
out["T1_stores_any_CI"] = has_ci
out["T1_code_arms"] = t1["code_arms"]["48B/qscale"]
out["T1_strongest_bm25"] = t1["strongest_bm25"]
lad = json.load(open(os.path.join(PKG, "coordinator/LADDER.json"), encoding="utf-8"))
out["LADDER_arm_keys"] = sorted(lad["arms"])
out["LADDER_stores_per_query"] = False  # aggregates only: hit10/fr3/bytes/n

# (b) hunt for stored per-question fair-BM25 outcomes (frozen_idfonly)
cands = [
    PKG + "/coordinator/why_bm25_per_query.jsonl",
    WT + "/coordinator/why_bm25_per_query.jsonl",
    PKG + "/audit/per_query_bm25_corrected.jsonl",
    WT + "/audit/per_query_bm25_corrected.jsonl",
]
found = {}
for c in cands:
    if os.path.exists(c):
        with open(c, encoding="utf-8") as fh:
            head = fh.readline()
        try:
            keys = sorted(json.loads(head).keys())
        except Exception as e:
            keys = ["UNPARSEABLE: %s" % e]
        found[c] = {"bytes": os.path.getsize(c), "first_row_keys": keys}
out["per_question_BM25_candidates"] = found
# what BM25 variant does the stored per-query file use? (fair=frozen_idfonly needed for H1)
out["H1_paired_data_exists"] = False
out["H1_note"] = ("decision_tests.py t1() builds per_q dict for 4 BM25 variants but "
                  "writes only means to DECISION_TESTS.json; code side reuses LADDER.json "
                  "aggregates. No stored paired per-question file for frozen_idfonly-vs-k384 "
                  "exists among candidates above (keys inspected).")

# (c1) binomial-SE approximation for H1 (UNPAIRED, labelled as such)
def binom_se(pct, n):
    p = pct / 100.0
    return 100 * math.sqrt(p * (1 - p) / n)
se_code = binom_se(57.87234042553192, 705)
se_bm25 = binom_se(65.67375886524822, 705)
se_diff_unpaired = math.sqrt(se_code ** 2 + se_bm25 ** 2)
out["H1_binomial_approx_unpaired"] = {
    "se_code_pp": round(se_code, 2), "se_bm25_pp": round(se_bm25, 2),
    "gap_pp": round(57.87234042553192 - 65.67375886524822, 2),
    "se_diff_pp": round(se_diff_unpaired, 2),
    "approx_95CI": [round(-7.80 - 1.96 * se_diff_unpaired, 2),
                    round(-7.80 + 1.96 * se_diff_unpaired, 2)],
    "warning": "UNPAIRED binomial; ignores pairing (conservative if positively correlated) "
               "and archive clustering (anti-conservative: RealTalk n=10 archives). NOT a substitute "
               "for the missing paired cluster bootstrap.",
}

# (c2) archive-level paired analysis for H2/H3 from LADDER_CACHE.jsonl (n=10 archives)
cache = [json.loads(l) for l in open(os.path.join(PKG, "coordinator/LADDER_CACHE.jsonl"), encoding="utf-8")]
assert len(cache) == 10, len(cache)
arch_n = {c["archive"]: c["n"] for c in cache}
out["LADDER_CACHE_archives"] = arch_n
out["LADDER_CACHE_total_q"] = sum(arch_n.values())


def arch_paired(key_a, key_b, metric):
    a = np.array([c["arms"][key_a][metric] for c in cache])
    b = np.array([c["arms"][key_b][metric] for c in cache])
    d = a - b
    # paired t over 10 archives + Wilcoxon + sign count
    t, p = st.ttest_rel(a, b)
    try:
        _, pw = st.wilcoxon(d)
    except Exception:
        pw = float("nan")
    return {"mean_diff_pp": round(float(d.mean()), 2),
            "sd_diff_pp": round(float(d.std(ddof=1)), 2),
            "se_diff_pp": round(float(d.std(ddof=1) / math.sqrt(len(d))), 2),
            "paired_t": round(float(t), 3), "paired_t_p": float(p),
            "wilcoxon_p": float(pw),
            "n_archives_favoring_a": int((d > 0).sum()),
            "per_archive_diff": [round(float(x), 2) for x in d]}


out["H2_sym_minus_float_k384_hit10_archpaired"] = arch_paired("k384/sym", "k384/float", "hit10")
out["H2_overall_means"] = {"sym": lad["arms"]["k384/sym"]["hit10"],
                           "float": lad["arms"]["k384/float"]["hit10"]}
out["H3_ladder_qscale_steps_archpaired_hit10"] = {
    "k192_minus_k96": arch_paired("k192/qscale", "k96/qscale", "hit10"),
    "k384_minus_k192": arch_paired("k384/qscale", "k192/qscale", "hit10"),
}
out["H3_overall_means"] = {k: lad["arms"][k]["hit10"] for k in ("k96/qscale", "k192/qscale", "k384/qscale")}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1))
