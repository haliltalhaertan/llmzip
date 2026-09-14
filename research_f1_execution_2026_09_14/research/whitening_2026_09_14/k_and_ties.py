#!/usr/bin/env python3
"""Verify the framing session's two NEW claims that I have not independently checked.

CONVERGENCE FIRST (no action needed, recorded): that session independently rebuilt a
per-axis standardized cosine and reported sign winning 0 of 4 against it, with
LME -1.53 n.s., REALTALK -0.36 n.s., LoCoMo -2.46 significant, PerLTQA -7.68. Those
are my own whitening numbers with the sign flipped (I reported whitened-minus-sign:
+1.53, +0.36, +2.46, +7.68). Two independent implementations, identical values.

CLAIM A (NEW, unverified): "+10pp is the maximum over K" -- Delta keeps its sign at
K=1..10 but LongMemEval FLIPS to -1.71 pp at K=20. If true, the programme's headline
is the peak of a curve over an arbitrary parameter, which is a real scope limit.

CLAIM B (NEW, unverified): "not tie bookkeeping" -- under WORST-CASE adversarial tie
breaking the sign arm still leads by +7.9/+4.3/+5.2 pp, i.e. only ~20% of the margin
is hedging. This defends the result against the accusation that the exact-expectation
tie rule flatters the sign arm.

Tie conventions used here, all three computed exactly (no sampling):
  worst : ties filled with NON-gold first -> g_strict + max(0, slots - (bc - g_tied))
  expect: g_strict + g_tied * slots / bc                       (the frozen rule)
  best  : ties filled with gold first     -> g_strict + min(slots, g_tied)
"""
import glob, json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = os.path.dirname(os.path.abspath(__file__))
KS = [1, 2, 3, 5, 10, 20]


def fr_modes(S, G, gs, K):
    """Returns (worst, expect, best) FR@K per query."""
    S = np.asarray(S, float)
    N = S.shape[0]
    kk = min(K, N)
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    better = S > thr[None, :]
    equal = S == thr[None, :]
    strictly = better.sum(0)
    bc = equal.sum(0)
    slots = np.maximum(kk - strictly, 0)
    g_s = (G & better).sum(0)
    g_t = (G & equal).sum(0)
    nongold_tied = bc - g_t
    worst = g_s + np.maximum(0, slots - nongold_tied)
    best = g_s + np.minimum(slots, g_t)
    exp = g_s + np.where(bc > 0, g_t * (slots / np.maximum(bc, 1)), 0.0)
    return worst / gs, exp / gs, best / gs


def cos_b(C, Q):
    den = np.linalg.norm(C, axis=1)[:, None] * np.linalg.norm(Q, axis=1)[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        o = (C @ Q.T) / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def ham_b(C, Q):
    D0 = (C >= 0).astype(np.uint8); Q0 = (Q >= 0).astype(np.uint8)
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    return -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))


def load_lme():
    for f in sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g):
            yield np.asarray(d['C'], float), np.asarray(d['qC'], float)[None, :], [g]


def load_perltqa():
    A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for q in Qd.values():
        by.setdefault(q['char'], []).append(q)
    for ch, items in by.items():
        keep = [q for q in items if len(np.asarray(q['gold']).ravel())]
        if keep:
            yield (np.asarray(A[ch]['C'], float),
                   np.stack([np.asarray(q['qC'], float) for q in keep]),
                   [np.asarray(q['gold']).ravel().astype(int) for q in keep])


def load_realtalk():
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        gs = [np.asarray(g).ravel().astype(int) for g in d['gold_rows']]
        keep = [i for i, g in enumerate(gs) if len(g)]
        if keep:
            yield (np.asarray(d['C'], float), np.asarray(d['QC'], float)[keep],
                   [gs[i] for i in keep])


def load_locomo():
    for f in sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        i2r = d['id_to_row']; gs = []; idx = []
        for i, qa in enumerate(d['qas']):
            rows = [i2r[e] for e in (qa.get('raw_evidence') or []) if e in i2r]
            if rows:
                gs.append(np.asarray(sorted(set(rows)), int)); idx.append(i)
        if gs:
            yield np.asarray(d['C'], float), np.asarray(d['QC'], float)[idx], gs


LOADERS = {'LME': load_lme, 'PerLTQA': load_perltqa,
           'REALTALK': load_realtalk, 'LoCoMo': load_locomo}
res = {}
for bname, ld in LOADERS.items():
    acc = {K: {m: {'s': [], 'f': []} for m in ('worst', 'exp', 'best')} for K in KS}
    for C, Q, golds in ld():
        N, nq = C.shape[0], Q.shape[0]
        gs = np.array([len(g) for g in golds], float)
        G = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            G[g, j] = True
        Sh, Sc = ham_b(C, Q), cos_b(C, Q)
        for K in KS:
            for arm, S in (('s', Sh), ('f', Sc)):
                w, e, b = fr_modes(S, G, gs, K)
                acc[K]['worst'][arm].append(w)
                acc[K]['exp'][arm].append(e)
                acc[K]['best'][arm].append(b)
    res[bname] = {str(K): {m: {a: float(np.concatenate(acc[K][m][a]).mean())
                               for a in ('s', 'f')} for m in ('worst', 'exp', 'best')}
                  for K in KS}
    res[bname]['n'] = int(len(np.concatenate(acc[3]['exp']['s'])))
    print(f'  {bname} done', flush=True)

print('\n=== CONTROL at K=3, expectation rule (must match frozen) ===')
ref = {'LME': 10.053783, 'PerLTQA': -6.274728, 'REALTALK': 5.300077, 'LoCoMo': 6.655046}
for b, r in res.items():
    d = 100 * (r['3']['exp']['s'] - r['3']['exp']['f'])
    print(f'  {b:9s} {d:>+11.6f}  (ref {ref[b]:+.6f})  '
          f'{"PASS" if abs(d-ref[b])<1e-3 else "FAIL"}')

print('\n=== CLAIM A: is "+10 pp" the maximum over K? ===')
print('  Delta = sign - float, expectation tie rule, pp')
print(f'  {"bench":9s} ' + ' '.join(f'{"K="+str(K):>9s}' for K in KS) + f'  {"sign flips?":>12s}')
for b, r in res.items():
    row = [100 * (r[str(K)]['exp']['s'] - r[str(K)]['exp']['f']) for K in KS]
    signs = set(x > 0 for x in row)
    print(f'  {b:9s} ' + ' '.join(f'{x:>+9.4f}' for x in row) +
          f'  {("YES" if len(signs) > 1 else "no"):>12s}')

print('\n=== CLAIM B: how much of the margin is tie bookkeeping? ===')
print('  worst = all ties resolved AGAINST gold; best = all FOR gold; exp = frozen rule')
print(f'  {"bench":9s} {"worst":>10s} {"expect":>10s} {"best":>10s} {"hedging share":>14s}')
for b, r in res.items():
    w = 100 * (r['3']['worst']['s'] - r['3']['worst']['f'])
    e = 100 * (r['3']['exp']['s'] - r['3']['exp']['f'])
    bs = 100 * (r['3']['best']['s'] - r['3']['best']['f'])
    share = 100 * (e - w) / e if abs(e) > 1e-9 else float('nan')
    print(f'  {b:9s} {w:>+10.4f} {e:>+10.4f} {bs:>+10.4f} {share:>13.1f}%')
print('  hedging share = (expect - worst) / expect: the part of the margin that comes')
print('  from favourable tie accounting rather than from strictly closer documents.')

print('\n=== Does the sign advantage survive WORST-CASE ties at every K? ===')
print(f'  {"bench":9s} ' + ' '.join(f'{"K="+str(K):>9s}' for K in KS))
for b, r in res.items():
    row = [100 * (r[str(K)]['worst']['s'] - r[str(K)]['worst']['f']) for K in KS]
    print(f'  {b:9s} ' + ' '.join(f'{x:>+9.4f}' for x in row))

json.dump(res, open(os.path.join(OUT, 'k_and_ties.json'), 'w'), indent=1)
print('\nWROTE k_and_ties.json')
