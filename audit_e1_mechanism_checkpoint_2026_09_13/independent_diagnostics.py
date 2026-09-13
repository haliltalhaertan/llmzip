#!/usr/bin/env python3
"""Independent E1 mechanism-checkpoint diagnostics.

Reads only already-committed exploratory campaign surfaces named by the audit prompt.
It does not read Task4F1 material and does not rebuild/refit representations.
"""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit_e1_mechanism_checkpoint_2026_09_13"

PATHS = {
    "question_level": ROOT / "docs/v52/task4c2/V52_T4C2_question_level.csv",
    "lme_geometry": ROOT / "campaign_2026_09_13/regen/lme/task1_extension_lme.json",
    "per_axis_npz": ROOT / "campaign_2026_09_13/pilots_round1/per_axis_matrices.npz",
    "lme_race": ROOT / "campaign_2026_09_13/race/rb2/race_sign_details.json",
    "perltqa": ROOT / "campaign_2026_09_13/bench3/b3b_perltqa/results.json",
    "realtalk_details": ROOT / "campaign_2026_09_13/bench3/b3a_realtalk/details.json",
    "realtalk_summary": ROOT / "campaign_2026_09_13/bench3/b3a_realtalk/rt_summary.json",
}
EXPECTED = {
    "question_level": "69c21b2ffaea1e92923bf3f0e83287e12d07a5f34b4b42afde1752d6b50b3b51",
    "lme_geometry": "682440a0e3329ebab223d45079455ff3b7f97122244cf077a969ce887dfe25da",
    "per_axis_npz": "be8c645d241bac3b913cfcf24f5533c55775a383b46a5f43401d633c873a635a",
    "lme_race": "87a4d1f2ac3da82ee5593e70d5b5347320349d8d266d895debe4a35698a76375",
    "perltqa": "ec9b8b2c7f384fe2f56c72fdc7a7216930a9db35eda2c4441496c8ad401bf958",
    "realtalk_details": "8bae1d380240adc856f8a787b142286efc16fd1d30dfc03bed7e5074769d1757",
    "realtalk_summary": "8e725fca6dff584f853ef9dbf6888b700b12acd1dde42752417f3fa5302bf946",
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def ranks(xs, mode="average"):
    xs = list(xs)
    order = sorted(range(len(xs)), key=lambda i: (xs[i], i))
    out = [0.0] * len(xs)
    j = 0
    dense = 1
    while j < len(order):
        k = j + 1
        while k < len(order) and xs[order[k]] == xs[order[j]]:
            k += 1
        if mode == "average":
            val = (j + 1 + k) / 2.0
        elif mode == "dense":
            val = float(dense)
        elif mode == "ordinal_low":
            val = float(j + 1)
        else:
            raise ValueError(mode)
        for t in range(j, k):
            out[order[t]] = val
        j = k
        dense += 1
    return out


def pearson(x, y):
    x = list(map(float, x)); y = list(map(float, y))
    if len(x) != len(y) or not x:
        return None
    mx = mean(x); my = mean(y)
    dx = [a - mx for a in x]; dy = [b - my for b in y]
    den = math.sqrt(sum(a*a for a in dx) * sum(b*b for b in dy))
    return sum(a*b for a,b in zip(dx,dy)) / den if den else None


def spearman(x, y, mode="average"):
    return pearson(ranks(x, mode), ranks(y, mode))


def weighted_pearson(x, y, w):
    x = list(map(float, x)); y = list(map(float, y)); w = list(map(float, w))
    sw = sum(w)
    if not sw:
        return None
    mx = sum(a*c for a,c in zip(x,w))/sw
    my = sum(b*c for b,c in zip(y,w))/sw
    num = sum(c*(a-mx)*(b-my) for a,b,c in zip(x,y,w))
    den = math.sqrt(sum(c*(a-mx)**2 for a,c in zip(x,w))*sum(c*(b-my)**2 for b,c in zip(y,w)))
    return num/den if den else None


def safe_num(x):
    return x if x is None or math.isfinite(float(x)) else None


def find_arm(obj, name, n):
    hits=[]
    def walk(x, path):
        if isinstance(x, dict):
            if name in x and isinstance(x[name], dict):
                v=x[name]
                if isinstance(v.get("fr"), list) and len(v["fr"]) == n:
                    hits.append((path+(name,), v["fr"]))
            for k,v in x.items():
                walk(v, path+(str(k),))
        elif isinstance(x, list):
            for i,v in enumerate(x):
                if isinstance(v, (dict,list)):
                    walk(v, path+(str(i),))
    walk(obj, ())
    if len(hits) != 1:
        raise RuntimeError(f"arm {name}: {len(hits)} hits")
    return "/".join(hits[0][0]), list(map(float,hits[0][1]))


def pair_stats(rows):
    x=[r["p64"] for r in rows]; y=[r["delta_pp"] for r in rows]
    nz=[(a,b) for a,b in zip(x,y) if a != 0 and b != 0]
    return {
        "n":len(rows), "mean_p64":mean(x), "mean_delta_pp":mean(y),
        "pearson":pearson(x,y), "spearman":spearman(x,y),
        "spearman_dense_rank":spearman(x,y,"dense"),
        "same_sign_nonzero":sum((a>0)==(b>0) for a,b in nz)/len(nz) if nz else None,
        "n_nonzero_both":len(nz),
        "unique_p64":len(set(x)), "unique_delta":len(set(y)),
    }


def jackknife_rho(rows):
    if len(rows) < 4:
        return None
    vals=[]
    for i in range(len(rows)):
        rr=rows[:i]+rows[i+1:]
        vals.append(spearman([r["p64"] for r in rr],[r["delta_pp"] for r in rr]))
    return {"min":min(vals),"max":max(vals),"mean":mean(vals),"n":len(vals)}


out={
    "schema":"LLMZIP_INDEPENDENT_E1_AUDIT_DIAGNOSTICS_V1",
    "label":"[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
    "hashes":{}, "claim_A":{}, "claim_B":{}, "claim_C":{}, "claim_D":{},
    "claim_E":{}, "claim_F":{}, "claim_G":{}, "claim_H":{}, "static_checks":{},
    "limitations":{
        "raw_C96_qC_V2_metrics":"NOT_RUN / NOT_AVAILABLE in committed campaign snapshot; no refit attempted",
        "locomo_centered_float_per_query":"NOT_RUN / NOT_AVAILABLE; no value invented",
    }
}

# Exact input byte checks.
for k,p in PATHS.items():
    got=sha256(p)
    out["hashes"][k]={"path":str(p.relative_to(ROOT)),"sha256":got,"expected":EXPECTED[k],"match":got==EXPECTED[k]}
if not all(v["match"] for v in out["hashes"].values()):
    raise SystemExit("HASH_GATE_FAIL")

# ---------- Claim A ----------
with PATHS["question_level"].open(newline="",encoding="utf-8") as f:
    qraw=list(csv.DictReader(f))
qids=[r["question_id"] for r in qraw]
qdup=[k for k,v in Counter(qids).items() if v>1]
q={r["question_id"]:r for r in qraw}
gobj=json.loads(PATHS["lme_geometry"].read_text(encoding="utf-8"))
graw=gobj["archives"]
gids=[r["question_id"] for r in graw]
gdup=[k for k,v in Counter(gids).items() if v>1]
g={r["question_id"]:r for r in graw}
metrics=["cv_sigma","top32_share","corr_off_mass","corr_median_abs","corr_p95_abs","sign_entropy_gt","N"]
rows=[]
scale_err=0.0
for qid in sorted(set(q)&set(g)):
    qr=q[qid]; gr=g[qid]
    d=float(qr["sign_minus_centered_float_fractional_pp"])
    derived=100.0*(float(qr["sign96_centered_fractional_r3"])-float(qr["float96_centered_fractional_r3"]))
    scale_err=max(scale_err,abs(d-derived))
    rows.append({"qid":qid,"type":qr["question_type"],"delta_pp":d,
                 "cv_sigma":float(gr["cv_sigma"]),"top32_share":float(gr["top32_share"]),
                 "corr_off_mass":float(gr["corr_off_mass"]),"corr_median_abs":float(gr["corr_median_abs"]),
                 "corr_p95_abs":float(gr["corr_p95_abs"]),"sign_entropy_gt":float(gr["sign_entropy_gt"]),"N":float(gr["N"])})
cor={}
for m in metrics:
    x=[r[m] for r in rows]; y=[r["delta_pp"] for r in rows]
    cor[m]={"spearman":spearman(x,y),"pearson":pearson(x,y),"nonfinite":sum(not math.isfinite(v) for v in x)}
# leave-one-question-type-out to detect one stratum driving the overall conclusion
loo={}
for qt in sorted(set(r["type"] for r in rows)):
    rr=[r for r in rows if r["type"]!=qt]
    loo[qt]={m:spearman([r[m] for r in rr],[r["delta_pp"] for r in rr]) for m in metrics}
out["claim_A"]={
    "n_csv_rows":len(qraw),"n_geom_rows":len(graw),"duplicate_csv_qids":qdup,"duplicate_geom_qids":gdup,
    "join_exact":set(q)==set(g),"n_join":len(rows),"max_pp_scale_identity_error":scale_err,
    "N_mismatches":sum(int(q[qid]["N_archive"])!=int(g[qid]["N"]) for qid in set(q)&set(g)),
    "correlations":cor,"leave_one_question_type_out_spearman":loo,
}

# ---------- Claims B/C from pre-existing NPZ ----------
d=np.load(PATHS["per_axis_npz"],allow_pickle=False)
keys=sorted(d.files)
D=np.asarray(d["delta"],float); alone=np.asarray(d["alone"],float); drop=np.asarray(d["drop"],float); vr=np.asarray(d["var_rank"],int)
npz_qids=[str(x) for x in d["qids"]]
axis_rows=[]; context_rows=[]
for i,qid in enumerate(npz_qids):
    x=D[i]; pos=np.maximum(x,0.0); neg=-np.minimum(x,0.0); ps=float(pos.sum()); p2=float(np.sum(pos*pos)); order=np.sort(pos)[::-1]
    axis_rows.append({"delta_pp":float(q[qid]["sign_minus_centered_float_fractional_pp"]),
      "positive_effdim":float(ps*ps/p2) if p2 else None,"positive_top32_share":float(order[:32].sum()/ps) if ps else None,
      "positive_top16_share":float(order[:16].sum()/ps) if ps else None,"positive_mass":ps,"negative_mass":float(neg.sum())})
    top=vr[i]<48; bot=vr[i]>=48
    native=float(q[qid]["sign96_centered_fractional_r3"]); loss=native-drop[i]
    context_rows.append({"delta_pp":float(q[qid]["sign_minus_centered_float_fractional_pp"]),
      "loss_top":float(loss[top].mean()),"loss_bot":float(loss[bot].mean()),"gap":float(loss[bot].mean()-loss[top].mean()),
      "alone_top":float(alone[i,top].mean()),"alone_bot":float(alone[i,bot].mean())})
axis_metrics=["positive_effdim","positive_top32_share","positive_top16_share","positive_mass","negative_mass"]
out["claim_B"]={
    "npz_keys":keys,"delta_shape":list(D.shape),"alone_shape":list(alone.shape),"drop_shape":list(drop.shape),"var_rank_shape":list(vr.shape),
    "qid_exact":set(npz_qids)==set(q),"delta_nonfinite":int(np.sum(~np.isfinite(D))),
    "delta_semantics_from_generator":"gold sign-agreement rate minus nongold sign-agreement rate; gold-informed explanatory surface",
    "spearman":{m:spearman([r[m] for r in axis_rows if r[m] is not None],[r["delta_pp"] for r in axis_rows if r[m] is not None]) for m in axis_metrics},
}
out["claim_C"]={
    "drop_loss_formula":"native - drop[q,j]",
    "top_definition":"var_rank < 48","bot_definition":"var_rank >= 48",
    "mean_loss_top":mean(r["loss_top"] for r in context_rows),"mean_loss_bot":mean(r["loss_bot"] for r in context_rows),
    "mean_alone_top":mean(r["alone_top"] for r in context_rows),"mean_alone_bot":mean(r["alone_bot"] for r in context_rows),
    "rho_delta_bot_minus_top":spearman([r["gap"] for r in context_rows],[r["delta_pp"] for r in context_rows]),
    "rho_delta_abs_top":spearman([r["loss_top"] for r in context_rows],[r["delta_pp"] for r in context_rows]),
    "rho_delta_abs_bot":spearman([r["loss_bot"] for r in context_rows],[r["delta_pp"] for r in context_rows]),
}

# ---------- Claim D: P64 across LME, PerLTQA, REALTALK ----------
race=json.loads(PATHS["lme_race"].read_text(encoding="utf-8")); lme=race["LME"]; lq=[str(x) for x in lme["qids"]]; n=len(lq)
arm_paths={}; arms={}
for name in ["NATIVE96","TOP64","BOT64"]:
    arm_paths[name],arms[name]=find_arm(lme,name,n)
lme_rows=[]
for i,qid in enumerate(lq):
    lme_rows.append({"delta_pp":float(q[qid]["sign_minus_centered_float_fractional_pp"]),"p64":arms["BOT64"][i]-arms["TOP64"][i]})

P=json.loads(PATHS["perltqa"].read_text(encoding="utf-8"))
per_rows=[]
for qid,r in P["per_q"].items():
    per_rows.append({"qid":qid,"char":r["char"],"section":r["section"],"tie":int(r["tie"]),
      "delta_pp":100.0*(float(r["native"])-float(r["float"])),"p64":float(r["BOT64"])-float(r["TOP64"])})
bychar=defaultdict(list)
for r in per_rows: bychar[r["char"]].append(r)
char_rows=[]
for c,rr in sorted(bychar.items()):
    char_rows.append({"unit":c,"n_q":len(rr),"delta_pp":mean(x["delta_pp"] for x in rr),"p64":mean(x["p64"] for x in rr)})

R=json.loads(PATHS["realtalk_details"].read_text(encoding="utf-8")); S=json.loads(PATHS["realtalk_summary"].read_text(encoding="utf-8"))
rt_rows=[]
for r in R["per_qa"]:
    if int(r["valid"]) != 1: continue
    a=r["arms"]
    rt_rows.append({"qid":r["qid"],"chat":str(r["chat"]),"cat":int(r["cat"]),
      "delta_pp":100.0*(float(a["NATIVE96"])-float(a["FLOAT96"])),"p64":float(a["BOT64"])-float(a["TOP64"])})
bychat=defaultdict(list)
for r in rt_rows: bychat[r["chat"]].append(r)
chat_rows=[]
for c,rr in sorted(bychat.items()):
    chat_rows.append({"unit":c,"n_q":len(rr),"delta_pp":mean(x["delta_pp"] for x in rr),"p64":mean(x["p64"] for x in rr)})

out["claim_D"]={
    "LME_per_query":pair_stats(lme_rows),
    "PerLTQA_per_query":pair_stats(per_rows),"PerLTQA_by_character_unweighted":pair_stats(char_rows),
    "PerLTQA_character_query_weighted_pearson":weighted_pearson([r["p64"] for r in char_rows],[r["delta_pp"] for r in char_rows],[r["n_q"] for r in char_rows]),
    "PerLTQA_character_max_query_share":max(r["n_q"] for r in char_rows)/sum(r["n_q"] for r in char_rows),
    "PerLTQA_character_leave_one_out_rho":jackknife_rho(char_rows),
    "REALTALK_per_query":pair_stats(rt_rows),"REALTALK_by_chat_unweighted":pair_stats(chat_rows),
    "REALTALK_chat_query_weighted_pearson":weighted_pearson([r["p64"] for r in chat_rows],[r["delta_pp"] for r in chat_rows],[r["n_q"] for r in chat_rows]),
    "REALTALK_chat_max_query_share":max(r["n_q"] for r in chat_rows)/sum(r["n_q"] for r in chat_rows),
    "REALTALK_chat_leave_one_out_rho":jackknife_rho(chat_rows),
}

# ---------- Claim E: within semantic strata and small-n fragility ----------
psec={}
for sec in sorted(set(r["section"] for r in per_rows)):
    units=[]
    for c,rr in sorted(bychar.items()):
        ss=[r for r in rr if r["section"]==sec]
        if ss: units.append({"unit":c,"n_q":len(ss),"delta_pp":mean(x["delta_pp"] for x in ss),"p64":mean(x["p64"] for x in ss)})
    psec[sec]={"stats":pair_stats(units),"jackknife_rho":jackknife_rho(units)}
rcat={}
for cat in sorted(set(r["cat"] for r in rt_rows)):
    units=[]
    for c,rr in sorted(bychat.items()):
        ss=[r for r in rr if r["cat"]==cat]
        if ss: units.append({"unit":c,"n_q":len(ss),"delta_pp":mean(x["delta_pp"] for x in ss),"p64":mean(x["p64"] for x in ss)})
    rcat[str(cat)]={"stats":pair_stats(units),"jackknife_rho":jackknife_rho(units)}
out["claim_E"]={"perltqa_character_within_section":psec,"realtalk_chat_within_category":rcat,
    "note":"Average-rank Spearman is primary; dense-rank and leave-one-unit-out are reviewer tie/small-n diagnostics."}

# ---------- Claim F: within-archive profile/events flips ----------
g=defaultdict(list)
for r in per_rows: g[(r["char"],r["section"])].append(r)
chars=sorted({r["char"] for r in per_rows})
def sgn(x): return 1 if x>0 else (-1 if x<0 else 0)
fixed=[]
for c in chars:
    rec={}
    for sec in sorted(set(r["section"] for r in per_rows)):
        rr=g.get((c,sec),[])
        if rr: rec[sec]={"delta_pp":mean(x["delta_pp"] for x in rr),"p64":mean(x["p64"] for x in rr),"n":len(rr)}
    fixed.append((c,rec))
valid=[rec for _,rec in fixed if "profile" in rec and "events" in rec]
pairs=[]
for _,rec in fixed:
    for sec,x in rec.items():
        if x["delta_pp"]!=0 and x["p64"]!=0: pairs.append((sgn(x["delta_pp"]),sgn(x["p64"])))
step2=(ROOT/"campaign_2026_09_13/bench3/b3b_perltqa/step2_eval.py").read_text(encoding="utf-8")
out["claim_F"]={
    "pipeline_same_archive_static_checks":{
        "archive_structures_keyed_by_char":"for char, a in arch.items()" in step2 and "A[char]" in step2,
        "document_C_loaded_from_A_char":"C = a['C']" in step2 or "C=a['C']" in step2,
        "query_qC_loaded_per_query":"qC = np.asarray(q['qC']" in step2,
    },
    "n_archives_profile_events":len(valid),
    "events_delta_negative":sum(sgn(r["events"]["delta_pp"])<0 for r in valid),
    "events_p64_negative":sum(sgn(r["events"]["p64"])<0 for r in valid),
    "profile_delta_positive":sum(sgn(r["profile"]["delta_pp"])>0 for r in valid),
    "profile_p64_positive":sum(sgn(r["profile"]["p64"])>0 for r in valid),
    "both_joint_flip":sum(sgn(r["profile"]["delta_pp"])>0 and sgn(r["events"]["delta_pp"])<0 and sgn(r["profile"]["p64"])>0 and sgn(r["events"]["p64"])<0 for r in valid),
    "char_section_nonzero_pairs":len(pairs),"char_section_same_sign":sum(a==b for a,b in pairs),
}

# ---------- Claim G: tie-rate / tie-conditioned P64 ----------
def tie_group(rr):
    tied=[r for r in rr if r["tie"]]; untied=[r for r in rr if not r["tie"]]
    return {"n":len(rr),"tie_rate":mean(r["tie"] for r in rr),"delta_all":mean(r["delta_pp"] for r in rr),
            "delta_tied":mean(r["delta_pp"] for r in tied),"delta_untied":mean(r["delta_pp"] for r in untied),
            "p64_tied":mean(r["p64"] for r in tied),"p64_untied":mean(r["p64"] for r in untied)}
bysec={sec:tie_group([r for r in per_rows if r["section"]==sec]) for sec in sorted(set(r["section"] for r in per_rows))}
unt=[r for r in per_rows if not r["tie"]]; tied=[r for r in per_rows if r["tie"]]
out["claim_G"]={
    "by_section":bysec,"untied_pair_stats":pair_stats(unt),"tied_pair_stats":pair_stats(tied),
    "untied_by_section":{sec:pair_stats([r for r in unt if r["section"]==sec]) for sec in bysec},
}

# ---------- Claim H / static hygiene ----------
checkpoint=(ROOT/"campaign_2026_09_13/e1_mechanism/E1_MECHANISM_CHECKPOINT.md").read_text(encoding="utf-8")
e1dir=ROOT/"campaign_2026_09_13/e1_mechanism"
scripts=sorted(e1dir.glob("e1_*.py"))
static={}
for p in scripts:
    txt=p.read_text(encoding="utf-8")
    static[p.name]={
        "mentions_task4f1": "task4f1" in txt.lower(),
        "reads_committed_e1_result": "E1_" in txt and "RESULT.json" in txt,
        "contains_fit_call": ".fit(" in txt or "fit_transform(" in txt,
        "contains_svd_refit_marker": "TruncatedSVD" in txt or "TfidfVectorizer" in txt,
    }
out["static_checks"]={"scripts":static,"all_no_task4f1":all(not v["mentions_task4f1"] for v in static.values()),
    "all_no_result_as_input":all(not v["reads_committed_e1_result"] for v in static.values()),
    "all_no_obvious_refit":all(not v["contains_fit_call"] and not v["contains_svd_refit_marker"] for v in static.values())}
out["claim_H"]={
    "checkpoint_contains_not_causal":"not causal" in checkpoint.lower() or "not causal proof" in checkpoint.lower(),
    "checkpoint_denies_deployable_query_predictor":"individual-query predictor" in checkpoint.lower() or "not an individual-query law" in checkpoint.lower(),
    "checkpoint_narrow_hypothesis_present":"query–archive regime interaction" in checkpoint and "descriptive marker" in checkpoint,
    "checkpoint_task4f1_block_present":"SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN" in checkpoint,
}

# Cross-check headline aggregate gates without using committed E1 derived results.
out["source_gates"]={
    "perltqa_n":len(per_rows),
    "perltqa_delta_mean_vs_aggregate_error":abs(mean(r["delta_pp"] for r in per_rows)-100.0*(float(P["aggregate"]["native"]["mean"])-float(P["aggregate"]["float"]["mean"]))),
    "perltqa_p64_mean_vs_aggregate_error":abs(mean(r["p64"] for r in per_rows)-(float(P["aggregate"]["BOT64"]["mean"])-float(P["aggregate"]["TOP64"]["mean"]))),
    "realtalk_n_valid":len(rt_rows),
    "realtalk_delta_mean_vs_summary_error":abs(mean(r["delta_pp"] for r in rt_rows)-100.0*(float(S["arm_means"]["NATIVE96"])-float(S["arm_means"]["FLOAT96"]))),
    "realtalk_p64_mean_vs_summary_error":abs(mean(r["p64"] for r in rt_rows)-(float(S["arm_means"]["BOT64"])-float(S["arm_means"]["TOP64"])),
}

OUT.mkdir(parents=True,exist_ok=True)
path=OUT/"INDEPENDENT_DIAGNOSTICS.json"
path.write_text(json.dumps(out,indent=2,sort_keys=True),encoding="utf-8")
print(json.dumps(out,indent=2,sort_keys=True))
print(f"WROTE {path.relative_to(ROOT)}")
