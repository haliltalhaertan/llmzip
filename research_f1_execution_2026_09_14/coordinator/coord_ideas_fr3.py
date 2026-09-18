#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Re-test of relayed ideas 1 (scale) and 6 (AQS) under the CORRECT frozen metric (FR@3, no re-centering).
# Supersedes coord_eval_ideas.py, which used ALL@3.
import pickle, glob, json
import numpy as np

ROOT = "/mnt/c/Users/MDP/dev/llmzip-work"
K = 3
rng = np.random.default_rng(20260914)


def efr(score_desc, gold, K=3):
    s = np.asarray(score_desc, float)
    ss = np.sort(s)[::-1]
    thr = ss[K - 1]
    strictly = int((s > thr).sum())
    slots = K - strictly
    bc = int((s == thr).sum())
    g_strict = sum(1 for x in gold if s[x] > thr)
    g_tied = sum(1 for x in gold if s[x] == thr)
    return (g_strict + g_tied * (slots / bc)) / len(gold), (bc > slots), bc


def three_arms(C, q, gold):
    """C already centered. sign=Hamming, float=cosine, aqs = sign_codes . continuous query."""
    D0 = C >= 0
    Q0 = q >= 0
    dh = (D0 != Q0[None, :]).sum(axis=1).astype(float)
    cs = (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))
    aqs = np.where(D0, 1.0, -1.0) @ q
    s, tie_s, bc_s = efr(-dh, gold, K)
    f, _, _ = efr(cs, gold, K)
    a, tie_a, _ = efr(aqs, gold, K)
    return s, f, a, tie_s, tie_a


arcs = []
for f in sorted(glob.glob(f"{ROOT}/regen/lme/cache_repr/*.pkl")):
    d = pickle.load(open(f, "rb"))
    g = [int(x) for x in np.atleast_1d(d["gold"])]
    if g:
        arcs.append((np.asarray(d["C"], float), np.asarray(d["qC"], float), g))
print(f"archives={len(arcs)}", flush=True)

# ---- native scale ----
S = np.array([three_arms(C, q, g) for C, q, g in arcs], dtype=float)
native = {"n": len(S), "sign": S[:, 0].mean(), "float": S[:, 1].mean(), "aqs": S[:, 2].mean(),
          "delta_sign_float_pp": 100 * (S[:, 0].mean() - S[:, 1].mean()),
          "delta_aqs_sign_pp": 100 * (S[:, 2].mean() - S[:, 0].mean()),
          "tie_rate_hamming": S[:, 3].mean(), "tie_rate_aqs": S[:, 4].mean()}
print("NATIVE(FR@3):", json.dumps(native, indent=1), flush=True)

# ---- scale probe: pool independent archives ----
scale = []
for kp in [1, 2, 4, 10, 20, 50]:
    nq = 120 if kp <= 20 else 60
    acc = np.zeros(5)
    Nsum = 0
    for p in rng.choice(len(arcs), size=nq, replace=False):
        C0, q, g0 = arcs[p]
        others = [j for j in rng.choice(len(arcs), size=kp * 3, replace=False) if j != p][: kp - 1]
        C = np.vstack([C0] + [arcs[j][0] for j in others])
        acc += np.array(three_arms(C, q, list(g0)), dtype=float)
        Nsum += C.shape[0]
    r = acc / nq
    scale.append({"pool": kp, "N_mean": Nsum / nq, "sign": r[0], "float": r[1], "aqs": r[2],
                  "delta_sign_float_pp": 100 * (r[0] - r[1]),
                  "delta_aqs_sign_pp": 100 * (r[2] - r[0]),
                  "tie_rate_hamming": r[3]})
    print("SCALE:", json.dumps(scale[-1]), flush=True)

json.dump({"native": native, "scale": scale},
          open(f"{ROOT}/coord_ideas_fr3.json", "w"), indent=1)
print("\nWROTE coord_ideas_fr3.json")
