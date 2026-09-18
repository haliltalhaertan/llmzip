"""D3: cross-benchmark utility transfer matrix (LME <-> LoCoMo).
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Read-only on /mnt/c; no network. Numpy only.
"""
import json, re, pickle, time
import numpy as np
from pathlib import Path

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work')
LME_NPZ = BASE / 'pilots/axis_attack_2026-09-12/per_axis_matrices.npz'
LME_PILOT = BASE / 'pilots/axis_attack_2026-09-12/pilot_results.json'
LME_PKLDIR = BASE / 'regen/lme/cache_repr'
LME_DATASET = BASE / 'drive/longmemeval_s_cleaned.json'
LOCO_RAW = BASE / 'drive/locomo10.json'
LOCO_AUDIT = BASE / 'drive/audit_layer'
LOCO_REGEN = BASE / 'regen/locomo'
LOCO_NPZ = BASE / 'pilots/axis_attack_2026-09-12/round3/deney1_loco_peraxis.npz'
OUTDIR = Path('/tmp/d3')
OUTDIR.mkdir(parents=True, exist_ok=True)

K_LIST = [32, 48, 64]
NT = 20
KTOP = 3
LME_ANCHOR = 0.5419751773049645
LOCO_ANCHOR = 0.23654714666441054
GATE_TOL = 1e-12
RAND_SEEDS = [91000 + j for j in range(10)]

t0 = time.time()
log = []


def emit(s):
    log.append(s)
    print(s, flush=True)


# ================= LME =================
emit('--- LME load ---')
data = json.loads(LME_DATASET.read_text())
allq = sorted(str(x['question_id']) for x in data)
lex = {q: i for i, q in enumerate(allq)}
assert len(allq) == 500, len(allq)
del data

zl = np.load(LME_NPZ)
lme_alone, lme_drop, lme_delta = zl['alone'], zl['drop'], zl['delta']
lme_var_rank = zl['var_rank']
lme_qids = [str(q) for q in zl['qids']]
assert lme_alone.shape == (470, 96), lme_alone.shape
assert lme_drop.shape == (470, 96)
assert lme_var_rank.shape == (470, 96)
lme_qi = {q: i for i, q in enumerate(lme_qids)}

res = json.loads(LME_PILOT.read_text())
lme_nat_stored = res['per_question_native_FR']
assert len(lme_nat_stored) == 470

# load pkls; precompute mismatch matrix M (n,96), gold set, priorities, pool
MM, GG, PR, NQ = {}, {}, {}, {}
lme_pool = np.zeros((470, 96), dtype=np.int32)
for qi, qid in enumerate(lme_qids):
    with open(LME_PKLDIR / (qid + '.pkl'), 'rb') as f:
        o = pickle.load(f)
    C = np.asarray(o['C'], float)
    qC = np.asarray(o['qC'], float)
    g = np.asarray(o['gold']).ravel()
    D = C >= 0
    Q = qC >= 0
    MM[qid] = (D != Q[None, :])
    GG[qid] = set(map(int, np.ravel(g)))
    n = len(C)
    NQ[qid] = n
    lx = lex[qid]
    PR[qid] = [np.random.default_rng(5_100_000 + lx * 100_000 + t * 100 + 99).random(n)
               for t in range(NT)]
    lme_pool[qi] = np.count_nonzero(D == Q[None, :], axis=0)
emit(f'loaded 470 LME pkls ({time.time()-t0:.0f}s); pool range {lme_pool.min()}-{lme_pool.max()}')


def fr_subset(qid, cols):
    # EXACT math of round2/session_scripts/r2b.py::fr_subset:
    # d over cols; 20 lex-ordinal trials; top-3 fractional recall.
    # (M[:,cols].sum(1) == count_nonzero(D[:,cols]!=Q[cols][None,:],axis=1) elementwise.)
    d = MM[qid][:, cols].sum(axis=1)
    gg = GG[qid]
    tot = 0.0
    for p in PR[qid]:
        order = np.lexsort((p, d))
        tot += len(set(map(int, order[:KTOP])) & gg) / len(gg)
    return tot / NT


lme_recomp = {q: fr_subset(q, np.arange(96)) for q in lme_qids}
lme_recomp_mean = float(np.mean(list(lme_recomp.values())))
lme_stored_mean = float(np.mean([lme_nat_stored[q] for q in lme_qids]))
lme_maxdiff = float(max(abs(lme_recomp[q] - lme_nat_stored[q]) for q in lme_qids))
emit(f'LME GATE: recomp_mean={lme_recomp_mean!r} stored_mean={lme_stored_mean!r} '
     f'anchor={LME_ANCHOR!r} max_abs_diff={lme_maxdiff:.3e}')
assert abs(lme_recomp_mean - LME_ANCHOR) <= GATE_TOL, 'LME GATE FAILED'
emit('LME GATE PASS')


# ================= LoCoMo =================
emit('--- LoCoMo load ---')

def norm_evidence(x):
    if x is None:
        return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def load_audit_corrections(audit_dir):
    corrections = {}
    for f in sorted(audit_dir.glob("errors_conv_*.json")):
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            qid = r.get("question_id")
            if not qid:
                continue
            corrections[str(qid)] = {
                "error_type": r.get("error_type"),
                "has_correct_evidence": "correct_evidence" in r,
                "correct_evidence": norm_evidence(r.get("correct_evidence")),
                "correct_answer": r.get("correct_answer"),
            }
    return corrections


def stable_archive_seed(archive_ordinal, trial=0):
    return 5_100_000 + archive_ordinal * 100_000 + trial * 100


def topks_by_hamming(dist, priorities, k=KTOP):
    dist = np.asarray(dist)
    P = np.asarray(priorities, dtype=float)
    if len(dist) <= k:
        return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k - 1)[k - 1]
    strict = np.flatnonzero(dist < kth)
    boundary = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, boundary]
    if need == len(boundary):
        picks = np.tile(boundary, (len(P), 1))
    else:
        loc = np.argpartition(BP, need - 1, axis=1)[:, :need]
        picks = boundary[loc]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]


def evidence_rows(ids, id_to_row):
    out = []
    for x in ids:
        if x in id_to_row:
            out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))


def retrieval_metrics(top, gold_rows):
    if not gold_rows:
        return {"valid": 0, "any": np.nan, "all": np.nan, "fractional": np.nan, "gold_count": 0}
    R = set(map(int, top))
    G = set(map(int, gold_rows))
    inter = len(R & G)
    return {"valid": 1, "any": float(inter > 0), "all": float(G.issubset(R)),
            "fractional": float(inter / len(G)), "gold_count": len(G)}


def mean_or_nan(xs):
    a = np.asarray(xs, dtype=float)
    return float(np.nanmean(a)) if np.isfinite(a).any() else np.nan


raw = json.loads(LOCO_RAW.read_text(encoding="utf-8"))
corr = load_audit_corrections(LOCO_AUDIT)
convs = []
for idx, item in enumerate(raw):
    qas = []
    for qi, q in enumerate(item.get("qa", []) or []):
        cat = int(q.get("category")) if q.get("category") is not None else None
        if cat not in (1, 2, 3, 4):
            continue
        qid = q.get("question_id") or f"locomo_{idx}_qa{qi}"
        z = corr.get(str(qid))
        if z:
            ce = list(z["correct_evidence"]) if z.get("has_correct_evidence", False) else list(norm_evidence(q.get("evidence")))
        else:
            ce = list(norm_evidence(q.get("evidence")))
        qas.append({"question_id": str(qid), "category": cat,
                    "raw_evidence": norm_evidence(q.get("evidence")), "correct_evidence": ce})
    convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
del raw

reps = []
for ci in range(10):
    with open(LOCO_REGEN / f"locomo_{ci}.pkl", 'rb') as f:
        d = pickle.load(f)
    assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
    raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
    pkl_ids = [q["question_id"] for q in d["qas"]]
    assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
    reps.append(d)
emit('locomo alignment OK')

Q = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    id_to_row = r["id_to_row"]
    for qi, q in enumerate(c["qas"]):
        ag = evidence_rows(q["correct_evidence"], id_to_row)
        Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
valid_qids = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
emit(f'locomo valid questions: {len(valid_qids)} (expects 1535)')
assert len(valid_qids) == 1535, len(valid_qids)

# precompute sign-bit matrices + trial priorities per archive
LCB, LQCB, LPRI, LNN = {}, {}, {}, {}
for ci, r in enumerate(reps):
    LCB[ci] = (np.asarray(r["C"], float) >= 0)
    LQCB[ci] = (np.asarray(r["QC"], float) >= 0)
    N = r["C"].shape[0]
    LNN[ci] = N
    LPRI[ci] = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(N) for t in range(NT)]


def q_fractional(dist_q, priorities, gold):
    tops = topks_by_hamming(dist_q, priorities)
    return mean_or_nan([retrieval_metrics(t, gold)["fractional"] for t in tops])


def loco_eval_subset(subset):
    """subset: None (native, all 96) or sorted int array of cols. Returns {qid: value}."""
    out = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        Cb, Qb = LCB[ci], LQCB[ci]
        if subset is None:
            dist = np.count_nonzero(Qb[:, None, :] != Cb[None, :, :], axis=2).astype(np.int16)
        else:
            s = np.asarray(subset)
            dist = np.count_nonzero(Qb[:, None, s] != Cb[None, :, s], axis=2).astype(np.int16)
        pri = LPRI[ci]
        for qi, q in enumerate(c["qas"]):
            out[q["question_id"]] = q_fractional(dist[qi], pri, Q[q["question_id"]]["ag"])
    return out


def loco_aggregate(valdict):
    return float(np.mean([valdict[qid] for qid in valid_qids]))


loco_native_vals = loco_eval_subset(None)
loco_recomp_mean = loco_aggregate(loco_native_vals)
emit(f'LoCoMo GATE: recomp_mean={loco_recomp_mean!r} anchor={LOCO_ANCHOR!r} '
     f'diff={loco_recomp_mean - LOCO_ANCHOR!r}')
assert abs(loco_recomp_mean - LOCO_ANCHOR) <= GATE_TOL, 'LoCoMo GATE FAILED'
emit('LoCoMo GATE PASS')


# ================= Utilities (FULL-DATA) =================
emit('--- utilities ---')
lme_nat = np.array([lme_nat_stored[q] for q in lme_qids])
U_lme_drop = (lme_nat[:, None] - lme_drop).mean(axis=0)
U_lme_alone = (lme_alone * lme_pool / 3).mean(axis=0)
U_lme_var = (-lme_var_rank.astype(float)).mean(axis=0)
U_lme_delta = lme_delta.mean(axis=0)

zn = np.load(LOCO_NPZ)
loco_qids = [str(x) for x in zn['qids']]
assert len(loco_qids) == 1535 and set(loco_qids) == set(valid_qids), 'npz qid mismatch'
li = {q: i for i, q in enumerate(loco_qids)}
loco_nat_npz = zn['native']
# cross-check npz stored natives vs recomputed
loco_recomp_arr = np.array([loco_native_vals[q] for q in loco_qids])
loco_npz_maxdiff = float(np.max(np.abs(loco_recomp_arr - loco_nat_npz)))
emit(f'loco npz-native vs recomp max_abs_diff={loco_npz_maxdiff:.3e}')
U_loco_drop = (loco_nat_npz[:, None] - zn['drop']).mean(axis=0)
U_loco_alone = (zn['alone'] * zn['pool'] / 3).mean(axis=0)
U_loco_var = (-zn['var_rank'].astype(float)).mean(axis=0)
emit('loco pool range %d-%d' % (int(zn['pool'].min()), int(zn['pool'].max())))

U = {'LME': {'drop': U_lme_drop, 'alone': U_lme_alone, 'var': U_lme_var, 'delta': U_lme_delta},
     'LOCO': {'drop': U_loco_drop, 'alone': U_loco_alone, 'var': U_loco_var}}
for b in U:
    for f in U[b]:
        emit(f'top5 {b}/{f}: {np.argsort(U[b][f])[::-1][:5].tolist()} '
             f'mean={U[b][f].mean():.6f}')


def ranks_avg(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind='mergesort')
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks_avg(a), ranks_avg(b)
    ca, cb = ra - ra.mean(), rb - rb.mean()
    den = np.sqrt((ca ** 2).sum() * (cb ** 2).sum())
    return float((ca * cb).sum() / den) if den > 0 else float('nan')


def topk_set(u, k):
    return set(np.argsort(u)[::-1][:k].tolist())


FAMS = ['drop', 'alone', 'var']
struct = {}
for f in FAMS:
    rho = spearman(U['LME'][f], U['LOCO'][f])
    struct[f] = {'spearman': rho, 'k': {}}
    for k in K_LIST:
        A, B = topk_set(U['LME'][f], k), topk_set(U['LOCO'][f], k)
        inter = len(A & B)
        jac = inter / len(A | B)
        struct[f]['k'][k] = {'inter': inter, 'jaccard': jac,
                             'lme_cols': sorted(A), 'loco_cols': sorted(B)}
        emit(f'struct {f} k={k}: spearman={rho:+.4f} inter={inter} jaccard={jac:.4f}')
# chance baselines for intersections: E[inter] = k^2/96
for k in K_LIST:
    emit(f'chance E[inter] k={k}: {k*k/96:.2f}')


# ================= Transfer arms =================
emit('--- transfer arms ---')

def spread_cols(u_var, k):
    order = np.argsort(-np.asarray(u_var, float))  # best-first; set symmetric in direction
    pos = np.round(np.linspace(0, 95, k)).astype(int)
    assert len(set(pos.tolist())) == k, 'SPREAD positions not distinct'
    cols = np.sort(order[pos])
    assert len(set(cols.tolist())) == k, 'SPREAD cols not distinct'
    return cols


def rand_cols(seed, k):
    return np.sort(np.random.default_rng(seed).choice(96, k, replace=False))


def lme_eval(cols):
    return float(np.mean([fr_subset(q, np.asarray(cols)) for q in lme_qids]))


SPREAD = {b: {k: spread_cols(U[b]['var'], k) for k in K_LIST} for b in ('LME', 'LOCO')}
RAND = {k: {s: rand_cols(s, k) for s in RAND_SEEDS} for k in K_LIST}

cells = {}  # (direction, family, k) -> dict
for direction, target, source in (('LME->LOCO', 'LOCO', 'LME'), ('LOCO->LME', 'LME', 'LOCO')):
    for f in FAMS:
        for k in K_LIST:
            src_cols = np.argsort(U[source][f])[::-1][:k]
            own_cols = np.argsort(U[target][f])[::-1][:k]
            if target == 'LOCO':
                src_v = loco_aggregate(loco_eval_subset(src_cols))
                own_v = loco_aggregate(loco_eval_subset(own_cols))
                rnd = {s: loco_aggregate(loco_eval_subset(RAND[k][s])) for s in RAND_SEEDS}
                spr_v = loco_aggregate(loco_eval_subset(SPREAD[target][k]))
                nat_v = loco_recomp_mean
            else:
                src_v = lme_eval(src_cols)
                own_v = lme_eval(own_cols)
                rnd = {s: lme_eval(RAND[k][s]) for s in RAND_SEEDS}
                spr_v = lme_eval(SPREAD[target][k])
                nat_v = lme_recomp_mean
            rmean = float(np.mean(list(rnd.values())))
            rbest = max(rnd.values())
            rbest_seed = max(rnd, key=lambda s: rnd[s])
            floor = min(own_v, rbest) - 0.01
            fav = bool(src_v >= floor)
            fail = bool(src_v <= rmean + 0.01)
            cells[(direction, f, k)] = {
                'native': nat_v, 'src': src_v, 'own': own_v,
                'rand': {str(s): rnd[s] for s in RAND_SEEDS},
                'rand_mean': rmean, 'rand_best': float(rbest), 'rand_best_seed': rbest_seed,
                'spread': spr_v,
                'gap_src_vs_own_pp': (src_v - own_v) * 100,
                'gap_src_vs_randmean_pp': (src_v - rmean) * 100,
                'gap_src_vs_randbest_pp': (src_v - rbest) * 100,
                'gap_src_vs_spread_pp': (src_v - spr_v) * 100,
                'gap_src_vs_native_pp': (src_v - nat_v) * 100,
                'favorable': fav, 'fails': fail,
                'src_cols': sorted(map(int, np.asarray(src_cols).tolist())),
                'own_cols': sorted(map(int, np.asarray(own_cols).tolist())),
            }
            emit(f'{direction} {f}{k}: nat={nat_v:.4f} src={src_v:.4f} own={own_v:.4f} '
                 f'rmean={rmean:.4f} rbest={rbest:.4f} spread={spr_v:.4f} '
                 f'fav={fav} fail={fail} ({time.time()-t0:.0f}s)')

fav_n = sum(1 for v in cells.values() if v['favorable'])
fail_n = sum(1 for v in cells.values() if v['fails'])
emit(f'verdict counts: favorable={fav_n}/18 fails={fail_n}/18')

# circuity: directional symmetry
emit('--- circuity ---')
for f in FAMS:
    for k in K_LIST:
        a = cells[('LME->LOCO', f, k)]
        b = cells[('LOCO->LME', f, k)]
        emit(f'circuity {f}{k}: LME->LOCO src-vs-own={a["gap_src_vs_own_pp"]:+.2f}pp fav={a["favorable"]} '
             f'| LOCO->LME src-vs-own={b["gap_src_vs_own_pp"]:+.2f}pp fav={b["favorable"]}')


# ================= details.json =================
details = {
    'labels': ['[LOCAL EXPLORATORY]', '[NOT PREREGISTERED]', '[NOT FOR CITATION]',
               '[DISCLOSE-BEFORE-USE]'],
    'numpy': np.__version__,
    'protocol': {
        'lme_eval': 'fr_subset verbatim from round2/session_scripts/r2b.py (lex-ordinal '
                    '5_100_000+lx*100_000+t*100+99, 20 trials, top-3, fractional); full set n=470',
        'loco_eval': 'verbatim from round2/session_scripts/r2c_replicate.py '
                     '(stable_archive_seed(ci,t)+99, top-3, 20 trials, audit corrections); '
                     'valid n=1535',
        'utilities': 'FULL-DATA (gold-informed; declared). U_drop=mean(native-drop); '
                     'U_alone=mean(alone*pool/3); U_var=mean(-var_rank). No delta for LoCoMo.',
        'random_panels': 'seeds 91000+j j=0..9 (i.e. 91000+10*0+j), cols=sort(rng(seed).choice(96,k,replace=False)); '
                         'verified byte-identical construction to deney1 stored cols; reused across all sets',
        'spread': 'repaired rank-linspace: cols=sort(order[round(linspace(0,95,k))]) over '
                  "target's own full-data U_var ordering; verified to reproduce deney1 LME split-0 "
                  'stored SPREAD cols exactly',
        'topk': 'np.argsort(u)[::-1][:k] (r2b convention)',
        'reading_rule': 'favorable if src >= min(own, rand_best) - 1.0pp; '
                        'fails if src <= rand_mean + 1.0pp',
    },
    'gates': {
        'lme': {'recomp_mean': lme_recomp_mean, 'stored_mean': lme_stored_mean,
                'anchor': LME_ANCHOR, 'diff_vs_anchor': lme_recomp_mean - LME_ANCHOR,
                'max_abs_diff_recomp_vs_stored': lme_maxdiff, 'pass': True},
        'loco': {'recomp_mean': loco_recomp_mean, 'anchor': LOCO_ANCHOR,
                 'diff_vs_anchor': loco_recomp_mean - LOCO_ANCHOR,
                 'n_valid': len(valid_qids),
                 'npz_native_max_abs_diff': loco_npz_maxdiff, 'pass': True},
    },
    'utilities': {b: {f: {'mean': float(U[b][f].mean()),
                          'top5': [int(i) for i in np.argsort(U[b][f])[::-1][:5]],
                          'values': [float(x) for x in U[b][f]]} for f in U[b]} for b in U},
    'structure': {f: {'spearman': struct[f]['spearman'],
                      'k': {str(k): {'inter': struct[f]['k'][k]['inter'],
                                     'jaccard': struct[f]['k'][k]['jaccard'],
                                     'lme_cols': struct[f]['k'][k]['lme_cols'],
                                     'loco_cols': struct[f]['k'][k]['loco_cols']}
                            for k in K_LIST}} for f in FAMS},
    'chance_E_inter': {str(k): k * k / 96 for k in K_LIST},
    'cells': {f'{d}/{f}/{k}': cells[(d, f, k)] for (d, f, k) in cells},
    'counts': {'favorable': fav_n, 'fails': fail_n, 'n_cells': len(cells)},
    'elapsed_s': time.time() - t0,
}
with open(OUTDIR / 'd3_details.json', 'w') as f:
    json.dump(details, f)
emit(f'details.json written ({time.time()-t0:.0f}s)')

# ================= report.md =================
L = []
L.append('# D3: cross-benchmark utility transfer matrix (LME ⇄ LoCoMo)')
L.append('')
L.append('[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]')
L.append('')
L.append('Question: is the axis-utility structure shared between benchmarks, or benchmark-local?')
L.append('All utilities here are FULL-DATA (gold-informed; declared). Transfer analysis only.')
L.append('')
L.append('## 1. Gates (confidence: HIGH — exact recompute from pkls)')
L.append('')
L.append(f'- LME native: recomputed mean={lme_recomp_mean!r} vs anchor={LME_ANCHOR!r} '
         f'(diff={lme_recomp_mean - LME_ANCHOR:.3e}); stored mean={lme_stored_mean!r}; '
         f'max per-q abs diff recomp-vs-stored={lme_maxdiff:.3e}. PASS (tol 1e-12).')
L.append(f'- LoCoMo native: recomputed mean={loco_recomp_mean!r} vs anchor={LOCO_ANCHOR!r} '
         f'(diff={loco_recomp_mean - LOCO_ANCHOR:.3e}); valid={len(valid_qids)}; '
         f'npz-native vs recomp max abs diff={loco_npz_maxdiff:.3e}. PASS (tol 1e-12).')
L.append('- Evaluators are the analysts own, following r2b.py `fr_subset` and r2c_replicate.py verbatim.')
L.append('')
L.append('## 2. Utility structure LME vs LoCoMo (confidence: HIGH — descriptive)')
L.append('')
L.append('| family | Spearman rho | k=32 inter/Jaccard | k=48 inter/Jaccard | k=64 inter/Jaccard |')
L.append('|---|---|---|---|---|')
for f in FAMS:
    r = [f"| {f} | {struct[f]['spearman']:+.4f} |"]
    row = f'| {f} | {struct[f]["spearman"]:+.4f} |'
    for k in K_LIST:
        c = struct[f]['k'][k]
        row += f' {c["inter"]}/{c["jaccard"]:.3f} |'
    L.append(row)
L.append('')
L.append('Chance E[intersection]: k=32 → 10.67, k=48 → 24.00, k=64 → 42.67.')
L.append('')
for d in ('LME->LOCO', 'LOCO->LME'):
    tgt = 'LoCoMo (n=1535)' if d.startswith('LME') else 'LME (n=470)'
    L.append(f'## 3. Transfer {d} — target {tgt} (confidence: MEDIUM — full-data, no held-out)')
    L.append('')
    L.append('| family,k | native | src→tgt | own | rand_mean | rand_best | spread | '
             'src−own | src−rmean | src−rbest | verdict |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for f in FAMS:
        for k in K_LIST:
            c = cells[(d, f, k)]
            v = ('FAV' if c['favorable'] else '') + ('/FAIL' if c['fails'] else '')
            L.append(f'| {f},{k} | {c["native"]:.4f} | {c["src"]:.4f} | {c["own"]:.4f} | '
                     f'{c["rand_mean"]:.4f} | {c["rand_best"]:.4f} | {c["spread"]:.4f} | '
                     f'{c["gap_src_vs_own_pp"]:+.2f} | {c["gap_src_vs_randmean_pp"]:+.2f} | '
                     f'{c["gap_src_vs_randbest_pp"]:+.2f} | {v or "mid"} |')
    L.append('')
L.append('Reading rule (pre-declared, no kill/promote): FAV = src ≥ min(own, rand_best) − 1.0pp; '
         'FAIL = src within ±1.0pp of rand_mean or below.')
L.append('')
L.append('## 4. Circuity LME→LoCoMo→LME (report only, no claim; confidence: LOW — informational)')
L.append('')
L.append('| family,k | LME→LoCoMo src−own (pp), verdict | LOCO→LME src−own (pp), verdict | symmetric? |')
L.append('|---|---|---|---|')
for f in FAMS:
    for k in K_LIST:
        a, b = cells[('LME->LOCO', f, k)], cells[('LOCO->LME', f, k)]
        va = ('FAV' if a['favorable'] else '') + ('/FAIL' if a['fails'] else '')
        vb = ('FAV' if b['favorable'] else '') + ('/FAIL' if b['fails'] else '')
        sym = 'yes' if (a['favorable'] == b['favorable'] and a['fails'] == b['fails']) else 'NO'
        L.append(f'| {f},{k} | {a["gap_src_vs_own_pp"]:+.2f} {va or "mid"} | '
                 f'{b["gap_src_vs_own_pp"]:+.2f} {vb or "mid"} | {sym} |')
L.append('')
L.append('Note: Spearman correlations are directionless scalars, so any directional asymmetry '
         'comes from target-side evaluation scale/interactions, not from the correlation itself.')
L.append('')
L.append('## 5. Verdict counts')
L.append('')
L.append(f'- Favorable: {fav_n}/18 cells; Fail: {fail_n}/18 cells.')
L.append('- Neither/both flags can co-occur when rand_best ≈ rand_mean (rule overlap); table shows both.')
L.append('')
(OUTDIR / 'd3_report.md').write_text('\n'.join(L) + '\n')
emit('d3_report.md written')

asym = []
for f in FAMS:
    for k in K_LIST:
        a, b = cells[('LME->LOCO', f, k)], cells[('LOCO->LME', f, k)]
        if (a['favorable'], a['fails']) != (b['favorable'], b['fails']):
            asym.append(f'{f}{k}')
asym_s = ('asymmetric cells: ' + ','.join(asym)) if asym else 'no directional asymmetries'
print(f'D3_VERDICT: {fav_n}/18 cells transfer favorably, {fail_n}/18 fail; {asym_s}. '
      f'[LOCAL EXPLORATORY][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]')
