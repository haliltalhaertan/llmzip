#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# CORRECTED coordinator execution of the R2 F1 contract on the REAL caches.
# Supersedes coord_f1_real.py, which had two coordinator errors:
#   (1) re-centered already-centered cached C  (colmean ~1e-16)
#   (2) used ALL@3 for Delta_q instead of the frozen FR@3 fractional-recall metric
# Frozen metric read from bytes: step2_eval.py:15-21 (met() returns any/all/frac; frac is used),
# NT=20 seeded tie-break permutations -> replaced here by the EXACT expectation
#   E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|      (order-independent, V43-compliant)
# Competition/Spearman/bootstrap code: f1_competition.py from branch muse/ultra-f1-repair, UNCHANGED.
import sys, os, glob, pickle, json, hashlib
import numpy as np

sys.path.insert(0, "/home/mdp/muse-work/ultra-f1-repair/research_e1_f1_repair_2026_09_14")
import f1_competition as F

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work"
OUT = f"{ROOT}/f1_real_fr3"
K = 3
os.makedirs(OUT, exist_ok=True)
manifest = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def efr(score_desc, gold, K=3):
    """Expected FR@K under uniform random tie-breaking. score_desc: higher = better."""
    s = np.asarray(score_desc, float)
    ss = np.sort(s)[::-1]
    thr = ss[K - 1]
    strictly = int((s > thr).sum())
    slots = K - strictly
    bc = int((s == thr).sum())
    g_strict = sum(1 for x in gold if s[x] > thr)
    g_tied = sum(1 for x in gold if s[x] == thr)
    return (g_strict + g_tied * (slots / bc)) / len(gold)


def delta_fr3(C, q, gold):
    """Frozen arms on ALREADY-CENTERED cache: sign=Hamming, float=cosine on raw cached C."""
    D0 = C >= 0
    Q0 = q >= 0
    dh = (D0 != Q0[None, :]).sum(axis=1).astype(float)
    cs = (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))
    return efr(-dh, gold, K), efr(cs, gold, K)


def build(items, bench):
    rows, sg, fl = [], 0.0, 0.0
    for qid, C, q, gold, cluster, section in items:
        C = np.asarray(C, float)
        q = np.asarray(q, float)
        s, f = delta_fr3(C, q, gold)
        sg += s
        fl += f
        rows.append(F.query_row(C.tolist(), q.tolist(), list(gold), s - f,
                                k=64, qid=qid, benchmark=bench,
                                cluster=cluster, section=section))
    n = len(rows)
    return rows, sg / n, fl / n


# ---------------- LongMemEval ----------------
items = []
for p in sorted(glob.glob(f"{ROOT}/regen/lme/cache_repr/*.pkl")):
    d = pickle.load(open(p, "rb"))
    g = [int(x) for x in np.atleast_1d(d["gold"])]
    if not g:
        continue
    qid = d["question_id"]
    items.append((qid, d["C"], d["qC"], g, qid, None))
    manifest.append((f"regen/lme/cache_repr/{os.path.basename(p)}", sha(p)))
print(f"LME n={len(items)}", flush=True)
lme_rows, lme_s, lme_f = build(items, "LME")
print(f"LME sign={lme_s!r} float={lme_f!r} delta_pp={100*(lme_s-lme_f):.6f}", flush=True)

# ---------------- PerLTQA ----------------
ap = f"{ROOT}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
qp = f"{ROOT}/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
arch = pickle.load(open(ap, "rb"))
qdat = pickle.load(open(qp, "rb"))
manifest += [("bench3/runs/b3b_perltqa/cache_arch_eval.pkl", sha(ap)),
             ("bench3/runs/b3b_perltqa/cache_q_eval.pkl", sha(qp))]
items = []
for qid, rec in qdat.items():
    g = [int(x) for x in np.atleast_1d(rec["gold"])]
    if not g:
        continue
    items.append((qid, arch[rec["char"]]["C"], rec["qC"], g, rec["char"], rec.get("section")))
print(f"PERLTQA n={len(items)} archives={len(arch)}", flush=True)
plt_rows, plt_s, plt_f = build(items, "PERLTQA")
print(f"PERLTQA sign={plt_s!r} float={plt_f!r} delta_pp={100*(plt_s-plt_f):.6f}", flush=True)

# ---------------- REALTALK ----------------
items = []
for p in sorted(glob.glob(f"{ROOT}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
    d = pickle.load(open(p, "rb"))
    manifest.append((f"bench3/runs/b3a_realtalk/rt_repr/{os.path.basename(p)}", sha(p)))
    QC = np.asarray(d["QC"], float)
    for i, qid in enumerate(d["qids"]):
        g = [int(x) for x in np.atleast_1d(d["gold_rows"][i])]
        if not g:
            continue
        items.append((qid, d["C"], QC[i], g, d.get("chat_no"), None))
print(f"REALTALK n={len(items)}", flush=True)
rt_rows, rt_s, rt_f = build(items, "REALTALK")
print(f"REALTALK sign={rt_s!r} float={rt_f!r} delta_pp={100*(rt_s-rt_f):.6f}", flush=True)

# ---------------- summaries + auditor comparison ----------------
AUD = {"LME": (0.1417, 0.1405), "REALTALK": (0.0979, 0.1228),
       "PERLTQA": (0.2542, 0.2798), "LOCOMO": (0.0949, 0.1038)}
FROZEN = {"LME": 10.037943, "PERLTQA": -6.275, "REALTALK": 5.2241}
summary = {}
for name, rows, s, f in [("LME", lme_rows, lme_s, lme_f),
                         ("PERLTQA", plt_rows, plt_s, plt_f),
                         ("REALTALK", rt_rows, rt_s, rt_f)]:
    ok = F.benchmark_summary(rows)
    bug = F.benchmark_summary(rows, strict_key="min_strict_gap", tie_key="min_tie_gap")
    boot = F.cluster_bootstrap(rows)
    summary[name] = {
        "n": ok["n"], "multi_gold_rate": ok["multi_gold_rate"],
        "sign_fr3": s, "float_fr3": f, "delta_pp": 100 * (s - f),
        "frozen_delta_pp": FROZEN[name], "delta_pp_diff": 100 * (s - f) - FROZEN[name],
        "rho_strict": ok["rho_strict"], "rho_tie": ok["rho_tie"],
        "auditor_strict": AUD[name][0], "auditor_tie": AUD[name][1],
        "diff_strict": (ok["rho_strict"] - AUD[name][0]) if ok["rho_strict"] is not None else None,
        "diff_tie": (ok["rho_tie"] - AUD[name][1]) if ok["rho_tie"] is not None else None,
        "rho_strict_MINGOLD_BUG": bug["rho_strict"], "rho_tie_MINGOLD_BUG": bug["rho_tie"],
        "bootstrap": boot,
    }
    d = summary[name]
    print(f"\n{name}: delta_pp={d['delta_pp']:+.6f} (frozen {d['frozen_delta_pp']:+.6f}, diff {d['delta_pp_diff']:+.6f})"
          f"\n  rho_strict={d['rho_strict']!r}  auditor={d['auditor_strict']}  diff={d['diff_strict']}"
          f"\n  rho_tie   ={d['rho_tie']!r}  auditor={d['auditor_tie']}  diff={d['diff_tie']}"
          f"\n  MINGOLD strict={d['rho_strict_MINGOLD_BUG']!r} tie={d['rho_tie_MINGOLD_BUG']!r}"
          f"\n  n={d['n']} multi_gold_rate={d['multi_gold_rate']:.4f}", flush=True)

json.dump({"summary": summary, "note": "LOCOMO not run: per-query float surface absent from committed caches"},
          open(f"{OUT}/results.json", "w"), indent=1)
with open(f"{OUT}/MANIFEST.sha256", "w", newline="\n") as fh:
    for p, h in sorted(manifest):
        fh.write(f"{h}  {p}\n")
print(f"\nWROTE {OUT}/results.json manifest={len(manifest)}")
