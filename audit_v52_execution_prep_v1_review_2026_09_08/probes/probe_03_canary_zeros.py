"""PROBE 03: SIGNED-PERMUTATION CANARY on EXACT ZERO coordinates.

Question under review: a signed permutation can break the `>= 0` sign convention at exact
zeros. Does the canary abort rather than silently changing zero handling, and is the canary
itself fixed in source rather than chosen after observing data?

Includes an exact/rational control (Fraction arithmetic, no floating point) as well as the
numerical one. Synthetic only. Usage: python probe_03_canary_zeros.py <prep_dir>
"""
import sys, os, re
from fractions import Fraction
PREP = sys.argv[1]
sys.path.insert(0, PREP)
import numpy as np
import pipeline as P
core = P.core

print('=' * 78)
print('P03.1  IEEE ground truth: what negation actually does to the >=0 code at zero')
for x in (0.0, -0.0, 1e-300, -1e-300):
    print(f'   x={x!r:10} (x>=0)={x >= 0!s:5}   (-1.0*x)={-1.0 * x!r:10} '
          f'((-1.0*x)>=0)={(-1.0 * x) >= 0!s:5}')
print('   -> for x == 0.0 the code is PRESERVED under negation because -0.0 >= 0 is True.')
print('   -> so an ALL-zero coordinate does NOT trip the canary; the danger is the MIXED case')
print('      where the archive side is exactly 0 and the query side is not (or vice versa).')

print()
print('=' * 78)
print('P03.2  the canary as written in the candidate')
src = open(os.path.join(PREP, 'pipeline.py'), encoding='utf-8').read()
ctl = src[src.index('def controls'):src.index('def score_archive')]
print(ctl.rstrip())
print()
perm = np.arange(95, -1, -1)
signs = np.where(np.arange(96) % 2, -1, 1)
print(f'   perm  = reverse permutation, fixed literal      : {perm[:6]} ... {perm[-3:]}')
print(f'   signs = alternating +1/-1, fixed literal        : {signs[:8]}')
print(f'   both are SOURCE LITERALS with no data dependence and no RNG: '
      f'{"np.random" not in ctl and "seed" not in ctl}')
print(f'   canary applied to both (C,Q) and (C@D, Q@D)     : '
      f'{"for X, V in ((C, Q), (C @ D, Q @ D))" in ctl}')

print()
print('=' * 78)
print('P03.3  ALL-ZERO coordinate: canary must NOT fire (and must not silently "fix" anything)')
rng = np.random.default_rng(7)
C = rng.normal(size=(12, 96)); Q = rng.normal(size=(3, 96))
C[:, 5] = 0.0; Q[:, 5] = 0.0                  # column 5 exactly zero on BOTH sides
try:
    P.controls(C, Q, np.eye(96)); print('   all-zero column -> canary did NOT fire (expected)')
except P.PipelineError as e:
    print(f'   all-zero column -> {e}')

print()
print('=' * 78)
print('P03.4  MIXED zero coordinate: archive exactly 0, query non-zero -> canary MUST abort')
C = rng.normal(size=(12, 96)); Q = rng.normal(size=(3, 96))
C[:, 0] = 0.0; Q[:, 0] = 1.0                  # the minimal breaking configuration
try:
    P.controls(C, Q, np.eye(96))
    print('   *** canary did NOT fire -- the >=0 convention broke SILENTLY ***')
except P.PipelineError as e:
    print(f'   -> ABORTED with {e}')
    print('   -> correct: it aborts, it does not reinterpret the zero')

print('   and the mirrored case (query exactly 0, archive non-zero):')
C = rng.normal(size=(12, 96)); Q = rng.normal(size=(3, 96))
C[:, 0] = 1.0; Q[:, 0] = 0.0
try:
    P.controls(C, Q, np.eye(96)); print('   -> NOT detected')
except P.PipelineError as e:
    print(f'   -> ABORTED with {e}')

print('   which coordinates can trip it?  only ones whose sign is NEGATED by `signs`:')
for col in (0, 1, 2, 3):
    C = rng.normal(size=(8, 96)); Q = rng.normal(size=(2, 96))
    C[:, col] = 0.0; Q[:, col] = 1.0
    try:
        P.controls(C, Q, np.eye(96)); r = 'not detected'
    except P.PipelineError:
        r = 'ABORTS'
    # after perm, old column `col` lands at new index 95-col, whose sign is signs[95-col]
    print(f'      zero at column {col}: new index {95 - col}, sign {signs[95 - col]:+d} -> {r}')
print('   -> a zero at a coordinate that keeps sign +1 is NOT detected by this canary.')
print('      (see P03.6 for the consequence)')

print()
print('=' * 78)
print('P03.5  EXACT / RATIONAL control -- no floating point anywhere')
def code_exact(v):            # the >=0 sign code, on exact rationals
    return [x >= 0 for x in v]
def ham_exact(Crows, q):
    return [sum(1 for a, b in zip(code_exact(r), code_exact(q)) if a != b) for r in Crows]
F = Fraction
perm_s = list(range(95, -1, -1))
signs_s = [(-1 if i % 2 else 1) for i in range(96)]
def apply_sp_row(r):
    return [F(signs_s[j]) * r[perm_s[j]] for j in range(96)]

# case A: no zeros -> Hamming distance must be exactly invariant
Crows = [[F((i * 7 + j * 13) % 11 - 5, 3) or F(1, 7) for j in range(96)] for i in range(6)]
q = [F((j * 5) % 9 - 4, 2) or F(1, 5) for j in range(96)]
before = ham_exact(Crows, q)
after = ham_exact([apply_sp_row(r) for r in Crows], apply_sp_row(q))
print(f'   A: no exact zeros      -> before={before} after={after}  invariant={before == after}')

# case B: archive exactly 0 at a NEGATED coordinate, query non-zero
Crows2 = [list(r) for r in Crows]; q2 = list(q)
for r in Crows2:
    r[0] = F(0)
q2[0] = F(1)
before = ham_exact(Crows2, q2)
after = ham_exact([apply_sp_row(r) for r in Crows2], apply_sp_row(q2))
print(f'   B: exact zero, mixed   -> before={before} after={after}  invariant={before == after}')
print('   -> in EXACT rational arithmetic the invariance genuinely fails, so the property the')
print('      canary tests is a real mathematical fact, not a floating-point artefact.')
print('   NOTE: in exact rationals 0 has no sign, so Fraction(-1)*Fraction(0) == 0 and 0 >= 0')
print('      stays True -- identical to the IEEE -0.0 >= 0 behaviour shown in P03.1.')

print()
print('=' * 78)
print('P03.6  can exact zeros arise on the real path, and is the canary complete?')
TEXTS = [f'alpha item{i} family{i % 13} token{i * 17} cat{i % 7} zulu' for i in range(110)]
rep = P.Representation(TEXTS)
Qr = rep.queries([TEXTS[4], 'alpha family3 cat2'])
print(f'   exact zeros in fitted C : {int((rep.C == 0).sum())} of {rep.C.size}')
print(f'   exact zeros in fitted Q : {int((Qr == 0).sum())} of {Qr.size}')
print(f'   min |C| = {np.min(np.abs(rep.C)):.3e}')
print('   -> on this synthetic archive exact zeros do not occur; the canary is a tripwire for')
print('      a condition that is rare, not a routine gate.')
print()
print('   COMPLETENESS: the canary uses ONE fixed sign vector, so it can only observe a')
print('   zero-coordinate break at coordinates it negates. After perm, new index j holds old')
print(f'   index {95}-j and is negated when j is odd, i.e. old index even is negated.')
neg_old = sorted(perm[np.flatnonzero(signs == -1)])
print(f'   old coordinates actually negated: {len(neg_old)} of 96 '
      f'(e.g. {neg_old[:5]} ... {neg_old[-3:]})')
print(f'   coordinates NEVER negated by this canary: {96 - len(neg_old)}')
print('   -> a zero-coordinate sign break confined to a never-negated coordinate would pass.')
print('      This is a COVERAGE limit of the canary, not an incorrect result.')
