"""T-transductive: does fitting the projection on the retrieval corpus inflate codes?
Pure-numpy synthetic demo (no project code, no sklearn). Mechanism only:
same pipeline both arms (L2 -> truncated SVD -> center -> sign -> Hamming top10);
only the SVD fit data differs:
  TRANS: SVD fit on the retrieval corpus itself (what the project does per archive)
  INDEP: SVD fit on a disjoint background corpus from the same distribution
         (the deployable/inductive setup: archive arrives after the projector is fixed)
Docs: Zipf-word count vectors; query = gold doc's rare words + common-word noise.
"""
import numpy as np

rng = np.random.default_rng(7)
V, N, Q, K = 4000, 400, 200, 96


def make_corpus(n, seed):
    r = np.random.default_rng(seed)
    freq = 1.0 / np.arange(1, V + 1) ** 1.1
    freq /= freq.sum()
    X = np.zeros((n, V))
    for i in range(n):
        L = r.integers(40, 120)
        ws = r.choice(V, size=L, replace=True, p=freq)
        for w in ws:
            X[i, w] += 1.0
        X[i] *= np.log(n / (1 + (X > 0).sum(axis=0)[ws[:1]][0] + 1)) if False else 1.0
    # sublinear tf + idf-ish weight inside corpus
    X = np.log1p(X)
    df = (X > 0).sum(axis=0) + 1
    X = X * np.log(n / df)[None, :]
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return X


def svd_project(X_fit, X, Xq, k):
    U, S, Vt = np.linalg.svd(X_fit, full_matrices=False)
    P = Vt[:k].T
    Y = X @ P
    Y /= np.linalg.norm(Y, axis=1, keepdims=True) + 1e-12
    QY = Xq @ P
    QY /= np.linalg.norm(QY, axis=1, keepdims=True) + 1e-12
    mu = Y.mean(axis=0, keepdims=True)
    return Y - mu, QY - mu


def hit10(C, QC, gold):
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    S = QB @ B.T
    top = np.argsort(-S, axis=1, kind="stable")[:, :10]
    return np.mean([1.0 if gold[i] in set(top[i].tolist()) else 0.0 for i in range(len(gold))])


X = make_corpus(N, seed=11)          # the retrieval corpus (test archive)
Xbg = make_corpus(N, seed=99)        # disjoint background corpus, same distribution
qgold = rng.integers(0, N, size=Q)
# queries: keep each gold doc's rarest 8 terms + 12 random common terms (simulates a question)
df = (X > 0).sum(axis=0)
Xq = np.zeros((Q, V))
for i, g in enumerate(qgold):
    nz = np.nonzero(X[g])[0]
    rare = nz[np.argsort(df[nz])[:8]]
    common = rng.choice(V, size=12, p=(1.0 / np.arange(1, V + 1)) / np.sum(1.0 / np.arange(1, V + 1)))
    for w in list(rare) + list(common):
        Xq[i, w] += 1.0
Xq = np.log1p(Xq)
Xq /= np.linalg.norm(Xq, axis=1, keepdims=True) + 1e-12

C_t, Q_t = svd_project(X, X, Xq, K)     # transductive (project fit on test corpus)
C_i, Q_i = svd_project(Xbg, X, Xq, K)   # inductive (project fit on held-out corpus)
h_t = hit10(C_t, Q_t, qgold)
h_i = hit10(C_i, Q_i, qgold)
print(f"TRANS (fit on retrieval corpus, project practice): Hit@10 = {100*h_t:.2f}")
print(f"INDEP (fit on disjoint background corpus):         Hit@10 = {100*h_i:.2f}")
print(f"transductive optimism gap = {100*(h_t-h_i):+.2f} pp (synthetic mechanism demo)")
