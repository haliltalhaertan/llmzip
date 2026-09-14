import json, pickle, csv
from pathlib import Path
import numpy as np

WORK = Path('/mnt/c/Users/MDP/dev/llmzip-work')
PKL_DIR = WORK/'regen'/'lme'/'cache_repr'
PILOT = WORK/'pilots'/'axis_attack_2026-09-12'/'pilot_results.json'
META = WORK/'drive'/'t4c3'/'V52_T4C3_question_level.csv'
DATA = WORK/'drive'/'longmemeval_s_cleaned.json'
OUT = Path('/tmp/r2a'); OUT.mkdir(parents=True, exist_ok=True)

K=3; NT=20; TOL=1e-12
EXP = {'TOP48':0.34949468085106383,'RAND48_s0':0.47292553191489356,'BOT48':0.4284574468085106}

data=json.load(open(DATA))
allq=sorted(str(x['question_id']) for x in data)
assert len(allq)==500, len(allq)
lex={q:i for i,q in enumerate(allq)}
del data

meta={}
with open(META,encoding='utf-8') as f:
    for row in csv.DictReader(f):
        meta[row['question_id']]=row

stored=json.load(open(PILOT))['per_question_native_FR']
assert len(stored)==470

RAND_IDX=np.random.default_rng(12000).choice(96,48,replace=False)
pkls=sorted(PKL_DIR.glob('*.pkl'))
assert len(pkls)==470, len(pkls)

def eval_arm(d,g,N,lx,want_ties):
    pris=[np.random.default_rng(5_100_000+lx*100_000+t*100+99).random(N) for t in range(NT)]
    gset=set(map(int,np.asarray(g).ravel()))
    ng=len(gset)
    fr=[]; grank=[]
    for p in pris:
        order=np.lexsort((p,np.asarray(d)))
        x=len(set(map(int,order[:K]))&gset)
        fr.append(x/ng)
        if want_ties:
            inv=np.empty(N,dtype=np.int64); inv[order]=np.arange(N)
            grank.append(min(int(inv[gg]) for gg in gset))
    out={'fr':float(np.mean(fr))}
    if want_ties:
        dg=min(int(d[gg]) for gg in gset)
        ncloser=int(np.count_nonzero(np.asarray(d)<dg))
        clus=int(np.count_nonzero(np.asarray(d)==dg))
        s=np.sort(np.asarray(d)); s2=int(s[2])
        clt=int(np.count_nonzero(np.asarray(d)<s2)); ceq=int(np.count_nonzero(np.asarray(d)==s2))
        bnd=1 if ceq>(K-clt) else 0
        out.update({'gold_rank':float(np.mean(grank)),'n_closer':float(ncloser),
                    'tie_cluster':float(clus),'boundary_tie':float(bnd)})
    return out

per={}
for i,p in enumerate(pkls):
    o=pickle.loads(p.read_bytes())
    qid=o['question_id']; C=o['C']; qC=o['qC']; g=np.asarray(o['gold']).ravel()
    N=len(C); lx=lex[qid]
    D0=(C>=0); Q0=(qC>=0)
    dnat=np.count_nonzero(D0!=Q0[None,:],axis=1).astype(np.int16)
    var=C.var(axis=0)
    od=np.argsort(var,kind='stable')[::-1]
    idxT=od[:48]; idxB=od[::-1][:48]; idxR=RAND_IDX
    dT=np.count_nonzero(D0[:,idxT]!=Q0[idxT][None,:],axis=1).astype(np.int16)
    dR=np.count_nonzero(D0[:,idxR]!=Q0[idxR][None,:],axis=1).astype(np.int16)
    dB=np.count_nonzero(D0[:,idxB]!=Q0[idxB][None,:],axis=1).astype(np.int16)
    rT=eval_arm(dT,g,N,lx,True); rR=eval_arm(dR,g,N,lx,True)
    rB=eval_arm(dB,g,N,lx,False); rN=eval_arm(dnat,g,N,lx,False)
    codes=(C[:,idxT]>=0)
    nunq=np.unique(codes,axis=0).shape[0]
    dup=1.0-nunq/N
    m=meta[qid]
    per[qid]={'lex':lx,'N':N,'ngold':int(len(g)),'qtype':m['question_type'],
        'N_meta':int(m['N_archive']),'ngold_meta':int(m['gold_count']),
        'fr_top':rT['fr'],'fr_rand':rR['fr'],'fr_bot':rB['fr'],'fr_nat':rN['fr'],
        'fr_nat_stored':float(stored[qid]),
        'gap':rT['fr']-rR['fr'],
        'top_gold_rank':rT['gold_rank'],'top_n_closer':rT['n_closer'],
        'top_tie_cluster':rT['tie_cluster'],'top_boundary_tie':rT['boundary_tie'],
        'rand_gold_rank':rR['gold_rank'],'rand_n_closer':rR['n_closer'],
        'rand_tie_cluster':rR['tie_cluster'],'rand_boundary_tie':rR['boundary_tie'],
        'top_dup_frac':float(dup)}
    if (i+1)%100==0: print(f'  {i+1}/470',flush=True)

qids=sorted(per.keys())
A={k:np.array([per[q][k] for q in qids]) for k in
   ['fr_top','fr_rand','fr_bot','fr_nat','gap','top_gold_rank','top_n_closer','top_tie_cluster',
    'top_boundary_tie','rand_gold_rank','rand_tie_cluster','top_dup_frac']}
Narr=np.array([per[q]['N'] for q in qids],float)
Ngold=np.array([per[q]['ngold'] for q in qids],float)

agg={k:float(A[k].mean()) if k!='gap' else None for k in ['fr_top','fr_rand','fr_bot']}
agg_full={'TOP48':float(A['fr_top'].mean()),'RAND48_s0':float(A['fr_rand'].mean()),'BOT48':float(A['fr_bot'].mean())}
diffs={k:agg_full[k]-EXP[k] for k in EXP}
nat_maxdiff=float(max(abs(per[q]['fr_nat']-per[q]['fr_nat_stored']) for q in qids))
nmeta_mismatch=sum(1 for q in qids if per[q]['N']!=per[q]['N_meta'] or per[q]['ngold']!=per[q]['ngold_meta'])

gap=A['gap']
W=int(np.sum(gap>TOL)); T=int(np.sum(np.abs(gap)<=TOL)); L=int(np.sum(gap<-TOL))
types=sorted(set(per[q]['qtype'] for q in qids))
pertype=[]
for t in types:
    gi=np.array([per[q]['gap'] for q in qids if per[q]['qtype']==t])
    pertype.append({'type':t,'n':int(len(gi)),
      'W':int(np.sum(gi>TOL)),'T':int(np.sum(np.abs(gi)<=TOL)),'L':int(np.sum(gi<-TOL)),
      'mean_gap':float(gi.mean()),'median_gap':float(np.median(gi))})
pertype.sort(key=lambda r:r['mean_gap'])

def pear(x,y):
    if np.std(x)==0 or np.std(y)==0: return float('nan')
    return float(np.corrcoef(x,y)[0,1])
corrs={'N_archive':pear(Narr,gap),'gold_count':pear(Ngold,gap),
  'RAND48_gold_rank':pear(A['rand_gold_rank'],gap),
  'TOP48_tie_cluster':pear(A['top_tie_cluster'],gap),
  'TOP48_dup_frac':pear(A['top_dup_frac'],gap)}

order=np.argsort(gap,kind='stable')
losers=[qids[i] for i in order[:10]]
winners=[qids[i] for i in order[::-1][:5]]
def row(q):
    r=per[q]
    return {'qid':q,'type':r['qtype'],'N':r['N'],'gap':r['gap'],'fr_top':r['fr_top'],'fr_rand':r['fr_rand']}
loser_rows=[row(q) for q in losers]; winner_rows=[row(q) for q in winners]

out={'per_question':{q:per[q] for q in qids},
 'aggregates':agg_full,'expected':EXP,'gate_diffs':diffs,
 'native_max_abs_diff_vs_stored':nat_maxdiff,
 'meta_mismatch_count':nmeta_mismatch,
 'WTL_overall':{'W':W,'T':T,'L':L},'per_type':pertype,'correlations':corrs,
 'losers':loser_rows,'winners':winner_rows,
 'conventions':{'gold_rank':'0-based min position in order, mean over 20 trials',
   'n_closer':'docs with d<d_gold(best-gold=min distance), trial-invariant',
   'tie_cluster':'docs with d==d_gold(best-gold), trial-invariant',
   'boundary_tie':'1 iff count(d==s[2])>(3-count(d<s[2])), s=sorted d, trial-invariant',
   'dup_frac':'1-nunique(codes)/N on TOP48 axes','gap':'TOP48-RAND48_s0','tol':TOL}}
json.dump(out,open(OUT/'per_q.json','w'))
print('GATE')
for k in EXP: print(f'  {k}: recomputed={agg_full[k]!r} expected={EXP[k]!r} diff={diffs[k]!r}')
print(f'  native_max_abs_diff_vs_stored={nat_maxdiff!r} meta_mismatch={nmeta_mismatch}')
print(f'  overall W/T/L (TOP48 vs RAND48_s0, tol 1e-12): {W}/{T}/{L}  meangap={float(gap.mean())!r} mediangap={float(np.median(gap))!r}')
print('PERTYPE (sorted by mean_gap)')
for r in pertype: print(f'  {r["type"]}: n={r["n"]} W/T/L={r["W"]}/{r["T"]}/{r["L"]} mean={r["mean_gap"]:.6f} median={r["median_gap"]:.6f}')
print('CORRS (pearson vs gap)')
for k,v in corrs.items(): print(f'  {k}: {v!r}')
print('LOSERS (10 most negative gap)')
for r in loser_rows: print(f'  {r["qid"]} {r["type"]} N={r["N"]} gap={r["gap"]:.4f} top={r["fr_top"]:.3f} rand={r["fr_rand"]:.3f}')
print('WINNERS (5 most positive gap)')
for r in winner_rows: print(f'  {r["qid"]} {r["type"]} N={r["N"]} gap={r["gap"]:.4f} top={r["fr_top"]:.3f} rand={r["fr_rand"]:.3f}')
