"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

repr_math: fix the REPRESENTATION before quantization. Payload stays exactly 96 bits / 12 B.

Family A - IDF-power reweighting: multiply the WORD block's column j by idf_j^p
  (idf from DOCUMENTS ONLY, per archive), L2-renormalize rows as production does,
  then the identical SVD96/normalize/center/sign chain. p in {0, 0.5, 1.0, 2.0}.
  NOTE: the LSA32 block is kept exactly as production (fit on unweighted Xw);
  only the WORD block inside Z is reweighted. p=0 must reproduce FULL bit-exactly.
Family B - all-but-the-top: SVD with 96+m components, USE components m+1..m+96
  (normalize full width, slice, then center on the slice, then sign).
  m in {0, 1, 2, 4}. m=0 must reproduce FULL bit-exactly.

Runs on BOTH benchmarks: RealTalk (10 archives, 705 queries) and PerLTQA (30 archives, 8265).
Never averages across benchmarks.

Stages:
  1. FIDELITY GATE (FULL rebuild vs cache, both benchmarks) -> FIDELITY_GATE.json
     Gate must pass or the script STOPS before any new arm number.
  2. Arms x scorers -> per_query.jsonl (streamed), RESULTS.json

Usage: $HOME/muse-work/ml-python repr_math.py   (run inside this directory)
"""
import ast
import hashlib
import importlib.util
import json
import os
import pickle
import re
import sys
import time
from collections import Counter, defaultdict

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_RT = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"
CACHE_RT = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"
FROZEN = "/mnt/c/Users/MDP/dev/llmzip-work/drive/v52_t4d_locomo_frozen_cross_benchmark.py"
AUDIT_LIB = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/audit/audit_baseline_lib.py"
PERLTQA_BASE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2"
PERLTQA_ARCH = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PERLTQA_Q = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"

RT_ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]
ARMS_A = [("IDF_p0", 0.0), ("IDF_p0.5", 0.5), ("IDF_p1", 1.0), ("IDF_p2", 2.0)]
ARMS_B = [("SHIFT_m0", 0), ("SHIFT_m1", 1), ("SHIFT_m2", 2), ("SHIFT_m4", 4)]
ARM_ORDER = ["FULL"] + [a for a, _ in ARMS_A] + [a for a, _ in ARMS_B]
NONCTRL = [a for a, _ in ARMS_A if a != "IDF_p0"] + [a for a, _ in ARMS_B if a != "SHIFT_m0"]
SELFCHECK = ["IDF_p0", "SHIFT_m0"]  # must reproduce FULL bit-exactly
SCORERS = ["sym", "qscale"]
BOOT_REPS = 20000
BOOT_SEED = 20260916
SVD_SEED = 5204
LSA_SEED = 5101

# G2 production targets (coordinator-specified)
G2_RT = {"qscale_hit10": 49.6454, "sym_det_hit10": 46.5248, "sym_exp_hit10": 46.6809,
         "qscale_fr3": 22.41, "n": 705}
G2_PQ = {"qscale_hit10": 80.0000, "sym_det_hit10": 75.6806, "sym_exp_hit10": 75.7612,
         "qscale_fr3": 53.24, "n": 8265}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


audit = load_module("audit_baseline_lib_ro", AUDIT_LIB)
frozen = load_module("frozen_builder_ro", FROZEN)
assert frozen.SVD_SEED == SVD_SEED, "SVD seed mismatch"

# ---------- shared builders (verbatim frozen recipe) ----------

def fit_base(texts):
    """Frozen source-block family: word+char tfidf, LSA32 on word. Returns fitted parts."""
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                         sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=LSA_SEED)
    Xl = normalize(svd.fit_transform(Xw))
    return wv, cv, svd, Xw, Xc, Xl


def query_blocks(wv, cv, svd, questions):
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(svd.transform(Qw))
    return Qw, Qc, Ql


def reweight_word(Xw_n, Qw_n, idf, p):
    """Family A: extra idf power on the WORD block (docs-only idf), then row-renormalize."""
    w = np.power(np.asarray(idf, dtype=np.float64), float(p))
    Xwr = normalize(Xw_n @ sparse.diags(w))
    Qwr = normalize(Qw_n @ sparse.diags(w))
    return Xwr, Qwr


def fit_final(Z, Zq, m):
    """Final SVD chain: normalize full width, slice cols m:, center on slice, sign later."""
    s = TruncatedSVD(n_components=96 + m, random_state=SVD_SEED)
    Y = normalize(s.fit_transform(Z))
    if m:
        Y = Y[:, m:]
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    QY = normalize(s.transform(Zq))
    if m:
        QY = QY[:, m:]
    QC = (QY - mu).astype(np.float64)
    return C, QC


# ---------- fast deterministic top-K (verified equivalent to audit.det_top10) ----------
tie_cache = {}


def fast_topk(scores, archive_id, k):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    key = (archive_id, len(s))
    tb = tie_cache.get(key)
    if tb is None:
        hs = [hashlib.sha256(f"top10-r1|{archive_id}|{r}".encode()).hexdigest()
              for r in range(len(s))]
        tb = np.array(sorted(range(len(s)), key=lambda r: (hs[r], r)))
        tie_cache[key] = tb
    return tb[np.argsort(-m[tb], kind="stable")][:k]


def verify_topk(chars_or_ids, sizes, seed=0):
    rng = np.random.default_rng(seed)
    n = 0
    for aid, N in zip(chars_or_ids, sizes):
        for _ in range(3):
            s = rng.normal(size=N)
            s[rng.random(N) < 0.3] = s[0]
            for k in (3, 10):
                a = np.asarray(audit.det_top10(s, aid, k)).tolist()
                b = np.asarray(fast_topk(s, aid, k)).tolist()
                assert a == b, f"fast_topk mismatch {aid} k={k}"
                n += 1
    return n


def score_mats(C, QC):
    """Vectorized sym + qscale score matrices (N_docs x N_queries). Docs-only sigma."""
    Db = (C >= 0)
    Dpm = np.where(Db, 1.0, -1.0)
    sigma = np.std(np.asarray(C, dtype=np.float64), axis=0, ddof=0)
    sigma = np.where(sigma < 1e-12, 1e-12, sigma)
    Qpm = np.where(QC >= 0, 1.0, -1.0)
    S_sym = (Dpm @ Qpm.T - 96.0) / 2.0  # == -Hamming exactly
    S_q = Dpm @ (QC / sigma).T
    return S_sym, S_q, Db


def metrics_from_top(top10, gold):
    hit10, _, _ = audit.hrn(top10, gold, 10)
    top3 = np.asarray(top10)[:3]
    hit3, fr3, _ = audit.hrn(top3, gold, 3)
    return float(hit10), float(fr3), float(hit3)


# ---------- data loading ----------
def load_realtalk():
    raw = {}
    for a in RT_ARCHIVES:
        with open(os.path.join(DATA_RT, a + ".json")) as f:
            d = json.load(f)
        docs = sorted(d["docs"], key=lambda r: r["row"])
        assert [r["row"] for r in docs] == list(range(len(docs)))
        raw[a] = {
            "texts": [r["text"] for r in docs],
            "doc_ids": [r["id"] for r in docs],
            "queries": [{"qid": q["qid"], "text": q["text"],
                         "gold": [int(g) for g in q["gold"]],
                         "category": q.get("category")} for q in d["queries"]],
        }
    cached = {}
    for a in RT_ARCHIVES:
        with open(os.path.join(CACHE_RT, a + ".pkl"), "rb") as f:
            cached[a] = pickle.load(f)
    return raw, cached


def parse_social(v):
    return v if isinstance(v, dict) else ast.literal_eval(v)


def load_perltqa():
    qa = json.load(open(os.path.join(PERLTQA_BASE, "perltqa_en_v2.json")))
    mem = json.load(open(os.path.join(PERLTQA_BASE, "perltmem_en_v2.json")))
    qachars = [list(e.keys())[0] for e in qa]
    BANKED = sorted([c for c in qachars if c in mem])
    ORD = {c: i for i, c in enumerate(BANKED)}
    arch_cache = pickle.load(open(PERLTQA_ARCH, "rb"))
    QDAT = pickle.load(open(PERLTQA_Q, "rb"))
    chars = sorted(arch_cache.keys())
    assert len(chars) == 30
    return qa, mem, ORD, arch_cache, QDAT, chars


def build_items_pq(char, mem, ORD):
    b = mem[char]
    items = []
    for i, (f, v) in enumerate(b["profile"].items()):
        items.append((f"PQ{ORD[char]:03d}_PRF_{i:03d}", f"[profile] {f}: {v}"))
    items.append((f"PQ{ORD[char]:03d}_DSC_000",
                  f"[profile_description] {b['profile_description']}"))
    soc = parse_social(b["social_relationship"])
    for i, k in enumerate(sorted(soc.keys())):
        e = soc[k]
        extra = "".join(f"; {kk}: {vv}" for kk, vv in sorted(e.items())
                        if kk not in ("Supporting Characters", "Relationship", "Description"))
        items.append((f"PQ{ORD[char]:03d}_SOC_{i:03d}",
                      f"[social {k}] {e.get('Supporting Characters','')} "
                      f"({e.get('Relationship','')}): {e.get('Description','')}{extra}"))
    for i, k in enumerate(sorted(b["events"].keys())):
        ev = b["events"][k]
        content = (ev["content"] if isinstance(ev, dict) and "content" in ev
                   else (ev if isinstance(ev, str) else json.dumps(ev)))
        items.append((f"PQ{ORD[char]:03d}_EVE_{i:03d}", f"[event {k}] {content}"))
    t = 0
    for k in sorted(b["dialogues"].keys()):
        for ts in sorted(b["dialogues"][k]["contents"].keys()):
            for turn in b["dialogues"][k]["contents"][ts]:
                items.append((f"PQ{ORD[char]:03d}_DLG_{t:03d}",
                              f"[dialogue {k} @ {ts}] {turn}"))
                t += 1
    return items


SEC = {"profile": "PRF", "social_relationship": "SOC", "events": "EVE", "dialogues": "DLG"}


def collect_qtext_pq(qa, mem, arch_cache, ORD):
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


# ---------- fidelity gate ----------
def gate_realtalk(raw, cached):
    per_arch = {}
    rebuilt = {}
    g1_diff = 0
    g1_total = 0
    g1_maxabs = 0.0
    g1_qc_diff = 0
    t0 = time.perf_counter()
    for a in RT_ARCHIVES:
        texts = raw[a]["texts"]
        qs = [q["text"] for q in raw[a]["queries"]]
        payload = frozen.fit_input_payload(list(texts))
        wv, cv, sv, Xw, Xc, Xl = frozen.fit_archive_representation(payload)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(axis=0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        Qw = normalize(wv.transform(qs))
        Qc = normalize(cv.transform(qs))
        Ql = normalize(sv.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
        QC = (normalize(s96.transform(Zq)) - mu).astype(np.float64)
        rebuilt[a] = {"C": C, "QC": QC, "wv": wv, "cv": cv, "sv": sv,
                      "Xw": Xw, "Xc": Xc, "Xl": Xl}
        Cc = np.asarray(cached[a]["C"], dtype=np.float64)
        assert Cc.shape == C.shape, f"{a} shape {C.shape} vs {Cc.shape}"
        g1_diff += int(np.count_nonzero((C >= 0) != (Cc >= 0)))
        g1_total += int(C.size)
        g1_maxabs = max(g1_maxabs, float(np.max(np.abs(C - Cc))))
        # QC check on matched qids (cache may carry pre-excluded extra rows)
        QCc = np.asarray(cached[a]["QC"], dtype=np.float64)
        c2i = {q: i for i, q in enumerate(cached[a]["qids"])}
        qidx = [c2i[q["qid"]] for q in raw[a]["queries"]]
        assert len(set(qidx)) == len(qidx)
        assert all(cached[a]["questions"][i] == q["text"]
                   for i, q in zip(qidx, raw[a]["queries"])), f"{a} qtext mismatch"
        assert all(sorted(map(int, cached[a]["gold_rows"][i])) == sorted(q["gold"])
                   for i, q in zip(qidx, raw[a]["queries"])), f"{a} gold mismatch"
        QCc_m = QCc[np.array(qidx)]
        qd = int(np.count_nonzero(np.sign(QC) != np.sign(QCc_m)))
        g1_qc_diff += qd
        per_arch[a] = {"C_shape": list(C.shape), "QC_shape": list(QC.shape),
                       "qc_sign_diff": qd,
                       "qc_maxabs": float(np.max(np.abs(QC - QCc_m))),
                       "qc_rows_cached": int(QCc.shape[0]),
                       "qc_rows_valid": int(len(qidx))}
    # G2: score REBUILT full over the 705 valid queries
    acc = {s: {"h10": [], "fr3": [], "h3": [], "exp": []} for s in SCORERS}
    for a in RT_ARCHIVES:
        C, QC = rebuilt[a]["C"], rebuilt[a]["QC"]
        S_sym, S_q, _ = score_mats(C, QC)
        for qi, q in enumerate(raw[a]["queries"]):
            gold = q["gold"]
            for s, S in (("sym", S_sym[:, qi]), ("qscale", S_q[:, qi])):
                top10 = audit.det_top10(S, a, 10)
                h10, fr3, h3 = metrics_from_top(top10, gold)
                acc[s]["h10"].append(h10)
                acc[s]["fr3"].append(fr3)
                acc[s]["h3"].append(h3)
                acc[s]["exp"].append(audit.expected_hit(S, gold, 10))
    g2 = {s: {"hit10_pct": float(np.mean(acc[s]["h10"]) * 100),
              "fr3_pct": float(np.mean(acc[s]["fr3"]) * 100),
              "hit3_pct": float(np.mean(acc[s]["h3"]) * 100),
              "exp_hit10_pct": float(np.mean(acc[s]["exp"]) * 100),
              "n": int(len(acc[s]["h10"]))} for s in SCORERS}
    build_s = time.perf_counter() - t0
    return rebuilt, {"diff_bits": g1_diff, "total": g1_total, "maxabs": g1_maxabs,
                     "qc_diff": g1_qc_diff, "per_arch": per_arch, "g2": g2,
                     "build_s": build_s}


def gate_perltqa(qa, mem, ORD, arch_cache, QDAT, chars):
    QTEXT = collect_qtext_pq(qa, mem, arch_cache, ORD)
    assert set(QDAT) <= set(QTEXT), "missing question texts"
    per_arch = {}
    rebuilt = {}
    g1_diff = 0
    g1_total = 0
    g1_maxabs = 0.0
    g1_qc_diff = 0
    t0 = time.perf_counter()
    for char in chars:
        items = build_items_pq(char, mem, ORD)
        texts = [t for _, t in items]
        assert len(items) == arch_cache[char]["N"]
        wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                             sublinear_tf=True)
        cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        Xw = normalize(wv.fit_transform(texts))
        Xc = normalize(cv.fit_transform(texts))
        d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
        svd = TruncatedSVD(n_components=d, random_state=LSA_SEED)
        Xl = normalize(svd.fit_transform(Xw))
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        qids = sorted([q for q, r in QDAT.items() if r["char"] == char])
        questions = [QTEXT[q] for q in qids]
        Qw = normalize(wv.transform(questions))
        Qc = normalize(cv.transform(questions))
        Ql = normalize(svd.transform(Qw))
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
        QC = (normalize(s96.transform(Zq)) - mu).astype(np.float64)
        rebuilt[char] = {"C": C, "QC": QC, "qids": qids, "items": items,
                         "wv": wv, "cv": cv, "svd": svd, "Xw": Xw, "Xc": Xc, "Xl": Xl}
        Cc = np.asarray(arch_cache[char]["C"], dtype=np.float64)
        assert Cc.shape == C.shape
        g1_diff += int(np.count_nonzero((C >= 0) != (Cc >= 0)))
        g1_total += int(C.size)
        g1_maxabs = max(g1_maxabs, float(np.max(np.abs(C - Cc))))
        for j, qid in enumerate(qids):
            qCc = np.asarray(QDAT[qid]["qC"], dtype=np.float64)
            g1_qc_diff += int(np.count_nonzero(np.sign(QC[j]) != np.sign(qCc)))
        per_arch[char] = {"N": len(items), "Z_shape": list(Z.shape), "nq": len(qids)}
    acc = {s: {"h10": [], "fr3": [], "h3": [], "exp": []} for s in SCORERS}
    for char in chars:
        C, QC, qids = rebuilt[char]["C"], rebuilt[char]["QC"], rebuilt[char]["qids"]
        S_sym, S_q, _ = score_mats(C, QC)
        for j, qid in enumerate(qids):
            gold = np.asarray(QDAT[qid]["gold"]).ravel()
            for s, S in (("sym", S_sym[:, j]), ("qscale", S_q[:, j])):
                top10 = audit.det_top10(S, char, 10)
                h10, fr3, h3 = metrics_from_top(top10, gold)
                acc[s]["h10"].append(h10)
                acc[s]["fr3"].append(fr3)
                acc[s]["h3"].append(h3)
                acc[s]["exp"].append(audit.expected_hit(S, gold, 10))
    g2 = {s: {"hit10_pct": float(np.mean(acc[s]["h10"]) * 100),
              "fr3_pct": float(np.mean(acc[s]["fr3"]) * 100),
              "hit3_pct": float(np.mean(acc[s]["h3"]) * 100),
              "exp_hit10_pct": float(np.mean(acc[s]["exp"]) * 100),
              "n": int(len(acc[s]["h10"]))} for s in SCORERS}
    build_s = time.perf_counter() - t0
    return rebuilt, QTEXT, {"diff_bits": g1_diff, "total": g1_total, "maxabs": g1_maxabs,
                            "qc_diff": g1_qc_diff, "per_arch": per_arch, "g2": g2,
                            "build_s": build_s}


# ---------- arm building + scoring ----------
def build_all_arms(Xl, Xw, Xc, Ql, Qw, Qc, idf_w):
    """Returns {arm: (C, QC, build_s)}. IDF_p0/SHIFT_m0 are separate pipeline runs
    used as bit-exact self-checks against FULL (asserted bitwise identical)."""
    out = {}
    Z_full = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    Zq_full = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    t0 = time.perf_counter()
    C_full, QC_full = fit_final(Z_full, Zq_full, 0)
    out["FULL"] = (C_full, QC_full, time.perf_counter() - t0)
    for arm, p in ARMS_A:
        t1 = time.perf_counter()
        Xwr, Qwr = reweight_word(Xw, Qw, idf_w, p)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xwr, Xc], format="csr")
        Zq = sparse.hstack([sparse.csr_matrix(Ql), Qwr, Qc], format="csr")
        C, QC = fit_final(Z, Zq, 0)
        out[arm] = (C, QC, time.perf_counter() - t1)
    for arm, m in ARMS_B:
        t1 = time.perf_counter()
        C, QC = fit_final(Z_full, Zq_full, m)
        out[arm] = (C, QC, time.perf_counter() - t1)
    # self-checks: p=0 and m=0 must reproduce FULL bit-exactly
    checks = {}
    for arm in SELFCHECK:
        C, QC, _ = out[arm]
        db = int(np.count_nonzero((C >= 0) != (C_full >= 0)))
        qb = int(np.count_nonzero(np.sign(QC) != np.sign(QC_full)))
        ma = float(np.max(np.abs(C - C_full)))
        checks[arm] = {"doc_sign_diff": db, "qc_sign_diff": qb, "maxabs": ma,
                       "pass": bool(db == 0 and qb == 0)}
    return out, checks, Z_full.shape[1]


def score_and_emit(bench, arch_id, C, QC, qids, golds, id_lists, arm, fout, store):
    """Vectorized scoring for one archive/arm; writes both scorers' rows."""
    S_sym, S_q, Db = score_mats(C, QC)
    packed = audit.pack_signs_bool(Db)
    assert packed.shape == (C.shape[0], 12), f"{bench}/{arch_id}/{arm} payload {packed.shape}"
    assert audit.decode_pm1(packed).shape == (C.shape[0], 96)
    zero_frac = float(np.mean(C == 0.0))
    # spot-check vectorized sym vs direct Hamming on first query
    chk = -np.count_nonzero(Db != (QC[0] >= 0)[None, :], axis=1).astype(np.float64)
    assert np.array_equal(S_sym[:, 0], chk), f"{bench}/{arch_id}/{arm} sym mismatch"
    doc_ids = id_lists
    for j, qid in enumerate(qids):
        gold = golds[j]
        gold_ids = [doc_ids[g] for g in np.asarray(gold).ravel().tolist()]
        for scorer, S in (("sym", S_sym[:, j]), ("qscale", S_q[:, j])):
            top10 = fast_topk(S, arch_id, 10)
            top = [int(x) for x in np.asarray(top10).ravel().tolist()]
            h10, fr3, h3 = metrics_from_top(top10, gold)
            exp10 = float(audit.expected_hit(S, gold, 10))
            fout.write(json.dumps({
                "_label": LABEL, "benchmark": bench, "archive_id": arch_id,
                "qid": qid, "arm": arm, "scorer": scorer,
                "gold": [int(g) for g in np.asarray(gold).ravel().tolist()],
                "gold_ids": gold_ids,
                "top10": top, "top10_ids": [doc_ids[g] for g in top],
                "hit10": h10, "fr3": fr3, "hit3": h3, "exp_hit10": exp10,
            }) + "\n")
            store.append((bench, arch_id, qid, arm, scorer, h10, fr3, h3, exp10))


# ---------- aggregates / bootstrap / mechanism ----------
def summarize(rows, bench):
    summary, by_archive = {}, {}
    arches = sorted(set(r[1] for r in rows if r[0] == bench))
    for arm in ARM_ORDER:
        for scorer in SCORERS:
            sel = [r for r in rows if r[0] == bench and r[3] == arm and r[4] == scorer]
            A = np.array([[r[5], r[6], r[7], r[8]] for r in sel])
            summary[f"{arm}/{scorer}"] = {
                "n": int(len(sel)), "hit10_pct": float(A[:, 0].mean() * 100),
                "fr3_pct": float(A[:, 1].mean() * 100),
                "hit3_pct": float(A[:, 2].mean() * 100),
                "exp_hit10_pct": float(A[:, 3].mean() * 100)}
            by_archive[f"{arm}/{scorer}"] = {}
            for a in arches:
                s2 = [r for r in sel if r[1] == a]
                B = np.array([[r[5], r[6], r[7], r[8]] for r in s2])
                by_archive[f"{arm}/{scorer}"][a] = {
                    "n": int(len(s2)), "hit10_pct": float(B[:, 0].mean() * 100),
                    "fr3_pct": float(B[:, 1].mean() * 100),
                    "hit3_pct": float(B[:, 2].mean() * 100),
                    "exp_hit10_pct": float(B[:, 3].mean() * 100)}
    return summary, by_archive, arches


def cluster_contrasts(rows, bench, arches, arms):
    """Paired archive-clustered bootstrap, 20000 reps, seed 20260916, vs FULL."""
    order = [(r[1], r[2]) for r in rows if r[0] == bench and r[3] == "FULL"
             and r[4] == "qscale"]
    cidx = {a: i for i, a in enumerate(arches)}
    cl = np.array([cidx[a] for (a, _) in order])
    C = len(arches)
    out = {}
    for arm in arms:
        out[arm] = {}
        for scorer in SCORERS:
            d_full = {(r[1], r[2]): r for r in rows
                      if r[0] == bench and r[3] == "FULL" and r[4] == scorer}
            d_arm = {(r[1], r[2]): r for r in rows
                     if r[0] == bench and r[3] == arm and r[4] == scorer}
            assert set(d_full) == set(d_arm) and len(d_full) == len(order)
            out[arm][scorer] = {}
            for m, pos in (("hit10", 5), ("fr3", 6), ("hit3", 7), ("exp_hit10", 8)):
                diff = np.array([d_arm[k][pos] - d_full[k][pos] for k in order])
                cs = np.array([diff[cl == i].sum() for i in range(C)])
                ns = np.array([(cl == i).sum() for i in range(C)])
                rng = np.random.default_rng(BOOT_SEED)
                counts = rng.multinomial(C, [1.0 / C] * C, size=BOOT_REPS)
                boots = (counts @ cs) / (counts @ ns)
                lo, hi = np.quantile(boots, [0.025, 0.975])
                out[arm][scorer][m] = {
                    "mean_diff_pp": float(diff.mean() * 100),
                    "ci95_lo_pp": float(lo * 100), "ci95_hi_pp": float(hi * 100),
                    "excludes_zero": bool(lo > 0 or hi < 0),
                    "reps": BOOT_REPS, "seed": BOOT_SEED, "clusters": C}
    return out


WORD_RE = re.compile(r"\w+", re.UNICODE)


def toks(s):
    return WORD_RE.findall(s.lower())


def stratify_band(doc_texts, query_text, gold_rows):
    """Verbatim why_bm25_wins.py recipe: BM25-style idf from DOCUMENTS ONLY;
    shared = query cap gold doc (gold[0] when multi); bands by max shared idf."""
    import math
    dtok = [toks(t) for t in doc_texts]
    N = len(dtok)
    df = Counter()
    for dt in dtok:
        for t in set(dt):
            df[t] += 1
    idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
    gold = [int(g) for g in np.asarray(gold_rows).ravel().tolist()]
    qt = toks(query_text)
    if len(gold) == 1:
        shared = set(qt).intersection(set(dtok[gold[0]]))
    else:
        shared = set(qt).intersection(set(dtok[gold[0]]))
    mx = max([idf[t] for t in shared if t in idf], default=0.0)
    band = ("no_shared" if not shared else "common" if mx < 2.0
            else "mid" if mx < 4.0 else "rare")
    return band, float(mx)


def mechanism_table(rows, bench, band_of, arms):
    """Hit@10 by rarity band for given arms (both scorers). band_of: (arch,qid)->band."""
    tab = {}
    for arm in arms:
        tab[arm] = {}
        for scorer in SCORERS:
            sel = [r for r in rows if r[0] == bench and r[3] == arm and r[4] == scorer]
            by_band = defaultdict(list)
            for r in sel:
                by_band[band_of[(r[1], r[2])]].append(r[5])
            tab[arm][scorer] = {
                b: {"n": int(len(v)), "hit10_pct": float(np.mean(v) * 100) if v else 0.0}
                for b, v in by_band.items()}
    return tab


def main():
    t_all = time.perf_counter()
    print("[load] realtalk + perltqa", flush=True)
    raw_rt, cached_rt = load_realtalk()
    qa, mem, ORD, arch_pq, QDAT, chars = load_perltqa()
    n_rt = sum(len(raw_rt[a]["queries"]) for a in RT_ARCHIVES)
    print(f"[load] RT queries={n_rt} PerLTQA queries={len(QDAT)}", flush=True)
    assert n_rt == 705 and len(QDAT) == 8265

    nv = verify_topk([a for a in RT_ARCHIVES] + chars[:3],
                     [len(raw_rt[a]["texts"]) for a in RT_ARCHIVES] +
                     [arch_pq[c]["N"] for c in chars[:3]])
    print(f"[check] fast_topk verified on {nv} samples", flush=True)

    # ================= FIDELITY GATE =================
    print("[gate] rebuilding FULL RealTalk...", flush=True)
    rt_full, g_rt = gate_realtalk(raw_rt, cached_rt)
    print("[gate] rebuilding FULL PerLTQA...", flush=True)
    pq_full, QTEXT, g_pq = gate_perltqa(qa, mem, ORD, arch_pq, QDAT, chars)

    def g2pass(g, tgt, rnd4=("hit10_pct", "exp_hit10_pct"), rnd2=("fr3_pct",)):
        ok = True
        det = {}
        q, s = g["qscale"], g["sym"]
        checks = [
            (round(q["hit10_pct"], 4), tgt["qscale_hit10"], "qscale_hit10"),
            (round(s["hit10_pct"], 4), tgt["sym_det_hit10"], "sym_det_hit10"),
            (round(s["exp_hit10_pct"], 4), tgt["sym_exp_hit10"], "sym_exp_hit10"),
            (round(q["fr3_pct"], 2), tgt["qscale_fr3"], "qscale_fr3"),
        ]
        for obs, exp, name in checks:
            good = (obs == exp)
            det[name] = {"observed": obs, "target": exp, "pass": bool(good)}
            ok = ok and good
        return ok, det

    rt_g1 = bool(g_rt["diff_bits"] == 0 and g_rt["qc_diff"] == 0)
    pq_g1 = bool(g_pq["diff_bits"] == 0 and g_pq["qc_diff"] == 0)
    rt_g2_ok, rt_g2_det = g2pass(g_rt["g2"], G2_RT)
    pq_g2_ok, pq_g2_det = g2pass(g_pq["g2"], G2_PQ)
    gate = {
        "_label": LABEL,
        "stage": "FIDELITY_GATE",
        "note": "Written BEFORE any new-arm number. Gate must pass to proceed.",
        "seeds": {"LSA32_random_state": LSA_SEED, "SVD96_random_state": SVD_SEED},
        "realtalk": {
            "n": 705, "G1_diff_bits": g_rt["diff_bits"], "G1_total": g_rt["total"],
            "G1_maxabs": g_rt["maxabs"], "G1_qc_diff": g_rt["qc_diff"],
            "G1_pass": rt_g1, "G2": g_rt["g2"], "G2_detail": rt_g2_det,
            "G2_pass": rt_g2_ok, "per_archive": g_rt["per_arch"],
            "rebuild_s": g_rt["build_s"]},
        "perltqa": {
            "n": 8265, "G1_diff_bits": g_pq["diff_bits"], "G1_total": g_pq["total"],
            "G1_maxabs": g_pq["maxabs"], "G1_qc_diff": g_pq["qc_diff"],
            "G1_pass": pq_g1, "G2": g_pq["g2"], "G2_detail": pq_g2_det,
            "G2_pass": pq_g2_ok, "per_archive": g_pq["per_arch"],
            "rebuild_s": g_pq["build_s"]},
        "gate_pass": bool(rt_g1 and pq_g1 and rt_g2_ok and pq_g2_ok),
    }
    with open(os.path.join(HERE, "FIDELITY_GATE.json"), "w") as f:
        json.dump(gate, f, indent=2)
    print(f"[gate] RT G1 diff={g_rt['diff_bits']}/{g_rt['total']} "
          f"maxabs={g_rt['maxabs']:.3e} qc_diff={g_rt['qc_diff']} pass={rt_g1}", flush=True)
    print(f"[gate] RT G2 {json.dumps(g_rt['g2'])} pass={rt_g2_ok}", flush=True)
    print(f"[gate] PQ G1 diff={g_pq['diff_bits']}/{g_pq['total']} "
          f"maxabs={g_pq['maxabs']:.3e} qc_diff={g_pq['qc_diff']} pass={pq_g1}", flush=True)
    print(f"[gate] PQ G2 {json.dumps(g_pq['g2'])} pass={pq_g2_ok}", flush=True)
    if not gate["gate_pass"]:
        print("[gate] FAIL -> STOP. No new arms will be reported.", flush=True)
        sys.exit(1)
    print("[gate] PASS -> running arms.", flush=True)

    # ================= ARMS =================
    fout = open(os.path.join(HERE, "per_query.jsonl"), "w")
    store = []  # (bench, arch, qid, arm, scorer, h10, fr3, h3, exp)
    cost = {}
    selfchecks = {}
    zwidth = {}
    # ---- RealTalk ----
    for a in RT_ARCHIVES:
        tA = time.perf_counter()
        R = rt_full[a]
        Xl, Xw, Xc = R["Xl"], R["Xw"], R["Xc"]
        qs = [q["text"] for q in raw_rt[a]["queries"]]
        Qw, Qc, Ql = query_blocks(R["wv"], R["cv"], R["sv"], qs)
        arms, checks, zw = build_all_arms(Xl, Xw, Xc, Ql, Qw, Qc, R["wv"].idf_)
        selfchecks[f"RealTalk/{a}"] = checks
        zwidth[a] = zw
        assert all(v["pass"] for v in checks.values()), f"{a} self-check FAIL {checks}"
        qids = [q["qid"] for q in raw_rt[a]["queries"]]
        golds = [q["gold"] for q in raw_rt[a]["queries"]]
        for arm in ARM_ORDER:
            C, QC, bs = arms[arm]
            cost.setdefault(arm, {})[a] = bs
            score_and_emit("RealTalk", a, C, QC, qids, golds, raw_rt[a]["doc_ids"],
                           arm, fout, store)
        fout.flush()
        print(f"[RT] {a} done {time.perf_counter()-tA:.1f}s", flush=True)
    # ---- PerLTQA ----
    for ci, char in enumerate(chars):
        tA = time.perf_counter()
        R = pq_full[char]
        Xl, Xw, Xc = R["Xl"], R["Xw"], R["Xc"]
        questions = [QTEXT[q] for q in R["qids"]]
        Qw, Qc, Ql = query_blocks(R["wv"], R["cv"], R["svd"], questions)
        arms, checks, zw = build_all_arms(Xl, Xw, Xc, Ql, Qw, Qc, R["wv"].idf_)
        selfchecks[f"PerLTQA/{char}"] = checks
        zwidth[char] = zw
        assert all(v["pass"] for v in checks.values()), f"{char} self-check FAIL"
        golds = [np.asarray(QDAT[q]["gold"]).ravel() for q in R["qids"]]
        mids = [mid for mid, _ in R["items"]]
        for arm in ARM_ORDER:
            C, QC, bs = arms[arm]
            cost.setdefault(arm, {})[char] = bs
            score_and_emit("PerLTQA", char, C, QC, R["qids"], golds, mids,
                           arm, fout, store)
        fout.flush()
        print(f"[PQ] [{ci+1}/30] {char} {time.perf_counter()-tA:.1f}s", flush=True)
    fout.close()

    # ================= AGGREGATES =================
    results = {"_label": LABEL,
               "note": "Per-benchmark only. Never averaged across benchmarks. "
                       "CIs are paired archive-clustered bootstrap, 20000 reps, seed 20260916.",
               "seeds": {"LSA32": LSA_SEED, "SVD96": SVD_SEED, "bootstrap": BOOT_SEED,
                         "bootstrap_reps": BOOT_REPS},
               "payload_bytes_per_doc": 12, "svd_dim": 96,
               "benchmarks": {}}
    mech_arms = {}
    for bench, arches in (("RealTalk", RT_ARCHIVES), ("PerLTQA", chars)):
        summary, by_archive, arches_out = summarize(store, bench)
        contrasts = cluster_contrasts(store, bench, arches_out, NONCTRL)
        # best/worst non-control arm by qscale Hit@10 delta vs FULL
        dq = {arm: contrasts[arm]["qscale"]["hit10"]["mean_diff_pp"] for arm in NONCTRL}
        best = max(dq, key=dq.get)
        worst = min(dq, key=dq.get)
        mech_arms[bench] = (best, worst)
        # rarity bands (verbatim why_bm25 recipe; docs-only idf)
        band_of = {}
        if bench == "RealTalk":
            for a in RT_ARCHIVES:
                for q in raw_rt[a]["queries"]:
                    b, _ = stratify_band(raw_rt[a]["texts"], q["text"], q["gold"])
                    band_of[(a, q["qid"])] = b
        else:
            for char in chars:
                texts = [t for _, t in pq_full[char]["items"]]
                for qid in pq_full[char]["qids"]:
                    b, _ = stratify_band(texts, QTEXT[qid], QDAT[qid]["gold"])
                    band_of[(char, qid)] = b
        mech = mechanism_table(store, bench, band_of, ["FULL", best, worst])
        band_n = dict(Counter(band_of.values()))
        results["benchmarks"][bench] = {
            "n": int(sum(1 for r in store if r[0] == bench and r[3] == "FULL"
                         and r[4] == "qscale")),
            "n_clusters": len(arches_out),
            "summary": summary, "by_archive": by_archive,
            "contrasts_vs_FULL_pp": contrasts,
            "qscale_hit10_delta_pp": dq, "best_arm": best, "worst_arm": worst,
            "mechanism": {"bands": mech, "band_n": band_n,
                          "recipe": "why_bm25_wins.py verbatim: BM25-style idf from "
                                    "DOCUMENTS ONLY; shared = query cap gold doc "
                                    "(gold[0] when multi); bands no_shared / common "
                                    "idf<2 / mid 2-4 / rare >=4; Hit@10 per band."},
        }
    results["cost"] = {
        arm: {"build_s_per_archive": {k: round(v, 3) for k, v in d.items()},
              "build_s_total": float(sum(d.values()))} for arm, d in cost.items()}
    results["z_features_per_archive"] = zwidth
    results["selfchecks_p0_m0_vs_FULL"] = {
        "all_pass": bool(all(v["pass"] for d in selfchecks.values() for v in d.values())),
        "n_archives": len(selfchecks)}
    results["total_wall_s"] = float(time.perf_counter() - t_all)
    with open(os.path.join(HERE, "RESULTS.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("=== SUMMARY (pct) ===", flush=True)
    for bench in ("RealTalk", "PerLTQA"):
        print(f"--- {bench} ---", flush=True)
        for arm in ARM_ORDER:
            for scorer in SCORERS:
                s = results["benchmarks"][bench]["summary"][f"{arm}/{scorer}"]
                print(f"{arm:9s} {scorer:6s} Hit@10={s['hit10_pct']:.4f} "
                      f"FR@3={s['fr3_pct']:.4f} Hit@3={s['hit3_pct']:.4f} "
                      f"expHit@10={s['exp_hit10_pct']:.4f} n={s['n']}", flush=True)
        b, w = mech_arms[bench]
        print(f"best={b} worst={w}", flush=True)
        for k, v in results["benchmarks"][bench]["contrasts_vs_FULL_pp"].items():
            print(f"{k}: " + "; ".join(
                f"{m}:{v['qscale'][m]['mean_diff_pp']:+.2f}"
                f"[{v['qscale'][m]['ci95_lo_pp']:+.2f},{v['qscale'][m]['ci95_hi_pp']:+.2f}]"
                for m in ["hit10", "fr3"]), flush=True)
    print("[done]", flush=True)


if __name__ == "__main__":
    main()



