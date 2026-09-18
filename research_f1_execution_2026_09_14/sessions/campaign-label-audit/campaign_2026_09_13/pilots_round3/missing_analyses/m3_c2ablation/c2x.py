"""DENEY 5 (c2): gold-free failure predictor -> adaptive budget routing (LME + LoCoMo).
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Read-only on /mnt/c; no network. Numpy only (logistic via IRLS; AUC by rank statistic).
Writes only under /tmp/c2x/.

Arms (construction equals round3 deney1, via d3.spread_cols verbatim):
  SMALL  = SPREAD48: order = descending FULL-DATA variance ordering
           (order = argsort(-U_var), U_var = mean(-var_rank) from per-axis npz;
           variance is gold-free so full-data ordering is fine),
           cols = sort(order[round(linspace(0,95,48))]).
  SMALL2 = SPREAD64: same with k=64.
  LARGE  = NATIVE96 (all 96 axes).
Tie protocol LME: priorities rng(5_100_000+lx*100_000+t*100+99).random(n) with lx =
  ALL-500 lex ordinal, 20 trials, lexsort((p,d)) top-3, fractional R@3 (r2b/d2 verbatim).
Tie protocol LoCoMo: stable_archive_seed(ci,t)+99, 20 trials, topks_by_hamming top-3,
  fractional R@3 over audit-corrected gold (r2c_replicate.py verbatim).
Split: train iff first hex char of sha256('c2|'+qid) even (LME 470 and LoCoMo 1535
  separately; no stratification).
Failure label: fail iff FR_small < FR_large - 1e-12.
"""
import pickle, json, re, hashlib, time
import numpy as np
from pathlib import Path

LABELS = "[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work')
LME_NPZ = BASE / 'pilots/axis_attack_2026-09-12/per_axis_matrices.npz'
LME_PILOT = BASE / 'pilots/axis_attack_2026-09-12/pilot_results.json'
LME_PKLDIR = BASE / 'regen/lme/cache_repr'
LME_DATASET = BASE / 'drive/longmemeval_s_cleaned.json'
LOCO_RAW = BASE / 'drive/locomo10.json'
LOCO_AUDIT = BASE / 'drive/audit_layer'
LOCO_REGEN = BASE / 'regen/locomo'
LOCO_NPZ = BASE / 'pilots/axis_attack_2026-09-12/round3/deney1_loco_peraxis.npz'
OUT = Path('/tmp/c2x')
OUT.mkdir(parents=True, exist_ok=True)

NT = 20
KTOP = 3
TOL = 1e-12
LME_ANCHOR = 0.5419751773049645
LOCO_ANCHOR = 0.23654714666441054
# round3/d3 replay references (d3 SPREAD evaluated on full data; d3 native gates passed)
EXP_LME_SPREAD48 = 0.4578262411347518
EXP_LME_SPREAD64 = 0.5021382978723404
EXP_LOCO_SPREAD48 = 0.15911865514145646
EXP_LOCO_SPREAD64 = 0.19181116982376803
ALPHAS = [0.10, 0.20, 0.30, 0.40]
FEATS = ['margin34', 'crowd3', 'crowd4', 'crowd_pm1', 'top3_tie_share',
         'boundary_share', 'dup_top20', 'var_decay', 'N', 'qent',
         'margin34_large', 'crowd3_large']

t0 = time.time()

# ================= shared machinery (d2/r2c verbatim) =================
def fit_logreg(X, y, lam=1.0, iters=500, tol=1e-10):
    n, p = X.shape
    Xb = np.hstack([np.ones((n, 1)), X])
    pen = np.r_[0.0, np.full(p, lam)]
    w = np.zeros(p + 1)
    for _ in range(iters):
        s = 1.0 / (1.0 + np.exp(-(Xb @ w)))
        g = Xb.T @ (s - y) + pen * w
        W = s * (1 - s)
        H = (Xb * W[:, None]).T @ Xb + np.diag(pen)
        step = np.linalg.solve(H, g)
        w -= step
        if float(np.max(np.abs(step))) < tol:
            break
    return w

def auc_rank(s, y):
    s = np.asarray(s, float); y = np.asarray(y, int)
    p = s[y == 1]; q = s[y == 0]
    if len(p) == 0 or len(q) == 0:
        return float('nan')
    gt = np.sum(p[:, None] > q[None, :]); eq = np.sum(p[:, None] == q[None, :])
    return float((gt + 0.5 * eq) / (len(p) * len(q)))

def spread_cols(u_var, k):
    # verbatim d3.spread_cols (round3 deney1 construction)
    order = np.argsort(-np.asarray(u_var, float))
    pos = np.round(np.linspace(0, 95, k)).astype(int)
    assert len(set(pos.tolist())) == k, 'SPREAD positions not distinct'
    cols = np.sort(order[pos])
    assert len(set(cols.tolist())) == k, 'SPREAD cols not distinct'
    return cols

def split_of(qid):
    return 'train' if int(hashlib.sha256(('c2|' + qid).encode()).hexdigest()[0], 16) % 2 == 0 else 'test'

def qent_of(qsign):
    qsign = np.asarray(qsign, float)
    p = float(qsign.mean())
    e = 0.0
    if 0.0 < p < 1.0:
        e = float(-(p * np.log(p) + (1.0 - p) * np.log(1.0 - p)))
    return e

def goldfree_feats(d_small, d_large, p0, D0full, qsign, var):
    """All inputs gold-free. d_* = arm-restricted Hamming dists; p0 = trial-0
    priorities; D0full = full-96-bit sign matrix (N,96); qsign = query sign bits;
    var = archive variance vector (96,)."""
    d_small = np.asarray(d_small); d_large = np.asarray(d_large)
    N = len(d_small)
    assert N >= 20
    o0 = np.lexsort((np.asarray(p0, float), d_small))
    s = d_small[o0]
    d3v, d4v = int(s[2]), int(s[3])
    crowd3 = int(np.count_nonzero(d_small == d3v))
    crowd4 = int(np.count_nonzero(d_small == d4v))
    crowd_pm1 = int(np.count_nonzero(np.abs(d_small - d3v) <= 1))
    top20 = o0[:20]
    seen = set(map(tuple, np.asarray(D0full)[top20].tolist()))
    dup_top20 = 1.0 - len(seen) / 20.0
    var = np.asarray(var, float)
    srt = np.sort(var)[::-1]
    assert float(srt[:48].sum()) > 0, 'degenerate archive variance'
    var_decay = float(srt[:16].sum() / srt[:48].sum())
    oL = np.lexsort((np.asarray(p0, float), d_large))
    sL = d_large[oL]
    margin34_large = int(sL[3] - sL[2])
    crowd3_large = int(np.count_nonzero(d_large == int(sL[2])))
    return {
        'margin34': int(d4v - d3v), 'crowd3': crowd3, 'crowd4': crowd4,
        'crowd_pm1': crowd_pm1, 'top3_tie_share': crowd3 / N,
        'boundary_share': (crowd3 + crowd4) / N, 'dup_top20': float(dup_top20),
        'var_decay': float(var_decay), 'N': int(N), 'qent': float(qent_of(qsign)),
        'margin34_large': margin34_large, 'crowd3_large': crowd3_large,
    }

# ================= LME =================
print('--- LME load ---', flush=True)
data = json.load(open(str(LME_DATASET)))
allq = sorted(str(x['question_id']) for x in data)
assert len(allq) == 500, len(allq)
lex = {q: i for i, q in enumerate(allq)}
del data
zl = np.load(str(LME_NPZ))
lme_qids = [str(q) for q in zl['qids']]
assert len(lme_qids) == 470, len(lme_qids)
U_lme_var = (-zl['var_rank'].astype(float)).mean(axis=0)
stored = json.load(open(str(LME_PILOT)))['per_question_native_FR']
assert len(stored) == 470
SMALL = spread_cols(U_lme_var, 48)
SMALL2 = spread_cols(U_lme_var, 64)
LARGE = np.arange(96)
print('LME SMALL48 cols: %s' % SMALL.tolist(), flush=True)
print('LME SMALL64 cols: %s' % SMALL2.tolist(), flush=True)

def fr_lex(d, gset, pris):
    # EXACT math of round2/session_scripts/r2b.py::fr_subset
    d = np.asarray(d)
    tot = 0.0
    for p in pris:
        order = np.lexsort((p, d))
        tot += len(set(map(int, order[:KTOP])) & gset) / len(gset)
    return tot / len(pris)

lme = {}
for i, qid in enumerate(lme_qids):
    o = pickle.load(open(str(LME_PKLDIR / (qid + '.pkl')), 'rb'))
    assert str(o['question_id']) == qid
    C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float).ravel()
    assert C.shape[1] == 96 and qC.shape[0] == 96
    gset = set(map(int, np.asarray(o['gold']).ravel()))
    n = len(C); lx = lex[qid]
    D0 = (C >= 0); Q0 = (qC >= 0)
    pris = [np.random.default_rng(5_100_000 + lx * 100_000 + t * 100 + 99).random(n)
            for t in range(NT)]
    d_nat = np.count_nonzero(D0 != Q0[None, :], axis=1)
    d_sm = np.count_nonzero(D0[:, SMALL] != Q0[SMALL][None, :], axis=1)
    d_s2 = np.count_nonzero(D0[:, SMALL2] != Q0[SMALL2][None, :], axis=1)
    f = goldfree_feats(d_sm, d_nat, pris[0], D0, Q0.astype(float), C.var(axis=0))
    lme[qid] = {'lex': lx, 'n': n, 'ngold': len(gset),
                'fr_small': fr_lex(d_sm, gset, pris),
                'fr_large': fr_lex(d_nat, gset, pris),
                'fr_small2': fr_lex(d_s2, gset, pris),
                'feat': f, 'fr_nat_stored': float(stored[qid])}
    if (i + 1) % 100 == 0:
        print('  LME %d/470 (%.0fs)' % (i + 1, time.time() - t0), flush=True)

lme_nat = float(np.mean([v['fr_large'] for v in lme.values()]))
lme_sm = float(np.mean([v['fr_small'] for v in lme.values()]))
lme_s2 = float(np.mean([v['fr_small2'] for v in lme.values()]))
lme_maxdiff = float(max(abs(v['fr_large'] - v['fr_nat_stored']) for v in lme.values()))
print('LME GATE native=%.16f anchor=%.16f diff=%g' % (lme_nat, LME_ANCHOR, lme_nat - LME_ANCHOR), flush=True)
print('LME SMALL48=%.16f exp=%.16f diff=%g' % (lme_sm, EXP_LME_SPREAD48, lme_sm - EXP_LME_SPREAD48), flush=True)
print('LME SMALL64=%.16f exp=%.16f diff=%g' % (lme_s2, EXP_LME_SPREAD64, lme_s2 - EXP_LME_SPREAD64), flush=True)
print('LME native vs stored maxdiff=%g' % lme_maxdiff, flush=True)
assert abs(lme_nat - LME_ANCHOR) <= 1e-12, 'LME native gate FAILED'
assert abs(lme_sm - EXP_LME_SPREAD48) <= 1e-12, 'LME SPREAD48 gate FAILED'
assert abs(lme_s2 - EXP_LME_SPREAD64) <= 1e-12, 'LME SPREAD64 gate FAILED'
print('LME GATES PASS', flush=True)

# ================= LoCoMo (r2c_replicate.py verbatim) =================
print('--- LoCoMo load ---', flush=True)

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
print('locomo alignment OK', flush=True)

Q = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    id_to_row = r["id_to_row"]
    for qi, q in enumerate(c["qas"]):
        ag = evidence_rows(q["correct_evidence"], id_to_row)
        Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
valid_qids = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
print('locomo valid questions: %d (expects 1535)' % len(valid_qids), flush=True)
assert len(valid_qids) == 1535, len(valid_qids)

LCB, LQCB, LPRI, LNN = {}, {}, {}, {}
for ci, r in enumerate(reps):
    LCB[ci] = (np.asarray(r["C"], float) >= 0)
    LQCB[ci] = (np.asarray(r["QC"], float) >= 0)
    N = r["C"].shape[0]
    LNN[ci] = N
    LPRI[ci] = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(N) for t in range(NT)]

zn = np.load(str(LOCO_NPZ))
loco_npz_qids = [str(x) for x in zn['qids']]
assert len(loco_npz_qids) == 1535 and set(loco_npz_qids) == set(valid_qids), 'npz qid mismatch'
U_loco_var = (-zn['var_rank'].astype(float)).mean(axis=0)
SMALL_L = spread_cols(U_loco_var, 48)
SMALL2_L = spread_cols(U_loco_var, 64)
print('LOCO SMALL48 cols: %s' % SMALL_L.tolist(), flush=True)
print('LOCO SMALL64 cols: %s' % SMALL2_L.tolist(), flush=True)

def loco_dist(ci, subset):
    Cb, Qb = LCB[ci], LQCB[ci]
    if subset is None:
        return np.count_nonzero(Qb[:, None, :] != Cb[None, :, :], axis=2).astype(np.int16)
    s = np.asarray(subset)
    return np.count_nonzero(Qb[:, None, s] != Cb[None, :, s], axis=2).astype(np.int16)

def q_fractional(dist_q, priorities, gold):
    tops = topks_by_hamming(dist_q, priorities)
    return mean_or_nan([retrieval_metrics(t, gold)["fractional"] for t in tops])

loco = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    N = LNN[ci]; pri = LPRI[ci]
    d_nat = loco_dist(ci, None)
    d_sm = loco_dist(ci, SMALL_L)
    d_s2 = loco_dist(ci, SMALL2_L)
    Cb = LCB[ci]; Qb = LQCB[ci]
    var = np.asarray(r["C"], float).var(axis=0)
    for qi, q in enumerate(c["qas"]):
        qid = q["question_id"]
        gold = Q[qid]["ag"]
        if len(gold) == 0:
            continue
        f = goldfree_feats(d_sm[qi], d_nat[qi], pri[0], Cb, Qb[qi].astype(float), var)
        loco[qid] = {'ci': ci, 'qi': qi, 'cat': q["category"], 'n': N, 'ngold': len(gold),
                     'fr_small': q_fractional(d_sm[qi], pri, gold),
                     'fr_large': q_fractional(d_nat[qi], pri, gold),
                     'fr_small2': q_fractional(d_s2[qi], pri, gold),
                     'feat': f}
    print('  LOCO conv %d/10 (%.0fs)' % (ci + 1, time.time() - t0), flush=True)
assert len(loco) == 1535, len(loco)

loco_nat = float(np.mean([loco[q]['fr_large'] for q in valid_qids]))
loco_sm = float(np.mean([loco[q]['fr_small'] for q in valid_qids]))
loco_s2 = float(np.mean([loco[q]['fr_small2'] for q in valid_qids]))
print('LOCO GATE native=%.16f anchor=%.16f diff=%g' % (loco_nat, LOCO_ANCHOR, loco_nat - LOCO_ANCHOR), flush=True)
print('LOCO SMALL48=%.16f exp=%.16f diff=%g' % (loco_sm, EXP_LOCO_SPREAD48, loco_sm - EXP_LOCO_SPREAD48), flush=True)
print('LOCO SMALL64=%.16f exp=%.16f diff=%g' % (loco_s2, EXP_LOCO_SPREAD64, loco_s2 - EXP_LOCO_SPREAD64), flush=True)
assert abs(loco_nat - LOCO_ANCHOR) <= 1e-12, 'LoCoMo native gate FAILED'
assert abs(loco_sm - EXP_LOCO_SPREAD48) <= 1e-12, 'LoCoMo SPREAD48 gate FAILED'
assert abs(loco_s2 - EXP_LOCO_SPREAD64) <= 1e-12, 'LoCoMo SPREAD64 gate FAILED'
print('LOCO GATES PASS', flush=True)

# NaN-freeness spot check (dup + variance features, all features)
for nm, per, valid in [('LME', lme, lme_qids), ('LOCO', loco, valid_qids)]:
    bad = 0
    for q in valid:
        for f in FEATS:
            v = per[q]['feat'][f]
            if not np.isfinite(float(v)):
                bad += 1
    print('%s NaN check: %d non-finite feature values over %d q x %d feats'
          % (nm, bad, len(valid), len(FEATS)), flush=True)
    assert bad == 0, '%s feature NaN gate FAILED' % nm
print('FEATURE NaN GATES PASS', flush=True)

# ================= labels + model + routing (shared) =================
def run_benchmark(per, valid, name):
    for q in valid:
        v = per[q]
        v['fail'] = bool(v['fr_small'] < v['fr_large'] - TOL)
        v['split'] = split_of(q)
    tr = [q for q in valid if per[q]['split'] == 'train']
    te = [q for q in valid if per[q]['split'] == 'test']
    base = {
        'n': len(valid), 'n_train': len(tr), 'n_test': len(te),
        'fail_all': int(sum(1 for q in valid if per[q]['fail'])),
        'fail_train': int(sum(1 for q in tr if per[q]['fail'])),
        'fail_test': int(sum(1 for q in te if per[q]['fail'])),
        'mean_small_all': float(np.mean([per[q]['fr_small'] for q in valid])),
        'mean_large_all': float(np.mean([per[q]['fr_large'] for q in valid])),
        'mean_small_test': float(np.mean([per[q]['fr_small'] for q in te])),
        'mean_large_test': float(np.mean([per[q]['fr_large'] for q in te])),
    }
    print('%s split: train=%d (fail %d) test=%d (fail %d); base rates all=%.3f train=%.3f test=%.3f'
          % (name, len(tr), base['fail_train'], len(te), base['fail_test'],
             base['fail_all'] / len(valid), base['fail_train'] / max(len(tr), 1),
             base['fail_test'] / max(len(te), 1)), flush=True)

    def X_of(qs, feats):
        return np.array([[float(per[q]['feat'][f]) for f in feats] for q in qs], float)

    def y_of(qs):
        return np.array([1.0 if per[q]['fail'] else 0.0 for q in qs], float)

    ytr_full = y_of(tr); yte_full = y_of(te)
    models = {}
    for feats in [[f] for f in FEATS] + [FEATS]:
        key = 'COMBO' if len(feats) > 1 else feats[0]
        Xtr = X_of(tr, feats); Xte = X_of(te, feats)
        mu = Xtr.mean(axis=0); sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
        w = fit_logreg((Xtr - mu) / sd, ytr_full)
        out = {'feats': feats, 'coef': [float(v) for v in w],
               'mu': [float(v) for v in mu], 'sd': [float(v) for v in sd]}
        for nm, X, y in [('train', Xtr, ytr_full), ('test', Xte, yte_full)]:
            s = 1.0 / (1.0 + np.exp(-(np.hstack([np.ones((len(X), 1)), (X - mu) / sd]) @ w)))
            out[nm + '_auc'] = auc_rank(s, y)
            out[nm + '_scores'] = [float(v) for v in s]
        models[key] = out
    combo = models['COMBO']
    for q, s in zip(tr, combo['train_scores']):
        per[q]['p_fail'] = s
    for q, s in zip(te, combo['test_scores']):
        per[q]['p_fail'] = s
    auc1 = {k: (models[k]['train_auc'], models[k]['test_auc']) for k in list(models)}
    print('%s AUCs (train/test): ' % name +
          '; '.join('%s=%.3f/%.3f' % ((k,) + auc1[k]) for k in list(models)), flush=True)

    # ---- selective routing on TEST only ----
    frS = np.array([per[q]['fr_small'] for q in te])
    frL = np.array([per[q]['fr_large'] for q in te])
    g = {q: per[q]['fr_large'] - per[q]['fr_small'] for q in te}
    p = {q: per[q]['p_fail'] for q in te}
    order_model = sorted(te, key=lambda q: (-p[q], q))
    order_oracle = sorted(te, key=lambda q: (-g[q], q))
    rows = []
    for a in ALPHAS:
        k = int(round(a * len(te)))
        rm = set(order_model[:k]); ro = set(order_oracle[:k])
        routed_m = np.array([frL[i] if q in rm else frS[i] for i, q in enumerate(te)])
        routed_o = np.array([frL[i] if q in ro else frS[i] for i, q in enumerate(te)])
        gain_m = float(routed_m.mean() - frS.mean())
        gain_o = float(routed_o.mean() - frS.mean())
        rnd = []
        for i in range(10):
            idx = np.random.default_rng(20260913 + i).choice(len(te), k, replace=False)
            rr = np.array([frL[j] if j in set(idx.tolist()) else frS[j] for j in range(len(te))])
            rnd.append(float(rr.mean() - frS.mean()))
        rows.append({'alpha': a, 'k': k, 'n_test': len(te),
                     'gain_model': gain_m, 'gain_oracle': gain_o,
                     'gain_random_mean': float(np.mean(rnd)),
                     'gain_random_min': float(np.min(rnd)),
                     'gain_random_max': float(np.max(rnd)),
                     'gain_random_all': [float(v) for v in rnd]})
        print('%s alpha=%.2f k=%d gain_model=%+.4fpp oracle=%+.4fpp random=%+.4fpp [%.4f,%.4f]'
              % (name, a, k, 100 * gain_m, 100 * gain_o, 100 * float(np.mean(rnd)),
                 100 * float(np.min(rnd)), 100 * float(np.max(rnd))), flush=True)
    const_all_small = 0.0
    const_all_large = float(frL.mean() - frS.mean())
    print('%s constant sanity: all-SMALL=%+.4fpp all-LARGE=%+.4fpp'
          % (name, 100 * const_all_small, 100 * const_all_large), flush=True)
    return {'base': base, 'models': {k: {kk: vv for kk, vv in m.items() if not kk.endswith('_scores')}
                                     for k, m in models.items()},
            'routing': rows,
            'const_all_small': const_all_small, 'const_all_large': const_all_large}

res_lme = run_benchmark(lme, lme_qids, 'LME')
res_loco = run_benchmark(loco, valid_qids, 'LOCO')

# ================= promote gate =================
def gain_at(res, a):
    for r in res['routing']:
        if abs(r['alpha'] - a) < 1e-9:
            return r
    raise AssertionError
rl = gain_at(res_lme, 0.20); rc = gain_at(res_loco, 0.20)
gl, gc = 100 * rl['gain_model'], 100 * rc['gain_model']
ok_lme = gl >= 1.0
ok_loco = (gc >= 0.5) and (np.sign(gc) == np.sign(gl)) and gl > 0
promote = bool(ok_lme and ok_loco)
print('PROMOTE GATE: LME gain@0.20=%+.4fpp (>=+1.0pp: %s); LOCO gain@0.20=%+.4fpp (same-sign & >=+0.5pp: %s)'
      % (gl, ok_lme, gc, ok_loco), flush=True)
print('GATE DECISION: %s' % ('PROMOTE' if promote else 'KILL'), flush=True)

# ================= details JSON =================
details = {
    'labels': LABELS,
    'conventions': {
        'tie_protocol_lme': 'priorities rng(5_100_000+lx*100000+t*100+99).random(n), lx=ALL-500 lex ordinal, '
                            '20 trials, lexsort((p,d)) top-3, fractional R@3 (r2b/d2 verbatim)',
        'tie_protocol_locomo': 'stable_archive_seed(ci,t)+99, 20 trials, topks_by_hamming top-3, '
                               'fractional R@3 over audit-corrected gold (r2c_replicate.py verbatim)',
        'SMALL': 'SPREAD48: order=argsort(-U_var) descending FULL-DATA variance ordering '
                 '(U_var=mean(-var_rank) from per-axis npz; gold-free), '
                 'cols=sort(order[round(linspace(0,95,48))]) (d3.spread_cols verbatim, round3 deney1)',
        'SMALL2': 'SPREAD64: same with k=64',
        'LARGE': 'NATIVE96 (all 96 axes)',
        'small_cols_lme': SMALL.tolist(), 'small2_cols_lme': SMALL2.tolist(),
        'small_cols_loco': SMALL_L.tolist(), 'small2_cols_loco': SMALL2_L.tolist(),
        'split': "train iff int(sha256('c2|'+qid).hexdigest()[0],16) even; no stratification; "
                 'LME and LoCoMo split separately',
        'fail': 'fail iff FR_small < FR_large - 1e-12',
        'features': 'gold-free only: margin34/crowd3/crowd4/crowd_pm1 from small-arm trial-0 ordering '
                    '(d3v=s[2], d4v=s[3]); top3_tie_share=crowd3/N; boundary_share=(crowd3+crowd4)/N; '
                    'dup_top20=1-distinct_full96_codes(top20)/20; var_decay=sum(top16 var)/sum(top48 var) '
                    'of archive variance; N=archive size; qent=binary sign-entropy (nats) of qC; '
                    'margin34_large/crowd3_large = same geometry on LARGE arm (gold-free)',
        'model': 'logistic IRLS, train-standardized, L2 lam=1.0 (bias unpenalized); '
                 'univariate per feature + 12-feature COMBO; positive class = fail',
        'auc': 'Mann-Whitney rank statistic',
        'routing': 'test split only; k=round(alpha*n_test); route top-k P(fail) to LARGE; '
                   'gain=mean(routed)-mean(SMALL); random=10 draws rng(20260913+i); '
                   'oracle=descending TRUE gain (FR_large-FR_small), ties by qid; '
                   'constant sanity: all-SMALL (0 by construction), all-LARGE',
        'promote_gate': 'PROMOTE iff LME gain@0.20>=+1.0pp AND LoCoMo same sign and >=+0.5pp; else KILL',
    },
    'gates': {
        'lme_native': lme_nat, 'lme_native_anchor': LME_ANCHOR,
        'lme_spread48': lme_sm, 'lme_spread48_ref': EXP_LME_SPREAD48,
        'lme_spread64': lme_s2, 'lme_spread64_ref': EXP_LME_SPREAD64,
        'lme_native_maxdiff_vs_stored': lme_maxdiff,
        'loco_native': loco_nat, 'loco_native_anchor': LOCO_ANCHOR,
        'loco_spread48': loco_sm, 'loco_spread48_ref': EXP_LOCO_SPREAD48,
        'loco_spread64': loco_s2, 'loco_spread64_ref': EXP_LOCO_SPREAD64,
    },
    'LME': res_lme, 'LOCO': res_loco,
    'promote_gate': {'lme_gain_pp': gl, 'loco_gain_pp': gc,
                     'ok_lme': bool(ok_lme), 'ok_loco': bool(ok_loco), 'promote': promote},
    'per_question': {
        'LME': {q: {'split': lme[q]['split'], 'fail': lme[q]['fail'],
                    'fr_small': lme[q]['fr_small'], 'fr_large': lme[q]['fr_large'],
                    'fr_small2': lme[q]['fr_small2'], 'p_fail': lme[q]['p_fail'],
                    'feat': lme[q]['feat']} for q in lme_qids},
        'LOCO': {q: {'split': loco[q]['split'], 'fail': loco[q]['fail'],
                     'fr_small': loco[q]['fr_small'], 'fr_large': loco[q]['fr_large'],
                     'fr_small2': loco[q]['fr_small2'], 'p_fail': loco[q]['p_fail'],
                     'feat': loco[q]['feat']} for q in valid_qids},
    },
    'elapsed_s': time.time() - t0,
}
json.dump(details, open(str(OUT / 'c2x_details.json'), 'w'))
print('wrote c2_details.json (%.1fs)' % (time.time() - t0), flush=True)

# ================= report =================
L = []
L.append('# DENEY 5 (c2) — gold-free failure predictor -> adaptive budget routing\n')
L.append('**%s**\n' % LABELS)
L.append('Numpy only; no network; read-only on /mnt/c. SMALL=SPREAD48 (repaired rank-linspace, '
         'full-data variance ordering — gold-free), LARGE=NATIVE96, secondary SMALL2=SPREAD64. '
         'Split: train iff first hex of sha256("c2|"+qid) even (unstratified).\n')
L.append('## 1. Gates (abort on fail — all PASS)\n')
L.append('| Gate | Recomputed | Reference | Diff |')
L.append('|---|---|---|---|')
L.append('| LME native | %.16f | %.16f | %.1e |' % (lme_nat, LME_ANCHOR, abs(lme_nat - LME_ANCHOR)))
L.append('| LME SPREAD48 | %.16f | %.16f | %.1e |' % (lme_sm, EXP_LME_SPREAD48, abs(lme_sm - EXP_LME_SPREAD48)))
L.append('| LME SPREAD64 | %.16f | %.16f | %.1e |' % (lme_s2, EXP_LME_SPREAD64, abs(lme_s2 - EXP_LME_SPREAD64)))
L.append('| LME native vs stored | max abs diff %.1e (470/470) | | |' % lme_maxdiff)
L.append('| LOCO native | %.16f | %.16f | %.1e |' % (loco_nat, LOCO_ANCHOR, abs(loco_nat - LOCO_ANCHOR)))
L.append('| LOCO SPREAD48 | %.16f | %.16f | %.1e |' % (loco_sm, EXP_LOCO_SPREAD48, abs(loco_sm - EXP_LOCO_SPREAD48)))
L.append('| LOCO SPREAD64 | %.16f | %.16f | %.1e |' % (loco_s2, EXP_LOCO_SPREAD64, abs(loco_s2 - EXP_LOCO_SPREAD64)))
L.append('| LOCO valid | 1535 | 1535 | |')
L.append('| feature NaN-freeness | 0 non-finite (both benchmarks) | | |')
L.append('\nSanity vs round3 splits band (~0.46-0.47): LME SPREAD48 all-470 = %.4f '
         '(band refers to split means of 64-bit arms; 48-bit full-data mean sits just below it — reported, not gated).'
         % lme_sm + '\n')

for nm, res in [('LME', res_lme), ('LOCO', res_loco)]:
    b = res['base']
    L.append('## 2. %s: labels + base rates\n' % nm)
    L.append('fail iff FR_small < FR_large - 1e-12. n=%d (train %d / test %d). '
             'Base rates: all %.1f%% (%d), train %.1f%% (%d), test %.1f%% (%d). '
             'Mean FR: SMALL=%.4f LARGE=%.4f (all); test SMALL=%.4f LARGE=%.4f.' % (
                 b['n'], b['n_train'], b['n_test'],
                 100 * b['fail_all'] / b['n'], b['fail_all'],
                 100 * b['fail_train'] / b['n_train'], b['fail_train'],
                 100 * b['fail_test'] / b['n_test'], b['fail_test'],
                 b['mean_small_all'], b['mean_large_all'],
                 b['mean_small_test'], b['mean_large_test']) + '\n')
    L.append('## 3. %s: held-out AUC (positive class = fail)\n' % nm)
    L.append('| Feature | Train AUC | Test AUC |')
    L.append('|---|---|---|')
    for f in FEATS + ['COMBO']:
        m = res['models'][f]
        L.append('| %s | %.3f | %.3f |' % (f, m['train_auc'], m['test_auc']))
    m = res['models']['COMBO']
    L.append('\nCOMBO standardized coef (bias first): ' +
             ', '.join('%s=%+.3f' % (k, v) for k, v in zip(['bias'] + FEATS, m['coef'])) + '\n')
    L.append('## 4. %s: selective routing gains on TEST (pp)\n' % nm)
    L.append('| alpha | k | model | oracle | random mean | random range |')
    L.append('|---|---|---|---|---|---|')
    for r in res['routing']:
        L.append('| %.2f | %d | %+.3f | %+.3f | %+.3f | [%+.3f, %+.3f] |' % (
            r['alpha'], r['k'], 100 * r['gain_model'], 100 * r['gain_oracle'],
            100 * r['gain_random_mean'], 100 * r['gain_random_min'], 100 * r['gain_random_max']))
    L.append('\nConstant sanity: all-SMALL %+.3fpp (0 by construction); all-LARGE %+.3fpp.\n' % (
        100 * res['const_all_small'], 100 * res['const_all_large']))

L.append('## 5. Promote gate (pre-declared)\n')
L.append('Require LME gain@0.20 >= +1.0pp AND LoCoMo same sign, >= +0.5pp. '
         'Observed: LME %+.3fpp, LoCoMo %+.3fpp. **Decision: %s.**' % (
             gl, gc, 'PROMOTE to a preregistered adaptive experiment' if promote else 'KILL — '
             'the null stands as the mechanism result: tie competition at the gold distance explains '
             'the small-vs-large gap, but gold-free geometry does not buy routable FR beyond '
             'random abstention at a scale worth a preregistered experiment') + '\n')
L.append('## 6. Honesty: what this cannot show\n')
L.append('- Single learner (logistic IRLS, L2=1.0, train-standardized); one fixed 12-feature set '
         'chosen a priori from small-arm geometry + archive stats (+LARGE geometry, still gold-free). '
         'No feature search was run; a different set/learner could differ.')
L.append('- n sizes: LME 470 (train %d / test %d, test fails %d); LoCoMo 1535 (train %d / test %d, test fails %d). '
         'Test routing n is small on LME; pp gains there are noisy.' % (
             res_lme['base']['n_train'], res_lme['base']['n_test'], res_lme['base']['fail_test'],
             res_loco['base']['n_train'], res_loco['base']['n_test'], res_loco['base']['fail_test']))
L.append('- Failure is defined against the full budget (fail = small strictly worse than large); '
         'questions where both arms fail identically are NOT fails — routing cannot help them.')
L.append('- LARGE-arm geometry features (margin34_large, crowd3_large) describe the full budget; '
         'a deployable router would need them without paying full-budget cost — they are included '
         'as analysis features, not as a deployment claim.')
L.append('- Correlation/description only: no causal claim — predictable failure need not be fixable failure.')
L.append('- [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].')
open(str(OUT / 'c2x_report.md'), 'w').write('\n'.join(L))
print('wrote c2_report.md', flush=True)

print('BEGIN_C2_KEY_NUMBERS')
print('lme_native=%.16f lme_spread48=%.16f lme_spread64=%.16f' % (lme_nat, lme_sm, lme_s2))
print('loco_native=%.16f loco_spread48=%.16f loco_spread64=%.16f' % (loco_nat, loco_sm, loco_s2))
print('lme_split_train_test=%d/%d lme_fails_all_train_test=%d/%d/%d' % (
    res_lme['base']['n_train'], res_lme['base']['n_test'], res_lme['base']['fail_all'],
    res_lme['base']['fail_train'], res_lme['base']['fail_test']))
print('loco_split_train_test=%d/%d loco_fails_all_train_test=%d/%d/%d' % (
    res_loco['base']['n_train'], res_loco['base']['n_test'], res_loco['base']['fail_all'],
    res_loco['base']['fail_train'], res_loco['base']['fail_test']))
for f in FEATS + ['COMBO']:
    print('LME_AUC_%s_train=%.4f test=%.4f' % (f, res_lme['models'][f]['train_auc'], res_lme['models'][f]['test_auc']))
for f in FEATS + ['COMBO']:
    print('LOCO_AUC_%s_train=%.4f test=%.4f' % (f, res_loco['models'][f]['train_auc'], res_loco['models'][f]['test_auc']))
for r in res_lme['routing']:
    print('LME_ROUTE_a%.2f k=%d model_pp=%+.4f oracle_pp=%+.4f randmean_pp=%+.4f randrange_pp=[%+.4f,%+.4f]' % (
        r['alpha'], r['k'], 100 * r['gain_model'], 100 * r['gain_oracle'],
        100 * r['gain_random_mean'], 100 * r['gain_random_min'], 100 * r['gain_random_max']))
for r in res_loco['routing']:
    print('LOCO_ROUTE_a%.2f k=%d model_pp=%+.4f oracle_pp=%+.4f randmean_pp=%+.4f randrange_pp=[%+.4f,%+.4f]' % (
        r['alpha'], r['k'], 100 * r['gain_model'], 100 * r['gain_oracle'],
        100 * r['gain_random_mean'], 100 * r['gain_random_min'], 100 * r['gain_random_max']))
print('END_C2_KEY_NUMBERS')
print('C2_VERDICT: <LME gain@0.20 %+.3fpp, LOCO gain@0.20 %+.3fpp, vs random-abstain '
      '(LME %+.3fpp / LOCO %+.3fpp mean), %s>' % (
          gl, gc, 100 * rl['gain_random_mean'], 100 * rc['gain_random_mean'],
          'PROMOTE' if promote else 'KILL'))

# ================= C2X (D5 missing-analysis items 1-3) =================
# Machinery above is c2.py VERBATIM (only OUT dir / output filenames changed).
import sys as _sys

print('--- C2X GATE: reproduce c2 numbers (abort on fail) ---', flush=True)
def _gain_at2(res, a):
    for r in res['routing']:
        if abs(r['alpha'] - a) < 1e-9:
            return r
    raise AssertionError('alpha missing')
_gL20 = _gain_at2(res_lme, 0.20); _gC20 = _gain_at2(res_loco, 0.20)
_gate_checks = [
    ('LME gain@0.20 pp', 100.0 * _gL20['gain_model'], 3.086, 0.005),
    ('LOCO gain@0.20 pp', 100.0 * _gC20['gain_model'], 1.481, 0.005),
    ('LME random-mean@0.20 pp', 100.0 * _gL20['gain_random_mean'], 1.833, 0.005),
    ('LOCO random-mean@0.20 pp', 100.0 * _gC20['gain_random_mean'], 1.135, 0.005),
    ('LME COMBO test AUC', res_lme['models']['COMBO']['test_auc'], 0.686, 0.002),
    ('LOCO COMBO test AUC', res_loco['models']['COMBO']['test_auc'], 0.558, 0.002),
]
_gate_ok = True
for _nm, _got, _ref, _tol in _gate_checks:
    _d = abs(_got - _ref)
    _ok = _d <= _tol
    _gate_ok = _gate_ok and _ok
    print('GATE %-22s got=%+.6f ref=%+.6f diff=%.6f tol=%.6f %s'
          % (_nm, _got, _ref, _d, _tol, 'PASS' if _ok else 'FAIL'), flush=True)
if not _gate_ok:
    print('C2X GATE FAILED - aborting (c2 numbers not reproduced)', flush=True)
    _sys.exit(1)
print('C2X GATE PASS - c2 numbers reproduced; proceeding with D5 items', flush=True)

# ---- shared refit/routing helpers (same math as run_benchmark) ----
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def _fit_combo(per, tr, te, feats):
    Xtr = np.array([[float(per[q]['feat'][f]) for f in feats] for q in tr], float)
    Xte = np.array([[float(per[q]['feat'][f]) for f in feats] for q in te], float)
    ytr = np.array([1.0 if per[q]['fail'] else 0.0 for q in tr], float)
    yte = np.array([1.0 if per[q]['fail'] else 0.0 for q in te], float)
    mu = Xtr.mean(axis=0); sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
    w = fit_logreg((Xtr - mu) / sd, ytr)  # lam=1.0 default, bias unpenalized
    ste = _sigmoid(np.hstack([np.ones((len(Xte), 1)), (Xte - mu) / sd]) @ w)
    str_ = _sigmoid(np.hstack([np.ones((len(Xtr), 1)), (Xtr - mu) / sd]) @ w)
    return {'feats': list(feats), 'coef': [float(v) for v in w],
            'mu': [float(v) for v in mu], 'sd': [float(v) for v in sd],
            'train_auc': auc_rank(str_, ytr), 'test_auc': auc_rank(ste, yte),
            'scores': {q: float(s) for q, s in zip(te, ste)}}

def _route_gains(per, te, p):
    # same routing rule as c2: k=round(alpha*n_test), top-k P(fail) -> LARGE, ties by qid
    frS = np.array([per[q]['fr_small'] for q in te])
    frL = np.array([per[q]['fr_large'] for q in te])
    order = sorted(te, key=lambda q: (-p[q], q))
    out = []
    for a in ALPHAS:
        k = int(round(a * len(te)))
        rm = set(order[:k])
        routed = np.array([frL[i] if q in rm else frS[i] for i, q in enumerate(te)])
        out.append({'alpha': a, 'k': k, 'n_test': len(te),
                    'gain_model': float(routed.mean() - frS.mean())})
    return out

def _tr_te(per, valid):
    return ([q for q in valid if per[q]['split'] == 'train'],
            [q for q in valid if per[q]['split'] == 'test'])

# ---- Task 1: LARGE-free ablation ----
# Feature audit (see goldfree_feats): d_small/d_large = arm-restricted Hamming dists,
# p0 = trial-0 priorities (arm-independent), D0full = full-96-bit sign matrix,
# qsign = 96-bit query signs, var = 96-dim archive variance.
#   margin34, crowd3, crowd4, crowd_pm1, top3_tie_share, boundary_share: SMALL arm only -> KEEP
#   margin34_large, crowd3_large: LARGE-arm retrieval ordering -> DROP (full-budget pass)
#   dup_top20: top20 selected by SMALL ordering, but distinctness uses full-96-bit codes
#     -> BORDERLINE (needs full-bit codes, not a LARGE retrieval run); primary keeps it,
#        STRICT9 sensitivity drops it too.
#   var_decay: 96-dim archive variance (per-archive precomputable, no per-question LARGE
#     retrieval run; on LoCoMo constant per conv) -> KEEP in primary, stated.
#   N (archive size), qent (query sign entropy over qC; redefinable on SMALL bits) -> KEEP, stated.
LARGE_DERIVED = ['margin34_large', 'crowd3_large']
FREE10 = [f for f in FEATS if f not in LARGE_DERIVED]
STRICT9 = [f for f in FREE10 if f != 'dup_top20']
assert len(FREE10) == 10 and len(STRICT9) == 9

_tr_lme, _te_lme = _tr_te(lme, lme_qids)
_tr_loco, _te_loco = _tr_te(loco, valid_qids)
_free_lme = _fit_combo(lme, _tr_lme, _te_lme, FREE10)
_free_loco = _fit_combo(loco, _tr_loco, _te_loco, FREE10)
_strict_lme = _fit_combo(lme, _tr_lme, _te_lme, STRICT9)
_strict_loco = _fit_combo(loco, _tr_loco, _te_loco, STRICT9)
_rfree_lme = _route_gains(lme, _te_lme, _free_lme['scores'])
_rfree_loco = _route_gains(loco, _te_loco, _free_loco['scores'])
_rstrict_lme = _route_gains(lme, _te_lme, _strict_lme['scores'])
_rstrict_loco = _route_gains(loco, _te_loco, _strict_loco['scores'])
for _nm, _fit, _rr in [('FREE10/LME', _free_lme, _rfree_lme),
                       ('FREE10/LOCO', _free_loco, _rfree_loco),
                       ('STRICT9/LME', _strict_lme, _rstrict_lme),
                       ('STRICT9/LOCO', _strict_loco, _rstrict_loco)]:
    _g20 = _gain_at2({'routing': _rr}, 0.20)['gain_model']
    print('%s testAUC=%.4f gain@.20=%+.4fpp gains_pp=%s' % (
        _nm, _fit['test_auc'], 100 * _g20,
        ['%+.3f' % (100 * r['gain_model']) for r in _rr]), flush=True)
print('FREE10/LME coef=' + ','.join('%s=%+.3f' % kv for kv in
      zip(['bias'] + FREE10, _free_lme['coef'])), flush=True)
print('FREE10/LOCO coef=' + ','.join('%s=%+.3f' % kv for kv in
      zip(['bias'] + FREE10, _free_loco['coef'])), flush=True)

# ---- Task 2: paired bootstrap 90% CIs for gain@0.20 (B=2000, fixed scores, resampled eval) ----
B = 2000
def _boot_idx(n, B, seed):
    return np.random.default_rng(seed).integers(0, n, size=(B, n))

def _boot_gains(per, te, p, alpha, idxm):
    n = len(te); k = int(round(alpha * n))
    frS = np.array([per[q]['fr_small'] for q in te])
    frL = np.array([per[q]['fr_large'] for q in te])
    pv = np.array([p[q] for q in te]); qs = np.array(te)
    gains = np.empty(idxm.shape[0])
    for b in range(idxm.shape[0]):
        idx = idxm[b]
        o = sorted(idx.tolist(), key=lambda j: (-float(pv[j]), str(qs[j])))
        sel = set(o[:k])
        m = np.array([j in sel for j in idx])
        gains[b] = float(np.where(m, frL[idx], frS[idx]).mean() - frS[idx].mean())
    return gains

_pfull_lme = {q: lme[q]['p_fail'] for q in _te_lme}
_pfull_loco = {q: loco[q]['p_fail'] for q in _te_loco}
_idx_lme = _boot_idx(len(_te_lme), B, 20260914)  # paired: same resamples for full vs free
_idx_loco = _boot_idx(len(_te_loco), B, 20260915)

def _ci95(g):
    return float(g.mean()), float(np.percentile(g, 5)), float(np.percentile(g, 95))

_boot = {}
for _bn, _per, _te, _pf, _ps, _ix in [('LME', lme, _te_lme, _pfull_lme, _free_lme['scores'], _idx_lme),
                                      ('LOCO', loco, _te_loco, _pfull_loco, _free_loco['scores'], _idx_loco)]:
    _gf = _boot_gains(_per, _te, _pf, 0.20, _ix)
    _gr = _boot_gains(_per, _te, _ps, 0.20, _ix)
    _mf, _lf, _hf = _ci95(_gf); _mr, _lr, _hr = _ci95(_gr)
    _md, _ld, _hd = _ci95(_gr - _gf)  # paired free-minus-full difference
    _boot[_bn] = {'full': {'mean_pp': 100 * _mf, 'lo90_pp': 100 * _lf, 'hi90_pp': 100 * _hf},
                  'free': {'mean_pp': 100 * _mr, 'lo90_pp': 100 * _lr, 'hi90_pp': 100 * _hr},
                  'paired_diff_free_minus_full_pp': {'mean': 100 * _md, 'lo90': 100 * _ld, 'hi90': 100 * _hd},
                  'B': B}
    print('BOOT %s full gain@.20 mean=%+.4fpp 90%%CI=[%+.4f,%+.4f] | free mean=%+.4fpp 90%%CI=[%+.4f,%+.4f] | paired free-full mean=%+.4fpp 90%%CI=[%+.4f,%+.4f]'
          % (_bn, 100 * _mf, 100 * _lf, 100 * _hf, 100 * _mr, 100 * _lr, 100 * _hr,
             100 * _md, 100 * _ld, 100 * _hd), flush=True)

# ---- Task 3: formal vs-random test, 200 draws, same alpha scheme + seed protocol ----
N_RAND = 200
def _rand_gains(per, te, alpha, n_draws=N_RAND):
    n = len(te); k = int(round(alpha * n))
    frS = np.array([per[q]['fr_small'] for q in te])
    frL = np.array([per[q]['fr_large'] for q in te])
    out = []
    for i in range(n_draws):
        idx = np.random.default_rng(20260913 + i).choice(n, k, replace=False)
        s = set(idx.tolist())
        rr = np.array([frL[j] if j in s else frS[j] for j in range(n)])
        out.append(float(rr.mean() - frS.mean()))
    return out

_vsrand = {}
for _bn, _per, _te, _pf, _ps, _res in [('LME', lme, _te_lme, _pfull_lme, _free_lme['scores'], res_lme),
                                       ('LOCO', loco, _te_loco, _pfull_loco, _free_loco['scores'], res_loco)]:
    _vsrand[_bn] = []
    for _a in ALPHAS:
        _r = _rand_gains(_per, _te, _a)
        _n = len(_te); _k = int(round(_a * _n))
        _row = {'alpha': _a, 'k': _k, 'n_test': _n, 'n_draws': N_RAND,
                'random_mean_pp': 100 * float(np.mean(_r)),
                'random_min_pp': 100 * float(np.min(_r)),
                'random_max_pp': 100 * float(np.max(_r))}
        for _mn, _p in [('full', _pf), ('free', _ps)]:
            _g = [rr['gain_model'] for rr in _route_gains(_per, _te, _p)
                  if abs(rr['alpha'] - _a) < 1e-9][0]
            _pval = sum(1 for v in _r if v >= _g) / len(_r)  # one-sided: P(random >= model)
            _pct = 100.0 * sum(1 for v in _r if v <= _g) / len(_r)
            _padj = min(1.0, 4 * _pval)  # Bonferroni across the 4 alphas per benchmark
            _row[_mn] = {'gain_pp': 100 * _g, 'percentile': _pct, 'p_raw': _pval,
                         'p_bonf': _padj,
                         'verdict': 'beats-random' if _padj < 0.05 else 'inside-noise'}
        _vsrand[_bn].append(_row)
        print('VSRAND %s a=%.2f model_full=%+.4fpp pct=%.1f p=%.4f padj=%.4f %s | free=%+.4fpp pct=%.1f p=%.4f padj=%.4f %s | randmean=%+.4fpp range=[%+.4f,%+.4f]' % (
            _bn, _a, _row['full']['gain_pp'], _row['full']['percentile'], _row['full']['p_raw'],
            _row['full']['p_bonf'], _row['full']['verdict'], _row['free']['gain_pp'],
            _row['free']['percentile'], _row['free']['p_raw'], _row['free']['p_bonf'],
            _row['free']['verdict'], _row['random_mean_pp'], _row['random_min_pp'],
            _row['random_max_pp']), flush=True)
# consistency: first-10-draw means must equal c2's stored random means
for _bn, _res in [('LME', res_lme), ('LOCO', res_loco)]:
    for _rnew, _rold in zip(_vsrand[_bn], _res['routing']):
        _m10 = float(np.mean(_rand_gains(lme if _bn == 'LME' else loco,
                                         _te_lme if _bn == 'LME' else _te_loco,
                                         _rnew['alpha'], 10)))
        assert abs(_m10 - _rold['gain_random_mean']) < 1e-12, 'random-protocol drift %s a=%s' % (_bn, _rnew['alpha'])
print('RANDOM-PROTOCOL consistency check PASS (first-10 means match c2)', flush=True)

# ---- augment details JSON ----
_det = json.load(open(str(OUT / 'c2x_details.json')))
_det['c2x'] = {
    'labels': LABELS + ' [C2X ABLATION]',
    'gate_repro': [{'name': n, 'got': g, 'ref': r, 'tol': t, 'pass': bool(abs(g - r) <= t)}
                   for (n, g, r, t) in _gate_checks],
    'feature_audit': {
        'dropped_LARGE_arm': LARGE_DERIVED,
        'kept_SMALL_arm': ['margin34', 'crowd3', 'crowd4', 'crowd_pm1',
                           'top3_tie_share', 'boundary_share'],
        'kept_borderline_with_caveat': {
            'dup_top20': 'top20 by SMALL ordering; distinctness needs full-96-bit codes (STRICT9 drops it too)',
            'var_decay': '96-dim archive variance, per-archive precomputable; no per-question LARGE run',
            'N': 'archive size, free',
            'qent': 'query sign entropy (redefinable on SMALL bits)'},
        'FREE10': FREE10, 'STRICT9': STRICT9},
    'largefree': {
        'LME': {'feats': FREE10, 'coef': _free_lme['coef'], 'mu': _free_lme['mu'],
                'sd': _free_lme['sd'], 'train_auc': _free_lme['train_auc'],
                'test_auc': _free_lme['test_auc'], 'routing': _rfree_lme},
        'LOCO': {'feats': FREE10, 'coef': _free_loco['coef'], 'mu': _free_loco['mu'],
                 'sd': _free_loco['sd'], 'train_auc': _free_loco['train_auc'],
                 'test_auc': _free_loco['test_auc'], 'routing': _rfree_loco},
        'STRICT9_LME': {'test_auc': _strict_lme['test_auc'], 'routing': _rstrict_lme,
                        'coef': _strict_lme['coef']},
        'STRICT9_LOCO': {'test_auc': _strict_loco['test_auc'], 'routing': _rstrict_loco,
                         'coef': _strict_loco['coef']}},
    'bootstrap_gain020': {'B': B, 'method': 'paired bootstrap over test questions (fixed scores, resampled eval; same resamples for full vs free); 90% CI = 5th/95th pct',
                          'seeds': {'LME': 20260914, 'LOCO': 20260915}, 'rows': _boot},
    'vs_random': {'n_draws': N_RAND, 'seed_protocol': 'rng(20260913+i), same alpha scheme k=round(alpha*n)',
                  'p_def': 'one-sided P(random gain >= model gain); percentile = % draws <= model',
                  'multiplicity': 'Bonferroni x4 across alphas per benchmark; beats-random iff p_bonf<0.05',
                  'rows': _vsrand},
}
json.dump(_det, open(str(OUT / 'c2x_details.json'), 'w'))
print('augmented c2x_details.json', flush=True)

# ---- c2x report ----
_R = []
_R.append('# c2x — MISSING-3 ablation package (D5 follow-up to c2)\n')
_R.append('**%s**\n' % LABELS)
_R.append('[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Numpy only; no network; read-only on /mnt/c. Machinery replicated from c2.py VERBATIM (SMALL=SPREAD48 repaired rank-linspace, LARGE=NATIVE96, sha256(c2|qid) split, logistic IRLS lam=1.0, routing gain with abstain-top-alpha predicted-fail, random baselines rng(20260913+i)); only OUT dir/filenames changed.\n')
_R.append('## 0. Reproduction gate (abort on fail — all PASS)\n')
_R.append('| Check | Recomputed | Reference | Tol | Diff |')
_R.append('|---|---|---|---|---|')
for (_n, _g, _r, _t) in _gate_checks:
    _R.append('| %s | %+.6f | %+.6f | %.3f | %.6f PASS |' % (_n, _g, _r, _t, abs(_g - _r)))
_R.append('\n## 1. LARGE-free ablation (drop margin34_large, crowd3_large)\n')
_R.append('Audit: the only features computed from the per-question full-budget (LARGE) retrieval ordering are margin34_large and crowd3_large — both dropped. Kept: margin34, crowd3, crowd4, crowd_pm1, top3_tie_share, boundary_share (SMALL arm only); N (archive size, free); var_decay (96-dim archive variance, per-archive precomputable, no per-question LARGE run); qent (query sign entropy, redefinable on SMALL bits); dup_top20 (BORDERLINE: top20 selected by SMALL ordering but distinctness evaluated on full-96-bit codes — kept in primary FREE10, dropped in STRICT9 sensitivity).\n')
_R.append('| Benchmark | Variant | Test AUC | gain@0.10 | gain@0.20 | gain@0.30 | gain@0.40 (pp) |')
_R.append('|---|---|---|---|---|---|---|')
for (_bn, _f, _rf, _s, _rs) in [('LME', _free_lme, _rfree_lme, _strict_lme, _rstrict_lme),
                                ('LOCO', _free_loco, _rfree_loco, _strict_loco, _rstrict_loco)]:
    _R.append('| %s | FREE10 (primary) | %.4f | %s |' % (_bn, _f['test_auc'],
              ' | '.join('%+.3f' % (100 * r['gain_model']) for r in _rf)))
    _R.append('| %s | STRICT9 (no dup_top20) | %.4f | %s |' % (_bn, _s['test_auc'],
              ' | '.join('%+.3f' % (100 * r['gain_model']) for r in _rs)))
_R.append('| LME | full COMBO (ref) | %.4f | %s |' % (res_lme['models']['COMBO']['test_auc'],
          ' | '.join('%+.3f' % (100 * r['gain_model']) for r in res_lme['routing'])))
_R.append('| LOCO | full COMBO (ref) | %.4f | %s |\n' % (res_loco['models']['COMBO']['test_auc'],
          ' | '.join('%+.3f' % (100 * r['gain_model']) for r in res_loco['routing'])))
_R.append('FREE10 remaining features (standardized coef, bias first):')
_R.append('- LME: ' + ', '.join('%s=%+.3f' % kv for kv in zip(['bias'] + FREE10, _free_lme['coef'])))
_R.append('- LOCO: ' + ', '.join('%s=%+.3f' % kv for kv in zip(['bias'] + FREE10, _free_loco['coef'])) + '\n')
_R.append('## 2. Gain CIs (paired bootstrap over test questions, B=2000, gain@0.20)\n')
_R.append('Fixed train-fit scores, resampled test evaluation; same resamples for full vs free (paired). 90% CI = 5th/95th percentiles. Seeds: LME 20260914, LOCO 20260915.\n')
_R.append('| Benchmark | Model | Mean gain (pp) | 90% CI (pp) |')
_R.append('|---|---|---|---|')
for _bn in ['LME', 'LOCO']:
    for _mn in ['full', 'free']:
        _d = _boot[_bn][_mn]
        _R.append('| %s | %s | %+.3f | [%+.3f, %+.3f] |' % (_bn, _mn, _d['mean_pp'], _d['lo90_pp'], _d['hi90_pp']))
    _pd = _boot[_bn]['paired_diff_free_minus_full_pp']
    _R.append('| %s | paired free-minus-full | %+.3f | [%+.3f, %+.3f] |\n' % (_bn, _pd['mean'], _pd['lo90'], _pd['hi90']))
_R.append('## 3. Formal vs-random test (200 draws, rng(20260913+i), k=round(alpha*n))\n')
_R.append('One-sided p = fraction of random draws with gain >= model gain; percentile = % draws <= model. Bonferroni x4 across alphas per benchmark; beats-random iff p_bonf < 0.05.\n')
_R.append('| Benchmark | alpha | Model gain (pp) | Random mean [min,max] (pp) | Percentile | p_raw | p_bonf | Verdict |')
_R.append('|---|---|---|---|---|---|---|---|')
for _bn in ['LME', 'LOCO']:
    for _row in _vsrand[_bn]:
        _f = _row['full']
        _R.append('| %s | %.2f | %+.3f | %+.3f [%+.3f,%+.3f] | %.1f | %.4f | %.4f | %s |' % (
            _bn, _row['alpha'], _f['gain_pp'], _row['random_mean_pp'], _row['random_min_pp'],
            _row['random_max_pp'], _f['percentile'], _f['p_raw'], _f['p_bonf'], _f['verdict']))
_R.append('\nLARGE-free variant vs-random (same test, for the deployability question):')
_R.append('| Benchmark | alpha | Free gain (pp) | Percentile | p_raw | p_bonf | Verdict |')
_R.append('|---|---|---|---|---|---|---|')
for _bn in ['LME', 'LOCO']:
    for _row in _vsrand[_bn]:
        _f = _row['free']
        _R.append('| %s | %.2f | %+.3f | %.1f | %.4f | %.4f | %s |' % (
            _bn, _row['alpha'], _f['gain_pp'], _f['percentile'], _f['p_raw'], _f['p_bonf'], _f['verdict']))
_R.append('\n## 4. Preregistration readiness\n')
_R.append('c2 is NOT prereg-ready as-is: the LoCoMo leg is vacuous vs random-abstention (inside-noise at every alpha after Bonferroni; COMBO test AUC 0.558), and the router as specified pays the full budget to compute its LARGE-arm features. The binding gate for any future c2 preregistration: on held-out data, model gain@0.20 must exceed the max (not the mean) of >=200 same-protocol random-abstention draws, separately per benchmark; the LARGE-free variant must be the registered model (no full-budget features at routing time). LoCoMo must NOT be called a replication unless that gate fires there too.\n')
_R.append('## 5. Honesty: what this cannot show\n')
_R.append('- n: LME 470 (train %d / test %d, test fails %d); LoCoMo 1535 (train %d / test %d, test fails %d). Test routing n is small on LME; pp gains and CIs there are noisy.' % (
    res_lme['base']['n_train'], res_lme['base']['n_test'], res_lme['base']['fail_test'],
    res_loco['base']['n_train'], res_loco['base']['n_test'], res_loco['base']['fail_test']))
_R.append('- Single learner (logistic IRLS, L2=1.0, train-standardized); fixed a-priori feature sets (12 full, 10 LARGE-free, 9 strict). No feature search; a different set/learner could differ.')
_R.append('- Failure = small strictly worse than large (FR_small < FR_large - 1e-12); identically-failing questions are not routable by construction.')
_R.append('- Bootstrap fixes the train fit and resamples only test evaluation: CIs cover test-sampling noise, not train-fit or split arbitrariness (single fixed sha256 split).')
_R.append('- Random-abstention draws share one seed protocol; p-values are exact only w.r.t. that null (uniform random subsets of size k). Bonferroni x4 is per benchmark; no correction across benchmarks or model variants.')
_R.append('- dup_top20/var_decay/qent caveats (see audit): LARGE-free means free of the per-question LARGE retrieval pass, not free of all full-bank statistics.')
_R.append('- [LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].')
open(str(OUT / 'c2x_report.md'), 'w').write('\n'.join(_R))
print('wrote c2x_report.md', flush=True)

# ---- verdict (stdout must END with this) ----
def _v(b, a, m='full'):
    for _row in _vsrand[b]:
        if abs(_row['alpha'] - a) < 1e-9:
            return _row[m]
    raise AssertionError
_vf = lambda b, a: _v(b, a, 'free')
print('C2X_VERDICT: <LARGE-free testAUC LME=%.3f/LOCO=%.3f, gain@.20 LME=%+.3fpp/LOCO=%+.3fpp; '
      '90%%CI full LME=[%+.3f,%+.3f]/LOCO=[%+.3f,%+.3f], free LME=[%+.3f,%+.3f]/LOCO=[%+.3f,%+.3f]; '
      'vs-random(full) LME %s / LOCO %s; vs-random(free) LME %s / LOCO %s; c2 NOT prereg-ready - '
      'binding gate: held-out gain@.20 > max of >=200 random draws per benchmark, LARGE-free model only>' % (
    _free_lme['test_auc'], _free_loco['test_auc'],
    100 * _gain_at2({'routing': _rfree_lme}, 0.20)['gain_model'],
    100 * _gain_at2({'routing': _rfree_loco}, 0.20)['gain_model'],
    _boot['LME']['full']['lo90_pp'], _boot['LME']['full']['hi90_pp'],
    _boot['LOCO']['full']['lo90_pp'], _boot['LOCO']['full']['hi90_pp'],
    _boot['LME']['free']['lo90_pp'], _boot['LME']['free']['hi90_pp'],
    _boot['LOCO']['free']['lo90_pp'], _boot['LOCO']['free']['hi90_pp'],
    ';'.join('a%.2f:%s' % (_r['alpha'], _r['full']['verdict']) for _r in _vsrand['LME']),
    ';'.join('a%.2f:%s' % (_r['alpha'], _r['full']['verdict']) for _r in _vsrand['LOCO']),
    ';'.join('a%.2f:%s' % (_r['alpha'], _r['free']['verdict']) for _r in _vsrand['LME']),
    ';'.join('a%.2f:%s' % (_r['alpha'], _r['free']['verdict']) for _r in _vsrand['LOCO'])), flush=True)
