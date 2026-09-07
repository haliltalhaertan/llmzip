"""Post-outcome paired sensitivity analysis; no retrieval or research imports."""
import os
for variable in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[variable] = '1'
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ARMS = ['NATIVE','SCALED_NATIVE','FULLHAAR_FRESH','SCALED_FULLHAAR','BLOCK32_FRESH','SCALED_BLOCK32']
PINS = {
    'locomo':'b7abd942c13cf9ce1b1c4a13e3ff39fb26a26e8b2f2749dd92d76f0b2a474602',
    'longmemeval':'1db682a277b8fe7f0b3aa7cf02831bf07f0d5c4c340796a57c93df5441df3157'}
N = {'locomo':1535,'longmemeval':470}
NATIVE = {'locomo':0.23654714666441054,'longmemeval':0.5419751773049646}
B = 10000
CHUNK = 128
KEYS = ['A_full','A_block','A_I','B_full','B_block','B_I']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def divide(num,den):
    out = np.full_like(num,np.nan,dtype=float)
    np.divide(num,den,out=out,where=den!=0)
    return out

def statistics(means):
    # shape batch x seed x arm. Every mean uses the same paired weights.
    native = means[:,:,0]
    den = np.stack([native-means[:,:,2],native-means[:,:,4]],axis=-1)
    gain = np.stack([means[:,:,3]-means[:,:,2],means[:,:,5]-means[:,:,4]],axis=-1)
    A = np.mean(divide(gain,den),axis=1)  # NOT nanmean: all ten seeds required.
    aggregate_den = den.mean(axis=1)
    ratios = divide(gain.mean(axis=1),aggregate_den)
    stats = np.column_stack([A[:,0],A[:,1],A[:,0]-A[:,1],ratios[:,0],ratios[:,1],ratios[:,0]-ratios[:,1]])
    if np.isinf(stats).any():
        raise ArithmeticError('overflow is an algorithmic failure, not an undefined ratio')
    return stats,den,aggregate_den

def load(name):
    path = ROOT/'research/v52'/(name+'_scale_outputs')/(name+'_scale_per_question.csv.gz')
    if sha(path)!=PINS[name]:
        raise ValueError('pinned input hash mismatch')
    with gzip.open(path,'rt',newline='') as stream:
        rows = list(csv.DictReader(stream))
    questions = sorted({r['question_id'] for r in rows})
    if len(questions)!=N[name] or len(rows)!=N[name]*60:
        raise ValueError('question/row cardinality')
    qi = {q:i for i,q in enumerate(questions)}
    x = np.full((len(questions),10,6),np.nan)
    seen = set()
    ties = {}
    for r in rows:
        key = (qi[r['question_id']],int(r['rotation_seed'])-59001,ARMS.index(r['arm']))
        if key in seen or not 0<=key[1]<10:
            raise ValueError('duplicate/domain')
        value = float(r['fractional_R3'])
        if not np.isfinite(value) or not 0<=value<=1:
            raise ValueError('invalid score')
        seen.add(key)
        x[key] = value
        q,t = r['question_id'],r['tie_identity']
        if q in ties and ties[q]!=t:
            raise ValueError('inconsistent grouping')
        ties[q]=t
    if not np.isfinite(x).all() or not np.array_equal(x[:,:,0],x[:,:,1]):
        raise ValueError('coverage/paired native')
    if not np.all(x[:,:,0]==x[:,0,0,None]) or abs(x[:,:,0].mean()-NATIVE[name])>1e-12:
        raise ValueError('native reproduction')
    clusters = None
    if name=='locomo':
        clusters=[]
        for q in questions:
            m=re.fullmatch(r'archive_ordinal=(\d+);nuisance=20;stable_archive_seed\(ci,t\)\+99',ties[q])
            if m is None:
                raise ValueError('cluster mapping')
            clusters.append(int(m[1]))
        clusters=np.asarray(clusters)
        if set(clusters)!=set(range(10)):
            raise ValueError('cluster universe')
    return x,clusters

def summaries(stats,den,ad):
    out={'planned_replicates':len(stats),'algorithmic_failures':0,'statistics':{},'denominators':{}}
    for j,key in enumerate(KEYS):
        v=stats[:,j]; finite=np.isfinite(v); f=v[finite]
        e={'finite':int(finite.sum()),'undefined':int((~finite).sum()),
           'percentiles_2_5_50_97_5':np.quantile(f,[.025,.5,.975],method='linear').tolist() if len(f) else None,
           'min':float(f.min()) if len(f) else None,'max':float(f.max()) if len(f) else None,
           'quantile_scope':'conditional on finite replicates' if (~finite).any() else 'all planned replicates; fixed-seed sensitivity only'}
        if key.endswith('_I'):
            e['positive_fraction_of_all_replicates']=float(np.sum(v>0)/len(v))
        else:
            e['band_frequencies_of_all_replicates']={'little':float(np.sum(v<=.2)/len(v)),'partial':float(np.sum((v>.2)&(v<.7))/len(v)),'most':float(np.sum(v>=.7)/len(v))}
        out['statistics'][key]=e
    for j,arm in enumerate(['full','block']):
        d=den[:,:,j]; a=ad[:,j]
        out['denominators'][arm]={
            'replicates_any_seed_negative':int(np.any(d<0,axis=1).sum()),
            'replicates_any_seed_zero':int(np.any(d==0,axis=1).sum()),
            'replicates_any_seed_near_zero_1e_12':int(np.any(np.abs(d)<=1e-12,axis=1).sum()),
            'replicates_seed_signs_cross_zero':int(((d.min(axis=1)<0)&(d.max(axis=1)>0)).sum()),
            'seed_denominator_range':[float(d.min()),float(d.max())],
            'aggregate_negative':int((a<0).sum()),'aggregate_zero':int((a==0).sum()),
            'aggregate_near_zero_1e_12':int((np.abs(a)<=1e-12).sum()),
            'aggregate_range':[float(a.min()),float(a.max())]}
    return out

def resample(x,clusters,seed):
    rng=np.random.Generator(np.random.PCG64(seed))
    if clusters is None:
        units=x.reshape(len(x),60); sizes=np.ones(len(x)); draws=len(x)
    else:
        ids=sorted(set(clusters)); sizes=np.array([np.sum(clusters==i) for i in ids])
        units=np.array([x[clusters==i].sum(axis=0).reshape(60) for i in ids]); draws=len(ids)
    values=[]; denominators=[]; aggregates=[]; sample_sizes=[]
    for start in range(0,B,CHUNK):
        count=min(CHUNK,B-start)
        w=rng.multinomial(draws,np.full(draws,1/draws),size=count)
        n=w@sizes
        means=((w@units)/n[:,None]).reshape(count,10,6)
        if not np.array_equal(means[:,:,0],means[:,:,1]):
            raise AssertionError('pairing lost')
        st,d,ad=statistics(means)
        values.append(st);denominators.append(d);aggregates.append(ad);sample_sizes.extend(n.tolist())
    return np.concatenate(values),np.concatenate(denominators),np.concatenate(aggregates),sample_sizes

def write_csv(path,stats,den,ad,sizes):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n')
        w.writerow(['replicate','n_questions']+KEYS+['den_full_min','den_full_max','den_block_min','den_block_max','den_full_mean','den_block_mean'])
        for i,row in enumerate(stats):
            vals=list(row)+[den[i,:,0].min(),den[i,:,0].max(),den[i,:,1].min(),den[i,:,1].max(),ad[i,0],ad[i,1]]
            w.writerow([i+1,int(sizes[i])]+[format(float(v),'.17g') if np.isfinite(v) else '' for v in vals])

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run',action='store_true');args=parser.parse_args()
    if not args.run:
        raise SystemExit('Explicit --run required for approved analysis; no research execution')
    output=HERE/'outputs'
    if output.exists():
        raise SystemExit('Refuse overwrite or rerun: outputs directory already exists')
    output.mkdir()
    result={'status':'POST_OUTCOME_SENSITIVITY_NOT_SCIENTIFIC_ACCEPTANCE','replicates_per_scheme':B,
            'fixed_rotation_seeds':list(range(59001,59011)),'input_sha256':PINS,
            'code_sha256':sha(Path(__file__)),'plan_sha256':sha(HERE/'ANALYSIS_PLAN.md'),
            'precomputation_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'threads':'1'},'schemes':{}}
    for name,kind,seed in [('locomo','question',2026090701),('locomo','cluster',2026090702),('longmemeval','question',2026090703)]:
        x,cl=load(name)
        point,pd,pa=statistics(x.mean(axis=0)[None,:,:])
        st,d,ad,sizes=resample(x,cl if kind=='cluster' else None,seed)
        key=name+'_'+kind
        write_csv(output/(key+'.csv'),st,d,ad,sizes)
        ent=summaries(st,d,ad)
        point_means=x.mean(axis=0)
        point_gain=np.stack([point_means[:,3]-point_means[:,2],point_means[:,5]-point_means[:,4]],axis=-1)
        point_ratio=divide(point_gain,pd[0])
        safe=lambda value: float(value) if np.isfinite(value) else None
        ent.update({'bootstrap_rng_seed':seed,'point':dict(zip(KEYS,[safe(v) for v in point[0]])),
                    'point_seed_gains':point_gain.tolist(),
                    'point_seed_ratios':[[safe(v) for v in row] for row in point_ratio],
                    'point_seed_denominators':pd[0].tolist(),'sample_size_range':[int(min(sizes)),int(max(sizes))],
                    'replicates_csv_sha256':sha(output/(key+'.csv'))})
        result['schemes'][key]=ent
        print(key, 'complete',flush=True)
    result['longmemeval_cluster']='NOT COMPUTED: conversation mapping not established'
    (output/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
    main()
