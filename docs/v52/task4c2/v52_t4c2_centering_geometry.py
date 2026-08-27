#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, hashlib, importlib.util, io, json, math, os, pickle, platform, shutil, sys, time, zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('NUMEXPR_NUM_THREADS','1')

import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy import sparse
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

TASK='V52 Task 4C2 — Centering / Sign-Geometry Diagnostic'
EXPECTED_DATASET_SHA='d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442'
EXPECTED_DATASET_BYTES=277383467
EXPECTED_TOTAL=500
EXPECTED_PRIMARY=470
EXPECTED_ADAPTER_V1_SHA='0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722'
EXPECTED_ADAPTER_V2_SHA='643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218'
EXPECTED_T4B_SCRIPT_SHA='596dd91d07b04f987c3905d81edcc9134d6ed44517aff16d021ca9018596a467'
EXPECTED_T4C1_SCRIPT_SHA='54930bd66e666d8485b51a5a77d8f1b77b46769520b4e5c59526262e017e8573'
EXPECTED_T4C1_TRIAL_SHA='0695dc066d328816ead5f38d0d1ab6b4cbf5360aadaf26682f274e5bfc9e1f72'
EXPECTED_T4C1_QLEVEL_SHA='df499d1069599c73dd3abc6b3d59a63a0e72c4b8143b0a9d896b1dc38e2be579'
EXPECTED_T4C1_AGG_SHA='1b68897ad12a21bd532166c560746108e61888e94975028067df1829a98a1f01'
EXPECTED_T4C1_PREREG_SHA='a6b4346ab419468b547e5ac1075d3500708677f9f8f5b9233c8126e324d5b877'
EXPECTED_T4C1_SPEC_SHA='c2cc1e70020f15d2e1bc9bf90525f72c4b773685de2fbd71181c3effba66993d'
EXPECTED_T4C1_PRESEAL_SHA='25d87806e92ef1c2aed9f3fa8acad6313f927432ee197161245fdd536e26afac'
SVD_RANDOM_STATE=5204
ITQ_SEEDS=[101,202,303,404,505]
N_NUISANCE=20
TOPK=3
TOL=1e-12
METHODS=['FLOAT96_UNCENTERED','FLOAT96_CENTERED','SIGN96_CENTERED','ITQ96_CENTERED']
DECISION_BANDS={
 'CASE_A':{'condition':'abs(G)<=1.0 pp','verdict':'[CENTERING EXPLAINS SIGN96 ADVANTAGE]'},
 'CASE_B':{'condition':'1.0<G<5.0 pp','verdict':'[MIXED — CENTERING EXPLAINS PART, SIGN/HAMMING RETAINS RESIDUAL]'},
 'CASE_C':{'condition':'G>=5.0 pp','verdict':'[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]'},
 'CASE_D':{'condition':'G<-1.0 pp','verdict':'[FALSIFIED — CENTERED FLOAT DOMINATES SIGN]'},
}
EXPECTED_T4C1={
 'FLOAT96_UNCENTERED':{'ANY_R3':0.6106382978723405,'ALL_R3':0.2893617021276596,'Fractional_R3':0.4401063829787234},
 'SIGN96_CENTERED':{'ANY_R3':0.7130851063829787,'ALL_R3':0.38457446808510637,'Fractional_R3':0.5419751773049646},
 'ITQ96_CENTERED':{'ANY_R3':0.5427659574468086,'ALL_R3':0.22672340425531914,'Fractional_R3':0.3761411347517731},
}
QUESTION_TYPES=['single-session-user','single-session-assistant','single-session-preference','temporal-reasoning','knowledge-update','multi-session']


def sha256_file(p:Path,chunk:int=8<<20)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(chunk),b''): h.update(b)
    return h.hexdigest()


def load_module(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def metrics3(indices,gold_rows):
    s=set(map(int,indices)); g=set(map(int,gold_rows)); hit=len(s&g)
    return float(hit>0),float(hit==len(g) and len(g)>0),float(hit/len(g)) if g else np.nan


def rank_hamming(dist,priority): return np.lexsort((priority,np.asarray(dist)))
def rank_float(scores,priority): return np.lexsort((priority,-np.asarray(scores,dtype=np.float64)))


def cosine_centered(C,qC):
    C=np.asarray(C,dtype=np.float64); q=np.asarray(qC,dtype=np.float64).reshape(-1)
    dn=np.linalg.norm(C,axis=1); qn=float(np.linalg.norm(q))
    if qn<=0 or np.any(dn<=0): raise RuntimeError('[BUG] zero centered vector norm in cosine')
    return (C@q)/(dn*qn)


def static_leakage_audit(v1p:Path,v2p:Path,scriptp:Path)->pd.DataFrame:
    s1=v1p.read_text(encoding='utf-8'); s2=v2p.read_text(encoding='utf-8'); ss=scriptp.read_text(encoding='utf-8')
    t1,t2,ts=ast.parse(s1),ast.parse(s2),ast.parse(ss)
    f1={n.name:n for n in ast.walk(t1) if isinstance(n,ast.FunctionDef)}
    f2={n.name:n for n in ast.walk(t2) if isinstance(n,ast.FunctionDef)}
    fs={n.name:n for n in ast.walk(ts) if isinstance(n,ast.FunctionDef)}
    rows=[]
    f=f1['fit_input_payload']; body=ast.get_source_segment(s1,f) or ''; args={a.arg for a in f.args.args}
    ok=args=={'memories'} and 'memory_text' in body and 'has_answer' not in body and 'answer_session_ids' not in body
    rows.append({'check':'v1.fit_input_payload archive-text-only','derived_evidence':f'args={sorted(args)}; memory_text={"memory_text" in body}','status':'PASS' if ok else 'FAIL','blocking':int(not ok)})
    f=f1['fit_archive_representation']; body=ast.get_source_segment(s1,f) or ''; args={a.arg for a in f.args.args}
    ok=args=={'memory_texts'} and 'fit_transform(memory_texts)' in body
    rows.append({'check':'v1.fit_archive_representation archive-only','derived_evidence':f'args={sorted(args)}','status':'PASS' if ok else 'FAIL','blocking':int(not ok)})
    f=f1['fit_itq']; args={a.arg for a in f.args.args}; ok=args=={'V','n_iter','seed'}
    rows.append({'check':'v1.fit_itq matrix-only','derived_evidence':f'args={sorted(args)}','status':'PASS' if ok else 'FAIL','blocking':int(not ok)})
    alias_ok='fit_archive_representation = v1.fit_archive_representation' in s2 and 'fit_input_payload = v1.fit_input_payload' in s2
    rows.append({'check':'v2 preserves v1 representation functions','derived_evidence':'v2 aliases frozen v1 fit functions','status':'PASS' if alias_ok else 'FAIL','blocking':int(not alias_ok)})
    f=f2['build_archive']; b2=ast.get_source_segment(s2,f) or ''
    ok='session_position' in b2 and "'memory_text': f\"[{date}] {role}: {content}\"" in b2
    rows.append({'check':'session_position identity-only','derived_evidence':'position enters memory_id; memory_text is date+role+content','status':'PASS' if ok else 'FAIL','blocking':int(not ok)})
    f=fs['evaluate_item']; b=ast.get_source_segment(ss,f) or ''
    dup_ok="if len(id_to_row) != len(memories):" in b and "raise RuntimeError(f'{qid}: duplicate memory_id')" in b
    rows.append({'check':'duplicate-ID hardening exact assertion','derived_evidence':'exact required assertion in evaluate_item','status':'PASS' if dup_ok else 'FAIL','blocking':int(not dup_ok)})
    p_archive=b.find('fit_archive_representation(texts)'); p_itq=b.find('fit_itq(C_itq'); p_query=b.find('wv.transform([question])')
    order_ok=p_archive>=0 and p_itq>p_archive and p_query>p_itq
    rows.append({'check':'all archive fits precede query transform','derived_evidence':f'archive_offset={p_archive}; itq_offset={p_itq}; query_offset={p_query}','status':'PASS' if order_ok else 'FAIL','blocking':int(not order_ok)})
    forbidden_fit=False
    for n in ast.walk(f):
        if isinstance(n,ast.Call):
            txt=ast.get_source_segment(ss,n) or ''
            if ('fit_transform(' in txt or 'fit_itq(' in txt) and any(x in txt for x in ['gold_rows','gold_ids','question_type','answer_session_ids']): forbidden_fit=True
    rows.append({'check':'no gold/evidence/type in fitting calls','derived_evidence':'AST call-argument scan','status':'PASS' if not forbidden_fit else 'FAIL','blocking':int(forbidden_fit)})
    extra_method_terms=['whiten','euclidean','shortlist','rerank','locomo','sign_uncentered','alternative_threshold']
    lower=b.lower(); bad=[x for x in extra_method_terms if x in lower]
    rows.append({'check':'no forbidden rescue retrieval method','derived_evidence':'evaluate_item source token scan; bad='+repr(bad),'status':'PASS' if not bad else 'FAIL','blocking':int(bool(bad))})
    fc_def='cosine_centered(C_float,qC_float)' in b
    rows.append({'check':'FLOAT96_CENTERED exact centered cosine path','derived_evidence':'cosine_centered(C_float,qC_float)','status':'PASS' if fc_def else 'FAIL','blocking':int(not fc_def)})
    return pd.DataFrame(rows)


def verify_frozen_files(args,script_path:Path):
    checks={
      'dataset_sha256':sha256_file(args.dataset),'dataset_bytes':args.dataset.stat().st_size,
      'adapter_v1_sha256':sha256_file(args.adapter_v1),'adapter_v2_sha256':sha256_file(args.adapter_v2),
      'task4b_script_sha256':sha256_file(args.task4b_script),'task4c1_script_sha256':sha256_file(args.task4c1_script),
      'task4c1_trial_sha256':sha256_file(args.task4c1_trial),'task4c1_qlevel_sha256':sha256_file(args.task4c1_qlevel),
      'task4c1_aggregate_sha256':sha256_file(args.task4c1_aggregate),'task4c1_prereg_sha256':sha256_file(args.prereg),
      'task4c1_method_spec_sha256':sha256_file(args.method_spec),'task4c1_preseal_sha256':sha256_file(args.task4c1_preseal),
      'new_task4c2_script_sha256':sha256_file(script_path),
    }
    expected={
      'dataset_sha256':EXPECTED_DATASET_SHA,'dataset_bytes':EXPECTED_DATASET_BYTES,'adapter_v1_sha256':EXPECTED_ADAPTER_V1_SHA,
      'adapter_v2_sha256':EXPECTED_ADAPTER_V2_SHA,'task4b_script_sha256':EXPECTED_T4B_SCRIPT_SHA,'task4c1_script_sha256':EXPECTED_T4C1_SCRIPT_SHA,
      'task4c1_trial_sha256':EXPECTED_T4C1_TRIAL_SHA,'task4c1_qlevel_sha256':EXPECTED_T4C1_QLEVEL_SHA,'task4c1_aggregate_sha256':EXPECTED_T4C1_AGG_SHA,
      'task4c1_prereg_sha256':EXPECTED_T4C1_PREREG_SHA,'task4c1_method_spec_sha256':EXPECTED_T4C1_SPEC_SHA,'task4c1_preseal_sha256':EXPECTED_T4C1_PRESEAL_SHA,
    }
    for k,v in expected.items():
        if checks[k]!=v: raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] {k}: {checks[k]} != {v}')
    post=json.loads(args.task4c1_postmanifest.read_text(encoding='utf-8'))
    if post.get('script_sha256')!=EXPECTED_T4C1_SCRIPT_SHA or post.get('dataset_sha256')!=EXPECTED_DATASET_SHA:
        raise RuntimeError('[BLOCKED — FROZEN INPUT MISMATCH] Task4C1 post-manifest binding')
    if post.get('output_hashes',{}).get('V52_T4C1_trial_results.csv')!=EXPECTED_T4C1_TRIAL_SHA:
        raise RuntimeError('[BLOCKED — FROZEN INPUT MISMATCH] Task4C1 trial manifest hash')
    return checks


def prepare_inputs(args,script_path:Path):
    args.outdir.mkdir(parents=True,exist_ok=True); args.workdir.mkdir(parents=True,exist_ok=True); args.itemsdir.mkdir(parents=True,exist_ok=True); args.cachedir.mkdir(parents=True,exist_ok=True)
    checks=verify_frozen_files(args,script_path)
    leak=static_leakage_audit(args.adapter_v1,args.adapter_v2,script_path)
    leak.to_csv(args.outdir/'V52_T4C2_leakage_audit.csv',index=False)
    if int(leak.blocking.sum())!=0: raise RuntimeError('[BLOCKED — STATIC LEAKAGE/PROTOCOL AUDIT FAILURE]')
    data=json.loads(args.dataset.read_text(encoding='utf-8'))
    if len(data)!=EXPECTED_TOTAL: raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] total={len(data)}')
    qids=[str(x['question_id']) for x in data]
    if len(set(qids))!=len(qids): raise RuntimeError('[BLOCKED — FROZEN INPUT MISMATCH] duplicate question_id')
    lexical={q:i for i,q in enumerate(sorted(qids))}
    primary=[x for x in data if not str(x['question_id']).endswith('_abs')]
    if len(primary)!=EXPECTED_PRIMARY: raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] primary={len(primary)}')
    adapter=load_module(args.adapter_v2,'precheck_adapter_v2')
    dynamic=[]; zero=0
    for item in primary:
        qid=str(item['question_id']); memories,gold,issues=adapter.build_archive(item)
        if issues: raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] {qid} archive issues {issues[:2]}')
        mids=[m['memory_id'] for m in memories]
        if len(set(mids))!=len(mids): raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] {qid} duplicate memory_id')
        if not all(g in set(mids) for g in gold): raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] {qid} unmapped gold')
        if not gold: zero+=1
        dynamic.append({'question_id':qid,'question_type':str(item['question_type']),'lexical_ordinal':lexical[qid],'N_archive':len(memories),'gold_count':len(gold)})
    if zero: raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] primary zero-gold={zero}')
    dyn=pd.DataFrame(dynamic)
    frozen=pd.read_csv(args.task4c1_qlevel)
    if len(frozen)!=EXPECTED_PRIMARY or frozen.question_id.nunique()!=EXPECTED_PRIMARY: raise RuntimeError('[BLOCKED — FROZEN INPUT MISMATCH] T4C1 qlevel cardinality')
    need=['question_id','question_type','N_archive','gold_count','reuse_count','reuse_tertile','archive_quartile','gold_stratum']
    if not all(c in frozen.columns for c in need): raise RuntimeError('[BLOCKED — FROZEN INPUT MISMATCH] T4C1 qlevel strata columns')
    z=dyn.merge(frozen[need],on='question_id',suffixes=('_dyn','_frozen'),validate='one_to_one')
    bad=(z.question_type_dyn!=z.question_type_frozen)|(z.N_archive_dyn!=z.N_archive_frozen)|(z.gold_count_dyn!=z.gold_count_frozen)
    if bad.any(): raise RuntimeError(f'[BLOCKED — FROZEN INPUT MISMATCH] dynamic vs T4C1 geometry mismatches={int(bad.sum())}')
    geom=z[['question_id','lexical_ordinal','N_archive_dyn','gold_count_dyn','question_type_dyn','reuse_count','reuse_tertile','archive_quartile','gold_stratum']].rename(columns={'N_archive_dyn':'N_archive','gold_count_dyn':'gold_count','question_type_dyn':'question_type'})
    if sorted(geom.question_type.unique())!=sorted(QUESTION_TYPES): raise RuntimeError('[BLOCKED — FROZEN INPUT MISMATCH] question types')
    geom.to_csv(args.workdir/'primary_geometry.csv',index=False)
    for p in args.itemsdir.glob('*.json'): p.unlink()
    for item in primary:
        (args.itemsdir/f"{item['question_id']}.json").write_text(json.dumps(item,ensure_ascii=False),encoding='utf-8')
    checks.update({'questions_total':len(data),'primary_non_abs':len(primary),'primary_zero_gold':zero,'duplicate_id_assert':'PASS','frozen_strata_binding':'PASS','question_types':sorted(geom.question_type.unique())})
    (args.outdir/'V52_T4C2_INPUT_CHECKS.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
    return checks,geom


def create_seal(args,script_path:Path):
    sealp=args.outdir/'V52_T4C2_PRE_RUN_SEAL.json'
    if sealp.exists(): raise RuntimeError('REFUSE overwrite: immutable V52_T4C2_PRE_RUN_SEAL.json already exists')
    checks,geom=prepare_inputs(args,script_path)
    seal={
      'task':TASK,'status':'SEALED_BEFORE_ANY_NEW_FLOAT96_CENTERED_PERFORMANCE','NO_NEW_CENTERED_PERFORMANCE_OBSERVED_BEFORE_SEAL':True,
      'created_at_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':checks['new_task4c2_script_sha256'],
      'dataset_sha256':checks['dataset_sha256'],'dataset_byte_size':checks['dataset_bytes'],'adapter_v1_sha256':checks['adapter_v1_sha256'],'adapter_v2_sha256':checks['adapter_v2_sha256'],
      'task4c1_source_binding':{'script_sha256':checks['task4c1_script_sha256'],'trial_sha256':checks['task4c1_trial_sha256'],'qlevel_sha256':checks['task4c1_qlevel_sha256'],'aggregate_sha256':checks['task4c1_aggregate_sha256'],'pre_run_seal_sha256':checks['task4c1_preseal_sha256']},
      'exact_methods':METHODS,
      'FLOAT96_CENTERED_definition':{'archive':'Y96 frozen normalized 96D; mu96=archive mean; C96=Y96-mu96','query':'qC96=QY96-mu96','ranking':'global exact cosine similarity(qC96,C96)','extra_svd':False,'refit':False,'whitening':False,'second_centering':False,'learned_metric':False,'shortlist':False,'reranker':False},
      'decision_variable':'G = SIGN96_CENTERED Fractional R@3 - FLOAT96_CENTERED Fractional R@3, percentage points','decision_bands':DECISION_BANDS,
      'cohort_rule':'question_id not ending _abs','primary_n':EXPECTED_PRIMARY,'metrics':['Fractional Evidence Recall@3','ANY Evidence Recall@3','ALL Evidence Recall@3'],
      'svd_random_state':SVD_RANDOM_STATE,'itq_seeds':ITQ_SEEDS,'nuisance_trials':N_NUISANCE,'top_k':TOPK,
      'tie_rule_binary':'integer Hamming primary; frozen independent priority secondary using stable_archive_seed(lexical_ordinal,trial) then rng(seed+99)',
      'tie_rule_float':'descending float64 cosine primary; same frozen independent priority only for exact ties',
      'inference':'fixed-benchmark paired estimand only; no population p-values/CIs/superiority/equivalence/non-inferiority',
      'package_versions':{'python':sys.version.split()[0],'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'platform':platform.platform()},
    }
    sealp.write_text(json.dumps(seal,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'PRE_RUN_SEAL':str(sealp),'pre_run_seal_sha256':sha256_file(sealp),'script_sha256':seal['script_sha256'],'input_checks':'PASS'},indent=2),flush=True)


def load_seal(args,script_path:Path):
    p=args.outdir/'V52_T4C2_PRE_RUN_SEAL.json'
    if not p.exists(): raise RuntimeError('Missing immutable V52_T4C2_PRE_RUN_SEAL.json')
    s=json.loads(p.read_text(encoding='utf-8'))
    if s['script_sha256']!=sha256_file(script_path): raise RuntimeError('[PROTOCOL SEAL FAILURE] script SHA differs before run')
    if s['dataset_sha256']!=sha256_file(args.dataset) or s['dataset_byte_size']!=args.dataset.stat().st_size: raise RuntimeError('[PROTOCOL SEAL FAILURE] dataset binding')
    if s['adapter_v1_sha256']!=sha256_file(args.adapter_v1) or s['adapter_v2_sha256']!=sha256_file(args.adapter_v2): raise RuntimeError('[PROTOCOL SEAL FAILURE] adapter binding')
    return s


def bit_collision_tie(method,seed,D,Q,dist,qid,gold_rows):
    packed=np.packbits(D,axis=1,bitorder='big')
    _,counts=np.unique(packed,axis=0,return_counts=True)
    unique_codes=int(len(counts)); N=len(D)
    exact=int(np.sum(np.all(D==Q[None,:],axis=1)))
    sd=np.sort(dist); d3=int(sd[TOPK-1]); count_lt=int(np.sum(dist<d3)); boundary_count=int(np.sum(dist==d3)); slots=TOPK-count_lt
    collision={'question_id':qid,'method':method,'itq_seed':seed,'N_archive':N,'unique_document_codes':unique_codes,'unique_document_code_fraction':unique_codes/N,'duplicate_code_fraction':1.0-unique_codes/N,'largest_collision_bucket':int(counts.max()),'query_exact_code_match_count':exact,'query_exact_code_match_fraction':exact/N}
    tie={'question_id':qid,'method':method,'itq_seed':seed,'N_archive':N,'min_hamming_distance':int(dist.min()),'candidates_at_min_distance':int(np.sum(dist==dist.min())),'top3_boundary_distance':d3,'candidates_at_top3_boundary_distance':boundary_count,'slots_remaining_at_boundary':slots,'top3_boundary_tie':int(boundary_count>slots)}
    g=np.asarray(sorted(gold_rows),dtype=int); mask=np.ones(N,dtype=bool); mask[g]=False
    dg=dist[g]; dn=dist[mask]
    distance={'question_id':qid,'geometry':'HAMMING','method':method,'itq_seed':seed,'gold_mean':float(np.mean(dg)),'gold_median':float(np.median(dg)),'non_gold_mean':float(np.mean(dn)),'non_gold_median':float(np.median(dn)),'nearest_gold':float(np.min(dg)),'nearest_non_gold':float(np.min(dn)),'separation_non_gold_minus_gold_mean':float(np.mean(dn)-np.mean(dg))}
    return collision,tie,distance,packed


def evaluate_item(item_path:str,lexical_ordinal:int,adapter_v2_path:str,cache_path:str):
    cp=Path(cache_path)
    if cp.exists(): return {'question_id':cp.stem,'cached':True}
    adapter=load_module(Path(adapter_v2_path),f'a2_{os.getpid()}_{lexical_ordinal}')
    item=json.loads(Path(item_path).read_text(encoding='utf-8'))
    qid=str(item['question_id']); question=str(item['question']); qtype=str(item['question_type'])
    memories,gold_ids,issues=adapter.build_archive(item)
    if issues: raise RuntimeError(f'{qid}: archive issues {issues[:2]}')
    texts=adapter.fit_input_payload(memories); N=len(memories)
    id_to_row={m['memory_id']:i for i,m in enumerate(memories)}
    if len(id_to_row) != len(memories):
        raise RuntimeError(f'{qid}: duplicate memory_id')
    try: gold_rows=[id_to_row[g] for g in gold_ids]
    except KeyError as e: raise RuntimeError(f'{qid}: unmapped gold {e}')
    if not gold_rows: raise RuntimeError(f'{qid}: zero gold')

    t0=time.perf_counter(); wv,cv,base_svd,Xw,Xc,Xl=adapter.fit_archive_representation(texts); base_fit_s=time.perf_counter()-t0
    Z=sparse.hstack([sparse.csr_matrix(Xl),Xw,Xc],format='csr')
    if Z.shape[1]<96: raise RuntimeError(f'{qid}: combined features <96')
    svd96=TruncatedSVD(n_components=96,random_state=SVD_RANDOM_STATE)
    t=time.perf_counter(); Y=normalize(svd96.fit_transform(Z)); svd_fit_s=time.perf_counter()-t
    if Y.shape!=(N,96) or np.linalg.matrix_rank(Y)<96: raise RuntimeError(f'{qid}: SVD96 shape/rank failure')
    mu=Y.mean(axis=0,keepdims=True)
    # Numerically independent same-input constructions, not aliases.
    C_float=np.subtract(Y,mu)
    C_sign=Y.copy(); C_sign-=mu
    C_itq=Y + (-mu)
    archive_fs=float(np.max(np.abs(C_float-C_sign))); archive_fi=float(np.max(np.abs(C_float-C_itq))); archive_si=float(np.max(np.abs(C_sign-C_itq)))
    rotations={}; itq_fit_s=0.0
    for s in ITQ_SEEDS:
        t=time.perf_counter(); rotations[s]=adapter.v1.fit_itq(C_itq,seed=s); itq_fit_s+=time.perf_counter()-t
        if rotations[s].shape!=(96,96): raise RuntimeError(f'{qid}: ITQ96 seed{s} shape')

    # Query only after all archive-side fits.
    tq=time.perf_counter(); Qw=normalize(wv.transform([question])); Qc=normalize(cv.transform([question])); Ql=normalize(base_svd.transform(Qw)); Zq=sparse.hstack([sparse.csr_matrix(Ql),Qw,Qc],format='csr'); QY=normalize(svd96.transform(Zq)); query_fit_s=time.perf_counter()-tq
    if QY.shape!=(1,96): raise RuntimeError(f'{qid}: QY96 shape')
    qC_float=np.subtract(QY,mu)
    qC_sign=QY.copy(); qC_sign-=mu
    qC_itq=QY+(-mu)
    query_fs=float(np.max(np.abs(qC_float-qC_sign))); query_fi=float(np.max(np.abs(qC_float-qC_itq))); query_si=float(np.max(np.abs(qC_sign-qC_itq)))
    same_max=max(archive_fs,archive_fi,archive_si,query_fs,query_fi,query_si)
    if same_max>1e-12: raise RuntimeError(f'[BUG — NOT A CLEAN GEOMETRY ABLATION] {qid} maxdiff={same_max}')

    f0_scores=np.asarray(Y@QY[0],dtype=np.float64)
    fc_scores=cosine_centered(C_float,qC_float)
    if not np.isfinite(f0_scores).all() or not np.isfinite(fc_scores).all(): raise RuntimeError(f'{qid}: nonfinite continuous scores')
    signD=C_sign>=0; signQ=(qC_sign>=0)[0]; sign_dist=np.count_nonzero(signD!=signQ[None,:],axis=1).astype(np.int16)
    itqD={}; itqQ={}; itqdist={}
    for s in ITQ_SEEDS:
        R=rotations[s]; D=(C_itq@R)>=0; Q=((qC_itq@R)>=0)[0]
        itqD[s]=D; itqQ[s]=Q; itqdist[s]=np.count_nonzero(D!=Q[None,:],axis=1).astype(np.int16)

    rows=[]
    for tr in range(N_NUISANCE):
        seed=adapter.v1.stable_archive_seed(lexical_ordinal,tr); priority=np.random.default_rng(seed+99).random(N)
        f0=metrics3(rank_float(f0_scores,priority)[:TOPK],gold_rows)
        fc=metrics3(rank_float(fc_scores,priority)[:TOPK],gold_rows)
        sg=metrics3(rank_hamming(sign_dist,priority)[:TOPK],gold_rows)
        for s in ITQ_SEEDS:
            iq=metrics3(rank_hamming(itqdist[s],priority)[:TOPK],gold_rows)
            rows.append({'question_id':qid,'question_type':qtype,'N_archive':N,'gold_count':len(gold_rows),'trial':tr,'itq_seed':s,
              'float96_uncentered_any_r3':f0[0],'float96_uncentered_all_r3':f0[1],'float96_uncentered_fractional_r3':f0[2],
              'float96_centered_any_r3':fc[0],'float96_centered_all_r3':fc[1],'float96_centered_fractional_r3':fc[2],
              'sign96_centered_any_r3':sg[0],'sign96_centered_all_r3':sg[1],'sign96_centered_fractional_r3':sg[2],
              'itq96_centered_any_r3':iq[0],'itq96_centered_all_r3':iq[1],'itq96_centered_fractional_r3':iq[2]})

    same={'question_id':qid,'N_archive':N,'archive_float_vs_sign_max_abs_diff':archive_fs,'archive_float_vs_itq_max_abs_diff':archive_fi,'archive_sign_vs_itq_max_abs_diff':archive_si,'query_float_vs_sign_max_abs_diff':query_fs,'query_float_vs_itq_max_abs_diff':query_fi,'query_sign_vs_itq_max_abs_diff':query_si,'overall_max_abs_diff':same_max,'status':'PASS' if same_max<=1e-12 else 'FAIL'}
    collisions=[]; ties=[]; distances=[]
    col,tie,dis,sign_packed=bit_collision_tie('SIGN96_CENTERED',None,signD,signQ,sign_dist,qid,gold_rows); collisions.append(col);ties.append(tie);distances.append(dis)
    itq_packed=[]; itq_qpacked=[]
    rankgeom=[]
    for s in ITQ_SEEDS:
        col,tie,dis,pk=bit_collision_tie('ITQ96_CENTERED',s,itqD[s],itqQ[s],itqdist[s],qid,gold_rows); collisions.append(col);ties.append(tie);distances.append(dis)
        itq_packed.append(pk); itq_qpacked.append(np.packbits(itqQ[s],bitorder='big'))
        rho=float(spearmanr(sign_dist,itqdist[s]).statistic)
        rankgeom.append({'question_id':qid,'itq_seed':s,'N_archive':N,'spearman_sign_hamming_vs_itq_hamming':rho,'sign_distance_mean':float(sign_dist.mean()),'itq_distance_mean':float(itqdist[s].mean())})
    g=np.asarray(sorted(gold_rows),dtype=int); mask=np.ones(N,dtype=bool); mask[g]=False
    for method,scores in [('FLOAT96_UNCENTERED',f0_scores),('FLOAT96_CENTERED',fc_scores)]:
        gs=scores[g]; ns=scores[mask]
        distances.append({'question_id':qid,'geometry':'COSINE','method':method,'itq_seed':None,'gold_mean':float(gs.mean()),'gold_median':float(np.median(gs)),'non_gold_mean':float(ns.mean()),'non_gold_median':float(np.median(ns)),'nearest_gold':float(gs.max()),'nearest_non_gold':float(ns.max()),'separation_non_gold_minus_gold_mean':float(ns.mean()-gs.mean()),'gold_minus_non_gold_mean':float(gs.mean()-ns.mean())})
    packed={'sign_doc':sign_packed,'sign_query':np.packbits(signQ,bitorder='big'),'itq_doc':np.stack(itq_packed,axis=0),'itq_query':np.stack(itq_qpacked,axis=0),'gold_rows':np.asarray(sorted(gold_rows),dtype=np.int32),'N_archive':N}
    bit_sums={'sign':signD.sum(axis=0).astype(np.int64),'itq':np.stack([itqD[s].sum(axis=0).astype(np.int64) for s in ITQ_SEEDS],axis=0),'N_archive':N}
    geometry={'question_id':qid,'N_archive':N,'word_columns':int(Xw.shape[1]),'char_columns':int(Xc.shape[1]),'combined_columns':int(Z.shape[1]),'base_rep_fit_seconds':base_fit_s,'svd96_fit_seconds':svd_fit_s,'itq96_fit_seconds_5seeds':itq_fit_s,'query_transform_seconds':query_fit_s,'centered_doc_norm_min':float(np.linalg.norm(C_float,axis=1).min()),'centered_doc_norm_max':float(np.linalg.norm(C_float,axis=1).max()),'centered_query_norm':float(np.linalg.norm(qC_float))}
    obj={'question_id':qid,'rows':rows,'same':same,'collisions':collisions,'ties':ties,'distances':distances,'rankgeom':rankgeom,'packed':packed,'bit_sums':bit_sums,'geometry':geometry}
    tmp=cp.with_suffix('.tmp'); tmp.write_bytes(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL)); os.replace(tmp,cp)
    return {'question_id':qid,'cached':False,'elapsed_s':base_fit_s+svd_fit_s+itq_fit_s+query_fit_s}


def metric_block(df,prefix):
    return {'ANY_R3':float(df[f'{prefix}_any_r3'].mean()),'ALL_R3':float(df[f'{prefix}_all_r3'].mean()),'Fractional_R3':float(df[f'{prefix}_fractional_r3'].mean())}


def decide(Gpp):
    if Gpp < -1.0: return DECISION_BANDS['CASE_D']['verdict']
    if abs(Gpp)<=1.0: return DECISION_BANDS['CASE_A']['verdict']
    if Gpp<5.0: return DECISION_BANDS['CASE_B']['verdict']
    return DECISION_BANDS['CASE_C']['verdict']


def q_wtl(q,a,b,label):
    d=(q[a]-q[b])*100.0; eps=1e-12
    wins=d>eps; losses=d<-eps; ties=~(wins|losses)
    return {'comparison':label,'win_count':int(wins.sum()),'tie_count':int(ties.sum()),'loss_count':int(losses.sum()),'mean_win_magnitude_pp':float(d[wins].mean()) if wins.any() else 0.0,'mean_loss_magnitude_pp':float((-d[losses]).mean()) if losses.any() else 0.0,'median_paired_gap_pp':float(np.median(d))}


def summarize_diag(df,method_cols,filename,out):
    df.to_csv(out/filename,index=False)


def finalize(args,seal,script_path:Path):
    out=args.outdir; geom=pd.read_csv(args.workdir/'primary_geometry.csv')
    caches=sorted(args.cachedir.glob('*.pkl'))
    if len(caches)!=EXPECTED_PRIMARY: raise RuntimeError(f'Need 470 caches, got {len(caches)}')
    objs=[pickle.loads(p.read_bytes()) for p in caches]
    trial=pd.DataFrame([r for o in objs for r in o['rows']])
    expected=EXPECTED_PRIMARY*N_NUISANCE*len(ITQ_SEEDS)
    if len(trial)!=expected: raise RuntimeError(f'trial rows {len(trial)} != {expected}')
    trial=trial.merge(geom[['question_id','reuse_count','reuse_tertile','archive_quartile','gold_stratum']],on='question_id',validate='many_to_one')
    trial.to_csv(out/'V52_T4C2_trial_results.csv',index=False)

    prefixes={'FLOAT96_UNCENTERED':'float96_uncentered','FLOAT96_CENTERED':'float96_centered','SIGN96_CENTERED':'sign96_centered','ITQ96_CENTERED':'itq96_centered'}
    agg={m:metric_block(trial,p) for m,p in prefixes.items()}
    adf=pd.DataFrame([{'method':m,**agg[m]} for m in METHODS]); adf.to_csv(out/'V52_T4C2_aggregate.csv',index=False)
    repro=[]; repro_bad=0
    for m in ['FLOAT96_UNCENTERED','SIGN96_CENTERED','ITQ96_CENTERED']:
        for met,expectedv in EXPECTED_T4C1[m].items():
            observed=agg[m][met]; d=observed-expectedv; bad=abs(d)>TOL; repro_bad+=int(bad)
            repro.append({'method':m,'metric':met,'expected_frozen':expectedv,'observed_4c2':observed,'difference':d,'status':'FAIL' if bad else 'PASS'})
    reprodf=pd.DataFrame(repro); reprodf.to_csv(out/'V52_T4C2_TASK4C1_REPRODUCTION.csv',index=False)
    if repro_bad: raise RuntimeError(f'[BUG] Task4C1 reproduction mismatches={repro_bad}; do not interpret 4C2')

    qkeys=['question_id','question_type','N_archive','gold_count','reuse_count','reuse_tertile','archive_quartile','gold_stratum']
    qagg={}
    for p in prefixes.values():
        for met in ['any_r3','all_r3','fractional_r3']: qagg[f'{p}_{met}']=(f'{p}_{met}','mean')
    q=trial.groupby(qkeys,as_index=False).agg(**qagg)
    q['sign_minus_centered_float_fractional_pp']=(q.sign96_centered_fractional_r3-q.float96_centered_fractional_r3)*100
    q['centered_minus_uncentered_float_fractional_pp']=(q.float96_centered_fractional_r3-q.float96_uncentered_fractional_r3)*100
    q.to_csv(out/'V52_T4C2_question_level.csv',index=False)

    cent=[]
    for met in ['Fractional_R3','ANY_R3','ALL_R3']:
        f0=agg['FLOAT96_UNCENTERED'][met]; fc=agg['FLOAT96_CENTERED'][met]
        cent.append({'metric':met,'FLOAT96_UNCENTERED':f0,'FLOAT96_CENTERED':fc,'centered_minus_uncentered_pp':(fc-f0)*100})
    pd.DataFrame(cent).to_csv(out/'V52_T4C2_centering_effect.csv',index=False)

    same=pd.DataFrame([o['same'] for o in objs]); same.to_csv(out/'V52_T4C2_same_input_proof.csv',index=False)
    same_max=float(same.overall_max_abs_diff.max())
    if same_max>1e-12 or not (same.status=='PASS').all(): raise RuntimeError('[BUG — NOT A CLEAN GEOMETRY ABLATION]')

    # Pooled per-bit occupancy. Local coordinate systems are comparable only by bit index under same construction; no cross-question code collision pooling.
    totalN=sum(int(o['bit_sums']['N_archive']) for o in objs)
    sign_sum=np.sum([o['bit_sums']['sign'] for o in objs],axis=0)
    itq_sum=np.sum([o['bit_sums']['itq'] for o in objs],axis=0)
    bitrows=[]
    def add_bits(method,seed,fracs):
        summary={'mean_occupancy':float(np.mean(fracs)),'min_occupancy':float(np.min(fracs)),'max_occupancy':float(np.max(fracs)),'dead_constant_bit_count':int(np.sum((fracs==0)|(fracs==1))),'mean_abs_deviation_from_0_5':float(np.mean(np.abs(fracs-.5)))}
        for j,v in enumerate(fracs): bitrows.append({'method':method,'itq_seed':seed,'bit_index':j,'positive_fraction':float(v),**summary})
    add_bits('SIGN96_CENTERED',None,sign_sum/totalN)
    for i,s in enumerate(ITQ_SEEDS): add_bits('ITQ96_CENTERED',s,itq_sum[i]/totalN)
    mean_seed=(itq_sum/totalN).mean(axis=0); add_bits('ITQ96_CENTERED_SEED_AVERAGE','MEAN',mean_seed)
    bitdf=pd.DataFrame(bitrows); bitdf.to_csv(out/'V52_T4C2_bit_balance.csv',index=False)

    coll=pd.DataFrame([r for o in objs for r in o['collisions']]);
    cs=[]
    for (m,s),x in coll.groupby(['method','itq_seed'],dropna=False):
        cs.append({'question_id':'__SUMMARY__','method':m,'itq_seed':s,'N_archive':int(x.N_archive.sum()),'unique_document_codes':np.nan,'unique_document_code_fraction':float(x.unique_document_code_fraction.mean()),'duplicate_code_fraction':float(x.duplicate_code_fraction.mean()),'largest_collision_bucket':int(x.largest_collision_bucket.max()),'query_exact_code_match_count':float(x.query_exact_code_match_count.mean()),'query_exact_code_match_fraction':float(x.query_exact_code_match_fraction.mean())})
    coll=pd.concat([coll,pd.DataFrame(cs)],ignore_index=True); coll.to_csv(out/'V52_T4C2_collision_diagnostics.csv',index=False)

    ties=pd.DataFrame([r for o in objs for r in o['ties']]); ts=[]
    for (m,s),x in ties.groupby(['method','itq_seed'],dropna=False):
        ts.append({'question_id':'__SUMMARY__','method':m,'itq_seed':s,'N_archive':int(x.N_archive.sum()),'min_hamming_distance':float(x.min_hamming_distance.mean()),'candidates_at_min_distance':float(x.candidates_at_min_distance.mean()),'top3_boundary_distance':float(x.top3_boundary_distance.mean()),'candidates_at_top3_boundary_distance':float(x.candidates_at_top3_boundary_distance.mean()),'slots_remaining_at_boundary':float(x.slots_remaining_at_boundary.mean()),'top3_boundary_tie':float(x.top3_boundary_tie.mean()),'boundary_tie_size_median':float(x.candidates_at_top3_boundary_distance.median()),'boundary_tie_size_p90':float(x.candidates_at_top3_boundary_distance.quantile(.9)),'boundary_tie_size_max':int(x.candidates_at_top3_boundary_distance.max())})
    ties=pd.concat([ties,pd.DataFrame(ts)],ignore_index=True); ties.to_csv(out/'V52_T4C2_tie_diagnostics.csv',index=False)

    dist=pd.DataFrame([r for o in objs for r in o['distances']]); ds=[]
    for (g,m,s),x in dist.groupby(['geometry','method','itq_seed'],dropna=False):
        ds.append({'question_id':'__SUMMARY__','geometry':g,'method':m,'itq_seed':s,'gold_mean':float(x.gold_mean.mean()),'gold_median':float(x.gold_median.median()),'non_gold_mean':float(x.non_gold_mean.mean()),'non_gold_median':float(x.non_gold_median.median()),'nearest_gold':float(x.nearest_gold.mean()),'nearest_non_gold':float(x.nearest_non_gold.mean()),'separation_non_gold_minus_gold_mean':float(x.separation_non_gold_minus_gold_mean.mean()),'gold_minus_non_gold_mean':float(x.gold_minus_non_gold_mean.mean()) if 'gold_minus_non_gold_mean' in x else np.nan})
    dist=pd.concat([dist,pd.DataFrame(ds)],ignore_index=True); dist.to_csv(out/'V52_T4C2_distance_geometry.csv',index=False)

    rg=pd.DataFrame([r for o in objs for r in o['rankgeom']]); rs=[]
    for s,x in rg.groupby('itq_seed'):
        rs.append({'question_id':'__SUMMARY__','itq_seed':s,'N_archive':int(x.N_archive.sum()),'spearman_sign_hamming_vs_itq_hamming':float(x.spearman_sign_hamming_vs_itq_hamming.mean()),'sign_distance_mean':float(x.sign_distance_mean.mean()),'itq_distance_mean':float(x.itq_distance_mean.mean()),'spearman_median':float(x.spearman_sign_hamming_vs_itq_hamming.median()),'spearman_min':float(x.spearman_sign_hamming_vs_itq_hamming.min()),'spearman_max':float(x.spearman_sign_hamming_vs_itq_hamming.max())})
    rg=pd.concat([rg,pd.DataFrame(rs)],ignore_index=True); rg.to_csv(out/'V52_T4C2_rank_geometry.csv',index=False)

    # Frozen strata, primary fractional plus secondary metric gaps, descriptive only.
    def strata(col,order,name):
        rows=[]
        for g in order:
            x=q[q[col]==g]
            rec={col:g,'n_questions':len(x)}
            for met in ['fractional_r3','any_r3','all_r3']:
                rec[f'sign_minus_centered_float_{met}_pp']=float((x[f'sign96_centered_{met}']-x[f'float96_centered_{met}']).mean()*100)
                rec[f'centered_minus_uncentered_float_{met}_pp']=float((x[f'float96_centered_{met}']-x[f'float96_uncentered_{met}']).mean()*100)
            rows.append(rec)
        pd.DataFrame(rows).to_csv(out/name,index=False)
    strata('question_type',QUESTION_TYPES,'V52_T4C2_question_type.csv')
    strata('gold_stratum',['one-gold','multi-gold'],'V52_T4C2_gold_cardinality.csv')
    strata('archive_quartile',['Q1','Q2','Q3','Q4'],'V52_T4C2_archive_size.csv')
    strata('reuse_tertile',['low','medium','high'],'V52_T4C2_reuse.csv')

    wtl=pd.DataFrame([q_wtl(q,'sign96_centered_fractional_r3','float96_centered_fractional_r3','SIGN96_CENTERED vs FLOAT96_CENTERED'),q_wtl(q,'float96_centered_fractional_r3','float96_uncentered_fractional_r3','FLOAT96_CENTERED vs FLOAT96_UNCENTERED')])
    wtl.to_csv(out/'V52_T4C2_WIN_TIE_LOSS.csv',index=False)

    # Packed codes: one NPZ per question in a zip, sufficient to independently recompute bit/collision/tie/distance geometry.
    codezip=out/'V52_T4C2_BINARY_GEOMETRY.zip'
    with zipfile.ZipFile(codezip,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as zf:
        manifest=[]
        for o in objs:
            p=o['packed']; bio=io.BytesIO(); np.savez_compressed(bio,sign_doc_packed=p['sign_doc'],sign_query_packed=p['sign_query'],itq_doc_packed=p['itq_doc'],itq_query_packed=p['itq_query'],itq_seeds=np.asarray(ITQ_SEEDS,dtype=np.int32),gold_rows=p['gold_rows'],N_archive=np.asarray([p['N_archive']],dtype=np.int32),bitorder=np.asarray(['big']))
            b=bio.getvalue(); fn=f"codes/{o['question_id']}.npz"; zf.writestr(fn,b); manifest.append({'question_id':o['question_id'],'file':fn,'sha256':hashlib.sha256(b).hexdigest(),'N_archive':int(p['N_archive'])})
        zf.writestr('MANIFEST.json',json.dumps({'task':TASK,'itq_seeds':ITQ_SEEDS,'bitorder':'big','files':manifest},indent=2).encode())

    fg=pd.DataFrame([o['geometry'] for o in objs]); fg.to_csv(out/'V52_T4C2_feature_geometry.csv',index=False)
    Gpp=(agg['SIGN96_CENTERED']['Fractional_R3']-agg['FLOAT96_CENTERED']['Fractional_R3'])*100
    verdict=decide(Gpp)
    gaps={
      'Fc_minus_F0_pp':(agg['FLOAT96_CENTERED']['Fractional_R3']-agg['FLOAT96_UNCENTERED']['Fractional_R3'])*100,
      'S_minus_Fc_pp':Gpp,
      'I_minus_Fc_pp':(agg['ITQ96_CENTERED']['Fractional_R3']-agg['FLOAT96_CENTERED']['Fractional_R3'])*100,
      'S_minus_I_pp':(agg['SIGN96_CENTERED']['Fractional_R3']-agg['ITQ96_CENTERED']['Fractional_R3'])*100,
    }
    # Sanity checks derived from actual outputs.
    sanity=[
      {'check':'dataset_sha256','observed':sha256_file(args.dataset),'expected':EXPECTED_DATASET_SHA,'status':'PASS' if sha256_file(args.dataset)==EXPECTED_DATASET_SHA else 'FAIL'},
      {'check':'dataset_bytes','observed':args.dataset.stat().st_size,'expected':EXPECTED_DATASET_BYTES,'status':'PASS' if args.dataset.stat().st_size==EXPECTED_DATASET_BYTES else 'FAIL'},
      {'check':'primary_questions','observed':len(q),'expected':EXPECTED_PRIMARY,'status':'PASS' if len(q)==EXPECTED_PRIMARY else 'FAIL'},
      {'check':'trial_rows','observed':len(trial),'expected':expected,'status':'PASS' if len(trial)==expected else 'FAIL'},
      {'check':'duplicate_id_assert','observed':'PASS','expected':'PASS','status':'PASS'},
      {'check':'task4c1_reproduction','observed':f'{len(reprodf)-repro_bad}/{len(reprodf)} PASS','expected':'9/9 PASS','status':'PASS' if repro_bad==0 else 'FAIL'},
      {'check':'same_input_max_abs_diff','observed':same_max,'expected':'<=1e-12','status':'PASS' if same_max<=1e-12 else 'FAIL'},
      {'check':'centered_cosine_finite','observed':int(np.isfinite(trial.filter(like='float96_centered_').to_numpy()).all()),'expected':1,'status':'PASS' if np.isfinite(trial.filter(like='float96_centered_').to_numpy()).all() else 'FAIL'},
      {'check':'centered_vector_norms_positive','observed':float(fg.centered_doc_norm_min.min()),'expected':'>0','status':'PASS' if fg.centered_doc_norm_min.min()>0 and fg.centered_query_norm.min()>0 else 'FAIL'},
    ]
    sdf=pd.DataFrame(sanity); sdf.to_csv(out/'V52_T4C2_sanity_checks.csv',index=False)
    if (sdf.status!='PASS').any(): raise RuntimeError('[BUG] sanity gate failure')

    # Reports.
    def pct(x): return f'{100*x:.6f}%'
    wtls={r.comparison:r for r in wtl.itertuples(index=False)}
    report=f"""# V52 Task 4C2 — Centering / Sign-Geometry Diagnostic\n\n**VERDICT:** `{verdict}`\n\nFixed-benchmark paired estimands only; 470 shared-session connected questions. No population p-values, confidence intervals, superiority/equivalence/non-inferiority claims.\n\n## Primary quality\n\n| Method | ANY R@3 | ALL R@3 | Fractional R@3 |\n|---|---:|---:|---:|\n"""
    for m in METHODS: report+=f"| {m} | {pct(agg[m]['ANY_R3'])} | {pct(agg[m]['ALL_R3'])} | {pct(agg[m]['Fractional_R3'])} |\n"
    report+=f"""\n## Paired headline gaps\n\n- Fc - F0 = {gaps['Fc_minus_F0_pp']:+.6f} pp\n- S - Fc = {gaps['S_minus_Fc_pp']:+.6f} pp\n- I - Fc = {gaps['I_minus_Fc_pp']:+.6f} pp\n- S - I = {gaps['S_minus_I_pp']:+.6f} pp\n\nDecision variable G=S-Fc={Gpp:+.6f} pp, mapped without changing the frozen bands to **{verdict}**.\n\n## Protocol gates\n\n- Task 4C1 reproduction: 9/9 metric checks exact within 1e-12.\n- Same-input proof: max absolute difference = {same_max:.3e}.\n- Dataset SHA/bytes, adapters, Task4B/Task4C1 sources: PASS.\n- Duplicate-ID assertion: PASS.\n- Pre-run script SHA remains unchanged at finalization.\n\n## Geometry artifacts\n\nBit balance, collision, tie, gold/non-gold distance, continuous cosine separation, SIGN-vs-ITQ Spearman distance correlation, and packed binary codes are exported as separate reproducible artifacts.\n\n## Question-level robustness (Fractional R@3)\n\n- SIGN vs centered float: W/T/L = {wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].win_count}/{wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].tie_count}/{wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].loss_count}; median gap {wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].median_paired_gap_pp:+.6f} pp.\n- Centered vs uncentered float: W/T/L = {wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].win_count}/{wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].tie_count}/{wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].loss_count}; median gap {wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].median_paired_gap_pp:+.6f} pp.\n\n## Interpretation boundary\n\nThis is a controlled fixed-benchmark method comparison. It isolates the effect of archive-mean centering relative to the frozen uncentered continuous reference and asks whether a residual SIGN/Hamming gap remains. It does not establish population causality or cross-benchmark generalization.\n"""
    (out/'V52_T4C2_COMPUTE_REPORT.md').write_text(report,encoding='utf-8')

    # compact diagnostic summaries for handoff
    bsum=bitdf.groupby(['method','itq_seed'],dropna=False).first().reset_index()[['method','itq_seed','mean_occupancy','min_occupancy','max_occupancy','dead_constant_bit_count','mean_abs_deviation_from_0_5']]
    csum=coll[coll.question_id=='__SUMMARY__']; tsum=ties[ties.question_id=='__SUMMARY__']; rsum=rg[rg.question_id=='__SUMMARY__']
    def one_line(df,cols):
        if df.empty:return 'N/A'
        return '; '.join(', '.join(f'{c}={getattr(r,c)}' for c in cols) for r in df.itertuples(index=False))
    handoff=f"""==================================================\nHEAD RESEARCHER HANDOFF\n==================================================\nTASK:\nV52 Task 4C2 — Centering / Sign-Geometry Diagnostic\nVERDICT:\n{verdict}\nAUDIT/INPUT STATUS:\nPASS — frozen hashes, cohort, no-leakage static audit, Task4C1 reproduction, same-input proof all passed.\nFLOAT96_UNCENTERED:\nANY = {pct(agg['FLOAT96_UNCENTERED']['ANY_R3'])}\nALL = {pct(agg['FLOAT96_UNCENTERED']['ALL_R3'])}\nFractional = {pct(agg['FLOAT96_UNCENTERED']['Fractional_R3'])}\nFLOAT96_CENTERED:\nANY = {pct(agg['FLOAT96_CENTERED']['ANY_R3'])}\nALL = {pct(agg['FLOAT96_CENTERED']['ALL_R3'])}\nFractional = {pct(agg['FLOAT96_CENTERED']['Fractional_R3'])}\nSIGN96_CENTERED:\nANY = {pct(agg['SIGN96_CENTERED']['ANY_R3'])}\nALL = {pct(agg['SIGN96_CENTERED']['ALL_R3'])}\nFractional = {pct(agg['SIGN96_CENTERED']['Fractional_R3'])}\nITQ96_CENTERED:\nANY = {pct(agg['ITQ96_CENTERED']['ANY_R3'])}\nALL = {pct(agg['ITQ96_CENTERED']['ALL_R3'])}\nFractional = {pct(agg['ITQ96_CENTERED']['Fractional_R3'])}\nCENTERING EFFECT:\nFc - F0 = {gaps['Fc_minus_F0_pp']:+.6f} pp\nSIGN RESIDUAL:\nS - Fc = {gaps['S_minus_Fc_pp']:+.6f} pp\nITQ VS CENTERED FLOAT:\nI - Fc = {gaps['I_minus_Fc_pp']:+.6f} pp\nSIGN VS ITQ:\nS - I = {gaps['S_minus_I_pp']:+.6f} pp\nSAME INPUT PROOF:\nPASS; max absolute difference = {same_max:.3e}\nBIT BALANCE:\n{one_line(bsum,['method','itq_seed','mean_occupancy','min_occupancy','max_occupancy','dead_constant_bit_count','mean_abs_deviation_from_0_5'])}\nCOLLISIONS:\n{one_line(csum,['method','itq_seed','unique_document_code_fraction','duplicate_code_fraction','largest_collision_bucket','query_exact_code_match_fraction'])}\nTIES:\n{one_line(tsum,['method','itq_seed','candidates_at_min_distance','candidates_at_top3_boundary_distance','top3_boundary_tie'])}\nDISTANCE GEOMETRY:\nSee V52_T4C2_distance_geometry.csv (Hamming and cosine gold/non-gold separation).\nRANK GEOMETRY:\n{one_line(rsum,['itq_seed','spearman_sign_hamming_vs_itq_hamming','spearman_median'])}\nSIGN VS CENTERED FLOAT W/T/L:\n{wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].win_count}/{wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].tie_count}/{wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].loss_count}; mean win={wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].mean_win_magnitude_pp:.6f} pp; mean loss={wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].mean_loss_magnitude_pp:.6f} pp; median gap={wtls['SIGN96_CENTERED vs FLOAT96_CENTERED'].median_paired_gap_pp:+.6f} pp\nCENTERING W/T/L:\n{wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].win_count}/{wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].tie_count}/{wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].loss_count}; mean win={wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].mean_win_magnitude_pp:.6f} pp; mean loss={wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].mean_loss_magnitude_pp:.6f} pp; median gap={wtls['FLOAT96_CENTERED vs FLOAT96_UNCENTERED'].median_paired_gap_pp:+.6f} pp\nQUESTION TYPES:\nSee V52_T4C2_question_type.csv\nGOLD:\nSee V52_T4C2_gold_cardinality.csv\nARCHIVE SIZE:\nSee V52_T4C2_archive_size.csv\nREUSE:\nSee V52_T4C2_reuse.csv\nTASK 4C1 REPRODUCTION:\nPASS — 9/9 aggregate metric checks.\nDATASET SHA:\n{EXPECTED_DATASET_SHA}\nADAPTER V1 SHA:\n{EXPECTED_ADAPTER_V1_SHA}\nDUPLICATE-ID ASSERT:\nPASS\nPRE-RUN SEAL:\n{sha256_file(out/'V52_T4C2_PRE_RUN_SEAL.json')}\nPOST-RUN SCRIPT HASH MATCH:\nYES\nFALSIFICATION:\nThe apparent SIGN advantage was challenged by the exact centered continuous control. Frozen decision bands were applied to observed G without retuning.\nIMPORTANT CAVEATS:\nFixed benchmark only; 470 questions form one shared-session connected component; no population inference; no LoCoMo run; no rescue method run.\nFILES / DRIVE FOLDER:\nV52_TASK_4C2_CENTERING_GEOMETRY\nRECOMMENDED NEXT QUESTION:\nUse the binary-geometry diagnostics to determine whether the residual gap, if any, is associated with threshold-induced neighborhood reordering rather than mean-centering alone.\n==================================================\n\nNE DENEDİK?\nAynı 96 boyutlu temsili hiç değiştirmeden yalnız iki geometriyi ayırdık: önce arşiv ortalamasını çıkarıp sürekli cosine araması yaptık, sonra aynı centered girdiyi SIGN/Hamming ve frozen ITQ ile karşılaştırdık.\nCENTERING NE KADARINI AÇIKLADI?\nFLOAT96_CENTERED - FLOAT96_UNCENTERED Fractional R@3 = {gaps['Fc_minus_F0_pp']:+.6f} puan.\nSIGN/HAMMING'İN KENDİ AVANTAJI KALDI MI?\nSIGN96_CENTERED - FLOAT96_CENTERED = {gaps['S_minus_Fc_pp']:+.6f} puan; frozen karar bandı sonucu {verdict}.\nITQ NEDEN GERİDE GÖRÜNÜYOR?\nBu task ITQ'nun nedenini nedensel olarak kanıtlamıyor; aynı centered girdiden sonra learned rotation + threshold ile oluşan Hamming komşuluklarının SIGN'dan ne kadar farklılaştığını distance/rank diagnostics ile ölçüyor.\nBU SONUÇ GERÇEKTEN YENİ BİR ARAŞTIRMA DALI MI, YOKSA REPRESENTATION PREPROCESSING ETKİSİ Mİ?\nKarar G ve centering etkisine göre ayrıştırıldı; centering tek başına açıklıyorsa yeni SIGN mekanizması iddiası zayıflar, residual büyük kalıyorsa geometri mekanizması ayrıca incelenebilir.\nBAŞ ARAŞTIRMACININ SONRAKİ KARARI NE OLMALI?\nÖnce bu frozen 4C2 paketini audit ettirmek; ancak audit sonrası residual geometri mekanizmasını tek teknik hipotez olarak test etmek. LoCoMo veya 4C3 bu compute sohbetinde başlatılmamalı.\n"""
    (out/'V52_T4C2_HEAD_RESEARCHER_HANDOFF.txt').write_text(handoff,encoding='utf-8')

    # Post-run manifest and all-output zip. Script must be byte-identical to seal.
    final_script_sha=sha256_file(script_path)
    if final_script_sha!=seal['script_sha256']: raise RuntimeError('[PROTOCOL SEAL FAILURE] pre-run script SHA != final script SHA')
    shutil.copy2(script_path,out/'v52_t4c2_centering_geometry.py')
    required=['V52_T4C2_PRE_RUN_SEAL.json','V52_T4C2_trial_results.csv','V52_T4C2_question_level.csv','V52_T4C2_aggregate.csv','V52_T4C2_centering_effect.csv','V52_T4C2_same_input_proof.csv','V52_T4C2_bit_balance.csv','V52_T4C2_collision_diagnostics.csv','V52_T4C2_tie_diagnostics.csv','V52_T4C2_distance_geometry.csv','V52_T4C2_rank_geometry.csv','V52_T4C2_question_type.csv','V52_T4C2_gold_cardinality.csv','V52_T4C2_archive_size.csv','V52_T4C2_reuse.csv','V52_T4C2_sanity_checks.csv','V52_T4C2_leakage_audit.csv','v52_t4c2_centering_geometry.py','V52_T4C2_COMPUTE_REPORT.md','V52_T4C2_HEAD_RESEARCHER_HANDOFF.txt','V52_T4C2_BINARY_GEOMETRY.zip','V52_T4C2_TASK4C1_REPRODUCTION.csv','V52_T4C2_WIN_TIE_LOSS.csv','V52_T4C2_feature_geometry.csv','V52_T4C2_INPUT_CHECKS.json']
    missing=[f for f in required if not (out/f).exists()]
    if missing: raise RuntimeError('missing required outputs '+repr(missing))
    manifest={'task':TASK,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'verdict':verdict,'pre_run_seal_sha256':sha256_file(out/'V52_T4C2_PRE_RUN_SEAL.json'),'pre_run_script_sha256':seal['script_sha256'],'final_script_sha256':final_script_sha,'script_hash_match':True,'dataset_sha256':EXPECTED_DATASET_SHA,'same_input_max_abs_diff':same_max,'task4c1_reproduction':'PASS','gaps_pp':gaps,'output_hashes':{f:sha256_file(out/f) for f in required}}
    (out/'V52_T4C2_POST_RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    allzip=out/'V52_T4C2_ALL_OUTPUTS.zip'
    with zipfile.ZipFile(allzip,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as zf:
        for f in required+['V52_T4C2_POST_RUN_MANIFEST.json']:
            zf.write(out/f,arcname=f)
    print(json.dumps({'FINAL_VERDICT':verdict,'G_pp':Gpp,'gaps_pp':gaps,'same_input_max_abs_diff':same_max,'task4c1_reproduction':'PASS','post_manifest':str(out/'V52_T4C2_POST_RUN_MANIFEST.json'),'all_outputs':str(allzip)},indent=2,ensure_ascii=False),flush=True)


def run(args,script_path:Path):
    seal=load_seal(args,script_path)
    geom=pd.read_csv(args.workdir/'primary_geometry.csv')
    args.cachedir.mkdir(parents=True,exist_ok=True)
    tasks=[]
    for r in geom.itertuples(index=False):
        cp=args.cachedir/f'{r.question_id}.pkl'
        if not cp.exists(): tasks.append((str(args.itemsdir/f'{r.question_id}.json'),int(r.lexical_ordinal),str(args.adapter_v2),str(cp)))
    print(f'[RUN] cached={EXPECTED_PRIMARY-len(tasks)} pending={len(tasks)} workers={args.workers}',flush=True)
    if tasks:
        done=0
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs={ex.submit(evaluate_item,*t):t[0] for t in tasks}
            for fut in as_completed(futs):
                res=fut.result(); done+=1
                if done%5==0 or done==len(tasks): print(f'[PROGRESS] newly_completed={done}/{len(tasks)} qid={res["question_id"]}',flush=True)
    finalize(args,seal,script_path)


def parse_args():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dataset',type=Path,required=True); ap.add_argument('--adapter-v1',type=Path,required=True); ap.add_argument('--adapter-v2',type=Path,required=True)
    ap.add_argument('--task4b-script',type=Path,required=True); ap.add_argument('--task4c1-script',type=Path,required=True); ap.add_argument('--task4c1-trial',type=Path,required=True); ap.add_argument('--task4c1-qlevel',type=Path,required=True); ap.add_argument('--task4c1-aggregate',type=Path,required=True); ap.add_argument('--task4c1-preseal',type=Path,required=True); ap.add_argument('--task4c1-postmanifest',type=Path,required=True); ap.add_argument('--prereg',type=Path,required=True); ap.add_argument('--method-spec',type=Path,required=True)
    ap.add_argument('--workdir',type=Path,required=True); ap.add_argument('--outdir',type=Path,required=True); ap.add_argument('--workers',type=int,default=4); ap.add_argument('--prepare-only',action='store_true'); ap.add_argument('--validate-only',action='store_true')
    a=ap.parse_args(); a.itemsdir=a.workdir/'items'; a.cachedir=a.workdir/'cache'; return a


def main():
    args=parse_args(); script_path=Path(__file__).resolve()
    if args.validate_only:
        checks=verify_frozen_files(args,script_path); leak=static_leakage_audit(args.adapter_v1,args.adapter_v2,script_path)
        print(json.dumps({'hash_bindings':'PASS','script_sha256':checks['new_task4c2_script_sha256'],'static_leakage_blocking':int(leak.blocking.sum()),'methods':METHODS,'decision_bands':DECISION_BANDS},indent=2,ensure_ascii=False)); return
    if args.prepare_only: create_seal(args,script_path)
    else: run(args,script_path)

if __name__=='__main__': main()
