"""V52 static-storage external binding preflight V3.

Preparation-only. Authenticates declaration and synthetic/source bytes without
authorizing storage measurement, model fitting, retrieval, or Task4F1 access.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, math, re
from pathlib import Path

MAX_DECLARATION_BYTES = 1_048_576
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_ENTITIES = 4096
MAX_DEPTH = 24
FIXTURE_BINDING_SCHEMA = "v52.fixture-bindings"
PHYSICAL_BINDING_SCHEMA = "v52.physical-copy-bindings"
FIXTURE_CONTENT_SCHEMA = "V52_SYNTHETIC_FIXTURE_BUNDLE_V2"
OPERATION_SECTIONS = {"TRANSFORM":"transform","ID_MAPPING":"id_mapping","CORRUPT":"corruption"}

class PreflightError(ValueError): pass

def need(c,m):
    if not c: raise PreflightError(m)
def fields(v,n,w): need(type(v) is dict and set(v)==set(n.split()), f"{w}: exact fields required: {n}")
def text(v,w): need(type(v) is str and bool(v.strip()) and len(v)<=4096, f"{w}: nonblank bounded string required")
def integer(v,w,minimum=0,maximum=2**63-1): need(type(v) is int and minimum<=v<=maximum, f"{w}: integer in [{minimum},{maximum}] required")
def digest(v,w): need(type(v) is str and re.fullmatch(r"[0-9a-f]{64}",v) is not None, f"{w}: lowercase SHA256 required")

def _pairs(pairs):
    out={}
    for k,v in pairs:
        need(k not in out, f"duplicate JSON key: {k}"); out[k]=v
    return out

def _bounded(v,d=0):
    need(d<=MAX_DEPTH,"JSON nesting limit")
    if type(v) is dict:
        need(len(v)<=MAX_ENTITIES,"JSON object limit")
        for k,x in v.items(): text(k,"JSON key"); _bounded(x,d+1)
    elif type(v) is list:
        need(len(v)<=MAX_ENTITIES,"JSON array limit")
        for x in v: _bounded(x,d+1)
    elif type(v) is str: need(len(v)<=4096,"JSON string limit")
    elif v is None or type(v) is bool: return
    elif type(v) in (int,float): need(math.isfinite(v) and abs(v)<=2**63-1,"numeric limit")
    else: raise PreflightError("non-JSON value")
def decode_json(raw,where):
    try:
        v=json.loads(raw.decode("utf-8"),object_pairs_hook=_pairs,
                     parse_constant=lambda t: (_ for _ in ()).throw(PreflightError(f"{where}: nonfinite JSON constant {t}")))
    except (UnicodeError,ValueError,RecursionError) as e:
        if isinstance(e,PreflightError): raise
        raise PreflightError(f"{where}: invalid JSON: {e}") from e
    _bounded(v); need(type(v) is dict,f"{where}: object required"); return v

def read_bytes(path,limit):
    p=Path(path)
    with p.open("rb") as s: raw=s.read(limit+1)
    need(len(raw)<=limit,f"{p}: file byte limit"); return raw
def authenticate(path,expected,where,artifact=False):
    digest(expected,f"{where} expected SHA256")
    raw=read_bytes(path,MAX_ARTIFACT_BYTES if artifact else MAX_DECLARATION_BYTES)
    need(hashlib.sha256(raw).hexdigest()==expected,f"{where}: SHA256 mismatch"); return raw
def safe_child(base_dir,relative_path,where):
    text(relative_path,where); rel=Path(relative_path)
    need(not rel.is_absolute() and ".." not in rel.parts,f"{where}: path must stay below binding directory")
    base=Path(base_dir).resolve(); child=(base/rel).resolve()
    try: child.relative_to(base)
    except ValueError as e: raise PreflightError(f"{where}: path escapes binding directory") from e
    return child
def unique_index(rows,where,id_key="id"):
    need(type(rows) is list,f"{where}: list required"); out={}
    for row in rows:
        need(type(row) is dict and id_key in row,f"{where}: {id_key} required")
        key=row[id_key]; text(key,f"{where} {id_key}"); need(key not in out,f"{where}: duplicate id {key}"); out[key]=row
    return out

def validate_fixture_payload(p):
    fields(p,"schema transform id_mapping corruption","fixture artifact"); need(p["schema"]==FIXTURE_CONTENT_SCHEMA,"fixture artifact schema mismatch")
    fields(p["transform"],"input_utf8","fixture transform"); text(p["transform"]["input_utf8"],"transform input_utf8")
    fields(p["id_mapping"],"logical_id offset payload_utf8","fixture id_mapping"); text(p["id_mapping"]["logical_id"],"id_mapping logical_id"); integer(p["id_mapping"]["offset"],"id_mapping offset"); text(p["id_mapping"]["payload_utf8"],"id_mapping payload_utf8")
    fields(p["corruption"],"target_kind target_id byte_offset xor_mask","fixture corruption"); need(p["corruption"]["target_kind"] in ("FIXTURE","PHYSICAL_COPY"),"corruption target_kind"); text(p["corruption"]["target_id"],"corruption target_id"); integer(p["corruption"]["byte_offset"],"corruption byte_offset"); integer(p["corruption"]["xor_mask"],"corruption xor_mask",1,255)

@dataclass(frozen=True)
class VerifiedFixture:
    fixture_id:str; raw_bytes:bytes; sha256:str; byte_length:int
@dataclass(frozen=True)
class VerifiedPhysicalCopy:
    physical_copy_id:str; raw_bytes:bytes; sha256:str; byte_length:int; denominator_states:tuple
@dataclass(frozen=True)
class VerifiedBindings:
    plan_sha256:str; fixture_bindings_sha256:str; physical_bindings_sha256:str; fixtures:tuple; physical_copies:tuple

def verify_fixture_artifact(binding_dir,plan_fixture,binding):
    fields(binding,"fixture_id relative_path byte_length sha256 content_schema operation_sections","fixture binding")
    need(binding["fixture_id"]==plan_fixture["id"],"fixture id mismatch"); integer(binding["byte_length"],"fixture byte_length",1); digest(binding["sha256"],"fixture binding SHA256"); need(binding["sha256"]==plan_fixture["sha256"],"fixture SHA disagrees with plan"); need(binding["content_schema"]==FIXTURE_CONTENT_SCHEMA,"fixture content schema mismatch")
    fields(binding["operation_sections"],"TRANSFORM ID_MAPPING CORRUPT","fixture operation_sections"); need(binding["operation_sections"]==OPERATION_SECTIONS,"fixture operation/subfixture mapping mismatch")
    artifact=safe_child(binding_dir,binding["relative_path"],"fixture relative_path"); raw=read_bytes(artifact,MAX_ARTIFACT_BYTES); need(len(raw)==binding["byte_length"],"fixture byte length mismatch"); need(hashlib.sha256(raw).hexdigest()==binding["sha256"],"fixture artifact SHA mismatch")
    validate_fixture_payload(decode_json(raw,"fixture artifact")); return VerifiedFixture(plan_fixture["id"],raw,binding["sha256"],len(raw))

def verify_physical_artifact(binding_dir,plan_copy,binding,populations):
    fields(binding,"physical_copy_id physical_locator source_raw_byte_length artifact_sha256 sharing_denominator_rule","physical binding")
    need(binding["physical_copy_id"]==plan_copy["id"],"physical copy id mismatch"); integer(binding["source_raw_byte_length"],"source raw byte length",0); digest(binding["artifact_sha256"],"physical artifact SHA256"); need(binding["artifact_sha256"]==plan_copy["artifact_sha256"],"physical binding SHA disagrees with plan"); need(binding["sharing_denominator_rule"]=="POPULATION_COUNT","unsupported sharing denominator rule")
    artifact=safe_child(binding_dir,binding["physical_locator"],"physical locator"); raw=read_bytes(artifact,MAX_ARTIFACT_BYTES); need(len(raw)==binding["source_raw_byte_length"],"physical source length mismatch"); need(hashlib.sha256(raw).hexdigest()==binding["artifact_sha256"],"physical source SHA mismatch")
    states=[]
    for pop_id in plan_copy["population_ids"]:
        need(pop_id in populations,f"unknown population {pop_id}"); count=populations[pop_id]["count"]; integer(count,f"population {pop_id} count")
        states.append((pop_id,"EMPTY_NO_AMORTIZATION",None) if count==0 else (pop_id,"POSITIVE",count))
    return VerifiedPhysicalCopy(plan_copy["id"],raw,binding["artifact_sha256"],len(raw),tuple(states))

def preflight(plan_path,expected_plan_sha256,fixture_bindings_path,expected_fixture_bindings_sha256,physical_bindings_path,expected_physical_bindings_sha256):
    plan=decode_json(authenticate(plan_path,expected_plan_sha256,"plan"),"plan"); need(plan.get("schema")=="v52.static-storage-plan" and plan.get("version")==1,"schema-1 plan required")
    plan_fixtures=unique_index(plan.get("fixtures"),"plan fixtures"); plan_copies=unique_index(plan.get("physical_copies"),"plan physical copies"); populations=unique_index(plan.get("populations"),"plan populations")
    fdoc=decode_json(authenticate(fixture_bindings_path,expected_fixture_bindings_sha256,"fixture bindings"),"fixture bindings"); fields(fdoc,"schema version fixtures","fixture bindings"); need(fdoc["schema"]==FIXTURE_BINDING_SCHEMA and fdoc["version"]==2,"fixture bindings schema/version"); fixture_bindings=unique_index(fdoc["fixtures"],"fixture bindings","fixture_id"); need(set(fixture_bindings)==set(plan_fixtures),"fixture binding coverage must equal plan fixture roster")
    pdoc=decode_json(authenticate(physical_bindings_path,expected_physical_bindings_sha256,"physical bindings"),"physical bindings"); fields(pdoc,"schema version physical_copies","physical bindings"); need(pdoc["schema"]==PHYSICAL_BINDING_SCHEMA and pdoc["version"]==2,"physical bindings schema/version"); physical_bindings=unique_index(pdoc["physical_copies"],"physical bindings","physical_copy_id"); need(set(physical_bindings)==set(plan_copies),"physical binding coverage must equal plan physical-copy roster")
    vf=tuple(verify_fixture_artifact(Path(fixture_bindings_path).resolve().parent,plan_fixtures[i],fixture_bindings[i]) for i in plan_fixtures)
    vc=tuple(verify_physical_artifact(Path(physical_bindings_path).resolve().parent,plan_copies[i],physical_bindings[i],populations) for i in plan_copies)
    return VerifiedBindings(expected_plan_sha256,expected_fixture_bindings_sha256,expected_physical_bindings_sha256,vf,vc)
