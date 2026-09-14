#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
Recover gates + levels table; compute the GOLD-FREE float-weight effective-dimension
statistic EFFW on PerLTQA (basis for the frozen rule).

EFFW(q)  = (sum_j w_j)^2 / sum_j w_j^2  with w_j = q_j^2 * v_j   (v_j = mean_i C_ij^2)
           = effective number of axes that actually drive the FLOAT cosine score.
EFFC     = (sum_j v_j)^2 / sum_j v_j^2  = archive's own effective coordinate count (EFF_COORD).
RHOEFF   = EFFW / EFFC   (dimensionless; how much of the archive's usable axis budget
           the float score actually uses).  SIGN uses all 96 axes with equal weight.
"""
import json, pickle
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
arch = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
QD = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
rows = pickle.load(open(OUT / 'evidence' / 'perltqa_levels_rows.pkl', 'rb'))

def spearman(x, y):
    rx = rankdata(x) - np.mean(rankdata(x)); ry = rankdata(y) - np.mean(rankdata(y))
    return float((rx @ ry) / np.sqrt((rx @ rx) * (ry @ ry)))

allr = list(rows.values())
D = np.array([r['delta'] for r in allr])
print('=== GATE 2: R2 audit Spearman targets (independent of my control gate) ===')
print(f'  rho(Delta,STRICT_GAP) = {spearman(D, [r["STRICT_GAP"] for r in allr]):.15f}  target 0.25416826537535475')
print(f'  rho(Delta,TIE_GAP)    = {spearman(D, [r["TIE_GAP"] for r in allr]):.15f}  target 0.27978783415712220')
secmap = defaultdict(list)
for r in allr: secmap[r['section']].append(r)
tgt = {'dialogues': (0.13054126734088975, 0.11123087254360414),
       'events': (0.39790634780463613, 0.38922832069574037),
       'profile': (0.0573253028779693, 0.018738683422868593),
       'social_relationship': (0.30428515802019, 0.2993013213223269)}
for s in sorted(secmap):
    rs = secmap[s]; d = [r['delta'] for r in rs]
    print(f'  {s:20s} strict {spearman(d, [r["STRICT_GAP"] for r in rs]):.12f} (tgt {tgt[s][0]:.12f})'
          f'   tie {spearman(d, [r["TIE_GAP"] for r in rs]):.12f} (tgt {tgt[s][1]:.12f})')

print('\n=== LEVELS: per-gold competition, means ===')
F = ['strict_TOP64','strict_BOT64','STRICT_GAP','tie_TOP64','tie_BOT64','TIE_GAP','STRICT_GAP_ng','gold_n','N']
print(f'{"section":22s}{"n":>6s}{"dPP":>9s}' + ''.join(f'{f:>15s}' for f in F))
for s in sorted(secmap):
    rs = secmap[s]
    print(f'{s:22s}{len(rs):>6d}{np.mean([r["delta"] for r in rs])*100:>9.3f}'
          + ''.join(f'{np.mean([r[f] for r in rs]):>15.4f}' for f in F))
print('\n=== LEVELS: STRICT_GAP distribution + sign fractions ===')
for s in sorted(secmap):
    g = np.array([r['STRICT_GAP'] for r in secmap[s]])
    t = np.array([r['TIE_GAP'] for r in secmap[s]])
    qs = np.percentile(g, [5,25,50,75,95])
    print(f'  {s:22s} STRICT_GAP mean {g.mean():>9.3f} med {qs[2]:>8.2f} p5 {qs[0]:>9.2f} p25 {qs[1]:>8.2f} p75 {qs[3]:>8.2f} p95 {qs[4]:>8.2f}'
          f'  frac>0 {np.mean(g>0):.4f} frac<0 {np.mean(g<0):.4f} frac=0 {np.mean(g==0):.4f}')
    print(f'  {"":22s} TIE_GAP    mean {t.mean():>9.3f} med {np.median(t):>8.2f}  frac>0 {np.mean(t>0):.4f}')

# ---------- GOLD-FREE statistic ----------
V = {}
for char, a in arch.items():
    C = np.asarray(a['C'], float)
    v = (C ** 2).mean(axis=0)
    V[char] = dict(v=v, effc=float(v.sum() ** 2 / (v ** 2).sum()))
for qid, q in QD.items():
    v = V[q['char']]['v']
    qc = np.asarray(q['qC'], float)
    w = (qc ** 2) * v
    rows[qid]['EFFW'] = float(w.sum() ** 2 / (w ** 2).sum())
    rows[qid]['EFFC'] = V[q['char']]['effc']
    rows[qid]['RHOEFF'] = rows[qid]['EFFW'] / rows[qid]['EFFC']
pickle.dump(rows, open(OUT / 'evidence' / 'perltqa_levels_rows.pkl', 'wb'))

print('\n=== GOLD-FREE float-weight effective dimension ===')
print(f'{"section":22s}{"dPP":>9s}{"EFFW":>10s}{"med":>9s}{"p25":>9s}{"p75":>9s}{"EFFC":>9s}{"RHOEFF":>10s}{"medRHO":>9s}')
for s in sorted(secmap):
    rs = secmap[s]
    e = np.array([r['EFFW'] for r in rs]); rh = np.array([r['RHOEFF'] for r in rs])
    print(f'{s:22s}{np.mean([r["delta"] for r in rs])*100:>9.3f}{e.mean():>10.4f}{np.median(e):>9.4f}'
          f'{np.percentile(e,25):>9.4f}{np.percentile(e,75):>9.4f}{np.mean([r["EFFC"] for r in rs]):>9.4f}'
          f'{rh.mean():>10.5f}{np.median(rh):>9.5f}')
print('\n  within-benchmark per-query rho(Delta, EFFW)  =', f'{spearman(D, [r["EFFW"] for r in allr]):.6f}')
print('  within-benchmark per-query rho(Delta, RHOEFF)=', f'{spearman(D, [r["RHOEFF"] for r in allr]):.6f}')
for s in sorted(secmap):
    rs = secmap[s]
    print(f'    {s:22s} rho(Delta,EFFW) {spearman([r["delta"] for r in rs], [r["EFFW"] for r in rs]):>9.5f}'
          f'   rho(Delta,RHOEFF) {spearman([r["delta"] for r in rs], [r["RHOEFF"] for r in rs]):>9.5f}'
          f'   rho(Delta,qPR) {spearman([r["delta"] for r in rs], [r["qPR"] for r in rs]):>9.5f}')

print('\n  paired within-archive profile vs events (same C, same v, same EFFC):')
np_ = 0
for char in V:
    pr = [r for r in allr if r['char'] == char and r['section'] == 'profile']
    ev = [r for r in allr if r['char'] == char and r['section'] == 'events']
    if pr and ev and np.mean([r['EFFW'] for r in pr]) < np.mean([r['EFFW'] for r in ev]): np_ += 1
print(f'    EFFW(profile) < EFFW(events) in {np_}/30 archives')

# decile monotonicity of Delta in EFFW (the frozen-rule shape)
e = np.array([r['EFFW'] for r in allr])
print('\n  PerLTQA EFFW deciles -> mean Delta_pp:')
edges = np.percentile(e, np.arange(0, 101, 10))
for i in range(10):
    m = (e >= edges[i]) & (e <= edges[i + 1] if i == 9 else e < edges[i + 1])
    print(f'    d{i+1}: EFFW<={edges[i+1]:7.3f}  n={m.sum():5d}  Delta {D[m].mean()*100:>8.3f} pp')
json.dump({'ok': True}, open(OUT / 'evidence' / 'step3b_done.json', 'w'))
