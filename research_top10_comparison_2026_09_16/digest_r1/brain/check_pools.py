"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Small read-only checks on stored per-query files (no refitting, no rescoring):
1. RealTalk rotation damage per archive (FULL vs RAND_20260916, qscale Hit@10) vs archive N.
2. Oracle-over-(sym,qscale) Hit@10 on RealTalk FULL.
3. CODE Hit@10-miss decomposition: gold in top-100 pool vs outside (firststage code_top500).
4. Equal-total-storage byte arithmetic from coordinator cost_audit.json.
"""
import json
from collections import defaultdict

R = "/mnt/c/Users/MDP/dev/llmzip-work"
QPATH = R + "/top10_comparison_r1/math_r1/quant/per_query.jsonl"
RPATH = R + "/top10_comparison_r1/math_r1/repr/per_query.jsonl"
FPATH = R + "/top10_comparison_r1/ideas_r1/firststage/per_query.jsonl"
AUDIT = R + "/top10_comparison_r1/coordinator/cost_audit.json"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/brain/check_pools.json"
out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"}

# ---- 1. per-archive rotation damage, RealTalk qscale ----
hit = defaultdict(dict)  # arch -> arm -> [hits]
narch = {}
with open(QPATH, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("benchmark") != "RealTalk" or r.get("scorer") != "qscale":
            continue
        if r.get("arm") not in ("FULL", "RAND_20260916"):
            continue
        hit[r["archive_id"]][r["arm"]] = hit[r["archive_id"]].get(r["arm"], []) + [r["hit10"]]
archN = {"RT01": 662, "RT02": 476, "RT03": 453, "RT04": 422, "RT05": 410,
         "RT06": 1548, "RT07": 1511, "RT08": 1162, "RT09": 1044, "RT10": 1256}
rows = []
for a in sorted(hit):
    f = sum(hit[a]["FULL"]) / len(hit[a]["FULL"])
    d = sum(hit[a]["RAND_20260916"]) / len(hit[a]["RAND_20260916"])
    rows.append({"arch": a, "N": archN[a], "n": len(hit[a]["FULL"]),
                 "full": round(100 * f, 2), "rand": round(100 * d, 2),
                 "delta_pp": round(100 * (d - f), 2)})
out["rotation_per_archive_RT_qscale"] = rows
small = [r for r in rows if r["N"] < 700]
large = [r for r in rows if r["N"] > 1000]
def avg(rs, k):
    return sum(r[k] for r in rs) / len(rs)
out["rotation_small_arch_avg_delta"] = round(avg(small, "delta_pp"), 2)
out["rotation_large_arch_avg_delta"] = round(avg(large, "delta_pp"), 2)

# ---- 2. oracle sym|qscale on RealTalk FULL (repr file has both scorers, FULL arm) ----
both = {}
with open(RPATH, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("benchmark") != "RealTalk" or r.get("arm") != "FULL":
            continue
        q = r["qid"]
        both.setdefault(q, {})[r["scorer"]] = r["hit10"]
n = len(both)
sym = sum(v.get("sym", 0) for v in both.values()) / n
qsc = sum(v.get("qscale", 0) for v in both.values()) / n
orc = sum(max(v.get("sym", 0), v.get("qscale", 0)) for v in both.values()) / n
bothmiss = sum(1 for v in both.values() if v.get("sym", 0) == 0 and v.get("qscale", 0) == 0)
out["oracle_RT_FULL"] = {"n": n, "sym_hit10": round(100 * sym, 2),
                         "qscale_hit10": round(100 * qsc, 2),
                         "oracle_hit10": round(100 * orc, 2),
                         "both_miss_n": bothmiss}

# ---- 3. CODE miss decomposition with code_top500 pool ----
miss_in100 = miss_out100 = hit10n = total = 0
with open(FPATH, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "code_top500" not in r:
            continue
        total += 1
        gold = set(r["gold"])
        top10 = r["code_top500"][:10]
        top100 = set(r["code_top500"][:100])
        if gold & set(top10):
            hit10n += 1
        else:
            if gold & top100:
                miss_in100 += 1
            else:
                miss_out100 += 1
out["code_pool_decomp"] = {"n": total, "hit10": hit10n,
    "miss_gold_in_top100": miss_in100, "miss_gold_outside_top100": miss_out100,
    "pool_hit100": round(100 * (hit10n + miss_in100) / total, 2)}

# ---- 4. byte arithmetic ----
ca = json.load(open(AUDIT, encoding="utf-8"))
n_docs = ca["n_docs"]
code = ca["code_total_B"]
compact = ca["bm25_compact_B"]
text = ca["raw_text_B"]
out["bytes"] = {"n_docs": n_docs, "code_B": code, "bm25_compact_B": compact,
    "raw_text_B": text,
    "bytes_per_doc_if_index_dropped": round(compact / n_docs, 1),
    "bytes_per_doc_if_index_plus_text_dropped": round((compact + text) / n_docs, 1),
    "float96_per_doc_B": 384,
    "ratio_compact_over_code": round(compact / code, 2)}

json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1))
