import pandas as pd, numpy as np
t=pd.read_csv('pkg/V52_T4C1_trial_results.csv')
# question-level after nuisance+seed averaging
q=t.groupby('question_id').agg(**{f'{p}':(f'{p}_fractional_r3','mean') for p in ['float96','sign96','itq96','itq64','itq48','itq32','itq24']}).reset_index()
print("questions:",len(q))
def wtl(a,b,na,nb):
    d=q[a]-q[b]; w=int((d>1e-12).sum()); l=int((d<-1e-12).sum()); ti=len(q)-w-l
    mw=float(d[d>1e-12].mean())*100 if w else 0.0
    ml=float(d[d<-1e-12].mean())*100 if l else 0.0
    print(f"{na} vs {nb}: W={w} T={ti} L={l} | mean win={mw:+.3f}pp mean loss={ml:+.3f}pp | median paired gap={float(d.median())*100:+.3f}pp mean={float(d.mean())*100:+.3f}pp")
    return d
d_si=wtl('sign96','itq96','SIGN96','ITQ96')
d_sf=wtl('sign96','float96','SIGN96','FLOAT96')
d_fi=wtl('float96','itq96','FLOAT96','ITQ96')
print()
# concentration: is +16.58pp driven by few questions?
d=np.sort(d_si.to_numpy())[::-1]*100
tot=d.sum()
for k in [10,25,47,94]:
    print(f"  top {k:>3} questions ({k/len(q)*100:.0f}%) contribute {d[:k].sum()/tot*100:5.1f}% of the total SIGN96-ITQ96 gap")
print(f"  questions where SIGN96 strictly better: {int((d_si>1e-12).sum())}/{len(q)} = {(d_si>1e-12).mean()*100:.1f}%")
# leave-one-out style: gap after dropping top-k contributors
for k in [10,25,50]:
    idx=d_si.sort_values(ascending=False).index[k:]
    print(f"  SIGN96-ITQ96 after dropping top-{k} contributors: {(q.loc[idx,'sign96']-q.loc[idx,'itq96']).mean()*100:+.3f} pp")
