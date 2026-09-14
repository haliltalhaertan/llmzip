#!/usr/bin/env python3
"""Apply frozen-support exclusion: drop archives whose C is not 96-dim + their QAs. Record reason."""
import json, pickle
from collections import Counter
import numpy as np
arch = pickle.load(open('/tmp/b3b/cache_arch.pkl', 'rb'))
QDAT = pickle.load(open('/tmp/b3b/cache_q.pkl', 'rb'))
qmeta = json.load(open('/tmp/b3b/cache_qmeta.json'))
excluded = {}
for c in list(arch.keys()):
    C = np.asarray(arch[c]['C'])
    if C.shape[1] != 96:
        excluded[c] = {'N': arch[c]['N'], 'C_shape': list(C.shape),
                       'reason': 'TruncatedSVD(n_components=96, seed=5204) silently capped output dim at N samples (no warning); archive cannot support frozen SVD96; excluded per port rule (do not silently shrink)'}
        del arch[c]
qdrop = [qid for qid, q in QDAT.items() if q['char'] in excluded]
sec = Counter(QDAT[q]['section'] for q in qdrop)
for q in qdrop:
    del QDAT[q]
for c, e in excluded.items():
    e['n_qa_dropped'] = int(sum(1 for q in qdrop if True)) if False else None
# per-char dropped counts
dropchar = Counter()
meta_drop = [r for r in qmeta if r['char'] in excluded]
for r in meta_drop:
    dropchar[(r['char'], r['section'])] += 1
for c in excluded:
    excluded[c]['qa_dropped_by_section'] = {s.split(',')[0] if False else k[1]: v for k, v in dropchar.items() if k[0] == c}
    excluded[c]['n_qa_dropped'] = int(sum(v for k, v in dropchar.items() if k[0] == c))
pickle.dump(arch, open('/tmp/b3b/cache_arch_eval.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
pickle.dump(QDAT, open('/tmp/b3b/cache_q_eval.pkl', 'wb'), pickle.HIGHEST_PROTOCOL)
json.dump({'excluded_archives': excluded, 'n_qa_dropped_total': len(qdrop),
           'qa_dropped_by_section': {k: int(v) for k, v in sec.items()}},
          open('/tmp/b3b/exclusions.json', 'w'), indent=2)
print('excluded:', json.dumps(excluded, indent=1))
print('remaining archives:', len(arch), 'remaining QAs:', len(QDAT))
assert all(np.asarray(a['C']).shape[1] == 96 for a in arch.values())
