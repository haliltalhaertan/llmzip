"""STEP 4: adversarial mutations against THEIR code (workspace copy).

Baseline + 5 mutations, full LME (470q) + PerLTQA (8265q) data, m=48.
Uses their fr_at_k_exact / hamming_batch / cos_batch unless the mutation
replaces that piece. Ranking replicates run_sweep.py logic.
"""
import sys, numpy as np
sys.path.insert(0, '/home/mdp/muse-work/audit-axis')
import their_core_copy as T

M = 48
lme_units = T.load_lme()
plt_units = T.load_perltqa()
print("units:", len(lme_units), len(plt_units),
      "nq:", sum(q.shape[0] for _, q, _, _ in lme_units),
      sum(q.shape[0] for _, q, _, _ in plt_units), flush=True)

def naive_firstK(S, Gmask, gold_size, K=3):
    # higher better; ties -> lowest index wins (arbitrary, order-dependent)
    N, nq = S.shape
    kk = min(K, N)
    o = np.argsort(-S, axis=0, kind='stable')
    top = np.zeros_like(Gmask)
    for j in range(nq):
        top[o[:kk, j], j] = True
    return (Gmask & top).sum(0) / gold_size

def cos_noguard(Cm, Qm):
    nC = np.linalg.norm(Cm, axis=1); nQ = np.linalg.norm(Qm, axis=1)
    return (Cm @ Qm.T) / (nC[:, None] * nQ[None, :])

def scores(C, Q, idx, quant, guard=True):
    Cm = C[:, idx]; Qm = Q[:, idx]
    if quant == 'sign':
        return -T.hamming_batch((Cm >= 0).astype(np.uint8), (Qm >= 0).astype(np.uint8))
    return T.cos_batch(Cm, Qm) if guard else cos_noguard(Cm, Qm)

def run(mut):
    out = {}
    for name, units in (('LME', lme_units), ('PLTQA', plt_units)):
        if mut == 'pooled':
            pall = np.concatenate([C for C, _, _, _ in units], axis=0)
            gorder = np.argsort(-(pall ** 2).mean(axis=0), kind='stable')
        st = ft = 0.0; n = 0; zr = 0
        for (C, Q, golds, labels) in units:
            N = C.shape[0]; nq = Q.shape[0]
            gold_size = np.array([len(g) for g in golds], float)
            Gmask = np.zeros((N, nq), bool)
            for j, g in enumerate(golds):
                Gmask[g, j] = True
            order = np.argsort(-(C ** 2).mean(axis=0), kind='stable')
            if mut == 'swap':
                top, bot = order[-M:], order[:M]
            elif mut == 'ascending':
                asc = np.argsort((C ** 2).mean(axis=0), kind='stable')
                top, bot = asc[:M], asc[-M:]
            elif mut == 'pooled':
                top, bot = gorder[:M], gorder[-M:]
            else:
                top, bot = order[:M], order[-M:]
            guard = (mut != 'noguard')
            fr = naive_firstK if mut == 'naive' else T.fr_at_k_exact
            S = scores(C, Q, top, 'sign', guard)
            F = scores(C, Q, top, 'float', guard)
            B = scores(C, Q, bot, 'sign', guard)
            st += fr(S, Gmask, gold_size).sum()
            ft += fr(F, Gmask, gold_size).sum()
            n += nq
            if mut == 'noguard':
                zr += int(np.isnan(F).sum())
        out[name] = ((st - ft) / n * 100, zr)
    return out

base = run('baseline')
print(f"BASELINE LME delta={base['LME'][0]:+.6f}  PLTQA delta={base['PLTQA'][0]:+.6f}", flush=True)
for mut in ['swap', 'ascending', 'naive', 'pooled', 'noguard']:
    r = run(mut)
    for name in ('LME', 'PLTQA'):
        d = r[name][0] - base[name][0]
        extra = f"  NaNcells={r[name][1]}" if mut == 'noguard' else ""
        print(f"MUT {mut:>9} {name}: delta={r[name][0]:+.6f}  shift_vs_base={d:+.6f}{extra}",
              flush=True)
print("DONE")
