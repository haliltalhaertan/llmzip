# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Own Top10-r1 metric/scorer implementation (baseline).

Four cached-representation arms reuse the cached FLOAT96 representation only:
  SIGN96 Hamming, FLOAT96 raw cosine, FLOAT96 document-standardized cosine
  (existing definition: per-axis doc std, zeros->1), asymmetric
  float-query x SIGN96 (dot(q, pm1)/sqrt(96)).

Deterministic Top10: descending score (nonfinite->-inf, worst), then ascending
SHA256('top10-r1|'+archive_id+'|'+str(row_index)), then ascending row_index.
Exactly ten IDs (or N if N<10); no gold-aware order; no duplicates.
"""
import hashlib
import math

import numpy as np

TIE_SALT = "top10-r1"
SQRT96 = float(np.sqrt(96))


def pack_signs_bool(signs_bool):
    signs_bool = np.asarray(signs_bool, dtype=bool)
    return np.packbits(signs_bool, axis=-1, bitorder="big").astype(np.uint8)


def decode_pm1(packed):
    packed = np.asarray(packed, dtype=np.uint8)
    assert packed.ndim == 2 and packed.shape[1] == 12, packed.shape
    bits = np.unpackbits(packed, axis=1, bitorder="big")[:, :96].astype(bool)
    return np.where(bits, 1, -1).astype(np.int8)


def hamming_from_packed(packed, q_bits):
    d = np.unpackbits(np.asarray(packed, dtype=np.uint8), axis=1,
                      bitorder="big")[:, :96].astype(bool)
    return np.count_nonzero(d != np.asarray(q_bits, dtype=bool)[None, :], axis=1)


def cosine_raw(C, q):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))


def fit_std(C):
    C = np.asarray(C, dtype=np.float64)
    std = np.std(C, axis=0, ddof=0).astype(np.float64)
    std = np.where(std == 0, 1.0, std)
    return std


def cosine_std(C, q, std):
    std = np.asarray(std, dtype=np.float64).reshape(-1)
    assert std.shape == (96,) and np.all(std != 0)
    return cosine_raw(C / std[None, :], q / std)


def asym_scores(packed12, q_float):
    D = decode_pm1(np.asarray(packed12, dtype=np.uint8)).astype(np.float64)
    q = np.asarray(q_float, dtype=np.float64).reshape(-1)
    assert q.shape == (96,)
    return (D @ q) / SQRT96


def _tie_hashes(archive_id, n):
    out = []
    for r in range(n):
        out.append(hashlib.sha256(f"{TIE_SALT}|{archive_id}|{r}".encode()).hexdigest())
    return out


def deterministic_top10(scores, archive_id, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    n = int(s.shape[0])
    k = int(min(k, n))
    mapped = np.where(np.isfinite(s), s, -np.inf)
    hashes = _tie_hashes(str(archive_id), n)
    order = sorted(range(n), key=lambda r: (-mapped[r], hashes[r], r))
    return np.asarray(order[:k], dtype=np.int64)


def hit_recall_ndcg_at_k(top_ids, gold, k=10):
    top = [int(x) for x in np.asarray(top_ids).ravel().tolist()][: int(k)]
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    m = len(gset)
    assert m > 0
    inter = len([x for x in top if x in gset])
    hit = 1.0 if inter > 0 else 0.0
    rec = inter / m
    disc = [1.0 / math.log2(r + 2) for r in range(int(k))]
    idcg = sum(disc[: min(int(k), m)])
    dcg = sum(disc[r] for r, doc in enumerate(top) if doc in gset)
    ndcg = (dcg / idcg) if idcg > 0 else 0.0
    return float(hit), float(rec), float(ndcg)


def _levels_desc(scores_mapped):
    uniq = np.unique(scores_mapped)[::-1]
    return uniq


def expected_recall_at_k(scores, gold, k=10, higher_better=True):
    s = np.asarray(scores, dtype=np.float64).ravel()
    if higher_better:
        s = np.where(np.isfinite(s), s, -np.inf)
    else:
        s = np.where(np.isfinite(s), s, np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    m = len(gset)
    assert m > 0
    uniq = np.unique(s)
    levels = uniq[::-1] if higher_better else uniq
    better = 0
    exp = 0.0
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        B = len(idx)
        if B == 0:
            continue
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + B <= k:
            exp += gb
        else:
            exp += (k - better) * gb / B
            break
        better += B
    return float(exp / m)


def expected_hit_at_k(scores, gold, k=10, higher_better=True):
    s = np.asarray(scores, dtype=np.float64).ravel()
    if higher_better:
        s = np.where(np.isfinite(s), s, -np.inf)
    else:
        s = np.where(np.isfinite(s), s, np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    assert len(gset) > 0
    uniq = np.unique(s)
    levels = uniq[::-1] if higher_better else uniq
    better = 0
    found_above = False
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        B = len(idx)
        if B == 0:
            continue
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + B <= k:
            if gb > 0:
                return 1.0
            better += B
        else:
            if found_above:
                return 1.0
            take = int(k - better)
            if gb == 0:
                return 0.0
            # hypergeometric: P(no gold in random take) = C(B-gb,take)/C(B,take)
            denom = math.comb(B, take)
            numer = math.comb(B - gb, take) if (B - gb) >= take else 0
            return float(1.0 - numer / denom)
    return 1.0 if found_above else 0.0


def tie_info_at_k(scores, gold, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    sm = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().tolist())
    uniq = np.unique(sm)[::-1]
    better = 0
    for lv in uniq:
        idx = np.nonzero(sm == lv)[0]
        B = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + B <= k:
            better += B
            continue
        return {"better": int(better), "bucket_size": int(B),
                "gold_in_bucket": int(gb), "take": int(k - better),
                "is_tie_at_cut": bool(B > 1)}
    return {"better": int(min(better, k)), "bucket_size": 0,
            "gold_in_bucket": 0, "take": 0, "is_tie_at_cut": False}
