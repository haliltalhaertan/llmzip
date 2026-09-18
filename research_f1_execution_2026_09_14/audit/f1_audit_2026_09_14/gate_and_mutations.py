#!/usr/bin/env python3
"""AUDIT step 3+4: (a) apply the contract C3 headline gate the coordinator never called;
(b) verify his tie-expectation formula against a large-NT permutation average;
(c) ADVERSARIAL MUTATION TESTING of his own f1_competition.py."""
import copy, glob, importlib.util, json, pickle, random, sys, types
import numpy as np
sys.path.insert(0, '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit')
from my_f1 import load_lme, load_realtalk, load_perltqa, spearman, topbot64, hamming, cos_scores

OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit'
COORD = OUT + '/coord_copy/f1_competition.py'
res = {}

# ---------------------------------------------------------------- (a) C3 GATE
# Contract C3: headline gates must reproduce to <=1e-12 BEFORE Claim-D computation.
# "A failed gate stops that benchmark." (E1_PREANALYSIS_SPEC_V2.md, 'Frozen inputs and gate')
GATES = {'LME': (0.5419751773049645, 0.4415957446808511),
         'REALTALK': (0.22477507598784194, 0.17253405381064954),
         'PERLTQA': (0.488941994930817, 0.551692074528853)}
MEASURED = {  # from my own frozen MY_NUMBERS.md run (exact-expectation FR@3)
    'LME': (0.5421335697399526, 0.4415957446808511),
    'PERLTQA': (0.48894479616364206, 0.551692074528853),
    'REALTALK': (0.22553482307028402, 0.17253405381064957)}
gate = {}
for b, (sr, fr) in GATES.items():
    s, f = MEASURED[b]
    ds, df = abs(s - sr), abs(f - fr)
    gate[b] = dict(sign_measured=s, sign_ref=sr, sign_absdiff=ds, sign_pass_1e_12=bool(ds <= 1e-12),
                   float_measured=f, float_ref=fr, float_absdiff=df, float_pass_1e_12=bool(df <= 1e-12),
                   benchmark_gate_pass=bool(ds <= 1e-12 and df <= 1e-12))
    print(f'C3 GATE {b:9} SIGN |d|={ds:.3e} {"PASS" if ds<=1e-12 else "FAIL"}   '
          f'FLOAT |d|={df:.3e} {"PASS" if df<=1e-12 else "FAIL"}  -> benchmark {"PASS" if gate[b]["benchmark_gate_pass"] else "FAIL (contract says STOP)"}')
res['C3_headline_gate'] = gate

# ---------------------------------------------------------------- (b) tie formula vs permutations
def efr_exact(s, gold, K=3):
    s = np.asarray(s, float); ss = np.sort(s)[::-1]; thr = ss[K-1]
    strictly = int((s > thr).sum()); slots = K - strictly; bc = int((s == thr).sum())
    gs = sum(1 for x in gold if s[x] > thr); gt = sum(1 for x in gold if s[x] == thr)
    return (gs + gt * (slots / bc)) / len(gold)

def efr_perm(s, gold, NT, seed, K=3):
    s = np.asarray(s, float); gg = set(int(x) for x in gold)
    rng = np.random.default_rng(seed); n = len(s); acc = []
    for _ in range(NT):
        p = rng.random(n)
        top = np.lexsort((p, -s))[:K]
        acc.append(len(gg & set(int(t) for t in top)) / len(gg))
    return float(np.mean(acc))

lme, _ = load_lme()
worst = 0.0; checked = 0
for r in lme[:60]:
    D0 = r['C'] >= 0; Q0 = r['qC'] >= 0
    dh = hamming(D0, Q0).astype(float)
    e = efr_exact(-dh, r['gold']); m = efr_perm(-dh, r['gold'], 20000, 12345)
    worst = max(worst, abs(e - m)); checked += 1
res['tie_formula_vs_20000_perms'] = dict(queries=checked, max_abs_diff=worst,
    verdict='formula is the exact NT->inf limit' if worst < 5e-3 else 'FORMULA MISMATCH')
print(f'\n(b) tie formula vs 20000-perm average over {checked} LME queries: max|diff|={worst:.2e} -> '
      f'{res["tie_formula_vs_20000_perms"]["verdict"]}')

# ---------------------------------------------------------------- (c) MUTATIONS
src = open(COORD).read()

def load_mod(text, name):
    mod = types.ModuleType(name)
    mod.__dict__['__name__'] = name
    exec(compile(text, name, 'exec'), mod.__dict__)
    return mod

def run_lme(mod, n=470):
    """Coefficients using HIS module end-to-end on real LME rows (Delta from my exact FR@3)."""
    rows = []
    for r in lme[:n]:
        C = r['C']; q = r['qC']
        D0 = C >= 0; Q0 = q >= 0
        dh = hamming(D0, Q0).astype(float)
        cs = cos_scores(C, q)
        delta = efr_exact(-dh, r['gold']) - efr_exact(cs, r['gold'])
        rows.append(mod.query_row(C.tolist(), q.tolist(), list(r['gold']), delta,
                                  k=64, qid=r['qid'], benchmark='LME', cluster=r['qid']))
    s = mod.benchmark_summary(rows)
    return s['rho_strict'], s['rho_tie'], rows

base_mod = load_mod(src, 'f1_base')
b_strict, b_tie, base_rows = run_lme(base_mod)
print(f'\n(c) BASELINE via coordinator module: strict={b_strict!r} tie={b_tie!r}')
res['mutation_baseline'] = dict(strict=b_strict, tie=b_tie,
    matches_my_independent_LME=bool(abs(b_strict - 0.1416251737011647) < 1e-12
                                    and abs(b_tie - 0.14069387548880735) < 1e-12))
print('    matches my independent LME numbers at 1e-12:', res['mutation_baseline']['matches_my_independent_LME'])

MUTS = [
 ('M1_swap_TOP_BOT', 'return order[:k], order[-k:]', 'return order[-k:], order[:k]'),
 ('M2_tie_uses_leq', 'elif di == dg:', 'elif di <= dg + 1e-9:'),
 ('M3_strict_tolerance', 'if di < dg:', 'if di < dg - 1e-9:'),
 ('M4_mingold_noop', 'dmin = min(d[g] for g in G)', 'dmin = d[G[0]]  # MUTANT: no min over golds'),
 ('M5_mingold_full_noop', '''        dmin = min(d[g] for g in G)
        min_s = sum(1 for di in d if di < dmin)
        min_t = sum(1 for di in d if di == dmin)''',
  '''        min_s = s_all / m   # MUTANT: min-gold control aliased to the primary
        min_t = t_all / m'''),
 ('M6_ascending_axis_order', 'order = sorted(range(len(v)), key=lambda j: -v[j])',
  'order = sorted(range(len(v)), key=lambda j: v[j])'),
 ('M7_rank_ties_ordinal', 'avg = (pos + 1 + end + 1) / 2.0', 'avg = float(pos + 1)'),
 ('M8_recenter_C', '''def col_mean_squares(C):''',
  '''def col_mean_squares(C):
    _n = len(C); _d = len(C[0])
    _mu = [sum(r[j] for r in C) / _n for j in range(_d)]
    C = [[r[j] - _mu[j] for j in range(_d)] for r in C]  # MUTANT: re-center already-centered'''),
 ('M9_gap_sign_flip', '"strict_gap": sT - sB, "tie_gap": tT - tB,', '"strict_gap": sB - sT, "tie_gap": tB - tT,'),
 ('M10_bootstrap_query_level', 'clusters.setdefault(("__q_%d" % idx if c is None else c), []).append(idx)',
  'clusters.setdefault("__q_%d" % idx, []).append(idx)  # MUTANT: always query-level'),
]
mut_res = {}
for name, old, new in MUTS:
    if old not in src:
        mut_res[name] = dict(applied=False, note='PATTERN NOT FOUND — mutation not applied')
        print(f'  {name:26} PATTERN NOT FOUND')
        continue
    text = src.replace(old, new, 1)
    try:
        m = load_mod(text, 'f1_' + name)
        if name == 'M10_bootstrap_query_level':
            rt, _ = load_realtalk()
            rows = []
            for r in rt[:300]:
                C = r['C']; q = r['qC']; D0 = C >= 0; Q0 = q >= 0
                dh = hamming(D0, Q0).astype(float); cs = cos_scores(C, q)
                delta = efr_exact(-dh, r['gold']) - efr_exact(cs, r['gold'])
                rows.append(m.query_row(C.tolist(), q.tolist(), list(r['gold']), delta,
                                        k=64, qid=r['qid'], benchmark='RT', cluster=r['cluster']))
            bb = base_mod.cluster_bootstrap(rows, n_boot=200)
            mm = m.cluster_bootstrap(rows, n_boot=200)
            ch = bb['strict_gap']['interval_95'] != mm['strict_gap']['interval_95']
            mut_res[name] = dict(applied=True, caught=bool(ch),
                                 base_ci=bb['strict_gap']['interval_95'], mut_ci=mm['strict_gap']['interval_95'])
            print(f'  {name:26} base_CI={bb["strict_gap"]["interval_95"]} mut_CI={mm["strict_gap"]["interval_95"]} '
                  f'-> {"CAUGHT" if ch else "!!! SILENT !!!"}')
            continue
        st, ti, _ = run_lme(m, 470)
        if name.startswith(('M4', 'M5')):
            bg = base_mod.benchmark_summary(base_rows, strict_key='min_strict_gap', tie_key='min_tie_gap')
            rows2 = []
            for r in lme:
                C = r['C']; q = r['qC']; D0 = C >= 0; Q0 = q >= 0
                dh = hamming(D0, Q0).astype(float); cs = cos_scores(C, q)
                delta = efr_exact(-dh, r['gold']) - efr_exact(cs, r['gold'])
                rows2.append(m.query_row(C.tolist(), q.tolist(), list(r['gold']), delta,
                                         k=64, qid=r['qid'], benchmark='LME', cluster=r['qid']))
            mg = m.benchmark_summary(rows2, strict_key='min_strict_gap', tie_key='min_tie_gap')
            ch = abs(bg['rho_strict'] - mg['rho_strict']) > 1e-12 or abs(bg['rho_tie'] - mg['rho_tie']) > 1e-12
            mut_res[name] = dict(applied=True, caught=bool(ch),
                                 base_mingold=(bg['rho_strict'], bg['rho_tie']),
                                 mut_mingold=(mg['rho_strict'], mg['rho_tie']))
            print(f'  {name:26} mingold base={bg["rho_strict"]:.10f}/{bg["rho_tie"]:.10f} '
                  f'mut={mg["rho_strict"]:.10f}/{mg["rho_tie"]:.10f} -> {"CAUGHT" if ch else "!!! SILENT !!!"}')
            continue
        ch = abs(st - b_strict) > 1e-12 or abs(ti - b_tie) > 1e-12
        mut_res[name] = dict(applied=True, caught=bool(ch), strict=st, tie=ti,
                             d_strict=st - b_strict, d_tie=ti - b_tie)
        print(f'  {name:26} strict={st!r} tie={ti!r}  d=({st-b_strict:+.3e},{ti-b_tie:+.3e}) '
              f'-> {"CAUGHT" if ch else "!!! SILENT !!!"}')
    except Exception as e:
        mut_res[name] = dict(applied=True, caught=True, exception=f'{type(e).__name__}: {e}')
        print(f'  {name:26} raised {type(e).__name__}: {e} -> CAUGHT (crash)')
res['mutations'] = mut_res
silent = [k for k, v in mut_res.items() if v.get('applied') and not v.get('caught')]
res['silent_mutations'] = silent
print('\nSILENT (undetected) mutations:', silent if silent else 'NONE')
json.dump(res, open(OUT + '/evidence/gate_and_mutations.json', 'w'), indent=2, default=str)
print('OK')
