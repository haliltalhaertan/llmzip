"""Ladder-INDEP audit: verbatim adaptation of t_inductive_all10.py parametrized by k.

Reference copy (unmodified): t_inductive_all10_REF_COPY.py in this directory
(sha256 c352c7241517500c48b49e72729991d8d08169840455bb4a1b6b64cb9984aaa3).
Adaptations vs reference: (1) second-stage SVD n_components=K from argv instead of
hardcoded 96; (2) OUT path inside this directory per-k; (3) K recorded per archive;
(4) per-fit try/except so one rank-limit failure cannot kill the whole sweep.
All seeds, vectorizer params, det_top10 tie-break, scoring, and bootstrap seed (20260917,
4000 resamples) are byte-identical to the reference.
Usage: ml-python t_ladder_k.py <K> [subset, e.g. RT05 or RT01,RT02,...]
"""
import hashlib, json, pickle, sys, traceback
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

K = int(sys.argv[1]) if len(sys.argv) > 1 else 96
SUB = None
if len(sys.argv) > 2:
    SUB = [s.strip() for s in sys.argv[2].split(",") if s.strip()]

R = "/mnt/c/Users/MDP/dev/llmzip-work"
DATA = R + "/top10_comparison_r1/data"
ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]
if SUB:
    ARCHIVES = [a for a in ARCHIVES if a in SUB]
MYDIR = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r4/ladder_indep"
OUT = f"{MYDIR}/INDUCTIVE_K{K}.json"


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
    sk = TruncatedSVD(n_components=k, random_state=5204)
    Y = normalize(sk.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    return wv, cv, sv, sk, mu, {"Z_shape": list(Z.shape), "dd": dd}


def encode(wv, cv, sv, sk, mu, texts):
    Qw = normalize(wv.transform(texts))
    Qc = normalize(cv.transform(texts))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(sk.transform(Zq)) - mu).astype(np.float64)


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

    try:
        P_t = fit_projector(docs_h, K)
        C_t = encode(*P_t[:5], docs_h); Q_t = encode(*P_t[:5], qtexts)
        z_trans = P_t[5]
        trans_err = None
    except Exception as e:
        trans_err = f"{type(e).__name__}: {e}"
        C_t = Q_t = None
        z_trans = {"Z_shape": None, "dd": None}

    bg = []
    for a in [f"RT{i:02d}" for i in range(1, 11)]:
        if a != held:
            bg.extend(load(a)[0])
    try:
        P_i = fit_projector(bg, K)
        C_i = encode(*P_i[:5], docs_h); Q_i = encode(*P_i[:5], qtexts)
        z_indep = P_i[5]
        indep_err = None
    except Exception as e:
        indep_err = f"{type(e).__name__}: {e}"
        C_i = Q_i = None
        z_indep = {"Z_shape": None, "dd": None}

    if K == 96 and C_t is not None:
        try:
            Cc = np.asarray(pickle.load(
                open(R + f"/bench3/runs/b3a_realtalk/rt_repr/{held}.pkl", "rb"))["C"])
            dbits = int(np.count_nonzero((C_t >= 0) != (Cc >= 0))); tot = int(Cc.size)
        except Exception:
            dbits, tot = -1, -1
    else:
        dbits, tot = (-2, -2)  # gate defined only at k=96 (cached repr is 96-dim)

    if C_t is not None:
        rt = score(C_t, Q_t, gold, held)
    else:
        rt = {"sym": float("nan"), "sym_perq": [], "qscale": float("nan"), "qscale_perq": []}
    if C_i is not None:
        ri = score(C_i, Q_i, gold, held)
    else:
        ri = {"sym": float("nan"), "sym_perq": [], "qscale": float("nan"), "qscale_perq": []}
    results[held] = {
        "k": K, "n_docs": len(docs_h), "n_q": len(qs), "bg_docs": len(bg),
        "gate_diff_bits": dbits, "gate_total_bits": tot,
        "Z_trans": z_trans, "Z_indep": z_indep,
        "trans_err": trans_err, "indep_err": indep_err,
        "TRANS": {kk: v for kk, v in rt.items() if not kk.endswith("_perq")},
        "INDEP": {kk: v for kk, v in ri.items() if not kk.endswith("_perq")},
        "perq": {"trans_sym": rt["sym_perq"], "trans_qscale": rt["qscale_perq"],
                 "indep_sym": ri["sym_perq"], "indep_qscale": ri["qscale_perq"]},
    }
    print(f"{held} k={K} n={len(qs)} gate={dbits}/{tot} | TRANS sym={rt['sym']:.2f} "
          f"qs={rt['qscale']:.2f} | INDEP sym={ri['sym']:.2f} qs={ri['qscale']:.2f}"
          + (f" [TRANS_ERR {trans_err}]" if trans_err else "")
          + (f" [INDEP_ERR {indep_err}]" if indep_err else "")
          + f" Zt={z_trans['Z_shape']} Zi={z_indep['Z_shape']}", flush=True)
    json.dump(results, open(OUT, "w"), indent=1)


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
                    "optimism_pp": round(t - i, 2), "n_queries": n, "k": K,
                    "n_archives": len(results),
                    "archive_boot_CI95": [round(float(lo), 2), round(float(hi), 2)]}
    print(f"\nPOOLED k={K} {arm}: TRANS={t:.2f} INDEP={i:.2f} optimism={t-i:+.2f} pp "
          f"(n={n}, arch={len(results)}) archive-boot CI95 [{lo:.2f},{hi:.2f}]")

results["_SUMMARY"] = summary
json.dump(results, open(OUT, "w"), indent=1)
print("\nyazildi:", OUT)
