#!/usr/bin/env python3
"""Test the PUBLISHED theory of Xiao (2026) against my own story, on this data.

PAPER (VERIFIED, fetched from arxiv.org/abs/2605.17524 and /html/2605.17524v2):
  Wenxuan Xiao, "Covariance Structure and Coordinate Heterogeneity Govern Binary
  Quantization of Contrastive Embeddings", arXiv:2605.17524v2, 29 May 2026.
  18 datasets, 9 embedding families, dimensions 100-3072.

ITS CLAIMS, quoted from the abstract/intro (VERIFIED):
  - "coordinate heterogeneity (the non-uniformity of per-coordinate variances) governs
     key design choices: how much each additional bit contributes, and whether random
     rotation helps or hurts"
  - "the magnitude bit carries information proportional to heterogeneity"
  - "random rotation destroys precisely the signal that one paradigm exploits while
     creating the isotropy that the other requires"
  - "rotation equalizes variances, destroying the implicit weighting that Hamming
     distance exploits"

THE TENSION WITH MY STORY -- this is the scientific point:
  MY story:    sign quantization EQUALIZES axes (cosine over-weights high-variance
               axes; sign gives every axis one vote). Advantage = implicit whitening.
  XIAO story:  Hamming EXPLOITS heterogeneity. High-variance axes carry reliable sign
               bits; low-variance axes carry near-coin-flip bits. Rotation equalizes
               variances and destroys that.
  These are opposite readings of the same word "equalization". Xiao's is about which
  BITS are informative; mine is about which AXES the SCORE weights.

Evidence already on record that bears on it:
  - My Haar rotation result (-15.93 pp on LongMemEval) is predicted by Xiao's
    Corollary 3 and was unexplained under my story.
  - My preregistered locus test killed "low-variance axes are the sign arm's friend"
    (Delta(bot16) < Delta(top16) on 7 of 8 units) -- which sits better with Xiao.

XIAO'S CENTRAL QUANTITATIVE PREDICTION, tested here for the first time on TF-IDF/SVD
corpora (his 9 families are all neural contrastive embedders):
  "the magnitude bit carries information proportional to heterogeneity", i.e. the gain
  of 2-bit over 1-bit should be MONOTONE INCREASING in coordinate heterogeneity.
  His Appendix table reports rho(CV, Delta F_mag) = +1.00 over an intervention ladder.

  Heterogeneity measure (his): CV(sigma) = std(sigma_j) / mean(sigma_j) over coordinates.
  2-bit code: sign bit PLUS a magnitude bit (|x_j| above/below the per-axis median).
  Distance: Hamming on the 2-bit code (both bits count equally), 24 bytes/doc vs 12.

PREDICTION FROZEN BEFORE RUNNING (coordinator): if Xiao's theory transfers to these
corpora, r(CV(sigma), 2bit-minus-1bit gain) should be strongly POSITIVE across the four
benchmarks and across the 30 PerLTQA archives. I expect it to hold across archives
(n=30) and to be noisy across 4 benchmarks. Confidence: medium. This is a test of HIS
theory, not mine, so a negative result is a finding about the paper's scope.
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


def hamming(Db, Qb):
    Db = Db.astype(np.int32); Qb = Qb.astype(np.int32)
    return -(Db.sum(1)[:, None] + Qb.sum(1)[None, :] - 2 * (Db @ Qb.T))


def codes_1bit(C, Q):
    return (C >= 0).astype(np.uint8), (Q >= 0).astype(np.uint8)


def codes_2bit(C, Q):
    """sign bit + magnitude bit (|x| above the per-axis median of |C|)."""
    med = np.median(np.abs(C), axis=0)
    Dc = np.hstack([(C >= 0), (np.abs(C) >= med[None, :])]).astype(np.uint8)
    Qc = np.hstack([(Q >= 0), (np.abs(Q) >= med[None, :])]).astype(np.uint8)
    return Dc, Qc


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
        sig = C.std(axis=0)
        cv = float(sig.std() / sig.mean()) if sig.mean() > 0 else 0.0
        D1, Q1 = codes_1bit(C, Q)
        D2, Q2 = codes_2bit(C, Q)
        f1 = fr_exact(hamming(D1, Q1), G, gs).mean()
        f2 = fr_exact(hamming(D2, Q2), G, gs).mean()
        fc = fr_exact(cos_b(C, Q), G, gs).mean()
        # Xiao's rotation corollary: Haar rotation before quantization
        rng = np.random.default_rng(11)
        Z = rng.normal(size=(C.shape[1], C.shape[1]))
        Qr, _ = np.linalg.qr(Z)
        Cr, Qq = C @ Qr, Q @ Qr
        Dr, Qrr = codes_1bit(Cr, Qq)
        fr_rot = fr_exact(hamming(Dr, Qrr), G, gs).mean()
        sigr = Cr.std(axis=0)
        cvr = float(sigr.std() / sigr.mean()) if sigr.mean() > 0 else 0.0
        rows.append({'bench': bench, 'nq': nq, 'cv': cv, 'cv_rot': cvr,
                     'f_1bit': float(f1), 'f_2bit': float(f2), 'f_cos': float(fc),
                     'f_rot': float(fr_rot)})
    print(f'  {rows[-1]["bench"]} done', flush=True)

B = {}
for b in ('LME', 'PerLTQA', 'REALTALK', 'LoCoMo'):
    rs = [r for r in rows if r['bench'] == b]
    w = np.array([r['nq'] for r in rs], float); w /= w.sum()
    B[b] = {k: float(np.sum(w * np.array([r[k] for r in rs])))
            for k in ('cv', 'cv_rot', 'f_1bit', 'f_2bit', 'f_cos', 'f_rot')}
    B[b]['n_arch'] = len(rs)

print('\n=== CONTROL: 1-bit minus cosine must reproduce the frozen headlines ===')
ref = {'LME': 10.053783, 'PerLTQA': -6.274728, 'REALTALK': 5.300077, 'LoCoMo': 6.655046}
for b in B:
    d = 100 * (B[b]['f_1bit'] - B[b]['f_cos'])
    print(f'  {b:9s} {d:>+11.6f}  (ref {ref[b]:+.6f})  {"PASS" if abs(d-ref[b])<0.05 else "FAIL"}')

print("\n=== XIAO PREDICTION 1: rotation equalizes variances and destroys the signal ===")
print(f'  {"bench":9s} {"CV before":>10s} {"CV after rot":>13s} {"1bit before":>12s} '
      f'{"1bit after":>11s} {"cost pp":>9s}')
for b in B:
    print(f'  {b:9s} {B[b]["cv"]:>10.4f} {B[b]["cv_rot"]:>13.4f} {B[b]["f_1bit"]:>12.6f} '
          f'{B[b]["f_rot"]:>11.6f} {100*(B[b]["f_rot"]-B[b]["f_1bit"]):>+9.4f}')
print('  his Corollary 3: rotation HARMS heterogeneity-aware BQ. Negative cost = confirmed.')

print('\n=== XIAO PREDICTION 2: magnitude-bit gain is monotone in heterogeneity ===')
print(f'  {"bench":9s} {"CV(sigma)":>10s} {"1-bit":>9s} {"2-bit":>9s} {"gain pp":>9s}')
for b in B:
    print(f'  {b:9s} {B[b]["cv"]:>10.4f} {B[b]["f_1bit"]:>9.6f} {B[b]["f_2bit"]:>9.6f} '
          f'{100*(B[b]["f_2bit"]-B[b]["f_1bit"]):>+9.4f}')
x = np.array([B[b]['cv'] for b in B])
y = np.array([100 * (B[b]['f_2bit'] - B[b]['f_1bit']) for b in B])
print(f'\n  r(CV, 2bit-1bit gain) = {np.corrcoef(x, y)[0,1]:+.4f}  (n=4 benchmarks)')
print('  his Appendix reports rho = +1.00 on an intervention ladder.')

for b in ('PerLTQA', 'LME'):
    rs = [r for r in rows if r['bench'] == b]
    xa = np.array([r['cv'] for r in rs])
    ya = np.array([100 * (r['f_2bit'] - r['f_1bit']) for r in rs])
    print(f'  {b:8s} across {len(rs):3d} archives: r = {np.corrcoef(xa, ya)[0,1]:+.4f}')

print('\n=== WHICH STORY DOES THE 2-BIT ARM SUPPORT? ===')
print('  MY story says sign wins by EQUALIZING; adding a magnitude bit restores')
print('  magnitude, so it should HURT (like the AQS arm did, -3.56 pp).')
print('  XIAO says the magnitude bit ADDS information proportional to heterogeneity,')
print('  so it should HELP. The sign of the gain decides between the two.')
for b in B:
    g = 100 * (B[b]['f_2bit'] - B[b]['f_1bit'])
    print(f'  {b:9s} gain {g:>+8.4f} pp  -> {"XIAO (helps)" if g > 0 else "MINE (hurts)"}')

json.dump({'rows': rows, 'bench': B}, open(os.path.join(OUT, 'xiao_test.json'), 'w'),
          indent=1)
print('\nWROTE xiao_test.json')
