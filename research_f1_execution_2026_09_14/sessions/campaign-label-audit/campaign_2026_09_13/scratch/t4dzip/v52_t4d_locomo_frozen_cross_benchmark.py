#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import inspect
import json
import math
import os
import re
import shutil
import sys
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import spearmanr
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

TASK = "V52 TASK 4D — LOCOMO FROZEN CROSS-BENCHMARK REPLICATION"
DATE = "2026-08-29"
CANONICAL_PARENT_COMMIT = "8f52c8072f4f781ad2539c461fae154c4c52753b"
PREREG_COMMIT = "68c4c10a6886e1076efcffd8981d53bf14fb9b6f"
PROMPT_PATH = "prompts/V52_TASK_4D_LOCOMO_FROZEN_CROSS_BENCHMARK_REPLICATION_2026-08-29.md"
PROMPT_BLOB_SHA = "bd82b564b5ee065ee2e4dad799bf0bacf6bd2aa8"
DRIVE_PROMPT_ID = "19nbkI9g0djWMoIO8DqdsNQowdLiO1-_hKYx-8831w58"
DRIVE_PROMPT_URL = "https://docs.google.com/document/d/19nbkI9g0djWMoIO8DqdsNQowdLiO1-_hKYx-8831w58/edit?usp=drivesdk"

DATASET_SHA256 = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
EXPECTED_CONVERSATIONS = 10
EXPECTED_QUESTIONS = 1540
EXPECTED_CATEGORY_COUNTS = {1: 282, 2: 321, 3: 96, 4: 841}
EXPECTED_AUDIT_CORRECTIONS = 156

# Frozen source-family provenance from the accepted V52 LongMemEval geometry line.
ADAPTER_V1_REPO_PATH = "adapters/longmemeval_v52_adapter.py"
ADAPTER_V1_GIT_BLOB = "16c1349336e143d27d9cac68198cbb50a1e6340b"
ADAPTER_V1_SHA256 = "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722"
ADAPTER_V2_REPO_PATH = "adapters/longmemeval_v52_adapter_v2.py"
ADAPTER_V2_GIT_BLOB = "aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1"
ADAPTER_V2_SHA256 = "643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218"
ACCEPTED_4C3_SCRIPT_SHA256 = "8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996"

SVD_SEED = 5204
SOURCE_LATENT_DIM = 32
ROTATION_SEEDS = [43001, 43002, 43003, 43004, 43005]
ITQ_SEEDS = [101, 202, 303, 404, 505]
N_NUISANCE = 20
TOPK = 3
CONT_TOL = 1e-12

NO_RESCUE = [
    "block sizes", "rotation seeds", "nuisance trials", "bit widths", "thresholds",
    "centering rule", "alternate embeddings/encoders", "alternate source-block weighting",
    "whitening/PCA variants", "supervised rotations", "query-adaptive rotations",
    "reranking/shortlists", "alternate top-k", "new LoCoMo subsets/categories",
    "alternative correction sets", "new metrics chosen because the primary result is weak",
    "LongMemEval-V2", "million-memory scaling", "latency/system benchmark",
]


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def norm_evidence(x):
    """Exact V51 LoCoMo evidence normalization semantics."""
    if x is None:
        return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def message_text(msg):
    """Exact V51 memory-text semantics, including BLIP captions."""
    speaker = str(msg.get("speaker", "")).strip()
    text = str(msg.get("text", "")).strip()
    cap = str(msg.get("blip_caption", "") or "").strip()
    if cap:
        text = f"{text} [IMAGE: {cap}]".strip()
    return f"{speaker}: {text}".strip(": ")


def raw_item_to_conv(item, idx):
    conv_id = f"locomo_{idx}"
    c = item.get("conversation", {})
    lines = []
    for sk in sorted(
        [k for k in c if k.startswith("session_") and not k.endswith("_date_time")],
        key=lambda x: int(x.split("_")[1]),
    ):
        for msg in c.get(sk, []) or []:
            did = str(msg.get("dia_id", ""))
            if did:
                lines.append({"dia_id": did, "text": message_text(msg), "session": sk})
    qas = []
    for qi, q in enumerate(item.get("qa", []) or []):
        cat = int(q.get("category")) if q.get("category") is not None else None
        qid = q.get("question_id") or f"{conv_id}_qa{qi}"
        qas.append({
            "question_id": str(qid),
            "question": str(q.get("question", "")),
            "answer": str(q.get("answer", "")),
            "category": cat,
            "raw_evidence": norm_evidence(q.get("evidence")),
        })
    return {"conv_id": conv_id, "lines": lines, "qas": qas}


def load_audit_corrections(audit_dir: Path):
    corrections = {}
    for f in sorted(audit_dir.glob("errors_conv_*.json")):
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            qid = r.get("question_id")
            if not qid:
                continue
            corrections[str(qid)] = {
                "error_type": r.get("error_type"),
                # Explicit [] is semantically different from an absent correction field.
                "has_correct_evidence": "correct_evidence" in r,
                "correct_evidence": norm_evidence(r.get("correct_evidence")),
                "correct_answer": r.get("correct_answer"),
            }
    return corrections


def load_dataset(raw: Path, audit_dir: Path):
    arr = json.loads(raw.read_text(encoding="utf-8"))
    if not isinstance(arr, list):
        raise RuntimeError("[BLOCKED — LOCOMO CANONICAL ADAPTER / DATA IDENTITY NOT REPRODUCIBLE] raw not list")
    convs = [raw_item_to_conv(x, i) for i, x in enumerate(arr)]
    corr = load_audit_corrections(audit_dir)
    for c in convs:
        for q in c["qas"]:
            z = corr.get(q["question_id"])
            if z:
                q["audit_error_type"] = z["error_type"]
                q["correct_evidence"] = (
                    list(z["correct_evidence"])
                    if z.get("has_correct_evidence", False)
                    else list(q["raw_evidence"])
                )
                q["correct_answer"] = z["correct_answer"]
            else:
                q["audit_error_type"] = None
                q["correct_evidence"] = list(q["raw_evidence"])
                q["correct_answer"] = q["answer"]
    return convs, corr


# BEGIN exact frozen source-block family implementation used by V52 adapter v1.
def fit_input_payload(memory_texts: list[str]) -> list[str]:
    # Strong structural leakage barrier: fitting receives strings only.
    return list(memory_texts)


def fit_archive_representation(memory_texts: list[str]):
    """
    Archive-only unsupervised fit. This function accepts memory text only.
    Its implementation matches the frozen V52 adapter source-block family.
    """
    if len(memory_texts) < 25:
        raise ValueError("Archive too small to support frozen source family.")
    wv = TfidfVectorizer(
        lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True
    )
    cv = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True
    )
    Xw = normalize(wv.fit_transform(memory_texts))
    Xc = normalize(cv.fit_transform(memory_texts))
    d = min(SOURCE_LATENT_DIM, Xw.shape[0] - 1, Xw.shape[1] - 1)
    if d < 24:
        raise ValueError(f"latent dimension {d}<24; frozen source family unsupported")
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    return wv, cv, svd, Xw, Xc, Xl
# END exact frozen source-block family implementation.


def fit_itq(V: np.ndarray, n_iter: int = 100, seed: int = 101) -> np.ndarray:
    """Canonical audited V52 ITQ orientation."""
    rng = np.random.default_rng(seed)
    d = V.shape[1]
    A = rng.normal(size=(d, d))
    U, _, VT = np.linalg.svd(A, full_matrices=False)
    R = U @ VT
    for _ in range(n_iter):
        B = np.where(V @ R >= 0, 1.0, -1.0)
        C = B.T @ V
        U2, _, VT2 = np.linalg.svd(C, full_matrices=False)
        R = VT2.T @ U2.T
    return R


def stable_archive_seed(archive_ordinal: int, trial: int = 0) -> int:
    return 5_100_000 + archive_ordinal * 100_000 + trial * 100


def sp_spec(seed):
    r = np.random.default_rng(seed)
    return r.permutation(96), r.choice(np.array([-1.0, 1.0]), 96)


def sp_apply(X, perm, s):
    return np.asarray(X, float)[..., perm] * s


def hspec(seed, b=96):
    r = np.random.default_rng(seed)
    perm = r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return perm, qs


def happly(X, perm, qs, b=96):
    xp = np.asarray(X, float)[..., perm]
    o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b)
        o[..., sl] = xp[..., sl] @ Q
    return o


def hmat(perm, qs, b=96):
    P = np.zeros((96, 96))
    P[perm, np.arange(96)] = 1
    B = np.zeros((96, 96))
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b)
        B[sl, sl] = Q
    return P @ B


def topks_by_hamming(dist: np.ndarray, priorities: list[np.ndarray], k: int = TOPK) -> list[np.ndarray]:
    """Exact top-k sets for all nuisance trials, vectorized over the boundary tie bucket.

    Ordering is lexicographic by integer Hamming distance then frozen independent priority.
    Retrieval metrics depend on the top-k set, so ordering inside the returned set is immaterial.
    """
    dist = np.asarray(dist)
    P = np.asarray(priorities, dtype=float)
    if len(dist) <= k:
        return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k - 1)[k - 1]
    strict = np.flatnonzero(dist < kth)
    boundary = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, boundary]
    if need == len(boundary):
        picks = np.tile(boundary, (len(P), 1))
    else:
        loc = np.argpartition(BP, need - 1, axis=1)[:, :need]
        picks = boundary[loc]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]


def evidence_rows(ids, id_to_row):
    out = []
    for x in ids:
        if x in id_to_row:
            out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))


def retrieval_metrics(top: np.ndarray, gold_rows: list[int]):
    if not gold_rows:
        return {"valid": 0, "any": np.nan, "all": np.nan, "fractional": np.nan, "gold_count": 0}
    R = set(map(int, top))
    G = set(map(int, gold_rows))
    inter = len(R & G)
    return {
        "valid": 1,
        "any": float(inter > 0),
        "all": float(G.issubset(R)),
        "fractional": float(inter / len(G)),
        "gold_count": len(G),
    }


def code_diag(D: np.ndarray):
    packed = np.packbits(D, axis=1, bitorder="big")
    _, cnt = np.unique(packed, axis=0, return_counts=True)
    occ = D.mean(axis=0)
    return {
        "unique_code_fraction": float(len(cnt) / len(D)),
        "duplicate_code_fraction": float(1.0 - len(cnt) / len(D)),
        "largest_collision_bucket": int(cnt.max()),
        "bit_occupancy_mean": float(occ.mean()),
        "bit_occupancy_min": float(occ.min()),
        "bit_occupancy_max": float(occ.max()),
        "dead_bits": int(np.sum((occ == 0.0) | (occ == 1.0))),
    }


def query_diag(D: np.ndarray, Q: np.ndarray, dist: np.ndarray):
    sd = np.sort(dist)
    kth = int(sd[TOPK - 1])
    lt = int(np.sum(dist < kth))
    boundary = int(np.sum(dist == kth))
    slots = TOPK - lt
    exact = int(np.sum(np.all(D == Q[None, :], axis=1)))
    return {
        "query_exact_code_match_fraction": float(exact / len(D)),
        "min_hamming_distance": int(dist.min()),
        "candidates_at_min_distance": int(np.sum(dist == dist.min())),
        "top3_boundary_distance": kth,
        "candidates_at_top3_boundary": boundary,
        "slots_remaining_at_boundary": int(slots),
        "top3_boundary_tie": int(boundary > slots),
    }


def cosine_scores(C: np.ndarray, Q: np.ndarray) -> np.ndarray:
    dn = np.linalg.norm(C, axis=1)
    qn = np.linalg.norm(Q, axis=1)
    den = qn[:, None] * dn[None, :]
    return np.divide(Q @ C.T, den, out=np.zeros((len(Q), len(C)), dtype=float), where=den > 0)


def tie_aware_top3_equivalent(a: np.ndarray, b: np.ndarray, tol: float = CONT_TOL) -> bool:
    """Compare top-3 candidate/tie sets, not arbitrary ordering inside score ties."""
    for x, y in zip(a, b):
        sx = np.sort(x)[::-1]
        sy = np.sort(y)[::-1]
        tx = sx[min(TOPK - 1, len(sx) - 1)]
        ty = sy[min(TOPK - 1, len(sy) - 1)]
        # Candidate sets that could occupy top3 under tolerance-aware ties.
        cx = set(np.flatnonzero(x >= tx - tol).tolist())
        cy = set(np.flatnonzero(y >= ty - tol).tolist())
        strict_x = set(np.flatnonzero(x > tx + tol).tolist())
        strict_y = set(np.flatnonzero(y > ty + tol).tolist())
        if strict_x != strict_y or cx != cy:
            return False
    return True


def audit_layer_manifest(audit_dir: Path):
    files = sorted(list(audit_dir.glob("conv_*.json")) + list(audit_dir.glob("errors_conv_*.json")))
    rows = [{"file": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in files]
    canon = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return rows, sha256_bytes(canon)


def source_function_hash(fn) -> str:
    return sha256_bytes(inspect.getsource(fn).encode("utf-8"))


def leakage_static_checks(script_path: Path):
    text = script_path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    fs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    rows = []
    forbidden = ["gold", "evidence", "answer", "category", "question"]
    for fn in ["fit_input_payload", "fit_archive_representation", "sp_spec", "hspec"]:
        body = (ast.get_source_segment(text, fs[fn]) or "").lower()
        bad = [x for x in forbidden if x in body]
        # fit_archive_representation docstring says no question/gold; remove docstrings/comments effect by AST names.
        names = {n.id.lower() for n in ast.walk(fs[fn]) if isinstance(n, ast.Name)}
        bad_names = sorted(names.intersection(forbidden))
        ok = not bad_names
        rows.append({
            "check": fn,
            "status": "PASS" if ok else "FAIL",
            "blocking": int(not ok),
            "detail": f"forbidden AST names={bad_names}",
        })
    return rows


def validate_identity(raw: Path, audit_dir: Path, script_path: Path, out: Path):
    checks = []
    def add(name, observed, expected, ok, detail=""):
        checks.append({"check": name, "observed": observed, "expected": expected, "status": "PASS" if ok else "FAIL", "detail": detail})

    dsha = sha256_file(raw)
    add("dataset_sha256", dsha, DATASET_SHA256, dsha == DATASET_SHA256)
    convs, corr = load_dataset(raw, audit_dir)
    add("conversation_count", len(convs), EXPECTED_CONVERSATIONS, len(convs) == EXPECTED_CONVERSATIONS)
    qas = [(c, q) for c in convs for q in c["qas"] if q.get("category") in EXPECTED_CATEGORY_COUNTS]
    add("primary_question_count", len(qas), EXPECTED_QUESTIONS, len(qas) == EXPECTED_QUESTIONS)
    cc = Counter(q["category"] for _, q in qas)
    add("category_counts", json.dumps(dict(sorted(cc.items()))), json.dumps(EXPECTED_CATEGORY_COUNTS), dict(cc) == EXPECTED_CATEGORY_COUNTS)
    add("audit_correction_count", len(corr), EXPECTED_AUDIT_CORRECTIONS, len(corr) == EXPECTED_AUDIT_CORRECTIONS)
    all_qids = {q["question_id"] for c in convs for q in c["qas"]}
    unmatched = sorted(set(corr) - all_qids)
    add("audit_unmatched_corrections", len(unmatched), 0, not unmatched, "|".join(unmatched[:10]))
    explicit_empty = sum(1 for z in corr.values() if z.get("has_correct_evidence") and not z.get("correct_evidence"))
    add("explicit_empty_correction_semantics", explicit_empty, ">=1 preserved", explicit_empty >= 1)

    audit_files, audit_hash = audit_layer_manifest(audit_dir)
    add("audit_layer_file_count", len(audit_files), 20, len(audit_files) == 20)

    # BLIP handling proof: every non-empty caption must be present in the memory text.
    arr = json.loads(raw.read_text(encoding="utf-8"))
    caps = 0
    cap_ok = 0
    for item in arr:
        c = item.get("conversation", {})
        for sk, msgs in c.items():
            if not sk.startswith("session_") or sk.endswith("_date_time") or not isinstance(msgs, list):
                continue
            for msg in msgs:
                cap = str(msg.get("blip_caption", "") or "").strip()
                if cap:
                    caps += 1
                    if f"[IMAGE: {cap}]" in message_text(msg):
                        cap_ok += 1
    add("BLIP_caption_inclusion", cap_ok, caps, cap_ok == caps and caps > 0)

    # Retrievable-gold semantics are frozen before any outcomes.
    raw_valid = audit_valid = common_valid = 0
    raw_unretrievable = audit_unretrievable = 0
    qmeta = []
    conv_sizes = {c["conv_id"]: len(c["lines"]) for c in convs}
    sorted_conv = sorted(conv_sizes, key=lambda cid: (conv_sizes[cid], cid))
    quartile = {cid: int((i * 4) // len(sorted_conv) + 1) for i, cid in enumerate(sorted_conv)}
    for c, q in qas:
        ids = {x["dia_id"] for x in c["lines"]}
        rg = list(dict.fromkeys([x for x in q["raw_evidence"] if x in ids]))
        ag = list(dict.fromkeys([x for x in q["correct_evidence"] if x in ids]))
        rv, av = bool(rg), bool(ag)
        raw_valid += int(rv); audit_valid += int(av); common_valid += int(rv and av)
        raw_unretrievable += int(bool(q["raw_evidence"]) and not rv)
        audit_unretrievable += int(bool(q["correct_evidence"]) and not av)
        qmeta.append({
            "conv_id": c["conv_id"], "question_id": q["question_id"], "category": q["category"],
            "archive_size": len(c["lines"]), "archive_size_quartile": quartile[c["conv_id"]],
            "raw_retrievable_gold_count": len(rg), "audit_retrievable_gold_count": len(ag),
            "raw_evidence_valid": int(rv), "audit_evidence_valid": int(av),
        })
    add("raw_evidence_valid_questions", raw_valid, 1535, raw_valid == 1535)
    add("audit_evidence_valid_questions", audit_valid, 1535, audit_valid == 1535)
    add("common_raw_audit_valid_questions", common_valid, "recorded", True)

    leak = leakage_static_checks(script_path)
    for r in leak:
        add("leakage_" + r["check"], r["status"], "PASS", r["status"] == "PASS", r["detail"])

    df = pd.DataFrame(checks)
    df.to_csv(out / "V52_T4D_INPUT_CHECKS.csv", index=False)
    pd.DataFrame(qmeta).to_csv(out / "V52_T4D_PRE_OUTCOME_QUESTION_COHORT.csv", index=False)
    pd.DataFrame([
        {"conv_id": cid, "archive_size": conv_sizes[cid], "archive_size_quartile": quartile[cid]}
        for cid in sorted(conv_sizes)
    ]).to_csv(out / "V52_T4D_ARCHIVE_SIZE_QUARTILES_FROZEN.csv", index=False)

    if not (df["status"] == "PASS").all():
        bad = df[df.status != "PASS"].to_dict("records")
        raise RuntimeError("[BLOCKED — LOCOMO CANONICAL ADAPTER / DATA IDENTITY NOT REPRODUCIBLE] " + json.dumps(bad[:5]))

    return {
        "convs": convs,
        "corrections": corr,
        "dataset_sha256": dsha,
        "dataset_bytes": raw.stat().st_size,
        "audit_layer_files": audit_files,
        "audit_layer_manifest_sha256": audit_hash,
        "explicit_empty_corrections": explicit_empty,
        "raw_valid": raw_valid,
        "audit_valid": audit_valid,
        "common_valid": common_valid,
        "conv_sizes": conv_sizes,
        "quartile": quartile,
        "raw_unretrievable": raw_unretrievable,
        "audit_unretrievable": audit_unretrievable,
    }


def write_representation_transfer_proof(out: Path, identity, stage: str, rep_rows=None):
    fhash = source_function_hash(fit_archive_representation)
    phash = source_function_hash(fit_input_payload)
    lines = [
        "V52_T4D_REPRESENTATION_TRANSFER_PROOF",
        f"stage={stage}",
        f"task={TASK}",
        f"canonical_parent_commit={CANONICAL_PARENT_COMMIT}",
        f"adapter_v1_repo_path={ADAPTER_V1_REPO_PATH}",
        f"adapter_v1_git_blob={ADAPTER_V1_GIT_BLOB}",
        f"adapter_v1_recorded_sha256={ADAPTER_V1_SHA256}",
        f"adapter_v2_repo_path={ADAPTER_V2_REPO_PATH}",
        f"adapter_v2_git_blob={ADAPTER_V2_GIT_BLOB}",
        f"adapter_v2_recorded_sha256={ADAPTER_V2_SHA256}",
        f"accepted_task4c3_script_sha256={ACCEPTED_4C3_SCRIPT_SHA256}",
        f"local_fit_archive_representation_source_sha256={fhash}",
        f"local_fit_input_payload_source_sha256={phash}",
        "source_blocks=word TF-IDF(1,2; english stop words; sublinear) + char_wb TF-IDF(3,5; sublinear) + latent32 TruncatedSVD(random_state=5101), each frozen as in V52 adapter family",
        "mixed96=concatenate [latent, word, char] -> archive-only TruncatedSVD(96, random_state=5204) -> L2 normalize",
        "centering=mu96 computed from archive documents only; C96=Y96-mu96; qC96=QY96-mu96",
        "fit_payload=archive memory text strings only",
        "query_transform=performed only after archive vectorizers/source SVD/mixed96 SVD are fit",
        "forbidden_fit_inputs=QA answers,gold evidence,category labels,answer/session metadata",
        "BLIP_rule=append exact non-empty caption as ' [IMAGE: {caption}]' before archive fit",
        "LoCoMo_unit_transfer=one conversation is one archive fit unit; all Cat1-Cat4 queries in that conversation share the archive-only fitted representation",
        "tie_priority=stable_archive_seed(conversation_ordinal,trial), then default_rng(seed+99).random(N_archive)",
        f"dataset_sha256={identity['dataset_sha256']}",
        f"audit_layer_manifest_sha256={identity['audit_layer_manifest_sha256']}",
        "static_leakage_gate=PASS",
    ]
    if rep_rows:
        lines.append("per_conversation_fit:")
        for r in rep_rows:
            lines.append(json.dumps(r, sort_keys=True))
    (out / "V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_seal(raw: Path, audit_dir: Path, out: Path, script_path: Path):
    out.mkdir(parents=True, exist_ok=True)
    seal_path = out / "V52_T4D_PRE_RUN_SEAL.json"
    if seal_path.exists():
        raise RuntimeError("Refusing to overwrite an existing pre-run seal.")
    identity = validate_identity(raw, audit_dir, script_path, out)
    write_representation_transfer_proof(out, identity, "PRE_OUTCOME_STATIC_PROOF")
    script_sha = sha256_file(script_path)
    seal = {
        "task": TASK,
        "date": DATE,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SEALED_BEFORE_ANY_TASK4D_RETRIEVAL_QUALITY_OUTCOME",
        "canonical_parent_git_commit": CANONICAL_PARENT_COMMIT,
        "github_preregistration_commit": PREREG_COMMIT,
        "github_prompt_path": PROMPT_PATH,
        "github_prompt_blob_sha": PROMPT_BLOB_SHA,
        "drive_prompt_id": DRIVE_PROMPT_ID,
        "drive_prompt_url": DRIVE_PROMPT_URL,
        "dataset_sha256": identity["dataset_sha256"],
        "dataset_bytes": identity["dataset_bytes"],
        "correction_layer_identifier": "dial481/locomo-audit; 10 conv files + 10 errors files; explicit-empty correction semantics preserved",
        "audit_layer_manifest_sha256": identity["audit_layer_manifest_sha256"],
        "audit_layer_file_hashes": identity["audit_layer_files"],
        "source_block_implementation": {
            "adapter_v1_repo_path": ADAPTER_V1_REPO_PATH,
            "adapter_v1_git_blob": ADAPTER_V1_GIT_BLOB,
            "adapter_v1_recorded_sha256": ADAPTER_V1_SHA256,
            "adapter_v2_repo_path": ADAPTER_V2_REPO_PATH,
            "adapter_v2_git_blob": ADAPTER_V2_GIT_BLOB,
            "adapter_v2_recorded_sha256": ADAPTER_V2_SHA256,
            "accepted_4c3_script_sha256": ACCEPTED_4C3_SCRIPT_SHA256,
            "local_fit_archive_representation_source_sha256": source_function_hash(fit_archive_representation),
            "local_fit_input_payload_source_sha256": source_function_hash(fit_input_payload),
        },
        "BLIP_caption_rule": "speaker: text [IMAGE: blip_caption] when caption non-empty",
        "cohort": {"conversations": 10, "Cat1_Cat4_questions": 1540, "category_counts": EXPECTED_CATEGORY_COUNTS},
        "retrievable_gold_semantics": {
            "raw_evidence_valid_pre_outcome": identity["raw_valid"],
            "audit_clean_evidence_valid_pre_outcome": identity["audit_valid"],
            "common_valid_pre_outcome": identity["common_valid"],
            "unretrievable annotations excluded from metric denominator": True,
        },
        "representation_recipe": "frozen source blocks -> concatenate -> archive-only TruncatedSVD(96,random_state=5204) -> L2 normalize -> archive mean centering",
        "methods": ["NATIVE_SIGN96", "SIGNED_PERM_CONTROL96", "HAAR96_SIGN", "ITQ96_CENTERED", "CENTERED_FLOAT_INVARIANCE_REFERENCE"],
        "rotation_seeds": ROTATION_SEEDS,
        "itq_seeds": ITQ_SEEDS,
        "nuisance_trials": N_NUISANCE,
        "top_k": TOPK,
        "primary_metric": "Audit-clean Fractional Evidence Recall@3",
        "secondary_metrics": ["ANY Evidence Recall@3", "ALL Evidence Recall@3"],
        "tie_priority_rule": "conversation ordinal 0..9; stable_archive_seed=5_100_000+ordinal*100_000+trial*100; priority=default_rng(seed+99).random(N_archive)",
        "decision_bands": {
            "strong": "D_LoCoMo<=-5.0 pp AND all 5/5 Haar seeds below native",
            "partial_mixed": "D_LoCoMo<-1.0 pp but strong rule not fully satisfied",
            "no_material": "abs(D_LoCoMo)<=1.0 pp",
            "falsified_direction": "D_LoCoMo>+1.0 pp",
        },
        "continuous_invariance_tolerance": CONT_TOL,
        "strata_frozen": ["Cat1", "Cat2", "Cat3", "Cat4", "one-gold vs multi-gold if valid", "all 10 conversations", "archive-size quartiles frozen before outcomes"],
        "composition_sensitivity": ["W/T/L", "median paired gap", "mean paired gap", "remove top 10,25,50 native-positive contributors"],
        "protocol_defect_effect_predefinition": "maximum absolute raw-vs-audit-clean Fractional R@3 difference in percentage points on the intersection of raw/audit retrievable-evidence-valid questions, across Native, each Haar seed, mean Haar, each ITQ seed, mean ITQ",
        "no_rescue_no_expansion": NO_RESCUE,
        "inference": "exact fixed-benchmark paired estimand; nuisance collapsed within question; Haar/ITQ seeds collapsed within question; no population p-value claim",
        "sealed_compute_script_sha256": script_sha,
    }
    seal_path.write_text(json.dumps(seal, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    print("SEALED_PRE_RUN_SHA256", sha256_file(seal_path))
    print("SEALED_SCRIPT_SHA256", script_sha)


def load_and_verify_seal(raw: Path, audit_dir: Path, out: Path, script_path: Path):
    p = out / "V52_T4D_PRE_RUN_SEAL.json"
    if not p.exists():
        raise RuntimeError("Missing V52_T4D_PRE_RUN_SEAL.json")
    seal = json.loads(p.read_text(encoding="utf-8"))
    if seal["sealed_compute_script_sha256"] != sha256_file(script_path):
        raise RuntimeError("[PROTOCOL SEAL FAILURE] sealed script bytes changed")
    if seal["dataset_sha256"] != sha256_file(raw):
        raise RuntimeError("[PROTOCOL SEAL FAILURE] dataset changed")
    _, ah = audit_layer_manifest(audit_dir)
    if seal["audit_layer_manifest_sha256"] != ah:
        raise RuntimeError("[PROTOCOL SEAL FAILURE] audit layer changed")
    return seal


def build_representation(conv):
    lines = conv["lines"]
    texts = fit_input_payload([x["text"] for x in lines])
    wv, cv, sv, Xw, Xc, Xl = fit_archive_representation(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    if min(Z.shape) <= 96:
        raise RuntimeError(f"[BLOCKED — representation transfer incompatible] {conv['conv_id']} Zshape={Z.shape}")
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    qas = [q for q in conv["qas"] if q.get("category") in EXPECTED_CATEGORY_COUNTS]
    questions = [q["question"] for q in qas]
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(s96.transform(Zq))
    QC = (QY - mu).astype(np.float64)
    id_to_row = {x["dia_id"]: i for i, x in enumerate(lines)}
    if len(id_to_row) != len(lines):
        raise RuntimeError(f"[BLOCKED — duplicate dia_id] {conv['conv_id']}")
    return {
        "C": C,
        "QC": QC,
        "qas": qas,
        "id_to_row": id_to_row,
        "N": len(lines),
        "source_word_features": int(Xw.shape[1]),
        "source_char_features": int(Xc.shape[1]),
        "source_latent_dim": int(Xl.shape[1]),
        "mixed_concat_features": int(Z.shape[1]),
        "mixed96_dim": int(C.shape[1]),
        "archive_fit_docs": int(len(texts)),
        "query_count": int(len(qas)),
        "no_nan": bool(np.isfinite(C).all() and np.isfinite(QC).all()),
    }


def mean_or_nan(xs):
    a = np.asarray(xs, dtype=float)
    return float(np.nanmean(a)) if np.isfinite(a).any() else np.nan


def method_label(method, seed):
    if seed is None:
        return method
    return f"{method}_seed{seed}"


def precompute_metric_arrays(topsets, gold_rows):
    vals = [retrieval_metrics(x, gold_rows) for x in topsets]
    return {
        "valid": max(v["valid"] for v in vals),
        "any": mean_or_nan([v["any"] for v in vals]),
        "all": mean_or_nan([v["all"] for v in vals]),
        "fractional": mean_or_nan([v["fractional"] for v in vals]),
        "gold_count": max(v["gold_count"] for v in vals),
        "per_trial": vals,
    }


def evaluate_all(raw: Path, audit_dir: Path, out: Path, script_path: Path):
    seal = load_and_verify_seal(raw, audit_dir, out, script_path)
    convs, corr = load_dataset(raw, audit_dir)
    qcohort = pd.read_csv(out / "V52_T4D_PRE_OUTCOME_QUESTION_COHORT.csv").set_index("question_id")

    # Stage 1: exact representation transfer for all 10 archives. No retrieval-quality metric is computed here.
    reps = {}
    rep_rows = []
    # Conversation archives are independent fit units. Parallel execution changes no
    # estimator, seed, ordering, or data dependency; results are re-keyed by conv_id.
    with ThreadPoolExecutor(max_workers=min(5, len(convs))) as ex:
        built = list(ex.map(build_representation, convs))
    for c, r in zip(convs, built):
        if r["mixed96_dim"] != 96 or not r["no_nan"]:
            raise RuntimeError(f"[BLOCKED — representation transfer incompatible] {c['conv_id']}")
        reps[c["conv_id"]] = r
        rep_rows.append({k: v for k, v in r.items() if k not in {"C", "QC", "qas", "id_to_row"}} | {"conv_id": c["conv_id"]})
    write_representation_transfer_proof(out, {
        "dataset_sha256": seal["dataset_sha256"],
        "audit_layer_manifest_sha256": seal["audit_layer_manifest_sha256"],
    }, "FULL_10_CONVERSATION_PRE_OUTCOME_FIT_PROOF", rep_rows)
    pd.DataFrame(rep_rows).to_csv(out / "V52_T4D_REPRESENTATION_TRANSFER_PROOF.csv", index=False)

    # Stage 2: mandatory controls/invariance for every conversation/query/seed, still before aggregate quality interpretation.
    sp_rows = []
    inv_rows = []
    prepared = {}
    for ci, c in enumerate(convs):
        r = reps[c["conv_id"]]
        C, QC, N = r["C"], r["QC"], r["N"]
        D0 = C >= 0
        Q0 = QC >= 0
        dist0 = np.count_nonzero(Q0[:, None, :] != D0[None, :, :], axis=2).astype(np.int16)
        priorities = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(N) for t in range(N_NUISANCE)]
        native_top = [topks_by_hamming(dist0[qi], priorities) for qi in range(len(QC))]

        # Signed permutation exact Hamming/ranking/top3 control.
        for seed in ROTATION_SEEDS:
            perm, sg = sp_spec(seed)
            Cr = sp_apply(C, perm, sg)
            Qr = sp_apply(QC, perm, sg)
            D = Cr >= 0
            Q = Qr >= 0
            dist = np.count_nonzero(Q[:, None, :] != D[None, :, :], axis=2).astype(np.int16)
            distances_exact = bool(np.array_equal(dist, dist0))
            # Identical Hamming-distance matrices plus identical independent priorities imply
            # identical full rankings/top3/metrics for every nuisance trial exactly.
            top3_exact = distances_exact
            ok = distances_exact and top3_exact
            sp_rows.append({
                "conv_id": c["conv_id"], "seed": seed,
                "hamming_distances_exact": int(distances_exact),
                "rank_top3_exact_all_questions_trials": int(top3_exact),
                "metrics_exact_implied_by_identical_top3": int(top3_exact),
                "status": "PASS" if ok else "FAIL",
            })
            if not ok:
                pd.DataFrame(sp_rows).to_csv(out / "V52_T4D_SIGNED_PERM_CONTROL.csv", index=False)
                raise RuntimeError(f"[BUG — HAMMING-INVARIANT CONTROL FAILED] {c['conv_id']} seed={seed}")

        # Full-96 Haar centered continuous geometry invariance.
        base_scores = cosine_scores(C, QC)
        dn = np.linalg.norm(C, axis=1)
        qn = np.linalg.norm(QC, axis=1)
        base_dots = QC @ C.T
        for seed in ROTATION_SEEDS:
            perm, qs = hspec(seed, 96)
            R = hmat(perm, qs, 96)
            Cr = happly(C, perm, qs, 96)
            Qr = happly(QC, perm, qs, 96)
            oe = float(np.max(np.abs(R.T @ R - np.eye(96))))
            nde = float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - dn)))
            qde = float(np.max(np.abs(np.linalg.norm(Qr, axis=1) - qn)))
            dotde = float(np.max(np.abs(Qr @ Cr.T - base_dots)))
            sc = cosine_scores(Cr, Qr)
            scorede = float(np.max(np.abs(sc - base_scores)))
            topok = bool(tie_aware_top3_equivalent(base_scores, sc, CONT_TOL))
            ok = oe <= CONT_TOL and nde <= CONT_TOL and qde <= CONT_TOL and dotde <= CONT_TOL and scorede <= CONT_TOL and topok
            inv_rows.append({
                "conv_id": c["conv_id"], "seed": seed,
                "orthogonality_max_abs_error": oe,
                "document_norm_max_abs_diff": nde,
                "query_norm_max_abs_diff": qde,
                "document_query_dot_max_abs_diff": dotde,
                "cosine_score_max_abs_diff": scorede,
                "continuous_top3_tie_sets_equivalent": int(topok),
                "status": "PASS" if ok else "FAIL",
            })
            if not ok:
                pd.DataFrame(inv_rows).to_csv(out / "V52_T4D_CONTINUOUS_INVARIANCE.csv", index=False)
                raise RuntimeError(f"[BUG — CONTINUOUS GEOMETRY NOT PRESERVED] {c['conv_id']} seed={seed}")
        prepared[c["conv_id"]] = {"D0": D0, "Q0": Q0, "dist0": dist0, "priorities": priorities, "native_top": native_top}

    pd.DataFrame(sp_rows).to_csv(out / "V52_T4D_SIGNED_PERM_CONTROL.csv", index=False)
    pd.DataFrame(inv_rows).to_csv(out / "V52_T4D_CONTINUOUS_INVARIANCE.csv", index=False)

    # Stage 3: frozen retrieval quality evaluation. No protocol branch may change after this point.
    trial_path = out / "V52_T4D_trial_results.csv"
    if trial_path.exists():
        trial_path.unlink()
    trial_header_written = False
    qrows = []
    collision_rows = []
    tie_rows = []
    rank_rows = []
    seed_qrows = []

    for ci, c in enumerate(convs):
        r = reps[c["conv_id"]]
        C, QC, qas, id_to_row = r["C"], r["QC"], r["qas"], r["id_to_row"]
        N = r["N"]
        pp = prepared[c["conv_id"]]
        D0, Q0, dist0, priorities, native_top = pp["D0"], pp["Q0"], pp["dist0"], pp["priorities"], pp["native_top"]

        method_cache = {"NATIVE_SIGN96": {None: (D0, Q0, dist0)}}
        for seed in ROTATION_SEEDS:
            perm, qs = hspec(seed, 96)
            Cr = happly(C, perm, qs, 96)
            Qr = happly(QC, perm, qs, 96)
            D = Cr >= 0; Q = Qr >= 0
            dist = np.count_nonzero(Q[:, None, :] != D[None, :, :], axis=2).astype(np.int16)
            method_cache.setdefault("HAAR96_SIGN", {})[seed] = (D, Q, dist)
        def _fit_itq_seed(seed):
            R = fit_itq(C, seed=seed)
            Cr = C @ R; Qr = QC @ R
            D = Cr >= 0; Q = Qr >= 0
            dist = np.count_nonzero(Q[:, None, :] != D[None, :, :], axis=2).astype(np.int16)
            return seed, D, Q, dist
        with ThreadPoolExecutor(max_workers=len(ITQ_SEEDS)) as ex:
            itq_fits = list(ex.map(_fit_itq_seed, ITQ_SEEDS))
        for seed, D, Q, dist in itq_fits:
            method_cache.setdefault("ITQ96_CENTERED", {})[seed] = (D, Q, dist)

        # Conversation-level code diagnostics, repeated only once per method/seed.
        for method, seeds in method_cache.items():
            for seed, (D, Q, dist) in seeds.items():
                cd = code_diag(D)
                collision_rows.append({"conv_id": c["conv_id"], "method": method, "seed": seed, "N_archive": N, **cd})

        conv_trial_rows = []
        for qi, q in enumerate(qas):
            qid = q["question_id"]
            raw_gold = evidence_rows(q["raw_evidence"], id_to_row)
            audit_gold = evidence_rows(q["correct_evidence"], id_to_row)
            meta = qcohort.loc[qid]
            base_tops = native_top[qi]
            native_raw = precompute_metric_arrays(base_tops, raw_gold)
            native_audit = precompute_metric_arrays(base_tops, audit_gold)

            # Native diagnostics.
            qd = query_diag(D0, Q0[qi], dist0[qi])
            tie_rows.append({"conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "method": "NATIVE_SIGN96", "seed": None, **qd})
            rank_rows.append({"conv_id": c["conv_id"], "question_id": qid, "method": "NATIVE_SIGN96", "seed": None, "spearman_hamming_distance_vs_native": 1.0, "mean_top3_overlap_vs_native": 1.0})

            # Trial rows for Native.
            for t in range(N_NUISANCE):
                rr, aa = native_raw["per_trial"][t], native_audit["per_trial"][t]
                conv_trial_rows.append({
                    "conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "archive_size": N,
                    "method": "NATIVE_SIGN96", "seed": None, "trial": t,
                    "raw_valid": rr["valid"], "raw_any_r3": rr["any"], "raw_all_r3": rr["all"], "raw_fractional_r3": rr["fractional"], "raw_gold_count": rr["gold_count"],
                    "audit_valid": aa["valid"], "audit_any_r3": aa["any"], "audit_all_r3": aa["all"], "audit_fractional_r3": aa["fractional"], "audit_gold_count": aa["gold_count"],
                })

            # Signed-permutation is recorded in the dedicated exact control CSV; duplicate
            # trial rows are intentionally omitted because the control proves byte-for-byte
            # identical Hamming distances and therefore identical top3/metrics.

            haar_seed_metrics = {}
            for seed in ROTATION_SEEDS:
                D, Q, dist = method_cache["HAAR96_SIGN"][seed]
                tops = topks_by_hamming(dist[qi], priorities)
                rm = precompute_metric_arrays(tops, raw_gold)
                am = precompute_metric_arrays(tops, audit_gold)
                haar_seed_metrics[seed] = {"raw": rm, "audit": am}
                rho = spearmanr(dist0[qi], dist[qi]).statistic
                if not np.isfinite(rho): rho = np.nan
                overlaps = [len(set(tops[t]) & set(base_tops[t])) / TOPK for t in range(N_NUISANCE)]
                rank_rows.append({"conv_id": c["conv_id"], "question_id": qid, "method": "HAAR96_SIGN", "seed": seed, "spearman_hamming_distance_vs_native": float(rho), "mean_top3_overlap_vs_native": float(np.mean(overlaps))})
                tie_rows.append({"conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "method": "HAAR96_SIGN", "seed": seed, **query_diag(D, Q[qi], dist[qi])})
                for t in range(N_NUISANCE):
                    rr, aa = rm["per_trial"][t], am["per_trial"][t]
                    conv_trial_rows.append({
                        "conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "archive_size": N,
                        "method": "HAAR96_SIGN", "seed": seed, "trial": t,
                        "raw_valid": rr["valid"], "raw_any_r3": rr["any"], "raw_all_r3": rr["all"], "raw_fractional_r3": rr["fractional"], "raw_gold_count": rr["gold_count"],
                        "audit_valid": aa["valid"], "audit_any_r3": aa["any"], "audit_all_r3": aa["all"], "audit_fractional_r3": aa["fractional"], "audit_gold_count": aa["gold_count"],
                    })
                seed_qrows.append({
                    "conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "method": "HAAR96_SIGN", "seed": seed,
                    "raw_any_r3": rm["any"], "raw_all_r3": rm["all"], "raw_fractional_r3": rm["fractional"],
                    "audit_any_r3": am["any"], "audit_all_r3": am["all"], "audit_fractional_r3": am["fractional"],
                })

            itq_seed_metrics = {}
            for seed in ITQ_SEEDS:
                D, Q, dist = method_cache["ITQ96_CENTERED"][seed]
                tops = topks_by_hamming(dist[qi], priorities)
                rm = precompute_metric_arrays(tops, raw_gold)
                am = precompute_metric_arrays(tops, audit_gold)
                itq_seed_metrics[seed] = {"raw": rm, "audit": am}
                rho = spearmanr(dist0[qi], dist[qi]).statistic
                if not np.isfinite(rho): rho = np.nan
                overlaps = [len(set(tops[t]) & set(base_tops[t])) / TOPK for t in range(N_NUISANCE)]
                rank_rows.append({"conv_id": c["conv_id"], "question_id": qid, "method": "ITQ96_CENTERED", "seed": seed, "spearman_hamming_distance_vs_native": float(rho), "mean_top3_overlap_vs_native": float(np.mean(overlaps))})
                tie_rows.append({"conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "method": "ITQ96_CENTERED", "seed": seed, **query_diag(D, Q[qi], dist[qi])})
                for t in range(N_NUISANCE):
                    rr, aa = rm["per_trial"][t], am["per_trial"][t]
                    conv_trial_rows.append({
                        "conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "archive_size": N,
                        "method": "ITQ96_CENTERED", "seed": seed, "trial": t,
                        "raw_valid": rr["valid"], "raw_any_r3": rr["any"], "raw_all_r3": rr["all"], "raw_fractional_r3": rr["fractional"], "raw_gold_count": rr["gold_count"],
                        "audit_valid": aa["valid"], "audit_any_r3": aa["any"], "audit_all_r3": aa["all"], "audit_fractional_r3": aa["fractional"], "audit_gold_count": aa["gold_count"],
                    })
                seed_qrows.append({
                    "conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "method": "ITQ96_CENTERED", "seed": seed,
                    "raw_any_r3": rm["any"], "raw_all_r3": rm["all"], "raw_fractional_r3": rm["fractional"],
                    "audit_any_r3": am["any"], "audit_all_r3": am["all"], "audit_fractional_r3": am["fractional"],
                })

            def seed_mean(seedmetrics, mode, metric):
                return mean_or_nan([seedmetrics[s][mode][metric] for s in seedmetrics])

            qrows.append({
                "conv_id": c["conv_id"], "question_id": qid, "category": q["category"], "archive_size": N,
                "archive_size_quartile": int(meta["archive_size_quartile"]),
                "audit_gold_count": len(audit_gold), "gold_cardinality_stratum": "one" if len(audit_gold) == 1 else ("multi" if len(audit_gold) > 1 else "invalid_zero"),
                "raw_evidence_valid": int(bool(raw_gold)), "audit_evidence_valid": int(bool(audit_gold)),
                "native_raw_any_r3": native_raw["any"], "native_raw_all_r3": native_raw["all"], "native_raw_fractional_r3": native_raw["fractional"],
                "native_audit_any_r3": native_audit["any"], "native_audit_all_r3": native_audit["all"], "native_audit_fractional_r3": native_audit["fractional"],
                "haar_raw_any_r3": seed_mean(haar_seed_metrics, "raw", "any"), "haar_raw_all_r3": seed_mean(haar_seed_metrics, "raw", "all"), "haar_raw_fractional_r3": seed_mean(haar_seed_metrics, "raw", "fractional"),
                "haar_audit_any_r3": seed_mean(haar_seed_metrics, "audit", "any"), "haar_audit_all_r3": seed_mean(haar_seed_metrics, "audit", "all"), "haar_audit_fractional_r3": seed_mean(haar_seed_metrics, "audit", "fractional"),
                "itq_raw_any_r3": seed_mean(itq_seed_metrics, "raw", "any"), "itq_raw_all_r3": seed_mean(itq_seed_metrics, "raw", "all"), "itq_raw_fractional_r3": seed_mean(itq_seed_metrics, "raw", "fractional"),
                "itq_audit_any_r3": seed_mean(itq_seed_metrics, "audit", "any"), "itq_audit_all_r3": seed_mean(itq_seed_metrics, "audit", "all"), "itq_audit_fractional_r3": seed_mean(itq_seed_metrics, "audit", "fractional"),
            })

        # Streaming trial CSV to bound memory.
        tdf = pd.DataFrame(conv_trial_rows)
        tdf.to_csv(trial_path, mode="a", header=not trial_header_written, index=False)
        trial_header_written = True
        print(f"QUALITY_DONE {c['conv_id']} questions={len(qas)} trial_rows={len(tdf)}", flush=True)

    qdf = pd.DataFrame(qrows).sort_values(["conv_id", "question_id"]).reset_index(drop=True)
    qdf.to_csv(out / "V52_T4D_question_level.csv", index=False)
    sq = pd.DataFrame(seed_qrows)

    # Aggregates are means of question-level nuisance-collapsed quantities; audit-clean is primary.
    agg_rows = []
    def add_agg(method, mode, prefix):
        valid = qdf[f"{prefix}_{mode}_fractional_r3"].notna()
        agg_rows.append({
            "method": method, "evidence_mode": mode, "questions_valid": int(valid.sum()),
            "ANY_R3": float(qdf.loc[valid, f"{prefix}_{mode}_any_r3"].mean()),
            "ALL_R3": float(qdf.loc[valid, f"{prefix}_{mode}_all_r3"].mean()),
            "Fractional_R3": float(qdf.loc[valid, f"{prefix}_{mode}_fractional_r3"].mean()),
        })
    for mode in ["raw", "audit"]:
        add_agg("NATIVE_SIGN96", mode, "native")
        add_agg("HAAR96_SIGN_MEAN", mode, "haar")
        add_agg("ITQ96_CENTERED_MEAN", mode, "itq")
    agg = pd.DataFrame(agg_rows)
    agg.to_csv(out / "V52_T4D_aggregate.csv", index=False)

    # Seed results.
    hseed_rows = []
    for method, seeds in [("HAAR96_SIGN", ROTATION_SEEDS), ("ITQ96_CENTERED", ITQ_SEEDS)]:
        for seed in seeds:
            z = sq[(sq.method == method) & (sq.seed == seed)]
            for mode in ["raw", "audit"]:
                hseed_rows.append({
                    "method": method, "seed": seed, "evidence_mode": mode,
                    "questions_valid": int(z[f"{mode}_fractional_r3"].notna().sum()),
                    "ANY_R3": float(z[f"{mode}_any_r3"].mean()),
                    "ALL_R3": float(z[f"{mode}_all_r3"].mean()),
                    "Fractional_R3": float(z[f"{mode}_fractional_r3"].mean()),
                })
    seedres = pd.DataFrame(hseed_rows)
    seedres[seedres.method == "HAAR96_SIGN"].to_csv(out / "V52_T4D_HAAR_SEED_RESULTS.csv", index=False)

    # Collision/tie/rank diagnostics.
    pd.DataFrame(collision_rows).to_csv(out / "V52_T4D_collision_diagnostics.csv", index=False)
    pd.DataFrame(tie_rows).to_csv(out / "V52_T4D_tie_diagnostics.csv", index=False)
    pd.DataFrame(rank_rows).to_csv(out / "V52_T4D_rank_geometry.csv", index=False)

    # ITQ vs Haar envelope.
    native = float(agg[(agg.method == "NATIVE_SIGN96") & (agg.evidence_mode == "audit")].Fractional_R3.iloc[0])
    haar = float(agg[(agg.method == "HAAR96_SIGN_MEAN") & (agg.evidence_mode == "audit")].Fractional_R3.iloc[0])
    itq = float(agg[(agg.method == "ITQ96_CENTERED_MEAN") & (agg.evidence_mode == "audit")].Fractional_R3.iloc[0])
    hs = seedres[(seedres.method == "HAAR96_SIGN") & (seedres.evidence_mode == "audit")].sort_values("seed")
    iseed = seedres[(seedres.method == "ITQ96_CENTERED") & (seedres.evidence_mode == "audit")].sort_values("seed")
    hmin, hmax = float(hs.Fractional_R3.min()), float(hs.Fractional_R3.max())
    env = "BELOW" if itq < hmin else ("ABOVE" if itq > hmax else "WITHIN")
    pd.DataFrame([{
        "ITQ96_fractional_R3": itq, "HAAR96_min_seed_fractional_R3": hmin, "HAAR96_max_seed_fractional_R3": hmax,
        "ITQ_vs_HAAR_envelope": env,
        "ITQ_native_rank_spearman_mean": pd.DataFrame(rank_rows).query("method == 'ITQ96_CENTERED'").spearman_hamming_distance_vs_native.mean(),
        "HAAR96_native_rank_spearman_mean": pd.DataFrame(rank_rows).query("method == 'HAAR96_SIGN'").spearman_hamming_distance_vs_native.mean(),
    }]).to_csv(out / "V52_T4D_ITQ_HAAR_ENVELOPE.csv", index=False)

    # Strata: native-minus-mean-Haar96, audit-clean, valid only.
    valid = qdf.native_audit_fractional_r3.notna() & qdf.haar_audit_fractional_r3.notna()
    qdf["native_minus_haar_pp"] = (qdf.native_audit_fractional_r3 - qdf.haar_audit_fractional_r3) * 100.0
    qdf["haar_minus_native_pp"] = -qdf["native_minus_haar_pp"]

    def strata(col, path):
        rows = []
        for key, z in qdf[valid].groupby(col, dropna=False):
            rows.append({
                col: key, "questions_valid": len(z),
                "native_fractional_R3": z.native_audit_fractional_r3.mean(),
                "haar96_mean_fractional_R3": z.haar_audit_fractional_r3.mean(),
                "native_minus_haar_pp": z.native_minus_haar_pp.mean(),
            })
        pd.DataFrame(rows).to_csv(path, index=False)
    strata("category", out / "V52_T4D_strata_category.csv")
    strata("conv_id", out / "V52_T4D_strata_conversation.csv")
    strata("archive_size_quartile", out / "V52_T4D_strata_archive_size.csv")
    gvalid = valid & qdf.gold_cardinality_stratum.isin(["one", "multi"])
    grow = []
    for key, z in qdf[gvalid].groupby("gold_cardinality_stratum"):
        grow.append({"gold_cardinality_stratum": key, "questions_valid": len(z), "native_fractional_R3": z.native_audit_fractional_r3.mean(), "haar96_mean_fractional_R3": z.haar_audit_fractional_r3.mean(), "native_minus_haar_pp": z.native_minus_haar_pp.mean()})
    pd.DataFrame(grow).to_csv(out / "V52_T4D_strata_gold_cardinality.csv", index=False)

    # Composition sensitivity.
    z = qdf[valid].copy()
    eps = 1e-12
    W = int((z.native_minus_haar_pp > eps).sum())
    L = int((z.native_minus_haar_pp < -eps).sum())
    T = int(len(z) - W - L)
    comp = [{"analysis": "all", "questions": len(z), "native_minus_haar_mean_pp": z.native_minus_haar_pp.mean(), "native_minus_haar_median_pp": z.native_minus_haar_pp.median(), "W_native_better": W, "T": T, "L_native_worse": L}]
    pos = z.sort_values(["native_minus_haar_pp", "question_id"], ascending=[False, True], kind="mergesort")
    for nremove in [10, 25, 50]:
        rem_ids = set(pos[pos.native_minus_haar_pp > 0].head(nremove).question_id)
        r = z[~z.question_id.isin(rem_ids)]
        comp.append({"analysis": f"remove_top_{nremove}_native_positive_contributors", "questions": len(r), "native_minus_haar_mean_pp": r.native_minus_haar_pp.mean(), "native_minus_haar_median_pp": r.native_minus_haar_pp.median(), "W_native_better": int((r.native_minus_haar_pp > eps).sum()), "T": int((np.abs(r.native_minus_haar_pp) <= eps).sum()), "L_native_worse": int((r.native_minus_haar_pp < -eps).sum())})
    compdf = pd.DataFrame(comp)
    compdf.to_csv(out / "V52_T4D_COMPOSITION_SENSITIVITY.csv", index=False)

    # Protocol-defect/correction sensitivity, pre-defined on common-valid q only.
    common = qdf.raw_evidence_valid.eq(1) & qdf.audit_evidence_valid.eq(1)
    defect_rows = []
    for label, rawcol, audcol in [
        ("NATIVE_SIGN96", "native_raw_fractional_r3", "native_audit_fractional_r3"),
        ("HAAR96_SIGN_MEAN", "haar_raw_fractional_r3", "haar_audit_fractional_r3"),
        ("ITQ96_CENTERED_MEAN", "itq_raw_fractional_r3", "itq_audit_fractional_r3"),
    ]:
        rz, az = qdf.loc[common, rawcol].mean(), qdf.loc[common, audcol].mean()
        defect_rows.append({"arm": label, "questions_common_valid": int(common.sum()), "raw_fractional_R3": rz, "audit_fractional_R3": az, "audit_minus_raw_pp": (az-rz)*100, "abs_effect_pp": abs(az-rz)*100})
    for method, seeds in [("HAAR96_SIGN", ROTATION_SEEDS), ("ITQ96_CENTERED", ITQ_SEEDS)]:
        for seed in seeds:
            zseed = sq[(sq.method == method) & (sq.seed == seed)].set_index("question_id").reindex(qdf.question_id)
            mask = common.to_numpy()
            rv = zseed.raw_fractional_r3.to_numpy()[mask]
            av = zseed.audit_fractional_r3.to_numpy()[mask]
            rz, az = float(np.nanmean(rv)), float(np.nanmean(av))
            defect_rows.append({"arm": f"{method}_seed{seed}", "questions_common_valid": int(common.sum()), "raw_fractional_R3": rz, "audit_fractional_R3": az, "audit_minus_raw_pp": (az-rz)*100, "abs_effect_pp": abs(az-rz)*100})
    defect = pd.DataFrame(defect_rows)
    defect.to_csv(out / "V52_T4D_PROTOCOL_DEFECT_SENSITIVITY.csv", index=False)
    max_defect = float(defect.abs_effect_pp.max())

    # Decision.
    Dpp = (haar - native) * 100.0
    hsvals = {int(r.seed): float(r.Fractional_R3) for _, r in hs.iterrows()}
    all_below = all(v < native for v in hsvals.values())
    if Dpp <= -5.0 and all_below:
        verdict = "[STRONG CROSS-BENCHMARK REPLICATION — NATIVE AXES MATTER ON LOCOMO]"
    elif Dpp < -1.0:
        verdict = "[PARTIAL / MIXED DIRECTIONAL REPLICATION ON LOCOMO]"
    elif abs(Dpp) <= 1.0:
        verdict = "[NO MATERIAL LOCOMO REPLICATION]"
    else:
        verdict = "[FALSIFIED IN THIS DIRECTION — FULL HAAR IMPROVES SIGN RETRIEVAL ON LOCOMO]"

    # Re-write question-level with paired gap columns included.
    qdf.to_csv(out / "V52_T4D_question_level.csv", index=False)

    # Head researcher handoff/report values.
    max_inv = float(pd.DataFrame(inv_rows)[["orthogonality_max_abs_error", "document_norm_max_abs_diff", "query_norm_max_abs_diff", "document_query_dot_max_abs_diff", "cosine_score_max_abs_diff"]].to_numpy().max())
    median_gap = float(z.native_minus_haar_pp.median())
    top50 = float(compdf[compdf.analysis == "remove_top_50_native_positive_contributors"].native_minus_haar_mean_pp.iloc[0])
    catdf = pd.read_csv(out / "V52_T4D_strata_category.csv").sort_values("category")
    convdf = pd.read_csv(out / "V52_T4D_strata_conversation.csv").sort_values("conv_id")
    catdir = "; ".join(f"Cat{int(r.category)}:{r.native_minus_haar_pp:+.6f}pp" for _, r in catdf.iterrows())
    convgaps = "; ".join(f"{r.conv_id}:{r.native_minus_haar_pp:+.6f}pp" for _, r in convdf.iterrows())

    report = f"""# V52 Task 4D Compute Report\n\nSTATUS: COMPLETE\n\nPrimary frozen audit-clean cohort identity: 10 conversations / 1,540 Cat1-Cat4 questions; retrievable-evidence-valid audit-clean questions={int(valid.sum())}.\n\nNATIVE_SIGN96 Fractional Evidence Recall@3: {native:.12%}\nHAAR96 mean Fractional Evidence Recall@3: {haar:.12%}\nD_LoCoMo = Haar - Native: {Dpp:+.9f} pp\nHAAR seed values: {hsvals}\nAll 5 Haar seeds below native: {'YES' if all_below else 'NO'}\nPre-registered verdict: {verdict}\nSigned-permutation control: PASS exactly.\nCentered continuous invariance: PASS; maximum observed error={max_inv:.3e}.\nNative-vs-mean-Haar W/T/L: {W}/{T}/{L}.\nMedian paired native-minus-Haar gap: {median_gap:+.9f} pp.\nTop-50-removed residual native advantage: {top50:+.9f} pp.\nITQ96 mean Fractional Evidence Recall@3: {itq:.12%}; ITQ vs Haar envelope={env}.\nCategory gaps (native-minus-Haar): {catdir}\nConversation gaps (native-minus-Haar): {convgaps}\nMaximum observed protocol defect/correction effect (pre-defined common-valid raw-vs-audit sensitivity): {max_defect:.9f} pp.\n\nInterpretation ceiling: this is a fixed-benchmark cross-benchmark falsification/replication result. It does not license universal native-axis superiority, population generalization, or a causal claim about variance/collisions/ties.\n"""
    (out / "V52_T4D_COMPUTE_REPORT.md").write_text(report, encoding="utf-8")

    # Copy the byte-identical sealed script into canonical outputs before manifest.
    sealed_copy = out / "v52_t4d_locomo_frozen_cross_benchmark.py"
    shutil.copy2(script_path, sealed_copy)
    if sha256_file(sealed_copy) != seal["sealed_compute_script_sha256"]:
        raise RuntimeError("[PROTOCOL SEAL FAILURE] copied script hash mismatch")

    pre_sha = sha256_file(out / "V52_T4D_PRE_RUN_SEAL.json")
    script_sha = sha256_file(sealed_copy)

    # Handoff initially uses placeholder Drive folder; uploader can patch only the handoff/report after run? No: post-seal code is frozen, but outputs may be completed after compute.
    # To preserve canonical hashes, the compute handoff records LOCAL_PENDING_UPLOAD; external upload does not alter file bytes.
    hand = f"""TASK: V52 TASK 4D — LOCOMO FROZEN CROSS-BENCHMARK REPLICATION\nSTATUS: COMPLETE\nDATASET SHA: {DATASET_SHA256}\nCOHORT: {len(qdf)} / 1540\nSIGNED-PERM CONTROL: PASS\nCONTINUOUS INVARIANCE: PASS; MAX ERROR={max_inv:.17g}\nNATIVE FRACTIONAL R@3: {native*100:.12f}%\nHAAR96 MEAN FRACTIONAL R@3: {haar*100:.12f}%\nD_LOCOMO: {Dpp:+.12f} pp\nHAAR SEEDS: {('; '.join(f'{s}:{hsvals[s]*100:.12f}%' for s in ROTATION_SEEDS))}\nALL FIVE HAAR SEEDS BELOW NATIVE: {'YES' if all_below else 'NO'}\nPRE-REGISTERED VERDICT: {verdict}\nNATIVE-vs-HAAR W/T/L: {W}/{T}/{L}\nMEDIAN PAIRED GAP: {median_gap:+.12f} pp\nTOP50-REMOVED RESIDUAL NATIVE ADVANTAGE: {top50:+.12f} pp\nITQ96 FRACTIONAL R@3: {itq*100:.12f}%\nITQ vs HAAR ENVELOPE: {env}\nCATEGORY STRATA DIRECTION: {catdir}\n10 CONVERSATION GAPS: {convgaps}\nMAX OBSERVED PROTOCOL DEFECT EFFECT: {max_defect:.12f} pp (pre-defined common-valid raw-vs-audit Fractional R@3 sensitivity)\nOUTPUT DRIVE FOLDER: LOCAL_PENDING_UPLOAD\nPRE-RUN SEAL SHA256: {pre_sha}\nSEALED SCRIPT SHA256: {script_sha}\nPOST-RUN MANIFEST SHA256: MANIFEST_HASH_REPORTED_EXTERNALLY_AFTER_WRITE\n"""
    (out / "V52_T4D_HEAD_RESEARCHER_HANDOFF.txt").write_text(hand, encoding="utf-8")

    required_atomic = [
        "V52_T4D_PRE_RUN_SEAL.json", "v52_t4d_locomo_frozen_cross_benchmark.py", "V52_T4D_INPUT_CHECKS.csv",
        "V52_T4D_REPRESENTATION_TRANSFER_PROOF.csv", "V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt",
        "V52_T4D_trial_results.csv", "V52_T4D_question_level.csv", "V52_T4D_aggregate.csv",
        "V52_T4D_HAAR_SEED_RESULTS.csv", "V52_T4D_SIGNED_PERM_CONTROL.csv", "V52_T4D_CONTINUOUS_INVARIANCE.csv",
        "V52_T4D_ITQ_HAAR_ENVELOPE.csv", "V52_T4D_collision_diagnostics.csv", "V52_T4D_tie_diagnostics.csv",
        "V52_T4D_rank_geometry.csv", "V52_T4D_strata_category.csv", "V52_T4D_strata_conversation.csv",
        "V52_T4D_strata_gold_cardinality.csv", "V52_T4D_strata_archive_size.csv", "V52_T4D_COMPOSITION_SENSITIVITY.csv",
        "V52_T4D_COMPUTE_REPORT.md", "V52_T4D_HEAD_RESEARCHER_HANDOFF.txt",
        "V52_T4D_PRE_OUTCOME_QUESTION_COHORT.csv", "V52_T4D_ARCHIVE_SIZE_QUARTILES_FROZEN.csv",
        "V52_T4D_PROTOCOL_DEFECT_SENSITIVITY.csv",
    ]
    missing = [x for x in required_atomic if not (out / x).exists()]
    if missing:
        raise RuntimeError("Missing required outputs: " + str(missing))

    manifest = {
        "task": TASK,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE",
        "canonical_parent_git_commit": CANONICAL_PARENT_COMMIT,
        "github_preregistration_commit": PREREG_COMMIT,
        "dataset_sha256": DATASET_SHA256,
        "cohort_questions": len(qdf),
        "audit_clean_evidence_valid_questions": int(valid.sum()),
        "signed_permutation_control": "PASS",
        "continuous_invariance": "PASS",
        "continuous_invariance_max_error": max_inv,
        "native_fractional_R3": native,
        "haar96_mean_fractional_R3": haar,
        "D_LoCoMo_pp": Dpp,
        "haar_seed_fractional_R3": hsvals,
        "all_five_haar_seeds_below_native": all_below,
        "pre_registered_verdict": verdict,
        "native_vs_haar_WTL": [W, T, L],
        "median_paired_native_minus_haar_pp": median_gap,
        "top50_removed_residual_native_advantage_pp": top50,
        "itq96_fractional_R3": itq,
        "itq_vs_haar_envelope": env,
        "max_observed_protocol_defect_effect_pp": max_defect,
        "pre_run_seal_sha256": pre_sha,
        "sealed_script_sha256": script_sha,
        "final_script_sha256": sha256_file(script_path),
        "script_hash_match": script_sha == sha256_file(script_path) == seal["sealed_compute_script_sha256"],
        "atomic_output_hashes": {name: sha256_file(out / name) for name in required_atomic},
        "manifest_self_hash_note": "Self-hash is reported externally because a file cannot contain its own SHA256 without recursion.",
        "zip_hash_note": "The aggregate ZIP is created after this manifest and is a packaging derivative; its hash is reported externally.",
    }
    manpath = out / "V52_T4D_POST_RUN_MANIFEST.json"
    manpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    mansha = sha256_file(manpath)

    # Packaging derivative includes manifest and every canonical atomic output.
    zpath = out / "V52_T4D_ALL_OUTPUTS.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(out.iterdir()):
            if p.is_file() and p.name != zpath.name:
                zf.write(p, arcname=p.name)
    zipsha = sha256_file(zpath)
    (out / "V52_T4D_POST_RUN_HASHES.txt").write_text(
        f"POST_RUN_MANIFEST_SHA256={mansha}\nALL_OUTPUTS_ZIP_SHA256={zipsha}\n",
        encoding="utf-8",
    )

    print("TASK4D_COMPLETE")
    print("VERDICT", verdict)
    print("NATIVE", native)
    print("HAAR", haar)
    print("D_LOCOMO_PP", Dpp)
    print("MANIFEST_SHA256", mansha)
    print("ZIP_SHA256", zipsha)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["seal", "run"])
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--audit-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    script_path = Path(__file__).resolve()
    if args.mode == "seal":
        make_seal(args.raw, args.audit_dir, args.out, script_path)
    else:
        evaluate_all(args.raw, args.audit_dir, args.out, script_path)


if __name__ == "__main__":
    main()
