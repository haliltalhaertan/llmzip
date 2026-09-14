#!/usr/bin/env python3
"""Outcome-blind full-BEIR generalization runner for FLOAT96_CENTERED vs SIGN96_CENTERED.

The ranking stage cannot read qrels. Corpus/query representation and all top-k
rankings are frozen to disk first; only then are qrels opened for evaluation.

This is an exploratory research benchmark, not Task4F1 and not a whole-system
12-byte storage claim.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import importlib.util
import json
import math
import os
import platform
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import scipy
from scipy import sparse
import sklearn
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

DATASETS = {
    "scifact": {
        "split": "test",
        "md5": "5f7d1de60b170fc8027bb7898e2efca1",
    },
    "scidocs": {
        "split": "test",
        "md5": "38121350fc3a4d2f48850f6aff52e4a9",
    },
    "arguana": {
        "split": "test",
        "md5": "8ad3e3c2a5867cdced806d6503f29b99",
    },
    "fiqa": {
        "split": "test",
        "md5": "17918ed23cd04fb15047f73e6c3bd9d9",
    },
    "nfcorpus": {
        "split": "test",
        "md5": "a89dba18a62ef92f7d323ec890a0d38d",
    },
    "trec-covid": {
        "split": "test",
        "md5": "ce62140cb23feb9becf6270d0d1fe6d1",
    },
}
BASE_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{name}.zip"
SVD_RANDOM_STATE = 5204
N_NUISANCE = 20
MAX_K = 100
BOOTSTRAP_REPS = 5000
LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
EXPECTED_ADAPTER_SHA256 = "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722"
EXPECTED_T4C2_SHA256 = "3bb1126090ab619c061d10d0f1a5c20db1372c5e2cd66b5158905a65f460061b"


def digest_file(path: Path, algo: str = "sha256", chunk: int = 8 << 20) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_frozen_adapter(repo_root: Path):
    adapter_path = repo_root / "adapters" / "longmemeval_v52_adapter.py"
    t4c2_path = repo_root / "docs" / "v52" / "task4c2" / "v52_t4c2_centering_geometry.py"
    observed_adapter = digest_file(adapter_path)
    observed_t4c2 = digest_file(t4c2_path)
    if observed_adapter != EXPECTED_ADAPTER_SHA256:
        raise RuntimeError(f"adapter SHA mismatch: {observed_adapter}")
    if observed_t4c2 != EXPECTED_T4C2_SHA256:
        raise RuntimeError(f"T4C2 SHA mismatch: {observed_t4c2}")
    spec = importlib.util.spec_from_file_location("llmzip_frozen_adapter_v1", adapter_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod, observed_adapter, observed_t4c2


def download_dataset(name: str, cache_dir: Path) -> tuple[Path, dict]:
    meta = DATASETS[name]
    cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache_dir / f"{name}.zip"
    root = cache_dir / name
    if not zip_path.exists():
        urllib.request.urlretrieve(BASE_URL.format(name=name), zip_path)
    observed_md5 = digest_file(zip_path, "md5")
    if observed_md5 != meta["md5"]:
        raise RuntimeError(f"{name}: MD5 mismatch {observed_md5} != {meta['md5']}")
    if not (root / "corpus.jsonl").exists():
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(cache_dir)
    required = [root / "corpus.jsonl", root / "queries.jsonl", root / "qrels" / f"{meta['split']}.tsv"]
    missing = [str(x) for x in required if not x.exists()]
    if missing:
        raise RuntimeError(f"{name}: missing extracted files: {missing}")
    return root, {
        "download_url": BASE_URL.format(name=name),
        "zip_md5": observed_md5,
        "zip_sha256": digest_file(zip_path),
        "zip_bytes": zip_path.stat().st_size,
    }


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def corpus_text(row: dict) -> str:
    # Standard BEIR document payload: title + body. This rule is frozen before outcomes.
    title = str(row.get("title", "") or "").strip()
    text = str(row.get("text", "") or "").strip()
    if title and text:
        return title + "\n" + text
    return title or text


def load_corpus_queries(root: Path):
    doc_ids, texts = [], []
    for row in read_jsonl(root / "corpus.jsonl"):
        doc_ids.append(str(row["_id"]))
        texts.append(corpus_text(row))
    query_ids, queries = [], []
    for row in read_jsonl(root / "queries.jsonl"):
        query_ids.append(str(row["_id"]))
        queries.append(str(row["text"]))
    if len(set(doc_ids)) != len(doc_ids):
        raise RuntimeError("duplicate document ids")
    if len(set(query_ids)) != len(query_ids):
        raise RuntimeError("duplicate query ids")
    if not doc_ids or not query_ids:
        raise RuntimeError("empty corpus or query set")
    return doc_ids, texts, query_ids, queries


def build_repr(adapter, corpus_texts: list[str]) -> dict:
    t0 = time.perf_counter()
    wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(corpus_texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    combined_features = int(Z.shape[1])
    if combined_features < 96:
        raise RuntimeError(f"combined feature width {combined_features}<96")
    svd96 = TruncatedSVD(n_components=96, random_state=SVD_RANDOM_STATE)
    Y = normalize(svd96.fit_transform(Z))
    if Y.shape != (len(corpus_texts), 96):
        raise RuntimeError(f"unexpected Y shape {Y.shape}")
    rank = int(np.linalg.matrix_rank(Y[: min(len(Y), 5000)]))
    if rank < 96:
        raise RuntimeError(f"SVD96 rank failure: {rank}")
    mu = Y.mean(axis=0, keepdims=True)
    C = np.asarray(Y - mu, dtype=np.float64)
    signD = C >= 0
    # Release the large sparse construction before ranking.
    del Z, Xw, Xc, Xl, Y
    gc.collect()
    return {
        "wv": wv,
        "cv": cv,
        "base_svd": base_svd,
        "svd96": svd96,
        "mu": mu,
        "C": C,
        "signD": signD,
        "fit_seconds": time.perf_counter() - t0,
        "combined_features": combined_features,
        "rank96_sample": rank,
    }


def transform_queries(rep: dict, query_texts: list[str]):
    t0 = time.perf_counter()
    Qw = normalize(rep["wv"].transform(query_texts))
    Qc = normalize(rep["cv"].transform(query_texts))
    Ql = normalize(rep["base_svd"].transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(rep["svd96"].transform(Zq))
    qC = np.asarray(QY - rep["mu"], dtype=np.float64)
    signQ = qC >= 0
    if qC.shape[1] != 96:
        raise RuntimeError("query centered dimension != 96")
    return qC, signQ, time.perf_counter() - t0


def cosine_centered(C: np.ndarray, q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if qn <= 0 or np.any(dn <= 0):
        raise RuntimeError("zero centered norm")
    return (C @ q) / (dn * qn)


def nuisance_priorities(task: str, qid: str, trial: int, n: int) -> np.ndarray:
    seed_bytes = hashlib.sha256(f"{task}\0{qid}\0{trial}".encode("utf-8")).digest()[:8]
    seed = int.from_bytes(seed_bytes, "big")
    return np.random.default_rng(seed).random(n)


def exact_topk_candidates(primary: np.ndarray, valid: np.ndarray, k: int, minimize: bool) -> np.ndarray:
    vals = primary[valid]
    valid_idx = np.flatnonzero(valid)
    if len(valid_idx) <= k:
        return valid_idx
    if minimize:
        threshold = np.partition(vals, k - 1)[k - 1]
        return np.flatnonzero(valid & (primary <= threshold))
    threshold = np.partition(vals, len(vals) - k)[len(vals) - k]
    return np.flatnonzero(valid & (primary >= threshold))


def freeze_rankings(task: str, doc_ids: list[str], query_ids: list[str], C: np.ndarray, signD: np.ndarray, qC: np.ndarray, signQ: np.ndarray):
    n_q, n_d = len(query_ids), len(doc_ids)
    k = min(MAX_K, max(1, n_d - 1))
    float_top = np.full((N_NUISANCE, n_q, k), -1, dtype=np.int32)
    sign_top = np.full((N_NUISANCE, n_q, k), -1, dtype=np.int32)
    sign_boundary_size = np.zeros(n_q, dtype=np.int32)
    sign_candidate_size = np.zeros(n_q, dtype=np.int32)
    float_candidate_size = np.zeros(n_q, dtype=np.int32)
    doc_index = {d: i for i, d in enumerate(doc_ids)}
    valid_base = np.ones(n_d, dtype=bool)

    t0 = time.perf_counter()
    for qi, qid in enumerate(query_ids):
        valid = valid_base.copy()
        same = doc_index.get(qid)
        if same is not None:
            valid[same] = False  # BEIR's default ignore_identical_ids semantics.
        available = int(valid.sum())
        qk = min(k, available)
        fs = cosine_centered(C, qC[qi])
        hd = np.count_nonzero(signD != signQ[qi][None, :], axis=1).astype(np.int16)
        if not np.isfinite(fs[valid]).all():
            raise RuntimeError(f"{qid}: nonfinite float scores")

        fcand = exact_topk_candidates(fs, valid, qk, minimize=False)
        scand = exact_topk_candidates(hd, valid, qk, minimize=True)
        float_candidate_size[qi] = len(fcand)
        sign_candidate_size[qi] = len(scand)
        kth_hd = int(np.partition(hd[valid], qk - 1)[qk - 1])
        sign_boundary_size[qi] = int(np.sum(valid & (hd == kth_hd)))

        for trial in range(N_NUISANCE):
            fp = nuisance_priorities(task + ":float", qid, trial, len(fcand))
            sp = nuisance_priorities(task + ":sign", qid, trial, len(scand))
            fo = np.lexsort((fp, -fs[fcand]))
            so = np.lexsort((sp, hd[scand]))
            float_top[trial, qi, :qk] = fcand[fo[:qk]]
            sign_top[trial, qi, :qk] = scand[so[:qk]]

        if (qi + 1) % 100 == 0 or qi + 1 == n_q:
            print(json.dumps({"progress_queries": qi + 1, "total_queries": n_q}, sort_keys=True), flush=True)

    return float_top, sign_top, {
        "ranking_seconds": time.perf_counter() - t0,
        "sign_boundary_tie_rate_at_k": float(np.mean(sign_boundary_size > 1)),
        "mean_sign_boundary_size": float(np.mean(sign_boundary_size)),
        "max_sign_boundary_size": int(np.max(sign_boundary_size)),
        "mean_sign_candidate_size": float(np.mean(sign_candidate_size)),
        "mean_float_candidate_size": float(np.mean(float_candidate_size)),
    }


def load_qrels_after_freeze(path: Path, query_ids: list[str], doc_ids: list[str]):
    doc_index = {d: i for i, d in enumerate(doc_ids)}
    qset = set(query_ids)
    qrels: dict[str, dict[int, int]] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            qid, did, score_s = str(row[0]), str(row[1]), row[2]
            if qid not in qset or did not in doc_index:
                continue
            try:
                rel = int(float(score_s))
            except ValueError:
                continue
            if rel > 0:
                qrels.setdefault(qid, {})[doc_index[did]] = rel
    missing = [q for q in query_ids if q not in qrels]
    if missing:
        raise RuntimeError(f"queries without positive qrels: {missing[:10]} (n={len(missing)})")
    return qrels


def metrics_for_order(order: np.ndarray, rels: dict[int, int]) -> dict[str, float]:
    order = [int(x) for x in order if int(x) >= 0]
    relevant = set(rels)
    nrel = len(relevant)
    out: dict[str, float] = {}
    for k in (3, 10, 100):
        hits = sum(int(x in relevant) for x in order[:k])
        out[f"recall@{k}"] = hits / nrel
    # trec_eval-style linear relevance gains for nDCG.
    dcg = 0.0
    for rank, idx in enumerate(order[:10], start=1):
        gain = float(rels.get(idx, 0))
        if gain:
            dcg += gain / math.log2(rank + 1.0)
    ideal = sorted((float(x) for x in rels.values() if x > 0), reverse=True)[:10]
    idcg = sum(g / math.log2(rank + 1.0) for rank, g in enumerate(ideal, start=1))
    out["ndcg@10"] = dcg / idcg if idcg else 0.0
    seen = 0
    ap = 0.0
    for rank, idx in enumerate(order[:100], start=1):
        if idx in relevant:
            seen += 1
            ap += seen / rank
    out["map@100"] = ap / min(nrel, 100)
    rr = 0.0
    for rank, idx in enumerate(order[:10], start=1):
        if idx in relevant:
            rr = 1.0 / rank
            break
    out["mrr@10"] = rr
    return out


def bootstrap_ci(values: np.ndarray, seed: int) -> list[float]:
    values = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(BOOTSTRAP_REPS, len(values)))
    means = values[idx].mean(axis=1)
    return [float(x) for x in np.quantile(means, [0.025, 0.975])]


def evaluate(query_ids: list[str], qrels: dict[str, dict[int, int]], float_top: np.ndarray, sign_top: np.ndarray, task: str):
    metric_names = ["recall@3", "recall@10", "recall@100", "ndcg@10", "map@100", "mrr@10"]
    n_t, n_q, _ = float_top.shape
    fm = {m: np.zeros((n_t, n_q), dtype=np.float64) for m in metric_names}
    sm = {m: np.zeros((n_t, n_q), dtype=np.float64) for m in metric_names}
    for trial in range(n_t):
        for qi, qid in enumerate(query_ids):
            f = metrics_for_order(float_top[trial, qi], qrels[qid])
            s = metrics_for_order(sign_top[trial, qi], qrels[qid])
            for m in metric_names:
                fm[m][trial, qi] = f[m]
                sm[m][trial, qi] = s[m]
    aggregate = {}
    per_query = []
    for m in metric_names:
        qf = fm[m].mean(axis=0)
        qs = sm[m].mean(axis=0)
        qd = qs - qf
        aggregate[m] = {
            "float": float(qf.mean()),
            "sign": float(qs.mean()),
            "delta": float(qd.mean()),
            "delta_pp": float(qd.mean() * 100.0),
            "paired_query_bootstrap_95ci_delta": bootstrap_ci(qd, 260914 + sum(map(ord, task + m))),
        }
    for qi, qid in enumerate(query_ids):
        per_query.append({
            "query_id": qid,
            "gold_count": len(qrels[qid]),
            "delta_recall@3": float(sm["recall@3"][:, qi].mean() - fm["recall@3"][:, qi].mean()),
            "delta_ndcg@10": float(sm["ndcg@10"][:, qi].mean() - fm["ndcg@10"][:, qi].mean()),
        })
    return aggregate, per_query


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=sorted(DATASETS))
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--cache-dir", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "beir")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    task = args.task
    repo_root = Path(__file__).resolve().parents[2]
    adapter, adapter_sha, t4c2_sha = load_frozen_adapter(repo_root)

    root, source_meta = download_dataset(task, args.cache_dir)
    doc_ids, corpus_texts, query_ids, query_texts = load_corpus_queries(root)
    print(json.dumps({"task": task, "documents": len(doc_ids), "queries": len(query_ids)}, sort_keys=True), flush=True)

    rep = build_repr(adapter, corpus_texts)
    qC, signQ, query_seconds = transform_queries(rep, query_texts)
    float_top, sign_top, ranking_diag = freeze_rankings(task, doc_ids, query_ids, rep["C"], rep["signD"], qC, signQ)

    # Freeze rankings on disk BEFORE opening qrels.
    frozen_path = args.outdir / f"{task}.frozen_rankings.npz"
    np.savez_compressed(frozen_path, float_top=float_top, sign_top=sign_top)
    frozen_sha = digest_file(frozen_path)
    freeze_manifest = {
        "label": LABEL,
        "task": task,
        "documents": len(doc_ids),
        "queries": len(query_ids),
        "nuisance_trials": N_NUISANCE,
        "max_k": MAX_K,
        "frozen_rankings_sha256": frozen_sha,
        "qrels_opened": False,
        "timestamp_unix": time.time(),
    }
    manifest_path = args.outdir / f"{task}.pre_qrels_manifest.json"
    manifest_path.write_text(json.dumps(freeze_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"PRE_QRELS_FREEZE": freeze_manifest}, sort_keys=True), flush=True)

    # Outcome labels enter only here.
    qrels_path = root / "qrels" / f"{DATASETS[task]['split']}.tsv"
    qrels = load_qrels_after_freeze(qrels_path, query_ids, doc_ids)
    aggregate, per_query = evaluate(query_ids, qrels, float_top, sign_top, task)

    result = {
        "label": LABEL,
        "task": task,
        "protocol": {
            "dataset": "BEIR full",
            "split": DATASETS[task]["split"],
            "document_payload": "title + newline + text",
            "fit_inputs": "corpus documents only",
            "query_used_for_fit": False,
            "qrels_loaded_after_rankings_frozen": True,
            "ignore_identical_query_doc_ids": True,
            "float": "same centered 96D representation; cosine",
            "sign": "sign(same centered 96D representation); Hamming",
            "active_sign_code_bits": 96,
            "active_sign_code_bytes": 12,
            "whole_system_12_byte_claim": False,
            "nuisance_trials": N_NUISANCE,
        },
        "source": source_meta,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
        },
        "integrity": {
            "adapter_sha256": adapter_sha,
            "t4c2_sha256": t4c2_sha,
            "frozen_rankings_sha256": frozen_sha,
            "pre_qrels_manifest_sha256": digest_file(manifest_path),
        },
        "sizes": {"documents": len(doc_ids), "queries": len(query_ids), "positive_qrel_queries": len(qrels)},
        "representation": {
            "combined_features": rep["combined_features"],
            "rank96_sample": rep["rank96_sample"],
            "fit_seconds": rep["fit_seconds"],
            "query_transform_seconds": query_seconds,
        },
        "ranking": ranking_diag,
        "metrics": aggregate,
    }
    result_path = args.outdir / f"{task}.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pq_path = args.outdir / f"{task}.queries.jsonl"
    with pq_path.open("w", encoding="utf-8") as f:
        for row in per_query:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    print(json.dumps({
        "task": task,
        "float_recall@3": aggregate["recall@3"]["float"],
        "sign_recall@3": aggregate["recall@3"]["sign"],
        "delta_recall@3_pp": aggregate["recall@3"]["delta_pp"],
        "float_ndcg@10": aggregate["ndcg@10"]["float"],
        "sign_ndcg@10": aggregate["ndcg@10"]["sign"],
        "delta_ndcg@10_pp": aggregate["ndcg@10"]["delta_pp"],
        "sign_boundary_tie_rate_at_k": ranking_diag["sign_boundary_tie_rate_at_k"],
    }, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
