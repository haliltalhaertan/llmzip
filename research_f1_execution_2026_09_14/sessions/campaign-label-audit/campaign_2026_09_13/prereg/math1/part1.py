#!/usr/bin/env python3
"""MATH-1: analytic model of top-3 sign-code retrieval + validation on frozen LME-470 data.
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]
Read-only /mnt/c; writes only /tmp/math1/.
"""
import json, pickle, glob, time, math
import numpy as np
from pathlib import Path

BUNDLE = Path('/mnt/c/Users/MDP/dev/llmzip-work/review_transfer/EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13')
PIL = BUNDLE/'pilots/axis_attack_2026-09-12'
PKLDIR = Path('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr')
OUT = Path('/tmp/math1')
K, NT = 3, 20
NATIVE_ANCHOR = 0.5419751773049645

def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100

# ---------- LEVEL-1 EXACT MODEL ----------
def exact_frac_r3(d, gold, k=K):
    """Exact E[fractional R@k] under conditional-uniform tie resolution.
    d: int array (n,); gold: int array of row indices.
    Per-gold inclusion P = 0 if S>=k; 1 if S+T<=k; else (k-S)/T,
    S=#{d_i<d_g}, T=#{d_i==d_g}; mean over golds (linearity of expectation)."""
    d = np.asarray(d); g = np.asarray(g).ravel()
    tot = 0.0
    for gg in g:
        dg = d[int(gg)]
        S = int(np.count_nonzero(d < dg)); T = int(np.count_nonzero(d == dg))
        if S >= k: p = 0.0
        elif S + T <= k: p = 1.0
        else: p = (k - S) / T
        tot += p
    return tot / len(g)

def measured_frac_r3(d, gold, pr, k=K):
    """Frozen 20-trial scheme: lexsort((priority, distance)) top-k fractional recall."""
    d = np.asarray(d); g = np.asarray(g).ravel()
    gg = set(map(int, g)); trials = []
    for p in pr:
        order = np.lexsort((p, d))
        trials.append(len(set(map(int, order[:k])) & gg) / len(gg))
    return float(np.mean(trials)), trials

def tie_stats(d, gold):
    """Mean over golds of (S, T, d_g); plus non-gold histogram moments."""
    d = np.asarray(d); g = np.asarray(g).ravel()
    n = len(d); mask = np.zeros(n, bool); mask[g] = True
    ng = d[~mask]
    Ss, Ts, dgs = [], [], []
    for gg in g:
        dg = d[int(gg)]
        Ss.append(int(np.count_nonzero(d < dg))); Ts.append(int(np.count_nonzero(d == dg))); dgs.append(int(dg))
    return (float(np.mean(Ss)), float(np.mean(Ts)), float(np.mean(dgs)),
            float(ng.mean()) if len(ng) else float('nan'),
            float(ng.std()) if len(ng) else float('nan'), len(ng))
