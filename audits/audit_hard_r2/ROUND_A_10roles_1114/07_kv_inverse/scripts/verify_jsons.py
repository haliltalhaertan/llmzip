"""Mechanical verification of KV repair carried-over proof + row accounting.

Reads ONLY (research root). Writes JSON to this audit dir.
Checks:
  K1 rows/coverage: kv/per_case.jsonl == 320, kv_repair == 320, identity keys unique.
  K2 align markers: original rows lack shifted-v2; repair rows all shifted-v2.
  K3 KL/top1 carryover: max|KL_old-KL_new|==0.0, top1 mismatches==0 (identity-keyed).
  K4 dNLL withdrawal scope: count changed values, max abs shift.
  K5 inverse rows: per_case.jsonl == 20; npz count == 12; continuation labels.
  K6 byte math: predictor 1497600, crossover 65, ledger 4736 vs FP32KV 24576.
  K7 on-disk sizes: predictor.pt, q4 payload.
  K8 model config GQA: num_key_value_heads * head_dim == 192, layers == 30.
"""
import json, os, collections

R = "/mnt/c/Users/MDP/dev/llmzip-work"
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/07_kv_inverse/outputs"
res = {"label": "[LOCAL EXPLORATORY PILOT] audit 07_kv_inverse mechanical check"}

def loadjl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]

kv_old = loadjl(os.path.join(R, "parallel_ideas_r1/kv/per_case.jsonl"))
kv_new = loadjl(os.path.join(R, "parallel_ideas_r1/kv_repair/per_case.jsonl"))
res["K1_kv_old_rows"] = len(kv_old)
res["K1_kv_new_rows"] = len(kv_new)
ko = collections.Counter((r["text_id"], r["ctx"], r["arm"], r["step"]) for r in kv_old)
kn = collections.Counter((r["text_id"], r["ctx"], r["arm"], r["step"]) for r in kv_new)
res["K1_old_unique_keys"] = len(ko)
res["K1_new_unique_keys"] = len(kn)
res["K1_old_dupes"] = sum(1 for c in ko.values() if c > 1)
res["K1_new_dupes"] = sum(1 for c in kn.values() if c > 1)
res["K2_old_align_values"] = sorted(set(r.get("align", "<ABSENT>") for r in kv_old))
res["K2_new_align_values"] = sorted(set(r.get("align", "<ABSENT>") for r in kv_new))

# K3/K4 identity-keyed join on non-full arms
old = {(r["text_id"], r["ctx"], r["arm"], r["step"]): r for r in kv_old if r["arm"] != "full"}
new = {(r["text_id"], r["ctx"], r["arm"], r["step"]): r for r in kv_new if r["arm"] != "full"}
common = sorted(set(old) & set(new))
res["K3_common_nonfull_keys"] = len(common)
kld = [abs(old[k]["kl_full_arm"] - new[k]["kl_full_arm"]) for k in common]
res["K3_max_abs_KL_diff"] = max(kld)
res["K3_n_KL_exact_zero"] = sum(1 for d in kld if d == 0.0)
ag_mis = sum(1 for k in common if old[k]["top1_agree"] != new[k]["top1_agree"])
res["K3_top1_mismatches"] = ag_mis
dd = [abs(old[k]["dnll"] - new[k]["dnll"]) for k in common]
res["K4_dnll_changed"] = sum(1 for k in common if old[k]["dnll"] != new[k]["dnll"])
res["K4_dnll_max_abs_shift"] = max(dd)
# repaired sign check: per (ctx,arm) mean dnll >= ~0?
by = collections.defaultdict(list)
for k in common:
    by[(new[k]["ctx"], new[k]["arm"])].append(new[k]["dnll"])
res["K4_repaired_mean_dnll"] = {f"{c}:{a}": sum(v)/len(v) for (c, a), v in sorted(by.items())}
# old sign check
byo = collections.defaultdict(list)
for k in common:
    byo[(old[k]["ctx"], old[k]["arm"])].append(old[k]["dnll"])
res["K4_original_mean_dnll"] = {f"{c}:{a}": sum(v)/len(v) for (c, a), v in sorted(byo.items())}

inv = loadjl(os.path.join(R, "parallel_ideas_r1/inverse/per_case.jsonl"))
res["K5_inverse_rows"] = len(inv)
res["K5_inverse_case_ids"] = sorted(set(r.get("case_id", "?") for r in inv))
import glob
res["K5_inverse_npz_count"] = len(glob.glob(os.path.join(R, "parallel_ideas_r1/inverse/L*.npz")))
res["K5_inverse_repair_npz_count"] = len(glob.glob(os.path.join(R, "parallel_ideas_r1/inverse_repair/L*.npz")))
inv_rep = loadjl(os.path.join(R, "parallel_ideas_r1/inverse_repair/per_case.jsonl"))
res["K5_inverse_repair_rows"] = len(inv_rep)
with open(os.path.join(R, "parallel_ideas_r1/inverse/continuation.json")) as f:
    cj = json.load(f)
res["K5_orig_continuation_ncases"] = len(cj)
res["K5_orig_continuation_armkeys"] = sorted(cj[0].keys())
with open(os.path.join(R, "parallel_ideas_r1/inverse_repair/kv_continuation.json")) as f:
    kj = json.load(f)
res["K5_kvcont_method"] = kj.get("method")
res["K5_kvcont_ncases"] = len(kj.get("cases", []))
res["K5_kvcont_parity"] = [c.get("cache_parity_trueKV_vs_full") for c in kj.get("cases", [])]

# K6 byte math (pure arithmetic from frozen protocol constants)
pred = 90 * (64*64 + 64) * 4
res["K6_predictor_bytes_formula"] = pred
res["K6_predictor_bytes_expected"] = 1497600
full_tok = 30*2*192*4
ret_tok = 15*2*192*4
res["K6_full_B_per_tok"] = full_tok
res["K6_retained_B_per_tok"] = ret_tok
res["K6_crossover_tokens"] = pred / ret_tok
res["K6_ledger_B_per_layer_T16"] = 16*576//2 + 16*4 + 16*4  # packed nibbles + scales + mins
res["K6_fp32KV_B_per_layer_T16"] = 2*192*16*4

# K7 on-disk
for p in ["parallel_ideas_r1/kv/predictor.pt",
          "parallel_ideas_r1/kv/q4_payload_8_16.pt",
          "parallel_ideas_r1/kv_repair/predictor.pt"]:
    fp = os.path.join(R, p)
    res["K7_size_" + p.replace("/", "__")] = os.path.getsize(fp) if os.path.exists(fp) else None

# K8 model config
with open(os.path.join(R, "parallel_ideas_r1/model/config.json")) as f:
    cfg = json.load(f)
res["K8_num_hidden_layers"] = cfg.get("num_hidden_layers")
res["K8_num_kv_heads"] = cfg.get("num_key_value_heads")
res["K8_num_attn_heads"] = cfg.get("num_attention_heads")
res["K8_hidden_size"] = cfg.get("hidden_size")
res["K8_head_dim"] = cfg.get("hidden_size") // cfg.get("num_attention_heads")
res["K8_gqa_width"] = cfg.get("num_key_value_heads") * (cfg.get("hidden_size") // cfg.get("num_attention_heads"))
res["K8_native_dtype"] = cfg.get("torch_dtype")

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "verify_jsons.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
