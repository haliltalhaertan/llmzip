"""Read-only reaggregation of stored raw rows (explicit verification)."""
import json, collections
p = "/mnt/c/Users/MDP/dev/llmzip-work/residual8_pilot_r1/perltqa/per_query.jsonl"
n=0; sb=ss=sm=sf=0.0; rsum=[0.0]*20; keys=None
with open(p) as f:
    for line in f:
        d=json.loads(line)
        if keys is None: keys=sorted(d.keys())
        sb+=d["base_sign"]; ss+=d["sign_only8"]; sm+=d["mag8"]; sf+=d["float_exact"]; n+=1
        for i,v in enumerate(d["random8"]): rsum[i]+=v
print(f"R8 PerLTQA n={n} BASE={sb/n:.15f} SIGN8={ss/n:.15f} MAG8={sm/n:.15f} FLOAT={sf/n:.15f}")
print(f"MAG8-BASE={(sm-sb)/n*100:.6f}pp MAG8-SIGN8={(sm-ss)/n*100:.6f}pp")
print(f"RANDOM8 seed-mean={sum(rsum)/20/n:.15f} best-global-seed-idx={max(range(20),key=lambda i:rsum[i])} best={max(rsum)/n:.15f}")
# per-query-max oracle inflation check (gold-dependent cherry-pick, NOT deployable)
import itertools
s=0.0
with open(p) as f:
    for line in f:
        d=json.loads(line); s+=max(d["random8"])
print(f"RANDOM8 per-query-max mean={s/n:.15f} (oracle selection; inflate vs best-global by {(s-max(rsum))/n*100:.4f}pp)")
print(f"row keys={keys}")
p2="/mnt/c/Users/MDP/dev/llmzip-work/parallel_ideas_r1/b8/per_query.jsonl"
agg=collections.defaultdict(lambda:[0,0.0,0.0,0.0])
with open(p2) as f:
    for line in f:
        d=json.loads(line)
        b=d.get("benchmark","?")
        agg[b][0]+=1; agg[b][1]+=d["fr_sym"]; agg[b][2]+=d["fr_asym"]; agg[b][3]+=d["fr_b8"]
for b,(nn,x,a,bb) in sorted(agg.items()):
    print(f"B8 {b} n={nn} sym={x/nn:.6f} asym={a/nn:.6f} b8={bb/nn:.6f} b8-asym={(bb-a)/nn:.6f}")
