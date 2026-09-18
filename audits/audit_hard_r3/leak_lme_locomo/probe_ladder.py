"""RealTalk inductive ladder probe (k=96/192/384). READ-ONLY on sources; writes own dir.
Usage: ml-python probe_ladder.py <ARCHIVE e.g. RT05>
Adapted from audit_hard_r2 .../t_inductive_all10.py (copied as
t_inductive_all10_refcopy.py in this dir; original untouched). Generalization:
SVD width k parameterized; per-archive job with JSON output for resumability.
TRANS: projector fitted on the archive's own docs. INDEP: fitted on pooled docs
of the other 9 archives (round-2 definition). Gate: k=96 TRANS sign(C)
bit-equality vs bench3/runs/b3a_realtalk/rt_repr/<ARCH>.pkl.
"""
import hashlib, json, os, pickle, sys
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
try:
    from threadpoolctl import threadpool_limits; threadpool_limits(limits=1)
except Exception:
    pass

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]
KS = (96, 192, 384)

def load(a):
    d = json.load(open(f"{DATA}/{a}.json"))
    return [x["text"] for x in d["docs"]], d["queries"], d

def det_top10(scores, aid, k=10):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k]

def fit_projector(fit_texts, k):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                         sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(fit_texts))
    Xc = normalize(cv.fit_transform(fit_texts))
    dd = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    sv = TruncatedSVD(n_components=dd, random_state=5101)
    Xl = normalize(sv.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    kk = min(k, min(Z.shape) - 1)
    s96 = TruncatedSVD(n_components=kk, random_state=5204)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    return wv, cv, sv, s96, mu, kk

def encode(P, texts):
    wv, cv, sv, s96, mu, kk = P
    Qw = normalize(wv.transform(texts))
    Qc = normalize(cv.transform(texts))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(s96.transform(Zq)) - mu).astype(np.float64)

def score(C, QC, gold, aid):
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    sig = C.std(axis=0, ddof=0); sig[sig < 1e-12] = 1e-12
    out = {}
    for name, S in (("sym", QB @ B.T), ("qscale", (QC / sig) @ B.T)):
        hits = [1.0 if (set(gold[r]) & set(det_top10(S[r], aid, 10))) else 0.0
                for r in range(S.shape[0])]
        out[name] = 100.0 * sum(hits) / len(hits)
        out[name + "_perq"] = hits
    return out

def main():
    held = sys.argv[1]
    docs_h, queries_h, D = load(held)
    row_of = {d["row"]: j for j, d in enumerate(D["docs"])}
    qs = [q for q in queries_h if any(g in row_of for g in q.get("gold", []))]
    gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
    qtexts = [q["text"] for q in qs]
    bg = []
    for a in ARCHIVES:
        if a != held:
            bg.extend(load(a)[0])
    res = {"archive": held, "n_docs": len(docs_h), "n_q": len(qs), "bg_docs": len(bg)}
    for k in KS:
        P_t = fit_projector(docs_h, k)
        C_t = encode(P_t, docs_h); Q_t = encode(P_t, qtexts)
        P_i = fit_projector(bg, k)
        C_i = encode(P_i, docs_h); Q_i = encode(P_i, qtexts)
        if k == 96:
            Cc = np.asarray(pickle.load(
                open(R + f"/bench3/runs/b3a_realtalk/rt_repr/{held}.pkl", "rb"))["C"])
            res["gate_diff_bits"] = int(np.count_nonzero((C_t >= 0) != (Cc >= 0)))
            res["gate_total_bits"] = int(Cc.size)
        rt = score(C_t, Q_t, gold, held); ri = score(C_i, Q_i, gold, held)
        res[f"TRANS_k{k}"] = {x: rt[x] for x in ("sym", "qscale")}
        res[f"INDEP_k{k}"] = {x: ri[x] for x in ("sym", "qscale")}
        res[f"perq_trans_k{k}_sym"] = rt["sym_perq"]
        res[f"perq_trans_k{k}_qscale"] = rt["qscale_perq"]
        res[f"perq_indep_k{k}_sym"] = ri["sym_perq"]
        res[f"perq_indep_k{k}_qscale"] = ri["qscale_perq"]
        print(f"{held} k={k} kk_fit={P_t[5]}/{P_i[5]} | TRANS sym={rt['sym']:.2f} "
              f"qs={rt['qscale']:.2f} | INDEP sym={ri['sym']:.2f} qs={ri['qscale']:.2f}",
              flush=True)
    print(f"{held} gate={res['gate_diff_bits']}/{res['gate_total_bits']}", flush=True)
    json.dump(res, open(os.path.join(HERE, f"LADDER_IND_{held}.json"), "w"), indent=1)

main()
