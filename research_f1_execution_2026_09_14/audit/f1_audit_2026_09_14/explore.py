import os, pickle, glob, json
import numpy as np
B='/mnt/c/Users/MDP/dev/llmzip-work'
print("== LME cache_repr ==")
fs=sorted(glob.glob(B+'/regen/lme/cache_repr/*.pkl'))
print("n files", len(fs))
d=pickle.load(open(fs[0],'rb'))
print("keys", list(d.keys()) if isinstance(d,dict) else type(d))
for k,v in d.items():
    print("  ",k, type(v), getattr(v,'shape',None), (v if not hasattr(v,'shape') and not isinstance(v,(list,)) else (v[:5] if isinstance(v,list) else '')))
print("== RT ==")
rts=sorted(glob.glob(B+'/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
print("n",len(rts), [os.path.basename(x) for x in rts])
r=pickle.load(open(rts[0],'rb'))
print("keys", list(r.keys()))
for k,v in r.items():
    print("  ",k,type(v),getattr(v,'shape',None))
print("qids0",r['qids'][:3]); print("gold0",r['gold_rows'][:3]); print("chat_no",r['chat_no'])
print("== PerLTQA ==")
arch=pickle.load(open(B+'/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
print("n arch", len(arch)); k0=list(arch)[0]; print("arch keys", list(arch[k0].keys()), arch[k0]['C'].shape if hasattr(arch[k0]['C'],'shape') else None, arch[k0]['N'])
qd=pickle.load(open(B+'/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
print("n q", len(qd)); q0=list(qd)[0]; print("q keys", list(qd[q0].keys()), qd[q0])
print("== search for frozen per-query result surfaces ==")
for pat in ['/bench3/runs/**/*.json','/regen/**/*.json','/bench3/**/*.json.gz','/regen/**/*.json.gz']:
    for f in glob.glob(B+pat, recursive=True):
        sz=os.path.getsize(f)
        if sz>200000: print("  BIG", f, sz)
