#!/usr/bin/env python3
"""Guarded V52 Task 4F1 BEAM retrieval implementation.

The preflight mode is outcome-free.  The run/finalize modes refuse to execute
without a separate Head Researcher authorization that binds these exact script
bytes and the independently accepted execution-candidate seal.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import os
import platform
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import psutil
import scipy
import sklearn
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


TASK = "V52 Task 4F1 - BEAM Restricted-Cohort Axis Probe"
SCRIPT_NAME = "v52_t4f1_beam_retrieval.py"
EXPECTED_PARENT_COMMIT = "d3c7aa09c9553cd5ac100e668923abab602e4257"
EXPECTED_BEAM_COMMIT = "3e12035532eb85768f1a7cd779832b650c4b2ef9"
EXPECTED_COHORT_SHA256 = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"
EXPECTED_RESTRICTED_SEAL_SHA256 = "596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c"
EXPECTED_PROTOCOL_SHA256 = "f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1"
EXPECTED_DEPENDENCY_LOCK_SHA256 = "86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e"
EXPECTED_BEAM_MANIFEST_SHA256 = "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318"

EXPECTED_TOTAL_ROWS = 2000
EXPECTED_ELIGIBLE = 1712
EXPECTED_ARCHIVES = 96
EXCLUDED_ARCHIVES = frozenset({"1M::5", "1M::26", "1M::33", "1M::34"})
TIERS = ("100K", "500K", "1M", "10M")

LATENT_DIM = 32
LATENT_SEED = 5101
MIXED_DIM = 96
MIXED_SEED = 5204
TOP_K = 3
HAAR_SEEDS = (43001, 43002, 43003, 43004, 43005)
SIGNED_PERM_SEEDS = HAAR_SEEDS
ITQ_SEEDS = (101, 202, 303, 404, 505)
ITQ_ITERATIONS = 100
NUISANCE_TRIALS = tuple(range(20))
INVARIANCE_TOLERANCE = 1e-12
TIE_PREFIX = b"V52_T4F0_TIE_PRIORITY_V1"
REAL_CANARY_QUERY = "Which project phase mentioned module 7 and a deadline?"
EXPECTED_REAL_CANARY_ARCHIVE_SHA256 = "25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025"
EXPECTED_REAL_CANARY_QUERY_SHA256 = "e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869"
AUTH_HMAC_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"
AUTH_SCHEMA = "V52_T4F1_RUN_AUTHORIZATION_V2"
AUTH_SIGNED_FIELDS = (
    "schema",
    "status",
    "retrieval_quality_outcome_access",
    "execution_script_sha256",
    "execution_candidate_seal_sha256",
    "cohort_sha256",
    "required_archive_count",
    "output_namespace_basename",
    "preregistration_seal_sha256",
    "authorization_id",
    "authorization_nonce",
)

ENVIRONMENT_LOCK = {
    "python": "3.12.13",
    "numpy": "2.3.2",
    "scipy": "1.16.1",
    "scikit_learn": "1.7.1",
    "psutil": "7.0.0",
}
THREAD_LOCK = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
}

TRIAL_FIELDS = (
    "audit_question_id",
    "tier",
    "conversation_id",
    "ability",
    "method",
    "seed",
    "trial",
    "archive_units",
    "gold_count",
    "retrieved_top3_ids",
    "top3_distances",
    "fractional_source_evidence_recall_at_3",
    "any_at_3",
    "all_at_3",
)


def sha256_file(path: Path, chunk_size: int = 8 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value))


def verify_environment() -> dict[str, Any]:
    observed = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "psutil": psutil.__version__,
    }
    mismatches = {
        name: {"expected": expected, "observed": observed[name]}
        for name, expected in ENVIRONMENT_LOCK.items()
        if observed[name] != expected
    }
    thread_mismatches = {
        name: {"expected": expected, "observed": os.environ.get(name)}
        for name, expected in THREAD_LOCK.items()
        if os.environ.get(name) != expected
    }
    if mismatches or thread_mismatches:
        raise RuntimeError(
            "[BLOCKED - ENVIRONMENT LOCK MISMATCH] "
            + json.dumps({"versions": mismatches, "thread_environment": thread_mismatches}, sort_keys=True)
        )
    return {"versions": observed, "thread_environment": dict(THREAD_LOCK)}


def verify_bound_file(path: Path, expected_sha256: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"[BLOCKED - MISSING BOUND FILE] {label}: {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise RuntimeError(f"[BLOCKED - HASH MISMATCH] {label}: {observed} != {expected_sha256}")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": observed}


def verify_execution_seal(path: Path, script_path: Path) -> tuple[dict[str, Any], str]:
    seal = json.loads(path.read_text(encoding="utf-8"))
    if seal.get("schema") != "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V2":
        raise RuntimeError("[BLOCKED - EXECUTION SEAL SCHEMA]")
    expected_script_hash = seal.get("implementation", {}).get("sha256")
    actual_script_hash = sha256_file(script_path)
    if expected_script_hash != actual_script_hash:
        raise RuntimeError(
            f"[BLOCKED - SCRIPT BYTE MISMATCH] {actual_script_hash} != {expected_script_hash}"
        )
    if seal.get("authorization", {}).get("task_4f1_run") != "BLOCKED":
        raise RuntimeError("[BLOCKED - CANDIDATE SEAL MUST NOT AUTHORIZE RUN]")
    control = seal.get("authorization_control", {})
    if (
        control.get("scheme") != "HMAC-SHA256"
        or control.get("key_environment_variable") != AUTH_HMAC_ENV
        or tuple(control.get("signed_fields", ())) != AUTH_SIGNED_FIELDS
    ):
        raise RuntimeError("[BLOCKED - AUTHORIZATION CONTROL BINDING]")
    return seal, sha256_file(path)


def verify_run_authorization(
    path: Path,
    script_path: Path,
    execution_seal_path: Path,
    cohort_path: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], str]:
    authorization_bytes = path.read_bytes()
    authorization = json.loads(authorization_bytes.decode("utf-8"))
    execution_seal = json.loads(execution_seal_path.read_text(encoding="utf-8"))
    required = {
        "schema": AUTH_SCHEMA,
        "status": "AUTHORIZED_FOR_TASK_4F1_EXECUTION",
        "retrieval_quality_outcome_access": "AUTHORIZED",
        "execution_script_sha256": sha256_file(script_path),
        "execution_candidate_seal_sha256": sha256_file(execution_seal_path),
        "cohort_sha256": sha256_file(cohort_path),
        "required_archive_count": EXPECTED_ARCHIVES,
        "output_namespace_basename": output_dir.name,
    }
    mismatches = {
        key: {"expected": value, "observed": authorization.get(key)}
        for key, value in required.items()
        if authorization.get(key) != value
    }
    if mismatches:
        raise RuntimeError("[BLOCKED - INVALID RUN AUTHORIZATION] " + json.dumps(mismatches, sort_keys=True))
    exact_keys = set(AUTH_SIGNED_FIELDS) | {"authorization_hmac_sha256"}
    if set(authorization) != exact_keys:
        raise RuntimeError("[BLOCKED - AUTHORIZATION FIELD SET]")
    for field in ("preregistration_seal_sha256", "authorization_nonce"):
        value = authorization.get(field)
        if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
            raise RuntimeError(f"[BLOCKED - INVALID AUTHORIZATION {field.upper()}]")
    authorization_id = authorization.get("authorization_id")
    if not isinstance(authorization_id, str) or not authorization_id.startswith("V52-T4F1-"):
        raise RuntimeError("[BLOCKED - INVALID AUTHORIZATION ID]")
    control = execution_seal.get("authorization_control", {})
    commitment = control.get("key_commitment_sha256")
    if not isinstance(commitment, str) or len(commitment) != 64 or any(
        character not in "0123456789abcdef" for character in commitment
    ):
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY NOT SEALED]")
    secret_hex = os.environ.get(AUTH_HMAC_ENV)
    if secret_hex is None:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY MISSING]")
    try:
        secret = bytes.fromhex(secret_hex)
    except ValueError as exc:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY FORMAT]") from exc
    if len(secret) != 32 or hashlib.sha256(secret).hexdigest() != commitment:
        raise RuntimeError("[BLOCKED - HEAD RESEARCHER AUTHORITY KEY MISMATCH]")
    signed_payload = {field: authorization[field] for field in AUTH_SIGNED_FIELDS}
    expected_hmac = hmac.new(secret, canonical_json_bytes(signed_payload), hashlib.sha256).hexdigest()
    observed_hmac = authorization.get("authorization_hmac_sha256")
    if not isinstance(observed_hmac, str) or not hmac.compare_digest(observed_hmac, expected_hmac):
        raise RuntimeError("[BLOCKED - INVALID AUTHORIZATION HMAC]")
    return authorization, hashlib.sha256(authorization_bytes).hexdigest()


def parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"invalid frozen boolean {value!r}")


def load_and_verify_cohort(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    verify_bound_file(path, EXPECTED_COHORT_SHA256, "restricted cohort")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(f"[BLOCKED - COHORT ROW COUNT] {len(rows)} != {EXPECTED_TOTAL_ROWS}")
    identifiers = [row["audit_question_id"] for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise RuntimeError("[BLOCKED - DUPLICATE AUDIT QUESTION ID]")
    eligible: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        is_eligible = parse_bool(row["primary_evidence_cohort_eligible"])
        archive_id = f"{row['tier']}::{row['conversation_id']}"
        if is_eligible:
            gold = json.loads(row["gold_source_ids"])
            if (
                row["audit_category"] != "EXACT_SOURCE_IDS"
                or row["ability"] == "abstention"
                or archive_id in EXCLUDED_ARCHIVES
                or not isinstance(gold, list)
                or len(gold) != int(row["gold_source_unit_count"])
                or not gold
            ):
                raise RuntimeError(f"[BLOCKED - COHORT SEMANTICS] {row['audit_question_id']}")
            row["gold_source_ids_parsed"] = gold
            eligible.append(row)
    if len(eligible) != EXPECTED_ELIGIBLE:
        raise RuntimeError(f"[BLOCKED - ELIGIBLE COUNT] {len(eligible)} != {EXPECTED_ELIGIBLE}")
    archive_ids = sorted({f"{row['tier']}::{row['conversation_id']}" for row in eligible})
    if len(archive_ids) != EXPECTED_ARCHIVES:
        raise RuntimeError(f"[BLOCKED - ARCHIVE COUNT] {len(archive_ids)} != {EXPECTED_ARCHIVES}")
    return eligible, {
        "total_rows": len(rows),
        "eligible_rows": len(eligible),
        "archive_count": len(archive_ids),
        "archive_ids": archive_ids,
    }


def archive_relative_paths(archive_id: str) -> tuple[str, str]:
    tier, conversation_id = archive_id.split("::", 1)
    base = f"chats/{tier}/{conversation_id}"
    return f"{base}/chat.json", f"{base}/probing_questions/probing_questions.json"


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def verify_beam_checkout(root: Path, archive_ids: Sequence[str], manifest_path: Path) -> dict[str, Any]:
    verify_bound_file(manifest_path, EXPECTED_BEAM_MANIFEST_SHA256, "accepted BEAM pinned-tree manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("commit") != EXPECTED_BEAM_COMMIT:
        raise RuntimeError(f"[BLOCKED - BEAM MANIFEST COMMIT] {manifest.get('commit')} != {EXPECTED_BEAM_COMMIT}")
    selected = {item["path"]: item for item in manifest.get("selected", [])}
    checked: list[dict[str, Any]] = []
    for archive_id in archive_ids:
        for relative in archive_relative_paths(archive_id):
            disk_path = root / Path(relative)
            if not disk_path.is_file():
                raise RuntimeError(f"[BLOCKED - MISSING BEAM FILE] {relative}")
            expected = selected.get(relative)
            if expected is None:
                raise RuntimeError(f"[BLOCKED - FILE ABSENT FROM PINNED MANIFEST] {relative}")
            payload = disk_path.read_bytes()
            actual_blob = git_blob_sha1(payload)
            if actual_blob != expected.get("git_blob_sha1") or len(payload) != expected.get("size"):
                raise RuntimeError(f"[BLOCKED - BEAM BLOB MISMATCH] {relative}")
            checked.append({"path": relative, "git_blob_sha1": actual_blob, "bytes": len(payload)})
    return {"commit": manifest["commit"], "files_checked": len(checked), "files": checked}


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


def canonical_raw_id(value: Any) -> str:
    if isinstance(value, bool):
        raise ValueError("boolean message id forbidden")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value.isdigit():
        return str(int(value))
    raise ValueError(f"non-canonical raw message id {value!r}")


def canonical_memory_key(tier: str, conversation_id: str, raw_message_id: str) -> str:
    return f"{tier}::{conversation_id}::{raw_message_id}"


def load_archive(chat_path: Path, tier: str, conversation_id: str) -> tuple[list[str], list[str], list[str]]:
    raw = json.loads(chat_path.read_text(encoding="utf-8"))
    raw_ids: list[str] = []
    memory_keys: list[str] = []
    memory_texts: list[str] = []
    for message in iter_messages(raw):
        role = message.get("role")
        content = message.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            raise RuntimeError("[BLOCKED - MALFORMED MESSAGE]")
        raw_id = canonical_raw_id(message.get("id"))
        raw_ids.append(raw_id)
        memory_keys.append(canonical_memory_key(tier, conversation_id, raw_id))
        memory_texts.append(f"{role}: {content}")
    if not memory_texts or len(set(raw_ids)) != len(raw_ids):
        raise RuntimeError(f"[BLOCKED - EMPTY OR DUPLICATE-ID ARCHIVE] {tier}::{conversation_id}")
    return raw_ids, memory_keys, memory_texts


def load_questions(path: Path) -> dict[str, list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("[BLOCKED - QUESTION ROOT SCHEMA]")
    out: dict[str, list[dict[str, Any]]] = {}
    for ability, values in raw.items():
        if not isinstance(ability, str) or not isinstance(values, list):
            raise RuntimeError("[BLOCKED - QUESTION ABILITY SCHEMA]")
        if not all(isinstance(value, dict) for value in values):
            raise RuntimeError("[BLOCKED - QUESTION RECORD SCHEMA]")
        out[ability] = values
    return out


def question_payload(row: dict[str, Any], questions: dict[str, list[dict[str, Any]]]) -> tuple[str, set[str]]:
    parts = row["audit_question_id"].split("::")
    if len(parts) != 4 or parts[0] != row["tier"] or parts[1] != row["conversation_id"] or parts[2] != row["ability"]:
        raise RuntimeError(f"[BLOCKED - QUESTION ID SCHEMA] {row['audit_question_id']}")
    index = int(parts[3]) - 1
    records = questions.get(row["ability"])
    if records is None or not 0 <= index < len(records):
        raise RuntimeError(f"[BLOCKED - QUESTION LOOKUP] {row['audit_question_id']}")
    question = records[index].get("question")
    if not isinstance(question, str) or not question:
        raise RuntimeError(f"[BLOCKED - QUESTION TEXT] {row['audit_question_id']}")
    gold = {canonical_raw_id(value) for value in row["gold_source_ids_parsed"]}
    if len(gold) != int(row["gold_source_unit_count"]):
        raise RuntimeError(f"[BLOCKED - GOLD CARDINALITY] {row['audit_question_id']}")
    return question, gold


@dataclass
class ArchiveRepresentation:
    word_vectorizer: TfidfVectorizer
    char_vectorizer: TfidfVectorizer
    latent_svd: TruncatedSVD
    mixed_svd: TruncatedSVD
    mean96: np.ndarray
    centered96: np.ndarray


def fit_archive_representation(memory_texts: list[str]) -> ArchiveRepresentation:
    """Fit only on ordered archive memory text; no query or label is accepted."""
    if len(memory_texts) < MIXED_DIM + 2:
        raise RuntimeError("[BLOCKED - ARCHIVE TOO SMALL FOR MIXED96]")
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
    x_word = normalize(word_vectorizer.fit_transform(memory_texts))
    x_char = normalize(char_vectorizer.fit_transform(memory_texts))
    if min(x_word.shape[0] - 1, x_word.shape[1] - 1) < LATENT_DIM:
        raise RuntimeError(f"[BLOCKED - LATENT32 PRECONDITION] {x_word.shape}")
    latent_svd = TruncatedSVD(n_components=LATENT_DIM, random_state=LATENT_SEED)
    x_latent = normalize(latent_svd.fit_transform(x_word))
    source = sparse.hstack([sparse.csr_matrix(x_latent), x_word, x_char], format="csr")
    if source.shape[0] <= MIXED_DIM or source.shape[1] < MIXED_DIM:
        raise RuntimeError(f"[BLOCKED - MIXED96 PRECONDITION] {source.shape}")
    mixed_svd = TruncatedSVD(n_components=MIXED_DIM, random_state=MIXED_SEED)
    y96 = normalize(mixed_svd.fit_transform(source))
    mean96 = np.asarray(y96.mean(axis=0, keepdims=True), dtype=np.float64)
    centered96 = np.asarray(y96 - mean96, dtype=np.float64)
    if centered96.shape != (len(memory_texts), MIXED_DIM) or not np.isfinite(centered96).all():
        raise RuntimeError("[BLOCKED - INVALID ARCHIVE REPRESENTATION]")
    if int(np.linalg.matrix_rank(np.asarray(y96, dtype=np.float64))) != MIXED_DIM:
        raise RuntimeError("[BLOCKED - MIXED96 RANK]")
    return ArchiveRepresentation(
        word_vectorizer=word_vectorizer,
        char_vectorizer=char_vectorizer,
        latent_svd=latent_svd,
        mixed_svd=mixed_svd,
        mean96=mean96,
        centered96=centered96,
    )


def transform_queries(model: ArchiveRepresentation, query_texts: Sequence[str]) -> np.ndarray:
    """Transform queries only after the archive-only model has been fitted."""
    q_word = normalize(model.word_vectorizer.transform(query_texts))
    q_char = normalize(model.char_vectorizer.transform(query_texts))
    q_latent = normalize(model.latent_svd.transform(q_word))
    q_source = sparse.hstack([sparse.csr_matrix(q_latent), q_word, q_char], format="csr")
    q_y96 = normalize(model.mixed_svd.transform(q_source))
    centered = np.asarray(q_y96 - model.mean96, dtype=np.float64)
    if centered.shape != (len(query_texts), MIXED_DIM) or not np.isfinite(centered).all():
        raise RuntimeError("[BLOCKED - INVALID QUERY REPRESENTATION]")
    return centered


def tie_priority(archive_id: str, memory_key: str) -> int:
    payload = TIE_PREFIX + b"\x00" + archive_id.encode("utf-8") + b"\x00" + memory_key.encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:16], "big", signed=False)


def priority_arrays(archive_id: str, memory_keys: Sequence[str]) -> tuple[np.ndarray, np.ndarray]:
    priorities = [tie_priority(archive_id, key) for key in memory_keys]
    high = np.asarray([value >> 64 for value in priorities], dtype=np.uint64)
    low = np.asarray([value & ((1 << 64) - 1) for value in priorities], dtype=np.uint64)
    return high, low


def rank_hamming(doc_codes: np.ndarray, query_code: np.ndarray, priority_hi: np.ndarray, priority_lo: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    distances = np.count_nonzero(doc_codes != query_code.reshape(1, -1), axis=1).astype(np.int16)
    canonical_order = np.arange(doc_codes.shape[0], dtype=np.int64)
    ranking = np.lexsort((canonical_order, priority_lo, priority_hi, distances))
    return ranking, distances


def signed_permutation(seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(MIXED_DIM)
    signs = rng.choice(np.asarray([-1.0, 1.0], dtype=np.float64), size=MIXED_DIM)
    return permutation, signs


def haar_rotation(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    gaussian = rng.normal(size=(MIXED_DIM, MIXED_DIM))
    q_matrix, r_matrix = np.linalg.qr(gaussian)
    diagonal_sign = np.sign(np.diag(r_matrix))
    diagonal_sign[diagonal_sign == 0] = 1.0
    rotation = np.asarray(q_matrix * diagonal_sign.reshape(1, -1), dtype=np.float64)
    error = float(np.max(np.abs(rotation.T @ rotation - np.eye(MIXED_DIM))))
    if error > INVARIANCE_TOLERANCE:
        raise RuntimeError(f"[BUG - NONORTHOGONAL HAAR] seed={seed} error={error}")
    return rotation


def fit_itq(centered_archive: np.ndarray, seed: int, iterations: int = ITQ_ITERATIONS) -> np.ndarray:
    """Canonical audited archive-only ITQ Procrustes iteration."""
    values = np.asarray(centered_archive, dtype=np.float64)
    rng = np.random.default_rng(seed)
    initial = rng.normal(size=(MIXED_DIM, MIXED_DIM))
    u_matrix, _, vt_matrix = np.linalg.svd(initial, full_matrices=False)
    rotation = u_matrix @ vt_matrix
    for _ in range(iterations):
        binary = np.where(values @ rotation >= 0, 1.0, -1.0)
        covariance = binary.T @ values
        u_matrix, _, vt_matrix = np.linalg.svd(covariance, full_matrices=False)
        rotation = vt_matrix.T @ u_matrix.T
    return np.asarray(rotation, dtype=np.float64)


def metrics_at_3(retrieved: Sequence[str], gold: set[str]) -> tuple[float, int, int]:
    retrieved_set = set(retrieved)
    hit_count = len(retrieved_set & gold)
    fractional = hit_count / len(gold)
    return float(fractional), int(hit_count > 0), int(gold.issubset(retrieved_set))


def append_trial_rows(
    rows: list[dict[str, Any]],
    cohort_row: dict[str, Any],
    method: str,
    seed: int | None,
    archive_units: int,
    raw_ids: Sequence[str],
    ranking: np.ndarray,
    distances: np.ndarray,
    gold: set[str],
) -> None:
    selected_indices = ranking[:TOP_K]
    retrieved = [raw_ids[int(index)] for index in selected_indices]
    selected_distances = [int(distances[int(index)]) for index in selected_indices]
    fractional, any_at_3, all_at_3 = metrics_at_3(retrieved, gold)
    base = {
        "audit_question_id": cohort_row["audit_question_id"],
        "tier": cohort_row["tier"],
        "conversation_id": cohort_row["conversation_id"],
        "ability": cohort_row["ability"],
        "method": method,
        "seed": "" if seed is None else seed,
        "archive_units": archive_units,
        "gold_count": len(gold),
        "retrieved_top3_ids": json.dumps(retrieved, separators=(",", ":")),
        "top3_distances": json.dumps(selected_distances, separators=(",", ":")),
        "fractional_source_evidence_recall_at_3": format(fractional, ".17g"),
        "any_at_3": any_at_3,
        "all_at_3": all_at_3,
    }
    # The sealed priority has no trial input.  Trials 0..19 are therefore
    # required deterministic replication identities and must be identical.
    for trial in NUISANCE_TRIALS:
        row = dict(base)
        row["trial"] = trial
        rows.append(row)


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def evaluate_archive(
    corpus_root: Path,
    archive_id: str,
    cohort_rows: Sequence[dict[str, Any]],
    provenance: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tier, conversation_id = archive_id.split("::", 1)
    chat_relative, question_relative = archive_relative_paths(archive_id)
    raw_ids, memory_keys, memory_texts = load_archive(corpus_root / chat_relative, tier, conversation_id)
    questions = load_questions(corpus_root / question_relative)
    queries: list[str] = []
    gold_sets: list[set[str]] = []
    archive_id_set = set(raw_ids)
    for row in cohort_rows:
        query, gold = question_payload(row, questions)
        if not gold.issubset(archive_id_set):
            raise RuntimeError(f"[BLOCKED - GOLD JOIN] {row['audit_question_id']}")
        queries.append(query)
        gold_sets.append(gold)

    started = time.perf_counter()
    model = fit_archive_representation(memory_texts)
    centered_archive = model.centered96
    centered_queries = transform_queries(model, queries)
    priority_hi, priority_lo = priority_arrays(archive_id, memory_keys)
    native_docs = centered_archive >= 0
    native_queries = centered_queries >= 0
    rows: list[dict[str, Any]] = []
    native_rankings: list[np.ndarray] = []
    native_distances: list[np.ndarray] = []

    for index, cohort_row in enumerate(cohort_rows):
        ranking, distances = rank_hamming(native_docs, native_queries[index], priority_hi, priority_lo)
        native_rankings.append(ranking)
        native_distances.append(distances)
        append_trial_rows(
            rows, cohort_row, "NATIVE_SIGN96", None, len(raw_ids), raw_ids, ranking, distances, gold_sets[index]
        )

    signed_control_checks = 0
    for seed in SIGNED_PERM_SEEDS:
        permutation, signs = signed_permutation(seed)
        signed_docs = (centered_archive[:, permutation] * signs) >= 0
        signed_queries = (centered_queries[:, permutation] * signs) >= 0
        for index, cohort_row in enumerate(cohort_rows):
            ranking, distances = rank_hamming(signed_docs, signed_queries[index], priority_hi, priority_lo)
            if not np.array_equal(distances, native_distances[index]) or not np.array_equal(ranking, native_rankings[index]):
                raise RuntimeError(
                    f"[BUG - HAMMING-INVARIANT CONTROL FAILED] {cohort_row['audit_question_id']} seed={seed}"
                )
            signed_control_checks += 1
            append_trial_rows(
                rows,
                cohort_row,
                "SIGNED_PERM_CONTROL96",
                seed,
                len(raw_ids),
                raw_ids,
                ranking,
                distances,
                gold_sets[index],
            )

    continuous_max_dot_diff = 0.0
    continuous_max_norm_diff = 0.0
    for seed in HAAR_SEEDS:
        rotation = haar_rotation(seed)
        rotated_docs_float = centered_archive @ rotation
        rotated_queries_float = centered_queries @ rotation
        doc_norm_difference = float(
            np.max(np.abs(np.linalg.norm(centered_archive, axis=1) - np.linalg.norm(rotated_docs_float, axis=1)))
        )
        query_norm_difference = float(
            np.max(np.abs(np.linalg.norm(centered_queries, axis=1) - np.linalg.norm(rotated_queries_float, axis=1)))
        )
        dot_difference = float(
            np.max(np.abs(centered_queries @ centered_archive.T - rotated_queries_float @ rotated_docs_float.T))
        )
        continuous_max_norm_diff = max(continuous_max_norm_diff, doc_norm_difference, query_norm_difference)
        continuous_max_dot_diff = max(continuous_max_dot_diff, dot_difference)
        if max(doc_norm_difference, query_norm_difference, dot_difference) > INVARIANCE_TOLERANCE:
            raise RuntimeError(f"[BUG - CONTINUOUS GEOMETRY NOT PRESERVED] {archive_id} seed={seed}")
        rotated_docs = rotated_docs_float >= 0
        rotated_queries = rotated_queries_float >= 0
        for index, cohort_row in enumerate(cohort_rows):
            ranking, distances = rank_hamming(rotated_docs, rotated_queries[index], priority_hi, priority_lo)
            append_trial_rows(
                rows,
                cohort_row,
                "HAAR96_SIGN",
                seed,
                len(raw_ids),
                raw_ids,
                ranking,
                distances,
                gold_sets[index],
            )

    for seed in ITQ_SEEDS:
        rotation = fit_itq(centered_archive, seed)
        itq_docs = (centered_archive @ rotation) >= 0
        itq_queries = (centered_queries @ rotation) >= 0
        for index, cohort_row in enumerate(cohort_rows):
            ranking, distances = rank_hamming(itq_docs, itq_queries[index], priority_hi, priority_lo)
            append_trial_rows(
                rows,
                cohort_row,
                "ITQ96_CENTERED",
                seed,
                len(raw_ids),
                raw_ids,
                ranking,
                distances,
                gold_sets[index],
            )

    expected_rows = len(cohort_rows) * 320
    if len(rows) != expected_rows:
        raise RuntimeError(f"[BUG - ARCHIVE TRIAL ROW COUNT] {len(rows)} != {expected_rows}")
    metadata = {
        "schema": "V52_T4F1_ARCHIVE_RESULT_META_V2",
        "archive_id": archive_id,
        "eligible_questions": len(cohort_rows),
        "archive_units": len(raw_ids),
        "trial_rows": len(rows),
        "signed_control_question_seed_checks": signed_control_checks,
        "continuous_max_abs_dot_diff": continuous_max_dot_diff,
        "continuous_max_abs_norm_diff": continuous_max_norm_diff,
        "centered_archive_sha256": array_sha256(centered_archive),
        "centered_queries_sha256": array_sha256(centered_queries),
        "peak_rss_bytes_at_completion": psutil.Process().memory_info().rss,
        "elapsed_seconds": time.perf_counter() - started,
        "outcomes_printed_to_console": False,
        "provenance": dict(provenance),
    }
    return rows, metadata


def write_archive_result(output_dir: Path, archive_id: str, rows: Sequence[dict[str, Any]], metadata: dict[str, Any]) -> None:
    safe_id = archive_id.replace("::", "__")
    csv_path = output_dir / "archives" / f"{safe_id}.csv"
    meta_path = output_dir / "archives" / f"{safe_id}.meta.json"
    if csv_path.exists() or meta_path.exists():
        raise RuntimeError(f"[BLOCKED - REFUSE ARCHIVE OVERWRITE] {archive_id}")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = csv_path.with_name(csv_path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRIAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, csv_path)
    metadata = dict(metadata)
    metadata["trial_csv"] = {
        "name": csv_path.name,
        "bytes": csv_path.stat().st_size,
        "sha256": sha256_file(csv_path),
    }
    write_json(meta_path, metadata)


def verify_existing_archive(
    output_dir: Path,
    archive_id: str,
    expected_questions: int,
    provenance: dict[str, str],
) -> bool:
    safe_id = archive_id.replace("::", "__")
    csv_path = output_dir / "archives" / f"{safe_id}.csv"
    meta_path = output_dir / "archives" / f"{safe_id}.meta.json"
    if not csv_path.exists() and not meta_path.exists():
        return False
    if not csv_path.is_file() or not meta_path.is_file():
        raise RuntimeError(f"[BLOCKED - INCOMPLETE ARCHIVE CHECKPOINT] {archive_id}")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    if (
        metadata.get("schema") != "V52_T4F1_ARCHIVE_RESULT_META_V2"
        or metadata.get("archive_id") != archive_id
        or metadata.get("eligible_questions") != expected_questions
        or metadata.get("trial_rows") != expected_questions * 320
        or metadata.get("signed_control_question_seed_checks") != expected_questions * len(SIGNED_PERM_SEEDS)
        or float(metadata.get("continuous_max_abs_dot_diff", float("inf"))) > INVARIANCE_TOLERANCE
        or float(metadata.get("continuous_max_abs_norm_diff", float("inf"))) > INVARIANCE_TOLERANCE
        or metadata.get("outcomes_printed_to_console") is not False
        or metadata.get("provenance") != provenance
        or metadata.get("trial_csv", {}).get("sha256") != sha256_file(csv_path)
        or metadata.get("trial_csv", {}).get("bytes") != csv_path.stat().st_size
    ):
        raise RuntimeError(f"[BLOCKED - ARCHIVE CHECKPOINT MISMATCH] {archive_id}")
    return True


def synthetic_preflight() -> dict[str, Any]:
    memory_texts = [
        f"user: synthetic archive document {index} token_{index} group_{index % 17} topic_{index % 11}"
        for index in range(128)
    ]
    model = fit_archive_representation(memory_texts)
    queries = transform_queries(model, ["synthetic topic query", "another group query"])
    archive_id = "100K::synthetic"
    memory_keys = [canonical_memory_key("100K", "synthetic", str(index)) for index in range(128)]
    priority_hi, priority_lo = priority_arrays(archive_id, memory_keys)
    native_docs = model.centered96 >= 0
    native_query = queries[0] >= 0
    native_rank, native_distance = rank_hamming(native_docs, native_query, priority_hi, priority_lo)
    signed_pass = True
    for seed in SIGNED_PERM_SEEDS:
        permutation, signs = signed_permutation(seed)
        docs = (model.centered96[:, permutation] * signs) >= 0
        query = (queries[0, permutation] * signs) >= 0
        ranking, distances = rank_hamming(docs, query, priority_hi, priority_lo)
        signed_pass = signed_pass and np.array_equal(ranking, native_rank) and np.array_equal(distances, native_distance)
    haar_max_error = 0.0
    for seed in HAAR_SEEDS:
        rotation = haar_rotation(seed)
        difference = float(
            np.max(np.abs(queries @ model.centered96.T - (queries @ rotation) @ (model.centered96 @ rotation).T))
        )
        haar_max_error = max(haar_max_error, difference)
    itq_orthogonality = []
    for seed in ITQ_SEEDS:
        rotation = fit_itq(model.centered96, seed)
        itq_orthogonality.append(float(np.max(np.abs(rotation.T @ rotation - np.eye(MIXED_DIM)))))
    structural_fractional, structural_any, structural_all = metrics_at_3(["1", "2", "3"], {"1", "2", "3", "4"})
    checks = {
        "representation_shape": list(model.centered96.shape),
        "query_shape": list(queries.shape),
        "finite": bool(np.isfinite(model.centered96).all() and np.isfinite(queries).all()),
        "rank96": int(np.linalg.matrix_rank(model.centered96 + model.mean96)) == MIXED_DIM,
        "signed_permutation_invariance": bool(signed_pass),
        "haar_max_abs_dot_diff": haar_max_error,
        "haar_invariance_pass": haar_max_error <= INVARIANCE_TOLERANCE,
        "itq_max_orthogonality_error": max(itq_orthogonality),
        "itq_orthogonality_pass": max(itq_orthogonality) <= INVARIANCE_TOLERANCE,
        "structural_zero_fixture": {
            "fractional": structural_fractional,
            "any": structural_any,
            "all": structural_all,
            "pass": structural_fractional == 0.75 and structural_any == 1 and structural_all == 0,
        },
        "tie_priority_trial_independent": True,
        "nuisance_trials": list(NUISANCE_TRIALS),
        "retrieval_quality_computed": False,
        "real_question_text_loaded": False,
        "gold_labels_loaded_by_synthetic_preflight": False,
    }
    blocking = [
        checks["representation_shape"] == [128, MIXED_DIM],
        checks["query_shape"] == [2, MIXED_DIM],
        checks["finite"],
        checks["rank96"],
        checks["signed_permutation_invariance"],
        checks["haar_invariance_pass"],
        checks["itq_orthogonality_pass"],
        checks["structural_zero_fixture"]["pass"],
    ]
    checks["status"] = "PASS" if all(blocking) else "FAIL"
    if checks["status"] != "PASS":
        raise RuntimeError("[BLOCKED - SYNTHETIC PREFLIGHT FAILURE]")
    return checks


def real_archive_canary(corpus_root: Path) -> dict[str, Any]:
    """Exercise the exact representation on raw 100K/12 bytes without labels."""
    raw_ids, _, memory_texts = load_archive(
        corpus_root / "chats" / "100K" / "12" / "chat.json",
        "100K",
        "12",
    )
    model = fit_archive_representation(memory_texts)
    query = transform_queries(model, [REAL_CANARY_QUERY])
    archive_digest = array_sha256(model.centered96)
    query_digest = array_sha256(query)
    checks = {
        "archive_id": "100K::12",
        "archive_units": len(raw_ids),
        "archive_shape": list(model.centered96.shape),
        "query_shape": list(query.shape),
        "archive_sha256": archive_digest,
        "query_sha256": query_digest,
        "expected_archive_sha256": EXPECTED_REAL_CANARY_ARCHIVE_SHA256,
        "expected_query_sha256": EXPECTED_REAL_CANARY_QUERY_SHA256,
        "question_file_opened": False,
        "gold_labels_loaded": False,
        "retrieval_quality_computed": False,
    }
    checks["status"] = "PASS" if (
        len(raw_ids) == 392
        and checks["archive_shape"] == [392, MIXED_DIM]
        and checks["query_shape"] == [1, MIXED_DIM]
        and archive_digest == EXPECTED_REAL_CANARY_ARCHIVE_SHA256
        and query_digest == EXPECTED_REAL_CANARY_QUERY_SHA256
    ) else "FAIL"
    if checks["status"] != "PASS":
        raise RuntimeError("[BLOCKED - REAL ARCHIVE REPRESENTATION CANARY]")
    return checks


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def finalize_results(
    output_dir: Path,
    eligible: Sequence[dict[str, Any]],
    provenance: dict[str, str],
) -> None:
    if (output_dir / "V52_T4F1_POST_RUN_MANIFEST.json").exists():
        raise RuntimeError("[BLOCKED - REFUSE FINALIZATION OVERWRITE]")
    by_archive: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        by_archive[f"{row['tier']}::{row['conversation_id']}"].append(row)
    expected_by_question = {row["audit_question_id"]: row for row in eligible}
    trial_rows: list[dict[str, str]] = []
    archive_evidence: list[dict[str, Any]] = []
    for archive_id in sorted(by_archive):
        if not verify_existing_archive(output_dir, archive_id, len(by_archive[archive_id]), provenance):
            raise RuntimeError(f"[BLOCKED - MISSING ARCHIVE RESULT] {archive_id}")
        safe_id = archive_id.replace("::", "__")
        csv_path = output_dir / "archives" / f"{safe_id}.csv"
        meta_path = output_dir / "archives" / f"{safe_id}.meta.json"
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != TRIAL_FIELDS:
                raise RuntimeError(f"[BLOCKED - TRIAL CSV SCHEMA] {archive_id}")
            trial_rows.extend(reader)
        archive_evidence.append(
            {
                "archive_id": archive_id,
                "csv_sha256": sha256_file(csv_path),
                "meta_sha256": sha256_file(meta_path),
            }
        )

    expected_trial_rows = EXPECTED_ELIGIBLE * 320
    if len(trial_rows) != expected_trial_rows:
        raise RuntimeError(f"[BLOCKED - FULL TRIAL ROW COUNT] {len(trial_rows)} != {expected_trial_rows}")
    valid_seeds = {
        "NATIVE_SIGN96": {""},
        "SIGNED_PERM_CONTROL96": {str(seed) for seed in SIGNED_PERM_SEEDS},
        "HAAR96_SIGN": {str(seed) for seed in HAAR_SEEDS},
        "ITQ96_CENTERED": {str(seed) for seed in ITQ_SEEDS},
    }
    metrics = (
        "fractional_source_evidence_recall_at_3",
        "any_at_3",
        "all_at_3",
    )
    seen_cells: set[tuple[str, str, str, int]] = set()
    for row in trial_rows:
        question_id = row["audit_question_id"]
        frozen = expected_by_question.get(question_id)
        if frozen is None:
            raise RuntimeError(f"[BLOCKED - UNKNOWN QUESTION RESULT] {question_id}")
        if (
            row["tier"] != frozen["tier"]
            or row["conversation_id"] != frozen["conversation_id"]
            or row["ability"] != frozen["ability"]
            or int(row["gold_count"]) != int(frozen["gold_source_unit_count"])
            or int(row["archive_units"]) <= TOP_K
        ):
            raise RuntimeError(f"[BLOCKED - QUESTION METADATA RESULT MISMATCH] {question_id}")
        method = row["method"]
        if method not in valid_seeds or row["seed"] not in valid_seeds[method]:
            raise RuntimeError(f"[BLOCKED - METHOD OR SEED RESULT] {question_id} {method} {row['seed']}")
        trial = int(row["trial"])
        if trial not in NUISANCE_TRIALS:
            raise RuntimeError(f"[BLOCKED - TRIAL ID RESULT] {question_id} {method} {trial}")
        cell = (question_id, method, row["seed"], trial)
        if cell in seen_cells:
            raise RuntimeError(f"[BLOCKED - DUPLICATE RESULT CELL] {cell}")
        seen_cells.add(cell)
        retrieved = json.loads(row["retrieved_top3_ids"])
        distances = json.loads(row["top3_distances"])
        if (
            not isinstance(retrieved, list)
            or len(retrieved) != TOP_K
            or len(set(retrieved)) != TOP_K
            or not isinstance(distances, list)
            or len(distances) != TOP_K
            or distances != sorted(distances)
            or any(not isinstance(distance, int) or distance < 0 or distance > MIXED_DIM for distance in distances)
        ):
            raise RuntimeError(f"[BLOCKED - TOP3 RESULT SCHEMA] {cell}")
        fractional = float(row["fractional_source_evidence_recall_at_3"])
        any_value = float(row["any_at_3"])
        all_value = float(row["all_at_3"])
        if (
            not 0.0 <= fractional <= 1.0
            or any_value not in {0.0, 1.0}
            or all_value not in {0.0, 1.0}
            or (fractional == 0.0) != (any_value == 0.0)
            or (int(row["gold_count"]) > TOP_K and all_value != 0.0)
        ):
            raise RuntimeError(f"[BLOCKED - METRIC RESULT SEMANTICS] {cell}")
    if len(seen_cells) != expected_trial_rows:
        raise RuntimeError("[BLOCKED - RESULT CELL COVERAGE]")
    by_question_seed: defaultdict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in trial_rows:
        by_question_seed[(row["audit_question_id"], row["method"], row["seed"])].append(row)
    question_seed_rows: list[dict[str, Any]] = []
    for (question_id, method, seed), values in sorted(by_question_seed.items()):
        trials = sorted(int(value["trial"]) for value in values)
        if trials != list(NUISANCE_TRIALS):
            raise RuntimeError(f"[BLOCKED - TRIAL COVERAGE] {question_id} {method} {seed}")
        if len({value["retrieved_top3_ids"] for value in values}) != 1:
            raise RuntimeError(f"[BUG - TRIAL-VARYING TOP3 UNDER FIXED PRIORITY] {question_id} {method} {seed}")
        base = {
            "audit_question_id": question_id,
            "tier": values[0]["tier"],
            "conversation_id": values[0]["conversation_id"],
            "ability": values[0]["ability"],
            "method": method,
            "seed": seed,
        }
        for metric in metrics:
            base[metric] = sum(float(value[metric]) for value in values) / len(values)
        question_seed_rows.append(base)

    by_question_method: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in question_seed_rows:
        by_question_method[(row["audit_question_id"], row["method"])].append(row)
    question_rows: list[dict[str, Any]] = []
    expected_seed_counts = {
        "NATIVE_SIGN96": 1,
        "SIGNED_PERM_CONTROL96": 5,
        "HAAR96_SIGN": 5,
        "ITQ96_CENTERED": 5,
    }
    for (question_id, method), values in sorted(by_question_method.items()):
        if len(values) != expected_seed_counts[method]:
            raise RuntimeError(f"[BLOCKED - SEED COVERAGE] {question_id} {method}")
        base = {
            "audit_question_id": question_id,
            "tier": values[0]["tier"],
            "conversation_id": values[0]["conversation_id"],
            "ability": values[0]["ability"],
            "method": method,
        }
        for metric in metrics:
            base[metric] = sum(float(value[metric]) for value in values) / len(values)
        question_rows.append(base)
    if len(question_rows) != EXPECTED_ELIGIBLE * 4:
        raise RuntimeError("[BLOCKED - QUESTION LEVEL ROW COUNT]")
    question_method_lookup = {
        (row["audit_question_id"], row["method"]): row for row in question_rows
    }
    for question_id in expected_by_question:
        methods = {
            method for (observed_question, method) in question_method_lookup if observed_question == question_id
        }
        if methods != set(valid_seeds):
            raise RuntimeError(f"[BLOCKED - QUESTION METHOD COVERAGE] {question_id}")
        native = question_method_lookup[(question_id, "NATIVE_SIGN96")]
        control = question_method_lookup[(question_id, "SIGNED_PERM_CONTROL96")]
        if any(float(native[metric]) != float(control[metric]) for metric in metrics):
            raise RuntimeError(f"[BUG - SIGNED CONTROL METRIC MISMATCH] {question_id}")

    by_method: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in question_rows:
        by_method[row["method"]].append(row)
    aggregate_rows: list[dict[str, Any]] = []
    for method in ("NATIVE_SIGN96", "SIGNED_PERM_CONTROL96", "HAAR96_SIGN", "ITQ96_CENTERED"):
        values = by_method[method]
        if len(values) != EXPECTED_ELIGIBLE:
            raise RuntimeError(f"[BLOCKED - AGGREGATE DENOMINATOR] {method}")
        row = {"method": method, "question_denominator": EXPECTED_ELIGIBLE}
        for metric in metrics:
            row[metric] = sum(float(value[metric]) for value in values) / EXPECTED_ELIGIBLE
        aggregate_rows.append(row)

    seed_fields = ("audit_question_id", "tier", "conversation_id", "ability", "method", "seed", *metrics)
    question_fields = ("audit_question_id", "tier", "conversation_id", "ability", "method", *metrics)
    aggregate_fields = ("method", "question_denominator", *metrics)
    seed_path = output_dir / "V52_T4F1_question_seed_level.csv"
    question_path = output_dir / "V52_T4F1_question_level.csv"
    aggregate_path = output_dir / "V52_T4F1_aggregate.csv"
    write_csv(seed_path, question_seed_rows, seed_fields)
    write_csv(question_path, question_rows, question_fields)
    write_csv(aggregate_path, aggregate_rows, aggregate_fields)

    output_files = [seed_path, question_path, aggregate_path]
    manifest = {
        "schema": "V52_T4F1_POST_RUN_MANIFEST_V2",
        "task": TASK,
        "status": "COMPLETE_PENDING_INDEPENDENT_RESULT_AUDIT",
        **provenance,
        "question_denominator": EXPECTED_ELIGIBLE,
        "archive_count": EXPECTED_ARCHIVES,
        "trial_rows": expected_trial_rows,
        "archive_evidence": archive_evidence,
        "outputs": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in output_files
        ],
        "console_outcomes_emitted": False,
        "interpretation_authorized": False,
    }
    write_json(output_dir / "V52_T4F1_POST_RUN_MANIFEST.json", manifest)
    print("COMPLETE: all 96 archives finalized; outcome values were not printed", flush=True)


def preflight(args: argparse.Namespace, script_path: Path) -> None:
    environment = verify_environment()
    restricted_seal = verify_bound_file(args.restricted_seal, EXPECTED_RESTRICTED_SEAL_SHA256, "restricted seal")
    protocol = verify_bound_file(args.protocol, EXPECTED_PROTOCOL_SHA256, "restricted protocol")
    dependency_lock = verify_bound_file(args.dependency_lock, EXPECTED_DEPENDENCY_LOCK_SHA256, "dependency lock")
    execution_seal, execution_seal_hash = verify_execution_seal(args.execution_seal, script_path)
    eligible, cohort_summary = load_and_verify_cohort(args.cohort)
    beam = verify_beam_checkout(args.corpus_root, cohort_summary["archive_ids"], args.beam_manifest)
    synthetic = synthetic_preflight()
    real_canary = real_archive_canary(args.corpus_root)
    report = {
        "schema": "V52_T4F1_IMPLEMENTATION_PREFLIGHT_V2",
        "status": "PASS",
        "script": {"bytes": script_path.stat().st_size, "sha256": sha256_file(script_path)},
        "execution_seal_sha256": execution_seal_hash,
        "execution_seal_status": execution_seal.get("status"),
        "restricted_seal": restricted_seal,
        "protocol": protocol,
        "dependency_lock": dependency_lock,
        "environment": environment,
        "cohort": cohort_summary,
        "beam": {"commit": beam["commit"], "files_checked": beam["files_checked"]},
        "synthetic": synthetic,
        "real_archive_canary": real_canary,
        "eligible_rows_loaded_for_structural_validation": len(eligible),
        "retrieval_quality_computed": False,
        "outcome_accessed": False,
        "task_4f1_run_authorized": False,
    }
    write_json(args.preflight_output, report)
    print("PASS: byte bindings, environment, corpus identity, cohort structure, and synthetic execution gates", flush=True)
    print("BLOCKED: Task 4F1 run still requires independent implementation audit and Head Researcher authorization", flush=True)


def run_archives(args: argparse.Namespace, script_path: Path) -> None:
    verify_environment()
    verify_bound_file(args.restricted_seal, EXPECTED_RESTRICTED_SEAL_SHA256, "restricted seal")
    verify_bound_file(args.protocol, EXPECTED_PROTOCOL_SHA256, "restricted protocol")
    verify_bound_file(args.dependency_lock, EXPECTED_DEPENDENCY_LOCK_SHA256, "dependency lock")
    _, execution_seal_hash = verify_execution_seal(args.execution_seal, script_path)
    eligible, cohort_summary = load_and_verify_cohort(args.cohort)
    _, authorization_hash = verify_run_authorization(
        args.authorization,
        script_path,
        args.execution_seal,
        args.cohort,
        args.output_dir,
    )
    provenance = {
        "script_sha256": sha256_file(script_path),
        "cohort_sha256": sha256_file(args.cohort),
        "run_authorization_sha256": authorization_hash,
        "execution_candidate_seal_sha256": execution_seal_hash,
    }
    verify_beam_checkout(args.corpus_root, cohort_summary["archive_ids"], args.beam_manifest)
    by_archive: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        by_archive[f"{row['tier']}::{row['conversation_id']}"].append(row)
    requested = list(args.archive) if args.archive else sorted(by_archive)
    invalid = sorted(set(requested) - set(by_archive))
    if invalid:
        raise RuntimeError(f"[BLOCKED - INVALID ARCHIVE SELECTION] {invalid}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if (args.output_dir / "V52_T4F1_POST_RUN_MANIFEST.json").exists():
        raise RuntimeError("[BLOCKED - OUTPUT ALREADY FINALIZED]")
    for archive_id in requested:
        if verify_existing_archive(args.output_dir, archive_id, len(by_archive[archive_id]), provenance):
            if args.resume:
                print(f"SKIP verified checkpoint {archive_id}", flush=True)
                continue
            raise RuntimeError(f"[BLOCKED - ARCHIVE RESULT EXISTS] {archive_id}; use --resume")
        print(f"START {archive_id} questions={len(by_archive[archive_id])}", flush=True)
        rows, metadata = evaluate_archive(args.corpus_root, archive_id, by_archive[archive_id], provenance)
        write_archive_result(args.output_dir, archive_id, rows, metadata)
        print(f"COMPLETE {archive_id} rows={len(rows)}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("preflight", "run", "finalize"))
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--beam-manifest", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--restricted-seal", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--dependency-lock", type=Path, required=True)
    parser.add_argument("--execution-seal", type=Path, required=True)
    parser.add_argument("--preflight-output", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--archive", action="append", help="authorized batching only; repeat tier::conversation")
    parser.add_argument("--resume", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    script_path = Path(__file__).resolve()
    if args.mode == "preflight":
        if args.preflight_output is None:
            parser.error("--preflight-output is required for preflight")
        if args.authorization is not None or args.output_dir is not None or args.archive or args.resume:
            parser.error("preflight forbids run/finalize arguments")
        preflight(args, script_path)
        return
    if args.authorization is None or args.output_dir is None:
        parser.error("--authorization and --output-dir are required for run/finalize")
    if not args.authorization.is_file():
        raise RuntimeError("[BLOCKED - RUN AUTHORIZATION FILE MISSING]")
    if args.mode == "run":
        run_archives(args, script_path)
    else:
        if args.archive or args.resume:
            parser.error("finalize forbids --archive and --resume")
        verify_environment()
        verify_bound_file(args.restricted_seal, EXPECTED_RESTRICTED_SEAL_SHA256, "restricted seal")
        verify_bound_file(args.protocol, EXPECTED_PROTOCOL_SHA256, "restricted protocol")
        verify_bound_file(args.dependency_lock, EXPECTED_DEPENDENCY_LOCK_SHA256, "dependency lock")
        _, execution_seal_hash = verify_execution_seal(args.execution_seal, script_path)
        eligible, cohort_summary = load_and_verify_cohort(args.cohort)
        _, authorization_hash = verify_run_authorization(
            args.authorization,
            script_path,
            args.execution_seal,
            args.cohort,
            args.output_dir,
        )
        provenance = {
            "script_sha256": sha256_file(script_path),
            "cohort_sha256": sha256_file(args.cohort),
            "run_authorization_sha256": authorization_hash,
            "execution_candidate_seal_sha256": execution_seal_hash,
        }
        verify_beam_checkout(args.corpus_root, cohort_summary["archive_ids"], args.beam_manifest)
        finalize_results(args.output_dir, eligible, provenance)


if __name__ == "__main__":
    main()
