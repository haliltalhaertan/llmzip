#!/usr/bin/env python3
"""PerLTQA within-archive section flip control for E1.

Same character archive C96 is held fixed. Aggregate committed per-QA outcomes by
(character, section), then test whether profile vs events flips SIGN-float and BOT-TOP
within the same archive. No representation rebuild or rescoring.
"""
from __future__ import annotations
import json,hashlib
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'campaign_2026_09_13/bench3/b3b_perltqa/results.json'
def mean(x): return sum(x)/len(x) if x else None
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads(R.read_text(encoding='utf-8'))['per_q']
g=defaultdict(list)
for qid,r in d.items():
    g[(r['char'],r['section'])].append((100.0*(float(r['native'])-float(r['float'])),float(r['BOT64'])-float(r['TOP64'])))
chars=sorted({k[0] for k in g})
sections=['profile','social_relationship','events','dialogues']
rows=[]
for c in chars:
    rec={'char':c}
    for s in sections:
        rr=g.get((c,s),[])
        rec[s]={'n':len(rr),'delta_pp':mean([x[0] for x in rr]),'p64':mean([x[1] for x in rr])} if rr else None
    rows.append(rec)
valid=[r for r in rows if r['profile'] and r['events']]
def sg(x): return 1 if x>0 else (-1 if x<0 else 0)
counts={
 'n_archives_profile_and_events':len(valid),
 'profile_delta_positive':sum(sg(r['profile']['delta_pp'])>0 for r in valid),
 'events_delta_negative':sum(sg(r['events']['delta_pp'])<0 for r in valid),
 'profile_p64_positive':sum(sg(r['profile']['p64'])>0 for r in valid),
 'events_p64_negative':sum(sg(r['events']['p64'])<0 for r in valid),
 'delta_profile_pos_events_neg':sum(sg(r['profile']['delta_pp'])>0 and sg(r['events']['delta_pp'])<0 for r in valid),
 'p64_profile_pos_events_neg':sum(sg(r['profile']['p64'])>0 and sg(r['events']['p64'])<0 for r in valid),
 'both_joint_flip':sum(sg(r['profile']['delta_pp'])>0 and sg(r['events']['delta_pp'])<0 and sg(r['profile']['p64'])>0 and sg(r['events']['p64'])<0 for r in valid),
}
# General within-archive concordance of section-level signs.
pairs=[]
for r in rows:
    for s in sections:
        x=r[s]
        if x and x['delta_pp']!=0 and x['p64']!=0:
            pairs.append((sg(x['delta_pp']),sg(x['p64'])))
counts['char_section_nonzero_pairs']=len(pairs)
counts['char_section_same_sign']=sum(a==b for a,b in pairs)
counts['char_section_same_sign_fraction']=sum(a==b for a,b in pairs)/len(pairs) if pairs else None
out={'schema':'LLMZIP_E1_PERLTQA_WITHIN_ARCHIVE_FLIP_V1','label':'[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]','scope':'Within-character fixed-archive comparison of semantic sections using committed verified results only.','input':{'results_sha256':sha(R),'n_char':len(chars)},'counts':counts,'interpretation_rule':'A widespread profile-positive/events-negative Delta flip within the same archive refutes archive-only geometry as a sufficient explanation. Parallel P64 flips imply task-relevant variance-tail polarity is query/section dependent even when archive C96 is fixed.','epistemic_note':'Post-hoc controlled comparison. Same archive does not make sections exchangeable; this identifies insufficiency of archive-only explanations, not causality.'}
print(json.dumps(out,indent=2,sort_keys=True))
