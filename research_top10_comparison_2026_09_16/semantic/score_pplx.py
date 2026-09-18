"""Score all semantic arms, fit declared PCA96, emit per-query JSONL + payloads.

Arms (all deterministic protocol ties, exactly 10):
  PPLX_INT8        cosine(int8_q, int8_d)            [required]
  PPLX_BIN         -Hamming(bin_q, bin_d)            [required, true native BIN]
  PPLX_ASYM        cosine(int8_q, bin_d as +-1)      [required]
  PREQUANT_POOLED  cosine(pooled_q, pooled_d)        [extra, NOT paper baseline]
  PPLX_PCA96_SIGN  -Hamming(sign(PCA96(int8)))       [declared exploratory;
                     PCA fit on REALTALK DOCUMENT INT8 (as f32) ONLY,
                     random_state 20260915, centering with saved doc mean;
                     no query/gold fit; NOT native MRL]
Per-query JSONL: {qid, archive_id, gold, top10{arm:[rows]}, scores10{arm:[float]},
metrics{arm:{hit10,recall10,ndcg10}}}. Full score matrices per archive in
scores/*.npz; embedding payloads reused from payloads/*.npz for replay.
"""
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pplx_scorer import (asym_scores_int8xbin, cosine_scores_float,
                         cosine_scores_int8, hamming_scores_bin, official_binary,
                         prf_metrics, rank_top10, unpack_sign)

OUT = pathlib.Path(__file__).resolve().parent
PAY = OUT / "payloads"
SCO = OUT / "scores"
SCO.mkdir(exist_ok=True)
ROOT = OUT.parent
DATA_DIR = ROOT / "data"

ARMS = ["PPLX_INT8", "PPLX_BIN", "PPLX_ASYM", "PREQUANT_POOLED", "PPLX_PCA96_SIGN"]


def main():
    import resource
    t0 = time.time()
    archives = [f"RT{i:02d}" for i in range(1, 11)]
    for a in archives:
        for k in ("docs", "queries"):
            if not (PAY / f"{a}_{k}.npz").exists():
                print(f"MISSING {a}_{k}.npz; run encode first", flush=True)
                sys.exit(2)
            with np.load(PAY / f"{a}_{k}.npz", allow_pickle=False) as payload:
                assert payload["complete"].all(), f"INCOMPLETE {a}_{k}"
                assert np.isfinite(payload["pooled_f32"]).all(), f"NONFINITE {a}_{k}"
                meta = json.loads((DATA_DIR / f"{a}.json").read_text())
                from pplx_scorer import text_hash
                assert list(payload["hashes"]) == [text_hash(x["text"]) for x in meta[k]]

    # ---- declared PCA96 on REALTALK DOCUMENT INT8 (f32) ONLY ----
    t_pca0 = time.time()
    doc_mats = [np.load(PAY / f"{a}_docs.npz")["int8"].astype(np.float32)
                for a in archives]
    Dall = np.concatenate(doc_mats, axis=0)
    mean = Dall.mean(axis=0, keepdims=True)
    Xc = Dall - mean
    from sklearn.decomposition import PCA
    pca = PCA(n_components=96, random_state=20260915)
    Z = pca.fit_transform(Xc)
    t_pca = time.time() - t_pca0
    np.save(PAY / "pca96_mean.npy", mean.astype(np.float32))
    np.save(PAY / "pca96_components.npy", pca.components_.astype(np.float32))
    pca_shared_bytes = int((PAY / "pca96_mean.npy").stat().st_size +
                           (PAY / "pca96_components.npy").stat().st_size)
    C = pca.components_.astype(np.float64)  # [96,1024]

    def pca_sign(M):
        return np.where((M.astype(np.float64) - mean.astype(np.float64)) @ C.T >= 0,
                        np.int8(1), np.int8(-1))

    # ---- score per archive ----
    t_score0 = time.time()
    per_query_path = OUT / "per_query_pplx.jsonl"
    if per_query_path.exists():
        per_query_path.unlink()
    agg = {arm: {"hit": 0, "rec": 0.0, "ndcg": 0.0, "n": 0} for arm in ARMS}
    n_total = 0
    for a in archives:
        dd = np.load(PAY / f"{a}_docs.npz")
        qq = np.load(PAY / f"{a}_queries.npz")
        meta = json.loads((DATA_DIR / f"{a}.json").read_text())
        doc_rows = [x["row"] for x in meta["docs"]]
        doc_int8 = dd["int8"].astype(np.int8)
        q_int8 = qq["int8"].astype(np.int8)
        doc_bin = unpack_sign(dd["packed"], 1024)
        q_bin = unpack_sign(qq["packed"], 1024)
        doc_pool = dd["pooled_f32"].astype(np.float64)
        q_pool = qq["pooled_f32"].astype(np.float64)
        doc_pca = pca_sign(dd["int8"].astype(np.float32))
        q_pca = pca_sign(qq["int8"].astype(np.float32))
        S = {
            "PPLX_INT8": cosine_scores_int8(q_int8, doc_int8),
            "PPLX_BIN": hamming_scores_bin(q_bin, doc_bin),
            "PPLX_ASYM": asym_scores_int8xbin(q_int8, doc_bin),
            "PREQUANT_POOLED": cosine_scores_float(q_pool, doc_pool),
            "PPLX_PCA96_SIGN": hamming_scores_bin(q_pca, doc_pca),
        }
        np.savez_compressed(SCO / f"{a}_scores.npz", **{k: v for k, v in S.items()},
                            doc_rows=np.array(doc_rows, dtype=np.int32),
                            qids=np.array([x["qid"] for x in meta["queries"]]))
        with per_query_path.open("a") as f:
            for qi, q in enumerate(meta["queries"]):
                rec = {"qid": q["qid"], "archive_id": a, "gold": q["gold"],
                       "top10": {}, "scores10": {}, "metrics": {}}
                for arm in ARMS:
                    top = rank_top10(S[arm][qi], a, doc_rows)
                    order_idx = [doc_rows.index(r) for r in top]
                    rec["top10"][arm] = top
                    rec["scores10"][arm] = [float(S[arm][qi, j]) for j in order_idx]
                    rec["metrics"][arm] = prf_metrics(top, q["gold"])
                    agg[arm]["hit"] += rec["metrics"][arm]["hit10"]
                    agg[arm]["rec"] += rec["metrics"][arm]["recall10"]
                    agg[arm]["ndcg"] += rec["metrics"][arm]["ndcg10"]
                    agg[arm]["n"] += 1
                f.write(json.dumps(rec) + "\n")
                n_total += 1
    t_score = time.time() - t_score0
    summary = {
        "n_queries": n_total,
        "arms": {arm: {"mean_hit10": agg[arm]["hit"] / agg[arm]["n"],
                       "mean_recall10": agg[arm]["rec"] / agg[arm]["n"],
                       "mean_ndcg10": agg[arm]["ndcg"] / agg[arm]["n"]}
                 for arm in ARMS},
        "pca_fit_s": t_pca,
        "candidate_scoring_s": t_score,
        "pca_shared_bytes": pca_shared_bytes,
        "elapsed_s": time.time() - t0,
    }
    try:
        summary["peak_rss_bytes"] = resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        pass
    (OUT / "score_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"SCORE_DONE n={n_total} scoring_s={t_score:.1f} pca_s={t_pca:.1f}", flush=True)


if __name__ == "__main__":
    main()
