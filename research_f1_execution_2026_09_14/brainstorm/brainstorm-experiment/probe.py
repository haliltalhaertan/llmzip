# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# probe.py — inspect one file per cache + control metric check
import pickle, glob, numpy as np, os

def fr3_exact(C, qC, gold, K=3):
    C = np.asarray(C, float); qC = np.asarray(qC, float)
    gold = list(gold)
    # float arm: cosine on raw C
    cn = np.linalg.norm(C, axis=1); qn = np.linalg.norm(qC)
    cos = (C @ qC) / (cn * qn + 1e-30)
    # sign arm: hamming between (C>=0),(qC>=0)
    Sb = (C >= 0).astype(np.int8); qb = (qC >= 0).astype(np.int8)
    ham = np.sum(Sb != qb, axis=1).astype(float)
    def E(scores, larger_better):
        order = np.argsort(-scores) if larger_better else np.argsort(scores)
        s = scores[order]
        thr = s[K-1] if len(s) >= K else s[-1]
        if larger_better:
            better = np.sum(scores > thr); tied = np.sum(scores == thr)
        else:
            better = np.sum(scores < thr); tied = np.sum(scores == thr)
        slots = K - better
        gset = set(gold)
        strict = sum(1 for i in gset if (scores[i] > thr if larger_better else scores[i] < thr))
        gtied = sum(1 for i in gset if scores[i] == thr)
        return (strict + gtied * slots / max(tied,1)) / max(len(gold),1)
    return E(cos, True), E(ham, False)

# LME sample
fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
print('LME n files:', len(fs))
d = pickle.load(open(fs[0],'rb'))
print('LME keys:', list(d.keys()))
for k,v in d.items():
    a = np.asarray(v) if not isinstance(v,str) else v
    print(' ', k, type(v), getattr(a,'shape',a if isinstance(v,str) else None))
C,qC,gold = np.asarray(d['C'],float), np.asarray(d['qC'],float), list(d['gold'])
print('LME colmean absmax:', float(np.abs(C.mean(0)).max()), 'N:',C.shape,'gold:',gold)
print('LME sample FR3:', fr3_exact(C,qC,gold))

# PerLTQA
pa = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
pq = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
print('PerLTQA chars:', len(pa), list(pa)[:3])
c0 = list(pa)[:1][0]; print('arch keys:', list(pa[c0].keys()), 'C shape:', np.asarray(pa[c0]['C']).shape)
q0 = list(pq)[:1][0]; print('q keys:', list(pq[q0].keys()), {k:pq[q0][k] for k in pq[q0] if k!='qC'})
print('n queries:', len(pq))

# REALTALK
rt = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT01.pkl','rb'))
print('RT keys:', list(rt.keys()))
for k,v in rt.items():
    print(' ', k, getattr(np.asarray(v),'shape',type(v)) if not isinstance(v,list) else f'list len {len(v)}')

# LoCoMo
lc = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_0.pkl','rb'))
print('LoCoMo keys:', list(lc.keys()))
for k,v in lc.items():
    print(' ', k, getattr(np.asarray(v),'shape',type(v)) if not isinstance(v,list) else f'list len {len(v)}')
print('id_to_row sample:', dict(list(lc['id_to_row'].items())[:3]))
print('qas[0]:', lc['qas'][0].keys(), {k:v for k,v in lc['qas'][0].items() if k!='raw_evidence'})
