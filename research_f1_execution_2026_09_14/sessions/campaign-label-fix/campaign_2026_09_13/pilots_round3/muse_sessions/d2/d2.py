"""DENEY 2 (c1): tie-mass decomposition + flip predictor (LME).
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
numpy only. Read-only elsewhere; writes only under /tmp/d2/.
"""
import pickle, json, glob, hashlib, time
import numpy as np

LABELS = "[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
WORK = '/mnt/c/Users/MDP/dev/llmzip-work'
PKL_DIR = WORK + '/regen/lme/cache_repr'
DATA = WORK + '/drive/longmemeval_s_cleaned.json'
PILOT = WORK + '/pilots/axis_attack_2026-09-12/pilot_results.json'
NPZ = WORK + '/pilots/axis_attack_2026-09-12/per_axis_matrices.npz'
OUT = '/tmp/d2'

K = 3; NT = 20; TOL = 1e-12
EXP_NATIVE = 0.5419751773049645
EXP = {'TOP48': 0.34949468085106383, 'RAND48_s0': 0.47292553191489356,
       'BOT48': 0.4284574468085106}
RAND_SEEDS = [12000, 12001, 12002]

def met_frac(order_top3, gset):
    x = len(set(map(int, order_top3)) & gset)
    return x / len(gset)

t0 = time.time()
# ---- lex ordinals over ALL 500 dataset qids ----
data = json.load(open(DATA))
allq = sorted(str(x['question_id']) for x in data)
assert len(allq) == 500, len(allq)
lex = {q: i for i, q in enumerate(allq)}
del data

stored = json.load(open(PILOT))['per_question_native_FR']
assert len(stored) == 470

# ---- drop utility (full-data, gold-informed analysis-only) ----
z = np.load(NPZ)
zqids = [str(q) for q in z['qids']]
zdrop = z['drop']  # (470,96) per-q FR with axis a removed
U = np.array([np.mean([stored[q] - zdrop[zqids.index(q), a] for q in zqids])
              for a in range(96)])
drop_order = np.argsort(U, kind='stable')[::-1]
DROP64 = np.sort(drop_order[:64])  # sorted for cleanliness; set membership is what matters
print('drop top-5 axes:', drop_order[:5].tolist(), flush=True)

RAND_IDX = [np.random.default_rng(s).choice(96, 48, replace=False) for s in RAND_SEEDS]
pkls = sorted(glob.glob(PKL_DIR + '/*.pkl'))
assert len(pkls) == 470, len(pkls)

def eval_fr(d, gset, pris):
    d = np.asarray(d)
    return float(np.mean([met_frac(np.lexsort((p, d))[:K], gset) for p in pris]))

def features(d, gidx, D0full, g_nearest_full, p0):
    """All distances are arm-restricted Hamming ints. p0 = trial-0 priorities.
    gold_bucket_size uses full-96-bit codes (arm-invariant)."""
    d = np.asarray(d)
    n = len(d)
    dg = d[gidx]
    dmin = int(dg.min())
    imeet = int(gidx[np.argmin(dg)])  # min-distance gold (first on ties)
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
    arms = {'TOP48': od[:48], 'BOT48': od[::-1][:48], 'DROP64': DROP64,
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
    # nearest gold by FULL-96-bit distance (for the arm-invariant bucket anchor)
    g_full_nearest = int(gidx[np.argmin(dnat[gidx])])
    feats = {}
    for name in ['TOP48', 'BOT48', 'DROP64', 'RAND48_s0', 'RAND48_s1', 'RAND48_s2', 'NATIVE']:
        feats[name] = features(dd[name], gidx, D0, g_full_nearest, pris[0])
    # RAND-mean features = mean across the 3 seeds
    fm = {}
    for k in feats['RAND48_s0']:
        fm[k] = float(np.mean([feats['RAND48_s%d' % s][k] for s in range(3)]))
    feats['RAND48_mean'] = fm
    delta = fr['TOP48'] - fr['RAND48_mean']
    if delta > TOL: outcome = 'win'
    elif delta < -TOL: outcome = 'loss'
    else: outcome = 'tie'
    per[qid] = {'lex': lx, 'n': n, 'ngold': len(gset), 'fr': fr, 'feat': feats,
                'delta': delta, 'outcome': outcome,
                'fr_nat_stored': float(stored[qid])}
    if (i + 1) % 100 == 0:
        print('  %d/470 (%.0fs)' % (i + 1, time.time() - t0), flush=True)

# ---- Gates (abort if fail) ----
qids = sorted(per.keys())
A = lambda k: np.array([per[q]['fr'][k] for q in qids])
nat = float(A('NATIVE').mean())
assert abs(nat - EXP_NATIVE) <= 1e-12, (nat, EXP_NATIVE)
for k in EXP:
    v = float(A(k).mean())
    assert abs(v - EXP[k]) <= 1e-12, (k, v, EXP[k])
nat_maxdiff = float(max(abs(per[q]['fr']['NATIVE'] - per[q]['fr_nat_stored']) for q in qids))
print('GATES PASS: native=%.16f TOP48=%.14f RAND48_s0=%.14f BOT48=%.14f nat_maxdiff=%g'
      % (nat, float(A('TOP48').mean()), float(A('RAND48_s0').mean()),
         float(A('BOT48').mean()), nat_maxdiff), flush=True)

# ---- flip target + split ----
def split_of(qid):
    return 'train' if int(hashlib.sha256(('c1|' + qid).encode()).hexdigest()[0], 16) % 2 == 0 else 'test'
splits = {q: split_of(q) for q in qids}
n_train = sum(1 for q in qids if splits[q] == 'train')
outcomes = {q: per[q]['outcome'] for q in qids}
W = [q for q in qids if outcomes[q] == 'win']; L = [q for q in qids if outcomes[q] == 'loss']
T = [q for q in qids if outcomes[q] == 'tie']
gap = np.array([per[q]['delta'] for q in qids])
print('flip(TOP48 vs RAND48-mean): W/T/L=%d/%d/%d mean_gap=%.4fpp' %
      (len(W), len(T), len(L), 100 * gap.mean()), flush=True)
print('split: train=%d test=%d' % (n_train, 470 - n_train), flush=True)

# ---- models: binary loss-vs-win (exclude ties); positive class = win ----
FEAT_T = ['tie_mass_at_dgold', 'margin', 'strictly_closer_than_gold']
FEAT_M = ['d_gold_mean', 'mean_nongold', 'min_nongold', 'top20_entropy']
# model features use TOP48-arm geometry (suspect arm only; declare)
def X_of(qs, feats):
    return np.array([[per[q]['feat']['TOP48'][f] for f in feats] for q in qs], float)
def y_of(qs):
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

def run_model(feats):
    out = {}
    for split, qs_all in [('train', [q for q in qids if splits[q] == 'train']),
                          ('test', [q for q in qids if splits[q] == 'test'])]:
        qs = [q for q in qs_all if outcomes[q] in ('win', 'loss')]
        out[split + '_n'] = len(qs)
        out[split + '_wins'] = int(sum(1 for q in qs if outcomes[q] == 'win'))
    qtr = [q for q in qids if splits[q] == 'train' and outcomes[q] in ('win', 'loss')]
    qte = [q for q in qids if splits[q] == 'test' and outcomes[q] in ('win', 'loss')]
    Xtr = X_of(qtr, feats); ytr = y_of(qtr)
    Xte = X_of(qte, feats); yte = y_of(qte)
    mu = Xtr.mean(axis=0); sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
    w = fit_logreg((Xtr - mu) / sd, ytr)
    for nm, X, y, qs in [('train', Xtr, ytr, qtr), ('test', Xte, yte, qte)]:
        s = 1.0 / (1.0 + np.exp(-(np.hstack([np.ones((len(qs), 1)), (X - mu) / sd]) @ w)))
        out[nm + '_auc'] = auc_rank(s, y)
        for q, v in zip(qs, s):
            per[q]['score_' + ('T' if len(feats) == 3 else ('M' if len(feats) == 4 else 'TM'))] = float(v)
    out['coef'] = dict(zip(['bias'] + feats, [float(v) for v in w]))
    out['mu'] = [float(v) for v in mu]; out['sd'] = [float(v) for v in sd]
    return out

res_T = run_model(FEAT_T)
res_M = run_model(FEAT_M)
res_TM = run_model(FEAT_T + FEAT_M)
print('AUC: T train=%.3f test=%.3f | M train=%.3f test=%.3f | TM train=%.3f test=%.3f' %
      (res_T['train_auc'], res_T['test_auc'], res_M['train_auc'], res_M['test_auc'],
       res_TM['train_auc'], res_TM['test_auc']), flush=True)

# ---- per-arm feature table: means for wins vs losses ----
ALLF = ['d_gold_mean', 'd_gold_min', 'tie_mass_at_dgold', 'tie_mass_at_dgold_m1',
        'tie_mass_at_dgold_p1', 'gold_bucket_size', 'margin',
        'strictly_closer_than_gold', 'top20_entropy', 'mean_nongold', 'min_nongold']
def fmean(qs, arm, f):
    return float(np.mean([per[q]['feat'][arm][f] for q in qs]))
ftab = {arm: {f: {'win': fmean(W, arm, f), 'loss': fmean(L, arm, f)}
              for f in ALLF} for arm in ['TOP48', 'RAND48_mean', 'BOT48', 'DROP64']}
armFR = {k: float(A(k).mean()) for k in
         ['NATIVE', 'TOP48', 'BOT48', 'DROP64', 'RAND48_s0', 'RAND48_s1', 'RAND48_s2', 'RAND48_mean']}

# ---- details JSON ----
details = {'labels': LABELS,
           'conventions': {
               'tie_protocol': 'priorities rng(5_100_000+lx*100000+t*100+99).random(n), 20 trials, lexsort((p,d)), top-3, fractional FR',
               'TOP48': "od=np.argsort(var,kind='stable')[::-1]; od[:48] (mirrors R2C/pilot)",
               'BOT48': 'od[::-1][:48]', 'RAND48': 'rng(12000+s).choice(96,48) s=0,1,2',
               'DROP64': 'top-64 axes by full-data drop utility from per_axis_matrices.npz; GOLD-INFORMED analysis-only',
               'drop_top5_axes': drop_order[:5].tolist(), 'drop64_axes_sorted': DROP64.tolist(),
               'features': 'arm-restricted Hamming d; nearest gold = min-distance gold (first on ties); tie_mass counts docs with d==dmin (==round(d_gold)); bucket = full-96-bit exact-code duplicates (arm-invariant); margin = s[3]-s[2] under TRIAL-0 ordering; top20_entropy = -sum p ln p (nats) over trial-0 top-20 distance histogram; RAND48_mean features = mean across 3 seeds',
               'min_nongold_clipped': 'no extra clipping; naturally bounded in [0,48]',
               'target': 'delta=FR(TOP48)-mean(FR RAND48 seeds); win delta>1e-12, tie |delta|<=1e-12, loss below; primary=binary loss-vs-win excluding ties (ties carry no flip direction; ordinal would be tie-dominated)',
               'split': "train iff int(sha256('c1|'+qid).hexdigest()[0],16) even",
               'model_features': 'TOP48-arm geometry only (suspect arm, deployable without baseline)',
               'logreg': 'IRLS, train-standardized, L2 lam=1.0 (bias unpenalized)',
               'auc': 'Mann-Whitney rank statistic, positive class = win'},
           'gates': {'native': nat, 'expected_native': EXP_NATIVE,
                     'arm_means': {k: float(A(k).mean()) for k in EXP},
                     'expected_arms': EXP, 'native_maxdiff_vs_stored': nat_maxdiff},
           'flip': {'W': len(W), 'T': len(T), 'L': len(L), 'mean_gap': float(gap.mean()),
                    'median_gap': float(np.median(gap)),
                    'drop64_mean_FR': armFR['DROP64'],
                    'train_n': n_train, 'test_n': 470 - n_train},
           'arm_FR_means': armFR,
           'models': {'T': res_T, 'M': res_M, 'TM': res_TM,
                      'feats_T': FEAT_T, 'feats_M': FEAT_M},
           'feature_table_win_loss': ftab,
           'per_question': {q: {'lex': per[q]['lex'], 'n': per[q]['n'], 'ngold': per[q]['ngold'],
                                'split': splits[q], 'outcome': per[q]['outcome'],
                                'delta': per[q]['delta'], 'fr': per[q]['fr'],
                                'feat': per[q]['feat'],
                                'score_T': per[q].get('score_T'), 'score_M': per[q].get('score_M'),
                                'score_TM': per[q].get('score_TM')}
                            for q in qids}}
json.dump(details, open(OUT + '/d2_details.json', 'w'))
print('wrote d2_details.json (%.1fs)' % (time.time() - t0), flush=True)

# ---- report ----
_t = res_T['test_auc']; _d = _t - res_M['test_auc']
if _t >= 0.65 and _d >= 0.05:
    decision = ('AUC(T)=%.3f (>=0.65), AUC(T)-AUC(M)=%+.3f (>=0.05) => thresholds CLEARED: '
                'tie features carry held-out flip signal; provisional predictor claim licensed '
                'by the roadmap rule (single benchmark, exploratory).' % (_t, _d))
else:
    decision = ('AUC(T)=%.3f, AUC(T)-AUC(M)=%+.3f => a threshold FAILED: '
                'tie story stays DESCRIPTIVE, no predictor claim.' % (_t, _d))
L_md = []
L_md.append('# DENEY 2 (c1) — tie-mass decomposition + flip predictor (LME)\n')
L_md.append('**%s**\n' % LABELS)
L_md.append('Frozen protocol verbatim (lexsort tie priorities, 20 trials, fractional R@3); '
            'numpy only; no network. Factors: per-question frozen pkls (470), '
            'ALL-500 lex ordinals, stored natives from pilot_results.json, drop matrix from per_axis_matrices.npz.\n')
L_md.append('## 1. Gates (all must pass; abort otherwise)\n')
L_md.append('| Gate | Recomputed | Expected | Diff |')
L_md.append('|---|---|---|---|')
L_md.append('| Native mean | %.16f | %.16f | %.1e |' % (nat, EXP_NATIVE, abs(nat - EXP_NATIVE)))
for k in EXP:
    v = float(A(k).mean())
    L_md.append('| %s | %.14f | %.14f | %.1e |' % (k, v, EXP[k], abs(v - EXP[k])))
L_md.append('| per-q native vs stored | max abs diff %.1e (470/470) | | |' % nat_maxdiff)
L_md.append('\n**All gates PASS.**\n')
L_md.append('## 2. Arms (mirror pilots)\n')
L_md.append('- TOP48: `od=np.argsort(var,kind="stable")[::-1]; od[:48]`; BOT48: `od[::-1][:48]` (RTD/E2 convention).')
L_md.append('- RAND48: `rng(12000+s).choice(96,48)`, s=0,1,2.')
L_md.append('- drop64: top-64 axes by full-data drop utility U_drop=mean(native-FR_drop_a); '
            'top-5 axes %s. **GOLD-INFORMED, analysis-only.**' % drop_order[:5].tolist())
L_md.append('- Arm FR means: ' + '; '.join('%s=%.4f' % (k, armFR[k]) for k in
            ['NATIVE', 'TOP48', 'BOT48', 'RAND48_s0', 'RAND48_s1', 'RAND48_s2', 'RAND48_mean', 'DROP64']) + '\n')
L_md.append('## 3. Flip target\n')
L_md.append('delta = FR(TOP48) - mean(FR RAND48 seeds); win delta>1e-12, tie |delta|<=1e-12, loss below. '
            'W/T/L = %d/%d/%d; mean gap %.2f pp; median %.2f pp.' %
            (len(W), len(T), len(L), 100 * float(gap.mean()), 100 * float(np.median(gap))))
L_md.append('Primary binary target: loss-vs-win, ties excluded (n=%d; ties carry no flip direction; '
            'an ordinal target would be tie-dominated).' % (len(W) + len(L)))
L_md.append('Split: train iff first hex char of sha256("c1|"+qid) even -> train %d / test %d; '
            'binary train n=%d (wins %d), test n=%d (wins %d).' %
            (n_train, 470 - n_train, res_T['train_n'], res_T['train_wins'], res_T['test_n'], res_T['test_wins']) + '\n')
L_md.append('## 4. Held-out AUC (test split; positive class = win)\n')
L_md.append('| Model | Features | Train AUC | Test AUC |')
L_md.append('|---|---|---|---|')
L_md.append('| T (tie) | tie_mass_at_dgold, margin, strictly_closer | %.3f | %.3f |' % (res_T['train_auc'], res_T['test_auc']))
L_md.append('| M (mean) | d_gold_mean, mean_nongold, min_nongold, top20_entropy | %.3f | %.3f |' % (res_M['train_auc'], res_M['test_auc']))
L_md.append('| T+M | all 7 | %.3f | %.3f |' % (res_TM['train_auc'], res_TM['test_auc']))
L_md.append('\nDecision reference: AUC(T)>=0.65 AND AUC(T)-AUC(M)>=0.05 for a predictor claim. '
            'Observed: AUC(T)=%.3f, AUC(T)-AUC(M)=%+.3f.' % (res_T['test_auc'], res_T['test_auc'] - res_M['test_auc']))
L_md.append('**Verdict: %s**\n' % decision)
L_md.append('## 5. Standardized coefficients (train fit; + favors win)\n')
for nm, r in [('T', res_T), ('M', res_M), ('TM', res_TM)]:
    L_md.append('- %s: ' % nm + '; '.join('%s=%+.3f' % (k, v) for k, v in r['coef'].items()))
L_md.append('\n## 6. Per-arm feature table (means: wins vs losses)\n')
L_md.append('| feature | TOP48 win | TOP48 loss | RANDmean win | RANDmean loss | BOT48 win | BOT48 loss | DROP64 win | DROP64 loss |')
L_md.append('|---|---|---|---|---|---|---|---|---|')
for f in ALLF:
    L_md.append('| %s | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f | %.3f |' % (
        f, ftab['TOP48'][f]['win'], ftab['TOP48'][f]['loss'],
        ftab['RAND48_mean'][f]['win'], ftab['RAND48_mean'][f]['loss'],
        ftab['BOT48'][f]['win'], ftab['BOT48'][f]['loss'],
        ftab['DROP64'][f]['win'], ftab['DROP64'][f]['loss']))
L_md.append('\n## 7. Honesty: what this cannot show\n')
L_md.append('- Single benchmark (LME-470), single representation family; no cross-benchmark claim.')
L_md.append('- drop64 is gold-informed (full-data utility) and analysis-only; its FR is not a selection claim.')
L_md.append('- Binary target drops ties, shrinking n (test binary n=%d); CIs are wide; no CI computed here.' % res_T['test_n'])
L_md.append('- Model features use TOP48-arm geometry only; arm-difference features might predict better but would bake in the baseline.')
L_md.append('- Logistic IRLS is one arbitrary learner (L2 lam=1.0); AUC differences near +/-0.03 are noise-scale at this n.')
L_md.append('- Correlation/description only: no causal claim about why top-variance fails; mechanism stays OPEN.')
L_md.append('- Margin/entropy use trial-0 ordering (declared); trial-averaged ranks could differ slightly.')
open(OUT + '/d2_report.md', 'w').write('\n'.join(L_md))
print('wrote d2_report.md', flush=True)

print('BEGIN_D2_KEY_NUMBERS')
print('native=%.16f' % nat)
for k in EXP:
    print('%s=%.14f' % (k, float(A(k).mean())))
print('RAND48_mean=%.14f DROP64=%.14f' % (armFR['RAND48_mean'], armFR['DROP64']))
print('WTL_vs_randmean=%d/%d/%d mean_gap_pp=%.4f' % (len(W), len(T), len(L), 100 * float(gap.mean())))
print('split_train_test=%d/%d bintrain_n=%d bintest_n=%d' %
      (n_train, 470 - n_train, res_T['train_n'], res_T['test_n']))
print('AUC_T_train=%.4f AUC_T_test=%.4f' % (res_T['train_auc'], res_T['test_auc']))
print('AUC_M_train=%.4f AUC_M_test=%.4f' % (res_M['train_auc'], res_M['test_auc']))
print('AUC_TM_train=%.4f AUC_TM_test=%.4f' % (res_TM['train_auc'], res_TM['test_auc']))
print('coef_T=' + json.dumps(res_T['coef'], sort_keys=True))
print('coef_M=' + json.dumps(res_M['coef'], sort_keys=True))
print('DECISION: ' + decision)
print('END_D2_KEY_NUMBERS')
