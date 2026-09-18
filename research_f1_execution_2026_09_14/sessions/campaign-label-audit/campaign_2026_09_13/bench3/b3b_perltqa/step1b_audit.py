#!/usr/bin/env python3
"""STEP 1b: SVD feasibility probe + missing-key detail + anchor substring rates + schema uniformity."""
import ast, json
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

# (a) SVD96 feasibility probe with producer's exact path on synthetic texts
rng = np.random.default_rng(0)
words = [f'w{i}' for i in range(400)]
def synth(n):
    return [' '.join(rng.choice(words, size=40)) for _ in range(n)]
for n in [35, 96, 97, 120, 293]:
    try:
        texts = synth(n)
        wv = TfidfVectorizer(lowercase=True, ngram_range=(1,2), stop_words='english', sublinear_tf=True)
        cv = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), sublinear_tf=True)
        Xw = normalize(wv.fit_transform(texts)); Xc = normalize(cv.fit_transform(texts))
        d = min(32, Xw.shape[0]-1, Xw.shape[1]-1)
        svd = TruncatedSVD(n_components=d, random_state=5101)
        Xl = normalize(svd.fit_transform(Xw))
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format='csr')
        s96 = TruncatedSVD(n_components=96, random_state=5204)
        Y = normalize(s96.fit_transform(Z))
        print(f'N={n}: SVD96 OK Z={Z.shape}')
    except Exception as e:
        print(f'N={n}: FAIL {type(e).__name__}: {str(e)[:160]}')

# (b) missing-key detail
for entry in qa:
    for char, d in entry.items():
        if char == 'Cao Lili':
            bkeys = set(mem[char]['events'].keys())
            for g in d['events']:
                k = list(g.keys())[0]
                if k not in bkeys:
                    print('CaoLili missing ev group:', repr(k), 'nQA=', len(list(g.values())[0]))
            print('CaoLili bank-only ev keys:', sorted(bkeys - set(list(g.keys())[0] for g in d['events'])))
        if char == 'Yang Wei':
            raw = mem[char]['social_relationship']
            bkeys = set(raw.keys()) if isinstance(raw, dict) else set()
            for g in d['social_relationship']:
                k = list(g.keys())[0]
                if k not in bkeys:
                    print('YangWei missing soc group:', repr(k), 'nQA=', len(list(g.values())[0]))
            print('YangWei bank soc keys:', sorted(bkeys))

# (c) schema uniformity of bank values
ev_struct = Counter(); dg_struct = Counter(); soc_struct = Counter()
for c, b in mem.items():
    for k, v in b['events'].items():
        ev_struct[type(v).__name__ + (':' + ','.join(sorted(v.keys())) if isinstance(v, dict) else '')] += 1
    for k, v in b['dialogues'].items():
        if isinstance(v, dict):
            dg_struct[type(v).__name__ + ':' + ','.join(sorted(v.keys()))] += 1
        else:
            dg_struct[type(v).__name__] += 1
    s = b['social_relationship']
    if isinstance(s, dict):
        for k, v in s.items():
            soc_struct[type(v).__name__ + (':' + ','.join(sorted(v.keys())) if isinstance(v, dict) else '')] += 1
    else:
        try:
            p = ast.literal_eval(s)
            for k, v in p.items():
                soc_struct['str-parsed:' + type(v).__name__ + (':' + ','.join(sorted(v.keys())) if isinstance(v, dict) else '')] += 1
        except Exception as e:
            soc_struct['UNPARSABLE'] += 1
print('event value schemas:', dict(ev_struct))
print('dialogue value schemas:', dict(dg_struct))
print('social value schemas:', dict(soc_struct))

# (d) anchor substring rates: events anchor text in event content; dialogue anchor text in dialogue full text
def turn_texts(dlg_val):
    out = []
    for ts, turns in dlg_val['contents'].items():
        for t, turn in enumerate(turns):
            out.append((ts, t, str(turn)))
    return out
ev_found = Counter(); dg_found = Counter(); dg_turnhits = []
n_ev = n_dg = 0
for entry in qa:
    for char, d in entry.items():
        bank = mem.get(char)
        if bank is None:
            continue
        for g in d['events']:
            k = list(g.keys())[0]
            if k not in bank['events']:
                continue
            ev = bank['events'][k]
            content = ev['content'] if isinstance(ev, dict) and 'content' in ev else (ev if isinstance(ev, str) else json.dumps(ev))
            for q in list(g.values())[0]:
                n_ev += 1
                ancs = [(list(a.keys())[0], list(a.values())[0]) for a in q['Memory Anchors']]
                num = [(t, s) for t, s in ancs if s != [-1, -1]]
                if not num:
                    ev_found['no_numeric'] += 1; continue
                hits = sum(1 for t, s in num if t.lower() in content.lower())
                ev_found['all' if hits == len(num) else ('partial' if hits else 'none')] += 1
        for g in d['dialogues']:
            k = list(g.keys())[0]
            if k not in bank['dialogues']:
                continue
            turns = turn_texts(bank['dialogues'][k])
            full = '\n'.join(t for _, _, t in turns)
            for q in list(g.values())[0]:
                n_dg += 1
                ancs = [(list(a.keys())[0], list(a.values())[0]) for a in q['Memory Anchors']]
                num = [(t, s) for t, s in ancs if s != [-1, -1]]
                if not num:
                    dg_found['no_numeric'] += 1; continue
                hits = sum(1 for t, s in num if t.lower() in full.lower())
                dg_found['all' if hits == len(num) else ('partial' if hits else 'none')] += 1
                if hits:
                    nth = sum(1 for _, _, t in turns if any(a.lower() in t.lower() for a, _ in num))
                    dg_turnhits.append(nth)
print('events anchor-substring (per QA):', dict(ev_found), 'n=', n_ev)
print('dialogues anchor-substring (per QA):', dict(dg_found), 'n=', n_dg)
if dg_turnhits:
    a = np.array(dg_turnhits)
    print(f'dialogue gold-turn counts (QAs w/>=1 anchor hit): n={len(a)} mean={a.mean():.2f} min={a.min()} max={a.max()}')
