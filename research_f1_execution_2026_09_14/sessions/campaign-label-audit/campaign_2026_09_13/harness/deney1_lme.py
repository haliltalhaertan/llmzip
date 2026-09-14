#!/usr/bin/env python3
"""Deney 1 (Muse roadmap Design 1): multi-split robustness of learned axis selection.
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Extends R2B (single split) to 10 stratified 50/50 splits, 10 fresh random seeds per split,
repaired SPREAD construction (rank-linspace, eff_k==k), per-split bootstrap CI vs best-seed,
and validity gates. Reuses the exact R2B machinery: same pkls, same tie protocol (per-question
lex-ordinal priorities, 20 nuisance trials), same utility formulas.
"""
import hashlib, json, pickle, time, csv
import numpy as np
from pathlib import Path
from collections import Counter

BASE = Path('C:/Users/MDP/dev/llmzip-work')
NPZ = BASE/'pilots/axis_attack_2026-09-12/per_axis_matrices.npz'
PILOT = BASE/'pilots/axis_attack_2026-09-12/pilot_results.json'
PKLDIR = BASE/'regen/lme/cache_repr'
DATASET = BASE/'drive/longmemeval_s_cleaned.json'
QLEVEL = BASE/'drive/t4c3/V52_T4C3_question_level.csv'
OUTDIR = BASE/'pilots/axis_attack_2026-09-12/round3'
OUT = OUTDIR/'deney1_lme_details.json'

K_LIST = [32, 48, 64]
NSALT = 10          # 10 stratified 50/50 splits
NT = 20             # nuisance tie trials
K = 3               # top-3
NBOOT = 2000

def rand_seeds(split_idx):
    """10 fresh seeds per split; declared literal formula."""
    return [91000 + split_idx * 10 + j for j in range(10)]

t0 = time.time()
OUTDIR.mkdir(parents=True, exist_ok=True)

# ---- lex ordinals over ALL 500 dataset qids (same as R2B/frozen protocol) ----
data = json.loads(DATASET.read_text())
allq = sorted(str(x['question_id']) for x in data)
lex = {q: i for i, q in enumerate(allq)}
assert len(allq) == 500, len(allq)
del data

z = np.load(NPZ)
alone, drop, delta = z['alone'], z['drop'], z['delta']
var_rank = z['var_rank']
qids = [str(q) for q in z['qids']]
assert alone.shape == (470, 96), alone.shape
qi_of = {q: i for i, q in enumerate(qids)}

res = json.loads(PILOT.read_text())
nat_stored = res['per_question_native_FR']
assert len(nat_stored) == 470

# question types
qtype = {}
with open(QLEVEL, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        qtype[row['question_id']] = row['question_type']
assert sum(1 for q in qids if q in qtype) == 470

# ---- stratified 50/50 splits (10 salts) ----
def make_split(s):
    """Within each question_type, sort by salted sha256 and deal alternately."""
    tr, te = [], []
    for t in sorted(set(qtype[q] for q in qids)):
        qs = sorted([q for q in qids if qtype[q] == t],
                    key=lambda q: hashlib.sha256(f'deney1|{s}|{q}'.encode()).hexdigest())
        for i, q in enumerate(qs):
            (tr if i % 2 == 0 else te).append(q)
    return sorted(tr), sorted(te)

splits = [make_split(s) for s in range(NSALT)]
for s, (tr, te) in enumerate(splits):
    assert len(set(tr) & set(te)) == 0 and len(tr) + len(te) == 470
    print(f'split {s}: train={len(tr)} test={len(te)} qtype_test={dict(Counter(qtype[q] for q in te))}', flush=True)

# ---- load pkls once; precompute D0/Q0/gold/prios/pool ----
D0, Q0, GOLD, PR, N = {}, {}, {}, {}, {}
pool = np.zeros((470, 96), dtype=np.int32)
for qi, qid in enumerate(qids):
    with open(PKLDIR / (qid + '.pkl'), 'rb') as f:
        o = pickle.load(f)
    C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
    g = np.asarray(o['gold']).ravel()
    D = C >= 0; Q = qC >= 0
    D0[qid] = D; Q0[qid] = Q; GOLD[qid] = g
    N[qid] = len(C)
    lx = lex[qid]
    PR[qid] = [np.random.default_rng(5_100_000 + lx * 100_000 + t * 100 + 99).random(len(C)) for t in range(NT)]
    pool[qi] = np.count_nonzero(D == Q[None, :], axis=0)
print(f'loaded 470 pkls ({time.time()-t0:.0f}s)', flush=True)

def fr_subset(qid, cols):
    D = D0[qid]; Q = Q0[qid]; g = GOLD[qid]
    d = np.count_nonzero(D[:, cols] != Q[cols][None, :], axis=1)
    gg = set(map(int, np.ravel(g)))
    tot = 0.0
    for p in PR[qid]:
        order = np.lexsort((p, d))
        tot += len(set(map(int, order[:K])) & gg) / len(gg)
    return tot / NT

# ---- GATE 1: native recompute vs stored ----
recomp = {q: fr_subset(q, np.arange(96)) for q in qids}
maxdiff = max(abs(recomp[q] - nat_stored[q]) for q in qids)
print(f'GATE1 native recompute: max_abs_diff={maxdiff:.3e} '
      f'mean_recomp={np.mean(list(recomp.values())):.10f} mean_stored={np.mean([nat_stored[q] for q in qids]):.10f}',
      flush=True)
assert maxdiff < 1e-12, 'GATE1 FAILED'

# ---- per-split run ----
all_out = {'labels': ['[LOCAL EXPLORATORY PILOT]', '[NOT PREREGISTERED]', '[DISCLOSE-BEFORE-USE]',
                      'Deney1 = R2B multi-split robustness (Muse roadmap Design 1)'],
           'numpy': np.__version__, 'nt': NT, 'k_top': K, 'n_splits': NSALT,
           'random_seed_formula': 'seeds = 91000 + 10*split + j, j=0..9',
           'gate1_native': {'max_abs_diff': float(maxdiff),
                            'mean_all': float(np.mean(list(recomp.values())))},
           'splits': [], 'summary': {}}

native_mean_all = float(np.mean(list(recomp.values())))
summary_rows = []
for s, (train_q, test_q) in enumerate(splits):
    tr_idx = np.array([qi_of[q] for q in train_q])
    nat_tr = np.array([nat_stored[q] for q in train_q])
    te_idx = np.array([qi_of[q] for q in test_q])
    nat_te = np.array([nat_stored[q] for q in test_q])

    # ---- utilities (train-only) ----
    U_delta = delta[tr_idx].mean(axis=0)
    U_drop = (nat_tr[:, None] - drop[tr_idx]).mean(axis=0)
    U_alone = (alone[tr_idx] * pool[tr_idx] / 3).mean(axis=0)
    U_var = (-var_rank[tr_idx].astype(float)).mean(axis=0)
    U = {'delta': U_delta, 'drop': U_drop, 'alone': U_alone, 'var': U_var}

    # provenance discrimination: train-only top-64 must differ from full-data top-64
    Ufull_drop = (np.array([nat_stored[q] for q in qids])[:, None] - drop).mean(axis=0)
    top_tr = set(np.argsort(U_drop)[::-1][:64].tolist())
    top_fu = set(np.argsort(Ufull_drop)[::-1][:64].tolist())
    ov = len(top_tr & top_fu)

    # ---- arms ----
    arms = {}
    for uname, u in U.items():
        for k in K_LIST:
            arms[f'{uname}{k}'] = np.sort(np.argsort(u)[::-1][:k]).astype(int)
    # repaired SPREAD: rank-linspace over descending train-variance order, eff_k==k asserted
    order_desc = np.argsort(U_var)[::-1]
    for k in K_LIST:
        pos = np.round(np.linspace(0, 95, k)).astype(int)
        assert len(np.unique(pos)) == k, f'SPREAD{k} positions not distinct'
        cols = np.sort(order_desc[pos]).astype(int)
        assert len(cols) == k
        arms[f'SPREAD{k}'] = cols
    rcols = {}
    for j, sd in enumerate(rand_seeds(s)):
        for k in K_LIST:
            c = np.sort(np.random.default_rng(sd).choice(96, k, replace=False)).astype(int)
            assert len(c) == k
            rcols[f'RANDOM{k}_s{sd}'] = c
            arms[f'RANDOM{k}_s{sd}'] = c

    # ---- evaluate on test ----
    per_q_test = {}
    for name, cols in arms.items():
        per_q_test[name] = np.array([fr_subset(q, cols) for q in test_q])
    per_q_tr = {}
    for name in [f'{u}{k}' for u in U for k in K_LIST] + [f'SPREAD{k}' for k in K_LIST]:
        per_q_tr[name] = np.array([fr_subset(q, arms[name]) for q in train_q])

    test_fr = {n: float(v.mean()) for n, v in per_q_test.items()}
    rmean = {k: float(np.mean([test_fr[f'RANDOM{k}_s{sd}'] for sd in rand_seeds(s)])) for k in K_LIST}
    rmax = {k: float(max(test_fr[f'RANDOM{k}_s{sd}'] for sd in rand_seeds(s))) for k in K_LIST}
    nat_test = float(np.mean([nat_stored[q] for q in test_q]))

    # ---- primary estimand: drop64/alone64 vs BEST random seed, bootstrap CI ----
    def gap_vs_best(armname, k):
        d = per_q_test[armname]
        R = np.array([per_q_test[f'RANDOM{k}_s{sd}'] for sd in rand_seeds(s)])
        gap = float(d.mean() - max(R[j].mean() for j in range(len(rand_seeds(s)))))
        rng = np.random.default_rng(777000 + s)
        nn = len(test_q)
        diffs = np.empty(NBOOT)
        for b in range(NBOOT):
            idx = rng.integers(0, nn, nn)
            md = d[idx].mean()
            mb = max(R[j][idx].mean() for j in range(len(rand_seeds(s))))
            diffs[b] = md - mb
        lo, hi = np.percentile(diffs, [5, 95])
        return gap, float(lo), float(hi), diffs

    g_drop64, lo_d, hi_d, _ = gap_vs_best('drop64', 64)
    g_alone64, lo_a, hi_a, _ = gap_vs_best('alone64', 64)
    g_drop48 = float(per_q_test['drop48'].mean() - rmax[48])
    g_alone48 = float(per_q_test['alone48'].mean() - rmax[48])
    g_drop32 = float(per_q_test['drop32'].mean() - rmax[32])
    g_alone32 = float(per_q_test['alone32'].mean() - rmax[32])

    # var-control validity: var worst among learned families at every k?
    var_worst = {}
    for k in K_LIST:
        fam = {u: test_fr[f'{u}{k}'] for u in ['delta', 'drop', 'alone', 'var', 'SPREAD']}
        var_worst[str(k)] = bool(min(fam, key=lambda x: fam[x]) == 'var')

    # W/T/L vs best-seed mean for drop64
    R64 = np.array([per_q_test[f'RANDOM64_s{sd}'] for sd in rand_seeds(s)])
    d = per_q_test['drop64'] - R64.max(axis=0)
    W = int((d > 1e-12).sum()); T = int((np.abs(d) <= 1e-12).sum()); L = int((d < -1e-12).sum())

    row = {'split': s, 'n_test': len(test_q),
           'native_test': nat_test,
           'drop64': test_fr['drop64'], 'alone64': test_fr['alone64'],
           'RANDOM64_best': rmax[64], 'RANDOM64_mean': rmean[64],
           'gap64_vs_best_pp': g_drop64 * 100, 'gap64_ci90': [lo_d * 100, hi_d * 100],
           'gap64_alone_vs_best_pp': g_alone64 * 100, 'gap64_alone_ci90': [lo_a * 100, hi_a * 100],
           'gap48_drop_vs_best_pp': g_drop48 * 100, 'gap48_alone_vs_best_pp': g_alone48 * 100,
           'gap32_drop_vs_best_pp': g_drop32 * 100, 'gap32_alone_vs_best_pp': g_alone32 * 100,
           'WTL_drop64_vs_best_seed': [W, T, L],
           'var_worst': var_worst,
           'top64_train_full_overlap': int(ov)}
    summary_rows.append(row)
    print(f"SPLIT {s}: native={nat_test:.4f} drop64={test_fr['drop64']:.4f} "
          f"alone64={test_fr['alone64']:.4f} rand_best64={rmax[64]:.4f} rand_mean64={rmean[64]:.4f} "
          f"gap64_vs_best={g_drop64*100:+.2f}pp CI90=[{lo_d*100:+.2f},{hi_d*100:+.2f}] "
          f"var_worst={var_worst}", flush=True)

    all_out['splits'].append({
        's': s, 'train_qids': train_q, 'test_qids': test_q,
        'utilities_top5': {k: [int(i) for i in np.argsort(v)[::-1][:5]] for k, v in U.items()},
        'arms': {n: {'test_FR': test_fr[n], 'cols': [int(c) for c in arms[n]]} for n in arms},
        'native_test': nat_test, 'random_seeds': rand_seeds(s),
        'run': row,
        'per_q_test': {n: [float(x) for x in per_q_test[n]] for n in per_q_test},
    })

# ---- cross-split summary ----
import statistics
g64 = [r['gap64_vs_best_pp'] for r in summary_rows]
g64a = [r['gap64_alone_vs_best_pp'] for r in summary_rows]
wins64 = sum(1 for x in g64 if x > 0)
wins64a = sum(1 for x in g64a if x > 0)
summ = {
    'drop64_gap_vs_best_pp': {'mean': float(np.mean(g64)), 'median': float(np.median(g64)),
                              'range': [float(min(g64)), float(max(g64))],
                              'wins': f'{wins64}/{NSALT}'},
    'alone64_gap_vs_best_pp': {'mean': float(np.mean(g64a)), 'median': float(np.median(g64a)),
                               'range': [float(min(g64a)), float(max(g64a))],
                               'wins': f'{wins64a}/{NSALT}'},
    'drop48_gap_mean_pp': float(np.mean([r['gap48_drop_vs_best_pp'] for r in summary_rows])),
    'alone48_gap_mean_pp': float(np.mean([r['gap48_alone_vs_best_pp'] for r in summary_rows])),
    'drop32_gap_mean_pp': float(np.mean([r['gap32_drop_vs_best_pp'] for r in summary_rows])),
    'alone32_gap_mean_pp': float(np.mean([r['gap32_alone_vs_best_pp'] for r in summary_rows])),
    'var_worst_all': all(all(r['var_worst'][k] for k in ('32', '48', '64')) for r in summary_rows),
    'top64_overlap_min': int(min(r['top64_train_full_overlap'] for r in summary_rows)),
}
all_out['summary'] = summ
OUT.write_text(json.dumps(all_out), encoding='utf-8')
print('SUMMARY ' + json.dumps(summ), flush=True)
print(f'wrote {OUT} ({OUT.stat().st_size} bytes, {time.time()-t0:.0f}s)', flush=True)
print('DENEY1_LME_DONE')
