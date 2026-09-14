#!/usr/bin/env python3
"""CERT: quality-equivalence certificates for the 12B-and-below ladder.
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]
Read-only /mnt/c; writes only /tmp/cert/. No network.
Recomputes per-question fractional R@3 (K=3, NT=20, frozen tie protocol) for
ladder rungs b in {96 native, 80 (10B), 64 (8B), 48 (6B)} x families
{RAND_avg(3 seeds), SPREAD (rank-linspace), BOT, TOP-ref} on LME-470 + LoCoMo-1535.
Gates every aggregate against frozen anchors, then paired-bootstrap certs.
"""
import json, pickle, re, time
from pathlib import Path
import numpy as np

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work')
LME_PKL = BASE/'regen/lme/cache_repr'
LME_DATA = BASE/'drive/longmemeval_s_cleaned.json'
LOCO_RAW = BASE/'drive/locomo10.json'
LOCO_AUD = BASE/'drive/audit_layer'
LOCO_REGEN = BASE/'regen/locomo'
OUT = Path('/tmp/cert')
K = 3; NT = 20; B = 20000; BOOTSEED = 20260913
RUNGS = [48, 64, 80]   # 6B, 8B, 10B ; 12B = native96
LME_NATIVE_ANCHOR = 0.5419751773049645
LOCO_NATIVE_ANCHOR = 0.23654714666441054
LME_FLOAT96 = 0.4416  # frozen continuous-quality anchor (given; not recomputed here)
# frozen aggregate gates from pilot/extra_arms/r2c artefacts
LME_GATES = {'RAND48_s0': 0.47292553191489356, 'RAND64_s0': 0.47402659574468076,
             'RAND80_s0': 0.5146737588652481, 'RANKSTRIDE48': 0.4502907801418439,
             'TOP48': 0.34949468085106383, 'BOT48': 0.4284574468085106,
             'IDXSTRIDE48': 0.4444858156028369}
t0 = time.time()

def f_of_ST(S, T, k=K):
    if S >= k: return 0.0
    if S + T <= k: return 1.0
    return (k - S) / T

def exact_fr(d, gold, k=K):
    d = np.asarray(d); tot = 0.0
    for g in np.ravel(gold):
        dg = d[int(g)]
        S = int(np.count_nonzero(d < dg)); T = int(np.count_nonzero(d == dg))
        tot += f_of_ST(S, T, k)
    return tot / len(np.ravel(gold))

def spread_cols(order_desc, k):
    pos = np.round(np.linspace(0, 95, k)).astype(int)
    assert len(np.unique(pos)) == k
    return np.sort(order_desc[pos]).astype(int)

# ---------------- LME ----------------
data = json.loads(LME_DATA.read_text())
allq = sorted(str(x['question_id']) for x in data); del data
lex = {q: i for i, q in enumerate(allq)}
assert len(allq) == 500
pkls = sorted(LME_PKL.glob('*.pkl')); assert len(pkls) == 470, len(pkls)
L = {}
for p in pkls:
    o = pickle.load(open(p, 'rb'))
    qid = str(o['question_id'])
    C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
    D0 = (C >= 0); Q0 = (qC >= 0)
    g = np.asarray(o['gold']).ravel()
    n = len(C); lx = lex[qid]
    pr = [np.random.default_rng(5_100_000 + lx*100_000 + t*100 + 99).random(n) for t in range(NT)]
    L[qid] = dict(D0=D0, Q0=Q0, g=g, pr=pr, var=C.var(axis=0))
print(f'LME loaded 470 ({time.time()-t0:.0f}s)', flush=True)
qids = sorted(L.keys())

def lme_fr(qid, cols):
    e = L[qid]; d = np.count_nonzero(e['D0'][:, cols] != e['Q0'][cols][None, :], axis=1)
    gg = set(map(int, e['g']))
    tot = 0.0
    for p in e['pr']:
        order = np.lexsort((p, d))
        tot += len(set(map(int, order[:K])) & gg) / len(gg)
    return tot / NT, exact_fr(d, e['g'])

lme_mc, lme_ex = {}, {}
lme_arms = {'NATIVE': None}
for k in RUNGS:
    for s in range(3):
        lme_arms[f'RAND{k}_s{s}'] = np.sort(np.random.default_rng(12000+s).choice(96, k, replace=False))
lme_res = {}
for name in ['NATIVE'] + sorted([a for a in lme_arms if a != 'NATIVE']):
    mc = np.empty(len(qids)); ex = np.empty(len(qids))
    for i, qid in enumerate(qids):
        if name == 'NATIVE':
            cols = np.arange(96)
        elif name.startswith('RAND'):
            cols = lme_arms[name]
        else:
            od = np.argsort(L[qid]['var'], kind='stable')[::-1]
            kk = int(name[4:]) if name[:3] in ('TOP','BOT') else int(name[6:])
            if name.startswith('TOP'): cols = np.sort(od[:kk])
            elif name.startswith('BOT'): cols = np.sort(od[::-1][:kk])
            else: cols = spread_cols(od, kk)
        a, b = lme_fr(qid, cols)
        mc[i] = a; ex[i] = b
    lme_res[name] = dict(mc=mc, ex=ex)
    if (len(lme_res)) % 4 == 0: print(f'  LME {len(lme_res)}/{1+len(lme_arms)} ({time.time()-t0:.0f}s)', flush=True)
# add TOP/BOT/SPREAD arms (not in lme_arms dict yet)
for fam in ('SPREAD', 'TOP', 'BOT'):
    for k in RUNGS:
        name = f'{fam}{k}'
        mc = np.empty(len(qids)); ex = np.empty(len(qids))
        for i, qid in enumerate(qids):
            od = np.argsort(L[qid]['var'], kind='stable')[::-1]
            cols = spread_cols(od, k) if fam=='SPREAD' else (np.sort(od[:k]) if fam=='TOP' else np.sort(od[::-1][:k]))
            a, b = lme_fr(qid, cols); mc[i] = a; ex[i] = b
        lme_res[name] = dict(mc=mc, ex=ex)
print(f'LME arms done ({time.time()-t0:.0f}s)', flush=True)
# stride constructions (frozen-verbatim pilot_extra_arms) for gates; certified SPREAD family = rank-linspace above
for sname, mode in (('RANKSTRIDE48', 'r'), ('IDXSTRIDE48', 'i')):
    mc = np.empty(len(qids)); ex = np.empty(len(qids))
    for i, qid in enumerate(qids):
        od = np.argsort(L[qid]['var'], kind='stable')[::-1]
        cols = np.sort(od[::2][:48]) if mode == 'r' else np.sort(np.arange(96)[::2][:48])
        a, b = lme_fr(qid, cols); mc[i] = a; ex[i] = b
    lme_res[sname] = dict(mc=mc, ex=ex)
# RAND_avg family
for k in RUNGS:
    mcs = np.mean([lme_res[f'RAND{k}_s{s}']['mc'] for s in range(3)], axis=0)
    exs = np.mean([lme_res[f'RAND{k}_s{s}']['ex'] for s in range(3)], axis=0)
    lme_res[f'RANDavg{k}'] = dict(mc=mcs, ex=exs)

nat = float(lme_res['NATIVE']['mc'].mean())
print(f'LME NATIVE mc={nat!r} anchor={LME_NATIVE_ANCHOR!r} diff={nat-LME_NATIVE_ANCHOR:.2e}', flush=True)
assert abs(nat - LME_NATIVE_ANCHOR) < 1e-12, 'LME native gate FAILED'
for gname, gval in LME_GATES.items():
    got = float(lme_res[gname]['mc'].mean())
    print(f'  gate {gname}: got={got:.8f} frozen={gval:.8f} diff={got-gval:.2e}', flush=True)
    assert abs(got - gval) < 1e-9, f'LME gate {gname} FAILED'
# exact-model cross-check
print(f'LME NATIVE exact={float(lme_res["NATIVE"]["ex"].mean()):.6f} (MATH-1 pred 0.542134)', flush=True)

# ---------------- LoCoMo ----------------
def norm_evidence(x):
    if x is None: return []
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
                if did: out.append(str(did))
        return list(dict.fromkeys(out))
    return []

corr = {}
for f in sorted(LOCO_AUD.glob("errors_conv_*.json")):
    try: rows = json.loads(f.read_text(encoding="utf-8"))
    except Exception: continue
    if not isinstance(rows, list): continue
    for r in rows:
        qid = r.get("question_id")
        if qid: corr[str(qid)] = list(norm_evidence(r.get("correct_evidence"))) if "correct_evidence" in r else list(norm_evidence(None))
raw = json.loads(LOCO_RAW.read_text(encoding="utf-8"))
convs = []
for idx, item in enumerate(raw):
    qas = []
    for qi, q in enumerate(item.get("qa", []) or []):
        cat = int(q.get("category")) if q.get("category") is not None else None
        if cat not in (1, 2, 3, 4): continue
        qid = q.get("question_id") or f"locomo_{idx}_qa{qi}"
        ce = corr[str(qid)] if str(qid) in corr and corr[str(qid)] else list(norm_evidence(q.get("evidence")))
        # note: audit semantics mirror deney1_loco (has_correct_evidence flag); recompute faithfully:
        qas.append({"question_id": str(qid), "category": cat, "ce_raw": ce})
    convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
del raw
# faithful audit application (verbatim deney1_loco logic)
import json as _j
corr2 = {}
for f in sorted(LOCO_AUD.glob("errors_conv_*.json")):
    try: rows = _j.loads(f.read_text(encoding="utf-8"))
    except Exception: continue
    if not isinstance(rows, list): continue
    for r in rows:
        qid = r.get("question_id")
        if not qid: continue
        corr2[str(qid)] = {"has": "correct_evidence" in r, "ce": norm_evidence(r.get("correct_evidence"))}
reps = []
for ci in range(10):
    d = pickle.load(open(LOCO_REGEN / f"locomo_{ci}.pkl", "rb"))
    assert d["conv_id"] == f"locomo_{ci}"
    reps.append(d)
Q = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    id_to_row = r["id_to_row"]
    for qi, q in enumerate(c["qas"]):
        z = corr2.get(q["question_id"])
        ce = list(z["ce"]) if (z and z["has"]) else list(norm_evidence(None))  # placeholder
        Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "idr": id_to_row, "_z": z}
# rebuild correct evidence exactly as deney1_loco: need raw evidence per question -> reload raw qa evidence
raw2 = json.loads(LOCO_RAW.read_text(encoding="utf-8"))
for ci, item in enumerate(raw2):
    k = 0
    for qi, q in enumerate(item.get("qa", []) or []):
        cat = int(q.get("category")) if q.get("category") is not None else None
        if cat not in (1, 2, 3, 4): continue
        qid = q.get("question_id") or f"locomo_{ci}_qa{qi}"
        z = corr2.get(str(qid))
        if z and z["has"]: ce = list(z["ce"])
        else: ce = list(norm_evidence(q.get("evidence")))
        idr = Q[str(qid)]["idr"]
        ag = [int(idr[x]) for x in ce if x in idr]
        ag = list(dict.fromkeys(ag))
        Q[str(qid)]["ag"] = ag
del raw2
valid = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
print(f'LoCoMo valid={len(valid)} (expect 1535)', flush=True)
assert len(valid) == 1535, 'LoCoMo validity gate FAILED'

A_of, D96_of, PR_of, VR_of = {}, {}, {}, {}
for ci, r in enumerate(reps):
    C = np.asarray(r["C"], float); QC = np.asarray(r["QC"], float)
    M = (QC[:, None, :] >= 0) != (C[None, :, :] >= 0)
    A_of[ci] = M.astype(np.int16)
    D96_of[ci] = M.sum(axis=2)
    N = C.shape[0]
    PR_of[ci] = np.array([np.random.default_rng(5_100_000 + ci*100_000 + t*100 + 99).random(N) for t in range(NT)])
    order = np.argsort(C.var(axis=0))[::-1]
    rank = np.empty(96, dtype=np.int16); rank[order] = np.arange(96, dtype=np.int16)
    VR_of[ci] = (order, rank)
print(f'LoCoMo mats ready ({time.time()-t0:.0f}s)', flush=True)

def loco_topks(dist, P, k=K):
    dist = np.asarray(dist)
    if len(dist) <= k:
        return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k-1)[k-1]
    strict = np.flatnonzero(dist < kth); bnd = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, bnd]
    if need == len(bnd): picks = np.tile(bnd, (len(P), 1))
    else: picks = bnd[np.argpartition(BP, need-1, axis=1)[:, :need]]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]

def loco_fr(dist_q, pr, gold):
    G = set(map(int, gold))
    ts = loco_topks(dist_q, pr)
    return float(np.mean([len(set(map(int, t)) & G) / len(G) for t in ts]))

loco_res = {}
armspec = ['NATIVE']
for k in RUNGS:
    armspec += [f'RAND{k}_s{s}' for s in range(3)] + [f'SPREAD{k}', f'BOT{k}', f'TOP{k}']
for name in armspec:
    mc = np.empty(len(valid)); ex = np.empty(len(valid))
    for i, qid in enumerate(valid):
        v = Q[qid]; ci, qi = v["ci"], v["qi"]
        A = A_of[ci]; pr = PR_of[ci]; ag = v["ag"]
        if name == 'NATIVE': cols = np.arange(96)
        elif name.startswith('RAND'):
            kk = int(name[4:6]); sd = int(name[-1])
            cols = np.sort(np.random.default_rng(12000+sd).choice(96, kk, replace=False))
        else:
            m = re.match(r'(SPREAD|BOT|TOP)(\d+)', name); fam, kk = m.group(1), int(m.group(2))
            od = VR_of[ci][0]
            cols = spread_cols(od, kk) if fam=='SPREAD' else (np.sort(od[:kk]) if fam=='TOP' else np.sort(od[::-1][:kk]))
        dq = A[qi][:, cols].sum(axis=1)
        mc[i] = loco_fr(dq, pr, ag)
        ex[i] = exact_fr(dq, ag)
    loco_res[name] = dict(mc=mc, ex=ex)
    print(f'  LoCoMo {name} mc={float(mc.mean()):.6f} ({time.time()-t0:.0f}s)', flush=True)
for k in RUNGS:
    loco_res[f'RANDavg{k}'] = dict(mc=np.mean([loco_res[f'RAND{k}_s{s}']['mc'] for s in range(3)], axis=0),
                                   ex=np.mean([loco_res[f'RAND{k}_s{s}']['ex'] for s in range(3)], axis=0))
natL = float(loco_res['NATIVE']['mc'].mean())
print(f'LoCoMo NATIVE mc={natL!r} anchor={LOCO_NATIVE_ANCHOR!r} diff={natL-LOCO_NATIVE_ANCHOR:.2e}', flush=True)
assert abs(natL - LOCO_NATIVE_ANCHOR) < 1e-12, 'LoCoMo native gate FAILED'
# R2C frozen gates (s0 values from r2c_loco_replication final JSON)
LOCO_G = {'RAND48_s0': 0.15912137829171744, 'RAND64_s0': 0.18862519440704917, 'RAND80_s0': 0.22767557849316805}
for gname, gval in LOCO_G.items():
    got = float(loco_res[gname]['mc'].mean())
    print(f'  gate {gname}: got={got:.8f} frozen={gval:.8f} diff={got-gval:.2e}', flush=True)
    assert abs(got - gval) < 1e-9, f'LoCoMo gate {gname} FAILED'
print(f'LoCoMo NATIVE exact={float(loco_res["NATIVE"]["ex"].mean()):.6f}', flush=True)
print(f'ALL GATES PASSED ({time.time()-t0:.0f}s)', flush=True)

# ---------------- certificates ----------------
rng = np.random.default_rng(BOOTSEED)
FAMS = ['RANDavg', 'SPREAD', 'BOT']  # certified families (+ TOP as reference)
M = len(RUNGS) * 2 * len(FAMS)       # Bonferroni family size = 18
q_bonf = 100 * 0.05 / M              # one-sided Bonferroni percentile level

def cert_row(d, B=B):
    d = np.asarray(d, float); n = len(d)
    gap = float(d.mean()); sd = float(d.std(ddof=1)); se = sd / np.sqrt(n)
    idx = rng.integers(0, n, size=(B, n))
    bm = d[idx].mean(axis=1)
    lb95 = float(np.percentile(bm, 5)); lb_fwer = float(np.percentile(bm, q_bonf))
    lo2, hi2 = [float(x) for x in np.percentile(bm, [2.5, 97.5])]
    p_no_worse = float((bm >= 0).mean())  # boot approx of P(mu>=0)? replaced below by t
    return dict(n=n, gap=gap, gap_pp=gap*100, sd=sd, se=se, se_pp=se*100,
                lb95=lb95, lb95_pp=lb95*100, lb_fwer=lb_fwer, lb_fwer_pp=lb_fwer*100,
                ci95_2sided_pp=[lo2*100, hi2*100],
                eps_pc_pp=max(0.0, -lb95*100), eps_fwer_pp=max(0.0, -lb_fwer*100))

cert = {}
for bench, res, natv in (('LME', lme_res, lme_res['NATIVE']['mc']),
                          ('LoCoMo', loco_res, loco_res['NATIVE']['mc'])):
    for k in RUNGS:
        for fam in FAMS + ['TOP']:
            name = f'{fam}{k}'
            row = cert_row(res[name]['mc'] - natv)
            row['arm_mean'] = float(res[name]['mc'].mean())
            row['arm_mean_exact'] = float(res[name]['ex'].mean())
            row['gap_exact_pp'] = float((res[name]['ex'] - res['NATIVE']['ex']).mean()*100)
            cert[f'{bench}|{name}'] = row
# beats-float96 (LME only): one-sided 95% LB of arm mean vs 0.4416
for k in RUNGS:
    for fam in FAMS:
        name = f'{fam}{k}'; a = lme_res[name]['mc']
        bm = a[rng.integers(0, len(a), size=(B, len(a)))].mean(axis=1)
        lb = float(np.percentile(bm, 5))
        cert[f'LME|{name}']['float96_lb95'] = lb
        cert[f'LME|{name}']['float96_margin_pp'] = (lb - LME_FLOAT96)*100
# MC trial-noise scale: mean over questions of Var(trials)/20 contributes SE_mc^2 = mean(var_t/20)/n
# (recompute cheaply on native only, both benchmarks)
def mc_noise_lme(nsamp=120):
    sv = []
    for qid in qids[:nsamp]:
        e = L[qid]; d = np.count_nonzero(e['D0'] != e['Q0'][None, :], axis=1)
        gg = set(map(int, e['g']))
        tv = np.array([len(set(map(int, np.lexsort((p, d))[:K])) & gg)/len(gg) for p in e['pr']])
        sv.append(tv.var(ddof=1)/NT)
    return float(np.mean(sv))
mcv = mc_noise_lme()
print(f'MC-noise var-per-q-mean/NT (LME native, n=120): {mcv:.6f}; sampling SE^2 scale ~ {(lme_res["NATIVE"]["mc"].var(ddof=1))/470:.6f}', flush=True)

details = {
  'labels': ['[LOCAL EXPLORATORY]', '[NOT PREREGISTERED]', '[NOT FOR CITATION]'],
  'protocol': 'K=3, NT=20 frozen tie priorities; LME lex over 500 qids, LoCoMo seed per conv ci; arms gold-free; RAND s0-2=rng(12000+s) global; SPREAD=rank-linspace; BOT/TOP per-archive variance tails',
  'anchors': {'LME_native': LME_NATIVE_ANCHOR, 'LoCoMo_native': LOCO_NATIVE_ANCHOR, 'LME_float96': LME_FLOAT96},
  'bootstrap': {'B': B, 'seed': BOOTSEED, 'unit': 'question (paired differences), iid/exchangeable questions',
                'per_comparison_level': 'one-sided 95%', 'family': f'Bonferroni M={M} (3 rungs x 2 bench x 3 fams), one-sided {100*(1-0.05/M):.3f}% LB'},
  'gates': 'all asserts passed (LME native+RAND48/64/80+RANKSTRIDE48+IDXSTRIDE48+TOP48+BOT48; LoCoMo native+RAND48/64/80 s0; validity counts 470/1535)',
  'mc_noise': {'LME_native_mean_vart_over_NT': mcv},
  'cert': cert,
  'per_question': {},
}
for bench, res, ids in (('LME', lme_res, qids), ('LoCoMo', loco_res, valid)):
    keep = ['NATIVE'] + [f'{f}{k}' for k in RUNGS for f in FAMS]
    details['per_question'][bench] = {
        'qids': ids,
        'arms': {a: {'mc': [float(x) for x in res[a]['mc']], 'ex': [float(x) for x in res[a]['ex']]} for a in keep}}
OUT.joinpath('cert_details.json').write_text(json.dumps(details), encoding='utf-8')
print('wrote cert_details.json', flush=True)
for key in sorted(cert):
    r = cert[key]
    print(f'{key}: mean={r["arm_mean"]:.4f} gap={r["gap_pp"]:+.2f}pp LB95={r["lb95_pp"]:+.2f} eps_pc={r["eps_pc_pp"]:.2f} eps_fwer={r["eps_fwer_pp"]:.2f} exact_gap={r["gap_exact_pp"]:+.2f}', flush=True)
print(f'CERT_COMPUTE_DONE ({time.time()-t0:.0f}s)', flush=True)
