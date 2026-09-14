from __future__ import annotations
import hashlib
from typing import NamedTuple
import v8_runtime as rt

class SemanticProof(NamedTuple):
    anchor_sha256:str; source_identity:str; archive_ids:tuple; authoritative_probe_ids:tuple; denominators:tuple
class FixtureSnapshot(NamedTuple):
    fixture_id:str; raw_bytes:bytes; sha256:str; byte_length:int
class PhysicalSnapshot(NamedTuple):
    physical_copy_id:str; raw_bytes:bytes; sha256:str; source_byte_length:int; population_id:str; denominator:int
class FreshSnapshot(NamedTuple):
    plan_sha256:str; contract_sha256:str; fixture_bindings_sha256:str; physical_bindings_sha256:str
    semantic_proof:SemanticProof; fixtures:tuple; physical_copies:tuple

def normalize_proof(p):
    return SemanticProof(str(p.anchor_sha256),str(p.source_identity),tuple(str(x) for x in p.archive_ids),
        tuple((str(a),str(q)) for a,q in p.authoritative_probe_ids),tuple((str(c),str(pop),int(d)) for c,pop,d in p.denominators))

def freeze_verified_bindings(proof,verified,plan_sha,contract_sha,fixture_sha,physical_sha):
    proof=normalize_proof(proof); pmap={c:(p,d) for c,p,d in proof.denominators}
    fixtures=[]
    for row in tuple(verified.fixtures):
        raw=row.reverify(); rt.need(type(raw) is bytes,f'fixture {row.fixture_id}: bytes required')
        rt.need(hashlib.sha256(raw).hexdigest()==row.sha256,f'fixture {row.fixture_id}: digest mismatch at freeze')
        rt.need(len(raw)==row.byte_length,f'fixture {row.fixture_id}: byte length mismatch at freeze')
        fixtures.append(FixtureSnapshot(str(row.fixture_id),bytes(raw),str(row.sha256),int(row.byte_length)))
    physicals=[]; seen=set()
    for row in tuple(verified.physical_copies):
        cid=str(row.physical_copy_id); rt.need(cid not in seen,f'duplicate physical copy {cid}'); seen.add(cid)
        rt.need(cid in pmap,f'physical copy {cid}: no semantic denominator'); raw=row.reverify()
        rt.need(type(raw) is bytes,f'physical copy {cid}: bytes required')
        rt.need(hashlib.sha256(raw).hexdigest()==row.sha256,f'physical copy {cid}: digest mismatch at freeze')
        rt.need(len(raw)==row.source_byte_length,f'physical copy {cid}: byte length mismatch at freeze')
        rt.need(type(row.denominator) is tuple and len(row.denominator)==2,f'physical copy {cid}: denominator pair required')
        pair=(str(row.denominator[0]),int(row.denominator[1]))
        rt.need(pair==pmap[cid],f'physical copy {cid}: V6 denominator disagrees with pinned semantic proof')
        physicals.append(PhysicalSnapshot(cid,bytes(raw),str(row.sha256),int(row.source_byte_length),pair[0],pair[1]))
    rt.need(seen==set(pmap),'semantic denominator coverage must equal verified physical-copy roster')
    return FreshSnapshot(str(plan_sha),str(contract_sha),str(fixture_sha),str(physical_sha),proof,tuple(fixtures),tuple(physicals))
