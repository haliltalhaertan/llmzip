"""Strict wrapper validation; immutable core is never responsible for sanitizing IDs."""
import math

FIELDS = frozenset(('question_id', 'rotation_seed', 'arm', 'fractional_R3'))


def valid_records(records, question_ids, seeds, arms):
    if (type(question_ids) is not list or not question_ids
            or any(type(q) is not str for q in question_ids)
            or len(set(question_ids)) != len(question_ids)
            or type(records) is not list or not records):
        return False
    expected = {(q, s, a) for q in question_ids for s in seeds for a in arms}
    seen = set()
    for record in records:
        if type(record) is not dict or set(record) != FIELDS:
            return False
        q, s, a, v = (record[k] for k in ('question_id', 'rotation_seed', 'arm', 'fractional_R3'))
        if (type(q) is not str or type(s) is not int or type(a) is not str
                or type(v) not in (int, float)):
            return False
        if not math.isfinite(v) or not 0 <= v <= 1:
            return False
        key = q, s, a
        if key not in expected or key in seen:
            return False
        seen.add(key)
    return seen == expected
