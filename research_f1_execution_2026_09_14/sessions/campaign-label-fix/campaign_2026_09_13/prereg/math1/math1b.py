#!/usr/bin/env python3
"""MATH-1 follow-up: d2-parity wins/losses, z2 misfit test, left-tail analysis, mixing regimes.
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]"""
import json, pickle, sys
import numpy as np
sys.path.insert(0, '/tmp/math1')
from math1 import (load_all, exact_frac_r3, measured_frac_r3, tie_stats, hspec_qs_only, happly,
                   BUNDLE, PIL, PKLDIR, K, NT, stable_archive_seed)
from math import comb

lex, D0, Q0, GOLD, PR, QIDS, VAR = load_all()
RAND = [np.sort(np.random.default_rng(s).choice(96, 48, replace=False)) for s in (12000, 12001, 12002)]

# ---- per-question: TOP48 + 3 RAND seeds FR, d2 features on TOP48 ----
rows = []
for qi, qid in enumerate(QIDS):
    D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
    od = np.argsort(VAR[qid], kind='stable')[::-1]
    dT = np.count_nonzero(D[:, od[:48]] != Q[od[:48]][None, :], axis=1)
    eT = exact_frac_r3(dT, g); mT, trT = measured_frac_r3(dT, g, pr)
    frs = []
    for r in RAND:
        d = np.count_nonzero(D[:, r] != Q[r][None, :], axis=1)
        m, _ = measured_frac_r3(d, g, pr); frs.append(m)
    rm = float(np.mean(frs)); delta = mT - rm
    out = 'win' if delta > 1e-12 else ('loss' if delta < -1e-12 else 'tie')
    gidx = np.array(sorted(map(int, np.asarray(g).ravel())))
    dmin = int(dT[gidx].min())
    closer = int(np.count_nonzero(dT < dmin)); tie = int(np.count_nonzero(dT == dmin))
    rows.append({'qid': qid, 'top': mT, 'exact': eT, 'tvar': float(np.var(trT, ddof=1)),
                 'randmean': rm, 'delta': delta, 'out': out, 'closer': closer, 'tie': tie,
                 'ngold': len(gidx), 'S': float(np.mean([np.count_nonzero(dT < dT[i]) for i in gidx])),
                 'dgmin': dmin})
    if (qi + 1) % 100 == 0: print(f'  {qi+1}/470', flush=True)

W = [r for r in rows if r['out'] == 'win']; L = [r for r in rows if r['out'] == 'loss']; T = [r for r in rows if r['out'] == 'tie']
print(f"WTL vs RANDmean: {len(W)}/{len(T)}/{len(L)}")
print(f"closer wins={np.mean([r['closer'] for r in W]):.4f} losses={np.mean([r['closer'] for r in L]):.4f}")
print(f"tie wins={np.mean([r['tie'] for r in W]):.4f} losses={np.mean([r['tie'] for r in L]):.4f}")
print(f" exact-model gap on wins={np.mean([r['exact']-r['top'] for r in W]):.5f} (MC noise check ~0)")

# ---- z2 misfit test on TOP48: z=(m-e)/sqrt(tvar/20); E[z^2]~19/17=1.118 under exact model ----
z2 = []
for r in rows:
    v = r['tvar'] / NT
    if v > 0: z2.append((r['top'] - r['exact']) ** 2 / v)
z2 = np.array(z2)
print(f"z2: n={len(z2)} mean={z2.mean():.3f} (expect ~1.12 under exact model)")

# ---- left-tail: empirical non-gold P(d<dgmin) vs binomial plug-in ----
def lefttail(qid_list, colfn, b):
    emp, plu = [], []
    for qid in qid_list:
        D, Q, g = D0[qid], Q0[qid], GOLD[qid]
        cc = colfn(qid); d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
        gidx = np.array(sorted(map(int, np.asarray(g).ravel())))
        n = len(d); mask = np.ones(n, bool); mask[gidx] = False
        ng = d[mask]; dmin = int(d[gidx].min())
        emp.append(np.count_nonzero(ng < dmin) / len(ng))
        ph = float(ng.mean()) / b
        ph = min(max(ph, 1e-12), 1 - 1e-12)
        Flo = sum(comb(b, x) * ph**x * (1 - ph)**(b - x) for x in range(0, min(dmin, b + 1)))
        plu.append(Flo)
    return float(np.mean(emp)), float(np.mean(plu))
od_of = lambda qid: np.argsort(VAR[qid], kind='stable')[::-1]
for tag, fn, b in (('NATIVE96', lambda q: np.arange(96), 96), ('TOP48', lambda q: od_of(q)[:48], 48),
                    ('RAND48', lambda q: RAND[0], 48), ('BOT48', lambda q: od_of(q)[::-1][:48], 48)):
    e, p = lefttail(QIDS, fn, b)
    print(f"lefttail {tag}: empirical={e:.4f} binomial-plugin={p:.4f} ratio={e/max(p,1e-9):.1f}x")

# ---- mixing retrievable-regime stats (seeds 43001, 44001) ----
for s in (43001, 44001):
    qs = hspec_qs_only(s, 2)
    print(f'--- mixing seed {s} ---')
    for a in ('matched', 'random', 'antimatched'):
        Sret, Tret, dgr, dgb, fr = [], [], [], [], []
        for qi, qid in enumerate(QIDS):
            with open(PKLDIR/(qid + '.pkl'), 'rb') as f: o = pickle.load(f)
            C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
            g = np.asarray(o['gold']).ravel()
            var = C.var(axis=0); rd = np.argsort(var, kind='stable')[::-1]
            am = np.empty(96, dtype=int); am[0::2] = rd[:48]; am[1::2] = rd[::-1][:48]
            perm = {'random': np.random.default_rng(s).permutation(96),
                    'matched': np.argsort(var, kind='stable'), 'antimatched': am}[a]
            Cr = happly(C, perm, qs, 2); qr = happly(qC, perm, qs, 2)
            d = np.count_nonzero((Cr >= 0) != (qr >= 0)[None, :], axis=1)
            gidx = np.array(sorted(map(int, g)))
            m, _ = measured_frac_r3(d, g, PR[qid]); fr.append(m)
            for gi in gidx:
                S = int(np.count_nonzero(d < d[gi])); T = int(np.count_nonzero(d == d[gi]))
                if S < 3: Sret.append(S); Tret.append(T); dgr.append(int(d[gi]))
                else: dgb.append(int(d[gi]))
        print(f"{a}: FR={np.mean(fr):.5f} P(S<3)={len(Sret)/(len(Sret)+len(dgb)):.3f} "
              f"T|retr={np.mean(Tret):.2f} dg|retr={np.mean(dgr):.2f} dg|buried={np.mean(dgb):.2f}")
json.dump({'ok': True}, open('/tmp/math1/math1b_done.json', 'w'))
