"""Isolated regression of the actual C1 assignment, not a retrieval rerun.
Synthetic contract fixture; no benchmark measurements are generated.
AST extraction avoids unrelated imports and machine-bound dataset reads.
"""
import ast
from pathlib import Path
import unittest

SOURCE = Path('C:/Users/MDP/dev/llmzip-work/top10_comparison_r1/coordinator/decision_tests.py')

class C1Regression(unittest.TestCase):
    def test_bad_second_dataset_cannot_pass(self):
        tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
        t1 = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 't1')
        assignments = [n for n in ast.walk(t1) if isinstance(n, ast.Assign)
                       and any('C1_gate_plus2pp_fr3' in ast.unparse(t) for t in n.targets)]
        self.assertEqual(len(assignments), 1, 'Must exercise the real, unique C1 assignment')
        helper = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'c1_gate']
        first = {'48B/qscale': {'vs_strongest_bm25_fr3_pp': 3.0, 'ci_lo': 2.1, 'ci_hi': 3.9}}
        second = {'48B/qscale': {'vs_strongest_bm25_fr3_pp': -1.0, 'ci_lo': -2.0, 'ci_hi': 0.5}}
        out = {'code_arms': first, 'benchmark_results': {'RealTalk': first, 'PerLTQA': second}, 'verdict': {}}
        ns = {'out': out}
        executable = ast.fix_missing_locations(ast.Module(body=helper + assignments, type_ignores=[]))
        exec(compile(executable, str(SOURCE), 'exec'), ns)
        self.assertFalse(out['verdict']['C1_gate_plus2pp_fr3'],
                         'C1 must FAIL: dataset 2 has a negative effect and its CI crosses zero')

if __name__ == '__main__':
    unittest.main(verbosity=2)
