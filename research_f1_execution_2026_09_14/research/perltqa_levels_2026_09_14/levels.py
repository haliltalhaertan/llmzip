#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 2+3: per-gold competition LEVELS (TOP64/BOT64) + query geometry, PerLTQA.

Definitions taken from spec blobs, not guessed:
 - R2_COMPETITION_RERUN_CONTRACT.md: v_j = mean_i(C_ij^2); stable descending sort;
   TOP64 = first 64 axes, BOT64 = last 64; codes C>=0 / qC>=0; ordinary Hamming.
 - per gold g, arm A: strict_all = #{i: d_A(i) < d_A(g)}, tie_all = #{i: d_A(i) == d_A(g)}
   (tie_all INCLUDES g itself); aggregate by arithmetic mean over gold rows.
 - GAP = TOP64 - BOT64. Sensitivity variant: competitors exclude all gold rows.
"""
import json, pickle
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
(OUT / 'evidence').mkdir(parents=True, exist_ok=True)
K = 3

arch = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
QD = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
DROWS = pickle.load(open(OUT / 'evidence' / 'perltqa_delta_rows.pkl', 'rb'))

# ---------------- axis ordering statistic: mean-of-squares vs variance --------
ordering_agree = []
A = {}
for char, a in arch.items():
    C = np.asarray(a['C'], float)
    v_ms = (C ** 2).mean(axis=0)          # spec: mean of squares
    v_var = C.var(axis=0)                 # step2_eval.py used this
    o_ms = np.argsort(-v_ms, kind='stable')
    o_var = np.argsort(-v_var, kind='stable')
    ordering_agree.append(bool(np.array_equal(o_ms, o_var)))
    top = np.sort(o_ms[:64]).astype(int)
    bot = np.sort(o_ms[-64:]).astype(int)
    D0 = C >= 0
    A[char] = dict(C=C, D0=D0, Dtop=D0[:, top], Dbot=D0[:, bot],
                   top=top, bot=bot, v=v_ms, N=C.shape[0],
                   nrm=np.linalg.norm(C, axis=1),
                   top_share=float(v_ms[top].sum() / v_ms.sum()))
print('axis ordering mean-of-squares == variance for all 30 archives:', all(ordering_agree))
print('max |v_ms - v_var| rel:', max(float(np.abs((np.asarray(a["C"],float)**2).mean(0) - np.asarray(a["C"],float).var(0)).max()) for a in arch.values()))

def comp(d, g, N, gmask):
    """per-gold strict/tie counts on one arm; mean over golds. Returns (strict, tie, strict_ng, tie_ng)."""
    dg = d[g]
    # all-competitor variant
    s = np.array([np.count_nonzero(d < x) for x in dg], float)
    t = np.array([np.count_nonzero(d == x) for x in dg], float)
    dn = d[~gmask]
    sn = np.array([np.count_nonzero(dn < x) for x in dg], float)
    tn = np.array([np.count_nonzero(dn == x) for x in dg], float)
    return s.mean(), t.mean(), sn.mean(), tn.mean()

rows = {}
for qid, q in QD.items():
    char = q['char']; a = A[char]; C = a['C']; N = a['N']
    qC = np.asarray(q['qC'], float)
    g = np.asarray(q['gold']).ravel().astype(int)
    gmask = np.zeros(N, bool); gmask[g] = True
    Q0 = qC >= 0
    d_full = np.count_nonzero(a['D0'] != Q0[None, :], axis=1)
    d_top = np.count_nonzero(a['Dtop'] != Q0[a['top']][None, :], axis=1)
    d_bot = np.count_nonzero(a['Dbot'] != Q0[a['bot']][None, :], axis=1)
    qn = np.linalg.norm(qC)
    cosv = (C @ qC) / (a['nrm'] * qn)

    r = dict(char=char, section=q['section'], gold_n=int(len(g)), N=int(N),
             delta=DROWS[qid]['delta'], sign=DROWS[qid]['sign'], float=DROWS[qid]['float'])
    for nm, d in (('TOP64', d_top), ('BOT64', d_bot), ('FULL96', d_full)):
        s, t, sn, tn = comp(d, g, N, gmask)
        r[f'strict_{nm}'] = s; r[f'tie_{nm}'] = t
        r[f'strictng_{nm}'] = sn; r[f'tieng_{nm}'] = tn
    r['STRICT_GAP'] = r['strict_TOP64'] - r['strict_BOT64']
    r['TIE_GAP'] = r['tie_TOP64'] - r['tie_BOT64']
    r['STRICT_GAP_ng'] = r['strictng_TOP64'] - r['strictng_BOT64']
    r['TIE_GAP_ng'] = r['tieng_TOP64'] - r['tieng_BOT64']
    # N-normalised levels (archives differ in N: 293..546)
    for nm in ('TOP64', 'BOT64', 'FULL96'):
        r[f'strictfrac_{nm}'] = r[f'strict_{nm}'] / N
        r[f'tiefrac_{nm}'] = r[f'tie_{nm}'] / N

    # ---------------- step 3 geometry (no Delta, no gold for the query-only ones)
    q2 = qC ** 2
    r['qnorm'] = float(qn)
    r['qPR'] = float(q2.sum() ** 2 / (q2 ** 2).sum())            # participation ratio / eff dim
    r['q_top_share'] = float(q2[a['top']].sum() / q2.sum())      # alignment w/ high-var axes
    r['q_absmax_share'] = float(q2.max() / q2.sum())
    # alignment of query energy profile with archive variance profile (cosine of q^2 vs v)
    v = a['v']
    r['q_v_align'] = float((q2 @ v) / (np.linalg.norm(q2) * np.linalg.norm(v)))
    r['arch_top_share'] = a['top_share']
    # gold-side
    r['gold_norm'] = float(a['nrm'][g].mean())
    r['gold_norm_rel'] = float(a['nrm'][g].mean() / a['nrm'].mean())
    r['doc_norm_mean'] = float(a['nrm'].mean())
    # float margin: best gold cos minus best non-gold cos
    r['float_margin'] = float(cosv[g].max() - cosv[~gmask].max())
    r['float_gold_cos'] = float(cosv[g].max())
    # hamming margin: best non-gold d minus best gold d (positive = gold strictly closer)
    r['ham_margin'] = float(d_full[~gmask].min() - d_full[g].min())
    r['ham_neartie'] = int(np.count_nonzero(d_full[~gmask] <= d_full[g].min()))
    r['ham_exacttie'] = int(np.count_nonzero(d_full[~gmask] == d_full[g].min()))
    r['gold_d'] = float(d_full[g].min())
    rows[qid] = r

pickle.dump(rows, open(OUT / 'evidence' / 'perltqa_levels_rows.pkl', 'wb'))
print('rows', len(rows))

# ---------------- gate 2: reproduce R2 audit Spearman targets -----------------
def spearman(x, y):
    from scipy.stats import rankdata
    rx = rankdata(x); ry = rankdata(y)
    rx = rx - rx.mean(); ry = ry - ry.mean()
    return float((rx @ ry) / np.sqrt((rx @ rx) * (ry @ ry)))

allr = list(rows.values())
D = np.array([r['delta'] for r in allr])
print('GATE2 rho(Delta,STRICT_GAP) =', spearman(D, np.array([r['STRICT_GAP'] for r in allr])), ' audit target 0.25416826537535475')
print('GATE2 rho(Delta,TIE_GAP)    =', spearman(D, np.array([r['TIE_GAP'] for r in allr])), ' audit target 0.27978783415712220')
secmap = defaultdict(list)
for r in allr:
    secmap[r['section']].append(r)
tgt = {'dialogues': (0.13054126734088975, 0.11123087254360414),
       'events': (0.39790634780463613, 0.38922832069574037),
       'profile': (0.0573253028779693, 0.018738683422868593),
       'social_relationship': (0.30428515802019, 0.2993013213223269)}
for s in sorted(secmap):
    rs = secmap[s]; d = np.array([r['delta'] for r in rs])
    print(f'  {s:20s} strict rho {spearman(d, np.array([r["STRICT_GAP"] for r in rs])):.6f} (tgt {tgt[s][0]:.6f})'
          f'  tie rho {spearman(d, np.array([r["TIE_GAP"] for r in rs])):.6f} (tgt {tgt[s][1]:.6f})')

# ---------------- LEVELS: means and distributions ----------------------------
FIELDS = ['strict_TOP64', 'strict_BOT64', 'STRICT_GAP', 'tie_TOP64', 'tie_BOT64', 'TIE_GAP',
          'strictfrac_TOP64', 'strictfrac_BOT64', 'strict_FULL96', 'tie_FULL96',
          'STRICT_GAP_ng', 'TIE_GAP_ng',
          'qnorm', 'qPR', 'q_top_share', 'q_absmax_share', 'q_v_align',
          'gold_norm', 'gold_norm_rel', 'float_margin', 'ham_margin',
          'ham_neartie', 'ham_exacttie', 'gold_d', 'N']

def dist(vals):
    v = np.asarray(vals, float)
    qs = np.percentile(v, [5, 25, 50, 75, 95])
    return dict(mean=float(v.mean()), sd=float(v.std()), p5=float(qs[0]), p25=float(qs[1]),
                med=float(qs[2]), p75=float(qs[3]), p95=float(qs[4]))

summary = {}
for s in sorted(secmap) + ['ALL']:
    rs = allr if s == 'ALL' else secmap[s]
    summary[s] = {'n': len(rs), 'delta_pp': float(np.mean([r['delta'] for r in rs]) * 100)}
    for f in FIELDS:
        summary[s][f] = dist([r[f] for r in rs])
json.dump(summary, open(OUT / 'evidence' / 'levels_summary.json', 'w'), indent=2)

print('\n=== LEVELS by section (mean [p25/med/p75]) ===')
hdr = f'{"section":22s}{"dPP":>9s}'
for f in ['strict_TOP64', 'strict_BOT64', 'STRICT_GAP', 'tie_TOP64', 'tie_BOT64', 'TIE_GAP']:
    hdr += f'{f:>16s}'
print(hdr)
for s in sorted(secmap):
    line = f'{s:22s}{summary[s]["delta_pp"]:>9.3f}'
    for f in ['strict_TOP64', 'strict_BOT64', 'STRICT_GAP', 'tie_TOP64', 'tie_BOT64', 'TIE_GAP']:
        line += f'{summary[s][f]["mean"]:>16.4f}'
    print(line)
print('\n  medians:')
for s in sorted(secmap):
    line = f'{s:22s}{"":>9s}'
    for f in ['strict_TOP64', 'strict_BOT64', 'STRICT_GAP', 'tie_TOP64', 'tie_BOT64', 'TIE_GAP']:
        line += f'{summary[s][f]["med"]:>16.4f}'
    print(line)

print('\n=== GEOMETRY by section (mean [p5..p95]) ===')
for f in ['qnorm', 'qPR', 'q_top_share', 'q_absmax_share', 'q_v_align', 'gold_norm_rel',
          'float_margin', 'ham_margin', 'ham_neartie', 'ham_exacttie', 'gold_d']:
    print(f'\n{f}:')
    for s in sorted(secmap):
        d = summary[s][f]
        print(f'   {s:22s} mean {d["mean"]:>9.4f} sd {d["sd"]:>8.4f}  p5 {d["p5"]:>8.3f} p25 {d["p25"]:>8.3f} med {d["med"]:>8.3f} p75 {d["p75"]:>8.3f} p95 {d["p95"]:>8.3f}')

# ---------------- within-archive paired profile vs events --------------------
print('\n=== WITHIN-ARCHIVE paired profile vs events (same C, same N) ===')
pairs = []
for char in A:
    pr = [r for r in allr if r['char'] == char and r['section'] == 'profile']
    ev = [r for r in allr if r['char'] == char and r['section'] == 'events']
    if not pr or not ev:
        continue
    pairs.append({'char': char, 'n_pro': len(pr), 'n_evt': len(ev),
                  **{f'{f}_pro': float(np.mean([r[f] for r in pr])) for f in FIELDS},
                  **{f'{f}_evt': float(np.mean([r[f] for r in ev])) for f in FIELDS},
                  'delta_pro': float(np.mean([r['delta'] for r in pr])),
                  'delta_evt': float(np.mean([r['delta'] for r in ev]))})
print('paired archives:', len(pairs))
print(f'  profile Delta>0 in {sum(p["delta_pro"]>0 for p in pairs)}/{len(pairs)};'
      f' events Delta<0 in {sum(p["delta_evt"]<0 for p in pairs)}/{len(pairs)}')
for f in ['qPR', 'qnorm', 'q_top_share', 'q_v_align', 'float_margin', 'ham_margin',
          'strict_TOP64', 'strict_BOT64', 'STRICT_GAP', 'gold_norm_rel']:
    npro = sum(p[f'{f}_pro'] > p[f'{f}_evt'] for p in pairs)
    print(f'  {f:16s} profile>events in {npro:2d}/{len(pairs)} archives   '
          f'mean pro {np.mean([p[f"{f}_pro"] for p in pairs]):>9.4f}  evt {np.mean([p[f"{f}_evt"] for p in pairs]):>9.4f}')
json.dump(pairs, open(OUT / 'evidence' / 'paired_archives.json', 'w'), indent=2)
print('\nsaved evidence')
