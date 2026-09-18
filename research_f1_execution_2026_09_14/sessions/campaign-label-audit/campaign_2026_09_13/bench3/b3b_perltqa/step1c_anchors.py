#!/usr/bin/env python3
"""Diagnose anchor misses: normalization, summary-vs-content, samples."""
import json, re
from pathlib import Path
BASE = Path('/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2')
qa = json.load(open(BASE/'perltqa_en_v2.json'))
mem = json.load(open(BASE/'perltmem_en_v2.json'))
def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', s.lower())
# events: test content vs summary vs theme
cc = Counter() if False else __import__('collections').Counter()
tried = 0
shown_none = 0; shown_part = 0
for entry in qa:
    for char, d in entry.items():
        bank = mem.get(char)
        if bank is None: continue
        for g in d['events']:
            k = list(g.keys())[0]
            if k not in bank['events']: continue
            ev = bank['events'][k]
            content = ev.get('content','') or ''
            summary = ev.get('summary','') or ''
            theme = ev.get('theme','') or ''
            for q in list(g.values())[0]:
                ancs = [(list(a.keys())[0], list(a.values())[0]) for a in q['Memory Anchors']]
                num = [t for t, s in ancs if s != [-1,-1]]
                if not num: cc['no_numeric'] += 1; continue
                in_c = sum(1 for t in num if t.lower() in content.lower())
                in_s = sum(1 for t in num if t.lower() in summary.lower())
                in_cn = sum(1 for t in num if norm(t) and norm(t) in norm(content))
                if in_c == 0:
                    cc['none_in_content'] += 1
                    if in_s: cc['none_c_but_in_summary'] += 1
                    if in_cn and not in_s: cc['none_c_fixed_by_norm'] += 1
                    if in_c == 0 and in_s == 0 and shown_none < 3:
                        print('EV-NONE key=',k,'anchors=',num[:4])
                        print('  content[:220]=',content[:220])
                        print('  summary[:220]=',summary[:220])
                        shown_none += 1
                elif in_c < len(num) and shown_part < 2:
                    miss = [t for t in num if t.lower() not in content.lower()]
                    print('EV-PART key=',k,'miss=',miss[:3])
                    print('  content[:300]=',content[:300])
                    shown_part += 1
                tried += 1
print('events:', dict(cc), 'tried=', tried)
# dialogues: sample nones
shown = 0
for entry in qa:
    for char, d in entry.items():
        bank = mem.get(char)
        if bank is None: continue
        for g in d['dialogues']:
            k = list(g.keys())[0]
            if k not in bank['dialogues']: continue
            turns = [str(t) for ts in bank['dialogues'][k]['contents'].values() for t in ts]
            full = '\n'.join(turns)
            for q in list(g.values())[0]:
                ancs = [(list(a.keys())[0], list(a.values())[0]) for a in q['Memory Anchors']]
                num = [t for t, s in ancs if s != [-1,-1]]
                if not num: continue
                if sum(1 for t in num if t.lower() in full.lower()) == 0 and shown < 3:
                    print('DG-NONE key=',k,'Q=',q['Question'][:150])
                    print('  anchors=',num[:5])
                    print('  dlg[:400]=',full[:400])
                    shown += 1
            if shown >= 3: break
        if shown >= 3: break
    if shown >= 3: break
