"""Implementation-team regressions derived from audit 5126766; synthetic only.

This is NOT an independent audit. Historical arithmetic is AST-selected from a
pinned source blob: no historical module, corpus, or outcome is imported/read.
"""
import os
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'

import ast
import copy
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import traceback
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr


def _guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError('synthetic tests forbid network')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        name = os.fsdecode(args[0]).lower()
        if name.endswith('direct_url.json') and '.dist-info' in name and 'site-packages' in name:
            return
        if name.endswith(('.json', '.jsonl', '.csv', '.gz', '.parquet')):
            raise RuntimeError('synthetic tests forbid data-file access')


sys.addaudithook(_guard)
import numpy as np
import pipeline as p


class ArrayRepresentation:
    """Generated arrays stand in for an archive-fitted representation."""
    def __init__(self):
        rng = np.random.default_rng(80908)
        self.C = rng.normal(size=(13, 96))
        self.Q = rng.normal(size=(2, 96))
        self.D = np.diag(np.linspace(0.7, 1.3, 96))
        self.diagnostics = {'synthetic_only': True}

    def queries(self, texts):
        return self.Q[:len(texts)].copy()


class AuditRegressions(unittest.TestCase):
    def assert_safe_refusal(self, call, code=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        exc = None
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                call()
            except p.PipelineError as error:
                exc = error
        self.assertIsNotNone(exc, 'candidate did not refuse with PipelineError')
        if code is not None:
            self.assertIn(code, str(exc))
        self.assertIsNone(exc.__cause__)
        self.assertIsNone(exc.__context__)
        # The canary does not occur literally on a call-site source line, so a
        # formatted traceback can be checked without confusing source echo with
        # a candidate-message leak. Locals are deliberately not captured.
        canary = 'PRIVATE_' + 'IDENTIFIER_Q7'
        surfaces = [str(exc), repr(exc), stdout.getvalue(), stderr.getvalue(),
                    ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))]
        for surface in surfaces:
            self.assertNotIn(canary, surface)
        return exc

    def test_4000_tie_heavy_cases_match_pinned_arithmetic(self):
        root = Path(__file__).resolve().parents[3]
        blob = subprocess.check_output(['git', '-C', str(root), 'show',
            '692f599eedeb7e7a649443f24ff507e8c4d1c17d:research/v52/locomo_sign_mechanism_replication.py'])
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         'a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b')
        module = ast.parse(blob)
        names = {'topks_by_hamming', 'fractional', 'stable_archive_seed'}
        selected = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in names]
        self.assertEqual({n.name for n in selected}, names)
        scope = {'np': np, 'TOPK': 3}
        exec(compile(ast.Module(body=selected, type_ignores=[]), '<pinned functions only>', 'exec'), scope)
        rng = np.random.default_rng(83127)
        branches = {'small': 0, 'all_boundary': 0, 'partial': 0}
        for case in range(4000):
            n = int(rng.integers(1, 98))
            high = (1, 2, 3, 5, 97)[case % 5]
            distance = rng.integers(0, high, size=n)
            priorities = rng.random((20, n))
            if case % 3 == 0:
                priorities = np.round(priorities, 1)
            if n <= 3:
                branches['small'] += 1
            else:
                kth = np.partition(distance, 2)[2]
                need = 3 - np.count_nonzero(distance < kth)
                branches['all_boundary' if need == np.count_nonzero(distance == kth) else 'partial'] += 1
            actual = p.topks_by_hamming(distance, priorities)
            expected = scope['topks_by_hamming'](distance, priorities)
            self.assertEqual(len(actual), len(expected))
            for got, want in zip(actual, expected):
                # Exact array parity, not merely set parity; priorities may tie.
                np.testing.assert_array_equal(got, want)
        self.assertEqual(sum(branches.values()), 4000)
        self.assertTrue(all(v > 0 for v in branches.values()), branches)
        for ordinal in (0, 9, 469, 499):
            for trial in range(20):
                self.assertEqual(p.stable_archive_seed(ordinal, trial),
                                 scope['stable_archive_seed'](ordinal, trial))

    def test_nuisance_priorities_drawn_once_and_reused(self):
        rep = ArrayRepresentation()
        ordinal = 7
        original_rng = np.random.default_rng
        priorities = np.array([original_rng(p.stable_archive_seed(ordinal, t) + 99).random(len(rep.C))
                               for t in range(20)])
        gold = [[0, 2], [3, 4]]
        anchors = [float(np.mean([len(set(np.lexsort((row, p.core.hamming_dist(rep.C, q)))[:3])
                                      & set(g)) / len(g) for row in priorities]))
                   for q, g in zip(rep.Q, gold)]
        draws, seen = [], []
        original_topks = p.topks_by_hamming

        def draw(seed=None):
            draws.append(seed)
            return original_rng(seed)

        def topks(distance, shared, *args, **kwargs):
            seen.append((id(shared), np.asarray(shared).copy()))
            return original_topks(distance, shared, *args, **kwargs)

        with patch.object(np.random, 'default_rng', side_effect=draw), \
                patch.object(p, 'topks_by_hamming', side_effect=topks):
            records, _ = p.score_archive(rep, ['query a', 'query b'], gold,
                                          ['synthetic_a', 'synthetic_b'], ordinal, anchors)
        expected_seeds = [p.stable_archive_seed(ordinal, t) + 99 for t in range(20)]
        for seed in expected_seeds:
            self.assertEqual(draws.count(seed), 1)
        self.assertEqual(len(records), 120)
        self.assertEqual(len(seen), 120)
        self.assertEqual(len({identity for identity, _ in seen}), 1)
        for _, shared in seen:
            np.testing.assert_array_equal(shared, priorities)

    def test_all_96_mixed_zero_canaries_both_directions(self):
        base_c = np.ones((2, 96))
        base_q = np.ones((1, 96))
        for coordinate in range(96):
            for zero_archive in (True, False):
                with self.subTest(coordinate=coordinate, zero_archive=zero_archive):
                    c, q = base_c.copy(), base_q.copy()
                    if zero_archive:
                        c[:, coordinate] = 0.0
                    else:
                        q[:, coordinate] = 0.0
                    self.assert_safe_refusal(lambda: p.controls(c, q, np.eye(96)), 'E-M-031')
        p.controls(np.zeros((2, 96)), np.zeros((1, 96)), np.eye(96))

    def test_two_coordinate_zero_break_cannot_cancel(self):
        c, q = np.ones((1, 96)), np.ones((1, 96))
        c[0, 0], q[0, 0] = 0.0, 1.0
        c[0, 1], q[0, 1] = 0.0, -1.0
        # All-coordinate negation misses this: one gained mismatch cancels one
        # lost mismatch. Single-coordinate controls must still refuse.
        np.testing.assert_array_equal(p.core.hamming_dist(c, q[0]),
                                      p.core.hamming_dist(-c, -q[0]))
        self.assert_safe_refusal(lambda: p.controls(c, q, np.eye(96)), 'E-M-031')

    def test_actual_placed_block_mutations_are_detected(self):
        a, b = p.core.draw_rotation_blocks(60001)
        membership = p.core.random_membership(70001)
        rs = p.core.build_rotation(a, b, p.core.spectral_membership())
        rr = p.core.build_rotation(a, b, membership)
        p.assert_placed_blocks(rs, rr, membership)
        alternate_a, alternate_b = p.core.draw_rotation_blocks(60002)
        for damaged in (p.core.build_rotation(alternate_a, b, membership),
                        p.core.build_rotation(a, alternate_b, membership)):
            with self.subTest(kind='independent alternate orthogonal block'):
                with self.assertRaises((p.PipelineError, p.core.DesignViolation)):
                    p.assert_placed_blocks(rs, damaged, membership)

    def test_empty_malformed_and_uncovered_ingestion_fails_safely(self):
        qid = 'PRIVATE_' + 'IDENTIFIER_Q7'
        cases = [None, {}, [], {'benchmark': 'LoCoMo'},
                 {'benchmark': 'LongMemEval', 'cohort_ids': [],
                  'questions_with_empty_gold': [], 'questions': {}},
                 {'benchmark': 'LoCoMo', 'cohort_ids': [],
                  'questions_with_empty_gold': [], 'conversations': {}},
                 {'benchmark': 'LongMemEval', 'cohort_ids': [qid],
                  'questions_with_empty_gold': [], 'questions': {}},
                 {'benchmark': 'LoCoMo', 'cohort_ids': [qid],
                  'questions_with_empty_gold': [], 'conversations': {}},
                 {'benchmark': qid, 'cohort_ids': [qid],
                  'questions_with_empty_gold': [], 'questions': {}},
                 {'benchmark': 'LongMemEval', 'cohort_ids': [qid],
                  'questions_with_empty_gold': [qid], 'questions': {}}]
        for fixture in cases:
            with self.subTest(case=cases.index(fixture)):
                self.assert_safe_refusal(lambda: p.assemble_in_memory(fixture, {qid: 0.0}))

    def test_core_record_validator_diagnostics_do_not_escape(self):
        qid = 'PRIVATE_' + 'IDENTIFIER_Q7'
        self.assert_safe_refusal(lambda: p.validate_records([], [qid]))
        records = [{'question_id': qid, 'rotation_seed': 60001,
                    'arm': 'NATIVE', 'fractional_R3': 2.0}]
        self.assert_safe_refusal(lambda: p.validate_records(records, [qid]))

    def test_ingestion_structure_refusals_are_before_fitting(self):
        qid = 'PRIVATE_' + 'IDENTIFIER_Q7'
        base = {'benchmark': 'LongMemEval', 'cohort_ids': [qid],
                'questions_with_empty_gold': [], 'questions': {
                    qid: {'units': [{'text': 'synthetic memory'}],
                          'text': 'synthetic query', 'gold_rows': [0]}}}
        mutations = []
        for field in ('text', 'units', 'gold_rows'):
            item = copy.deepcopy(base)
            del item['questions'][qid][field]
            mutations.append(item)
        for bad_units in (None, [], {}, ['synthetic memory'], [{'text': None}]):
            item = copy.deepcopy(base)
            item['questions'][qid]['units'] = bad_units
            mutations.append(item)
        for bad_questions in (None, [], {qid: None}):
            item = copy.deepcopy(base)
            item['questions'] = bad_questions
            mutations.append(item)
        for bad_gold in ([], [True], [-1], [1], [0, 0]):
            item = copy.deepcopy(base)
            item['questions'][qid]['gold_rows'] = bad_gold
            mutations.append(item)
        item = copy.deepcopy(base)
        item['questions']['outside_cohort'] = copy.deepcopy(item['questions'][qid])
        mutations.append(item)
        with patch.object(p, 'Representation', side_effect=AssertionError('must not fit')):
            for index, item in enumerate(mutations):
                with self.subTest(index=index):
                    self.assert_safe_refusal(lambda: p.assemble_in_memory(
                        item, {qid: 0.0}, source_ids=[qid], synthetic_counts=(1, 1)))
            self.assert_safe_refusal(lambda: p.assemble_in_memory(base, {}), 'E-M-027')
            unknown = copy.deepcopy(base)
            unknown['benchmark'] = qid
            self.assert_safe_refusal(lambda: p.assemble_in_memory(unknown, {qid: 0.0}), 'E-M-028')
            empty = copy.deepcopy(base)
            empty['questions_with_empty_gold'] = [qid]
            self.assert_safe_refusal(lambda: p.assemble_in_memory(empty, {qid: 0.0}), 'E-M-026')

    def test_library_exception_chain_is_suppressed(self):
        secret = 'PRIVATE_' + 'IDENTIFIER_Q7'
        texts = ['synthetic memory token' + str(i) for i in range(100)]
        with patch.object(p.TfidfVectorizer, 'fit_transform', side_effect=ValueError(secret)):
            self.assert_safe_refusal(lambda: p.Representation(texts), 'E-M-006')
        # Build a minimal transform receiver. The first transform raises, so no
        # fitted estimators or source text need to exist for the rejection path.
        rep = p.Representation.__new__(p.Representation)
        rep.word = p.TfidfVectorizer()
        with patch.object(rep.word, 'transform', side_effect=ValueError(secret)):
            self.assert_safe_refusal(lambda: rep.queries(['synthetic query']), 'E-M-008')

    def test_invalid_anchor_values_fail_before_queries(self):
        rep = ArrayRepresentation()
        for value in (True, 0, '0.0', None, float('nan'), float('inf'), -0.1, 1.1):
            with self.subTest(type=type(value).__name__):
                with patch.object(rep, 'queries', side_effect=AssertionError('must not transform')):
                    self.assert_safe_refusal(lambda: p.score_archive(
                        rep, ['query'], [[0]], ['synthetic_q'], 0, [value]), 'E-M-022')

    def test_feature_failure_is_not_an_unreachable_specific_code(self):
        # Audit F5's original exact fixture. Generic safe fit failure is valid,
        # but advertising E-M-005 while swallowing it is not.
        exc = self.assert_safe_refusal(lambda: p.Representation(
            ['the a of and alpha alpha alpha'] * 100))
        self.assertNotIn('E-M-005', str(exc))
        self.assertNotIn('E-M-005', Path(p.__file__).read_text(encoding='utf-8'))

    def test_real_entry_always_refuses(self):
        self.assert_safe_refusal(lambda: p.run_on_real_corpus(
            enabled=True, authorized=True, force=True), 'E-M-029')


if __name__ == '__main__':
    unittest.main(verbosity=2)
