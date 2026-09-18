#!/usr/bin/env python3
"""MATH-1d: bootstrap R-test per panel arm + T|retrievable joint check.
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]"""
import json, sys
import numpy as np
sys.path.insert(0, '/tmp/math1')
from math1 import load_all, exact_frac_r3, measured_frac_r3, panel_cols
from math import comb
lex, D0, Q0, GOLD, PR, QIDS, VAR = load_all()
R48 = np.sort(np.random.default_rng(12000).choice(96, 48, replace=False))
rng = np.random.default_rng(999001)
B = 3000
for a in ['NATIVE96', 'SPREAD48', 'TOP48', 'RAND48_s0', 'BOT48']:
    Xobs, Xexp, boot = 0.0, 0.0, np.zeros(B)
    for qi, qid in enumerate(QIDS):
        D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
        cc = panel_cols(VAR, qid, R48)[a]
        d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
        e = exact_frac_r3(d, g); m, tr = measured_frac_r3(d, g, pr)
        tr = np.array(tr); tv = tr.var(ddof=1) / 20
        Xobs += (m - e) ** 2; Xexp += tv
        S = rng.choice(tr, size=(B, 20))
        mb = S.mean(axis=1); vb = S.var(axis=1, ddof=1) / 20
        boot += (mb - e) ** 2
    R = Xobs / Xexp
    # null distribution of R: replicate numerator AND denominator
    bootR = np.zeros(B)
    for qi, qid in enumerate(QIDS):
        D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
        cc = panel_cols(VAR, qid, R48)[a]
        d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
        e = exact_frac_r3(d, g); m, tr = measured_frac_r3(d, g, pr)
        tr = np.array(tr)
        S = rng.choice(tr, size=(B, 20))
        bootR += (S.mean(axis=1) - e) ** 2
    # denominator under null resampled independently
    den = np.zeros(B)
    for qi, qid in enumerate(QIDS):
        D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
        cc = panel_cols(VAR, qid, R48)[a]
        d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
        e = exact_frac_r3(d, g); m, tr = measured_frac_r3(d, g, pr)
        S = rng.choice(np.array(tr), size=(B, 20))
        den += S.var(axis=1, ddof=1) / 20
    Rn = bootR / np.maximum(den, 1e-300)
    print(f"{a}: R=Xobs/Xexp={R:.3f} nullmean={Rn.mean():.3f} null95=[{np.percentile(Rn,2.5):.3f},{np.percentile(Rn,97.5):.3f}] P(Rn>=R)={(Rn>=R).mean():.4f}")

# ---- T|retrievable(S<3): empirical vs binomial-plugin, TOP48 vs RAND48 ----
for tag, fn in (('TOP48', lambda q: np.argsort(VAR[q], kind='stable')[::-1][:48]), ('RAND48', lambda q: R48)):
    Te, Tp, n = [], [], 0
    for qid in QIDS:
        D, Q, g = D0[qid], Q0[qid], GOLD[qid]
        cc = fn(qid); d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
        gidx = np.array(sorted(map(int, np.asarray(g).ravel())))
        n_ = len(d); mask = np.ones(n_, bool); mask[gidx] = False
        ng = d[mask]; b = 48; ph = min(max(float(ng.mean()) / b, 1e-12), 1 - 1e-12)
        for gi in gidx:
            if int(np.count_nonzero(d < d[gi])) < 3:
                n += 1; Te.append(int(np.count_nonzero(d == d[gi])))
                dg = int(d[gi])
                Tp.append(len(ng) * (comb(b, dg) * ph**dg * (1 - ph)**(b - dg)) if 0 <= dg <= b else 0.0)
    print(f"{tag} retrievable golds: n={n} T_emp={np.mean(Te):.2f} T_plugin={np.mean(Tp):.2f}")
json.dump({'ok': True}, open('/tmp/math1/math1d_done.json', 'w'))
