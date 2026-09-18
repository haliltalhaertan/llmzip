"""R2B: train/test-split LEARNED axis selection (LME). Exploratory."""
import hashlib, json, pickle, time
import numpy as np
from pathlib import Path

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work')
NPZ = BASE/'pilots/axis_attack_2026-09-12/per_axis_matrices.npz'
PILOT = BASE/'pilots/axis_attack_2026-09-12/pilot_results.json'
PKLDIR = BASE/'regen/lme/cache_repr'
DATASET = BASE/'drive/longmemeval_s_cleaned.json'
QLEVEL = BASE/'drive/t4c3/V52_T4C3_question_level.csv'
K_LIST = [32, 48, 64]; NT = 20; K = 3

t0 = time.time()
# ---- lex ordinals over ALL 500 dataset qids ----
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

# ---- 1. split ----
def is_train(q):
    return int(hashlib.sha256(q.encode()).hexdigest()[0], 16) % 2 == 0
train_q = [q for q in qids if is_train(q)]
test_q = [q for q in qids if not is_train(q)]
print(f'split: train={len(train_q)} test={len(test_q)} total={len(qids)}', flush=True)

# question_type balance from CSV
import csv
qtype = {}
with open(QLEVEL, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        qtype[row['question_id']] = row['question_type']
from collections import Counter
ctr = lambda qs: dict(Counter(qtype.get(q, 'MISSING') for q in qs))
print('qtype train:', ctr(train_q), flush=True)
print('qtype test :', ctr(test_q), flush=True)
print('qtype csv coverage of 470:', sum(1 for q in qids if q in qtype), flush=True)

# ---- load pkls once; precompute D0/Q0/gold/prios/pool ----
D0, Q0, GOLD, PR, N = {}, {}, {}, {}, {}
pool = np.zeros((470, 96), dtype=np.int32)
for qi, qid in enumerate(qids):
    with open(PKLDIR/(qid + '.pkl'), 'rb') as f:
        o = pickle.load(f)
    C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
    g = np.asarray(o['gold']).ravel()
    D = C >= 0; Q = qC >= 0
    D0[qid] = D; Q0[qid] = Q; GOLD[qid] = g
    n = len(C); N[qid] = n
    lx = lex[qid]
    PR[qid] = [np.random.default_rng(5_100_000 + lx * 100_000 + t * 100 + 99).random(n) for t in range(NT)]
    pool[qi] = np.count_nonzero(D == Q[None, :], axis=0)
print(f'loaded 470 pkls ({time.time()-t0:.0f}s); pool range: {pool.min()}-{pool.max()}', flush=True)

def fr_subset(qid, cols):
    D = D0[qid]; Q = Q0[qid]; g = GOLD[qid]
    d = np.count_nonzero(D[:, cols] != Q[cols][None, :], axis=1)
    gg = set(map(int, np.ravel(g)))
    tot = 0.0
    for p in PR[qid]:
        order = np.lexsort((p, d))
        tot += len(set(map(int, order[:K])) & gg) / len(gg)
    return tot / NT

# ---- gate: recomputed native (all 96) vs stored ----
recomp = {q: fr_subset(q, np.arange(96)) for q in qids}
maxdiff = max(abs(recomp[q] - nat_stored[q]) for q in qids)
print(f'GATE native recompute: mean_recomp={np.mean(list(recomp.values())):.10f} '
      f'mean_stored={np.mean(list(nat_stored[q] for q in qids)):.10f} max_abs_diff={maxdiff:.3e}', flush=True)
print(f'GATE test-set: recomp_mean={np.mean([recomp[q] for q in test_q]):.10f} '
      f'stored_mean={np.mean([nat_stored[q] for q in test_q]):.10f}', flush=True)
print(f'GATE train-set: recomp_mean={np.mean([recomp[q] for q in train_q]):.10f} '
      f'stored_mean={np.mean([nat_stored[q] for q in train_q]):.10f}', flush=True)

# ---- 2. train utilities ----
tr_idx = np.array([qi_of[q] for q in train_q])
nat_tr = np.array([nat_stored[q] for q in train_q])
U_delta = delta[tr_idx].mean(axis=0)
U_drop = (nat_tr[:, None] - drop[tr_idx]).mean(axis=0)
U_alone = (alone[tr_idx] * pool[tr_idx] / 3).mean(axis=0)
U_var = (-var_rank[tr_idx].astype(float)).mean(axis=0)
U = {'delta': U_delta, 'drop': U_drop, 'alone': U_alone, 'var': U_var}
print('utility tops:', {k: np.argsort(v)[::-1][:5].tolist() for k, v in U.items()}, flush=True)

# ---- 3. arms ----
arms = {}  # name -> ('global', cols) or ('spread', k)
for uname, u in U.items():
    for k in K_LIST:
        arms[f'{uname}{k}'] = ('global', np.argsort(u)[::-1][:k])
for k in K_LIST:
    for s in (12000, 12001, 12002):
        arms[f'RANDOM{k}_s{s}'] = ('global', np.random.default_rng(s).choice(96, k, replace=False))
    arms[f'SPREAD{k}'] = ('spread', k)

def cols_for(qid, arm):
    kind, spec = arms[arm]
    if kind == 'global':
        return spec
    qi = qi_of[qid]
    return np.argsort(var_rank[qi])[::2][:spec]

# ---- 4. evaluate ----
test_fr, train_fr, per_q_test, per_q_train = {}, {}, {}, {}
for name in arms:
    st = np.array([fr_subset(q, cols_for(q, name)) for q in test_q])
    sr = np.array([fr_subset(q, cols_for(q, name)) for q in train_q])
    per_q_test[name] = st; per_q_train[name] = sr
    test_fr[name] = float(st.mean()); train_fr[name] = float(sr.mean())
    print(f'  {name}: train={sr.mean():.6f} test={st.mean():.6f} ({time.time()-t0:.0f}s)', flush=True)

rmean = {k: float(np.mean([test_fr[f'RANDOM{k}_s{s}'] for s in (12000, 12001, 12002)])) for k in K_LIST}
rmean_tr = {k: float(np.mean([train_fr[f'RANDOM{k}_s{s}'] for s in (12000, 12001, 12002)])) for k in K_LIST}
nat_test = float(np.mean([nat_stored[q] for q in test_q]))
nat_train = float(np.mean([nat_stored[q] for q in train_q]))

learned = [n for n in arms if any(n.startswith(u) for u in U)]
best = max(learned, key=lambda n: test_fr[n])
bk = int(''.join(c for c in best if c.isdigit()))
rm_perq = np.mean([per_q_test[f'RANDOM{bk}_s{s}'] for s in (12000, 12001, 12002)], axis=0)
d = per_q_test[best] - rm_perq
W, T, L = int((d > 1e-12).sum()), int((np.abs(d) <= 1e-12).sum()), int((d < -1e-12).sum())
print(f'best learned={best} (k={bk}); W/T/L vs RANDOM{bk}-mean on test: {W}/{T}/{L} (n={len(test_q)})', flush=True)

def gap(name):
    for k in K_LIST:
        if name.endswith(str(k)) and (name[: -len(str(k))] in U or name.startswith('SPREAD')):
            return (test_fr[name] - rmean[k]) * 100
        if name.startswith(f'RANDOM{k}_'):
            return (test_fr[name] - rmean[k]) * 100
    return None

rows = []
for uname in list(U) + ['SPREAD']:
    for k in K_LIST:
        n = f'{uname}{k}'
        rows.append((n, train_fr[n], test_fr[n], gap(n)))
for k in K_LIST:
    for s in (12000, 12001, 12002):
        n = f'RANDOM{k}_s{s}'
        rows.append((n, train_fr[n], test_fr[n], gap(n)))
    rows.append((f'RANDOM{k}-mean', rmean_tr[k], rmean[k], 0.0))
rows.append(('NATIVE96', nat_train, nat_test, None))

print('\nTABLE arm train_FR test_FR gap_vs_random_pp')
for n, tr, te, g in rows:
    print(f'{n:14s} {tr:.6f} {te:.6f} {("NA" if g is None else f"{g:+.2f}")}')

out = {
  'labels': ['[LOCAL EXPLORATORY]', '[NOT PREREGISTERED]', '[TRAIN/TEST SPLIT PILOT FOLLOW-UP]'],
  'numpy': np.__version__,
  'split': {'rule': 'train iff first hex char of sha256(qid) even', 'n_train': len(train_q),
            'n_test': len(test_q), 'qtype_train': ctr(train_q), 'qtype_test': ctr(test_q)},
  'gate_native': {'recomp_mean_all': float(np.mean(list(recomp.values()))),
                  'stored_mean_all': float(np.mean([nat_stored[q] for q in qids])),
                  'max_abs_diff': float(maxdiff),
                  'test_recomp_mean': float(np.mean([recomp[q] for q in test_q])),
                  'test_stored_mean': nat_test,
                  'train_recomp_mean': float(np.mean([recomp[q] for q in train_q])),
                  'train_stored_mean': nat_train},
  'utilities': {k: {'top5': [int(i) for i in np.argsort(v)[::-1][:5]], 'mean': float(v.mean())} for k, v in U.items()},
  'arms': {n: {'train_FR': train_fr[n], 'test_FR': test_fr[n], 'gap_vs_random_pp': gap(n),
               'cols': [int(i) for i in (arms[n][1] if arms[n][0] == 'global' else [-1])]} for n in arms},
  'random_mean': {str(k): {'train': rmean_tr[k], 'test': rmean[k]} for k in K_LIST},
  'native': {'train': nat_train, 'test': nat_test},
  'best_learned': {'arm': best, 'k': bk, 'WTL_vs_random_mean_tol1e-12': [W, T, L]},
  'per_q_test': {n: [float(x) for x in per_q_test[n]] for n in arms},
  'per_q_train': {n: [float(x) for x in per_q_train[n]] for n in arms},
  'test_qids': test_q, 'train_qids': train_q,
}
with open('/tmp/r2b/details.json', 'w') as f:
    json.dump(out, f)
import os
print('details.json bytes:', os.path.getsize('/tmp/r2b/details.json'))
print('FINAL_JSON ' + json.dumps({k: out[k] for k in
      ('split','gate_native','utilities','random_mean','native','best_learned') } | {'arms': out['arms']}))
