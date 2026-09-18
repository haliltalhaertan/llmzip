"""T-inductive-RT: real-data magnitude of transductive optimism on RealTalk.
READ-ONLY on source trees. Run with ml-python (sklearn).
Held-out archive RT05 (410 docs, 70 queries). Two projectors, same recipe
(TFIDF word 1-2 + char_wb 3-5, LSA32 seed 5101, SVD96 seed 5204, L2, doc-mean
center, sign, Hamming det-top10):
  TRANS: fit on RT05 docs (project practice; expect ~gate-exact rebuild)
  INDEP: fit on the OTHER 9 RT archives' docs (inductive: projector fixed
         before the test archive arrives; OOV terms dropped naturally)
Reports Hit@10 sym + qscale for both. No files written.
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
OTHERS = [f"RT{i:02d}" for i in range(1, 11) if f"RT{i:02d}" != HELD]


def load(a):
    d = json.load(open(f"{DATA}/{a}.json"))
    return [x["text"] for x in d["docs"]], d["queries"]


def det_top10(scores, aid, k=10):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


def fit_projector(fit_texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                         sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(fit_texts))
    Xc = normalize(cv.fit_transform(fit_texts))
    dd = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    sv = TruncatedSVD(n_components=dd, random_state=5101)
    Xl = normalize(sv.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s96 = TruncatedSVD(n_components=96, random_state=5204)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    return wv, cv, sv, s96, mu


def encode(wv, cv, sv, s96, mu, texts):
    Qw = normalize(wv.transform(texts))
    Qc = normalize(cv.transform(texts))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(s96.transform(Zq)) - mu).astype(np.float64)


def score(C, QC, gold, aid):
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    sig = C.std(axis=0, ddof=0)
    sig[sig < 1e-12] = 1e-12
    out = {}
    for name, S in (("sym", QB @ B.T), ("qscale", (QC / sig) @ B.T)):
        h = 0.0
        for r in range(S.shape[0]):
            h += 1.0 if (set(gold[r]) & set(det_top10(S[r], aid, 10).tolist())) else 0.0
        out[name] = 100 * h / S.shape[0]
    return out


docs_h, queries_h = load(HELD)
row_of = {i: i for i in range(len(docs_h))}  # RT rows are 0..N-1 positional here
# gold rows in RT jsons are doc 'row' ids; map via docs list order
D = json.load(open(f"{DATA}/{HELD}.json"))
row_of = {d["row"]: j for j, d in enumerate(D["docs"])}
qs = [q for q in queries_h if any(g in row_of for g in q.get("gold", []))]
gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
qtexts = [q["text"] for q in qs]
print(f"held-out {HELD}: N={len(docs_h)} nq={len(qs)}", flush=True)

print("fitting TRANS projector on held-out docs ...", flush=True)
P_t = fit_projector(docs_h)
C_t = encode(*P_t, docs_h)
Q_t = encode(*P_t, qtexts)

print("fitting INDEP projector on other-9-archives docs ...", flush=True)
bg = []
for a in OTHERS:
    dt, _ = load(a)
    bg.extend(dt)
print(f"background docs: {len(bg)}", flush=True)
P_i = fit_projector(bg)
C_i = encode(*P_i, docs_h)
Q_i = encode(*P_i, qtexts)

# sanity: TRANS rebuild should match cached production signs ~exactly
import pickle
Cc = np.asarray(pickle.load(open(R + f"/bench3/runs/b3a_realtalk/rt_repr/{HELD}.pkl", "rb"))["C"])
print(f"TRANS vs cache differing bits: {int(np.count_nonzero((C_t >= 0) != (Cc >= 0)))} "
      f"of {Cc.size}", flush=True)

rt = score(C_t, Q_t, gold, HELD)
ri = score(C_i, Q_i, gold, HELD)
print(f"TRANS sym Hit@10={rt['sym']:.2f} qscale Hit@10={rt['qscale']:.2f}")
print(f"INDEP sym Hit@10={ri['sym']:.2f} qscale Hit@10={ri['qscale']:.2f}")
print(f"transductive optimism: sym {rt['sym']-ri['sym']:+.2f} pp, "
      f"qscale {rt['qscale']-ri['qscale']:+.2f} pp (one archive, {len(qs)} queries)")
