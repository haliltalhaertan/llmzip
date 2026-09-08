"""PROBE 01 (M-1): archive-only fitting, no query leakage, memory-only, pinned-arithmetic parity.

Independent review probe. Synthetic strings only. Run as its own process.
Usage: python probe_01_m1_representation.py <prep_dir>
"""
import sys, os, io, json, copy, hashlib
PREP = sys.argv[1]
sys.path.insert(0, PREP)
import numpy as np
import scipy.sparse as sp

# ---- record every file the process OPENS while M-1 fits, to test "memory-only" -------------
OPENED = []
def _hook(event, args):
    if event == 'open':
        OPENED.append((os.fsdecode(args[0]) if isinstance(args[0], (str, bytes)) else repr(args[0]),
                       args[1]))
sys.addaudithook(_hook)

import pipeline as P

TEXTS = [f'alpha item{i} family{i % 13} token{i * 17} cat{i % 7} zulu' for i in range(110)]

def fingerprint(rep):
    """Every piece of fitted state that could carry query information."""
    fp = {}
    fp['word_vocab'] = hashlib.sha256(json.dumps(sorted(rep.word.vocabulary_.items()),
                                                 sort_keys=True).encode()).hexdigest()
    fp['char_vocab'] = hashlib.sha256(json.dumps(sorted(rep.char.vocabulary_.items()),
                                                 sort_keys=True).encode()).hexdigest()
    fp['word_idf'] = rep.word.idf_.tobytes()
    fp['char_idf'] = rep.char.idf_.tobytes()
    fp['lsa_comp'] = rep.lsa.components_.tobytes()
    fp['svd_comp'] = rep.svd.components_.tobytes()
    fp['svd_expvar'] = rep.svd.explained_variance_.tobytes()
    fp['mu'] = rep.mu.tobytes()
    fp['C'] = rep.C.tobytes()
    fp['D'] = rep.D.tobytes()
    fp['diag'] = json.dumps(rep.diagnostics, sort_keys=True)
    return fp

print('=' * 78)
print('P01.1  fitting is archive-only: fitted state must be byte-identical before/after queries')
n_open_before = len(OPENED)
rep = P.Representation(TEXTS)
fit_opens = OPENED[n_open_before:]
fp0 = fingerprint(rep)

# adversarial queries: brand-new vocabulary, huge, empty-ish, repeated, unicode
ADVERSARIAL = [
    'zzzz totally unseen vocabulary quux frobnicate',
    'a', '', 'alpha ' * 400, 'üñîçødé 你好',
    'item3 family3 token51 cat3 zulu',
]
for t in ADVERSARIAL:
    try:
        rep.queries([t])
    except P.PipelineError as e:
        print(f'   query {t[:20]!r} refused -> {e}')
fp1 = fingerprint(rep)
diffs = [k for k in fp0 if fp0[k] != fp1[k]]
print(f'   fitted-state keys compared : {len(fp0)}')
print(f'   keys changed by queries    : {diffs}')
print(f'   VERDICT P01.1 -> {"PASS (no query leakage into fitted state)" if not diffs else "FAIL"}')

print()
print('=' * 78)
print('P01.2  attempt to force a query-derived quantity into the transform')
# (a) does queries() ever call a fit method?  Instrument every estimator.
calls = []
for name in ('word', 'char', 'lsa', 'svd'):
    est = getattr(rep, name)
    for meth in ('fit', 'fit_transform', 'partial_fit'):
        if hasattr(est, meth):
            orig = getattr(est, meth)
            def mk(n=name, m=meth, o=orig):
                def f(*a, **k):
                    calls.append(f'{n}.{m}')
                    return o(*a, **k)
                return f
            setattr(est, meth, mk())
rep.queries(['brand new never seen tokens qqq www eee', 'alpha item9'])
print(f'   fit-family calls during queries(): {calls}')
print(f'   VERDICT P01.2a -> {"PASS (no refitting on queries)" if not calls else "FAIL"}')

# (b) can a query grow the vocabulary / change dimensionality?
w_before = rep.word.transform(['alpha']).shape[1]
rep.queries(['qqqzzz unseen unseen unseen'])
w_after = rep.word.transform(['alpha']).shape[1]
print(f'   word feature dim before/after unseen query: {w_before} / {w_after}')
print(f'   VERDICT P01.2b -> {"PASS" if w_before == w_after else "FAIL"}')

# (c) order-independence: query results must not depend on other queries in the batch
qa = rep.queries(['alpha item5 family5'])
qb = rep.queries(['alpha item5 family5', 'completely different unseen text zzz'])
same = np.array_equal(qa[0], qb[0])
print(f'   same query alone vs batched with another: identical = {same}')
print(f'   VERDICT P01.2c -> {"PASS (no cross-query contamination)" if same else "FAIL"}')

print()
print('=' * 78)
print('P01.3  memory-only fitting: files opened during Representation() construction')
writes = [o for o in fit_opens if any(m in (o[1] or '') for m in ('w', 'a', '+'))]
print(f'   total open() events during fit : {len(fit_opens)}')
print(f'   open() events with write mode  : {len(writes)}')
for o in writes[:10]:
    print(f'      {o}')
print(f'   VERDICT P01.3 -> {"PASS (no artefact written during fit)" if not writes else "FAIL"}')

print()
print('=' * 78)
print('P01.4  query transform genuinely reuses the archive-fitted objects')
# Re-implement the query path by hand from the *fitted* objects and compare bitwise.
from sklearn.preprocessing import normalize
texts = ['alpha item7 family7 token119 cat0 zulu', 'unseen frobnicate quux']
w = normalize(rep.word.transform(texts))
c = normalize(rep.char.transform(texts))
lat = normalize(rep.lsa.transform(w))
z = sp.hstack([sp.csr_matrix(lat), w, c], format='csr')
manual = (normalize(rep.svd.transform(z)) - rep.mu).astype(np.float64)
got = rep.queries(texts)
print(f'   max |manual - queries()| = {np.max(np.abs(manual - got)):.3e}')
print(f'   bitwise identical        = {np.array_equal(manual, got)}')
print(f'   VERDICT P01.4 -> {"PASS" if np.array_equal(manual, got) else "FAIL"}')

# archive row put back through queries() must reproduce C (numerically)
back = rep.queries(TEXTS)
print(f'   max |queries(archive) - C| = {np.max(np.abs(back - rep.C)):.3e}')

print()
print('=' * 78)
print('P01.5  pinned arithmetic parity: M-1 hyperparameters vs a6ecee02 source')
import ast, subprocess
blob = subprocess.check_output(
    ['git', 'show', '692f599eedeb7e7a649443f24ff507e8c4d1c17d:research/v52/'
     'locomo_sign_mechanism_replication.py'], cwd=os.environ.get('REPO_ROOT', '.'))
assert hashlib.sha256(blob).hexdigest() == \
    'a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b', 'pinned source hash'
print('   pinned source sha256 verified: a6ecee02...')
tree = ast.parse(blob)
consts = {t.targets[0].id: ast.literal_eval(t.value) for t in tree.body
          if isinstance(t, ast.Assign) and isinstance(t.targets[0], ast.Name)
          and isinstance(t.targets[0].ctx, ast.Store)
          and t.targets[0].id in ('SVD_SEED', 'SOURCE_LATENT_DIM', 'N_NUISANCE', 'TOPK')}
print(f'   pinned constants          : {consts}')
print(f'   prep TOPK / N_NUISANCE    : {P.TOPK} / {P.N_NUISANCE}')
ok = (consts['TOPK'] == P.TOPK and consts['N_NUISANCE'] == P.N_NUISANCE
      and rep.svd.random_state == consts['SVD_SEED']
      and rep.lsa.random_state == 5101
      and rep.lsa.n_components == min(consts['SOURCE_LATENT_DIM'], 109, 10 ** 9))
print(f'   prep lsa.random_state={rep.lsa.random_state} svd.random_state={rep.svd.random_state}'
      f' lsa.n_components={rep.lsa.n_components} svd.n_components={rep.svd.n_components}')
print(f'   VERDICT P01.5 -> {"PASS (seeds/dims match pinned)" if ok else "FAIL"}')

print()
print('=' * 78)
print('P01.6  scale_matrix comes from the closed core, unchanged')
print(f'   core path : {P.CORE_PATH}')
print(f'   core hash pinned in pipeline.py : {P.CORE_HASH}')
print(f'   sha256 of file actually loaded  : '
      f'{hashlib.sha256(open(P.CORE_PATH, "rb").read()).hexdigest()}')
D2, diag2 = P.core.scale_matrix(rep.C)
print(f'   rep.D equals core.scale_matrix(rep.C) bitwise : {np.array_equal(D2, rep.D)}')
print(f'   diagnostics equal                            : {diag2 == rep.diagnostics}')
print(f'   D is diagonal, strictly positive             : '
      f'{np.array_equal(rep.D, np.diag(np.diag(rep.D))) and bool((np.diag(rep.D) > 0).all())}')

print()
print('=' * 78)
print('P01.7  boundary: exactly 96 archive rows (minimum the code accepts for SVD96)')
for n in (95, 96, 97):
    t = [f'alpha item{i} family{i % 13} token{i * 17} cat{i % 7} zulu' for i in range(n)]
    try:
        r = P.Representation(t)
        print(f'   n={n}: OK  C.shape={r.C.shape}  degenerate_coords='
              f'{r.diagnostics["degenerate_coords"]}  flagged={r.diagnostics["flagged"]}')
    except Exception as e:
        print(f'   n={n}: {type(e).__name__}: {e}')

print()
print('=' * 78)
print('P01.8  E-M-005 reachability (require() inside the try/except that raises E-M-006)')
# vocabulary of size 1 after english stopwords -> d = min(32, n-1, n_features-1) = 0
tiny = ['the a of and ' + ('alpha ' * 3) for _ in range(100)]
try:
    P.Representation(tiny)
    print('   no error raised')
except P.PipelineError as e:
    print(f'   raised: {e}')
    print(f'   -> E-M-005 is MASKED by E-M-006' if 'E-M-006' in str(e) else '   -> E-M-005 surfaced')
