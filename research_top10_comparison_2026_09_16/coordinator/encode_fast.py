"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Coordinator PPLX-0.6B encoder: identical official semantics to semantic/pplx_scorer
(fixed FP32 torch pooling + official INT8/BIN), but token-budget batching and full
CPU threads. Writes the SAME payload schema semantic/score_pplx.py consumes.

Usage: ml-python encode_fast.py [--probe N]
"""
import argparse, json, os, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SEM = ROOT / "semantic"
sys.path.insert(0, str(SEM))
os.environ.setdefault("HF_MODULES_CACHE", str(SEM / ".hf_modules"))
MODEL_DIR = ROOT / "model"
DATA_DIR = ROOT / "data"
PAY = SEM / "payloads"
PAY.mkdir(exist_ok=True)
MAXLEN = 1024
TOKEN_BUDGET = 16384
MAX_TEXTS = 256

from pplx_scorer import (load_checkpoint, masked_mean_pool, official_binary,
                         official_int8, pack_sign, text_hash)


def plan_token_batches(lengths, budget=TOKEN_BUDGET, max_texts=MAX_TEXTS):
    """Length-sorted batches capped by padded-token budget. Returns index lists."""
    order = sorted(range(len(lengths)), key=lambda i: lengths[i])
    out, cur, curmax = [], [], 0
    for i in order:
        L = min(int(lengths[i]), MAXLEN)
        newmax = max(curmax, L)
        if cur and (newmax * (len(cur) + 1) > budget or len(cur) >= max_texts):
            out.append(cur); cur, curmax = [i], L
        else:
            cur.append(i); curmax = newmax
    if cur:
        out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=int, default=0)
    ap.add_argument("--threads", type=int, default=16)
    args = ap.parse_args()
    import resource, torch
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    from transformers import AutoModel, AutoTokenizer

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True, trust_remote_code=True)
    model = AutoModel.from_pretrained(str(MODEL_DIR), local_files_only=True,
                                      trust_remote_code=True, dtype=torch.float32)
    model.eval()
    print(f"load_s={time.time()-t0:.1f} threads={args.threads}", flush=True)

    archives = [f"RT{i:02d}" for i in range(1, 11)]
    total_done, enc_s, t_start = 0, 0.0, time.time()
    for a in archives:
        meta = json.loads((DATA_DIR / f"{a}.json").read_text())
        for kind in ("docs", "queries"):
            items = meta[kind]
            texts = [x["text"] for x in items]
            hashes = [text_hash(t) for t in texts]
            n = len(texts)
            out_npz = PAY / f"{a}_{kind}.npz"
            pooled, have = load_checkpoint(out_npz, hashes, 1024)
            if have.all():
                print(f"{a}_{kind}: cached {n}", flush=True)
                continue
            untrunc = np.load(PAY / f"{a}_{kind}_untrunc_len.npy")
            missing = [i for i in range(n) if not have[i]]
            batches = plan_token_batches([int(untrunc[i]) for i in missing])
            batches = [[missing[j] for j in b] for b in batches]
            for bi, bidx in enumerate(batches):
                bt = tok([texts[i] for i in bidx], padding=True, truncation=True,
                         max_length=MAXLEN, return_tensors="pt")
                s = time.time()
                with torch.inference_mode():
                    o = model(input_ids=bt["input_ids"], attention_mask=bt["attention_mask"])
                    p = masked_mean_pool(o.last_hidden_state.numpy(), bt["attention_mask"].numpy())
                dt = time.time() - s
                enc_s += dt
                pooled[np.array(bidx)] = p
                have[np.array(bidx)] = True
                total_done += len(bidx)
                print(f"{a}_{kind} batch{bi} texts={len(bidx)} pad={bt['input_ids'].shape[1]} "
                      f"s={dt:.2f} rate={len(bidx)/dt:.2f}/s done={total_done}", flush=True)
                np.savez(out_npz, pooled_f32=pooled, int8=official_int8(pooled),
                         packed=pack_sign(official_binary(pooled)),
                         hashes=np.array(hashes), untrunc_len=untrunc, complete=have)
                (SEM / "progress_fast.json").write_text(json.dumps({
                    "archive": a, "kind": kind, "done_texts": total_done,
                    "encode_s": enc_s, "elapsed_s": time.time() - t_start,
                    "rate_texts_per_s": total_done / max(enc_s, 1e-9),
                    "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                }, indent=2))
                if args.probe and total_done >= args.probe:
                    print(f"PROBE_DONE texts={total_done} enc_s={enc_s:.1f} "
                          f"rate={total_done/enc_s:.2f}/s est_all_s={9649/(total_done/enc_s):.0f}", flush=True)
                    return
    print(f"ENCODE_DONE texts={total_done} enc_s={enc_s:.1f} wall_s={time.time()-t_start:.1f}", flush=True)


if __name__ == "__main__":
    main()
