"""T-bytes: what does '12 B/doc' omit? Measure the per-archive decoder state.
READ-ONLY: reads data/RT05.json (smallest archive) only; all fitting in memory.
Run with ml-python (sklearn). Writes nothing outside this script's stdout.
Recipe mirrors coordinator/ladder.py build() + frozen source blocks exactly.
"""
import json
import pickle

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

R = "/mnt/c/Users/MDP/dev/llmzip-work"
D = json.load(open(R + "/top10_comparison_r1/data/RT05.json"))
texts = [d["text"] for d in D["docs"]]
N = len(texts)
print(f"archive RT05 N={N} docs")

wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                     sublinear_tf=True)
cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
Xw = normalize(wv.fit_transform(texts))
Xc = normalize(cv.fit_transform(texts))
d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
svd = TruncatedSVD(n_components=d, random_state=5101)
Xl = normalize(svd.fit_transform(Xw))
Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
s96 = TruncatedSVD(n_components=96, random_state=5204)
Y = normalize(s96.fit_transform(Z))
mu = Y.mean(axis=0, keepdims=True)
C = (Y - mu).astype(np.float64)
sig = C.std(axis=0, ddof=0)

F = Z.shape[1]
print(f"word feats={Xw.shape[1]} char feats={Xc.shape[1]} latent={Xl.shape[1]} "
      f"Z feats F={F}")
print(f"C shape={C.shape} (sanity: N x 96)")

# Side-info inventory (bytes a decoder needs beyond the N*12 payload):
svd_mat = s96.components_.nbytes          # 96 x F
lsa_mat = svd.components_.nbytes          # 32 x W
mu_b = mu.nbytes
sig_b = sig.nbytes
wv_b = len(pickle.dumps(wv))
cv_b = len(pickle.dumps(cv))
payload = N * 12
itq_R = 96 * 96 * 8                        # float64 rotation (quant_math family C)
itq_R32 = 96 * 96 * 4
print(f"\nside-info bytes (per archive, shared across its {N} docs):")
print(f"  SVD96 components_ 96x{F} {s96.components_.dtype}: {svd_mat:,}")
print(f"  LSA32 components_: {lsa_mat:,}")
print(f"  mu (96 f64): {mu_b:,}")
print(f"  sigma (96 f64): {sig_b:,}")
print(f"  word vectorizer pickle: {wv_b:,}")
print(f"  char vectorizer pickle: {cv_b:,}")
side = svd_mat + lsa_mat + mu_b + sig_b + wv_b + cv_b
print(f"  SIDE TOTAL (no rotation): {side:,} B = {side/1024:.1f} KiB")
print(f"  payload N*12: {payload:,} B")
print(f"  side/payload ratio: {side/payload:.1f}x")
print(f"  amortized true cost per doc: 12 + {side/N:.0f} = {12 + side/N:.0f} B/doc")
print(f"  ITQ rotation extra: {itq_R:,} B f64 ({itq_R32:,} B f32) = "
      f"{itq_R/payload:.1f}x the whole payload (f64)")
print(f"\nSVD96 float32 variant would be {96*F*4:,} B "
      f"({(96*F*4)/payload:.1f}x payload)")
