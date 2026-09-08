"""User-approved historical-six-reference exception, one exact source case."""
import hashlib
import json

QID = 'locomo_4_qa18'
REFS_HASH = 'eb2c9923e8d466be272dda586b6c90141a28b38b90bbf6c0c8f35ae5efb4a0b8'
MISSING_HASH = '5c2956ff44b1faadb3da64535fafa03d2a108d3433b63cfd5eb0498441b6b2d8'
ARCHIVE_HASH = '27b820ad8692af465dc9578925bf426ce81d2d455855e751bc1e1d01d222f001'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


def resolve_with_exception(contract, ids, raw, corrections, maps):
    contract.identifiers(ids)
    contract.require(all(type(x) is dict for x in (raw, corrections, maps)), 'E-X-001')
    contract.require(QID in ids and set(raw) == set(maps) == set(ids), 'E-X-002')
    contract.require(QID not in corrections, 'E-X-003')
    refs = contract.evidence(raw[QID])
    mapping = maps[QID]
    contract.require(type(mapping) is dict and len(mapping) == 680, 'E-X-004')
    contract.require(all(type(k) is str and type(v) is int for k, v in mapping.items()), 'E-X-004')
    contract.require(set(mapping.values()) == set(range(680)), 'E-X-004')
    ordered = sorted(mapping, key=mapping.get)
    contract.require(digest(ordered) == ARCHIVE_HASH, 'E-X-005')
    contract.require(len(refs) == 7 and digest(refs) == REFS_HASH, 'E-X-006')
    missing = [ref for ref in refs if ref not in mapping]
    retained = [ref for ref in refs if ref in mapping]
    contract.require(len(missing) == 1 and digest(missing) == MISSING_HASH
                     and len(retained) == 6, 'E-X-007')
    adjusted = dict(raw)
    adjusted[QID] = retained
    # Old core and source contract are unmodified; all other questions stay strict.
    result = contract.resolve_locomo_gold(ids, adjusted, corrections, maps)
    result[QID]['evidence_declared_original'] = 7
    result[QID]['evidence_unresolved_original'] = 1
    result[QID]['authorized_omitted_reference_count'] = 1
    result[QID]['gold_exception'] = 'USER_APPROVED_HISTORICAL_SIX_REFERENCES'
    return result
