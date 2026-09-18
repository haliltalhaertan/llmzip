#!/usr/bin/env python3
"""
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

INDEPENDENT AUDIT re-implementation of the R2 Claim-D competition metric.
Written ONLY from:
  - R2_COMPETITION_RERUN_CONTRACT.md  (TOP64/BOT64 defn, per-gold competition defn, Spearman avg-rank)
  - E1_PREANALYSIS_SPEC_V2.md         (Delta_q defn, v_j = mean_i(C_ij^2))
  - bench3/b3b_perltqa/step2_eval.py  (frozen FR@3 = met()[2], K=3, NT=20 tie convention)
NO coordinator script was read before this file was frozen.

Author: audit subagent. Numbers emitted here go to MY_NUMBERS.md and are frozen.
"""
import glob, json, os, pickle, sys
import numpy as np

B = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit'
K = 3
NT = 20

# ---------------------------------------------------------------- primitives
def avg_ranks(x):
    """Average ranks for ties (contract: 'Spearman uses average ranks for ties')."""
    x = np.asarray(x, float)
    n = len(x)
    order = np.argsort(x, kind='stable')
    xs = x[order]
    r = np.empty(n, float)
    i = 0
    while i < n:
        j = i + 1
        while j < n and xs[j] == xs[i]:
            j += 1
        r[order[i:j]] = (i + 1 + j) / 2.0   # 1-based average rank
        i = j
    return r

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    a = x - x.mean(); b = y - y.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else float('nan')

def spearman(x, y):
    return pearson(avg_ranks(x), avg_ranks(y))

def topbot64(C):
    """Contract: v_j = mean_i(C_ij^2); stable DESCENDING sort; TOP64=first 64, BOT64=last 64."""
    v = np.mean(np.asarray(C, float) ** 2, axis=0)
    order_desc = np.argsort(-v, kind='stable')
    return np.sort(order_desc[:64]).astype(int), np.sort(order_desc[-64:]).astype(int), v

def fr3_exact(scores_desc_better, gold, K=3):
    """
    EXACT expectation of FR@K = |gold cap topK|/|gold| under uniform random tie-breaking.
    scores_desc_better: array where SMALLER = better (a distance). Caller converts.
    This is the NT->infinity limit of the frozen NT=20 seeded-permutation average,
    and is exactly order-independent.
    """
    d = np.asarray(scores_desc_better, float)
    sd = np.sort(d)
    dK = sd[K - 1]
    lt = int(np.count_nonzero(d < dK))
    bc = int(np.count_nonzero(d == dK))
    slots = K - lt
    g = np.asarray(gold, int)
    dg = d[g]
    g_strict = int(np.count_nonzero(dg < dK))
    g_tied = int(np.count_nonzero(dg == dK))
    return (g_strict + g_tied * (slots / bc)) / len(g)

def fr3_perm(d, gold, perms, K=3):
    """Frozen convention: mean over NT seeded permutations, lexsort tie-break."""
    d = np.asarray(d, float); gg = set(int(x) for x in np.asarray(gold).ravel())
    acc = []
    for p in perms:
        top = np.lexsort((p, d))[:K]
        acc.append(len(gg & set(int(t) for t in top)) / len(gg))
    return float(np.mean(acc))

def competition(dTOP, dBOT, gold):
    """
    Contract 'Correct per-gold competition metric'.
    For every gold row g SEPARATELY, arm A in {TOP64,BOT64}:
       strict_all(A,g) = count_i[ d_A(i) <  d_A(g) ]
       tie_all(A,g)    = count_i[ d_A(i) == d_A(g) ]
    Aggregate inside query by ARITHMETIC MEAN over gold rows.
    Distances are integer Hamming -> exact == comparison is valid and required.
    """
    g = np.asarray(gold, int)
    out = {}
    for name, d in (('TOP', dTOP), ('BOT', dBOT)):
        dg = d[g]                                  # (G,)
        strict = (d[None, :] < dg[:, None]).sum(axis=1)   # (G,)
        tie = (d[None, :] == dg[:, None]).sum(axis=1)     # includes g itself
        out['STRICT_' + name] = float(strict.mean())
        out['TIE_' + name] = float(tie.mean())
        # mandatory sensitivity variant: all gold rows excluded from competitor mask
        mask = np.ones(len(d), bool); mask[g] = False
        dn = d[mask]
        sn = (dn[None, :] < dg[:, None]).sum(axis=1)
        tn = (dn[None, :] == dg[:, None]).sum(axis=1)
        out['NG_STRICT_' + name] = float(sn.mean())
        out['NG_TIE_' + name] = float(tn.mean())
    out['STRICT_GAP'] = out['STRICT_TOP'] - out['STRICT_BOT']
    out['TIE_GAP'] = out['TIE_TOP'] - out['TIE_BOT']
    out['NG_STRICT_GAP'] = out['NG_STRICT_TOP'] - out['NG_STRICT_BOT']
    out['NG_TIE_GAP'] = out['NG_TIE_TOP'] - out['NG_TIE_BOT']
    return out

def mingold_competition(dTOP, dBOT, gold):
    """The R1 BUG, for the control: replace multi-gold query by dmin=min(d[gold]), count once."""
    g = np.asarray(gold, int)
    out = {}
    for name, d in (('TOP', dTOP), ('BOT', dBOT)):
        dmin = d[g].min()
        out['STRICT_' + name] = float(np.count_nonzero(d < dmin))
        out['TIE_' + name] = float(np.count_nonzero(d == dmin))
    out['STRICT_GAP'] = out['STRICT_TOP'] - out['STRICT_BOT']
    out['TIE_GAP'] = out['TIE_TOP'] - out['TIE_BOT']
    return out

def cos_scores(C, q):
    dn = np.linalg.norm(C, axis=1); qn = np.linalg.norm(q)
    return (C @ q) / (dn * qn)

def hamming(D0, Q0, cols=None):
    if cols is None:
        return np.count_nonzero(D0 != Q0[None, :], axis=1)
    return np.count_nonzero(D0[:, cols] != Q0[cols][None, :], axis=1)

# ---------------------------------------------------------------- loaders
def load_lme():
    rows = []
    center_max = 0.0
    for f in sorted(glob.glob(B + '/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); qC = np.asarray(d['qC'], float)
        gold = np.asarray(d['gold']).ravel().astype(int)
        center_max = max(center_max, float(np.abs(C.mean(axis=0)).max()))
        rows.append(dict(qid=str(d['question_id']), cluster=str(d['question_id']),
                         C=C, qC=qC, gold=gold, section=None))
    return rows, center_max

def load_realtalk():
    rows = []; center_max = 0.0
    for f in sorted(glob.glob(B + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
        center_max = max(center_max, float(np.abs(C.mean(axis=0)).max()))
        chat = str(d['chat_no'])
        for i, qid in enumerate(d['qids']):
            g = np.asarray(d['gold_rows'][i]).ravel().astype(int)
            if len(g) == 0:
                continue
            if g.min() < 0 or g.max() >= C.shape[0]:
                continue
            q = QC[i]
            if not np.all(np.isfinite(q)) or np.linalg.norm(q) == 0:
                continue
            rows.append(dict(qid=str(qid), cluster=chat, C=C, qC=q, gold=g, section=None))
    return rows, center_max

def load_perltqa():
    arch = pickle.load(open(B + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    QD = pickle.load(open(B + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    center_max = 0.0
    AC = {}
    for ch, a in arch.items():
        C = np.asarray(a['C'], float)
        center_max = max(center_max, float(np.abs(C.mean(axis=0)).max()))
        AC[ch] = C
    rows = []
    for qid, q in QD.items():
        ch = q['char']
        rows.append(dict(qid=str(qid), cluster=str(ch), C=AC[ch],
                         qC=np.asarray(q['qC'], float),
                         gold=np.asarray(q['gold']).ravel().astype(int),
                         section=str(q['section'])))
    return rows, center_max

# ---------------------------------------------------------------- main run
def run_bench(name, rows, center_max):
    # cache per-archive structures keyed by id(C) to avoid recompute
    archcache = {}
    def arch_for(C):
        k = id(C)
        if k not in archcache:
            t, b, v = topbot64(C)
            archcache[k] = (C >= 0, t, b)
        return archcache[k]

    per_q = []
    for r in rows:
        C = r['C']; qC = r['qC']; gold = r['gold']
        D0, tcols, bcols = arch_for(C)
        Q0 = qC >= 0
        d_sign = hamming(D0, Q0)
        s_float = cos_scores(C, qC)
        if not np.all(np.isfinite(s_float)):
            s_float = np.nan_to_num(s_float, nan=-1e18)
        # FR@3 exact expectation; float arm: higher cos = better -> negate to a "distance"
        fr_sign = fr3_exact(d_sign.astype(float), gold, K)
        fr_float = fr3_exact(-s_float.astype(float), gold, K)
        delta = fr_sign - fr_float
        dT = hamming(D0, Q0, tcols).astype(np.int64)
        dB = hamming(D0, Q0, bcols).astype(np.int64)
        comp = competition(dT, dB, gold)
        mg = mingold_competition(dT, dB, gold)
        per_q.append(dict(qid=r['qid'], cluster=r['cluster'], section=r['section'],
                          gold_n=int(len(gold)), delta=delta,
                          fr_sign=fr_sign, fr_float=fr_float,
                          STRICT_GAP=comp['STRICT_GAP'], TIE_GAP=comp['TIE_GAP'],
                          NG_STRICT_GAP=comp['NG_STRICT_GAP'], NG_TIE_GAP=comp['NG_TIE_GAP'],
                          MG_STRICT_GAP=mg['STRICT_GAP'], MG_TIE_GAP=mg['TIE_GAP'],
                          STRICT_TOP=comp['STRICT_TOP'], STRICT_BOT=comp['STRICT_BOT'],
                          TIE_TOP=comp['TIE_TOP'], TIE_BOT=comp['TIE_BOT']))

    dl = [p['delta'] for p in per_q]
    res = dict(
        benchmark=name, n=len(per_q),
        column_mean_abs_max=center_max,
        headline_sign=float(np.mean([p['fr_sign'] for p in per_q])),
        headline_float=float(np.mean([p['fr_float'] for p in per_q])),
        headline_delta_pp=100.0 * float(np.mean(dl)),
        multi_gold_n=int(sum(1 for p in per_q if p['gold_n'] > 1)),
        multi_gold_rate=float(np.mean([p['gold_n'] > 1 for p in per_q])),
        rho_strict=spearman(dl, [p['STRICT_GAP'] for p in per_q]),
        rho_tie=spearman(dl, [p['TIE_GAP'] for p in per_q]),
        rho_strict_nongold=spearman(dl, [p['NG_STRICT_GAP'] for p in per_q]),
        rho_tie_nongold=spearman(dl, [p['NG_TIE_GAP'] for p in per_q]),
        rho_strict_MINGOLD_BUG=spearman(dl, [p['MG_STRICT_GAP'] for p in per_q]),
        rho_tie_MINGOLD_BUG=spearman(dl, [p['MG_TIE_GAP'] for p in per_q]),
        n_clusters=len(set(p['cluster'] for p in per_q)),
    )
    if name == 'PERLTQA':
        secs = {}
        for s in sorted(set(p['section'] for p in per_q)):
            rr = [p for p in per_q if p['section'] == s]
            secs[s] = dict(n=len(rr),
                           strict=spearman([p['delta'] for p in rr], [p['STRICT_GAP'] for p in rr]),
                           tie=spearman([p['delta'] for p in rr], [p['TIE_GAP'] for p in rr]))
        res['sections'] = secs
    # descriptive cluster bootstrap, seed 96013, B=2000
    res['bootstrap'] = bootstrap(per_q)
    return res, per_q

def bootstrap(per_q, seed=96013, Bn=2000):
    from collections import defaultdict
    gidx = defaultdict(list)
    for i, p in enumerate(per_q):
        gidx[p['cluster']].append(i)
    keys = sorted(gidx)
    rng = np.random.default_rng(seed)
    st = []; ti = []; invalid = {'nan_rho': 0, 'degenerate_constant': 0}
    for _ in range(Bn):
        pick = rng.integers(0, len(keys), len(keys))
        idx = []
        for k in pick:
            idx.extend(gidx[keys[k]])
        d = [per_q[i]['delta'] for i in idx]
        s = [per_q[i]['STRICT_GAP'] for i in idx]
        t = [per_q[i]['TIE_GAP'] for i in idx]
        rs = spearman(d, s); rt = spearman(d, t)
        if not (np.isfinite(rs) and np.isfinite(rt)):
            invalid['degenerate_constant'] += 1
            continue
        st.append(rs); ti.append(rt)
    return dict(seed=seed, B_attempted=Bn, B_valid=len(st),
                B_invalid=Bn - len(st), invalid_reasons=invalid,
                strict_ci=[float(np.percentile(st, 2.5)), float(np.percentile(st, 97.5))] if st else None,
                tie_ci=[float(np.percentile(ti, 2.5)), float(np.percentile(ti, 97.5))] if ti else None,
                note='descriptive/post-hoc, NOT preregistered inference; cluster-level resample')

if __name__ == '__main__':
    all_res = {}
    lme, cm = load_lme();       all_res['LME'], pqL = run_bench('LME', lme, cm)
    rt, cm = load_realtalk();   all_res['REALTALK'], pqR = run_bench('REALTALK', rt, cm)
    pl, cm = load_perltqa();    all_res['PERLTQA'], pqP = run_bench('PERLTQA', pl, cm)
    all_res['_meta'] = dict(
        note='INDEPENDENT AUDIT reimplementation. FR@3 uses EXACT tie expectation (NT->inf limit).',
        K=K, topbot_rule='v_j = mean_i(C_ij^2), stable descending, first64 / last64',
        locomo='NOT RUN: no committed per-query float96 surface in the local caches (checked).')
    json.dump(all_res, open(OUT + '/evidence/results.json', 'w'), indent=2)
    for b in ('LME', 'PERLTQA', 'REALTALK'):
        r = all_res[b]
        print(f"{b}: n={r['n']} strict={r['rho_strict']!r} tie={r['rho_tie']!r}")
        print(f"   headline sign={r['headline_sign']!r} float={r['headline_float']!r} delta_pp={r['headline_delta_pp']!r}")
        print(f"   multigold={r['multi_gold_rate']!r} ({r['multi_gold_n']}/{r['n']}) colmean={r['column_mean_abs_max']:.3e}")
        print(f"   MINGOLD-BUG strict={r['rho_strict_MINGOLD_BUG']!r} tie={r['rho_tie_MINGOLD_BUG']!r}")
        print(f"   nongold-sens strict={r['rho_strict_nongold']!r} tie={r['rho_tie_nongold']!r}")
        print(f"   boot strict={r['bootstrap']['strict_ci']} tie={r['bootstrap']['tie_ci']} valid={r['bootstrap']['B_valid']}")
    print(json.dumps(all_res['PERLTQA'].get('sections'), indent=1))
