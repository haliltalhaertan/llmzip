import hashlib,importlib,sys,tempfile,unittest,inspect
from pathlib import Path
import storage_semantic_gate_v8 as v8
import v8_runtime as rt
import v8_snapshot as snap
class F:
 def __init__(self): self.fixture_id='f'; self.raw_bytes=b'f'; self.sha256=hashlib.sha256(b'f').hexdigest(); self.byte_length=1
 def reverify(self): return self.raw_bytes
class P:
 def __init__(self,d=('p',10)): self.physical_copy_id='c'; self.raw_bytes=b'p'; self.sha256=hashlib.sha256(b'p').hexdigest(); self.source_byte_length=1; self.denominator=d
 def reverify(self): return self.raw_bytes
class B:
 def __init__(self,p): self.fixtures=(F(),); self.physical_copies=(p,)
class Proof:
 anchor_sha256='a'*64; source_identity='x'; archive_ids=('a',); authoritative_probe_ids=(('a','q'),); denominators=(('c','p',10),)
class T(unittest.TestCase):
 def test_fresh_exec_ignores_preloaded_monkeypatch(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); path=td/'victim.py'; path.write_text('def f():\n return 1\n'); h=hashlib.sha256(path.read_bytes()).hexdigest(); sys.path.insert(0,str(td))
   try:
    victim=importlib.import_module('victim'); victim.f=lambda:999; fresh=rt.exec_pinned_module('victim',path,h); self.assertEqual(fresh.f(),1); self.assertEqual(victim.f(),999)
   finally: sys.path.remove(str(td)); sys.modules.pop('victim',None)
 def test_diluted_denominator_rejected(self):
  with self.assertRaises(rt.V8ValidationError): snap.freeze_verified_bindings(Proof(),B(P(('p',10**9))),'1'*64,'2'*64,'3'*64,'4'*64)
 def test_immutable_snapshot(self):
  s=snap.freeze_verified_bindings(Proof(),B(P()),'1'*64,'2'*64,'3'*64,'4'*64); self.assertEqual(s.semantic_proof.denominators,(('c','p',10),))
  with self.assertRaises(AttributeError): object.__setattr__(s.physical_copies[0],'denominator',10**9)
 def test_refresh_calls_fresh_chain(self):
  old=v8._fresh_preflight; calls=[]; sentinel=object(); v8._fresh_preflight=lambda *a:(calls.append(a) or sentinel)
  try: self.assertIs(v8.V8Context('p','1'*64,'f','2'*64,'b','3'*64,None).refresh(),sentinel); self.assertEqual(len(calls),1)
  finally: v8._fresh_preflight=old
 def test_public_signature(self):
  self.assertEqual(tuple(inspect.signature(v8.preflight_longmemeval_v8).parameters),('plan_path','expected_plan_sha256','fixture_bindings_path','expected_fixture_bindings_sha256','physical_bindings_path','expected_physical_bindings_sha256'))
@unittest.skipUnless(rt.V7_PATH.exists(),'canonical repo checkout unavailable')
class Canon(unittest.TestCase):
 def test_chain(self):
  a,b,c=v8._load_pinned_chain(); self.assertTrue(hasattr(a,'_verify_plan_data_against_anchor')); self.assertTrue(hasattr(b,'load_plan')); self.assertTrue(hasattr(c,'preflight'))
 def test_v7_hash(self): self.assertEqual(hashlib.sha256(rt.V7_PATH.read_bytes()).hexdigest(),rt.V7_SOURCE_SHA256)
if __name__=='__main__': unittest.main()
