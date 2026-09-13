"""EXPLICITLY MALICIOUS test double. NEVER part of any gate, V10, or shipment.

Simulates an attacker-controlled ``v8_snapshot`` dependency: whatever the
verified chain produced, freezing returns an attacker-chosen snapshot whose
logical denominator is inflated to 10**9.
"""

from typing import NamedTuple


class SemanticProof(NamedTuple):
    anchor_sha256: str
    source_identity: str
    archive_ids: tuple
    authoritative_probe_ids: tuple
    denominators: tuple


class FreshSnapshot(NamedTuple):
    plan_sha256: str
    contract_sha256: str
    fixture_bindings_sha256: str
    physical_bindings_sha256: str
    semantic_proof: SemanticProof
    fixtures: tuple
    physical_copies: tuple


ATTACK_PROOF = SemanticProof(
    anchor_sha256="f" * 64,
    source_identity="attacker",
    archive_ids=("a",),
    authoritative_probe_ids=(("a", "q"),),
    denominators=(("copy-x", "pop-x", 10 ** 9),),
)


def normalize_proof(p):
    return p


def freeze_verified_bindings(proof, verified, plan_sha, contract_sha,
                             fixture_sha, physical_sha):
    return FreshSnapshot(str(plan_sha), str(contract_sha), str(fixture_sha),
                         str(physical_sha), ATTACK_PROOF, (), ())
