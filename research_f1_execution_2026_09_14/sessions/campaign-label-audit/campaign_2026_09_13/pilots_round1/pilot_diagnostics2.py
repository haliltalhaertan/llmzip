"""Pilot diagnostic 2: direct retrieval-mechanism readout per axis-set.

For TOP48 / RAND48(s0..s2) / BOT48 (and 16-bit variants) computes per question:
  - gold_rank_mean : mean position (0-based) of the gold doc in the lexsort ranking over 20 trials
  - d_gold         : mean Hamming distance query->gold
  - d_min_nongold  : mean of min Hamming distance among non-gold docs
  - crowding       : mean #non-gold docs with distance <= d_gold  (competition density)
  - lat           : mean gold distance percentile among all docs (0 = closest)
LOCAL EXPLORATORY PILOT — NOT PREREGISTERED — NOT FOR CITATION.
"""
import json
import pickle
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
PIL = WORK / "pilots" / "axis_attack_2026-09-12"
PKL_DIR = WORK / "regen" / "lme" / "cache_repr"
K = 3
NT = 20


def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100


def lex_map():
    data = json.loads((WORK / "drive" / "longmemeval_s_cleaned.json").read_text())
    allq = sorted(str(x["question_id"]) for x in data)
    return {q: i for i, q in enumerate(allq)}


def main():
    lex = lex_map()
    sets = [(f"TOP{k}", "desc", k, None) for k in (16, 48)]
    sets += [(f"BOT{k}", "asc", k, None) for k in (16, 48)]
    sets += [(f"RAND{k}_s{s}", "rand", k, s) for k in (16, 48) for s in range(3)]
    acc = {name: {kk: [] for kk in ("gold_rank", "d_gold", "d_min_ng", "crowd", "pct")} for name, *_ in sets}

    pkls = sorted(PKL_DIR.glob("*.pkl"))
    for qi, p in enumerate(pkls):
        with open(p, "rb") as f:
            o = pickle.loads(f.read())
        qid = o["question_id"]; C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
        n = len(C)
        D0 = C >= 0; Q0 = qC >= 0
        var = C.var(axis=0)
        gm = np.zeros(n, dtype=bool); gm[g] = True
        pr = [np.random.default_rng(stable_archive_seed(lex[qid], t) + 99).random(n) for t in range(NT)]
        for name, mode, k, s in sets:
            if mode == "desc":
                idx = np.argsort(var, kind="stable")[::-1][:k]
            elif mode == "asc":
                idx = np.argsort(var, kind="stable")[:k]
            else:
                idx = np.random.default_rng(12000 + s).choice(96, k, replace=False)
            d = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1)
            ranks = []
            for pz in pr:
                order = np.lexsort((pz, d))
                r = np.where(gm[order])[0]
                ranks.append(r.min())
            a = acc[name]
            a["gold_rank"].append(float(np.mean(ranks)))
            a["d_gold"].append(float(d[gm].mean()))
            a["d_min_ng"].append(float(d[~gm].min()))
            a["crowd"].append(float(np.mean([np.sum(d[~gm] <= d[gt]) for gt in g])))
            a["pct"].append(float(np.mean(d[~gm] < d[gm].mean()) if False else np.mean((d < d[gm].mean()).astype(float))))
        if (qi + 1) % 100 == 0:
            print(f"  {qi+1}/470", flush=True)

    out = {name: {kk: float(np.mean(vv)) for kk, vv in a.items()} for name, a in acc.items()}
    (PIL / "diagnostics2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
