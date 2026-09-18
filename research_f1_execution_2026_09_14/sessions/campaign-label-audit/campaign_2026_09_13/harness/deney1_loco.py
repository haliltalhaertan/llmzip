#!/usr/bin/env python3
"""Deney 1 LoCoMo mirror: multi-split robustness of learned axis selection on LoCoMo.
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Mirrors harness/deney1_lme.py on LoCoMo Cat1-4 (valid 1535 q). Reuses the frozen T4D/R2C
protocol verbatim: sign hamming (C>=0, QC>=0), top-3, stable_archive_seed(ci,t)+99 priorities,
20 nuisance trials, audit corrections applied. Per-axis drop/alone FR arrays are computed here
(do not exist for LoCoMo) and saved as npz for independent verification. delta-arm omitted
(no per-axis delta array for LoCoMo; noted).
"""
import hashlib, json, re, pickle, time
from pathlib import Path
from collections import Counter
import numpy as np

BASE = Path('C:/Users/MDP/dev/llmzip-work')
RAW = BASE/'drive/locomo10.json'
AUDIT = BASE/'drive/audit_layer'
REGEN = BASE/'regen/locomo'
OUTDIR = BASE/'pilots/axis_attack_2026-09-12/round3'
OUT = OUTDIR/'deney1_loco_details.json'
NPZOUT = OUTDIR/'deney1_loco_peraxis.npz'

NATIVE_ANCHOR = 0.23654714666441054
EXPECT_VALID = 1535
TOPK = 3
N_NUISANCE = 20
K_LIST = [32, 48, 64]
NSALT = 10
NBOOT = 2000

def rand_seeds(split_idx):
    return [91000 + split_idx * 10 + j for j in range(10)]

# ---- verbatim frozen protocol helpers (from r2c_replicate.py) ----
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

def topks_by_hamming(dist, priorities, k=TOPK):
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
    R = set(map(int, top)); G = set(map(int, gold_rows))
    inter = len(R & G)
    return {"valid": 1, "any": float(inter > 0), "all": float(G.issubset(R)),
            "fractional": float(inter / len(G)), "gold_count": len(G)}

def mean_or_nan(xs):
    a = np.asarray(xs, dtype=float)
    return float(np.nanmean(a)) if np.isfinite(a).any() else np.nan

t0 = time.time()
OUTDIR.mkdir(parents=True, exist_ok=True)

# ---- load raw + corrections ----
raw = json.loads(RAW.read_text(encoding="utf-8"))
corr = load_audit_corrections(AUDIT)
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
        qas.append({"question_id": str(qid), "category": cat, "correct_evidence": ce})
    convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
print("raw_convs:", len(convs), "cat14_questions:", sum(len(c['qas']) for c in convs), "corrections:", len(corr), flush=True)

# ---- load regen matrices, verify alignment ----
reps = []
for ci in range(10):
    d = pickle.load(open(REGEN / f"locomo_{ci}.pkl", "rb"))
    assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
    raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
    pkl_ids = [q["question_id"] for q in d["qas"]]
    assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
    assert d["QC"].shape[0] == len(d["qas"]), (ci, d["QC"].shape)
    reps.append(d)
print("alignment OK (pkl qas order == raw Cat1-4 order)", flush=True)

# ---- per-question gold, validity ----
Q = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    id_to_row = r["id_to_row"]
    for qi, q in enumerate(c["qas"]):
        ag = evidence_rows(q["correct_evidence"], id_to_row)
        Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
valid_qids = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
print("valid_audit_questions:", len(valid_qids), f"(frozen expects {EXPECT_VALID})", flush=True)
assert len(valid_qids) == EXPECT_VALID

# ---- per-conv structures: A (disagree counts), dist96, priorities, pool ----
A_of, D96_of, PR_of, AG_of, VR_of = {}, {}, {}, {}, {}
N_of = {}
for ci, r in enumerate(reps):
    C = np.asarray(r["C"], float); QC = np.asarray(r["QC"], float)
    M = (QC[:, None, :] >= 0) != (C[None, :, :] >= 0)
    A = M.astype(np.int16)
    A_of[ci] = A
    D96_of[ci] = A.sum(axis=2)
    N = C.shape[0]; N_of[ci] = N
    PR_of[ci] = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(N) for t in range(N_NUISANCE)]
    order = np.argsort(C.var(axis=0))[::-1]  # descending variance
    rank = np.empty(96, dtype=np.int16); rank[order] = np.arange(96, dtype=np.int16)
    VR_of[ci] = rank  # rank 0 = most variance (consistent with LME var_rank via U_var=(-rank).mean)
    AG_of[ci] = {qi: Q[qid]["ag"] for qi, qid in enumerate([q["question_id"] for q in convs[ci]["qas"]]) }

def q_fractional(dist_q, pr, gold):
    tops = topks_by_hamming(dist_q, pr)
    return mean_or_nan([retrieval_metrics(t, gold)["fractional"] for t in tops])

# ---- per-axis arrays for VALID questions ----
vidx_of_conv = {ci: [] for ci in range(10)}
for qid in valid_qids:
    vidx_of_conv[Q[qid]["ci"]].append(Q[qid]["qi"])
V = len(valid_qids)
native_fr = np.full(V, np.nan); drop_fr = np.full((V, 96), np.nan)
alone_fr = np.full((V, 96), np.nan); pool_q = np.zeros((V, 96), dtype=np.int32)
vr_of_q = np.zeros((V, 96), dtype=np.int16)
cat_of_q = np.zeros(V, dtype=np.int8)
pos_of = {}
p = 0
for ci in range(10):
    A = A_of[ci]; D96 = D96_of[ci]; pr = PR_of[ci]; N = N_of[ci]
    for qi in sorted(vidx_of_conv[ci]):
        qid = convs[ci]["qas"][qi]["question_id"]
        ag = Q[qid]["ag"]
        pos_of[qid] = p
        cat_of_q[p] = Q[qid]["cat"]
        vr_of_q[p] = VR_of[ci]
        native_fr[p] = q_fractional(D96[qi], pr, ag)
        for a in range(96):
            drop_fr[p, a] = q_fractional(D96[qi] - A[qi, :, a], pr, ag)
            alone_fr[p, a] = q_fractional(A[qi, :, a], pr, ag)
        pool_q[p] = N - A[qi].sum(axis=0)
        p += 1
print(f"per-axis arrays done ({time.time()-t0:.0f}s)", flush=True)

# ---- GATE: native vs frozen anchor ----
nat_mean = float(np.nanmean(native_fr))
print(f"NATIVE = {nat_mean!r} anchor = {NATIVE_ANCHOR!r} diff = {nat_mean - NATIVE_ANCHOR!r}", flush=True)
assert abs(nat_mean - NATIVE_ANCHOR) < 1e-12, 'native gate failed'

np.savez_compressed(NPZOUT, qids=np.array(valid_qids), cats=cat_of_q,
                    native=native_fr, drop=drop_fr, alone=alone_fr, pool=pool_q, var_rank=vr_of_q)
print(f"saved per-axis npz: {NPZOUT}", flush=True)

# ---- splits (stratified by category, 10 salts) ----
def make_split(s):
    tr, te = [], []
    for c in (1, 2, 3, 4):
        qs = sorted([qid for qid in valid_qids if Q[qid]["cat"] == c],
                    key=lambda q: hashlib.sha256(f'deney1loco|{s}|{q}'.encode()).hexdigest())
        for i, q in enumerate(qs):
            (tr if i % 2 == 0 else te).append(q)
    return sorted(tr), sorted(te)

splits = [make_split(s) for s in range(NSALT)]
for s, (tr, te) in enumerate(splits):
    assert len(set(tr) & set(te)) == 0 and len(tr) + len(te) == V
    print(f'split {s}: train={len(tr)} test={len(te)}', flush=True)

all_out = {'labels': ['[LOCAL EXPLORATORY PILOT]', '[NOT PREREGISTERED]', '[DISCLOSE-BEFORE-USE]',
                      'Deney1 LoCoMo mirror (Muse roadmap Design 1)'],
           'protocol': 'T4D/R2C verbatim: sign hamming, top-3, stable_archive_seed(ci,t)+99, 20 trials',
           'native_anchor': NATIVE_ANCHOR, 'native_recomputed': nat_mean,
           'n_valid': V, 'n_splits': NSALT, 'note': 'delta-arm omitted (no per-axis delta for LoCoMo)',
           'splits': [], 'summary': {}}

summary_rows = []
for s, (train_q, test_q) in enumerate(splits):
    tr = np.array([pos_of[q] for q in train_q]); te = np.array([pos_of[q] for q in test_q])
    nat_tr = native_fr[tr]; nat_te = native_fr[te]
    U_drop = (nat_tr[:, None] - drop_fr[tr]).mean(axis=0)
    U_alone = (alone_fr[tr] * pool_q[tr] / 3).mean(axis=0)
    U_var = (-vr_of_q[tr].astype(float)).mean(axis=0)
    U = {'drop': U_drop, 'alone': U_alone, 'var': U_var}

    Ufull_drop = (native_fr[:, None] - drop_fr).mean(axis=0)
    ov = len(set(np.argsort(U_drop)[::-1][:64].tolist()) & set(np.argsort(Ufull_drop)[::-1][:64].tolist()))

    arms = {}
    for uname, u in U.items():
        for k in K_LIST:
            arms[f'{uname}{k}'] = np.sort(np.argsort(u)[::-1][:k]).astype(int)
    order_desc = np.argsort(U_var)[::-1]
    for k in K_LIST:
        pos = np.round(np.linspace(0, 95, k)).astype(int)
        assert len(np.unique(pos)) == k
        arms[f'SPREAD{k}'] = np.sort(order_desc[pos]).astype(int)
    for j, sd in enumerate(rand_seeds(s)):
        for k in K_LIST:
            arms[f'RANDOM{k}_s{sd}'] = np.sort(np.random.default_rng(sd).choice(96, k, replace=False)).astype(int)

    # evaluate on test (per conv slice; cache per-split test slices to avoid repeat copies)
    te_by_conv = {ci: [] for ci in range(10)}
    pos_in_test = {q: i for i, q in enumerate(test_q)}
    for q in test_q:
        te_by_conv[Q[q]["ci"]].append(Q[q]["qi"])
    Ate_cache, meta_conv = {}, {}
    for ci in range(10):
        qis = sorted(te_by_conv[ci])
        if not qis:
            continue
        Ate_cache[ci] = A_of[ci][qis]
        meta_conv[ci] = (qis, [convs[ci]["qas"][qi]["question_id"] for qi in qis])
    per_q_test = {}
    for name, cols in arms.items():
        vals = np.empty(len(test_q))
        for ci in range(10):
            if ci not in Ate_cache:
                continue
            Ate = Ate_cache[ci][:, :, cols].sum(axis=2)
            pr = PR_of[ci]
            _, qid_list = meta_conv[ci]
            for i, qid in enumerate(qid_list):
                vals[pos_in_test[qid]] = q_fractional(Ate[i], pr, Q[qid]["ag"])
        per_q_test[name] = vals

    test_fr = {n: float(v.mean()) for n, v in per_q_test.items()}
    rmean = {k: float(np.mean([test_fr[f'RANDOM{k}_s{sd}'] for sd in rand_seeds(s)])) for k in K_LIST}
    rmax = {k: float(max(test_fr[f'RANDOM{k}_s{sd}'] for sd in rand_seeds(s))) for k in K_LIST}
    nat_test = float(nat_te.mean())

    def gap_vs_best(armname, k):
        d = per_q_test[armname]
        R = np.array([per_q_test[f'RANDOM{k}_s{sd}'] for sd in rand_seeds(s)])
        gap = float(d.mean() - max(R[j].mean() for j in range(len(rand_seeds(s)))))
        rng = np.random.default_rng(778000 + s); nn = len(test_q)
        diffs = np.empty(NBOOT)
        for b in range(NBOOT):
            idx = rng.integers(0, nn, nn)
            diffs[b] = d[idx].mean() - max(R[j][idx].mean() for j in range(len(rand_seeds(s))))
        lo, hi = np.percentile(diffs, [5, 95])
        return gap, float(lo), float(hi)

    g64, lo_d, hi_d = gap_vs_best('drop64', 64)
    g64a, lo_a, hi_a = gap_vs_best('alone64', 64)
    var_worst = {}
    for k in K_LIST:
        fam = {u: test_fr[f'{u}{k}'] for u in ['drop', 'alone', 'var', 'SPREAD']}
        var_worst[str(k)] = bool(min(fam, key=lambda x: fam[x]) == 'var')

    row = {'split': s, 'n_test': len(test_q), 'native_test': nat_test,
           'drop64': test_fr['drop64'], 'alone64': test_fr['alone64'],
           'RANDOM64_best': rmax[64], 'RANDOM64_mean': rmean[64],
           'gap64_vs_best_pp': g64 * 100, 'gap64_ci90': [lo_d * 100, hi_d * 100],
           'gap64_alone_vs_best_pp': g64a * 100, 'gap64_alone_ci90': [lo_a * 100, hi_a * 100],
           'gap48_drop_vs_best_pp': float((test_fr['drop48'] - rmax[48]) * 100),
           'gap48_alone_vs_best_pp': float((test_fr['alone48'] - rmax[48]) * 100),
           'gap32_drop_vs_best_pp': float((test_fr['drop32'] - rmax[32]) * 100),
           'gap32_alone_vs_best_pp': float((test_fr['alone32'] - rmax[32]) * 100),
           'var_worst': var_worst, 'top64_train_full_overlap': int(ov)}
    summary_rows.append(row)
    print(f"SPLIT {s}: native={nat_test:.4f} drop64={test_fr['drop64']:.4f} alone64={test_fr['alone64']:.4f} "
          f"rand_best64={rmax[64]:.4f} gap64_vs_best={g64*100:+.2f}pp CI90=[{lo_d*100:+.2f},{hi_d*100:+.2f}] "
          f"var_worst={var_worst}", flush=True)

    all_out['splits'].append({'s': s, 'run': row,
                              'utilities_top5': {k: [int(i) for i in np.argsort(v)[::-1][:5]] for k, v in U.items()},
                              'arms': {n: {'test_FR': test_fr[n], 'cols': [int(c) for c in arms[n]]} for n in arms},
                              'random_seeds': rand_seeds(s),
                              'per_q_test': {n: [float(x) for x in per_q_test[n]] for n in per_q_test}})

g64 = [r['gap64_vs_best_pp'] for r in summary_rows]
g64a = [r['gap64_alone_vs_best_pp'] for r in summary_rows]
summ = {
    'drop64_gap_vs_best_pp': {'mean': float(np.mean(g64)), 'median': float(np.median(g64)),
                              'range': [float(min(g64)), float(max(g64))],
                              'wins': f"{sum(1 for x in g64 if x > 0)}/{NSALT}"},
    'alone64_gap_vs_best_pp': {'mean': float(np.mean(g64a)), 'median': float(np.median(g64a)),
                               'range': [float(min(g64a)), float(max(g64a))],
                               'wins': f"{sum(1 for x in g64a if x > 0)}/{NSALT}"},
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
print('DENEY1_LOCO_DONE')
