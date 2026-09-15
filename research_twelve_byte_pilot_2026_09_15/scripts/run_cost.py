#!/usr/bin/env python3
"""CPU and RAM of scoring: 12-byte codes vs the 768-byte float baseline.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Three things are measured and kept apart, because mixing them is how a
storage ratio gets mis-sold as a system speedup:

  INDEX RAM      bytes actually resident to score one archive
  SCORE CPU      wall time to score one query against the whole archive
  BUILD CPU      the shared TF-IDF + SVD fit that produces the vectors at all

The Hamming arm is timed TWICE on purpose:
  sign_naive   exactly as `lib_b8.sym_sign96_scores` does it today -- it
               compares against the FLOAT matrix, so it holds 768 B/doc in
               RAM and gets no bit-level speed at all
  sign_packed  the 12 B/doc payload with XOR + popcount, i.e. what the byte
               budget actually claims
Reporting only the second would overstate the current code; reporting only
the first would understate the method.  Both are here.

Real archive sizes here are ~500 documents, where fixed overheads dominate.
A tiled synthetic archive is added to show the asymptotic regime; it is
labelled synthetic and carries no retrieval-quality meaning.
"""
import glob
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

HAS_BITCOUNT = hasattr(np, "bitwise_count")
POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def popcount(a):
    return (np.bitwise_count(a) if HAS_BITCOUNT else POP8[a])


def timeit(fn, reps, warm=3):
    for _ in range(warm):
        fn()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t)
    return float(np.median(ts))


def bench(C, Q, reps=60):
    C = np.ascontiguousarray(np.asarray(C, dtype=np.float64))
    N = C.shape[0]
    Q = np.atleast_2d(np.asarray(Q, dtype=np.float64))
    q = np.ascontiguousarray(Q[0])
    # representations actually resident for each arm
    packed = np.packbits((C >= 0), axis=1, bitorder="big").astype(np.uint8)
    qpack = np.packbits((q >= 0)[None, :], axis=1,
                        bitorder="big").astype(np.uint8)[0]
    S = np.where(C >= 0, 1.0, -1.0)
    cn = np.linalg.norm(C, axis=1)
    out = {"N": N}
    out["ram_bytes"] = {
        "float96": int(C.nbytes + cn.nbytes),
        "sign_naive": int(C.nbytes),          # today's code needs the floats
        "sign_packed": int(packed.nbytes),
        "dot_pm1": int(S.nbytes),
    }

    def f_float():
        return (C @ q) / cn

    def f_sign_naive():
        return -np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1)

    def f_sign_packed():
        # popcount sums to an UNSIGNED dtype; negating it without the cast
        # wraps around and silently produces garbage.  Cast, then negate.
        return -(popcount(np.bitwise_xor(packed, qpack[None, :]))
                 .sum(axis=1).astype(np.int64))

    def f_dot():
        return S @ q

    out["score_ms"] = {
        "float96": timeit(f_float, reps) * 1e3,
        "sign_naive": timeit(f_sign_naive, reps) * 1e3,
        "sign_packed": timeit(f_sign_packed, reps) * 1e3,
        "dot_pm1": timeit(f_dot, reps) * 1e3,
    }
    # agreement check: packed Hamming must equal the frozen naive scorer
    a = f_sign_naive()
    b = f_sign_packed()
    out["packed_matches_frozen"] = bool(np.array_equal(a, b))
    return out


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "numpy": np.__version__, "has_native_popcount": HAS_BITCOUNT,
           "threads": {k: os.environ.get(k) for k in
                       ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
                        "OPENBLAS_NUM_THREADS")},
           "real": {}, "synthetic": {}, "build": {}}

    # ---- real archives ----
    f = sorted(glob.glob(H.LME_GLOB))[0]
    d = pickle.loads(open(f, "rb").read())
    res["real"]["lme_one_archive"] = bench(np.asarray(d["C"], float),
                                           np.asarray(d["qC"], float))
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    Qc = pickle.load(open(H.Q_PKL, "rb"))
    ch = sorted(arch)[0]
    qid = next(k for k, v in Qc.items() if v["char"] == ch)
    res["real"]["perltqa_one_archive"] = bench(
        np.asarray(arch[ch]["C"], float), np.asarray(Qc[qid]["qC"], float))
    base = np.asarray(d["C"], float)
    del arch, Qc

    # ---- synthetic scale-up (tiled real codes; no quality meaning) ----
    rng = np.random.default_rng(0)
    for N in (10_000, 100_000, 1_000_000):
        reps = 20 if N <= 100_000 else 5
        idx = rng.integers(0, base.shape[0], size=N)
        big = np.ascontiguousarray(base[idx]
                                   + rng.normal(0, 1e-3, (N, 96)))
        res["synthetic"][str(N)] = bench(big, np.asarray(d["qC"], float),
                                         reps=reps)
        del big

    # ---- build cost (shared by every arm) ----
    import run_bottleneck as BN
    from scipy import sparse
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize
    ad = BN.load_adapter()
    item = json.loads(open(sorted(glob.glob(BN.ITEMS))[0],
                           encoding="utf-8").read())
    mem, _, _ = ad.build_archive(item)
    texts = ad.fit_input_payload(mem)
    t0 = time.perf_counter()
    wv, cv, bs, Xw, Xc, Xl = ad.fit_archive_representation(texts)
    t_tfidf = time.perf_counter() - t0
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    t0 = time.perf_counter()
    sv = TruncatedSVD(n_components=96, random_state=5101)
    normalize(sv.fit_transform(Z))
    t_svd = time.perf_counter() - t0
    res["build"] = {"N": len(texts), "tfidf_seconds": t_tfidf,
                    "svd96_seconds": t_svd,
                    "total_seconds": t_tfidf + t_svd,
                    "note": "per archive, identical for every arm; the "
                            "frozen protocol refits this per question"}

    with open("COST.json", "w") as fh:
        json.dump(res, fh, indent=2)

    def show(tag, v):
        print(f"\n== {tag}  N={v['N']:,} ==")
        print("  arm            RAM        score/query")
        for a in ("float96", "sign_naive", "sign_packed", "dot_pm1"):
            print(f"  {a:12s} {v['ram_bytes'][a]/1e6:8.3f} MB "
                  f"{v['score_ms'][a]:9.3f} ms")
        r = v["ram_bytes"]["float96"] / v["ram_bytes"]["sign_packed"]
        s = v["score_ms"]["float96"] / v["score_ms"]["sign_packed"]
        print(f"  -> packed vs float:  RAM {r:.1f}x   CPU {s:.2f}x   "
              f"(eşleşme: {v['packed_matches_frozen']})")
    for k, v in res["real"].items():
        show(k, v)
    for k, v in res["synthetic"].items():
        show("synthetic", v)
    b = res["build"]
    print(f"\n== BUILD (her kol için aynı) N={b['N']} ==")
    print(f"  TF-IDF {b['tfidf_seconds']:.2f}s + SVD96 "
          f"{b['svd96_seconds']:.2f}s = {b['total_seconds']:.2f}s")
    print("\nwrote COST.json")


if __name__ == "__main__":
    main()
