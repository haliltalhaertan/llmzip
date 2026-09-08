"""Actual scoring port: historical aggregate Native gate is enforced by run.py.
Arithmetic, seeds, controls and tie rules inherited unchanged from integration v2.
"""
from pathlib import Path
import hashlib
import importlib.util

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from pinned import load_pinned
core = load_pinned('core')
contracts = load_pinned('contracts')
TOPK, N_NUISANCE = 3, 20


class PipelineError(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise PipelineError(code)


def text_list(value):
    require(type(value) is list and len(value) > 0, 'E-M-002: text list required')
    require(all(type(x) is str for x in value), 'E-M-003: text type')


class Representation:
    """Memory-only fitting; every query uses the same four fitted estimators."""
    def __init__(self, memory_texts):
        text_list(memory_texts)
        require(len(memory_texts) >= 96, 'E-M-004: insufficient rows for dimension 96')
        self.word = TfidfVectorizer(lowercase=True, ngram_range=(1, 2),
                                   stop_words='english', sublinear_tf=True)
        self.char = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
        # Do not retain a library exception containing input text in an exception chain.
        failed = False
        try:
            w = normalize(self.word.fit_transform(memory_texts))
            c = normalize(self.char.fit_transform(memory_texts))
            d = min(32, w.shape[0] - 1, w.shape[1] - 1)
            if d < 1:
                raise ValueError('insufficient features')
            self.lsa = TruncatedSVD(n_components=d, random_state=5101)
            latent = normalize(self.lsa.fit_transform(w))
            z = sparse.hstack([sparse.csr_matrix(latent), w, c], format='csr')
            self.svd = TruncatedSVD(n_components=96, random_state=5204)
            y = normalize(self.svd.fit_transform(z))
        except Exception:
            failed = True
        if failed:
            raise PipelineError('E-M-006: representation fit failed')
        require(y.shape == (len(memory_texts), 96) and np.isfinite(y).all(),
                'E-M-007: invalid representation')
        self.mu = y.mean(axis=0, keepdims=True)
        self.C = (y - self.mu).astype(np.float64)
        self.D, self.diagnostics = core.scale_matrix(self.C)

    def queries(self, texts):
        text_list(texts)
        failed = False
        try:
            w = normalize(self.word.transform(texts))
            c = normalize(self.char.transform(texts))
            latent = normalize(self.lsa.transform(w))
            z = sparse.hstack([sparse.csr_matrix(latent), w, c], format='csr')
            q = (normalize(self.svd.transform(z)) - self.mu).astype(np.float64)
        except Exception:
            failed = True
        if failed:
            raise PipelineError('E-M-008: query transform failed')
        require(q.shape == (len(texts), 96) and np.isfinite(q).all(), 'E-M-009: invalid query')
        return q


def stable_archive_seed(ordinal, trial=0):
    require(type(ordinal) is int and ordinal >= 0, 'E-M-010: archive ordinal')
    require(type(trial) is int and 0 <= trial < N_NUISANCE, 'E-M-011: nuisance trial')
    return 5100000 + ordinal * 100000 + trial * 100


def topks_by_hamming(dist, priorities, k=TOPK):
    """Arithmetic port of pinned source a6ecee02; outputs selection sets, not sorted ranks."""
    dist, P = np.asarray(dist), np.asarray(priorities, dtype=float)
    require(dist.ndim == 1 and len(dist) > 0 and np.isfinite(dist).all(), 'E-M-012: distance')
    require(P.ndim == 2 and P.shape[1] == len(dist) and np.isfinite(P).all(), 'E-M-013: priority')
    require(type(k) is int and k > 0, 'E-M-014: topk')
    if len(dist) <= k:
        return [np.lexsort((p, dist))[:k] for p in P]
    kth = np.partition(dist, k - 1)[k - 1]
    strict, boundary = np.flatnonzero(dist < kth), np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need == len(boundary):
        picks = np.tile(boundary, (len(P), 1))
    else:
        picks = boundary[np.argpartition(P[:, boundary], need - 1, axis=1)[:, :need]]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]


def validate_gold(gold, n):
    require(type(gold) is list and len(gold) > 0, 'E-M-015: empty or invalid gold')
    require(all(type(i) is int and 0 <= i < n for i in gold), 'E-M-016: gold row')
    require(len(set(gold)) == len(gold), 'E-M-017: duplicate gold')


def fractional(top, gold):
    return len(set(map(int, top)) & set(gold)) / len(gold)


def controls(C, Q, D):
    require(D.shape == (96, 96) and np.array_equal(D, np.diag(np.diag(D)))
            and np.isfinite(D).all() and (np.diag(D) > 0).all(), 'E-M-030: positive diagonal required')
    core.check_identity(C, Q, D)
    # Deterministic canary, not a new experimental arm or a seed panel.
    # At exact zero, signed real coordinates need not preserve >=0 codes;
    # an observed failure aborts rather than silently changing zero convention.
    perm = np.arange(95, -1, -1)
    # Fixed 96 single-coordinate sign flips: no cancellation across flipped columns.
    # Includes reversal and both scaled/unscaled representations, no data-driven choice.
    for X, V in ((C, Q), (C @ D, Q @ D)):
        for q in V:
            baseline = core.hamming_dist(X, q)
            for j in range(96):
                signs = np.ones(96)
                signs[j] = -1
                require(np.array_equal(baseline,
                                       core.hamming_dist(X[:, perm] * signs, q[perm] * signs)),
                        'E-M-031: signed permutation control')


def assert_placed_blocks(rs, rr, membership):
    S = np.asarray(membership, dtype=int)
    T = np.setdiff1d(np.arange(96), S)
    require(np.array_equal(rs[:32, :32], rr[np.ix_(S, S)])
            and np.array_equal(rs[32:, 32:], rr[np.ix_(T, T)]),
            'E-M-032: placed blocks differ')


def validate_records(records, ids):
    # Isolate closed-core diagnostic strings from package exception surfaces.
    failed = False
    try:
        core.validate_per_question_records(records, ids)
    except Exception:
        failed = True
    if failed:
        raise PipelineError('E-M-033: record validation')


def score_archive(rep, query_texts, gold_sets, question_ids, ordinal):
    """Six arms, fixed ten paired seeds, common twenty nuisance priorities.

    Native records are retained; a historical aggregate gate is enforced after full
    cohort coverage in run.py. No per-question historical anchor is manufactured.
    """
    require(type(question_ids) is list and all(type(q) is str for q in question_ids), 'E-M-018: identifiers')
    require(len(question_ids) == len(set(question_ids)) > 0, 'E-M-019: duplicate identifiers')
    require(type(query_texts) is list and type(gold_sets) is list, 'E-M-020: alignment')
    require(len(query_texts) == len(gold_sets) == len(question_ids), 'E-M-020: alignment')
    for gold in gold_sets:
        validate_gold(gold, len(rep.C))
    C, Q, D = rep.C, rep.queries(query_texts), rep.D
    controls(C, Q, D)
    Cs, Qs = C @ D, Q @ D
    P = np.array([np.random.default_rng(stable_archive_seed(ordinal, t) + 99).random(len(C))
                  for t in range(N_NUISANCE)])
    records = []
    for seed, partition in zip(core.ROTATION_SEEDS, core.PARTITION_SEEDS):
        a, b = core.draw_rotation_blocks(seed)
        rs = core.build_rotation(a, b, core.spectral_membership())
        membership = core.random_membership(partition)
        rr = core.build_rotation(a, b, membership)
        assert_placed_blocks(rs, rr, membership)
        for X, V in ((C, Q), (Cs, Qs)):
            for R in (rs, rr):
                norm, dot = core.check_rotation_invariance(X, V, R)
                require(norm <= core.TOL and dot <= core.TOL, 'E-M-023: invariance')
        cells = [(C, Q), (Cs, Qs), (C @ rs, Q @ rs), (Cs @ rs, Qs @ rs),
                 (C @ rr, Q @ rr), (Cs @ rr, Qs @ rr)]
        names = ['NATIVE', 'SCALED_NATIVE', 'B32_FRESH', 'SCALED_B32', 'RANDOM32_FRESH', 'SCALED_RANDOM32']
        for j, qid in enumerate(question_ids):
            baseline = core.hamming_dist(C, Q[j])
            require(np.array_equal(baseline, core.hamming_dist(Cs, Qs[j])), 'E-M-024: native distance')
            for arm, (X, V) in zip(names, cells):
                picks = topks_by_hamming(core.hamming_dist(X, V[j]), P)
                value = float(np.mean([fractional(top, gold_sets[j]) for top in picks]))
                records.append(dict(question_id=qid, rotation_seed=int(seed), arm=arm, fractional_R3=value))
    validate_records(records, question_ids)
    return records, dict(rep.diagnostics)
