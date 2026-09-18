#!/usr/bin/env python3
"""Significance + robustness for the whitening result.

FINDING TO VERIFY: whitened cosine (384 B) beats the sign arm (12 B) on all four
benchmarks, and closes >100% of the sign-vs-cosine gap on three of them. If true,
the programme's headline "+10 pp for 12 bytes" is a statement about an UNWHITENED
baseline, not about quantization.

Before publishing I need:
 1. PAIRED bootstrap CIs (per query) on (whitened - sign) and (whitened - cosine).
    Clustered by archive where archives hold many queries, since queries in one
    archive are not independent.
 2. Robustness of whitening to its own free choice: sigma is estimated per archive
    from the documents. Test sigma floors / shrinkage so the result is not an
    artifact of dividing by a tiny sigma.
 3. The storage-honest framing: whitened cosine costs 384 B. Also test a CHEAP
    whitened arm -- sign bits of the WHITENED vector (still 12 B) -- which asks
    whether whitening helps the 12-byte method too.
"""
import glob, json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))


def fr_exact(S, Gmask, gsize, K=K):
    S = np.asarray(S, float)
    kk = min(K, S.shape[0])
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    better = S > thr[None, :]; equal = S == thr[None, :]
    slots = np.maximum(kk - better.sum(0), 0); bc = equal.sum(0)
    g_s = (Gmask & better).sum(0); g_t = (Gmask & equal).sum(0)
    frac = np.where(bc > 0, g_t * (slots / np.maximum(bc, 1)), 0.0)
    return (g_s + frac) / gsize


def cos_b(Cm, Qm):
    den = np.linalg.norm(Cm, axis=1)[:, None] * np.linalg.norm(Qm, axis=1)[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        o = (Cm @ Qm.T) / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def ham_b(D0, Q0):
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    return -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))


def load_lme():
    for i, f in enumerate(sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl'))):
        d = pickle.load(open(f, 'rb'))
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g):
            yield (str(i), np.asarray(d['C'], float),
                   np.asarray(d['qC'], float)[None, :], [g], [''])


def load_perltqa():
    A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for qid, q in Qd.items():
        by.setdefault(q['char'], []).append(q)
    for ch, items in by.items():
        C = np.asarray(A[ch]['C'], float)
        keep = [q for q in items if len(np.asarray(q['gold']).ravel())]
        if not keep:
            continue
        Q = np.stack([np.asarray(q['qC'], float) for q in keep])
        yield (ch, C, Q, [np.asarray(q['gold']).ravel().astype(int) for q in keep],
               [q.get('section', '') for q in keep])


def load_realtalk():
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); Q = np.asarray(d['QC'], float)
        golds = [np.asarray(g).ravel().astype(int) for g in d['gold_rows']]
        keep = [i for i, g in enumerate(golds) if len(g)]
        if keep:
            yield (os.path.basename(f), C, Q[keep], [golds[i] for i in keep],
                   [''] * len(keep))


def load_locomo():
    for f in sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); Q = np.asarray(d['QC'], float)
        i2r = d['id_to_row']; golds = []; idx = []
        for i, qa in enumerate(d['qas']):
            rows = [i2r[e] for e in (qa.get('raw_evidence') or []) if e in i2r]
            if rows:
                golds.append(np.asarray(sorted(set(rows)), int)); idx.append(i)
        if golds:
            yield (os.path.basename(f), C, Q[idx], golds, [''] * len(golds))


LOADERS = {'LME': load_lme, 'PerLTQA': load_perltqa,
           'REALTALK': load_realtalk, 'LoCoMo': load_locomo}
FLOORS = [0.0, 0.01, 0.05, 0.10]          # sigma floor as a fraction of mean sigma
out = {}

for bname, ld in LOADERS.items():
    per = {a: [] for a in ('sign', 'cosine', 'whitened', 'signwhit')}
    per.update({f'whit_floor{f}': [] for f in FLOORS})
    clusters = []
    secs_all = []
    for cid, C, Q, golds, secs in ld():
        N, nq = C.shape[0], Q.shape[0]
        gs = np.array([len(g) for g in golds], float)
        G = np.zeros((N, nq), bool)
        for j, g in enumerate(golds):
            G[g, j] = True
        sig = C.std(axis=0)
        msig = sig[sig > 0].mean() if (sig > 0).any() else 1.0
        per['sign'].append(fr_exact(ham_b((C >= 0).astype(np.uint8),
                                          (Q >= 0).astype(np.uint8)), G, gs))
        per['cosine'].append(fr_exact(cos_b(C, Q), G, gs))
        for f in FLOORS:
            s = np.maximum(sig, f * msig)
            s = np.where(s > 0, s, 1.0)
            v = fr_exact(cos_b(C / s, Q / s), G, gs)
            per[f'whit_floor{f}'].append(v)
            if f == 0.0:
                per['whitened'].append(v)
                # 12-byte arm on whitened coordinates
                per['signwhit'].append(fr_exact(
                    ham_b(((C / s) >= 0).astype(np.uint8), ((Q / s) >= 0).astype(np.uint8)),
                    G, gs))
        clusters += [cid] * nq
        secs_all += list(secs)
    arr = {a: np.concatenate(v) for a, v in per.items()}
    cl = np.array(clusters)
    uc = np.unique(cl)
    idx_by = {c: np.where(cl == c)[0] for c in uc}
    rng = np.random.default_rng(99)

    def cluster_boot(diff, nboot=2000):
        vals = np.empty(nboot)
        for i in range(nboot):
            pick = rng.choice(uc, len(uc), replace=True)
            ii = np.concatenate([idx_by[c] for c in pick])
            vals[i] = diff[ii].mean()
        return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))

    o = {'n': int(len(arr['sign'])), 'n_clusters': int(len(uc))}
    for a in arr:
        o[a] = float(arr[a].mean())
    for label, d in (('whit_minus_sign', arr['whitened'] - arr['sign']),
                     ('whit_minus_cos', arr['whitened'] - arr['cosine']),
                     ('sign_minus_cos', arr['sign'] - arr['cosine']),
                     ('signwhit_minus_sign', arr['signwhit'] - arr['sign'])):
        lo, hi = cluster_boot(d)
        o[label] = {'pp': float(100 * d.mean()), 'ci_pp': [100 * lo, 100 * hi],
                    'excludes_zero': bool(not (lo < 0 < hi))}
    out[bname] = o
    print(f'  {bname} done', flush=True)

print('\n=== PAIRED, CLUSTER-BOOTSTRAPPED (clusters = archives) ===')
print(f'  {"bench":9s} {"n":>6s} {"clus":>5s} {"whit-sign pp":>14s} {"95% CI":>22s} {"sig?":>6s}')
for b, o in out.items():
    d = o['whit_minus_sign']
    print(f'  {b:9s} {o["n"]:>6d} {o["n_clusters"]:>5d} {d["pp"]:>+14.4f} '
          f'[{d["ci_pp"][0]:+.4f},{d["ci_pp"][1]:+.4f}] {str(d["excludes_zero"]):>6s}')

print('\n=== How much of the sign advantage does whitening account for? ===')
for b, o in out.items():
    sc = o['sign_minus_cos']['pp']; wc = o['whit_minus_cos']['pp']
    print(f'  {b:9s} sign-cos={sc:>+8.4f}  whit-cos={wc:>+8.4f}  '
          f'ratio={wc/sc if abs(sc)>1e-9 else float("nan"):>7.2f}x  '
          f'CI(whit-cos)=[{o["whit_minus_cos"]["ci_pp"][0]:+.3f},'
          f'{o["whit_minus_cos"]["ci_pp"][1]:+.3f}]')

print('\n=== ROBUSTNESS: sigma floor (is whitening exploiting tiny sigmas?) ===')
print(f'  {"bench":9s} ' + ' '.join(f'{"floor="+str(f):>13s}' for f in FLOORS))
for b, o in out.items():
    print(f'  {b:9s} ' + ' '.join(f'{o[f"whit_floor{f}"]:>13.6f}' for f in FLOORS))

print('\n=== THE 12-BYTE QUESTION: does whitening help the SIGN arm too? ===')
print('  sign bits of the whitened vector -- still 12 bytes')
for b, o in out.items():
    d = o['signwhit_minus_sign']
    print(f'  {b:9s} sign={o["sign"]:.6f}  sign-on-whitened={o["signwhit"]:.6f}  '
          f'{d["pp"]:>+8.4f} pp  CI[{d["ci_pp"][0]:+.3f},{d["ci_pp"][1]:+.3f}]  '
          f'sig={d["excludes_zero"]}')

json.dump(out, open(os.path.join(OUT, 'whitening_significance.json'), 'w'), indent=1)
print('\nWROTE whitening_significance.json')
