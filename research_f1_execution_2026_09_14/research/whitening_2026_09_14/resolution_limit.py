#!/usr/bin/env python3
"""Does the 12-byte method have a RESOLUTION limit that only appears at scale?

THE USER'S QUESTION: is testing at 1M documents actually necessary? Information is
information, at any N.

The answer splits. Mechanism questions (why does sign quantization work) are about
the geometry of the representation and do not depend on N. But RETRIEVAL is a
competition against N-1 rivals, and the sign arm has a hard structural property the
float arm does not:

  Hamming distance on 96 bits takes only 97 distinct integer values.
  Cosine takes essentially N distinct values.

So as N grows, the sign arm must separate more and more documents using a FIXED
number of levels. Documents pile into buckets. Once the bucket at the top-3 boundary
holds far more than 3 documents, the top-3 is a lottery draw from that bucket, and
accuracy must fall toward the bucket's gold density.

CRUCIAL: this argument is method-independent. Today's earlier finding was that the
tie RATE moves in opposite directions depending on how you synthesise a larger
archive (pooling vs subsampling). But "97 buckets is 97 buckets" holds no matter how
the archive is built. Bucket OCCUPANCY grows with N by counting alone.

WHAT THIS SCRIPT MEASURES (all on real archives, no synthesis):
 1. The distance distribution: how many of the 97 levels are actually populated, and
    how concentrated the mass is. This is the EFFECTIVE resolution, which is far
    below 97.
 2. Occupancy of the boundary bucket (the one containing the K-th best score) at
    current N, per benchmark.
 3. How occupancy scales with N, measured by subsampling rows WITHIN a single real
    archive -- a counting measurement, not a retrieval-quality claim.
 4. Projection: at what N does the boundary bucket hold >> K documents, and what
    does that imply for the float arm (which has no such limit).
"""
import glob, json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))


def ham(D0, q0):
    return (D0 != q0[None, :]).sum(axis=1)


def load_lme(limit=120):
    for i, f in enumerate(sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl'))):
        if i >= limit:
            break
        d = pickle.load(open(f, 'rb'))
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g):
            yield np.asarray(d['C'], float), np.asarray(d['qC'], float)[None, :], [g]


def load_perltqa(limit=30):
    A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for q in Qd.values():
        by.setdefault(q['char'], []).append(q)
    for n, (ch, items) in enumerate(by.items()):
        if n >= limit:
            break
        keep = [q for q in items if len(np.asarray(q['gold']).ravel())][:200]
        if keep:
            yield (np.asarray(A[ch]['C'], float),
                   np.stack([np.asarray(q['qC'], float) for q in keep]),
                   [np.asarray(q['gold']).ravel().astype(int) for q in keep])


def load_realtalk():
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        gs = [np.asarray(g).ravel().astype(int) for g in d['gold_rows']]
        keep = [i for i, g in enumerate(gs) if len(g)][:150]
        if keep:
            yield (np.asarray(d['C'], float), np.asarray(d['QC'], float)[keep],
                   [gs[i] for i in keep])


def load_locomo():
    for f in sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        i2r = d['id_to_row']; gs = []; idx = []
        for i, qa in enumerate(d['qas']):
            rows = [i2r[e] for e in (qa.get('raw_evidence') or []) if e in i2r]
            if rows:
                gs.append(np.asarray(sorted(set(rows)), int)); idx.append(i)
        if gs:
            yield (np.asarray(d['C'], float), np.asarray(d['QC'], float)[idx[:150]],
                   gs[:150])


LOADERS = {'LME': load_lme, 'PerLTQA': load_perltqa,
           'REALTALK': load_realtalk, 'LoCoMo': load_locomo}
out = {}

for bname, ld in LOADERS.items():
    occ, levels, mass90, Ns = [], [], [], []
    cos_ties = []
    for C, Q, golds in ld():
        N = C.shape[0]
        D0 = (C >= 0)
        Q0 = (Q >= 0)
        nrm = np.linalg.norm(C, axis=1)
        for j in range(Q.shape[0]):
            d = ham(D0, Q0[j])
            # boundary bucket = the bucket holding the K-th smallest distance
            thr = np.partition(d, K - 1)[K - 1]
            occ.append(int((d == thr).sum()))
            cnt = np.bincount(d, minlength=97)
            levels.append(int((cnt > 0).sum()))
            s = np.sort(cnt)[::-1].cumsum() / cnt.sum()
            mass90.append(int(np.searchsorted(s, 0.90) + 1))
            # float arm: how many exact ties at its own boundary
            cs = (C @ Q[j]) / (nrm * np.linalg.norm(Q[j]) + 1e-12)
            t2 = -np.partition(-cs, K - 1)[K - 1]
            cos_ties.append(int((cs == t2).sum()))
            Ns.append(N)
    out[bname] = {
        'n_queries': len(occ), 'N_mean': float(np.mean(Ns)),
        'boundary_occupancy_mean': float(np.mean(occ)),
        'boundary_occupancy_median': float(np.median(occ)),
        'levels_populated_mean': float(np.mean(levels)),
        'levels_holding_90pct_mass': float(np.mean(mass90)),
        'float_boundary_ties_mean': float(np.mean(cos_ties)),
    }
    print(f'  {bname} done', flush=True)

print('\n=== EFFECTIVE RESOLUTION: 96 bits gives 97 levels, but how many are used? ===')
print(f'  {"bench":9s} {"N":>7s} {"levels used":>12s} {"levels w/ 90% mass":>19s} '
      f'{"docs/level":>11s}')
for b, r in out.items():
    dpl = r['N_mean'] / r['levels_holding_90pct_mass']
    print(f'  {b:9s} {r["N_mean"]:>7.0f} {r["levels_populated_mean"]:>12.1f} '
          f'{r["levels_holding_90pct_mass"]:>19.1f} {dpl:>11.1f}')
print('  -> the usable resolution is the third column, NOT 97.')

print('\n=== BOUNDARY BUCKET: how many documents share the K=3 cut-off? ===')
print(f'  {"bench":9s} {"sign: mean":>11s} {"sign: median":>13s} {"float: mean":>12s}')
for b, r in out.items():
    print(f'  {b:9s} {r["boundary_occupancy_mean"]:>11.2f} '
          f'{r["boundary_occupancy_median"]:>13.1f} {r["float_boundary_ties_mean"]:>12.2f}')
print('  float is ~1.00 by construction: continuous scores essentially never tie.')

# --- scaling of occupancy by subsampling WITHIN one real archive (counting only) ---
print('\n=== HOW OCCUPANCY GROWS WITH N (subsampling inside real archives) ===')
rng = np.random.default_rng(3)
fracs = [0.125, 0.25, 0.5, 1.0]
scal = {}
for bname, ld in LOADERS.items():
    rows = {f: [] for f in fracs}
    for C, Q, golds in list(ld())[:40]:
        N = C.shape[0]
        D0 = (C >= 0); Q0 = (Q >= 0)
        for f in fracs:
            m = max(20, int(N * f))
            sub = rng.permutation(N)[:m]
            Ds = D0[sub]
            for j in range(min(Q.shape[0], 40)):
                d = (Ds != Q0[j][None, :]).sum(axis=1)
                thr = np.partition(d, K - 1)[K - 1]
                rows[f].append(((d == thr).sum(), m))
    scal[bname] = {str(f): (float(np.mean([a for a, _ in rows[f]])),
                            float(np.mean([b for _, b in rows[f]]))) for f in fracs}
    o = scal[bname]
    print(f'  {bname:9s} ' + '  '.join(
        f'N={o[str(f)][1]:.0f}:{o[str(f)][0]:.2f}' for f in fracs))

print('\n=== PROJECTION to 1,000,000 documents ===')
print('  Occupancy grows about linearly in N (counting argument, method-independent).')
print(f'  {"bench":9s} {"N now":>7s} {"occ now":>8s} {"x to 1M":>9s} {"occ at 1M":>11s}')
for b, r in out.items():
    n = r['N_mean']; o = r['boundary_occupancy_mean']
    f = 1e6 / n
    print(f'  {b:9s} {n:>7.0f} {o:>8.2f} {f:>9.0f}x {o*f:>11.0f}')
print('  If the K=3 boundary bucket holds thousands of documents, the top-3 is a')
print('  draw from that bucket. The float arm has no equivalent limit.')

json.dump({'now': out, 'scaling': scal}, open(os.path.join(OUT, 'resolution.json'), 'w'),
          indent=1)
print('\nWROTE resolution.json')
