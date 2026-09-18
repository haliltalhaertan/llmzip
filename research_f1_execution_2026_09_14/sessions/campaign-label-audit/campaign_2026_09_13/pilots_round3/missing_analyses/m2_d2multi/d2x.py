"""D2X (MISSING-2): D2 multi-split robustness + fully GOLD-FREE tie model (c2 premise).
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
numpy only. Read-only on /mnt/c; writes only under /tmp/d2x/.
Replicates D2 (d2.py) machinery VERBATIM where noted: TOP48/BOT48 per-archive
variance convention; RAND48 seeds 12000/12001/12002; frozen lexsort tie protocol
(20 trials, top-3, fractional); delta = FR(TOP48) - mean(FR RAND48); binary target
loss-vs-win excluding ties; IRLS logistic train-standardized L2=1.0; AUC rank stat.
"""
import pickle, json, glob, hashlib, time
import numpy as np

LABELS = "[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
WORK = '/mnt/c/Users/MDP/dev/llmzip-work'
PKL_DIR = WORK + '/regen/lme/cache_repr'
DATA = WORK + '/drive/longmemeval_s_cleaned.json'
PILOT = WORK + '/pilots/axis_attack_2026-09-12/pilot_results.json'
OUT = '/tmp/d2x'

K = 3; NT = 20; TOL = 1e-12
RAND_SEEDS = [12000, 12001, 12002]
NSPLIT = 10
B_BOOT = 5000

def met_frac(order_top3, gset):
    x = len(set(map(int, order_top3)) & gset)
    return x / len(gset)

t0 = time.time()
data = json.load(open(DATA))
allq = sorted(str(x['question_id']) for x in data)
assert len(allq) == 500, len(allq)
lex = {q: i for i, q in enumerate(allq)}
del data

stored = json.load(open(PILOT))['per_question_native_FR']
assert len(stored) == 470

RAND_IDX = [np.random.default_rng(s).choice(96, 48, replace=False) for s in RAND_SEEDS]
pkls = sorted(glob.glob(PKL_DIR + '/*.pkl'))
assert len(pkls) == 470, len(pkls)

def eval_fr(d, gset, pris):
    d = np.asarray(d)
    return float(np.mean([met_frac(np.lexsort((p, d))[:K], gset) for p in pris]))

def features(d, gidx, D0full, g_nearest_full, p0):
    """VERBATIM from D2 d2.py."""
    d = np.asarray(d)
    n = len(d)
    dg = d[gidx]
    dmin = int(dg.min())
    imeet = int(gidx[np.argmin(dg)])
    tie = int(np.count_nonzero(d == dmin))
    below = int(np.count_nonzero(d == dmin - 1)) if dmin > 0 else 0
    above = int(np.count_nonzero(d == dmin + 1))
    closer = int(np.count_nonzero(d < dmin))
    mask = np.ones(n, dtype=bool); mask[gidx] = False
    dng = d[mask]
    mean_ng = float(dng.mean())
    min_ng = float(dng.min())
    order0 = np.lexsort((p0, d))
    s = d[order0]
    margin = int(s[3] - s[2]) if n >= 4 else 0
    w = s[:min(20, n)]
    _, c = np.unique(w, return_counts=True)
    pk = c / c.sum()
    ent = float(-np.sum(pk * np.log(pk)))
    bucket = int(np.count_nonzero(np.all(D0full == D0full[g_nearest_full], axis=1)))
    return {'d_gold_mean': float(dg.mean()), 'd_gold_min': dmin,
            'tie_mass_at_dgold': tie, 'tie_mass_at_dgold_m1': below,
            'tie_mass_at_dgold_p1': above, 'gold_bucket_size': bucket,
            'margin': margin, 'strictly_closer_than_gold': closer,
            'top20_entropy': ent, 'mean_nongold': mean_ng, 'min_nongold': min_ng}

def gfeatures(d_top, D0full, cvar, od, qC, p0):
    """Strictly GOLD-FREE features (no gidx/gold anywhere).
    d_top: TOP48-arm Hamming distances; order0: trial-0 ordering (lexsort((p0,d)))."""
    d = np.asarray(d_top)
    n = len(d)
    order0 = np.lexsort((p0, d))
    s_ord = d[order0]
    ss = np.sort(d)
    d3 = int(ss[2]); d4 = int(ss[3]) if n >= 4 else int(ss[2])
    margin34 = int(s_ord[3] - s_ord[2]) if n >= 4 else 0  # == D2 margin (declared dup)
    crowd3 = int(np.count_nonzero(d == d3))
    crowd4 = int(np.count_nonzero(d == d4))
    crowd_pm1 = int(np.count_nonzero(np.abs(d - d3) <= 1))
    t3 = d[order0[:3]]
    top3_tie_share = float(np.count_nonzero(t3 == d3)) / 3.0
    boundary_share = float(crowd_pm1) / n
    top20codes = D0full[order0[:min(20, n)]]
    distinct = np.unique(top20codes, axis=0).shape[0]
    dup_top20 = 1.0 - distinct / 20.0
    v16 = float(cvar[od[:16]].sum()); v48 = float(cvar[od[:48]].sum())
    var_decay = v16 / v48 if v48 > 0 else 0.0
    qp = float(np.count_nonzero(qC >= 0)) / qC.size
    qent = float(-(qp * np.log(qp) + (1 - qp) * np.log(1 - qp))) if 0.0 < qp < 1.0 else 0.0
    return {'margin34': float(margin34), 'crowd3': float(crowd3), 'crowd4': float(crowd4),
            'crowd_pm1': float(crowd_pm1), 'top3_tie_share': top3_tie_share,
            'boundary_share': boundary_share, 'dup_top20': dup_top20,
            'var_decay': var_decay, 'N': float(n), 'qent': qent}

per = {}
for i, p in enumerate(pkls):
    o = pickle.loads(open(p, 'rb').read())
    qid = o['question_id']; C = o['C']; qC = o['qC']
    g = np.asarray(o['gold']).ravel()
    n = len(C); lx = lex[qid]
    gset = set(map(int, g)); gidx = np.array(sorted(gset))
    D0 = (C >= 0); Q0 = (qC >= 0)
    dnat = np.count_nonzero(D0 != Q0[None, :], axis=1).astype(np.int16)
    var = C.var(axis=0)
    od = np.argsort(var, kind='stable')[::-1]
    arms = {'TOP48': od[:48], 'BOT48': od[::-1][:48],
            'RAND48_s0': RAND_IDX[0], 'RAND48_s1': RAND_IDX[1], 'RAND48_s2': RAND_IDX[2]}
    pris = [np.random.default_rng(5_100_000 + lx * 100_000 + t * 100 + 99).random(n)
            for t in range(NT)]
    fr = {}; dd = {}
    dd['NATIVE'] = dnat
    fr['NATIVE'] = eval_fr(dnat, gset, pris)
    for name, idx in arms.items():
        d = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1).astype(np.int16)
        dd[name] = d
        fr[name] = eval_fr(d, gset, pris)
    fr['RAND48_mean'] = float(np.mean([fr['RAND48_s0'], fr['RAND48_s1'], fr['RAND48_s2']]))
    g_full_nearest = int(gidx[np.argmin(dnat[gidx])])
    feats = {}
    for name in ['TOP48', 'BOT48', 'RAND48_s0', 'RAND48_s1', 'RAND48_s2', 'NATIVE']:
        feats[name] = features(dd[name], gidx, D0, g_full_nearest, pris[0])
    fm = {}
    for k in feats['RAND48_s0']:
        fm[k] = float(np.mean([feats['RAND48_s%d' % s][k] for s in range(3)]))
    feats['RAND48_mean'] = fm
    gfeat = gfeatures(dd['TOP48'], D0, var, od, np.asarray(qC).ravel(), pris[0])
    delta = fr['TOP48'] - fr['RAND48_mean']
    if delta > TOL: outcome = 'win'
    elif delta < -TOL: outcome = 'loss'
    else: outcome = 'tie'
    per[qid] = {'lex': lx, 'n': n, 'ngold': len(gset), 'fr': fr, 'feat': feats,
                'gfeat': gfeat, 'delta': delta, 'outcome': outcome,
                'fr_nat_stored': float(stored[qid])}
    if (i + 1) % 100 == 0:
        print('  %d/470 (%.0fs)' % (i + 1, time.time() - t0), flush=True)
# ---- model machinery (VERBATIM IRLS/AUC from D2) ----
FEAT_T = ['tie_mass_at_dgold', 'margin', 'strictly_closer_than_gold']
FEAT_M = ['d_gold_mean', 'mean_nongold', 'min_nongold', 'top20_entropy']
FEAT_G = ['margin34', 'crowd3', 'crowd4', 'crowd_pm1', 'top3_tie_share',
          'boundary_share', 'dup_top20', 'var_decay', 'N', 'qent']
# G u T drops margin34: it is EXACTLY D2 margin (same trial-0 s[3]-s[2]); declared.
FEAT_GT = [f for f in FEAT_G if f != 'margin34'] + FEAT_T
FEAT_GM = FEAT_G + FEAT_M

def X_of(qs, feats, goldfree):
    src = 'gfeat' if goldfree else 'TOP48'
    if goldfree and set(feats) <= set(FEAT_G):
        return np.array([[per[q]['gfeat'][f] for f in feats] for q in qs], float)
    out = []
    for q in qs:
        row = []
        for f in feats:
            row.append(per[q]['gfeat'][f] if f in per[q]['gfeat'] else per[q]['feat']['TOP48'][f])
        out.append(row)
    return np.array(out, float)

def y_of(qs, outcomes):
    return np.array([1 if outcomes[q] == 'win' else 0 for q in qs], float)

def fit_logreg(X, y, lam=1.0, iters=500, tol=1e-10):
    n, p = X.shape
    Xb = np.hstack([np.ones((n, 1)), X])
    pen = np.r_[0.0, np.full(p, lam)]
    w = np.zeros(p + 1)
    for _ in range(iters):
        s = 1.0 / (1.0 + np.exp(-(Xb @ w)))
        g = Xb.T @ (s - y) + pen * w
        W = s * (1 - s)
        H = (Xb * W[:, None]).T @ Xb + np.diag(pen)
        step = np.linalg.solve(H, g)
        w -= step
        if float(np.max(np.abs(step))) < tol:
            break
    return w

def auc_rank(s, y):
    p = s[y == 1]; q = s[y == 0]
    gt = np.sum(p[:, None] > q[None, :]); eq = np.sum(p[:, None] == q[None, :])
    return float((gt + 0.5 * eq) / (len(p) * len(q)))

def fit_eval(qtr, qte, feats, outcomes):
    goldfree = all(f in per[qtr[0]]['gfeat'] for f in feats)
    Xtr = X_of(qtr, feats, goldfree); ytr = y_of(qtr, outcomes)
    Xte = X_of(qte, feats, goldfree); yte = y_of(qte, outcomes)
    mu = Xtr.mean(axis=0); sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
    w = fit_logreg((Xtr - mu) / sd, ytr)
    out = {}
    for nm, X, y in [('train', Xtr, ytr), ('test', Xte, yte)]:
        s = 1.0 / (1.0 + np.exp(-(np.hstack([np.ones((X.shape[0], 1)), (X - mu) / sd]) @ w)))
        out[nm + '_auc'] = auc_rank(s, y)
        out[nm + '_scores'] = s
    out['coef'] = dict(zip(['bias'] + feats, [float(v) for v in w]))
    out['mu'] = [float(v) for v in mu]; out['sd'] = [float(v) for v in sd]
    return out

qids = sorted(per.keys())
outcomes = {q: per[q]['outcome'] for q in qids}

def split_c1(qid):
    return 'train' if int(hashlib.sha256(('c1|' + qid).encode()).hexdigest()[0], 16) % 2 == 0 else 'test'

def split_salted(s, qid):
    return 'train' if int(hashlib.sha256(('c1s|%d|%s' % (s, qid)).encode()).hexdigest()[0], 16) % 2 == 0 else 'test'

# ---- Gate: reproduce D2 single-split numbers ----
sp_c1 = {q: split_c1(q) for q in qids}
qtr0 = [q for q in qids if sp_c1[q] == 'train' and outcomes[q] in ('win', 'loss')]
qte0 = [q for q in qids if sp_c1[q] == 'test' and outcomes[q] in ('win', 'loss')]
g0T = fit_eval(qtr0, qte0, FEAT_T, outcomes)
g0M = fit_eval(qtr0, qte0, FEAT_M, outcomes)
print('GATE: AUC(T)=%.4f (exp 0.798) AUC(M)=%.4f (exp 0.686) bintrain=%d/%d bintest=%d/%d'
      % (g0T['test_auc'], g0M['test_auc'], len(qtr0), int(y_of(qtr0, outcomes).sum()),
         len(qte0), int(y_of(qte0, outcomes).sum())), flush=True)
assert abs(g0T['test_auc'] - 0.798) <= 0.002 + 0.001, g0T['test_auc']  # 0.79846 rounds .798
assert abs(g0T['test_auc'] - 0.7984597500726534) <= 0.002, g0T['test_auc']
assert abs(g0M['test_auc'] - 0.6864283638477187) <= 0.002, g0M['test_auc']
assert (len(qtr0), int(y_of(qtr0, outcomes).sum())) == (161, 54)
assert (len(qte0), int(y_of(qte0, outcomes).sum())) == (130, 37)
print('GATE PASS', flush=True)

# ---- Task 1+2: 10 salted splits x {T, M, TM, G, GT, GM} ----
MODELS = {'T': FEAT_T, 'M': FEAT_M, 'TM': FEAT_T + FEAT_M,
          'G': FEAT_G, 'GT': FEAT_GT, 'GM': FEAT_GM}
splits = []
for s in range(NSPLIT):
    sp = {q: split_salted(s, q) for q in qids}
    qtr = [q for q in qids if sp[q] == 'train' and outcomes[q] in ('win', 'loss')]
    qte = [q for q in qids if sp[q] == 'test' and outcomes[q] in ('win', 'loss')]
    rec = {'s': s, 'train_n': len(qtr), 'train_wins': int(y_of(qtr, outcomes).sum()),
           'test_n': len(qte), 'test_wins': int(y_of(qte, outcomes).sum()),
           'qte': qte, 'yte': y_of(qte, outcomes)}
    for m, feats in MODELS.items():
        r = fit_eval(qtr, qte, feats, outcomes)
        rec[m] = {'train_auc': r['train_auc'], 'test_auc': r['test_auc'],
                  'coef': r['coef'], 'test_scores': [float(v) for v in r['test_scores']]}
    splits.append(rec)
    print('split %d: ntr=%d/%d nte=%d/%d AUC T=%.3f M=%.3f TM=%.3f G=%.3f GT=%.3f GM=%.3f'
          % (s, rec['train_n'], rec['train_wins'], rec['test_n'], rec['test_wins'],
             rec['T']['test_auc'], rec['M']['test_auc'], rec['TM']['test_auc'],
             rec['G']['test_auc'], rec['GT']['test_auc'], rec['GM']['test_auc']), flush=True)
# ---- Task 1 stats + bootstrap CI (two-stage: resample splits, then test questions) ----
A = lambda m: np.array([r[m]['test_auc'] for r in splits])
D = A('T') - A('M')
def summ(v):
    return {'mean': float(v.mean()), 'sd': float(v.std(ddof=1)),
            'min': float(v.min()), 'max': float(v.max()), 'values': [float(x) for x in v]}
stats = {m: summ(A(m)) for m in MODELS}
stats['TminusM'] = summ(D)
stats['TminusM']['frac_ge_0.05'] = float(np.mean(D >= 0.05))
stats['G_gt_0.65_frac'] = float(np.mean(A('G') > 0.65))
stats['T_gt_0.65_frac'] = float(np.mean(A('T') > 0.65))

brng = np.random.default_rng(7)
Tscores = [np.array(r['T']['test_scores']) for r in splits]
Mscores = [np.array(r['M']['test_scores']) for r in splits]
Ytes = [np.array(r['yte']) for r in splits]
b_meanT, b_meanD = [], []
for b in range(B_BOOT):
    si = brng.integers(0, NSPLIT, NSPLIT)
    mT, mD = [], []
    for i in si:
        n = len(Ytes[i])
        idx = brng.integers(0, n, n)
        yb = Ytes[i][idx]
        if yb.sum() == 0 or yb.sum() == len(yb):
            continue
        aT = auc_rank(Tscores[i][idx], yb); aM = auc_rank(Mscores[i][idx], yb)
        mT.append(aT); mD.append(aT - aM)
    if mT:
        b_meanT.append(float(np.mean(mT))); b_meanD.append(float(np.mean(mD)))
ci_T = [float(np.percentile(b_meanT, 2.5)), float(np.percentile(b_meanT, 97.5))]
ci_D = [float(np.percentile(b_meanD, 2.5)), float(np.percentile(b_meanD, 97.5))]
print('BOOT: meanAUC(T) CI95=[%.3f,%.3f] mean(T-M) CI95=[%+.3f,%+.3f] (B=%d, two-stage)' %
      (ci_T[0], ci_T[1], ci_D[0], ci_D[1], B_BOOT), flush=True)

# ---- G signal: standardized coefs across splits ----
gcoef = {}
for f in FEAT_G:
    v = np.array([r['G']['coef'][f] for r in splits])
    gcoef[f] = {'mean': float(v.mean()), 'sd': float(v.std(ddof=1)),
                'values': [float(x) for x in v]}
gcoef['bias'] = {'mean': float(np.mean([r['G']['coef']['bias'] for r in splits])),
                 'sd': float(np.std([r['G']['coef']['bias'] for r in splits], ddof=1))}

# ---- details JSON ----
details = {'labels': LABELS,
           'conventions': {
               'arms': "TOP48/BOT48/RAND48 VERBATIM from D2 (same seeds 12000/12001/12002); DROP64 omitted (gold-informed analysis-only, unused here)",
               'tie_protocol': 'priorities rng(5_100_000+lx*100000+t*100+99).random(n), 20 trials, lexsort((p,d)), top-3, fractional FR (VERBATIM)',
               'target': 'delta=FR(TOP48)-mean(FR RAND48); win/loss/tie at 1e-12; binary loss-vs-win excl ties (VERBATIM)',
               'learner': 'IRLS logistic, train-standardized, L2 lam=1.0 bias unpenalized; AUC Mann-Whitney, pos=win (VERBATIM)',
               'splits': "train iff int(sha256('c1s|{s}|'+qid).hexdigest()[0],16) even, s=0..9",
               'G_features': {'margin34': 's[3]-s[2] trial-0 TOP48 ordering; IDENTICAL to D2 margin (dup declared)',
                              'crowd3': '#docs with d==d3 (3rd-smallest TOP48 distance)',
                              'crowd4': '#docs with d==d4',
                              'crowd_pm1': '#docs with |d-d3|<=1',
                              'top3_tie_share': 'fraction of top-3 slots tied at cutoff d3 (in {1/3,2/3,1})',
                              'boundary_share': 'crowd_pm1/N (share version; N-normalized)',
                              'dup_top20': '1-distinct/20 over top-20 FULL-96bit codes under trial-0 order',
                              'var_decay': 'sum top-16 var / sum top-48 var (C variances, same od)',
                              'N': 'archive size', 'qent': 'binary entropy (nats) of query sign (qC>=0)'},
               'GT': 'G-minus-margin34 + T (margin34==margin exactly; dedup declared)',
               'bootstrap': 'two-stage B=5000 seed 7: (1) resample 10 splits w/ replacement; (2) within each, resample its test binary questions w/ replacement (same n), recompute AUC(T),AUC(M) from STORED fitted scores; mean over 10; percentile 2.5/97.5 CI'},
           'gate_c1': {'AUC_T': float(g0T['test_auc']), 'AUC_M': float(g0M['test_auc']),
                       'bintrain_n': len(qtr0), 'bintrain_wins': 54,
                       'bintest_n': len(qte0), 'bintest_wins': 37, 'pass': True},
           'split_stats_testAUC': stats,
           'bootstrap_CI95': {'mean_AUC_T': ci_T, 'mean_TminusM': ci_D, 'B': B_BOOT},
           'G_coef_across_splits': gcoef,
           'splits': [{'s': r['s'], 'train_n': r['train_n'], 'train_wins': r['train_wins'],
                       'test_n': r['test_n'], 'test_wins': r['test_wins'],
                       **{m: {'train_auc': r[m]['train_auc'], 'test_auc': r[m]['test_auc'],
                               'coef': r[m]['coef']} for m in MODELS}} for r in splits]}
json.dump(details, open(OUT + '/d2x_details.json', 'w'))
print('wrote d2x_details.json (%.1fs)' % (time.time() - t0), flush=True)

# ---- report ----
L = []
L.append('# D2X (MISSING-2) — D2 multi-split robustness + fully gold-free tie model (c2 premise)\n')
L.append('**%s**\n' % LABELS)
L.append('Frozen protocol verbatim from D2 (lexsort tie priorities, 20 trials, fractional R@3); numpy only; no network. Read-only on /mnt/c; all writes under /tmp/d2x/.\n')
L.append('## 0. Gate (D2 single-split reproduction, sha256("c1|"+qid) parity)\n')
L.append('Recomputed AUC(T)=%.4f (expected 0.798, tol 0.002), AUC(M)=%.4f (expected 0.686, tol 0.002); binary train n=%d (wins %d), test n=%d (wins %d) — identical to D2 (161/54, 130/37).' % (g0T['test_auc'], g0M['test_auc'], len(qtr0), 54, len(qte0), 37))
L.append('\n**Gate PASS — D2 machinery replicated.**\n')
L.append('## 1. Multi-split stability (10 salted splits, s=0..9; held-out = test AUC)\n')
L.append('| Model | Mean | SD | Min | Max | Splits detail |')
L.append('|---|---|---|---|---|---|')
for m in ['T', 'M', 'TM', 'G', 'GT', 'GM']:
    v = stats[m]
    L.append('| %s | %.3f | %.3f | %.3f | %.3f | %s |' % (m, v['mean'], v['sd'], v['min'], v['max'], ', '.join('%.3f' % x for x in v['values'])))
L.append('')
L.append('T-M delta per split: ' + ', '.join('%+.3f' % x for x in (A('T') - A('M'))) + '.')
L.append('Delta distribution: mean=%+.3f, sd=%.3f, range=[%+.3f,%+.3f], fraction of splits with delta>=0.05: %.1f%% (%d/10).' % (stats['TminusM']['mean'], stats['TminusM']['sd'], stats['TminusM']['min'], stats['TminusM']['max'], 100 * stats['TminusM']['frac_ge_0.05'], int(round(10 * stats['TminusM']['frac_ge_0.05']))))
L.append('Binary n per split (train/test): ' + '; '.join('%d:%d/%d' % (r['s'], r['train_n'], r['test_n']) for r in splits) + '; wins per split train: ' + ', '.join(str(r['train_wins']) for r in splits) + '; test: ' + ', '.join(str(r['test_wins']) for r in splits) + '.')
L.append('Bootstrap (two-stage: resample 10 splits w/ replacement, then resample each split\'s test binary questions w/ replacement and recompute AUCs from stored fitted scores; B=5000, seed 7): mean AUC(T) 95%% CI=[%.3f, %.3f]; mean(T-M) 95%% CI=[%+.3f, %+.3f].' % (ci_T[0], ci_T[1], ci_D[0], ci_D[1]))
L.append('\n## 2. Fully gold-free model G (10 features, no gold at train or inference)\n')
L.append('Held-out AUC(G) per split: ' + ', '.join('%.3f' % x for x in A('G')) + '; mean=%.3f, sd=%.3f, range=[%.3f, %.3f]; splits above kill-bar 0.65: %d/10.' % (stats['G']['mean'], stats['G']['sd'], stats['G']['min'], stats['G']['max'], int(round(10 * stats['G_gt_0.65_frac']))))
L.append('Context: mean AUC(GT)=%.3f, mean AUC(GM)=%.3f.' % (stats['GT']['mean'], stats['GM']['mean']))
L.append('Standardized G coefficients across splits (mean +/- sd; + favors win): ' + '; '.join('%s=%+.3f+/-%.3f' % (f, gcoef[f]['mean'], gcoef[f]['sd']) for f in FEAT_G) + '; bias=%+.3f+/-%.3f.' % (gcoef['bias']['mean'], gcoef['bias']['sd']))
L.append('Signal carriers (|mean| largest): ' + ', '.join('%s (%+.3f)' % (f, gcoef[f]['mean']) for f in sorted(FEAT_G, key=lambda f: -abs(gcoef[f]['mean']))[:4]) + '.')
L.append('Declared overlaps: margin34 is EXACTLY D2 margin (same trial-0 s[3]-s[2]); boundary_share=crowd_pm1/N (count vs share pair, L2 absorbs); GT dedups margin34.')
L.append('\n## 3. Verdict\n')
meanT = stats['T']['mean']; meanD = stats['TminusM']['mean']; meanG = stats['G']['mean']
L.append('AUC(T) across splits: mean=%.3f (D2 single-split 0.798); Delta(T-M): mean=%+.3f (D2 +0.112), frac>=0.05=%.0f%%; gold-free AUC(G): mean=%.3f, %d/10 splits >0.65.' % (meanT, meanD, 100 * stats['TminusM']['frac_ge_0.05'], meanG, int(round(10 * stats['G_gt_0.65_frac']))))
L.append('\n## 4. Honesty: what this cannot show\n')
L.append('- Single benchmark (LME-470), one learner (IRLS logistic, L2=1.0), one target definition (binary loss-vs-win EXCLUDING ties: per-split binary test n≈%d-%d only; ties carry no flip direction).' % (min(r['test_n'] for r in splits), max(r['test_n'] for r in splits)))
L.append('- 10 salted hash splits of the SAME 470 questions: split-to-split variation only, no new data; bootstrap CI reflects resampling, not population sampling.')
L.append('- G is gold-free at inference but built on the TOP48-variance arm (unsupervised) and validated on the same flip target that T/M were tuned against; margin34 duplicates D2 margin.')
L.append('- AUC differences near +/-0.03 are noise-scale at this n; G vs M gaps must be read with that ruler.')
L.append('- Correlation/description only: no causal claim; mechanism stays OPEN. Verdict is LOCAL EXPLORATORY, not preregistered, not for citation.')
open(OUT + '/d2x_report.md', 'w').write('\n'.join(L))
print('wrote d2x_report.md', flush=True)

verdict = ('tie story across splits: AUC(T) mean=%.3f sd=%.3f, Delta(T-M) mean=%+.3f frac>=0.05=%.0f%%; '
           'gold-free AUC(G) mean=%.3f (%d/10 splits >0.65) -> %s 0.65 kill-bar' %
           (meanT, stats['T']['sd'], meanD, 100 * stats['TminusM']['frac_ge_0.05'],
            meanG, int(round(10 * stats['G_gt_0.65_frac'])),
            'CLEARS' if stats['G_gt_0.65_frac'] > 0.5 else 'DOES NOT CLEAR'))
print('D2X_VERDICT: ' + verdict, flush=True)
