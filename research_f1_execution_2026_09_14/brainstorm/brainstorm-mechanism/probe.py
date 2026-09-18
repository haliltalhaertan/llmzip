import pickle, glob
p = '/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/'
fs = sorted(glob.glob(p + '*.pkl'))
print('n_lme_files', len(fs))
d = pickle.load(open(fs[0], 'rb'))
print('keys', list(d.keys()))
for k, v in d.items():
    import numpy as np
    a = np.asarray(v) if not isinstance(v, (list, str)) else v
    print(k, type(v), getattr(a, 'shape', None), getattr(a, 'dtype', None))
d2 = pickle.load(open(fs[1], 'rb'))
print('q2', d2.get('question_id'), np.asarray(d2['C']).shape, np.asarray(d2['qC']).shape, d2.get('gold'))

pa = '/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl'
A = pickle.load(open(pa, 'rb'))
print('arch keys', list(A.keys())[:5], 'n_arch', len(A))
c0 = list(A.keys())[0]
print('arch0', list(A[c0].keys()))
import numpy as np
print('C shape', np.asarray(A[c0]['C']).shape)
pq = '/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl'
Q = pickle.load(open(pq, 'rb'))
print('n_q', len(Q))
q0 = list(Q.keys())[0]
print('q0', list(Q[q0].keys()), {k: Q[q0][k] for k in Q[q0] if k != 'qC'})
print('qC shape', np.asarray(Q[q0]['qC']).shape)
from collections import Counter
print('sections', Counter(v['section'] for v in Q.values()))
