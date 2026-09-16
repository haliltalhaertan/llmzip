"""PQ12B conventional equal-payload arm for top10-r1 (pq worker).

Faiss ProductQuantizer d=96 M=12 nbits=8, seed 20260915, niter 20,
omp threads 1. Trained once globally on all REAL DOCUMENTS ONLY (8944 rows,
L2-normalized FLOAT96 C). Queries: original L2-normalized QC, asymmetric
LUT ADC without full doc reconstruction for the primary scorer.
Score = -sum_m ||q_m - c_{m,code}||^2 (higher better).
Deterministic ties: score desc, SHA256('top10-r1|RTxx|row') asc, row asc.
"""
import glob
import hashlib
import os
import pickle
import resource
import time

import numpy as np

D = 96
M = 12
NBITS = 8
KSUB = 256
DSUB = 8
SEED = 20260915
NITER = 20
CODE_SIZE = 12
CODEBOOK_BYTES_EXPECTED = 98304
RT_REPR = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"
OUTDIR = os.path.dirname(os.path.abspath(__file__))

# Zero-vector / nonfinite policy (declared before running): any zero-norm or
# nonfinite row in C/QC raises ValueError and aborts the run. None observed
# in the 10 caches (C norms 0.799..1.027, QC norms 0.724..1.046, 0 zeros).


def l2_normalize_rows(X):
    X = np.asarray(X, dtype=np.float64)
    if not np.all(np.isfinite(X)):
        raise ValueError("nonfinite input to l2_normalize_rows")
    norms = np.linalg.norm(X, axis=1)
    if np.any(norms == 0):
        raise ValueError("zero-norm row cannot be L2-normalized")
    return X / norms[:, None]


def tie_hash(archive_id, row):
    return hashlib.sha256(f"top10-r1|{archive_id}|{int(row)}".encode()).hexdigest()


def rank_top10(scores, archive_id):
    scores = np.asarray(scores)
    if scores.ndim != 1:
        raise ValueError("scores must be 1-D")
    if not np.all(np.isfinite(scores)):
        raise ValueError("nonfinite scores rejected (no silent zero handling)")
    n = len(scores)
    if n < 10:
        raise ValueError("need >=10 docs")
    hashes = [tie_hash(archive_id, r) for r in range(n)]
    order = sorted(range(n), key=lambda r: (-float(scores[r]), hashes[r], r))
    top = np.array(order[:10], dtype=np.int64)
    assert len(set(top.tolist())) == 10
    return top


def check_packed_codes(codes, n_docs):
    codes = np.asarray(codes)
    assert codes.dtype == np.uint8, codes.dtype
    assert codes.shape == (n_docs, CODE_SIZE), codes.shape
    assert codes.nbytes == n_docs * 12
    return 12


def pack_codes(codes):
    codes = np.asarray(codes, dtype=np.uint8)
    assert codes.ndim == 2 and codes.shape[1] == CODE_SIZE
    return codes.tobytes()


def unpack_codes(blob, n_docs):
    arr = np.frombuffer(blob, dtype=np.uint8).reshape(n_docs, CODE_SIZE).copy()
    return arr


def build_lut(q_norm, centroids):
    q_norm = np.asarray(q_norm, dtype=np.float64)
    centroids = np.asarray(centroids, dtype=np.float64)
    assert q_norm.shape == (96,)
    assert centroids.shape == (12, 256, 8)
    lut = np.empty((12, 256), dtype=np.float64)
    for m in range(12):
        qm = q_norm[m * 8:(m + 1) * 8]
        diff = centroids[m] - qm[None, :]
        lut[m] = np.sum(diff * diff, axis=1)
    return lut


def adc_scores_from_lut(lut, codes):
    lut = np.asarray(lut, dtype=np.float64)
    codes = np.asarray(codes, dtype=np.uint8)
    assert lut.shape == (12, 256)
    assert codes.ndim == 2 and codes.shape[1] == 12
    # sum per-subspace squared distances, negate (higher = closer)
    s = np.zeros(codes.shape[0], dtype=np.float64)
    for m in range(12):
        s += lut[m, codes[:, m]]
    return -s


def reconstruct(codes, centroids):
    codes = np.asarray(codes, dtype=np.uint8)
    centroids = np.asarray(centroids, dtype=np.float64)
    n = codes.shape[0]
    out = np.empty((n, 96), dtype=np.float64)
    for m in range(12):
        out[:, m * 8:(m + 1) * 8] = centroids[m][codes[:, m]]
    return out


def brute_scores(q_norm, xhat):
    q_norm = np.asarray(q_norm, dtype=np.float64)
    xhat = np.asarray(xhat, dtype=np.float64)
    diff = xhat - q_norm[None, :]
    return -np.sum(diff * diff, axis=1)


def compute_metrics(top10_rows, gold_rows):
    top = list(int(r) for r in top10_rows)
    gold = list(int(r) for r in gold_rows)
    gset = set(gold)
    hits = len(gset.intersection(top))
    hit10 = 1 if hits > 0 else 0
    recall10 = hits / len(gset) if gset else 0.0
    if not gset:
        ndcg10 = 0.0
    else:
        import math
        dcg = sum(1.0 / math.log2(i + 2) for i, r in enumerate(top) if r in gset)
        ideal_n = min(len(gset), 10)
        idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_n))
        ndcg10 = dcg / idcg if idcg > 0 else 0.0
    return {"hit10": hit10, "recall10": float(recall10), "ndcg10": float(ndcg10)}


def expected_hit_uniform(scores, gold_rows):
    """Exact expected binary Hit@10 under uniform random tie-breaking.

    If any gold is strictly above the cutoff, Hit=1 deterministically.
    Otherwise Hit depends only on sampling `slots' docs uniformly from the
    `n_tied' cutoff-tied pool: E[Hit] = 1 - C(n_tied-gold_tied, slots)/C(n_tied, slots).
    """
    import math
    scores = np.asarray(scores, dtype=np.float64)
    n = len(scores)
    thr = float(sorted(scores.tolist(), reverse=True)[9])
    greater_mask = scores > thr
    tied_mask = scores == thr
    n_greater = int(np.sum(greater_mask))
    n_tied = int(np.sum(tied_mask))
    assert n_tied >= 1
    slots = 10 - n_greater
    assert 1 <= slots <= n_tied
    gset = set(int(r) for r in gold_rows)
    n_gold_greater = sum(1 for r in range(n) if greater_mask[r] and r in gset)
    if n_gold_greater > 0:
        return 1.0
    n_gold_tied = sum(1 for r in range(n) if tied_mask[r] and r in gset)
    if n_gold_tied == 0:
        return 0.0
    if slots >= n_tied:
        return 1.0
    # hypergeometric tail: P(no gold drawn)
    denom = math.comb(n_tied, slots)
    numer = math.comb(n_tied - n_gold_tied, slots) if (n_tied - n_gold_tied) >= slots else 0
    return float(1.0 - numer / denom)


def input_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def build_training_matrix():
    """Stack L2-normalized C from all 10 archives (documents only).

    Returns (Xtr float64 (8944,96), meta). Never touches QC/gold.
    """
    files = sorted(glob.glob(os.path.join(RT_REPR, "RT*.pkl")))
    assert len(files) == 10, files
    parts = []
    n_docs = 0
    n_q_excluded = 0
    shas = {}
    per = {}
    for p in files:
        d = pickle.load(open(p, "rb"))
        Cn = l2_normalize_rows(d["C"])
        parts.append(Cn)
        n_docs += d["N"]
        n_q_excluded += len(d["qids"])
        shas[os.path.basename(p)] = input_sha256(p)
        per[os.path.basename(p)] = {"N": d["N"], "nq": len(d["qids"])}
    Xtr = np.vstack(parts)
    assert Xtr.shape == (8944, 96), Xtr.shape
    meta = {"n_docs": n_docs, "n_queries_excluded": n_q_excluded,
            "input_shas": shas, "per_archive": per}
    return Xtr, meta


def run_pipeline():
    import json
    import faiss
    faiss.omp_set_num_threads(1)
    t_all0 = time.perf_counter()
    # ---- train ----
    Xtr, meta = build_training_matrix()
    Xtr32 = np.ascontiguousarray(Xtr, dtype=np.float32)
    t0 = time.perf_counter()
    pq = faiss.ProductQuantizer(D, M, NBITS)
    pq.cp.seed = SEED
    pq.cp.niter = NITER
    assert pq.code_size == CODE_SIZE
    pq.train(Xtr32)
    train_s = time.perf_counter() - t0
    cent_vec = faiss.vector_to_array(pq.centroids)
    centroids32 = np.array(cent_vec, dtype=np.float32).reshape(M, KSUB, DSUB)
    assert centroids32.nbytes == CODEBOOK_BYTES_EXPECTED, centroids32.nbytes
    np.save(os.path.join(OUTDIR, "centroids.npy"), centroids32)
    centroids = centroids32.astype(np.float64)
    # ---- encode per archive ----
    files = sorted(glob.glob(os.path.join(RT_REPR, "RT*.pkl")))
    t1 = time.perf_counter()
    per_arch = {}
    for p in files:
        d = pickle.load(open(p, "rb"))
        arch = d["conv_id"]
        Cn = l2_normalize_rows(d["C"])
        Cn32 = np.ascontiguousarray(Cn, dtype=np.float32)
        codes = pq.compute_codes(Cn32)
        check_packed_codes(codes, d["N"])
        assert unpack_codes(pack_codes(codes), d["N"]).tobytes() == codes.tobytes()
        QCn = l2_normalize_rows(d["QC"])
        row_to_id = [None] * d["N"]
        for dia, row in d["id_to_row"].items():
            row_to_id[int(row)] = str(dia)
        assert all(x is not None for x in row_to_id)
        sha = input_sha256(p)
        np.savez_compressed(
            os.path.join(OUTDIR, f"{arch}_codes.npz"),
            codes=codes,
            QC_norm=np.asarray(QCn, dtype=np.float64),
            QC_orig=np.asarray(d["QC"], dtype=np.float64),
            qids=np.array(d["qids"]),
            gold_rows=np.array(d["gold_rows"], dtype=object),
            qa_valid=np.array([int(x.get("valid", 0)) for x in d["qa_diag"]]),
            row_to_id=np.array(row_to_id),
            input_sha=np.array([sha]),
            archive_id=np.array([arch]),
            source_file=np.array([d["file"]]),
            faiss_params=np.array([f"d={D},M={M},nbits={NBITS},seed={SEED},niter={NITER},threads=1"]),
        )
        per_arch[arch] = {"N": d["N"], "nq": len(d["qids"]),
                          "codes_shape": list(codes.shape),
                          "codes_bytes": int(codes.nbytes),
                          "input_sha": sha, "source_file": d["file"]}
    encode_s = time.perf_counter() - t1
    # ---- query (primary LUT ADC) + brute-force audit sample ----
    import math
    t2 = time.perf_counter()
    per_query_path = os.path.join(OUTDIR, "per_query.jsonl")
    n_valid = 0
    sum_hit = 0
    sum_rec = 0.0
    sum_ndcg = 0.0
    sum_exp = 0.0
    audit_maxdiff = 0.0
    per_arch_hits = {}
    with open(per_query_path, "w", encoding="utf-8") as out:
        for p in files:
            z = np.load(os.path.join(OUTDIR, f"{pickle.load(open(p,'rb'))['conv_id']}_codes.npz"),
                        allow_pickle=True)
            d = pickle.load(open(p, "rb"))
            arch = d["conv_id"]
            codes = z["codes"]
            QCn = np.asarray(z["QC_norm"], dtype=np.float64)
            row_to_id = [str(x) for x in z["row_to_id"].tolist()]
            arch_hit = 0
            arch_n = 0
            for qi, qid in enumerate(d["qids"]):
                gold = [int(r) for r in d["gold_rows"][qi]]
                valid = int(d["qa_diag"][qi].get("valid", 0))
                if not valid:
                    assert len(gold) == 0
                    continue
                q = QCn[qi]
                assert np.all(np.isfinite(q))
                lut = build_lut(q, centroids)
                scores = adc_scores_from_lut(lut, codes)
                assert np.all(np.isfinite(scores))
                top = rank_top10(scores, arch)
                # determinism rerun
                assert list(rank_top10(scores, arch)) == list(top)
                # brute-force audit on first valid query per archive
                m = compute_metrics(top, gold)
                exp_hit = expected_hit_uniform(scores, gold)
                top_ids = [row_to_id[int(r)] for r in top.tolist()]
                gold_ids = [row_to_id[g] for g in gold]
                out.write(json.dumps({
                    "qid": qid, "archive_id": arch, "query_index": qi,
                    "n_docs": d["N"],
                    "gold_rows": gold, "gold_ids": gold_ids,
                    "top10_rows": [int(r) for r in top.tolist()],
                    "top10_ids": top_ids,
                    "top10_scores": [float(scores[int(r)]) for r in top.tolist()],
                    "hit10": m["hit10"], "recall10": m["recall10"],
                    "ndcg10": m["ndcg10"],
                    "expected_hit10_uniform": float(exp_hit),
                    "category": int(d["cats"][qi]),
                }) + "\n")
                n_valid += 1
                arch_n += 1
                arch_hit += m["hit10"]
                sum_hit += m["hit10"]
                sum_rec += m["recall10"]
                sum_ndcg += m["ndcg10"]
                sum_exp += float(exp_hit)
            # brute-force cross-check: first valid query of this archive
            for qi2 in range(len(d["qids"])):
                if int(d["qa_diag"][qi2].get("valid", 0)):
                    qb = QCn[qi2]
                    lutb = build_lut(qb, centroids)
                    sb_lut = adc_scores_from_lut(lutb, codes)
                    xb = reconstruct(codes, centroids)
                    sb_bf = brute_scores(qb, xb)
                    diff = float(np.max(np.abs(sb_lut - sb_bf)))
                    audit_maxdiff = max(audit_maxdiff, diff)
                    assert diff <= 1e-5, (arch, diff)
                    break
            per_arch_hits[arch] = {"n_valid": arch_n,
                                   "hit10": arch_hit / arch_n if arch_n else 0.0}
    query_s = time.perf_counter() - t2
    assert n_valid == 705, n_valid
    total_s = time.perf_counter() - t_all0
    try:
        rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss_mb = float(rss_kb) / 1024.0
    except Exception:
        rss_mb = -1.0
    summary = {
        "arm": "PQ12B_FAISS_M12_NBITS8",
        "labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]",
                   "[NOT FOR CITATION]", "[DISCLOSE-BEFORE-USE]"],
        "params": {"d": D, "M": M, "nbits": NBITS, "ksub": KSUB, "dsub": DSUB,
                   "seed": SEED, "niter": NITER, "threads": 1,
                   "normalize": "L2 docs+queries before train/code/score",
                   "score": "-sum_m ||q_m-c||^2 (LUT ADC, higher better)",
                   "tie": "score desc, SHA256(top10-r1|ARCH|row) asc, row asc",
                   "reconstruction": "kept unnormalized (no silent renorm)"},
        "counts": {"n_archives": 10, "n_docs_total": 8944,
                   "n_queries_total": 728, "n_valid": n_valid,
                   "n_excluded_empty_gold": 23,
                   "per_archive_docs": {k: v["N"] for k, v in per_arch.items()}},
        "memory_bytes": {
            "payload_per_doc": 12,
            "payload_total": 8944 * 12,
            "codebook_actual": int(centroids32.nbytes),
            "codebook_expected": CODEBOOK_BYTES_EXPECTED,
            "codebook_amortized_per_doc": float(centroids32.nbytes) / 8944.0,
            "effective_per_doc_amortized": 12.0 + float(centroids32.nbytes) / 8944.0,
            "note": "Equal 12B payload does NOT imply equal total memory; "
                    "shared codebook charged separately.",
            "original_SVD_encoder_projector": "NOT MEASURED (missing from old cache, not zero)",
        },
        "metrics_overall": {
            "hit10": sum_hit / n_valid,
            "recall10": sum_rec / n_valid,
            "ndcg10": sum_ndcg / n_valid,
            "expected_hit10_uniform": sum_exp / n_valid,
            "n": n_valid,
        },
        "per_archive_hit10": per_arch_hits,
        "verification": {
            "lut_vs_brute_max_abs_diff": audit_maxdiff,
            "lut_vs_brute_tol": 1e-5,
            "packed_shape_ok": True,
            "bit_roundtrip_ok": True,
            "no_query_leak": {"train_rows": 8944, "queries_excluded": 728},
            "determinism_rerun_ok": True,
            "canonical_gold_705_ok": True,
        },
        "timing_s": {"train": train_s, "encode_all": encode_s,
                     "query_all": query_s, "total": total_s,
                     "per_query_ms": query_s / n_valid * 1000.0},
        "peak_rss_mb": rss_mb,
        "inputs": {"rt_repr_shas": meta["input_shas"],
                   "adapter_sha": input_sha256(
                       "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/bench3_realtalk_adapter.py")},
        "outputs": {"centroids": "centroids.npy",
                    "codes": [f"{a}_codes.npz" for a in sorted(per_arch)],
                    "per_query": "per_query.jsonl"},
        "tuning": "none (no hyperparameter search; no other workers' scores read)",
    }
    with open(os.path.join(OUTDIR, "SUMMARY.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"PQ12B done: n_valid={n_valid} hit10={sum_hit/n_valid:.4f} "
          f"recall={sum_rec/n_valid:.4f} ndcg={sum_ndcg/n_valid:.4f} "
          f"maxdiff={audit_maxdiff:.2e} train={train_s:.1f}s "
          f"encode={encode_s:.1f}s query={query_s:.1f}s rss={rss_mb:.0f}MB")
    return summary


if __name__ == "__main__":
    run_pipeline()
