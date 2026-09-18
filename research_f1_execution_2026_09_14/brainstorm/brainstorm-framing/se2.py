"""Paired SEs K=3 for REALTALK + LoCoMo. READ-ONLY on caches."""
import pickle, glob, numpy as np, sys
sys.path.insert(0,'/home/mdp/muse-work/brainstorm-framing')
from se import per_query, summarize
R=[]
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    d=pickle.load(open(f,'rb'))
    for i in range(len(d['qids'])):
        g=list(d['gold_rows'][i])
        if g: R.append(per_query(d['C'],d['QC'][i],g))
summarize('REALTALK',R)
M=[]
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
    d=pickle.load(open(f,'rb')); m=d['id_to_row']
    for i,qa in enumerate(d['qas']):
        g=[m[e] for e in qa['raw_evidence'] if e in m]
        if g: M.append(per_query(d['C'],d['QC'][i],g))
summarize('LoCoMo',M)
