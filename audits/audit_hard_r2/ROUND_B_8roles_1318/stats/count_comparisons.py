"""Round-2 stats audit: project-wide comparison counting (task B).

READ-ONLY on sources; writes only to this stats dir.
Counts: (1) distinct (benchmark, arm) combos in inventory ledger.csv (lower bound on
evaluated combos); (2) SIG-labelled contrasts in the four key docs; (3) corrected
alpha for family-wise control over the plausible family sizes.
"""
import csv, json, re
from collections import Counter

PKG = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/stats/comparison_count.json"
out = {}

rows = list(csv.DictReader(open(PKG + "/inventory/results/ledger.csv", encoding="utf-8")))
out["ledger_rows"] = len(rows)
combos = {(r["benchmark"], r["arm/method"]) for r in rows}
out["distinct_benchmark_x_arm"] = len(combos)
out["by_benchmark"] = dict(Counter(b for b, _ in combos))
metrics = {(r["benchmark"], r["arm/method"], r["metric"]) for r in rows}
out["distinct_benchmark_x_arm_x_metric"] = len(metrics)

# per-query-backed result files = separate evaluated configurations beyond ledger?
import glob
pq = glob.glob(PKG + "/**/per_query*.jsonl*", recursive=True) + glob.glob(
    PKG + "/**/*per_query*.csv", recursive=True)
out["per_query_files_in_package"] = sorted(pq)

# SIG claims in the four key docs
docs = ["FINAL_STATE.md", "REPORT.md", "DECISION_TESTS.md", "LADDER_REALTALK.md"]
sig_hits = []
for d in docs:
    txt = open(PKG + "/" + d, encoding="utf-8").read()
    for mm in re.finditer(r"SIG", txt):
        s = max(0, mm.start() - 160)
        sig_hits.append({"doc": d, "context": " ".join(txt[s:mm.start() + 3].split())[-170:]})
out["SIG_mentions"] = sig_hits
out["n_SIG_mentions"] = len(sig_hits)

for fam in (15, 30, 50, 100, 200, 817):
    out.setdefault("corrected_alpha", {})[str(fam)] = {
        "bonferroni": 0.05 / fam, "sidak": 1 - 0.95 ** (1 / fam)}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "SIG_mentions"}, indent=1))
print("SIG contexts:")
for h in sig_hits:
    print(" -", h["doc"], "::", h["context"][-150:])
