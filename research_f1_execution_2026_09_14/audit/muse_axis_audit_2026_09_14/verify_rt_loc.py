"""Independent check of REALTALK + LoCoMo CLAIM grids (my own code, STEP 2 extension).

Same spec as my_axis.py: per-archive var ranking descending, Hamming (C>=0)
lower-better, cosine higher-better, exact tie expectation, K=3, no re-centering.
Also counts zero-norm cosine events per m.
"""
import pickle, glob, ast, numpy as np

K = 3
MS = [24, 32, 48, 64, 80, 96]
zero_events = {m: 0 for m in MS}
zero_q = {m: 0 for m in MS}
total_cells = {m: 0 for m in MS}

def fr_h(dist, gold):
    o = np.argsort(dist, kind='stable')
    thr = dist[o[K-1]]
    better = dist < thr; tied = dist == thr
    bc = int(tied.sum()); slots = K - int(better.sum())
    g = np.asarray(gold)
    return (int(better[g].sum()) + int(tied[g].sum()) * slots / bc) / len(g)

def fr_c(cos, gold):
    cos = np.where(np.isnan(cos), -np.inf, cos)
    o = np.argsort(-cos, kind='stable')
    thr = cos[o[K-1]]
    better = cos > thr; tied = cos == thr
    bc = int(tied.sum()); slots = K - int(better.sum())
    g = np.asarray(gold)
    return (int(better[g].sum()) + int(tied[g].sum()) * slots / bc) / len(g)

def run_units(units, tag):
    # units: list of (C, QC, golds)
    # precompute per-unit orders once
    Us = []
    for (C, QC, golds) in units:
        var = np.mean(C * C, axis=0)
        order = np.argsort(-var, kind='stable')
        Us.append((C, QC, golds, order))
    nq = sum(len(g) for _, _, g, _ in Us)
    print(f"{tag} units={len(Us)} queries={nq}", flush=True)
    for m in MS:
        ss = ff = bb = 0.0; n = 0
        for (C, QC, golds, order) in units and [] or Us:
            top = order[:m]; bot = order[-m:]
            for j, g in enumerate(golds):
                q = QC[j]
                # TOP
                d, c, zr, zq = sub(C, q, top)
                ss += fr_h(d, g); ff += fr_c(c, g)
                bb += fr_h(sub(C, q, bot)[0], g)
                zero_events[m] += zr; zero_q[m] += zq; total_cells[m] += len(d) + 1
                n += 1
        ss /= n; ff /= n; bb /= n
        print(f"{tag} m={m} sign_top={ss*100:.6f} float_top={ff*100:.6f} "
              f"delta={(ss-ff)*100:.6f} sign_bot={bb*100:.6f} bot-top={(bb-ss)*100:.6f}",
              flush=True)

def sub(C, q, idx):
    Cs = C[:, idx]; qs = q[idx]
    d = np.sum((Cs >= 0) != (qs >= 0), axis=1).astype(np.int32)
    rn = np.sqrt(np.sum(Cs * Cs, axis=1)); qn = float(np.sqrt(np.sum(qs * qs)))
    den = rn * qn
    with np.errstate(divide='ignore', invalid='ignore'):
        c = (Cs @ qs) / den
    c = np.where(den == 0, np.nan, c)
    return d, c, int(np.sum(den == 0)), int(qn == 0)

# REALTALK
rt_units = []
for fp in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    with open(fp, 'rb') as f:
        d = pickle.load(f)
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
    golds = [np.asarray(g).ravel().astype(int) for g in d['gold_rows'] if len(np.asarray(g).ravel()) > 0]
    keep = [i for i, g in enumerate(d['gold_rows']) if len(np.asarray(g).ravel()) > 0]
    rt_units.append((C, QC[keep], golds))
run_units(rt_units, "REALTLK")

# LoCoMo
loc_units = []
for fp in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
    with open(fp, 'rb') as f:
        d = pickle.load(f)
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float); i2r = d['id_to_row']
    keep, golds = [], []
    for i, qa in enumerate(d['qas']):
        ev = qa.get('raw_evidence')
        if ev is None:
            continue
        if isinstance(ev, str):
            try:
                ev = ast.literal_eval(ev)
            except Exception:
                ev = [ev]
        if isinstance(ev, str):
            ev = [ev]
        rows = sorted({i2r[e] for e in ev if e in i2r})
        if not rows:
            continue
        keep.append(i); golds.append(np.asarray(rows, int))
    loc_units.append((C, QC[keep], golds))
run_units(loc_units, "LOCOMO")
print("zero row-norm events:", zero_events)
print("zero query-norm events:", zero_q)
print("DONE")
