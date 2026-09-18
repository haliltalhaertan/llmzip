#!/usr/bin/env python3
"""DATA audit A+B: dataset inventory + gold sanity. READ-ONLY on sources; writes only to CWD out."""
import json, os, glob, pickle, csv
from collections import Counter

OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/data"
W = "/mnt/c/Users/MDP/dev/llmzip-work"

def jdump(o, fn):
    json.dump(o, open(os.path.join(OUT, fn), "w"), indent=1)

# ---- RealTalk ----
rt = {}
Ns, nq = {}, {}
for i in range(1, 11):
    aid = f"RT{i:02d}"
    d = json.load(open(f"{W}/top10_comparison_r1/data/{aid}.json"))
    docs = d["docs"]; qs = d["queries"]
    rt[aid] = {"n_docs": len(docs), "n_q": len(qs)}
    Ns[aid] = len(docs); nq[aid] = len(qs)
excl = json.load(open(f"{W}/top10_comparison_r1/data/exclusions.json"))
print("RealTalk per-archive:", rt)
print("RealTalk total docs:", sum(Ns.values()), "valid Q:", sum(nq.values()), "excluded:", len(excl) if isinstance(excl, list) else excl)

# gold sanity RealTalk: gold in range? multi-gold sizes? dup doc texts? empty docs?
import re
gold_sizes = Counter(); oor = 0; empty_docs = 0; near_empty = 0
dup_texts = 0
for i in range(1, 11):
    aid = f"RT{i:02d}"
    d = json.load(open(f"{W}/top10_comparison_r1/data/{aid}.json"))
    N = len(d["docs"])
    seen = Counter(t["text"] for t in d["docs"])
    dup_texts += sum(c - 1 for c in seen.values() if c > 1)
    for t in d["docs"]:
        if len(t["text"].strip()) == 0: empty_docs += 1
        if len(t["text"].split()) <= 1: near_empty += 1
    for q in d["queries"]:
        gold_sizes[len(q["gold"])] += 1
        for g in q["gold"]:
            if not (0 <= g < N): oor += 1
print("RT gold-size hist:", dict(sorted(gold_sizes.items())[:15]), "... total keys:", len(gold_sizes))
print("RT gold out-of-range:", oor, "empty docs:", empty_docs, "near-empty(<=1 tok):", near_empty, "dup doc texts (extra copies):", dup_texts)
jdump({"per_archive": rt, "gold_sizes": dict(gold_sizes), "oor": oor, "empty": empty_docs, "near_empty": near_empty, "dup_extra": dup_texts}, "audit_rt_gold.json")

# ---- PerLTQA via ablation per_query + caches ----
arch_cache = pickle.load(open(f"{W}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
qdat = pickle.load(open(f"{W}/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
print("PerLTQA n_arch:", len(arch_cache), "n_q:", len(qdat))
archN = {c: arch_cache[c]["N"] for c in sorted(arch_cache)}
print("PerLTQA N: min", min(archN.values()), "max", max(archN.values()), "median", sorted(archN.values())[15], "total docs:", sum(archN.values()))
gs = Counter(len(qdat[q]["gold"]) for q in qdat)
print("PerLTQA gold-size hist (first 15):", dict(sorted(gs.items())[:15]))
oor2 = 0; empty_gold = 0
for q, r in qdat.items():
    N = arch_cache[r["char"]]["N"]
    if len(r["gold"]) == 0: empty_gold += 1
    for g in list(r["gold"]):
        if not (0 <= int(g) < N): oor2 += 1
print("PerLTQA empty-gold:", empty_gold, "oor gold:", oor2)
# check per_query.jsonl gold agreement FULL/sym vs QDAT
n_chk = 0; mism = 0
for line in open(f"{W}/top10_comparison_r1/ablation_r2/perltqa/per_query.jsonl"):
    r = json.loads(line)
    if r["arm"] == "FULL" and r["scorer"] == "sym":
        n_chk += 1
        if list(r["gold"]) != list(map(int, qdat[r["qid"]]["gold"])): mism += 1
print("PerLTQA per_query FULL/sym rows:", n_chk, "gold mismatches vs cache:", mism)
# dup gold rows within a query?
dupgold = sum(1 for q in qdat if len(set(map(int, qdat[q]["gold"]))) != len(qdat[q]["gold"]))
print("PerLTQA queries w/ duplicate gold entries:", dupgold)
jdump({"archN": archN, "gold_sizes": {str(k): v for k, v in gs.items()}, "empty_gold": empty_gold, "oor": oor2, "dupgold": dupgold, "mism": mism}, "audit_perltqa_gold.json")
