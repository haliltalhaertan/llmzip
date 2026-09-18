import pickle, glob, os, numpy as np
B='/mnt/c/Users/MDP/dev/llmzip-work/'
f=sorted(glob.glob(B+'regen/lme/cache_repr/*.pkl'))[0]
d=pickle.load(open(f,'rb'))
print('LME keys',list(d.keys()))
for k,v in d.items():
    print(' ',k,type(v), getattr(v,'shape',None) if hasattr(v,'shape') else (v if not isinstance(v,(list,dict)) else str(v)[:120]))
print()
f=sorted(glob.glob(B+'bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))
print('RT files',len(f))
d=pickle.load(open(f[0],'rb'))
print('RT keys',list(d.keys()))
for k,v in d.items():
    print(' ',k,type(v), getattr(v,'shape',None), str(v)[:150] if not hasattr(v,'shape') else '')
print()
a=pickle.load(open(B+'bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
print('PER arch',len(a),list(a.keys())[:3])
k0=list(a.keys())[0]
print(' arch entry keys',list(a[k0].keys()))
for k,v in a[k0].items(): print('   ',k,type(v),getattr(v,'shape',None),str(v)[:80] if not hasattr(v,'shape') else '')
q=pickle.load(open(B+'bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
print('PER q',len(q))
k0=list(q.keys())[0]
print(' q entry',{k:(str(type(v)),getattr(v,'shape',None),str(v)[:60]) for k,v in q[k0].items()})
print()
f=sorted(glob.glob(B+'regen/locomo/locomo_*.pkl'))
print('LOCO files',len(f),[os.path.basename(x) for x in f])
d=pickle.load(open(f[0],'rb'))
print('LOCO keys',list(d.keys()))
for k,v in d.items():
    if k=='qas': print('  qas',len(v),v[0])
    elif k=='id_to_row': print('  id_to_row',len(v),list(v.items())[:3])
    else: print(' ',k,type(v),getattr(v,'shape',None),str(v)[:80] if not hasattr(v,'shape') else '')
