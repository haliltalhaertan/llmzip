# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# cm_test.py — FOLLOW-UP: does a shared background component on high-variance axes
# (a) amplify Delta to real magnitudes, (b) reproduce the rising dimension-matched
# budget curve, (c) explain why the locus proxy reads top-loaded on sign-positive corpora?
# Model: docs carry a common direction u (support: top-16 variance axes) with per-doc
# loading L_i; the query shares the subspace with a FRESH loading (same topic, new doc).
# Per-axis variance is renormalized to s_j^2 so the spectrum dial stays fixed.
import numpy as np, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth import spectrum, draw, locus_mask, fr3_exact, delta_of, budget_curve

D = 96
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cm_results.json')

def gen_cm(rng, N=500, alpha=1.0, shape='gauss', locus='broad', gamma=0.0,
           sigma=1.0, beta=1.0, nq=400):
    s = spectrum(alpha)
    top = np.argsort(-s)[:16]
    u = np.zeros(D); u[top] = rng.choice([-1.0, 1.0], 16); u /= np.linalg.norm(u)
    den = np.sqrt(1.0 + (gamma ** 2) * (u ** 2))  # per-axis renorm keeps Var=s^2
    L = rng.standard_normal(N)
    C = (draw(rng, shape, (N, D)) + gamma * L[:, None] * u[None, :]) / den * s
    w = locus_mask(locus, s, rng)
    Q, G = [], []
    for _ in range(nq):
        g = rng.choice(N, 1)
        m = C[g[0]]
        Lq = rng.standard_normal()
        q = (beta * (w * m) + sigma * (draw(rng, shape, D) * s)
             + gamma * Lq * u / den * s)
        Q.append(q); G.append(g)
    return C, np.array(Q), G, s, u

def proxy_rho(Cs_V, QGs):
    V = Cs_V
    A = np.mean([q * g for q, g, _ in QGs], axis=0)
    An = A / (V + 1e-30)
    for name, x in (('raw', A), ('norm', An)):
        r = x - x.mean(); v = V - V.mean()
        print(f'    proxy rho_{name}={float((r*v).sum()/np.sqrt((r**2).sum()*(v**2).sum()+1e-30)):+.3f}', flush=True)
    return A

R = {'cells': {}, 'budget': {}}
for locus in ('broad', 'bot16', 'top16'):
    for gamma in (0.0, 1.0, 2.0, 3.0):
        ds = []
        for sd in (0, 1, 2):
            rng = np.random.default_rng(1000 + sd)
            C, Q, G, s, u = gen_cm(rng, locus=locus, gamma=gamma)
            ds.append(delta_of(C, Q, G))
        key = f'{locus}_g{gamma}'
        R['cells'][key] = ds
        print(f'CM locus={locus} gamma={gamma}: Delta={np.mean(ds):+.2f}pp sd={np.std(ds,ddof=1):.2f} {np.round(ds,2)}', flush=True)
        if sd == 2 and gamma in (0.0, 2.0) and locus in ('broad', 'bot16'):
            pass
# proxy-on-synthetic: what does the calibration proxy report when truth is known?
print('proxy check (truth: broad mask, gamma=2):', flush=True)
rng = np.random.default_rng(7)
C, Q, G, s, u = gen_cm(rng, locus='broad', gamma=2.0, nq=800)
V = (C ** 2).mean(0)
proxy_rho(V, [(q, C[g[0]], 1) for q, g in zip(Q, G)])
print('proxy check (truth: bot16 mask, gamma=2):', flush=True)
rng = np.random.default_rng(7)
C, Q, G, s, u = gen_cm(rng, locus='bot16', gamma=2.0, nq=800)
V = (C ** 2).mean(0)
proxy_rho(V, [(q, C[g[0]], 1) for q, g in zip(Q, G)])
# budget curves under common mode
for tag, kw in (('broad_g0', dict(locus='broad', gamma=0.0)),
                ('broad_g2', dict(locus='broad', gamma=2.0)),
                ('bot16_g2', dict(locus='bot16', gamma=2.0))):
    rng = np.random.default_rng(0)
    C, Q, G, s, u = gen_cm(rng, nq=400, **kw)
    bc = budget_curve(C, Q, G, s)
    R['budget'][tag] = bc
    print(f"  budget {tag}: " + ' '.join(f'm{m}={v:+.2f}' for m, v in bc.items()), flush=True)
json.dump(R, open(OUT, 'w'), indent=1)
print('wrote', OUT, flush=True)
