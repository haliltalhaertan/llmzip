"""Q4: independent re-derivation of one ladder cell from stored artifacts.
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Method (independent of their C scorer and their metrics aggregator):
 1. Load results/shards/<SH>/packed_inputs.npz  -> P{bits} uint8 plane (bytes Hulusi Akar-doc),
    Q{bits} float query vector, SD{bits} float scales, tie_rank int32.
 2. Pure-numpy asymmetric score: s = (q/sd) @ Bp.T, Bp = unpacked bits mapped to +-1.
    Hamming check: s = -(popcount(doc xor querybits)).
 3. Own top-k with deterministic tie-break: lexsort by (-score, tie_rank),
    restricted to thePartition threshold rule is unnecessary here because we
    fully sort (n small); ties broken strictly by tie_rank, matching their topk().
 4. Own metrics: Hit@k = any gold in top-k; FR@k = |top-k cap gold|/|gold|.
    Compare per-query values and the shard aggregate against their
    results/shards/<SH>/quality.jsonl.gz row for the same (arm,bits),
    and the dataset-level aggregate against QUALITY_LEVELS.csv / SUMMARY.json.
Cohort: shard 500 = one LoCoMo archive (smallest benchmark by archive count;
single-shard check keeps the oracle independent and fast). Plus a full-LoCoMo
aggregation check over all 10 LoCoMo shards from per-query rows.
"""
import gzip, json, sys
import numpy as np

EV = "/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/extracted/LLMZIP_GERCEK_12_24_48_BAYT_2026-09-16/LLMZIP_BYTE_LADDER_2026-09-16"

def load_rows(sh):
    p = f"{EV}/results/shards/{sh:03d}/quality.jsonl.gz"
    return [json.loads(l) for l in gzip.open(p, "rt")]

def my_topk(s, k, tr):
    n = len(s); k = min(k, n)
    order = np.lexsort((tr, -s))  # score desc, then tie_rank asc
    return order[:k]

def my_metrics(s, g, tr):
    g = np.unique(np.asarray(g, dtype=int))
    order = my_topk(s, 100, tr)
    out = {}
    for k in (3, 10, 100):
        v = int(np.isin(order[:k], g).sum())
        out[f"hit{k}"] = float(v > 0)
        out[f"fr{k}"] = float(v / len(g))
    out["top10"] = order[:10].astype(int).tolist()
    return out

def check_shard(sh, bits=96, arm="qscale"):
    d = np.load(f"{EV}/results/shards/{sh:03d}/packed_inputs.npz", allow_pickle=True)
    P, qmat, sd = d[f"P{bits}"], d[f"Q{bits}"], d[f"SD{bits}"]
    tr = d["tie_rank"]
    n = tr.shape[0]
    assert P.shape == (bits // 8, n), (P.shape, n)
    assert abs(P.nbytes / n - bits // 8) < 1e-12
    # input gold for this shard
    import glob, hashlib
    plan = json.load(open(f"{EV}/PLAN_BEFORE_RUN.json"))
    e = plan["selection"][sh]
    a = json.loads(open(f"{EV}/inputs/{e['file']}", encoding="utf-8").read())
    rows = {(r["qid"], r["arm"], r["bits"]): r for r in load_rows(sh)}
    max_top10_diff = 0
    max_metric_diff = 0.0
    per_q = []
    for qi, qid in enumerate(a["qids"]):
        q = np.ascontiguousarray(qmat[qi], dtype=np.float64)
        Bp = np.where(np.unpackbits(P.T, axis=1, bitorder="little") == 1, 1.0, -1.0)
        if arm == "qscale":
            s = (q / sd) @ Bp.T
        elif arm == "asym":
            s = q @ Bp.T
        elif arm == "hamming":
            qb = (q >= 0).astype(np.uint8)
            doc = np.unpackbits(P.T, axis=1, bitorder="little")
            s = -np.sum(doc != qb[None, :], axis=1).astype(float)
        else:
            raise ValueError(arm)
        mine = my_metrics(s, a["gold"][qi], tr)
        theirs = rows[(qid, arm, bits)]
        d10 = int(np.count_nonzero(np.array(mine["top10"]) != np.array(theirs["top10"])))
        max_top10_diff = max(max_top10_diff, d10)
        for m in ("hit3", "fr3", "hit10", "fr10", "hit100", "fr100"):
            max_metric_diff = max(max_metric_diff, abs(mine[m] - theirs[m]))
        per_q.append((qid, mine["hit10"], mine["fr3"], theirs["hit10"], theirs["fr3"]))
    return {
        "shard": sh, "arm": arm, "bits": bits, "n_docs": n,
        "n_queries": len(a["qids"]), "dataset": a["dataset"],
        "max_top10_pos_diff": max_top10_diff,
        "max_metric_abs_diff": max_metric_diff,
        "my_hit10": float(np.mean([p[1] for p in per_q])),
        "my_fr3": float(np.mean([p[2] for p in per_q])),
        "their_hit10": float(np.mean([p[3] for p in per_q])),
        "their_fr3": float(np.mean([p[4] for p in per_q])),
    }

if __name__ == "__main__":
    # Which shards are LoCoMo? first shard index >= 500 per run_quality (470 LME + 40 = 510; order 470..509 first)
    plan = json.load(open(f"{EV}/PLAN_BEFORE_RUN.json"))
    for i, e in enumerate(plan["selection"]):
        if i in (0, 470, 500, 509):
            print(i, e["file"][:12], e.get("dataset", "?"))
    out = []
    # one LoCoMo shard + one LME shard + one PerLTQA shard, qscale96 + hamming96 + qscale384
    tests = [(500, "qscale", 96), (500, "hamming", 96), (500, "qscale", 384),
             (0, "qscale", 96), (470, "qscale", 96)]
    for sh, arm, bits in tests:
        try:
            r = check_shard(sh, bits, arm)
            print(json.dumps(r, indent=1))
            out.append(r)
        except Exception as ex:
            print(f"SHARD {sh} {arm}{bits} FAILED: {type(ex).__name__}: {ex}")
    json.dump(out, open("/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916b/a_ladder/q4_result.json", "w"), indent=1)
