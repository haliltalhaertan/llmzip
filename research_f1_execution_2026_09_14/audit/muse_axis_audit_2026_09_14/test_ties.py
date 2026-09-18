"""STEP 3c: brute-force check of their fr_at_k_exact vs permutation-average truth.

Truth definition: for one query with scores S (higher better), all total orders
consistent with S (ties broken uniformly at random); FR@K = |gold in top K|/|gold|
averaged over all such orders. Enumerate the tied block's permutations exactly.
"""
import sys, itertools, numpy as np
sys.path.insert(0, '/home/mdp/muse-work/audit-axis')
from their_core_copy import fr_at_k_exact

def brute(S, gold, K=3):
    S = np.asarray(S, float); gold = list(gold)
    N = len(S)
    kk = min(K, N)
    # group indices by score value (exact equality, NaN each its own group -> treat NaN as -inf rank last)
    order_vals = sorted(set(v for v in S if not np.isnan(v)), reverse=True)
    # expand: blocks from best to worst; NaNs form the final block
    blocks = []
    for v in order_vals:
        blocks.append([i for i in range(N) if S[i] == v])
    nanb = [i for i in range(N) if np.isnan(S[i])]
    if nanb:
        blocks.append(nanb)
    # enumerate all global orders consistent with blocks
    total, cnt = 0.0, 0
    for perm_lists in itertools.product(*(itertools.permutations(b) for b in blocks)):
        seq = [i for b in perm_lists for i in b][:kk]
        hits = len(set(seq) & set(gold))
        total += hits / len(gold); cnt += 1
    return total / cnt

rng = np.random.default_rng(0)
fails = 0
# 1) randomized fuzz: integer scores (heavy ties, like Hamming) + float scores
for t in range(300):
    N = int(rng.integers(4, 8))
    if t % 2 == 0:
        S = rng.integers(0, 5, size=(N, 1)).astype(float)  # hamming-like ties
    else:
        S = np.round(rng.normal(size=(N, 1)), 1)  # float ties via rounding
    ng = int(rng.integers(1, 3))
    gold = rng.choice(N, size=ng, replace=False)
    Gmask = np.zeros((N, 1), bool); Gmask[gold, 0] = True
    got = float(fr_at_k_exact(S, Gmask, np.array([ng]))[0])
    exp = brute(S[:, 0], gold)
    if abs(got - exp) > 1e-12:
        fails += 1; print("MISMATCH", S[:, 0], gold, got, exp)
print("fuzz mismatches:", fails, "/300")

# 2) hand edge cases
cases = [
    (np.array([3., 2., 2., 2., 1.]), [1], "1 gold in 3-way tie for 2 slots"),
    (np.array([3., 2., 2., 2., 1.]), [0], "gold strictly in"),
    (np.array([3., 2., 2., 2., 1.]), [4], "gold strictly out"),
    (np.array([1., 1., 1., 1., 1.]), [0, 3], "all tied, 2 gold"),
    (np.array([5., 4., 3.]), [2], "no ties, gold 3rd"),
    (np.array([5., 4., 3.]), [0, 1, 2], "no ties, all gold"),
    (np.array([2., 2., 2.]), [1], "N=K all tied"),
    (np.array([2., 1.]), [0], "N<K"),
    (np.array([-3., -3., -5., -5., -5.]), [2, 4], "neg-hamming-like, golds in tie"),
]
for S, gold, tag in cases:
    N = len(S); Gmask = np.zeros((N, 1), bool); Gmask[gold, 0] = True
    got = float(fr_at_k_exact(S[:, None], Gmask, np.array([len(gold)]))[0])
    exp = brute(S, gold)
    flag = "OK " if abs(got - exp) < 1e-12 else "FAIL"
    print(f"{flag} {tag}: formula={got:.6f} brute={exp:.6f}")
print("DONE")
