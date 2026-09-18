"""Synthetic integration fixture, NOT benchmark measurements.
Runs real t1 tokenization, BM25, ranking, aggregation and decision.
Before the fix t1 has no second-benchmark input: signature fallback records
that limitation while still exercising the old function, rather than failing
on an unsupported keyword. After the fix the same test supplies that input.
"""
import importlib.util
import inspect
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path('/mnt/c/Users/MDP/dev/llmzip-work')
SOURCE = ROOT / 'top10_comparison_r1/coordinator/decision_tests.py'
LIB = ROOT / 'top10_comparison_r1/audit/audit_baseline_lib.py'

class T1Integration(unittest.TestCase):
    def test_bad_second_dataset_must_not_pass_c1(self):
        spec = importlib.util.spec_from_file_location('actual_decision', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            data = root / 'top10_comparison_r1/data'
            audit = root / 'top10_comparison_r1/audit'
            data.mkdir(parents=True)
            audit.mkdir(parents=True)
            (audit / LIB.name).write_bytes(LIB.read_bytes())
            # Ten high-scoring nongold documents exclude the gold from top 3/10.
            for i in range(1, 11):
                docs = [{'row': j, 'text': 'zebra'} for j in range(10)]
                docs.append({'row': 10, 'text': 'otter'})
                obj = {'docs': docs, 'queries': [{'qid': f'RT{i:02d}_q',
                       'text': 'zebra', 'gold': [10]}]}
                (data / f'RT{i:02d}.json').write_text(json.dumps(obj))
            arms = {f'k{k}/{s}': {'hit10': 100.0, 'fr3': 100.0}
                    for k in (96,192,384) for s in ('sym','qscale')}
            (root / 'LADDER.json').write_text(json.dumps({'arms': arms}))
            module.W = str(root)
            module.HERE = str(root)
            evidence = {
                'RealTalk': {'48B/qscale': {'ci_lo': 90.0, 'ci_hi': 100.0}},
                'PerLTQA': {'48B/qscale': {'vs_strongest_bm25_fr3_pp': -1.0,
                                         'ci_lo': -2.0, 'ci_hi': 0.5}}}
            supports = 'benchmark_results' in inspect.signature(module.t1).parameters
            result = module.t1(**({'benchmark_results': evidence} if supports else {}))
            self.assertEqual(result['code_arms']['48B/qscale']['vs_strongest_bm25_fr3_pp'],100.0)
            self.assertFalse(result['verdict']['C1_gate_plus2pp_fr3'],
                'Real t1 wrongly passes C1 with no valid second-dataset evidence')
            # Positive control: ensures the repair is not an always-false gate.
            evidence['PerLTQA']['48B/qscale'] = {
                'vs_strongest_bm25_fr3_pp': 100.0, 'ci_lo':90.0,'ci_hi':100.0}
            good = module.t1(benchmark_results=evidence)
            self.assertTrue(good['verdict']['C1_gate_plus2pp_fr3'])
            # Same positive estimates, but uncertainty crosses zero: must fail.
            evidence['PerLTQA']['48B/qscale']['ci_lo'] = -0.1
            uncertain = module.t1(benchmark_results=evidence)
            self.assertFalse(uncertain['verdict']['C1_gate_plus2pp_fr3'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
