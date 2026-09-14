#!/usr/bin/env python3
"""
axis_budget_core.py -- shared loaders + exact FR@K expectation.
READ-ONLY on all llmzip-work caches. Additive output only.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""
import ast
import glob
import pickle

import numpy as np

R = '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3

# ---------------------------------------------------------------- metric
def fr_at_k_exact(S, Gmask, gold_size, K=K):
    """Exact expectation of FR@K under uniform random tie-breaking.

    S       : (N, nq) score matrix, HIGHER is better.
    Gmask   : (N, nq) bool, gold membership.
    gold_size: (nq,) int, |gold| per query.

    E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|
    where thr = K-th best score, strictly = #{> thr}, slots = K - strictly,
    bc = #{== thr}, g_strict/g_tied = golds strictly-better / tied-at thr.
    This is the order-independent expectation of the frozen NT=20 permutation
    estimator (no sampling noise).
    """
    S = np.asarray(S)
    N = S.shape[0]
    kk = min(K, N)
    # k-th largest per column
    thr = -np.partition(-S, kk - 1, axis=0)[kk - 1]          # (nq,)
    better = S > thr[None, :]
    equal = S == thr[None, :]
    strictly = better.sum(0)
    bc = equal.sum(0)
    slots = np.maximum(kk - strictly, 0)
    g_strict = (Gmask & better).sum(0)
    g_tied = (Gmask & equal).sum(0)
    with np.errstate(divide='ignore', invalid='ignore'):
        frac = np.where(bc > 0, g_tied * (slots / np.maximum(bc, 1)), 0.0)
    return (g_strict + frac) / gold_size


def hamming_batch(D0m, Q0m):
    """D0m (N,m) uint8 0/1, Q0m (nq,m) uint8 -> (N,nq) int hamming distance."""
    sD = D0m.sum(1).astype(np.int32)
    sQ = Q0m.sum(1).astype(np.int32)
    dot = D0m.astype(np.int32) @ Q0m.astype(np.int32).T
    return sD[:, None] + sQ[None, :] - 2 * dot


def cos_batch(Cm, Qm):
    """Cm (N,m), Qm (nq,m) -> (N,nq) cosine."""
    nC = np.linalg.norm(Cm, axis=1)
    nQ = np.linalg.norm(Qm, axis=1)
    denom = nC[:, None] * nQ[None, :]
    num = Cm @ Qm.T
    with np.errstate(divide='ignore', invalid='ignore'):
        out = num / denom
    return np.nan_to_num(out, nan=-2.0, posinf=-2.0, neginf=-2.0)


# ---------------------------------------------------------------- loaders
# Each loader yields "units": (C, QC, gold_lists, tags)
#   C          (N,96) float64, ALREADY CENTERED -- never re-center.
#   QC         (nq,96) float64
#   gold_lists list of nq arrays of row indices
#   tags       list of nq strings (section / category label, '' if none)

def load_lme():
    units = []
    for f in sorted(glob.glob(R + '/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float)
        qC = np.asarray(d['qC'], float)[None, :]
        g = np.asarray(d['gold']).ravel().astype(int)
        if len(g) == 0:
            continue
        units.append((C, qC, [g], ['']))
    return units


def load_realtalk():
    units = []
    for f in sorted(glob.glob(R + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float)
        QC = np.asarray(d['QC'], float)
        keep, golds, tags = [], [], []
        for i, g in enumerate(d['gold_rows']):
            gg = np.asarray(g).ravel().astype(int)
            if len(gg) == 0:
                continue
            keep.append(i)
            golds.append(gg)
            tags.append(str(d['cats'][i]) if 'cats' in d else '')
        if not keep:
            continue
        units.append((C, QC[keep], golds, tags))
    return units


def load_perltqa():
    arch = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Q = pickle.load(open(R + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by_char = {}
    for qid, q in Q.items():
        by_char.setdefault(q['char'], []).append(q)
    units = []
    for char in sorted(by_char):
        C = np.asarray(arch[char]['C'], float)
        qs = by_char[char]
        QC = np.stack([np.asarray(q['qC'], float) for q in qs])
        golds = [np.asarray(q['gold']).ravel().astype(int) for q in qs]
        tags = [q['section'] for q in qs]
        units.append((C, QC, golds, tags))
    return units


def load_locomo():
    units = []
    for f in sorted(glob.glob(R + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], float)
        QC = np.asarray(d['QC'], float)
        i2r = d['id_to_row']
        keep, golds, tags = [], [], []
        for i, qa in enumerate(d['qas']):
            ev = qa.get('raw_evidence')
            if ev is None:
                continue
            if isinstance(ev, str):
                try:
                    ev = ast.literal_eval(ev)
                except Exception:
                    ev = [ev]
            if isinstance(ev, str):
                ev = [ev]
            rows = sorted({i2r[e] for e in ev if e in i2r})
            if not rows:
                continue
            keep.append(i)
            golds.append(np.asarray(rows, int))
            tags.append(str(qa.get('category', '')))
        if not keep:
            continue
        units.append((C, QC[keep], golds, tags))
    return units


LOADERS = {'LME': load_lme, 'PerLTQA': load_perltqa,
           'REALTALK': load_realtalk, 'LoCoMo': load_locomo}
