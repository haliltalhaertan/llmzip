"""ATTACK script: control headlines + attacks 1,2,3. READ-ONLY on caches."""
import pickle, glob, json, numpy as np, time
t0=time.time()
OUT='/home/mdp/muse-work/brainstorm-framing/atk_results.json'

def fr_stats(scores, gold, K, higher_better):
    gold=np.asarray(gold,int); n=len(gold)
    if higher_better: thr=np.sort(scores)[::-1][K-1]; nb=(scores>thr).sum(); be=(scores==thr).sum()
    else: thr=np.sort(scores)[K-1]; nb=(scores<thr).sum(); be=(scores==thr).sum()
    g=np.asarray(scores)[gold]
    if higher_better: gs=(g>thr).sum(); gt=(g==thr).sum()
    else: gs=(g<thr).sum(); gt=(g==thr).sum()
    slots=K-nb
    exp=(gs+gt*slots/be)/n
    worst=(gs+max(0,slots-(be-gt)))/n
    best=(gs+min(gt,slots))/n
    tied = be>slots  # boundary tie present (bc exceeds slots)
    return exp,worst,best,tied

def load_all():
    L=[]
    for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl')):
        d=pickle.load(open(f,'rb')); L.append((d['C'],d['qC'],list(d['gold'])))
    arch=pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl','rb'))
    qq=pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl','rb'))
    P=[(arch[v['char']]['C'],v['qC'],list(v['gold'])) for v in qq.values()]
    R=[]
    for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d=pickle.load(open(f,'rb'))
        for i in range(len(d['qids'])):
            R.append((d['C'],d['QC'][i],list(d['gold_rows'][i])))
    M=[]
    for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
        d=pickle.load(open(f,'rb')); m=d['id_to_row']
        for i,qa in enumerate(d['qas']):
            g=[m[e] for e in qa['raw_evidence'] if e in m]
            if g: M.append((d['C'],d['QC'][i],g))
    return {'LME':L,'PerLTQA':P,'REALTALK':R,'LoCoMo':M}

DATA=load_all()
for k,v in DATA.items(): print(f'{k}: {len(v)} queries', flush=True)

def scores_for(C,q):
    Cn=np.linalg.norm(C,axis=1); qn=np.linalg.norm(q)
    cos=(C@q)/np.maximum(Cn*qn,1e-300)
    ham=((C>=0)!=(q>=0)).sum(axis=1).astype(float)
    dot=(C@q)
    euc=-np.linalg.norm(C-q,axis=1)
    sd=C.std(axis=0); sd[sd==0]=1.0
    Zs=(C/sd); zs=(q/sd)
    zcos=(Zs@zs)/np.maximum(np.linalg.norm(Zs,axis=1)*np.linalg.norm(zs),1e-300)
    # spearman across 96 dims: rank each row + query
    M96=np.vstack([C,q]); r=np.argsort(np.argsort(M96,axis=1),axis=1).astype(float)
    rc=r-np.mean(r); sd2=np.sqrt((rc**2).sum(axis=1)); sd2[sd2==0]=1
    sp=(rc[:-1]@rc[-1])/ (sd2[:-1]*sd2[-1])
    return {'sign':(ham,False),'cos':(cos,True),'dot':(dot,True),'euc':(euc,True),
            'zcos':(zcos,True),'spear':(sp,True)}

res={}
for bench,items in DATA.items():
    # CONTROL at K=3 + K-curve + tie bounds + float variants at K=3
    for K in [1,2,3,5,10,20]:
        acc={m:[] for m in ['sign','cos','dot','euc','zcos','spear']}
        w={}; b={}; tw=0
        for ci,(C,q,g) in enumerate(items):
            S=scores_for(C,q)
            for m,(s,hb) in S.items():
                e,wo,be,td=fr_stats(s,g,K,hb)
                acc[m].append(e)
                if m=='sign':
                    w[ci]=wo; b[ci]=be; tw+=td
        row={m:float(np.mean(acc[m])) for m in acc}
        row['sign_worst']=float(np.mean([w[i] for i in range(len(items))]))
        row['sign_best']=float(np.mean([b[i] for i in range(len(items))]))
        row['tie_rate']=float(tw/len(items))
        row['n']=len(items)
        res.setdefault(bench,{})[K]=row
    print(f'done {bench} {time.time()-t0:.0f}s', flush=True)

json.dump(res,open(OUT,'w'),indent=1)
for bench in ['LME','PerLTQA','REALTALK','LoCoMo']:
    r=res[bench]
    print(f"== {bench} ==")
    print(f"  CONTROL K=3: sign={r[3]['sign']:.6f} cos={r[3]['cos']:.6f} d={100*(r[3]['sign']-r[3]['cos']):+.4f}pp")
    print(f"  K-curve Delta(pp): "+", ".join(f"K={K}:{100*(r[K]['sign']-r[K]['cos']):+.2f}" for K in [1,2,3,5,10,20]))
    print(f"  K=3 float variants: "+", ".join(f"{m}={r[3][m]:.4f}" for m in ['cos','dot','euc','zcos','spear']))
    print(f"  K=3 sign worst/exp/best: {r[3]['sign_worst']:.4f}/{r[3]['sign']:.4f}/{r[3]['sign_best']:.4f} tie_rate={r[3]['tie_rate']:.3f}")
print('TOTAL',time.time()-t0,'s')
