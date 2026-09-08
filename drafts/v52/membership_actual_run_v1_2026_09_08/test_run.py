import ast
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

import numpy as np
import pipeline as p
import run


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        texts = [f'synthetic memory item{i} family{i%13} token{i*17} category{i%7}' for i in range(110)]
        rep = p.Representation(texts)
        q = rep.queries([texts[4]])[0]
        dist = p.core.hamming_dist(rep.C, q)
        anchors = [float(np.mean([p.fractional(np.lexsort((np.random.default_rng(
            p.stable_archive_seed(0,t)+99).random(110),dist))[:3],[4]) for t in range(20)]))]
        cls.rows, _ = p.score_archive(rep, [texts[4]], [[4]], ['q0'], 0)
        raw = subprocess.check_output(['git','-C',str(run.ROOT),'cat-file','blob',
            '1863f11a8e5b3046d257aed907f1c380793d21a0:drafts/v52/membership_integration_v2_2026_09_08/pipeline.py'])
        nodes = [n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='score_archive']
        namespace = dict(p.__dict__)
        exec(compile(ast.Module(body=nodes,type_ignores=[]), '<previous-score>', 'exec'), namespace)
        cls.old, _ = namespace['score_archive'](rep,[texts[4]],[[4]],['q0'],0,anchors)
        cls.anchor = anchors[0]

    def test_arithmetic_port_exact(self):
        self.assertEqual(self.rows,self.old)
        self.assertEqual(len(self.rows),60)

    def test_native_gate(self):
        self.assertTrue(run.aggregate_native_gate(self.rows,['q0'],self.anchor)['passed'])
        with self.assertRaises(p.PipelineError):
            run.aggregate_native_gate(self.rows,['q0'],self.anchor+0.01)

    def test_missing_record_rejected(self):
        with self.assertRaises(p.PipelineError):
            run.aggregate_native_gate(self.rows[:-1],['q0'],self.anchor)

    def test_create_only(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder)/'result.json'
            digest=run.write_json(file,{'a':1})
            with self.assertRaises(FileExistsError):
                run.write_json(file,{'a':2})
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),digest)

    def test_nonfinite_not_written(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'result.json'
            with self.assertRaises(ValueError):
                run.write_json(file,{'a':float('nan')})
            self.assertFalse(file.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
