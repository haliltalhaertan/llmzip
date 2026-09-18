"""T-ties: quantify hash tie-break luck + det-vs-expected gap on cached RealTalk codes.
READ-ONLY on source trees: only reads bench3 rt_repr/*.pkl + data/*.json.
Reimplements scoring inline (sym Hamming, qscale dot) with numpy+hashlib only.
"""
import hashlib
import json
import pickle
import numpy as np

R = "/mnt/c/Users/MDP/dev/llmzip-work"
CACHE = R + "/bench3/runs/b3a_realtalk/rt_repr"
DATA = R + "/top10_comparison_r1/data"
ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]


def det_top10(scores, archive_id, k, salt="top10-r1"):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{salt}|{archive_id}|{r}".encode()).hexdigest()
          for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


def expected_hit(scores, gold, k=10):
    import math
    s = np.asarray(scores, dtype=np.float64).ravel()
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    uniq = np.unique(s)[::-1]
    better = 0
    for lv in uniq:
        idx = np.nonzero(s == lv)[0]
        Bb = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + Bb <= k:
            if gb > 0:
                return 1.0
            better += Bb
        else:
            take = int(k - better)
            if gb == 0:
                return 0.0
            return float(1.0 - (math.comb(Bb - gb, take) if (Bb - gb) >= take else 0)
                         / math.comb(Bb, take))
    return 0.0


def expected_recall(scores, gold, k=3):
    s = np.asarray(scores, dtype=np.float64).ravel()
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    uniq = np.unique(s)[::-1]
    better, exp = 0, 0.0
    for lv in uniq:
        idx = np.nonzero(s == lv)[0]
        Bb = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + Bb <= k:
            exp += gb
        else:
            exp += (k - better) * gb / Bb
            break
        better += Bb
    return float(exp / len(gset))


def main():
    det_hits, exp_hits, det_fr3, exp_fr3 = [], [], [], []
    tie_at_cut_10, tie_at_cut_3 = 0, 0
    nq = 0
    salt_spread_num = []  # per-query det hit under alternate salts
    n_levels_dist = []
    for a in ARCHIVES:
        d = pickle.load(open(f"{CACHE}/{a}.pkl", "rb"))
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        pos = {q: i for i, q in enumerate(d["qids"])}
        Db = (C >= 0)
        for q in json.load(open(f"{DATA}/{a}.json"))["queries"]:
            if q["qid"] not in pos:
                continue
            j = pos[q["qid"]]
            gold = [int(g) for g in d["gold_rows"][pos[q["qid"]]]]
            s_sym = -np.count_nonzero(Db != (QC[j] >= 0)[None, :], axis=1).astype(float)
            n_levels_dist.append(len(np.unique(s_sym)))
            top10 = det_top10(s_sym, a, 10)
            det_hits.append(1.0 if (set(gold) & set(top10.tolist())) else 0.0)
            exp_hits.append(expected_hit(s_sym, gold, 10))
            det_fr3.append(len(set(gold) & set(top10[:3].tolist())) / len(gold))
            exp_fr3.append(expected_recall(s_sym, gold, 3))
            # tie at cut?
            sm = np.where(np.isfinite(s_sym), s_sym, -np.inf)
            uniq = np.unique(sm)[::-1]
            better = 0
            for lv in uniq:
                B = int(np.sum(sm == lv))
                if better >= 10:
                    break
                if better + B <= 10:
                    better += B
                else:
                    tie_at_cut_10 += 1 if B > 1 else 0
                    break
            better = 0
            for lv in uniq:
                B = int(np.sum(sm == lv))
                if better >= 3:
                    break
                if better + B <= 3:
                    better += B
                else:
                    tie_at_cut_3 += 1 if B > 1 else 0
                    break
            # alternate-salt draws for this query
            draws = []
            for salt in ("top10-r1", "salt-A", "salt-B", "salt-C", "salt-D"):
                t = det_top10(s_sym, a, 10, salt=salt)
                draws.append(1.0 if (set(gold) & set(t.tolist())) else 0.0)
            salt_spread_num.append(draws)
            nq += 1
    det_hits = np.array(det_hits)
    exp_hits = np.array(exp_hits)
    draws = np.array(salt_spread_num)
    print(f"n_queries={nq}")
    print(f"sym det Hit@10 (salt top10-r1) = {100*det_hits.mean():.4f}")
    print(f"sym exp Hit@10 (tie-averaged)  = {100*exp_hits.mean():.4f}")
    print(f"det - exp gap = {100*(det_hits-exp_hits).mean():+.4f} pp")
    print(f"sym det FR@3  = {100*np.mean(det_fr3):.4f}")
    print(f"sym exp FR@3  = {100*np.mean(exp_fr3):.4f}")
    print(f"queries with tie AT the top-10 cut = {tie_at_cut_10}/{nq} "
          f"({100*tie_at_cut_10/nq:.1f}%)")
    print(f"queries with tie AT the top-3 cut  = {tie_at_cut_3}/{nq} "
          f"({100*tie_at_cut_3/nq:.1f}%)")
    print(f"distinct sym score levels per query: min={min(n_levels_dist)}, "
          f"median={float(np.median(n_levels_dist)):.0f}, max={max(n_levels_dist)}")
    for i, salt in enumerate(("top10-r1", "salt-A", "salt-B", "salt-C", "salt-D")):
        print(f"  salt {salt:9s} Hit@10 = {100*draws[:, i].mean():.4f}")
    print(f"  salt-luck spread (max-min over 5 salts) = "
          f"{100*(draws.mean(axis=0).max()-draws.mean(axis=0).min()):.4f} pp")
    print(f"  per-query disagreement: queries where 5 salts disagree = "
          f"{int(((draws.max(axis=1)-draws.min(axis=1)) > 0).sum())}/{nq}")
    # qscale tie check (continuous scores -> ties rare?)
    q_ties = 0
    for a in ARCHIVES:
        d = pickle.load(open(f"{CACHE}/{a}.pkl", "rb"))
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        sig = C.std(axis=0, ddof=0)
        sig[sig < 1e-12] = 1e-12
        Dpm = np.where(C >= 0, 1.0, -1.0)
        pos = {q: i for i, q in enumerate(d["qids"])}
        for q in json.load(open(f"{DATA}/{a}.json"))["queries"]:
            if q["qid"] not in pos:
                continue
            s_q = Dpm @ (QC[pos[q["qid"]]] / sig)
            if len(np.unique(s_q)) < len(s_q):
                q_ties += 1
    print(f"qscale queries with ANY tied doc pair = {q_ties}/{nq}")


if __name__ == "__main__":
    main()
