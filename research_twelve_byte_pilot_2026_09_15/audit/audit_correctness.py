#!/usr/bin/env python3
"""INDEPENDENT AUDIT - correctness, ties, hit_expected, positional bias.

Re-derived from bytes. Does not import any run_*.py.
Run with venv_faiss python.
"""
import glob
import json
import math
import os

import faiss
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "faissdeep")
K = 10
OUT = {}


# ---------------------------------------------------------------- utilities
def popcount_ref(docs_u8, q_u8):
    """Independent Hamming: unpack to bits, XOR, count. Deliberately naive."""
    db = np.unpackbits(docs_u8, axis=1)            # (N,96)
    qb = np.unpackbits(q_u8.reshape(1, -1), axis=1)  # (1,96)
    return np.count_nonzero(db != qb, axis=1).astype(np.int64)


def hit_expected_claimed(dist, gold, k=K):
    """VERBATIM copy of run_faiss_deep.hit_expected (the thing under test)."""
    gs = set(int(x) for x in gold)
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


def hit_at_k_frozen(scores, gold, k=K):
    """VERBATIM port of run_hit10.hit_at_k -- the ACTUAL frozen convention.

    Operates on scores (higher=better), walks unique levels descending.
    """
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    levels = np.unique(s)[::-1]
    gset = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    assert len(gset) > 0
    better = 0
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        bsz = len(idx)
        if bsz == 0:
            continue
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + bsz <= k:
            if gb > 0:
                return 1.0
            better += bsz
        else:
            take = k - better
            if gb == 0:
                return 0.0
            if take > bsz - gb:
                return 1.0
            p_none = math.comb(bsz - gb, take) / math.comb(bsz, take)
            return 1.0 - p_none
    return 0.0


def tags():
    for f in sorted(glob.glob(os.path.join(DATA, "*.npz"))):
        if f.endswith("_float.npz"):
            continue
        t = os.path.basename(f)[:-4]
        bench = "lme" if t.startswith("lme") else (
            "perltqa" if t.startswith("pq") else "realtalk")
        yield t, f, bench


# ============================================================ MAIN PASS
def main():
    rng = np.random.default_rng(20260915)

    # accumulators
    n_arch = 0
    n_q = 0
    # C1
    faiss_vs_ref_full_mismatch = 0     # elementwise, ALL queries, ALL docs
    ref_vs_truth_mismatch = 0          # refdist vs independent popcount
    faiss_labels_wrong = 0             # returned labels' true dist != returned dist
    float_repack_archives = 0
    float_repack_bit_mismatch = 0
    float_repack_q_mismatch = 0
    # C2
    straddle = 0
    forced_claimed = []                # n_lt / K  (their metric)
    ambiguous_true = []                # slots/K when straddling else 0
    determined_frac = []               # (K - ambiguous)/K
    bucket_sizes = []
    # C3
    hf_all, hx_all, cl_all, bench_all = [], [], [], []
    hf_frozen_all = []
    differs = 0
    frozen_vs_claimed_maxdiff = 0.0
    # faiss tie-break behaviour
    tiebreak_ascending_ok = 0
    tiebreak_ascending_bad = 0
    # W4 positional bias
    pos_gold, pos_nongold = [], []      # normalised index within straddling bucket
    rank_gold_in_bucket = []            # rank of gold among bucket (0=first)
    global_gold_pos, global_gold_n = [], []
    # MC sample store
    mc_cases = []

    for tag, f, bench in tags():
        z = np.load(f, allow_pickle=True)
        docs, qs, ref = z["docs"], z["queries"], z["refdist"].astype(np.int64)
        golds = z["gold"]
        n, nq = docs.shape[0], qs.shape[0]
        n_arch += 1

        idx = faiss.IndexBinaryFlat(96)
        idx.add(docs)
        # FULL distance matrix from faiss for EVERY query (n is small)
        Dfull, Ifull = idx.search(qs, n)
        # reorder faiss full distances back into document order
        faiss_dist = np.empty((nq, n), dtype=np.int64)
        rowi = np.arange(nq)[:, None]
        faiss_dist[rowi, Ifull.astype(np.int64)] = Dfull.astype(np.int64)
        faiss_vs_ref_full_mismatch += int(np.count_nonzero(faiss_dist != ref))

        # independent ground truth popcount, every query
        for j in range(nq):
            truth = popcount_ref(docs, qs[j])
            ref_vs_truth_mismatch += int(np.count_nonzero(truth != ref[j]))

        # top-K search, the operation actually used
        D, I = idx.search(qs, K)
        for j in range(nq):
            d = ref[j]
            # labels really have the distances faiss reports
            if not np.array_equal(d[I[j].astype(np.int64)],
                                  D[j].astype(np.int64)):
                faiss_labels_wrong += 1
            # is faiss's tie-break ascending index?
            dk = np.sort(d)[K - 1]
            n_lt = int(np.count_nonzero(d < dk))
            bucket = np.nonzero(d == dk)[0]
            slots = K - n_lt
            b = len(bucket)
            bucket_sizes.append(b)
            amb = 0.0
            if b > slots:
                straddle += 1
                amb = slots / K
                chosen = np.array(sorted(
                    i for i in I[j].astype(np.int64) if d[i] == dk))
                if np.array_equal(chosen, np.sort(bucket)[:slots]):
                    tiebreak_ascending_ok += 1
                else:
                    tiebreak_ascending_bad += 1
            forced_claimed.append(min(n_lt, K) / K)
            ambiguous_true.append(amb)
            determined_frac.append(1.0 - amb)

            g = np.asarray(golds[j]).ravel().astype(int)
            gset = set(int(x) for x in g)
            hf = hit_expected_claimed(d, gset)
            hx = 1.0 if (set(int(i) for i in I[j]) & gset) else 0.0
            hfz = hit_at_k_frozen(-d.astype(np.float64), g)
            frozen_vs_claimed_maxdiff = max(frozen_vs_claimed_maxdiff,
                                            abs(hfz - hf))
            hf_all.append(hf)
            hx_all.append(hx)
            hf_frozen_all.append(hfz)
            cl_all.append(tag)
            bench_all.append(bench)
            if abs(hf - hx) > 1e-9:
                differs += 1

            # ---- W4 positional bias, straddling buckets only
            if b > slots:
                isg = np.array([int(i) in gset for i in bucket])
                if isg.any():
                    pos_gold.extend((bucket[isg] / (n - 1)).tolist())
                    ranks = np.nonzero(isg)[0] / (b - 1) if b > 1 else [0.0]
                    rank_gold_in_bucket.extend(np.atleast_1d(ranks).tolist())
                if (~isg).any():
                    pos_nongold.extend((bucket[~isg] / (n - 1)).tolist())
                # store MC case
                if isg.any() and len(mc_cases) < 4000:
                    mc_cases.append((tag, j, int(b), int(isg.sum()),
                                     int(slots), float(hf)))
            # global gold position
            global_gold_pos.extend((g / (n - 1)).tolist())
            global_gold_n.append(n)
            n_q += 1

        # ---- verify the bridge itself from the float archive (provenance)
        ff = os.path.join(DATA, tag + "_float.npz")
        if os.path.exists(ff):
            zf = np.load(ff)
            C, Qf = zf["docs"], zf["queries"]
            repack_d = np.packbits((C >= 0), axis=1,
                                   bitorder="big").astype(np.uint8)
            repack_q = np.packbits((Qf >= 0), axis=1,
                                   bitorder="big").astype(np.uint8)
            float_repack_archives += 1
            float_repack_bit_mismatch += int(np.count_nonzero(
                repack_d != docs))
            float_repack_q_mismatch += int(np.count_nonzero(repack_q != qs))

    hf = np.asarray(hf_all)
    hx = np.asarray(hx_all)
    hfz = np.asarray(hf_frozen_all)
    cl = np.asarray(cl_all)
    bn = np.asarray(bench_all)
    d = hx - hf

    # ---- naive iid CI (what run_faiss_deep.py does)
    se_iid = d.std(ddof=1) / np.sqrt(len(d))
    # ---- cluster bootstrap over the 90 archives (what run_hit10.py does)
    uq = np.unique(cl)
    by = {c: d[cl == c] for c in uq}
    keys = list(by)
    reps = np.empty(4000)
    for b in range(4000):
        pick = rng.integers(0, len(keys), len(keys))
        reps[b] = np.concatenate([by[keys[p]] for p in pick]).mean()
    ci_cluster = [float(np.percentile(reps, 2.5) * 100),
                  float(np.percentile(reps, 97.5) * 100)]

    OUT["C1_correctness"] = {
        "archives": n_arch, "queries": n_q,
        "faiss_vs_refdist_FULL_matrix_elementwise_mismatches":
            faiss_vs_ref_full_mismatch,
        "total_distance_cells_compared": int(sum(
            np.load(f, allow_pickle=True)["refdist"].size
            for _, f, _ in tags())),
        "refdist_vs_independent_popcount_mismatches": ref_vs_truth_mismatch,
        "faiss_label_distance_inconsistencies": faiss_labels_wrong,
        "bridge_provenance_float_archives_checked": float_repack_archives,
        "repacked_sign_docs_vs_bridge_byte_mismatches":
            float_repack_bit_mismatch,
        "repacked_sign_queries_vs_bridge_byte_mismatches":
            float_repack_q_mismatch,
    }
    OUT["C2_ties"] = {
        "straddle_count": straddle,
        "straddle_rate": straddle / n_q,
        "claimed_forced_fraction_median": float(np.median(forced_claimed)),
        "claimed_forced_fraction_mean": float(np.mean(forced_claimed)),
        "TRUE_determined_fraction_median": float(np.median(determined_frac)),
        "TRUE_determined_fraction_mean": float(np.mean(determined_frac)),
        "TRUE_ambiguous_slots_fraction_mean": float(np.mean(ambiguous_true)),
        "boundary_bucket_size_median": float(np.median(bucket_sizes)),
        "boundary_bucket_size_p95": float(np.percentile(bucket_sizes, 95)),
        "faiss_tiebreak_is_ascending_index_ok": tiebreak_ascending_ok,
        "faiss_tiebreak_is_ascending_index_violations":
            tiebreak_ascending_bad,
    }
    OUT["C3_hit"] = {
        "hit10_frozen_expected_pct": float(hf.mean() * 100),
        "hit10_frozen_via_run_hit10_port_pct": float(hfz.mean() * 100),
        "max_abs_diff_claimed_vs_frozen_port": frozen_vs_claimed_maxdiff,
        "hit10_faiss_pct": float(hx.mean() * 100),
        "delta_pp": float(d.mean() * 100),
        "ci95_iid_queries": [float((d.mean() - 1.96 * se_iid) * 100),
                             float((d.mean() + 1.96 * se_iid) * 100)],
        "ci95_cluster_bootstrap_90_archives": ci_cluster,
        "queries_where_conventions_differ": differs,
        "per_bench": {},
    }
    for b in ["lme", "perltqa", "realtalk"]:
        m = bn == b
        db = d[m]
        cb = cl[m]
        uk = list(np.unique(cb))
        byb = {c: db[cb == c] for c in uk}
        rb = np.empty(4000)
        for i in range(4000):
            pk = rng.integers(0, len(uk), len(uk))
            rb[i] = np.concatenate([byb[uk[p]] for p in pk]).mean()
        OUT["C3_hit"]["per_bench"][b] = {
            "queries": int(m.sum()), "archives": len(uk),
            "frozen_pct": float(hf[m].mean() * 100),
            "faiss_pct": float(hx[m].mean() * 100),
            "delta_pp": float(db.mean() * 100),
            "ci95_cluster": [float(np.percentile(rb, 2.5) * 100),
                             float(np.percentile(rb, 97.5) * 100)],
        }

    pg = np.asarray(pos_gold)
    pn = np.asarray(pos_nongold)
    rg = np.asarray(rank_gold_in_bucket)
    gg = np.asarray(global_gold_pos)
    # Mann-Whitney style: P(gold index < nongold index) via normal approx
    OUT["W4_position"] = {
        "straddling_buckets_with_gold_docs": len(rg),
        "gold_norm_index_in_bucket_mean": float(pg.mean()) if len(pg) else None,
        "nongold_norm_index_in_bucket_mean":
            float(pn.mean()) if len(pn) else None,
        "gold_minus_nongold": (float(pg.mean() - pn.mean())
                               if len(pg) and len(pn) else None),
        "gold_rank_within_bucket_mean_0is_first": float(rg.mean()),
        "expected_if_no_bias": 0.5,
        "global_gold_norm_index_mean_all_queries": float(gg.mean()),
        "mc_cases_available": len(mc_cases),
    }

    # ------------------------------------------------ store MC case list
    np.save(os.path.join(HERE, "audit_mc_cases.npy"),
            np.array([(t, j, b, g, s, h) for t, j, b, g, s, h in mc_cases],
                     dtype=object), allow_pickle=True)

    print(json.dumps(OUT, indent=2))
    with open(os.path.join(HERE, "AUDIT_CORRECTNESS.json"), "w") as fh:
        json.dump(OUT, fh, indent=2)


if __name__ == "__main__":
    main()
