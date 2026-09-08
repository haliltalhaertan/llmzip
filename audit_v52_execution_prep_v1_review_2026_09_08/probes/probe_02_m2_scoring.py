"""PROBE 02 (M-2): six arms and order, scaling-before-rotation, seed panel, priority reuse,
matched blocks, top-k ties, fractional recall / gold accounting, native anchor.

Independent review probe. Synthetic only. Usage: python probe_02_m2_scoring.py <prep_dir>
"""
import sys, os, itertools, json
PREP = sys.argv[1]
sys.path.insert(0, PREP)
import numpy as np
import pipeline as P
core = P.core

TEXTS = [f'alpha item{i} family{i % 13} token{i * 17} cat{i % 7} zulu' for i in range(110)]
rep = P.Representation(TEXTS)
QUERY = [TEXTS[4], 'alpha family3 cat2']
GOLD = [[4], [3, 16]]
QIDS = ['s0', 's1']

def anchors_for(rep, query, gold):
    """Independent full-sort oracle for the NATIVE arm (not the candidate's top-k path)."""
    q = rep.queries(query)
    pri = np.array([np.random.default_rng(P.stable_archive_seed(0, t) + 99).random(len(rep.C))
                    for t in range(P.N_NUISANCE)])
    out = []
    for v, g in zip(q, gold):
        d = core.hamming_dist(rep.C, v)
        vals = [len(set(map(int, np.lexsort((x, d))[:3])) & set(g)) / len(g) for x in pri]
        out.append(float(np.mean(vals)))
    return out

ANCH = anchors_for(rep, QUERY, GOLD)
print(f'independent native anchors = {ANCH}')

print()
print('=' * 78)
print('P02.1  six arms, their ORDER, and the ten paired seeds')
rows, diag = P.score_archive(rep, QUERY, GOLD, QIDS, 0, ANCH)
seen_order = []
for r in rows:
    if r['question_id'] == 's0' and r['rotation_seed'] == 60001:
        seen_order.append(r['arm'])
print(f'   arm order as emitted   : {seen_order}')
print(f'   core.ARMS (normative)  : {list(core.ARMS)}')
print(f'   ORDER MATCHES CORE     : {seen_order == list(core.ARMS)}')
print(f'   rotation seeds emitted : {sorted({r["rotation_seed"] for r in rows})}')
print(f'   core.ROTATION_SEEDS    : {list(core.ROTATION_SEEDS)}')
print(f'   core.PARTITION_SEEDS   : {list(core.PARTITION_SEEDS)}')
print(f'   SEED PANEL MATCHES     : '
      f'{sorted({r["rotation_seed"] for r in rows}) == list(core.ROTATION_SEEDS)}')
print(f'   record count = {len(rows)} (expect 2 q x 10 seeds x 6 arms = 120)')
print(f'   no historical seed panel (e.g. 5101/5204/1..10) present : '
      f'{not ({r["rotation_seed"] for r in rows} & {5101, 5204, 1, 2, 3})}')

print()
print('=' * 78)
print('P02.2  scaling is applied BEFORE rotation')
C, D = rep.C, rep.D
Q = rep.queries(QUERY)
Cs, Qs = C @ D, Q @ D
a, b = core.draw_rotation_blocks(60001)
rs = core.build_rotation(a, b, core.spectral_membership())
rr = core.build_rotation(a, b, core.random_membership(70001))
# Reproduce each arm independently and compare the resulting SCORES.
Pmat = np.array([np.random.default_rng(P.stable_archive_seed(0, t) + 99).random(len(C))
                 for t in range(P.N_NUISANCE)])
cells = {'NATIVE': (C, Q), 'SCALED_NATIVE': (Cs, Qs), 'B32_FRESH': (C @ rs, Q @ rs),
         'SCALED_B32': (Cs @ rs, Qs @ rs), 'RANDOM32_FRESH': (C @ rr, Q @ rr),
         'SCALED_RANDOM32': (Cs @ rr, Qs @ rr)}
mine = {}
for arm, (X, V) in cells.items():
    for j, qid in enumerate(QIDS):
        picks = P.topks_by_hamming(core.hamming_dist(X, V[j]), Pmat)
        mine[(qid, arm)] = float(np.mean([P.fractional(t, GOLD[j]) for t in picks]))
theirs = {(r['question_id'], r['arm']): r['fractional_R3'] for r in rows
          if r['rotation_seed'] == 60001}
print(f'   independent reconstruction equals candidate at seed 60001 : {mine == theirs}')
# Wrong order (rotate then scale) must differ -> proves the order is load-bearing & correct
wrong = C @ rs @ D
print(f'   (C@D)@rs  vs  (C@rs)@D  identical? {np.allclose(Cs @ rs, wrong)}   '
      f'max diff = {np.max(np.abs(Cs @ rs - wrong)):.3e}')
print('   -> the two orders are genuinely different; candidate uses scale-then-rotate')

print()
print('=' * 78)
print('P02.3  nuisance priority vectors REUSED across arms and seeds (not redrawn)')
src = open(os.path.join(PREP, 'pipeline.py'), encoding='utf-8').read()
body = src[src.index('def score_archive'):src.index('def assemble_in_memory')]
p_line = [l for l in body.split('\n') if 'default_rng' in l]
print(f'   P is constructed at: {" ".join(l.strip() for l in p_line)}')
print(f'   P constructed INSIDE the seed loop? '
      f'{body.index("for seed, partition") < body.index("P = np.array")}')
print(f'   P constructed BEFORE the seed loop?  '
      f'{body.index("P = np.array") < body.index("for seed, partition")}')
# behavioural proof: count how many distinct RNG draws happen during a full score_archive
draws = []
_orig_rng = np.random.default_rng
def spy(seed=None):
    draws.append(seed)
    return _orig_rng(seed)
np.random.default_rng = spy
P.score_archive(rep, QUERY, GOLD, QIDS, 0, ANCH)
np.random.default_rng = _orig_rng
nuis = [d for d in draws if isinstance(d, (int, np.integer)) and d >= 5_100_000]
print(f'   default_rng() calls with a nuisance seed during one score_archive : {len(nuis)}')
print(f'   distinct nuisance seeds                                           : {len(set(nuis))}')
print(f'   expected if reused once per archive                               : {P.N_NUISANCE}')
print(f'   VERDICT P02.3 -> {"PASS (drawn once, reused for all 10 seeds x 6 arms)" if len(nuis) == P.N_NUISANCE else "FAIL"}')
print(f'   other default_rng seeds seen (rotation/partition) : {sorted(set(d for d in draws if isinstance(d,(int,np.integer)) and d < 5_100_000))}')

print()
print('=' * 78)
print('P02.4  matched block identity across arms')
print('   source line: ' + [l.strip() for l in body.split('\n') if 'assert_matched_blocks' in l][0])
print('   -> the call passes the SAME objects (a, b, a, b) to both argument pairs.')
aa, bb = core.draw_rotation_blocks(60001)
cc, dd = core.draw_rotation_blocks(60002)
try:
    core.assert_matched_blocks(aa, bb, cc, dd)
    print('   control CAN distinguish different blocks : NO')
except core.DesignViolation:
    print('   control CAN distinguish different blocks : YES (it works when given different blocks)')
print('   but as CALLED, assert_matched_blocks(a,b,a,b) computes max|a-a| and max|b-b| == 0.0')
print(f'   -> the assertion as invoked is VACUOUS: it cannot fail for any input. '
      f'max|a-a| = {float(np.max(np.abs(aa - aa)))}')
# The real guarantee is structural: rs and rr are built from the same a,b objects.
rs1 = core.build_rotation(aa, bb, core.spectral_membership())
rr1 = core.build_rotation(aa, bb, core.random_membership(70001))
S, T = core.spectral_membership(), np.setdiff1d(np.arange(96), core.random_membership(70001))
print(f'   structural check: rs and rr both embed the identical q32 block : '
      f'{np.array_equal(rs1[np.ix_(S, S)], aa)}')

print()
print('=' * 78)
print('P02.5  top-k tie handling: parity with pinned a6ecee02 under HEAVY ties')
import ast, subprocess, hashlib
blob = subprocess.check_output(
    ['git', 'show', '692f599eedeb7e7a649443f24ff507e8c4d1c17d:research/v52/'
     'locomo_sign_mechanism_replication.py'], cwd=os.environ['REPO_ROOT'])
assert hashlib.sha256(blob).hexdigest() == \
    'a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b'
tree = ast.parse(blob)
sel = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                       and n.name in {'topks_by_hamming', 'fractional'}], type_ignores=[])
scope = {'np': np, 'TOPK': 3}
exec(compile(sel, '<pinned>', 'exec'), scope)
old = scope['topks_by_hamming']

rng = np.random.default_rng(20260908)
mismatch = 0; cases = 0; branch = {'small': 0, 'all_boundary': 0, 'partial': 0}
for trial in range(4000):
    n = int(rng.integers(1, 40))
    hi = int(rng.choice([1, 2, 3, 5, 97]))          # hi=1 -> ALL distances identical
    d = rng.integers(0, hi, n)
    pri = rng.random((20, n))
    if rng.random() < 0.3:                          # force priority ties too
        pri = np.round(pri, 1)
    A = P.topks_by_hamming(d, pri); B = old(d, pri)
    cases += 1
    if n <= 3:
        branch['small'] += 1
    else:
        k = 3; kth = np.partition(d, k - 1)[k - 1]
        st = np.flatnonzero(d < kth); bd = np.flatnonzero(d == kth)
        branch['all_boundary' if (k - len(st)) == len(bd) else 'partial'] += 1
    for x, y in zip(A, B):
        if not np.array_equal(np.asarray(x), np.asarray(y)):
            mismatch += 1
            if mismatch == 1:
                print(f'   FIRST MISMATCH n={n} d={list(d)} -> new {list(x)} old {list(y)}')
print(f'   fuzz cases={cases}  branch coverage={branch}')
print(f'   element-wise mismatches vs pinned = {mismatch}')
print(f'   VERDICT P02.5 -> {"PASS (bit-identical to pinned incl. heavy ties)" if not mismatch else "FAIL"}')

# the branch the port DROPPED (`if need <= 0`) -- prove it is unreachable
bad = 0
for trial in range(20000):
    n = int(rng.integers(4, 60)); d = rng.integers(0, int(rng.choice([1, 2, 3, 8])), n)
    kth = np.partition(d, 2)[2]
    if 3 - len(np.flatnonzero(d < kth)) <= 0:
        bad += 1
print(f'   pinned source has an extra `if need <= 0` branch that the port omits.')
print(f'   times `need <= 0` occurred in 20000 random cases : {bad}')
print('   proof: strict = {i : d_i < d_(k)} has at most k-1 elements by definition of the')
print('   k-th order statistic, so need = k - |strict| >= 1 always. The omitted branch is')
print('   DEAD CODE in the pinned source; omitting it is behaviour-preserving.')

print()
print('=' * 78)
print('P02.6  fractional recall / gold accounting')
print(f'   fractional(top,gold) = |set(top) & set(gold)| / len(gold)  (denominator = |gold|)')
for g in ([4], [3, 16], [1, 2, 3, 4, 5]):
    top = [4, 3, 16]
    print(f'      gold={g} top={top} -> {P.fractional(top, g):.4f}  '
          f'(max attainable with k=3 is {min(3, len(g)) / len(g):.4f})')
print('   NOTE: with |gold| > k=3 the arm can never reach 1.0; this is recall, not precision.')
print(f'   core record validator accepts scores in [0,1] only -> consistent.')
print('   gold validation:')
for g, why in (([], 'empty'), ([True], 'bool'), ([-1], 'negative'), ([110], 'out of range'),
               ([0, 0], 'duplicate'), ([np.int64(3)], 'numpy int'), ((3,), 'tuple not list'),
               ([3.0], 'float')):
    try:
        P.validate_gold(g, 110); print(f'      {why:16} {g!r:14} -> ACCEPTED')
    except P.PipelineError as e:
        print(f'      {why:16} {g!r:14} -> {e}')

print()
print('=' * 78)
print('P02.7  native anchor semantics')
for label, anch in (('correct', ANCH),
                    ('perturbed by 1e-9', [ANCH[0] + 1e-9, ANCH[1]]),
                    ('perturbed by 1e-13', [ANCH[0] + 1e-13, ANCH[1]]),
                    ('wrong', [1.0 - ANCH[0], ANCH[1]]),
                    ('missing (None)', None),
                    ('wrong length', [ANCH[0]]),
                    ('out of range', [1.5, ANCH[1]]),
                    ('numpy float', [np.float64(ANCH[0]), ANCH[1]]),
                    ('int', [0, ANCH[1]]),
                    ('nan', [float('nan'), ANCH[1]])):
    try:
        P.score_archive(rep, QUERY, GOLD, QIDS, 0, anch)
        print(f'   {label:20} -> ACCEPTED')
    except P.PipelineError as e:
        print(f'   {label:20} -> {e}')
print(f'   core.TOL = {core.TOL:g} (anchor tolerance)')

print()
print('=' * 78)
print('P02.8  native / scaled-native sign and distance controls; rotation norm/dot')
print('   check_identity: sign(xD) == sign(x) bitwise for archive AND query')
try:
    core.check_identity(C, Q, D); print('   check_identity on real fitted D : PASS')
except core.DesignViolation as e:
    print(f'   check_identity : {e}')
Dneg = D.copy(); Dneg[0, 0] = -Dneg[0, 0]
try:
    core.check_identity(C, Q, Dneg); print('   check_identity with a negated coordinate : NOT DETECTED')
except core.DesignViolation as e:
    print(f'   check_identity with a negated coordinate : DETECTED -> {str(e)[:60]}')
print(f'   NATIVE vs SCALED_NATIVE distances identical for every query : '
      f'{all(np.array_equal(core.hamming_dist(C, Q[j]), core.hamming_dist(Cs, Qs[j])) for j in range(2))}')
nv = {(r["rotation_seed"], r["question_id"]): r["fractional_R3"] for r in rows if r["arm"] == "NATIVE"}
sn = {(r["rotation_seed"], r["question_id"]): r["fractional_R3"] for r in rows if r["arm"] == "SCALED_NATIVE"}
print(f'   consequently NATIVE == SCALED_NATIVE in every emitted record : {nv == sn}')
for nm, R in (('spectral', rs), ('random', rr)):
    for xn, (X, V) in (('native', (C, Q)), ('scaled', (Cs, Qs))):
        n_, d_ = core.check_rotation_invariance(X, V, R)
        print(f'   rotation invariance {nm:9}/{xn:7}: norm={n_:.3e} dot={d_:.3e} TOL={core.TOL:g} '
              f'-> {"ok" if n_ <= core.TOL and d_ <= core.TOL else "VIOLATION"}')
