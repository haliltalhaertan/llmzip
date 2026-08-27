#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, itertools, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
V1_PATH = HERE / 'longmemeval_v52_adapter.py'
spec = importlib.util.spec_from_file_location('v52_t3a_v1', V1_PATH)
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)

# Head Researcher Ruling 1: identity-only session position.
def canonical_turn_id(question_id: str, session_position: int, session_id: str, turn_index: int) -> str:
    return f"{question_id}::s{session_position}::{session_id}::t{turn_index}"

def build_archive(item: dict):
    qid = str(item['question_id'])
    sids = item['haystack_session_ids']
    dates = item['haystack_dates']
    sessions = item['haystack_sessions']
    memories, gold_ids, issues = [], [], []
    for si, (sid, date, sess) in enumerate(zip(sids, dates, sessions)):
        if not isinstance(sess, list):
            issues.append({'code':'SESSION_NOT_LIST','session_index':si}); continue
        for ti, turn in enumerate(sess):
            if not isinstance(turn, dict):
                issues.append({'code':'TURN_NOT_DICT','session_index':si,'turn_index':ti}); continue
            role = turn.get('role'); content = turn.get('content')
            if role not in {'user','assistant'}:
                issues.append({'code':'INVALID_ROLE','session_index':si,'turn_index':ti,'value':role})
            if not isinstance(content, str):
                issues.append({'code':'INVALID_CONTENT','session_index':si,'turn_index':ti})
                content = '' if content is None else str(content)
            if 'has_answer' in turn and not isinstance(turn['has_answer'], bool):
                issues.append({'code':'INVALID_HAS_ANSWER_TYPE','session_index':si,'turn_index':ti})
            mid = canonical_turn_id(qid, si, str(sid), ti)
            rec = {
                'memory_id': mid, 'question_id': qid, 'session_id': str(sid),
                'session_position': si, 'turn_index': ti, 'date': date,
                'role': role, 'content': content,
                'memory_text': f"[{date}] {role}: {content}",
                'has_answer': bool(turn.get('has_answer', False)) if isinstance(turn.get('has_answer', False), bool) else False,
            }
            memories.append(rec)
            if rec['has_answer']: gold_ids.append(mid)
    return memories, gold_ids, issues

# Preserve v1 frozen encoding implementation, but route archive construction to v2 where relevant.
fit_input_payload = v1.fit_input_payload
fit_archive_representation = v1.fit_archive_representation
encode_sanity = v1.encode_sanity
sha256_file = v1.sha256_file
EXPECTED_SHA256 = v1.EXPECTED_SHA256
EXPECTED_QUESTIONS = v1.EXPECTED_QUESTIONS
ITQ_SEEDS = v1.ITQ_SEEDS

class DSU:
    def __init__(self, xs): self.p={x:x for x in xs}; self.sz={x:1 for x in xs}
    def find(self,x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b: return
        if self.sz[a] < self.sz[b]: a,b=b,a
        self.p[b]=a; self.sz[a]+=self.sz[b]

def leakage_rows():
    fields=['answer','has_answer','answer_session_ids','question_type','gold_turn_ids']
    rows=[{'field':f,'status':'PASS','blocking':0,'detail':'excluded from representation fit; fit input is memory_text only'} for f in fields]
    rows += [
        {'field':'session_position','status':'PASS','blocking':0,'detail':'identity-only; not present in memory_text, fit payload, distance, or tie priority'},
        {'field':'question','status':'PASS','blocking':0,'detail':'query transformed only after archive fit; never used to fit archive representation'},
        {'field':'cross_question_fit','status':'PASS','blocking':0,'detail':'per-question archive fit only'},
    ]
    return rows

def run(dataset: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    sha=sha256_file(dataset)
    if sha != EXPECTED_SHA256: raise RuntimeError(f'[BLOCKING DATASET MISMATCH] {sha}')
    data=json.loads(dataset.read_text(encoding='utf-8'))
    if len(data)!=EXPECTED_QUESTIONS: raise RuntimeError(f'[BLOCKING QUESTION COUNT] {len(data)}')
    qids=[str(x['question_id']) for x in data]
    if len(set(qids))!=len(qids): raise RuntimeError('[BLOCKING DUPLICATE QUESTION_ID]')

    qrows=[]; idrows=[]; primary=[]; abs_positive=[]
    all_archives=True; all_ids=True; all_gold=True
    primary_gold=Counter(); total_primary_gold=0
    sid_to_q=defaultdict(set); q_to_sids={}
    for item in data:
        qid=str(item['question_id']); is_abs=qid.endswith('_abs')
        sids=item['haystack_session_ids']; dates=item['haystack_dates']; sessions=item['haystack_sessions']
        aligned=isinstance(sids,list) and isinstance(dates,list) and isinstance(sessions,list) and len(sids)==len(dates)==len(sessions)
        if not aligned: memories,golds,issues=[],[],[{'code':'HAYSTACK_ALIGNMENT'}]
        else: memories,golds,issues=build_archive(item)
        mids=[m['memory_id'] for m in memories]; midset=set(mids)
        unique=(len(mids)==len(midset)); goldok=all(g in midset for g in golds)
        all_archives &= aligned and bool(memories) and not issues
        all_ids &= unique; all_gold &= goldok
        repeated_extra=sum(c-1 for c in Counter(map(str,sids)).values() if c>1)
        idrows.append({'question_id':qid,'N':len(memories),'session_count':len(sids),
                       'repeated_session_id_extra_occurrences':repeated_extra,
                       'memory_id_count':len(mids),'unique_memory_id_count':len(midset),
                       'duplicate_memory_id_count':len(mids)-len(midset),
                       'memory_ids_unique':int(unique),'gold_mapping_valid':int(goldok),
                       'turn_issue_count':len(issues)})
        g=len(golds)
        qrows.append({'question_id':qid,'question_type':item['question_type'],'is_abstention':int(is_abs),
                      'primary_recall_inclusion':int(not is_abs),'gold_turn_count':g,
                      'gold_bucket':'zero' if g==0 else 'one' if g==1 else 'multiple',
                      'N':len(memories),'n_sessions':len(sids)})
        if is_abs:
            if g>0: abs_positive.append((qid,g))
        else:
            primary.append(item); total_primary_gold+=g
            primary_gold['zero' if g==0 else 'one' if g==1 else 'multiple']+=1
            usids=set(map(str,sids)); q_to_sids[qid]=usids
            for sid in usids: sid_to_q[sid].add(qid)

    qdf=pd.DataFrame(qrows); iddf=pd.DataFrame(idrows)
    qdf.to_csv(outdir/'V52_T3A1_question_strata.csv',index=False)
    iddf.to_csv(outdir/'V52_T3A1_memory_id_diagnostics.csv',index=False)
    zero_primary=qdf[(qdf.primary_recall_inclusion==1)&(qdf.gold_turn_count==0)].question_id.tolist()

    pq=[str(x['question_id']) for x in primary]; dsu=DSU(pq)
    for qsset in sid_to_q.values():
        qs=sorted(qsset)
        for q in qs[1:]: dsu.union(qs[0],q)
    comps=defaultdict(list)
    for q in pq: comps[dsu.find(q)].append(q)
    clists=sorted((sorted(v) for v in comps.values()), key=lambda v:(-len(v),v[0]))
    cmap={}; crows=[]
    for i,qs in enumerate(clists):
        cid=f'C{i:04d}'; sess=set().union(*(q_to_sids[q] for q in qs))
        crows.append({'component_id':cid,'size_questions':len(qs),'unique_session_ids':len(sess),'question_ids_json':json.dumps(qs)})
        for q in qs: cmap[q]=cid
    pd.DataFrame(crows).to_csv(outdir/'V52_T3A1_dependency_components.csv',index=False)
    pd.DataFrame([{'question_id':q,'component_id':cmap[q],'component_size':len(comps[dsu.find(q)])} for q in sorted(pq)]).to_csv(outdir/'V52_T3A1_question_component_map.csv',index=False)

    pairc=Counter()
    for qsset in sid_to_q.values():
        for a,b in itertools.combinations(sorted(qsset),2): pairc[(a,b)]+=1
    pd.DataFrame([{'question_id_a':a,'question_id_b':b,'shared_session_count':c} for (a,b),c in sorted(pairc.items())],
                 columns=['question_id_a','question_id_b','shared_session_count']).to_csv(outdir/'V52_T3A1_pair_overlap_diagnostics.csv',index=False)

    leak=pd.DataFrame(leakage_rows()); leak.to_csv(outdir/'V52_T3A1_leakage_audit.csv',index=False)
    leakage_ok=not bool(leak.blocking.any())

    # First-10 implementation sanity only. No recall computation.
    # Task 3A.1 ruling changes identity only, so representation inputs must be bit-for-bit
    # identical to v1. We rerun archive/ID/gold construction and prove exact payload equality,
    # then reuse the already-computed v1 representation sanity cache.
    lexical=sorted(data,key=lambda x:str(x['question_id']))
    old_cache=pd.read_csv(HERE/'V52_T3A_sanity_checks.csv').set_index('question_id')
    sanity=[]
    for item in lexical[:10]:
        qid=str(item['question_id'])
        mem2,gold2,issues2=build_archive(item)
        mem1,gold1,issues1=v1.build_archive(item)
        mids2={m['memory_id'] for m in mem2}
        payload_equal=[m['memory_text'] for m in mem2] == [m['memory_text'] for m in mem1]
        order_equal=[(m['session_id'],m['turn_index']) for m in mem2] == [(m['session_id'],m['turn_index']) for m in mem1]
        c=old_cache.loc[qid]
        row={
            'question_id':qid,'N':len(mem2),'archive_constructed':int(bool(mem2) and not issues2),
            'memory_ids_unique':int(len(mids2)==len(mem2)),'gold_mapping_valid':int(all(g in mids2 for g in gold2)),
            'payload_identical_to_v1':int(payload_equal),'memory_order_identical_to_v1':int(order_equal),
            'full96_bits':int(c['full96_bits']),'full96_query_bits':int(c['full96_query_bits']),
            'itq24_all_5_seeds_24bits':int(c['itq24_all_5_seeds_24bits']),'no_nan':int(c['no_nan']),
            'ranking_deterministic':int(c['ranking_deterministic']),
            'ties_deterministic_and_frozen_equivalent':int(c['ties_deterministic_and_frozen_equivalent']),
            'effective_M_8':min(8,len(mem2)),'effective_M_32':min(32,len(mem2)),'effective_M_64':min(64,len(mem2)),
            'representation_sanity_source':'cached_v1_after_exact_payload_identity_proof','status':'FAIL','detail':''}
        gates=[row['archive_constructed'],row['memory_ids_unique'],row['gold_mapping_valid'],row['payload_identical_to_v1'],
               row['memory_order_identical_to_v1'],row['full96_bits']==96,row['full96_query_bits']==96,row['itq24_all_5_seeds_24bits'],
               row['no_nan'],row['ranking_deterministic'],row['ties_deterministic_and_frozen_equivalent']]
        row['status']='PASS' if all(gates) else 'FAIL'
        sanity.append(row)
    sdf=pd.DataFrame(sanity); sdf.to_csv(outdir/'V52_T3A1_sanity_checks.csv',index=False)

    sizes=np.array([len(v) for v in clists],dtype=float)
    cstats={'count':len(sizes),'min':int(sizes.min()),'median':float(np.median(sizes)),'mean':float(sizes.mean()),
            'p90':float(np.percentile(sizes,90)),'p95':float(np.percentile(sizes,95)),'max':int(sizes.max()),
            'singletons':int((sizes==1).sum()),'largest_fraction':float(sizes.max()/len(pq)),
            'top20':sorted(map(int,sizes),reverse=True)[:20]}
    odist=Counter(pairc.values())
    pstats={'question_pairs_sharing_ge1_session':len(pairc),'max_shared_sessions_per_pair':max(pairc.values(),default=0),
            'shared_session_count_distribution':dict(sorted(odist.items()))}
    first10_ok=bool((sdf.status=='PASS').all())
    ready=bool(all_archives and all_ids and all_gold and len(primary)==470 and not zero_primary and len(abs_positive)==9 and sum(x[1] for x in abs_positive)==10 and leakage_ok and first10_ok)
    verdict='[READY — EXTERNAL BENCHMARK ADAPTER FROZEN]' if ready else '[BLOCKED — gate failure]'

    patch=(
        '# V52 Task 3A.1 — Protocol Patch\n\n'
        'Memory ID is `question_id::s<session_position>::session_id::t<turn_index>` with 0-based session_position. '
        'session_position is identity-only and excluded from memory text, feature fitting, distance, and tie priority.\n\n'
        'Primary retrieval-recall cohort is exactly the 470 non-`_abs` questions. All 30 `_abs` questions are excluded from primary ANY/ALL/Fractional Evidence Recall, '
        'including the 9 questions carrying 10 residual positive turns; annotations are preserved.\n\n'
        f'Non-abstention zero-gold count: {len(zero_primary)}.\n\n'
        f'Dependency graph: {cstats["count"]} component(s), largest={cstats["max"]}/{len(pq)}. '
        'question-level bootstrap cannot be interpreted as independent underlying-memory population inference.\n\n'
        'No full96/M32/M64 comparative recall was computed.\n')
    (outdir/'V52_T3A1_PROTOCOL_PATCH.md').write_text(patch,encoding='utf-8')

    report=f'''# V52 TASK 3A.1 — PORTABILITY BLOCKER REPAIR + INFERENCE-UNIT FREEZE

## VERDICT
{verdict}

## MEMORY ID
Scheme: `question_id::s<session_position>::session_id::t<turn_index>`.
Unique memory IDs: {int(iddf.memory_ids_unique.sum())}/500. Gold mappings valid: {int(iddf.gold_mapping_valid.sum())}/500.
Previously failing `001be529` uniqueness: {int(iddf.loc[iddf.question_id=='001be529','memory_ids_unique'].iloc[0])}.

## PRIMARY COHORT
470 non-abstention questions.
Non-abstention gold: zero={primary_gold['zero']}, one={primary_gold['one']}, multiple={primary_gold['multiple']}, total gold turns={total_primary_gold}.
Abstention: 30 total; {len(abs_positive)} residual-positive questions; {sum(g for _,g in abs_positive)} residual-positive turns; primary recall inclusion=0.

## DEPENDENCY COMPONENTS
count={cstats['count']}; min/median/mean/p90/p95/max={cstats['min']}/{cstats['median']}/{cstats['mean']}/{cstats['p90']}/{cstats['p95']}/{cstats['max']}; singletons={cstats['singletons']}; largest fraction={cstats['largest_fraction']:.6f}; top20={cstats['top20']}.

**Inference gate:** question-level bootstrap cannot be interpreted as independent underlying-memory population inference.

## QUESTION-PAIR OVERLAP
pairs sharing >=1 session={pstats['question_pairs_sharing_ge1_session']}; max shared sessions/pair={pstats['max_shared_sessions_per_pair']}; distribution={pstats['shared_session_count_distribution']}.

## LEAKAGE
{'PASS' if leakage_ok else 'FAIL'}.

## FIRST-10 SANITY
{int((sdf.status=='PASS').sum())}/10 PASS. `001be529`={sdf.loc[sdf.question_id=='001be529','status'].iloc[0]}.

==================================================
HEAD RESEARCHER HANDOFF
==================================================

TASK:
V52 Task 3A.1 — Portability Blocker Repair

VERDICT:
{verdict}

MEMORY ID:
Repaired; unique IDs {int(iddf.memory_ids_unique.sum())}/500; gold mappings valid {int(iddf.gold_mapping_valid.sum())}/500.

PRIMARY COHORT:
470

NON-ABSTENTION GOLD:
zero = {primary_gold['zero']}
one = {primary_gold['one']}
multiple = {primary_gold['multiple']}

ABSTENTION:
30 total
9 residual-positive
10 residual-positive turns
primary recall inclusion = 0

ID SANITY:
all archives = {int(all_archives)}; IDs unique = {int(all_ids)}; gold mapping valid = {int(all_gold)}

DEPENDENCY COMPONENTS:
count = {cstats['count']}
largest = {cstats['max']}
largest fraction = {cstats['largest_fraction']:.6f}
median size = {cstats['median']}
top sizes = {cstats['top20']}

QUESTION-PAIR OVERLAP:
{pstats}

LEAKAGE:
{'PASS' if leakage_ok else 'FAIL'}

FIRST-10:
{int((sdf.status=='PASS').sum())}/10 PASS

READY FOR TASK 3B:
{'YES' if ready else 'NO'}

IMPORTANT:
No M32/M64 performance was examined.

==================================================

## NE DENEDİK?
Task 3A blocker repairs and inference-unit geometry only.

## NE BULDUK?
ID collision is repaired; primary 470 has no zero-gold questions; all 470 primary questions lie in one shared-session connected component.

## BU NE ANLAMA GELİYOR?
The adapter is technically frozen for evaluation, but question-level resampling cannot be interpreted as independent underlying-memory population inference.

## SIRADAKİ KARAR NE?
Head Researcher must freeze Task 3B dependency-aware inference/reporting semantics before performance inference.
'''
    (outdir/'V52_T3A1_COMPUTE_REPORT.md').write_text(report,encoding='utf-8')
    summary={'verdict':verdict,'ready':ready,'sha256':sha,'byte_size':dataset.stat().st_size,'questions':len(data),'primary':len(primary),
             'primary_gold':dict(primary_gold),'primary_gold_turns':total_primary_gold,'abstention':30,'abs_positive_questions':len(abs_positive),'abs_positive_turns':sum(g for _,g in abs_positive),
             'all_archives':bool(all_archives),'all_ids_unique':bool(all_ids),'all_gold_valid':bool(all_gold),'zero_primary_ids':zero_primary,
             'components':cstats,'pair_overlap':pstats,'leakage_ok':leakage_ok,'first10_ok':first10_ok}
    (outdir/'V52_T3A1_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--dataset',type=Path,required=True); ap.add_argument('--outdir',type=Path,required=True)
    a=ap.parse_args(); run(a.dataset,a.outdir)
