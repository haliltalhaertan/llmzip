# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# synth.py — synthetic (documents, queries, gold) generator with controlled ground truth.
# Design + rationale live in GENERATOR.md. Results (JSON + tables) go to dial_results.json.
# Arms & metric mirror the programme exactly: sign=Hamming on (C>=0),(qC>=0);
# float=cosine on raw C; FR@3 = exact tie expectation E[FR@K].
import json, numpy as np, itertools, sys, os

D = 96
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dial_results.json')

def spectrum(alpha, d=D):
    s2 = (np.arange(1, d + 1, dtype=float)) ** (-alpha)
    s2 *= d / s2.sum()  # total variance fixed at d -> mean per-axis var 1
    return np.sqrt(s2)

def draw(rng, shape, size):
    if shape == 'gauss':
        return rng.standard_normal(size)
    if shape == 'heavy':  # Student-t df=3, unit variance
        return rng.standard_t(3, size) / np.sqrt(3.0)
    if shape == 'skew':  # centered exponential, unit variance, skew=+2
        return rng.standard_exponential(size) - 1.0
    raise ValueError(shape)

def locus_mask(locus, s, rng):
    d = len(s)
    if locus == 'broad':
        w = np.ones(d)
    elif locus == 'top16':
        w = np.zeros(d); w[np.argsort(-s)[:16]] = 1.0
    elif locus == 'mid16':
        w = np.zeros(d); w[np.argsort(-s)[40:56]] = 1.0
    elif locus == 'bot16':
        w = np.zeros(d); w[np.argsort(-s)[-16:]] = 1.0
    elif locus == 'rand16':
        w = np.zeros(d); w[rng.choice(d, 16, replace=False)] = 1.0
    else:
        raise ValueError(locus)
    w = w / np.sqrt(np.sum(w * s ** 2))  # equal signal power across loci (see GENERATOR.md)
    return w

def gen_archive(rng, N, alpha, shape, locus, ngold, sigma, beta=1.0, nq=400):
    s = spectrum(alpha)
    C = draw(rng, shape, (N, D)) * s
    w = locus_mask(locus, s, rng)
    Q, G = [], []
    for _ in range(nq):
        g = rng.choice(N, ngold, replace=False)
        m = C[g].mean(axis=0)
        q = beta * (w * m) + sigma * (draw(rng, shape, D) * s)
        Q.append(q); G.append(np.asarray(g, dtype=int))
    return C, np.array(Q), G

def fr3_exact(scores, gold, K, larger_better):
    s = np.asarray(scores, float)
    p = np.partition(s, -K if larger_better else K - 1)
    thr = p[-K] if larger_better else p[K - 1]
    if larger_better:
        better = np.sum(s > thr); tied = np.sum(s == thr)
        st = sum(1 for i in gold if s[i] > thr); gt = sum(1 for i in gold if s[i] == thr)
    else:
        better = np.sum(s < thr); tied = np.sum(s == thr)
        st = sum(1 for i in gold if s[i] < thr); gt = sum(1 for i in gold if s[i] == thr)
    return (st + gt * (K - better) / max(tied, 1)) / max(len(gold), 1)

def delta_of(C, Q, G, K=3):
    Sb = (C >= 0).astype(np.int8)
    cn = np.linalg.norm(C, axis=1)
    ds, dfs = [], []
    for q, g in zip(Q, G):
        cos = (C @ q) / (cn * np.linalg.norm(q) + 1e-30)
        ham = np.sum(Sb != (q >= 0).astype(np.int8), axis=1).astype(float)
        dfs.append(fr3_exact(cos, g, K, True))
        ds.append(fr3_exact(ham, g, K, False))
    return (np.mean(ds) - np.mean(dfs)) * 100.0

def run_cell(seed, Kconf):
    rng = np.random.default_rng(seed)
    C, Q, G = gen_archive(rng, **Kconf)
    return delta_of(C, Q, G)

def sweep(name, base, var, vals, seeds=(0, 1, 2, 3, 4)):
    rows = []
    for v in vals:
        conf = dict(base, **{var: v})
        ds = [run_cell(sd, conf) for sd in seeds]
        rows.append((v, float(np.mean(ds)), float(np.std(ds, ddof=1)), ds))
        print(f'  {name} {var}={v}: Delta={np.mean(ds):+.2f}pp sd={np.std(ds,ddof=1):.2f} {np.round(ds,2)}', flush=True)
    return rows

def budget_curve(C, Q, G, s, K=3):
    # dimension-matched: restrict BOTH arms to top-m variance axes (programme usage)
    order = np.argsort(-(np.mean(C ** 2, axis=0)))
    out = {}
    for m in (8, 16, 32, 48, 64, 80, 96):
        ax = order[:m]
        Cm, Qm = C[:, ax], Q[:, ax]
        out[m] = float(np.mean([fr3_exact(np.sum((Cm >= 0).astype(np.int8) != (q >= 0), axis=1),
                                           g, K, False) for q, g in zip(Qm, G)]) -
                       np.mean([fr3_exact((Cm @ q) / (np.linalg.norm(Cm, axis=1) * np.linalg.norm(q) + 1e-30),
                                           g, K, True) for q, g in zip(Qm, G)])) * 100.0
    return out

if __name__ == '__main__':
    BASE = dict(N=500, alpha=1.0, shape='gauss', locus='broad', ngold=1, sigma=1.0, nq=400)
    R = {}
    print('DIAL A: spectrum alpha (locus=broad)', flush=True)
    R['A_alpha'] = sweep('A', BASE, 'alpha', [0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
    print('DIAL B: locus x alpha interaction', flush=True)
    R['B_locus'] = {}
    for a in (0.5, 1.0, 2.0):
        print(f' alpha={a}', flush=True)
        R['B_locus'][str(a)] = sweep('B', dict(BASE, alpha=a), 'locus',
                                     ['top16', 'mid16', 'bot16', 'rand16', 'broad'])
    print('DIAL C: shape', flush=True)
    R['C_shape_broad'] = sweep('C', dict(BASE, alpha=1.0, locus='broad'), 'shape', ['gauss', 'heavy', 'skew'])
    R['C_shape_bot'] = sweep('C', dict(BASE, alpha=1.0, locus='bot16'), 'shape', ['gauss', 'heavy', 'skew'])
    print('DIAL D: archive size N', flush=True)
    R['D_N'] = sweep('D', BASE, 'N', [100, 400, 1500, 5000])
    print('DIAL E: golds per query', flush=True)
    R['E_ngold'] = sweep('E', BASE, 'ngold', [1, 2, 4])
    print('DIAL F: query noise sigma', flush=True)
    R['F_sigma'] = sweep('F', BASE, 'sigma', [0.5, 1.0, 2.0])
    print('BUDGET CURVES (dimension-matched, programme convention)', flush=True)
    R['budget'] = {}
    for tag, conf in (('broad_a1', dict(BASE)), ('bot16_a1', dict(BASE, locus='bot16')),
                      ('top16_a2', dict(BASE, alpha=2.0, locus='top16'))):
        rng = np.random.default_rng(0)
        C, Q, G = gen_archive(rng, **conf)
        bc = budget_curve(C, Q, G, spectrum(conf['alpha']))
        R['budget'][tag] = bc
        print(f'  {tag}: ' + ' '.join(f'm{m}={v:+.2f}' for m, v in bc.items()), flush=True)
    json.dump(R, open(OUT, 'w'), indent=1)
    print('wrote', OUT, flush=True)
