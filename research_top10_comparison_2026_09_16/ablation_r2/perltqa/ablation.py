"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
PerLTQA channel ablation: FULL / NO_LSA / NO_CHAR / WORD_ONLY x sym / qscale.
Frozen recipe rebuilt verbatim (see fidelity_gate.py; FIDELITY_GATE.json PASS written first).
Final SVD always 96 comps, seed 5204; LSA32 seed 5101. 12-byte sign coding.
Writes per_query.jsonl (streamed per archive), RESULTS.json, and prints summary.
"""
import ast
import json
import pickle
import sys
import time

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

sys.path.insert(0, "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/audit")
import audit_baseline_lib as abl

BASE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2"
ARCH_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
Q_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
ARMS = ["FULL", "NO_LSA", "NO_CHAR", "WORD_ONLY"]
SCORERS = ["sym", "qscale"]

qa = json.load(open(BASE + "/perltqa_en_v2.json"))
mem = json.load(open(BASE + "/perltmem_en_v2.json"))
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem])
ORD = {c: i for i, c in enumerate(BANKED)}
arch_cache = pickle.load(open(ARCH_PKL, "rb"))
QDAT = pickle.load(open(Q_PKL, "rb"))
chars = sorted(arch_cache.keys())
assert len(chars) == 30

# questions per archive in deterministic order; question text re-resolved exactly as step2_build
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


# qid -> question text: replay step2_build gold mapping to recover exact question strings
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
assert set(QTEXT) >= set(QDAT), "missing question texts"
# every evaluated qid must resolve
assert set(QDAT) <= set(QTEXT)

# fast deterministic top-K, exactly equivalent to abl.det_top10 (verified below on samples)
tie_cache = {}


def fast_topk(scores, archive_id, k):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    key = (archive_id, len(s))
    tb = tie_cache.get(key)
    if tb is None:
        import hashlib
        hs = [hashlib.sha256(f"top10-r1|{archive_id}|{r}".encode()).hexdigest() for r in range(len(s))]
        tb = np.array(sorted(range(len(s)), key=lambda r: (hs[r], r)))
        tie_cache[key] = tb
    ordered = tb[np.argsort(-m[tb], kind="stable")]
    return ordered[:k]


# verify equivalence on random samples before trusting (fails loudly on mismatch)
rng = np.random.default_rng(0)
verified = 0
for char in chars[:3]:
    N = arch_cache[char]["N"]
    for _ in range(5):
        s = rng.normal(size=N)
        s[rng.random(N) < 0.3] = s[0]  # force ties
        for k in (3, 10):
            a = np.asarray(abl.det_top10(s, char, k)).tolist()
            b = np.asarray(fast_topk(s, char, k)).tolist()
            assert a == b, f"fast_topk mismatch {char} k={k}"
            verified += 1
print(f"fast_topk verified on {verified} samples", flush=True)

cost = {a: {"z_features": {}, "build_s": {}} for a in ARMS}
per_arch_rows = []  # accumulate metric rows for RESULTS + bootstrap
fout = open("per_query.jsonl", "w")
t_all = time.time()
n_q_total = 0
for ci, char in enumerate(chars):
    t_arch = time.time()
    items = build_items(char)
    texts = [t for _, t in items]
    N = len(items)
    assert N == arch_cache[char]["N"]
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    blocks = {"lsa": sparse.csr_matrix(Xl), "word": Xw, "char": Xc}
    arm_blocks = {"FULL": ["lsa", "word", "char"], "NO_LSA": ["word", "char"],
                  "NO_CHAR": ["lsa", "word"], "WORD_ONLY": ["word"]}
    qids = sorted([q for q, r in QDAT.items() if r["char"] == char])
    questions = [QTEXT[q] for q in qids]
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(svd.transform(Qw))
    Qblocks = {"lsa": sparse.csr_matrix(Ql), "word": Qw, "char": Qc}
    golds = [np.asarray(QDAT[q]["gold"]).ravel() for q in qids]
    secs = [QDAT[q]["section"] for q in qids]
    for arm in ARMS:
        t0 = time.time()
        Z = sparse.hstack([blocks[b] for b in arm_blocks[arm]], format="csr")
        assert min(Z.shape) > 96, f"{char} {arm}: Z {Z.shape} violates min>96"
        Zq = sparse.hstack([Qblocks[b] for b in arm_blocks[arm]], format="csr")
        s96 = TruncatedSVD(n_components=96, random_state=5204)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        QY = normalize(s96.transform(Zq))
        QC = (QY - mu).astype(np.float64)
        cost[arm]["z_features"][char] = int(Z.shape[1])
        cost[arm]["build_s"][char] = cost[arm]["build_s"].get(char, 0.0) + (time.time() - t0)
        # sanity: FULL must match cached production C signs (already gated, re-assert)
        if arm == "FULL":
            Cc = np.asarray(arch_cache[char]["C"], dtype=np.float64)
            assert C.shape == Cc.shape and np.count_nonzero((C >= 0) != (Cc >= 0)) == 0, f"{char} FULL drift"
        Db = (C >= 0)
        Dpm = np.where(Db, 1.0, -1.0)
        assert Dpm.shape[1] == 96
        payload_b = int(np.packbits(Db, axis=-1, bitorder="big").shape[1])
        assert payload_b == 12, f"{char} {arm}: payload {payload_b}B != 12B"
        sigma = np.std(C, axis=0, ddof=0)
        sigma = np.where(sigma < 1e-12, 1e-12, sigma)
        Qpm = np.where(QC >= 0, 1.0, -1.0)
        S_sym = -(96.0 - Dpm @ Qpm.T) / 2.0  # == -Hamming exactly
        S_q = Dpm @ (QC / sigma).T
        # spot-check sym against count_nonzero on first 3 queries
        for j in range(min(3, len(qids))):
            exact = -np.count_nonzero(Db != (QC[j] >= 0)[None, :], axis=1).astype(np.float64)
            assert np.array_equal(S_sym[:, j], exact), f"{char} {arm}: sym mismatch"
        for j, qid in enumerate(qids):
            gold = golds[j]
            for scorer, S in (("sym", S_sym[:, j]), ("qscale", S_q[:, j])):
                top10 = fast_topk(S, char, 10)
                top3 = fast_topk(S, char, 3)
                hit10, _, _ = abl.hrn(top10, gold, 10)
                hit3, rec3, _ = abl.hrn(top3, gold, 3)
                exp10 = abl.expected_hit(S, gold, 10)
                fout.write(json.dumps({"qid": qid, "char": char, "section": secs[j], "arm": arm,
                                       "scorer": scorer, "top10": [int(x) for x in top10],
                                       "gold": [int(x) for x in gold], "hit10": hit10, "fr3": rec3,
                                       "hit3": hit3, "exp_hit10": exp10}) + "\n")
                per_arch_rows.append((qid, char, arm, scorer, hit10, rec3, hit3, exp10))
    n_q_total += len(qids)
    fout.flush()
    print(f"[{ci+1}/30] {char} N={N} nq={len(qids)} {time.time()-t_arch:.1f}s", flush=True)
fout.close()
print(f"per_query rows: {n_q_total * 8}, total {time.time()-t_all:.1f}s", flush=True)

# ---- aggregates ----
import collections
agg = {}
for arm in ARMS:
    agg[arm] = {}
    for sc in SCORERS:
        vals = [(h, f, h3, e) for (q, c, a, s, h, f, h3, e) in per_arch_rows if a == arm and s == sc]
        A = np.array(vals)
        agg[arm][sc] = {"n": len(vals), "hit10": float(A[:, 0].mean()), "fr3": float(A[:, 1].mean()),
                        "hit3": float(A[:, 2].mean()), "exp_hit10": float(A[:, 3].mean())}
by_arch = {}
for arm in ARMS:
    by_arch[arm] = {}
    for sc in SCORERS:
        by_arch[arm][sc] = {}
        for char in chars:
            vals = [(h, f, h3, e) for (q, c, a, s, h, f, h3, e) in per_arch_rows if a == arm and s == sc and c == char]
            A = np.array(vals)
            by_arch[arm][sc][char] = {"n": len(vals), "hit10": float(A[:, 0].mean()), "fr3": float(A[:, 1].mean()),
                                      "hit3": float(A[:, 2].mean()), "exp_hit10": float(A[:, 3].mean())}

# ---- paired archive-clustered bootstrap, 20000 reps, seed 20260916 ----
R = 20000
brng = np.random.default_rng(20260916)
counts = brng.multinomial(30, [1 / 30] * 30, size=R)  # (R,30) cluster multiplicities
cidx = {c: i for i, c in enumerate(chars)}
contrasts = {}
for arm in ["NO_LSA", "NO_CHAR", "WORD_ONLY"]:
    contrasts[arm] = {}
    for sc in SCORERS:
        contrasts[arm][sc] = {}
        for m, pos in (("hit10", 4), ("fr3", 5), ("hit3", 6), ("exp_hit10", 7)):
            # per-query paired diffs in fixed query order
            diffs = np.array([row[pos] for row in per_arch_rows if row[2] == arm and row[3] == sc]) - \
                    np.array([row[pos] for row in per_arch_rows if row[2] == "FULL" and row[3] == sc])
            qchars = [row[1] for row in per_arch_rows if row[2] == arm and row[3] == sc]
            assert len(diffs) == len(QDAT) == 8265
            cs = np.array([np.sum([d for d, c in zip(diffs, qchars) if c == ch]) for ch in chars])
            ns = np.array([sum(1 for c in qchars if c == ch) for ch in chars])
            num = counts @ cs
            den = counts @ ns
            boots = num / den
            lo, hi = np.quantile(boots, [0.025, 0.975])
            contrasts[arm][sc][m] = {"diff": float(diffs.mean()), "ci_lo": float(lo), "ci_hi": float(hi),
                                     "excludes_zero": bool(lo > 0 or hi < 0)}

results = {
    "label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
    "benchmark": "PerLTQA en_v2, 30 archives (clusters), 8265 queries",
    "seeds": {"LSA32": 5101, "SVD96": 5204, "bootstrap": 20260916, "bootstrap_reps": R},
    "aggregate": agg,
    "per_archive": by_arch,
    "contrasts_vs_FULL_pp": {a: {s: {m: {"diff_pp": v["diff"] * 100, "ci_lo_pp": v["ci_lo"] * 100,
                                          "ci_hi_pp": v["ci_hi"] * 100, "excludes_zero": v["excludes_zero"]}
                                      for m, v in d.items()} for s, d in dd.items()} for a, dd in contrasts.items()},
    "cost": {a: {"z_features_per_archive": cost[a]["z_features"],
                 "mean_z_features": float(np.mean(list(cost[a]["z_features"].values()))),
                 "build_s_per_archive": cost[a]["build_s"],
                 "total_build_s": float(sum(cost[a]["build_s"].values()))} for a in ARMS},
    "payload_bytes_per_doc": 12,
}
json.dump(results, open("RESULTS.json", "w"), indent=2)
print(json.dumps(agg, indent=1))
print(json.dumps(results["contrasts_vs_FULL_pp"], indent=1))
