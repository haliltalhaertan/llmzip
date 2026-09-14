#!/usr/bin/env python3
"""STEP 2a: build PerLTQA archives (frozen itemization) + gold mapping + frozen fit (C96, qC per QA)."""
import ast, hashlib, json, pickle
from collections import Counter
from pathlib import Path
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2')
qa = json.load(open(BASE/'perltqa_en_v2.json'))
mem = json.load(open(BASE/'perltmem_en_v2.json'))
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem])  # 31; lexical ordinal over evaluated archives
ORD = {c: i for i, c in enumerate(BANKED)}
SEC = {'profile': 'PRF', 'social_relationship': 'SOC', 'events': 'EVE', 'dialogues': 'DLG'}
SVD_SEED = 5204

def parse_social(v):
    if isinstance(v, dict): return v
    return ast.literal_eval(v)

def build_items(char):
    b = mem[char]; items = []  # (memory_id, memory_text)
    for i, (f, v) in enumerate(b['profile'].items()):
        items.append((f'PQ{ORD[char]:03d}_PRF_{i:03d}', f'[profile] {f}: {v}'))
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
                items.append((f'PQ{ORD[char]:03d}_DLG_{t:03d}', f'[dialogue {k} @ {ts}] {turn}'))
                t += 1
    return items

def refkey(s):
    s = s.strip()
    if s.startswith('['):
        return [str(x) for x in ast.literal_eval(s)]
    return [s]

# fit one archive (producer buildrep lines 109-110 verbatim structure)
def fit_archive(texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
    cv = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts)); Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format='csr')
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    Y = normalize(s96.fit_transform(Z)); mu = Y.mean(0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    return (wv, cv, svd, s96, mu, C)

def main():
    arch = {}   # char -> dict(N, items, C, key->idx, dlgkey->turn idxs, turn texts)
    res = Counter(); gold_sizes = Counter()
    qrecs = []  # (qid, char, section, question, gold_idx_list)
    for entry in qa:
        for char, d in entry.items():
            if char not in mem:
                for s in ['profile', 'social_relationship', 'events', 'dialogues']:
                    qs = d[s] if s == 'profile' else [q for g in d[s] for q in list(g.values())[0]]
                    res[(s, 'unresolved:nobank')] += len(qs)
                continue
            if char not in arch:
                items = build_items(char)
                texts = [t for _, t in items]
                wv, cv, svd, s96, mu, C = fit_archive(texts)
                key2idx = {}
                for i, (mid, _) in enumerate(items):
                    key2idx[mid] = i
                # section key -> item idx: PRF field order, SOC/EVE sorted-key order; DLG key -> [turn idxs]
                b = mem[char]
                prof_keys = list(b['profile'].keys())
                soc_keys = sorted(parse_social(b['social_relationship']).keys())
                ev_keys = sorted(b['events'].keys())
                dlg_turns = {}
                base = len(prof_keys) + 1 + len(soc_keys) + len(ev_keys)
                t = 0
                for k in sorted(b['dialogues'].keys()):
                    idxs = []
                    for ts in sorted(b['dialogues'][k]['contents'].keys()):
                        for turn in b['dialogues'][k]['contents'][ts]:
                            idxs.append(base + t); t += 1
                    dlg_turns[k] = idxs
                turn_text = {i: tx for i, (_, tx) in enumerate(items)}
                arch[char] = dict(N=len(items), items=items, key2idx=key2idx, prof={f: i for i, f in enumerate(prof_keys)},
                                  soc={k: len(prof_keys) + 1 + i for i, k in enumerate(soc_keys)},
                                  ev={k: len(prof_keys) + 1 + len(soc_keys) + i for i, k in enumerate(ev_keys)},
                                  dlg=dlg_turns, turn_text=turn_text, fit=(wv, cv, svd, s96, mu), C=C,
                                  zero_mass=float(np.mean(C == 0.0)))
                print(f'{char}: N={len(items)} zero_mass={arch[char]["zero_mass"]:.3e}', flush=True)
            A = arch[char]
            wv, cv, svd, s96, mu = A['fit']
            # profile QAs
            for qi, q in enumerate(d['profile']):
                rk = refkey(q['Reference Memory'])[0]
                qid = f'PQ{ORD[char]:03d}_PRF_q{qi:03d}'
                if rk in A['prof']:
                    g = [A['prof'][rk]]; res[('profile', 'resolved')] += 1
                else:
                    g = []; res[('profile', 'unresolved:keymiss')] += 1
                qrecs.append((qid, char, 'profile', str(q['Question']), g))
            # grouped sections
            for s in ['social_relationship', 'events', 'dialogues']:
                qi = 0
                for g_ in d[s]:
                    k = list(g_.keys())[0]
                    for q in list(g_.values())[0]:
                        qid = f'PQ{ORD[char]:03d}_{SEC[s]}_q{qi:03d}'; qi += 1
                        if s == 'social_relationship':
                            g = [A['soc'][k]] if k in A['soc'] else []
                        elif s == 'events':
                            g = [A['ev'][k]] if k in A['ev'] else []
                        else:
                            if k not in A['dlg']:
                                g = []
                            else:
                                idxs = A['dlg'][k]
                                ancs = [(list(a.keys())[0], list(a.values())[0]) for a in q['Memory Anchors']]
                                num = [t for t, sp in ancs if sp != [-1, -1]]
                                hit = [i for i in idxs if any(a.lower() in A['turn_text'][i].lower() for a in num)] if num else []
                                g = hit if hit else list(idxs)
                        if g: res[(s, 'resolved')] += 1
                        else: res[(s, 'unresolved:keymiss')] += 1
                        qrecs.append((qid, char, s, str(q['Question']), g))
    # query transform per resolved QA
    nq = 0
    QDAT = {}
    for (qid, char, s, question, g) in qrecs:
        if not g:
            continue
        A = arch[char]
        wv, cv, svd, s96, mu = A['fit']
        Qw = normalize(wv.transform([question])); Qc = normalize(cv.transform([question])); Ql = normalize(svd.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format='csr')
        QY = normalize(s96.transform(Zq)); qC = (QY - mu)[0].astype(np.float64)
        QDAT[qid] = dict(char=char, section=s, gold=np.array(sorted(g), dtype=np.int32), qC=qC)
        nq += 1
    print('resolved QAs:', nq, dict(res), flush=True)
    # persist
    with open('/tmp/b3b/cache_arch.pkl', 'wb') as f:
        pickle.dump({c: dict(N=A['N'], C=A['C'], zero_mass=A['zero_mass']) for c, A in arch.items()}, f, pickle.HIGHEST_PROTOCOL)
    with open('/tmp/b3b/cache_q.pkl', 'wb') as f:
        pickle.dump(QDAT, f, pickle.HIGHEST_PROTOCOL)
    with open('/tmp/b3b/cache_items.json', 'w') as f:
        json.dump({c: dict(N=A['N'], ordinal=ORD[c], items=[[m, t] for m, t in A['items']]) for c, A in arch.items()}, f)
    with open('/tmp/b3b/cache_qmeta.json', 'w') as f:
        json.dump([dict(qid=q, char=c, section=s, gold=list(map(int, g))) for (q, c, s, _, g) in qrecs], f)
    with open('/tmp/b3b/resolution.json', 'w') as f:
        json.dump({'counts': {f'{k[0]}:{k[1]}': v for k, v in res.items()}, 'ordinals': ORD}, f, indent=2)
    # gold size diagnostics
    gs = {}
    for (qid, char, s, _, g) in qrecs:
        if g: gs.setdefault(s, []).append(len(g))
    import statistics
    for s, v in gs.items():
        a = np.array(v)
        print(f'goldsize {s}: n={len(a)} mean={a.mean():.2f} min={a.min()} max={a.max()}', flush=True)

if __name__ == '__main__':
    main()
