#!/usr/bin/env python3
"""Replication test of a PUBLISHED claim on this programme's data.

PAPER: "Anisotropy Decides Cosine vs. Rank Metrics for Text Embeddings"
(arXiv 2606.29571, 2026-06-28). 19 metrics x 19 encoders x 7 datasets.

ITS CENTRAL CLAIM (RELAYED from the abstract):
 - When variance spreads evenly across directions, cosine is the best parameter-free
   choice and nothing else helps by a usable margin.
 - When variance CONCENTRATES into a few dominant directions (anisotropy), rank-based
   and L1-type metrics beat cosine.
 - "One number captures the concentration, namely the fraction of variance held by the
   single most dominant dimension, and it predicts how much the alternatives help
   across all nineteen encoders, with a rank correlation of 0.86 and a linear
   correlation of 0.95."
 - Causal check: projecting out the dominant directions makes cosine recover and the
   alternatives' advantage nearly vanish -- but only on encoders that were anisotropic.
 - The effect is DIRECTIONAL, not magnitude-based: it survives unit-length
   normalization, and the one length-dependent metric is the worst of the set.

WHY THIS MATTERS HERE: that is essentially this session's mechanism, reached
independently. But our measurement today went the OTHER WAY: across four benchmarks
r(top-12 variance share, whitening gain) = -0.90, and across 30 PerLTQA archives
r = -0.002. The paper predicts a STRONG POSITIVE correlation (+0.95 linear).

Possible reconciliations, all tested below:
 (a) wrong statistic -- they use the TOP-1 dimension share, we used top-12;
 (b) wrong alternative -- they use RANK and L1 metrics, we used whitening;
 (c) wrong unit of analysis -- they vary the ENCODER, we vary the corpus with the
     encoder held fixed. If the law is about encoders, our corpora cannot test it.
 (d) their causal control: project out the top directions and see whether the
     alternatives' advantage collapses.
"""
import glob, json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))


def fr_exact(S, G, gs, K=K):
    S = np.asarray(S, float)
    kk = min(K, S.shape[0])
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    b = S > thr[None, :]; e = S == thr[None, :]
    slots = np.maximum(kk - b.sum(0), 0); bc = e.sum(0)
    return ((G & b).sum(0) + np.where(bc > 0, (G & e).sum(0) * (slots / np.maximum(bc, 1)), 0.0)) / gs


def cos_b(C, Q):
    den = np.linalg.norm(C, axis=1)[:, None] * np.linalg.norm(Q, axis=1)[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        o = (C @ Q.T) / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def rank_tf(X):
    out = np.empty_like(X, dtype=float)
    n = X.shape[0]
    for j in range(X.shape[1]):
        v = X[:, j]; o = np.argsort(v, kind='stable'); r = np.empty(n, float)
        sv = v[o]; i = 0
        while i < n:
            k = i
            while k + 1 < n and sv[k + 1] == sv[i]:
                k += 1
            r[o[i:k + 1]] = (i + k) / 2.0 + 1.0
            i = k + 1
        out[:, j] = r - r.mean()
    return out


def arms(C, Q, nproj=0):
    """nproj>0: project out the top-nproj variance directions first (the paper's control)."""
    if nproj > 0:
        Cc = C - C.mean(0)
        _, _, Vt = np.linalg.svd(Cc, full_matrices=False)
        P = Vt[:nproj]
        C = C - (C @ P.T) @ P
        Q = Q - (Q @ P.T) @ P
    out = {}
    out['cosine'] = cos_b(C, Q)
    # L1 metric (their "L1-type"): negative mean absolute difference on unit vectors
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12)
    out['L1'] = -np.abs(Cn[:, None, :] - Qn[None, :, :]).sum(-1).T.T if C.shape[0] * Q.shape[0] * C.shape[1] < 4e7 else None
    # rank metric (their "rank-based")
    Cr = rank_tf(C)
    Qr = np.empty_like(Q, dtype=float)
    for j in range(C.shape[1]):
        Qr[:, j] = np.searchsorted(np.sort(C[:, j]), Q[:, j]) - C.shape[0] / 2.0
    out['rank'] = cos_b(Cr, Qr)
    sig = C.std(axis=0); sig = np.where(sig > 0, sig, 1.0)
    out['whitened'] = cos_b(C / sig, Q / sig)
    D0 = (C >= 0).astype(np.uint8); Q0 = (Q >= 0).astype(np.uint8)
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    out['sign'] = -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))
    return out


def load_lme():
    for f in sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g):
            yield 'LME', np.asarray(d['C'], float), np.asarray(d['qC'], float)[None, :], [g]


def load_perltqa():
    A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for q in Qd.values():
        by.setdefault(q['char'], []).append(q)
    for ch, items in by.items():
        keep = [q for q in items if len(np.asarray(q['gold']).ravel())]
        if keep:
            yield ('PerLTQA', np.asarray(A[ch]['C'], float),
                   np.stack([np.asarray(q['qC'], float) for q in keep]),
                   [np.asarray(q['gold']).ravel().astype(int) for q in keep])


def load_realtalk():
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        gs = [np.asarray(g).ravel().astype(int) for g in d['gold_rows']]
        keep = [i for i, g in enumerate(gs) if len(g)]
        if keep:
            yield ('REALTALK', np.asarray(d['C'], float),
                   np.asarray(d['QC'], float)[keep], [gs[i] for i in keep])


def load_locomo():
    for f in sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        i2r = d['id_to_row']; gs = []; idx = []
        for i, qa in enumerate(d['qas']):
            rows = [i2r[e] for e in (qa.get('raw_evidence') or []) if e in i2r]
            if rows:
                gs.append(np.asarray(sorted(set(rows)), int)); idx.append(i)
        if gs:
            yield ('LoCoMo', np.asarray(d['C'], float), np.asarray(d['QC'], float)[idx], gs)


rows = []
for ld in (load_lme, load_perltqa, load_realtalk, load_locomo):
    for bench, C, Q, golds in ld():
        N, nq = C.shape[0], Q.shape[0]
        gs = np.array([len(g) for g in golds], float)
        G = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            G[g, j] = True
        # THEIR diagnostic: fraction of variance in the single most dominant direction
        Cc = C - C.mean(0)
        sv = np.linalg.svd(Cc, compute_uv=False)
        ev = sv ** 2
        f1_svd = float(ev[0] / ev.sum())
        v = (C ** 2).mean(0)
        f1_coord = float(v.max() / v.sum())
        a = arms(C, Q)
        sc = {k: float(fr_exact(x, G, gs).mean()) for k, x in a.items() if x is not None}
        a2 = arms(C, Q, nproj=3)
        sc2 = {k: float(fr_exact(x, G, gs).mean()) for k, x in a2.items() if x is not None}
        rows.append({'bench': bench, 'N': N, 'nq': nq, 'f1_svd': f1_svd,
                     'f1_coord': f1_coord, **{f's_{k}': v2 for k, v2 in sc.items()},
                     **{f'p_{k}': v2 for k, v2 in sc2.items()}})
    print(f'  {rows[-1]["bench"]} done', flush=True)

B = {}
for b in ('LME', 'PerLTQA', 'REALTALK', 'LoCoMo'):
    rs = [r for r in rows if r['bench'] == b]
    w = np.array([r['nq'] for r in rs], float); w /= w.sum()
    B[b] = {k: float(np.sum(w * np.array([r[k] for r in rs])))
            for k in rs[0] if k != 'bench'}
    B[b]['n_arch'] = len(rs)

print('\n=== CONTROL: sign - cosine must reproduce the frozen headlines ===')
ref = {'LME': 10.053783, 'PerLTQA': -6.274728, 'REALTALK': 5.300077, 'LoCoMo': 6.655046}
for b in B:
    d = 100 * (B[b]['s_sign'] - B[b]['s_cosine'])
    print(f'  {b:9s} {d:>+11.6f}  (ref {ref[b]:+.6f})  {"PASS" if abs(d-ref[b])<0.05 else "CHECK"}')

print('\n=== THE PAPER\'S DIAGNOSTIC vs the gain of each alternative ===')
print('  f1 = fraction of variance in the single most dominant direction (their number)')
print(f'  {"bench":9s} {"f1(svd)":>9s} {"f1(coord)":>10s} {"rank-cos":>10s} {"whit-cos":>10s} {"sign-cos":>10s}')
for b in B:
    print(f'  {b:9s} {B[b]["f1_svd"]:>9.4f} {B[b]["f1_coord"]:>10.4f} '
          f'{100*(B[b]["s_rank"]-B[b]["s_cosine"]):>+10.4f} '
          f'{100*(B[b]["s_whitened"]-B[b]["s_cosine"]):>+10.4f} '
          f'{100*(B[b]["s_sign"]-B[b]["s_cosine"]):>+10.4f}')

print('\n  PAPER PREDICTS: strong POSITIVE correlation (linear 0.95, rank 0.86)')
for stat in ('f1_svd', 'f1_coord'):
    x = np.array([B[b][stat] for b in B])
    for alt in ('rank', 'whitened', 'sign'):
        y = np.array([B[b][f's_{alt}'] - B[b]['s_cosine'] for b in B])
        print(f'    r({stat}, {alt}-cos gain) = {np.corrcoef(x, y)[0,1]:+.4f}   (n=4 benchmarks)')

print('\n  Per-archive, the unit with real sample size:')
for b in ('PerLTQA', 'LME'):
    rs = [r for r in rows if r['bench'] == b]
    x = np.array([r['f1_svd'] for r in rs])
    for alt in ('rank', 'whitened', 'sign'):
        y = np.array([r[f's_{alt}'] - r['s_cosine'] for r in rs])
        print(f'    {b:8s} n={len(rs):3d}  r(f1_svd, {alt}-cos) = {np.corrcoef(x, y)[0,1]:+.4f}')

print('\n=== THEIR CAUSAL CONTROL: project out the top-3 directions ===')
print('  paper: cosine recovers and the alternatives\' advantage nearly vanishes')
print(f'  {"bench":9s} {"gain before":>12s} {"gain after":>11s} {"collapsed?":>11s}   (whitening)')
for b in B:
    g0 = 100 * (B[b]['s_whitened'] - B[b]['s_cosine'])
    g1 = 100 * (B[b]['p_whitened'] - B[b]['p_cosine'])
    print(f'  {b:9s} {g0:>+12.4f} {g1:>+11.4f} {("YES" if abs(g1) < 0.5*abs(g0) else "no"):>11s}')

json.dump({'rows': rows, 'bench': B}, open(os.path.join(OUT, 'lit_replication.json'), 'w'),
          indent=1)
print('\nWROTE lit_replication.json')
