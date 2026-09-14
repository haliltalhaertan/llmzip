"""Pilot probe: per-question FR for TOP48/RAND48/BOT48 + tie-free variant + W/T/L.
LOCAL EXPLORATORY PILOT — NOT PREREGISTERED — NOT FOR CITATION.
"""
import json
import pickle
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
PIL = WORK / "pilots" / "axis_attack_2026-09-12"
PKL_DIR = WORK / "regen" / "lme" / "cache_repr"
K, NT = 3, 20


def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100


def met(idx, g):
    s = set(map(int, idx)); gg = set(map(int, g)); x = len(s & gg)
    return float(x > 0), float(x == len(gg) and len(gg) > 0), float(x / len(gg))


def main():
    data = json.loads((WORK / "drive" / "longmemeval_s_cleaned.json").read_text())
    lex = {q: i for i, q in enumerate(sorted(str(x["question_id"]) for x in data))}
    del data

    sets = {"TOP48": ("desc", 48, None), "RAND48_s0": ("rand", 48, 0),
            "RAND48_s1": ("rand", 48, 1), "RAND48_s2": ("rand", 48, 2),
            "BOT48": ("asc", 48, None), "TOP16": ("desc", 16, None)}
    per_q = {n: {} for n in sets}
    per_q_strict = {n: {} for n in sets}
    dup = {n: {} for n in sets}

    pkls = sorted(PKL_DIR.glob("*.pkl"))
    for qi, p in enumerate(pkls):
        with open(p, "rb") as f:
            o = pickle.loads(f.read())
        qid = o["question_id"]; C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
        n = len(C); D0 = C >= 0; Q0 = qC >= 0
        var = C.var(axis=0)
        pr = [np.random.default_rng(stable_archive_seed(lex[qid], t) + 99).random(n) for t in range(NT)]
        for name, (mode, k, s) in sets.items():
            if mode == "desc":
                idx = np.argsort(var, kind="stable")[::-1][:k]
            elif mode == "asc":
                idx = np.argsort(var, kind="stable")[:k]
            else:
                idx = np.random.default_rng(12000 + s).choice(96, k, replace=False)
            d = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1)
            per_q[name][qid] = float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr]))
            idxs = np.arange(n)
            per_q_strict[name][qid] = float(met(np.lexsort((idxs, d))[:K], g)[2])
            pk = np.packbits(D0[:, idx], axis=1, bitorder="big")
            _, cnt = np.unique(pk, axis=0, return_counts=True)
            dup[name][qid] = float(cnt.max())   # largest collision bucket
        if (qi + 1) % 100 == 0:
            print(f"  {qi+1}/470", flush=True)

    out = {}
    for name in sets:
        a = np.array(list(per_q[name].values())); b = np.array(list(per_q_strict[name].values()))
        out[name] = {"FR_mean": float(a.mean()), "FR_strict_mean": float(b.mean()),
                     "dup_bucket_mean": float(np.mean(list(dup[name].values())))}
    # paired gaps vs native-like RAND48 mean per question
    grand = {qid: np.mean([per_q[f"RAND48_s{s}"][qid] for s in range(3)]) for qid in per_q["RAND48_s0"]}
    for name in ["TOP48", "BOT48", "TOP16"]:
        g = np.array([per_q[name][q] - grand[q] for q in grand])
        w = int((g > 1e-12).sum()); l = int((g < -1e-12).sum()); t = int((np.abs(g) <= 1e-12).sum())
        out[name]["vs_RAND48mean_W_T_L"] = [w, t, l]
        out[name]["vs_RAND48mean_median_gap"] = float(np.median(g))
        out[name]["vs_RAND48mean_q25_q75"] = [float(np.percentile(g, 25)), float(np.percentile(g, 75))]
        out[name]["vs_RAND48mean_min"] = float(g.min())
        # correlation of gap with the set's own collision bucket
        dd = np.array([dup[name][q] for q in grand]); gg = np.array([dup["RAND48_s0"][q] for q in grand])
        out[name]["corr_gap_vs_bucket_excess"] = float(np.corrcoef(g, dd - gg)[0, 1])
    (PIL / "probe48.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
