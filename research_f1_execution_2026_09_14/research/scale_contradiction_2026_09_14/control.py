#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 1 control: reproduce frozen headlines with EXACT tie expectation + report N ranges.
READ-ONLY on all caches.
"""
import json, pickle, glob, os
import numpy as np

OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/scale-contradiction/evidence'
W = '/mnt/c/Users/MDP/dev/llmzip-work'
os.makedirs(OUT, exist_ok=True)
K = 3

def fr_exact(scores_better_is_lower, gold, K=3):
    """scores: lower = better. Exact expectation of FR@K under uniform random tie-break."""
    s = np.asarray(scores_better_is_lower, float)
    srt = np.sort(s)
    thr = srt[K-1]
    strictly = int(np.sum(s < thr))
    slots = K - strictly
    bc = int(np.sum(s == thr))
    g = np.asarray(gold).ravel().astype(int)
    gs = s[g]
    g_strict = int(np.sum(gs < thr))
    g_tied = int(np.sum(gs == thr))
    fr = (g_strict + g_tied * slots / bc) / len(g)
    gap = float(srt[K] - srt[K-1]) if len(srt) > K else float('nan')
    return fr, int(bc > slots), bc, slots, strictly, gap

def hamming(D0, Q0):
    return np.count_nonzero(D0 != Q0[None, :], axis=1)

def cosneg(C, q):
    dn = np.linalg.norm(C, axis=1); qn = np.linalg.norm(q)
    return -((C @ q) / (dn * qn))

res = {}

# ---------------- LME ----------------
files = sorted(glob.glob(f'{W}/regen/lme/cache_repr/*.pkl'))
lme_sign, lme_flt, lme_N = [], [], []
cmax = 0.0
for f in files:
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); qC = np.asarray(d['qC'], float); g = np.asarray(d['gold']).ravel()
    cmax = max(cmax, float(np.abs(C.mean(axis=0)).max()))
    lme_N.append(C.shape[0])
    D0 = C >= 0; Q0 = qC >= 0
    dh = hamming(D0, Q0).astype(float)
    lme_sign.append(fr_exact(dh, g, K)[0])
    lme_flt.append(fr_exact(cosneg(C, qC), g, K)[0])
res['LME'] = {'n_q': len(files), 'sign_FR3': float(np.mean(lme_sign)), 'float_FR3': float(np.mean(lme_flt)),
              'delta_pp': float((np.mean(lme_sign)-np.mean(lme_flt))*100),
              'N_min': int(min(lme_N)), 'N_max': int(max(lme_N)), 'N_mean': float(np.mean(lme_N)),
              'N_median': float(np.median(lme_N)), 'col_mean_absmax': cmax}
print('LME', json.dumps(res['LME']), flush=True)

# ---------------- PerLTQA ----------------
arch = pickle.load(open(f'{W}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
QD = pickle.load(open(f'{W}/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
Ns = {c: int(a['N']) for c, a in arch.items()}
pre = {}
cmax = 0.0
for c, a in arch.items():
    C = np.asarray(a['C'], float)
    cmax = max(cmax, float(np.abs(C.mean(axis=0)).max()))
    pre[c] = (C, C >= 0, np.linalg.norm(C, axis=1))
ps, pf = [], []
for qid, q in QD.items():
    C, D0, dn = pre[q['char']]
    qC = np.asarray(q['qC'], float); g = np.asarray(q['gold']).ravel()
    ps.append(fr_exact(hamming(D0, qC >= 0).astype(float), g, K)[0])
    pf.append(fr_exact(-((C @ qC)/(dn*np.linalg.norm(qC))), g, K)[0])
res['PERLTQA'] = {'n_q': len(QD), 'n_arch': len(arch), 'sign_FR3': float(np.mean(ps)), 'float_FR3': float(np.mean(pf)),
                  'delta_pp': float((np.mean(ps)-np.mean(pf))*100),
                  'N_min': min(Ns.values()), 'N_max': max(Ns.values()),
                  'N_mean': float(np.mean(list(Ns.values()))), 'N_all': sorted(Ns.values()),
                  'col_mean_absmax': cmax}
print('PERLTQA', json.dumps({k: v for k, v in res['PERLTQA'].items() if k != 'N_all'}), flush=True)

# ---------------- LoCoMo ----------------
lo = []
for i in range(10):
    d = pickle.load(open(f'{W}/regen/locomo/locomo_{i}.pkl', 'rb'))
    lo.append(d)
print('LOCOMO keys', list(lo[0].keys()), flush=True)
lN = [np.asarray(d['C']).shape[0] for d in lo]
res['LOCOMO'] = {'n_conv': 10, 'N_min': int(min(lN)), 'N_max': int(max(lN)), 'N_all': [int(x) for x in lN],
                 'n_qas': [len(d['qas']) for d in lo], 'QC_shape': list(np.asarray(lo[0]['QC']).shape)}
print('LOCOMO', json.dumps(res['LOCOMO']), flush=True)

# ---------------- REALTALK ----------------
rts = sorted(glob.glob(f'{W}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
rN = []
rs, rf_ = [], []
for f in rts:
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float); gr = d['gold_rows']
    rN.append(C.shape[0])
    D0 = C >= 0; dn = np.linalg.norm(C, axis=1)
    for j in range(QC.shape[0]):
        g = np.asarray(gr[j]).ravel()
        if len(g) == 0: continue
        qC = QC[j]
        rs.append(fr_exact(hamming(D0, qC >= 0).astype(float), g, K)[0])
        rf_.append(fr_exact(-((C @ qC)/(dn*np.linalg.norm(qC))), g, K)[0])
res['REALTALK'] = {'n_q': len(rs), 'sign_FR3': float(np.mean(rs)), 'float_FR3': float(np.mean(rf_)),
                   'delta_pp': float((np.mean(rs)-np.mean(rf_))*100),
                   'N_min': int(min(rN)), 'N_max': int(max(rN)), 'N_all': [int(x) for x in rN]}
print('REALTALK', json.dumps(res['REALTALK']), flush=True)

json.dump(res, open(f'{OUT}/control.json', 'w'), indent=1)
print('WROTE control.json', flush=True)
