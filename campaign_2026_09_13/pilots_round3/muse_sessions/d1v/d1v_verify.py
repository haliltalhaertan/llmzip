#!/usr/bin/env python3
"""D1V: independent recompute of Deney 1 (round3) numbers FROM RAW ARTIFACTS.
Read-only on /mnt/c; writes only /tmp/d1v/. No network. No imports from harness.
Logic reimplemented from reading harness/deney1_lme.py + harness/deney1_loco.py."""
import hashlib, json, pickle, csv, re, statistics
import numpy as np
from pathlib import Path

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUTD = Path('/tmp/d1v'); OUTD.mkdir(parents=True, exist_ok=True)
CHECKS = []
def record(cid, label, status, detail, nums=None):
    CHECKS.append({'id': cid, 'label': label, 'status': status,
                   'detail': detail, 'numbers': nums or {}})
    print(f"[{status}] {cid} {label}: {detail}", flush=True)

NT, KTOP, NSALT = 20, 3, 10
def rand_seeds(s): return [91000 + s*10 + j for j in range(10)]

# ============ LME RAW LOADS ============
z = np.load(BASE/'pilots/axis_attack_2026-09-12/per_axis_matrices.npz')
alone, drop, delta = z['alone'], z['drop'], z['delta']
var_rank = z['var_rank']
qids = [str(q) for q in z['qids']]
qi_of = {q: i for i, q in enumerate(qids)}
nat_stored = json.loads((BASE/'pilots/axis_attack_2026-09-12/pilot_results.json').read_text())['per_question_native_FR']
qtype = {}
with open(BASE/'drive/t4c3/V52_T4C3_question_level.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        qtype[row['question_id']] = row['question_type']
data = json.loads((BASE/'drive/longmemeval_s_cleaned.json').read_text())
lex = {q: i for i, q in enumerate(sorted(str(x['question_id']) for x in data))}
del data
LME = json.loads((BASE/'pilots/axis_attack_2026-09-12/round3/deney1_lme_details.json').read_text())
LOCO = json.loads((BASE/'pilots/axis_attack_2026-09-12/round3/deney1_loco_details.json').read_text())

def make_split_lme(s):
    tr, te = [], []
    for t in sorted(set(qtype[q] for q in qids)):
        qs = sorted([q for q in qids if qtype[q] == t],
                    key=lambda q: hashlib.sha256(f'deney1|{s}|{q}'.encode()).hexdigest())
        for i, q in enumerate(qs):
            (tr if i % 2 == 0 else te).append(q)
    return sorted(tr), sorted(te)

# ---- CHECK 1: split reconstruction s=0, s=7 ----
for s in (0, 7):
    tr, te = make_split_lme(s)
    st = LME['splits'][s]
    ok_tr = (tr == st['train_qids']); ok_te = (te == st['test_qids'])
    disj = len(set(tr) & set(te)) == 0; comp = len(tr) + len(te) == 470
    status = 'EXACT' if (ok_tr and ok_te and disj and comp) else 'DIFF'
    record(f'LME-1-s{s}', f'split s={s} reconstruction',
           status, f'train_match={ok_tr} test_match={ok_te} disjoint={disj} complete={comp} '
                   f'n_train={len(tr)} n_test={len(te)}',
           {'n_train': len(tr), 'n_test': len(te)})

# ---- load 470 pkls once (pool + FR machinery) ----
PKLDIR = BASE/'regen/lme/cache_repr'
D0, Q0, GOLD, PR, pool = {}, {}, {}, {}, np.zeros((470, 96), dtype=np.int32)
for qi, qid in enumerate(qids):
    with open(PKLDIR/(qid+'.pkl'), 'rb') as f:
        o = pickle.load(f)
    C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
    g = np.asarray(o['gold']).ravel()
    D = C >= 0; Q = qC >= 0
    D0[qid] = D; Q0[qid] = Q; GOLD[qid] = g
    lx = lex[qid]
    PR[qid] = [np.random.default_rng(5_100_000 + lx*100_000 + t*100 + 99).random(len(C)) for t in range(NT)]
    pool[qi] = np.count_nonzero(D == Q[None, :], axis=0)

def fr_subset(qid, cols):
    D = D0[qid]; Q = Q0[qid]; g = GOLD[qid]
    d = np.count_nonzero(D[:, cols] != Q[cols][None, :], axis=1)
    gg = set(map(int, np.ravel(g)))
    tot = 0.0
    for p in PR[qid]:
        order = np.lexsort((p, d))
        tot += len(set(map(int, order[:KTOP])) & gg) / len(gg)
    return tot / NT

# ---- CHECK 5b (cheap order): full native gate over 470 ----
recomp_nat = {q: fr_subset(q, np.arange(96)) for q in qids}
md = max(abs(recomp_nat[q] - nat_stored[q]) for q in qids)
mn_r = float(np.mean(list(recomp_nat.values()))); mn_s = float(np.mean([nat_stored[q] for q in qids]))
record('LME-GATE1', 'native recompute all 470',
       'EXACT' if md < 1e-12 else 'DIFF',
       f'max_abs_diff={md:.3e} mean_recomp={mn_r:.16f} mean_stored={mn_s:.16f} '
       f'stored_claim=1.11e-16',
       {'max_abs_diff': md, 'mean_recomp': mn_r, 'mean_stored': mn_s})
# ---- CHECK 2: utility recompute s=0, s=7 ----
for s in (0, 7):
    train_q, _ = make_split_lme(s)
    tr_idx = np.array([qi_of[q] for q in train_q])
    nat_tr = np.array([nat_stored[q] for q in train_q])
    U_drop = (nat_tr[:, None] - drop[tr_idx]).mean(axis=0)
    U_alone = (alone[tr_idx] * pool[tr_idx] / 3).mean(axis=0)
    U_var = (-var_rank[tr_idx].astype(float)).mean(axis=0)
    got = {'drop64': sorted(np.argsort(U_drop)[::-1][:64].tolist()),
           'alone64': sorted(np.argsort(U_alone)[::-1][:64].tolist()),
           'var64': sorted(np.argsort(U_var)[::-1][:64].tolist())}
    for arm, cols in got.items():
        stored = LME['splits'][s]['arms'][arm]['cols']
        ok = (cols == stored)
        record(f'LME-2-s{s}-{arm}', f'utility top-64 {arm} s={s}',
               'EXACT' if ok else 'DIFF',
               f"match={ok} n={len(cols)} first5={cols[:5]} stored_first5={stored[:5]}",
               {'cols': cols, 'stored': stored})

# ---- CHECK 3: SPREAD64 s=0 ----
tr0, _ = make_split_lme(0)
tr_idx0 = np.array([qi_of[q] for q in tr0])
U_var0 = (-var_rank[tr_idx0].astype(float)).mean(axis=0)
order_desc = np.argsort(U_var0)[::-1]
pos = np.round(np.linspace(0, 95, 64)).astype(int)
spread_re = sorted(order_desc[pos].tolist())
spread_st = LME['splits'][0]['arms']['SPREAD64']['cols']
record('LME-3-SPREAD64', 'SPREAD64 cols s=0',
       'EXACT' if spread_re == spread_st else 'DIFF',
       f"match={spread_re == spread_st} distinct_pos={len(set(pos.tolist()))==64} "
       f"first5={spread_re[:5]} stored_first5={spread_st[:5]}",
       {'cols': spread_re, 'stored': spread_st})

# ---- CHECK 4: RANDOM64_s91000 s=0 ----
rand_re = sorted(np.random.default_rng(91000).choice(96, 64, replace=False).tolist())
rand_st = LME['splits'][0]['arms']['RANDOM64_s91000']['cols']
record('LME-4-RAND', 'RANDOM64_s91000 cols s=0',
       'EXACT' if rand_re == rand_st else 'DIFF',
       f"match={rand_re == rand_st} first5={rand_re[:5]} stored_first5={rand_st[:5]}",
       {'cols': rand_re, 'stored': rand_st})

# ---- CHECK 5: FR spot-check, 30 q from s=0 test ----
_, te0 = make_split_lme(0)
spot = te0[:30]  # deterministic: first 30 of sorted test qids
s0 = LME['splits'][0]
idx_of = {q: i for i, q in enumerate(s0['test_qids'])}
arms5 = {'drop64': np.array(s0['arms']['drop64']['cols']),
         'alone64': np.array(s0['arms']['alone64']['cols']),
         'RANDOM64_s91000': np.array(s0['arms']['RANDOM64_s91000']['cols'])}
maxd = 0.0; worst = None
for q in spot:
    i = idx_of[q]
    for name, cols in arms5.items():
        r = fr_subset(q, cols)
        stv = s0['per_q_test'][name][i]
        dd = abs(r - stv)
        if dd > maxd: maxd, worst = dd, (q, name, r, stv)
    rn = fr_subset(q, np.arange(96))
    dd = abs(rn - recomp_nat[q])
    if dd > maxd: maxd, worst = dd, (q, 'native-internal', rn, recomp_nat[q])
    # stored native for test q: pilot_results value; per_q_test has no native arm -> compare vs nat_stored
    dd2 = abs(rn - nat_stored[q])
    if dd2 > maxd: maxd, worst = dd2, (q, 'native-vs-pilot', rn, nat_stored[q])
record('LME-5-FR30', 'FR spot-check 30q x arms{s=0 test}',
       'EXACT' if maxd <= 1e-12 else 'DIFF',
       f'max_abs_diff={maxd:.3e} worst={worst} tol=1e-12 arms=drop64/alone64/RANDOM64_s91000+native',
       {'max_abs_diff': maxd, 'worst': str(worst)})

# ---- CHECK 6: summary recompute from stored per_q_test ----
gaps_d, gaps_a, gmean_d, gmean_a = [], [], [], []
per_split_ok = True
for s in range(10):
    sp = LME['splits'][s]
    pq = sp['per_q_test']
    d = np.array(pq['drop64']); a = np.array(pq['alone64'])
    R = np.array([pq[f'RANDOM64_s{sd}'] for sd in rand_seeds(s)])
    Rm = np.array([v.mean() for v in R])
    gd = float(d.mean() - Rm.max()); ga = float(a.mean() - Rm.max())
    gmd = float(d.mean() - Rm.mean()); gma = float(a.mean() - Rm.mean())
    gaps_d.append(gd*100); gaps_a.append(ga*100); gmean_d.append(gmd*100); gmean_a.append(gma*100)
    for key, val in (('gap64_vs_best_pp', gd*100), ('gap64_alone_vs_best_pp', ga*100)):
        if abs(val - sp['run'][key]) > 1e-9:
            per_split_ok = False
            record(f'LME-6-s{s}-{key}', f'per-split {key} s={s}', 'DIFF',
                   f"recomputed={val!r} stored={sp['run'][key]!r} diff={val-sp['run'][key]:.3e}")
summ = LME['summary']
def sm(v): return float(np.mean(v))
exp = {'drop_mean': sm(gaps_d), 'drop_med': float(np.median(gaps_d)),
       'drop_range': [min(gaps_d), max(gaps_d)],
       'drop_wins': f"{sum(1 for x in gaps_d if x>0)}/10",
       'alone_mean': sm(gaps_a), 'alone_med': float(np.median(gaps_a)),
       'alone_range': [min(gaps_a), max(gaps_a)],
       'alone_wins': f"{sum(1 for x in gaps_a if x>0)}/10"}
st = summ['drop64_gap_vs_best_pp']; sa = summ['alone64_gap_vs_best_pp']
diffs = [abs(exp['drop_mean']-st['mean']), abs(exp['drop_med']-st['median']),
         abs(exp['drop_range'][0]-st['range'][0]), abs(exp['drop_range'][1]-st['range'][1]),
         abs(exp['alone_mean']-sa['mean']), abs(exp['alone_med']-sa['median']),
         abs(exp['alone_range'][0]-sa['range'][0]), abs(exp['alone_range'][1]-sa['range'][1])]
wins_ok = (exp['drop_wins']==st['wins'] and exp['alone_wins']==sa['wins'])
ok6 = per_split_ok and max(diffs) < 1e-9 and wins_ok
record('LME-6-SUMMARY', 'summary recompute vs-best (10 splits)',
       'EXACT' if ok6 else 'DIFF',
       f"per_split_gaps_ok={per_split_ok} max_summary_diff={max(diffs):.3e} wins_ok={wins_ok} "
       f"drop_mean={exp['drop_mean']!r} stored={st['mean']!r} drop_wins={exp['drop_wins']} stored={st['wins']} "
       f"alone_mean={exp['alone_mean']!r} stored={sa['mean']!r} alone_wins={exp['alone_wins']} stored={sa['wins']}",
       {'recomputed': exp, 'max_diff': max(diffs)})
# vs-mean secondary (report claims drop +0.43pp 7/10; not in JSON summary -> recompute & state)
mw_d, mw_a = sm(gmean_d), sm(gmean_a)
ww_d = f"{sum(1 for x in gmean_d if x>0)}/10"; ww_a = f"{sum(1 for x in gmean_a if x>0)}/10"
record('LME-6-MEAN', 'secondary vs-mean panel (recompute only)',
       'INFO',
       f"drop_vs_mean={mw_d:.4f}pp wins={ww_d} (report claims +0.43pp 7/10); "
       f"alone_vs_mean={mw_a:.4f}pp wins={ww_a} (report claims -1.47pp)",
       {'drop_vs_mean_pp': mw_d, 'drop_vs_mean_wins': ww_d,
        'alone_vs_mean_pp': mw_a, 'alone_vs_mean_wins': ww_a})
# s=0 bootstrap CI + WTL + var_worst + overlap spot re-verification
sp0 = LME['splits'][0]; pq0 = sp0['per_q_test']
d0 = np.array(pq0['drop64']); R0 = np.array([pq0[f'RANDOM64_s{sd}'] for sd in rand_seeds(0)])
rng = np.random.default_rng(777000+0); nn = len(d0); NBOOT = 2000
diffs_b = np.empty(NBOOT)
for b in range(NBOOT):
    idx = rng.integers(0, nn, nn)
    diffs_b[b] = d0[idx].mean() - max(R0[j][idx].mean() for j in range(10))
lo, hi = np.percentile(diffs_b, [5, 95])
clo, chi = sp0['run']['gap64_ci90']
ci_ok = abs(lo*100-clo) < 1e-9 and abs(hi*100-chi) < 1e-9
dd = d0 - R0.max(axis=0)
WTL = [int((dd>1e-12).sum()), int((np.abs(dd)<=1e-12).sum()), int((dd<-1e-12).sum())]
wtl_ok = (WTL == sp0['run']['WTL_drop64_vs_best_seed'])
tf = {n: sp0['arms'][n]['test_FR'] for n in ['delta64','drop64','alone64','var64','SPREAD64']}
vw = (min(tf, key=lambda x: tf[x]) == 'var64')
vw_ok = (vw == sp0['run']['var_worst']['64'])
record('LME-6b-CI', 's=0 bootstrap CI90 drop64 recompute', 'EXACT' if ci_ok else 'DIFF',
       f"recomputed=[{lo*100:.6f},{hi*100:.6f}] stored={clo,chi}",
       {'recomputed': [lo*100, hi*100], 'stored': [clo, chi]})
record('LME-6b-WTL', 's=0 WTL drop64 vs best-seed', 'EXACT' if wtl_ok else 'DIFF',
       f"recomputed={WTL} stored={sp0['run']['WTL_drop64_vs_best_seed']}")
record('LME-6b-VARW', 's=0 var-worst k=64', 'EXACT' if vw_ok else 'DIFF',
       f"recomputed={vw} stored={sp0['run']['var_worst']['64']} fam={ {k: round(v,4) for k,v in tf.items()} }")
# ============ LOCOMO ============
def norm_evidence(x):
    if x is None: return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for vv in x:
            if isinstance(vv, str):
                ids = re.findall(r"D\d+:\d+", vv)
                out.extend(ids if ids else [vv])
            elif isinstance(vv, dict):
                did = vv.get("dia_id") or vv.get("id")
                if did: out.append(str(did))
        return list(dict.fromkeys(out))
    return []

def stable_archive_seed(ci, t=0): return 5_100_000 + ci*100_000 + t*100
TOPK = 3; NN = 20
def topks_by_hamming(dist, priorities, k=TOPK):
    dist = np.asarray(dist); P = np.asarray(priorities, dtype=float)
    if len(dist) <= k:
        return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k-1)[k-1]
    strict = np.flatnonzero(dist < kth); boundary = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, boundary]
    if need == len(boundary):
        picks = np.tile(boundary, (len(P), 1))
    else:
        loc = np.argpartition(BP, need-1, axis=1)[:, :need]
        picks = boundary[loc]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]

def retrieval_metrics(top, gold_rows):
    if not gold_rows:
        return {"valid": 0, "fractional": np.nan}
    R = set(map(int, top)); G = set(map(int, gold_rows))
    return {"valid": 1, "fractional": float(len(R & G) / len(G))}

def mean_or_nan(xs):
    a = np.asarray(xs, dtype=float)
    return float(np.nanmean(a)) if np.isfinite(a).any() else np.nan

raw = json.loads((BASE/'drive/locomo10.json').read_text(encoding='utf-8'))
corr = {}
for f in sorted((BASE/'drive/audit_layer').glob('errors_conv_*.json')):
    try: rows = json.loads(f.read_text(encoding='utf-8'))
    except Exception: continue
    if not isinstance(rows, list): continue
    for r in rows:
        qid = r.get('question_id')
        if qid: corr[str(qid)] = {'has_ce': 'correct_evidence' in r,
                                  'ce': norm_evidence(r.get('correct_evidence'))}
convs = []
for idx, item in enumerate(raw):
    qas = []
    for qi, q in enumerate(item.get('qa', []) or []):
        cat = int(q.get('category')) if q.get('category') is not None else None
        if cat not in (1, 2, 3, 4): continue
        qid = q.get('question_id') or f'locomo_{idx}_qa{qi}'
        cc = corr.get(str(qid))
        ce = list(cc['ce']) if (cc and cc['has_ce']) else list(norm_evidence(q.get('evidence')))
        qas.append({'question_id': str(qid), 'category': cat, 'correct_evidence': ce})
    convs.append({'conv_id': f'locomo_{idx}', 'qas': qas})
del raw
reps = []
for ci in range(10):
    with open(BASE/f'regen/locomo/locomo_{ci}.pkl', 'rb') as f:
        reps.append(pickle.load(f))
Q = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    id_to_row = r['id_to_row']
    for qi, q in enumerate(c['qas']):
        ag = []
        for x in q['correct_evidence']:
            if x in id_to_row: ag.append(int(id_to_row[x]))
        ag = list(dict.fromkeys(ag))
        Q[q['question_id']] = {'cat': q['category'], 'ci': ci, 'qi': qi, 'ag': ag}
valid_qids = [qid for qid, v in Q.items() if len(v['ag']) > 0]
record('LOCO-7-VALID', 'LoCoMo valid count',
       'EXACT' if len(valid_qids) == 1535 == LOCO['n_valid'] else 'DIFF',
       f"recomputed_valid={len(valid_qids)} stored_n_valid={LOCO['n_valid']} expect=1535",
       {'recomputed': len(valid_qids), 'stored': LOCO['n_valid']})

A_of, D96_of, PR_of, N_of = {}, {}, {}, {}
for ci, r in enumerate(reps):
    C = np.asarray(r['C'], float); QC = np.asarray(r['QC'], float)
    A = ((QC[:, None, :] >= 0) != (C[None, :, :] >= 0)).astype(np.int16)
    A_of[ci] = A; D96_of[ci] = A.sum(axis=2); N_of[ci] = C.shape[0]
    PR_of[ci] = [np.random.default_rng(stable_archive_seed(ci, t)+99).random(C.shape[0]) for t in range(NN)]

def q_fractional(dist_q, pr, gold):
    return mean_or_nan([retrieval_metrics(t, gold)['fractional'] for t in topks_by_hamming(dist_q, pr)])

npz = np.load(BASE/'pilots/axis_attack_2026-09-12/round3/deney1_loco_peraxis.npz')
nq = np.array(npz['qids']).tolist()
npos = {q: i for i, q in enumerate(nq)}
nm = float(np.nanmean(np.asarray(npz['native'], float)))
anchor = 0.23654714666441054
record('LOCO-7-NATIVE', 'LoCoMo native mean vs anchor',
       'EXACT' if abs(nm-anchor) < 1e-12 else 'DIFF',
       f"npz_native_mean={nm!r} anchor={anchor!r} diff={nm-anchor:.3e} stored_recomputed={LOCO['native_recomputed']!r}",
       {'npz_mean': nm, 'anchor': anchor})
qids_match = (sorted(nq) == sorted(valid_qids))
record('LOCO-7-QIDS', 'peraxis.npz qids == valid set',
       'EXACT' if qids_match else 'DIFF',
       f"match={qids_match} npz_n={len(nq)} valid_n={len(valid_qids)}",
       {'npz_n': len(nq)})

# 15 random (qid, axis) cells
rng15 = np.random.default_rng(777)
cells = [(valid_qids[rng15.integers(0, len(valid_qids))], int(rng15.integers(0, 96))) for _ in range(15)]
maxd15 = 0.0; worst15 = None
for qid, a in cells:
    v = Q[qid]; ci, qi, ag = v['ci'], v['qi'], v['ag']
    pr = PR_of[ci]; D96 = D96_of[ci][qi]; A = A_of[ci][qi]
    for kind, dist in (('drop', D96 - A[:, a]), ('alone', A[:, a])):
        r = q_fractional(dist, pr, ag)
        arr = npz[kind][npos[qid], a]
        dd = abs(float(r) - float(arr))
        if dd > maxd15: maxd15, worst15 = dd, (qid, ci, qi, a, kind, r, float(arr))
record('LOCO-7-CELLS', 'peraxis.npz 15 random cells recompute',
       'EXACT' if maxd15 <= 1e-12 else 'DIFF',
       f'max_abs_diff={maxd15:.3e} worst={worst15} tol=1e-12 cells={cells}',
       {'max_abs_diff': maxd15, 'worst': str(worst15)})

# split s=3 gap recompute from stored per_q_test vs summary
def make_split_loco(s):
    tr, te = [], []
    for c in (1, 2, 3, 4):
        qs = sorted([qid for qid in valid_qids if Q[qid]['cat'] == c],
                    key=lambda q: hashlib.sha256(f'deney1loco|{s}|{q}'.encode()).hexdigest())
        for i, q in enumerate(qs):
            (tr if i % 2 == 0 else te).append(q)
    return sorted(tr), sorted(te)
tr3, te3 = make_split_loco(3)
sp3 = LOCO['splits'][3]
ntest_ok = (len(te3) == sp3['run']['n_test'] == len(sp3['per_q_test']['drop64']))
pq3 = sp3['per_q_test']
d3 = np.array(pq3['drop64']); a3 = np.array(pq3['alone64'])
R3 = np.array([pq3[f'RANDOM64_s{sd}'] for sd in rand_seeds(3)])
g3 = float(d3.mean() - max(v.mean() for v in R3))*100
g3a = float(a3.mean() - max(v.mean() for v in R3))*100
ok3 = abs(g3-sp3['run']['gap64_vs_best_pp']) < 1e-9 and abs(g3a-sp3['run']['gap64_alone_vs_best_pp']) < 1e-9
record('LOCO-7-S3', 'LoCoMo s=3 gap vs best-of-10 recompute',
       'EXACT' if (ok3 and ntest_ok) else 'DIFF',
       f"n_test_re={len(te3)} stored={sp3['run']['n_test']} perq_len={len(sp3['per_q_test']['drop64'])} "
       f"gap_drop_re={g3!r} stored={sp3['run']['gap64_vs_best_pp']!r} "
       f"gap_alone_re={g3a!r} stored={sp3['run']['gap64_alone_vs_best_pp']!r}",
       {'gap_drop': g3, 'gap_alone': g3a})
# full loco summary recompute
lg_d = []; lg_a = []
for s in range(10):
    pq = LOCO['splits'][s]['per_q_test']
    dd = np.array(pq['drop64']); aa = np.array(pq['alone64'])
    RR = np.array([np.array(pq[f'RANDOM64_s{sd}']).mean() for sd in rand_seeds(s)])
    lg_d.append(float(dd.mean()-RR.max())*100); lg_a.append(float(aa.mean()-RR.max())*100)
ls = LOCO['summary']['drop64_gap_vs_best_pp']; la = LOCO['summary']['alone64_gap_vs_best_pp']
ld = [abs(float(np.mean(lg_d))-ls['mean']), abs(float(np.median(lg_d))-ls['median']),
      abs(min(lg_d)-ls['range'][0]), abs(max(lg_d)-ls['range'][1]),
      abs(float(np.mean(lg_a))-la['mean']), abs(float(np.median(lg_a))-la['median']),
      abs(min(lg_a)-la['range'][0]), abs(max(lg_a)-la['range'][1])]
lw = (f"{sum(1 for x in lg_d if x>0)}/10" == ls['wins'] and f"{sum(1 for x in lg_a if x>0)}/10" == la['wins'])
record('LOCO-7-SUMMARY', 'LoCoMo summary recompute',
       'EXACT' if (max(ld) < 1e-9 and lw) else 'DIFF',
       f"max_diff={max(ld):.3e} wins_ok={lw} drop_mean={float(np.mean(lg_d))!r} stored={ls['mean']!r} "
       f"wins={sum(1 for x in lg_d if x>0)}/10 stored={ls['wins']} "
       f"alone_mean={float(np.mean(lg_a))!r} stored={la['mean']!r} wins={sum(1 for x in lg_a if x>0)}/10 stored={la['wins']}",
       {'drop_mean': float(np.mean(lg_d)), 'alone_mean': float(np.mean(lg_a)), 'max_diff': max(ld)})

# ---- CHECK 8: kill-criteria arithmetic ----
kd = float(np.mean(gaps_d)); kw = f"{sum(1 for x in gaps_d if x>0)}/10"; kl = float(np.mean(lg_d))
c8a = kd < 1.0; c8b = (sum(1 for x in gaps_d if x>0) < 7); c8c = kl <= 0
rep_ok = (round(kd,2) == -1.25 and kw == '2/10' and round(kl,2) == -0.15)
record('KILL-8', 'kill-criteria arithmetic',
       'EXACT' if (c8a and c8b and c8c and rep_ok) else 'DIFF',
       f"LME mean-vs-best={kd:.6f}pp (<+1.0: {c8a}); LME wins={kw} (<7/10: {c8b}); "
       f"LoCoMo mean-vs-best={kl:.6f}pp (<=0: {c8c}); report claims (-1.25pp,2/10,-0.15pp) "
       f"round_match={rep_ok} (round LME={round(kd,2)}, loco={round(kl,2)})",
       {'lme_mean': kd, 'lme_wins': kw, 'loco_mean': kl})

# ---- CHECK 9: JSON self-consistency ----
issues = []
for s in range(10):
    sp = LME['splits'][s]
    if len(sp['train_qids'])+len(sp['test_qids']) != 470:
        issues.append(f'LME s={s} count {len(sp["train_qids"])}+{len(sp["test_qids"])}')
    if len(set(sp['train_qids']) & set(sp['test_qids'])) != 0:
        issues.append(f'LME s={s} overlap')
    for n, c in sp['arms'].items():
        cc = c['cols']
        k = int(n.split('_s')[0][len('RANDOM'):] if n.startswith('RANDOM') else ''.join(ch for ch in n if ch.isdigit()))
        if len(cc) != k or min(cc) < 0 or max(cc) > 95 or len(set(cc)) != k:
            issues.append(f'LME s={s} arm {n} bad cols')
    for n, v in sp['per_q_test'].items():
        a = np.array(v, float)
        if len(a) != len(sp['test_qids']) or bool(np.isnan(a).any()):
            issues.append(f'LME s={s} perq {n} len/nan')
for s in range(10):
    sp = LOCO['splits'][s]
    for n, c in sp['arms'].items():
        cc = c['cols']
        k = int(n.split('_s')[0][len('RANDOM'):] if n.startswith('RANDOM') else ''.join(ch for ch in n if ch.isdigit()))
        if len(cc) != k or min(cc) < 0 or max(cc) > 95 or len(set(cc)) != k:
            issues.append(f'LOCO s={s} arm {n} bad cols')
    for n, v in sp['per_q_test'].items():
        a = np.array(v, float)
        if bool(np.isnan(a).any()):
            issues.append(f'LOCO s={s} perq {n} nan')
    if sp['run']['n_test'] != len(sp['per_q_test']['drop64']):
        issues.append(f"LOCO s={s} n_test mismatch")
# SPREAD eff_k: distinct positions per k in {32,48,64} both datasets (checked via cols uniqueness above; state)
record('JSON-9', 'JSON self-consistency',
       'EXACT' if not issues else 'DIFF',
       f"issues={issues if issues else 'none'}; LME 10x(236/234 or balanced, train+test=470) checked; "
       f"arms cols in 0..95 unique len==k checked (LME 45 + LoCoMo 42 arm entries per split); per_q NaN/len checked",
       {'issues': issues})

CANNOT = [
    'LoCoMo split membership lists: deney1_loco_details.json stores no train_qids/test_qids (only run n_test + per_q_test); s=3 membership vs stored list cannot be checked — only reconstructed counts (767/768 pattern) vs run n_test.',
    'r2c_replicate.py not found in repo (only reports/muse_sessions/r2c_r2.json matched r2c*); LoCoMo protocol verbatim-ness vs frozen R2C checked only against harness/deney1_loco.py text, not an independent r2c source.',
    'Train-side per-question FR (per_q_tr) computed by scripts but not persisted in either details JSON; train FR values cannot be checked.',
    'Bootstrap CIs for splits other than LME s=0 not recomputed (same code path verified once); LoCoMo CI seed 778000+s path not re-executed.',
    'LME delta-arm utility top-64 (U_delta) not in check-2 arm list (only drop/alone/var per task spec); delta64 cols trusted from same argsort path.',
    'No network use; hashes in HASHES_ROUND3.txt not re-verified (out of task scope).',
]
OUT = {'checks': CHECKS, 'cannot_check': CANNOT,
       'counts': {'exact': sum(1 for c in CHECKS if c['status']=='EXACT'),
                  'diff': sum(1 for c in CHECKS if c['status']=='DIFF'),
                  'info': sum(1 for c in CHECKS if c['status']=='INFO'),
                  'total': len(CHECKS)}}
(OUTD/'d1v_details.json').write_text(json.dumps(OUT, indent=1))
print('WROTE /tmp/d1v/d1v_details.json', OUT['counts'], flush=True)
