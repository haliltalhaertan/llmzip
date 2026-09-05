#!/usr/bin/env python3
"""Gate N — test the shard-invariance claim from the persisted bytes alone.

The tie-break RNG seed is 5100000 + lex*100000 + t*100 + 99. If `lex` were the
within-shard position, it would depend on shard membership and the aggregate
would be sharding-dependent. The runner claims `lex` is the GLOBAL
lexicographic rank over all 500 dataset question ids. That is checkable: the
per-question CSV persists the tie_identity string containing global_lex.
"""
import csv, gzip, json, re
rows=[]
with gzip.open("research/v52/longmemeval_boundary_outputs/longmemeval_boundary_per_question.csv.gz","rt",newline="") as fh:
    for r in csv.DictReader(fh): rows.append(r)
lex={}
for r in rows:
    m=re.match(r"global_lex=(\d+);nuisance=(\d+);(.+)$", r["tie_identity"])
    assert m, r["tie_identity"]
    q=r["question_id"]; v=int(m.group(1))
    if q in lex: assert lex[q]==v, f"lex not constant for {q}"
    else: lex[q]=v
    assert m.group(2)=="20"
    assert m.group(3)=="5100000+lex*100000+t*100+99"

qs=sorted(lex)
vals=[lex[q] for q in qs]
strictly_increasing = all(vals[i]<vals[i+1] for i in range(len(vals)-1))
out={
 "n_primary_questions": len(qs),
 "lex_values_unique": len(set(vals))==len(vals),
 "lex_min": min(vals), "lex_max": max(vals),
 "lex_strictly_increasing_in_sorted_qid_order": strictly_increasing,
 "lex_range_consistent_with_500_item_global_sort": (min(vals)>=0 and max(vals)<=499),
 "n_lex_slots_unused": 500-len(vals),
 "nuisance_constant_20": True,
 "tie_seed_formula_constant": True,
 # a shard-dependent index would be 0..46 repeated; check it is not
 "max_lex_exceeds_max_shard_size": max(vals) > (470//10 + 1),
}
# stride reconstruction: which shard each question would land in is i%10 over prim
# order; the per-question file must NOT depend on it. Confirm no shard column exists.
out["no_shard_column_in_per_question_file"]= "shard" not in rows[0].keys()
json.dump(out,open("audit_v52_boundary_localization_independent_2026_09_04/evidence/shard_invariance.json","w"),indent=2)
for k,v in out.items(): print(f"  {k} = {v}")
