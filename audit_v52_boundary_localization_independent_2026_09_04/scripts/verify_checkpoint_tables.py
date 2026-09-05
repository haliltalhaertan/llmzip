#!/usr/bin/env python3
"""Gate O/M — check every per-seed rho printed in the checkpoint prose against
the auditor's own per-question reconstruction (6 dp as printed)."""
import json,re
R=json.load(open("audit_v52_boundary_localization_independent_2026_09_04/evidence/reconstruction.json"))
txt=open("research/v52/CROSS_DATASET_HEAD_TAIL_BOUNDARY_LOCALIZATION_CHECKPOINT_2026-09-04.md").read()
LBL={"16/80":"B16","24/72":"B24","32/64":"B32","48/48":"B48","64/32":"B64","random 32/64":"RANDOM32"}
sec={}
for ds,key in (("LoCoMo","### LoCoMo"),("LongMemEval","### LongMemEval")):
    i=txt.index(key,txt.index("## 3. All ten per-seed rho values")); j=txt.find("Authoritative",i)
    sec[ds]=txt[i:j]
worst=0.0; bad=[]; n=0
for ds in sec:
    for lbl,arm in LBL.items():
        m=re.search(re.escape("- "+lbl+": `[")+r"([^\]]+)\]",sec[ds])
        assert m,(ds,lbl)
        printed=[float(x) for x in m.group(1).split(",")]
        mine=R[ds]["arm_stats"][arm]["per_seed_rho"]
        assert len(printed)==len(mine)==10
        for k,(p,q) in enumerate(zip(printed,mine)):
            e=abs(p-round(q,6)); n+=1; worst=max(worst,e)
            if e>0: bad.append((ds,lbl,58001+k,p,q))
print(f"checked {n} printed per-seed rho values")
print(f"worst deviation from auditor reconstruction (rounded to 6dp): {worst:.1e}")
print("mismatches:", bad or "NONE")
# headline table means / SE / ranges (3dp as printed)
tbl=[]
for ds in ("LoCoMo","LongMemEval"):
    for lbl,arm in LBL.items():
        m=re.search(r"\|\s*\**"+re.escape(lbl)+r"\**\s*\|\s*\**([\d.]+)\**\s*\|\s*\**([\d.]+)\**\s*\|\s*\**([\d.]+)\**\s*\|\s*\**([\d.]+)[–-]([\d.]+)\**",txt)
        if m: tbl.append((ds,lbl))
json.dump({"n_checked":n,"worst_abs_dev":worst,"mismatches":bad},
          open("audit_v52_boundary_localization_independent_2026_09_04/evidence/checkpoint_table_check.json","w"),indent=2)
