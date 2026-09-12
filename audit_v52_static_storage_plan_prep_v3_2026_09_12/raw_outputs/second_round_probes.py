import hashlib,json,tempfile,os
from pathlib import Path
from storage_adapter_preflight_v3 import preflight, PreflightError
def h(r): return hashlib.sha256(r).hexdigest()
def build(root, plan_mut=None, fb_mut=None, pb_mut=None, extra=None):
    root=Path(root)
    fx={"schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V3","transform":{"input_utf8":"h"},
        "id_mapping":{"rows":[{"logical_id":"a","offset":0,"payload_utf8":"A"},{"logical_id":"b","offset":1,"payload_utf8":"B"}]},
        "corruption":{"strategy":"XOR_SINGLE_BYTE","byte_offset":0,"xor_mask":1}}
    fr=json.dumps(fx,sort_keys=True,separators=(",",":")).encode(); (root/"fx.json").write_bytes(fr)
    (root/"phys.bin").write_bytes(b"PHYS")
    if extra: extra(root)
    plan={"schema":"v52.static-storage-plan","version":1,"fixtures":[{"id":"fx1","sha256":h(fr)}],
     "physical_copies":[{"id":"pc1","artifact_sha256":h(b"PHYS"),"population_ids":["p1"]}],
     "populations":[{"id":"p1","count":4}]}
    if plan_mut: plan_mut(plan)
    fb={"schema":"v52.fixture-bindings","version":3,"fixtures":[{"fixture_id":"fx1","relative_path":"fx.json","byte_length":len(fr),"sha256":h(fr),"content_schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V3","consumer_sections":{"TRANSFORM":"transform","ID_MAPPING":"id_mapping","CORRUPT":"corruption"}}]}
    if fb_mut: fb_mut(fb)
    pb={"schema":"v52.physical-copy-bindings","version":3,"physical_copies":[{"physical_copy_id":"pc1","physical_locator":"phys.bin","source_raw_byte_length":4,"artifact_sha256":h(b"PHYS"),"sharing_denominator_rule":"POPULATION_COUNT"}]}
    if pb_mut: pb_mut(pb)
    def w(n,o):
        raw=json.dumps(o,sort_keys=True,separators=(",",":")).encode(); (root/n).write_bytes(raw); return h(raw)
    return w("plan.json",plan),w("fb.json",fb),w("pb.json",pb)
def run(name,**kw):
    with tempfile.TemporaryDirectory() as td:
        try:
            hs=build(td,**kw)
            o=preflight(Path(td)/"plan.json",hs[0],Path(td)/"fb.json",hs[1],Path(td)/"pb.json",hs[2])
            r=f"ACCEPTED copies={len(o.physical_copies)} states={o.physical_copies[0].denominator_states if o.physical_copies else ()}"
        except PreflightError as e: r=f"REJECTED(PreflightError) {str(e)[:60]}"
        except Exception as e: r=f"LEAK({type(e).__name__}) {str(e)[:60]}"
    print(f"{name:<52} {r}")

print("--- NEW-3: uncaught OSError/ValueError from companion docs ---")
run("relative_path = '.' (a directory)", fb_mut=lambda d: d["fixtures"][0].update(relative_path="."))
run("relative_path with embedded NUL",   fb_mut=lambda d: d["fixtures"][0].update(relative_path="a\x00b"))
run("physical_locator = '.' (a directory)", pb_mut=lambda d: d["physical_copies"][0].update(physical_locator="."))
print("--- NEW-4: how many candidate D_k does ONE copy emit? ---")
run("copy bound to 4 populations",
    plan_mut=lambda p:(p["physical_copies"][0].update(population_ids=["p1","p2","p3","p4"]),
                       p.update(populations=[{"id":"p1","count":0},{"id":"p2","count":1},
                                             {"id":"p3","count":1000000000},{"id":"p4","count":4}])))
print("--- NEW-6: version field type confusion ---")
run("plan version = True (bool)",  plan_mut=lambda p: p.update(version=True))
run("plan version = 1.0 (float)",  plan_mut=lambda p: p.update(version=1.0))
run("plan version = 2 (control)",  plan_mut=lambda p: p.update(version=2))
print("--- NEW-7: two physical copies bound to the SAME file ---")
run("pc1 and pc2 both -> phys.bin",
    plan_mut=lambda p: p["physical_copies"].append({"id":"pc2","artifact_sha256":h(b"PHYS"),"population_ids":["p1"]}),
    pb_mut=lambda d: d["physical_copies"].append({"physical_copy_id":"pc2","physical_locator":"phys.bin","source_raw_byte_length":4,"artifact_sha256":h(b"PHYS"),"sharing_denominator_rule":"POPULATION_COUNT"}))
print("--- NEW-5: is there ANY aggregate byte cap in the module? ---")
import storage_adapter_preflight_v3 as m
print("   caps present:", [k for k in dir(m) if k.startswith("MAX_")])
