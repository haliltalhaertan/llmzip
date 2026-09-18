import pickle, glob, os
# Peek at structures only
f = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))[0]
d = pickle.load(open(f,'rb'))
print('LME keys:', d.keys())
print('C', d['C'].shape, d['C'].dtype, 'qC', d['qC'].shape, 'gold', d['gold'][:5], 'qid', d.get('question_id'))
print('colmean absmax', abs(d['C'].mean(axis=0)).max())
import numpy as np
print('qC[:5]', d['qC'][:5])
print('C[0,:5]', d['C'][0,:5])
print()
d2 = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
k = list(d2.keys())[0]
print('PerLTQA q keys:', d2[k].keys(), 'sample:', {kk: (v if not isinstance(v,np.ndarray) else v.shape) for kk,v in d2[k].items()})
a = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
ck = list(a.keys())[0]
print('PerLTQA arch keys:', a[ck].keys(), {kk: (v.shape if isinstance(v,np.ndarray) else type(v)) for kk,v in a[ck].items()})
print()
r = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
d3 = pickle.load(open(r[0],'rb'))
print('RT keys:', d3.keys())
for kk,v in d3.items():
    print('  ', kk, v.shape if isinstance(v,np.ndarray) else (len(v) if isinstance(v,list) else type(v)))
print()
l = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl'))
d4 = pickle.load(open(l[0],'rb'))
print('LoCoMo keys:', d4.keys())
for kk,v in d4.items():
    if isinstance(v,np.ndarray): print('  ',kk,v.shape,v.dtype)
    elif isinstance(v,list): print('  ',kk,'list len',len(v), v[0].keys() if v and isinstance(v[0],dict) else '')
    elif isinstance(v,dict): print('  ',kk,'dict len',len(v), list(v)[:3])
    else: print('  ',kk,type(v))
