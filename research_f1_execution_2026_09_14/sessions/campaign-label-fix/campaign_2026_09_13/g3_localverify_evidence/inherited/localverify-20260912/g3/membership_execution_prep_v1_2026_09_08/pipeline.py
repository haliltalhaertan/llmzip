"""M-1/M-2/M-3 preparation. No CLI, acquisition, writer, or real-data authorization.

The in-memory functions are computational primitives, not access-control sandboxes.
Only synthetic calls are authorized at this stage. Existing ingestion is NOT enabled.
"""
from pathlib import Path
import hashlib
import importlib.util

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

CORE_PATH = Path(__file__).resolve().parents[1] / 'membership_impl_v3_2026_09_07/membership_scaling_core.py'
CORE_HASH = 'bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72'
if hashlib.sha256(CORE_PATH.read_bytes()).hexdigest() != CORE_HASH:
    raise RuntimeError('E-M-001: core identity mismatch')
_spec = importlib.util.spec_from_file_location('membership_closed_core', CORE_PATH)
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)
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
            require(d >= 1, 'E-M-005: insufficient features')
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
    signs = np.where(np.arange(96) % 2, -1, 1)
    for X, V in ((C, Q), (C @ D, Q @ D)):
        for q in V:
            require(np.array_equal(core.hamming_dist(X, q),
                                   core.hamming_dist(X[:, perm] * signs, q[perm] * signs)),
                    'E-M-031: signed permutation control')


def score_archive(rep, query_texts, gold_sets, question_ids, ordinal, native_anchor):
    """Six arms, fixed ten paired seeds, common twenty nuisance priorities.

    native_anchor is required, not generated as a substitute here. Binding to real
    anchors remains a separate pre-run obligation. Synthetic tests supply synthetic anchors.
    """
    require(type(question_ids) is list and all(type(q) is str for q in question_ids), 'E-M-018: identifiers')
    require(len(question_ids) == len(set(question_ids)) > 0, 'E-M-019: duplicate identifiers')
    require(len(query_texts) == len(gold_sets) == len(question_ids), 'E-M-020: alignment')
    for gold in gold_sets:
        validate_gold(gold, len(rep.C))
    require(type(native_anchor) is list and len(native_anchor) == len(question_ids), 'E-M-021: anchor required')
    require(all(type(v) is float and np.isfinite(v) and 0 <= v <= 1 for v in native_anchor), 'E-M-022: anchor value')
    C, Q, D = rep.C, rep.queries(query_texts), rep.D
    controls(C, Q, D)
    Cs, Qs = C @ D, Q @ D
    P = np.array([np.random.default_rng(stable_archive_seed(ordinal, t) + 99).random(len(C))
                  for t in range(N_NUISANCE)])
    records = []
    for seed, partition in zip(core.ROTATION_SEEDS, core.PARTITION_SEEDS):
        a, b = core.draw_rotation_blocks(seed)
        rs = core.build_rotation(a, b, core.spectral_membership())
        rr = core.build_rotation(a, b, core.random_membership(partition))
        # Shared actual block objects, not independently redrawn lookalikes.
        core.assert_matched_blocks(a, b, a, b)
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
                if arm == 'NATIVE':
                    require(abs(value - native_anchor[j]) <= core.TOL, 'E-M-025: native anchor mismatch')
                records.append(dict(question_id=qid, rotation_seed=int(seed), arm=arm, fractional_R3=value))
    core.validate_per_question_records(records, question_ids)
    return records, dict(rep.diagnostics)


def assemble_in_memory(ingested, native_anchors):
    """M-3 schema connector. No source read, cohort reconstruction, writer or bootstrap.

    Caller must already hold authorized ingestion output. This preparation is tested
    only on fake objects. A real source entry point below unconditionally refuses.
    """
    require(ingested['questions_with_empty_gold'] == [], 'E-M-026: empty gold in cohort')
    ids = ingested['cohort_ids']
    require(set(native_anchors) == set(ids), 'E-M-027: anchor coverage')
    benchmark = ingested['benchmark']
    if benchmark == 'LoCoMo':
        archives = [(c['index'], c['units'], c['questions']) for c in ingested['conversations'].values()
                    if c['questions']]
    elif benchmark == 'LongMemEval':
        archives = [(i, ingested['questions'][qid]['units'], {qid: ingested['questions'][qid]})
                    for i, qid in enumerate(ids)]
    else:
        raise PipelineError('E-M-028: benchmark')
    records, diagnostics = [], []
    for ordinal, units, questions in archives:
        qids = list(questions)
        rep = Representation([u['text'] for u in units])
        rows, diag = score_archive(rep, [questions[q]['text'] for q in qids],
                                   [questions[q]['gold_rows'] for q in qids], qids, ordinal,
                                   [native_anchors[q] for q in qids])
        records.extend(rows)
        diagnostics.append(dict(archive_ordinal=ordinal, **diag))
    core.validate_per_question_records(records, ids)
    return {'records': records, 'diagnostics': diagnostics}


def run_on_real_corpus(*args, **kwargs):
    raise PipelineError('E-M-029: real execution not authorized')
