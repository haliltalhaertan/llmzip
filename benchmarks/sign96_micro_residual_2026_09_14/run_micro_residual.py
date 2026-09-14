#!/usr/bin/env python3
"""Outcome-blind SIGN96 micro-residual NanoBEIR experiment.

Frozen protocol: see PROTOCOL.md.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
BUDGETS = (0, 4, 8, 16)
PRIMARY_BUDGET = 8
METRICS = ("recall@3", "ndcg@10", "mrr@10", "map@100")


def load_base(repo_root: Path):
    path = repo_root / "benchmarks" / "sign96_nanobeir_2026_09_14" / "run_nanobeir.py"
    spec = importlib.util.spec_from_file_location("sign96_nanobeir_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load NanoBEIR base runner")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def residual_spec(C: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    C = np.asarray(C, dtype=np.float64)
    if C.ndim != 2 or C.shape[1] != 96:
        raise RuntimeError(f"unexpected C shape {C.shape}")
    absC = np.abs(C)
    dispersion = np.var(absC, axis=0)
    coord = np.arange(96, dtype=np.int64)
    order = np.lexsort((coord, -dispersion)).astype(np.int64)
    thresholds = np.median(absC, axis=0)
    if len(set(order.tolist())) != 96:
        raise RuntimeError("residual coordinate order is not a permutation")
    if not np.isfinite(dispersion).all() or not np.isfinite(thresholds).all():
        raise RuntimeError("nonfinite residual specification")
    return order, thresholds, dispersion


def make_residual_bits(X: np.ndarray, order: np.ndarray, thresholds: np.ndarray, r: int) -> np.ndarray:
    if r == 0:
        return np.zeros((len(X), 0), dtype=bool)
    cols = order[:r]
    return np.abs(np.asarray(X)[:, cols]) >= thresholds[cols][None, :]


def collision_stats(sign_bits: np.ndarray, residual_bits: np.ndarray) -> dict[str, float | int]:
    full = np.concatenate([sign_bits, residual_bits], axis=1)
    packed = np.packbits(full.astype(np.uint8), axis=1, bitorder="little")
    _, counts = np.unique(packed, axis=0, return_counts=True)
    collided = counts[counts > 1]
    docs_in_collision = int(collided.sum()) if len(collided) else 0
    collision_pairs = int(np.sum(collided * (collided - 1) // 2)) if len(collided) else 0
    return {
        "active_bits": int(full.shape[1]),
        "min_byte_aligned_packed_bytes": int(math.ceil(full.shape[1] / 8)),
        "unique_codes": int(len(counts)),
        "docs_in_nonunique_codes": docs_in_collision,
        "doc_collision_fraction": float(docs_in_collision / len(full)),
        "collision_pairs": collision_pairs,
        "max_bucket_size": int(counts.max()) if len(counts) else 0,
    }


def boundary_tie_pair(base_hd: np.ndarray, residual_hd: np.ndarray, k: int = 3) -> tuple[bool, int]:
    n = len(base_hd)
    if n == 0:
        return False, 0
    kk = min(k, n)
    order = np.lexsort((residual_hd, base_hd))
    idx = int(order[kk - 1])
    b = int(base_hd[idx])
    r = int(residual_hd[idx])
    less = (base_hd < b) | ((base_hd == b) & (residual_hd < r))
    equal = (base_hd == b) & (residual_hd == r)
    before = int(np.sum(less))
    at = int(np.sum(equal))
    tied = at > (kk - before)
    return tied, at


def freeze_rankings(B, task: str, doc_ids: list[str], query_ids: list[str], C: np.ndarray,
                    signD: np.ndarray, qC: np.ndarray, signQ: np.ndarray,
                    doc_res: dict[int, np.ndarray], query_res: dict[int, np.ndarray]):
    n_q = len(query_ids)
    k = min(B.MAX_K, len(doc_ids))
    float_top = np.empty((B.N_NUISANCE, n_q, k), dtype=np.int32)
    variant_top = {r: np.empty((B.N_NUISANCE, n_q, k), dtype=np.int32) for r in BUDGETS}
    tie_flags = {r: np.zeros(n_q, dtype=bool) for r in BUDGETS}
    tie_groups = {r: np.zeros(n_q, dtype=np.int32) for r in BUDGETS}

    for qi, qid in enumerate(query_ids):
        fs = B.cosine_centered(C, qC[qi])
        base_hd = np.count_nonzero(signD != signQ[qi][None, :], axis=1).astype(np.int16)
        if not np.isfinite(fs).all():
            raise RuntimeError(f"{qid}: nonfinite FLOAT96 score")

        rhds: dict[int, np.ndarray] = {0: np.zeros(len(doc_ids), dtype=np.int16)}
        for r in BUDGETS[1:]:
            rhds[r] = np.count_nonzero(doc_res[r] != query_res[r][qi][None, :], axis=1).astype(np.int16)

        for r in BUDGETS:
            tied, group = boundary_tie_pair(base_hd, rhds[r], k=3)
            tie_flags[r][qi] = tied
            tie_groups[r][qi] = group

        for trial in range(B.N_NUISANCE):
            pri = B.deterministic_priority(task, qid, trial, doc_ids)
            float_top[trial, qi] = np.lexsort((pri, -fs))[:k]
            for r in BUDGETS:
                # Lexicographic: base SIGN96 Hamming first, residual Hamming second.
                variant_top[r][trial, qi] = np.lexsort((pri, rhds[r], base_hd))[:k]

        if (qi + 1) % 100 == 0 or qi + 1 == n_q:
            print(json.dumps({"progress_queries": qi + 1, "total_queries": n_q, "task": task}), flush=True)

    return float_top, variant_top, tie_flags, tie_groups


def bootstrap_ci(B, values: np.ndarray, seed: int) -> list[float]:
    return B.bootstrap_ci(np.asarray(values, dtype=np.float64), seed)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]
    B = load_base(repo_root)
    if args.task not in B.TASKS:
        raise RuntimeError(f"unknown task {args.task}")
    task = args.task

    adapter, adapter_sha, t4c2_sha = B.load_frozen_adapter(repo_root)
    revision = B.HfApi().dataset_info(B.DATASET_ID).sha

    # OUTCOME-BLIND: corpus and queries only.
    corpus_ds = B.load_dataset(B.DATASET_ID, "corpus", split=task, revision=revision)
    queries_ds = B.load_dataset(B.DATASET_ID, "queries", split=task, revision=revision)
    doc_ids = [str(x["_id"]) for x in corpus_ds]
    corpus_texts = [str(x["text"]) for x in corpus_ds]
    query_ids = [str(x["_id"]) for x in queries_ds]
    query_texts = [str(x["text"]) for x in queries_ds]
    if len(set(doc_ids)) != len(doc_ids) or len(set(query_ids)) != len(query_ids):
        raise RuntimeError("duplicate IDs")

    t0 = time.perf_counter()
    rep = B.build_repr(adapter, corpus_texts)
    _, qC, signQ, query_seconds = B.transform_queries(rep, query_texts)
    order, thresholds, dispersion = residual_spec(rep["C"])

    doc_res = {r: make_residual_bits(rep["C"], order, thresholds, r) for r in BUDGETS}
    query_res = {r: make_residual_bits(qC, order, thresholds, r) for r in BUDGETS}
    collisions = {str(r): collision_stats(rep["signD"], doc_res[r]) for r in BUDGETS}

    # Adding residual bits may split codes but may never merge previously distinct full codes.
    uniques = [int(collisions[str(r)]["unique_codes"]) for r in BUDGETS]
    if uniques != sorted(uniques):
        raise RuntimeError(f"code uniqueness is not monotone: {uniques}")

    float_top, variant_top, tie_flags, tie_groups = freeze_rankings(
        B, task, doc_ids, query_ids, rep["C"], rep["signD"], qC, signQ, doc_res, query_res
    )

    # Freeze rankings to disk BEFORE qrels access.
    freeze_path = args.outdir / f"{task}.pre_qrels_rankings.npz"
    np.savez_compressed(
        freeze_path,
        float_top=float_top,
        sign96=variant_top[0],
        sign96_r4=variant_top[4],
        sign96_r8=variant_top[8],
        sign96_r16=variant_top[16],
        residual_order=order,
        residual_thresholds=thresholds,
    )
    freeze_sha = B.sha256_file(freeze_path)
    pre_manifest = {
        "label": LABEL,
        "task": task,
        "dataset_revision": revision,
        "documents": len(doc_ids),
        "queries": len(query_ids),
        "qrels_opened": False,
        "rankings_sha256": freeze_sha,
        "primary_budget_extra_bits": PRIMARY_BUDGET,
        "ranking_rule": "lexicographic(base_SIGN96_Hamming, residual_Hamming, relevance-independent SHA256 priority)",
        "residual_rule": "top corpus-only Var(abs(C_j)) coordinates; bit=abs(value)>=corpus median",
        "selected_16_coordinates": [int(x) for x in order[:16]],
        "selected_16_dispersion": [float(dispersion[int(x)]) for x in order[:16]],
        "timestamp_unix": time.time(),
    }
    manifest_path = args.outdir / f"{task}.pre_qrels_manifest.json"
    manifest_path.write_text(json.dumps(pre_manifest, indent=2), encoding="utf-8")
    print(json.dumps({"PRE_QRELS_FREEZE": pre_manifest}), flush=True)

    # Only now may relevance labels enter.
    qrels_ds = B.load_dataset(B.DATASET_ID, "qrels", split=task, revision=revision)
    doc_index = {d: i for i, d in enumerate(doc_ids)}
    qrels: dict[str, set[int]] = {q: set() for q in query_ids}
    unknown = []
    for row in qrels_ds:
        qid = str(row["query-id"])
        did = str(row["corpus-id"])
        if qid not in qrels or did not in doc_index:
            unknown.append((qid, did))
        else:
            qrels[qid].add(doc_index[did])
    if unknown:
        raise RuntimeError(f"unmapped qrels: {unknown[:3]}")
    zero = [q for q, s in qrels.items() if not s]
    if zero:
        raise RuntimeError(f"zero-gold queries: {zero[:5]}")

    n_q = len(query_ids)
    float_metrics = {m: np.zeros((B.N_NUISANCE, n_q), dtype=np.float64) for m in METRICS}
    variant_metrics = {
        r: {m: np.zeros((B.N_NUISANCE, n_q), dtype=np.float64) for m in METRICS}
        for r in BUDGETS
    }

    for trial in range(B.N_NUISANCE):
        for qi, qid in enumerate(query_ids):
            fm = B.metric_block(float_top[trial, qi], qrels[qid])
            for m in METRICS:
                float_metrics[m][trial, qi] = fm[m]
            for r in BUDGETS:
                vm = B.metric_block(variant_top[r][trial, qi], qrels[qid])
                for m in METRICS:
                    variant_metrics[r][m][trial, qi] = vm[m]

    methods: dict[str, dict] = {}
    float_ag = {m: float(float_metrics[m].mean()) for m in METRICS}
    methods["FLOAT96"] = {
        "active_bits": 3072,
        "note": "96 float32 coordinates for comparison; not an active-code packing claim",
        "metrics": float_ag,
    }

    for r in BUDGETS:
        name = "SIGN96" if r == 0 else f"SIGN96_R{r}"
        metrics = {}
        for m in METRICS:
            v = variant_metrics[r][m]
            f = float_metrics[m]
            s0 = variant_metrics[0][m]
            qv = v.mean(axis=0)
            qf = f.mean(axis=0)
            qs0 = s0.mean(axis=0)
            dfloat = qv - qf
            dbase = qv - qs0
            seed_base = 260914 + sum(ord(c) for c in (task + name + m))
            metrics[m] = {
                "value": float(v.mean()),
                "delta_vs_float": float(dfloat.mean()),
                "delta_vs_float_pp": float(dfloat.mean() * 100.0),
                "delta_vs_sign96": float(dbase.mean()),
                "delta_vs_sign96_pp": float(dbase.mean() * 100.0),
                "paired_query_bootstrap_95ci_vs_float": bootstrap_ci(B, dfloat, seed_base),
                "paired_query_bootstrap_95ci_vs_sign96": bootstrap_ci(B, dbase, seed_base + 17),
            }
        methods[name] = {
            "extra_residual_bits": r,
            "active_bits": 96 + r,
            "min_byte_aligned_packed_bytes": int(math.ceil((96 + r) / 8)),
            "collision": collisions[str(r)],
            "top3_boundary_tie_rate": float(tie_flags[r].mean()),
            "median_top3_boundary_tie_group": float(np.median(tie_groups[r])),
            "metrics": metrics,
        }

    query_rows = []
    for qi, qid in enumerate(query_ids):
        row = {
            "query_id": qid,
            "gold_count": len(qrels[qid]),
            "float_recall@3": float(float_metrics["recall@3"][:, qi].mean()),
        }
        for r in BUDGETS:
            name = "sign96" if r == 0 else f"sign96_r{r}"
            rv = float(variant_metrics[r]["recall@3"][:, qi].mean())
            row[f"{name}_recall@3"] = rv
            row[f"{name}_delta_vs_float_recall@3"] = rv - row["float_recall@3"]
            row[f"{name}_top3_boundary_tied"] = bool(tie_flags[r][qi])
        query_rows.append(row)

    result = {
        "label": LABEL,
        "schema": "LLMZIP_SIGN96_MICRO_RESIDUAL_NANOBEIR_V1",
        "task": task,
        "dataset": {
            "id": B.DATASET_ID,
            "revision": revision,
            "n_docs": len(doc_ids),
            "n_queries": len(query_ids),
            "n_qrels": len(qrels_ds),
        },
        "source_bindings": {
            "adapter_sha256": adapter_sha,
            "t4c2_script_sha256": t4c2_sha,
            "base_nanobeir_runner_sha256": B.sha256_file(repo_root / "benchmarks" / "sign96_nanobeir_2026_09_14" / "run_nanobeir.py"),
        },
        "protocol": {
            "primary_method": "SIGN96_R8",
            "primary_endpoint": "task-macro Recall@3 improvement vs SIGN96 across frozen 13-task wave",
            "qrels_access": "only after all method rankings are written and SHA-256 frozen",
            "residual_fit": "corpus only; no queries or qrels",
            "residual_selector": "decreasing Var(abs(centered_coordinate))",
            "residual_threshold": "per-coordinate corpus median abs(centered_coordinate)",
            "ranking": "lexicographic base Hamming, residual Hamming, nuisance priority",
            "nuisance_trials": B.N_NUISANCE,
            "active_code_warning": "bit/byte figures exclude shared projector/vectorizer/index state",
        },
        "residual_spec": {
            "coordinate_order": [int(x) for x in order.tolist()],
            "thresholds": [float(x) for x in thresholds.tolist()],
            "dispersion": [float(x) for x in dispersion.tolist()],
        },
        "pre_qrels_rankings_sha256": freeze_sha,
        "methods": methods,
        "timing": {
            "representation_fit_seconds": float(rep["fit_seconds"]),
            "query_transform_seconds": float(query_seconds),
            "total_seconds": float(time.perf_counter() - t0),
        },
        "package_versions": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "interpretation_boundary": (
            "Exploratory label-free tie-resolution test. Not Task4F1, not whole-system storage proof, "
            "not novelty proof, and not external independent reproduction."
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
        "float_recall@3": float_ag["recall@3"],
        "sign96_delta_vs_float_pp": methods["SIGN96"]["metrics"]["recall@3"]["delta_vs_float_pp"],
        "r4_delta_vs_sign96_pp": methods["SIGN96_R4"]["metrics"]["recall@3"]["delta_vs_sign96_pp"],
        "r8_delta_vs_sign96_pp": methods["SIGN96_R8"]["metrics"]["recall@3"]["delta_vs_sign96_pp"],
        "r16_delta_vs_sign96_pp": methods["SIGN96_R16"]["metrics"]["recall@3"]["delta_vs_sign96_pp"],
        "sign96_collision_fraction": methods["SIGN96"]["collision"]["doc_collision_fraction"],
        "r8_collision_fraction": methods["SIGN96_R8"]["collision"]["doc_collision_fraction"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
