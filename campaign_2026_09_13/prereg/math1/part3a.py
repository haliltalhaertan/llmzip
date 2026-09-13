
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
