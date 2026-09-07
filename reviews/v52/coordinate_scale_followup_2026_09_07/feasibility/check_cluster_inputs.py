"""Inspect persisted cluster identifiers only; never resample or read raw corpus."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[4]

def locomo_cluster(tie):
    match = re.fullmatch(r'archive_ordinal=(\d+);nuisance=20;stable_archive_seed\(ci,t\)\+99', tie)
    if match is None:
        raise ValueError('invalid persisted cluster encoding')
    return int(match[1])

def main():
    evidence = {'scope':'input feasibility, no bootstrap, no new endpoint', 'datasets':{}}
    for name in ['locomo','longmemeval']:
        path = ROOT / 'research/v52' / (name+'_scale_outputs') / (name+'_scale_per_question.csv.gz')
        ties = {}
        with gzip.open(path,'rt',newline='') as stream:
            for row in csv.DictReader(stream):
                q, tie = row['question_id'], row['tie_identity']
                if q in ties and ties[q] != tie:
                    raise ValueError('inconsistent tie mapping')
                ties[q] = tie
        ent = {'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'questions':len(ties), 'tie_examples':sorted(set(ties.values()))[:2]}
        if name == 'locomo':
            mapping = {q:locomo_cluster(tie) for q,tie in ties.items()}
            counts = Counter(mapping.values())
            assert set(counts) == set(range(10)) and len(mapping) == 1535
            ent['cluster_question_counts'] = dict(sorted(counts.items()))
            ent['mapping_sha256'] = hashlib.sha256(json.dumps(mapping,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            ent['status'] = '10 archive-ordinal clusters recoverable from persisted producer encoding; no independent corpus join'
        else:
            ent['status'] = '470 question IDs; no conversation-cluster mapping certified by this check. Do not equate per-question archive with shared conversation.'
        evidence['datasets'][name] = ent
    for bad in ['', 'archive_ordinal=-1', 'archive_ordinal=0;wrong']:
        try:
            locomo_cluster(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('malformed encoding accepted')
    evidence['malformed_encoding_negative_controls'] = '3/3 REJECTED'
    Path(__file__).with_name('RESULT.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(evidence,indent=2))

if __name__ == '__main__':
    main()
