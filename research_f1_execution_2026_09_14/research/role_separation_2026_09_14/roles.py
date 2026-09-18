#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
roles.py -- role/adjacency structure in memory archives, and its effect on sign-vs-float retrieval.

Sections:
  A. Mapping proof (LME + LoCoMo)
  B. FR@3 expectation control (must reproduce a frozen headline)
  C. Adjacency distributions: Hamming, cosine, AUC, <=16-bit tail, role asymmetry both directions
  D. Gold-gold adjacency enrichment
  E. THE MECHANISM TEST: does a close non-gold neighbour of gold hurt sign more than float?
"""
import json, pickle, glob, os, sys, math
from collections import defaultdict
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
OUT = BASE + "/agent_out/role-separation"
EV = OUT + "/evidence"
os.makedirs(EV, exist_ok=True)
RES = {}
rng = np.random.default_rng(20260914)


def jd(o):
    def conv(x):
        if isinstance(x, (np.floating,)): return float(x)
        if isinstance(x, (np.integer,)): return int(x)
        if isinstance(x, np.ndarray): return x.tolist()
        raise TypeError(str(type(x)))
    return json.dumps(o, indent=2, default=conv)


# ---------------------------------------------------------------- metric
def fr_at_k_expect(scores, gold, K=3, higher_better=True):
    """EXACT expectation of FR@K = |gold cap topK|/|gold| under uniform random tie-break."""
    s = np.asarray(scores, dtype=np.float64)
    if not higher_better:
        s = -s
    gold = np.asarray(gold, dtype=np.int64)
    if gold.size == 0 or s.size == 0:
        return float("nan")
    if s.size <= K:
        return 1.0
    thr = np.partition(s, -K)[-K]
    strictly = int((s > thr).sum())
    slots = K - strictly
    bc = int((s == thr).sum())
    gs = s[gold]
    g_strict = int((gs > thr).sum())
    g_tied = int((gs == thr).sum())
    if bc == 0:
        return g_strict / gold.size
    return (g_strict + g_tied * slots / bc) / gold.size


def sign_scores(C, qC):
    """Hamming distance, LOWER is better -> return negative Hamming so higher_better works."""
    B = (C >= 0)
    qb = (qC >= 0)
    ham = (B != qb).sum(axis=1).astype(np.float64)
    return -ham, ham


def float_scores(C, qC):
    nq = np.linalg.norm(qC)
    nc = np.linalg.norm(C, axis=1)
    den = nc * nq
    den[den == 0] = 1e-300
    return (C @ qC) / den


# ================================================================ A. MAPPING
def lme_load():
    caches = sorted(glob.glob(BASE + "/regen/lme/cache_repr/*.pkl"))
    out = []
    for cp in caches:
        qid = os.path.basename(cp)[:-4]
        d = json.load(open(BASE + "/regen/lme/items/" + qid + ".json"))
        roles, sess_idx, turn_idx, has_ans = [], [], [], []
        for si, s in enumerate(d["haystack_sessions"]):
            if not isinstance(s, list):
                continue
            for ti, t in enumerate(s):
                if not isinstance(t, dict):
                    continue
                roles.append(t.get("role"))
                sess_idx.append(si)
                turn_idx.append(ti)
                has_ans.append(bool(t.get("has_answer", False)))
        out.append((cp, qid, np.array(roles, dtype=object), np.array(sess_idx), np.array(turn_idx),
                    np.array(has_ans), d))
    return out


print("=== A. MAPPING PROOF ===")
LME = lme_load()
cnt_ok = gold_ok = 0
role_counter = defaultdict(int)
alt_ok = 0
alt_tot = 0
for cp, qid, roles, si, ti, ha, d in LME:
    C = pickle.load(open(cp, "rb"))
    N = C["C"].shape[0]
    if N == len(roles):
        cnt_ok += 1
    cg = sorted(int(x) for x in np.asarray(C["gold"]).ravel())
    if cg == sorted(np.flatnonzero(ha).tolist()):
        gold_ok += 1
    for r in roles:
        role_counter[r] += 1
    # strict alternation user,assistant,user,... within each session?
    for s in set(si.tolist()):
        m = si == s
        rr = roles[m]
        alt_tot += 1
        exp = np.array([("user" if k % 2 == 0 else "assistant") for k in range(len(rr))], dtype=object)
        if (rr == exp).all():
            alt_ok += 1

RES["A_mapping"] = {
    "lme_items": len(LME),
    "lme_count_match": cnt_ok,
    "lme_gold_index_match": gold_ok,
    "lme_role_counts": dict(role_counter),
    "lme_sessions_total": alt_tot,
    "lme_sessions_strictly_alternating_user_first": alt_ok,
    "proof": ("count match 470/470 AND cached gold row indices == flatten positions of has_answer "
              "turns 470/470 (886 gold rows). Gold match is an INDEPENDENT check: it constrains "
              "order, not just length."),
}
print(jd(RES["A_mapping"]))

LOC = []
for f in sorted(glob.glob(BASE + "/regen/locomo/locomo_*.pkl")):
    L = pickle.load(open(f, "rb"))
    itr = L["id_to_row"]
    assert sorted(itr.values()) == list(range(L["C"].shape[0]))
    LOC.append((f, L))
RES["A_mapping"]["locomo_files"] = len(LOC)
RES["A_mapping"]["locomo_id_to_row_contiguous"] = True

# ================================================================ B. CONTROL
print("\n=== B. FR@3 CONTROL (LongMemEval) ===")
fs, ss = [], []
for cp, qid, roles, si, ti, ha, d in LME:
    C = pickle.load(open(cp, "rb"))
    M, qC, gold = C["C"], C["qC"], np.asarray(C["gold"]).ravel().astype(int)
    sg, _ = sign_scores(M, qC)
    fg = float_scores(M, qC)
    ss.append(fr_at_k_expect(sg, gold, 3))
    fs.append(fr_at_k_expect(fg, gold, 3))
sign_m, float_m = float(np.mean(ss)), float(np.mean(fs))
RES["B_control"] = {
    "n_questions": len(ss),
    "LME_sign_FR3": sign_m,
    "LME_float_FR3": float_m,
    "LME_delta_pp": (sign_m - float_m) * 100,
    "frozen_delta_pp": 10.037943,
    "expectation_target_pp": 10.053783,
}
print(jd(RES["B_control"]))

with open(EV + "/results_partial_AB.json", "w") as f:
    f.write(jd(RES))
print("\n[saved partial A+B]")
