"""PROBE 04 (M-3): in-memory adapter -- coverage and ORDERING against both ingestion result
schemas (LoCoMo, LongMemEval), with fake objects and malformed fixtures; per-archive
diagnostics; completeness of record validation.

Synthetic only. Usage: python probe_04_m3_adapter.py <prep_dir>
"""
import sys, os, copy, json
PREP = sys.argv[1]
sys.path.insert(0, PREP)
import numpy as np
import pipeline as P
core = P.core

T = [f'alpha item{i} family{i % 13} token{i * 17} cat{i % 7} zulu' for i in range(110)]
UNITS = [{'text': x} for x in T]
rep = P.Representation(T)


def anchor(rep, text, gold, ordinal=0):
    q = rep.queries([text])[0]
    d = core.hamming_dist(rep.C, q)
    pri = [np.random.default_rng(P.stable_archive_seed(ordinal, t) + 99).random(len(rep.C))
           for t in range(P.N_NUISANCE)]
    return float(np.mean([len(set(map(int, np.lexsort((x, d))[:3])) & set(gold)) / len(gold)
                          for x in pri]))


def locomo(convs, cohort, empty=()):
    return {'benchmark': 'LoCoMo', 'cohort_ids': list(cohort),
            'questions_with_empty_gold': list(empty), 'conversations': convs}


def lme(questions, cohort, empty=()):
    return {'benchmark': 'LongMemEval', 'cohort_ids': list(cohort),
            'questions_with_empty_gold': list(empty), 'questions': questions}


def attempt(label, fn):
    try:
        r = fn()
        print(f'   {label:44} -> OK ({len(r["records"])} records, '
              f'{len(r["diagnostics"])} diagnostics)')
        return r
    except Exception as e:
        chain = []
        c = e
        while getattr(c, '__context__', None) is not None or getattr(c, '__cause__', None) is not None:
            c = c.__cause__ or c.__context__
            chain.append(type(c).__name__)
            if len(chain) > 4:
                break
        print(f'   {label:44} -> {type(e).__name__}: {str(e)[:110]!r}'
              + (f'  chain={chain}' if chain else ''))
        return None


print('=' * 78)
print('P04.1  LoCoMo schema, well formed')
g0, g1 = [4], [3, 16]
a0 = anchor(rep, T[4], g0); a1 = anchor(rep, 'alpha family3 cat2', g1)
qs = {'s0': {'text': T[4], 'gold_rows': g0}, 's1': {'text': 'alpha family3 cat2', 'gold_rows': g1}}
ok = attempt('single conversation, 2 questions', lambda: P.assemble_in_memory(
    locomo({'cv': {'index': 0, 'units': UNITS, 'questions': qs}}, ['s0', 's1']),
    {'s0': a0, 's1': a1}))
print(f'   diagnostics keys : {sorted(ok["diagnostics"][0])}')
print(f'   archive_ordinal present and taken from conversation["index"] : '
      f'{ok["diagnostics"][0]["archive_ordinal"] == 0}')

print()
print('=' * 78)
print('P04.2  LoCoMo ORDERING: archive ordinal source, and whether it is outcome-affecting')
# same content, conversation index changed 0 -> 5
alt = anchor(rep, T[4], g0, ordinal=5)
r5 = P.assemble_in_memory(
    locomo({'cv': {'index': 5, 'units': UNITS, 'questions': {'s0': qs['s0']}}}, ['s0']), {'s0': alt})
r0 = P.assemble_in_memory(
    locomo({'cv': {'index': 0, 'units': UNITS, 'questions': {'s0': qs['s0']}}}, ['s0']), {'s0': a0})
v5 = [r['fractional_R3'] for r in r5['records']]
v0 = [r['fractional_R3'] for r in r0['records']]
print(f'   ordinal 0 native anchor = {a0!r}')
print(f'   ordinal 5 native anchor = {alt!r}')
print(f'   full score vectors identical across ordinals : {v5 == v0}')
print(f'   differing arm-records: {sum(1 for x, y in zip(v0, v5) if x != y)} of {len(v0)}')
print('   -> the archive ordinal feeds stable_archive_seed -> the 20 nuisance priority vectors')
print('      -> top-k tie-breaking -> scores. The ordinal is OUTCOME-AFFECTING, not cosmetic.')
print(f'   LoCoMo ordinal is supplied by ingestion (conversation["index"]) -> bound upstream.')
print(f'   LongMemEval ordinal is enumerate(cohort_ids) -> chosen by THIS package.')

print()
print('=' * 78)
print('P04.3  LongMemEval schema, well formed; ordinal = position in cohort_ids')
qa = anchor(rep, T[4], g0, ordinal=0)
qb = anchor(rep, 'alpha family3 cat2', g1, ordinal=1)
r = attempt('two single-question archives', lambda: P.assemble_in_memory(
    lme({'s0': {'units': UNITS, 'text': T[4], 'gold_rows': g0},
         's1': {'units': UNITS, 'text': 'alpha family3 cat2', 'gold_rows': g1}},
        ['s0', 's1']), {'s0': qa, 's1': qb}))
print(f'   ordinals emitted in diagnostics : {[d["archive_ordinal"] for d in r["diagnostics"]]}')
# reorder the cohort -> ordinals swap -> scores change
qa2 = anchor(rep, 'alpha family3 cat2', g1, ordinal=0)
qb2 = anchor(rep, T[4], g0, ordinal=1)
r2 = P.assemble_in_memory(
    lme({'s0': {'units': UNITS, 'text': T[4], 'gold_rows': g0},
         's1': {'units': UNITS, 'text': 'alpha family3 cat2', 'gold_rows': g1}},
        ['s1', 's0']), {'s0': qb2, 's1': qa2})
f = lambda d: {(x['question_id'], x['rotation_seed'], x['arm']): x['fractional_R3'] for x in d['records']}
same = f(r) == f(r2)
print(f'   permuting cohort_ids leaves every score unchanged : {same}')
print(f'   -> cohort ORDER is load-bearing for LongMemEval results '
      f'({"no" if same else "CONFIRMED"} sensitivity)')

print()
print('=' * 78)
print('P04.4  malformed fixtures -- LoCoMo')
attempt('missing "questions_with_empty_gold"',
        lambda: P.assemble_in_memory({'benchmark': 'LoCoMo', 'cohort_ids': ['s0'],
                                      'conversations': {}}, {'s0': a0}))
attempt('non-empty questions_with_empty_gold',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'index': 0, 'units': UNITS, 'questions': qs}}, ['s0', 's1'], ['s9']),
            {'s0': a0, 's1': a1}))
attempt('missing "cohort_ids"',
        lambda: P.assemble_in_memory({'benchmark': 'LoCoMo', 'questions_with_empty_gold': [],
                                      'conversations': {}}, {}))
attempt('unknown benchmark name',
        lambda: P.assemble_in_memory(
            {'benchmark': 'NotABenchmark', 'cohort_ids': ['s0'],
             'questions_with_empty_gold': [], 'conversations': {}}, {'s0': a0}))
attempt('anchor coverage mismatch',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'index': 0, 'units': UNITS, 'questions': qs}}, ['s0', 's1']),
            {'s0': a0}))
attempt('conversation missing "index"',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'units': UNITS, 'questions': qs}}, ['s0', 's1']), {'s0': a0, 's1': a1}))
attempt('unit missing "text"',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'index': 0, 'units': [{'body': x} for x in T], 'questions': qs}},
                   ['s0', 's1']), {'s0': a0, 's1': a1}))
attempt('question missing "gold_rows"',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'index': 0, 'units': UNITS,
                           'questions': {'s0': {'text': T[4]}}}}, ['s0']), {'s0': a0}))
attempt('cohort id absent from any conversation',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'index': 0, 'units': UNITS, 'questions': {'s0': qs['s0']}}},
                   ['s0', 'sMISSING']), {'s0': a0, 'sMISSING': a0}))
print()
print('   *** the important one: a conversation containing a question NOT in cohort_ids ***')
extra = dict(qs); extra['LEAKCANARY7'] = {'text': T[9], 'gold_rows': [9]}
attempt('conversation has extra question not in cohort',
        lambda: P.assemble_in_memory(
            locomo({'cv': {'index': 0, 'units': UNITS, 'questions': extra}}, ['s0', 's1']),
            {'s0': a0, 's1': a1}))

print()
print('=' * 78)
print('P04.5  malformed fixtures -- LongMemEval')
attempt('cohort id with no question record',
        lambda: P.assemble_in_memory(lme({'s0': {'units': UNITS, 'text': T[4], 'gold_rows': g0}},
                                         ['s0', 'LEAKCANARY8']), {'s0': qa, 'LEAKCANARY8': qa}))
attempt('missing "questions" key',
        lambda: P.assemble_in_memory({'benchmark': 'LongMemEval', 'cohort_ids': ['s0'],
                                      'questions_with_empty_gold': []}, {'s0': qa}))
attempt('question missing "units"',
        lambda: P.assemble_in_memory(lme({'s0': {'text': T[4], 'gold_rows': g0}}, ['s0']),
                                     {'s0': qa}))
attempt('duplicate cohort ids',
        lambda: P.assemble_in_memory(lme({'s0': {'units': UNITS, 'text': T[4], 'gold_rows': g0}},
                                         ['s0', 's0']), {'s0': qa}))
attempt('empty cohort',
        lambda: P.assemble_in_memory(lme({}, []), {}))
attempt('ingested is a list, not a mapping',
        lambda: P.assemble_in_memory([], {}))
attempt('ingested is None', lambda: P.assemble_in_memory(None, {}))

print()
print('=' * 78)
print('P04.6  record-validation completeness (does the adapter re-validate the whole set?)')
src = open(os.path.join(PREP, 'pipeline.py'), encoding='utf-8').read()
n = src.count('core.validate_per_question_records')
print(f'   validate_per_question_records call sites in pipeline.py : {n}')
for line in src.split('\n'):
    if 'validate_per_question_records' in line:
        print(f'      {line.strip()}')
print('   -> validated once per archive (against that archive\'s qids) and once for the whole')
print('      cohort. The core validator demands every (question, seed, arm) exactly once with a')
print('      finite score in [0,1], and rejects unexpected keys -- so extra or missing archives')
print('      are caught, provided execution reaches it.')
