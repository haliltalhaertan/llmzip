#!/usr/bin/env python3
"""Outcome-blind BRIGHT reasoning-intensive retrieval runner.

Only query/id/excluded-id columns are read from the examples parquet before
rankings are frozen. gold_ids are read in a second parquet projection only
after the frozen ranking file exists and is hashed.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, platform, sys, time
from pathlib import Path

import numpy as np
import pyarrow
import pyarrow.parquet as pq
import scipy
import sklearn
from huggingface_hub import HfApi, hf_hub_download

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
DATASET_ID = "xlangai/BRIGHT"
TASKS = [
    "biology",
    "earth_science",
    "economics",
    "psychology",
    "robotics",
    "stackoverflow",
    "sustainable_living",
    "pony",
]


def digest_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_beir_helpers(repo_root: Path):
    p = repo_root / "benchmarks" / "sign96_beir_full_2026_09_14" / "run_beir_full.py"
    spec = importlib.util.spec_from_file_location("sign96_beir_helpers", p)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def as_text_list(values):
    return [str(x) for x in values]


def validate_no_special_exclusions(task: str, excluded_rows: list):
    # BRIGHT documentation says special exclusion lists apply to theoremqa/aops/leetcode,
    # none of which are in this frozen wave. Fail closed if the data contradicts that.
    bad = []
    for i, xs in enumerate(excluded_rows):
        if xs is None:
            continue
        vals = [str(x) for x in (xs if isinstance(xs, list) else [xs])]
        vals = [x for x in vals if x not in {"", "N/A", "None"}]
        if vals:
            bad.append((i, vals[:3]))
    if bad:
        raise RuntimeError(f"{task}: unexpected nonempty excluded_ids in frozen no-special-exclusion wave: {bad[:3]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=TASKS)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    task = args.task
    repo_root = Path(__file__).resolve().parents[2]
    H = load_beir_helpers(repo_root)
    adapter, adapter_sha, t4c2_sha = H.load_frozen_adapter(repo_root)

    revision = HfApi().dataset_info(DATASET_ID).sha
    doc_rel = f"documents/{task}-00000-of-00001.parquet"
    ex_rel = f"examples/{task}-00000-of-00001.parquet"
    doc_path = Path(hf_hub_download(DATASET_ID, filename=doc_rel, repo_type="dataset", revision=revision))
    ex_path = Path(hf_hub_download(DATASET_ID, filename=ex_rel, repo_type="dataset", revision=revision))

    # OUTCOME-BLIND projection: documents + query fields only. Do not read gold_ids.
    docs = pq.read_table(doc_path, columns=["id", "content"])
    doc_ids = as_text_list(docs["id"].to_pylist())
    corpus_texts = as_text_list(docs["content"].to_pylist())
    pre = pq.read_table(ex_path, columns=["id", "query", "excluded_ids"])
    query_ids = as_text_list(pre["id"].to_pylist())
    query_texts = as_text_list(pre["query"].to_pylist())
    excluded_rows = pre["excluded_ids"].to_pylist()
    validate_no_special_exclusions(task, excluded_rows)
    del docs, pre

    if len(set(doc_ids)) != len(doc_ids) or len(set(query_ids)) != len(query_ids):
        raise RuntimeError("duplicate ids")
    print(json.dumps({"task": task, "documents": len(doc_ids), "queries": len(query_ids), "revision": revision}, sort_keys=True), flush=True)

    rep = H.build_repr(adapter, corpus_texts)
    qC, signQ, query_seconds = H.transform_queries(rep, query_texts)
    float_top, sign_top, ranking_diag = H.freeze_rankings(task, doc_ids, query_ids, rep["C"], rep["signD"], qC, signQ)

    frozen_path = args.outdir / f"{task}.frozen_rankings.npz"
    np.savez_compressed(frozen_path, float_top=float_top, sign_top=sign_top)
    frozen_sha = digest_file(frozen_path)
    manifest = {
        "label": LABEL,
        "benchmark": "BRIGHT",
        "task": task,
        "hf_revision": revision,
        "documents": len(doc_ids),
        "queries": len(query_ids),
        "frozen_rankings_sha256": frozen_sha,
        "gold_ids_column_read": False,
        "timestamp_unix": time.time(),
    }
    manifest_path = args.outdir / f"{task}.pre_gold_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"PRE_GOLD_FREEZE": manifest}, sort_keys=True), flush=True)

    # Labels enter only now, via a new column projection.
    gold_table = pq.read_table(ex_path, columns=["id", "gold_ids"])
    gold_qids = as_text_list(gold_table["id"].to_pylist())
    gold_lists = gold_table["gold_ids"].to_pylist()
    if gold_qids != query_ids:
        raise RuntimeError("query order changed between pre-gold and gold projections")
    doc_index = {d: i for i, d in enumerate(doc_ids)}
    qrels: dict[str, dict[int, int]] = {}
    missing_gold_ids = []
    for qid, gids in zip(query_ids, gold_lists):
        rels = {}
        for gid in gids or []:
            sg = str(gid)
            if sg not in doc_index:
                missing_gold_ids.append((qid, sg))
                continue
            rels[doc_index[sg]] = 1
        if not rels:
            raise RuntimeError(f"{qid}: zero mapped gold documents")
        qrels[qid] = rels
    if missing_gold_ids:
        raise RuntimeError(f"unmapped gold ids: {missing_gold_ids[:5]} (n={len(missing_gold_ids)})")

    aggregate, per_query = H.evaluate(query_ids, qrels, float_top, sign_top, "BRIGHT:" + task)
    result = {
        "label": LABEL,
        "task": task,
        "benchmark": "BRIGHT",
        "protocol": {
            "hf_dataset": DATASET_ID,
            "hf_revision": revision,
            "fit_inputs": "task corpus documents only",
            "query_used_for_fit": False,
            "gold_ids_read_after_rankings_frozen": True,
            "pre_gold_example_columns": ["id", "query", "excluded_ids"],
            "float": "same centered 96D representation; cosine",
            "sign": "sign(same centered 96D representation); Hamming",
            "active_sign_code_bits": 96,
            "whole_system_12_byte_claim": False,
            "nuisance_trials": H.N_NUISANCE,
        },
        "source": {
            "documents_file": doc_rel,
            "examples_file": ex_rel,
            "documents_sha256": digest_file(doc_path),
            "examples_sha256": digest_file(ex_path),
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
            "pre_gold_manifest_sha256": digest_file(manifest_path),
        },
        "sizes": {"documents": len(doc_ids), "queries": len(query_ids)},
        "representation": {
            "combined_features": rep["combined_features"],
            "rank96_sample": rep["rank96_sample"],
            "fit_seconds": rep["fit_seconds"],
            "query_transform_seconds": query_seconds,
        },
        "ranking": ranking_diag,
        "metrics": aggregate,
    }
    (args.outdir / f"{task}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (args.outdir / f"{task}.queries.jsonl").open("w", encoding="utf-8") as f:
        for row in per_query:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({
        "task": task,
        "delta_recall@3_pp": aggregate["recall@3"]["delta_pp"],
        "delta_ndcg@10_pp": aggregate["ndcg@10"]["delta_pp"],
        "float_ndcg@10": aggregate["ndcg@10"]["float"],
        "sign_ndcg@10": aggregate["ndcg@10"]["sign"],
    }, indent=2, sort_keys=True), flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
