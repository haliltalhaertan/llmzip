#!/usr/bin/env python3
"""MATH-1c: z2 bootstrap null, plugin tie-mass gap, within-pair covariance.
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]"""
import json, pickle, sys
import numpy as np
sys.path.insert(0, '/tmp/math1')
from math1 import (load_all, exact_frac_r3, measured_frac_r3, hspec_qs_only, happly,
                   PKLDIR, K, NT)
from math import comb
lex, D0, Q0, GOLD, PR, QIDS, VAR = load_all()

# ---- (a) z2 bootstrap null for TOP48 ----
rng = np.random.default_rng(31337)
zobs, znull, zmax = [], [], 0.0
for qi, qid in enumerate(QIDS):
    D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
    od = np.argsort(VAR[qid], kind='stable')[::-1]
    d = np.count_nonzero(D[:, od[:48]] != Q[od[:48]][None, :], axis=1)
    e = exact_frac_r3(d, g); m, tr = measured_frac_r3(d, g, pr)
    tr = np.array(tr); v = tr.var(ddof=1) / NT
    if v > 0:
        zobs.append((m - e) ** 2 / v); zmax = max(zmax, (m - e) ** 2 / v)
        # null: 20 iid draws from empirical trial law, truth = e
        S = rng.choice(tr, size=(4000, 20), replace=True)
        mb = S.mean(axis=1); vb = S.var(axis=1, ddof=1) / NT
        ok = vb > 0
        znull.extend(list(((mb[ok] - e) ** 2) / vb[ok]))
zobs, znull = np.array(zobs), np.array(znull)
print(f"z2 obs mean={zobs.mean():.3f} median={np.median(zobs):.3f} max={zmax:.1f} | null mean={znull.mean():.3f} median={np.median(znull):.3f}")
print(f"frac obs z2>10: {(zobs>10).mean():.3f} | null: {(znull>10).mean():.4f}")

# ---- (b) plugin-implied tie mass T vs empirical, per arm ----
def tiemass(colfn, b):
    Te, Tp = [], []
    for qid in QIDS:
        D, Q, g = D0[qid], Q0[qid], GOLD[qid]
        cc = colfn(qid); d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
        gidx = np.array(sorted(map(int, np.asarray(g).ravel())))
        n = len(d); mask = np.ones(n, bool); mask[gidx] = False
        ng = d[mask]; ph = min(max(float(ng.mean()) / b, 1e-12), 1 - 1e-12)
        for gi in gidx:
            dg = int(d[gi])
            Te.append(int(np.count_nonzero(d == dg)))
            Tp.append(len(ng) * (comb(b, dg) * ph**dg * (1 - ph)**(b - dg)) if 0 <= dg <= b else 0.0)
    return float(np.mean(Te)), float(np.mean(Tp))
od_of = lambda qid: np.argsort(VAR[qid], kind='stable')[::-1]
R48 = np.sort(np.random.default_rng(12000).choice(96, 48, replace=False))
for tag, fn, b in (('NATIVE96', lambda q: np.arange(96), 96), ('TOP48', lambda q: od_of(q)[:48], 48),
                    ('SPREAD48', lambda q: od_of(q)[::2][:48], 48),
                    ('RAND48', lambda q: R48, 48), ('BOT48', lambda q: od_of(q)[::-1][:48], 48)):
    e, p = tiemass(fn, b)
    print(f"T {tag}: empirical={e:.2f} plugin={p:.2f} excess={e-p:.2f}")

# ---- (c) within-pair agreement covariance per mixing arm (seed 44001) ----
s = 44001; qs = hspec_qs_only(s, 2)
covs = {a: [] for a in ('matched', 'random', 'antimatched')}
for qi, qid in enumerate(QIDS):
    with open(PKLDIR/(qid + '.pkl'), 'rb') as f: o = pickle.load(f)
    C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
    var = C.var(axis=0); rd = np.argsort(var, kind='stable')[::-1]
    am = np.empty(96, dtype=int); am[0::2] = rd[:48]; am[1::2] = rd[::-1][:48]
    perms = {'random': np.random.default_rng(s).permutation(96),
             'matched': np.argsort(var, kind='stable'), 'antimatched': am}
    for a, perm in perms.items():
        Cr = happly(C, perm, qs, 2); qr = happly(qC, perm, qs, 2)
        A = ((Cr >= 0) == (qr >= 0)[None, :]).astype(float)  # (n,96) agreement
        Ac = A - A.mean(axis=0, keepdims=True)
        Cv = (Ac.T @ Ac) / (len(A) - 1)  # 96x96 cov across docs
        w = float(np.mean([Cv[2 * j, 2 * j + 1] for j in range(48)]))
        covs[a].append(w)
    if (qi + 1) % 150 == 0: print(f'  cov {qi+1}/470', flush=True)
for a in ('matched', 'random', 'antimatched'):
    print(f"within-pair cov {a}: mean={np.mean(covs[a]):.5f}")
json.dump({'ok': True}, open('/tmp/math1/math1c_done.json', 'w'))
