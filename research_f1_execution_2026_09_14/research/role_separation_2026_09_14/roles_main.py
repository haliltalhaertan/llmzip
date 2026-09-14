#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
roles_main.py -- sections C, D, E. Appends to evidence/results.json.
C. Adjacency distributions (Hamming/cosine/AUC/<=16 tail/role asymmetry both directions)
D. Gold-gold adjacency enrichment
E. MECHANISM: does a close non-gold neighbour of gold hurt sign more than float?
"""
import json, pickle, glob, os, math
from collections import defaultdict
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
OUT = BASE + "/agent_out/role-separation"
EV = OUT + "/evidence"
os.makedirs(EV, exist_ok=True)
rng = np.random.default_rng(20260914)
RES = json.load(open(EV + "/results_partial_AB.json"))


def jd(o):
    def conv(x):
        if isinstance(x, np.floating): return float(x)
        if isinstance(x, np.integer): return int(x)
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, (np.bool_,)): return bool(x)
        raise TypeError(str(type(x)))
    return json.dumps(o, indent=2, default=conv)


def fr3(scores, gold, K=3):
    s = np.asarray(scores, np.float64); gold = np.asarray(gold, np.int64)
    if gold.size == 0 or s.size == 0: return float("nan")
    if s.size <= K: return 1.0
    thr = np.partition(s, -K)[-K]
    strictly = int((s > thr).sum()); slots = K - strictly; bc = int((s == thr).sum())
    gs = s[gold]; g_strict = int((gs > thr).sum()); g_tied = int((gs == thr).sum())
    if bc == 0: return g_strict / gold.size
    return (g_strict + g_tied * slots / bc) / gold.size


def bits(C): return np.where(C >= 0, 1, -1).astype(np.int16)
def ham_mat(Bpm): return ((96 - (Bpm @ Bpm.T)) // 2).astype(np.int16)
def cos_mat(C):
    n = np.linalg.norm(C, axis=1, keepdims=True); n[n == 0] = 1e-300
    U = C / n; return U @ U.T
def ham_q(Bpm, qC): return ((96 - (Bpm @ np.where(qC >= 0, 1, -1).astype(np.int16))) // 2).astype(np.float64)
def cos_q(C, qC):
    nq = np.linalg.norm(qC); nc = np.linalg.norm(C, axis=1); d = nc * nq; d[d == 0] = 1e-300
    return (C @ qC) / d


# ---------------- build per-archive adjacency structures ----------------
def lme_archives():
    for cp in sorted(glob.glob(BASE + "/regen/lme/cache_repr/*.pkl")):
        qid = os.path.basename(cp)[:-4]
        d = json.load(open(BASE + "/regen/lme/items/" + qid + ".json"))
        roles, sess = [], []
        for si, s in enumerate(d["haystack_sessions"]):
            if not isinstance(s, list): continue
            for t in s:
                if not isinstance(t, dict): continue
                roles.append(t.get("role")); sess.append(si)
        P = pickle.load(open(cp, "rb"))
        yield dict(name=qid, C=P["C"], qC=P["qC"], gold=np.asarray(P["gold"]).ravel().astype(int),
                   roles=np.array(roles, object), sess=np.array(sess), bench="LME")


def locomo_archives():
    for f in sorted(glob.glob(BASE + "/regen/locomo/locomo_*.pkl")):
        L = pickle.load(open(f, "rb"))
        itr = L["id_to_row"]; N = L["C"].shape[0]
        sess = np.zeros(N, int); turn = np.zeros(N, int)
        for k, r in itr.items():
            a, b = k.split(":"); sess[r] = int(a[1:]); turn[r] = int(b)
        yield dict(name=L["conv_id"], C=L["C"], QC=L["QC"], qas=L["qas"], itr=itr,
                   sess=sess, turn=turn, bench="LOCOMO")


print("=== C. ADJACENCY DISTRIBUTIONS ===")
C_RES = {}

# ---- LME ----
adj_h, adj_c, rnd_h, rnd_c = [], [], [], []
dir_ua, dir_au = [], []          # user_i -> assistant_{i+1} ; assistant_i -> user_{i+1}
hist = np.zeros(97, np.int64)    # all within-archive pairs
adj_hist = np.zeros(97, np.int64)
tot_pairs = 0; tot_adj = 0
tail16_all = 0; tail16_adj = 0
for A in lme_archives():
    C = A["C"]; N = C.shape[0]; Bpm = bits(C)
    H = ham_mat(Bpm); S = cos_mat(C)
    iu = np.triu_indices(N, 1)
    hv = H[iu]
    hist += np.bincount(hv, minlength=97)
    tot_pairs += hv.size
    # adjacency: consecutive rows in same session
    a = np.arange(N - 1)
    m = A["sess"][a] == A["sess"][a + 1]
    ai, aj = a[m], a[m] + 1
    ah = H[ai, aj]; ac = S[ai, aj]
    adj_hist += np.bincount(ah, minlength=97)
    tot_adj += ah.size
    tail16_all += int((hv <= 16).sum()); tail16_adj += int((ah <= 16).sum())
    ri = A["roles"][ai]; rj = A["roles"][aj]
    dir_ua.append(ah[(ri == "user") & (rj == "assistant")])
    dir_au.append(ah[(ri == "assistant") & (rj == "user")])
    # subsample for distribution storage
    if ah.size: 
        k = min(400, ah.size); s = rng.choice(ah.size, k, replace=False)
        adj_h.append(ah[s]); adj_c.append(ac[s])
    if N > 3:
        k = min(400, hv.size); s = rng.choice(hv.size, k, replace=False)
        rnd_h.append(hv[s]); rnd_c.append(S[iu[0][s], iu[1][s]])

adj_h = np.concatenate(adj_h); adj_c = np.concatenate(adj_c)
rnd_h = np.concatenate(rnd_h); rnd_c = np.concatenate(rnd_c)
dir_ua = np.concatenate(dir_ua); dir_au = np.concatenate(dir_au)


def auc_lower_better(pos, neg):
    """P(pos < neg) + 0.5 P(=) ; pos=adjacent (should be SMALLER hamming)."""
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort().astype(np.float64)
    # average ranks for ties
    import scipy.stats as st  # noqa
    return None


def auc_fast(pos, neg):
    # AUC that adjacency-Hamming separates: P(ham_adj < ham_rnd) + .5*P(eq)
    hp = np.bincount(pos.astype(int), minlength=97).astype(np.float64)
    hn = np.bincount(neg.astype(int), minlength=97).astype(np.float64)
    hp /= hp.sum(); hn /= hn.sum()
    cn = np.concatenate([[0.0], np.cumsum(hn)])  # P(neg < k)
    return float((hp * (cn[:-1] + 0.5 * hn)).sum())


def pct(x, qs=(0, 1, 5, 25, 50, 75, 95, 99, 100)):
    return {f"p{q}": float(np.percentile(x, q)) for q in qs}


C_RES["LME"] = {
    "n_adjacent_pairs": int(tot_adj), "n_all_within_archive_pairs": int(tot_pairs),
    "adj_hamming_mean": float(adj_h.mean()), "adj_hamming_sd": float(adj_h.std()),
    "rnd_hamming_mean": float(rnd_h.mean()), "rnd_hamming_sd": float(rnd_h.std()),
    "adj_hamming_pct": pct(adj_h), "rnd_hamming_pct": pct(rnd_h),
    "adj_cosine_mean": float(adj_c.mean()), "rnd_cosine_mean": float(rnd_c.mean()),
    "adj_cosine_pct": pct(adj_c), "rnd_cosine_pct": pct(rnd_c),
    "AUC_adj_vs_rnd": auc_fast(adj_h, rnd_h),
    "tail_le16_count": int(tail16_all),
    "tail_le16_frac_of_all_pairs_pct": 100.0 * tail16_all / tot_pairs,
    "tail_le16_adjacent_count": int(tail16_adj),
    "tail_le16_frac_that_is_adjacent_pct": 100.0 * tail16_adj / max(tail16_all, 1),
    "tail_le16_frac_NOT_adjacent_pct": 100.0 * (1 - tail16_adj / max(tail16_all, 1)),
    "role_user_to_assistant_mean_ham": float(dir_ua.mean()), "n_ua": int(dir_ua.size),
    "role_assistant_to_user_mean_ham": float(dir_au.mean()), "n_au": int(dir_au.size),
    "role_asymmetry_bits_(au_minus_ua)": float(dir_au.mean() - dir_ua.mean()),
    "full_hamming_histogram_all_pairs": hist.tolist(),
    "adjacent_hamming_histogram": adj_hist.tolist(),
}
print(jd({k: v for k, v in C_RES["LME"].items() if "histogram" not in k}))

# ---- LoCoMo ----
adj_h2, adj_c2, rnd_h2, rnd_c2 = [], [], [], []
hist2 = np.zeros(97, np.int64); tot2 = 0; adj2 = 0; t16a = 0; t16j = 0
for A in locomo_archives():
    C = A["C"]; N = C.shape[0]; Bpm = bits(C); H = ham_mat(Bpm); S = cos_mat(C)
    iu = np.triu_indices(N, 1); hv = H[iu]
    hist2 += np.bincount(hv, minlength=97); tot2 += hv.size
    order = np.lexsort((A["turn"], A["sess"]))
    a = order[:-1]; b = order[1:]
    m = (A["sess"][a] == A["sess"][b]) & (A["turn"][b] - A["turn"][a] == 1)
    ai, aj = a[m], b[m]
    ah = H[ai, aj]; ac = S[ai, aj]; adj2 += ah.size
    t16a += int((hv <= 16).sum()); t16j += int((ah <= 16).sum())
    adj_h2.append(ah); adj_c2.append(ac)
    k = min(4000, hv.size); s = rng.choice(hv.size, k, replace=False)
    rnd_h2.append(hv[s]); rnd_c2.append(S[iu[0][s], iu[1][s]])
adj_h2 = np.concatenate(adj_h2); adj_c2 = np.concatenate(adj_c2)
rnd_h2 = np.concatenate(rnd_h2); rnd_c2 = np.concatenate(rnd_c2)
C_RES["LOCOMO"] = {
    "n_adjacent_pairs": int(adj2), "n_all_within_archive_pairs": int(tot2),
    "adj_hamming_mean": float(adj_h2.mean()), "rnd_hamming_mean": float(rnd_h2.mean()),
    "adj_hamming_pct": pct(adj_h2), "rnd_hamming_pct": pct(rnd_h2),
    "adj_cosine_mean": float(adj_c2.mean()), "rnd_cosine_mean": float(rnd_c2.mean()),
    "AUC_adj_vs_rnd": auc_fast(adj_h2, rnd_h2),
    "tail_le16_count": int(t16a), "tail_le16_frac_of_all_pairs_pct": 100.0 * t16a / tot2,
    "tail_le16_adjacent_count": int(t16j),
    "tail_le16_frac_that_is_adjacent_pct": 100.0 * t16j / max(t16a, 1),
    "full_hamming_histogram_all_pairs": hist2.tolist(),
}
print(jd({k: v for k, v in C_RES["LOCOMO"].items() if "histogram" not in k}))
RES["C_distributions"] = C_RES
open(EV + "/results_partial_ABC.json", "w").write(jd(RES))
print("[saved C]")

# ================================================================ D. GOLD-GOLD ADJACENCY
print("\n=== D. GOLD-GOLD ADJACENCY ENRICHMENT ===")
gg_obs = 0; gg_pairs_total = 0; adj_total = 0; pairs_total = 0
gold_rows_total = 0; rows_total = 0
per_item = []
for A in lme_archives():
    N = A["C"].shape[0]; g = set(A["gold"].tolist())
    a = np.arange(N - 1); m = A["sess"][a] == A["sess"][a + 1]
    ai, aj = a[m], a[m] + 1
    na = ai.size
    hits = sum(1 for x, y in zip(ai, aj) if x in g and y in g)
    gg_obs += hits; adj_total += na
    ng = len(g); gold_rows_total += ng; rows_total += N
    pairs_total += N * (N - 1) // 2
    gg_pairs_total += ng * (ng - 1) // 2
    per_item.append((A["name"], N, ng, na, hits))
p_gold = gold_rows_total / rows_total
exp_rate = p_gold * p_gold
obs_rate = gg_obs / adj_total
# exact-ish null: fraction of ALL within-archive pairs that are gold-gold
null_gg_rate = gg_pairs_total / pairs_total
RES["D_gold_adjacency"] = {
    "adjacent_pairs": int(adj_total), "gold_gold_adjacent_pairs": int(gg_obs),
    "gold_gold_adjacent_rate": obs_rate,
    "all_within_archive_pairs": int(pairs_total), "gold_gold_all_pairs": int(gg_pairs_total),
    "null_gold_gold_rate_all_pairs": null_gg_rate,
    "enrichment_vs_all_pairs_x": obs_rate / null_gg_rate if null_gg_rate > 0 else float("inf"),
    "marginal_p_gold": p_gold, "naive_iid_expected_rate": exp_rate,
    "enrichment_vs_iid_x": obs_rate / exp_rate if exp_rate > 0 else float("inf"),
    "note": "LME only; each archive has ~1-2 gold rows so absolute counts are small.",
}
print(jd(RES["D_gold_adjacency"]))

# ================================================================ E. MECHANISM
print("\n=== E. MECHANISM TEST ===")
E = {}


def mech(rows, label):
    """rows: list of dicts with keys delta, dnn_sign, arch, section, fr_s, fr_f"""
    import numpy as np
    d = np.array([r["delta"] for r in rows]); x = np.array([r["dnn"] for r in rows], float)
    fs = np.array([r["fr_s"] for r in rows]); ff = np.array([r["fr_f"] for r in rows])
    ok = np.isfinite(d) & np.isfinite(x)
    d, x, fs, ff = d[ok], x[ok], fs[ok], ff[ok]
    arch = np.array([r["arch"] for r in rows], object)[ok]
    sec = np.array([r.get("section", "_") for r in rows], object)[ok]
    med = float(np.median(x))
    close = x <= med
    out = {
        "n": int(d.size), "dnn_median": med, "dnn_mean": float(x.mean()),
        "dnn_pct": {f"p{q}": float(np.percentile(x, q)) for q in (0, 5, 25, 50, 75, 95, 100)},
        "delta_overall_pp": float(d.mean() * 100),
        "delta_close_neighbour_pp": float(d[close].mean() * 100),
        "delta_far_neighbour_pp": float(d[~close].mean() * 100),
        "effect_close_minus_far_pp": float((d[close].mean() - d[~close].mean()) * 100),
        "n_close": int(close.sum()), "n_far": int((~close).sum()),
        "sign_FR3_close": float(fs[close].mean()), "float_FR3_close": float(ff[close].mean()),
        "sign_FR3_far": float(fs[~close].mean()), "float_FR3_far": float(ff[~close].mean()),
    }
    # very-close tail (dnn <= 16 bits)
    tail = x <= 16
    if tail.sum() >= 5:
        out["n_dnn_le16"] = int(tail.sum())
        out["delta_dnn_le16_pp"] = float(d[tail].mean() * 100)
        out["delta_dnn_gt16_pp"] = float(d[~tail].mean() * 100)
        out["effect_le16_minus_gt16_pp"] = float((d[tail].mean() - d[~tail].mean()) * 100)
    else:
        out["n_dnn_le16"] = int(tail.sum())
    # raw correlation (slope of delta on dnn)
    if x.std() > 0:
        out["pearson_r_delta_vs_dnn"] = float(np.corrcoef(x, d)[0, 1])
        out["ols_slope_pp_per_bit"] = float(np.polyfit(x, d, 1)[0] * 100)
    # archive-controlled: within-archive demeaning
    def demean(vals, key):
        v = vals.copy().astype(float)
        for k in set(key.tolist()):
            m = key == k
            if m.sum() > 1: v[m] -= v[m].mean()
            else: v[m] = np.nan
        return v
    dx = demean(x, arch); dd = demean(d, arch)
    ok2 = np.isfinite(dx) & np.isfinite(dd)
    if ok2.sum() > 10 and dx[ok2].std() > 0:
        out["archive_controlled_pearson_r"] = float(np.corrcoef(dx[ok2], dd[ok2])[0, 1])
        out["archive_controlled_slope_pp_per_bit"] = float(np.polyfit(dx[ok2], dd[ok2], 1)[0] * 100)
        out["archive_controlled_n"] = int(ok2.sum())
    # archive+section controlled
    key2 = np.array([f"{a}||{s}" for a, s in zip(arch, sec)], object)
    dx2 = demean(x, key2); dd2 = demean(d, key2)
    ok3 = np.isfinite(dx2) & np.isfinite(dd2)
    if ok3.sum() > 10 and dx2[ok3].std() > 0:
        out["arch_section_controlled_pearson_r"] = float(np.corrcoef(dx2[ok3], dd2[ok3])[0, 1])
        out["arch_section_controlled_slope_pp_per_bit"] = float(np.polyfit(dx2[ok3], dd2[ok3], 1)[0] * 100)
        out["arch_section_controlled_n"] = int(ok3.sum())
    # bootstrap CI on close-minus-far
    bs = []
    n = d.size
    for _ in range(2000):
        s = rng.integers(0, n, n)
        ds, cs = d[s], close[s]
        if cs.sum() > 0 and (~cs).sum() > 0:
            bs.append((ds[cs].mean() - ds[~cs].mean()) * 100)
    if bs:
        out["effect_close_minus_far_CI95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return out


# --- LME ---
rows = []
for A in lme_archives():
    C = A["C"]; qC = A["qC"]; gold = A["gold"]; N = C.shape[0]
    Bpm = bits(C); hq = ham_q(Bpm, qC); cq = cos_q(C, qC)
    fr_s = fr3(-hq, gold); fr_f = fr3(cq, gold)
    # min hamming from any gold row to any NON-gold row
    mask = np.ones(N, bool); mask[gold] = False
    if mask.sum() == 0: continue
    Hg = ((96 - (Bpm[gold] @ Bpm.T)) // 2)
    dnn = int(Hg[:, mask].min())
    rows.append(dict(delta=fr_s - fr_f, dnn=dnn, arch=A["name"], section="_", fr_s=fr_s, fr_f=fr_f))
E["LME"] = mech(rows, "LME")
E["LME"]["archive_control_note"] = "LME has 1 question per archive -> within-archive control is degenerate/undefined."
print("LME:", jd({k: v for k, v in E["LME"].items() if "pct" not in k}))
open(EV + "/results_partial_ABCDE_lme.json", "w").write(jd({"E": E, "D": RES["D_gold_adjacency"]}))

# --- PerLTQA (archive + section control available) ---
Aq = pickle.load(open(BASE + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
Qq = pickle.load(open(BASE + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
pre = {}
for ch, v in Aq.items():
    C = v["C"]; Bpm = bits(C)
    pre[ch] = (C, Bpm)
rows = []
ss, ff_ = [], []
for qid, q in Qq.items():
    ch = q["char"]; C, Bpm = pre[ch]; N = C.shape[0]
    gold = np.atleast_1d(np.asarray(q["gold"])).astype(int)
    gold = gold[(gold >= 0) & (gold < N)]
    if gold.size == 0: continue
    hq = ham_q(Bpm, q["qC"]); cq = cos_q(C, q["qC"])
    a = fr3(-hq, gold); b = fr3(cq, gold)
    ss.append(a); ff_.append(b)
    mask = np.ones(N, bool); mask[gold] = False
    if mask.sum() == 0: continue
    Hg = ((96 - (Bpm[gold] @ Bpm.T)) // 2)
    dnn = int(Hg[:, mask].min())
    rows.append(dict(delta=a - b, dnn=dnn, arch=ch, section=q.get("section", "_"), fr_s=a, fr_f=b))
E["PERLTQA"] = mech(rows, "PERLTQA")
E["PERLTQA"]["control_FR3_sign"] = float(np.mean(ss))
E["PERLTQA"]["control_FR3_float"] = float(np.mean(ff_))
E["PERLTQA"]["control_delta_pp"] = float((np.mean(ss) - np.mean(ff_)) * 100)
E["PERLTQA"]["control_frozen_target_pp"] = -6.274728
print("PERLTQA:", jd({k: v for k, v in E["PERLTQA"].items() if "pct" not in k}))

# --- LoCoMo ---
rows = []
sl, fl = [], []
for A in locomo_archives():
    C = A["C"]; Bpm = bits(C); N = C.shape[0]; itr = A["itr"]
    for i, qa in enumerate(A["qas"]):
        ev = [itr[e] for e in qa.get("raw_evidence", []) or [] if e in itr]
        if not ev: continue
        gold = np.array(sorted(set(ev)), int)
        qC = A["QC"][i]
        hq = ham_q(Bpm, qC); cq = cos_q(C, qC)
        a = fr3(-hq, gold); b = fr3(cq, gold)
        sl.append(a); fl.append(b)
        mask = np.ones(N, bool); mask[gold] = False
        if mask.sum() == 0: continue
        Hg = ((96 - (Bpm[gold] @ Bpm.T)) // 2)
        dnn = int(Hg[:, mask].min())
        rows.append(dict(delta=a - b, dnn=dnn, arch=A["name"], section=str(qa.get("category", "_")),
                         fr_s=a, fr_f=b))
E["LOCOMO"] = mech(rows, "LOCOMO")
E["LOCOMO"]["control_FR3_sign"] = float(np.mean(sl)); E["LOCOMO"]["control_FR3_float"] = float(np.mean(fl))
E["LOCOMO"]["control_delta_pp"] = float((np.mean(sl) - np.mean(fl)) * 100)
E["LOCOMO"]["control_frozen_target_pp"] = 6.82838013
print("LOCOMO:", jd({k: v for k, v in E["LOCOMO"].items() if "pct" not in k}))

# --- REALTALK ---
rows = []
sr, fr_ = [], []
for f in sorted(glob.glob(BASE + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
    R = pickle.load(open(f, "rb"))
    C = R["C"]; Bpm = bits(C); N = C.shape[0]
    for i, g in enumerate(R["gold_rows"]):
        gold = np.atleast_1d(np.asarray(g)).astype(int)
        gold = gold[(gold >= 0) & (gold < N)]
        if gold.size == 0: continue
        qC = R["QC"][i]
        hq = ham_q(Bpm, qC); cq = cos_q(C, qC)
        a = fr3(-hq, gold); b = fr3(cq, gold)
        sr.append(a); fr_.append(b)
        mask = np.ones(N, bool); mask[gold] = False
        if mask.sum() == 0: continue
        Hg = ((96 - (Bpm[gold] @ Bpm.T)) // 2)
        dnn = int(Hg[:, mask].min())
        rows.append(dict(delta=a - b, dnn=dnn, arch=R["conv_id"], section="_", fr_s=a, fr_f=b))
E["REALTALK"] = mech(rows, "REALTALK")
E["REALTALK"]["control_delta_pp"] = float((np.mean(sr) - np.mean(fr_)) * 100)
E["REALTALK"]["control_frozen_target_pp"] = 5.300077
print("REALTALK:", jd({k: v for k, v in E["REALTALK"].items() if "pct" not in k}))

RES["E_mechanism"] = E

# --- corollary: does the sign-LOSING benchmark have MORE near-duplicate structure? ---
RES["E_corollary_near_dup_density"] = {
    "LME_delta_pp": RES["B_control"]["LME_delta_pp"],
    "LME_median_gold_dnn_bits": E["LME"]["dnn_median"],
    "LME_frac_gold_dnn_le16_pct": 100.0 * E["LME"]["n_dnn_le16"] / E["LME"]["n"],
    "PERLTQA_delta_pp": E["PERLTQA"]["control_delta_pp"],
    "PERLTQA_median_gold_dnn_bits": E["PERLTQA"]["dnn_median"],
    "PERLTQA_frac_gold_dnn_le16_pct": 100.0 * E["PERLTQA"]["n_dnn_le16"] / E["PERLTQA"]["n"],
    "LOCOMO_delta_pp": E["LOCOMO"]["control_delta_pp"],
    "LOCOMO_median_gold_dnn_bits": E["LOCOMO"]["dnn_median"],
    "REALTALK_delta_pp": E["REALTALK"]["control_delta_pp"],
    "REALTALK_median_gold_dnn_bits": E["REALTALK"]["dnn_median"],
    "test": ("If near-duplicate confusion drives the reversal, the benchmark where SIGN LOSES "
             "(PerLTQA) must have MORE near-duplicate gold neighbours (smaller dnn) than the "
             "benchmarks where SIGN WINS."),
}
print("\nCOROLLARY:", jd(RES["E_corollary_near_dup_density"]))

open(EV + "/results.json", "w").write(jd(RES))
print("\n[SAVED evidence/results.json]")
