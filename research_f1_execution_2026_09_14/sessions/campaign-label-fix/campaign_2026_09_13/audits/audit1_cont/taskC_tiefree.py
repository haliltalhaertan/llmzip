import pickle, json
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/c/Users/MDP/dev/llmzip-work')
# LME NATIVE tie-share + tie-free exactness
data=json.load(open(ROOT/'drive/longmemeval_s_cleaned.json'))
allq=sorted(str(x['question_id']) for x in data); lex={q:i for i,q in enumerate(allq)}; del data
pkls=sorted((ROOT/'regen/lme/cache_repr').glob('*.pkl'))
n_tie=0; worst_free=0.0
d=json.load(open('/tmp/audit1/taskC_LME_perq.json'))
for i,p in enumerate(pkls):
    o=pickle.loads(p.read_bytes()); C=o['C']; qC=o['qC']; g=np.asarray(o['gold']).ravel()
    D0=C>=0; Q0=qC>=0
    dvec=np.count_nonzero(D0!=Q0[None,:],axis=1)
    tie=any(int(np.count_nonzero(dvec==dvec[int(gg)]))-1>0 for gg in g)
    n_tie+=tie
    if not tie:
        diff=abs(d['per_arm']['NATIVE96']['exp'][i]-d['per_arm']['NATIVE96']['fr_off'][i])
        worst_free=max(worst_free,diff)
print('LME NATIVE: tied questions',n_tie,'/470 share',n_tie/470,'; tie-free max|exp-mc| =',repr(worst_free))
