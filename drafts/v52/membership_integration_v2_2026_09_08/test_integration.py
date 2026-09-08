"""Synthetic end-to-end computation, no corpus ingestion and no production acceptance."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pipeline as p
import finish_synthetic as f
import source_adapter as a
import pinned


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = [f'synthetic memory item{i} family{i % 13} token{i * 17} category{i % 7}' for i in range(110)]
        cls.units = [{'text': t, 'dia_id': f'D1:{i}'} for i, t in enumerate(cls.texts)]
        cls.rep = p.Representation(cls.texts)

    def anchor(self, ordinal, gold):
        q = self.rep.queries([self.texts[4]])[0]
        dist = np.count_nonzero((self.rep.C >= 0) != (q >= 0), axis=1)
        values = []
        for trial in range(20):
            pri = np.random.default_rng(5100000 + ordinal * 100000 + trial * 100 + 99).random(110)
            top = np.lexsort((pri, dist))[:3]
            values.append(len(set(top) & set(gold)) / len(gold))
        return float(np.mean(values))

    def test_locomo_correction_to_bootstrap_to_writer(self):
        # Both raw gold sets are deliberately different from the corrected sets.
        groups = {f'conv{i}': {'index': i, 'units': copy.deepcopy(self.units),
                  'questions': {f'q{i}': {'text': self.texts[4], 'gold_rows': [99]}}} for i in range(2)}
        fake = {'benchmark': 'LoCoMo', 'cohort_ids': ['q0', 'q1'],
                'questions_with_empty_gold': [], 'conversations': groups}
        before = copy.deepcopy(fake)
        correction = a.corrections_from_historical_normalized({q: {'has_correct_evidence': True,
                      'correct_evidence': ['D1:4']} for q in fake['cohort_ids']})
        result = f.compute_synthetic(fake, {f'q{i}': self.anchor(i, [4]) for i in range(2)},
                  locomo_raw_evidence={q: ['D1:99'] for q in fake['cohort_ids']}, locomo_corrections=correction)
        self.assertEqual(fake, before)
        self.assertEqual(len(result['records']), 120)
        self.assertEqual(set(result['uncertainty']), {'question', 'cluster'})
        self.assertEqual(result['uncertainty']['cluster']['replicates'], 10000)
        g, gs = p.core.paired_matrices(result['records'], fake['cohort_ids'])
        self.assertEqual(result['estimates'], p.core.aggregate(g, gs))
        self.assertFalse(result['provenance']['historical_anchor_identity_verified'])
        with tempfile.TemporaryDirectory(prefix='synthetic-v2-', dir=Path(__file__).parent) as temp:
            folder = Path(temp) / 'bundle'
            receipt = f.write_synthetic_bundle(folder, result)
            raw = (folder / 'synthetic_result.json').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt['sha256'])
            self.assertEqual(json.loads(raw)['estimates'], result['estimates'])
            with self.assertRaisesRegex(p.PipelineError, 'E-F-006'):
                f.write_synthetic_bundle(folder, result)
            self.assertEqual((folder / 'synthetic_result.json').read_bytes(), raw)

    def test_lme_all_source_ordinal_to_score(self):
        fake = {'benchmark': 'LongMemEval', 'cohort_ids': ['z'], 'questions_with_empty_gold': [],
                'questions': {'z': {'text': self.texts[4], 'gold_rows': [4], 'units': self.units}}}
        # z has global lexical ordinal1 although primary position0.
        result = f.compute_synthetic(fake, {'z': self.anchor(1, [4])}, source_ids=['z', 'a_abs'], synthetic_counts=(2, 1))
        self.assertEqual(result['source_plan'][0]['archive_ordinal'], 1)
        self.assertEqual(result['source_plan'][0]['shard_index'], 0)
        self.assertEqual(set(result['uncertainty']), {'question'})
        self.assertIn('not recomputed', result['longmemeval_limit'])
        self.assertEqual(result['provenance']['bootstrap']['question']['seed'], 52002107)

    def test_presence_bridge_absent_null_empty(self):
        missing = a.corrections_from_historical_normalized({'q': {'has_correct_evidence': False, 'correct_evidence': []}})
        self.assertEqual(missing, {'q': {}})
        result = p.contracts.resolve_locomo_gold(['q'], {'q': ['D1:0']}, missing, {'q': {'D1:0': 0}})
        self.assertEqual(result['q']['gold_rows'], [0])
        empty = a.corrections_from_historical_normalized({'q': {'has_correct_evidence': True, 'correct_evidence': []}})
        with self.assertRaisesRegex(p.contracts.ContractError, 'E-S-009'):
            p.contracts.resolve_locomo_gold(['q'], {'q': ['D1:0']}, empty, {'q': {'D1:0': 0}})
        with self.assertRaisesRegex(p.PipelineError, 'E-A-004'):
            a.corrections_from_historical_normalized({'q': {'has_correct_evidence': True, 'correct_evidence': None}})
        with self.assertRaisesRegex(p.PipelineError, 'E-A-003'):
            a.corrections_from_historical_normalized({'q': {'correct_evidence': []}})

    def test_git_loader_ignores_checkout_and_rejects_wrong_bytes(self):
        # No checked-out core read is needed, including a CRLF-converted checkout.
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('checkout read forbidden')):
            module = pinned.load_pinned('core')
        self.assertEqual(module.ROTATION_SEEDS, tuple(range(60001, 60011)))
        bad = subprocess.CompletedProcess([], 0, stdout=b'bad source', stderr=b'')
        with patch.object(pinned.subprocess, 'run', return_value=bad):
            with self.assertRaisesRegex(RuntimeError, 'E-P-002'):
                pinned.load_pinned('core')

    def test_bad_direct_args_real_gate_and_empty_writer(self):
        with self.assertRaisesRegex(p.PipelineError, 'E-M-020'):
            p.score_archive(self.rep, None, [[4]], ['q'], 0, [0.0])
        with self.assertRaisesRegex(p.PipelineError, 'E-F-007'):
            f.run_on_real_corpus(enabled=True)
        with self.assertRaisesRegex(p.PipelineError, 'E-F-004'):
            f.write_synthetic_bundle('unused', {'status': 'SYNTHETIC_ONLY_NOT_EXECUTION_READY', 'question_ids': []})


if __name__ == '__main__':
    unittest.main(verbosity=2)
