"""Tum 10 RealTalk arsivinde transduktif iyimserligi olcer.
READ-ONLY kaynak agaci; ciktilar yalnizca bu dizine.
Her arsiv icin: TRANS (izdusum o arsivden) vs INDEP (izdusum diger 9 arsivden).
"""
import hashlib, json, pickle, sys
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]
OUT = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/code/INDUCTIVE_ALL10.json"


def load(a):
    d = json.load(open(f"{DATA}/{a}.json"))
    return [x["text"] for x in d["docs"]], d["queries"], d


def det_top10(scores, aid, k=10):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k]


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
        hits = [1.0 if (set(gold[r]) & set(det_top10(S[r], aid, 10))) else 0.0
                for r in range(S.shape[0])]
        out[name] = 100.0 * sum(hits) / len(hits)
        out[name + "_perq"] = hits
    return out


results = {}
for held in ARCHIVES:
    docs_h, queries_h, D = load(held)
    row_of = {d["row"]: j for j, d in enumerate(D["docs"])}
    qs = [q for q in queries_h if any(g in row_of for g in q.get("gold", []))]
    gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
    qtexts = [q["text"] for q in qs]

    P_t = fit_projector(docs_h)
    C_t = encode(*P_t, docs_h); Q_t = encode(*P_t, qtexts)

    bg = []
    for a in ARCHIVES:
        if a != held:
            bg.extend(load(a)[0])
    P_i = fit_projector(bg)
    C_i = encode(*P_i, docs_h); Q_i = encode(*P_i, qtexts)

    # uretim onbellegiyle bit-esitligi (TRANS dogrulugu kaniti)
    try:
        Cc = np.asarray(pickle.load(
            open(R + f"/bench3/runs/b3a_realtalk/rt_repr/{held}.pkl", "rb"))["C"])
        dbits = int(np.count_nonzero((C_t >= 0) != (Cc >= 0))); tot = int(Cc.size)
    except Exception as e:
        dbits, tot = -1, -1

    rt = score(C_t, Q_t, gold, held); ri = score(C_i, Q_i, gold, held)
    results[held] = {
        "n_docs": len(docs_h), "n_q": len(qs), "bg_docs": len(bg),
        "gate_diff_bits": dbits, "gate_total_bits": tot,
        "TRANS": {k: v for k, v in rt.items() if not k.endswith("_perq")},
        "INDEP": {k: v for k, v in ri.items() if not k.endswith("_perq")},
        "perq": {"trans_sym": rt["sym_perq"], "trans_qscale": rt["qscale_perq"],
                 "indep_sym": ri["sym_perq"], "indep_qscale": ri["qscale_perq"]},
    }
    print(f"{held} n={len(qs)} gate={dbits}/{tot} | TRANS sym={rt['sym']:.2f} "
          f"qs={rt['qscale']:.2f} | INDEP sym={ri['sym']:.2f} qs={ri['qscale']:.2f}",
          flush=True)
    json.dump(results, open(OUT, "w"), indent=1)

# havuzlanmis toplam + arsiv-kumelenmis bootstrap
def pooled(key):
    v = [x for a in results for x in results[a]["perq"][key]]
    return 100.0 * sum(v) / len(v), len(v)

summary = {}
for arm in ("sym", "qscale"):
    t, n = pooled("trans_" + arm); i, _ = pooled("indep_" + arm)
    per_arch = [(np.mean(results[a]["perq"]["trans_" + arm]) -
                 np.mean(results[a]["perq"]["indep_" + arm])) * 100 for a in results]
    rng = np.random.default_rng(20260917)
    boots = [np.mean(rng.choice(per_arch, len(per_arch), replace=True)) for _ in range(4000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    summary[arm] = {"TRANS_pooled": round(t, 2), "INDEP_pooled": round(i, 2),
                    "optimism_pp": round(t - i, 2), "n_queries": n,
                    "archive_boot_CI95": [round(float(lo), 2), round(float(hi), 2)]}
    print(f"\nPOOLED {arm}: TRANS={t:.2f} INDEP={i:.2f} optimism={t-i:+.2f} pp "
          f"(n={n}) archive-boot CI95 [{lo:.2f},{hi:.2f}]")

results["_SUMMARY"] = summary
json.dump(results, open(OUT, "w"), indent=1)
print("\nyazildi:", OUT)
