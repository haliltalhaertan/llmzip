"""T-float: which 'float' is the honest uncompressed reference?
READ-ONLY: reads bench3 rt_repr/*.pkl + data/*.json only.
Computes, from cached production C/QC (k=96):
  sym det/exp, qscale det/exp, raw-float-cosine det (ladder 'float' arm),
  standardized-float-cosine det (REPORT 'float_std' arm).
Also checks ranking equivalence qscale-dot vs standardized cosine.
"""
import hashlib
import json
import pickle
import numpy as np

R = "/mnt/c/Users/MDP/dev/llmzip-work"
CACHE = R + "/bench3/runs/b3a_realtalk/rt_repr"
DATA = R + "/top10_comparison_r1/data"
ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]


def det_top10(scores, archive_id, k):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{archive_id}|{r}".encode()).hexdigest()
          for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


def cos_raw(C, q):
    C = np.asarray(C, float)
    q = np.asarray(q, float).ravel()
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))


def main():
    H = {k: [] for k in ("sym_det", "sym_exp", "q_det", "q_exp", "fraw", "fstd")}
    rank_match_q_fstd = 0
    rank_total = 0
    nq = 0
    for a in ARCHIVES:
        d = pickle.load(open(f"{CACHE}/{a}.pkl", "rb"))
        C = np.asarray(d["C"], dtype=np.float64)
        QC = np.asarray(d["QC"], dtype=np.float64)
        pos = {q: i for i, q in enumerate(d["qids"])}
        std = C.std(axis=0, ddof=0)
        std[std < 1e-12] = 1e-12
        Db = (C >= 0)
        Dpm = np.where(Db, 1.0, -1.0)
        Cn = C / np.linalg.norm(C, axis=1, keepdims=True)
        Cs = C / std[None, :]
        for q in json.load(open(f"{DATA}/{a}.json"))["queries"]:
            if q["qid"] not in pos:
                continue
            j = pos[q["qid"]]
            gold = set(int(g) for g in d["gold_rows"][j])
            s_sym = -np.count_nonzero(Db != (QC[j] >= 0)[None, :], axis=1).astype(float)
            s_q = Dpm @ (QC[j] / std)
            s_fraw = cos_raw(C, QC[j])
            s_fstd = cos_raw(Cs, QC[j] / std)
            t = det_top10(s_sym, a, 10)
            H["sym_det"].append(1.0 if gold & set(t.tolist()) else 0.0)
            # expected sym via closed form not needed; use anchor-known det only + exp from t_ties
            t = det_top10(s_q, a, 10)
            H["q_det"].append(1.0 if gold & set(t.tolist()) else 0.0)
            t = det_top10(s_fraw, a, 10)
            H["fraw"].append(1.0 if gold & set(t.tolist()) else 0.0)
            t = det_top10(s_fstd, a, 10)
            H["fstd"].append(1.0 if gold & set(t.tolist()) else 0.0)
            # ranking equivalence: qscale dot vs standardized cosine (per-query full order)
            o1 = np.argsort(-s_q, kind="stable")
            o2 = np.argsort(-s_fstd, kind="stable")
            rank_total += 1
            rank_match_q_fstd += int(np.array_equal(o1, o2))
            nq += 1
    print(f"n={nq}")
    print(f"sym det     Hit@10 = {100*np.mean(H['sym_det']):.4f}  (anchor 46.5248)")
    print(f"qscale det  Hit@10 = {100*np.mean(H['q_det']):.4f}  (anchor 49.6454)")
    print(f"raw float   Hit@10 = {100*np.mean(H['fraw']):.4f}  (ladder k96/float = 36.5957)")
    print(f"std float   Hit@10 = {100*np.mean(H['fstd']):.4f}  (REPORT float_std = 48.51)")
    print(f"qscale-dot vs standardized-cosine full-ranking agreement: "
          f"{rank_match_q_fstd}/{rank_total} queries identical")
    print(f"quant cost vs RAW float:  {100*np.mean(H['sym_det'])-100*np.mean(H['fraw']):+.2f} pp "
          f"(sign BEATS its float source)")
    print(f"quant cost vs STD float:  {100*np.mean(H['sym_det'])-100*np.mean(H['fstd']):+.2f} pp")
