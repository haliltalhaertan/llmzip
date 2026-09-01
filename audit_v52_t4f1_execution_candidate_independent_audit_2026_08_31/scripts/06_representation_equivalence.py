#!/usr/bin/env python3
"""Gate 6: independent representation-equivalence canary on raw 100K::12.

The pipeline is re-implemented here directly from the sealed Task 4F0
representation spec (word tf-idf 1-2 + english stop words + sublinear;
char_wb 3-5 sublinear; L2; TruncatedSVD 32 @ 5101; L2; hstack; TruncatedSVD
96 @ 5204; L2; archive-mean centering) rather than by calling the candidate,
then compared byte-for-byte against the candidate's own output and against the
sealed canary anchors.

Archive bytes only.  probing_questions.json is never opened.  The query is the
fixed invented canary string.  No gold, no ranking, no retrieval-quality value.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "task4f1_execution_candidate_2026_08_31"
OUT = ROOT / "audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31"
CORPUS = ROOT.parent / "BEAM_pinned_3e12035532eb85768f1a7cd779832b650c4b2ef9"
ANCHOR = "28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428"
EXP_ARCHIVE = "25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025"
EXP_QUERY = "e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869"
QUERY = "Which project phase mentioned module 7 and a deadline?"

work = OUT / "_harness"
work.mkdir(parents=True, exist_ok=True)
copy = work / "candidate_under_audit.py"
shutil.copyfile(CAND / "v52_t4f1_beam_retrieval.py", copy)
assert hashlib.sha256(copy.read_bytes()).hexdigest() == ANCHOR
spec = importlib.util.spec_from_file_location("cua6", copy)
mod = importlib.util.module_from_spec(spec)
sys.modules["cua6"] = mod
spec.loader.exec_module(mod)


def digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


# ---- independent archive load, straight from raw bytes ----
raw = json.loads((CORPUS / "chats/100K/12/chat.json").read_text(encoding="utf-8"))


def walk(v):
    if isinstance(v, dict):
        if {"role", "id", "content"}.issubset(v):
            yield v
            return
        for c in v.values():
            yield from walk(c)
    elif isinstance(v, list):
        for c in v:
            yield from walk(c)


msgs = list(walk(raw))
ids = [str(int(m["id"])) if not isinstance(m["id"], bool) else None for m in msgs]
texts = [f"{m['role']}: {m['content']}" for m in msgs]


# ---- independent representation, from the sealed spec ----
def independent_fit(memory_texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    xw = normalize(wv.fit_transform(memory_texts))
    xc = normalize(cv.fit_transform(memory_texts))
    lsvd = TruncatedSVD(n_components=32, random_state=5101)
    xl = normalize(lsvd.fit_transform(xw))
    src = sparse.hstack([sparse.csr_matrix(xl), xw, xc], format="csr")
    msvd = TruncatedSVD(n_components=96, random_state=5204)
    y = normalize(msvd.fit_transform(src))
    mean = np.asarray(y.mean(axis=0, keepdims=True), dtype=np.float64)
    return wv, cv, lsvd, msvd, mean, np.asarray(y - mean, dtype=np.float64), y


wv, cv, lsvd, msvd, mean96, centered, y96 = independent_fit(texts)


def independent_transform(qs):
    qw = normalize(wv.transform(qs))
    qc = normalize(cv.transform(qs))
    ql = normalize(lsvd.transform(qw))
    qs_src = sparse.hstack([sparse.csr_matrix(ql), qw, qc], format="csr")
    qy = normalize(msvd.transform(qs_src))
    return np.asarray(qy - mean96, dtype=np.float64)


q_ind = independent_transform([QUERY])

# ---- candidate's own path ----
c_ids, c_keys, c_texts = mod.load_archive(CORPUS / "chats/100K/12/chat.json", "100K", "12")
model = mod.fit_archive_representation(c_texts)
q_cand = mod.transform_queries(model, [QUERY])

# repeat determinism
model2 = mod.fit_archive_representation(c_texts)
q_cand2 = mod.transform_queries(model2, [QUERY])

# cache equivalence: one fit reused for many queries == refit per query
multi = ["alpha probe one", QUERY, "gamma probe three"]
cached = mod.transform_queries(model, multi)
per_query = np.vstack([mod.transform_queries(mod.fit_archive_representation(c_texts), [t])
                       for t in multi])

# a different archive must not be reachable from this model
other_ids, _, other_texts = mod.load_archive(CORPUS / "chats/500K/12/chat.json", "500K", "12")
other_model = mod.fit_archive_representation(other_texts)

R = {
    "schema": "V52_T4F1_REPRESENTATION_EQUIVALENCE_V1",
    "archive": "100K::12",
    "probing_questions_file_opened": False,
    "gold_labels_loaded": False,
    "retrieval_quality_computed": False,
    "ranking_performed": False,
    "query_is_fixed_invented_canary_string": True,
    "independent": {
        "units": len(texts),
        "units_is_392": len(texts) == 392,
        "archive_shape": list(centered.shape),
        "archive_shape_is_392x96": list(centered.shape) == [392, 96],
        "query_shape": list(q_ind.shape),
        "query_shape_is_1x96": list(q_ind.shape) == [1, 96],
        "archive_sha256": digest(centered),
        "query_sha256": digest(q_ind),
        "matches_sealed_archive_anchor": digest(centered) == EXP_ARCHIVE,
        "matches_sealed_query_anchor": digest(q_ind) == EXP_QUERY,
        "rank_of_y96": int(np.linalg.matrix_rank(np.asarray(y96, dtype=np.float64))),
        "rank_is_96": int(np.linalg.matrix_rank(np.asarray(y96, dtype=np.float64))) == 96,
        "all_finite": bool(np.isfinite(centered).all() and np.isfinite(q_ind).all()),
    },
    "candidate": {
        "units": len(c_texts),
        "archive_sha256": digest(model.centered96),
        "query_sha256": digest(q_cand),
        "matches_sealed_archive_anchor": digest(model.centered96) == EXP_ARCHIVE,
        "matches_sealed_query_anchor": digest(q_cand) == EXP_QUERY,
        "raw_ids_unique": len(set(c_ids)) == len(c_ids),
        "memory_keys_well_formed": all(k.startswith("100K::12::") for k in c_keys),
        "memory_key_sample": c_keys[0],
        "texts_role_prefixed": all(t.startswith(("user: ", "assistant: ")) for t in c_texts),
    },
    "equivalence": {
        "independent_archive_equals_candidate_archive": digest(centered) == digest(model.centered96),
        "independent_query_equals_candidate_query": digest(q_ind) == digest(q_cand),
        "independent_texts_equal_candidate_texts": texts == c_texts,
        "independent_ids_equal_candidate_ids": ids == c_ids,
        "repeat_fit_byte_identical": digest(model.centered96) == digest(model2.centered96),
        "repeat_query_byte_identical": digest(q_cand) == digest(q_cand2),
        "cached_fit_equals_per_query_refit": bool(np.array_equal(cached, per_query)),
        "cached_query_row_matches_single_query": bool(np.array_equal(cached[1:2], q_cand)),
        "different_archive_gives_different_model":
            digest(other_model.centered96) != digest(model.centered96),
        "different_archive_has_different_unit_count": len(other_texts) != len(c_texts),
        "mean_is_archive_mean_of_y96": bool(
            np.allclose(model.mean96, np.asarray(y96.mean(axis=0, keepdims=True)), atol=0, rtol=0)
            or np.array_equal(model.mean96, mean96)),
        "centered_columns_sum_to_zero": float(np.max(np.abs(model.centered96.sum(axis=0)))) < 1e-9,
    },
    "cache_argument": (
        "fit_archive_representation takes exactly one argument, the ordered archive "
        "memory-text list, so its output is a pure function of the archive.  Reusing "
        "one fit across the questions of that archive is therefore identical to "
        "refitting per question, which is verified numerically above; and because the "
        "model is a local of evaluate_archive with no module-level cache, a model "
        "cannot be reached from a different conversation."
    ),
}


def bad(node, path=""):
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, bool) and not v and k not in (
                    "probing_questions_file_opened", "gold_labels_loaded",
                    "retrieval_quality_computed", "ranking_performed"):
                out.append(f"{path}.{k}")
            elif isinstance(v, dict):
                out += bad(v, f"{path}.{k}")
    return out


fails = bad(R)
R["failing_flags"] = fails
R["status"] = "PASS" if not fails else "FAIL"
(OUT / "REPRESENTATION_EQUIVALENCE.json").write_text(
    json.dumps(R, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
print("status:", R["status"])
for f in fails:
    print("FAIL:", f)
print("archive sha256:", digest(centered))
print("query   sha256:", digest(q_ind))
print("units:", len(texts), "rank:", R["independent"]["rank_of_y96"])
