import hashlib, importlib, inspect, sys, tempfile, unittest
from pathlib import Path
import consumption_gate_v9 as v9

class Tests(unittest.TestCase):
    def test_context_exposes_no_snapshot_field(self):
        c = v9.V9Context('p','1'*64,'f','2'*64,'b','3'*64)
        self.assertFalse(hasattr(c, 'initial_snapshot'))
        self.assertEqual(c._fields, ('plan_path','expected_plan_sha256','fixture_bindings_path','expected_fixture_bindings_sha256','physical_bindings_path','expected_physical_bindings_sha256'))

    def test_preflight_discards_validation_snapshot(self):
        old = v9._fresh_v8; calls=[]; marker=object()
        v9._fresh_v8 = lambda *a: (calls.append(a) or marker)
        try:
            c = v9.preflight_longmemeval_v9('p','1'*64,'f','2'*64,'b','3'*64)
            self.assertEqual(len(calls), 1)
            self.assertNotIn(marker, tuple(c))
        finally: v9._fresh_v8 = old

    def test_fresh_snapshot_reruns_each_access(self):
        old=v9._fresh_v8; calls=[]
        v9._fresh_v8=lambda *a: calls.append(a) or len(calls)
        try:
            c=v9.V9Context('p','1'*64,'f','2'*64,'b','3'*64)
            self.assertEqual(c.fresh_snapshot(),1); self.assertEqual(c.fresh_snapshot(),2); self.assertEqual(len(calls),2)
        finally: v9._fresh_v8=old

    def test_exact_loader_ignores_preloaded_same_name(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'victim.py'; p.write_text('def f():\n return 1\n'); h=hashlib.sha256(p.read_bytes()).hexdigest()
            sys.path.insert(0,td)
            try:
                victim=importlib.import_module('victim'); victim.f=lambda:999
                fresh=v9._exec_exact('victim',p,h)
                self.assertEqual(fresh.f(),1); self.assertEqual(victim.f(),999)
            finally:
                sys.path.remove(td); sys.modules.pop('victim',None)

    def test_public_signature(self):
        self.assertEqual(tuple(inspect.signature(v9.preflight_longmemeval_v9).parameters),
            ('plan_path','expected_plan_sha256','fixture_bindings_path','expected_fixture_bindings_sha256','physical_bindings_path','expected_physical_bindings_sha256'))

@unittest.skipUnless(v9._V8_GATE_PATH.exists(), 'canonical repo checkout unavailable')
class Canonical(unittest.TestCase):
    def test_exact_v8_chain_loads(self):
        gate=v9._load_v8_exact(); self.assertTrue(hasattr(gate,'_fresh_preflight'))
    def test_v8_hashes_match(self):
        self.assertEqual(hashlib.sha256(v9._V8_RUNTIME_PATH.read_bytes()).hexdigest(),v9.V8_RUNTIME_SHA256)
        self.assertEqual(hashlib.sha256(v9._V8_SNAPSHOT_PATH.read_bytes()).hexdigest(),v9.V8_SNAPSHOT_SHA256)
        self.assertEqual(hashlib.sha256(v9._V8_GATE_PATH.read_bytes()).hexdigest(),v9.V8_GATE_SHA256)

if __name__=='__main__': unittest.main()
