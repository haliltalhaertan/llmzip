#!/usr/bin/env python3
import json, math, sys
from pathlib import Path

def ranks(xs):
    # average ranks, 1-based
    order=sorted(range(len(xs)), key=lambda i: xs[i])
    r=[0.0]*len(xs)
    j=0
    while j<len(order):
        k=j+1
        while k<len(order) and xs[order[k]]==xs[order[j]]:
            k+=1
        avg=(j+1+k)/2.0
        for t in range(j,k): r[order[t]]=avg
        j=k
    return r

def pearson(x,y):
    mx=sum(x)/len(x); my=sum(y)/len(y)
    a=[v-mx for v in x]; b=[v-my for v in y]
    num=sum(u*v for u,v in zip(a,b))
    den=math.sqrt(sum(u*u for u in a)*sum(v*v for v in b))
    return num/den if den else float("nan")

def main(inp,out):
    d=json.loads(Path(inp).read_text(encoding="utf-8"))
    xs=[u["polarity_pp"] for u in d["units"]]
    ys=[u["sign_minus_float_pp"] for u in d["units"]]
    concord=sum((x>0)==(y>0) for x,y in zip(xs,ys) if x!=0 and y!=0)
    result={
      "schema":"LLMZIP_E1_BRIDGE_OUTPUT_V1",
      "n_units":len(xs),
      "sign_concordance":f"{concord}/{len(xs)}",
      "pearson_r":pearson(xs,ys),
      "spearman_rho":pearson(ranks(xs),ranks(ys)),
      "interpretation":"Exploratory/post-hoc only. Mixed k (LME=48; others=64), rounded PerLTQA strata, and non-independent PerLTQA sections forbid confirmatory inference.",
      "falsified_simple_story":"Boundary tie rate alone cannot explain the direction of SIGN-minus-float advantage."
    }
    Path(out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":
    main(sys.argv[1],sys.argv[2])
