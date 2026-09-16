"""Diagnostic: where does PPLX-0.6B CPU time go? mask build vs attention impl."""
import os, pathlib, sys, time
import numpy as np
SEM = pathlib.Path('/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/semantic')
os.environ.setdefault("HF_MODULES_CACHE", str(SEM / ".hf_modules"))
sys.path.insert(0, str(SEM))
import torch
torch.set_num_threads(16); torch.set_num_interop_threads(1)
from transformers import AutoModel, AutoTokenizer
MD = '/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/model'
tok = AutoTokenizer.from_pretrained(MD, local_files_only=True, trust_remote_code=True)
texts = ["Fahim Khan: Hey good afternoon, how are you doing today my friend?"] * 64
b = tok(texts, padding=True, truncation=True, max_length=1024, return_tensors="pt")
print("shape", tuple(b["input_ids"].shape), "threads", torch.get_num_threads(), flush=True)
for impl in ("sdpa", "eager"):
    try:
        m = AutoModel.from_pretrained(MD, local_files_only=True, trust_remote_code=True,
                                      dtype=torch.float32, attn_implementation=impl)
        m.eval()
        with torch.inference_mode():
            m(input_ids=b["input_ids"][:8], attention_mask=b["attention_mask"][:8])
            t = time.time()
            m(input_ids=b["input_ids"], attention_mask=b["attention_mask"])
            dt = time.time() - t
        ntok = int(b["attention_mask"].numel())
        print(f"impl={impl} config={m.config._attn_implementation} s={dt:.2f} "
              f"tok/s={ntok/dt:.1f} texts/s={len(texts)/dt:.2f}", flush=True)
        del m
    except Exception as e:
        print(f"impl={impl} FAILED {type(e).__name__}: {e}", flush=True)
