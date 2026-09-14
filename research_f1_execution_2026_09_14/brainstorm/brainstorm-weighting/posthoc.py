"""POST-HOC (not frozen; exploratory refinement): normalized spectral quantity."""
import pickle, glob
import numpy as np
from collections import defaultdict
EPS = 1e-12

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if np.std(x) < 1e-15 or np.std(y) < 1e-15:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])

archives = []
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    archives.append(('LME', None, d['C'], d['qC'][None, :], [list(d['gold'])]))
arch = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
qq = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
bychar = defaultdict(list)
for qid, v in qq.items():
    bychar[v['char']].append(v)
for ch, items in bychar.items():
    C = arch[ch]['C']
    archives.append(('PerLTQA', None, C, np.stack([v['qC'] for v in items]),
                    [list(v['gold']) for v in items],
                    [v['section'] for v in items]))
# normalize to (bench, C, Q, golds, secs)
archives2 = []
for a in archives:
    if a[1] is None and len(a) == 5:  # LME entries: (bench, None, C, Q, golds)
        archives2.append((a[0], a[2], a[3], a[4], [None]*len(a[4])))
    else:  # PerLTQA entries: (bench, None, C, Q, golds, secs)
        archives2.append((a[0], a[2], a[3], a[4], a[5]))

for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    d = pickle.load(open(f, 'rb'))
    archives2.append(('REALTALK', d['C'], d['QC'], [list(g) for g in d['gold_rows']],
                      [None]*len(d['gold_rows'])))
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
    d = pickle.load(open(f, 'rb'))
    m = d['id_to_row']
    golds = [[m[e] for e in qa['raw_evidence'] if e in m] for qa in d['qas']]
    archives2.append(('LoCoMo', d['C'], d['QC'], golds, [None]*len(golds)))

rows = []
for entry in archives2:
    bench, C, Q, golds, secs = entry
    v = (C ** 2).mean(0); lv = np.log(v + EPS)
    G = np.stack([C[g].mean(0) if len(g) else np.zeros(96) for g in golds])
    for i in range(Q.shape[0]):
        if len(golds[i]) == 0:
            continue
        s = Q[i] * G[i]
        u = s / (v + EPS)  # whitened support: per-axis contribution after full whitening
        align = float(Q[i] @ G[i]) / (np.linalg.norm(Q[i]) * np.linalg.norm(G[i]) + 1e-12)
        rows.append(dict(bench=bench, sec=secs[i], qw=pearson(lv, u),
                         rraw=pearson(lv, s), align=align))

def summ(vals):
    x = np.array([t for t in vals if np.isfinite(t)])
    return float(x.mean()), 1.96*float(x.std(ddof=1))/np.sqrt(len(x)), len(x)

for b, s in [('LME',None),('LoCoMo',None),('REALTALK',None),('PerLTQA',None),
             ('PerLTQA','profile'),('PerLTQA','social_relationship'),
             ('PerLTQA','dialogues'),('PerLTQA','events')]:
    sub = [r for r in rows if r['bench']==b and (s is None or r['sec']==s)]
    mw, cw, n = summ([r['qw'] for r in sub])
    mr, cr, _ = summ([r['rraw'] for r in sub])
    ma, ca, _ = summ([r['align'] for r in sub])
    print(f'{b:8s} {str(s):18s} Q-WHITE={mw:+.4f}+/-{cw:.4f} Rraw={mr:+.4f}+/-{cr:.4f} align={ma:+.4f}+/-{ca:.4f} n={n}')
# confound check: across benchmarks, does mean alignment strength track Rraw?
print('confound check done: compare align column vs Rraw column')
