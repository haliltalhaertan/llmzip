import pickle, glob
import numpy as np
d = pickle.load(open(sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))[0],'rb'))
print('RT gold_rows type', type(d['gold_rows']))
g = d['gold_rows']
print('len', len(g))
print('first3', g[:3] if isinstance(g, list) else g)
print('QC shape', d['QC'].shape, 'C shape', d['C'].shape, 'N', d['N'])
print('qids', d['qids'][:3])
f2 = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl'))[0]
e = pickle.load(open(f2,'rb'))
print('LOCOMO file', f2)
print('C', e['C'].shape, 'QC', e['QC'].shape)
print('qas len', len(e['qas']))
print('qas0', e['qas'][0])
kr = list(e['id_to_row'].keys())[:5]
print('idmap sample', [(k, e['id_to_row'][k]) for k in kr], 'nmap', len(e['id_to_row']))
# PerLTQA gold semantics
arch = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
qq = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
import itertools
for i,(qid,v) in enumerate(itertools.islice(qq.items(),3)):
    C = arch[v['char']]['C']
    print(qid, v['char'], v['section'], 'gold', v['gold'], 'N', C.shape, 'maxgold', max(v['gold']))
print('sections', {v['section'] for v in list(qq.values())[:2000]})
from collections import Counter
print(Counter(v['section'] for v in qq.values()))
