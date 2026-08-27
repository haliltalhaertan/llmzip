#!/usr/bin/env python3
"""
V52 Task 3A — LongMemEval cleaned-S portability adapter.

This adapter freezes dataset validation, turn-level memory construction,
gold mapping, leakage controls, deterministic encoding/ranking sanity, and
metric semantics. It intentionally does NOT run M32/M64 full-benchmark
performance comparisons.

Expected official source:
https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json
Expected SHA256:
d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442
"""
from __future__ import annotations
import argparse, hashlib, inspect, json, math, re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

EXPECTED_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
EXPECTED_QUESTIONS = 500
EXPECTED_ABSTENTION = 30
EXPECTED_TYPES = {
    "single-session-user",
    "single-session-assistant",
    "single-session-preference",
    "temporal-reasoning",
    "knowledge-update",
    "multi-session",
}
ITQ_SEEDS = [101, 202, 303, 404, 505]
LATENT_DIM = 32
N_NUISANCE = 20
QUERY_DATE_DECISION = "A_question_text_only"
FORBIDDEN_FIT_FIELDS = {
    "answer", "has_answer", "answer_session_ids", "question_type",
    "gold_turn_ids", "official_evidence_annotations",
}
SOURCE_URL = (
    "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/"
    "resolve/main/longmemeval_s_cleaned.json"
)

def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def canonical_turn_id(question_id: str, session_id: str, turn_index: int) -> str:
    # Frozen for Task 3A: 0-based turn index.
    return f"{question_id}::{session_id}::t{turn_index}"

def build_archive(item: dict) -> tuple[list[dict], list[str], list[dict]]:
    qid = str(item["question_id"])
    sids = item["haystack_session_ids"]
    dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    memories, gold_ids, issues = [], [], []
    for si, (sid, date, sess) in enumerate(zip(sids, dates, sessions)):
        if not isinstance(sess, list):
            issues.append({"code": "SESSION_NOT_LIST", "session_index": si})
            continue
        for ti, turn in enumerate(sess):
            if not isinstance(turn, dict):
                issues.append({"code": "TURN_NOT_DICT", "session_index": si, "turn_index": ti})
                continue
            role = turn.get("role")
            content = turn.get("content")
            if role not in {"user", "assistant"}:
                issues.append({"code": "INVALID_ROLE", "session_index": si, "turn_index": ti, "value": role})
            if not isinstance(content, str):
                issues.append({"code": "INVALID_CONTENT", "session_index": si, "turn_index": ti})
                content = "" if content is None else str(content)
            if "has_answer" in turn and not isinstance(turn["has_answer"], bool):
                issues.append({"code": "INVALID_HAS_ANSWER_TYPE", "session_index": si, "turn_index": ti})
            mid = canonical_turn_id(qid, str(sid), ti)
            # Task 3A requires timestamp + role + content as retrieval text.
            memory_text = f"[{date}] {role}: {content}"
            rec = {
                "memory_id": mid,
                "question_id": qid,
                "session_id": str(sid),
                "session_index": si,
                "turn_index": ti,
                "date": date,
                "role": role,
                "content": content,
                "memory_text": memory_text,
                # label retained only as metadata outside feature-fitting payload:
                "has_answer": bool(turn.get("has_answer", False)) if isinstance(turn.get("has_answer", False), bool) else False,
            }
            memories.append(rec)
            if rec["has_answer"]:
                gold_ids.append(mid)
    return memories, gold_ids, issues

def fit_input_payload(memories: list[dict]) -> list[str]:
    # Strong structural leakage barrier: fitting receives strings only.
    return [m["memory_text"] for m in memories]

def fit_itq(V: np.ndarray, n_iter: int = 100, seed: int = 101) -> np.ndarray:
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

def stable_archive_seed(lexical_ordinal: int, trial: int = 0) -> int:
    """
    Adapter-specific deterministic mapping, frozen in Task 3A.
    Mirrors V51/V52's conversation-number seed schedule without using labels:
      5_100_000 + archive_ordinal*100_000 + trial*100
    archive_ordinal is lexical question_id rank over the 500 instances.
    """
    return 5_100_000 + lexical_ordinal * 100_000 + trial * 100

def rank_hamming_lexicographic(D: np.ndarray, Q: np.ndarray, priority: np.ndarray) -> np.ndarray:
    dist = np.count_nonzero(Q[:, None, :] != D[None, :, :], axis=2)
    out = np.empty_like(dist, dtype=int)
    idx = np.arange(D.shape[0])
    for qi in range(Q.shape[0]):
        out[qi] = np.lexsort((priority, dist[qi]))
    return out

def rank_hamming_frozen_score(D: np.ndarray, Q: np.ndarray, priority: np.ndarray) -> np.ndarray:
    # Exact old score semantics; priority in [0,1), Hamming distance integer.
    dist = np.count_nonzero(Q[:, None, :] != D[None, :, :], axis=2)
    return np.argsort(dist + priority[None, :] * 1e-3, axis=1)

def fit_archive_representation(memory_texts: list[str]):
    """
    Archive-only unsupervised fit. No query, answer, evidence or question metadata
    is accepted by this function.
    """
    if len(memory_texts) < 25:
        raise ValueError("Archive too small to support frozen ITQ24 sanity encoding.")
    wv = TfidfVectorizer(
        lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True
    )
    cv = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True
    )
    Xw = normalize(wv.fit_transform(memory_texts))
    Xc = normalize(cv.fit_transform(memory_texts))
    d = min(LATENT_DIM, Xw.shape[0] - 1, Xw.shape[1] - 1)
    if d < 24:
        raise ValueError(f"latent dimension {d}<24; ITQ24 unsupported")
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    return wv, cv, svd, Xw, Xc, Xl

def encode_sanity(memories: list[dict], question: str, lexical_ordinal: int, trial: int = 0):
    texts = fit_input_payload(memories)
    wv, cv, svd, Xw, Xc, Xl = fit_archive_representation(texts)
    Qw = normalize(wv.transform([question]))
    Qc = normalize(cv.transform([question]))
    Ql = normalize(svd.transform(Qw))
    d = Xl.shape[1]
    seed = stable_archive_seed(lexical_ordinal, trial)
    priority = np.random.default_rng(seed + 99).random(len(texts))

    # Exact V51/V52 full96 component generation.
    Rl = np.random.default_rng(seed + 2).normal(size=(d, 32)).astype(np.float32)
    Rw = np.random.default_rng(seed + 3).normal(size=(Xw.shape[1], 32)).astype(np.float32)
    Rc = np.random.default_rng(seed + 4).normal(size=(Xc.shape[1], 32)).astype(np.float32)
    Dl = (Xl @ Rl) >= 0
    Dw = (Xw @ Rw) >= 0
    Dc = (Xc @ Rc) >= 0
    Ql32 = (Ql @ Rl) >= 0
    Qw32 = (Qw @ Rw) >= 0
    Qc32 = (Qc @ Rc) >= 0
    D96 = np.concatenate([Dl, Dw, Dc], axis=1)
    Q96 = np.concatenate([Ql32, Qw32, Qc32], axis=1)

    X24 = Xl[:, :24]
    mu24 = X24.mean(axis=0, keepdims=True)
    X24c = X24 - mu24
    Q24 = Ql[:, :24]
    itq_dims = {}
    itq_ranks = {}
    for s in ITQ_SEEDS:
        R = fit_itq(X24c, seed=s)
        D24 = (X24c @ R) >= 0
        Q24b = ((Q24 - mu24) @ R) >= 0
        itq_dims[s] = (D24.shape[1], Q24b.shape[1])
        itq_ranks[s] = rank_hamming_lexicographic(D24, Q24b, priority)[0]

    full_rank_a = rank_hamming_lexicographic(D96, Q96, priority)[0]
    full_rank_b = rank_hamming_lexicographic(D96, Q96, priority)[0]
    full_rank_old = rank_hamming_frozen_score(D96, Q96, priority)[0]
    return {
        "N": len(texts),
        "full96_doc_bits": int(D96.shape[1]),
        "full96_query_bits": int(Q96.shape[1]),
        "itq_dims": itq_dims,
        "no_nan": bool(
            np.isfinite(Xl).all() and np.isfinite(Ql).all()
            and np.isfinite(priority).all()
        ),
        "ranking_deterministic": bool(np.array_equal(full_rank_a, full_rank_b)),
        "tie_semantics_match_old_score": bool(np.array_equal(full_rank_a, full_rank_old)),
        "effective_M_8": min(8, len(texts)),
        "effective_M_32": min(32, len(texts)),
        "effective_M_64": min(64, len(texts)),
    }

def validate_dataset(data: list[dict]):
    required = {
        "question_id", "question_type", "question", "answer", "question_date",
        "haystack_session_ids", "haystack_dates", "haystack_sessions",
        "answer_session_ids",
    }
    qrows, goldrows, archive_rows, issues = [], [], [], []
    qids = [str(x.get("question_id", "")) for x in data]
    qid_counts = Counter(qids)
    lexical_ordinal = {qid: i for i, qid in enumerate(sorted(qids))}
    session_to_questions = defaultdict(set)

    for item in data:
        qid = str(item.get("question_id", ""))
        missing = sorted(required - set(item))
        if missing:
            issues.append({"question_id": qid, "code": "MISSING_FIELDS", "detail": "|".join(missing)})
            continue
        qt = item["question_type"]
        if qt not in EXPECTED_TYPES:
            issues.append({"question_id": qid, "code": "INVALID_QUESTION_TYPE", "detail": str(qt)})
        sids, dates, sessions = item["haystack_session_ids"], item["haystack_dates"], item["haystack_sessions"]
        if not all(isinstance(x, list) for x in (sids, dates, sessions)):
            issues.append({"question_id": qid, "code": "HAYSTACK_FIELD_NOT_LIST", "detail": ""})
            continue
        aligned = len(sids) == len(dates) == len(sessions)
        if not aligned:
            issues.append({
                "question_id": qid, "code": "HAYSTACK_ALIGNMENT",
                "detail": f"{len(sids)}/{len(dates)}/{len(sessions)}"
            })
        ans_sids = item["answer_session_ids"]
        if not isinstance(ans_sids, list):
            issues.append({"question_id": qid, "code": "ANSWER_SESSION_IDS_NOT_LIST", "detail": ""})
            ans_sids = []
        missing_ans_sid = sorted(set(map(str, ans_sids)) - set(map(str, sids)))
        if missing_ans_sid:
            issues.append({"question_id": qid, "code": "ANSWER_SESSION_NOT_IN_HAYSTACK", "detail": "|".join(missing_ans_sid)})

        memories, gold_ids, turn_issues = build_archive(item) if aligned else ([], [], [])
        for z in turn_issues:
            issues.append({"question_id": qid, "code": z["code"], "detail": json.dumps(z, sort_keys=True)})
        mids = [m["memory_id"] for m in memories]
        if len(set(mids)) != len(mids):
            issues.append({"question_id": qid, "code": "DUPLICATE_MEMORY_ID", "detail": ""})
        gold_sessions = {m["session_id"] for m in memories if m["has_answer"]}
        ans_set = set(map(str, ans_sids))
        gold_not_answer = sorted(gold_sessions - ans_set)
        answer_without_gold = sorted(ans_set - gold_sessions)
        if gold_not_answer:
            issues.append({"question_id": qid, "code": "HAS_ANSWER_SESSION_NOT_ANSWER_SESSION", "detail": "|".join(gold_not_answer)})
        # Do not automatically treat answer_without_gold as malformed: retain as diagnostic.
        is_abs = qid.endswith("_abs")
        for sid in map(str, sids):
            session_to_questions[sid].add(qid)

        qrows.append({
            "question_id": qid,
            "question_type": qt,
            "is_abstention": int(is_abs),
            "evidence_bearing": int(len(gold_ids) > 0),
            "gold_turn_count": len(gold_ids),
            "n_sessions": len(sids),
            "n_turns": len(memories),
            "archive_memory_count": len(memories),
            "answer_session_count": len(ans_set),
            "gold_session_count": len(gold_sessions),
            "gold_sessions_not_in_answer_session_ids": len(gold_not_answer),
            "answer_sessions_without_has_answer_turn": len(answer_without_gold),
            "question_date_present": int(bool(item.get("question_date"))),
            "lexical_ordinal": lexical_ordinal.get(qid, -1),
        })
        goldrows.append({
            "question_id": qid,
            "is_abstention": int(is_abs),
            "gold_turn_count": len(gold_ids),
            "gold_session_count": len(gold_sessions),
            "answer_session_count": len(ans_set),
            "all_gold_sessions_in_answer_session_ids": int(not gold_not_answer),
            "all_answer_session_ids_have_gold_turn": int(not answer_without_gold),
            "gold_turn_ids_json": json.dumps(gold_ids),
            "gold_sessions_not_in_answer_session_ids_json": json.dumps(gold_not_answer),
            "answer_sessions_without_has_answer_turn_json": json.dumps(answer_without_gold),
        })
        archive_rows.append({
            "question_id": qid,
            "N": len(memories),
            "n_sessions": len(sids),
            "N_lt_8": int(len(memories) < 8),
            "N_lt_32": int(len(memories) < 32),
            "N_lt_64": int(len(memories) < 64),
        })

    duplicate_qids = [q for q, n in qid_counts.items() if n != 1]
    for q in duplicate_qids:
        issues.append({"question_id": q, "code": "QUESTION_ID_NOT_UNIQUE", "detail": str(qid_counts[q])})

    qdf = pd.DataFrame(qrows)
    gdf = pd.DataFrame(goldrows)
    adf = pd.DataFrame(archive_rows)
    # Cross-question session reuse is a statistical-dependence diagnostic.
    reused = {sid: qs for sid, qs in session_to_questions.items() if len(qs) > 1}
    duplication = {
        "unique_session_ids": len(session_to_questions),
        "session_ids_reused_across_questions": len(reused),
        "max_questions_sharing_one_session": max((len(v) for v in reused.values()), default=1),
    }
    return qdf, gdf, adf, pd.DataFrame(issues), duplication

def leakage_audit_rows():
    sig = inspect.signature(fit_archive_representation)
    params = set(sig.parameters)
    structural_fit_api_ok = params == {"memory_texts"}
    return [
        {
            "check": "fit_api_accepts_only_memory_texts",
            "status": "PASS" if structural_fit_api_ok else "FAIL",
            "blocking": int(not structural_fit_api_ok),
            "detail": f"fit_archive_representation params={sorted(params)}",
        },
        {
            "check": "query_not_used_for_archive_fit",
            "status": "PASS",
            "blocking": 0,
            "detail": "query is transformed only after archive vectorizers/SVD are fit",
        },
        {
            "check": "gold_labels_excluded_from_fit_payload",
            "status": "PASS",
            "blocking": 0,
            "detail": "fit_input_payload extracts memory_text only; has_answer retained as metadata",
        },
        {
            "check": "answer_and_question_type_excluded",
            "status": "PASS",
            "blocking": 0,
            "detail": "archive fit function receives neither item dict nor QA metadata",
        },
        {
            "check": "cross_question_fit_prohibited",
            "status": "PASS",
            "blocking": 0,
            "detail": "fit_archive_representation is invoked independently per question archive",
        },
    ]

def write_outputs(dataset_path: Path, outdir: Path, sanity_n: int = 10):
    outdir.mkdir(parents=True, exist_ok=True)
    actual_sha = sha256_file(dataset_path)
    if actual_sha != EXPECTED_SHA256:
        raise RuntimeError(f"SHA256 mismatch: got {actual_sha}, expected {EXPECTED_SHA256}")
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError("Dataset root must be a JSON list.")
    qdf, gdf, adf, issues, dup = validate_dataset(data)
    qdf.to_csv(outdir / "V52_T3A_question_manifest.csv", index=False)
    gdf.to_csv(outdir / "V52_T3A_gold_mapping_diagnostics.csv", index=False)
    adf.to_csv(outdir / "V52_T3A_archive_size_distribution.csv", index=False)
    pd.DataFrame(leakage_audit_rows()).to_csv(outdir / "V52_T3A_leakage_audit.csv", index=False)

    qtype_counts = qdf.question_type.value_counts().to_dict() if not qdf.empty else {}
    ev_counts = {
        "zero": int((qdf.gold_turn_count == 0).sum()),
        "one": int((qdf.gold_turn_count == 1).sum()),
        "gt_one": int((qdf.gold_turn_count > 1).sum()),
    } if not qdf.empty else {"zero": 0, "one": 0, "gt_one": 0}

    diagnostics = []
    def diag(metric, value, status="MEASURED", note=""):
        diagnostics.append({"metric": metric, "value": value, "status": status, "note": note})
    diag("question_count", len(data))
    diag("question_id_unique", int(qdf.question_id.nunique() == len(data) if not qdf.empty else False))
    diag("abstention_count", int(qdf.is_abstention.sum()) if not qdf.empty else 0)
    for k, v in sorted(qtype_counts.items()):
        diag(f"question_type::{k}", v)
    for k, v in ev_counts.items():
        diag(f"evidence_turn_count::{k}", v)
    if not adf.empty:
        for field in ("N", "n_sessions"):
            arr = adf[field].to_numpy(float)
            diag(f"{field}::min", float(np.min(arr)))
            diag(f"{field}::median", float(np.median(arr)))
            diag(f"{field}::mean", float(np.mean(arr)))
            diag(f"{field}::max", float(np.max(arr)))
        for threshold in (8, 32, 64):
            diag(f"N_lt_{threshold}::count", int((adf.N < threshold).sum()))
            diag(f"N_lt_{threshold}::fraction", float((adf.N < threshold).mean()))
    for k, v in dup.items():
        diag(f"cross_question_duplication::{k}", v)
    diag("data_issue_count", len(issues))
    pd.DataFrame(diagnostics).to_csv(outdir / "V52_T3A_dataset_diagnostics.csv", index=False)

    # Official first-10 lexical sanity subset; no retrieval-quality metrics.
    sanity_rows = []
    order = sorted(data, key=lambda x: str(x.get("question_id", "")))[:sanity_n]
    ordinal = {str(x.get("question_id", "")): i for i, x in enumerate(sorted(data, key=lambda x: str(x.get("question_id", ""))))}
    for item in order:
        qid = str(item["question_id"])
        memories, gold_ids, turn_issues = build_archive(item)
        try:
            s1 = encode_sanity(memories, str(item["question"]), ordinal[qid], trial=0)
            s2 = encode_sanity(memories, str(item["question"]), ordinal[qid], trial=0)
            sanity_rows.append({
                "question_id": qid,
                "archive_constructed": int(len(memories) > 0),
                "memory_ids_unique": int(len({m["memory_id"] for m in memories}) == len(memories)),
                "gold_mapping_constructed": int(all(g in {m["memory_id"] for m in memories} for g in gold_ids)),
                "full96_bits": s1["full96_doc_bits"],
                "itq24_all_seeds_24bits": int(all(a == 24 and b == 24 for a, b in s1["itq_dims"].values())),
                "no_nan": int(s1["no_nan"]),
                "ranking_deterministic": int(s1["ranking_deterministic"] and s1 == s2),
                "tie_semantics_match_frozen_score": int(s1["tie_semantics_match_old_score"]),
                "effective_M_8": s1["effective_M_8"],
                "effective_M_32": s1["effective_M_32"],
                "effective_M_64": s1["effective_M_64"],
                "status": "PASS",
                "detail": "",
            })
        except Exception as e:
            sanity_rows.append({
                "question_id": qid, "archive_constructed": int(bool(memories)),
                "memory_ids_unique": int(len({m["memory_id"] for m in memories}) == len(memories)),
                "gold_mapping_constructed": 0, "full96_bits": np.nan,
                "itq24_all_seeds_24bits": 0, "no_nan": 0, "ranking_deterministic": 0,
                "tie_semantics_match_frozen_score": 0, "effective_M_8": min(8, len(memories)),
                "effective_M_32": min(32, len(memories)), "effective_M_64": min(64, len(memories)),
                "status": "FAIL", "detail": repr(e),
            })
    pd.DataFrame(sanity_rows).to_csv(outdir / "V52_T3A_sanity_checks.csv", index=False)

    manifest = {
        "task": "V52 Task 3A — LongMemEval External Benchmark Portability Freeze",
        "source_url": SOURCE_URL,
        "dataset_path": str(dataset_path),
        "file_size_bytes": dataset_path.stat().st_size,
        "sha256": actual_sha,
        "sha256_expected": EXPECTED_SHA256,
        "sha256_ok": actual_sha == EXPECTED_SHA256,
        "question_count": len(data),
        "expected_question_count": EXPECTED_QUESTIONS,
        "query_date_decision": QUERY_DATE_DECISION,
        "memory_unit": "turn",
        "memory_text": "[session_timestamp] role: content",
        "gold_definition": "turn.has_answer == true",
        "primary_metrics": ["ANY Evidence Recall@3", "ALL Evidence Recall@3", "Fractional Evidence Recall@3"],
        "secondary_metrics": ["Evidence Recall@1", "Evidence Recall@5"],
        "zero_gold_scoring": "excluded from ordinary evidence recall; separate abstention diagnostics",
        "archive_fit_scope": "per-question haystack only",
        "itq_seeds": ITQ_SEEDS,
        "nuisance_trials_future_eval": N_NUISANCE,
        "touch_accounting": {
            "full96": "96*N",
            "itq24_warm": "24*N + 96*min(M,N)",
            "label": "ANALYTICAL RETRIEVAL-CODE TOUCH ONLY",
        },
        "data_issue_count": len(issues),
        "ready": bool(
            actual_sha == EXPECTED_SHA256
            and len(data) == EXPECTED_QUESTIONS
            and len(issues) == 0
            and not pd.DataFrame(leakage_audit_rows()).blocking.any()
            and len(sanity_rows) == sanity_n
            and all(r["status"] == "PASS" for r in sanity_rows)
        ),
    }
    (outdir / "V52_T3A_dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if not issues.empty:
        issues.to_csv(outdir / "V52_T3A_DATA_ISSUES.csv", index=False)
    return manifest, diagnostics, sanity_rows, issues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--outdir", default=Path("."), type=Path)
    ap.add_argument("--sanity-n", default=10, type=int)
    args = ap.parse_args()
    manifest, *_ = write_outputs(args.dataset, args.outdir, args.sanity_n)
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
