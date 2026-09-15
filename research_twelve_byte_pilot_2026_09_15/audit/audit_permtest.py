#!/usr/bin/env python3
"""Decisive test for W4 / C3: is the +0.41pp an artifact of DOCUMENT ORDER?

Permute document indices within each archive (identical codes, identical
distances, identical gold set -- only the storage order changes), rebuild the
faiss index, recompute the hit10 delta.  Under the null that document order
carries no information, the delta must average 0.
"""
import glob
import json
import os

import faiss
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "faissdeep")
K = 10


def hit_expected(dist, gs, k=K):
    order = np.sort(dist)
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


def load():
    arr = []
    for f in sorted(glob.glob(os.path.join(DATA, "*.npz"))):
        if f.endswith("_float.npz"):
            continue
        t = os.path.basename(f)[:-4]
        z = np.load(f, allow_pickle=True)
        arr.append((t, z["docs"], z["queries"], z["refdist"].astype(np.int64),
                    z["gold"]))
    return arr


def evaluate(archives, perms=None):
    """Returns (delta_pp, n_decisive, p_lowest_is_gold, p_lowest_expected)."""
    hf_s = hx_s = 0.0
    nq_tot = 0
    ndec = 0
    low_obs = []
    low_exp = []
    for ai, (t, docs, qs, ref, golds) in enumerate(archives):
        n, nq = docs.shape[0], qs.shape[0]
        if perms is None:
            p = np.arange(n)
        else:
            p = perms[ai]
        # p[new_position] = old_index
        docs_p = np.ascontiguousarray(docs[p])
        inv = np.empty(n, dtype=np.int64)
        inv[p] = np.arange(n)            # inv[old_index] = new_position
        idx = faiss.IndexBinaryFlat(96)
        idx.add(docs_p)
        _, I = idx.search(qs, K)
        for j in range(nq):
            d_old = ref[j]
            d_new = d_old[p]             # distances in permuted order
            g_old = set(int(x) for x in np.asarray(golds[j]).ravel())
            g_new = set(int(inv[x]) for x in g_old)
            hf = hit_expected(d_new, g_new)
            hx = 1.0 if (set(int(i) for i in I[j]) & g_new) else 0.0
            hf_s += hf
            hx_s += hx
            nq_tot += 1
            if abs(hf - hx) > 1e-9:
                ndec += 1
                dk = np.sort(d_new)[K - 1]
                bucket = np.nonzero(d_new == dk)[0]
                isg = np.array([int(i) in g_new for i in bucket])
                low_obs.append(float(isg[0]))
                low_exp.append(isg.sum() / len(bucket))
    return ((hx_s - hf_s) / nq_tot * 100, ndec,
            float(np.mean(low_obs)), float(np.mean(low_exp)))


def main():
    archives = load()
    real = evaluate(archives, None)
    rng = np.random.default_rng(31337)
    B = 60
    deltas, ndecs, lobs, lexp = [], [], [], []
    for b in range(B):
        perms = [rng.permutation(a[1].shape[0]) for a in archives]
        dpp, nd, lo, le = evaluate(archives, perms)
        deltas.append(dpp)
        ndecs.append(nd)
        lobs.append(lo)
        lexp.append(le)
    dl = np.asarray(deltas)
    out = {
        "real_document_order": {
            "delta_pp": real[0], "n_decisive_queries": real[1],
            "P_lowest_bucket_member_is_gold": real[2],
            "P_expected_gb_over_b": real[3]},
        "permuted_document_order": {
            "n_permutations": B,
            "delta_pp_mean": float(dl.mean()),
            "delta_pp_sd": float(dl.std(ddof=1)),
            "delta_pp_p2.5": float(np.percentile(dl, 2.5)),
            "delta_pp_p97.5": float(np.percentile(dl, 97.5)),
            "delta_pp_min": float(dl.min()), "delta_pp_max": float(dl.max()),
            "n_decisive_mean": float(np.mean(ndecs)),
            "P_lowest_is_gold_mean": float(np.mean(lobs)),
            "P_expected_gb_over_b_mean": float(np.mean(lexp))},
        "permutation_p_value_two_sided": float(
            (np.abs(dl) >= abs(real[0])).mean()),
        "z_of_real_vs_permutation_null": float(
            (real[0] - dl.mean()) / dl.std(ddof=1)),
    }
    print(json.dumps(out, indent=2))
    with open(os.path.join(HERE, "AUDIT_PERMTEST.json"), "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
