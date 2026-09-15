#!/usr/bin/env python3
"""Make the 4.85 s per-archive build cheaper WITHOUT changing what it computes.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The feature matrix Z is ~500 x ~100000: very wide, very short.  Its rank is
at most N=500, so the whole factorisation lives in an N-dimensional space,
and sklearn's randomized TruncatedSVD is solving it on the 100000-wide side
and materialising a 96 x 100000 projector (76.7 MB) to transform the query.

Exact alternative (method B), same object, no approximation:

    G = Z Z^T                    (N x N, here 500 x 500)
    G = U S^2 U^T                (symmetric eigendecomposition)
    fit_transform(Z) = U S       (what TruncatedSVD returns)
    V = Z^T U S^-1               (the right singular vectors)
    Zq V = (Zq Z^T) U S^-1       <- never forms V at all

So the query transform becomes a 1 x N sparse dot plus two tiny dense
products, and the 76.7 MB projector is never built.

Component SIGNS are arbitrary in any SVD.  A per-coordinate sign flip is
applied to documents AND query alike, so Hamming distance and centered
cosine are invariant to it -- retrieval is unchanged even though the stored
bytes would differ.  This script therefore checks RETRIEVAL agreement
(scores and hit@10), not byte equality, and says so.

Usage: python run_svdopt.py [n_archives]
"""
import glob
import json
import os
import sys
import time

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
import run_ksweep as KS  # noqa: E402
import run_bottleneck as BN  # noqa: E402

SVD_RANDOM_STATE = 5101
DIM = 96


def method_A(Z, Zq):
    """Production path: sklearn randomized TruncatedSVD + explicit projector."""
    sv = TruncatedSVD(n_components=DIM, random_state=SVD_RANDOM_STATE)
    Y = normalize(sv.fit_transform(Z))
    QY = normalize(sv.transform(Zq))
    return Y, QY, int(sv.components_.nbytes)


def method_B(Z, Zq):
    """Exact Gram path: eigendecompose Z Z^T, never build the projector."""
    G = (Z @ Z.T).toarray()
    G = (G + G.T) * 0.5                       # kill asymmetry from round-off
    w, U = np.linalg.eigh(G)                  # ascending
    w = w[::-1][:DIM]
    U = U[:, ::-1][:, :DIM]
    w = np.maximum(w, 0.0)
    S = np.sqrt(w)
    Y = normalize(U * S)
    # query: Zq V = (Zq Z^T) U S^-1, no 96 x F projector anywhere
    inv = np.divide(1.0, S, out=np.zeros_like(S), where=S > 1e-12)
    QY = normalize(np.asarray((Zq @ Z.T).todense()) @ U * inv)
    return Y, QY, 0


def arms(Y, QY):
    mu = Y.mean(axis=0, keepdims=True)
    C = Y - mu
    q = (QY - mu).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        flt = (C @ q) / (dn * np.linalg.norm(q))
    ham = -np.count_nonzero((C >= 0) != (q >= 0)[None, :],
                            axis=1).astype(np.float64)
    return {"float": flt, "sym": ham}


def main():
    n_arch = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    ad = BN.load_adapter()
    files = sorted(glob.glob(BN.ITEMS))[:n_arch]
    rows = []
    for f in files:
        item = json.loads(open(f, encoding="utf-8").read())
        mem, gold_ids, issues = ad.build_archive(item)
        if issues:
            continue
        texts = ad.fit_input_payload(mem)
        id_to_row = {m["memory_id"]: i for i, m in enumerate(mem)}
        gold = np.asarray([id_to_row[g] for g in gold_ids], dtype=int)
        t0 = time.perf_counter()
        wv, cv, bs, Xw, Xc, Xl = ad.fit_archive_representation(texts)
        t_tfidf = time.perf_counter() - t0
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        q = str(item["question"])
        Zq = sparse.hstack([sparse.csr_matrix(normalize(bs.transform(
            normalize(wv.transform([q]))))),
            normalize(wv.transform([q])),
            normalize(cv.transform([q]))], format="csr")
        tA = time.perf_counter()
        YA, QA, projA = method_A(Z, Zq)
        tA = time.perf_counter() - tA
        tB = time.perf_counter()
        YB, QB, projB = method_B(Z, Zq)
        tB = time.perf_counter() - tB
        sA, sB = arms(YA, QA), arms(YB, QB)
        r = {"N": Z.shape[0], "F": Z.shape[1], "nnz": int(Z.nnz),
             "t_tfidf": t_tfidf, "t_svd_A": tA, "t_svd_B": tB,
             "proj_bytes_A": projA, "proj_bytes_B": projB}
        for a in ("float", "sym"):
            r[f"maxdiff_{a}"] = float(np.max(np.abs(sA[a] - sB[a])))
            r[f"hit10_A_{a}"] = KS.hit_from_facts(
                *KS.bucket_facts(sA[a], gold), 10)
            r[f"hit10_B_{a}"] = KS.hit_from_facts(
                *KS.bucket_facts(sB[a], gold), 10)
        # rank agreement of the top-10 sets (order-insensitive)
        for a in ("float", "sym"):
            ta = set(np.argsort(-sA[a], kind="stable")[:10])
            tb = set(np.argsort(-sB[a], kind="stable")[:10])
            r[f"top10_overlap_{a}"] = len(ta & tb) / 10.0
        rows.append(r)
        print(f"  N={r['N']:4d} F={r['F']:6d} nnz={r['nnz']:8d}  "
              f"A={tA:6.2f}s  B={tB:6.2f}s  "
              f"x{tA / tB:5.1f}  maxdiff_float={r['maxdiff_float']:.2e}",
              flush=True)
    agg = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "n_archives": len(rows),
           "equivalence_claim": "retrieval-equivalent, not byte-equivalent: "
                                "SVD component signs are arbitrary and cancel "
                                "in both Hamming and centered cosine",
           "mean": {k: float(np.mean([r[k] for r in rows]))
                    for k in rows[0] if k != "N"},
           "rows": rows}
    with open("SVDOPT.json", "w") as fh:
        json.dump(agg, fh, indent=2)
    m = agg["mean"]
    print(f"\n== {len(rows)} arşiv ortalaması ==")
    print(f"  TF-IDF            {m['t_tfidf']:.2f} s")
    print(f"  SVD  A (sklearn)  {m['t_svd_A']:.2f} s")
    print(f"  SVD  B (Gram)     {m['t_svd_B']:.2f} s   "
          f"-> {m['t_svd_A'] / m['t_svd_B']:.1f}x hızlı")
    print(f"  toplam A          {m['t_tfidf'] + m['t_svd_A']:.2f} s")
    print(f"  toplam B          {m['t_tfidf'] + m['t_svd_B']:.2f} s   "
          f"-> {(m['t_tfidf'] + m['t_svd_A']) / (m['t_tfidf'] + m['t_svd_B']):.2f}x")
    print(f"  izdüşüm A         {m['proj_bytes_A'] / 1e6:.1f} MB")
    print(f"  izdüşüm B         {m['proj_bytes_B'] / 1e6:.1f} MB")
    for a in ("float", "sym"):
        print(f"  {a:6s} hit@10 A={m['hit10_A_' + a] * 100:.2f}  "
              f"B={m['hit10_B_' + a] * 100:.2f}   "
              f"top10 örtüşme={m['top10_overlap_' + a] * 100:.1f}%  "
              f"maxdiff={m['maxdiff_' + a]:.2e}")
    print("\nwrote SVDOPT.json")


if __name__ == "__main__":
    main()
