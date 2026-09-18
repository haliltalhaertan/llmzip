"""T-hybrid: decompose the transductive gap into vocab vs subspace.
READ-ONLY. ml-python. Held-out RT05.
  HYBRID: TFIDF vocab/IDF fit on background+test UNION (no dropped test terms),
          but SVD96+mu fit on BACKGROUND docs only, test docs encoded through it.
If HYBRID ~= TRANS -> vocab/OOV drives the gap. If HYBRID ~= INDEP -> subspace does.
"""
import hashlib
import json

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
HELD = "RT05"


def load(a):
    d = json.load(open(f"{DATA}/{a}.json"))
    return [x["text"] for x in d["docs"]], d["queries"]


def det_top10(scores, aid, k=10):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


docs_h, queries_h = load(HELD)
D = json.load(open(f"{DATA}/{HELD}.json"))
row_of = {d["row"]: j for j, d in enumerate(D["docs"])}
qs = [q for q in queries_h if any(g in row_of for g in q.get("gold", []))]
gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
qtexts = [q["text"] for q in qs]
bg = []
for i in range(1, 11):
    a = f"RT{i:02d}"
    if a != HELD:
        bg.extend(load(a)[0])
print(f"N_test={len(docs_h)} N_bg={len(bg)} nq={len(qs)}", flush=True)

print("fitting union TFIDF ...", flush=True)
wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                     sublinear_tf=True)
cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
Xw_bg = normalize(wv.fit_transform(bg + docs_h))
Xc_bg = normalize(cv.fit_transform(bg + docs_h))
n_bg = len(bg)
Xw_b, Xw_h = Xw_bg[:n_bg], Xw_bg[n_bg:]
Xc_b, Xc_h = Xc_bg[:n_bg], Xc_bg[n_bg:]
dd = min(32, Xw_bg.shape[0] - 1, Xw_bg.shape[1] - 1)
sv = TruncatedSVD(n_components=dd, random_state=5101)
Xl_b = normalize(sv.fit_transform(Xw_b))          # LSA fit on background only
Xl_h = normalize(sv.transform(Xw_h))
Z_b = sparse.hstack([sparse.csr_matrix(Xl_b), Xw_b, Xc_b], format="csr")
Z_h = sparse.hstack([sparse.csr_matrix(Xl_h), Xw_h, Xc_h], format="csr")
print("fitting SVD96 on background only ...", flush=True)
s96 = TruncatedSVD(n_components=96, random_state=5204)
Y_b = normalize(s96.fit_transform(Z_b))
mu = Y_b.mean(axis=0, keepdims=True)
C_h = (normalize(s96.transform(Z_h)) - mu).astype(np.float64)


def enc(texts):
    Qw = normalize(wv.transform(texts))
    Qc = normalize(cv.transform(texts))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(s96.transform(Zq)) - mu).astype(np.float64)


Q_h = enc(qtexts)
B = np.where(C_h >= 0, 1.0, -1.0)
QB = np.where(Q_h >= 0, 1.0, -1.0)
sig = C_h.std(axis=0, ddof=0)
sig[sig < 1e-12] = 1e-12
for name, S in (("sym", QB @ B.T), ("qscale", (Q_h / sig) @ B.T)):
    h = np.mean([1.0 if (set(gold[r]) & set(det_top10(S[r], HELD, 10).tolist())) else 0.0
                 for r in range(S.shape[0])])
    print(f"HYBRID {name} Hit@10={100*h:.2f}  "
          f"(TRANS sym=55.71 qscale=60.00; INDEP sym=18.57 qscale=24.29)")
