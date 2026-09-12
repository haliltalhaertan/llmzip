import hashlib,json,os,tempfile
from pathlib import Path
from storage_adapter_preflight_v3 import preflight, PreflightError
def h(r): return hashlib.sha256(r).hexdigest()
td=tempfile.mkdtemp(); root=Path(td)
fx={"schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V3","transform":{"input_utf8":"h"},
    "id_mapping":{"rows":[{"logical_id":"a","offset":0,"payload_utf8":"A"},{"logical_id":"b","offset":1,"payload_utf8":"B"}]},
    "corruption":{"strategy":"XOR_SINGLE_BYTE","byte_offset":0,"xor_mask":1}}
fr=json.dumps(fx,sort_keys=True,separators=(",",":")).encode(); (root/"fx.json").write_bytes(fr)
os.mkfifo(root/"pipe")                      # <-- a FIFO, not a regular file
plan={"schema":"v52.static-storage-plan","version":1,"fixtures":[{"id":"fx1","sha256":h(fr)}],
 "physical_copies":[{"id":"pc1","artifact_sha256":h(b"X"),"population_ids":["p1"]}],
 "populations":[{"id":"p1","count":4}]}
fb={"schema":"v52.fixture-bindings","version":3,"fixtures":[{"fixture_id":"fx1","relative_path":"fx.json","byte_length":len(fr),"sha256":h(fr),"content_schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V3","consumer_sections":{"TRANSFORM":"transform","ID_MAPPING":"id_mapping","CORRUPT":"corruption"}}]}
pb={"schema":"v52.physical-copy-bindings","version":3,"physical_copies":[{"physical_copy_id":"pc1","physical_locator":"pipe","source_raw_byte_length":1,"artifact_sha256":h(b"X"),"sharing_denominator_rule":"POPULATION_COUNT"}]}
def w(n,o):
    raw=json.dumps(o,sort_keys=True,separators=(",",":")).encode(); (root/n).write_bytes(raw); return h(raw)
hp,hf,hb=w("plan.json",plan),w("fb.json",fb),w("pb.json",pb)
print("calling preflight with physical_locator -> FIFO ...",flush=True)
try: preflight(root/"plan.json",hp,root/"fb.json",hf,root/"pb.json",hb); print("ACCEPTED")
except PreflightError as e: print("REJECTED:",e)
print("RETURNED")
