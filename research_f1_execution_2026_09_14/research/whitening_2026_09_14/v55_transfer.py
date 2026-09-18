#!/usr/bin/env python3
"""Two tests imported from the V55/Gemini thread, applied to THIS session's findings.

TRANSFER 1 -- SELECTION BIAS IN AXIS RANKING.
That thread measured: sorting axes by sample variance inflates the measured top-k
share even under PURE NOISE (isotropic truth 12.5% -> sorted top-48 of noise gives
13.825%) and manufactures a fake power law (p ~ 0.059 where truth is 0).
My axis-budget finding ranks axes by mean_i(C_ij^2) computed on the SAME documents
I then retrieve from, with N~500 samples for 96 axes. So part of the TOP/BOT gap
could be selection noise rather than real structure.
CLEAN TEST: rank the axes on HALF the documents, evaluate on all. If the BOT-vs-TOP
gap survives out-of-sample ranking, it is real. If it shrinks toward zero, part of
what I published was selection bias.

TRANSFER 2 -- VARIANCE CONCENTRATION AS THE MISSING ANCHOR FOR WHITENING.
That thread measured f_12,B = 35.7% on LongMemEval TF-IDF SVD: 12 of 96 axes carry
35.7% of variance against an isotropic 12.5%, i.e. 2.85x concentration.
My whitening result says the sign advantage IS axis equalisation. Those two connect:
cosine weights axes by magnitude, so the MORE concentrated the variance, the more
cosine over-weights a few axes, and the more equalisation should gain.
PREDICTION (frozen here, before running): across the four benchmarks and across the
30 PerLTQA archives, HIGHER variance concentration should go with a LARGER whitening
gain (whitened - cosine). If concentration does not predict the gain, my proposed
mechanism loses its quantitative leg.
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
    better = S > thr[None, :]; equal = S == thr[None, :]
    slots = np.maximum(kk - better.sum(0), 0); bc = equal.sum(0)
    g_s = (G & better).sum(0); g_t = (G & equal).sum(0)
    return (g_s + np.where(bc > 0, g_t * (slots / np.maximum(bc, 1)), 0.0)) / gs


def cos_b(C, Q):
    den = np.linalg.norm(C, axis=1)[:, None] * np.linalg.norm(Q, axis=1)[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        o = (C @ Q.T) / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def ham_b(D0, Q0):
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
M = 48
res = {}

for bname, ld in LOADERS.items():
    ins, out_, rnd = [], [], []
    conc12, conc48, whgain, nlist = [], [], [], []
    noise12 = []
    rng = np.random.default_rng(7)
    for C, Q, golds in ld():
        N, D = C.shape
        nq = Q.shape[0]
        gs = np.array([len(g) for g in golds], float)
        G = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            G[g, j] = True
        v = (C ** 2).mean(axis=0)

        # --- TRANSFER 1: in-sample vs split-half axis ranking ---
        order_in = np.argsort(-v, kind='stable')
        half = rng.permutation(N)[: max(2, N // 2)]
        order_out = np.argsort(-(C[half] ** 2).mean(axis=0), kind='stable')

        def gap(order):
            top, bot = order[:M], order[-M:]
            st = fr_exact(ham_b((C[:, top] >= 0).astype(np.uint8),
                                (Q[:, top] >= 0).astype(np.uint8)), G, gs)
            sb = fr_exact(ham_b((C[:, bot] >= 0).astype(np.uint8),
                                (Q[:, bot] >= 0).astype(np.uint8)), G, gs)
            return sb - st

        ins.append(gap(order_in))
        out_.append(gap(order_out))
        ridx = rng.permutation(D)
        rnd.append(gap(ridx))

        # --- noise baseline for the concentration measure ---
        Z = rng.normal(size=(N, D))
        Z -= Z.mean(0)
        vz = np.sort((Z ** 2).mean(axis=0))[::-1]
        noise12.append(vz[:12].sum() / vz.sum())

        # --- TRANSFER 2: concentration vs whitening gain, per archive ---
        vs = np.sort(v)[::-1]
        conc12.append(vs[:12].sum() / vs.sum())
        conc48.append(vs[:48].sum() / vs.sum())
        sig = C.std(axis=0); sig = np.where(sig > 0, sig, 1.0)
        wc = fr_exact(cos_b(C / sig, Q / sig), G, gs).mean()
        cc = fr_exact(cos_b(C, Q), G, gs).mean()
        whgain.append(100 * (wc - cc))
        nlist.append(N)

    a_in = np.concatenate(ins); a_out = np.concatenate(out_); a_rnd = np.concatenate(rnd)
    res[bname] = {
        'n_q': int(len(a_in)), 'n_arch': len(conc12),
        'gap_insample_pp': float(100 * a_in.mean()),
        'gap_splithalf_pp': float(100 * a_out.mean()),
        'gap_randomorder_pp': float(100 * a_rnd.mean()),
        'f12_mean': float(np.mean(conc12)), 'f12_noise_mean': float(np.mean(noise12)),
        'f48_mean': float(np.mean(conc48)),
        'whgain_mean_pp': float(np.mean(whgain)),
        'per_archive': {'f12': conc12, 'whgain': whgain, 'N': nlist},
    }
    print(f'  {bname} done ({len(conc12)} archives)', flush=True)

print('\n=== TRANSFER 1: is the BOT-vs-TOP gap selection bias? ===')
print('  gap = FR@3(BOT-48) - FR@3(TOP-48), in pp. Higher = low-variance axes better.')
print(f'  {"bench":9s} {"in-sample":>11s} {"split-half":>11s} {"random order":>13s} {"survives?":>10s}')
for b, r in res.items():
    surv = 'YES' if abs(r['gap_splithalf_pp']) > 0.5 * abs(r['gap_insample_pp']) else 'SHRINKS'
    print(f'  {b:9s} {r["gap_insample_pp"]:>+11.4f} {r["gap_splithalf_pp"]:>+11.4f} '
          f'{r["gap_randomorder_pp"]:>+13.4f} {surv:>10s}')
print('  random-order column is the null: axis identity scrambled, so it should be ~0.')

print('\n=== Finite-sample inflation check (the V55 thread\'s warning) ===')
print(f'  {"bench":9s} {"f12 real":>10s} {"f12 noise":>10s} {"isotropic":>10s} {"real/noise":>11s}')
for b, r in res.items():
    print(f'  {b:9s} {100*r["f12_mean"]:>9.3f}% {100*r["f12_noise_mean"]:>9.3f}% '
          f'{12/96*100:>9.3f}% {r["f12_mean"]/r["f12_noise_mean"]:>11.3f}x')
print('  noise column shows how much of the measured concentration is sorting artifact.')

print('\n=== TRANSFER 2: does variance concentration predict the whitening gain? ===')
print(f'  {"bench":9s} {"f12":>8s} {"f48":>8s} {"whiten gain pp":>15s}')
for b, r in res.items():
    print(f'  {b:9s} {100*r["f12_mean"]:>7.2f}% {100*r["f48_mean"]:>7.2f}% '
          f'{r["whgain_mean_pp"]:>+15.4f}')

x = [res[b]['f12_mean'] for b in res]; y = [res[b]['whgain_mean_pp'] for b in res]
print(f'\n  across the 4 benchmarks: r(f12, whitening gain) = {np.corrcoef(x, y)[0,1]:+.4f} (n=4)')
p = res['PerLTQA']['per_archive']
if len(p['f12']) > 5:
    rr = np.corrcoef(p['f12'], p['whgain'])[0, 1]
    print(f'  across the {len(p["f12"])} PerLTQA archives: r = {rr:+.4f}')
    rn = np.corrcoef(p['N'], p['whgain'])[0, 1]
    print(f'  control r(N, whitening gain) = {rn:+.4f}  (guards against an archive-size proxy)')

json.dump(res, open(os.path.join(OUT, 'v55_transfer.json'), 'w'), indent=1)
print('\nWROTE v55_transfer.json')
