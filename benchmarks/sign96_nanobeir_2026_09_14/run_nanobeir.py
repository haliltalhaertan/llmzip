#!/usr/bin/env python3
"""
Outcome-blind NanoBEIR sweep for the LLMZIP V52 FLOAT96_CENTERED vs SIGN96_CENTERED phenomenon.

This is an exploratory cross-benchmark generalization test, not Task4F1 and not a storage-cost claim.

Protocol:
1. Load only corpus + queries.
2. Fit the exact V52 archive-side representation on corpus text only.
3. Produce FLOAT96 centered-cosine and SIGN96 centered-Hamming rankings.
4. Only after rankings are frozen in memory, load qrels and score them.
5. Repeat deterministic binary tie breaking over 20 nuisance trials.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import datasets
from datasets import load_dataset
from huggingface_hub import HfApi
import numpy as np
import scipy
from scipy import sparse
import sklearn
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

DATASET_ID = "sentence-transformers/NanoBEIR-en"
TASKS = [
    "NanoArguAna",
    "NanoClimateFEVER",
    "NanoDBPedia",
    "NanoFEVER",
    "NanoFiQA2018",
    "NanoHotpotQA",
    "NanoMSMARCO",
    "NanoNFCorpus",
    "NanoNQ",
    "NanoQuoraRetrieval",
    "NanoSCIDOCS",
    "NanoSciFact",
    "NanoTouche2020",
]
SVD_RANDOM_STATE = 5204
N_NUISANCE = 20
MAX_K = 100
BOOTSTRAP_REPS = 5000
BASE_COMMIT = "ccedd5613c337e455a91043fd971c36360aa2fda"
EXPECTED_ADAPTER_SHA256 = "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722"
EXPECTED_T4C2_SHA256 = "3bb1126090ab619c061d10d0f1a5c20db1372c5e2cd66b5158905a65f460061b"
LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_frozen_adapter(repo_root: Path):
    adapter_path = repo_root / "adapters" / "longmemeval_v52_adapter.py"
    t4c2_path = repo_root / "docs" / "v52" / "task4c2" / "v52_t4c2_centering_geometry.py"
    observed_adapter = sha256_file(adapter_path)
    observed_t4c2 = sha256_file(t4c2_path)
    if observed_adapter != EXPECTED_ADAPTER_SHA256:
        raise RuntimeError(
            f"adapter SHA mismatch: {observed_adapter} != {EXPECTED_ADAPTER_SHA256}"
        )
    if observed_t4c2 != EXPECTED_T4C2_SHA256:
        raise RuntimeError(
            f"T4C2 SHA mismatch: {observed_t4c2} != {EXPECTED_T4C2_SHA256}"
        )
    spec = importlib.util.spec_from_file_location("llmzip_frozen_adapter_v1", adapter_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod, observed_adapter, observed_t4c2


def deterministic_priority(task: str, query_id: str, trial: int, doc_ids: list[str]) -> np.ndarray:
    vals = np.empty(len(doc_ids), dtype=np.float64)
    scale = float(2**64)
    for i, did in enumerate(doc_ids):
        payload = f"{task}\0{query_id}\0{trial}\0{did}".encode("utf-8")
        x = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
        vals[i] = x / scale
    return vals


def cosine_centered(C: np.ndarray, qC: np.ndarray) -> np.ndarray:
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(qC, dtype=np.float64).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if qn <= 0 or np.any(dn <= 0):
        raise RuntimeError("zero centered vector norm")
    return (C @ q) / (dn * qn)


def build_repr(adapter, corpus_texts: list[str]):
    t0 = time.perf_counter()
    wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(corpus_texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    if Z.shape[1] < 96:
        raise RuntimeError(f"combined feature width {Z.shape[1]} < 96")
    svd96 = TruncatedSVD(n_components=96, random_state=SVD_RANDOM_STATE)
    Y = normalize(svd96.fit_transform(Z))
    if Y.shape != (len(corpus_texts), 96):
        raise RuntimeError(f"Y shape {Y.shape} != ({len(corpus_texts)}, 96)")
    rank = int(np.linalg.matrix_rank(Y))
    if rank < 96:
        raise RuntimeError(f"SVD96 rank failure: {rank}")
    mu = Y.mean(axis=0, keepdims=True)
    C = np.asarray(Y - mu, dtype=np.float64)
    signD = C >= 0
    return {
        "wv": wv,
        "cv": cv,
        "base_svd": base_svd,
        "svd96": svd96,
        "Y": Y,
        "mu": mu,
        "C": C,
        "signD": signD,
        "fit_seconds": time.perf_counter() - t0,
        "combined_features": int(Z.shape[1]),
        "rank96": rank,
    }


def transform_queries(rep, query_texts: list[str]):
    t0 = time.perf_counter()
    Qw = normalize(rep["wv"].transform(query_texts))
    Qc = normalize(rep["cv"].transform(query_texts))
    Ql = normalize(rep["base_svd"].transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(rep["svd96"].transform(Zq))
    if QY.shape != (len(query_texts), 96):
        raise RuntimeError(f"QY shape {QY.shape} unexpected")
    qC = np.asarray(QY - rep["mu"], dtype=np.float64)
    signQ = qC >= 0
    return QY, qC, signQ, time.perf_counter() - t0


def freeze_topk_rankings(
    task: str,
    doc_ids: list[str],
    query_ids: list[str],
    C: np.ndarray,
    signD: np.ndarray,
    qC: np.ndarray,
    signQ: np.ndarray,
):
    """
    Produce top-100 rankings before qrels are loaded.
    Output arrays are [trial, query, rank].
    """
    n_q = len(query_ids)
    k = min(MAX_K, len(doc_ids))
    float_top = np.empty((N_NUISANCE, n_q, k), dtype=np.int32)
    sign_top = np.empty((N_NUISANCE, n_q, k), dtype=np.int32)
    boundary_tied = np.zeros(n_q, dtype=bool)
    boundary_group = np.zeros(n_q, dtype=np.int32)

    for qi, qid in enumerate(query_ids):
        fs = cosine_centered(C, qC[qi])
        hd = np.count_nonzero(signD != signQ[qi][None, :], axis=1).astype(np.int16)
        if not np.isfinite(fs).all():
            raise RuntimeError(f"{qid}: nonfinite FLOAT96 scores")

        sd = np.sort(hd)
        if len(sd) >= 3:
            d3 = int(sd[2])
            before = int(np.sum(hd < d3))
            at = int(np.sum(hd == d3))
            boundary_group[qi] = at
            boundary_tied[qi] = at > (3 - before)

        for trial in range(N_NUISANCE):
            pri = deterministic_priority(task, qid, trial, doc_ids)
            float_order = np.lexsort((pri, -fs))
            sign_order = np.lexsort((pri, hd))
            float_top[trial, qi] = float_order[:k]
            sign_top[trial, qi] = sign_order[:k]

    return float_top, sign_top, boundary_tied, boundary_group


def metric_block(order: np.ndarray, relevant: set[int]) -> dict[str, float]:
    if not relevant:
        raise RuntimeError("zero relevant documents")
    relset = relevant

    def hits(k: int) -> int:
        return sum(int(int(x) in relset) for x in order[: min(k, len(order))])

    out: dict[str, float] = {}
    for k in (1, 3, 5, 10):
        hk = hits(k)
        out[f"accuracy@{k}"] = float(hk > 0)
        out[f"recall@{k}"] = hk / len(relset)
        out[f"precision@{k}"] = hk / min(k, len(order))

    first = 0.0
    for rank, idx in enumerate(order[: min(10, len(order))], start=1):
        if int(idx) in relset:
            first = 1.0 / rank
            break
    out["mrr@10"] = first

    dcg = 0.0
    for rank, idx in enumerate(order[: min(10, len(order))], start=1):
        if int(idx) in relset:
            dcg += 1.0 / math.log2(rank + 1.0)
    ideal_n = min(len(relset), 10)
    idcg = sum(1.0 / math.log2(rank + 1.0) for rank in range(1, ideal_n + 1))
    out["ndcg@10"] = dcg / idcg if idcg else 0.0

    ap_sum = 0.0
    seen = 0
    cutoff = min(100, len(order))
    for rank, idx in enumerate(order[:cutoff], start=1):
        if int(idx) in relset:
            seen += 1
            ap_sum += seen / rank
    out["map@100"] = ap_sum / min(len(relset), 100)
    return out


def bootstrap_ci(values: np.ndarray, seed: int) -> list[float]:
    values = np.asarray(values, dtype=np.float64)
    if len(values) == 0:
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(BOOTSTRAP_REPS, len(values)))
    means = values[idx].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return [float(lo), float(hi)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=TASKS)
    ap.add_argument("--outdir", type=Path, default=Path("benchmark_out"))
    args = ap.parse_args()
    task = args.task
    args.outdir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]
    adapter, adapter_sha, t4c2_sha = load_frozen_adapter(repo_root)

    # Freeze the exact HF dataset revision before loading any benchmark data.
    revision = HfApi().dataset_info(DATASET_ID).sha

    # OUTCOME-BLIND STAGE: corpus + queries only.
    corpus_ds = load_dataset(DATASET_ID, "corpus", split=task, revision=revision)
    queries_ds = load_dataset(DATASET_ID, "queries", split=task, revision=revision)
    doc_ids = [str(x["_id"]) for x in corpus_ds]
    corpus_texts = [str(x["text"]) for x in corpus_ds]
    query_ids = [str(x["_id"]) for x in queries_ds]
    query_texts = [str(x["text"]) for x in queries_ds]
    if len(set(doc_ids)) != len(doc_ids):
        raise RuntimeError("duplicate corpus ids")
    if len(set(query_ids)) != len(query_ids):
        raise RuntimeError("duplicate query ids")

    rep = build_repr(adapter, corpus_texts)
    QY, qC, signQ, query_seconds = transform_queries(rep, query_texts)

    # Same-input proof: FLOAT and SIGN use exactly the same centered arrays.
    if rep["C"].shape[1] != 96 or qC.shape[1] != 96:
        raise RuntimeError("same-input dimensionality failure")

    float_top, sign_top, boundary_tied, boundary_group = freeze_topk_rankings(
        task, doc_ids, query_ids, rep["C"], rep["signD"], qC, signQ
    )

    # Only now may relevance labels enter the process.
    qrels_ds = load_dataset(DATASET_ID, "qrels", split=task, revision=revision)
    doc_index = {d: i for i, d in enumerate(doc_ids)}
    qrels: dict[str, set[int]] = {q: set() for q in query_ids}
    unknown_qrels = []
    for row in qrels_ds:
        qid = str(row["query-id"])
        did = str(row["corpus-id"])
        if qid not in qrels or did not in doc_index:
            unknown_qrels.append((qid, did))
            continue
        qrels[qid].add(doc_index[did])
    if unknown_qrels:
        raise RuntimeError(f"unmapped qrels: {unknown_qrels[:3]}")
    zero_gold = [q for q, s in qrels.items() if not s]
    if zero_gold:
        raise RuntimeError(f"zero-gold queries: {zero_gold[:5]}")

    metric_names = [
        "accuracy@1", "accuracy@3", "accuracy@5", "accuracy@10",
        "recall@1", "recall@3", "recall@5", "recall@10",
        "precision@1", "precision@3", "precision@5", "precision@10",
        "mrr@10", "ndcg@10", "map@100",
    ]
    n_q = len(query_ids)
    float_metrics = {m: np.zeros((N_NUISANCE, n_q), dtype=np.float64) for m in metric_names}
    sign_metrics = {m: np.zeros((N_NUISANCE, n_q), dtype=np.float64) for m in metric_names}

    for trial in range(N_NUISANCE):
        for qi, qid in enumerate(query_ids):
            fm = metric_block(float_top[trial, qi], qrels[qid])
            sm = metric_block(sign_top[trial, qi], qrels[qid])
            for m in metric_names:
                float_metrics[m][trial, qi] = fm[m]
                sign_metrics[m][trial, qi] = sm[m]

    aggregate = {}
    for m in metric_names:
        f = float_metrics[m]
        s = sign_metrics[m]
        qf = f.mean(axis=0)
        qs = s.mean(axis=0)
        qd = qs - qf
        aggregate[m] = {
            "float": float(f.mean()),
            "sign": float(s.mean()),
            "delta": float(qd.mean()),
            "delta_pp": float(qd.mean() * 100.0),
            "paired_query_bootstrap_95ci_delta": bootstrap_ci(
                qd, seed=260914 + sum(ord(c) for c in (task + m))
            ),
        }

    primary_qdelta = sign_metrics["recall@3"].mean(axis=0) - float_metrics["recall@3"].mean(axis=0)
    wins = int(np.sum(primary_qdelta > 1e-15))
    ties = int(np.sum(np.abs(primary_qdelta) <= 1e-15))
    losses = int(np.sum(primary_qdelta < -1e-15))

    query_rows = []
    for qi, qid in enumerate(query_ids):
        row = {
            "query_id": qid,
            "gold_count": len(qrels[qid]),
            "sign_boundary_tied_at_3": bool(boundary_tied[qi]),
            "sign_boundary_group_size_at_3": int(boundary_group[qi]),
        }
        for m in ("recall@3", "ndcg@10", "mrr@10", "map@100"):
            fv = float(float_metrics[m][:, qi].mean())
            sv = float(sign_metrics[m][:, qi].mean())
            row[f"float_{m}"] = fv
            row[f"sign_{m}"] = sv
            row[f"delta_{m}"] = sv - fv
        query_rows.append(row)

    result = {
        "label": LABEL,
        "schema": "LLMZIP_SIGN96_NANOBEIR_SWEEP_V1",
        "base_commit": BASE_COMMIT,
        "task": task,
        "dataset": {
            "id": DATASET_ID,
            "revision": revision,
            "corpus_fingerprint": getattr(corpus_ds, "_fingerprint", None),
            "queries_fingerprint": getattr(queries_ds, "_fingerprint", None),
            "qrels_fingerprint": getattr(qrels_ds, "_fingerprint", None),
            "n_docs": len(doc_ids),
            "n_queries": len(query_ids),
            "n_qrels": len(qrels_ds),
        },
        "source_bindings": {
            "adapter_sha256": adapter_sha,
            "t4c2_script_sha256": t4c2_sha,
        },
        "protocol": {
            "archive_fit": "corpus-only, no queries or qrels in fitting",
            "query_transform": "only after archive-side fit",
            "qrels_access": "only after FLOAT96/SIGN96 top-100 rankings frozen in memory",
            "float96": "centered 96D exact cosine",
            "sign96": "same centered 96D sign bits, integer Hamming",
            "active_sign_code_bytes": 12,
            "active_code_only_warning": "12 bytes excludes shared projector/vectorizer/index state",
            "nuisance_tie_trials": N_NUISANCE,
            "tie_priority": "SHA256(task, query_id, trial, doc_id), independent of relevance",
            "svd_random_state": SVD_RANDOM_STATE,
            "max_rank_depth": MAX_K,
            "primary_crosswalk_metric": "Recall@3 (same fractional-evidence semantics as original when qrels are binary)",
            "standard_ir_primary": "nDCG@10",
        },
        "representation": {
            "combined_features": rep["combined_features"],
            "rank96": rep["rank96"],
            "fit_seconds": rep["fit_seconds"],
            "query_transform_seconds": query_seconds,
        },
        "diagnostics": {
            "sign_boundary_tie_rate_at_3": float(boundary_tied.mean()),
            "median_sign_boundary_group_size_at_3": float(np.median(boundary_group)),
            "query_wtl_recall@3": {"wins": wins, "ties": ties, "losses": losses},
        },
        "metrics": aggregate,
        "package_versions": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "datasets": datasets.__version__,
            "platform": platform.platform(),
        },
        "interpretation_boundary": (
            "Exploratory out-of-domain generalization of the representation phenomenon. "
            "Not a preregistered Task4F1 result, not causal proof, and not a full-system storage-cost claim."
        ),
    }

    result_path = args.outdir / f"{task}.json"
    query_path = args.outdir / f"{task}.queries.jsonl"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    with query_path.open("w", encoding="utf-8") as f:
        for row in query_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({
        "task": task,
        "float_recall@3": aggregate["recall@3"]["float"],
        "sign_recall@3": aggregate["recall@3"]["sign"],
        "delta_recall@3_pp": aggregate["recall@3"]["delta_pp"],
        "float_ndcg@10": aggregate["ndcg@10"]["float"],
        "sign_ndcg@10": aggregate["ndcg@10"]["sign"],
        "delta_ndcg@10_pp": aggregate["ndcg@10"]["delta_pp"],
        "sign_boundary_tie_rate_at_3": result["diagnostics"]["sign_boundary_tie_rate_at_3"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
