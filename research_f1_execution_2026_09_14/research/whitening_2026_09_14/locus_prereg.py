#!/usr/bin/env python3
"""PREREGISTERED TEST, specified by an independent brainstorm session before seeing
the answer. Its NEXT_BRIEF.md states the kill criterion verbatim:

  "restrict both arms to top-16-only vs bot-16-only axes per archive, compare
   Delta(band) across the 4 benchmarks and 4 PerLTQA sections. Preregistered kill:
   if Delta(bot16) <= Delta(top16) on LME or profile, the locus hypothesis is dead."

LOCUS HYPOTHESIS: the sign arm wins when the query-relevant signal sits in
LOW-variance axes (where cosine's magnitude weighting under-serves it) and loses when
the signal sits in high-variance axes. If so, restricting both arms to the bottom band
should favour sign MORE than restricting them to the top band.

Delta(band) = FR@3(sign on band) - FR@3(cosine on SAME band). Both arms restricted
identically, so the contrast isolates where the signal lives, not dimensionality.

I did not write this test and did not choose its kill criterion. The 4 benchmark rows
come from a sweep I ran BEFORE this brief existed (evidence/axis_budget_results.json,
which already stored sign_bot/float_bot at m=16); the section rows are computed here.
"""
import json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))
SWEEP = '/mnt/c/Users/MDP/dev/llmzip-work/agent_out/axis-budget/evidence/axis_budget_results.json'


def fr_exact(S, G, gs, K=K):
    S = np.asarray(S, float)
    kk = min(K, S.shape[0])
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    b = S > thr[None, :]; e = S == thr[None, :]
    slots = np.maximum(kk - b.sum(0), 0); bc = e.sum(0)
    return ((G & b).sum(0) + np.where(bc > 0, (G & e).sum(0) * (slots / np.maximum(bc, 1)), 0.0)) / gs


def cos_b(C, Q):
    den = np.linalg.norm(C, axis=1)[:, None] * np.linalg.norm(Q, axis=1)[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        o = (C @ Q.T) / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def ham_b(C, Q):
    D0 = (C >= 0).astype(np.uint8); Q0 = (Q >= 0).astype(np.uint8)
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    return -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))


# ---------- part 1: the four benchmarks, from the pre-existing sweep ----------
S = json.load(open(SWEEP))
print('=== PREREGISTERED TEST, four benchmarks (m=16 band) ===')
print('  Delta(band) = FR@3(sign on band) - FR@3(cosine on same band), pp')
print(f'  {"bench":9s} {"Delta(top16)":>13s} {"Delta(bot16)":>13s} {"bot-top":>9s} {"locus?":>8s}')
part1 = {}
for b in ['LME', 'LoCoMo', 'REALTALK', 'PerLTQA']:
    r = S[b]['budgets']['16']
    dt = 100 * (r['sign_top']['mean'] - r['float_top']['mean'])
    db = 100 * (r['sign_bot']['mean'] - r['float_bot']['mean'])
    ok = 'SUPPORTS' if db > dt else 'KILLS'
    part1[b] = {'top': dt, 'bot': db}
    print(f'  {b:9s} {dt:>+13.4f} {db:>+13.4f} {db-dt:>+9.4f} {ok:>8s}')

# ---------- part 2: the four PerLTQA sections, computed fresh ----------
A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
by = {}
for q in Qd.values():
    by.setdefault(q['char'], []).append(q)

sec = {}
ctrl_s, ctrl_f = [], []
for ch, items in by.items():
    keep = [q for q in items if len(np.asarray(q['gold']).ravel())]
    if not keep:
        continue
    C = np.asarray(A[ch]['C'], float)
    Q = np.stack([np.asarray(q['qC'], float) for q in keep])
    secs = [q.get('section', '') for q in keep]
    golds = [np.asarray(q['gold']).ravel().astype(int) for q in keep]
    N, nq = C.shape[0], Q.shape[0]
    gs = np.array([len(g) for g in golds], float)
    G = np.zeros((N, nq), bool)
    for j, g in enumerate(golds):
        G[g, j] = True
    order = np.argsort(-(C ** 2).mean(axis=0), kind='stable')
    top, bot = order[:16], order[-16:]
    vals = {
        'sign_top': fr_exact(ham_b(C[:, top], Q[:, top]), G, gs),
        'float_top': fr_exact(cos_b(C[:, top], Q[:, top]), G, gs),
        'sign_bot': fr_exact(ham_b(C[:, bot], Q[:, bot]), G, gs),
        'float_bot': fr_exact(cos_b(C[:, bot], Q[:, bot]), G, gs),
    }
    ctrl_s.append(fr_exact(ham_b(C, Q), G, gs))
    ctrl_f.append(fr_exact(cos_b(C, Q), G, gs))
    for j, s in enumerate(secs):
        d = sec.setdefault(s, {k: [] for k in vals})
        for k in vals:
            d[k].append(vals[k][j])

cs, cf = np.concatenate(ctrl_s), np.concatenate(ctrl_f)
print(f'\n  CONTROL (full 96 axes, PerLTQA): Delta={100*(cs.mean()-cf.mean()):+.6f} pp '
      f'(frozen -6.274728)  {"PASS" if abs(100*(cs.mean()-cf.mean())+6.274728)<1e-3 else "FAIL"}')

print('\n=== PREREGISTERED TEST, four PerLTQA sections (same documents) ===')
print(f'  {"section":22s} {"Delta(top16)":>13s} {"Delta(bot16)":>13s} {"bot-top":>9s} '
      f'{"full-96 Delta":>14s} {"locus?":>8s}')
full = {'profile': 20.355, 'social_relationship': -0.780,
        'dialogues': -1.502, 'events': -12.394}
part2 = {}
for s in sorted(sec, key=lambda x: -full.get(x, 0)):
    d = sec[s]
    dt = 100 * (np.mean(d['sign_top']) - np.mean(d['float_top']))
    db = 100 * (np.mean(d['sign_bot']) - np.mean(d['float_bot']))
    ok = 'SUPPORTS' if db > dt else 'KILLS'
    part2[s] = {'top': dt, 'bot': db, 'n': len(d['sign_top'])}
    print(f'  {s:22s} {dt:>+13.4f} {db:>+13.4f} {db-dt:>+9.4f} '
          f'{full.get(s, float("nan")):>+14.3f} {ok:>8s}')

print('\n=== VERDICT against the preregistered kill criterion ===')
lme_kill = part1['LME']['bot'] <= part1['LME']['top']
pro_kill = part2.get('profile', {}).get('bot', 0) <= part2.get('profile', {}).get('top', 0)
print(f'  criterion: Delta(bot16) <= Delta(top16) on LME  -> {"KILL" if lme_kill else "survives"}')
print(f'  criterion: Delta(bot16) <= Delta(top16) on profile -> {"KILL" if pro_kill else "survives"}')
print(f'  LOCUS HYPOTHESIS: {"DEAD" if (lme_kill or pro_kill) else "SURVIVES this test"}')

print('\n  Does the band contrast track the full-96 Delta ordering across sections?')
xs = [part2[s]['bot'] - part2[s]['top'] for s in part2 if s in full]
ys = [full[s] for s in part2 if s in full]
if len(xs) > 2:
    print(f'    r(bot-top band gap, full Delta) = {np.corrcoef(xs, ys)[0,1]:+.4f}  (n={len(xs)})')

json.dump({'benchmarks': part1, 'sections': part2},
          open(os.path.join(OUT, 'locus_prereg.json'), 'w'), indent=1)
print('\nWROTE locus_prereg.json')
