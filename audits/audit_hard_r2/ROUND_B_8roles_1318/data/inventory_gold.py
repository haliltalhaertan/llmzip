#!/usr/bin/env python3
"""DATA audit A+B: full inventory + gold sanity for RealTalk/PerLTQA/LME/LoCoMo.
READ-ONLY on sources; writes only to OUT."""
import json, os, re, glob, pickle
from collections import Counter

OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/data"
W = "/mnt/c/Users/MDP/dev/llmzip-work"
R = {}

def note(k, v):
    R[k] = v
    print(f"{k}: {v}", flush=True)

# ================= RealTalk =================
RT = f"{W}/top10_comparison_r1/data"
per = {}
tot_docs = 0
tot_q = 0
gold_sizes = Counter()
oor = 0
empty_docs = 0
ws1_docs = 0
dup_extra = 0
dup_detail = {}
for i in range(1, 11):
    aid = f"RT{i:02d}"
    d = json.load(open(f"{RT}/{aid}.json", encoding="utf-8"))
    docs, qs = d["docs"], d["queries"]
    per[aid] = {"n_docs": len(docs), "n_q": len(qs)}
    tot_docs += len(docs)
    tot_q += len(qs)
    N = len(docs)
    seen = Counter(t["text"] for t in docs)
    extra = sum(c - 1 for c in seen.values() if c > 1)
    dup_extra += extra
    dup_detail[aid] = {"n_dup_groups": sum(1 for c in seen.values() if c > 1), "extra_copies": extra}
    for t in docs:
        if len(t["text"].strip()) == 0:
            empty_docs += 1
        if len(t["text"].split()) <= 1:
            ws1_docs += 1
    for q in qs:
        gold_sizes[len(q["gold"])] += 1
        for g in q["gold"]:
            if not (0 <= int(g) < N):
                oor += 1
note("RT_per_archive", per)
note("RT_total_docs", tot_docs)
note("RT_valid_q", tot_q)
note("RT_gold_size_hist", dict(sorted(gold_sizes.items())))
note("RT_gold_oor", oor)
note("RT_empty_docs", empty_docs)
note("RT_le1tok_docs", ws1_docs)
note("RT_dup_extra_copies", dup_extra)
note("RT_dup_detail", dup_detail)
excl = json.load(open(f"{RT}/exclusions.json", encoding="utf-8"))
eq = excl["excluded_qids"] if isinstance(excl, dict) and "excluded_qids" in excl else excl
note("RT_excluded_n", len(eq))
# unresolved-evidence check: independent recompute from raw chats
EV_RE = re.compile(r"D\d+:\d+")
def norm_old(x):
    if x is None:
        return []
    if isinstance(x, str):
        vals = EV_RE.findall(x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = EV_RE.findall(z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []
cache_files = sorted(glob.glob(f"{W}/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"))
partial = 0
partial_ex = []
unres_tokens_total = 0
for i, cf in enumerate(cache_files):
    aid = f"RT{i+1:02d}"
    cache = pickle.load(open(cf, "rb"))
    raw = json.load(open(os.path.join(f"{W}/bench3/REALTALK/data", cache["file"]), encoding="utf-8"))
    idmap = cache["id_to_row"]
    for qi, qid in enumerate(cache["qids"]):
        toks = norm_old(raw["qa"][qi].get("evidence"))
        unres = [t for t in toks if t not in idmap]
        if unres:
            gold = [int(g) for g in cache["gold_rows"][qi]]
            if gold:
                partial += 1
                unres_tokens_total += len(unres)
                if len(partial_ex) < 8:
                    partial_ex.append({"qid": qid, "aid": aid, "unresolved": unres,
                                       "n_tokens": len(toks), "gold": gold})
note("RT_partial_valid_with_unresolved", partial)
note("RT_unresolved_tokens_total", unres_tokens_total)
note("RT_partial_examples", partial_ex)
# lexical audit cross-check
lex = json.load(open(f"{W}/top10_comparison_r1/audit/lexical_audit.json", encoding="utf-8"))
note("RT_lexical_audit_partial", lex.get("n_partial_valid_with_unresolved"))

# ================= PerLTQA =================
arch = pickle.load(open(f"{W}/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
qd = pickle.load(open(f"{W}/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
archN = {c: arch[c]["N"] for c in sorted(arch)}
note("PQ_n_arch", len(archN))
note("PQ_N_minmax_total", (min(archN.values()), max(archN.values()), sum(archN.values())))
gs = Counter(len(qd[q]["gold"]) for q in qd)
note("PQ_n_q", len(qd))
note("PQ_gold_hist", dict(sorted(gs.items())))
oor2 = 0
for q, r in qd.items():
    N = arch[r["char"]]["N"]
    for g in list(r["gold"]):
        if not (0 <= int(g) < N):
            oor2 += 1
note("PQ_gold_oor", oor2)
note("PQ_empty_gold", sum(1 for q in qd if len(qd[q]["gold"]) == 0))
note("PQ_dup_gold_entries", sum(1 for q in qd if len(set(map(int, qd[q]["gold"]))) != len(qd[q]["gold"])))
# multi-gold share (gold_size>1)
note("PQ_multigold_q", sum(1 for q in qd if len(qd[q]["gold"]) > 1))
# raw resolution counts
res = json.load(open(f"{W}/bench3/runs/b3b_perltqa/resolution.json", encoding="utf-8"))
note("PQ_resolution_counts", res.get("counts"))
exc = json.load(open(f"{W}/bench3/runs/b3b_perltqa/exclusions.json", encoding="utf-8"))
note("PQ_excluded_archive", list(exc.get("excluded_archives", {}).keys()))
note("PQ_n_qa_dropped", exc.get("n_qa_dropped_total"))

# ================= LME =================
lme_files = sorted(glob.glob(f"{W}/regen/lme/cache_repr/*.pkl"))
note("LME_n_arch", len(lme_files))
lme_gs = Counter()
lme_oor = 0
lme_N = {}
lme_empty = 0
for f in lme_files:
    c = pickle.load(open(f, "rb"))
    N = c["C"].shape[0]
    qid = c["question_id"]
    lme_N[qid] = N
    g = [int(x) for x in c["gold"].ravel().tolist()]
    lme_gs[len(g)] += 1
    if len(g) == 0:
        lme_empty += 1
    for x in g:
        if not (0 <= x < N):
            lme_oor += 1
import statistics
note("LME_N_minmax_total", (min(lme_N.values()), max(lme_N.values()), sum(lme_N.values())))
note("LME_N_median", sorted(lme_N.values())[len(lme_N)//2])
note("LME_gold_hist", dict(sorted(lme_gs.items())))
note("LME_gold_oor", lme_oor)
note("LME_empty_gold", lme_empty)
# LME items: doc texts for dup/empty check on a SAMPLE of archives (state sample-only, 20 archives)
sample = lme_files[:20]
dup_e = 0
emp = 0
for f in sample:
    qid = pickle.load(open(f, "rb"))["question_id"]
    it = json.load(open(f"{W}/regen/lme/items/{qid}.json", encoding="utf-8"))
    texts = it["texts"] if isinstance(it, dict) and "texts" in it else (it if isinstance(it, list) else list(it.values())[0] if isinstance(it, dict) else [])
    if isinstance(texts, dict):
        texts = list(texts.values())
    seen = Counter(str(t) for t in texts)
    dup_e += sum(c - 1 for c in seen.values() if c > 1)
    emp += sum(1 for t in texts if len(str(t).strip()) == 0)
note("LME_sample20_dup_extra", dup_e)
note("LME_sample20_empty", emp)
note("LME_dup_scope", "SAMPLE 20/470 archives only")

# ================= LoCoMo =================
loc_files = sorted(glob.glob(f"{W}/regen/locomo/locomo_*.pkl"))
note("LOC_n_arch", len(loc_files))
loc_q = 0
loc_N = {}
loc_unres = 0
loc_empty = 0
for f in loc_files:
    c = pickle.load(open(f, "rb"))
    N = c["C"].shape[0]
    loc_N[c["conv_id"]] = N
    idm = c["id_to_row"]
    for qa in c["qas"]:
        loc_q += 1
        ev = qa.get("raw_evidence", [])
        if isinstance(ev, str):
            try:
                ev = json.loads(ev.replace("'", '"'))
            except Exception:
                ev = [ev]
        unres = [e for e in [str(x) for x in (ev if isinstance(ev, list) else [ev])] if e not in idm]
        if unres:
            loc_unres += 1
        if not ev:
            loc_empty += 1
note("LOC_N_per_arch", loc_N)
note("LOC_N_total", sum(loc_N.values()))
note("LOC_n_q_regen", loc_q)
note("LOC_q_with_unresolved_evidence", loc_unres)
note("LOC_q_empty_evidence", loc_empty)
ad = json.load(open(f"{W}/incoming_20260916b/extracted/LLMZIP_HIZ_GENELLEME_2026-09-16/LLMZIP_HIZ_GENELLEME_2026-09-16/results/locomo_adapter_before_scores.json"))
note("LOC_HIZ_total", ad.get("total_questions"))
note("LOC_HIZ_kept", ad.get("kept_questions"))
note("LOC_HIZ_excluded", ad.get("excluded"))
lj = json.load(open(f"{W}/parallel_ideas_r1/hit10/LOCOMO.json"))
note("LOC_LOCOMOjson_n", lj.get("n_queries"))
note("LOC_LOCOMOjson_skipped", lj.get("queries_skipped_no_retrievable_gold"))

json.dump(R, open(os.path.join(OUT, "audit_inventory_gold.json"), "w"), indent=1, default=str)
print("WROTE audit_inventory_gold.json", flush=True)
