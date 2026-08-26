import pandas as pd, numpy as np
P='pkg/V52_T4C1_trial_results.csv'
t=pd.read_csv(P)
print("rows",len(t),"expected",470*20*5)
print("unique qid",t.question_id.nunique())
print("trials",sorted(t.trial.unique())==list(range(20)),"seeds",sorted(t.itq_seed.unique()))
# duplicate cells
k=t.groupby(['question_id','trial','itq_seed']).size()
print("dup cells:",int((k>1).sum()),"| cells:",len(k))
# rows per question -> balance
rpq=t.groupby('question_id').size()
print("rows/question min,max:",rpq.min(),rpq.max(),"| all==100:",bool((rpq==100).all()))
# abstention leakage
print("any _abs qid:",int(t.question_id.str.endswith('_abs').sum()))
print("gold_count==0:",int((t.gold_count==0).sum()))
# NaN / Inf check on metric cols
mc=[c for c in t.columns if c.endswith(('_any_r3','_all_r3','_fractional_r3'))]
print("metric cols:",len(mc))
print("NaN total:",int(t[mc].isna().sum().sum()),"| out-of-range:",int(((t[mc]<0)|(t[mc]>1)).sum().sum()))
# sign96/float96 must be constant within (qid,trial) across the 5 seeds
for p in ['float96','sign96']:
    g=t.groupby(['question_id','trial'])[[f'{p}_any_r3',f'{p}_all_r3',f'{p}_fractional_r3']].nunique()
    print(f"{p}: max distinct values within (qid,trial) =",int(g.to_numpy().max()))
# ITQ96 varies across seeds? (sanity: should not be constant everywhere)
g=t.groupby(['question_id','trial'])['itq96_fractional_r3'].nunique()
print("itq96 distinct-across-seed within (qid,trial): mean",round(float(g.mean()),4),"max",int(g.max()))
