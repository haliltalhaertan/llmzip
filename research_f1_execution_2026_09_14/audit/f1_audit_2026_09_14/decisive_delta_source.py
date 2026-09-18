#!/usr/bin/env python3
"""DECISIVE TEST (audit step 2 diagnosis).

Hypothesis H: the auditor's published 1e-12 targets are reproducible ONLY when Delta_q is taken
from the FROZEN committed per-query evaluation surface (as competition_variants.py does:
`delta = INDEPENDENT_QUERY_ROWS.json`), NOT when Delta_q is RECOMPUTED with an
exact-expectation FR@3 (what the coordinator and I both did).

Test: hold my competition code EXACTLY fixed; swap ONLY the Delta source.
  LME      frozen Delta <- docs/v52/task4c2/V52_T4C2_question_level.csv
                           column sign_minus_centered_float_fractional_pp
  REALTALK frozen Delta <- bench3/b3a_realtalk/details.json per_qa arms NATIVE96-FLOAT96

If rho then lands on the auditor target at ~1e-12, H is confirmed and the coordinator's
"reproduced all six" claim is wrong in kind (he matched 4-dp rounded display values).

I am NOT tuning to a target: I change the INPUT SOURCE to the contract-mandated one
("Use the exact per-query Delta_q values from the recovered/frozen evaluation surface"),
and report whatever comes out.
"""
import csv, io, json, subprocess, sys
import numpy as np
sys.path.insert(0, '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit')
from my_f1 import spearman, topbot64, competition, hamming, load_lme, load_realtalk

EV = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit/evidence'
# Frozen blobs exported verbatim from git (sha256 recorded in EVIDENCE_SHA.txt):
#   frozen_lme_question_level.csv  <- FROZ:docs/v52/task4c2/V52_T4C2_question_level.csv
#   frozen_rt_details.json         <- FROZ:campaign_2026_09_13/bench3/b3a_realtalk/details.json
FROZ = 'origin/research/e1-mechanism-checkpoint-frozen-2026-09-13'

def gitshow(ref, path):
    fn = {'docs/v52/task4c2/V52_T4C2_question_level.csv': EV + '/frozen_lme_question_level.csv',
          'campaign_2026_09_13/bench3/b3a_realtalk/details.json': EV + '/frozen_rt_details.json'}[path]
    return open(fn, 'r', encoding='utf-8', errors='replace').read()

AUD = {'LME': (0.14168629605302735, 0.14045379360271315),
       'REALTALK': (0.09793912889111700, 0.12281952421315011)}
MINE = {'LME': (0.1416251737011647, 0.14069387548880735),
        'REALTALK': (0.09793425648573494, 0.12307477776090332)}

def gaps_for(rows, dedupe_gold):
    """competition gaps only - no Delta involved. dedupe_gold toggles np.unique on gold
    (the auditor does np.unique; I did not) so I can price that difference too."""
    ac = {}
    res = {}
    for r in rows:
        C = r['C']
        k = id(C)
        if k not in ac:
            t, b, _ = topbot64(C); ac[k] = (C >= 0, t, b)
        D0, tc, bc = ac[k]
        Q0 = r['qC'] >= 0
        g = np.asarray(r['gold'], int)
        if dedupe_gold:
            g = np.unique(g)
        cp = competition(hamming(D0, Q0, tc).astype(np.int64),
                         hamming(D0, Q0, bc).astype(np.int64), g)
        res[r['qid']] = (cp['STRICT_GAP'], cp['TIE_GAP'])
    return res

out = {}

# ---------------- LME ----------------
lme, _ = load_lme()
txt = gitshow(FROZ, 'docs/v52/task4c2/V52_T4C2_question_level.csv')
frozen_delta = {}
for row in csv.DictReader(io.StringIO(txt)):
    frozen_delta[row['question_id']] = float(row['sign_minus_centered_float_fractional_pp'])
for dd in (False, True):
    gp = gaps_for(lme, dd)
    qids = [r['qid'] for r in lme if r['qid'] in frozen_delta and r['qid'] in gp]
    d = [frozen_delta[q] for q in qids]
    s = [gp[q][0] for q in qids]; t = [gp[q][1] for q in qids]
    rs, rt = spearman(d, s), spearman(d, t)
    tag = f'LME_frozenDelta_dedupe={dd}'
    out[tag] = dict(n=len(qids), strict=rs, tie=rt,
                    strict_minus_auditor=rs - AUD['LME'][0], tie_minus_auditor=rt - AUD['LME'][1],
                    hits_1e_12=bool(abs(rs - AUD['LME'][0]) <= 1e-12 and abs(rt - AUD['LME'][1]) <= 1e-12))
    print(f'{tag}: n={len(qids)} strict={rs!r} tie={rt!r}')
    print(f'   vs auditor: {rs-AUD["LME"][0]:+.3e} / {rt-AUD["LME"][1]:+.3e}  hits1e-12={out[tag]["hits_1e_12"]}', flush=True)

# ---------------- REALTALK ----------------
rt_rows, _ = load_realtalk()
dj = json.loads(gitshow(FROZ, 'campaign_2026_09_13/bench3/b3a_realtalk/details.json'))
fd = {}
for r in dj['per_qa']:
    if int(r['valid']) != 1:
        continue
    a = r['arms']
    if a.get('NATIVE96') is None or a.get('FLOAT96') is None:
        continue
    fd[str(r['qid'])] = 100.0 * (float(a['NATIVE96']) - float(a['FLOAT96']))
for dd in (False, True):
    gp = gaps_for(rt_rows, dd)
    qids = [r['qid'] for r in rt_rows if r['qid'] in fd and r['qid'] in gp]
    d = [fd[q] for q in qids]
    s = [gp[q][0] for q in qids]; t = [gp[q][1] for q in qids]
    rs, rt_ = spearman(d, s), spearman(d, t)
    tag = f'REALTALK_frozenDelta_dedupe={dd}'
    out[tag] = dict(n=len(qids), strict=rs, tie=rt_,
                    strict_minus_auditor=rs - AUD['REALTALK'][0], tie_minus_auditor=rt_ - AUD['REALTALK'][1],
                    hits_1e_12=bool(abs(rs - AUD['REALTALK'][0]) <= 1e-12 and abs(rt_ - AUD['REALTALK'][1]) <= 1e-12))
    print(f'{tag}: n={len(qids)} strict={rs!r} tie={rt_!r}')
    print(f'   vs auditor: {rs-AUD["REALTALK"][0]:+.3e} / {rt_-AUD["REALTALK"][1]:+.3e}  hits1e-12={out[tag]["hits_1e_12"]}', flush=True)

# ---------------- does v_j ever tie? (auditor argsort(v)[::-1] vs contract argsort(-v) stable) ----------------
tie_v = 0; tot = 0; difforder = 0
seen = set()
for r in lme + rt_rows:
    if id(r['C']) in seen:
        continue
    seen.add(id(r['C'])); tot += 1
    v = np.mean(np.asarray(r['C'], float) ** 2, axis=0)
    if len(np.unique(v)) < len(v):
        tie_v += 1
    a = np.argsort(v, kind='stable')[::-1]          # auditor
    b = np.argsort(-v, kind='stable')               # contract wording
    if not np.array_equal(np.sort(a[:64]), np.sort(b[:64])) or not np.array_equal(np.sort(a[-64:]), np.sort(b[-64:])):
        difforder += 1
out['axis_order_check'] = dict(archives=tot, archives_with_tied_v=tie_v,
                               archives_where_auditor_and_contract_arms_differ=difforder)
print('axis order check:', out['axis_order_check'])

# ---------------- duplicate gold rows? ----------------
dups = sum(1 for r in lme + rt_rows if len(np.unique(r['gold'])) != len(np.asarray(r['gold']).ravel()))
out['duplicate_gold_queries_lme_plus_rt'] = int(dups)
print('queries with duplicate gold indices (LME+RT):', dups)

json.dump(out, open('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit/evidence/decisive_delta_source.json', 'w'), indent=2)
print('OK')
