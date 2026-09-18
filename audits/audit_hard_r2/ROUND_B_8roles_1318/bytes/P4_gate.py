"""P4: gate semantics + byte-claim arithmetic. Pure python3, READ-ONLY. Writes P4_gate.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
W = "/mnt/c/Users/MDP/dev/llmzip-work"
PKG = f"{W}/_wt_top10/research_top10_comparison_2026_09_16"

lad = json.load(open(f"{PKG}/coordinator/LADDER.json"))
t3 = json.load(open(f"{PKG}/coordinator/T3_PERLTQA_KLTN.json"))
# gate arithmetic
gate_bits = lad["gate"]["n_bits"]; gate_diff = lad["gate"]["differing_bits"]
# RealTalk totals from data (probe already verified 8944 docs)
n_docs = 8944
out = {
  "ladder_gate_bits": gate_bits, "ladder_gate_diff": gate_diff,
  "equals_8944x96": gate_bits == 8944*96,
  "8944x96": 8944*96,
  "t3_gate": t3.get("gate", {}),
  "ladder_bytes_per_doc_claims": {k: v["bytes_per_doc"] for k, v in lad["arms"].items()},
  # corrected narrow totals (packed + sigma f64 only, the report's own boundary)
  "narrow_packed": {96: n_docs*12, 192: n_docs*24, 384: n_docs*48},
  "narrow_sigma_f64": {96: 10*96*8, 192: 10*192*8, 384: 10*384*8},
}
for k in (96, 192, 384):
    p = out["narrow_packed"][k]; s = out["narrow_sigma_f64"][k]
    out[f"narrow_total_k{k}"] = p + s
    out[f"narrow_perdoc_k{k}"] = (p + s)/n_docs
# with mu added (mu same shape as sigma, required for QC centering)
for k in (96, 192, 384):
    p = out["narrow_packed"][k]; s = out["narrow_sigma_f64"][k]
    out[f"with_mu_total_k{k}"] = p + 2*s
    out[f"with_mu_perdoc_k{k}"] = (p + 2*s)/n_docs
# precision variants
out["R_bytes"] = {"k96_f32": 96*96*4, "k96_f64": 96*96*8,
                  "k192_f32": 192*192*4, "k384_f32": 384*384*4}
out["float_bytes_per_doc_claim"] = {"k96": 384, "k192": 768, "k384": 1536}
json.dump(out, open(os.path.join(HERE, "P4_gate.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
print("WROTE P4_gate.json")
# code-evidence notes (manual, from reads):
print("---")
print("ladder.py:147 B=sign(C);149 sym=QB@B.T;150-152 sigma=C.std+floor;152 qscale=(QC/sigma)@B.T;153 float=cosine")
print("ladder.py:194-200 gate compares ONLY C96 signs vs cache (no QC, no sigma, no k192/384)")
print("ladder.py:243 bytes_per_doc=k/8 (sign) or 4k (float); sigma/mu/encoder not in field")
