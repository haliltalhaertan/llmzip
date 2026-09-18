import pickle, glob, os
import numpy as np
# LME
fs = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
print('LME n files', len(fs))
d = pickle.load(open(fs[0],'rb'))
print('LME keys', d.keys())
print('C shape', d['C'].shape, 'qC shape', d['qC'].shape, 'gold', d['gold'], 'qid', d.get('question_id'))
print('C colmean absmax', np.abs(d['C'].mean(0)).max())
# PerLTQA
d2 = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
ks = list(d2.keys())[:2]
for k in ks:
    print('Q', k, d2[k].keys(), {kk: (np.asarray(v).shape if isinstance(v,(list,np.ndarray)) else v) for kk,v in d2[k].items() if kk!='qC'})
    print(' section', d2[k].get('section'), 'char', d2[k].get('char'), 'gold len', len(d2[k].get('gold',[])))
print('nQ', len(d2))
d3 = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
print('nArch', len(d3))
k0 = list(d3.keys())[0]
print('arch', k0, d3[k0].keys(), d3[k0]['C'].shape)
# REALTALK
fs2 = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
print('RT files', fs2)
d4 = pickle.load(open(fs2[0],'rb'))
print('RT keys', d4.keys())
for k,v in d4.items():
    print(' ', k, type(v), np.asarray(v).shape if isinstance(v,(list,np.ndarray)) else (len(v) if isinstance(v,(list,dict)) else v))
# LoCoMo
fs3 = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl'))
print('locomo files', fs3)
d5 = pickle.load(open(fs3[0],'rb'))
print('locomo keys', d5.keys())
for k,v in d5.items():
    t=np.asarray(v) if isinstance(v,(list,np.ndarray)) else v
    print(' ',k,type(v), getattr(t,'shape', len(v) if isinstance(v,(list,dict)) else v))
print('qas0', d5['qas'][0].keys() if 'qas' in d5 else None)
print('id_to_row sample', list(d5['id_to_row'].items())[:3] if 'id_to_row' in d5 else None)
