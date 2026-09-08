"""Synthetic-only source contracts. No file reader, execution driver or authorization.

Inputs are already-normalized in-memory structures. Production must independently
verify source bytes, normalization, correction inventory and accepted cohort identity.
These functions do not certify those upstream obligations.
"""


class ContractError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise ContractError(code)


def identifiers(values):
    require(type(values) is list and bool(values), 'E-S-001')
    require(all(type(x) is str and bool(x.strip()) for x in values), 'E-S-002')
    require(len(set(values)) == len(values), 'E-S-003')


def evidence(value):
    # Deliberately no coercion: historical normalization belongs upstream.
    require(type(value) is list, 'E-S-004')
    require(all(type(x) is str and bool(x.strip()) for x in value), 'E-S-005')
    return list(dict.fromkeys(value))


def resolve_locomo_gold(bound_ids, raw_evidence, corrections, rows_by_question):
    """Resolve only fixed cohort IDs. Present-but-empty correction never falls back.

raw_evidence: qid -> normalized reference list.
corrections: qid -> dict, optional correct_evidence normalized reference list.
rows_by_question: qid -> archive reference-ID-to-row mapping.
Extra correction entries are permitted (full historical correction inventory).
No question is dropped and no source structure is mutated.
"""
    identifiers(bound_ids)
    require(all(type(x) is dict for x in (raw_evidence, corrections, rows_by_question)), 'E-S-006')
    require(set(raw_evidence) == set(bound_ids) == set(rows_by_question), 'E-S-007')
    result = {}
    for qid in bound_ids:
        correction = corrections.get(qid, {})
        require(type(correction) is dict, 'E-S-008')
        corrected = 'correct_evidence' in correction
        refs = evidence(correction['correct_evidence'] if corrected else raw_evidence[qid])
        require(bool(refs), 'E-S-009')
        mapping = rows_by_question[qid]
        require(type(mapping) is dict and bool(mapping), 'E-S-010')
        require(all(type(k) is str and type(v) is int and v >= 0 for k, v in mapping.items()), 'E-S-011')
        require(len(set(mapping.values())) == len(mapping), 'E-S-012')
        require(set(mapping.values()) == set(range(len(mapping))), 'E-S-013')
        require(all(ref in mapping for ref in refs), 'E-S-014')
        result[qid] = {'gold_rows': [mapping[ref] for ref in refs],
                       'evidence_declared': len(refs), 'evidence_unresolved': 0,
                       'correction_applied': corrected}
    return result


def longmemeval_plan(source_ids, bound_ids, *, expected_source=500, expected_primary=470):
    """Lexical ordinal over ALL source IDs; shards over source-order primary IDs.

Counts may be reduced only by synthetic callers. This pure helper does not
constitute a production gate. Exactly ten shards; no new nuisance seed rule.
"""
    identifiers(source_ids)
    identifiers(bound_ids)
    require(type(expected_source) is int and type(expected_primary) is int
            and expected_source >= expected_primary > 0, 'E-S-015')
    require(len(source_ids) == expected_source and len(bound_ids) == expected_primary, 'E-S-016')
    primary = [qid for qid in source_ids if not qid.endswith('_abs')]
    require(len(primary) == expected_primary and set(primary) == set(bound_ids), 'E-S-017')
    lexical = {qid: i for i, qid in enumerate(sorted(source_ids))}
    return [{'question_id': qid, 'archive_ordinal': lexical[qid],
             'primary_position': i, 'shard_index': i % 10}
            for i, qid in enumerate(primary)]


def run_on_real_corpus(*args, **kwargs):
    raise ContractError('E-S-018')
