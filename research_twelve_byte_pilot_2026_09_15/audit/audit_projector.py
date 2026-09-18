#!/usr/bin/env python3
"""Is the PRODUCTION projector V already inside the row space of Z?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

An external reviewer proposes something sharper than the exact-Gram path
this session measured.  My Gram trick computes a DIFFERENT (exact)
factorization and therefore a different representation -- which is why it
moved the sign arm.  Their claim is that no new factorization is needed:

    if the columns of V lie in the row space of Z, then V = Z^T A for some
    A, and    z_q V = (z_q Z^T) A
    -- the same projection, without ever storing the wide V.

That would keep the PRODUCTION representation bit-for-bit and still drop the
74.8 MB projector.  It is checkable, so this checks it instead of arguing.

sklearn's randomized_svd builds an orthonormal Q spanning range(Z), forms
B = Q^T Z, and takes V from the right singular vectors of B.  Since
B^T = Z^T Q, every column of V is a combination of columns of Z^T, so the
claim should hold EXACTLY, not approximately.  Measured here:

  1. residual of V after projecting onto row space of Z  (should be ~0)
  2. does the reconstructed query projection equal sklearn's transform,
     bit-for-bit or to float noise
  3. do the resulting SIGN96 query bits agree
  4. what it actually costs: memory saved vs query-projection time, which
     goes from 96 columns to N columns of work and may get SLOWER
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
import run_bottleneck as BN  # noqa: E402

SVD_SEED = 5204          # the FINAL SVD96 seed (5101 is the LSA32 stage)
REPS = 200


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    adapter = BN.load_adapter()
    rows = []
    for f in sorted(glob.glob(BN.ITEMS))[:k]:
        tag = os.path.basename(f)[:-5]
        item = json.loads(open(f, encoding="utf-8").read())
        memories, gold_ids, issues = adapter.build_archive(item)
        assert not issues, issues[:2]
        texts = adapter.fit_input_payload(memories)
        wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(texts)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        q = str(item["question"])
        Qw = normalize(wv.transform([q]))
        Qc = normalize(cv.transform([q]))
        Ql = normalize(base_svd.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")

        sv = TruncatedSVD(n_components=96, random_state=SVD_SEED)
        Y = sv.fit_transform(Z)                      # production path
        V = sv.components_.T                         # F x 96
        N, F = Z.shape

        # ---- 1. is V in the row space of Z? solve Z^T A = V in least squares
        # Z^T A = V  <=>  A = (Z Z^T)^+ Z V   (normal equations on the small side)
        G = (Z @ Z.T).toarray()
        ZV = np.asarray((Z @ V))                     # N x 96
        A = np.linalg.lstsq(G, ZV, rcond=None)[0]    # N x 96
        V_hat = np.asarray((Z.T @ A))                # F x 96
        resid = float(np.abs(V_hat - V).max())
        rel = resid / float(np.abs(V).max())

        # ---- 2. query projection both ways
        proj_ref = np.asarray(Zq @ V).reshape(-1)            # sklearn's transform
        proj_new = np.asarray((Zq @ Z.T).todense()) @ A       # (z_q Z^T) A
        proj_new = np.asarray(proj_new).reshape(-1)
        dproj = float(np.abs(proj_new - proj_ref).max())

        # ---- 3. do the SIGN bits of the query agree after the full recipe
        mu = normalize(Y).mean(axis=0, keepdims=True)
        qb_ref = (normalize(proj_ref.reshape(1, -1)) - mu >= 0)
        qb_new = (normalize(proj_new.reshape(1, -1)) - mu >= 0)
        bit_diff = int(np.count_nonzero(qb_ref != qb_new))

        # ---- 4. cost: memory and query-projection time
        t0 = time.perf_counter()
        for _ in range(REPS):
            np.asarray(Zq @ V)
        t_ref = (time.perf_counter() - t0) / REPS
        t0 = time.perf_counter()
        for _ in range(REPS):
            np.asarray((Zq @ Z.T).todense()) @ A
        t_new = (time.perf_counter() - t0) / REPS

        rows.append({
            "tag": tag, "N": int(N), "F": int(F),
            "projector_V_bytes": int(V.nbytes),
            "factor_A_bytes": int(A.nbytes),
            "Z_sparse_bytes": int(Z.data.nbytes + Z.indices.nbytes
                                  + Z.indptr.nbytes),
            "max_abs_residual_V": resid,
            "relative_residual_V": rel,
            "max_abs_query_projection_diff": dproj,
            "query_sign_bits_differing": bit_diff,
            "query_proj_ms_V": t_ref * 1e3,
            "query_proj_ms_ZtA": t_new * 1e3,
        })
        r = rows[-1]
        print(f"  {tag} N={N:4d} F={F:6d}  "
              f"V-artik {rel:.2e}  proj-fark {dproj:.2e}  "
              f"bit-fark {bit_diff:2d}  "
              f"V {V.nbytes/1e6:5.1f}MB -> A {A.nbytes/1e6:.3f}MB  "
              f"(+Z {r['Z_sparse_bytes']/1e6:.1f}MB)  "
              f"sorgu {t_ref*1e3:.3f} -> {t_new*1e3:.3f} ms", flush=True)

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "claim": ("V lies in the row space of Z, so V = Z^T A and the wide "
                     "projector need never be stored -- same representation, "
                     "unlike the exact-Gram path"),
           "seed_note": "SVD96 uses 5204; 5101 is the LSA32 stage",
           "n_archives": len(rows),
           "max_relative_residual_V": max(r["relative_residual_V"] for r in rows),
           "max_query_projection_diff": max(
               r["max_abs_query_projection_diff"] for r in rows),
           "total_query_sign_bits_differing": sum(
               r["query_sign_bits_differing"] for r in rows),
           "memory": {
               "V_total_MB": sum(r["projector_V_bytes"] for r in rows) / 1e6,
               "A_total_MB": sum(r["factor_A_bytes"] for r in rows) / 1e6,
               "Z_total_MB": sum(r["Z_sparse_bytes"] for r in rows) / 1e6},
           "query_projection_ms": {
               "via_V_mean": float(np.mean([r["query_proj_ms_V"] for r in rows])),
               "via_ZtA_mean": float(np.mean([r["query_proj_ms_ZtA"]
                                              for r in rows]))},
           "rows": rows}
    with open(os.path.join(HERE, "AUDIT_PROJECTOR.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    m, qp = out["memory"], out["query_projection_ms"]
    print("\n=== SONUC ===")
    print(f"  V satir uzayinda mi : en buyuk bagil artik "
          f"{out['max_relative_residual_V']:.3e}")
    print(f"  sorgu projeksiyonu  : en buyuk fark "
          f"{out['max_query_projection_diff']:.3e}, "
          f"farkli isaret biti {out['total_query_sign_bits_differing']}")
    print(f"  bellek              : V {m['V_total_MB']:.1f} MB -> "
          f"A {m['A_total_MB']:.3f} MB, ama Z {m['Z_total_MB']:.1f} MB "
          f"zaten tutulmali")
    print(f"  sorgu projeksiyonu  : {qp['via_V_mean']:.3f} ms -> "
          f"{qp['via_ZtA_mean']:.3f} ms "
          f"({qp['via_ZtA_mean']/qp['via_V_mean']:.2f}x)")
    print("\nwrote AUDIT_PROJECTOR.json")


if __name__ == "__main__":
    main()
