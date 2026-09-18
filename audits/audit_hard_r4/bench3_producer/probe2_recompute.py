#!/usr/bin/env python3
"""Probe2: recompute cached reprs, centering axis, leakage, exclusions, gates."""
import json, pickle, importlib.util
from pathlib import Path
import numpy as np
W = Path('/mnt/c/Users/MDP/dev/llmzip-work')
import os
os.environ.setdefault('OMP_NUM_THREADS','1'); os.environ.setdefault('MKL_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1'); os.environ.setdefault('NUMEXPR_NUM_THREADS','1')

# ---- 1. RealTalk recompute 2 archives via frozen build_representation ----
def load_mod(p, n):
    s = importlib.util.spec_from_file_location(n, str(p))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
t4d = load_mod(W/'drive/v52_t4d_locomo_frozen_cross_benchmark.py', 'fz')
from sklearn.feature_extraction.text import TfidfVectorizer
print('char_cv lowercase default:', TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), sublinear_tf=True).get_params()['lowercase'])
for ci, fpname in [(2, 'Chat_1_Emi_Elise.json'), (5, 'Chat_4_Emi_Paola.json')]:
    fp = W/('bench3/REALTALK/data/'+fpname)
    d = json.loads(fp.read_text(encoding='utf-8'))
    skeys = sorted([k for k in d if k.startswith('session_') and not k.endswith('_date_time') and not k.startswith('events_session_')], key=lambda k: int(k.split('_')[1]))
    lines = []
    for sk in skeys:
        for m in d[sk]:
            tx = t4d.message_text({'speaker': m.get('speaker',''), 'text': m.get('clean_text',''), 'blip_caption': m.get('blip_caption','') or ''})
            lines.append({'dia_id': str(m['dia_id']), 'text': tx, 'session': sk})
    qas = [{'question_id': f'RT{ci:02d}_q{qi:03d}', 'question': str(q.get('question','')), 'answer': str(q.get('answer','')), 'category': int(q['category']), 'raw_evidence': str(q.get('evidence') or '')} for qi, q in enumerate(d['qa'])]
    # note: build_representation only uses lines+qas questions; raw_evidence unused inside
    conv = {'conv_id': f'RT{ci:02d}', 'lines': lines, 'qas': qas}
    rep = t4d.build_representation(conv)
    o = pickle.loads((W/f'bench3/runs/b3a_realtalk/rt_repr/RT{ci:02d}.pkl').read_bytes())
    C, QC = np.asarray(rep['C'], float), np.asarray(rep['QC'], float)
    Cr, QCr = np.asarray(o['C'], float), np.asarray(o['QC'], float)
    print(f'RT{ci:02d} N={rep["N"]} Cshape={C.shape} max|C-Cr|={np.max(np.abs(C-Cr)):.3e} signC={np.mean(np.sign(C)==np.sign(Cr)):.6f} max|QC-QCr|={np.max(np.abs(QC-QCr)):.3e} signQ={np.mean(np.sign(QC)==np.sign(QCr)):.6f}')
    # centering axis check: column means ~0, row means not
    print(f'  colmean_absmax={np.abs(C.mean(axis=0)).max():.3e} rowmean_absmax={np.abs(C.mean(axis=1)).max():.3e}')
    # leakage: questions must not appear in fit texts
    qset = set(q['question'] for q in qas)
    tset = set(x['text'] for x in lines)
    print(f'  question-in-corpus exact overlap: {len(qset & tset)}/{len(qset)}')

# ---- 2. PerLTQA recompute 2 archives via step2_build replica ----
import ast
from scipy import sparse
from sklearn.preprocessing import normalize
from sklearn.decomposition import TruncatedSVD
mem = json.load(open(W/'bench3/PerLTQA/Dataset/en_v2/perltmem_en_v2.json'))
def parse_social(v): return v if isinstance(v, dict) else ast.literal_eval(v)
qa = json.load(open(W/'bench3/PerLTQA/Dataset/en_v2/perltqa_en_v2.json'))
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem]); ORD = {c: i for i, c in enumerate(BANKED)}
def build_items(char):
    b = mem[char]; items = []
    for i, (f, v) in enumerate(b['profile'].items()): items.append((f'PQ{ORD[char]:03d}_PRF_{i:03d}', f'[profile] {f}: {v}'))
    items.append((f'PQ{ORD[char]:03d}_DSC_000', f"[profile_description] {b['profile_description']}"))
    soc = parse_social(b['social_relationship'])
    for i, k in enumerate(sorted(soc.keys())):
        e = soc[k]
        extra = ''.join(f'; {kk}: {vv}' for kk, vv in sorted(e.items()) if kk not in ('Supporting Characters', 'Relationship', 'Description'))
        items.append((f'PQ{ORD[char]:03d}_SOC_{i:03d}', f"[social {k}] {e.get('Supporting Characters','')} ({e.get('Relationship','')}): {e.get('Description','')}{extra}"))
    for i, k in enumerate(sorted(b['events'].keys())):
        ev = b['events'][k]
        content = ev['content'] if isinstance(ev, dict) and 'content' in ev else (ev if isinstance(ev, str) else json.dumps(ev))
        items.append((f'PQ{ORD[char]:03d}_EVE_{i:03d}', f'[event {k}] {content}'))
    t = 0
    for k in sorted(b['dialogues'].keys()):
        for ts in sorted(b['dialogues'][k]['contents'].keys()):
            for turn in b['dialogues'][k]['contents'][ts]:
                items.append((f'PQ{ORD[char]:03d}_DLG_{t:03d}', f'[dialogue {k} @ {ts}] {turn}')); t += 1
    return items
def fit_archive(texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
    cv = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts)); Xc = normalize(cv.fit_transform(texts))
    dd = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=dd, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format='csr')
    s96 = TruncatedSVD(n_components=96, random_state=5204)
    Y = normalize(s96.fit_transform(Z)); mu = Y.mean(0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    return (wv, cv, svd, s96, mu, C)
arch = pickle.load(open(W/'bench3/runs/b3b_perltqa/cache_arch.pkl', 'rb'))
QDAT = pickle.load(open(W/'bench3/runs/b3b_perltqa/cache_q.pkl', 'rb'))
for char in ['Kong Tingting', 'Cai Xiuying']:
    items = build_items(char); texts = [t for _, t in items]
    wv, cv, svd, s96, mu, C = fit_archive(texts)
    Cr = np.asarray(arch[char]['C'], float)
    print(f'{char} N={len(items)} Cshape={C.shape} cached={Cr.shape} maxdiff={np.max(np.abs(C-Cr)):.3e} signmatch={np.mean(np.sign(C)==np.sign(Cr)):.6f} latent_d={svd.n_components}')
    print(f'  colmean_absmax={np.abs(C.mean(axis=0)).max():.3e}')
    # one query recompute
    qid = next(q for q, v in QDAT.items() if v['char'] == char)
    qq = None
    for entry in qa:
        if char in entry:
            dd = entry[char]
            for qi2, q in enumerate(dd['profile']):
                if f'PQ{ORD[char]:03d}_PRF_q{qi2:03d}' == qid: qq = str(q['Question']); break
    if qq is None:
        for entry in qa:
            if char in entry:
                dd = entry[char]
                for s in ['social_relationship', 'events', 'dialogues']:
                    qi2 = 0
                    SEC = {'social_relationship': 'SOC', 'events': 'EVE', 'dialogues': 'DLG'}
                    for g_ in dd[s]:
                        for q in list(g_.values())[0]:
                            if f'PQ{ORD[char]:03d}_{SEC[s]}_q{qi2:03d}' == qid: qq = str(q['Question']); break
                            qi2 += 1
                        if qq: break
                    if qq: break
    Qw = normalize(wv.transform([qq])); Qc = normalize(cv.transform([qq])); Ql = normalize(svd.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format='csr')
    qC = (normalize(s96.transform(Zq)) - mu)[0].astype(np.float64)
    print(f'  {qid} max|qC-qCr|={np.max(np.abs(qC-np.asarray(QDAT[qid]["qC"], float))):.3e} signmatch={np.mean(np.sign(qC)==np.sign(np.asarray(QDAT[qid]["qC"], float))):.6f}')
# Chen Zhi: show SVD capping
print('Chen Zhi cached shape:', np.asarray(arch['Chen Zhi']['C']).shape, 'N=', arch['Chen Zhi']['N'])
# exclusions asymmetry: gold sizes of dropped vs kept dialogue QAs
res = json.load(open(W/'bench3/runs/b3b_perltqa/resolution.json'))
print('resolution counts:', res['counts'])
