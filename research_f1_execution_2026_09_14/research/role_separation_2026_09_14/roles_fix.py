#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
roles_fix.py -- (F1) FIX AUC direction bug in roles_main.py auc_fast();
                (F2) LoCoMo gold-gold adjacency (multi-gold, unlike LME);
                (F3) DIRECT test of the stated hypothesis: gold whose NEAREST non-gold neighbour
                     is literally an adjacent conversational turn (the "both speakers indexed"
                     near-duplicate). Does THAT hurt the sign arm?
                (F4) adversarial: shuffled-label control for the mapping.
Appends to evidence/results.json.
"""
import json, pickle, glob, os
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
EV = BASE + "/agent_out/role-separation/evidence"
rng = np.random.default_rng(777)
RES = json.load(open(EV + "/results.json"))


def jd(o):
    def conv(x):
        if isinstance(x, np.floating): return float(x)
        if isinstance(x, np.integer): return int(x)
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, np.bool_): return bool(x)
        raise TypeError(str(type(x)))
    return json.dumps(o, indent=2, default=conv)


def fr3(s, gold, K=3):
    s = np.asarray(s, np.float64); gold = np.asarray(gold, np.int64)
    if gold.size == 0 or s.size == 0: return float("nan")
    if s.size <= K: return 1.0
    thr = np.partition(s, -K)[-K]
    st = int((s > thr).sum()); slots = K - st; bc = int((s == thr).sum())
    gs = s[gold]; g1 = int((gs > thr).sum()); g2 = int((gs == thr).sum())
    return (g1 + g2 * slots / bc) / gold.size if bc else g1 / gold.size


def bits(C): return np.where(C >= 0, 1, -1).astype(np.int16)
def ham_q(B, q): return ((96 - (B @ np.where(q >= 0, 1, -1).astype(np.int16))) // 2).astype(np.float64)
def cos_q(C, q):
    d = np.linalg.norm(C, axis=1) * np.linalg.norm(q); d[d == 0] = 1e-300
    return (C @ q) / d


# ---------------- F1: correct AUC ----------------
def auc_pos_lt_neg(hp, hn):
    """P(pos < neg) + 0.5 P(pos == neg), from Hamming histograms (0..96)."""
    hp = np.asarray(hp, float); hn = np.asarray(hn, float)
    hp = hp / hp.sum(); hn = hn / hn.sum()
    surv = np.concatenate([np.cumsum(hn[::-1])[::-1][1:], [0.0]])  # surv[k] = P(neg > k)
    return float((hp * (surv + 0.5 * hn)).sum())


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
        yield dict(name=qid, C=P["C"], qC=P["qC"], gold=np.asarray(P["gold"]).ravel().astype(int),
                   roles=np.array(roles, object), sess=np.array(sess))


def locomo_archives():
    for f in sorted(glob.glob(BASE + "/regen/locomo/locomo_*.pkl")):
        L = pickle.load(open(f, "rb"))
        N = L["C"].shape[0]; sess = np.zeros(N, int); turn = np.zeros(N, int)
        for k, r in L["id_to_row"].items():
            a, b = k.split(":"); sess[r] = int(a[1:]); turn[r] = int(b)
        yield dict(name=L["conv_id"], C=L["C"], QC=L["QC"], qas=L["qas"], itr=L["id_to_row"],
                   sess=sess, turn=turn)


FIX = {}
# recompute AUC from stored histograms is not possible (rnd was subsampled separately),
# so recompute both histograms exactly here.
adjh = np.zeros(97, np.int64); allh = np.zeros(97, np.int64)
adjh2 = np.zeros(97, np.int64); allh2 = np.zeros(97, np.int64)
for A in lme_archives():
    C = A["C"]; N = C.shape[0]; B = bits(C)
    H = ((96 - (B @ B.T)) // 2)
    iu = np.triu_indices(N, 1)
    allh += np.bincount(H[iu], minlength=97)
    a = np.arange(N - 1); m = A["sess"][a] == A["sess"][a + 1]
    adjh += np.bincount(H[a[m], a[m] + 1], minlength=97)
for A in locomo_archives():
    C = A["C"]; N = C.shape[0]; B = bits(C)
    H = ((96 - (B @ B.T)) // 2)
    iu = np.triu_indices(N, 1)
    allh2 += np.bincount(H[iu], minlength=97)
    o = np.lexsort((A["turn"], A["sess"])); a, b = o[:-1], o[1:]
    m = (A["sess"][a] == A["sess"][b]) & (A["turn"][b] - A["turn"][a] == 1)
    adjh2 += np.bincount(H[a[m], b[m]], minlength=97)

# non-adjacent histogram = all - adjacent
nonadj = allh - adjh
nonadj2 = allh2 - adjh2
FIX["F1_AUC_corrected"] = {
    "BUG": ("roles_main.py auc_fast() used P(neg < k) instead of P(neg > k), so it reported "
            "P(adj > rnd). Correct AUC = 1 - reported."),
    "LME_AUC_adjacent_vs_nonadjacent": auc_pos_lt_neg(adjh, nonadj),
    "LME_AUC_reported_buggy": RES["C_distributions"]["LME"]["AUC_adj_vs_rnd"],
    "LOCOMO_AUC_adjacent_vs_nonadjacent": auc_pos_lt_neg(adjh2, nonadj2),
    "LOCOMO_AUC_reported_buggy": RES["C_distributions"]["LOCOMO"]["AUC_adj_vs_rnd"],
    "LME_adj_mean_exact": float((adjh * np.arange(97)).sum() / adjh.sum()),
    "LME_nonadj_mean_exact": float((nonadj * np.arange(97)).sum() / nonadj.sum()),
    "LOCOMO_adj_mean_exact": float((adjh2 * np.arange(97)).sum() / adjh2.sum()),
    "LOCOMO_nonadj_mean_exact": float((nonadj2 * np.arange(97)).sum() / nonadj2.sum()),
    "LME_tail_le16_nonadjacent_frac_pct": 100.0 * nonadj[:17].sum() / allh[:17].sum(),
    "LOCOMO_tail_le16_nonadjacent_frac_pct": 100.0 * nonadj2[:17].sum() / allh2[:17].sum(),
}
print(jd(FIX["F1_AUC_corrected"]))

# ---------------- F2: LoCoMo gold-gold adjacency ----------------
gg = 0; adj_tot = 0; gg_all = 0; all_tot = 0
for A in locomo_archives():
    N = A["C"].shape[0]; itr = A["itr"]
    goldset = set()
    per_q = []
    for qa in A["qas"]:
        ev = sorted({itr[e] for e in (qa.get("raw_evidence") or []) if e in itr})
        if ev: per_q.append(ev); goldset.update(ev)
    o = np.lexsort((A["turn"], A["sess"])); a, b = o[:-1], o[1:]
    m = (A["sess"][a] == A["sess"][b]) & (A["turn"][b] - A["turn"][a] == 1)
    ai, bi = a[m], b[m]; adj_tot += ai.size
    all_tot += N * (N - 1) // 2
    for ev in per_q:
        s = set(ev)
        gg += sum(1 for x, y in zip(ai, bi) if x in s and y in s)
        gg_all += len(ev) * (len(ev) - 1) // 2
FIX["F2_locomo_gold_adjacency"] = {
    "adjacent_pairs": int(adj_tot), "gold_gold_adjacent_pairs_summed_over_queries": int(gg),
    "gold_gold_pairs_any_distance_summed": int(gg_all),
    "frac_of_within_query_gold_pairs_that_are_adjacent_pct": 100.0 * gg / max(gg_all, 1),
    "chance_frac_adjacent_pct": 100.0 * adj_tot / all_tot,
    "enrichment_x": (gg / max(gg_all, 1)) / (adj_tot / all_tot),
    "note": "per-query gold sets (raw_evidence), so this measures whether EVIDENCE spans adjacent turns.",
}
print(jd(FIX["F2_locomo_gold_adjacency"]))

# ---------------- F3: DIRECT hypothesis test ----------------
# For each query: is the gold row's NEAREST non-gold row an ADJACENT conversational turn?
def direct(rows, name):
    d = np.array([r["delta"] for r in rows]); isadj = np.array([r["nn_is_adj"] for r in rows], bool)
    arch = np.array([r["arch"] for r in rows], object)
    sec = np.array([r["section"] for r in rows], object)
    out = {"n": int(d.size), "n_nn_is_adjacent": int(isadj.sum()),
           "frac_nn_is_adjacent_pct": 100.0 * isadj.mean(),
           "delta_when_nn_adjacent_pp": float(d[isadj].mean() * 100) if isadj.any() else None,
           "delta_when_nn_not_adjacent_pp": float(d[~isadj].mean() * 100) if (~isadj).any() else None}
    if isadj.any() and (~isadj).any():
        out["effect_pp"] = out["delta_when_nn_adjacent_pp"] - out["delta_when_nn_not_adjacent_pp"]
        bs = []
        for _ in range(3000):
            s = rng.integers(0, d.size, d.size); ds, js = d[s], isadj[s]
            if js.any() and (~js).any(): bs.append((ds[js].mean() - ds[~js].mean()) * 100)
        out["effect_CI95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        # archive+section demeaned
        v = d.astype(float).copy(); w = isadj.astype(float).copy()
        key = np.array([f"{a}||{s}" for a, s in zip(arch, sec)], object)
        for k in set(key.tolist()):
            m2 = key == k
            if m2.sum() > 1: v[m2] -= v[m2].mean(); w[m2] -= w[m2].mean()
            else: v[m2] = np.nan
        ok = np.isfinite(v) & np.isfinite(w)
        if ok.sum() > 10 and w[ok].std() > 0:
            out["arch_section_controlled_slope_pp"] = float(np.polyfit(w[ok], v[ok], 1)[0] * 100)
            out["arch_section_controlled_n"] = int(ok.sum())
    return out


rows = []
for A in lme_archives():
    C = A["C"]; B = bits(C); N = C.shape[0]; gold = A["gold"]
    hq = ham_q(B, A["qC"]); cq = cos_q(C, A["qC"])
    a_, b_ = fr3(-hq, gold), fr3(cq, gold)
    mask = np.ones(N, bool); mask[gold] = False
    if mask.sum() == 0: continue
    Hg = ((96 - (B[gold] @ B.T)) // 2).astype(float)
    Hg[:, ~mask] = 1e9
    gi, ni = np.unravel_index(np.argmin(Hg), Hg.shape)
    grow = gold[gi]
    nn_adj = (abs(int(ni) - int(grow)) == 1) and (A["sess"][ni] == A["sess"][grow])
    rows.append(dict(delta=a_ - b_, nn_is_adj=nn_adj, arch=A["name"], section="_"))
FIX["F3_LME_direct"] = direct(rows, "LME")
print("F3 LME:", jd(FIX["F3_LME_direct"]))

rows = []
for A in locomo_archives():
    C = A["C"]; B = bits(C); N = C.shape[0]; itr = A["itr"]
    for i, qa in enumerate(A["qas"]):
        ev = sorted({itr[e] for e in (qa.get("raw_evidence") or []) if e in itr})
        if not ev: continue
        gold = np.array(ev, int)
        qC = A["QC"][i]
        a_, b_ = fr3(-ham_q(B, qC), gold), fr3(cos_q(C, qC), gold)
        mask = np.ones(N, bool); mask[gold] = False
        if mask.sum() == 0: continue
        Hg = ((96 - (B[gold] @ B.T)) // 2).astype(float); Hg[:, ~mask] = 1e9
        gi, ni = np.unravel_index(np.argmin(Hg), Hg.shape)
        grow = gold[gi]
        nn_adj = (A["sess"][ni] == A["sess"][grow]) and (abs(int(A["turn"][ni]) - int(A["turn"][grow])) == 1)
        rows.append(dict(delta=a_ - b_, nn_is_adj=nn_adj, arch=A["name"],
                         section=str(qa.get("category", "_"))))
FIX["F3_LOCOMO_direct"] = direct(rows, "LOCOMO")
print("F3 LOCOMO:", jd(FIX["F3_LOCOMO_direct"]))

# ---------------- F4: adversarial mapping control ----------------
# If my LME role/session mapping were wrong, the adjacency signal should vanish under a
# WITHIN-ARCHIVE ROW SHUFFLE of the session labels. Also: shuffle roles and re-measure asymmetry.
sh_adj = np.zeros(97, np.int64)
ua = []; au = []; ua_s = []; au_s = []
for A in lme_archives():
    C = A["C"]; N = C.shape[0]; B = bits(C)
    H = ((96 - (B @ B.T)) // 2)
    perm = rng.permutation(N)
    sess_p = A["sess"][perm]
    a = np.arange(N - 1); m = sess_p[a] == sess_p[a + 1]
    if m.any(): sh_adj += np.bincount(H[a[m], a[m] + 1], minlength=97)
    # true role asymmetry
    m2 = A["sess"][a] == A["sess"][a + 1]
    ai, aj = a[m2], a[m2] + 1
    ri, rj = A["roles"][ai], A["roles"][aj]
    h = H[ai, aj]
    ua.append(h[(ri == "user") & (rj == "assistant")])
    au.append(h[(ri == "assistant") & (rj == "user")])
    # role-shuffled control (keep adjacency, permute role labels)
    rp = rng.permutation(A["roles"])
    ri2, rj2 = rp[ai], rp[aj]
    ua_s.append(h[(ri2 == "user") & (rj2 == "assistant")])
    au_s.append(h[(ri2 == "assistant") & (rj2 == "user")])
ua = np.concatenate(ua); au = np.concatenate(au)
ua_s = np.concatenate(ua_s); au_s = np.concatenate(au_s)
FIX["F4_adversarial_controls"] = {
    "LME_adjacent_mean_TRUE_mapping": float((adjh * np.arange(97)).sum() / adjh.sum()),
    "LME_adjacent_mean_SESSION_SHUFFLED": float((sh_adj * np.arange(97)).sum() / sh_adj.sum()),
    "interpretation_mapping": ("If the mapping were arbitrary, shuffled 'adjacency' would match "
                               "the true adjacency mean. A large gap proves the mapping carries "
                               "real conversational order."),
    "role_ua_mean_TRUE": float(ua.mean()), "role_au_mean_TRUE": float(au.mean()),
    "role_asym_bits_TRUE_(au-ua)": float(au.mean() - ua.mean()),
    "role_ua_mean_SHUFFLED": float(ua_s.mean()), "role_au_mean_SHUFFLED": float(au_s.mean()),
    "role_asym_bits_SHUFFLED": float(au_s.mean() - ua_s.mean()),
    "n_ua": int(ua.size), "n_au": int(au.size),
}
print(jd(FIX["F4_adversarial_controls"]))

RES["F_fixes_and_adversarial"] = FIX
open(EV + "/results.json", "w").write(jd(RES))
print("\n[SAVED evidence/results.json with F block]")
