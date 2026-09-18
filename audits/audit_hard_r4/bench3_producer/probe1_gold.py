#!/usr/bin/env python3
"""Bench3 producer audit probes (read-only on sources; writes stdout only)."""
import json, pickle, re, sys
from pathlib import Path
import numpy as np

W = Path('/mnt/c/Users/MDP/dev/llmzip-work')
RT_RAW = W/'bench3/REALTALK/data'
RT_REPR = W/'bench3/runs/b3a_realtalk/rt_repr'
PQ_MEM = W/'bench3/PerLTQA/Dataset/en_v2/perltmem_en_v2.json'
PQ_QA = W/'bench3/PerLTQA/Dataset/en_v2/perltqa_en_v2.json'

out = {}
# ---- A. RealTalk gold end-to-end (>=20) ----
files = sorted(RT_RAW.glob('Chat_*.json'), key=lambda p: p.name)
TOK = re.compile(r'D\d+:\d+')
def rt_norm(x):
    if x is None: return []
    if isinstance(x, str):
        v = TOK.findall(x); return v if v else [x]
    if isinstance(x, (list, tuple)):
        o = []
        for z in x:
            if isinstance(z, str):
                ids = TOK.findall(z); o.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get('dia_id') or z.get('id')
                if did: o.append(str(did))
        return list(dict.fromkeys(o))
    return []
rng = np.random.default_rng(7)
rt_checked = rt_ok = 0; rt_errs = []; rt_valid_zero = 0
rt_dupes = {}; rt_neardup = {}
for ci, fp in enumerate(files):
    d = json.loads(fp.read_text(encoding='utf-8'))
    o = pickle.loads((RT_REPR/f'RT{ci+1:02d}.pkl').read_bytes())
    skeys = sorted([k for k in d if k.startswith('session_') and not k.endswith('_date_time') and not k.startswith('events_session_')], key=lambda k: int(k.split('_')[1]))
    mids = []
    for sk in skeys:
        for m in d[sk]: mids.append(str(m['dia_id']))
    id2row = {x: i for i, x in enumerate(mids)}
    # cache id_to_row must match raw order
    assert o['id_to_row'] == id2row, f"RT{ci+1:02d} id_to_row mismatch"
    # duplicate dia_id + duplicate text check
    assert len(set(mids)) == len(mids)
    texts = []
    for sk in skeys:
        for m in d[sk]:
            sp = str(m.get('speaker','')); tx = str(m.get('clean_text','')); cap = str(m.get('blip_caption','') or '')
            t = f"{sp}: {tx}" + (f" [IMAGE: {cap}]" if cap.strip() else "")
            texts.append(t.strip(': '))
    assert len(texts) == o['N'] == len(mids), (fp.name, len(texts), o['N'])
    # cached text? pkl has no texts; verify count of IMAGE-captioned
    # exact-text duplicates
    from collections import Counter
    c = Counter(texts)
    nd = sum(1 for k, v in c.items() if v > 1)
    rt_dupes[fp.name] = (nd, sum(v-1 for k, v in c.items() if v > 1))
    # sample 3 QAs per chat = 30 total
    idxs = rng.choice(len(d['qa']), size=3, replace=False)
    for qi in idxs:
        q = d['qa'][qi]
        toks = rt_norm(q.get('evidence'))
        rows = list(dict.fromkeys(id2row[t] for t in toks if t in id2row))
        cached = list(map(int, o['gold_rows'][qi]))
        rt_checked += 1
        if rows == cached: rt_ok += 1
        else: rt_errs.append((fp.name, qi, toks[:4], rows[:6], cached[:6]))
        if not cached: rt_valid_zero += 1
        # gold text sanity: resolved row's dia_id must equal token
        for t, r in zip([t for t in toks if t in id2row], rows):
            assert mids[r] == t
out['rt_gold'] = dict(checked=rt_checked, ok=rt_ok, errs=rt_errs[:6], sampled_zero_gold=rt_valid_zero)
out['rt_dupes_exact'] = rt_dupes
# unresolved evidence tokens across all RT QAs
unres = sum(1 for ci, fp in enumerate(files) for q in json.loads(fp.read_text())['qa'] for t in rt_norm(q.get('evidence')) if t not in pickle.loads((RT_REPR/f'RT{ci+1:02d}.pkl').read_bytes())['id_to_row'])
out['rt_unresolved_tokens_total'] = unres

# ---- B. PerLTQA gold end-to-end (>=20) ----
mem = json.load(open(PQ_MEM)); qa = json.load(open(PQ_QA))
qmeta = json.load(open(W/'bench3/runs/b3b_perltqa/cache_qmeta.json'))
import ast
def parse_social(v): return v if isinstance(v, dict) else ast.literal_eval(v)
def refkey(s):
    s = s.strip()
    if s.startswith('['): return [str(x) for x in ast.literal_eval(s)]
    return [s]
# rebuild item index for each banked char exactly as step2_build
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem])
ORD = {c: i for i, c in enumerate(BANKED)}
def build_index(char):
    b = mem[char]
    prof_keys = list(b['profile'].keys())
    soc_keys = sorted(parse_social(b['social_relationship']).keys())
    ev_keys = sorted(b['events'].keys())
    base = len(prof_keys)+1+len(soc_keys)+len(ev_keys)
    dlg_turns = {}; t = 0
    for k in sorted(b['dialogues'].keys()):
        idxs = []
        for ts in sorted(b['dialogues'][k]['contents'].keys()):
            for turn in b['dialogues'][k]['contents'][ts]: idxs.append(base+t); t += 1
        dlg_turns[k] = idxs
    N = base + t
    return dict(prof={f: i for i, f in enumerate(prof_keys)},
                soc={k: len(prof_keys)+1+i for i, k in enumerate(soc_keys)},
                ev={k: len(prof_keys)+1+len(soc_keys)+i for i, k in enumerate(ev_keys)},
                dlg=dlg_turns, N=N)
SEC = {'profile': 'PRF', 'social_relationship': 'SOC', 'events': 'EVE', 'dialogues': 'DLG'}
meta_by_qid = {r['qid']: r for r in qmeta}
# independent gold recompute for sample: 24 QAs stratified
rng2 = np.random.default_rng(11)
sample = rng2.choice(qmeta, size=24, replace=False)
pq_ok = 0; pq_errs = []
for r in sample:
    qid, char, sec, gold = r['qid'], r['char'], r['section'], r['gold']
    # find raw question
    rawq = None
    for entry in qa:
        if char in entry:
            dd = entry[char]
            if sec == 'profile':
                for qi2, qq in enumerate(dd['profile']):
                    if f'PQ{ORD[char]:03d}_PRF_q{qi2:03d}' == qid: rawq = qq; gk = None; break
            else:
                qi2 = 0; inv = {v: k for k, v in SEC.items()}
                sraw = [k for k, v in SEC.items() if v == qid.split('_')[1]][0] if '_' in qid else sec
                for g_ in dd[sec]:
                    k = list(g_.keys())[0]
                    for qq in list(g_.values())[0]:
                        qqid = f'PQ{ORD[char]:03d}_{SEC[sec]}_q{qi2:03d}'; qi2 += 1
                        if qqid == qid: rawq = qq; gk = k; break
                    if rawq: break
        if rawq is not None: break
    assert rawq is not None, qid
    A = build_index(char)
    if sec == 'profile':
        rk = refkey(rawq['Reference Memory'])[0]
        exp = [A['prof'][rk]] if rk in A['prof'] else []
    elif sec == 'social_relationship':
        exp = [A['soc'][gk]] if gk in A['soc'] else []
    elif sec == 'events':
        exp = [A['ev'][gk]] if gk in A['ev'] else []
    else:
        if gk not in A['dlg']: exp = []
        else:
            idxs = A['dlg'][gk]
            b = mem[char]
            turns = []
            for kk in sorted(b['dialogues'].keys()):
                pass
            base = len(list(b['profile'].keys()))+1+len(sorted(parse_social(b['social_relationship']).keys()))+len(sorted(b['events'].keys()))
            tmap = {}
            _t = 0
            for kk in sorted(b['dialogues'].keys()):
                for ts in sorted(b['dialogues'][kk]['contents'].keys()):
                    for turn in b['dialogues'][kk]['contents'][ts]:
                        tmap[base + _t] = f'[dialogue {kk} @ {ts}] {turn}'
                        _t += 1
            ancs = [(list(a.keys())[0], list(a.values())[0]) for a in rawq['Memory Anchors']]
            num = [t for t, sp in ancs if sp != [-1, -1]]
            if num:
                hit = [i for i in idxs if any(a.lower() in tmap[i].lower() for a in num)]
                exp = hit if hit else list(idxs)
            else:
                exp = list(idxs)
    if sorted(exp) == sorted(gold): pq_ok += 1
    else: pq_errs.append((qid, gk if sec != 'profile' else refkey(rawq['Reference Memory'])[0], sorted(exp)[:8], sorted(gold)[:8]))
out['pq_gold'] = dict(checked=24, ok=pq_ok, errs=pq_errs[:8])
# multi-ref profile truncation check
multi = sum(1 for entry in qa for char, d in entry.items() for q in d.get('profile', []) if len(refkey(q['Reference Memory'])) > 1)
out['pq_profile_multiref_n'] = multi
# ref!=groupkey mismatches (grouped sections)
mm = 0
for entry in qa:
    for char, d in entry.items():
        for s in ['social_relationship', 'events', 'dialogues']:
            for g_ in d.get(s, []):
                k = list(g_.keys())[0]
                for q in list(g_.values())[0]:
                    rk = refkey(q['Reference Memory'])
                    if len(rk) > 1 or (rk and rk[0] != k): mm += 1
out['pq_grouped_ref_mismatch_n'] = mm
# PerLTQA exact-text duplicate docs per archive (all 31 banked)
import collections
pq_dup = {}
for char in BANKED:
    b = mem[char]
    items = []
    for i, (f, v) in enumerate(b['profile'].items()): items.append(f'[profile] {f}: {v}')
    items.append(f"[profile_description] {b['profile_description']}")
    soc = parse_social(b['social_relationship'])
    for i, k in enumerate(sorted(soc.keys())):
        e = soc[k]
        extra = ''.join(f'; {kk}: {vv}' for kk, vv in sorted(e.items()) if kk not in ('Supporting Characters', 'Relationship', 'Description'))
        items.append(f"[social {k}] {e.get('Supporting Characters','')} ({e.get('Relationship','')}): {e.get('Description','')}{extra}")
    for i, k in enumerate(sorted(b['events'].keys())):
        ev = b['events'][k]
        content = ev['content'] if isinstance(ev, dict) and 'content' in ev else (ev if isinstance(ev, str) else json.dumps(ev))
        items.append(f'[event {k}] {content}')
    for k in sorted(b['dialogues'].keys()):
        for ts in sorted(b['dialogues'][k]['contents'].keys()):
            for turn in b['dialogues'][k]['contents'][ts]:
                items.append(f'[dialogue {k} @ {ts}] {turn}')
    cc = collections.Counter(items)
    pq_dup[char] = (sum(1 for k, v in cc.items() if v > 1), len(items))
out['pq_dupes'] = pq_dup
# question-in-corpus leak: any question string exactly equal to a doc text?
nq = 0; leak = 0
for entry in qa:
    for char, d in entry.items():
        if char not in mem: continue
        for q in d.get('profile', []): nq += 1
print(json.dumps(out, indent=1)[:6000])
