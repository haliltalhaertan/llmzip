#!/usr/bin/env python3
"""MANDATORY ADVERSARIAL SELF-CHECK.

The assumption that would most damage MY conclusion:
  I concluded "the corrected per-gold metric is sound because two independent implementations agree
  bit-for-bit." But my implementation and his could agree because we made the SAME mistake --
  we both read the same contract text, and a shared misreading would produce shared agreement.
  Agreement is only evidence of correctness if the implementations are genuinely independent
  AND a third, differently-structured oracle agrees.

Test: build a THIRD implementation that is deliberately structured differently from both --
  a naive O(G*N) double loop in pure Python with no vectorisation, no shared helper, written
  straight from the contract sentence -- and ALSO reproduce the AUDITOR's own competition_variants.py
  metric function verbatim (it is committed and readable). If all three agree, shared-misreading
  is ruled out. If the auditor's function disagrees, my agreement with the coordinator is the
  shared-misreading scenario and my PASS-leaning conclusion collapses.
"""
import json, sys
import numpy as np
sys.path.insert(0, '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit')
from my_f1 import load_lme, load_realtalk, topbot64, hamming, cos_scores, spearman, competition
OUT = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit'

def efr_exact(s, gold, K=3):
    s = np.asarray(s, float); ss = np.sort(s)[::-1]; thr = ss[K-1]
    st = int((s > thr).sum()); slots = K - st; bc = int((s == thr).sum())
    gs = sum(1 for x in gold if s[x] > thr); gt = sum(1 for x in gold if s[x] == thr)
    return (gs + gt * (slots / bc)) / len(gold)

# ---- Implementation C: naive pure-Python triple loop, written from the contract sentence ----
def naive_gaps(dT, dB, gold):
    dT = [int(x) for x in dT]; dB = [int(x) for x in dB]; G = [int(g) for g in gold]
    def arm(d):
        tot_s = 0; tot_t = 0
        for g in G:
            dg = d[g]; s = 0; t = 0
            for i in range(len(d)):
                if d[i] < dg: s += 1
                if d[i] == dg: t += 1
            tot_s += s; tot_t += t
        return tot_s / len(G), tot_t / len(G)
    sT, tT = arm(dT); sB, tB = arm(dB)
    return sT - sB, tT - tB

# ---- Implementation D: the AUDITOR's own metrics(), transcribed verbatim from
#      origin/audit/...:competition_variants.py (pg_all_strict / pg_all_tie) ----
def auditor_metrics(d, gold):
    gold = np.unique(np.asarray(gold, int)); n = len(d)
    non = np.ones(n, bool); non[gold] = False
    as_ = []; at = []
    for g in gold:
        dg = d[g]
        as_.append(np.count_nonzero(d < dg)); at.append(np.count_nonzero(d == dg))
    return float(np.mean(as_)), float(np.mean(at))

def auditor_gaps(dT, dB, gold):
    aS, aT = auditor_metrics(dT, gold); bS, bT = auditor_metrics(dB, gold)
    return aS - bS, aT - bT

res = {}
for bench, loader, lim in (('LME', load_lme, None), ('REALTALK', load_realtalk, 300)):
    rows, _ = loader()
    if lim: rows = rows[:lim]
    ac = {}
    dl = []; mine_s = []; mine_t = []; nai_s = []; nai_t = []; aud_s = []; aud_t = []
    for r in rows:
        C = r['C']; q = r['qC']; k = id(C)
        if k not in ac:
            t, b, _ = topbot64(C); ac[k] = (C >= 0, t, b)
        D0, tc, bc = ac[k]
        Q0 = q >= 0
        dT = hamming(D0, Q0, tc).astype(np.int64); dB = hamming(D0, Q0, bc).astype(np.int64)
        dh = hamming(D0, Q0).astype(float); cs = cos_scores(C, q)
        dl.append(efr_exact(-dh, r['gold']) - efr_exact(cs, r['gold']))
        cp = competition(dT, dB, r['gold']); mine_s.append(cp['STRICT_GAP']); mine_t.append(cp['TIE_GAP'])
        a, b2 = naive_gaps(dT, dB, r['gold']); nai_s.append(a); nai_t.append(b2)
        a, b2 = auditor_gaps(dT, dB, r['gold']); aud_s.append(a); aud_t.append(b2)
    rm = (spearman(dl, mine_s), spearman(dl, mine_t))
    rn = (spearman(dl, nai_s), spearman(dl, nai_t))
    ra = (spearman(dl, aud_s), spearman(dl, aud_t))
    row_mismatch_naive = sum(1 for x, y in zip(mine_s, nai_s) if x != y)
    row_mismatch_aud = sum(1 for x, y in zip(mine_s, aud_s) if x != y)
    res[bench] = dict(n=len(rows), mine=rm, naive_pure_python=rn, auditor_verbatim_metrics=ra,
                      per_row_mismatch_vs_naive=row_mismatch_naive,
                      per_row_mismatch_vs_auditor=row_mismatch_aud,
                      all_three_agree=bool(abs(rm[0]-rn[0])<1e-12 and abs(rm[0]-ra[0])<1e-12
                                           and abs(rm[1]-rn[1])<1e-12 and abs(rm[1]-ra[1])<1e-12))
    print(f'{bench} n={len(rows)}')
    print(f'  mine (numpy vectorised)      strict={rm[0]!r} tie={rm[1]!r}')
    print(f'  naive pure-python triple loop strict={rn[0]!r} tie={rn[1]!r}')
    print(f'  AUDITOR metrics() verbatim    strict={ra[0]!r} tie={ra[1]!r}')
    print(f'  per-row gap mismatches: vs naive={row_mismatch_naive}  vs auditor={row_mismatch_aud}')
    print(f'  ALL THREE AGREE AT 1e-12: {res[bench]["all_three_agree"]}\n', flush=True)

json.dump(res, open(OUT + '/evidence/selfcheck_three_implementations.json', 'w'), indent=2, default=str)
print('OK')
