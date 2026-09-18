#!/usr/bin/env python3
"""Held-out test of the interior-clip finding, and its convergence with whitening.

WHAT THE BRAINSTORM SESSION FOUND (LongMemEval only): scoring with a per-axis CLIPPED
product, score = sum_j clip(p_j, +-t), interpolates cosine (t=inf) to Hamming (t->0).
It peaks at an INTERIOR t ~ 1e-3 with FR@3 0.5626, beating cosine by +12.10 pp and
beating sign by +2.05 pp (t=2.10). The session flagged its own weakness: that peak is
the MAXIMUM OVER 8 THRESHOLDS on the same data, so the margin over sign is
selection-biased and the honest interval is wider.

CONVERGENCE WORTH NOTING: my own whitening run found that softsign = cosine on
tanh(C/sigma) -- a SOFT clip -- beat the sign arm on all four benchmarks
(LME 0.568085 vs 0.542134). Two independent routes, two different parameterisations,
same conclusion: the operative variable is the per-axis nonlinearity, and HARD sign
(infinite clipping) is not the optimum.

THE HONEST TEST, run here:
 1. Select t on LongMemEval ALONE (the benchmark the session used).
 2. Apply that FROZEN t to PerLTQA, REALTALK and LoCoMo -- never seen during selection.
 3. Report paired, cluster-bootstrapped intervals on (clip - sign) out of sample.
If the interior clip only wins where it was tuned, it is selection bias and dies.
"""
import glob, json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))
GRID = [1e-6, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2]


def fr_exact(S, G, gs, K=K):
    S = np.asarray(S, float)
    kk = min(K, S.shape[0])
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    better = S > thr[None, :]; equal = S == thr[None, :]
    slots = np.maximum(kk - better.sum(0), 0); bc = equal.sum(0)
    g_s = (G & better).sum(0); g_t = (G & equal).sum(0)
    return (g_s + np.where(bc > 0, g_t * (slots / np.maximum(bc, 1)), 0.0)) / gs


def arms(C, Q, ts):
    """Per-axis normalised products, clipped at +-t. t=inf -> cosine; t->0 -> sign."""
    nC = np.linalg.norm(C, axis=1)[:, None]
    nQ = np.linalg.norm(Q, axis=1)[None, :]
    out = {}
    # p_{ij,axis} built implicitly: clip then sum over axes
    for t in ts:
        acc = np.zeros((C.shape[0], Q.shape[0]))
        for j in range(C.shape[1]):
            p = np.outer(C[:, j], Q[:, j]) / (nC * nQ + 1e-30)
            acc += np.clip(p, -t, t)
        out[t] = acc
    cs = (C @ Q.T) / (nC * nQ + 1e-30)
    out['cos'] = np.nan_to_num(cs, nan=-2.0)
    D0 = (C >= 0).astype(np.uint8); Q0 = (Q >= 0).astype(np.uint8)
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    out['sign'] = -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))
    sig = C.std(axis=0); sig = np.where(sig > 0, sig, 1.0)
    Cw, Qw = np.tanh(C / sig), np.tanh(Q / sig)
    nw = np.linalg.norm(Cw, axis=1)[:, None] * np.linalg.norm(Qw, axis=1)[None, :]
    out['softsign'] = np.nan_to_num((Cw @ Qw.T) / (nw + 1e-30), nan=-2.0)
    return out


def load_lme(limit=470):
    for i, f in enumerate(sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl'))):
        if i >= limit:
            break
        d = pickle.load(open(f, 'rb'))
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g):
            yield str(i), np.asarray(d['C'], float), np.asarray(d['qC'], float)[None, :], [g]


def load_perltqa():
    A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for q in Qd.values():
        by.setdefault(q['char'], []).append(q)
    for ch, items in by.items():
        keep = [q for q in items if len(np.asarray(q['gold']).ravel())][:120]
        if keep:
            yield (ch, np.asarray(A[ch]['C'], float),
                   np.stack([np.asarray(q['qC'], float) for q in keep]),
                   [np.asarray(q['gold']).ravel().astype(int) for q in keep])


def load_realtalk():
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        gs = [np.asarray(g).ravel().astype(int) for g in d['gold_rows']]
        keep = [i for i, g in enumerate(gs) if len(g)][:120]
        if keep:
            yield (os.path.basename(f), np.asarray(d['C'], float),
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
            yield (os.path.basename(f), np.asarray(d['C'], float),
                   np.asarray(d['QC'], float)[idx[:120]], gs[:120])


LOADERS = {'LME': load_lme, 'PerLTQA': load_perltqa,
           'REALTALK': load_realtalk, 'LoCoMo': load_locomo}
res = {}
for bname, ld in LOADERS.items():
    per = {k: [] for k in GRID + ['cos', 'sign', 'softsign']}
    cl = []
    for cid, C, Q, golds in ld():
        N, nq = C.shape[0], Q.shape[0]
        gs = np.array([len(g) for g in golds], float)
        G = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            G[g, j] = True
        a = arms(C, Q, GRID)
        for k in per:
            per[k].append(fr_exact(a[k], G, gs))
        cl += [cid] * nq
    res[bname] = {'arr': {k: np.concatenate(v) for k, v in per.items()},
                  'cl': np.array(cl)}
    print(f'  {bname} done', flush=True)

# --- step 1: select t on LongMemEval only ---
L = res['LME']['arr']
best_t = max(GRID, key=lambda t: L[t].mean())
print(f'\n=== STEP 1: threshold selected on LongMemEval ALONE ===')
for t in GRID:
    mark = '  <-- selected' if t == best_t else ''
    print(f'  t={t:<8g} FR@3={L[t].mean():.6f}{mark}')
print(f'  sign={L["sign"].mean():.6f}  cosine={L["cos"].mean():.6f}  '
      f'softsign={L["softsign"].mean():.6f}')


def cboot(d, cl, nboot=2000, seed=5):
    rng = np.random.default_rng(seed)
    uc = np.unique(cl)
    idx = {c: np.where(cl == c)[0] for c in uc}
    v = np.empty(nboot)
    for i in range(nboot):
        pick = rng.choice(uc, len(uc), replace=True)
        v[i] = d[np.concatenate([idx[c] for c in pick])].mean()
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


print(f'\n=== STEP 2: apply the FROZEN t={best_t:g} to the three HELD-OUT benchmarks ===')
print(f'  {"bench":9s} {"sign":>9s} {"clip@t":>9s} {"clip-sign pp":>13s} {"95% CI":>20s} {"sig?":>6s}')
summary = {}
for b in ['LME', 'PerLTQA', 'REALTALK', 'LoCoMo']:
    a = res[b]['arr']; cl = res[b]['cl']
    d = a[best_t] - a['sign']
    lo, hi = cboot(d, cl)
    tag = '(tuned)' if b == 'LME' else ''
    sig = 'YES' if not (lo < 0 < hi) else 'no'
    summary[b] = {'sign': float(a['sign'].mean()), 'clip': float(a[best_t].mean()),
                  'diff_pp': float(100 * d.mean()), 'ci': [100 * lo, 100 * hi]}
    print(f'  {b:9s} {a["sign"].mean():>9.6f} {a[best_t].mean():>9.6f} '
          f'{100*d.mean():>+13.4f} [{100*lo:+.3f},{100*hi:+.3f}] {sig:>6s} {tag}')

print(f'\n=== STEP 3: does the SOFT clip (tanh) agree? independent parameterisation ===')
print(f'  {"bench":9s} {"softsign-sign pp":>17s} {"95% CI":>20s} {"agrees w/ clip?":>16s}')
for b in ['LME', 'PerLTQA', 'REALTALK', 'LoCoMo']:
    a = res[b]['arr']; cl = res[b]['cl']
    d = a['softsign'] - a['sign']
    lo, hi = cboot(d, cl)
    agree = (d.mean() > 0) == (summary[b]['diff_pp'] > 0)
    print(f'  {b:9s} {100*d.mean():>+17.4f} [{100*lo:+.3f},{100*hi:+.3f}] {str(agree):>16s}')

print('\n=== VERDICT INPUT ===')
held = [b for b in ['PerLTQA', 'REALTALK', 'LoCoMo']]
wins = sum(1 for b in held if summary[b]['ci'][0] > 0)
print(f'  held-out benchmarks where clip STRICTLY beats sign: {wins}/3')
print(f'  if 0/3, the +2.05 pp was selection bias on the tuning benchmark.')

json.dump({'best_t': best_t, 'summary': summary},
          open(os.path.join(OUT, 'clip_heldout.json'), 'w'), indent=1)
print('\nWROTE clip_heldout.json')
