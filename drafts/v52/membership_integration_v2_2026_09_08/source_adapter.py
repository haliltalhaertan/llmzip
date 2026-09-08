"""Pure normalized correction bridge; no raw JSON or acquisition.

Supports explicit historical intermediate records, whose correct_evidence key is
always present and whose has_correct_evidence flag preserves original presence.
Raw correction records must instead be normalized by a separately checked adapter.
"""
from pipeline import require


def corrections_from_historical_normalized(records):
    require(type(records) is dict, 'E-A-001')
    out = {}
    for qid, row in records.items():
        require(type(qid) is str and bool(qid.strip()) and type(row) is dict, 'E-A-002')
        require(type(row.get('has_correct_evidence')) is bool, 'E-A-003')
        if row['has_correct_evidence']:
            require('correct_evidence' in row and type(row['correct_evidence']) is list,
                    'E-A-004')
            require(all(type(x) is str for x in row['correct_evidence']), 'E-A-005')
            out[qid] = {'correct_evidence': list(row['correct_evidence'])}
        else:
            out[qid] = {}
    return out
