import pickle, glob, numpy as np
B = '/mnt/c/Users/MDP/dev/llmzip-work'

f = sorted(glob.glob(B+'/regen/lme/cache_repr/*.pkl'))[0]
d = pickle.load(open(f,'rb'))
print('LME keys', list(d.keys()))
print('  C', np.asarray(d['C']).shape, np.asarray(d['C']).dtype, 'qC', np.asarray(d['qC']).shape, 'gold', d['gold'])

d = pickle.load(open(B+'/bench3/runs/b3a_realtalk/rt_repr/RT01.pkl','rb'))
print('RT keys', list(d.keys()))
print('  C', np.asarray(d['C']).shape, 'QC', np.asarray(d['QC']).shape, 'gold_rows', type(d['gold_rows']), d['gold_rows'][:2], 'qids', len(d['qids']))

ca = pickle.load(open(B+'/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
k = list(ca.keys())[0]
print('PLT arch keys', list(ca[k].keys()), 'nchar', len(ca))
print('  C', np.asarray(ca[k]['C']).shape)
cq = pickle.load(open(B+'/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
qk = list(cq.keys())[0]
print('PLT q keys', list(cq[qk].keys()), 'nq', len(cq))
print('  sample', {kk:(np.asarray(v).shape if kk=='qC' else v) for kk,v in cq[qk].items()})
import collections
print('  sections', collections.Counter(v['section'] for v in cq.values()))

d = pickle.load(open(B+'/regen/locomo/locomo_0.pkl','rb'))
print('LOC keys', list(d.keys()))
print('  C', np.asarray(d['C']).shape, 'QC', np.asarray(d['QC']).shape, 'nqas', len(d['qas']))
print('  qas0', {kk:v for kk,v in d['qas'][0].items() if kk!='question'})
print('  id_to_row sample', list(d['id_to_row'].items())[:3])
