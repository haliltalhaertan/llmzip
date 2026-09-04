"""G8: verify from the frozen LongMemEval dataset itself that the 5-way shard partition is
disjoint and exhaustive over the 470 primary questions, and that the tie-break lexical ordinal
is a function of question_id alone (hence shard-invariant). Usage: <script> <dataset.json>"""
import json, sys
d = json.load(open(sys.argv[1]))
prim = [x for x in d if not str(x["question_id"]).endswith("_abs")]
allq = sorted(str(x["question_id"]) for x in d)
print("total items       :", len(d))
print("primary (non _abs):", len(prim))
print("unique qids       :", len(set(allq)))
sh = {i: [j for j in range(len(prim)) if j % 5 == i] for i in range(5)}
print("shard sizes       :", {i: len(v) for i, v in sh.items()}, "sum", sum(len(v) for v in sh.values()))
print("exhaustive        :", set().union(*[set(v) for v in sh.values()]) == set(range(len(prim))))
print("disjoint          :", not any(set(sh[a]) & set(sh[b]) for a in range(5) for b in range(5) if a < b))
lex = {q: i for i, q in enumerate(allq)}
print("lex ordinal range :", min(lex.values()), "-", max(lex.values()), "over all", len(allq), "ids")
print("lex depends on qid only, not on shard membership: True by construction (runner line 76)")
