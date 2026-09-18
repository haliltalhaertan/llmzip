#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 1 CONTROL: reproduce frozen PerLTQA headline FR@3 before trusting any new number.
Exact tie expectation (order-independent), per METRIC FACTS.
"""
import json, pickle, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
(OUT / 'evidence').mkdir(parents=True, exist_ok=True)
K = 3

arch = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
QD = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
print('archives', len(arch), 'queries', len(QD))
k0 = list(arch)[0]
print('arch keys', sorted(arch[k0].keys()))
q0 = list(QD)[0]
print('q keys', sorted(QD[q0].keys()), {k: (np.shape(v) if hasattr(v, "__len__") else v) for k, v in QD[q0].items() if k != 'qC'})
C0 = np.asarray(arch[k0]['C'], float)
print('C shape', C0.shape, 'colmean absmax', float(np.abs(C0.mean(0)).max()))
print('N sizes', sorted(int(a['N']) for a in arch.values())[:5], '...', sorted(int(a['N']) for a in arch.values())[-5:])

# ---- exact FR@K expectation -------------------------------------------------
def fr_exact(scores_better_is_larger, gold, K=3):
    """E[FR@K] under uniform random tie-break. scores: larger = better."""
    s = np.asarray(scores_better_is_larger, float)
    ss = np.sort(s)[::-1]
    thr = ss[K - 1]
    strictly = int(np.count_nonzero(s > thr))
    slots = K - strictly
    bc = int(np.count_nonzero(s == thr))
    g = np.asarray(gold).ravel().astype(int)
    sg = s[g]
    g_strict = int(np.count_nonzero(sg > thr))
    g_tied = int(np.count_nonzero(sg == thr))
    return (g_strict + g_tied * slots / bc) / len(g)

A = {}
for char, a in arch.items():
    C = np.asarray(a['C'], float)
    A[char] = dict(C=C, D0=(C >= 0), nrm=np.linalg.norm(C, axis=1))

rows = {}
for qid, q in QD.items():
    char = q['char']; a = A[char]; C = a['C']
    qC = np.asarray(q['qC'], float)
    g = np.asarray(q['gold']).ravel().astype(int)
    Q0 = qC >= 0
    d = np.count_nonzero(a['D0'] != Q0[None, :], axis=1)
    fr_s = fr_exact(-d.astype(float), g, K)          # smaller hamming = better
    cosv = (C @ qC) / (a['nrm'] * np.linalg.norm(qC))
    fr_f = fr_exact(cosv, g, K)
    rows[qid] = dict(char=char, section=q['section'], gold_n=int(len(g)),
                     sign=float(fr_s), float=float(fr_f), delta=float(fr_s - fr_f))

sec = defaultdict(list)
for r in rows.values():
    sec[r['section']].append(r)
allr = list(rows.values())
res = {'overall': {'n': len(allr),
                   'sign': float(np.mean([r['sign'] for r in allr])),
                   'float': float(np.mean([r['float'] for r in allr])),
                   'delta_pp': float(np.mean([r['delta'] for r in allr]) * 100)}}
for s, rs in sorted(sec.items()):
    res[s] = {'n': len(rs), 'sign': float(np.mean([r['sign'] for r in rs])),
              'float': float(np.mean([r['float'] for r in rs])),
              'delta_pp': float(np.mean([r['delta'] for r in rs]) * 100)}
print(json.dumps(res, indent=2))
print('FROZEN REF: sign 0.488941994930817 float 0.551692074528853 delta -6.275pp')
print('COORD REF sections: profile +20.355355 social -0.780016 events -12.393717 dialogues -1.501652')

json.dump({'control': res}, open(OUT / 'evidence' / 'control.json', 'w'), indent=2)
pickle.dump(rows, open(OUT / 'evidence' / 'perltqa_delta_rows.pkl', 'wb'))
print('saved')
