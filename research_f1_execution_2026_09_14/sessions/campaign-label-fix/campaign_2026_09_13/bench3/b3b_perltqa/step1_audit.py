#!/usr/bin/env python3
"""STEP 1 audit: reference-key coverage, anchor stats, bank type quirks, archive sizes."""
import ast, json
from collections import Counter
from pathlib import Path
import numpy as np

BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2')
qa = json.load(open(BASE/'perltqa_en_v2.json'))
mem = json.load(open(BASE/'perltmem_en_v2.json'))
qachars = [list(e.keys())[0] for e in qa]
print('n_chars_QA:', len(qachars))

def parse_bank_social(v):
    if isinstance(v, dict):
        return v, 'dict'
    if isinstance(v, str):
        try:
            return ast.literal_eval(v), 'str-parsed'
        except Exception as e:
            return None, f'str-UNPARSABLE:{e}'
    return None, f'unexpected:{type(v).__name__}'

# per-char: bank key sets vs QA ref key sets
def refkeys(s):
    s = s.strip()
    if s.startswith('['):
        try:
            v = ast.literal_eval(s)
            return [str(x) for x in v] if isinstance(v, list) else [s]
        except Exception:
            return [s]
    return [s]

cov = {}
multi = Counter()
anchor_span = Counter()  # have_numeric vs all_minus1
prof_refs_bank = Counter()
for entry in qa:
    for char, d in entry.items():
        bank = mem.get(char)
        # profile
        for q in d['profile']:
            rk = refkeys(q['Reference Memory'])
            if len(rk) > 1: multi['profile'] += 1
            key = rk[0]
            if bank is not None and key in bank['profile']:
                prof_refs_bank['hit'] += 1
            else:
                prof_refs_bank['miss:' + ('nobank' if bank is None else 'field')] += 1
            ancs = q['Memory Anchors']
            if all(list(a.values())[0] == [-1, -1] for a in ancs):
                anchor_span['profile_all_minus1'] += 1
            else:
                anchor_span['profile_has_span'] += 1
        for sec, bsec in [('social_relationship', 'social_relationship'), ('events', 'events'), ('dialogues', 'dialogues')]:
            qkeys = []
            qkey2n = Counter()
            for g in d[sec]:
                k = list(g.keys())[0]
                qs = list(g.values())[0]
                qkeys.append(k)
                qkey2n[k] += len(qs)
                for q in qs:
                    rk = refkeys(q['Reference Memory'])
                    if len(rk) > 1 or (len(rk) == 1 and rk[0] != k):
                        multi[(sec, 'ref!=groupkey', k, rk[0] if rk else None)] += 1
                    ancs = q['Memory Anchors']
                    if all(list(a.values())[0] == [-1, -1] for a in ancs):
                        anchor_span[(sec, 'all_minus1')] += 1
                    else:
                        anchor_span[(sec, 'has_span')] += 1
            if bank is None:
                cov[(char, sec)] = ('NOBANK', len(set(qkeys)), 0, sum(qkey2n.values()))
                continue
            braw = bank[bsec]
            if sec == 'social_relationship':
                bparsed, how = parse_bank_social(braw)
            else:
                bparsed, how = (braw, 'dict') if isinstance(braw, dict) else (None, f'unexpected:{type(braw).__name__}')
            bkeys = set(bparsed.keys()) if bparsed is not None else set()
            qk = set(qkeys)
            cov[(char, sec)] = (how, len(qk), len(bkeys), sum(qkey2n.values()), len(qk - bkeys), len(bkeys - qk))
print('profile ref->bank field:', dict(prof_refs_bank))
print('multi/ref-mismatch:', dict(multi))
print('anchor spans:', dict(anchor_span))
n_miss = 0
for (char, sec), v in cov.items():
    if len(v) == 4 or (len(v) == 6 and (v[4] or v[1] == 0)):
        pass
    if len(v) == 6 and v[4]:
        n_miss += 1
        print('KEYMISS', char, sec, 'how=', v[0], 'qkeys=', v[1], 'bkeys=', v[2], 'nQA=', v[3], 'missing=', v[4], 'bankonly=', v[5])
print('chars*sections with QA-key-missing-from-bank:', n_miss)
# QA ref keys that are missing: list them (cap)
shown = 0
for entry in qa:
    for char, d in entry.items():
        for sec, bsec in [('social_relationship', 'social_relationship'), ('events', 'events'), ('dialogues', 'dialogues')]:
            bank = mem.get(char)
            if bank is None:
                continue
            braw = bank[bsec]
            bparsed, how = parse_bank_social(braw) if sec == 'social_relationship' else ((braw, 'dict') if isinstance(braw, dict) else (None, 'x'))
            bkeys = set(bparsed.keys()) if bparsed is not None else set()
            for g in d[sec]:
                k = list(g.keys())[0]
                if k not in bkeys and shown < 15:
                    print('MISSKEY', char, sec, repr(k), 'bank_how=', how)
                    shown += 1
# dialogue turn counts per char + archive N under per-turn itemization
print('--- archive N (per-turn dlg) ---')
for c in qachars:
    b = mem.get(c)
    if b is None:
        print(f'{c!r}: NOBANK'); continue
    nprof = len(b['profile']); nsoc = len(parse_bank_social(b['social_relationship'])[0] or {})
    nev = len(b['events']) if isinstance(b['events'], dict) else -1
    ndg = 0; nturns = 0
    if isinstance(b['dialogues'], dict):
        ndg = len(b['dialogues'])
        for k, v in b['dialogues'].items():
            if isinstance(v, dict) and 'contents' in v and isinstance(v['contents'], dict):
                nturns += sum(len(vv) for vv in v['contents'].values())
            else:
                nturns = -999; break
    N = nprof + 1 + nsoc + nev + nturns
    print(f'{c!r}: prof={nprof} soc={nsoc} ev={nev} dlg={ndg} turns={nturns} N={N} svd96_ok={N>=97}')
