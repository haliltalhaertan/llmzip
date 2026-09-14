"""M-1/M-2/M-3 preparation. No CLI, acquisition, writer, or real-data authorization.

The in-memory functions are computational primitives, not access-control sandboxes.
Only synthetic calls are authorized at this stage. Existing ingestion is NOT enabled.
"""
from pathlib import Path
import hashlib
import importlib.util
import exact_oracle
import record_boundary

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

CORE_PATH = Path(__file__).resolve().parent / 'membership_scaling_core.py'
CORE_HASH = 'bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72'


def _verified_core_bytes(raw):
    """Require raw blob identity; use the documented LF checkout/materializer."""
    if hashlib.sha256(raw).hexdigest() == CORE_HASH:
        return raw
    raise RuntimeError('E-M-001: core identity mismatch')


_verified_core_bytes(CORE_PATH.read_bytes())
_spec = importlib.util.spec_from_file_location('membership_closed_core', CORE_PATH)
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)
TOPK, N_NUISANCE = 3, 20

# Fixed before any data: 96 singleton coordinate negations plus all-96 negation.
# These are source literals by governance decision; do not generate them from observed data.
SIGNED_CANARY_MASKS = (
    0x000000000000000000000001,
    0x000000000000000000000002,
    0x000000000000000000000004,
    0x000000000000000000000008,
    0x000000000000000000000010,
    0x000000000000000000000020,
    0x000000000000000000000040,
    0x000000000000000000000080,
    0x000000000000000000000100,
    0x000000000000000000000200,
    0x000000000000000000000400,
    0x000000000000000000000800,
    0x000000000000000000001000,
    0x000000000000000000002000,
    0x000000000000000000004000,
    0x000000000000000000008000,
    0x000000000000000000010000,
    0x000000000000000000020000,
    0x000000000000000000040000,
    0x000000000000000000080000,
    0x000000000000000000100000,
    0x000000000000000000200000,
    0x000000000000000000400000,
    0x000000000000000000800000,
    0x000000000000000001000000,
    0x000000000000000002000000,
    0x000000000000000004000000,
    0x000000000000000008000000,
    0x000000000000000010000000,
    0x000000000000000020000000,
    0x000000000000000040000000,
    0x000000000000000080000000,
    0x000000000000000100000000,
    0x000000000000000200000000,
    0x000000000000000400000000,
    0x000000000000000800000000,
    0x000000000000001000000000,
    0x000000000000002000000000,
    0x000000000000004000000000,
    0x000000000000008000000000,
    0x000000000000010000000000,
    0x000000000000020000000000,
    0x000000000000040000000000,
    0x000000000000080000000000,
    0x000000000000100000000000,
    0x000000000000200000000000,
    0x000000000000400000000000,
    0x000000000000800000000000,
    0x000000000001000000000000,
    0x000000000002000000000000,
    0x000000000004000000000000,
    0x000000000008000000000000,
    0x000000000010000000000000,
    0x000000000020000000000000,
    0x000000000040000000000000,
    0x000000000080000000000000,
    0x000000000100000000000000,
    0x000000000200000000000000,
    0x000000000400000000000000,
    0x000000000800000000000000,
    0x000000001000000000000000,
    0x000000002000000000000000,
    0x000000004000000000000000,
    0x000000008000000000000000,
    0x000000010000000000000000,
    0x000000020000000000000000,
    0x000000040000000000000000,
    0x000000080000000000000000,
    0x000000100000000000000000,
    0x000000200000000000000000,
    0x000000400000000000000000,
    0x000000800000000000000000,
    0x000001000000000000000000,
    0x000002000000000000000000,
    0x000004000000000000000000,
    0x000008000000000000000000,
    0x000010000000000000000000,
    0x000020000000000000000000,
    0x000040000000000000000000,
    0x000080000000000000000000,
    0x000100000000000000000000,
    0x000200000000000000000000,
    0x000400000000000000000000,
    0x000800000000000000000000,
    0x001000000000000000000000,
    0x002000000000000000000000,
    0x004000000000000000000000,
    0x008000000000000000000000,
    0x010000000000000000000000,
    0x020000000000000000000000,
    0x040000000000000000000000,
    0x080000000000000000000000,
    0x100000000000000000000000,
    0x200000000000000000000000,
    0x400000000000000000000000,
    0x800000000000000000000000,
    0xffffffffffffffffffffffff,
)


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
        except Exception:
            failed = True
        if failed:
            raise PipelineError('E-M-006: representation fit failed')
        d = min(32, w.shape[0] - 1, w.shape[1] - 1)
        require(d >= 1, 'E-M-005: insufficient features')
        failed = False
        try:
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


def _signs_from_mask(mask):
    require(type(mask) is int and 0 < mask < (1 << 96), 'E-M-032: canary mask')
    return np.array([-1.0 if (mask >> j) & 1 else 1.0 for j in range(96)], dtype=np.float64)


# Filled once from the declared seed before observing any archive; tests rederive
# the literal independently. The 97 masks above are applied in this output basis.
SIGNED_CANARY_SEED = 52003107
SIGNED_CANARY_PERMUTATION = (53, 77, 36, 58, 54, 11, 10, 50, 90, 76, 49, 12, 51, 32, 64, 60, 28, 86, 31, 66, 63, 56, 91, 82, 20, 87, 3, 7, 92, 17, 43, 83, 18, 81, 46, 24, 57, 9, 35, 47, 68, 30, 14, 25, 29, 15, 69, 21, 55, 74, 41, 88, 73, 5, 6, 23, 72, 59, 38, 61, 8, 79, 22, 65, 2, 48, 34, 1, 85, 40, 16, 70, 62, 52, 44, 95, 19, 39, 67, 45, 26, 13, 78, 37, 42, 89, 80, 0, 4, 75, 84, 94, 93, 27, 71, 33)


def signed_code_images(rows, permutation, mask):
    """Implementation under test: numerical permutation, sign, zero threshold."""
    return (rows[:, permutation] * _signs_from_mask(mask)) >= 0


def _assert_member_codes(X, V, mask, permutation, codes):
    for rows, source_codes in zip((X, V), codes):
        wanted = exact_oracle.expected_images(source_codes, permutation, mask)
        actual = signed_code_images(rows, permutation, mask)
        require(np.array_equal(actual, np.asarray(wanted, dtype=bool)),
                'E-M-031: signed permutation control')


def assert_signed_member(X, V, mask, permutation=None):
    """One independently testable member; no caller-provided expected bit images."""
    if permutation is None:
        permutation = SIGNED_CANARY_PERMUTATION
    codes = tuple(exact_oracle.exact_codes(rows) for rows in (X, V))
    _assert_member_codes(X, V, mask, permutation, codes)


def coordinatewise_signed_certificate(X, V):
    """Independent exact oracle vs every transported code bit for every member.

    In particular all-zero coordinates fail when negated: shared disagreement
    equality cannot hide two wrong bits. No aggregate comparison is a certificate.
    """
    X, V = np.asarray(X), np.asarray(V)
    require(X.ndim == 2 and X.shape[0] > 0 and X.shape[1] == 96 and np.isfinite(X).all(), 'E-M-033: canary archive')
    require(V.ndim == 2 and V.shape[0] > 0 and V.shape[1] == 96 and np.isfinite(V).all(), 'E-M-034: canary queries')
    # The exact source bits do not depend on the family member. Compute once,
    # then independently transport and compare all bits for each of 97 members.
    codes = tuple(exact_oracle.exact_codes(rows) for rows in (X, V))
    for mask in SIGNED_CANARY_MASKS:
        _assert_member_codes(X, V, mask, SIGNED_CANARY_PERMUTATION, codes)


def legacy_signed_canary(X, V):
    """Historical 48-coordinate aggregate canary; regression only, never authority."""
    perm = np.arange(95, -1, -1)
    signs = np.array([1.0 if i % 2 == 0 else -1.0 for i in range(96)])
    for q in V:
        require(np.array_equal(core.hamming_dist(X, q),
                               core.hamming_dist(X[:, perm] * signs, q[perm] * signs)),
                'E-M-031: signed permutation control')


def validate_records(records, question_ids):
    """Keep immutable core diagnostics behind a fixed-message wrapper."""
    require(type(records) is list and len(records) > 0, 'E-M-042: empty record set')
    require(record_boundary.valid_records(records, question_ids, core.ROTATION_SEEDS, core.ARMS),
            'E-M-043: invalid record set')
    failed = False
    try:
        core.validate_per_question_records(records, question_ids)
    except Exception:
        failed = True
    if failed:
        raise PipelineError('E-M-043: invalid record set')


def controls(C, Q, D):
    require(D.shape == (96, 96) and np.array_equal(D, np.diag(np.diag(D)))
            and np.isfinite(D).all() and (np.diag(D) > 0).all(), 'E-M-030: positive diagonal required')
    core.check_identity(C, Q, D)
    for X, V in ((C, Q), (C @ D, Q @ D)):
        coordinatewise_signed_certificate(X, V)


def _nuisance_priorities(ordinal, n_rows):
    require(type(n_rows) is int and n_rows > 0, 'E-M-035: archive rows')
    return np.array([np.random.default_rng(stable_archive_seed(ordinal, t) + 99).random(n_rows)
                     for t in range(N_NUISANCE)])


def assert_embedded_blocks(rotation, membership, expected_a, expected_b):
    """Check blocks ACTUALLY embedded, not only two detached RNG outputs."""
    complement = np.setdiff1d(np.arange(96), membership)
    failed = False
    try:
        core.assert_matched_blocks(rotation[np.ix_(membership, membership)],
                                   rotation[np.ix_(complement, complement)], expected_a, expected_b)
    except Exception:
        failed = True
    if failed:
        raise PipelineError('E-M-044: rotation block mismatch')
    require(np.count_nonzero(rotation[np.ix_(membership, complement)]) == 0
            and np.count_nonzero(rotation[np.ix_(complement, membership)]) == 0,
            'E-M-044: rotation block mismatch')


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
    P = _nuisance_priorities(ordinal, len(C))
    records = []
    for seed, partition in zip(core.ROTATION_SEEDS, core.PARTITION_SEEDS):
        a, b = core.draw_rotation_blocks(seed)
        a_check, b_check = core.draw_rotation_blocks(seed)
        core.assert_matched_blocks(a, b, a_check, b_check)
        spectral, random = core.spectral_membership(), core.random_membership(partition)
        rs = core.build_rotation(a, b, spectral)
        rr = core.build_rotation(a, b, random)
        assert_embedded_blocks(rs, spectral, a_check, b_check)
        assert_embedded_blocks(rr, random, a_check, b_check)
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
    validate_records(records, question_ids)
    return records, dict(rep.diagnostics)


def _validate_ingested_schema(ingested):
    require(type(ingested) is dict, 'E-M-036: ingestion schema')
    require(type(ingested.get('benchmark')) is str, 'E-M-036: ingestion schema')
    require(type(ingested.get('questions_with_empty_gold')) is list, 'E-M-036: ingestion schema')
    ids = ingested.get('cohort_ids')
    require(type(ids) is list and len(ids) > 0 and all(type(q) is str for q in ids),
            'E-M-037: cohort schema')
    require(len(ids) == len(set(ids)), 'E-M-037: cohort schema')
    benchmark = ingested['benchmark']
    if benchmark == 'LoCoMo':
        convs = ingested.get('conversations')
        require(type(convs) is dict and len(convs) > 0, 'E-M-038: LoCoMo ingestion schema')
        seen, ordinals = set(), set()
        for conv in convs.values():
            require(type(conv) is dict and type(conv.get('index')) is int and conv['index'] >= 0,
                    'E-M-038: LoCoMo ingestion schema')
            require(conv['index'] not in ordinals, 'E-M-038: LoCoMo ingestion schema')
            ordinals.add(conv['index'])
            units, questions = conv.get('units'), conv.get('questions')
            require(type(units) is list and all(type(u) is dict and type(u.get('text')) is str for u in units),
                    'E-M-038: LoCoMo ingestion schema')
            require(type(questions) is dict, 'E-M-038: LoCoMo ingestion schema')
            for qid, q in questions.items():
                require(type(qid) is str and type(q) is dict and type(q.get('text')) is str
                        and type(q.get('gold_rows')) is list, 'E-M-038: LoCoMo ingestion schema')
                require(qid not in seen, 'E-M-040: ingestion cohort coverage')
                validate_gold(q['gold_rows'], len(units))
                seen.add(qid)
        require(seen == set(ids), 'E-M-040: ingestion cohort coverage')
    elif benchmark == 'LongMemEval':
        questions = ingested.get('questions')
        require(type(questions) is dict and set(questions) == set(ids),
                'E-M-039: LongMemEval ingestion schema')
        for qid, q in questions.items():
            require(type(qid) is str and type(q) is dict and type(q.get('text')) is str
                    and type(q.get('gold_rows')) is list, 'E-M-039: LongMemEval ingestion schema')
            units = q.get('units')
            require(type(units) is list and all(type(u) is dict and type(u.get('text')) is str for u in units),
                    'E-M-039: LongMemEval ingestion schema')
            validate_gold(q['gold_rows'], len(units))
    else:
        raise PipelineError('E-M-028: benchmark')
    return ids


def assemble_in_memory(ingested, native_anchors):
    """M-3 schema connector. No source read, cohort reconstruction, writer or bootstrap.

    Caller must already hold authorized ingestion output. This preparation is tested
    only on fake objects. A real source entry point below unconditionally refuses.
    """
    ids = _validate_ingested_schema(ingested)
    require(ingested['questions_with_empty_gold'] == [], 'E-M-026: empty gold in cohort')
    require(type(native_anchors) is dict and set(native_anchors) == set(ids), 'E-M-027: anchor coverage')
    benchmark = ingested['benchmark']
    if benchmark == 'LoCoMo':
        archives = [(c['index'], c['units'], c['questions']) for c in ingested['conversations'].values()
                    if c['questions']]
    elif benchmark == 'LongMemEval':
        archives = [(i, ingested['questions'][qid]['units'], {qid: ingested['questions'][qid]})
                    for i, qid in enumerate(sorted(ids))]
    require(len(archives) > 0, 'E-M-041: empty archive set')
    records, diagnostics = [], []
    for ordinal, units, questions in archives:
        qids = list(questions)
        rep = Representation([u['text'] for u in units])
        rows, diag = score_archive(rep, [questions[q]['text'] for q in qids],
                                   [questions[q]['gold_rows'] for q in qids], qids, ordinal,
                                   [native_anchors[q] for q in qids])
        records.extend(rows)
        diagnostics.append(dict(archive_ordinal=ordinal, **diag))
    require(len(records) > 0, 'E-M-042: empty record set')
    validate_records(records, ids)
    return {'records': records, 'diagnostics': diagnostics}


def run_on_real_corpus(*args, **kwargs):
    raise PipelineError('E-M-029: real execution not authorized')
