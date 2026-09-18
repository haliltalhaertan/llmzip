#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 5: MANDATORY cross-benchmark test of the FROZEN rule R (PREDICTION.md).
R: stratum mean ALIGN < 0.4530  =>  predict Delta > 0 ; else Delta < 0.
ALIGN(q) = cos(qC^2, v), v_j = mean_i(C_ij^2).
Nothing here may alter PREDICTION.md.
"""
import json, pickle, glob, os
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
K = 3
THETA = 0.4530

def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    rx = rankdata(x); ry = rankdata(y); rx = rx - rx.mean(); ry = ry - ry.mean()
    return float((rx @ ry) / np.sqrt((rx @ rx) * (ry @ ry)))

def fr_exact(s, gold, K=3):
    s = np.asarray(s, float); ss = np.sort(s)[::-1]; thr = ss[K - 1]
    strictly = int(np.count_nonzero(s > thr)); slots = K - strictly
    bc = int(np.count_nonzero(s == thr))
    g = np.asarray(gold).ravel().astype(int)
    sg = s[g]
    return (int(np.count_nonzero(sg > thr)) + int(np.count_nonzero(sg == thr)) * slots / bc) / len(g)

def score_one(C, qC, gold):
    C = np.asarray(C, float); qC = np.asarray(qC, float).ravel()
    d = np.count_nonzero((C >= 0) != (qC >= 0)[None, :], axis=1)
    nrm = np.linalg.norm(C, axis=1)
    cosv = (C @ qC) / (nrm * np.linalg.norm(qC))
    v = (C ** 2).mean(axis=0); w = qC ** 2
    align = float((w @ v) / (np.linalg.norm(w) * np.linalg.norm(v)))
    return (fr_exact(-d.astype(float), gold, K), fr_exact(cosv, gold, K), align,
            float(np.linalg.norm(qC)), float(w.sum() ** 2 / (w ** 2).sum()))

REP = {}

# ---------------------------------------------------------------- LongMemEval
lme = []
for f in sorted(glob.glob(str(ROOT / 'regen/lme/cache_repr/*.pkl'))):
    d = pickle.load(open(f, 'rb'))
    s, fl, al, qn, pr = score_one(d['C'], d['qC'], d['gold'])
    lme.append(dict(qid=d['question_id'], sign=s, float=fl, delta=s - fl, align=al, qnorm=qn, qPR=pr,
                    N=int(np.asarray(d['C']).shape[0]), gold_n=int(len(np.asarray(d['gold']).ravel()))))
S = float(np.mean([r['sign'] for r in lme])); F = float(np.mean([r['float'] for r in lme]))
print(f'LME GATE n={len(lme)} SIGN {S!r} (frozen 0.5419751773049645)  float {F!r} (frozen 0.4415957446808511)')
print(f'   delta_pp {(S-F)*100:.6f}  (coordinator exact-expectation ref +10.053783)')
REP['lme_gate'] = dict(n=len(lme), sign=S, float=F, delta_pp=(S - F) * 100)

# ---------------------------------------------------------------- REALTALK
rt = []
for f in sorted(glob.glob(str(ROOT / 'bench3/runs/b3a_realtalk/rt_repr/RT*.pkl'))):
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
    for i, qid in enumerate(d['qids']):
        g = np.asarray(d['gold_rows'][i]).ravel().astype(int)
        if len(g) == 0: continue
        s, fl, al, qn, pr = score_one(C, QC[i], g)
        rt.append(dict(qid=str(qid), chat=str(d.get('chat_no', os.path.basename(f))), sign=s, float=fl,
                       delta=s - fl, align=al, qnorm=qn, qPR=pr, N=C.shape[0], gold_n=int(len(g))))
S = float(np.mean([r['sign'] for r in rt])); F = float(np.mean([r['float'] for r in rt]))
print(f'RT  GATE n={len(rt)} SIGN {S!r} (frozen 0.22477507598784194)  float {F!r} (frozen 0.17253405381064954)')
print(f'   delta_pp {(S-F)*100:.6f}  (frozen +5.2241 / coordinator exact +5.300077)')
REP['rt_gate'] = dict(n=len(rt), sign=S, float=F, delta_pp=(S - F) * 100)

# ---------------------------------------------------------------- LoCoMo
lc = []
lc_note = ''
try:
    for f in sorted(glob.glob(str(ROOT / 'regen/locomo/locomo_*.pkl'))):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
        idm = d.get('id_to_row', {})
        for i, qa in enumerate(d['qas']):
            ev = qa.get('evidence') or qa.get('gold') or qa.get('evidence_ids') or []
            rowsg = [idm[e] for e in ev if e in idm] if isinstance(ev, (list, tuple)) else []
            if not rowsg: continue
            s, fl, al, qn, pr = score_one(C, QC[i], np.array(sorted(set(rowsg)), int))
            lc.append(dict(conv=str(d['conv_id']), sign=s, float=fl, delta=s - fl, align=al,
                           qnorm=qn, qPR=pr, N=C.shape[0], gold_n=len(set(rowsg))))
    if lc:
        S = float(np.mean([r['sign'] for r in lc])); F = float(np.mean([r['float'] for r in lc]))
        print(f'LOC GATE n={len(lc)} SIGN {S!r} (frozen 0.23654714666441054) float {F!r} (frozen cand 0.16826334541318252) delta_pp {(S-F)*100:.6f}')
        REP['locomo_gate'] = dict(n=len(lc), sign=S, float=F, delta_pp=(S - F) * 100)
    else:
        lc_note = 'no gold rows resolvable from committed caches'
except Exception as e:
    lc_note = f'exception: {type(e).__name__}: {e}'
if lc_note: print('LOC: UNTESTABLE —', lc_note)
REP['locomo_note'] = lc_note

# ---------------------------------------------------------------- THE TEST
def strat_report(name, rowsl, keyfn=None, nq=10):
    al = np.array([r['align'] for r in rowsl]); dl = np.array([r['delta'] for r in rowsl])
    print(f'\n===== {name}  n={len(rowsl)}  overall Delta {dl.mean()*100:+.4f} pp  mean ALIGN {al.mean():.4f}  med {np.median(al):.4f} =====')
    pred = '+' if al.mean() < THETA else '-'
    obs = '+' if dl.mean() > 0 else '-'
    print(f'  RULE R on whole benchmark: mean ALIGN {al.mean():.4f} vs THETA {THETA} -> predict Delta {pred};  OBSERVED {obs}   => {"PASS" if pred==obs else "FAIL"}')
    edges = np.percentile(al, np.arange(0, 101, 100 / nq))
    dec = []
    for i in range(nq):
        m = (al >= edges[i]) & ((al <= edges[i + 1]) if i == nq - 1 else (al < edges[i + 1]))
        if m.sum() == 0: continue
        dec.append(dict(i=i + 1, n=int(m.sum()), align=float(al[m].mean()), delta_pp=float(dl[m].mean() * 100)))
    print(f'  {"dec":>4s}{"n":>7s}{"meanALIGN":>11s}{"Delta_pp":>11s}{"R pred":>8s}{"obs":>5s}{"ok":>4s}')
    ok = 0
    for d in dec:
        p = '+' if d['align'] < THETA else '-'; o = '+' if d['delta_pp'] > 0 else '-'
        ok += (p == o)
        print(f'  {d["i"]:>4d}{d["n"]:>7d}{d["align"]:>11.4f}{d["delta_pp"]:>11.4f}{p:>8s}{o:>5s}{"Y" if p==o else "N":>4s}')
    npos = sum(d['delta_pp'] > 0 for d in dec)
    maj = max(npos, len(dec) - npos)
    rho = spearman([d['align'] for d in dec], [d['delta_pp'] for d in dec])
    rho_q = spearman(al, dl)
    print(f'  P4 Spearman(decile ALIGN, decile Delta) = {rho:+.5f}   (R requires < 0 => {"PASS" if rho<0 else "FAIL"})')
    print(f'  P5 decile accuracy {ok}/{len(dec)} = {ok/len(dec):.3f}  vs majority baseline {maj}/{len(dec)} = {maj/len(dec):.3f}'
          f'  => {"BEATS" if ok>maj else "DOES NOT BEAT"} baseline')
    print(f'  per-query rho(Delta, ALIGN) = {rho_q:+.5f}   per-query rho(Delta, qnorm) = {spearman([r["qnorm"] for r in rowsl], dl):+.5f}')
    return dict(n=len(rowsl), mean_align=float(al.mean()), delta_pp=float(dl.mean() * 100),
                rule_pred=pred, observed=obs, whole_pass=bool(pred == obs), deciles=dec,
                p4_rho=rho, p5_acc=ok / len(dec), p5_majority=maj / len(dec),
                p5_beats=bool(ok > maj), rho_query_align=rho_q,
                rho_query_qnorm=spearman([r['qnorm'] for r in rowsl], dl))

REP['LME'] = strat_report('LongMemEval', lme)
REP['REALTALK'] = strat_report('REALTALK', rt)
if lc: REP['LoCoMo'] = strat_report('LoCoMo', lc)

# P6 REALTALK per-chat
print('\n===== P6 REALTALK per-chat strata =====')
ch = defaultdict(list)
for r in rt: ch[r['chat']].append(r)
cr = []
for c, rs in sorted(ch.items()):
    a = float(np.mean([r['align'] for r in rs])); d = float(np.mean([r['delta'] for r in rs]) * 100)
    p = '+' if a < THETA else '-'; o = '+' if d > 0 else '-'
    cr.append(dict(chat=c, n=len(rs), align=a, delta_pp=d, pred=p, obs=o, ok=bool(p == o)))
    print(f'  {c:>24s} n={len(rs):>4d} ALIGN {a:.4f} Delta {d:+8.3f} pred {p} obs {o} {"Y" if p==o else "N"}')
rho6 = spearman([x['align'] for x in cr], [x['delta_pp'] for x in cr])
nok = sum(x['ok'] for x in cr); npos = sum(x['delta_pp'] > 0 for x in cr)
print(f'  P6 Spearman = {rho6:+.5f} (R requires < 0 => {"PASS" if rho6<0 else "FAIL"});  acc {nok}/{len(cr)} vs majority {max(npos,len(cr)-npos)}/{len(cr)}')
REP['P6_realtalk_chats'] = dict(rows=cr, rho=rho6, acc=nok / len(cr), majority=max(npos, len(cr) - npos) / len(cr))

# PerLTQA section check (in-sample, for the record)
plr = pickle.load(open(OUT / 'evidence' / 'perltqa_levels_rows.pkl', 'rb'))
QD = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
arch = pickle.load(open(ROOT / 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
VV = {c: (np.asarray(a['C'], float) ** 2).mean(axis=0) for c, a in arch.items()}
for qid, q in QD.items():
    v = VV[q['char']]; w = np.asarray(q['qC'], float) ** 2
    plr[qid]['align'] = float((w @ v) / (np.linalg.norm(w) * np.linalg.norm(v)))
sm = defaultdict(list)
for r in plr.values(): sm[r['section']].append(r)
print('\n===== PerLTQA sections (IN-SAMPLE, not evidence) =====')
pl = []
for s in sorted(sm):
    a = float(np.mean([r['align'] for r in sm[s]])); d = float(np.mean([r['delta'] for r in sm[s]]) * 100)
    p = '+' if a < THETA else '-'; o = '+' if d > 0 else '-'
    pl.append(dict(section=s, n=len(sm[s]), align=a, delta_pp=d, pred=p, obs=o, ok=bool(p == o)))
    print(f'  {s:22s} n={len(sm[s]):>5d} ALIGN {a:.4f} Delta {d:+8.3f} pred {p} obs {o} {"Y" if p==o else "N"}')
REP['perltqa_sections_insample'] = pl
REP['per_query_rho_perltqa_align'] = spearman([r['align'] for r in plr.values()], [r['delta'] for r in plr.values()])
print(f'  PerLTQA per-query rho(Delta, ALIGN) = {REP["per_query_rho_perltqa_align"]:+.5f}')
pickle.dump(plr, open(OUT / 'evidence' / 'perltqa_levels_rows.pkl', 'wb'))
json.dump(REP, open(OUT / 'evidence' / 'results.json', 'w'), indent=2, default=float)
print('\nwrote evidence/results.json')
