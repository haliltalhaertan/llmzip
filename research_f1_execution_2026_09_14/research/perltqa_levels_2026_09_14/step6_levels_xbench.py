#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 6 (post-freeze, reported in CROSS_CHECK.md only):
 (a) Does the LEVELS relation itself -- sign(STRICT_GAP) == sign(Delta) at stratum level --
     survive on LME/REALTALK? This tests the MEASUREMENT, not the dead ALIGN proxy.
 (b) Adversarial: is ALIGN just qnorm? is profile's positive gap an artifact of gold_norm?
"""
import json, pickle, glob
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
K = 3

def spearman(x, y):
    rx = rankdata(x); ry = rankdata(y); rx = rx - rx.mean(); ry = ry - ry.mean()
    return float((rx @ ry) / np.sqrt((rx @ rx) * (ry @ ry)))

def fr_exact(s, gold, K=3):
    s = np.asarray(s, float); ss = np.sort(s)[::-1]; thr = ss[K - 1]
    st = int(np.count_nonzero(s > thr)); slots = K - st; bc = int(np.count_nonzero(s == thr))
    g = np.asarray(gold).ravel().astype(int); sg = s[g]
    return (int(np.count_nonzero(sg > thr)) + int(np.count_nonzero(sg == thr)) * slots / bc) / len(g)

def row_for(C, qC, gold):
    C = np.asarray(C, float); qC = np.asarray(qC, float).ravel()
    N = C.shape[0]; g = np.asarray(gold).ravel().astype(int)
    v = (C ** 2).mean(axis=0)
    o = np.argsort(-v, kind='stable')
    top = np.sort(o[:64]).astype(int); bot = np.sort(o[-64:]).astype(int)
    D0 = C >= 0; Q0 = qC >= 0
    d_f = np.count_nonzero(D0 != Q0[None, :], axis=1)
    d_t = np.count_nonzero(D0[:, top] != Q0[top][None, :], axis=1)
    d_b = np.count_nonzero(D0[:, bot] != Q0[bot][None, :], axis=1)
    def cg(d):
        dg = d[g]
        return (float(np.mean([np.count_nonzero(d < x) for x in dg])),
                float(np.mean([np.count_nonzero(d == x) for x in dg])))
    st_t, ti_t = cg(d_t); st_b, ti_b = cg(d_b)
    nrm = np.linalg.norm(C, axis=1)
    cosv = (C @ qC) / (nrm * np.linalg.norm(qC))
    w = qC ** 2
    gm = np.zeros(N, bool); gm[g] = True
    return dict(sign=fr_exact(-d_f.astype(float), g, K), float=fr_exact(cosv, g, K),
                strict_TOP64=st_t, strict_BOT64=st_b, STRICT_GAP=st_t - st_b,
                tie_TOP64=ti_t, tie_BOT64=ti_b, TIE_GAP=ti_t - ti_b,
                strictfrac_TOP=st_t / N, strictfrac_BOT=st_b / N,
                STRICT_GAP_frac=(st_t - st_b) / N,
                align=float((w @ v) / (np.linalg.norm(w) * np.linalg.norm(v))),
                qnorm=float(np.linalg.norm(qC)), N=N, gold_n=int(len(g)),
                gold_norm_rel=float(nrm[g].mean() / nrm.mean()),
                float_margin=float(cosv[g].max() - cosv[~gm].max()))

BENCH = {}
lme = []
for f in sorted(glob.glob(str(ROOT / 'regen/lme/cache_repr/*.pkl'))):
    d = pickle.load(open(f, 'rb'))
    r = row_for(d['C'], d['qC'], d['gold']); r['delta'] = r['sign'] - r['float']; lme.append(r)
BENCH['LongMemEval'] = lme
rt = []
for f in sorted(glob.glob(str(ROOT / 'bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))):
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
    for i, qid in enumerate(d['qids']):
        g = np.asarray(d['gold_rows'][i]).ravel().astype(int)
        if len(g) == 0: continue
        r = row_for(C, QC[i], g); r['delta'] = r['sign'] - r['float']
        r['chat'] = str(d.get('chat_no', f)); rt.append(r)
BENCH['REALTALK'] = rt
pl = pickle.load(open(OUT / 'evidence' / 'perltqa_levels_rows.pkl', 'rb'))
BENCH['PerLTQA'] = list(pl.values())

REP = {}
print('=== (a) LEVELS relation out-of-sample: sign(mean STRICT_GAP) vs sign(mean Delta) ===')
print(f'{"benchmark":14s}{"n":>7s}{"Delta_pp":>11s}{"STRICT_GAP":>12s}{"TIE_GAP":>10s}{"GAPfrac":>10s}{"rho(D,SG)":>11s}{"whole":>8s}')
for b, rs in BENCH.items():
    d = np.array([r['delta'] for r in rs]); sg = np.array([r['STRICT_GAP'] for r in rs])
    tg = np.array([r['TIE_GAP'] for r in rs])
    gf = np.array([r.get('STRICT_GAP_frac', r['STRICT_GAP'] / r['N']) for r in rs])
    okw = 'PASS' if (np.sign(sg.mean()) == np.sign(d.mean())) else 'FAIL'
    print(f'{b:14s}{len(rs):>7d}{d.mean()*100:>11.4f}{sg.mean():>12.4f}{tg.mean():>10.4f}{gf.mean():>10.5f}{spearman(sg,d):>11.5f}{okw:>8s}')
    REP[b] = dict(n=len(rs), delta_pp=float(d.mean() * 100), strict_gap=float(sg.mean()),
                  tie_gap=float(tg.mean()), gap_frac=float(gf.mean()),
                  rho_delta_strictgap=spearman(sg, d), whole=okw)

print('\n=== (a2) stratum-level test: LEVELS rule "mean STRICT_GAP > 0 => Delta > 0" ===')
strata = []
for s, rs in sorted({k: [r for r in BENCH['PerLTQA'] if r['section'] == k] for k in {r['section'] for r in BENCH['PerLTQA']}}.items()):
    strata.append(('PerLTQA/' + s, rs))
ch = defaultdict(list)
for r in rt: ch[r['chat']].append(r)
for c, rs in sorted(ch.items()): strata.append(('REALTALK/chat' + c, rs))
# LME deciles by STRICT_GAP-free stratifier: use archive size deciles (gold-free grouping)
lsg = np.array([r['N'] for r in lme]); ed = np.percentile(lsg, np.arange(0, 101, 10))
for i in range(10):
    m = [r for r in lme if (r['N'] >= ed[i] and (r['N'] <= ed[i + 1] if i == 9 else r['N'] < ed[i + 1]))]
    if m: strata.append((f'LME/Ndec{i+1}', m))
nok = 0; npos = 0; out = []
for nm, rs in strata:
    sg = float(np.mean([r['STRICT_GAP'] for r in rs])); d = float(np.mean([r['delta'] for r in rs]) * 100)
    p = '+' if sg > 0 else '-'; o = '+' if d > 0 else '-'
    nok += (p == o); npos += (d > 0)
    out.append(dict(stratum=nm, n=len(rs), strict_gap=sg, delta_pp=d, pred=p, obs=o, ok=bool(p == o)))
    print(f'  {nm:22s} n={len(rs):>5d} SG {sg:>10.3f} Delta {d:>+8.3f} pred {p} obs {o} {"Y" if p==o else "N"}')
maj = max(npos, len(strata) - npos)
print(f'  LEVELS-rule stratum accuracy {nok}/{len(strata)} = {nok/len(strata):.3f}  vs majority {maj}/{len(strata)} = {maj/len(strata):.3f}'
      f'  => {"BEATS" if nok>maj else "DOES NOT BEAT"}')
REP['levels_rule_strata'] = dict(rows=out, acc=nok / len(strata), majority=maj / len(strata), beats=bool(nok > maj))

print('\n=== (b) adversarial: ALIGN vs qnorm, and gold_norm artifact ===')
for b, rs in BENCH.items():
    d = np.array([r['delta'] for r in rs])
    print(f'  {b:12s} rho(D,align) {spearman([r["align"] for r in rs], d):+.5f}'
          f'  rho(D,qnorm) {spearman([r["qnorm"] for r in rs], d):+.5f}'
          f'  rho(align,qnorm) {spearman([r["align"] for r in rs], [r["qnorm"] for r in rs]):+.5f}'
          f'  rho(D,gold_norm_rel) {spearman([r["gold_norm_rel"] for r in rs], d):+.5f}'
          f'  rho(D,float_margin) {spearman([r["float_margin"] for r in rs], d):+.5f}')

print('\n=== (c) which single query property best tracks Delta cross-benchmark? ===')
cands = ['align', 'qnorm', 'gold_norm_rel', 'float_margin', 'STRICT_GAP', 'TIE_GAP', 'strict_TOP64', 'strict_BOT64', 'N', 'gold_n']
print(f'{"stat":16s}' + ''.join(f'{b:>14s}' for b in BENCH) + '   sign-consistent?')
for c in cands:
    rr = []
    for b, rs in BENCH.items():
        try: rr.append(spearman([r[c] for r in rs], [r['delta'] for r in rs]))
        except KeyError: rr.append(float('nan'))
    cons = 'YES' if (all(x > 0 for x in rr) or all(x < 0 for x in rr)) else 'no'
    print(f'{c:16s}' + ''.join(f'{x:>14.5f}' for x in rr) + f'   {cons}')
    REP.setdefault('cross_rho', {})[c] = rr

json.dump(REP, open(OUT / 'evidence' / 'step6.json', 'w'), indent=2, default=float)
print('\nwrote evidence/step6.json')
