#!/usr/bin/env python3
"""Verify the weighting session's strongest claim, and fix my own subsampling flaw.

MY FLAW (disclosed): in clip_heldout.py I capped queries per archive at 120, so the
absolute FR@3 values there are NOT the frozen headlines (PerLTQA showed 0.692934
instead of 0.488945, LoCoMo 0.211889 instead of 0.237907). The PAIRED differences on
that subsample are internally valid, but the control was not reproduced. This script
runs the FULL query sets and reproduces the controls before anything else.

THE CLAIM I AM CHECKING (from the weighting brainstorm session, RELAYED):
"The 33 pp profile/events flip is reproduced by the one knob from shared documents:
profile rises +25 pp, events net -11 pp, middle sections flat."
This matters because the within-PerLTQA section split is EXACTLY what my whitening
mechanism could not explain. If one axis-weighting knob reproduces it from identical
documents, the mechanism gains the quantitative leg it was missing today.

Also checking their two stated caveats:
 (a) "full whitening beats sign everywhere, including PerLTQA";
 (b) "|Delta| shrinks from alpha 1->2 in all 8 rows -- the arms always converge",
     which would make the win partly degenerate.

Weighted cosine: score = sum_j w_j C_ij q_j / norms, with w_j = v_j^(-alpha),
v_j = mean_i(C_ij^2). alpha=0 is plain cosine; alpha=1 is full whitening.
"""
import glob, json, os, pickle
import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
OUT = os.path.dirname(os.path.abspath(__file__))
ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]


def fr_exact(S, G, gs, K=K):
    S = np.asarray(S, float)
    kk = min(K, S.shape[0])
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]
    b = S > thr[None, :]; e = S == thr[None, :]
    slots = np.maximum(kk - b.sum(0), 0); bc = e.sum(0)
    return ((G & b).sum(0) + np.where(bc > 0, (G & e).sum(0) * (slots / np.maximum(bc, 1)), 0.0)) / gs


def wcos(C, Q, w):
    Cw, Qw = C * w[None, :], Q * w[None, :]
    den = np.linalg.norm(Cw, axis=1)[:, None] * np.linalg.norm(Qw, axis=1)[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        o = (Cw @ Qw.T) / den
    return np.nan_to_num(o, nan=-2.0, posinf=-2.0, neginf=-2.0)


def sign_arm(C, Q):
    D0 = (C >= 0).astype(np.uint8); Q0 = (Q >= 0).astype(np.uint8)
    sD = D0.sum(1).astype(np.int32); sQ = Q0.sum(1).astype(np.int32)
    return -(sD[:, None] + sQ[None, :] - 2 * (D0.astype(np.int32) @ Q0.astype(np.int32).T))


# ---- PerLTQA with sections, FULL query set ----
A = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
Qd = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
by = {}
for q in Qd.values():
    by.setdefault(q['char'], []).append(q)

sec_acc = {}
glob_acc = {a: [] for a in ALPHAS}
glob_sign = []
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
    v = (C ** 2).mean(axis=0); v = np.where(v > 0, v, v[v > 0].min() if (v > 0).any() else 1.0)
    sg = fr_exact(sign_arm(C, Q), G, gs)
    glob_sign.append(sg)
    for a in ALPHAS:
        f = fr_exact(wcos(C, Q, v ** (-a / 2.0)), G, gs)
        glob_acc[a].append(f)
        for j, s in enumerate(secs):
            sec_acc.setdefault(s, {}).setdefault(a, []).append(f[j])
    for j, s in enumerate(secs):
        sec_acc.setdefault(s, {}).setdefault('sign', []).append(sg[j])

sign_all = np.concatenate(glob_sign)
print('=== CONTROL (FULL PerLTQA query set, must match frozen) ===')
c0 = np.concatenate(glob_acc[0.0])
print(f'  sign  = {sign_all.mean():.12f}   (frozen 0.488944994930817)')
print(f'  cosine= {c0.mean():.12f}   (frozen 0.551692074528853)')
print(f'  Delta = {100*(sign_all.mean()-c0.mean()):+.6f} pp   (frozen -6.274728)')
print(f'  n={len(sign_all)}  {"PASS" if abs(100*(sign_all.mean()-c0.mean())+6.274728) < 1e-3 else "FAIL"}')

print('\n=== THE CLAIM: does ONE axis-weighting knob reproduce the section flip? ===')
print('  Delta = weighted-cosine minus PLAIN cosine, per section, in pp')
print(f'  {"section":22s} ' + ' '.join(f'{"a="+str(a):>8s}' for a in ALPHAS))
order = sorted(sec_acc, key=lambda s: -(np.mean(sec_acc[s]['sign']) - np.mean(sec_acc[s][0.0])))
rows = {}
for s in order:
    base = np.mean(sec_acc[s][0.0])
    rows[s] = [100 * (np.mean(sec_acc[s][a]) - base) for a in ALPHAS]
    print(f'  {s:22s} ' + ' '.join(f'{x:>+8.2f}' for x in rows[s]))

print('\n  sign-minus-cosine per section (the flip to be explained):')
for s in order:
    d = 100 * (np.mean(sec_acc[s]['sign']) - np.mean(sec_acc[s][0.0]))
    print(f'  {s:22s} {d:>+8.3f} pp   n={len(sec_acc[s]["sign"])}')

print('\n  CHECK: does the alpha knob move profile UP and events DOWN (relative)?')
if 'profile' in rows and 'events' in rows:
    pa = rows['profile'][ALPHAS.index(1.0)]
    ev = rows['events'][ALPHAS.index(1.0)]
    print(f'    at alpha=1.0: profile {pa:+.2f} pp, events {ev:+.2f} pp, spread {pa-ev:+.2f} pp')
    pa2 = rows['profile'][ALPHAS.index(2.0)]
    ev2 = rows['events'][ALPHAS.index(2.0)]
    print(f'    at alpha=2.0: profile {pa2:+.2f} pp, events {ev2:+.2f} pp, spread {pa2-ev2:+.2f} pp')
    print(f'    the SIGN arm spread between these sections is '
          f'{100*(np.mean(sec_acc["profile"]["sign"])-np.mean(sec_acc["profile"][0.0])) - 100*(np.mean(sec_acc["events"]["sign"])-np.mean(sec_acc["events"][0.0])):+.2f} pp')

print('\n=== CAVEAT CHECK (b): do the arms converge as alpha grows? ===')
print('  |weighted-cosine minus sign| per section; if it shrinks to ~0 the win is degenerate')
print(f'  {"section":22s} ' + ' '.join(f'{"a="+str(a):>8s}' for a in ALPHAS))
for s in order:
    sgn = np.mean(sec_acc[s]['sign'])
    print(f'  {s:22s} ' + ' '.join(
        f'{100*(np.mean(sec_acc[s][a])-sgn):>+8.2f}' for a in ALPHAS))
print('  positive = weighted cosine beats the 12-byte sign arm at that alpha')

json.dump({'sections': {s: {str(a): float(np.mean(sec_acc[s][a])) for a in ALPHAS}
                        for s in sec_acc},
           'section_sign': {s: float(np.mean(sec_acc[s]['sign'])) for s in sec_acc}},
          open(os.path.join(OUT, 'alpha_sections.json'), 'w'), indent=1)
print('\nWROTE alpha_sections.json')
