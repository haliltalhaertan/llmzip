#!/usr/bin/env python3
"""Numeric-tree diff build vs official for RB2 and RB3."""
import json, math
from pathlib import Path
W=Path("/mnt/c/Users/MDP/dev/llmzip-work/race_2026-09-13")
def walk(a,b,path,diffs):
    if isinstance(a,dict) and isinstance(b,dict):
        ka,kb=set(a),set(b)
        for k in sorted(ka-kb): diffs.append((path+"/"+k,"ONLY_BUILD",repr(a[k])[:120],None))
        for k in sorted(kb-ka): diffs.append((path+"/"+k,"ONLY_OFFICIAL",None,repr(b[k])[:120]))
        for k in sorted(ka&kb): walk(a[k],b[k],path+"/"+k,diffs)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b): diffs.append((path,"LEN",len(a),len(b))); return
        for i,(x,y) in enumerate(zip(a,b)): walk(x,y,f"{path}[{i}]",diffs)
    elif isinstance(a,float) and isinstance(b,float):
        if not (a==b or (math.isnan(a) and math.isnan(b))):
            diffs.append((path,"FLOAT",repr(a),repr(b),repr(a-b)))
    else:
        if a!=b or type(a)!=type(b): diffs.append((path,"VAL",repr(a)[:160],repr(b)[:160]))
for tag,bp,op in [("RB2","rb2/race_sign_details.json","official_run/sign/race_sign_details.json"),
                  ("RB3","rb3/race_faiss_details.json","official_run/faiss/race_faiss_details.json")]:
    b=json.load(open(W/bp)); o=json.load(open(W/op))
    diffs=[]; walk(b,o,"$",diffs)
    print(f"===== {tag} diffs: {len(diffs)} =====")
    for d in diffs[:60]: print(" ",d)
    json.dump(diffs,open(f"/tmp/racev/rv_diff_{tag}.json","w"),indent=1)
