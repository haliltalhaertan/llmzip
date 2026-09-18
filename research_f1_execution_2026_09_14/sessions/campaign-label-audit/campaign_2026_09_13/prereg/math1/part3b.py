
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
