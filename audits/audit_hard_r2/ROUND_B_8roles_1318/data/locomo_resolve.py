#!/usr/bin/env python3
"""Resolve LoCoMo 1531 vs 1535: which qids differ. READ-ONLY sources; writes OUT only."""
import json, glob, pickle

OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/data"
W = "/mnt/c/Users/MDP/dev/llmzip-work"
R = {}

def note(k, v):
    R[k] = v
    print(f"{k}: {v}", flush=True)

# regen cohort: all qas with resolved gold
regen_qids = set()
regen_per_arch = {}
unres_qids = []
empty_qids = []
for f in sorted(glob.glob(f"{W}/regen/locomo/locomo_*.pkl")):
    c = pickle.load(open(f, "rb"))
    idm = c["id_to_row"]
    kept = []
    for qa in c["qas"]:
        qid = qa["question_id"]
        ev = qa.get("raw_evidence", [])
        if isinstance(ev, str):
            try:
                ev = json.loads(ev.replace("'", '"'))
            except Exception:
                ev = [ev]
        ev = [str(x) for x in (ev if isinstance(ev, list) else [ev])]
        if not ev:
            empty_qids.append(qid)
            continue
        rows = [idm[e] for e in ev if e in idm]
        if not rows:
            unres_qids.append((qid, ev))
            continue
        kept.append(qid)
        regen_qids.add(qid)
    regen_per_arch[c["conv_id"]] = len(kept)
note("regen_kept_total", len(regen_qids))
note("regen_per_arch_kept", regen_per_arch)
note("regen_unres_qids", unres_qids)
note("regen_empty_qids", empty_qids)

# HIZ adapter: kept = total - excluded
ad = json.load(open(f"{W}/incoming_20260916b/extracted/LLMZIP_HIZ_GENELLEME_2026-09-16/LLMZIP_HIZ_GENELLEME_2026-09-16/results/locomo_adapter_before_scores.json"))
excl = ad["excluded"]
from collections import Counter
note("HIZ_excluded_by_reason", dict(Counter(e["reason"] for e in excl)))
hiz_excl_qids = set(e["qid"] for e in excl)
note("HIZ_excluded_n", len(hiz_excl_qids))
# HIZ qid namespace is L00..L09; regen namespace is locomo_I_qaJ. Build mapping via per-archive counts?
note("HIZ_counts_per_archive", dict(Counter(e["archive"] for e in excl)))
note("HIZ_kept_per_archive", ad["counts"] if isinstance(ad.get("counts"), dict) else str(ad.get("counts"))[:500])

# LOCOMO.json run: which qids? run_locomo.py builds from regen/locomo globs; 5 skipped
lj = json.load(open(f"{W}/parallel_ideas_r1/hit10/LOCOMO.json"))
note("LOCOMOjson_n", lj["n_queries"])
note("LOCOMOjson_skipped", lj["queries_skipped_no_retrievable_gold"])
# The 5 skipped should equal regen unresolved+empty that yield no gold: check run_locomo.py skip logic
src = open(f"{W}/parallel_ideas_r1/hit10/run_locomo.py", encoding="utf-8").read()
note("run_locomo_skip_logic", [l.strip() for l in src.splitlines() if "skip" in l.lower()][:10])

# HIZ quality_per_query.csv: actual evaluated qids
import csv, os
qp = f"{W}/incoming_20260916b/extracted/LLMZIP_HIZ_GENELLEME_2026-09-16/LLMZIP_HIZ_GENELLEME_2026-09-16/results/quality_per_query.csv"
hiz_qids = set()
if os.path.exists(qp):
    with open(qp, encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        note("HIZ_qpq_columns", rd.fieldnames)
        n = 0
        for r in rd:
            n += 1
            qk = r.get("qid", r.get("question_id", "?"))
            hiz_qids.add((r.get("archive", r.get("conv_id", "?")), qk))
    note("HIZ_qpq_rows", n)
    note("HIZ_qpq_distinct_q", len(hiz_qids))
    print("HIZ sample qids:", sorted(hiz_qids)[:5], flush=True)

# Overlap analysis in a namespace-agnostic way: compare per-archive kept counts
# regen kept per arch (locomo_I) vs HIZ kept per arch (L0I)
note("regen_vs_hiz_arch_counts", {"regen": regen_per_arch})
# Difference sets within regen namespace:
# LOCOMO.json cohort in regen namespace = regen kept minus its 5 skipped.
# HIZ cohort in regen namespace: need mapping L0I_qNNNN -> locomo_I_qaJ. Try locomo_provenance + HIZ sources?
prov = f"{W}/incoming_20260916b/extracted/LLMZIP_HIZ_GENELLEME_2026-09-16/LLMZIP_HIZ_GENELLEME_2026-09-16/sources/locomo_provenance.json"
if os.path.exists(prov):
    p = json.load(open(prov))
    note("provenance_keys", list(p.keys())[:10])
    note("provenance_head", json.dumps(p, default=str)[:800])

json.dump(R, open(f"{OUT}/audit_locomo_resolve.json", "w"), indent=1, default=str)
print("WROTE audit_locomo_resolve.json", flush=True)
