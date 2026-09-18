#!/usr/bin/env python3
"""Residual8 pilot library: fixed encoding + fixed arms + exact expectation.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Conventions are verbatim-compatible with the PerLTQA theory-benchmark source
script (runner.py): signs are (x >= 0), magnitude bits are STRICT (abs > thr),
raw cosine is (C @ q)/(dn*qn) with non-finite mapped to worst in exact_frac.
"""
import numpy as np

K = 3
STRIDE_MAG8 = 65    # > max-min of MAG8 residual in [-32, +32]
STRIDE_SIGN8 = 17   # > max-min of SIGN_ONLY8 residual in [-8, +8]
STRIDE_RAND8 = 9    # > max-min of 8-bit suffix Hamming distance in [0, 8]
N_DIMS = 96
N_EXTRA = 8


def exact_frac(scores, gold, higher_better):
    """Expected fractional R@K under uniform random within-bucket tiebreak."""
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, (-np.inf if higher_better else np.inf))
    g = np.asarray(gold).ravel()
    m = int(len(g))
    assert m > 0
    gset = set(map(int, g))
    uniq = np.unique(s)
    levels = uniq[::-1] if higher_better else uniq
    better = 0
    exp = 0.0
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        B = len(idx)
        if B == 0:
            continue
        if better >= K:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + B <= K:
            exp += gb
        else:
            exp += (K - better) * gb / B
            break
        better += B
    return exp / m


def oracle_bounds(primary_scores, gold, k=K):
    """Diagnostic (best, worst) FR@K over tie resolutions at the K boundary."""
    s = np.asarray(primary_scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    g = np.asarray(gold).ravel()
    m = int(len(g))
    gset = set(map(int, g))
    kk = min(k, len(s))
    thr = -np.partition(-s, kk - 1)[kk - 1]
    better = s > thr
    equal = s == thr
    strictly = int(better.sum())
    bc = int(equal.sum())
    slots = max(kk - strictly, 0)
    g_strict = sum(1 for i in np.nonzero(better)[0] if int(i) in gset)
    g_tied = sum(1 for i in np.nonzero(equal)[0] if int(i) in gset)
    best = (g_strict + min(slots, g_tied)) / m
    worst = (g_strict + max(0, slots - (bc - g_tied))) / m
    return worst, best


def cos_scores(C, q):
    """Raw cosine, source-compatible: plain division, no norm guard."""
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))


def select_axes(C):
    """Document-only variance axis selection (no query/gold input)."""
    C = np.asarray(C, dtype=np.float64)
    return np.lexsort((np.arange(C.shape[1]),
                       -np.var(C, axis=0, ddof=0)))[:N_EXTRA].astype(np.uint8)


def encode_archive(C):
    """Fit thresholds on float64 docs; emit real packed uint8 [N,13] payload."""
    C = np.asarray(C, dtype=np.float64)
    assert C.shape[1] == N_DIMS and np.isfinite(C).all()
    axes = select_axes(C)
    thr = np.median(np.abs(C[:, axes.astype(int)]), axis=0).astype(np.float64)
    signs = (C >= 0)
    mags = (np.abs(C[:, axes.astype(int)]) > thr[None, :])
    packed_signs = np.packbits(signs, axis=1, bitorder="big")
    packed_mags = np.packbits(mags, axis=1, bitorder="big")
    assert packed_signs.shape[1] == 12 and packed_mags.shape[1] == 1
    return {"axes": axes, "thresholds": thr,
            "packed": np.concatenate([packed_signs, packed_mags], axis=1)}


def decode_packed(packed):
    """Split a real [N,13] payload into 96 sign bits + 8 magnitude bits."""
    packed = np.asarray(packed, dtype=np.uint8)
    assert packed.ndim == 2 and packed.shape[1] == 13
    signs = np.unpackbits(packed[:, :12], axis=1, bitorder="big").astype(bool)
    mags = np.unpackbits(packed[:, 12:], axis=1, bitorder="big").astype(bool)
    return signs, mags


def encode_query(qC, axes, thresholds):
    """Encode a query vector with stored archive thresholds (query never fit).

    Returns the packed-only query channel: 12 packed sign bytes plus the
    selected-axis signs/magnitudes. Query float state is consumed here and
    never stored in the document payload path.
    """
    qC = np.asarray(qC, dtype=np.float64)
    axes = np.asarray(axes).astype(int)
    thr = np.asarray(thresholds, dtype=np.float64)
    signs96 = (qC >= 0)
    return {"qpacked": np.packbits(signs96, bitorder="big").astype(np.uint8),
            "signs96": signs96,
            "s8": np.where(signs96[axes], 1, -1).astype(np.int64),
            "m01": (np.abs(qC[axes]) > thr).astype(np.int64)}


def hamming96(packed, query_signs96):
    """Hamming distance from decoded payload signs to a query sign vector."""
    signs, _ = decode_packed(packed)
    return np.count_nonzero(signs != np.asarray(query_signs96)[None, :], axis=1)


def mag8_residual(packed, sel_signs, sel_mags, axis_map):
    """Weighted signed-product residual from decoded tail bits only."""
    signs, mags = decode_packed(np.asarray(packed, dtype=np.uint8))
    ax = np.asarray(axis_map).astype(int)
    s_doc = np.where(signs[:, ax], 1, -1).astype(np.int64)
    s_q = np.asarray(sel_signs, dtype=np.int64)[None, :]
    w = ((1 + mags.astype(np.int64))
         * (1 + np.asarray(sel_mags, dtype=np.int64)[None, :]))
    return np.sum(w * s_doc * s_q, axis=1)


def _packed_hamming(packed, query_packed_signs):
    """Hamming distance between decoded payload signs and packed query signs."""
    d_signs, _ = decode_packed(np.asarray(packed, dtype=np.uint8))
    q_signs = np.unpackbits(np.asarray(query_packed_signs, dtype=np.uint8),
                            bitorder="big").astype(bool)
    assert q_signs.shape == (96,)
    return np.count_nonzero(d_signs != q_signs[None, :], axis=1)


def mag8_scores(packed, encoded_query, axis_map):
    """Lexicographic (-H96, MAG8 residual) via stride-65 integer encoding.

    Accepts only the packed document payload, the packed-channel encoded
    query and the shared axis map; no document float state is accepted,
    decoded, or touched anywhere in this function.
    """
    packed = np.asarray(packed, dtype=np.uint8)
    axis_map = np.asarray(axis_map).astype(int)
    prim = _packed_hamming(packed, encoded_query["qpacked"])
    d_signs, mags = decode_packed(packed)
    s_doc = np.where(d_signs[:, axis_map], 1, -1).astype(np.int64)
    s_q = np.asarray(encoded_query["s8"], dtype=np.int64)[None, :]
    w = ((1 + mags.astype(np.int64))
         * (1 + np.asarray(encoded_query["m01"], dtype=np.int64)[None, :]))
    resid = np.sum(w * s_doc * s_q, axis=1)
    return -prim.astype(np.int64) * STRIDE_MAG8 + resid


def signonly8_scores(packed, encoded_query, axis_map):
    """Lexicographic (-H96, sign-only residual) via stride-17 integer encoding.

    Accepts only the packed document payload, the packed-channel encoded
    query and the shared axis map; no document float state is accepted,
    decoded, or touched anywhere in this function.
    """
    packed = np.asarray(packed, dtype=np.uint8)
    axis_map = np.asarray(axis_map).astype(int)
    prim = _packed_hamming(packed, encoded_query["qpacked"])
    d_signs, _ = decode_packed(packed)
    s_doc = np.where(d_signs[:, axis_map], 1, -1).astype(np.int64)
    resid = np.sum(s_doc * np.asarray(encoded_query["s8"], dtype=np.int64)[None, :],
                   axis=1)
    return -prim.astype(np.int64) * STRIDE_SIGN8 + resid


def random8_scores(primary_hamming, doc_suffix, query_suffix):
    """Lexicographic (-H96, -suffix-Hamming) via stride-9 integer encoding."""
    h8 = np.count_nonzero(np.asarray(doc_suffix, dtype=np.uint8)
                          != np.asarray(query_suffix, dtype=np.uint8)[None, :],
                          axis=1)
    return -np.asarray(primary_hamming, dtype=np.int64) * STRIDE_RAND8 - h8
