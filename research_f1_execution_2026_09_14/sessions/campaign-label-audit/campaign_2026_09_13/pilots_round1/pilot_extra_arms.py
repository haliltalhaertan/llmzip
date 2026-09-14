"""Pilot extra arms: extend the budget curve with spread strategies.
LOCAL EXPLORATORY PILOT — NOT PREREGISTERED — NOT FOR CITATION.
Arms (all gold-free, per-question where 'rank'/'idx' stride):
  RAND{k}_s{s}   : fixed random subsets (seeds 12000+s)
  RANKSTRIDE{k}  : every 2nd/3rd/4th variance-RANK (uniform spread across the spectrum)
  IDXSTRIDE{k}   : every 2nd axis index (0,2,4,...)
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

    arms = {}
    for k in (24, 32, 64, 80, 88):
        arms[f"RAND{k}_s0"] = ("rand", k, 0)
    for k, st in ((48, 2), (32, 3), (24, 4)):
        arms[f"RANKSTRIDE{k}"] = ("rstride", k, st)
    for k, st in ((48, 2), (64, 2)):
        arms[f"IDXSTRIDE{k}"] = ("istride", k, st)

    acc = {a: [] for a in arms}
    pkls = sorted(PKL_DIR.glob("*.pkl"))
    for qi, p in enumerate(pkls):
        with open(p, "rb") as f:
            o = pickle.loads(f.read())
        qid = o["question_id"]; C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
        n = len(C); D0 = C >= 0; Q0 = qC >= 0
        var = C.var(axis=0)
        rank_desc = np.argsort(var, kind="stable")[::-1]
        pr = [np.random.default_rng(stable_archive_seed(lex[qid], t) + 99).random(n) for t in range(NT)]
        for name, (mode, k, s) in arms.items():
            if mode == "rand":
                idx = np.random.default_rng(12000 + s).choice(96, k, replace=False)
            elif mode == "rstride":
                idx = rank_desc[::s][:k]
            else:
                idx = np.arange(96)[::s][:k]
            d = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1)
            acc[name].append(float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr])))
        if (qi + 1) % 100 == 0:
            print(f"  {qi+1}/470", flush=True)

    out = {a: float(np.mean(v)) for a, v in acc.items()}
    (PIL / "extra_arms.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
