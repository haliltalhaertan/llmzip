#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Coordinator execution of the R2 F1 contract on the REAL caches.
# Implementation: f1_competition.py from branch muse/ultra-f1-repair (SPEC-derived, 27 oracle checks PASS).
# This script only (a) loads real caches, (b) computes Delta_q per the frozen ALL@3 spec,
# (c) calls the agent's competition/Spearman/bootstrap code unchanged.
import sys, os, glob, pickle, json, hashlib, collections
from math import comb
import numpy as np

sys.path.insert(0, "/home/mdp/muse-work/ultra-f1-repair/research_e1_f1_repair_2026_09_14")
import f1_competition as F

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work"
K = 3
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/f1_real"
os.makedirs(OUT, exist_ok=True)
manifest = []


def sha(p, cap=None):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def exp_all_at_k(d, gold, K=3):
    """Expected ALL@K under uniform random tie-breaking (frozen order-independent rule)."""
    sd = np.sort(d)
    thr = sd[K - 1]
    strictly = int((d < thr).sum())
    slots = K - strictly
    bc = int((d == thr).sum())
    g_strict = sum(1 for g in gold if d[g] < thr)
    g_tied = sum(1 for g in gold if d[g] == thr)
    if len(gold) - g_strict - g_tied > 0:
        return 0.0
    if g_tied == 0:
        return 1.0
    if g_tied > slots:
        return 0.0
    return comb(bc - g_tied, slots - g_tied) / comb(bc, slots)


def delta_q(C, qC, gold):
    """SIGN96 Hamming ALL@3 minus centered-float cosine ALL@3, per query."""
    mu = C.mean(axis=0)
    Cc = C - mu
    qc = qC - mu
    B = Cc >= 0
    qb = qc >= 0
    dh = (B != qb).sum(axis=1).astype(np.float64)
    nb = np.linalg.norm(Cc, axis=1)
    cos = (Cc @ qc) / (nb * np.linalg.norm(qc) + 1e-30)
    return exp_all_at_k(dh, gold, K), exp_all_at_k(-cos.astype(np.float64), gold, K)


def rows_for(items, bench):
    """items: list of (qid, C, qC, gold, cluster, section)"""
    rows, sgn, flt = [], [], []
    for qid, C, qC, gold, cluster, section in items:
        C = np.asarray(C, dtype=np.float64)
        qC = np.asarray(qC, dtype=np.float64)
        hs, hf = delta_q(C, qC, gold)
        sgn.append(hs)
        flt.append(hf)
        rows.append(F.query_row(C.tolist(), qC.tolist(), list(gold), hs - hf,
                                k=64, qid=qid, benchmark=bench,
                                cluster=cluster, section=section))
    return rows, float(np.mean(sgn)), float(np.mean(flt))


# ---------------- LME: 470 archives, one query each ----------------
items = []
for f in sorted(glob.glob(f"{ROOT}/regen/lme/cache_repr/*.pkl")):
    d = pickle.load(open(f, "rb"))
    qid = d["question_id"]
    items.append((qid, d["C"], d["qC"], [int(g) for g in np.atleast_1d(d["gold"])], qid, None))
    manifest.append((f"regen/lme/cache_repr/{os.path.basename(f)}", sha(f)))
print(f"LME items: {len(items)}", flush=True)
lme_rows, lme_s, lme_f = rows_for(items, "LME")
print(f"LME sign={lme_s!r} float={lme_f!r} delta_pp={100*(lme_s-lme_f):.10f}", flush=True)

# ---------------- PerLTQA: 30 archives, 8265 queries ----------------
ap = f"{ROOT}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
qp = f"{ROOT}/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
arch = pickle.load(open(ap, "rb"))
qdat = pickle.load(open(qp, "rb"))
manifest += [("bench3/runs/b3b_perltqa/cache_arch_eval.pkl", sha(ap)),
             ("bench3/runs/b3b_perltqa/cache_q_eval.pkl", sha(qp))]
items = []
for qid, rec in qdat.items():
    ch = rec["char"]
    gold = [int(g) for g in np.atleast_1d(rec["gold"])]
    if not gold:
        continue
    items.append((qid, arch[ch]["C"], rec["qC"], gold, ch, rec.get("section")))
print(f"PerLTQA items: {len(items)} archives={len(arch)}", flush=True)
plt_rows, plt_s, plt_f = rows_for(items, "PERLTQA")
print(f"PERLTQA sign={plt_s!r} float={plt_f!r} delta_pp={100*(plt_s-plt_f):.10f}", flush=True)

# ---------------- REALTALK: 10 files ----------------
items = []
for f in sorted(glob.glob(f"{ROOT}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
    d = pickle.load(open(f, "rb"))
    manifest.append((f"bench3/runs/b3a_realtalk/rt_repr/{os.path.basename(f)}", sha(f)))
    C = d["C"]
    QC = d["QC"]
    qids = d["qids"]
    gr = d["gold_rows"]
    cl = d.get("chat_no")
    for i, qid in enumerate(qids):
        gold = [int(g) for g in np.atleast_1d(gr[i])]
        if not gold:
            continue
        items.append((qid, C, np.asarray(QC)[i], gold, cl, None))
print(f"REALTALK items: {len(items)}", flush=True)
rt_rows, rt_s, rt_f = rows_for(items, "REALTALK")
print(f"REALTALK sign={rt_s!r} float={rt_f!r} delta_pp={100*(rt_s-rt_f):.10f}", flush=True)

summary = {}
for name, rows, s, fl in [("LME", lme_rows, lme_s, lme_f),
                          ("PERLTQA", plt_rows, plt_s, plt_f),
                          ("REALTALK", rt_rows, rt_s, rt_f)]:
    summary[name] = F.benchmark_summary(rows)
    summary[name].update({"sign_all3": s, "float_all3": fl, "delta_pp": 100 * (s - fl)})
    # min-gold bug reproduction
    mg = F.benchmark_summary(rows, strict_key="min_strict_gap", tie_key="min_tie_gap")
    summary[name]["rho_strict_MINGOLD_BUG"] = mg["rho_strict"]
    summary[name]["rho_tie_MINGOLD_BUG"] = mg["rho_tie"]
    print(f"\n{name}: rho_strict={summary[name]['rho_strict']!r} rho_tie={summary[name]['rho_tie']!r}"
          f"\n      MINGOLD strict={mg['rho_strict']!r} tie={mg['rho_tie']!r}"
          f"\n      n={summary[name]['n']} multi_gold_rate={summary[name]['multi_gold_rate']:.4f}", flush=True)

json.dump({"summary": summary,
           "cohort": {"lme_n": len(lme_rows), "perltqa_n": len(plt_rows), "realtalk_n": len(rt_rows)}},
          open(f"{OUT}/results.json", "w"), indent=1)
with open(f"{OUT}/MANIFEST.sha256", "w", newline="\n") as fh:
    for p, h in sorted(manifest):
        fh.write(f"{h}  {p}\n")
print(f"\nWROTE {OUT}/results.json  manifest_entries={len(manifest)}")
