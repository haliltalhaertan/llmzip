import hashlib, json, tempfile
from pathlib import Path
import unittest
from storage_adapter_preflight_v3 import preflight, PreflightError

def h(raw): return hashlib.sha256(raw).hexdigest()

class V3PreflightTests(unittest.TestCase):
    def setup_case(self, root):
        root=Path(root)
        fixture={"schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V2","transform":{"input_utf8":"hello"},"id_mapping":{"logical_id":"toy-1","offset":0,"payload_utf8":"payload"},"corruption":{"target_kind":"FIXTURE","target_id":"fx1","byte_offset":1,"xor_mask":1}}
        fr=json.dumps(fixture,sort_keys=True,separators=(",",":")).encode(); (root/"fx.json").write_bytes(fr)
        pr=b"PHYS"; (root/"phys.bin").write_bytes(pr)
        plan={"schema":"v52.static-storage-plan","version":1,"fixtures":[{"id":"fx1","sha256":h(fr)}],"physical_copies":[{"id":"pc1","artifact_sha256":h(pr),"population_ids":["p0","p1"]}],"populations":[{"id":"p0","count":0},{"id":"p1","count":4}]}
        p=json.dumps(plan,sort_keys=True,separators=(",",":")).encode(); (root/"plan.json").write_bytes(p)
        fb={"schema":"v52.fixture-bindings","version":2,"fixtures":[{"fixture_id":"fx1","relative_path":"fx.json","byte_length":len(fr),"sha256":h(fr),"content_schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V2","operation_sections":{"TRANSFORM":"transform","ID_MAPPING":"id_mapping","CORRUPT":"corruption"}}]}
        f=json.dumps(fb,sort_keys=True,separators=(",",":")).encode(); (root/"fb.json").write_bytes(f)
        pb={"schema":"v52.physical-copy-bindings","version":2,"physical_copies":[{"physical_copy_id":"pc1","physical_locator":"phys.bin","source_raw_byte_length":len(pr),"artifact_sha256":h(pr),"sharing_denominator_rule":"POPULATION_COUNT"}]}
        b=json.dumps(pb,sort_keys=True,separators=(",",":")).encode(); (root/"pb.json").write_bytes(b)
        return h(p),h(f),h(b)
    def run_pf(self, root, hs):
        return preflight(Path(root)/"plan.json",hs[0],Path(root)/"fb.json",hs[1],Path(root)/"pb.json",hs[2])
    def test_authenticated_bytes_survive_path_mutation_and_zero_is_nonamortized(self):
        with tempfile.TemporaryDirectory() as td:
            hs=self.setup_case(td); out=self.run_pf(td,hs); before=out.fixtures[0].raw_bytes
            Path(td,"fx.json").write_bytes(b'{"mutated":true}')
            self.assertEqual(before,out.fixtures[0].raw_bytes)
            self.assertEqual(out.physical_copies[0].denominator_states[0],("p0","EMPTY_NO_AMORTIZATION",None))
            self.assertEqual(out.physical_copies[0].denominator_states[1],("p1","POSITIVE",4))
    def test_duplicate_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            hs=list(self.setup_case(td)); raw=b'{"schema":"v52.fixture-bindings","schema":"v52.fixture-bindings","version":2,"fixtures":[]}'
            Path(td,"fb.json").write_bytes(raw); hs[1]=h(raw)
            with self.assertRaises(PreflightError): self.run_pf(td,hs)
    def test_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            hs=list(self.setup_case(td)); raw=b'{"schema":"v52.fixture-bindings","version":2,"fixtures":NaN}'
            Path(td,"fb.json").write_bytes(raw); hs[1]=h(raw)
            with self.assertRaises(PreflightError): self.run_pf(td,hs)
    def test_fixture_section_schema_is_exact(self):
        with tempfile.TemporaryDirectory() as td:
            hs=list(self.setup_case(td)); root=Path(td); fx=json.loads((root/"fx.json").read_text()); fx["transform"]["extra"]=1
            fr=json.dumps(fx,sort_keys=True,separators=(",",":")).encode(); (root/"fx.json").write_bytes(fr)
            plan=json.loads((root/"plan.json").read_text()); plan["fixtures"][0]["sha256"]=h(fr); p=json.dumps(plan,sort_keys=True,separators=(",",":")).encode(); (root/"plan.json").write_bytes(p); hs[0]=h(p)
            fb=json.loads((root/"fb.json").read_text()); fb["fixtures"][0]["sha256"]=h(fr); fb["fixtures"][0]["byte_length"]=len(fr); f=json.dumps(fb,sort_keys=True,separators=(",",":")).encode(); (root/"fb.json").write_bytes(f); hs[1]=h(f)
            with self.assertRaises(PreflightError): self.run_pf(td,hs)

if __name__=="__main__": unittest.main()
