"""Fix REALTALK: inspect empty golds, recompute. READ-ONLY on caches."""
import pickle, glob, json, numpy as np
from atk import fr_stats, scores_for  # reuse
R=[]; nskip=0
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    d=pickle.load(open(f,'rb'))
    for i in range(len(d['qids'])):
        g=list(d['gold_rows'][i])
        if len(g)==0: nskip+=1; continue
        R.append((d['C'],d['QC'][i],g))
print('RT nonempty queries:',len(R),'skipped empty-gold:',nskip)
for K in [1,2,3,5,10,20]:
    acc={m:[] for m in ['sign','cos','dot','euc','zcos','spear']}; ws=[]; bs=[]; tw=0
    for (C,q,g) in R:
        S=scores_for(C,q)
        for m,(s,hb) in S.items():
            e,wo,be,td=fr_stats(s,g,K,hb)
            acc[m].append(e)
            if m=='sign': ws.append(wo); bs.append(be); tw+=td
    row={m:float(np.mean(acc[m])) for m in acc}
    print(f"K={K}: sign={row['sign']:.6f} cos={row['cos']:.6f} d={100*(row['sign']-row['cos']):+.4f}pp | "
          f"dot={row['dot']:.4f} euc={row['euc']:.4f} zcos={row['zcos']:.4f} spear={row['spear']:.4f} | "
          f"sign worst/exp/best={np.mean(ws):.4f}/{row['sign']:.4f}/{np.mean(bs):.4f} tierate={tw/len(R):.3f}")
