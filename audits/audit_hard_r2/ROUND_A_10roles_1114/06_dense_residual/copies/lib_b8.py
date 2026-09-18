#!/usr/bin/env python3
"""TASK B fixed 96-bit B8 codec + scoring + metrics (frozen per PROTOCOL.md).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
import numpy as np

K = 3
DIM = 96
N_DROP = 8
N_SEL = 8
LVL_BASE = 1.0
LVL_MAG = 2.0


def exact_frac(scores, gold, higher_better=True):
    """Expected fractional R@K under uniform random within-bucket tiebreak."""
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, (-np.inf if higher_better else np.inf))
    g = np.asarray(gold).ravel().astype(int)
    m = int(len(g))
    assert m > 0
    gset = set(int(x) for x in g)
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


def ndcg3_expected(scores, gold):
    """Expected nDCG@3, binary unique gold relevance, uniform tiebreak."""
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    m = len(gset)
    assert m > 0
    disc = np.array([1.0 / np.log2(2 + p) for p in range(K)])
    idcg = float(disc[:min(K, m)].sum())
    exp_dcg = 0.0
    pos = 0
    for lv in np.unique(s)[::-1]:
        if pos >= K:
            break
        idx = np.nonzero(s == lv)[0]
        B = len(idx)
        take = min(B, K - pos)
        gb = sum(1 for i in idx if int(i) in gset)
        exp_dcg += gb * float(disc[pos:pos + take].mean())
        pos += B
    return exp_dcg / idcg


def oracle_bounds(primary_scores, gold, k=K):
    s = np.asarray(primary_scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, -np.inf)
    gset = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    m = len(gset)
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


def select_axes(C):
    """Descending population variance; ties -> lower coordinate index."""
    C = np.asarray(C, dtype=np.float64)
    var = np.var(C, axis=0, ddof=0)
    order = np.lexsort((np.arange(C.shape[1]), -var))
    return order, var


def fit_archive(C):
    """Document-only fit. Returns dict with sel/one/drop ids + thresholds."""
    C = np.asarray(C, dtype=np.float64)
    assert C.ndim == 2 and C.shape[1] == DIM and np.all(np.isfinite(C))
    order, var = select_axes(C)
    sel = np.sort(order[:N_SEL]).astype(np.uint8)
    one = np.sort(order[N_SEL:DIM - N_DROP]).astype(np.uint8)
    drop = np.sort(order[DIM - N_DROP:]).astype(np.uint8)
    assert len(set(sel.tolist()) | set(one.tolist()) | set(drop.tolist())) == DIM
    thr = np.median(np.abs(C[:, sel.astype(int)]), axis=0).astype(np.float64)
    std = np.sqrt(var)
    std = np.where(std == 0.0, 1.0, std)
    return {"sel": sel, "one": one, "drop": drop, "ret": np.sort(
        np.concatenate([sel, one])).astype(np.uint8),
        "thresholds": thr, "std": std}


def encode_docs(C, st):
    """Real [N,12] uint8 payload: 88 sign bits + 8 magnitude flags."""
    C = np.asarray(C, dtype=np.float64)
    sel = st["sel"].astype(int)
    ret = st["ret"].astype(int)
    signs = (C[:, ret] >= 0)
    mags = (np.abs(C[:, sel]) > st["thresholds"][None, :])
    ps = np.packbits(signs, axis=1, bitorder="big")
    pm = np.packbits(mags, axis=1, bitorder="big")
    assert ps.shape[1] == 11 and pm.shape[1] == 1
    return np.concatenate([ps, pm], axis=1).astype(np.uint8)


def decode_b8(packed, st):
    """Decode to float64 reconstruction. Dropped axes -> 0."""
    packed = np.asarray(packed, dtype=np.uint8)
    if packed.ndim != 2 or packed.shape[1] != 12:
        raise ValueError("B8 payload must be [N,12] uint8 (96-bit budget)")
    ret = st["ret"].astype(int)
    sel = st["sel"].astype(int)
    sign_bits = np.unpackbits(packed[:, :11], axis=1,
                              bitorder="big")[:, :88].astype(bool)
    mag_bits = np.unpackbits(packed[:, 12 - 1:12], axis=1,
                             bitorder="big")[:, :8].astype(bool)
    pm = np.where(sign_bits, LVL_BASE, -LVL_BASE)
    r = np.zeros((packed.shape[0], DIM), dtype=np.float64)
    r[:, ret] = pm
    # magnitude upgrade on selected axes (ascending-sel flag order):
    col_of = {ax: c for c, ax in enumerate(ret)}
    sel_cols = np.array([col_of[a] for a in sel])
    pm_sel = pm[:, sel_cols]
    r[:, sel] = np.where(mag_bits, LVL_MAG * np.sign(pm_sel), pm_sel)
    return r


def decode_sign88(packed11, st):
    """Ablation: signs only on retained axes, dropped -> 0. 11-byte payload."""
    packed11 = np.asarray(packed11, dtype=np.uint8)
    if packed11.ndim != 2 or packed11.shape[1] != 11:
        raise ValueError("SIGN88 payload must be [N,11] uint8")
    ret = st["ret"].astype(int)
    sign_bits = np.unpackbits(packed11, axis=1,
                              bitorder="big")[:, :88].astype(bool)
    s = np.zeros((packed11.shape[0], DIM), dtype=np.float64)
    s[:, ret] = np.where(sign_bits, 1.0, -1.0)
    return s


def cosine_from_code(R, q):
    """cosine(float q, code reconstruction); norms FROM CODE. Worst on null q."""
    R = np.asarray(R, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    qn = float(np.linalg.norm(q))
    rn = np.linalg.norm(R, axis=1)
    assert np.all(rn > 0), "reconstruction norm must be positive (88+ ones)"
    if not np.isfinite(qn) or qn == 0.0:
        return np.full(R.shape[0], -np.inf)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (R @ q) / (rn * qn)


def sym_sign96_scores(C, q):
    """A0: -Hamming distance, signs (x>=0)."""
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    return (-np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1)
            .astype(np.float64))


def asym_sign96_scores(C, q):
    """A1: cosine(float q, pm1 doc signs), norm from code (=sqrt(96))."""
    P = np.where(np.asarray(C, dtype=np.float64) >= 0, 1.0, -1.0)
    return cosine_from_code(P, q)


def b8_scores(packed, st, q):
    """A2: cosine(float q, decoded B8 reconstruction). Packed-only + state."""
    return cosine_from_code(decode_b8(packed, st), q)


def sign88_scores(packed, st, q):
    """A3: cosine(float q, signs-only reconstruction)."""
    payload11 = np.asarray(packed, dtype=np.uint8)[:, :11]
    return cosine_from_code(decode_sign88(payload11, st), q)


def float_raw_scores(C, q):
    """A4: plain raw cosine, source-compatible division."""
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))


def float_std_scores(C, q, std):
    """A5: scale-only standardized cosine; std doc-fitted, 0->1 (declared)."""
    C = np.asarray(C, dtype=np.float64) / np.asarray(std, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1) / np.asarray(
        std, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))
