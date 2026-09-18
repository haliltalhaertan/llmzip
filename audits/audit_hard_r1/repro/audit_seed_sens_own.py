"""OWN audit code: seed sensitivity of the T3 192->384 delta on Kong Tingting (n=293).

Recipe adapted from the published ablation path (documented adaptation): TF-IDF word
(1-2g, english stop, sublinear) + char_wb (3-5g) + LSA32 (seed 5101, fixed: fidelity
anchor) then final SVD with k_eff=min(k,n-1), seeds {5204, 1, 999}. Scorers sym /
qscale / asym, own tie-break (TIE_SALT top10-r1) and FR@3. Question: does the
standardized decline persist across final-SVD seeds, or is it a one-seed event?
"""
import ast, hashlib, json, pickle
from collections import defaultdict
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

import sys as _sys
BASE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2"
ARCH_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
Q_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
CHAR = _sys.argv[1] if len(_sys.argv) > 1 else "Kong Tingting"
SEEDS = [5204, 1, 999]

qa = json.load(open(BASE + "/perltqa_en_v2.json"))
mem = json.load(open(BASE + "/perltmem_en_v2.json"))
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem])
ORD = {c: i for i, c in enumerate(BANKED)}
arch_cache = pickle.load(open(ARCH_PKL, "rb"))
QDAT = pickle.load(open(Q_PKL, "rb"))
SEC = {"profile": "PRF", "social_relationship": "SOC", "events": "EVE", "dialogues": "DLG"}

def parse_social(v):
    return v if isinstance(v, dict) else ast.literal_eval(v)

def build_items(char):
    b = mem[char]
    items = []
    for i, (f, v) in enumerate(b["profile"].items()):
        items.append((f"PQ{ORD[char]:03d}_PRF_{i:03d}", f"[profile] {f}: {v}"))
    items.append((f"PQ{ORD[char]:03d}_DSC_000", f"[profile_description] {b['profile_description']}"))
    soc = parse_social(b["social_relationship"])
    for i, k in enumerate(sorted(soc.keys())):
        e = soc[k]
        extra = "".join(f"; {kk}: {vv}" for kk, vv in sorted(e.items())
                        if kk not in ("Supporting Characters", "Relationship", "Description"))
        items.append((f"PQ{ORD[char]:03d}_SOC_{i:03d}",
                      f"[social {k}] {e.get('Supporting Characters','')} ({e.get('Relationship','')}): {e.get('Description','')}{extra}"))
    for i, k in enumerate(sorted(b["events"].keys())):
        ev = b["events"][k]
        content = ev["content"] if isinstance(ev, dict) and "content" in ev else (ev if isinstance(ev, str) else json.dumps(ev))
        items.append((f"PQ{ORD[char]:03d}_EVE_{i:03d}", f"[event {k}] {content}"))
    t = 0
    for k in sorted(b["dialogues"].keys()):
        for ts in sorted(b["dialogues"][k]["contents"].keys()):
            for turn in b["dialogues"][k]["contents"][ts]:
                items.append((f"PQ{ORD[char]:03d}_DLG_{t:03d}", f"[dialogue {k} @ {ts}] {turn}"))
                t += 1
    return items

def collect_questions():
    out = {}
    for entry in qa:
        for char, d in entry.items():
            if char not in mem or char not in arch_cache:
                continue
            for qi, q in enumerate(d["profile"]):
                out[f"PQ{ORD[char]:03d}_PRF_q{qi:03d}"] = str(q["Question"])
            for s in ["social_relationship", "events", "dialogues"]:
                qi = 0
                for g_ in d[s]:
                    k = list(g_.keys())[0]
                    for q in list(g_.values())[0]:
                        out[f"PQ{ORD[char]:03d}_{SEC[s]}_q{qi:03d}"] = str(q["Question"])
                        qi += 1
    return out

QTEXT = collect_questions()

def topk(scores, aid, k):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k]

items = build_items(CHAR)
texts = [t for _, t in items]
N = len(items)
assert N == arch_cache[CHAR]["N"], (N, arch_cache[CHAR]["N"])
wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
Xw = normalize(wv.fit_transform(texts))
Xc = normalize(cv.fit_transform(texts))
d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
svd = TruncatedSVD(n_components=d, random_state=5101)
Xl = normalize(svd.fit_transform(Xw))
Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
qids = sorted([q for q, r in QDAT.items() if r["char"] == CHAR])
questions = [QTEXT[q] for q in qids]
Qw = normalize(wv.transform(questions))
Qc = normalize(cv.transform(questions))
Ql = normalize(svd.transform(Qw))
Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
golds = [np.asarray(QDAT[q]["gold"]).ravel() for q in qids]
print(f"{CHAR}: N={N} nq={len(qids)}", flush=True)

def fr3_for(S_col, gold):
    t3 = topk(S_col, CHAR, 3)
    g = set(int(x) for x in np.asarray(gold).ravel().tolist())
    return len([x for x in t3 if x in g]) / len(g)

print(f"{'seed':>6s} " + " ".join(f"{c:>22s}" for c in ["dFR3 sym", "dFR3 qscale", "dFR3 asym"]))
results = {}
for seed in SEEDS:
    fr = {}
    for k in (192, 384):
        k_eff = min(k, N - 1, min(Z.shape) - 1)
        s2 = TruncatedSVD(n_components=k_eff, random_state=seed)
        Y = normalize(s2.fit_transform(Z))
        mu = Y.mean(axis=0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        QC = (normalize(s2.transform(Zq)) - mu).astype(np.float64)
        if k == 96 or seed == 5204 and k == 192:
            pass
        Db = np.where(C >= 0, 1.0, -1.0)
        sigma = C.std(axis=0, ddof=0)
        sigma[sigma < 1e-12] = 1e-12
        S = {"sym": Db @ np.where(QC >= 0, 1.0, -1.0).T,
             "qscale": Db @ (QC / sigma).T,
             "asym": Db @ QC.T}
        for sc in S:
            fr[(k, sc)] = float(np.mean([fr3_for(S[sc][:, j], golds[j]) for j in range(len(qids))]))
    d = {sc: 100 * (fr[(384, sc)] - fr[(192, sc)]) for sc in ("sym", "qscale", "asym")}
    results[seed] = {**{f"k{k}/{sc}": round(100 * fr[(k, sc)], 2) for k in (192, 384) for sc in ("sym", "qscale", "asym")}, **{f"d_{sc}": round(d[sc], 2) for sc in d}}
    print(f"{seed:6d} " + " ".join(f"{d[sc]:+22.2f}" for sc in ("sym", "qscale", "asym")), flush=True)
_fn = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r1/repro/seed_sens_" + "".join(c for c in CHAR if c.isalnum()) + ".json"
json.dump(results, open(_fn, "w"), indent=1)
print("WROTE " + _fn)
