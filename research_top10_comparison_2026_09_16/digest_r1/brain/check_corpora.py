"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Small read-only corpus comparison: RealTalk vs PerLTQA structure.
Reads inputs only; writes one JSON + prints summary. No fitting, no benchmark."""
import json, math, os, pickle, re
from collections import Counter

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/check_corpora.json"
WORD = re.compile(r"\w+", re.UNICODE)

def toks(s):
    return WORD.findall((s or "").lower())

out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"}

# ---- RealTalk: raw texts on disk ----
rt_docs, rt_qs = [], []
rt_per_arch = {}
for i in range(1, 11):
    a = f"RT{i:02d}"
    exp = json.load(open(f"{DATA}/{a}.json", encoding="utf-8"))
    docs = [x["text"] for x in exp["docs"]]
    qs = [x["text"] for x in exp["queries"]]
    rt_docs += [(a, t) for t in docs]
    rt_qs += [(a, t) for t in qs]
    rt_per_arch[a] = {"n_docs": len(docs), "n_queries": len(qs)}

def stats(texts):
    ls = [len(toks(t)) for _, t in texts]
    cs = [len(t) for _, t in texts]
    ls_sorted = sorted(ls)
    def pct(p):
        return ls_sorted[min(len(ls_sorted) - 1, int(p * len(ls_sorted)))]
    return {"n": len(ls), "mean_tok": sum(ls) / len(ls), "median_tok": pct(0.5),
            "p10_tok": pct(0.10), "p90_tok": pct(0.90), "mean_chars": sum(cs) / len(cs)}

out["realtalk_docs"] = stats(rt_docs)
out["realtalk_queries"] = stats(rt_qs)
out["realtalk_per_archive"] = rt_per_arch

# df spectrum on one mid-size archive (RT06, 1548 docs) vs small (RT05, 410 docs)
for a in ("RT05", "RT06"):
    exp = json.load(open(f"{DATA}/{a}.json", encoding="utf-8"))
    dtok = [set(toks(x["text"])) for x in exp["docs"]]
    N = len(dtok)
    df = Counter()
    for s in dtok:
        for t in s:
            df[t] += 1
    vals = sorted(df.values())
    out[f"{a}_vocab"] = len(df)
    out[f"{a}_df"] = {"N": N, "df1": sum(1 for v in vals if v == 1),
                      "df_le2": sum(1 for v in vals if v <= 2),
                      "df_le5": sum(1 for v in vals if v <= 5),
                      "frac_vocab_df1": sum(1 for v in vals if v == 1) / len(vals),
                      "median_df": vals[len(vals) // 2]}

# ---- PerLTQA: cached matrices + texts if present ----
pq_arch = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
pq_q = pickle.load(open(R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
out["perltqa_n_archives"] = len(pq_arch)
ns = []
cs_shapes = []
for k, v in pq_arch.items():
    if isinstance(v, dict) and "C" in v:
        import numpy as np
        C = np.asarray(v["C"])
        ns.append(int(C.shape[0]))
        cs_shapes.append(list(C.shape))
ns_sorted = sorted(ns)
out["perltqa_docs_per_archive"] = {"n_arch": len(ns_sorted), "total_docs": sum(ns_sorted),
    "min": ns_sorted[0], "median": ns_sorted[len(ns_sorted)//2], "max": ns_sorted[-1],
    "mean": sum(ns_sorted)/len(ns_sorted)}
out["perltqa_C_shape_example"] = cs_shapes[0] if cs_shapes else None
out["perltqa_n_query_rows"] = len(pq_q)
# query key sample
qk = next(iter(pq_q))
out["perltqa_query_key_sample"] = str(qk)[:120]
qv = pq_q[qk]
out["perltqa_query_val_type"] = str(type(qv))[:120]
if isinstance(qv, dict):
    out["perltqa_query_val_keys"] = list(qv.keys())[:20]

# PerLTQA raw texts? look for items/dialogue files
out["perltqa_cache_keys_sample"] = [str(k)[:60] for k in list(pq_arch.keys())[:5]]
av = pq_arch[list(pq_arch.keys())[0]]
out["perltqa_arch_val_type"] = str(type(av))[:120]
if isinstance(av, dict):
    out["perltqa_arch_val_keys"] = list(av.keys())[:20]

json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1))
