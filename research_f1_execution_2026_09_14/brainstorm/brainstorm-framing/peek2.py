import pickle, glob
l = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl'))
d4 = pickle.load(open(l[0],'rb'))
q = d4['qas'][0]
print({k: (v if not isinstance(v,str) or len(v)<200 else v[:200]) for k,v in q.items()})
print('id_to_row sample:', list(d4['id_to_row'].items())[:3])
r = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
d3 = pickle.load(open(r[0],'rb'))
print('gold_rows[0]:', d3['gold_rows'][0], 'qids[0]:', d3['qids'][0])
print('gold_rows types:', set(type(g).__name__ for g in d3['gold_rows']))
import numpy as np
print('QC shape', d3['QC'].shape, 'C shape', d3['C'].shape)
