#!/usr/bin/env python3
"""STEP 0 port fidelity gate: reconstruct C96+qC via producer frozen logic, compare to cache_repr pkls."""
import hashlib, importlib.util, json, pickle, sys
from pathlib import Path
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work')
PRODUCER = BASE/'drive/v52_t4c3_coordinate_axis_probe.py'
A1 = Path('/home/mdp/muse-work/llmzip-audit/adapters/longmemeval_v52_adapter.py')
A2 = Path('/home/mdp/muse-work/llmzip-audit/adapters/longmemeval_v52_adapter_v2.py')
DATASET = BASE/'drive/longmemeval_s_cleaned.json'
PKLDIR = BASE/'regen/lme/cache_repr'
SVD_SEED = 5204

EXP_PRODUCER = '8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996'
EXP_A1 = '0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722'
EXP_A2 = '643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218'

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()

def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def main():
    got = {'producer': sha(PRODUCER), 'a1': sha(A1), 'a2': sha(A2)}
    assert got['producer'] == EXP_PRODUCER, got
    assert got['a1'] == EXP_A1 and got['a2'] == EXP_A2, got
    print('hashes OK', flush=True)
    ad = mod(A2, 'a2_gate')  # producer buildrep imports a2 (v2 re-exports v1 fit fns)
    data = json.loads(DATASET.read_text())
    lex = {q: i for i, q in enumerate(sorted(str(x['question_id']) for x in data))}
    prim = sorted([x for x in data if not str(x['question_id']).endswith('_abs')], key=lambda x: str(x['question_id']))
    assert len(prim) == 470, len(prim)
    idx = [0, 94, 188, 282, 376, 469]
    sample = [prim[i] for i in idx]
    rows = []
    for item0 in sample:
        item = json.loads(json.dumps(item0))  # mirror producer items/*.json round-trip
        qid = str(item['question_id'])
        mem, gids, iss = ad.build_archive(item)
        assert not iss, (qid, iss[:2])
        texts = ad.fit_input_payload(mem)
        ids = {m['memory_id']: i for i, m in enumerate(mem)}
        gold = sorted(ids[g] for g in gids)
        wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(texts)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format='csr')
        s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        q = str(item['question'])
        Qw = normalize(wv.transform([q])); Qc = normalize(cv.transform([q])); Ql = normalize(sv.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format='csr')
        QY = normalize(s96.transform(Zq))
        qC = (QY - mu)[0].astype(np.float64)
        o = pickle.loads((PKLDIR/(qid + '.pkl')).read_bytes())
        Cr = np.asarray(o['C'], float); qCr = np.asarray(o['qC'], float); gr = np.asarray(o['gold']).ravel().tolist()
        dC = float(np.max(np.abs(C - Cr))); dq = float(np.max(np.abs(qC - qCr)))
        signC = bool(np.array_equal(C >= 0, Cr >= 0)); signq = bool(np.array_equal(qC >= 0, qCr >= 0))
        goldok = (sorted(map(int, gold)) == sorted(map(int, gr)))
        ok = dC <= 1e-10 and dq <= 1e-10 and signC and signq and goldok
        rows.append({'question_id': qid, 'lex': lex[qid], 'N': len(mem),
                     'max_abs_diff_C': dC, 'max_abs_diff_qC': dq,
                     'sign_C_identical': signC, 'sign_qC_identical': signq,
                     'gold_identical': goldok, 'pass': ok})
        print(f"{qid} N={len(mem)} dC={dC:.3e} dq={dq:.3e} sign={signC and signq} gold={goldok} {'PASS' if ok else 'FAIL'}", flush=True)
    gate = bool(all(r['pass'] for r in rows))
    out = {'gate': 'PASS' if gate else 'FAIL', 'hashes': got,
           'versions': {'numpy': np.__version__,
                        'sklearn': importlib.import_module('sklearn').__version__,
                        'scipy': importlib.import_module('scipy').__version__},
           'n_sampled': len(rows), 'threshold': 1e-10, 'rows': rows}
    Path('/tmp/b3b/port_gate.json').write_text(json.dumps(out, indent=2))
    print('PORT_GATE:', out['gate'], flush=True)
    if not gate:
        sys.exit(1)

if __name__ == '__main__':
    main()
