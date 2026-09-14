#!/usr/bin/env python3
"""Coordinator's own run at the most dangerous question: is the FLOAT arm a weak baseline?

The programme's headline is "12 bytes beats 384 bytes". That comparison uses ONE float
baseline: cosine on the centered 96-D vector. Centering, 96 dimensions and cosine are
all project choices. If a cheap, reasonable variant of the FLOAT arm erases the sign
advantage, the headline is a statement about the baseline, not about quantization.

Arms compared (all computable from the cached C, no new embeddings):
  sign        Hamming on (C>=0) vs (q>=0)              12 B/doc
  cosine      cosine on C                       (frozen float arm, 384 B/doc)
  rawdot      C_i . q                                  384 B
  whitened    cosine on C / per-axis sigma              384 B   <- implicit uniform axis weight
  rank        Spearman-style: cosine on per-axis rank-transformed C   384 B
  l2norm      Euclidean on L2-normalised C (monotone with cosine; sanity check)
  softsign    cosine on tanh(C / sigma)                 384 B   <- soft version of sign

The whitened arm is the decisive one. Sign quantization treats every axis identically
(each contributes 0 or 1 regardless of magnitude), i.e. it is an implicit UNIFORM axis
weighting. Whitening gives the float arm the same property while keeping magnitudes.
If whitened cosine matches or beats sign, the advantage is explained as implicit
whitening and is NOT about discarding magnitude.

PREDICTION (frozen before running, coordinator):
  P1 whitened cosine will beat plain cosine on the three sign-positive benchmarks.
  P2 whitened cosine will NOT fully close the +10.05 pp gap on LongMemEval; I expect it
     to close between 30% and 80% of it.
  P3 on PerLTQA (where sign LOSES) whitening will change little or hurt, since the
     high-variance axes are the informative ones there.
  Confidence: P1 high, P2 low (this is the one I most expect to be wrong), P3 medium.
"""
import glob, json, os, pickle, sys
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))


def fr_exact(S, Gmask, gsize, K=K):
    S = np.asarray(S, float)
    N = S.shape[0]
    kk = min(K, N)
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    better = S > thr[None, :]
    equal = S == thr[None, :]
    strictly = better.sum(0)
    bc = equal.sum(0)
    slots = np.maximum(kk - strictly, 0)
    g_s = (Gmask & better).sum(0)
    g_t = (Gmask & equal).sum(0)
    frac = np.where(bc > 0, g_t * (slots / np.maximum(bc, 1)), 0.0)
    return (g_s + frac) / gsize


def cos_b(Cm, Qm):
    nC = np.linalg.norm(Cm, axis=1)
    nQ = np.linalg.norm(Qm, axis=1)
    den = nC[:, None] * nQ[None, :]
    num = Cm @ Qm.T
    with np.errstate(divide='ignore', invalid='ignore'):
        o = num / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def ham_b(D0, Q0):
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    return -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))


def rank_tf(X):
    """per-axis rank transform, ties averaged, centered."""
    out = np.empty_like(X, dtype=float)
    n = X.shape[0]
    for j in range(X.shape[1]):
        v = X[:, j]
        o = np.argsort(v, kind='stable')
        r = np.empty(n, float)
        sv = v[o]
        i = 0
        while i < n:
            k = i
            while k + 1 < n and sv[k + 1] == sv[i]:
                k += 1
            r[o[i:k + 1]] = (i + k) / 2.0 + 1.0
            i = k + 1
        out[:, j] = r - r.mean()
    return out


def arms(C, Q):
    """Q is (nq, D). Returns dict arm -> (N, nq) score matrices, higher better."""
    sig = C.std(axis=0)
    sig = np.where(sig > 0, sig, 1.0)
    Cw, Qw = C / sig, Q / sig
    out = {
        'sign': ham_b((C >= 0).astype(np.uint8), (Q >= 0).astype(np.uint8)),
        'cosine': cos_b(C, Q),
        'rawdot': C @ Q.T,
        'whitened': cos_b(Cw, Qw),
        'softsign': cos_b(np.tanh(Cw), np.tanh(Qw)),
    }
    Cr = rank_tf(C)
    # query rank-transformed against the document rank scale: rank q per axis within C
    Qr = np.empty_like(Q, dtype=float)
    for j in range(C.shape[1]):
        Qr[:, j] = np.searchsorted(np.sort(C[:, j]), Q[:, j]) - C.shape[0] / 2.0
    out['rank'] = cos_b(Cr, Qr)
    return out


def load_lme():
    for f in sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g):
            yield (np.asarray(d['C'], float), np.asarray(d['qC'], float)[None, :], [g], [''])


def load_perltqa():
    A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for qid, q in Qd.items():
        by.setdefault(q['char'], []).append((qid, q))
    for ch, items in by.items():
        C = np.asarray(A[ch]['C'], float)
        Q = np.stack([np.asarray(q['qC'], float) for _, q in items])
        golds = [np.asarray(q['gold']).ravel().astype(int) for _, q in items]
        secs = [q.get('section', '') for _, q in items]
        keep = [i for i, g in enumerate(golds) if len(g)]
        yield (C, Q[keep], [golds[i] for i in keep], [secs[i] for i in keep])


def load_realtalk():
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); Q = np.asarray(d['QC'], float)
        gr = d['gold_rows']
        golds = [np.asarray(g).ravel().astype(int) for g in gr]
        keep = [i for i, g in enumerate(golds) if len(g)]
        if keep:
            yield (C, Q[keep], [golds[i] for i in keep], [''] * len(keep))


def load_locomo():
    for f in sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); Q = np.asarray(d['QC'], float)
        i2r = d['id_to_row']
        golds, idx = [], []
        for i, qa in enumerate(d['qas']):
            ev = qa.get('raw_evidence') or []
            rows = [i2r[e] for e in ev if e in i2r]
            if rows:
                golds.append(np.asarray(sorted(set(rows)), int)); idx.append(i)
        if golds:
            yield (C, Q[idx], golds, [''] * len(golds))


LOADERS = {'LME': load_lme, 'PerLTQA': load_perltqa,
           'REALTALK': load_realtalk, 'LoCoMo': load_locomo}
ARMS = ['sign', 'cosine', 'rawdot', 'whitened', 'softsign', 'rank']

results = {}
sections = {}
for bname, ld in LOADERS.items():
    acc = {a: [] for a in ARMS}
    sacc = {}
    for C, Q, golds, secs in ld():
        N = C.shape[0]; nq = Q.shape[0]
        gs = np.array([len(g) for g in golds], float)
        G = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            G[g, j] = True
        sc = arms(C, Q)
        for a in ARMS:
            v = fr_exact(sc[a], G, gs)
            acc[a].append(v)
            if secs and secs[0]:
                for j, s in enumerate(secs):
                    sacc.setdefault(s, {}).setdefault(a, []).append(v[j])
    results[bname] = {a: float(np.concatenate(acc[a]).mean()) for a in ARMS}
    n = len(np.concatenate(acc['sign']))
    results[bname]['n'] = n
    if sacc:
        sections[bname] = {s: {a: float(np.mean(d[a])) for a in ARMS}
                           for s, d in sacc.items()}
    print(f'  {bname} done (n={n})', flush=True)

print('\n=== CONTROL: sign - cosine must reproduce the frozen headlines ===')
ref = {'LME': 10.053783, 'PerLTQA': -6.274728, 'REALTALK': 5.300077, 'LoCoMo': 6.655046}
for b, r in results.items():
    d = 100 * (r['sign'] - r['cosine'])
    print(f'  {b:9s} {d:+11.6f}  (ref {ref[b]:+.6f})  diff {d-ref[b]:+.2e}'
          f'  {"PASS" if abs(d-ref[b]) < 1e-4 else "FAIL"}')

print('\n=== ALL ARMS, FR@3 ===')
print(f'  {"bench":9s} ' + ' '.join(f'{a:>10s}' for a in ARMS))
for b, r in results.items():
    print(f'  {b:9s} ' + ' '.join(f'{r[a]:>10.6f}' for a in ARMS))

print('\n=== THE QUESTION: does any 384-byte float arm beat the 12-byte sign arm? ===')
print(f'  {"bench":9s} {"sign":>10s} ' +
      ' '.join(f'{a+" vs sign":>17s}' for a in ARMS if a != 'sign'))
for b, r in results.items():
    row = [f'{100*(r[a]-r["sign"]):>+17.4f}' for a in ARMS if a != 'sign']
    print(f'  {b:9s} {r["sign"]:>10.6f} ' + ' '.join(row))
print('  positive => that FLOAT arm BEATS the sign arm (sign advantage erased)')

print('\n=== WHITENING: how much of the sign advantage does it explain? ===')
for b, r in results.items():
    gap = r['sign'] - r['cosine']
    closed = r['whitened'] - r['cosine']
    pct = 100 * closed / gap if abs(gap) > 1e-12 else float('nan')
    print(f'  {b:9s} sign-cos={100*gap:>+8.4f} pp  whit-cos={100*closed:>+8.4f} pp  '
          f'closed={pct:>7.1f}%  whit-sign={100*(r["whitened"]-r["sign"]):>+8.4f} pp')

if sections:
    print('\n=== PerLTQA sections ===')
    for b, secs in sections.items():
        print(f'  {"section":22s} ' + ' '.join(f'{a:>10s}' for a in ARMS))
        for s, r in sorted(secs.items(), key=lambda x: -(x[1]['sign'] - x[1]['cosine'])):
            print(f'  {s:22s} ' + ' '.join(f'{r[a]:>10.6f}' for a in ARMS))

json.dump({'results': results, 'sections': sections},
          open(os.path.join(OUT, 'baseline_strength.json'), 'w'), indent=1)
print('\nWROTE baseline_strength.json')
