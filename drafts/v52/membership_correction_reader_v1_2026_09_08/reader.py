"""Fail-closed correction-byte reader. Synthetic preparation, not production IO.

Caller supplies expected identities and bytes. Matching them authenticates only
against that supplied inventory, not against an accepted experiment manifest.
No files, networks, models or historical outcomes are read by this module.
"""
import hashlib
import json
import math
import re


class ReaderError(ValueError):
    pass


def _need(condition, code):
    if not condition:
        raise ReaderError(code)


def _label(value):
    return type(value) is str and bool(value.strip()) and value == value.strip()


def _object(pairs):
    result = {}
    for key, value in pairs:
        _need(key not in result, 'E-R-007')
        result[key] = value
    return result


def _constant(value):
    raise ReaderError('E-R-008')


def _float(value):
    parsed = float(value)
    _need(math.isfinite(parsed), 'E-R-008')
    return parsed


def _parse_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_object,
                      parse_constant=_constant, parse_float=_float)


def _evidence(value):
    if value is None:
        return []
    if type(value) is str:
        _need(bool(value.strip()), 'E-R-013')
        return list(dict.fromkeys(re.findall(r'D\d+:\d+', value) or [value]))
    _need(type(value) is list, 'E-R-013')
    result = []
    for item in value:
        if type(item) is str:
            _need(bool(item.strip()), 'E-R-013')
            result.extend(re.findall(r'D\d+:\d+', item) or [item])
        elif type(item) is dict:
            # Do not coerce numbers or choose between conflicting aliases.
            ids = [item[k] for k in ('dia_id', 'id') if k in item]
            _need(bool(ids) and all(type(x) is str and bool(x.strip()) for x in ids), 'E-R-014')
            _need(len(set(ids)) == 1, 'E-R-014')
            result.append(ids[0])
        else:
            raise ReaderError('E-R-013')
    return list(dict.fromkeys(result))


def _read(payloads, expected):
    _need(type(payloads) is dict and type(expected) is list and bool(expected), 'E-R-001')
    inventory = {}
    for row in expected:
        _need(type(row) is dict and set(row) == {'file', 'bytes', 'sha256'}, 'E-R-002')
        name, size, digest = row['file'], row['bytes'], row['sha256']
        _need(type(name) is str and re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', name)
              and '..' not in name, 'E-R-002')
        _need(type(size) is int and size >= 0 and type(digest) is str
              and re.fullmatch(r'[0-9a-f]{64}', digest), 'E-R-002')
        _need(name not in inventory, 'E-R-003')
        inventory[name] = (size, digest)
    _need(set(payloads) == set(inventory), 'E-R-004')
    # Validate every file before JSON parsing, not one verify/parse loop.
    for name, (size, digest) in inventory.items():
        raw = payloads[name]
        _need(type(raw) is bytes, 'E-R-005')
        _need(len(raw) == size and hashlib.sha256(raw).hexdigest() == digest, 'E-R-006')
    corrections = {}
    for name in sorted(inventory):
        rows = _parse_json(payloads[name])
        _need(type(rows) is list, 'E-R-009')
        for row in rows:
            _need(type(row) is dict, 'E-R-010')
            qid = row.get('question_id')
            _need(_label(qid), 'E-R-011')
            _need(qid not in corrections, 'E-R-012')
            corrections[qid] = ({'correct_evidence': _evidence(row['correct_evidence'])}
                                if 'correct_evidence' in row else {})
    return corrections


def parse_verified(payloads, expected):
    """Return normalized corrections or code-only error; never partial success.

Only the question ID and presence/value of correct_evidence enter the result.
Other row metadata is intentionally outside this gold-resolution projection.
No claim about hostile Python objects, concurrent caller mutation or traceback
local-variable inspection is made. Error strings and implicit chains are bounded.
"""
    failure = None
    try:
        result = _read(payloads, expected)
    except ReaderError as exc:
        failure = str(exc)
    except Exception:
        failure = 'E-R-015'
    if failure is not None:
        # Raise after the except scope so JSON decoder context carries no content.
        raise ReaderError(failure)
    return result


def run_on_real_corpus(*args, **kwargs):
    raise ReaderError('E-R-016')
