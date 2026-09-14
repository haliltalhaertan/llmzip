#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT][NOT PREREGISTERED][NOT FOR CITATION][DISCLOSE-BEFORE-USE]
STEP 8: LoCoMo IS testable -- gold rows resolve via qas[i]['raw_evidence'] -> id_to_row.
(cross_check.py looked for 'evidence'/'gold' keys and found none; corrected here.)
Tests frozen rule R (P7) and the LEVELS relation on LoCoMo.
"""
import json, pickle, glob
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
OUT = Path('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/perltqa-levels')
K = 3; THETA = 0.4530

def spearman(x, y):
    rx = rankdata(x); ry = rankdata(y); rx = rx - rx.mean(); ry = ry - ry.mean()
    return float((rx @ ry) / np.sqrt((rx @ rx) * (ry @ ry)))

def fr_exact(s, gold, K=3):
    s = np.asarray(s, float); ss = np.sort(s)[::-1]; thr = ss[K - 1]
    st = int(np.count_nonzero(s > thr)); slots = K - st; bc = int(np.count_nonzero(s == thr))
    g = np.asarray(gold).ravel().astype(int); sg = s[g]
    return (int(np.count_nonzero(sg > thr)) + int(np.count_nonzero(sg == thr)) * slots / bc) / len(g)

rows = []
for f in sorted(glob.glob(str(ROOT / 'regen/locomo/locomo_*.pkl'))):
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float); idm = d['id_to_row']
    v = (C ** 2).mean(axis=0); o = np.argsort(-v, kind='stable')
    top = np.sort(o[:64]).astype(int); bot = np.sort(o[-64:]).astype(int)
    D0 = C >= 0; nrm = np.linalg.norm(C, axis=1); N = C.shape[0]
    for i, qa in enumerate(d['qas']):
        ev = qa.get('raw_evidence') or []
        g = sorted({idm[e] for e in ev if e in idm})
        if not g: continue
        g = np.array(g, int); qC = QC[i]; Q0 = qC >= 0
        d_f = np.count_nonzero(D0 != Q0[None, :], axis=1)
        d_t = np.count_nonzero(D0[:, top] != Q0[top][None, :], axis=1)
        d_b = np.count_nonzero(D0[:, bot] != Q0[bot][None, :], axis=1)
        cosv = (C @ qC) / (nrm * np.linalg.norm(qC))
        st_t = float(np.mean([np.count_nonzero(d_t < x) for x in d_t[g]]))
        st_b = float(np.mean([np.count_nonzero(d_b < x) for x in d_b[g]]))
        ti_t = float(np.mean([np.count_nonzero(d_t == x) for x in d_t[g]]))
        ti_b = float(np.mean([np.count_nonzero(d_b == x) for x in d_b[g]]))
        w = qC ** 2
        s_ = fr_exact(-d_f.astype(float), g, K); f_ = fr_exact(cosv, g, K)
        rows.append(dict(conv=str(d['conv_id']), sign=s_, float=f_, delta=s_ - f_,
                         align=float((w @ v) / (np.linalg.norm(w) * np.linalg.norm(v))),
                         STRICT_GAP=st_t - st_b, TIE_GAP=ti_t - ti_b,
                         strict_TOP64=st_t, strict_BOT64=st_b, N=N, gold_n=len(g),
                         qnorm=float(np.linalg.norm(qC))))
S = float(np.mean([r['sign'] for r in rows])); F = float(np.mean([r['float'] for r in rows]))
print(f'LoCoMo GATE n={len(rows)} SIGN {S!r} (frozen 0.23654714666441054)')
print(f'                       float {F!r} (frozen cand 0.16826334541318252)  delta_pp {(S-F)*100:+.6f} (frozen +6.82838013)')
al = np.array([r['align'] for r in rows]); dl = np.array([r['delta'] for r in rows])
pred = '+' if al.mean() < THETA else '-'; obs = '+' if dl.mean() > 0 else '-'
print(f'\nP7 RULE R whole-benchmark: mean ALIGN {al.mean():.4f} vs THETA {THETA} -> predict {pred}; OBSERVED {obs} => {"PASS" if pred==obs else "FAIL"}')
ed = np.percentile(al, np.arange(0, 101, 10)); ok = 0; dec = []
print(f'  {"dec":>4s}{"n":>7s}{"ALIGN":>10s}{"Delta_pp":>11s}{"pred":>6s}{"obs":>5s}')
for i in range(10):
    m = (al >= ed[i]) & ((al <= ed[i + 1]) if i == 9 else (al < ed[i + 1]))
    if m.sum() == 0: continue
    p = '+' if al[m].mean() < THETA else '-'; o = '+' if dl[m].mean() > 0 else '-'
    ok += (p == o); dec.append((float(al[m].mean()), float(dl[m].mean() * 100)))
    print(f'  {i+1:>4d}{int(m.sum()):>7d}{al[m].mean():>10.4f}{dl[m].mean()*100:>11.4f}{p:>6s}{o:>5s}')
rho4 = spearman([x[0] for x in dec], [x[1] for x in dec])
npos = sum(x[1] > 0 for x in dec); maj = max(npos, len(dec) - npos)
print(f'  P4/P7 Spearman(decile ALIGN, decile Delta) = {rho4:+.5f} (R requires <0 => {"PASS" if rho4<0 else "FAIL"})')
print(f'  decile accuracy {ok}/{len(dec)} vs majority {maj}/{len(dec)} => {"BEATS" if ok>maj else "DOES NOT BEAT"}')
print(f'\nLEVELS: mean STRICT_GAP {np.mean([r["STRICT_GAP"] for r in rows]):+.4f}  mean Delta_pp {dl.mean()*100:+.4f}'
      f'  => sign match {"PASS" if np.sign(np.mean([r["STRICT_GAP"] for r in rows]))==np.sign(dl.mean()) else "FAIL"}')
print(f'  rho(Delta,STRICT_GAP) {spearman([r["STRICT_GAP"] for r in rows], dl):+.5f} (R2 audit target 0.09491957131277647)')
print(f'  rho(Delta,TIE_GAP)    {spearman([r["TIE_GAP"] for r in rows], dl):+.5f} (R2 audit target 0.10376015063205302)')
print(f'  rho(Delta,strict_BOT64) {spearman([r["strict_BOT64"] for r in rows], dl):+.5f}')
print(f'  rho(Delta,align) {spearman(al, dl):+.5f}')
json.dump(dict(n=len(rows), sign=S, float=F, delta_pp=(S - F) * 100, mean_align=float(al.mean()),
               p7_pred=pred, p7_obs=obs, p7_pass=bool(pred == obs), p4_rho=rho4,
               dec_acc=ok / max(len(dec), 1), majority=maj / max(len(dec), 1),
               strict_gap=float(np.mean([r['STRICT_GAP'] for r in rows])),
               rho_strictgap=spearman([r['STRICT_GAP'] for r in rows], dl),
               rho_tiegap=spearman([r['TIE_GAP'] for r in rows], dl),
               rho_bot64=spearman([r['strict_BOT64'] for r in rows], dl),
               rho_align=spearman(al, dl)),
          open(OUT / 'evidence' / 'locomo.json', 'w'), indent=2)
print('\nwrote evidence/locomo.json')
