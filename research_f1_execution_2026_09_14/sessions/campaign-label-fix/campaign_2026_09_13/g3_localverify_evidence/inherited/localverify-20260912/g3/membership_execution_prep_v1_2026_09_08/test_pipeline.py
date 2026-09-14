"""Synthetic-only preparation tests; no independent-audit claim."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

# Reject data files and network before importing the computation package.
def guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError('test network forbidden')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        p = os.fsdecode(args[0]).lower()
        # Installed-package origin metadata is not corpus data.
        if p.endswith('direct_url.json') and '.dist-info' in p and 'site-packages' in p:
            return
        if p.endswith(('.json', '.jsonl', '.csv', '.gz', '.parquet')):
            raise RuntimeError('test data file access forbidden')
sys.addaudithook(guard)
import pipeline_g3 as p
import numpy as np


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = [f'synthetic memory item{i} family{i % 13} token{i * 17} category{i % 7}'
                     for i in range(110)]
        cls.rep = p.Representation(cls.texts)
        cls.query = [cls.texts[4], 'synthetic family3 category2']
        cls.gold = [[4], [3, 16]]
        q = cls.rep.queries(cls.query)
        pri = np.array([np.random.default_rng(p.stable_archive_seed(0, t) + 99).random(110)
                        for t in range(20)])
        # Synthetic test oracle: full lexsort, not candidate top-k.
        cls.anchors = [float(np.mean([p.fractional(np.lexsort((x, p.core.hamming_dist(cls.rep.C, v)))[:3], g)
                                     for x in pri])) for v, g in zip(q, cls.gold)]

    def test_representation(self):
        self.assertEqual(self.rep.C.shape, (110, 96))
        self.assertLess(np.max(np.abs(self.rep.C.mean(axis=0))), 1e-12)
        # SVD fit_transform vs transform is numerical equality, not a sign identity gate.
        self.assertLessEqual(np.max(np.abs(self.rep.queries(self.texts) - self.rep.C)), 1e-12)
        snapshot = self.rep.C.copy(), self.rep.D.copy(), self.rep.mu.copy()
        self.rep.queries(['never seen synthetic query'])
        for old, new in zip(snapshot, (self.rep.C, self.rep.D, self.rep.mu)):
            self.assertTrue(np.array_equal(old, new))

    def test_topk_oracle(self):
        for n in (1, 2, 3, 4, 27, 110):
            rng = np.random.default_rng(n)
            d, pri = rng.integers(0, 5, n), rng.random((20, n))
            for got, row in zip(p.topks_by_hamming(d, pri), pri):
                self.assertEqual(set(got), set(np.lexsort((row, d))[:3]))

    def test_score_and_connector(self):
        rows, diag = p.score_archive(self.rep, self.query, self.gold, ['s0', 's1'], 0, self.anchors)
        self.assertEqual(len(rows), 120)
        self.assertIn('cv_sigma_after', diag)
        self.assertEqual({r['rotation_seed'] for r in rows}, set(range(60001, 60011)))
        for seed in range(60001, 60011):
            for qid in ('s0', 's1'):
                values = {r['arm']: r['fractional_R3'] for r in rows
                          if r['rotation_seed'] == seed and r['question_id'] == qid}
                self.assertEqual(values['NATIVE'], values['SCALED_NATIVE'])
        units = [{'text': x} for x in self.texts]
        questions = {qid: {'text': t, 'gold_rows': g} for qid, t, g in zip(['s0', 's1'], self.query, self.gold)}
        fake = {'benchmark': 'LoCoMo', 'cohort_ids': ['s0', 's1'], 'questions_with_empty_gold': [],
                'conversations': {'synthetic': {'index': 0, 'units': units, 'questions': questions}}}
        actual = p.assemble_in_memory(fake, dict(zip(['s0', 's1'], self.anchors)))
        self.assertEqual(actual['records'], rows)

    def test_refusals(self):
        with self.assertRaisesRegex(p.PipelineError, 'E-M-004'):
            p.Representation(['too small'])
        for gold in ([], [True], [-1], [110], [0, 0]):
            with self.assertRaises(p.PipelineError):
                p.validate_gold(gold, 110)
        with self.assertRaisesRegex(p.PipelineError, 'E-M-025'):
            p.score_archive(self.rep, self.query, self.gold, ['s0', 's1'], 0,
                            [1.0 - self.anchors[0], self.anchors[1]])
        with self.assertRaisesRegex(p.PipelineError, 'E-M-021'):
            p.score_archive(self.rep, self.query, self.gold, ['s0', 's1'], 0, None)
        with self.assertRaisesRegex(p.PipelineError, 'E-M-029'):
            p.run_on_real_corpus(enabled=True)
        with self.assertRaises(RuntimeError):
            open('synthetic_forbidden.json')

    def test_controls_negative(self):
        q = self.rep.queries(self.query)
        with self.assertRaisesRegex(p.PipelineError, 'E-M-030'):
            p.controls(self.rep.C, q, -self.rep.D)
        rng = np.random.default_rng(1)
        c, v = rng.normal(size=(10, 96)), rng.normal(size=(2, 96))
        p.controls(c, v, np.eye(96))
        c[:, 0], v[:, 0] = 0, 1
        with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
            p.controls(c, v, np.eye(96))
        bad = self.rep.C.copy()
        bad[0, 0] = np.nan
        with self.assertRaises(p.core.DesignViolation):
            p.core.scale_matrix(bad)

    def test_lme_connector(self):
        # One question archive, one synthetic anchor; no cluster inference.
        fake = {'benchmark': 'LongMemEval', 'cohort_ids': ['s0'], 'questions_with_empty_gold': [],
                'questions': {'s0': {'units': [{'text': t} for t in self.texts],
                                     'text': self.query[0], 'gold_rows': self.gold[0]}}}
        got = p.assemble_in_memory(fake, {'s0': self.anchors[0]})
        self.assertEqual(len(got['records']), 60)

    def test_old_source_arithmetic(self):
        # Read source code as a raw Git blob, never import the historical module.
        import ast
        blob = subprocess.check_output(['git', 'show',
            '692f599eedeb7e7a649443f24ff507e8c4d1c17d:research/v52/locomo_sign_mechanism_replication.py'])
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         'a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b')
        tree = ast.parse(blob)
        names = {'topks_by_hamming', 'fractional', 'stable_archive_seed'}
        selected = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[])
        scope = {'np': np, 'TOPK': 3}
        exec(compile(selected, '<pinned arithmetic only>', 'exec'), scope)
        for ordinal in (0, 9, 469):
            for trial in range(20):
                self.assertEqual(p.stable_archive_seed(ordinal, trial), scope['stable_archive_seed'](ordinal, trial))
        rng = np.random.default_rng(128)
        for n in (2, 3, 4, 110):
            d, pri = rng.integers(0, 96, n), rng.random((20, n))
            for a, b in zip(p.topks_by_hamming(d, pri), scope['topks_by_hamming'](d, pri)):
                self.assertTrue(np.array_equal(a, b))


if __name__ == '__main__':
    unittest.main(verbosity=2)
