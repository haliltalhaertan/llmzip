"""LME sampled inductive probe (k=96, FULL arm recipe). READ-ONLY on sources; writes own dir.
Usage: ml-python probe_lme.py <QID> <SIBS_FILE>
Recipe copied from top10_comparison_r1/ablation_r2/lme/ablation.py fit_sources +
build_arm(FULL) + score_archive (frozen seeds 5101/5204, det top-K via
audit_baseline_lib semantics re-implemented here with hashlib to avoid imports).
TRANS: sources+SVD96 fitted on the archive's own memory texts.
INDEP (SAMPLED honest regime): sources+SVD96 fitted on pooled memory texts of 9
sibling archives listed in SIBS_FILE (NOT all 469: full leave-one-out pooling is
infeasible here; disclosed in report).
Gate: TRANS sign(C)/sign(QC) bit-equality vs regen/lme/cache_repr/<QID>.pkl.
Metric: single-query Hit@10 (sym + qscale).
"""
import glob, hashlib, json, os, pickle, sys
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
try:
    from threadpoolctl import threadpool_limits; threadpool_limits(limits=1)
except Exception:
    pass

W = "/mnt/c/Users/MDP/dev/llmzip-work"
HERE = os.path.dirname(os.path.abspath(__file__))
ITEM = W + "/regen/lme/items/%s.json"
CACHE = W + "/regen/lme/cache_repr/%s.pkl"

def build_memory_texts(item):
    texts, gold_rows = [], []
    row = 0
    for date, sess in zip(item["haystack_dates"], item["haystack_sessions"]):
        for turn in sess:
            role = turn.get("role")
            content = turn.get("content")
            if not isinstance(content, str):
                content = "" if content is None else str(content)
            texts.append(f"[{date}] {role}: {content}")
            if turn.get("has_answer", False) is True:
                gold_rows.append(row)
            row += 1
    return texts, np.asarray(gold_rows, dtype=np.int64)

def fit_sources(texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                         sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    return wv, cv, svd, Xw, Xc, Xl

def X_of(texts, wv, cv, svd):
    Xw = normalize(wv.transform(texts))
    Xc = normalize(cv.transform(texts))
    Xl = normalize(svd.transform(Xw))
    return Xl, Xw, Xc

def fit_svd(Z):
    s96 = TruncatedSVD(n_components=96, random_state=5204)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    return s96, mu

def encode_docs(s96, mu, Z):
    return (normalize(s96.transform(Z)) - mu).astype(np.float64)

def det_topk(scores, aid, k):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k]

def main():
    qid = sys.argv[1]
    sibs = [l.strip() for l in open(sys.argv[2]) if l.strip()]
    item = json.load(open(ITEM % qid))
    cached = pickle.load(open(CACHE % qid, "rb"))
    Cc = np.asarray(cached["C"], dtype=np.float64)
    qCc = np.asarray(cached["qC"], dtype=np.float64).reshape(-1)
    gold_cached = [int(x) for x in np.asarray(cached["gold"]).ravel().tolist()]
    texts, gold_rebuilt = build_memory_texts(item)
    assert len(texts) == Cc.shape[0]
    assert [int(x) for x in gold_rebuilt.tolist()] == gold_cached
    assert len(gold_cached) > 0

    # TRANS
    wv, cv, svd, Xw, Xc, Xl = fit_sources(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    assert min(Z.shape) > 96
    s96, mu = fit_svd(Z)
    C_t = (normalize(s96.transform(Z)) - mu).astype(np.float64)
    Xlq, Xwq, Xcq = X_of([item["question"]], wv, cv, svd)
    Zq = sparse.hstack([sparse.csr_matrix(Xlq), Xwq, Xcq], format="csr")
    Q_t = (normalize(s96.transform(Zq)) - mu).astype(np.float64).reshape(-1)

    dbits = int(np.count_nonzero((C_t >= 0) != (Cc >= 0)))
    qbits = int(np.count_nonzero((Q_t >= 0) != (qCc >= 0)))

    # INDEP on pooled sib texts
    bg = []
    for s in sibs:
        it = json.load(open(ITEM % s))
        t, _ = build_memory_texts(it)
        bg.extend(t)
    w2, c2, s2, Xw2, Xc2, Xl2 = fit_sources(bg)
    Zb = sparse.hstack([sparse.csr_matrix(Xl2), Xw2, Xc2], format="csr")
    s96b, mub = fit_svd(Zb)
    Xld, Xwd, Xcd = X_of(texts, w2, c2, s2)
    Zd = sparse.hstack([sparse.csr_matrix(Xld), Xwd, Xcd], format="csr")
    C_i = encode_docs(s96b, mub, Zd)
    Xlq2, Xwq2, Xcq2 = X_of([item["question"]], w2, c2, s2)
    Zq2 = sparse.hstack([sparse.csr_matrix(Xlq2), Xwq2, Xcq2], format="csr")
    Q_i = encode_docs(s96b, mub, Zq2).reshape(-1)

    out = {"qid": qid, "N": len(texts), "bg_docs": len(bg), "n_sibs": len(sibs),
           "gate_diff_bits": dbits, "gate_total_bits": int(Cc.size),
           "gate_qc_diff_bits": qbits,
           "gate_max_abs": float(np.max(np.abs(C_t - Cc)))}
    for tag, (C, Q) in (("TRANS", (C_t, Q_t)), ("INDEP", (C_i, Q_i))):
        Db = (C >= 0); Qb = (Q >= 0)
        s_sym = -np.count_nonzero(Db != Qb[None, :], axis=1).astype(np.float64)
        std = np.std(C, axis=0, ddof=0).astype(np.float64)
        sigma = np.where(std < 1e-12, 1e-12, std)
        s_q = np.where(Db, 1.0, -1.0) @ (Q / sigma)
        for name, s in (("sym", s_sym), ("qscale", s_q)):
            top10 = det_topk(s, qid, 10)
            out[f"{tag}_{name}_hit10"] = 1.0 if (set(gold_cached) & set(top10)) else 0.0
    json.dump(out, open(os.path.join(HERE, f"LME_IND_{qid}.json"), "w"), indent=1)
    print(f"{qid} N={len(texts)} bg={len(bg)} gate={dbits}/{Cc.size} qgate={qbits} | "
          f"TRANS sym={out['TRANS_sym_hit10']:.0f} qs={out['TRANS_qscale_hit10']:.0f} | "
          f"INDEP sym={out['INDEP_sym_hit10']:.0f} qs={out['INDEP_qscale_hit10']:.0f}",
          flush=True)

main()
