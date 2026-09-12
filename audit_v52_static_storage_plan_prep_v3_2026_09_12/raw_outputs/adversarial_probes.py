import hashlib, json, tempfile, traceback
from pathlib import Path
from storage_adapter_preflight_v3 import preflight, PreflightError
def h(r): return hashlib.sha256(r).hexdigest()
def w(root,name,obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode(); (Path(root)/name).write_bytes(raw); return raw

def base(root, plan_mut=None, fb_mut=None, pb_mut=None, fx_mut=None, phys=b"PHYS"):
    root=Path(root)
    fx={"schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V3","transform":{"input_utf8":"hello"},
        "id_mapping":{"rows":[{"logical_id":"a","offset":0,"payload_utf8":"A"},{"logical_id":"b","offset":1,"payload_utf8":"B"}]},
        "corruption":{"strategy":"XOR_SINGLE_BYTE","byte_offset":0,"xor_mask":1}}
    if fx_mut: fx_mut(fx)
    fr=json.dumps(fx,sort_keys=True,separators=(",",":")).encode(); (root/"fx.json").write_bytes(fr)
    (root/"phys.bin").write_bytes(phys)
    plan={"schema":"v52.static-storage-plan","version":1,
          "fixtures":[{"id":"fx1","sha256":h(fr)}],
          "physical_copies":[{"id":"pc1","artifact_sha256":h(phys),"population_ids":["p1"]}],
          "populations":[{"id":"p1","count":4}]}
    if plan_mut: plan_mut(plan)
    fb={"schema":"v52.fixture-bindings","version":3,"fixtures":[{"fixture_id":"fx1","relative_path":"fx.json","byte_length":len(fr),"sha256":h(fr),"content_schema":"V52_SYNTHETIC_FIXTURE_BUNDLE_V3","consumer_sections":{"TRANSFORM":"transform","ID_MAPPING":"id_mapping","CORRUPT":"corruption"}}]}
    if fb_mut: fb_mut(fb)
    pb={"schema":"v52.physical-copy-bindings","version":3,"physical_copies":[{"physical_copy_id":"pc1","physical_locator":"phys.bin","source_raw_byte_length":len(phys),"artifact_sha256":h(phys),"sharing_denominator_rule":"POPULATION_COUNT"}]}
    if pb_mut: pb_mut(pb)
    p=w(root,"plan.json",plan); f=w(root,"fb.json",fb); b=w(root,"pb.json",pb)
    return h(p),h(f),h(b)

def probe(name, expect, **kw):
    with tempfile.TemporaryDirectory() as td:
        try:
            hs=base(td,**kw)
            out=preflight(Path(td)/"plan.json",hs[0],Path(td)/"fb.json",hs[1],Path(td)/"pb.json",hs[2])
            got="ACCEPTED"; detail=f"fixtures={len(out.fixtures)} copies={len(out.physical_copies)} states={out.physical_copies[0].denominator_states if out.physical_copies else ()}"
        except PreflightError as e: got="REJECTED(PreflightError)"; detail=str(e)[:90]
        except Exception as e: got=f"CRASH({type(e).__name__})"; detail=str(e)[:90]
    flag = "  <-- FINDING" if got.split("(")[0]!=expect else ""
    print(f"{name:<46} {got:<26} {detail}{flag}")

print("=== A. empty rosters ===")
def empt(p): p["fixtures"]=[]; p["physical_copies"]=[]; p["populations"]=[]
probe("A1 empty plan rosters","REJECTED",plan_mut=empt,fb_mut=lambda d:d.update(fixtures=[]),pb_mut=lambda d:d.update(physical_copies=[]))
print("=== B. plan schema laxity ===")
probe("B1 plan carries arbitrary extra top keys","REJECTED",plan_mut=lambda p:p.update(evil="anything",probes=None))
probe("B2 plan has NO probes/archives/items key","REJECTED")
print("=== C. plan entry field validation ===")
probe("C1 plan fixture missing sha256","REJECTED",plan_mut=lambda p:p["fixtures"][0].pop("sha256"))
probe("C2 plan copy missing population_ids","REJECTED",plan_mut=lambda p:p["physical_copies"][0].pop("population_ids"))
probe("C3 population entry missing count","REJECTED",plan_mut=lambda p:p["populations"][0].pop("count"))
probe("C4 population_ids not a list (string)","REJECTED",plan_mut=lambda p:p["physical_copies"][0].update(population_ids="p1"))
print("=== D. denominator semantics ===")
probe("D1 D_k declared 10,000,000 (dilution)","REJECTED",plan_mut=lambda p:p["populations"][0].update(count=10_000_000))
probe("D2 duplicate population_ids in one copy","REJECTED",plan_mut=lambda p:p["physical_copies"][0].update(population_ids=["p1","p1"]))
print("=== E. control vacuity ===")
probe("E1 corruption byte_offset beyond artifact","REJECTED",fx_mut=lambda f:f["corruption"].update(byte_offset=10**12))
print("=== F. zero-byte artifact ===")
probe("F1 physical artifact is zero bytes","REJECTED",phys=b"")
