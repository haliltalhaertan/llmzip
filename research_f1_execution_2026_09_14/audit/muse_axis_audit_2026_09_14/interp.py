"""STEP 5: interpretation attacks (evidence JSON + focused recomputation)."""
import json, pickle, glob, numpy as np

R = json.load(open('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/axis-budget/evidence/axis_budget_results.json'))
MS = [8, 12, 16, 24, 32, 48, 64, 80, 96]
BEN = ['LME', 'LoCoMo', 'REALTALK', 'PerLTQA']
D = {b: np.array([R[b]['budgets'][str(m)]['delta_matched_pp'] for m in MS]) for b in BEN}
SE = {b: np.array([R[b]['budgets'][str(m)]['delta_matched_se_pp'] for m in MS]) for b in BEN}

print("--- S1 strict monotonicity (tolerance 1e-9, as their code) ---")
for b in BEN:
    mono = all(D[b][i] <= D[b][i+1] + 1e-9 for i in range(8))
    print(f" {b:9s} monotone={mono} diffs={np.round(np.diff(D[b]),3)}")

print("--- S2 shape: pairwise correlation of 9-pt Delta curves ---")
for i in range(4):
    for j in range(i+1, 4):
        c = float(np.corrcoef(D[BEN[i]], D[BEN[j]])[0, 1])
        print(f" corr({BEN[i]},{BEN[j]})={c:.4f}")
print("--- S2b total rise 8->96 and demeaned-shape residual ---")
for b in BEN:
    print(f" {b:9s} rise={D[b][-1]-D[b][0]:+.4f}pp")
cen = np.stack([D[b] - D[b].mean() for b in BEN])
print(" demeaned SD across benchmarks per m:", np.round(cen.std(0), 3),
      " mean signal SD:", round(float(np.stack([D[b] for b in BEN]).std(0).mean()), 3))

print("--- S3 crossover CI: parametric bootstrap of bracketing pair ---")
rng = np.random.default_rng(7)
pairs = {'LME': (32, 48), 'REALTALK': (32, 48), 'LoCoMo': (48, 64)}
for b, (a, c) in pairs.items():
    i, j = MS.index(a), MS.index(c)
    v0, v1, s0, s1 = D[b][i], D[b][j], SE[b][i], SE[b][j]
    det = a + (c - a) * (0 - v0) / (v1 - v0)
    for rho in (0.0, 0.9):
        draws = []
        for _ in range(20000):
            z = rng.multivariate_normal([v0, v1], [[s0**2, rho*s0*s1], [rho*s0*s1, s1**2]])
            if (z[0] < 0) != (z[1] < 0) and z[1] != z[0]:
                draws.append(a + (c - a) * (0 - z[0]) / (z[1] - z[0]))
        draws = np.array(draws)
        print(f" {b:9s} point={det:.2f} rho={rho}: 95%CI=[{np.percentile(draws,2.5):.1f},{np.percentile(draws,97.5):.1f}] "
              f"frac_cross={len(draws)/20000:.2f} (v0={v0:+.2f}+-{s0:.2f}, v1={v1:+.2f}+-{s1:.2f})")

print("--- S4 PerLTQA extrapolation by window ---")
p = D['PerLTQA']
wins = {'80..96': [80, 96], '64..96': [64, 80, 96], '48..96': [48, 64, 80, 96], 'all9': MS}
for name, ms in wins.items():
    xs = np.array(ms); ys = np.array([p[MS.index(m)] for m in ms])
    slope, icept = np.polyfit(xs, ys, 1)
    mstar = -icept / slope if slope > 0 else np.inf
    print(f" window {name:6s}: slope={slope:+.5f} pp/axis -> m*={mstar:.0f} ({mstar/96:.2f}x budget)")
print(" increments:", np.round(np.diff(p), 3))

print("--- S5 alignment sign(bot-top)==sign(Delta) per m (their evidence) ---")
for b in BEN:
    row = []
    for m in MS:
        r = R[b]['budgets'][str(m)]
        bt = 100 * (r['sign_bot']['mean'] - r['sign_top']['mean'])
        dl = r['delta_matched_pp']
        row.append('Y' if (bt > 0) == (dl > 0) else 'n')
    print(f" {b:9s} " + ' '.join(f"{m}:{a}" for m, a in zip(MS, row)))

print("--- S6 exclusive-axes contrast (overlap-free) ---")
def fr_h(dist, gold, K=3):
    o = np.argsort(dist, kind='stable'); thr = dist[o[K-1]]
    btr = dist < thr; tied = dist == thr
    bc = int(tied.sum()); slots = K - int(btr.sum()); g = np.asarray(gold)
    return (int(btr[g].sum()) + int(tied[g].sum()) * slots / bc) / len(g)

def exclusive(bench):
    if bench == 'LME':
        files = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
        units = []
        for fp in files:
            d = pickle.load(open(fp, 'rb'))
            units.append((np.asarray(d['C'], float), np.asarray(d['qC'], float).ravel(),
                          np.asarray(d['gold']).ravel(), None))
    else:
        arch = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
        Q = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
        units = [(np.asarray(arch[q['char']]['C'], float), np.asarray(q['qC'], float).ravel(),
                  np.asarray(q['gold']).ravel(), None) for q in Q.values()]
    for m in (48, 64, 80):
        k = 96 - m  # exclusive sizes when overlapping; at 48 => 48 (partition)
        st = sb = se_t = se_b = 0.0; n = 0
        for (C, q, g, _) in units:
            order = np.argsort(-(C * C).mean(axis=0), kind='stable')
            top, bot = order[:m], order[-m:]
            Cb = (C[:, bot] >= 0); qb = (q[bot] >= 0)
            Ct = (C[:, top] >= 0); qt = (q[top] >= 0)
            sb += fr_h(np.sum(Cb != qb, 1).astype(np.int32), g)
            st += fr_h(np.sum(Ct != qt, 1).astype(np.int32), g)
            et, eb = order[:k], order[-k:]
            Ce = (C[:, eb] >= 0); qe = (q[eb] >= 0)
            Cf = (C[:, et] >= 0); qf = (q[et] >= 0)
            se_b += fr_h(np.sum(Ce != qe, 1).astype(np.int32), g)
            se_t += fr_h(np.sum(Cf != qf, 1).astype(np.int32), g)
            n += 1
        print(f" {bench} m={m}: overlapping bot-top={(sb-st)/n*100:+.4f}pp | "
              f"EXCLUSIVE bot{k}-top{k}={(se_b-se_t)/n*100:+.4f}pp", flush=True)

exclusive('LME')
exclusive('PerLTQA')

print("--- S7 zero-norm sweep, all benchmarks x all budgets (norms only) ---")
def arch_iter():
    out = []
    for fp in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(fp, 'rb'))
        out.append((np.asarray(d['C'], float), np.asarray(d['qC'], float).ravel()))
    arch = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Q = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    for q in Q.values():
        out.append((np.asarray(arch[q['char']]['C'], float), np.asarray(q['qC'], float).ravel()))
    for fp in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(fp, 'rb'))
        C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
        for j in range(QC.shape[0]):
            out.append((C, QC[j]))
    for fp in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(fp, 'rb'))
        C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
        for j in range(QC.shape[0]):
            out.append((C, QC[j]))
    return out

units = arch_iter()
print("units:", len(units))
tot_r = tot_q = 0
for m in MS:
    zr = zq = 0
    for (C, q) in units:
        var = (C * C).mean(axis=0); order = np.argsort(-var, kind='stable')
        for idx in (order[:m], order[-m:]):
            Cs = C[:, idx]; qs = q[idx]
            rn = np.sum(Cs * Cs, axis=1); qn = float(np.sum(qs * qs))
            zr += int(np.sum(rn == 0)); zq += int(qn == 0)
    tot_r += zr; tot_q += zq
    print(f" m={m:>3}: zero row-norms={zr} zero query-norms={zq}", flush=True)
print("TOTAL zero events:", tot_r, tot_q)
print("DONE")
