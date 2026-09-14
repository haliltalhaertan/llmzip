#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Step 1: reproduce a frozen headline (CONTROL).
Step 2: scope facts -- exact N distribution per benchmark family.
READ-ONLY on all caches.
"""
import os, sys, glob, json, pickle, hashlib
import numpy as np

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/agent_out/scale-honest"
os.makedirs(os.path.join(OUT, "evidence"), exist_ok=True)


# ---------------- frozen metric machinery ----------------
def fr_at_k_expect(scores, gold, K=3, higher_is_better=True):
    """EXACT expectation of FR@K under uniform random tie-breaking.
    E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|
    thr = K-th best score; slots = K - #{strictly better than thr}; bc = #{equal to thr}
    """
    s = np.asarray(scores, dtype=np.float64)
    if not higher_is_better:
        s = -s
    n = s.shape[0]
    if n <= K:
        # everything retrieved
        return 1.0
    # K-th best
    part = np.partition(s, n - K)
    thr = part[n - K]
    better = int(np.sum(s > thr))
    bc = int(np.sum(s == thr))
    slots = K - better
    g = np.asarray(gold, dtype=np.int64)
    if g.size == 0:
        return float("nan")
    gs = s[g]
    g_strict = int(np.sum(gs > thr))
    g_tied = int(np.sum(gs == thr))
    if bc <= 0:
        return g_strict / g.size
    return (g_strict + g_tied * (slots / bc)) / g.size


def sign_scores(C, qC):
    """Hamming-based similarity: higher = better. score = -hamming."""
    B = (C >= 0)
    qb = (qC >= 0)
    ham = np.sum(B != qb[None, :], axis=1)
    return -ham.astype(np.float64)


def float_scores(C, qC):
    """cosine on raw cached (already-centered) C."""
    nC = np.linalg.norm(C, axis=1)
    nq = np.linalg.norm(qC)
    d = nC * nq
    d[d == 0] = 1e-30
    return (C @ qC) / d


def tie_stats(scores, K=3):
    s = np.asarray(scores, dtype=np.float64)
    n = s.shape[0]
    if n <= K:
        return 0.0, 0
    part = np.partition(s, n - K)
    thr = part[n - K]
    bc = int(np.sum(s == thr))
    better = int(np.sum(s > thr))
    slots = K - better
    tied = 1.0 if bc > slots else 0.0
    return tied, bc


# ---------------- loaders ----------------
def load_lme():
    files = sorted(glob.glob(os.path.join(ROOT, "regen/lme/cache_repr/*.pkl")))
    out = []
    for f in files:
        with open(f, "rb") as fh:
            d = pickle.load(fh)
        out.append(d)
    return out


def load_realtalk():
    files = sorted(glob.glob(os.path.join(ROOT, "bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")))
    out = []
    for f in files:
        with open(f, "rb") as fh:
            out.append(pickle.load(fh))
    return out


def load_perltqa():
    with open(os.path.join(ROOT, "bench3/runs/b3b_perltqa/cache_arch_eval.pkl"), "rb") as fh:
        arch = pickle.load(fh)
    with open(os.path.join(ROOT, "bench3/runs/b3b_perltqa/cache_q_eval.pkl"), "rb") as fh:
        qs = pickle.load(fh)
    return arch, qs


def load_locomo():
    files = sorted(glob.glob(os.path.join(ROOT, "regen/locomo/locomo_*.pkl")))
    out = []
    for f in files:
        with open(f, "rb") as fh:
            out.append(pickle.load(fh))
    return out


# ---------------- CONTROL: LME frozen headline ----------------
def control_lme():
    L = load_lme()
    sg, fl = [], []
    Ns = []
    for d in L:
        C = np.asarray(d["C"], dtype=np.float64)
        qC = np.asarray(d["qC"], dtype=np.float64)
        gold = np.asarray(d["gold"], dtype=np.int64)
        Ns.append(C.shape[0])
        sg.append(fr_at_k_expect(sign_scores(C, qC), gold, 3))
        fl.append(fr_at_k_expect(float_scores(C, qC), gold, 3))
    sg = np.array(sg); fl = np.array(fl)
    return dict(n_queries=len(sg), sign=float(sg.mean()), float_=float(fl.mean()),
                delta_pp=float((sg - fl).mean() * 100),
                delta_se_pp=float((sg - fl).std(ddof=1) / np.sqrt(len(sg)) * 100),
                N_list=Ns), L


def control_realtalk():
    R = load_realtalk()
    sg, fl, Ns = [], [], []
    for d in R:
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        gold_rows = d["gold_rows"]
        for i in range(QC.shape[0]):
            g = np.asarray(gold_rows[i], dtype=np.int64)
            if g.size == 0:
                continue
            Ns.append(C.shape[0])
            sg.append(fr_at_k_expect(sign_scores(C, QC[i]), g, 3))
            fl.append(fr_at_k_expect(float_scores(C, QC[i]), g, 3))
    sg = np.array(sg); fl = np.array(fl)
    return dict(n_queries=len(sg), sign=float(sg.mean()), float_=float(fl.mean()),
                delta_pp=float((sg - fl).mean() * 100),
                delta_se_pp=float((sg - fl).std(ddof=1) / np.sqrt(len(sg)) * 100),
                N_arch=sorted(set(np.asarray(d["C"]).shape[0] for d in R)))


def control_perltqa():
    arch, qs = load_perltqa()
    sg, fl = [], []
    for qid, q in qs.items():
        ch = q["char"]
        if ch not in arch:
            continue
        C = np.asarray(arch[ch]["C"], dtype=np.float64)
        qC = np.asarray(q["qC"], dtype=np.float64)
        g = np.asarray(q["gold"], dtype=np.int64)
        if g.size == 0:
            continue
        sg.append(fr_at_k_expect(sign_scores(C, qC), g, 3))
        fl.append(fr_at_k_expect(float_scores(C, qC), g, 3))
    sg = np.array(sg); fl = np.array(fl)
    return dict(n_queries=len(sg), sign=float(sg.mean()), float_=float(fl.mean()),
                delta_pp=float((sg - fl).mean() * 100),
                delta_se_pp=float((sg - fl).std(ddof=1) / np.sqrt(len(sg)) * 100),
                N_arch=sorted(np.asarray(v["C"]).shape[0] for v in arch.values()))


def control_locomo():
    Lo = load_locomo()
    sg, fl, Ns = [], [], []
    for d in Lo:
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        id_to_row = d["id_to_row"]
        qas = d["qas"]
        for i, qa in enumerate(qas):
            ev = qa.get("raw_evidence") or []
            rows = [id_to_row[e] for e in ev if e in id_to_row]
            if not rows:
                continue
            g = np.asarray(sorted(set(rows)), dtype=np.int64)
            Ns.append(C.shape[0])
            sg.append(fr_at_k_expect(sign_scores(C, QC[i]), g, 3))
            fl.append(fr_at_k_expect(float_scores(C, QC[i]), g, 3))
    sg = np.array(sg); fl = np.array(fl)
    return dict(n_queries=len(sg), sign=float(sg.mean()), float_=float(fl.mean()),
                delta_pp=float((sg - fl).mean() * 100),
                delta_se_pp=float((sg - fl).std(ddof=1) / np.sqrt(len(sg)) * 100),
                N_arch=sorted(set(np.asarray(d["C"]).shape[0] for d in Lo)))


def dist_summary(v):
    v = np.asarray(sorted(v))
    return dict(count=int(v.size), min=int(v.min()), p25=float(np.percentile(v, 25)),
                median=float(np.median(v)), p75=float(np.percentile(v, 75)),
                max=int(v.max()), total=int(v.sum()), mean=float(v.mean()))


if __name__ == "__main__":
    res = {}
    print("=== CONTROL: frozen headline reproduction ===", flush=True)
    lme, L = control_lme()
    res["control_lme"] = lme
    print("LME  FR@3 sign=%.16f float=%.16f delta=%+.6f pp (SE %.4f) nq=%d"
          % (lme["sign"], lme["float_"], lme["delta_pp"], lme["delta_se_pp"], lme["n_queries"]), flush=True)

    plt = control_perltqa(); res["control_perltqa"] = plt
    print("PLT  delta=%+.6f pp (SE %.4f) nq=%d" % (plt["delta_pp"], plt["delta_se_pp"], plt["n_queries"]), flush=True)
    rt = control_realtalk(); res["control_realtalk"] = rt
    print("RT   delta=%+.6f pp (SE %.4f) nq=%d" % (rt["delta_pp"], rt["delta_se_pp"], rt["n_queries"]), flush=True)
    lo = control_locomo(); res["control_locomo"] = lo
    print("LOCO delta=%+.6f pp (SE %.4f) nq=%d" % (lo["delta_pp"], lo["delta_se_pp"], lo["n_queries"]), flush=True)

    # ---- scope facts ----
    print("\n=== SCOPE FACTS: archive N distributions ===", flush=True)
    scope = {}
    scope["LongMemEval"] = dist_summary(lme["N_list"])
    # per-archive unique N for RT/PLT/LOCO
    R = load_realtalk()
    scope["REALTALK"] = dist_summary([np.asarray(d["C"]).shape[0] for d in R])
    arch, qs = load_perltqa()
    scope["PerLTQA"] = dist_summary([np.asarray(v["C"]).shape[0] for v in arch.values()])
    Lo = load_locomo()
    scope["LoCoMo"] = dist_summary([np.asarray(d["C"]).shape[0] for d in Lo])
    for k, v in scope.items():
        print("%-12s n_arch=%4d  min=%5d  med=%8.1f  max=%5d  total_docs=%8d"
              % (k, v["count"], v["min"], v["median"], v["max"], v["total"]), flush=True)
    res["scope"] = scope

    grand_total = sum(v["total"] for v in scope.values())
    grand_max = max(v["max"] for v in scope.values())
    res["grand_total_docs"] = grand_total
    res["largest_single_archive"] = grand_max
    print("\nGRAND TOTAL documents across all 4 families: %d" % grand_total, flush=True)
    print("LARGEST SINGLE REAL ARCHIVE: %d" % grand_max, flush=True)
    for tier in (100_000, 500_000, 1_000_000, 10_000_000):
        print("  tier %9d : ratio to largest real archive = %.1fx ; to grand total = %.2fx"
              % (tier, tier / grand_max, tier / grand_total), flush=True)
    res["tier_ratios"] = {str(t): dict(vs_largest_archive=t / grand_max, vs_grand_total=t / grand_total)
                          for t in (100_000, 500_000, 1_000_000, 10_000_000)}

    with open(os.path.join(OUT, "evidence", "step1_control_scope.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote evidence/step1_control_scope.json", flush=True)
