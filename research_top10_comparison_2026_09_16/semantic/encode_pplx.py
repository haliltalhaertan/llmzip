"""PPLX-0.6B local CPU encoder (REAL TALK, all 10 archives, 705 queries).

Official semantics: masked mean pool (attention_mask) of last hidden states,
then INT8=clip(round(127*tanh(pooled))) and native BIN=sign(pooled>=0) on the
UNQUANTIZED pooled values. PACK=packbits(pooled>=0).

Remote-code review (../model/modeling.py, configuration.py, BEFORE enabling
trust_remote_code): modeling.py subclasses Qwen3Model, sets is_causal=False on
all layers, builds a bidirectional mask via create_causal_mask with an
or_mask_function reading attention_mask; imports only torch/transformers.
No network, subprocess, file writes, or env access. configuration.py is a
trivial Qwen3Config subclass. No code installed; model run unmodified via
AutoModel(local dir, trust_remote_code=True, local_files_only=True).

CPU: torch.set_num_threads(6), interop 1, float32 weights, inference_mode.
Batching: untruncated tokenizer lengths, length-sorted buckets of 8,
max_length 1024, original rows preserved. Checkpoints per batch + per archive,
resume-safe via per-text SHA256, no re-encode. First-batch speed to
progress.json. No synthetic embeddings: hard failure aborts with blocker.
"""
import hashlib
import json
import os
import pathlib
import sys
import time

import numpy as np

# Remote-code dynamic modules must not use the read-only default HF cache.
os.environ.setdefault("HF_MODULES_CACHE",
                      str(pathlib.Path(__file__).resolve().parent / ".hf_modules"))

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "model"
DATA_DIR = ROOT / "data"
OUT = pathlib.Path(__file__).resolve().parent
CKPT = OUT / "checkpoints"
PAY = OUT / "payloads"
CKPT.mkdir(exist_ok=True)
PAY.mkdir(exist_ok=True)

MAXLEN = 1024
BATCH = 8

from pplx_scorer import (masked_mean_pool, official_binary, official_int8,
                         pack_sign, plan_batches, text_hash, load_checkpoint)


def fail_blocker(msg, **kw):
    doc = {"status": "BLOCKER", "error": msg, **kw}
    (OUT / "BLOCKER.json").write_text(json.dumps(doc, indent=2))
    print("BLOCKER: " + msg, flush=True)
    sys.exit(2)


def main():
    import resource
    import torch
    torch.set_num_threads(6)
    torch.set_num_interop_threads(1)
    from transformers import AutoModel, AutoTokenizer

    t0 = time.time()
    if not (MODEL_DIR / "model.safetensors").exists():
        fail_blocker("model.safetensors missing (download incomplete)",
                     model_dir=str(MODEL_DIR),
                     files=sorted(os.listdir(MODEL_DIR)))
    if not (DATA_DIR / "EXPORT_DONE.json").exists():
        fail_blocker("dataset EXPORT_DONE.json missing")

    archives = [f"RT{i:02d}" for i in range(1, 11)]
    texts_meta = {}
    for a in archives:
        d = json.loads((DATA_DIR / f"{a}.json").read_text())
        texts_meta[a] = d

    # Encoder weight bytes (read-only stat, never loaded into payload claim)
    wbytes = sum((MODEL_DIR / f).stat().st_size for f in os.listdir(MODEL_DIR)
                 if (MODEL_DIR / f).is_file())

    tok = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True,
                                        trust_remote_code=True)
    model = AutoModel.from_pretrained(str(MODEL_DIR), local_files_only=True,
                                      trust_remote_code=True,
                                      torch_dtype=torch.float32)
    model.eval()
    load_s = time.time() - t0

    # ---- tokenizer untruncated lengths (exact truncation accounting) ----
    tok_stats = {}
    for a in archives:
        d = texts_meta[a]
        for kind in ("docs", "queries"):
            key = kind
            enc = tok([x["text"] for x in d[key]], add_special_tokens=True,
                      truncation=False, padding=False)
            lens = [len(ids) for ids in enc["input_ids"]]
            trunc = sum(1 for L in lens if L > MAXLEN)
            empty = sum(1 for x in d[key] if x["text"] == "")
            tok_stats[f"{a}_{kind}"] = {
                "n": len(lens), "trunc_gt1024": trunc, "empty_strings": empty,
                "max_untrunc": max(lens) if lens else 0,
                "mean_untrunc": float(sum(lens) / len(lens)) if lens else 0.0,
            }
            np.save(PAY / f"{a}_{kind}_untrunc_len.npy",
                    np.array(lens, dtype=np.int32))
    (OUT / "tokenizer_stats.json").write_text(json.dumps(tok_stats, indent=2))

    # ---- encode ----
    prog = {"started": t0, "load_s": load_s, "weight_bytes": wbytes,
            "archives": {}, "first_batch": None}
    total_texts = sum(len(texts_meta[a]["docs"]) + len(texts_meta[a]["queries"])
                      for a in archives)
    done_texts = 0
    enc_t_total = 0.0
    first_done = False

    for a in archives:
        d = texts_meta[a]
        for kind, rowkey in (("docs", "row"), ("queries", None)):
            items = d[kind]
            texts = [x["text"] for x in items]
            hashes = [text_hash(t) for t in texts]
            untrunc = np.load(PAY / f"{a}_{kind}_untrunc_len.npy")
            n = len(texts)
            # resume: existing archive payload with matching hashes
            out_npz = PAY / f"{a}_{kind}.npz"
            pooled, have = load_checkpoint(out_npz, hashes, 1024)
            # batch plan over missing only, length-sorted
            missing = [i for i in range(n) if not have[i]]
            batches = plan_batches([int(untrunc[i]) for i in missing], BATCH)
            # map back to original indices, sorted by length within batch
            batches = [[missing[i] for i in b] for b in batches]
            for bi, bidx in enumerate(batches):
                btok = tok([texts[i] for i in bidx], padding=True, truncation=True,
                           max_length=MAXLEN, return_tensors="pt")
                bt0 = time.time()
                with torch.inference_mode():
                    out = model(input_ids=btok["input_ids"],
                                attention_mask=btok["attention_mask"])
                    h = out.last_hidden_state.detach().cpu().numpy()
                    m = btok["attention_mask"].detach().cpu().numpy()
                    p = masked_mean_pool(h, m)
                bt1 = time.time()
                pooled[np.array(bidx)] = p
                enc_t_total += (bt1 - bt0)
                done_texts += len(bidx)
                if not first_done:
                    dt = bt1 - bt0
                    prog["first_batch"] = {
                        "archive": a, "kind": kind, "batch": len(bidx),
                        "seconds": dt, "texts_per_s": len(bidx) / max(dt, 1e-9),
                        "est_total_s": (total_texts / len(bidx)) * dt,
                    }
                    first_done = True
                # per-batch shard checkpoint
                np.savez_compressed(
                    CKPT / f"{a}_{kind}_batch{bi:04d}.npz",
                    idx=np.array(bidx, dtype=np.int32), pooled=p.astype(np.float32))
                # per-archive cumulative checkpoint after each batch
                int8 = official_int8(pooled)
                packed = pack_sign(official_binary(pooled))
                have[np.array(bidx)] = True
                np.savez_compressed(
                    out_npz, pooled_f32=pooled, int8=int8, packed=packed,
                    hashes=np.array(hashes),
                    rows=np.array([x[rowkey] if rowkey else x["qid"] for x in items],
                                  dtype=object),
                    untrunc_len=untrunc, complete=have)
                prog["archives"].setdefault(a, {})[kind] = {
                    "done": int(have.sum()), "total": n}
                prog["done_texts"] = done_texts
                prog["total_texts"] = total_texts
                prog["encode_s_so_far"] = enc_t_total
                prog["elapsed_s"] = time.time() - t0
                try:
                    prog["peak_rss_bytes"] = resource.getrusage(
                        resource.RUSAGE_SELF).ru_maxrss * 1024
                except Exception:
                    pass
                (OUT / "progress.json").write_text(json.dumps(prog, indent=2))
            # finalize derived arrays exact (all rows now present)
            int8 = official_int8(pooled)
            packed = pack_sign(official_binary(pooled))
            np.savez_compressed(
                out_npz, pooled_f32=pooled, int8=int8, packed=packed,
                hashes=np.array(hashes),
                rows=np.array([x[rowkey] if rowkey else x["qid"] for x in items],
                              dtype=object),
                untrunc_len=untrunc, complete=np.ones(n, dtype=bool))
    prog["status"] = "ENCODE_DONE"
    prog["total_encode_s"] = enc_t_total
    prog["total_elapsed_s"] = time.time() - t0
    try:
        prog["peak_rss_bytes"] = resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        pass
    (OUT / "progress.json").write_text(json.dumps(prog, indent=2))
    print(f"ENCODE_DONE docs+queries={done_texts} encode_s={enc_t_total:.1f}", flush=True)


if __name__ == "__main__":
    main()
