#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
roles_fix2.py -- SELF-CORRECTION of a bug in roles_fix.py F4.

BUG: F4 masked pairs by PERMUTED session labels but then indexed the Hamming matrix with the
ORIGINAL row indices H[a, a+1]. So the "shuffled" control still measured TRUE adjacent pairs
(just a subsample) -> 33.71 bits, which wrongly looked like the control half-survived.
FIX: index the permuted rows, H[perm[a], perm[a+1]].

Adds three genuine mapping-falsification controls + the decisive cross-benchmark corollary table.
"""
import json, pickle, glob, os
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
EV = BASE + "/agent_out/role-separation/evidence"
rng = np.random.default_rng(31337)
RES = json.load(open(EV + "/results.json"))


def jd(o):
    def conv(x):
        if isinstance(x, np.floating): return float(x)
        if isinstance(x, np.integer): return int(x)
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, np.bool_): return bool(x)
        raise TypeError(str(type(x)))
    return json.dumps(o, indent=2, default=conv)


def bits(C): return np.where(C >= 0, 1, -1).astype(np.int16)


def lme_archives():
    for cp in sorted(glob.glob(BASE + "/regen/lme/cache_repr/*.pkl")):
        qid = os.path.basename(cp)[:-4]
        d = json.load(open(BASE + "/regen/lme/items/" + qid + ".json"))
        roles, sess = [], []
        for si, s in enumerate(d["haystack_sessions"]):
            if not isinstance(s, list): continue
            for t in s:
                if isinstance(t, dict):
                    roles.append(t.get("role")); sess.append(si)
        P = pickle.load(open(cp, "rb"))
        yield dict(name=qid, C=P["C"], sess=np.array(sess), roles=np.array(roles, object))


G = {}
true_h = np.zeros(97, np.int64)      # true adjacent
perm_h = np.zeros(97, np.int64)      # row-permuted "adjacent" (mapping destroyed)
samesess_nonadj = np.zeros(97, np.int64)  # same session, NOT adjacent
crosssess = np.zeros(97, np.int64)   # different session
lag2_h = np.zeros(97, np.int64)      # same session, lag 2 (same speaker!)
lag3_h = np.zeros(97, np.int64)

for A in lme_archives():
    C = A["C"]; N = C.shape[0]; B = bits(C); sess = A["sess"]
    H = ((96 - (B @ B.T)) // 2)
    a = np.arange(N - 1)
    m = sess[a] == sess[a + 1]
    true_h += np.bincount(H[a[m], a[m] + 1], minlength=97)
    # CORRECT permutation control: destroy the row<->turn mapping
    p = rng.permutation(N)
    mp = sess[a] == sess[a + 1]          # same adjacency pattern, but rows are permuted
    perm_h += np.bincount(H[p[a[mp]], p[a[mp] + 1]], minlength=97)
    # lag-2 (same speaker) and lag-3
    if N > 2:
        a2 = np.arange(N - 2); m2 = sess[a2] == sess[a2 + 2]
        lag2_h += np.bincount(H[a2[m2], a2[m2] + 2], minlength=97)
    if N > 3:
        a3 = np.arange(N - 3); m3 = sess[a3] == sess[a3 + 3]
        lag3_h += np.bincount(H[a3[m3], a3[m3] + 3], minlength=97)
    # same-session non-adjacent vs cross-session
    iu = np.triu_indices(N, 1)
    same = sess[iu[0]] == sess[iu[1]]
    adjmask = same & (np.abs(iu[1] - iu[0]) == 1)
    samesess_nonadj += np.bincount(H[iu][same & ~adjmask], minlength=97)
    crosssess += np.bincount(H[iu][~same], minlength=97)


def mean_of(h): return float((h * np.arange(97)).sum() / max(h.sum(), 1))


def auc_pos_lt_neg(hp, hn):
    hp = np.asarray(hp, float) / max(np.asarray(hp, float).sum(), 1)
    hn = np.asarray(hn, float) / max(np.asarray(hn, float).sum(), 1)
    surv = np.concatenate([np.cumsum(hn[::-1])[::-1][1:], [0.0]])
    return float((hp * (surv + 0.5 * hn)).sum())


G["G1_mapping_falsification_LME"] = {
    "CORRECTION": ("roles_fix.py F4 was buggy: it masked with permuted session labels but indexed "
                   "ORIGINAL rows, so its 'shuffled' value 33.71 was NOT a real control. "
                   "Superseded by the numbers below."),
    "true_adjacent_mean_bits": mean_of(true_h),
    "row_permuted_adjacent_mean_bits": mean_of(perm_h),
    "same_session_NONadjacent_mean_bits": mean_of(samesess_nonadj),
    "cross_session_mean_bits": mean_of(crosssess),
    "lag2_same_speaker_mean_bits": mean_of(lag2_h),
    "lag3_mean_bits": mean_of(lag3_h),
    "n_true_adj": int(true_h.sum()), "n_perm": int(perm_h.sum()),
    "n_same_sess_nonadj": int(samesess_nonadj.sum()), "n_cross_sess": int(crosssess.sum()),
    "AUC_true_adj_vs_cross_session": auc_pos_lt_neg(true_h, crosssess),
    "AUC_permuted_vs_cross_session": auc_pos_lt_neg(perm_h, crosssess),
    "verdict": ("Mapping is CORRECT iff true adjacency is much closer than the row-permuted "
                "control, which must sit at the cross-session baseline (~48)."),
    "tail_le16": {
        "true_adjacent_pct": 100.0 * true_h[:17].sum() / max(true_h.sum(), 1),
        "row_permuted_pct": 100.0 * perm_h[:17].sum() / max(perm_h.sum(), 1),
        "same_session_nonadj_pct": 100.0 * samesess_nonadj[:17].sum() / max(samesess_nonadj.sum(), 1),
        "cross_session_pct": 100.0 * crosssess[:17].sum() / max(crosssess.sum(), 1),
    },
    "histograms": {"true_adjacent": true_h.tolist(), "row_permuted": perm_h.tolist(),
                   "same_session_nonadjacent": samesess_nonadj.tolist(),
                   "cross_session": crosssess.tolist(), "lag2": lag2_h.tolist()},
}
print(jd({k: v for k, v in G["G1_mapping_falsification_LME"].items() if k != "histograms"}))

# ---- decisive corollary table ----
E = RES["E_mechanism"]
G["G2_decisive_corollary"] = {
    "statement": ("The near-duplicate hypothesis predicts: the benchmark where SIGN LOSES must have "
                  "MORE near-duplicate structure around gold. Observed is the exact OPPOSITE."),
    "table": [
        {"bench": "LongMemEval", "sign_minus_float_pp": RES["B_control"]["LME_delta_pp"],
         "median_gold_nn_bits": E["LME"]["dnn_median"],
         "pct_gold_nn_le16": 100.0 * E["LME"]["n_dnn_le16"] / E["LME"]["n"],
         "pct_adjacent_pairs_le16_bits": RES["C_distributions"]["LME"]["tail_le16_frac_of_all_pairs_pct"]},
        {"bench": "LoCoMo", "sign_minus_float_pp": E["LOCOMO"]["control_delta_pp"],
         "median_gold_nn_bits": E["LOCOMO"]["dnn_median"],
         "pct_gold_nn_le16": 100.0 * E["LOCOMO"]["n_dnn_le16"] / E["LOCOMO"]["n"],
         "pct_adjacent_pairs_le16_bits": RES["C_distributions"]["LOCOMO"]["tail_le16_frac_of_all_pairs_pct"]},
        {"bench": "REALTALK", "sign_minus_float_pp": E["REALTALK"]["control_delta_pp"],
         "median_gold_nn_bits": E["REALTALK"]["dnn_median"],
         "pct_gold_nn_le16": 100.0 * E["REALTALK"]["n_dnn_le16"] / E["REALTALK"]["n"]},
        {"bench": "PerLTQA (SIGN LOSES)", "sign_minus_float_pp": E["PERLTQA"]["control_delta_pp"],
         "median_gold_nn_bits": E["PERLTQA"]["dnn_median"],
         "pct_gold_nn_le16": 100.0 * E["PERLTQA"]["n_dnn_le16"] / E["PERLTQA"]["n"]},
    ],
    "conclusion": ("LongMemEval has BY FAR the most near-duplicate gold neighbours (median 18 bits, "
                   "38.5% of golds have a non-gold neighbour within 16 bits) and SIGN WINS there by "
                   "+10.05 pp. PerLTQA has the FEWEST (median 27 bits, 3.2%) and SIGN LOSES by "
                   "-6.27 pp. The correlation across benchmarks runs OPPOSITE to the hypothesis."),
}
print(jd(G["G2_decisive_corollary"]))

RES["G_corrections_and_decisive"] = G
open(EV + "/results.json", "w").write(jd(RES))
print("\n[SAVED]")
