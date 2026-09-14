#!/usr/bin/env python3
"""Disposition arithmetic from official numbers + sealed K membership."""
import json
from pathlib import Path
W=Path("/mnt/c/Users/MDP/dev/llmzip-work/race_2026-09-13")
S=json.load(open(W/"official_run/sign/race_sign_details.json"))
F=json.load(open(W/"official_run/faiss/race_faiss_details.json"))
SIGN_LME=S["LME"]["arms"]["NATIVE96"]["mean"]
SIGN_LOCO=S["LoCoMo"]["arms"]["NATIVE96"]["mean"]
def comp(bench, extra_sign_arms):
    c={}
    for a in extra_sign_arms: c[f"SIGN:{a}"]=S[bench]["arms"][a]["mean"]
    for a in ["A4_spread_rot94101","A4_spread_rot94102","A4_spread_rot94103"]:
        c[f"A4:{a}"]=F["arms_summary"][a]["LME_FR" if bench=="LME" else "LoCoMo_FR"]
    c["A6:A6_PQ"]=F["arms_summary"]["A6_PQ"]["LME_FR" if bench=="LME" else "LoCoMo_FR"]
    return c
lme_rand=[f"RAND{k}_s{j}" for k in (48,64,80) for j in range(10)]
loco_rand=list(lme_rand)
lme_set=lme_rand+["SPREAD48","SPREAD64","SPREAD80","BOT48","TOP48","TOP64"]
loco_set=loco_rand+["SPREAD48","SPREAD64","SPREAD80","BOT80","BOT64","BOT48","TOP48"]
cl=comp("LME",lme_set); co=comp("LoCoMo",loco_set)
assert len(cl)==40 and len(co)==41, (len(cl),len(co))
bl=max(cl,key=cl.get); bo=max(co,key=co.get)
gl=(SIGN_LME-cl[bl])*100; go=(SIGN_LOCO-co[bo])*100
print(f"SIGN LME={SIGN_LME!r} LoCoMo={SIGN_LOCO!r}")
print(f"LME max competitor: {bl}={cl[bl]!r} gap={gl!r}pp")
print(f"LoCoMo max competitor: {bo}={co[bo]!r} gap={go!r}pp")
print("top5 LME:",sorted(cl.items(),key=lambda x:-x[1])[:5])
print("top5 LoCoMo:",sorted(co.items(),key=lambda x:-x[1])[:5])
def zone(g): return "KILL" if g<-6.4 or g<-3.7 else None
print("LME zone:", "KILL" if gl<-6.4 else ("LOW" if gl<-0.5 else ("MID" if gl<2.0 else "PRO")))
print("LoCoMo zone:", "KILL" if go<-3.7 else ("LOW" if go<-0.5 else ("MID" if go<2.0 else "PRO")))
json.dump({"LME":{"sign":SIGN_LME,"max_comp":bl,"max_val":cl[bl],"gap_pp":gl},
 "LoCoMo":{"sign":SIGN_LOCO,"max_comp":bo,"max_val":co[bo],"gap_pp":go}},open("/tmp/racev/rv_dispo.json","w"),indent=1)
