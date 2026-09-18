#!/usr/bin/env python3
"""W3: brute-force Monte-Carlo check of hit_expected.
W4: what actually causes faiss to score higher.
"""
import glob
import json
import os

import faiss
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "faissdeep")
K = 10
OUT = {}


def hit_expected_claimed(dist, gs, k=K):
    order = np.sort(dist)
    if len(dist) <= k:
        return 1.0 if gs else 0.0
    dk = order[k - 1]
    inside = np.nonzero(dist < dk)[0]
    if any(int(i) in gs for i in inside):
        return 1.0
    bucket = np.nonzero(dist == dk)[0]
    gb = sum(1 for i in bucket if int(i) in gs)
    slots = k - len(inside)
    b = len(bucket)
    if gb == 0:
        return 0.0
    if slots > b - gb:
        return 1.0
    num = den = 1.0
    for i in range(slots):
        num *= (b - gb - i)
        den *= (b - i)
    return 1.0 - num / den


def brute_force_hit(dist, gs, rng, M, k=K):
    """Full simulation of the frozen convention: shuffle EVERYTHING, stable
    sort by distance, take top-k, check gold. No tie-bucket shortcut."""
    n = len(dist)
    isg = np.zeros(n, dtype=bool)
    isg[list(gs)] = True
    perm = np.argsort(rng.random((M, n)), axis=1)          # random order
    dp = dist[perm]
    order = np.argsort(dp, axis=1, kind="stable")           # stable -> ties keep random order
    topk = np.take_along_axis(perm, order[:, :k], axis=1)
    return float(isg[topk].any(axis=1).mean())


def tags():
    for f in sorted(glob.glob(os.path.join(DATA, "*.npz"))):
        if f.endswith("_float.npz"):
            continue
        t = os.path.basename(f)[:-4]
        b = "lme" if t.startswith("lme") else (
            "perltqa" if t.startswith("pq") else "realtalk")
        yield t, f, b


def main():
    rng = np.random.default_rng(777)
    M = 4000

    mc_rows = []            # (claimed, mc)
    # W4 accumulators over queries where the conventions differ
    diff_hf, diff_hx, diff_bench, diff_tag = [], [], [], []
    lowest_is_gold, lowest_expect = [], []
    minrank_obs, minrank_exp_cdf = [], []
    gb_list, b_list, slots_list = [], [], []
    # does faiss pick low indices AND are golds at low index *conditional on
    # being in the bucket*?  measure exact rank of each gold inside bucket
    gold_ranks_norm = []
    # competing hypothesis: duplicate codes / block structure
    gold_contiguity = []

    for tag, f, bench in tags():
        z = np.load(f, allow_pickle=True)
        docs, qs, ref = z["docs"], z["queries"], z["refdist"].astype(np.int64)
        golds = z["gold"]
        n, nq = docs.shape[0], qs.shape[0]
        idx = faiss.IndexBinaryFlat(96)
        idx.add(docs)
        D, I = idx.search(qs, K)
        for j in range(nq):
            d = ref[j]
            g = np.asarray(golds[j]).ravel().astype(int)
            gs = set(int(x) for x in g)
            hf = hit_expected_claimed(d, gs)
            hx = 1.0 if (set(int(i) for i in I[j]) & gs) else 0.0
            if abs(hf - hx) < 1e-9:
                continue
            # ---- these are exactly the queries where tie-breaking decides
            diff_hf.append(hf)
            diff_hx.append(hx)
            diff_bench.append(bench)
            diff_tag.append(tag)
            dk = np.sort(d)[K - 1]
            n_lt = int(np.count_nonzero(d < dk))
            bucket = np.nonzero(d == dk)[0]
            slots = K - n_lt
            b = len(bucket)
            isg = np.array([int(i) in gs for i in bucket])
            gb = int(isg.sum())
            gb_list.append(gb)
            b_list.append(b)
            slots_list.append(slots)
            lowest_is_gold.append(float(isg[0]))
            lowest_expect.append(gb / b)
            r = np.nonzero(isg)[0]
            gold_ranks_norm.extend((r / (b - 1)).tolist() if b > 1 else [])
            minrank_obs.append(int(r.min()))
            # P(min gold rank <= observed) under uniform  (for KS-ish check)
            # gold contiguity: are gold doc indices a near-contiguous block?
            if len(g) > 1:
                gold_contiguity.append(
                    float((g.max() - g.min() + 1) / len(g)))
            # MC on a subset
            if len(mc_rows) < 400:
                mc = brute_force_hit(d, gs, rng, M)
                mc_rows.append((hf, mc, b, gb, slots))

    # ---------------- W3 verdict
    a = np.array([r[0] for r in mc_rows])
    m = np.array([r[1] for r in mc_rows])
    se = np.sqrt(a * (1 - a) / M)
    z = (m - a) / np.where(se > 0, se, 1)
    OUT["W3_monte_carlo"] = {
        "cases": len(a), "sims_per_case": M,
        "all_cases_have_straddling_tie_and_gold_in_bucket": True,
        "mean_claimed": float(a.mean()), "mean_montecarlo": float(m.mean()),
        "mean_abs_error": float(np.abs(m - a).mean()),
        "max_abs_error": float(np.abs(m - a).max()),
        "mean_z": float(z.mean()), "max_abs_z": float(np.abs(z).max()),
        "cases_with_abs_z_gt_4": int((np.abs(z) > 4).sum()),
        "expected_cases_gt_4_by_chance": float(len(a) * 6.3e-5),
    }

    # ---------------- W4 verdict
    hf = np.asarray(diff_hf)
    hx = np.asarray(diff_hx)
    bn = np.asarray(diff_bench)
    tg = np.asarray(diff_tag)
    obs = hx.sum()
    exp = hf.sum()
    var = (hf * (1 - hf)).sum()
    OUT["W4_why_faiss_wins"] = {
        "queries_where_tiebreak_decides": len(hf),
        "expected_hits_if_tiebreak_uniform": float(exp),
        "observed_hits_with_faiss_ascending_index": float(obs),
        "excess_hits": float(obs - exp),
        "z_vs_uniform_null": float((obs - exp) / np.sqrt(var)),
        "delta_pp_on_9020": float((obs - exp) / 9020 * 100),
        "positional_hypothesis": {
            "P_lowest_index_bucket_member_is_gold_observed":
                float(np.mean(lowest_is_gold)),
            "P_expected_if_gold_position_random":
                float(np.mean(lowest_expect)),
            "gold_rank_within_bucket_normalised_mean":
                float(np.mean(gold_ranks_norm)),
            "uniform_expectation": 0.5,
            "mean_min_gold_rank_observed": float(np.mean(minrank_obs)),
        },
        "structure": {
            "bucket_size_mean": float(np.mean(b_list)),
            "slots_mean": float(np.mean(slots_list)),
            "gold_in_bucket_mean": float(np.mean(gb_list)),
            "gold_contiguity_span_over_count_mean":
                float(np.mean(gold_contiguity)) if gold_contiguity else None,
        },
        "per_bench": {},
        "per_archive_excess_top5": {},
    }
    for b in ["lme", "perltqa", "realtalk"]:
        mk = bn == b
        if mk.sum() == 0:
            continue
        o, e = hx[mk].sum(), hf[mk].sum()
        v = (hf[mk] * (1 - hf[mk])).sum()
        OUT["W4_why_faiss_wins"]["per_bench"][b] = {
            "n": int(mk.sum()), "obs": float(o), "exp": float(e),
            "z": float((o - e) / np.sqrt(v)) if v > 0 else None}
    exc = {}
    for t in np.unique(tg):
        mk = tg == t
        exc[t] = float(hx[mk].sum() - hf[mk].sum())
    top = sorted(exc.items(), key=lambda kv: -abs(kv[1]))[:8]
    OUT["W4_why_faiss_wins"]["per_archive_excess_top5"] = dict(top)
    OUT["W4_why_faiss_wins"]["archives_with_positive_excess"] = int(
        sum(1 for v in exc.values() if v > 0))
    OUT["W4_why_faiss_wins"]["archives_with_negative_excess"] = int(
        sum(1 for v in exc.values() if v < 0))

    print(json.dumps(OUT, indent=2))
    with open(os.path.join(HERE, "AUDIT_W3_W4.json"), "w") as fh:
        json.dump(OUT, fh, indent=2)


if __name__ == "__main__":
    main()
