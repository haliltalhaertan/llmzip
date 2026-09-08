"""PROBE 06: empty-cohort behaviour, native-anchor tolerance boundary, and the evidence
bearing on the README's five open integration obligations (classification only -- this probe
resolves nothing and runs no data).

Synthetic only. Usage: python probe_06_obligations_and_edges.py <prep_dir>
"""
import sys, os, re
PREP = sys.argv[1]
sys.path.insert(0, PREP)
import numpy as np
import pipeline as P
core = P.core
src = open(os.path.join(PREP, 'pipeline.py'), encoding='utf-8').read()

T = [f'alpha item{i} family{i % 13} token{i * 17} cat{i % 7} zulu' for i in range(110)]
U = [{'text': x} for x in T]
rep = P.Representation(T)

def anchor(text, gold, ordinal=0):
    d = core.hamming_dist(rep.C, rep.queries([text])[0])
    pri = [np.random.default_rng(P.stable_archive_seed(ordinal, t) + 99).random(110)
           for t in range(P.N_NUISANCE)]
    return float(np.mean([len(set(map(int, np.lexsort((x, d))[:3])) & set(gold)) / len(gold)
                          for x in pri]))

print('=' * 78)
print('P06.1  EMPTY COHORT -- does the adapter refuse, or silently succeed?')
for label, fx in (
        ('LongMemEval, empty cohort', {'benchmark': 'LongMemEval', 'cohort_ids': [],
                                       'questions_with_empty_gold': [], 'questions': {}}),
        ('LoCoMo, empty cohort', {'benchmark': 'LoCoMo', 'cohort_ids': [],
                                  'questions_with_empty_gold': [], 'conversations': {}}),
        ('LoCoMo, cohort empty but conversations present',
         {'benchmark': 'LoCoMo', 'cohort_ids': [], 'questions_with_empty_gold': [],
          'conversations': {'cv': {'index': 0, 'units': U, 'questions': {}}}})):
    try:
        r = P.assemble_in_memory(fx, {})
        print(f'   {label:48} -> RETURNED SUCCESSFULLY  '
              f'records={len(r["records"])} diagnostics={len(r["diagnostics"])}')
    except Exception as e:
        print(f'   {label:48} -> {type(e).__name__}: {str(e)[:60]}')
print('   -> an empty cohort produces a well-formed, EMPTY, apparently successful result.')
print('      core.validate_per_question_records([], []) has an empty expected set, so nothing')
print('      is missing and nothing is invalid. No minimum-cohort guard exists in M-3.')
print(f'   core.validate_per_question_records([], []) raises? ', end='')
try:
    core.validate_per_question_records([], [])
    print('NO (accepts the empty set)')
except Exception as e:
    print(f'YES {type(e).__name__}')

print()
print('=' * 78)
print('P06.2  native-anchor tolerance boundary, with a STRICTLY INTERIOR anchor')
g = [1, 2, 3, 4, 5]                       # |gold| = 5 > k, forces a fractional value
a = anchor(T[4], g)
print(f'   interior anchor value = {a!r}   (0 < a < 1 : {0 < a < 1})')
for delta, label in ((0.0, 'exact'), (1e-13, '+1e-13 (< TOL)'), (1e-12, '+1e-12 (== TOL)'),
                     (2e-12, '+2e-12 (> TOL)'), (1e-9, '+1e-9'), (-1e-13, '-1e-13'),
                     (-2e-12, '-2e-12')):
    try:
        P.score_archive(rep, [T[4]], [g], ['s0'], 0, [a + delta])
        print(f'   anchor {label:16} -> ACCEPTED')
    except P.PipelineError as e:
        print(f'   anchor {label:16} -> {e}')
print(f'   -> tolerance is core.TOL = {core.TOL:g}, applied as abs(value - anchor) <= TOL')

print()
print('=' * 78)
print('P06.3  evidence for OBLIGATION 1 -- native-anchor provenance and granularity')
anch_lines = [l.strip() for l in src.split('\n') if 'native_anchor' in l]
for l in anch_lines:
    print(f'      {l}')
print('   the anchor is a REQUIRED argument; nothing in pipeline.py generates, defaults,')
print(f'   caches or derives it: generation keywords present = '
      f'{sorted(set(re.findall(r"default_anchor|make_anchor|compute_anchor|anchor\\s*=\\s*None", src))) or "NONE"}')
print('   BUT the signature FIXES the granularity to one float per question id')
print('   (len(native_anchor) == len(question_ids)), which is itself part of obligation 1.')

print()
print('=' * 78)
print('P06.4  evidence for OBLIGATION 2 -- LoCoMo gold divergence')
print(f'   audit-correction machinery in pipeline.py: '
      f'{sorted(set(re.findall(r"correction|audit|conv_\\d|raw_evidence", src, re.I))) or "NONE"}')
print(f'   gold enters only as caller-supplied "gold_rows": '
      f'{src.count("gold_rows")} reference(s)')
for l in [l.strip() for l in src.split('\n') if 'gold_rows' in l]:
    print(f'      {l}')
print('   -> the package neither loads corrections nor reinterprets gold; it validates the')
print('      indices it is handed (validate_gold) and nothing more.')

print()
print('=' * 78)
print('P06.5  evidence for OBLIGATION 3 -- LME ordinal, priority ordering, ten-shard assignment')
print(f'   sharding machinery in pipeline.py: '
      f'{sorted(set(re.findall(r"shard|fold|split_ten|partition_cohort", src, re.I))) or "NONE"}')
print('   ordinal assignment, verbatim:')
for l in [l.strip() for l in src.split('\n') if 'archives = [' in l or "enumerate(ids)" in l
          or "c['index']" in l]:
    print(f'      {l}')
print('   -> NO sharding policy is invented (obligation stays open).')
print('   -> BUT the LongMemEval archive ordinal IS chosen here (enumerate(cohort_ids)), and')
print('      P06.6 shows that choice changes the numbers.')

print()
print('=' * 78)
print('P06.6  is the LongMemEval ordinal choice outcome-affecting?  (direct demonstration)')
g0, g1 = [1, 2, 3, 4, 5], [2, 7, 11, 30, 61]
qA, qB = T[4], 'alpha family3 cat2'
# order [s0, s1] -> s0 gets ordinal 0, s1 gets ordinal 1
fxA = {'benchmark': 'LongMemEval', 'cohort_ids': ['s0', 's1'], 'questions_with_empty_gold': [],
       'questions': {'s0': {'units': U, 'text': qA, 'gold_rows': g0},
                     's1': {'units': U, 'text': qB, 'gold_rows': g1}}}
rA = P.assemble_in_memory(fxA, {'s0': anchor(qA, g0, 0), 's1': anchor(qB, g1, 1)})
# order [s1, s0] -> ordinals swap
fxB = dict(fxA, cohort_ids=['s1', 's0'])
rB = P.assemble_in_memory(fxB, {'s1': anchor(qB, g1, 0), 's0': anchor(qA, g0, 1)})
f = lambda d: {(x['question_id'], x['rotation_seed'], x['arm']): x['fractional_R3']
               for x in d['records']}
A, B = f(rA), f(rB)
diff = {k for k in A if A[k] != B[k]}
print(f'   records compared        : {len(A)}')
print(f'   records whose score CHANGED when only cohort_ids order changed : {len(diff)}')
ex = sorted(diff)[:3]
for k in ex:
    print(f'      {k}: {A[k]:.6f} -> {B[k]:.6f}')
print(f'   VERDICT -> the LongMemEval ordinal is '
      f'{"OUTCOME-AFFECTING" if diff else "not outcome-affecting in this fixture"}')

print()
print('=' * 78)
print('P06.7  evidence for OBLIGATION 4 -- finalizer / bootstrap / output path')
print(f'   bootstrap or writer calls in pipeline.py: '
      f'{sorted(set(re.findall(r"question_bootstrap|cluster_bootstrap|safe_write_json|aggregate|paired_matrices|build_clusters", src))) or "NONE"}')
FS = r"write_text|write_bytes|mkdir|to_json|to_csv|read_bytes"
print(f'   pipeline.py returns records in memory only; file-system calls: '
      f'{sorted(set(re.findall(FS, src)))}')
print('   -> read_bytes is used ONCE, to hash-verify the closed core. No output path exists.')

print()
print('=' * 78)
print('P06.8  evidence for OBLIGATION 5 -- seal / HMAC / lock / acceptance')
print(f'   sealing machinery in pipeline.py: '
      f'{sorted(set(re.findall(r"hmac|seal|lock|manifest|acceptance", src, re.I))) or "NONE"}')
print(f'   hashlib used only for the core identity check: '
      f'{[l.strip() for l in src.split(chr(10)) if "hashlib" in l]}')
