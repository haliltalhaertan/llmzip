'''V52 static-storage V8 trusted-consumption repair. Preparation-only, LongMemEval-only.'''
from __future__ import annotations
from pathlib import Path
from typing import NamedTuple
import v8_runtime as rt
import v8_snapshot as snap


def _load_pinned_chain():
    v7=rt.exec_pinned_module('v7_semantic_gate',rt.V7_PATH,rt.V7_SOURCE_SHA256)
    guard=rt.exec_pinned_module('measurement_plan_guard',rt.PARENT_GUARD_PATH,rt.PARENT_GUARD_SHA256)
    v6=rt.exec_pinned_module('storage_adapter_preflight_v6',rt.V6_PATH,rt.V6_PREFLIGHT_SHA256)
    rt.authenticate_fixed(rt.CONTRACT_PATH,rt.CONTRACT_SHA256,'measurement contract')
    expected=(('PARENT_GUARD_SHA256',rt.PARENT_GUARD_SHA256),('CONTRACT_SHA256',rt.CONTRACT_SHA256),
      ('V6_PREFLIGHT_SHA256',rt.V6_PREFLIGHT_SHA256),('LONGMEMEVAL_ANCHOR_SHA256',rt.LONGMEMEVAL_ANCHOR_SHA256),
      ('LONGMEMEVAL_ID_COLUMN',rt.LONGMEMEVAL_ID_COLUMN),('LONGMEMEVAL_VALUE_COLUMN',rt.LONGMEMEVAL_VALUE_COLUMN),
      ('LONGMEMEVAL_EXPECTED_ROWS',rt.LONGMEMEVAL_EXPECTED_ROWS))
    for name,value in expected: rt.need(getattr(v7,name,None)==value,f'pinned V7 semantic constant {name} disagrees with V8')
    return v7,guard,v6

def _fresh_preflight(plan_path,plan_sha,fixture_path,fixture_sha,physical_path,physical_sha):
    rt.digest(plan_sha,'expected plan SHA256'); rt.digest(fixture_sha,'expected fixture bindings SHA256'); rt.digest(physical_sha,'expected physical bindings SHA256')
    v7,guard,v6=_load_pinned_chain()
    try: gp=guard.load_plan(plan_path,plan_sha,rt.CONTRACT_PATH)
    except Exception as e: raise rt.V8ValidationError(f'pinned parent guard refused: {e.__class__.__name__}: {e}') from e
    rt.need(type(gp) is guard.Plan,'parent guard did not return exact Plan type'); rt.need(gp.contract_sha256==rt.CONTRACT_SHA256,'guarded Plan contract digest disagrees with V8')
    try:
        anchor=v7.load_longmemeval_anchor(); proof=v7._verify_plan_data_against_anchor(gp.data,anchor)
    except Exception as e: raise rt.V8ValidationError(f'pinned V7 semantic anchor refused: {e.__class__.__name__}: {e}') from e
    try:
        verified=v6.preflight(plan_path,gp.sha256,rt.CONTRACT_PATH,gp.contract_sha256,fixture_path,fixture_sha,physical_path,physical_sha,gp.sha256,gp.contract_sha256,proof.denominator_map())
    except Exception as e: raise rt.V8ValidationError(f'pinned V6 preflight refused: {e.__class__.__name__}: {e}') from e
    return snap.freeze_verified_bindings(proof,verified,gp.sha256,gp.contract_sha256,fixture_sha,physical_sha)

class V8Context(NamedTuple):
    plan_path:str; expected_plan_sha256:str; fixture_bindings_path:str; expected_fixture_bindings_sha256:str
    physical_bindings_path:str; expected_physical_bindings_sha256:str; initial_snapshot:snap.FreshSnapshot
    def refresh(self):
        return _fresh_preflight(self.plan_path,self.expected_plan_sha256,self.fixture_bindings_path,self.expected_fixture_bindings_sha256,self.physical_bindings_path,self.expected_physical_bindings_sha256)
    def authoritative_denominators(self): return self.refresh().semantic_proof.denominators

def preflight_longmemeval_v8(plan_path,expected_plan_sha256,fixture_bindings_path,expected_fixture_bindings_sha256,physical_bindings_path,expected_physical_bindings_sha256):
    s=_fresh_preflight(plan_path,expected_plan_sha256,fixture_bindings_path,expected_fixture_bindings_sha256,physical_bindings_path,expected_physical_bindings_sha256)
    return V8Context(str(Path(plan_path)),expected_plan_sha256,str(Path(fixture_bindings_path)),expected_fixture_bindings_sha256,str(Path(physical_bindings_path)),expected_physical_bindings_sha256,s)
