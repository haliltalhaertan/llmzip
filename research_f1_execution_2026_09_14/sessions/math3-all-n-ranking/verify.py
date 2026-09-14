# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# verify.py — shared-gold all-N/K dominance (model H)

from fractions import Fraction as F
from itertools import permutations, product
from math import factorial
import json

W, T, L = 2, 1, 0  # gold: strictly closer / tied / strictly farther
PA = {0: F(1, 4), 1: F(1, 2), 2: F(1, 4)}
PB = {0: F(1, 4), 1: F(1, 2), 2: F(1, 4)}
T_REPS = {'t025': F(1, 4), 't05': F(1, 2), 't075': F(3, 4),
          't1': F(1), 't15': F(3, 2), 't10': F(10)}


def sign_out(D):
    return W if D <= 0 else (T if D == 1 else L)


def cos_out(D, t):
    g = F(2) - F(2) * t * D
    return W if g > 0 else (T if g == 0 else L)


def tie_recall(S, Tc, K):
    # S = #nongolds strictly closer than gold, Tc = #tied.
    # Uniform tie priorities: gold uniform among Tc+1 tied slots.
    if S >= K:
        return F(0)
    return min(F(1), F(K - S, Tc + 1))


# Checker A: joint (A, composition) enumeration, exact Fractions.
def expected_A(N, K, method, t):
    n = N - 1
    total = F(0)
    for A, pa in PA.items():
        for n0 in range(n + 1):
            for n1 in range(n - n0 + 1):
                n2 = n - n0 - n1
                w = (F(factorial(n), factorial(n0) * factorial(n1) * factorial(n2))
                     * PB[0] ** n0 * PB[1] ** n1 * PB[2] ** n2)
                S = Tc = 0
                for c, nc in ((0, n0), (1, n1), (2, n2)):
                    o = sign_out(c - A) if method == 'sign' else cos_out(c - A, t)
                    if o == L:
                        S += nc
                    elif o == T:
                        Tc += nc
                total += pa * w * tie_recall(S, Tc, K)
    return total


# Checker B: coordinator-formula replication (condition on gold, multinomial, average).
def topk_multinom(n, u, v, K):
    w = 1 - u - v
    ans = F(0)
    for i in range(n + 1):
        for j in range(n - i + 1):
            k = n - i - j
            wt = (F(factorial(n), factorial(i) * factorial(j) * factorial(k))
                  * u ** i * v ** j * w ** k)
            ans += wt * tie_recall(i, j, K)
    return ans


def expected_B(N, K, method, t):
    cond = []
    for eps in product((-1, 1), repeat=2):
        A = sum(e == 1 for e in eps)
        ws = ts = 0
        for dl in product((-1, 1), repeat=2):
            B = sum(d == 1 for d in dl)
            o = sign_out(B - A) if method == 'sign' else cos_out(B - A, t)
            ws += (o == L)
            ts += (o == T)
        cond.append(topk_multinom(N - 1, F(ws, 4), F(ts, 4), K))
    return sum(cond, F(0)) / 4


fails = []
def check(name, cond):
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


# 1. Per-cell coupling table: all (A,B) x all t reps (finite exhaustive witness).
for tname, t in T_REPS.items():
    ok = True
    for A in (0, 1, 2):
        for B in (0, 1, 2):
            s, c = sign_out(B - A), cos_out(B - A, t)
            ok &= (c >= s) if t < 1 else (c == s) if t == 1 else (c <= s)
    check(f'coupling-cells {tname}', ok)

# 2. Same-priority permutation check, N=3, all joint states x all 6 priority orders.
for tname, t in T_REPS.items():
    for K in (1, 2, 3):
        ok = True
        for eps in product((-1, 1), repeat=2):
            A = sum(e == 1 for e in eps)
            for dls in product(product((-1, 1), repeat=2), repeat=2):
                Bs = [sum(d == 1 for d in dl) for dl in dls]
                so = [sign_out(B - A) for B in Bs]
                co = [cos_out(B - A, t) for B in Bs]
                for perm in permutations((0, 1, 2)):
                    rank = {doc: r for r, doc in enumerate(perm)}  # lower = better priority
                    def incl(outs):
                        prec = sum((o == L) or (o == T and rank[j + 1] < rank[0])
                                   for j, o in enumerate(outs))
                        return prec < K
                    si, ci = incl(so), incl(co)
                    ok &= (ci >= si) if t <= 1 else (ci <= si)
                    # t==1 included in >= (equality holds; asserted separately)
        check(f'perm-N3-K{K} {tname}', ok)
# t==1 pointwise equality (stronger than >=).
for K in (1, 2, 3):
    ok = True
    for eps in product((-1, 1), repeat=2):
        A = sum(e == 1 for e in eps)
        for dls in product(product((-1, 1), repeat=2), repeat=2):
            Bs = [sum(d == 1 for d in dl) for dl in dls]
            if any(sign_out(B - A) != cos_out(B - A, F(1)) for B in Bs):
                ok = False
    check(f'perm-N3-K{K} t1-exact-equality', ok)

# 3. Hand derivation, N=2/K=1: recall = P(W)+P(T)/2 from 3x3 (A,B) table.
# P(D<=0)=11/16, P(D=1)=1/4, P(D=2)=1/16 (marginals of PAxPB).
PD = {0: F(11, 16), 1: F(1, 4), 2: F(1, 16)}
hand = {'sign': PD[0] + PD[1] / 2, 't025': F(1), 't05': F(15, 16) + F(1, 16) / 2,
        't075': F(15, 16), 't1': PD[0] + PD[1] / 2, 't10': PD[0]}
for name, want in hand.items():
    got = expected_A(2, 1, 'sign', F(1)) if name == 'sign' \
        else expected_A(2, 1, 'cos', T_REPS[name])
    check(f'hand-N2K1 {name}={want}', got == want)

# 4. Corrected coordinator values, two independent computations (A and B agree + match).
known = {6: {'sign': F(1763, 2048), 't05': F(4067, 4096), 't10': F(1483, 2048)},
         10: {'sign': F(475849, 655360), 't05': F(2535999, 2621440),
              't10': F(36089, 65536)}}
for N, ks in known.items():
    for name, want in ks.items():
        m, t = ('sign', F(1)) if name == 'sign' else ('cos', T_REPS[name])
        a, b = expected_A(N, 3, m, t), expected_B(N, 3, m, t)
        check(f'N{N}K3 {name} A==B=={want}', a == b == want)

# 5. All-N/K dominance sweep incl. strict-vs-degenerate pattern.
sweep = {}
for N in (2, 3, 4, 5, 6):
    for K in range(1, N + 1):
        s = expected_A(N, K, 'sign', F(1))
        row = {}
        for tname, t in T_REPS.items():
            c = expected_A(N, K, 'cos', t)
            b = expected_B(N, K, 'cos', t)  # second formulation agrees everywhere
            if t < 1:
                good = (c == s) if K == N else (c > s)
            elif t == 1:
                good = (c == s)
            else:
                good = (c == s) if K == N else (c < s)
            row[tname] = str(c)
            if not (good and b == c):
                fails.append(f'sweep N{N}K{K} {tname}: sign={s} cos={c} B={b}')
        sweep[f'N{N}K{K}'] = {'sign': str(s), **row}
check('sweep-all-ordering-and-AB-agree', not any(f.startswith('sweep') for f in fails))
# Degenerate edges: N=1 always 1; K>=N always 1.
check('edge-N1', all(expected_A(1, 1, m, t) == 1
      for m, t in [('sign', F(1))] + [('cos', t) for t in T_REPS.values()]))
check('edge-KgeN', all(expected_A(N, N, m, t) == 1
      for N in (2, 3, 4) for m, t in [('sign', F(1))] + [('cos', t) for t in T_REPS.values()]))

# 6. FALSE-CLAIM NEGATIVE CONTROL: unconditional multinomial (the original error).
# Marginal pairwise for sign: P(W)=11/16, P(T)=1/4; treat as iid across nongolds.
false_val = topk_multinom(5, F(11, 16), F(1, 4), 3)
check('control-unconditional-mismatches-N6K3-sign', false_val != F(1763, 2048))

res = {'known_N6_N10_K3': {str(N): {k: str(v) for k, v in ks.items()}
                           for N, ks in known.items()},
       'hand_N2K1': {k: str(v) for k, v in hand.items()},
       'sweep': sweep,
       'negative_control': {'unconditional_multinom_N6K3_sign': str(false_val),
                            'corrected_sign': '1763/2048',
                            'mismatch': bool(false_val != F(1763, 2048))},
       'status': 'ALL-PASS' if not fails else 'FAILURES',
       'failures': fails}
with open('results.json', 'w') as f:
    f.write(json.dumps(res, indent=2) + '\n')
print('FAILURES:', fails if fails else 'none')
raise SystemExit(1 if fails else 0)
