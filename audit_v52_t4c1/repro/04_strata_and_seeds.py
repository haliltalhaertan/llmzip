import pandas as pd, numpy as np
t=pd.read_csv('pkg/V52_T4C1_trial_results.csv')
cols=['float96','sign96','itq96','itq64']
q=t.groupby(['question_id','question_type','gold_stratum','archive_quartile','reuse_tertile'],as_index=False).agg(
    **{p:(f'{p}_fractional_r3','mean') for p in cols})
print(f"{'stratum':<34}{'n':>5}{'SIGN-ITQ96':>12}{'SIGN-FLOAT':>12}{'ITQ64-ITQ96':>13}")
def blk(col,order=None):
    order=order or sorted(q[col].unique())
    for g in order:
        x=q[q[col]==g]
        print(f"  {str(g):<32}{len(x):>5}{(x.sign96-x.itq96).mean()*100:>12.3f}{(x.sign96-x.float96).mean()*100:>12.3f}{(x.itq64-x.itq96).mean()*100:>13.3f}")
print("-- question_type --"); blk('question_type')
print("-- gold_stratum --"); blk('gold_stratum',['one-gold','multi-gold'])
print("-- archive_quartile --"); blk('archive_quartile',['Q1','Q2','Q3','Q4'])
print("-- reuse_tertile --"); blk('reuse_tertile',['low','medium','high'])
print()
print("SEEDS (Fractional R@3, %):")
print(f"{'method':<26}"+"".join(f"{s:>10}" for s in [101,202,303,404,505])+f"{'spread':>9}")
for m,p in [('MIXED_FLOAT96_GLOBAL','float96'),('SIMPLE_SIGN96_GLOBAL','sign96')]+[(f'MIXED_SVD_ITQ{b}_GLOBAL',f'itq{b}') for b in [96,64,48,32,24]]:
    v=[100*t[t.itq_seed==s][f'{p}_fractional_r3'].mean() for s in [101,202,303,404,505]]
    print(f"{m:<26}"+"".join(f"{x:>10.4f}" for x in v)+f"{max(v)-min(v):>9.4f}")
print()
print("Worst-case seed check: does ANY ITQ96 seed beat SIGN96?")
best=max(100*t[t.itq_seed==s]['itq96_fractional_r3'].mean() for s in [101,202,303,404,505])
print(f"  best ITQ96 seed = {best:.4f}%  vs SIGN96 = {100*t.sign96_fractional_r3.mean():.4f}%  -> gap still {100*t.sign96_fractional_r3.mean()-best:+.4f} pp")
