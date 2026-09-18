"""T2/T3 cleanroom blockers: real command outputs, no ambient reads.
Proves each failing open() from inside the cleanroom with a stranger-equivalent
relative path, and records that the absolute ambient path exists (so this is a
packaging gap, not a missing-data claim).
"""
import csv
import importlib.util
import json
import os
import sys
import traceback

OWN = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/09_portability"
CR = os.path.join(OWN, "cleanroom")
PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
out = {"t2": {}, "t3": {}, "deps": {}}

# ---- T2: no relative equivalent in package ----
pkg_csvs = []
for root, _, files in os.walk(PUB):
    for f in files:
        if f.endswith(".csv"):
            pkg_csvs.append(os.path.relpath(os.path.join(root, f), PUB))
out["t2"]["package_csvs"] = pkg_csvs
out["t2"]["has_text_rerank_relative"] = any("text_rerank" in p for p in pkg_csvs)

# Stranger-equivalent relative open inside cleanroom -> must fail
rel_csv = os.path.join(CR, "incoming_20260916b", "text_rerank_per_query.csv")
try:
    open(rel_csv, encoding="utf-8").close()
    out["t2"]["relative_open"] = "UNEXPECTEDLY_SUCCEEDED"
except FileNotFoundError as e:
    out["t2"]["relative_open"] = f"FileNotFoundError: {e}"

# As-shipped absolute path (ambient, exists on this machine only)
spec = importlib.util.spec_from_file_location(
    "dt_clean2",
    os.path.join(CR, "coordinator", "decision_tests_clean.py"))
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)
out["t2"]["as_shipped_RERANK_CSV"] = dc.RERANK_CSV
out["t2"]["as_shipped_exists_here"] = os.path.exists(dc.RERANK_CSV)
# Stranger view: remap to cleanroom-relative -> real t2() failure, captured
dc.RERANK_CSV = rel_csv
try:
    dc.t2()
    out["t2"]["cleanroom_t2"] = "UNEXPECTEDLY_SUCCEEDED"
except FileNotFoundError as e:
    out["t2"]["cleanroom_t2"] = f"FileNotFoundError: {e}"
    out["t2"]["cleanroom_t2_trace_tail"] = traceback.format_exc(limit=3)

# Ambient ground truth (read-only stat, NOT imported): size + row count of header only
amb = "/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/LLMZIP_FIKIR1_2026-09-16/results/text_rerank_per_query.csv"
st = os.stat(amb)
with open(amb, encoding="utf-8") as fh:
    header = fh.readline().strip().split(",")
    n_rows = sum(1 for _ in fh)
out["t2"]["ambient_csv_bytes"] = st.st_size
out["t2"]["ambient_csv_rows"] = n_rows
out["t2"]["ambient_csv_header"] = header

# ---- T3: no relative equivalents in package ----
needles = ["perltqa_en_v2.json", "perltmem_en_v2.json", "cache_arch_eval.pkl", "cache_q_eval.pkl"]
found = {}
for n in needles:
    hits = []
    for root, _, files in os.walk(PUB):
        if n in files:
            hits.append(os.path.relpath(os.path.join(root, n), PUB))
    found[n] = hits
out["t3"]["package_hits"] = found
for rel, abs_p in [
    ("t3_base/perltqa_en_v2.json", "BASE"),
    ("t3_base/perltmem_en_v2.json", "BASE"),
    ("t3_base/cache_arch_eval.pkl", "ARCH_PKL"),
    ("t3_base/cache_q_eval.pkl", "Q_PKL"),
]:
    p = os.path.join(CR, rel)
    try:
        open(p, "rb").close()
        out["t3"][rel] = "UNEXPECTEDLY_SUCCEEDED"
    except FileNotFoundError as e:
        out["t3"][rel] = f"FileNotFoundError: {e}"

# Static proof: as-shipped T3 scripts hardcode absolute machine paths
import re
for name, path in [
    ("t3_ladder_pkg.py", os.path.join(CR, "ablation_r2", "perltqa", "t3_ladder_pkg.py")),
    ("t3_perltqa_kltn_pkg.py", os.path.join(CR, "coordinator", "t3_perltqa_kltn_pkg.py")),
    ("ladder_pkg.py", os.path.join(CR, "coordinator", "ladder_pkg.py")),
]:
    txt = open(path, encoding="utf-8").read()
    abs_lines = [ln.strip() for ln in txt.splitlines() if "/mnt/c/Users/MDP/dev/llmzip-work" in ln]
    out["t3"][f"{name}_absolute_lines"] = abs_lines

# Ambient ground truth sizes (stat only)
for label, p in [
    ("perltqa_en_v2.json", "/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2/perltqa_en_v2.json"),
    ("perltmem_en_v2.json", "/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2/perltmem_en_v2.json"),
    ("cache_arch_eval.pkl", "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"),
    ("cache_q_eval.pkl", "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"),
    ("rt_repr_dir", "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"),
]:
    try:
        st = os.stat(p)
        out["t3"][f"ambient_{label}"] = {"exists": True, "bytes": st.st_size}
    except FileNotFoundError:
        out["t3"][f"ambient_{label}"] = {"exists": False}

# ---- dep check for the cleanroom T1 path (what a stranger needs installed) ----
for pkg in ("numpy", "scipy", "sklearn"):
    try:
        m = importlib.import_module(pkg)
        out["deps"][pkg] = getattr(m, "__version__", "present")
    except ImportError as e:
        out["deps"][pkg] = f"MISSING: {e}"
try:
    importlib.import_module("sentence_transformers")
    out["deps"]["sentence_transformers"] = "present (NOT needed for T1 cleanroom)"
except ImportError:
    out["deps"]["sentence_transformers"] = "absent (NOT needed for T1 cleanroom)"

json.dump(out, open(os.path.join(OWN, "outputs", "T2_T3_blockers.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:4000])
print("WROTE outputs/T2_T3_blockers.json")
