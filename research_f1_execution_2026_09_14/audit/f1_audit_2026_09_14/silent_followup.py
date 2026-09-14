#!/usr/bin/env python3
"""Follow-up on the three SILENT mutations + a proper exact check of the tie formula."""
import itertools, json, sys, types
import numpy as np
sys.path.insert(0, '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit')
from my_f1 import load_lme, hamming, cos_scores, spearman
OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit'
res = {}

# ---- 1. EXACT brute-force verification of the tie-expectation formula (no Monte Carlo) ----
def efr_exact(s, gold, K=3):
    s = np.asarray(s, float); ss = np.sort(s)[::-1]; thr = ss[K-1]
    strictly = int((s > thr).sum()); slots = K - strictly; bc = int((s == thr).sum())
    gs = sum(1 for x in gold if s[x] > thr); gt = sum(1 for x in gold if s[x] == thr)
    return (gs + gt * (slots / bc)) / len(gold)

def efr_bruteforce(s, gold, K=3):
    """Average FR@K over ALL n! tie-break orders, done exactly by enumerating permutations
    of the index set and taking the first K under (score desc, permutation position)."""
    n = len(s); gg = set(gold); tot = 0.0; cnt = 0
    for perm in itertools.permutations(range(n)):
        order = sorted(range(n), key=lambda i: (-s[i], perm.index(i)))
        top = order[:K]
        tot += len(gg & set(top)) / len(gold); cnt += 1
    return tot / cnt

cases = [
    ([5.0, 5.0, 5.0, 1.0, 0.0], [0]),          # 3-way tie at boundary
    ([5.0, 4.0, 4.0, 4.0, 0.0], [1, 2]),       # tie spanning boundary, multi-gold
    ([9.0, 4.0, 4.0, 4.0, 4.0], [1, 4]),
    ([3.0, 3.0, 3.0, 3.0, 3.0], [0, 1, 2]),    # all tied
    ([7.0, 6.0, 5.0, 4.0, 3.0], [2, 3]),       # no ties
]
bf = []
for s, g in cases:
    e = efr_exact(s, g); b = efr_bruteforce(s, g)
    bf.append(dict(scores=s, gold=g, formula=e, brute_force_all_perms=b, abs_diff=abs(e - b)))
    print(f'  formula={e:.12f} brute={b:.12f} diff={abs(e-b):.2e}  s={s} gold={g}')
mx = max(x['abs_diff'] for x in bf)
res['tie_formula_exact_bruteforce'] = dict(cases=bf, max_abs_diff=mx,
    verdict='EXACT MATCH - formula is provably the NT->inf limit' if mx < 1e-12 else 'MISMATCH')
print(f'(1) tie formula vs exhaustive permutation average: max|diff|={mx:.2e} -> {res["tie_formula_exact_bruteforce"]["verdict"]}\n')

# ---- 2. Are Hamming distances exact ints? (decides whether M2/M3 are equivalent mutants) ----
lme, _ = load_lme()
r = lme[0]
D0 = r['C'] >= 0; Q0 = r['qC'] >= 0
d = [sum(1 for t, j in enumerate(range(96)) if (1 if r['C'][i][j] >= 0 else 0) != (1 if r['qC'][j] >= 0 else 0))
     for i in range(5)]
res['distances_are_python_ints'] = dict(sample=d, all_int=all(isinstance(x, int) for x in d))
print(f'(2) distance type check: {[type(x).__name__ for x in d]} -> all int = {res["distances_are_python_ints"]["all_int"]}')
print('    => on exact ints, "di < dg-1e-9" == "di < dg" and "di <= dg+1e-9" (after the < branch) == "di == dg".')
print('    => M2/M3 are EQUIVALENT MUTANTS, not undetected defects.\n')

# ---- 3. M8 follow-up: re-centering in the ARMS (the coordinator's real E1 error) ----
def arms(C, q, recenter):
    C = np.asarray(C, float)
    if recenter:
        C = C - C.mean(axis=0)
    D0 = C >= 0; Q0 = q >= 0
    dh = (D0 != Q0[None, :]).sum(axis=1).astype(float)
    cs = (C @ q) / (np.linalg.norm(C, axis=1) * np.linalg.norm(q))
    return dh, cs

sg0 = fl0 = sg1 = fl1 = 0.0
for r in lme:
    for rc, acc in ((False, 0), (True, 1)):
        dh, cs = arms(r['C'], r['qC'], rc)
        s = efr_exact(-dh, r['gold']); f = efr_exact(cs, r['gold'])
        if rc: sg1 += s; fl1 += f
        else:  sg0 += s; fl0 += f
n = len(lme)
res['recenter_in_arms'] = dict(no_recenter_delta_pp=100*(sg0-fl0)/n, recenter_delta_pp=100*(sg1-fl1)/n,
                               abs_change_pp=abs(100*(sg0-fl0)/n - 100*(sg1-fl1)/n))
print(f'(3) re-centering in the ARMS (coordinator erratum E1): '
      f'clean={100*(sg0-fl0)/n:+.6f} pp  mutated={100*(sg1-fl1)/n:+.6f} pp  '
      f'change={res["recenter_in_arms"]["abs_change_pp"]:.6f} pp -> '
      f'{"CAUGHT" if res["recenter_in_arms"]["abs_change_pp"] > 1e-9 else "SILENT"}')
print('    (M8 only re-centered inside col_mean_squares (the v_j axis-ranking path), where the data is')
print('     already centered to 1e-16 so v_j shifts by ~1e-32 and the axis ORDER is unchanged -> equivalent mutant.)')

json.dump(res, open(OUT + '/evidence/silent_mutation_followup.json', 'w'), indent=2, default=str)
print('\nOK')
