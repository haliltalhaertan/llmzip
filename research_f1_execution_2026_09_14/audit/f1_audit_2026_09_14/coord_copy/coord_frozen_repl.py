#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# CORRECTED replication of the frozen E1 metric.
# Fixes two coordinator errors found by reading step2_eval.py bytes:
#   (1) cached C is ALREADY centered (colmean ~1e-16) -> do NOT re-center
#   (2) frozen metric is FR@3 = |gold n top3| / |gold|  (fractional recall), not ALL@3
# Tie handling: frozen code uses NT=20 seeded random tie-break permutations.
# E[FR] under uniform random tie-breaking is exact and order-independent:
#   E[FR] = (g_strict + g_tied * slots / bc) / |gold|
import pickle, glob, json, os
import numpy as np

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work"
K = 3
out = {}


def efr(score_desc, gold, K=3):
    """Expected FR@K under uniform random tie-breaking. score_desc: higher = better."""
    s = np.asarray(score_desc, dtype=np.float64)
    ss = np.sort(s)[::-1]
    thr = ss[K - 1]
    strictly = int((s > thr).sum())
    slots = K - strictly
    bc = int((s == thr).sum())
    g = list(gold)
    g_strict = sum(1 for x in g if s[x] > thr)
    g_tied = sum(1 for x in g if s[x] == thr)
    return (g_strict + g_tied * (slots / bc)) / len(g)


def arms_raw(C, q, gold):
    """No re-centering: cache C is already centered. Frozen: D0 = C>=0, cos on raw cached C."""
    D0 = C >= 0
    Q0 = q >= 0
    dh = (D0 != Q0[None, :]).sum(axis=1).astype(np.float64)
    dn = np.linalg.norm(C, axis=1)
    cs = (C @ q) / (dn * np.linalg.norm(q))
    return efr(-dh, gold, K), efr(cs, gold, K)


# ---------------- LongMemEval ----------------
sg = fl = 0.0
n = 0
for f in sorted(glob.glob(f"{ROOT}/regen/lme/cache_repr/*.pkl")):
    d = pickle.load(open(f, "rb"))
    C = np.asarray(d["C"], float)
    q = np.asarray(d["qC"], float)
    gold = [int(x) for x in np.atleast_1d(d["gold"])]
    if not gold:
        continue
    a, b = arms_raw(C, q, gold)
    sg += a
    fl += b
    n += 1
out["LME"] = {"n": n, "sign": sg / n, "float": fl / n, "delta_pp": 100 * (sg - fl) / n,
              "frozen_sign": 0.5419751773049645, "frozen_float": 0.4415957446808511,
              "frozen_delta_pp": 10.037943}
print("LME ", json.dumps(out["LME"], indent=1), flush=True)

# ---------------- PerLTQA ----------------
arch = pickle.load(open(f"{ROOT}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
qdat = pickle.load(open(f"{ROOT}/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
sec = {}
tn = ts = tf = 0
for qid, rec in qdat.items():
    C = np.asarray(arch[rec["char"]]["C"], float)
    q = np.asarray(rec["qC"], float)
    gold = [int(x) for x in np.atleast_1d(rec["gold"])]
    if not gold:
        continue
    a, b = arms_raw(C, q, gold)
    s = rec.get("section", "?")
    e = sec.setdefault(s, [0, 0.0, 0.0])
    e[0] += 1
    e[1] += a
    e[2] += b
    tn += 1
    ts += a
    tf += b
out["PERLTQA"] = {"n": tn, "sign": ts / tn, "float": tf / tn, "delta_pp": 100 * (ts - tf) / tn,
                  "frozen_sign": 0.488941994930817, "frozen_float": 0.551692074528853,
                  "frozen_delta_pp": -6.275,
                  "sections": {k: {"n": v[0], "sign": v[1] / v[0], "float": v[2] / v[0],
                                   "delta_pp": 100 * (v[1] - v[2]) / v[0]} for k, v in sorted(sec.items())}}
print("PERLTQA", json.dumps(out["PERLTQA"], indent=1), flush=True)

# ---------------- REALTALK ----------------
sg = fl = 0.0
n = 0
for f in sorted(glob.glob(f"{ROOT}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl")):
    d = pickle.load(open(f, "rb"))
    C = np.asarray(d["C"], float)
    QC = np.asarray(d["QC"], float)
    for i, qid in enumerate(d["qids"]):
        gold = [int(x) for x in np.atleast_1d(d["gold_rows"][i])]
        if not gold:
            continue
        a, b = arms_raw(C, QC[i], gold)
        sg += a
        fl += b
        n += 1
out["REALTALK"] = {"n": n, "sign": sg / n, "float": fl / n, "delta_pp": 100 * (sg - fl) / n,
                   "frozen_delta_pp": 5.2241}
print("REALTALK", json.dumps(out["REALTALK"], indent=1), flush=True)

json.dump(out, open(f"{ROOT}/coord_frozen_replication.json", "w"), indent=1)
print("\n=== MATCH CHECK (pp, mine - frozen) ===")
for k in ("LME", "PERLTQA", "REALTALK"):
    d = out[k]["delta_pp"] - out[k]["frozen_delta_pp"]
    print(f"  {k:9s} mine={out[k]['delta_pp']:+.6f}  frozen={out[k]['frozen_delta_pp']:+.6f}  diff={d:+.6f}")
