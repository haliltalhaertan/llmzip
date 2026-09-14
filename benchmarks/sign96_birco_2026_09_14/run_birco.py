#!/usr/bin/env python3
"""Outcome-blind BIRCO complex-objective retrieval runner."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow
import pyarrow.parquet as pq
import scipy
import sklearn
from huggingface_hub import HfApi, hf_hub_download

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
TASKS = {
    "doris-mae": "mteb/BIRCO-DorisMae-Test",
    "arguana": "mteb/BIRCO-Arguana-Test",
    "clinical-trial": "mteb/BIRCO-ClinicalTrial-Test",
    "wtb": "mteb/BIRCO-WTB-Test",
    "relic": "mteb/BIRCO-Relic-Test",
}


def digest_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_helpers(repo_root: Path):
    p = repo_root / "benchmarks" / "sign96_beir_full_2026_09_14" / "run_beir_full.py"
    spec = importlib.util.spec_from_file_location("sign96_beir_helpers", p)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def find_parquet(api: HfApi, repo_id: str, revision: str, config: str) -> str:
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset", revision=revision)
    candidates = [
        f for f in files
        if f.startswith(f"data/{config}/") and f.endswith(".parquet") and "test" in Path(f).name
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"{repo_id}/{config}: expected one test parquet, got {candidates}")
    return candidates[0]


def load_corpus(path: Path):
    schema = pq.read_schema(path)
    cols = ["_id", "text"] + (["title"] if "title" in schema.names else [])
    t = pq.read_table(path, columns=cols)
    ids = [str(x) for x in t["_id"].to_pylist()]
    texts = []
    titles = t["title"].to_pylist() if "title" in t.column_names else [""] * len(ids)
    bodies = t["text"].to_pylist()
    for title, body in zip(titles, bodies):
        title = str(title or "").strip()
        body = str(body or "").strip()
        texts.append((title + "\n" + body) if title and body else (title or body))
    if len(set(ids)) != len(ids):
        raise RuntimeError("duplicate corpus IDs")
    return ids, texts


def load_queries(path: Path):
    t = pq.read_table(path, columns=["_id", "text"])
    ids = [str(x) for x in t["_id"].to_pylist()]
    texts = [str(x or "") for x in t["text"].to_pylist()]
    if len(set(ids)) != len(ids):
        raise RuntimeError("duplicate query IDs")
    return ids, texts


def structural_candidate_pools(default_path: Path, query_ids: list[str], doc_ids: list[str]):
    # Deliberately do not project/read `score` here.
    t = pq.read_table(default_path, columns=["query-id", "corpus-id"])
    qset = set(query_ids)
    didx = {d: i for i, d in enumerate(doc_ids)}
    pools: dict[str, list[int]] = defaultdict(list)
    seen_pairs = set()
    for q, d in zip(t["query-id"].to_pylist(), t["corpus-id"].to_pylist()):
        qid, did = str(q), str(d)
        if qid not in qset:
            raise RuntimeError(f"candidate row has unknown query {qid}")
        if did not in didx:
            raise RuntimeError(f"candidate row has unknown doc {did}")
        pair = (qid, did)
        if pair in seen_pairs:
            raise RuntimeError(f"duplicate candidate pair {pair}")
        seen_pairs.add(pair)
        pools[qid].append(didx[did])
    missing = [q for q in query_ids if not pools.get(q)]
    if missing:
        raise RuntimeError(f"queries without candidate pool: {missing[:5]}")
    return {q: pools[q] for q in query_ids}


def freeze_candidate_rankings(H, task: str, query_ids: list[str], pools: dict[str, list[int]], C: np.ndarray, signD: np.ndarray, qC: np.ndarray, signQ: np.ndarray):
    n_q = len(query_ids)
    max_pool = max(len(pools[q]) for q in query_ids)
    F = np.full((H.N_NUISANCE, n_q, max_pool), -1, dtype=np.int32)
    S = np.full((H.N_NUISANCE, n_q, max_pool), -1, dtype=np.int32)
    pool_sizes = np.zeros(n_q, dtype=np.int32)
    boundary_sizes = np.zeros(n_q, dtype=np.int32)
    t0 = time.perf_counter()
    for qi, qid in enumerate(query_ids):
        cand = np.asarray(pools[qid], dtype=np.int32)
        pool_sizes[qi] = len(cand)
        fs = H.cosine_centered(C[cand], qC[qi])
        hd = np.count_nonzero(signD[cand] != signQ[qi][None, :], axis=1).astype(np.int16)
        boundary_sizes[qi] = int(np.sum(hd == np.min(hd)))
        for trial in range(H.N_NUISANCE):
            fp = H.nuisance_priorities("BIRCO:" + task + ":float", qid, trial, len(cand))
            sp = H.nuisance_priorities("BIRCO:" + task + ":sign", qid, trial, len(cand))
            fo = np.lexsort((fp, -fs))
            so = np.lexsort((sp, hd))
            F[trial, qi, : len(cand)] = cand[fo]
            S[trial, qi, : len(cand)] = cand[so]
    return F, S, {
        "ranking_seconds": time.perf_counter() - t0,
        "min_candidate_pool": int(pool_sizes.min()),
        "mean_candidate_pool": float(pool_sizes.mean()),
        "max_candidate_pool": int(pool_sizes.max()),
        "sign_best_distance_tie_rate": float(np.mean(boundary_sizes > 1)),
        "mean_sign_best_tie_size": float(boundary_sizes.mean()),
    }


def load_relevance_after_freeze(default_path: Path, query_ids: list[str], doc_ids: list[str], expected_pools: dict[str, list[int]]):
    t = pq.read_table(default_path, columns=["query-id", "corpus-id", "score"])
    didx = {d: i for i, d in enumerate(doc_ids)}
    qset = set(query_ids)
    observed: dict[str, set[int]] = defaultdict(set)
    rels: dict[str, dict[int, float]] = defaultdict(dict)
    for q, d, score in zip(t["query-id"].to_pylist(), t["corpus-id"].to_pylist(), t["score"].to_pylist()):
        qid, did = str(q), str(d)
        if qid not in qset or did not in didx:
            raise RuntimeError("relevance row changed IDs after freeze")
        di = didx[did]
        observed[qid].add(di)
        s = float(score)
        if s > 0:
            rels[qid][di] = s
    for qid in query_ids:
        if observed[qid] != set(expected_pools[qid]):
            raise RuntimeError(f"{qid}: candidate pool changed between structural and relevance projections")
        if not rels[qid]:
            raise RuntimeError(f"{qid}: no positive relevance")
    return {q: rels[q] for q in query_ids}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=sorted(TASKS))
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    task, repo_id = args.task, TASKS[args.task]
    repo_root = Path(__file__).resolve().parents[2]
    H = load_helpers(repo_root)
    adapter, adapter_sha, t4c2_sha = H.load_frozen_adapter(repo_root)

    api = HfApi()
    revision = api.dataset_info(repo_id).sha
    corpus_rel = find_parquet(api, repo_id, revision, "corpus")
    queries_rel = find_parquet(api, repo_id, revision, "queries")
    default_rel = find_parquet(api, repo_id, revision, "default")
    corpus_path = Path(hf_hub_download(repo_id, corpus_rel, repo_type="dataset", revision=revision))
    queries_path = Path(hf_hub_download(repo_id, queries_rel, repo_type="dataset", revision=revision))
    default_path = Path(hf_hub_download(repo_id, default_rel, repo_type="dataset", revision=revision))

    doc_ids, corpus_texts = load_corpus(corpus_path)
    query_ids, query_texts = load_queries(queries_path)
    pools = structural_candidate_pools(default_path, query_ids, doc_ids)
    print(json.dumps({"task": task, "documents": len(doc_ids), "queries": len(query_ids), "candidate_rows": sum(map(len, pools.values())), "revision": revision}, sort_keys=True), flush=True)

    rep = H.build_repr(adapter, corpus_texts)
    qC, signQ, query_seconds = H.transform_queries(rep, query_texts)
    float_rank, sign_rank, ranking_diag = freeze_candidate_rankings(H, task, query_ids, pools, rep["C"], rep["signD"], qC, signQ)

    frozen_path = args.outdir / f"{task}.frozen_rankings.npz"
    np.savez_compressed(frozen_path, float_rank=float_rank, sign_rank=sign_rank)
    frozen_sha = digest_file(frozen_path)
    manifest = {
        "label": LABEL,
        "benchmark": "BIRCO",
        "task": task,
        "hf_repo": repo_id,
        "hf_revision": revision,
        "documents": len(doc_ids),
        "queries": len(query_ids),
        "candidate_rows": sum(map(len, pools.values())),
        "score_column_read": False,
        "frozen_rankings_sha256": frozen_sha,
        "timestamp_unix": time.time(),
    }
    manifest_path = args.outdir / f"{task}.pre_score_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"PRE_SCORE_FREEZE": manifest}, sort_keys=True), flush=True)

    rels = load_relevance_after_freeze(default_path, query_ids, doc_ids, pools)
    aggregate, per_query = H.evaluate(query_ids, rels, float_rank, sign_rank, "BIRCO:" + task)
    result = {
        "label": LABEL,
        "benchmark": "BIRCO",
        "task": task,
        "protocol": {
            "hf_repo": repo_id,
            "hf_revision": revision,
            "fit_inputs": "complete task corpus only",
            "query_used_for_fit": False,
            "candidate_pool_columns_read_before_freeze": ["query-id", "corpus-id"],
            "score_column_read_after_rankings_frozen": True,
            "float": "same centered 96D representation; cosine within candidate pool",
            "sign": "sign(same centered 96D representation); Hamming within candidate pool",
            "active_sign_code_bits": 96,
            "whole_system_12_byte_claim": False,
            "nuisance_trials": H.N_NUISANCE,
        },
        "source": {
            "corpus_file": corpus_rel,
            "queries_file": queries_rel,
            "default_file": default_rel,
            "corpus_sha256": digest_file(corpus_path),
            "queries_sha256": digest_file(queries_path),
            "default_sha256": digest_file(default_path),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "pyarrow": pyarrow.__version__,
        },
        "integrity": {
            "adapter_sha256": adapter_sha,
            "t4c2_sha256": t4c2_sha,
            "frozen_rankings_sha256": frozen_sha,
            "pre_score_manifest_sha256": digest_file(manifest_path),
        },
        "sizes": {"documents": len(doc_ids), "queries": len(query_ids), "candidate_rows": sum(map(len, pools.values()))},
        "representation": {"combined_features": rep["combined_features"], "rank96_sample": rep["rank96_sample"], "fit_seconds": rep["fit_seconds"], "query_transform_seconds": query_seconds},
        "ranking": ranking_diag,
        "metrics": aggregate,
    }
    (args.outdir / f"{task}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (args.outdir / f"{task}.queries.jsonl").open("w", encoding="utf-8") as f:
        for row in per_query:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"task": task, "delta_recall@3_pp": aggregate["recall@3"]["delta_pp"], "delta_ndcg@10_pp": aggregate["ndcg@10"]["delta_pp"], "float_ndcg@10": aggregate["ndcg@10"]["float"], "sign_ndcg@10": aggregate["ndcg@10"]["sign"]}, indent=2, sort_keys=True), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
