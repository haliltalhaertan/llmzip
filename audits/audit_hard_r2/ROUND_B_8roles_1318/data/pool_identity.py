#!/usr/bin/env python3
"""DATA audit D: pool identity across arms. READ-ONLY on sources; writes only to OUT."""
import json, os, glob
from collections import Counter

OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/data"
W = "/mnt/c/Users/MDP/dev/llmzip-work"
R = {}

def note(k, v):
    R[k] = v
    print(f"{k}: {v}", flush=True)

# ---- RealTalk: compare (archive,qid)->(N,gold) across data per_query, audit corrected, pq, baseline ckpts, ladder cache
def load_jsonl(path, key):
    d = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            d[key(r)] = r
    return d

RT = f"{W}/top10_comparison_r1/data"
AU = f"{W}/top10_comparison_r1/audit"
PQ = f"{W}/top10_comparison_r1/pq"
BL = f"{W}/top10_comparison_r1/baseline"

# data per_query.jsonl has arm column (bm25/tfidf)
dp = load_jsonl(f"{RT}/per_query.jsonl", lambda r: (r["archive_id"], r["qid"], r["arm"]))
note("data_per_query_rows", len(dp))
# check gold identity across bm25/tfidf arms within data/
mism_gold_arms = 0
qids = set((a, q) for (a, q, arm) in dp)
for (a, q) in qids:
    g1 = dp[(a, q, "bm25")]["gold"]
    g2 = dp[(a, q, "tfidf")]["gold"]
    if [int(x) for x in g1] != [int(x) for x in g2]:
        mism_gold_arms += 1
    if dp[(a, q, "bm25")]["N"] != dp[(a, q, "tfidf")]["N"]:
        mism_gold_arms += 1
note("data_bm25_vs_tfidf_gold_or_N_mismatch", mism_gold_arms)

# audit corrected files
for name in ("per_query_bm25_corrected.jsonl", "per_query_tfidf_corrected.jsonl", "per_query_corrected.jsonl"):
    p = os.path.join(AU, name)
    if os.path.exists(p):
        d = load_jsonl(p, lambda r: (r.get("archive_id"), r.get("qid"), r.get("arm", "?")))
        note(f"audit_{name}_rows", len(d))

# pq per_query.jsonl (PQ codes): key format differs
pqp = load_jsonl(f"{PQ}/per_query.jsonl", lambda r: (r["archive_id"], r["qid"]))
note("pq_rows", len(pqp))
# compare pq gold vs data gold
pq_gold_mism = 0
pq_N_mism = 0
n_comp = 0
for (a, q) in qids:
    if (a, q) not in pqp:
        continue
    n_comp += 1
    g_data = [int(x) for x in dp[(a, q, "bm25")]["gold"]]
    g_pq = [int(x) for x in pqp[(a, q)]["gold_rows"]]
    if g_data != g_pq:
        pq_gold_mism += 1
    if dp[(a, q, "bm25")]["N"] != pqp[(a, q)]["n_docs"]:
        pq_N_mism += 1
note("pq_vs_data_compared", n_comp)
note("pq_vs_data_gold_mismatch", pq_gold_mism)
note("pq_vs_data_N_mismatch", pq_N_mism)

# baseline per_query_top10.jsonl: RealTalk subset
bl_rows = load_jsonl(f"{BL}/per_query_top10.jsonl", lambda r: (r["benchmark"], r["archive_id"], r["qid"]))
rt_bl = {k: v for k, v in bl_rows.items() if k[0] in ("REALTALK", "realtalk", "RealTalk")}
note("baseline_total_rows", len(bl_rows))
note("baseline_realtalk_rows", len(rt_bl))
bl_gold_mism = 0
bl_N_mism = 0
for (a, q) in qids:
    hit = [k for k in rt_bl if k[1] == a and k[2] == q]
    if not hit:
        continue
    r = rt_bl[hit[0]]
    if [int(x) for x in r["gold"]] != [int(x) for x in dp[(a, q, "bm25")]["gold"]]:
        bl_gold_mism += 1
    if r["N"] != dp[(a, q, "bm25")]["N"]:
        bl_N_mism += 1
note("baseline_vs_data_gold_mismatch", bl_gold_mism)
note("baseline_vs_data_N_mismatch", bl_N_mism)
# baseline: check gold identity across its own 4 arms (sign96/float_raw/float_std/asym are per-row sub-objects, single gold per row -> trivially same)
# instead check per_query_top10 gold vs ckpt files for one archive
ckpt = load_jsonl(f"{BL}/ckpt_top10_realtalk_00.jsonl", lambda r: (r["archive_id"], r["qid"]))
note("ckpt_rt00_rows", len(ckpt))

# ---- PerLTQA: ablation per_query vs baseline per_query_top10
abl = load_jsonl(f"{W}/top10_comparison_r1/ablation_r2/perltqa/per_query.jsonl",
                 lambda r: (r["archive_id"] if "archive_id" in r else r.get("char"), r["qid"], r["arm"], r["scorer"]))
note("perltqa_abl_rows", len(abl))
# distinct (qid) set in ablation FULL/sym
abl_q = set((a, q) for (a, q, arm, sc) in abl if arm == "FULL" and sc == "sym")
note("perltqa_abl_nq_full_sym", len(abl_q))
bl_plt = {k: v for k, v in bl_rows.items() if k[0] in ("PerLTQA", "perltqa", "PERLTQA")}
note("baseline_perltqa_rows", len(bl_plt))
bl_plt_q = set((k[1], k[2]) for k in bl_plt)
note("perltqa_qset_diff_abl_minus_bl", len(abl_q - bl_plt_q))
note("perltqa_qset_diff_bl_minus_abl", len(bl_plt_q - abl_q))
# gold agreement on intersection, FULL/sym vs baseline
gm = 0
nm = 0
nint = 0
for (a, q) in sorted(abl_q & bl_plt_q)[:9000]:
    ra = abl[(a, q, "FULL", "sym")]
    rb = bl_plt[("PerLTQA", a, q)] if ("PerLTQA", a, q) in bl_plt else None
    if rb is None:
        # find actual benchmark key
        cand = [k for k in bl_plt if k[1] == a and k[2] == q]
        if not cand:
            continue
        rb = bl_plt[cand[0]]
    nint += 1
    if [int(x) for x in ra["gold"]] != [int(x) for x in rb["gold"]]:
        gm += 1
    if ra.get("N", ra.get("n_docs")) != rb["N"]:
        nm += 1
note("perltqa_abl_vs_bl_compared", nint)
note("perltqa_abl_vs_bl_gold_mismatch", gm)
note("perltqa_abl_vs_bl_N_mismatch", nm)
# ablation internal: gold identity across 4 arms x 2 scorers for same qid
int_mism = 0
for (a, q) in list(abl_q)[:2000]:
    g0 = [int(x) for x in abl[(a, q, "FULL", "sym")]["gold"]]
    for arm in ("NO_LSA", "NO_CHAR", "WORD_ONLY"):
        for sc in ("sym", "qscale"):
            if (a, q, arm, sc) not in abl:
                continue
            if [int(x) for x in abl[(a, q, arm, sc)]["gold"]] != g0:
                int_mism += 1
note("perltqa_abl_internal_gold_mismatch_sample2000", int_mism)

# ---- LME: baseline vs ablation_r2/lme ARCHIVE_CACHE
bl_lme = {k: v for k, v in bl_rows.items() if k[0] in ("LME", "lme")}
note("baseline_lme_rows", len(bl_lme))
ac_path = f"{W}/top10_comparison_r1/ablation_r2/lme/ARCHIVE_CACHE.jsonl"
if os.path.exists(ac_path):
    ac = load_jsonl(ac_path, lambda r: (r.get("archive_id", r.get("qid", "?"))))
    note("lme_archive_cache_rows", len(ac))

json.dump(R, open(os.path.join(OUT, "audit_pool_identity.json"), "w"), indent=1)
print("WROTE audit_pool_identity.json", flush=True)
