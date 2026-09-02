#!/usr/bin/env python3
"""Gate 3 - INDEPENDENT outcome-free reconstruction of the 100K::12 representation.

Reimplemented from the audited specification. The candidate module is NOT imported.
Stops at the centered 96-d representation and the single canary query transform:
no ranking, no gold, no metric, no probing-questions file.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

LATENT_DIM, LATENT_SEED = 32, 5101
MIXED_DIM, MIXED_SEED = 96, 5204
CANARY_QUERY = "Which project phase mentioned module 7 and a deadline?"

corpus_root = Path(sys.argv[1]); out_json = Path(sys.argv[2]); out_npz = Path(sys.argv[3])

def iter_messages(value):
    if isinstance(value, dict):
        if {"role", "id", "content"}.issubset(value):
            yield value; return
        for child in value.values(): yield from iter_messages(child)
    elif isinstance(value, list):
        for child in value: yield from iter_messages(child)

def canonical_raw_id(v):
    if isinstance(v, bool): raise ValueError("bool id")
    if isinstance(v, int): return str(v)
    if isinstance(v, str) and v.isdigit(): return str(int(v))
    raise ValueError(f"non-canonical id {v!r}")

chat = corpus_root / "chats" / "100K" / "12" / "chat.json"
raw = json.loads(chat.read_text(encoding="utf-8"))
raw_ids, texts = [], []
for m in iter_messages(raw):
    role, content = m.get("role"), m.get("content")
    assert role in {"user", "assistant"} and isinstance(content, str)
    raw_ids.append(canonical_raw_id(m.get("id")))
    texts.append(f"{role}: {content}")
assert len(set(raw_ids)) == len(raw_ids)

wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
x_word = normalize(wv.fit_transform(texts))
x_char = normalize(cv.fit_transform(texts))
lsvd = TruncatedSVD(n_components=LATENT_DIM, random_state=LATENT_SEED)
x_latent = normalize(lsvd.fit_transform(x_word))
source = sparse.hstack([sparse.csr_matrix(x_latent), x_word, x_char], format="csr")
msvd = TruncatedSVD(n_components=MIXED_DIM, random_state=MIXED_SEED)
y96 = normalize(msvd.fit_transform(source))
mean96 = np.asarray(y96.mean(axis=0, keepdims=True), dtype=np.float64)
centered96 = np.asarray(y96 - mean96, dtype=np.float64)

q_word = normalize(wv.transform([CANARY_QUERY]))
q_char = normalize(cv.transform([CANARY_QUERY]))
q_latent = normalize(lsvd.transform(q_word))
q_source = sparse.hstack([sparse.csr_matrix(q_latent), q_word, q_char], format="csr")
q_y96 = normalize(msvd.transform(q_source))
q_centered = np.asarray(q_y96 - mean96, dtype=np.float64)

def sign_digest(a):
    return hashlib.sha256(np.packbits(np.asarray(a, dtype=np.float64) >= 0).tobytes()).hexdigest()
def raw_digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

result = {
    "coretype": sys.argv[4] if len(sys.argv) > 4 else None,
    "archive_units": len(raw_ids),
    "archive_shape": list(centered96.shape),
    "query_shape": list(q_centered.shape),
    "mixed96_rank": int(np.linalg.matrix_rank(np.asarray(y96, dtype=np.float64))),
    "archive_sign_sha256": sign_digest(centered96),
    "query_sign_sha256": sign_digest(q_centered),
    "archive_raw_float_sha256": raw_digest(centered96),
    "query_raw_float_sha256": raw_digest(q_centered),
    "archive_min_abs": float(np.min(np.abs(centered96))),
    "query_min_abs": float(np.min(np.abs(q_centered))),
    "numpy": np.__version__,
    "blas": np.show_config("dicts").get("Build Dependencies", {}).get("blas", {}).get("openblas configuration"),
}
out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
np.savez_compressed(out_npz, archive=centered96, query=q_centered)
print(json.dumps({k: result[k] for k in ("coretype","archive_units","archive_sign_sha256","query_sign_sha256","archive_raw_float_sha256","archive_min_abs","query_min_abs")}))
