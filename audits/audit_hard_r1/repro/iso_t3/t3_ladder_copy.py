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
ARMS = ["FULL"]  # T3: k-ladder, not channel arms
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


# ============================================================================
# T3 — PerLTQA k<n ladder on the 8 archives with n<384.
# Setup above is the VERIFIED ablation path (bit-exact vs cached C, seeds 5101/5204).
# Only the arm definition changes: instead of channel masks, we sweep k with
# k_eff = min(k, n-1) and score standardized (qscale, sym) AND unstandardized (asym).
# ============================================================================
KS = [96, 192, 384]
small = sorted([c for c in chars if arch_cache[c]["N"] < 384], key=lambda c: arch_cache[c]["N"])
# AUDIT ADAPTATION (own dir, bounded probe): 2 smallest archives only.
small = [c for c in small if c in ("Kong Tingting", "Zhu Xiaolong")]
assert len(small) == 2, small
print(f"archives with n<384: {len(small)}", flush=True)

rows = []
gate_total = {"diff": 0, "bits": 0}
t_all = time.time()
for ci, char in enumerate(small):
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

    Z = sparse.hstack([blocks[b] for b in ["lsa", "word", "char"]], format="csr")
    Zq = sparse.hstack([Qblocks[b] for b in ["lsa", "word", "char"]], format="csr")
    for k in KS:
        k_eff = min(k, N - 1, min(Z.shape) - 1)
        s2 = TruncatedSVD(n_components=k_eff, random_state=5204)
        Y = normalize(s2.fit_transform(Z))
        mu = Y.mean(axis=0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        QC = (normalize(s2.transform(Zq)) - mu).astype(np.float64)
        if k == 96:
            Cc = arch_cache[char]["C"]
            nd = int(np.count_nonzero((C >= 0) != (Cc >= 0)))
            gate_total["diff"] += nd
            gate_total["bits"] += int(C.size)
        Db = C >= 0
        Dpm = np.where(Db, 1.0, -1.0)
        sigma = C.std(axis=0, ddof=0)
        sigma[sigma < 1e-12] = 1e-12
        n_const = int(np.sum(C.std(axis=0, ddof=0) < 1e-12))
        S = {"sym": Dpm @ np.where(QC >= 0, 1.0, -1.0).T,
             "qscale": Dpm @ (QC / sigma).T,
             "asym": Dpm @ QC.T}
        for j, qid in enumerate(qids):
            gold = golds[j]
            for scorer in ("sym", "qscale", "asym"):
                top10 = fast_topk(S[scorer][:, j], char, 10)
                top3 = fast_topk(S[scorer][:, j], char, 3)
                h10, _, _ = abl.hrn(top10, gold, 10)
                _, rec3, _ = abl.hrn(top3, gold, 3)
                rows.append((char, N, k, k_eff, n_const, scorer, qid, h10, rec3))
    print(f"[{ci+1}/{len(small)}] {char} N={N} nq={len(qids)} const_dims@384="
          f"{n_const} {time.time()-t_all:.0f}s", flush=True)

print(f"\n=== FIDELITY GATE (k=96 vs cached): {gate_total['diff']} differing of {gate_total['bits']} bits ===")

import collections
agg = collections.defaultdict(list)
const_at = {}
for char, N, k, k_eff, n_const, scorer, qid, h10, rec3 in rows:
    agg[(k, scorer)].append((h10, rec3))
    if k == 384:
        const_at[char] = (N, k_eff, n_const)

print("\nconstant dimensions at k=384 (the rank-overflow mechanism):")
for c, (N, ke, nc) in sorted(const_at.items(), key=lambda x: x[1][0]):
    print(f"   {c:22s} n={N:4d} k_eff={ke:4d} constant_dims={nc}")

print(f"\n{'arm':16s} {'Hit@10':>8s} {'FR@3':>8s}  (n={len(agg[(96,'sym')])} queries)")
out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
       "scope": "PerLTQA archives with n<384", "n_archives": len(small),
       "gate": gate_total, "const_dims_at_384": {c: {"n": v[0], "k_eff": v[1], "const": v[2]}
                                                  for c, v in const_at.items()},
       "arms": {}}
for k in KS:
    for sc in ("sym", "qscale", "asym"):
        v = np.array(agg[(k, sc)])
        out["arms"][f"k{k}/{sc}"] = {"hit10": 100*float(v[:,0].mean()), "fr3": 100*float(v[:,1].mean()),
                                     "n": len(v)}
        print(f"k{k}/{sc:8s} {100*v[:,0].mean():8.2f} {100*v[:,1].mean():8.2f}")

print("\n192 -> 384 change (the contested step):")
for sc in ("qscale", "sym", "asym"):
    d_fr = out["arms"][f"k384/{sc}"]["fr3"] - out["arms"][f"k192/{sc}"]["fr3"]
    d_h = out["arms"][f"k384/{sc}"]["hit10"] - out["arms"][f"k192/{sc}"]["hit10"]
    lab = "standardized" if sc in ("sym", "qscale") else "UNstandardized"
    print(f"  {sc:8s} ({lab:14s}) FR@3 {d_fr:+6.2f}   Hit@10 {d_h:+6.2f}")
    out.setdefault("delta_192_384", {})[sc] = {"fr3": d_fr, "hit10": d_h}

import os as _os
_out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "T3_2ARCH.json")
json.dump(out, open(_out, "w"), indent=1)
print(f"\nWROTE {_out}")
