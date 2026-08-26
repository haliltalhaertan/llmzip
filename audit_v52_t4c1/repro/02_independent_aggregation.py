import pandas as pd, numpy as np
t=pd.read_csv('pkg/V52_T4C1_trial_results.csv')
PRE={'MIXED_FLOAT96_GLOBAL':'float96','MIXED_SVD_ITQ96_GLOBAL':'itq96','MIXED_SVD_ITQ64_GLOBAL':'itq64',
     'MIXED_SVD_ITQ48_GLOBAL':'itq48','MIXED_SVD_ITQ32_GLOBAL':'itq32','MIXED_SVD_ITQ24_GLOBAL':'itq24',
     'SIMPLE_SIGN96_GLOBAL':'sign96'}
claim={'MIXED_FLOAT96_GLOBAL':44.0106,'MIXED_SVD_ITQ96_GLOBAL':37.6141,'MIXED_SVD_ITQ64_GLOBAL':30.6287,
       'MIXED_SVD_ITQ48_GLOBAL':26.2202,'MIXED_SVD_ITQ32_GLOBAL':22.8093,'MIXED_SVD_ITQ24_GLOBAL':19.9449,
       'SIMPLE_SIGN96_GLOBAL':54.1975}
res={}
print(f"{'method':<26}{'ANY':>11}{'ALL':>11}{'FRAC(flat)':>13}{'FRAC(nested)':>14}{'claim':>10}{'d_pp':>10}")
for m,p in PRE.items():
    flat={k:100*t[f'{p}_{k}_r3'].mean() for k in ['any','all','fractional']}
    # correct nesting: nuisance trials averaged inside question/seed; seeds averaged as nuisance; then equal-weight questions
    lvl1=t.groupby(['question_id','itq_seed'])[f'{p}_fractional_r3'].mean()      # avg over 20 trials
    lvl2=lvl1.groupby('question_id').mean()                                       # avg over 5 seeds (nuisance)
    nested=100*lvl2.mean()                                                        # equal weight per question
    a=100*t.groupby(['question_id','itq_seed'])[f'{p}_any_r3'].mean().groupby('question_id').mean().mean()
    al=100*t.groupby(['question_id','itq_seed'])[f'{p}_all_r3'].mean().groupby('question_id').mean().mean()
    res[m]=dict(ANY=a,ALL=al,FRAC=nested,flat=flat['fractional'])
    print(f"{m:<26}{a:>11.4f}{al:>11.4f}{flat['fractional']:>13.4f}{nested:>14.4f}{claim[m]:>10.4f}{nested-claim[m]:>+10.4f}")
print()
print("max |flat - nested| across methods:", max(abs(res[m]['FRAC']-res[m]['flat']) for m in res))
print()
f=res['MIXED_FLOAT96_GLOBAL']['FRAC']; i96=res['MIXED_SVD_ITQ96_GLOBAL']['FRAC']; s=res['SIMPLE_SIGN96_GLOBAL']['FRAC']
print(f"SIGN96 - ITQ96   = {s-i96:+.4f} pp   (claimed +16.5834)")
print(f"SIGN96 - FLOAT96 = {s-f:+.4f} pp")
print(f"FLOAT96 - ITQ96  = {f-i96:+.4f} pp   (claimed +6.3965)")
print()
print("FRONTIER (loss vs ITQ96, pp):")
for b in [24,32,48,64,96]:
    m=f'MIXED_SVD_ITQ{b}_GLOBAL'; loss=i96-res[m]['FRAC']
    print(f"  ITQ{b:<3} frac={res[m]['FRAC']:.4f}  ITQ{b}-ITQ96={res[m]['FRAC']-i96:+.4f}  loss={loss:.4f}")
for tau in [0.5,1.0,2.0]:
    ok=[b for b in [24,32,48,64,96] if (i96-res[f'MIXED_SVD_ITQ{b}_GLOBAL']['FRAC'])<=tau+1e-12]
    print(f"  smallest b within {tau} pp: {min(ok) if ok else 96}")
