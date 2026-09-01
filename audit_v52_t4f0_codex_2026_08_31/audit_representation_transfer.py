#!/usr/bin/env python3
"""Real-data audit of the frozen V52 representation family.

The script computes representation shape/integrity only.  It contains no
binary code construction, ranking, Native/Haar comparison, or retrieval metric.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import psutil
import scipy
import sklearn
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


TIERS = ("100K", "500K", "1M", "10M")
LATENT_DIM = 32
LATENT_SEED = 5101
MIXED_DIM = 96
MIXED_SEED = 5204
CANARY_QUERY = "audit canary text for deterministic post-fit transform"


def iter_messages(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if {"role", "id", "content"}.issubset(value):
            yield value
            return
        for child in value.values():
            yield from iter_messages(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_messages(child)


class PeakMemoryMonitor:
    def __init__(self, interval: float = 0.05) -> None:
        self.interval = interval
        self.peak_rss = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        process = psutil.Process()
        while not self._stop.is_set():
            self.peak_rss = max(self.peak_rss, process.memory_info().rss)
            self._stop.wait(self.interval)

    def __enter__(self) -> "PeakMemoryMonitor":
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join()
        self.peak_rss = max(self.peak_rss, psutil.Process().memory_info().rss)


def timed(stage_times: dict[str, float], name: str, function, *args):
    started = time.perf_counter()
    result = function(*args)
    stage_times[name] = time.perf_counter() - started
    print(f"  {name}: {stage_times[name]:.3f}s", flush=True)
    return result


def load_memory_texts(chat_path: Path) -> list[str]:
    chat = json.loads(chat_path.read_text(encoding="utf-8"))
    texts: list[str] = []
    for message in iter_messages(chat):
        role = message.get("role")
        content = message.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            raise ValueError(f"invalid message payload role={role!r} content={type(content).__name__}")
        texts.append(f"{role}: {content}")
    return texts


def fit_once(memory_texts: list[str]) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    if len(memory_texts) < 98:
        raise ValueError("mixed96 rank precondition requires at least 98 archive units")
    stage_times: dict[str, float] = {}
    started = time.perf_counter()
    with PeakMemoryMonitor() as memory:
        word_vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )
        char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            sublinear_tf=True,
        )
        x_word = timed(stage_times, "word_tfidf_fit_transform", word_vectorizer.fit_transform, memory_texts)
        x_word = timed(stage_times, "word_l2_normalize", normalize, x_word)
        x_char = timed(stage_times, "char_tfidf_fit_transform", char_vectorizer.fit_transform, memory_texts)
        x_char = timed(stage_times, "char_l2_normalize", normalize, x_char)
        if min(x_word.shape[0] - 1, x_word.shape[1] - 1) < LATENT_DIM:
            raise ValueError(f"latent32 rank precondition fails for {x_word.shape}")
        latent_svd = TruncatedSVD(n_components=LATENT_DIM, random_state=LATENT_SEED)
        x_latent = timed(stage_times, "latent32_fit_transform", latent_svd.fit_transform, x_word)
        x_latent = timed(stage_times, "latent32_l2_normalize", normalize, x_latent)
        z_source = timed(
            stage_times,
            "source_block_hstack",
            sparse.hstack,
            [sparse.csr_matrix(x_latent), x_word, x_char],
            "csr",
        )
        if z_source.shape[0] <= MIXED_DIM or z_source.shape[1] < MIXED_DIM:
            raise ValueError(f"mixed96 rank precondition fails for {z_source.shape}")
        mixed_svd = TruncatedSVD(n_components=MIXED_DIM, random_state=MIXED_SEED)
        y96 = timed(stage_times, "mixed96_fit_transform", mixed_svd.fit_transform, z_source)
        y96 = timed(stage_times, "mixed96_l2_normalize", normalize, y96)
        mean96 = y96.mean(axis=0, keepdims=True)
        centered96 = np.asarray(y96 - mean96, dtype=np.float64)

        q_word = word_vectorizer.transform([CANARY_QUERY])
        q_word = normalize(q_word)
        q_char = char_vectorizer.transform([CANARY_QUERY])
        q_char = normalize(q_char)
        q_latent = normalize(latent_svd.transform(q_word))
        q_source = sparse.hstack([sparse.csr_matrix(q_latent), q_word, q_char], format="csr")
        q_y96 = normalize(mixed_svd.transform(q_source))
        q_centered96 = np.asarray(q_y96 - mean96, dtype=np.float64)

        finite = bool(np.isfinite(centered96).all() and np.isfinite(q_centered96).all())
        rank = int(np.linalg.matrix_rank(np.asarray(y96, dtype=np.float64)))
        metrics = {
            "archive_units": len(memory_texts),
            "word_shape": list(x_word.shape),
            "word_nnz": int(x_word.nnz),
            "char_shape": list(x_char.shape),
            "char_nnz": int(x_char.nnz),
            "latent_shape": list(x_latent.shape),
            "source_block_shape": list(z_source.shape),
            "source_block_nnz": int(z_source.nnz),
            "mixed_shape": list(centered96.shape),
            "query_shape": list(q_centered96.shape),
            "mixed_rank": rank,
            "finite_no_nan_inf": finite,
            "centered96_sha256": hashlib.sha256(
                np.ascontiguousarray(centered96).tobytes()
            ).hexdigest(),
            "query_centered96_sha256": hashlib.sha256(
                np.ascontiguousarray(q_centered96).tobytes()
            ).hexdigest(),
            "peak_rss_bytes": memory.peak_rss,
            "total_seconds": time.perf_counter() - started,
            "stage_seconds": stage_times,
        }
    return metrics, centered96, q_centered96


def run_tier(corpus: Path, tier: str, conversation_id: str, repeats: int) -> dict[str, Any]:
    chat_path = corpus / "chats" / tier / conversation_id / "chat.json"
    if not chat_path.is_file():
        raise FileNotFoundError(chat_path)
    load_started = time.perf_counter()
    texts = load_memory_texts(chat_path)
    load_seconds = time.perf_counter() - load_started
    print(f"{tier}/{conversation_id}: {len(texts)} messages; load={load_seconds:.3f}s", flush=True)

    print(" repeat 1", flush=True)
    first_metrics, first_archive, first_query = fit_once(texts)
    second_metrics = None
    archive_diff = None
    query_diff = None
    if repeats == 2:
        gc.collect()
        print(" repeat 2", flush=True)
        second_metrics, second_archive, second_query = fit_once(texts)
        archive_diff = float(np.max(np.abs(first_archive - second_archive)))
        query_diff = float(np.max(np.abs(first_query - second_query)))
    result = {
        "status": "PASS"
        if (
            first_metrics["mixed_shape"] == [len(texts), MIXED_DIM]
            and first_metrics["mixed_rank"] == MIXED_DIM
            and first_metrics["finite_no_nan_inf"]
            and (archive_diff is None or archive_diff <= 1e-12)
            and (query_diff is None or query_diff <= 1e-12)
        )
        else "FAIL",
        "tier": tier,
        "conversation_id": conversation_id,
        "chat_path": chat_path.as_posix(),
        "load_seconds": load_seconds,
        "repeat_1": first_metrics,
        "repeat_2": second_metrics,
        "repeatability_max_abs_archive_diff": archive_diff,
        "repeatability_max_abs_query_diff": query_diff,
        "retrieval_quality_computed": False,
    }
    del first_archive, first_query, texts
    if repeats == 2:
        del second_archive, second_query
    gc.collect()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--conversation-id", default="1")
    parser.add_argument("--repeats", type=int, choices=(1, 2), default=2)
    parser.add_argument("--tiers", nargs="+", choices=TIERS, default=list(TIERS))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "task": "V52 TASK 4F0 - REAL BEAM REPRESENTATION TRANSFER AUDIT",
        "method": {
            "memory_text": "role + ': ' + content",
            "word_tfidf": {"lowercase": True, "ngram_range": [1, 2], "stop_words": "english", "sublinear_tf": True},
            "char_tfidf": {"analyzer": "char_wb", "ngram_range": [3, 5], "sublinear_tf": True},
            "latent_svd": {"n_components": LATENT_DIM, "random_state": LATENT_SEED},
            "mixed_svd": {"n_components": MIXED_DIM, "random_state": MIXED_SEED},
            "l2_normalize": True,
            "archive_mean_center": True,
            "query_fit_rule": "transform only after archive fit",
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "psutil": psutil.__version__,
            "thread_environment": {
                name: os.environ.get(name)
                for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")
            },
        },
        "scientific_native_vs_haar_outcome_inspected": False,
        "tiers": {},
    }
    for tier in args.tiers:
        try:
            payload["tiers"][tier] = run_tier(
                args.corpus, tier, args.conversation_id, args.repeats
            )
        except Exception as exc:
            payload["tiers"][tier] = {
                "status": "FAIL",
                "tier": tier,
                "conversation_id": args.conversation_id,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "retrieval_quality_computed": False,
            }
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if any(row["status"] != "PASS" for row in payload["tiers"].values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
