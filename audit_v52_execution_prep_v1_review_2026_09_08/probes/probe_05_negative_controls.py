"""PROBE 05: negative controls, exception surfaces and leakage.

Drives short synthetic canaries (well under 120 characters) and checks whether any
caller- or fixture-supplied value can reach an exception message, its repr, the
__cause__/__context__ chain, stdout, stderr, or any written file. Also checks the
non-finite / bad-gold / wrong-and-missing-anchor / real-gate refusals, and checks whether
the package overclaims what its Python audit hook is.

Synthetic only. Usage: python probe_05_negative_controls.py <prep_dir>
"""
import sys, os, io, traceback, contextlib, tempfile
PREP = sys.argv[1]
sys.path.insert(0, PREP)
import numpy as np
import pipeline as P
core = P.core

CANARY_TEXT = 'CANARYTEXT_ZQ7'          # 14 chars
CANARY_ID = 'CANARYID_ZQ8'              # 12 chars
WRITES = []
def _hook(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        mode = args[1] or ''
        if any(m in mode for m in ('w', 'a', '+', 'x')):
            WRITES.append((os.fsdecode(args[0]), mode))
sys.addaudithook(_hook)


def surfaces(label, fn, needles):
    """Run fn and report every surface on which any needle appears."""
    so, se = io.StringIO(), io.StringIO()
    hit = {}
    try:
        with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
            fn()
        print(f'   {label:46} -> no exception raised')
        return
    except BaseException as e:
        msg = str(e)
        rep = repr(e)
        tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        chain, c, names = [], e, []
        while True:
            nxt = c.__cause__ or c.__context__
            if nxt is None or len(chain) > 6:
                break
            c = nxt
            chain.append(str(c))
            names.append(type(c).__name__)
        surf = {'str(e)': msg, 'repr(e)': rep, 'chain': ' | '.join(chain),
                'traceback': tb, 'stdout': so.getvalue(), 'stderr': se.getvalue()}
        for n in needles:
            for k, v in surf.items():
                if n in v:
                    hit.setdefault(n, []).append(k)
        print(f'   {label:46} -> {type(e).__name__}: {msg[:70]!r}')
        print(f'   {"":46}    chain={names or "NONE"}')
        if hit:
            for n, ks in hit.items():
                print(f'   {"":46}    *** {n!r} LEAKS on: {ks} ***')
        else:
            print(f'   {"":46}    no canary on any surface')


print('=' * 78)
print('P05.1  can caller-supplied TEXT reach an exception surface?')
# a text list that makes the sklearn pipeline fail (empty vocabulary after stop-words)
bad = [f'the a of and {CANARY_TEXT}'] * 100
surfaces('Representation(text that fails to vectorise)',
         lambda: P.Representation(bad), [CANARY_TEXT])
rep = P.Representation([f'alpha item{i} family{i % 13} token{i * 17} zulu' for i in range(110)])
surfaces('queries() with a text the vectoriser rejects',
         lambda: rep.queries([CANARY_TEXT, None]), [CANARY_TEXT])
surfaces('queries() with a non-str element',
         lambda: rep.queries([CANARY_TEXT, 3]), [CANARY_TEXT])
surfaces('Representation with non-str element',
         lambda: P.Representation([CANARY_TEXT] * 50 + [7] * 50), [CANARY_TEXT])
print('   NOTE: the fit/query bodies set a flag inside `except Exception:` and raise the')
print('   PipelineError AFTER the handler exits, so __context__ is not attached. Verified above.')

print()
print('=' * 78)
print('P05.2  can caller-supplied IDENTIFIERS reach an exception surface?')
T = [f'alpha item{i} family{i % 13} token{i * 17} zulu' for i in range(110)]
U = [{'text': x} for x in T]
g = [4]
q = rep.queries([T[4]])[0]
d = core.hamming_dist(rep.C, q)
pri = [np.random.default_rng(P.stable_archive_seed(0, t) + 99).random(110) for t in range(20)]
a0 = float(np.mean([len(set(map(int, np.lexsort((x, d))[:3])) & set(g)) / len(g) for x in pri]))

surfaces('score_archive with a duplicate question id',
         lambda: P.score_archive(rep, [T[4], T[4]], [g, g], [CANARY_ID, CANARY_ID], 0, [a0, a0]),
         [CANARY_ID])
surfaces('LoCoMo: conversation question not in cohort',
         lambda: P.assemble_in_memory(
             {'benchmark': 'LoCoMo', 'cohort_ids': ['s0'], 'questions_with_empty_gold': [],
              'conversations': {'cv': {'index': 0, 'units': U, 'questions': {
                  's0': {'text': T[4], 'gold_rows': g},
                  CANARY_ID: {'text': T[9], 'gold_rows': [9]}}}}},
             {'s0': a0}), [CANARY_ID])
surfaces('LongMemEval: cohort id with no question record',
         lambda: P.assemble_in_memory(
             {'benchmark': 'LongMemEval', 'cohort_ids': ['s0', CANARY_ID],
              'questions_with_empty_gold': [],
              'questions': {'s0': {'units': U, 'text': T[4], 'gold_rows': g}}},
             {'s0': a0, CANARY_ID: a0}), [CANARY_ID])
surfaces('LoCoMo: cohort id never scored (missing records)',
         lambda: P.assemble_in_memory(
             {'benchmark': 'LoCoMo', 'cohort_ids': ['s0', CANARY_ID],
              'questions_with_empty_gold': [],
              'conversations': {'cv': {'index': 0, 'units': U,
                                       'questions': {'s0': {'text': T[4], 'gold_rows': g}}}}},
             {'s0': a0, CANARY_ID: a0}), [CANARY_ID])

print()
print('=' * 78)
print('P05.3  non-finite refusals')
for label, mut in (
        ('nan in centered archive', lambda C: C.__setitem__((0, 0), np.nan)),
        ('inf in centered archive', lambda C: C.__setitem__((0, 0), np.inf)),
        ('-inf in centered archive', lambda C: C.__setitem__((3, 7), -np.inf))):
    C = rep.C.copy(); mut(C)
    try:
        core.scale_matrix(C); print(f'   {label:30} -> NOT REFUSED')
    except core.DesignViolation as e:
        print(f'   {label:30} -> DesignViolation: {str(e)[:60]}')
for label, D in (('nan in D', np.diag(np.full(96, np.nan))),
                 ('inf in D', np.diag(np.full(96, np.inf))),
                 ('zero on diagonal', np.diag(np.concatenate([[0.0], np.ones(95)]))),
                 ('negative diagonal', -np.eye(96)),
                 ('non-diagonal D', np.ones((96, 96))),
                 ('wrong shape D', np.eye(95))):
    try:
        P.controls(rep.C, rep.queries([T[4]]), D); print(f'   {label:30} -> NOT REFUSED')
    except P.PipelineError as e:
        print(f'   {label:30} -> {e}')
    except Exception as e:
        print(f'   {label:30} -> {type(e).__name__}: {str(e)[:50]}')
for label, dist in (('nan distance', np.array([np.nan, 1.0, 2.0, 3.0])),
                    ('inf distance', np.array([np.inf, 1.0, 2.0, 3.0])),
                    ('empty distance', np.array([]))):
    try:
        P.topks_by_hamming(dist, np.random.default_rng(0).random((20, max(len(dist), 1))))
        print(f'   {label:30} -> NOT REFUSED')
    except P.PipelineError as e:
        print(f'   {label:30} -> {e}')
try:
    P.topks_by_hamming(np.array([1, 2, 3, 4]), np.full((20, 4), np.nan))
    print(f'   {"nan priority":30} -> NOT REFUSED')
except P.PipelineError as e:
    print(f'   {"nan priority":30} -> {e}')

print()
print('=' * 78)
print('P05.4  real-gate refusal')
for call in (lambda: P.run_on_real_corpus(),
             lambda: P.run_on_real_corpus(enabled=True),
             lambda: P.run_on_real_corpus('locomo10.json', force=True, authorized=True)):
    try:
        call(); print('   run_on_real_corpus -> RETURNED (gate open!)')
    except P.PipelineError as e:
        print(f'   run_on_real_corpus(...) -> {e}')
print(f'   core.REAL_DATA_EXECUTION_ENABLED = {core.REAL_DATA_EXECUTION_ENABLED}')
try:
    core.require_real_data_authorization()
    print('   core.require_real_data_authorization() -> PASSED (gate open!)')
except Exception as e:
    print(f'   core.require_real_data_authorization() -> {type(e).__name__}: {str(e)[:70]}')
src = open(os.path.join(PREP, 'pipeline.py'), encoding='utf-8').read()
import re
ACQ = r"urlopen|urlretrieve|requests\.|httpx|socket|subprocess|\.to_csv|json\.dump|pickle"
found_acq = sorted(set(re.findall(ACQ, src)))
print(f'   pipeline.py acquisition/writer verbs found: {found_acq or "NONE"}')
fs = sorted(set(re.findall(r"(read_bytes|read_text|write_bytes|write_text|open|mkdir|glob)\(", src)))
print(f'   pipeline.py file-system calls: {fs}')

print()
print('=' * 78)
print('P05.5  did anything write a file during this whole probe?')
print(f'   write-mode open() events observed: {len(WRITES)}')
for w in WRITES[:10]:
    print(f'      {w}')

print()
print('=' * 78)
print('P05.6  the Python audit hook is NOT an OS sandbox -- does the package claim otherwise?')
readme = open(os.path.join(PREP, 'README.md'), encoding='utf-8').read()
for phrase in ('not a universal security boundary', 'audit hook', 'sandbox', 'security'):
    found = [l.strip() for l in readme.split('\n') if phrase in l]
    print(f'   README lines mentioning {phrase!r}: {len(found)}')
    for l in found[:3]:
        print(f'      {l}')
# demonstrate the limits concretely, on a file WE create in a temp dir (no corpus involved)
td = tempfile.mkdtemp()
p_json = os.path.join(td, 'synthetic_probe.json')
open(p_json, 'w').write('{"synthetic": 1}')          # our own hook allows writes; test-hook blocks .json reads
test_src = open(os.path.join(PREP, 'test_pipeline.py'), encoding='utf-8').read()
guard = test_src[test_src.index('def guard'):test_src.index('sys.addaudithook')]
print()
print('   the test-file guard, verbatim:')
for l in guard.rstrip().split('\n'):
    print('      ' + l)
ns = {'os': os}
exec(compile(guard, '<guard>', 'exec'), ns)
g = ns['guard']
for path in ('data/locomo10.json', 'data/x.jsonl', 'data/x.csv', 'a.gz', 'a.parquet',
             'corpus.txt', 'corpus.dat', 'corpus', 'corpus.JSON', 'corpus.pkl', 'corpus.npy',
             'site-packages/numpy-2.3.5.dist-info/direct_url.json'):
    try:
        g('open', (path, 'r', 0)); r = 'ALLOWED'
    except RuntimeError:
        r = 'blocked'
    print(f'      guard({path!r:58}) -> {r}')
print()
print('   -> the guard is an extension allow/deny list inside ONE Python process. It does not')
print('      cover: other extensions (.txt/.dat/.pkl/.npy/no extension), reads by a child')
print('      process, memory-mapped or C-level reads, or anything outside this interpreter.')
print(f'   -> README states this limitation explicitly: '
      f'{"not a universal security boundary" in readme}')
print(f'   -> pipeline.py itself installs NO audit hook (guard lives only in the test file): '
      f'{"addaudithook" not in src}')
