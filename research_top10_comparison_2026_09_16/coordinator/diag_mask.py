"""Isolate: mask construction vs transformer layers."""
import os, pathlib, sys, time
SEM = pathlib.Path('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/semantic')
os.environ.setdefault("HF_MODULES_CACHE", str(SEM / ".hf_modules"))
sys.path.insert(0, str(SEM))
import torch
torch.set_num_threads(16); torch.set_num_interop_threads(1)
from transformers import AutoModel, AutoTokenizer
from transformers.masking_utils import create_causal_mask
MD = '/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/model'
tok = AutoTokenizer.from_pretrained(MD, local_files_only=True, trust_remote_code=True)
m = AutoModel.from_pretrained(MD, local_files_only=True, trust_remote_code=True, dtype=torch.float32)
m.eval()
import importlib
mod = importlib.import_module(type(m).__module__)
b = tok(["Fahim Khan: Hey good afternoon, how are you doing today?"] * 64,
        padding=True, truncation=True, max_length=1024, return_tensors="pt")
ids, am = b["input_ids"], b["attention_mask"]
with torch.inference_mode():
    emb = m.embed_tokens(ids)
    for label, fn in (("mask_build", None),):
        pass
    t = time.time()
    mask = create_causal_mask(config=m.config, inputs_embeds=emb, attention_mask=am,
                              past_key_values=None, position_ids=None,
                              or_mask_function=mod.bidirectional_mask_function(am))
    t_mask = time.time() - t
    print(f"mask_build_s={t_mask:.2f} shape={tuple(mask.shape) if mask is not None else None}", flush=True)
    t = time.time()
    from transformers import Qwen3Model
    out = Qwen3Model.forward(m, input_ids=None, attention_mask={"full_attention": mask},
                             position_ids=None, past_key_values=None, inputs_embeds=emb,
                             use_cache=False, cache_position=None)
    t_layers = time.time() - t
    ntok = int(am.numel())
    print(f"layers_s={t_layers:.2f} tok/s={ntok/t_layers:.1f} texts/s={64/t_layers:.2f}", flush=True)
    t = time.time()
    m(input_ids=ids, attention_mask=am)
    print(f"full_forward_s={time.time()-t:.2f}", flush=True)
