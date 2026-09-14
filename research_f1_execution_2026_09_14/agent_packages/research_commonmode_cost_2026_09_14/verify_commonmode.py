# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Verify the common-mode projector classification from committed bytes.

Reads (no sealed material, no network, stdlib only):
  --projector : PROJECTOR_BYTES.json bytes (branch-only blob; passed as a path
                to a copy staged OUTSIDE the repo, e.g. via
                `git show origin/findings/representation-geometry-2026-09-13:...`)
  --geometry  : docs/v52/task4c2/V52_T4C2_feature_geometry.csv (N_archive column)
  --t4c2      : v52_t4c2_centering_geometry.py (sealed compute script bytes)
  --adapter   : adapters/longmemeval_v52_adapter.py
  --e1core    : e1_geometry_core.py (E1 branch blob copy, staged outside repo)
Writes evidence/results.json into --outdir (the task namespace).

Every number it prints is recomputed here; every source fact is asserted by
substring match against file bytes read in this process (VERIFIED), with the
locator recorded alongside.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys

LABELS = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"

# Arm-specific index shared state (serialized S0, faiss 1.15.0), from
# origin/evidence/twelve-byte-cost-2026-09-11:evidence/twelve_byte_cost_2026_09_11/EVIDENCE.json
S0 = {
    "SIGN96_BinaryFlat": 33,
    "TOP32_RABITQ32": 202,
    "RABITQ96": 458,
    "PQ96_m12x8": 98390,
    "OPQ_PQ96_m12x8": 135325,
}
# Analytic arm-specific rotating state where no serialized S0 was published.
ANALYTIC = {"ITQ96_rotation_f32": 96 * 96 * 4, "SIMHASH_Haar_f32": 96 * 96 * 4}
FLOAT_PAYLOAD = 384  # 96 x float32
SIGN_MARGINAL = 12


def check(name, cond, detail, failures):
    print(("PASS " if cond else "FAIL ") + name + " :: " + detail)
    if not cond:
        failures.append(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projector", required=True)
    ap.add_argument("--geometry", required=True)
    ap.add_argument("--t4c2", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--e1core", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    failures = []
    res = {"_labels": LABELS, "provenance": {}, "source_assertions": {},
           "projector_recompute": {}, "comparison": {}}

    proj = json.load(open(a.projector, encoding="utf-8"))
    t4c2 = open(a.t4c2, encoding="utf-8").read()
    adap = open(a.adapter, encoding="utf-8").read()
    e1 = open(a.e1core, encoding="utf-8").read()
    res["provenance"] = {
        "projector": a.projector + " (bytes of origin/findings/representation-geometry-2026-09-13:"
                     "research_representation_geometry_2026_09_13/measurements/projector/PROJECTOR_BYTES.json)",
        "geometry": a.geometry + " (local docs/v52/task4c2/V52_T4C2_feature_geometry.csv)",
        "t4c2_script": a.t4c2,
        "adapter": a.adapter + " (local adapters/longmemeval_v52_adapter.py)",
        "e1core": a.e1core + " (bytes of origin/research/e1-sign-float-mechanism-frozen-2026-09-13:"
                 "campaign_2026_09_13/e1_mechanism/e1_geometry_core.py)",
    }

    # ---- A. source facts: float96 and SIGN96 are two views of one fit ----
    a1 = ("C_float=np.subtract(Y,mu)" in t4c2
          and "C_sign=Y.copy(); C_sign-=mu" in t4c2
          and "signD=C_sign>=0" in t4c2
          and "fc_scores=cosine_centered(C_float,qC_float)" in t4c2
          and "wv,cv,base_svd,Xw,Xc,Xl=adapter.fit_archive_representation(texts)" in t4c2
          and "svd96=TruncatedSVD(n_components=96,random_state=SVD_RANDOM_STATE)" in t4c2
          and "Y=normalize(svd96.fit_transform(Z))" in t4c2
          and "mu=Y.mean(axis=0,keepdims=True)" in t4c2)
    check("A1_same_Y_mu_for_sign_and_float", a1,
          "T4C2 evaluate_item builds C_float and C_sign from one Y, one mu (loc: :265-267,285,287)", failures)
    a2 = "if same_max>1e-12: raise RuntimeError(f'[BUG" in t4c2
    check("A2_same_input_gate", a2, "T4C2 aborts unless maxdiff<=1e-12 (loc: :282)", failures)
    a3 = ("QY=normalize(svd96.transform(Zq))" in t4c2
          and "qC_float=np.subtract(QY,mu)" in t4c2)
    check("A3_query_uses_fitted_state", a3,
          "query transformed through fitted wv/cv/base_svd/svd96, centered by archive mu (loc: :275-277)", failures)
    import re
    m = re.search(r"def fit_archive_representation\(([^)]*)\)", adap)
    a4 = m is not None and m.group(1).split(":")[0].strip() == "memory_texts"
    check("A4_fit_api_archive_texts_only", a4,
          "adapter fit signature params={'memory_texts'} (loc: adapters/longmemeval_v52_adapter.py:147)", failures)
    a5 = ('"cross_question_fit_prohibited"' in adap
          and "fit_archive_representation is invoked independently per question archive" in adap)
    check("A5_per_archive_fit_rule", a5,
          "leakage audit: cross-question fit prohibited (loc: adapter :363-367)", failures)
    a6 = ("consumes already-frozen C/qC arrays" in e1 and "sign=np.where(C>=0.0" in e1)
    check("A6_e1_one_pair_two_views", a6,
          "E1 core consumes one frozen C/qC pair; sign derived as where(C>=0) (loc: e1_geometry_core.py:1,12)", failures)
    res["source_assertions"] = {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5, "A6": a6}

    # ---- B. projector arithmetic from committed bytes ----
    pa = proj["per_archive"]
    eff = [r["ratios"]["a_raw"]["effective"] for r in pa]
    tot = [r["ratios"]["a_raw"]["shared_total"] for r in pa]
    narr = [r["N_archive"] for r in pa]
    med_eff = statistics.median(eff)
    med_tot = statistics.median(tot)
    check("B1_median_effective_88886", abs(med_eff - 88886.36234817814) < 1e-6,
          "median=%.5f range=[%.2f,%.2f] N 15-arch=[%d,%d]" % (med_eff, min(eff), max(eff), min(narr), max(narr)),
          failures)
    check("B2_median_total_44220235", med_tot == 44220235.0, "median shared total=%.1f" % med_tot, failures)
    med_row = [r for r in pa if r["question_id"] == "078150f1"][0]
    comp = med_row["components"]
    p_s96 = comp["s96_components"]["raw32"]
    p_sv = comp["sv_components"]["raw32"]
    p_vocab = comp["word_vocab"]["structured_bytes"] + comp["char_vocab"]["structured_bytes"]
    p_idf = comp["word_idf"]["raw32"] + comp["char_idf"]["raw32"]
    p_mu = comp["mu"]["raw32"]
    p_sum = p_s96 + p_sv + p_vocab + p_idf + p_mu
    check("B3_components_sum_to_total", p_sum == med_row["totals"]["a_raw_f32_struct"],
          "078150f1: s96=%d sv=%d vocab=%d idf=%d mu=%d sum=%d total=%d"
          % (p_s96, p_sv, p_vocab, p_idf, p_mu, p_sum, med_row["totals"]["a_raw_f32_struct"]), failures)
    shares = {k: round(100 * v / p_sum, 2) for k, v in
              [("s96", p_s96), ("sv", p_sv), ("vocab", p_vocab), ("idf", p_idf), ("mu", p_mu)]}
    res["projector_recompute"] = {
        "median_effective_a_raw": med_eff, "median_shared_total": med_tot,
        "min_effective": min(eff), "max_effective": max(eff),
        "median_archive_components_a_raw": {
            "question_id": "078150f1", "N": med_row["N_archive"], "total": p_sum,
            "s96": p_s96, "sv": p_sv, "vocab_struct": p_vocab, "idf_f32": p_idf, "mu_f32": p_mu,
            "shares_pct": shares},
        "shapes": {"sv": comp["sv_components"]["shape"], "s96": comp["s96_components"]["shape"],
                   "lexical_d": med_row["lexical_dim_d"]},
    }

    # ---- C. frozen 470-archive cardinalities ----
    with open(a.geometry, encoding="utf-8") as f:
        Ns = [int(r["N_archive"]) for r in csv.DictReader(f)]
    check("C1_cohort_470", len(Ns) == 470, "n=%d min=%d max=%d" % (len(Ns), min(Ns), max(Ns)), failures)
    meanN = sum(Ns) / len(Ns)
    totV = sum(Ns)
    res["comparison"]["frozen_N"] = {"n": len(Ns), "min": min(Ns), "max": max(Ns),
                                    "mean": meanN, "total_vectors": totV}

    def idx_only(s0, N):
        return 12 + s0 / N

    panel = {}
    for arm, s0 in [("SIGN96", 33), ("PQ96", 98390), ("OPQ_PQ96", 135325)]:
        costs = [idx_only(s0, n) for n in Ns]
        panel[arm] = {"mean_of_costs": sum(costs) / len(costs),
                      "min": min(costs), "max": max(costs)}
    panel["FLOAT96_CENTERED_payload"] = {"per_vector": 384}
    check("C2_opq_panel_28769",
          abs(panel["OPQ_PQ96"]["mean_of_costs"] - 287.6889713064122) < 1e-9,
          "OPQ index-only panel mean=%.10f" % panel["OPQ_PQ96"]["mean_of_costs"], failures)
    res["comparison"]["index_only_panel_mean_over_470"] = panel

    # ---- D. full-pipeline tables at realistic N and break-even ----
    P = med_tot  # median per-archive shared projector, f32+struct vocab
    N_real = 500

    def full(marginal, s0, N):
        return marginal + (P + s0) / N

    table_real = {arm: full(m, s, N_real) for arm, (m, s) in
                  {"SIGN96": (12, 33), "FLOAT96": (384, 0),
                   "PQ96": (12, 98390), "OPQ_PQ96": (12, 135325)}.items()}
    N_star_bare = math.ceil(P / (FLOAT_PAYLOAD - SIGN_MARGINAL))  # SIGN-full vs FLOAT-bare fantasy
    table_star = {arm: full(m, s, N_star_bare) for arm, (m, s) in
                  {"SIGN96": (12, 33), "FLOAT96": (384, 0),
                   "PQ96": (12, 98390), "OPQ_PQ96": (12, 135325)}.items()}
    ratio_claim = med_eff / FLOAT_PAYLOAD
    honest_gap = FLOAT_PAYLOAD - SIGN_MARGINAL  # SIGN-full undercuts FLOAT-full by this at every N
    # global-sharing estimate (prereg forbids; shown as cost of the choice):
    # ONE projector of median size serves all totV vectors. This is optimistic
    # for the rescue case (a true global vocab would be LARGER than P_med),
    # so the resulting effective is a LOWER bound.
    share_eff = {k: 12 + P / totV for k in ["SIGN96"]}
    res["comparison"]["full_pipeline_at_N500_Pmedian"] = table_real
    res["comparison"]["full_pipeline_at_Nstar_bare"] = table_star
    res["comparison"]["N_star_bare_float_parity"] = N_star_bare
    res["comparison"]["claimed_234x_recomputed_as_median_eff_over_384"] = ratio_claim
    res["comparison"]["honest_SIGN_vs_FLOAT_gap_B_per_vector_all_N"] = honest_gap
    res["comparison"]["global_sharing_estimate_SIGN_effective"] = share_eff["SIGN96"]
    res["comparison"]["global_sharing_vectors"] = totV
    check("D1_Nstar_bare", N_star_bare == math.ceil(44220235 / 372),
          "N*=ceil(44220235/372)=%d" % N_star_bare, failures)
    check("D2_sign_always_cheaper_than_float_full",
          all(full(12, 33, n) < full(384, 0, n) for n in [1, 396, 500, 616, N_star_bare, 3685020]),
          "SIGN-full < FLOAT-full at N in {1,396,500,616,N*,3685020} by exactly 372-33/N", failures)
    check("D3_sign_always_cheaper_than_pq_full",
          all(full(12, 33, n) < full(12, 98390, n) for n in [1, 500, N_star_bare]),
          "SIGN-full < PQ-full at every N (same P, smaller S0)", failures)

    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("WROTE " + os.path.join(a.outdir, "results.json"))
    if failures:
        print("FAILURES: " + ",".join(failures))
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
