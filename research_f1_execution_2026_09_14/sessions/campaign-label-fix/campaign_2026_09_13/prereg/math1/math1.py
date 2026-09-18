#!/usr/bin/env python3
"""MATH-1: analytic model of top-3 sign-code retrieval + validation on frozen LME-470 data.
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]
Read-only /mnt/c; writes only /tmp/math1/.
"""
import json, pickle, glob, time, math
import numpy as np
from pathlib import Path

BUNDLE = Path('/mnt/c/Users/MDP/dev/llmzip-work/review_transfer/EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13')
PIL = BUNDLE/'pilots/axis_attack_2026-09-12'
PKLDIR = Path('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr')
OUT = Path('/tmp/math1')
K, NT = 3, 20
NATIVE_ANCHOR = 0.5419751773049645

def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100

# ---------- LEVEL-1 EXACT MODEL ----------
def exact_frac_r3(d, gold, k=K):
    """Exact E[fractional R@k] under conditional-uniform tie resolution.
    d: int array (n,); gold: int array of row indices.
    Per-gold inclusion P = 0 if S>=k; 1 if S+T<=k; else (k-S)/T,
    S=#{d_i<d_g}, T=#{d_i==d_g}; mean over golds (linearity of expectation)."""
    d = np.asarray(d); g = np.asarray(gold).ravel()
    tot = 0.0
    for gg in g:
        dg = d[int(gg)]
        S = int(np.count_nonzero(d < dg)); T = int(np.count_nonzero(d == dg))
        if S >= k: p = 0.0
        elif S + T <= k: p = 1.0
        else: p = (k - S) / T
        tot += p
    return tot / len(g)

def measured_frac_r3(d, gold, pr, k=K):
    """Frozen 20-trial scheme: lexsort((priority, distance)) top-k fractional recall."""
    d = np.asarray(d); g = np.asarray(gold).ravel()
    gg = set(map(int, g)); trials = []
    for p in pr:
        order = np.lexsort((p, d))
        trials.append(len(set(map(int, order[:k])) & gg) / len(gg))
    return float(np.mean(trials)), trials

def tie_stats(d, gold):
    """Mean over golds of (S, T, d_g); plus non-gold histogram moments."""
    d = np.asarray(d); g = np.asarray(gold).ravel()
    n = len(d); mask = np.zeros(n, bool); mask[g] = True
    ng = d[~mask]
    Ss, Ts, dgs = [], [], []
    for gg in g:
        dg = d[int(gg)]
        Ss.append(int(np.count_nonzero(d < dg))); Ts.append(int(np.count_nonzero(d == dg))); dgs.append(int(dg))
    return (float(np.mean(Ss)), float(np.mean(Ts)), float(np.mean(dgs)),
            float(ng.mean()) if len(ng) else float('nan'),
            float(ng.std()) if len(ng) else float('nan'), len(ng))
# ---------- LEVEL-2: binomial plug-in (independent-bits strawman) ----------
def plugin_frac_r3(d, gold, b, n_mc=3000, rng=None, k=K):
    """Independent-bits plug-in: non-gold distances iid ~ Binomial(b, phat),
    phat = empirical non-gold mean/b; gold distances fixed. E[exact formula]
    over multinomial (S,T) draws. Returns MC estimate."""
    d = np.asarray(d); g = np.asarray(gold).ravel()
    n = len(d); mask = np.zeros(n, bool); mask[g] = True
    ng = d[~mask]; Np = len(ng)
    if Np == 0: return exact_frac_r3(d, gold, k)
    phat = float(ng.mean()) / b
    phat = min(max(phat, 1e-12), 1 - 1e-12)
    if rng is None: rng = np.random.default_rng(777)
    tot = 0.0
    # precompute binomial pmf values at needed points via log-comb loop
    from math import comb
    def binpmf(x):
        return comb(b, x) * (phat ** x) * ((1 - phat) ** (b - x))
    for gg in g:
        dg = int(d[int(gg)])
        Flo = sum(binpmf(x) for x in range(0, dg))
        Feq = binpmf(dg) if 0 <= dg <= b else 0.0
        draws = rng.multinomial(Np, [Flo, Feq, max(0.0, 1 - Flo - Feq)], size=n_mc)
        Sfix = int(np.count_nonzero(d[list(map(int, g))] < dg))
        Tfix = int(np.count_nonzero(d[list(map(int, g))] == dg))
        S = Sfix + draws[:, 0]; T = Tfix + draws[:, 1]
        p = np.where(S >= k, 0.0, np.where(S + T <= k, 1.0, (k - S) / np.maximum(T, 1)))
        tot += float(p.mean())
    return tot / len(g)

def hspec_qs_only(seed, b):
    r = np.random.default_rng(seed); r.permutation(96); qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b)); Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0); qs.append(Q * sg[None, :])
    return qs

def happly(X, perm, qs, b):
    xp = np.asarray(X, float)[..., perm]; o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b); o[..., sl] = xp[..., sl] @ Q
    return o

def load_all():
    t0 = time.time()
    qsorted = json.loads((BUNDLE/'protocol_sources/qids_500_sorted.json').read_text())
    assert len(qsorted) == 500
    lex = {q: i for i, q in enumerate(qsorted)}
    pkls = sorted(glob.glob(str(PKLDIR/'*.pkl')))
    assert len(pkls) == 470, len(pkls)
    D0, Q0, GOLD, PR, QIDS, VAR = {}, {}, {}, {}, [], {}
    for p in pkls:
        with open(p, 'rb') as f: o = pickle.load(f)
        qid = str(o['question_id'])
        C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
        g = np.asarray(o['gold']).ravel()
        D = C >= 0; Q = qC >= 0
        D0[qid] = D; Q0[qid] = Q; GOLD[qid] = g; QIDS.append(qid)
        VAR[qid] = np.asarray(o['C'], float).var(axis=0)
        lx = lex[qid]
        PR[qid] = [np.random.default_rng(stable_archive_seed(lx, t) + 99).random(len(C)) for t in range(NT)]
    print(f'loaded 470 pkls in {time.time()-t0:.0f}s', flush=True)
    return lex, D0, Q0, GOLD, PR, QIDS, VAR

def panel_cols(VAR, qid, rand48):
    od = np.argsort(VAR[qid], kind='stable')[::-1]
    return {'NATIVE96': np.arange(96), 'SPREAD48': od[::2][:48],
            'TOP48': od[:48], 'RAND48_s0': rand48, 'BOT48': od[::-1][:48]}

def run_panel(D0, Q0, GOLD, PR, QIDS, VAR):
    rng = np.random.default_rng(12000); rand48 = np.sort(rng.choice(96, 48, replace=False))
    arms = ['NATIVE96', 'SPREAD48', 'TOP48', 'RAND48_s0', 'BOT48']
    out = {a: {'exact': [], 'meas': [], 'plugin': [], 'tvar': [], 'S': [], 'T': [], 'dg': [], 'ngm': [], 'ngs': []} for a in arms}
    prng = np.random.default_rng(777001)
    for qi, qid in enumerate(QIDS):
        D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
        cols = panel_cols(VAR, qid, rand48)
        for a in arms:
            cc = cols[a]; b = len(cc)
            d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
            e = exact_frac_r3(d, g); m, tr = measured_frac_r3(d, g, pr)
            pl = plugin_frac_r3(d, g, b, rng=prng)
            S, T, dg, ngm, ngs, Np = tie_stats(d, g)
            o = out[a]
            o['exact'].append(e); o['meas'].append(m); o['plugin'].append(pl)
            o['tvar'].append(float(np.var(tr, ddof=1)) if len(tr) > 1 else 0.0)
            o['S'].append(S); o['T'].append(T); o['dg'].append(dg); o['ngm'].append(ngm); o['ngs'].append(ngs)
        if (qi + 1) % 100 == 0: print(f'  panel {qi+1}/470', flush=True)
    return out, [int(x) for x in rand48]

def run_budget(D0, Q0, GOLD, PR, QIDS, VAR):
    BLIST = [8, 16, 24, 32, 48, 64, 80]
    out = {}
    for b in BLIST:
        cb = np.random.default_rng(12000).choice(96, b, replace=False)
        out[f'RAND{b}'] = cb
    res = {}
    prng = np.random.default_rng(888002)
    for qi, qid in enumerate(QIDS):
        D, Q, g, pr = D0[qid], Q0[qid], GOLD[qid], PR[qid]
        od = np.argsort(VAR[qid], kind='stable')[::-1]
        for b in BLIST:
            for tag, cc in (('TOP', od[:b]), ('RAND', out[f'RAND{b}'])):
                d = np.count_nonzero(D[:, cc] != Q[cc][None, :], axis=1)
                key = f'{tag}{b}'
                r = res.setdefault(key, {'exact': [], 'meas': []})
                e = exact_frac_r3(d, g); m, _ = measured_frac_r3(d, g, pr)
                r['exact'].append(e); r['meas'].append(m)
                if tag == 'RAND' and b in (16, 32, 64):
                    r.setdefault('plugin', []).append(plugin_frac_r3(d, g, b, n_mc=1500, rng=prng))
        if (qi + 1) % 100 == 0: print(f'  budget {qi+1}/470', flush=True)
    return res

def run_mixing(QIDS, lex, seeds=(43001, 44001)):
    res = {}
    for s in seeds:
        qs = hspec_qs_only(s, 2)
        acc = {a: {'meas': [], 'exact': [], 'ngs': [], 'T': [], 'S': []} for a in ('matched', 'random', 'antimatched')}
        for qi, qid in enumerate(QIDS):
            with open(PKLDIR/(qid + '.pkl'), 'rb') as f: o = pickle.load(f)
            C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
            g = np.asarray(o['gold']).ravel(); n = len(C)
            var = C.var(axis=0)
            rank_desc = np.argsort(var, kind='stable')[::-1]
            am = np.empty(96, dtype=int); am[0::2] = rank_desc[:48]; am[1::2] = rank_desc[::-1][:48]
            perms = {'random': np.random.default_rng(s).permutation(96),
                     'matched': np.argsort(var, kind='stable'), 'antimatched': am}
            pr = [np.random.default_rng(stable_archive_seed(lex[qid], t) + 99).random(n) for t in range(NT)]
            for a, perm in perms.items():
                Cr = happly(C, perm, qs, 2); qr = happly(qC, perm, qs, 2)
                d = np.count_nonzero((Cr >= 0) != (qr >= 0)[None, :], axis=1)
                m, _ = measured_frac_r3(d, g, pr); e = exact_frac_r3(d, g)
                S, T, dg, ngm, ngs, Np = tie_stats(d, g)
                acc[a]['meas'].append(m); acc[a]['exact'].append(e)
                acc[a]['ngs'].append(ngs); acc[a]['T'].append(T); acc[a]['S'].append(S)
            if (qi + 1) % 100 == 0: print(f'  mixing s={s} {qi+1}/470', flush=True)
        res[str(s)] = {a: {'meas_mean': float(np.mean(v['meas'])), 'exact_mean': float(np.mean(v['exact'])),
                           'ngs_mean': float(np.nanmean(v['ngs'])), 'T_mean': float(np.mean(v['T'])),
                           'S_mean': float(np.mean(v['S']))} for a, v in acc.items()}
    return res

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    xm, ym = x - x.mean(), y - y.mean()
    return float(xm @ ym / math.sqrt((xm @ xm) * (ym @ ym)))

def main():
    t0 = time.time()
    lex, D0, Q0, GOLD, PR, QIDS, VAR = load_all()
    panel, rand48cols = run_panel(D0, Q0, GOLD, PR, QIDS, VAR)
    budget = run_budget(D0, Q0, GOLD, PR, QIDS, VAR)
    mixing = run_mixing(QIDS, lex)
    arms = ['NATIVE96', 'SPREAD48', 'TOP48', 'RAND48_s0', 'BOT48']
    summary = {}
    for a in arms:
        o = panel[a]
        ex, me = np.array(o['exact']), np.array(o['meas'])
        rmse = float(np.sqrt(np.mean((me - ex) ** 2)))
        floor = float(np.sqrt(np.mean(np.array(o['tvar']) / NT)))
        summary[a] = {'pred_mean': float(ex.mean()), 'meas_mean': float(me.mean()),
                      'plugin_mean': float(np.mean(o['plugin'])),
                      'pearson': pearson(ex, me), 'mae': float(np.mean(np.abs(me - ex))),
                      'rmse': rmse, 'mc_floor_rmse': floor,
                      'S_mean': float(np.mean(o['S'])), 'T_mean': float(np.mean(o['T'])),
                      'dg_mean': float(np.mean(o['dg'])), 'ngm_mean': float(np.nanmean(o['ngm'])),
                      'ngs_mean': float(np.nanmean(o['ngs']))}
    # paradox stats: TOP48 vs RAND48_s0
    dm = np.array(panel['TOP48']['meas']) - np.array(panel['RAND48_s0']['meas'])
    W, T, L = int((dm > 1e-12).sum()), int((np.abs(dm) <= 1e-12).sum()), int((dm < -1e-12).sum())
    ST, SR = np.array(panel['TOP48']['S']), np.array(panel['RAND48_s0']['S'])
    win, los = dm > 1e-12, dm < -1e-12
    S_winlos = [float(ST[win].mean()) if win.sum() else float('nan'), float(ST[los].mean()) if los.sum() else float('nan')]
    sepT = np.array(panel['TOP48']['ngm']) - np.array(panel['TOP48']['dg'])
    sepR = np.array(panel['RAND48_s0']['ngm']) - np.array(panel['RAND48_s0']['dg'])
    sepwin = int((sepT > sepR).sum())
    paradox = {'WTL_top_vs_rand_s0': [W, T, L], 'S_top_wins_vs_losses': S_winlos,
               'frac_q_sep_favors_top': float(np.mean(sepT > sepR)),
               'frac_q_fr_favors_top': float(np.mean(np.array(panel['TOP48']['meas']) > np.array(panel['RAND48_s0']['meas']))),
               'mean_sep_top': float(sepT.mean()), 'mean_sep_rand': float(sepR.mean())}
    budget_sum = {k: {'meas_mean': float(np.mean(v['meas'])), 'exact_mean': float(np.mean(v['exact'])),
                      'plugin_mean': float(np.mean(v['plugin'])) if 'plugin' in v else None} for k, v in budget.items()}
    # gates vs frozen published numbers
    pilot = json.loads((PIL/'pilot_results.json').read_text())
    nat_pub = pilot['per_question_native_FR']
    nat_re = np.array([panel['NATIVE96']['meas'][i] for i in range(len(QIDS))])
    nat_pu = np.array([nat_pub[q] for q in QIDS])
    probe = json.loads((PIL/'probe48.json').read_text())
    extra = json.loads((PIL/'extra_arms.json').read_text())
    corr = json.loads((PIL/'pilot_results_corrections.json').read_text())
    gates = {'native_agg': float(nat_re.mean()), 'native_anchor': NATIVE_ANCHOR,
             'native_perq_maxdiff_vs_pilot': float(np.max(np.abs(nat_re - nat_pu))),
             'top48_vs_probe': [summary['TOP48']['meas_mean'], probe['TOP48']['FR_mean']],
             'rand48s0_vs_probe': [summary['RAND48_s0']['meas_mean'], probe['RAND48_s0']['FR_mean']],
             'bot48_vs_probe': [summary['BOT48']['meas_mean'], probe['BOT48']['FR_mean']],
             'spread48_vs_extra': [summary['SPREAD48']['meas_mean'], extra['RANKSTRIDE48']],
             'e4_corr_keys': {k: v for k, v in corr.get('E4_seeds5', {}).items()} if isinstance(corr, dict) else {}}
    det = {'labels': ['[LOCAL EXPLORATORY]', '[NOT PREREGISTERED]', '[NOT FOR CITATION]'],
           'arms_summary': summary, 'paradox': paradox, 'wtl': {'W': W, 'T': T, 'L': L},
           'budget': budget_sum, 'mixing': mixing, 'gates': gates,
           'rand48_s0_cols': rand48cols,
           'per_question': {a: {'exact': [float(x) for x in panel[a]['exact']],
                                'meas': [float(x) for x in panel[a]['meas']]} for a in arms},
           'qids': QIDS, 'elapsed_s': time.time() - t0}
    (OUT/'math1_details.json').write_text(json.dumps(det), encoding='utf-8')
    print('GATES ' + json.dumps({k: v for k, v in gates.items() if k != 'e4_corr_keys'}) + f' elapsed={time.time()-t0:.0f}s', flush=True)
    for a in arms:
        s = summary[a]
        print(f"ARM {a}: pred={s['pred_mean']:.6f} meas={s['meas_mean']:.6f} plugin={s['plugin_mean']:.6f} r={s['pearson']:.5f} mae={s['mae']:.5f} rmse={s['rmse']:.5f} floor={s['mc_floor_rmse']:.5f} S={s['S_mean']:.3f} T={s['T_mean']:.3f} dg={s['dg_mean']:.3f} ngm={s['ngm_mean']:.3f} ngs={s['ngs_mean']:.3f}", flush=True)
    print('PARADOX ' + json.dumps(paradox), flush=True)
    print('BUDGET ' + json.dumps({k: [round(v['meas_mean'], 5), round(v['exact_mean'], 5), (round(v['plugin_mean'], 5) if v['plugin_mean'] is not None else None)] for k, v in budget_sum.items()}), flush=True)
    print('MIXING ' + json.dumps(mixing), flush=True)
    return det

if __name__ == '__main__':
    main()
