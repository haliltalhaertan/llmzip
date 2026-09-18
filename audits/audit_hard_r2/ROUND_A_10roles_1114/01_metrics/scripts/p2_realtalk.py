"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
01_metrics probe P2 — RealTalk denominator/gold mapping + Hit@10 vs FR@3 join.
Own aggregation code only (no scorer rerun, no coordinator import).
Reads (READ ONLY): top10_comparison_r1/data/RT*.json (raw),
 published audit/per_query_bm25_corrected.jsonl (stored top10),
 published data/exclusions.json.
Checks: total vs valid denominator, per-archive n, gold_size distribution,
 stored Hit@10 vs FR@3 means per arm, comparator BM25 definitions in circulation.
"""
import glob
import json
import os

W = "/mnt/c/Users/MDP/dev/llmzip-work"
PUB = W + "/_wt_top10/research_top10_comparison_2026_09_16"
RAW = W + "/top10_comparison_r1/data"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                   "p2_realtalk_denominator.json")
res = {}

# raw denominator mapping (same rule as decision_tests.py t1: keep queries with
# >=1 gold id present in doc rows)
per_arch, total_q = {}, 0
gold_sizes = {}
for i in range(1, 11):
    aid = f"RT{i:02d}"
    D = json.load(open(f"{RAW}/{aid}.json", encoding="utf-8"))
    docs = D["docs"]
    row_of = {d["row"]: j for j, d in enumerate(docs)}
    qs = D["queries"]
    valid = [q for q in qs
             if any(g in row_of for g in q.get("gold", []))]
    per_arch[aid] = {"n_total": len(qs), "n_valid": len(valid),
                     "n_docs": len(docs)}
    total_q += len(qs)
    for q in valid:
        g = len([x for x in q.get("gold", []) if x in row_of])
        gold_sizes[g] = gold_sizes.get(g, 0) + 1
res["raw_denominator"] = {
    "n_total": total_q,
    "n_valid": sum(v["n_valid"] for v in per_arch.values()),
    "per_archive": per_arch,
    "gold_size_dist_valid": dict(sorted(gold_sizes.items())),
    "multi_gold_share": sum(c for g, c in gold_sizes.items() if g > 1) / max(
        1, sum(gold_sizes.values())),
}
excl = json.load(open(f"{PUB}/data/exclusions.json", encoding="utf-8"))
res["exclusions_agree"] = {
    "n_total": excl["n_total"], "n_valid": excl["n_valid"],
    "n_excluded": excl["n_excluded"],
    "match_raw": (excl["n_total"] == total_q and
                  excl["n_valid"] == sum(v["n_valid"] for v in per_arch.values())),
}

# stored per-query aggregation (own means over stored columns; this file carries
# Hit@10/Recall@10 only — there is no FR@3 column here)
agg = {}
n = 0
for line in open(f"{PUB}/audit/per_query_bm25_corrected.jsonl", encoding="utf-8"):
    r = json.loads(line)
    n += 1
    arm = r.get("arm", "bm25")
    a = agg.setdefault(arm, {"hit": [], "rec10": []})
    h = r["hit_at_10"]
    a["hit"].append(float(h) if not isinstance(h, bool) else (1.0 if h else 0.0))
    a["rec10"].append(float(r["recall_at_10"]))
res["stored_aggregation"] = {
    arm: {"n": len(v["hit"]),
          "hit10": 100 * sum(v["hit"]) / len(v["hit"]),
          "recall10": 100 * sum(v["rec10"]) / len(v["rec10"]),
          "note": "Recall@10 < Hit@10 whenever multi-gold queries are partially hit; "
                  "same join, different estimand — see metric_divergence below"}
    for arm, v in agg.items()
}
res["stored_n"] = n
# Hit@10 vs FR@3 headline divergence, read from copied DECISION_TESTS.json
t1v = dec["T1_fair_baseline"]["bm25_variants"] if "dec" in dir() else None
dec2 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "orig", "DECISION_TESTS.json"),
                      encoding="utf-8"))
b = dec2["T1_fair_baseline"]["bm25_variants"]
res["metric_divergence"] = {
    "tokenizer_worth_hit10_pp": b["frozen_idfonly"]["hit10"] - b["coarse_textbook"]["hit10"],
    "tokenizer_worth_fr3_pp": b["frozen_idfonly"]["fr3"] - b["coarse_textbook"]["fr3"],
    "strongest_variant_by_hit10": dec2["T1_fair_baseline"]["strongest_bm25"]["variant"],
    "strongest_by_hit10_fr3": dec2["T1_fair_baseline"]["strongest_bm25"]["fr3"],
    "fr3_rank_agrees_with_hit10_rank":
        max(b, key=lambda v: b[v]["hit10"]) == max(b, key=lambda v: b[v]["fr3"]),
}

# comparator BM25 definitions currently in circulation (read from copied origs)
lex = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "orig", "lexical_summary.json"),
                     encoding="utf-8"))
dec = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "orig", "DECISION_TESTS.json"),
                     encoding="utf-8"))
t1 = dec["T1_fair_baseline"]["bm25_variants"]
res["comparator_definitions"] = {
    "PROTOCOL_BM25_k1_1.5_unicode_word": lex["arms"]["bm25"]["hit_at_10"] * 100,
    "decision_coarse_textbook_k1_1.2": t1["coarse_textbook"]["hit10"],
    "decision_frozen_textbook_k1_1.2": t1["frozen_textbook"]["hit10"],
    "decision_frozen_idfonly": t1["frozen_idfonly"]["hit10"],
    "lexical_summary_expected_hit_eq_recall_bm25":
        lex["arms"]["bm25"]["expected_hit_at_10"] == lex["arms"]["bm25"]["recall_at_10"],
    "lexical_summary_expected_hit_eq_recall_tfidf":
        lex["arms"]["tfidf"]["expected_hit_at_10"] == lex["arms"]["tfidf"]["recall_at_10"],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
