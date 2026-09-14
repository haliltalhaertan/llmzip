#!/usr/bin/env python3
"""Loader-fixed full-BEIR runner.

BEIR queries.jsonl may contain queries from multiple splits. Rankings are still
frozen for every query before qrels are opened. After the freeze, evaluation is
restricted to query IDs that occur with positive relevance in the frozen test
qrels, matching standard BEIR split semantics.
"""
from __future__ import annotations
import argparse, csv, importlib.util, json, os, platform, sys, time
from pathlib import Path
import numpy as np
import scipy, sklearn


def load_base(repo_root: Path):
    p = repo_root / "benchmarks" / "sign96_beir_full_2026_09_14" / "run_beir_full.py"
    spec = importlib.util.spec_from_file_location("beir_v1", p)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def load_split_qrels(path: Path, query_ids: list[str], doc_ids: list[str]):
    doc_index = {d: i for i, d in enumerate(doc_ids)}
    qset = set(query_ids)
    qrels: dict[str, dict[int, int]] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            qid, did = str(row[0]), str(row[1])
            if qid not in qset or did not in doc_index:
                continue
            try:
                rel = int(float(row[2]))
            except ValueError:
                continue
            if rel > 0:
                qrels.setdefault(qid, {})[doc_index[did]] = rel
    eval_qids = [q for q in query_ids if q in qrels]
    if not eval_qids:
        raise RuntimeError("test split contains no mapped positive qrels")
    return qrels, eval_qids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--cache-dir", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "beir")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]
    H = load_base(repo_root)
    if args.task not in H.DATASETS:
        raise RuntimeError(f"unknown task {args.task}")
    task = args.task
    adapter, adapter_sha, t4c2_sha = H.load_frozen_adapter(repo_root)
    root, source_meta = H.download_dataset(task, args.cache_dir)
    doc_ids, corpus_texts, query_ids, query_texts = H.load_corpus_queries(root)
    print(json.dumps({"task": task, "documents": len(doc_ids), "all_queries": len(query_ids), "loader_fix": "evaluate test-qrels subset only"}, sort_keys=True), flush=True)

    rep = H.build_repr(adapter, corpus_texts)
    qC, signQ, query_seconds = H.transform_queries(rep, query_texts)
    float_top, sign_top, ranking_diag = H.freeze_rankings(task, doc_ids, query_ids, rep["C"], rep["signD"], qC, signQ)

    frozen_path = args.outdir / f"{task}.frozen_rankings.npz"
    np.savez_compressed(frozen_path, float_top=float_top, sign_top=sign_top)
    frozen_sha = H.digest_file(frozen_path)
    manifest = {
        "label": H.LABEL,
        "task": task,
        "documents": len(doc_ids),
        "all_queries_ranked": len(query_ids),
        "nuisance_trials": H.N_NUISANCE,
        "max_k": H.MAX_K,
        "frozen_rankings_sha256": frozen_sha,
        "qrels_opened": False,
        "loader_fix": "BEIR queries.jsonl may contain multiple splits; score only qids present in test qrels after blind freeze",
        "timestamp_unix": time.time(),
    }
    manifest_path = args.outdir / f"{task}.pre_qrels_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"PRE_QRELS_FREEZE": manifest}, sort_keys=True), flush=True)

    qrels_path = root / "qrels" / f"{H.DATASETS[task]['split']}.tsv"
    qrels, eval_qids = load_split_qrels(qrels_path, query_ids, doc_ids)
    qpos = {q: i for i, q in enumerate(query_ids)}
    eval_idx = np.asarray([qpos[q] for q in eval_qids], dtype=np.int64)
    eval_float = float_top[:, eval_idx, :]
    eval_sign = sign_top[:, eval_idx, :]
    aggregate, per_query = H.evaluate(eval_qids, qrels, eval_float, eval_sign, task)

    result = {
        "label": H.LABEL,
        "task": task,
        "protocol": {
            "dataset": "BEIR full",
            "split": H.DATASETS[task]["split"],
            "document_payload": "title + newline + text",
            "fit_inputs": "corpus documents only",
            "query_used_for_fit": False,
            "all_queries_ranked_before_qrels": True,
            "evaluation_query_selection_after_freeze": "query IDs with positive qrels in requested split",
            "qrels_loaded_after_rankings_frozen": True,
            "ignore_identical_query_doc_ids": True,
            "float": "same centered 96D representation; cosine",
            "sign": "sign(same centered 96D representation); Hamming",
            "active_sign_code_bits": 96,
            "active_sign_code_bytes": 12,
            "whole_system_12_byte_claim": False,
            "nuisance_trials": H.N_NUISANCE,
        },
        "source": source_meta,
        "environment": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__, "sklearn": sklearn.__version__},
        "integrity": {"adapter_sha256": adapter_sha, "t4c2_sha256": t4c2_sha, "frozen_rankings_sha256": frozen_sha, "pre_qrels_manifest_sha256": H.digest_file(manifest_path)},
        "sizes": {
            "documents": len(doc_ids),
            "all_queries_ranked": len(query_ids),
            "queries": len(eval_qids),
            "unjudged_or_other_split_queries_not_scored": len(query_ids) - len(eval_qids),
        },
        "representation": {"combined_features": rep["combined_features"], "rank96_sample": rep["rank96_sample"], "fit_seconds": rep["fit_seconds"], "query_transform_seconds": query_seconds},
        "ranking": ranking_diag,
        "metrics": aggregate,
    }
    (args.outdir / f"{task}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (args.outdir / f"{task}.queries.jsonl").open("w", encoding="utf-8") as f:
        for row in per_query:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"task": task, "evaluated_queries": len(eval_qids), "delta_recall@3_pp": aggregate["recall@3"]["delta_pp"], "delta_ndcg@10_pp": aggregate["ndcg@10"]["delta_pp"], "float_ndcg@10": aggregate["ndcg@10"]["float"], "sign_ndcg@10": aggregate["ndcg@10"]["sign"]}, indent=2, sort_keys=True), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
