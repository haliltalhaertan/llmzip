#!/usr/bin/env python3
"""RACE-1 Task 2 — pre-seal calibration notebook (executable record).
Reads ONLY frozen pilot artefacts (/mnt/c, read-only); writes /tmp/rb1/.
Null draws: Gaussian, seed 94301 (+offset per metric, stated below).
Gate: reproduce m1 LOO null from deney1 details within 0.05pp of m1 json.
"""
import json, numpy as np
from pathlib import Path

OUT = Path('/tmp/rb1')
R3 = Path('/mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3')
M1J = R3 / 'missing_analyses/m1_kill_null/missing1_kill_null.json'
LME = R3 / 'deney1_lme_details.json'
LOCO = R3 / 'deney1_loco_details.json'
SEED = 94301
N_MAIN = 2_000_000
DET = {'seed': SEED, 'N_main': N_MAIN}

def load(p):
    return json.loads(p.read_text(encoding='utf-8'))

def within_stats(d):
    out = {}
    for w in (32, 48, 64):
        per = []
        for sp in d['splits']:
            ms = np.array([np.mean(sp['per_q_test'][f'RANDOM{w}_s{sd}'])
                           for sd in sp['random_seeds']]) * 100.0
            per.append(ms)
        per = np.array(per)
        dem = per - per.mean(axis=1, keepdims=True)
        out[w] = {'mean_within_sd': float(per.std(axis=1, ddof=1).mean()),
                  'pooled_demeaned_sd': float(dem.std(ddof=1)),
                  'mean_range': float((per.max(axis=1) - per.min(axis=1)).mean())}
    return out

def loo_null(d):
    g = []
    for sp in d['splits']:
        ms = np.array([np.mean(sp['per_q_test'][f'RANDOM64_s{sd}'])
                       for sd in sp['random_seeds']]) * 100.0
        for j in range(len(ms)):
            g.append(ms[j] - np.delete(ms, j).max())
    g = np.array(g)
    return {'mean': float(g.mean()), 'sd': float(g.std(ddof=1)),
            'min': float(g.min()), 'max': float(g.max()),
            'winrate': float((g > 0).mean())}

def boot_rho(d, ka, kb, B=2000, seed=SEED):
    rng = np.random.default_rng(seed)
    sp = d['splits'][0]
    A = np.array(sp['per_q_test'][ka])
    Bp = np.array(sp['per_q_test'][kb])
    nq = len(A)
    idx = rng.integers(0, nq, size=(B, nq))
    mA = A[idx].mean(axis=1)
    mB = Bp[idx].mean(axis=1)
    return float(np.corrcoef(mA, mB)[0, 1])

def sim_contrast(sigs, N, seed):
    """SIGN - max(comp): X0 sd = mean(sigs); chunked (memory-safe)."""
    rng = np.random.default_rng(seed)
    s = np.array(sigs)
    K = len(s)
    out = np.empty(N)
    blk = 100_000
    for a in range(0, N, blk):
        n = min(blk, N - a)
        X = rng.standard_normal((n, K)) * s
        x0 = rng.standard_normal(n) * s.mean()
        out[a:a + n] = x0 - X.max(axis=1)
    return out

def sim_loo(sigma, rho, N, seed):
    """Exchangeable K=10 LOO gaps; returns pooled gaps array."""
    rng = np.random.default_rng(seed)
    K = 10
    C = np.full((K, K), rho)
    np.fill_diagonal(C, 1.0)
    L = np.linalg.cholesky(C)
    parts = []
    blk = 50_000
    for a in range(0, N, blk):
        n = min(blk, N - a)
        X = (rng.standard_normal((n, K)) @ L.T) * sigma
        m_all = X.max(axis=1, keepdims=True)
        # LOO gap per position: Xj - max(others)
        for j in range(K):
            omit = np.delete(X, j, axis=1).max(axis=1)
            parts.append(X[:, j] - omit)
    return np.concatenate(parts)

def pcts(g):
    qs = [1, 2.5, 5, 20, 25, 50, 75, 90, 95, 97.5, 99]
    return {str(q): float(np.percentile(g, q)) for q in qs}

# ---- GATE: m1 reproduction ----
m1 = load(M1J)
dl = load(LME)
dc = load(LOCO)
gate = {}
for bench, d, m in (('LME', dl, m1['LME']), ('LOCOMO', dc, m1['LOCOMO'])):
    r = loo_null(d)
    dm = abs(r['mean'] - m['null_mean_pp'])
    ds = abs(r['sd'] - m['null_sd_pp'])
    gate[bench] = {'recomputed': r,
                   'm1': {'mean': m['null_mean_pp'], 'sd': m['null_sd_pp']},
                   'absdiff_mean_pp': dm, 'absdiff_sd_pp': ds,
                   'PASS': bool(dm <= 0.05 and ds <= 0.05)}
DET['gate_m1_reproduction'] = gate
assert all(v['PASS'] for v in gate.values()), 'GATE FAILED'
print('GATE PASS: m1 LOO null reproduced within 0.05pp (both benchmarks)')

DET['within_seed_sd_pp'] = {'LME': within_stats(dl), 'LOCOMO': within_stats(dc)}

DET['bootstrap_aggregate_rho'] = {
    'LME': {
        'sameW64': boot_rho(dl, 'RANDOM64_s91000', 'RANDOM64_s91001'),
        'crossW_64v48': boot_rho(dl, 'RANDOM64_s91000', 'RANDOM48_s91000'),
        'spread_vs_rand64': boot_rho(dl, 'SPREAD64', 'RANDOM64_s91000')},
    'LOCOMO': {
        'sameW64': boot_rho(dc, 'RANDOM64_s91000', 'RANDOM64_s91001'),
        'crossW_64v48': boot_rho(dc, 'RANDOM64_s91000', 'RANDOM48_s91000'),
        'spread_vs_rand64': boot_rho(dc, 'SPREAD64', 'RANDOM64_s91000')}}

# ---- model validation: K=9-pool LOO, independence vs equicorrelation ----
DET['model_validation_K9'] = {}
for bench, d, m, off in (('LME', dl, m1['LME'], 0), ('LOCOMO', dc, m1['LOCOMO'], 100)):
    sig = DET['within_seed_sd_pp'][bench][64]['mean_within_sd']
    g_ind = sim_loo(sig, 0.0, 200_000, SEED + off + 11)
    rho = DET['bootstrap_aggregate_rho'][bench]['sameW64']
    g_rho = sim_loo(sig, rho, 200_000, SEED + off + 12)
    DET['model_validation_K9'][bench] = {
        'sigma_used': sig, 'rho_boot': rho,
        'empirical_m1': {'mean': m['null_mean_pp'], 'sd': m['null_sd_pp']},
        'sim_independence': {'mean': float(g_ind.mean()), 'sd': float(g_ind.std(ddof=1))},
        'sim_equicorr': {'mean': float(g_rho.mean()), 'sd': float(g_rho.std(ddof=1))}}
    v = DET['model_validation_K9'][bench]
    print(f"{bench} K9: empirical mean={v['empirical_m1']['mean']:+.3f} sd={v['empirical_m1']['sd']:.3f} | "
          f"indep mean={v['sim_independence']['mean']:+.3f} sd={v['sim_independence']['sd']:.3f} | "
          f"equicorr(r={rho:.2f}) mean={v['sim_equicorr']['mean']:+.3f} sd={v['sim_equicorr']['sd']:.3f}")

# ---- FULL sealed-set null: SIGN - max(competitors), heterogeneous per-width sd ----
# PRIMARY-MAX enumeration (v2 s5; curve-only A7 / TOP32-curve / secondaries excluded):
# LME K=40: RANDOM 30 + SPREAD 3 + BOT48 1 + TOP48/TOP64 2 + RQ32-primary 3 + PQ 1
# LOCO K=41: RANDOM 30 + SPREAD 3 + BOT 3 + TOP48 1 + RQ32-primary 3 + PQ 1
def build_sigs(bench):
    w = DET['within_seed_sd_pp'][bench]
    s32, s48, s64 = w[32]['mean_within_sd'], w[48]['mean_within_sd'], w[64]['mean_within_sd']
    sigs = [s32] * 10 + [s48] * 10 + [s64] * 10          # RANDOM panels
    sigs += [s32, s48, s64]                                # SPREAD80/64/48 -> width-matched
    if bench == 'LME':
        sigs += [s48]                                      # BOT48 (descriptive contrast)
        sigs += [s48, s64]                                 # TOP48 + TOP64(LME opt)
    else:
        sigs += [s32, s48, s64]                            # BOT80/64/48 (width order irrelevant)
        sigs += [s48]                                      # TOP48
    sigs += [s32] * 3                                      # RaBitQ32-primary x3 rotations
    sigs += [(s32 + s48 + s64) / 3.0]                      # PQ (pooled scale)
    return sigs

DET['full_null'] = {}
for bench, off in (('LME', 0), ('LOCOMO', 1000)):
    sigs = build_sigs(bench)
    assert len(sigs) == (40 if bench == 'LME' else 41), len(sigs)
    g = sim_contrast(sigs, N_MAIN, SEED + off + 21)
    DET['full_null'][bench] = {'K': len(sigs), 'mean': float(g.mean()),
                               'sd': float(g.std(ddof=1)), 'min': float(g.min()),
                               'max': float(g.max()), 'percentiles': pcts(g),
                               'P_contrast_gt0': float((g > 0).mean())}
    f = DET['full_null'][bench]
    print(f"{bench} FULL K={f['K']}: mean={f['mean']:+.3f} sd={f['sd']:.3f} "
          f"p2.5={f['percentiles']['2.5']:+.3f} p50={f['percentiles']['50']:+.3f} "
          f"p97.5={f['percentiles']['97.5']:+.3f} P(>0)={f['P_contrast_gt0']:.4f}")

# ---- sensitivities: homogeneous-sigma; full-N (/sqrt2) scale ----
DET['sensitivities'] = {}
for bench, off in (('LME', 0), ('LOCOMO', 1000)):
    sigs = build_sigs(bench)
    homo = [float(np.mean(sigs))] * len(sigs)
    gh = sim_contrast(homo, 400_000, SEED + off + 31)
    gs = sim_contrast([s / np.sqrt(2) for s in sigs], 400_000, SEED + off + 32)
    DET['sensitivities'][bench] = {
        'homogeneous_sigma': {'mean': float(gh.mean()), 'sd': float(gh.std(ddof=1)), 'pcts': pcts(gh)},
        'fullN_sqrt2_scale': {'mean': float(gs.mean()), 'sd': float(gs.std(ddof=1)), 'pcts': pcts(gs)}}
    print(f"{bench} SENS homo: mean={gh.mean():+.3f} sd={gh.std(ddof=1):.3f} p2.5={np.percentile(gh,2.5):+.3f} "
          f"p97.5={np.percentile(gh,97.5):+.3f}")
    print(f"{bench} SENS /sqrt2: mean={gs.mean():+.3f} sd={gs.std(ddof=1):.3f} p2.5={np.percentile(gs,2.5):+.3f} "
          f"p97.5={np.percentile(gs,97.5):+.3f}")

# ---- frozen lines + premium figures ----
import math
DET['lines'] = {}
for bench in ('LME', 'LOCOMO'):
    f = DET['full_null'][bench]
    p25 = f['percentiles']['2.5']
    p975 = f['percentiles']['97.5']
    kill = math.floor(p25 * 10) / 10.0          # outward (more negative), 0.1pp
    promote = 2.0                                # v1 literal retained; verified > p97.5 both benches
    assert promote > p975, (bench, promote, p975)
    delta_clear = p975 - f['mean']               # true edge so E[contrast] sits at p97.5
    delta_p80 = p975 - float(f['percentiles']['20'])  # true edge for 80% power vs promote band
    DET['lines'][bench] = {
        'kill_line_pp': kill, 'kill_basis': 'full-null 2.5th pct, rounded outward to 0.1pp',
        'promote_line_pp': promote,
        'promote_basis': 'max(full-null 97.5th rounded up, +2.0 absolute floor); floor binds',
        'null_p2.5': p25, 'null_p97.5': p975, 'null_mean': f['mean'], 'null_sd': f['sd'],
        'margin_promote_over_p97.5_pp': promote - p975,
        'premium_to_clear_expectation_pp': delta_clear,
        'premium_for_80power_pp': delta_p80}
    L = DET['lines'][bench]
    print(f"{bench} LINES: kill={L['kill_line_pp']:+.1f} (p2.5={p25:+.3f}) promote={L['promote_line_pp']:+.1f} "
          f"(p97.5={p975:+.3f}, margin={L['margin_promote_over_p97.5_pp']:+.2f}) "
          f"premium-clear={delta_clear:+.2f} premium-p80={delta_p80:+.2f}")

DET['competitor_enumeration'] = {
    'LME_K40': 'RANDOM30 + SPREAD3 + BOT48(1) + TOP48/TOP64(2) + RQ32-primary3 + PQ1; '
               'excluded from max: random-32 secondary(3), A5 wrapper, TOP32 curve, A7-44B curve',
    'LOCOMO_K41': 'RANDOM30 + SPREAD3 + BOT80/64/48(3) + TOP48(1) + RQ32-primary3 + PQ1; exclusions as LME',
    'note': 'v2 "~27+" shorthand used >=7 seeds; frozen K uses the sealed 10-seed panels (C2)'}
DET['labels'] = ['RACE-1 Task2 calibration (pre-seal)', 'Gaussian exchangeable-competitor null',
                 'validated against m1 (K=9 LOO); extended to the full sealed set',
                 'half-split scale: conservative for full-benchmark use (see notebook)']
(OUT / 'calib_details.json').write_text(json.dumps(DET, indent=1), encoding='utf-8')
print('wrote', str(OUT / 'calib_details.json'))
print('CALIB_DONE')
