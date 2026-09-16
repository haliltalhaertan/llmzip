"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

math_r1/quant: sign-quantization pilot. Keeps the production 96-dim representation
EXACTLY as is; changes only the SIGN QUANTIZATION. Payload stays 96 bits / 12 B/doc.

Arms (x scorers sym/qscale, x benchmarks RealTalk/PerLTQA, never averaged):
  FULL            production control: bits = (C >= 0)
  ITQ_C           family C: orthogonal R (96x96) via 50 alternating-minimization
                  iterations from random-orthogonal init (seed 20260916);
                  bits = sign(C R); query rotated the same way (QC R).
                  Fit on DOCUMENTS ONLY, per archive.
  RAND_20260916 / RAND_20260917 / RAND_20260918
                  family D (mandatory control): same pipeline, R fixed random
                  orthogonal (no optimization). RAND_20260916 uses the same
                  generator+seed as the ITQ init, so ITQ starts exactly there.
  MED             family E: bit = 1 iff C_ij >= median_j(DOCUMENTS col j);
                  query sym-bits use the same thresholds; qscale query side
                  stays continuous QC/sigma (documented choice).

Shared definitions (exact): det top-K = score DESC, then ascending
SHA256("top10-r1|"+archive_id+"|"+row), then row. Hit@10, FR@3, Hit@3,
expected-Hit@10 under uniform ties. Paired archive-clustered bootstrap,
20000 reps, seed 20260916, for every contrast. sigma = per-archive std of
DOCUMENT C columns of THAT ARM (rotated C for C/D arms), ddof=0, floor 1e-12.

Usage: $HOME/muse-work/ml-python quant_math.py
Writes (this directory only): FIDELITY_GATE.json, per_query.jsonl, RESULTS.json.
Gate fails -> exit 1 before any new arm.
"""

import hashlib
import importlib.util
import json
import math
import os
import pickle
import re
import sys
import time
from collections import Counter

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"

HERE = os.path.dirname(os.path.abspath(__file__))
R = "/mnt/c/Users/MDP/dev/llmzip-work"
RT_DATA = R + "/top10_comparison_r1/data"
RT_CACHE = R + "/bench3/runs/b3a_realtalk/rt_repr"
FROZEN = R + "/drive/v52_t4d_locomo_frozen_cross_benchmark.py"
AUDIT_LIB = R + "/top10_comparison_r1/audit/audit_baseline_lib.py"
PQ_BASE = R + "/bench3/PerLTQA/Dataset/en_v2"
PQ_ARCH = R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PQ_Q = R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl"

RT_ARCHIVES = [f"RT{i:02d}" for i in range(1, 11)]
ARMS = ["FULL", "ITQ_C", "RAND_20260916", "RAND_20260917", "RAND_20260918", "MED"]
NEW_ARMS = [a for a in ARMS if a != "FULL"]
RAND_SEEDS = [20260916, 20260917, 20260918]
SCORERS = ["sym", "qscale"]
METRICS = ["hit10", "fr3", "hit3", "exp_hit10"]
BOOT_REPS = 20000
BOOT_SEED = 20260916
ITQ_ITERS = 50
ITQ_SEED = 20260916

# G2 references (coordinator-verified production numbers).
RT_REF = {"qscale_hit10": 49.6454, "qscale_fr3": 22.41,
          "sym_det_hit10": 46.5248, "sym_exp_hit10": 46.6809}
PQ_REF = {"qscale_hit10": 80.0000, "qscale_fr3": 53.24,
          "sym_det_hit10": 75.6806, "sym_exp_hit10": 75.7612}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


frozen = load_module("frozen_builder_ro", FROZEN)
audit = load_module("audit_baseline_lib_ro", AUDIT_LIB)
assert frozen.SVD_SEED == 5204, "wrong SVD seed in frozen builder"

# ---------- fast deterministic top-K, verified equivalent to audit.det_top10 ----
_tie_cache = {}


def fast_topk(scores, archive_id, k):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    key = (archive_id, len(s))
    tb = _tie_cache.get(key)
    if tb is None:
        hs = [hashlib.sha256(f"top10-r1|{archive_id}|{r}".encode()).hexdigest()
              for r in range(len(s))]
        tb = np.array(sorted(range(len(s)), key=lambda r: (hs[r], r)))
        _tie_cache[key] = tb
    return tb[np.argsort(-m[tb], kind="stable")][:k]


def verify_topk(chars_or_archives, sizes, n_checks=30):
    rng = np.random.default_rng(0)
    n = 0
    for a, N in zip(chars_or_archives, sizes):
        for _ in range(5):
            s = rng.normal(size=N)
            s[rng.random(N) < 0.3] = s[0]
            for k in (3, 10):
                x = np.asarray(audit.det_top10(s, a, k)).tolist()
                y = np.asarray(fast_topk(s, a, k)).tolist()
                assert x == y, f"fast_topk mismatch {a} k={k}"
                n += 1
    print(f"[topk] verified equivalent on {n} samples", flush=True)


def query_metrics(scores, gold, archive_id):
    top10 = fast_topk(scores, archive_id, 10)
    hit10, _, _ = audit.hrn(top10, gold, 10)
    top3 = fast_topk(scores, archive_id, 3)
    hit3, fr3, _ = audit.hrn(top3, gold, 3)
    exp10 = audit.expected_hit(np.asarray(scores, dtype=np.float64), gold, 10)
    return {"hit10": float(hit10), "fr3": float(fr3), "hit3": float(hit3),
            "exp_hit10": float(exp10),
            "top10": [int(x) for x in np.asarray(top10).ravel().tolist()]}


# ---------- rotation machinery (families C and D) ----------
def random_orthogonal(d, seed):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((d, d))
    U, _, Vt = np.linalg.svd(A, full_matrices=False)
    return (U @ Vt).astype(np.float64)


def fit_itq(C, n_iter=ITQ_ITERS, seed=ITQ_SEED):
    """Gong-Lazebnik-style alternating minimization of ||B - C R||_F^2.

    B <- sign(CR) (production convention >= 0 -> +1); R <- U V^T from the
    SVD of C^T B. Documents only. Returns (R, fit_seconds, loss_init, loss_final).
    """
    t0 = time.perf_counter()
    C = np.asarray(C, dtype=np.float64)
    R = random_orthogonal(C.shape[1], seed)
    B = np.where(C @ R >= 0, 1.0, -1.0)
    loss_init = float(np.sum((B - C @ R) ** 2))
    for _ in range(n_iter):
        B = np.where(C @ R >= 0, 1.0, -1.0)
        M = C.T @ B
        U, _, Vt = np.linalg.svd(M, full_matrices=False)
        R = U @ Vt
    B = np.where(C @ R >= 0, 1.0, -1.0)
    loss_final = float(np.sum((B - C @ R) ** 2))
    return R.astype(np.float64), time.perf_counter() - t0, loss_init, loss_final


def sigma_docs(C):
    return np.maximum(np.std(np.asarray(C, dtype=np.float64), axis=0, ddof=0), 1e-12)


def sym_scores_from_bits(Db, qb):
    return -np.count_nonzero(np.asarray(Db, dtype=bool) != np.asarray(qb, dtype=bool)[None, :],
                             axis=1).astype(np.float64)


def qscale_scores_from_bits(Dpm, qc, sig):
    return np.asarray(Dpm, dtype=np.float64) @ (np.asarray(qc, dtype=np.float64).ravel() / sig)


# ---------- rarity stratification (coordinator recipe, documents-only) ----------
WORD = re.compile(r"\w+", re.UNICODE)


def toks(s):
    return WORD.findall(s.lower())


def idf_bands(doc_texts, queries):
    """queries: list of (qkey, qtext, gold_rows). Returns {qkey: (band, max_idf)}.

    IDF (BM25-style log((N-c+0.5)/(c+0.5)+1)) fitted on DOCUMENTS ONLY.
    shared/mx/band rule verbatim from coordinator/why_bm25_wins.py.
    """
    dtok = [toks(t) for t in doc_texts]
    N = len(dtok)
    df = Counter()
    for dt in dtok:
        for t in set(dt):
            df[t] += 1
    idf = {t: math.log((N - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
    out = {}
    for qkey, qtext, gold in queries:
        gold = [int(g) for g in gold]
        qt = toks(qtext)
        if len(gold) == 0:
            out[qkey] = ("no_shared", 0.0)
            continue
        if len(gold) == 1:
            shared = set(qt).intersection(*[set(dtok[g]) for g in gold])
        else:
            shared = set(qt).intersection(set(dtok[gold[0]]))
        mx = max([idf[t] for t in shared if t in idf], default=0.0)
        band = ("no_shared" if not shared else
                "common" if mx < 2.0 else
                "mid" if mx < 4.0 else "rare")
        out[qkey] = (band, float(mx))
    return out


# ================= REALTALK =================
def rt_load_raw():
    raw = {}
    for a in RT_ARCHIVES:
        with open(os.path.join(RT_DATA, a + ".json")) as f:
            d = json.load(f)
        docs = sorted(d["docs"], key=lambda r: r["row"])
        assert [r["row"] for r in docs] == list(range(len(docs)))
        raw[a] = {
            "texts": [r["text"] for r in docs],
            "queries": [{"qid": q["qid"], "text": q["text"],
                         "gold": [int(g) for g in q["gold"]]} for q in d["queries"]],
        }
    return raw


def rt_build_full(texts, questions):
    """FULL C/QC via the frozen builder path (verbatim recipe)."""
    t0 = time.perf_counter()
    payload = frozen.fit_input_payload(list(texts))
    wv, cv, sv, Xw, Xc, Xl = frozen.fit_archive_representation(payload)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    assert min(Z.shape) > 96
    s96 = TruncatedSVD(n_components=96, random_state=frozen.SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(s96.transform(Zq))
    QC = (QY - mu).astype(np.float64)
    return C, QC, time.perf_counter() - t0


def rt_fidelity(raw):
    """G1: sign(C), sign(QC by qid) vs cache. G2: rebuilt FULL metrics vs refs."""
    cached = {}
    for a in RT_ARCHIVES:
        with open(os.path.join(RT_CACHE, a + ".pkl"), "rb") as f:
            cached[a] = pickle.load(f)
    rebuilt, per_arch = {}, {}
    g1_bits = g1_tot = g1_qc = 0
    g1_maxabs = 0.0
    for a in RT_ARCHIVES:
        C, QC, _ = rt_build_full(raw[a]["texts"], [q["text"] for q in raw[a]["queries"]])
        rebuilt[a] = (C, QC)
        Cc = np.asarray(cached[a]["C"], dtype=np.float64)
        assert Cc.shape == C.shape, f"{a} C shape {C.shape} vs {Cc.shape}"
        g1_bits += int(np.count_nonzero((C >= 0) != (Cc >= 0)))
        g1_tot += int(C.size)
        g1_maxabs = max(g1_maxabs, float(np.max(np.abs(C - Cc))))
        QCc = np.asarray(cached[a]["QC"], dtype=np.float64)
        pos = {q: i for i, q in enumerate(cached[a]["qids"])}
        qi = [pos[q["qid"]] for q in raw[a]["queries"]]
        assert len(set(qi)) == len(qi)
        assert all(cached[a]["questions"][i] == q["text"]
                   for i, q in zip(qi, raw[a]["queries"]))
        assert all(sorted(map(int, cached[a]["gold_rows"][i])) == sorted(q["gold"])
                   for i, q in zip(qi, raw[a]["queries"]))
        d = int(np.count_nonzero(np.sign(QC) != np.sign(QCc[np.array(qi)])))
        g1_qc += d
        per_arch[a] = {"C_shape": list(C.shape), "QC_shape": list(QC.shape),
                       "qc_sign_diff": d, "qc_rows_cached": int(QCc.shape[0]),
                       "qc_rows_compared": int(len(qi))}
    # G2 from rebuilt; plus cache-direct crosscheck (must agree: guards alignment)
    def agg_of(getCQ):
        h = {s: [] for s in SCORERS}
        f = {s: [] for s in SCORERS}
        h3 = {s: [] for s in SCORERS}
        ex = {s: [] for s in SCORERS}
        for a in RT_ARCHIVES:
            C, QC = getCQ(a)
            sig = sigma_docs(C)
            Db = (C >= 0)
            Dpm = np.where(Db, 1.0, -1.0)
            for j, q in enumerate(raw[a]["queries"]):
                s_sym = sym_scores_from_bits(Db, QC[j] >= 0)
                s_q = qscale_scores_from_bits(Dpm, QC[j], sig)
                for s, sc in (("sym", s_sym), ("qscale", s_q)):
                    m = query_metrics(sc, q["gold"], a)
                    h[s].append(m["hit10"])
                    f[s].append(m["fr3"])
                    h3[s].append(m["hit3"])
                    ex[s].append(m["exp_hit10"])
        return {s: {"hit10_pct": float(np.mean(h[s]) * 100),
                    "fr3_pct": float(np.mean(f[s]) * 100),
                    "hit3_pct": float(np.mean(h3[s]) * 100),
                    "exp_hit10_pct": float(np.mean(ex[s]) * 100),
                    "n": int(len(h[s]))} for s in SCORERS}

    g2_rebuilt = agg_of(lambda a: rebuilt[a])

    def cachedCQ(a):
        Cc = np.asarray(cached[a]["C"], dtype=np.float64)
        QCc = np.asarray(cached[a]["QC"], dtype=np.float64)
        pos = {q: i for i, q in enumerate(cached[a]["qids"])}
        return Cc, QCc[np.array([pos[q["qid"]] for q in raw[a]["queries"]])]

    g2_cached = agg_of(cachedCQ)
    g2 = g2_rebuilt
    g1_pass = bool(g1_bits == 0 and g1_qc == 0)
    g2_pass = bool(round(g2["qscale"]["hit10_pct"], 4) == RT_REF["qscale_hit10"]
                   and round(g2["qscale"]["fr3_pct"], 2) == RT_REF["qscale_fr3"]
                   and round(g2["sym"]["hit10_pct"], 4) == RT_REF["sym_det_hit10"]
                   and round(g2["sym"]["exp_hit10_pct"], 4) == RT_REF["sym_exp_hit10"])
    return {"rebuilt": rebuilt, "g2_rebuilt": g2_rebuilt, "g2_cached_direct": g2_cached,
            "gate": {
                "_label": LABEL,
                "G1_differing_ge0_bits": int(g1_bits), "G1_total_bits": int(g1_tot),
                "G1_differing_qc_signs": int(g1_qc), "G1_max_abs_C_diff": float(g1_maxabs),
                "G1_pass": g1_pass, "per_archive": per_arch,
                "G2_rebuilt": g2_rebuilt, "G2_cached_direct": g2_cached,
                "G2_reference": RT_REF, "G2_pass": g2_pass,
                "n_queries": int(sum(len(raw[a]["queries"]) for a in RT_ARCHIVES))}}


# ================= PERLTQA =================
def pq_parse_social(v):
    import ast
    return v if isinstance(v, dict) else ast.literal_eval(v)


def pq_load():
    import ast  # noqa: F401 (kept local to mirror frozen recipe file)
    qa = json.load(open(PQ_BASE + "/perltqa_en_v2.json"))
    mem = json.load(open(PQ_BASE + "/perltmem_en_v2.json"))
    qachars = [list(e.keys())[0] for e in qa]
    banked = sorted([c for c in qachars if c in mem])
    ORD = {c: i for i, c in enumerate(banked)}
    arch = pickle.load(open(PQ_ARCH, "rb"))
    QDAT = pickle.load(open(PQ_Q, "rb"))
    return qa, mem, ORD, arch, QDAT


def pq_build_items(char, mem, ORD):
    b = mem[char]

    def parse_social(v):
        import ast
        return v if isinstance(v, dict) else ast.literal_eval(v)

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
        content = ev["content"] if isinstance(ev, dict) and "content" in ev \
            else (ev if isinstance(ev, str) else json.dumps(ev))
        items.append((f"PQ{ORD[char]:03d}_EVE_{i:03d}", f"[event {k}] {content}"))
    t = 0
    for k in sorted(b["dialogues"].keys()):
        for ts in sorted(b["dialogues"][k]["contents"].keys()):
            for turn in b["dialogues"][k]["contents"][ts]:
                items.append((f"PQ{ORD[char]:03d}_DLG_{t:03d}",
                              f"[dialogue {k} @ {ts}] {turn}"))
                t += 1
    return items


def pq_fit_archive(texts):
    """Verbatim frozen recipe (step2_build.fit_archive): LSA32 seed 5101, SVD96 5204."""
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                         sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s96 = TruncatedSVD(n_components=96, random_state=5204)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    return C


def pq_fidelity(mem, ORD, arch, QDAT):
    """G1: rebuilt sign(C) vs cache, all 30 archives. G2: cached-code metric replay."""
    chars = sorted(arch.keys())
    assert len(chars) == 30
    tot = diff = 0
    maxabs = 0.0
    per_arch = {}
    rebuilt = {}
    for char in chars:
        texts = [t for _, t in pq_build_items(char, mem, ORD)]
        C = pq_fit_archive(texts)
        rebuilt[char] = C
        Cc = np.asarray(arch[char]["C"], dtype=np.float64)
        assert C.shape == Cc.shape, f"{char} shape {C.shape} vs {Cc.shape}"
        assert len(texts) == arch[char]["N"]
        d = int(np.count_nonzero((C >= 0) != (Cc >= 0)))
        mad = float(np.max(np.abs(C - Cc)))
        tot += int(C.size)
        diff += d
        maxabs = max(maxabs, mad)
        per_arch[char] = {"N": int(len(texts)), "differing_bits": d,
                          "n_bits": int(C.size), "max_abs_diff": mad}
        print(f"[gate/pq] {char}: N={len(texts)} diffbits={d}/{C.size} maxabs={mad:.3e}",
              flush=True)
    # G2: replay production metrics from CACHED codes (frozen recipe, shared scorers)
    sig = {c: sigma_docs(np.asarray(arch[c]["C"], dtype=np.float64)) for c in chars}
    acc = {s: {"h10": [], "fr3": [], "h3": [], "ex": []} for s in SCORERS}
    for qid, q in QDAT.items():
        char = q["char"]
        C = np.asarray(arch[char]["C"], dtype=np.float64)
        qC = np.asarray(q["qC"], dtype=np.float64)
        gold = np.asarray(q["gold"]).ravel()
        Db = (C >= 0)
        Dpm = np.where(Db, 1.0, -1.0)
        for s, sc in (("sym", sym_scores_from_bits(Db, qC >= 0)),
                      ("qscale", qscale_scores_from_bits(Dpm, qC, sig[char]))):
            m = query_metrics(sc, gold, char)
            acc[s]["h10"].append(m["hit10"])
            acc[s]["fr3"].append(m["fr3"])
            acc[s]["h3"].append(m["hit3"])
            acc[s]["ex"].append(m["exp_hit10"])
    g2 = {s: {"hit10_pct": float(np.mean(acc[s]["h10"]) * 100),
              "fr3_pct": float(np.mean(acc[s]["fr3"]) * 100),
              "hit3_pct": float(np.mean(acc[s]["h3"]) * 100),
              "exp_hit10_pct": float(np.mean(acc[s]["ex"]) * 100),
              "n": int(len(acc[s]["h10"]))} for s in SCORERS}
    g1_pass = bool(diff == 0)
    g2_pass = bool(round(g2["qscale"]["hit10_pct"], 4) == PQ_REF["qscale_hit10"]
                   and round(g2["qscale"]["fr3_pct"], 2) == PQ_REF["qscale_fr3"]
                   and round(g2["sym"]["hit10_pct"], 4) == PQ_REF["sym_det_hit10"]
                   and round(g2["sym"]["exp_hit10_pct"], 4) == PQ_REF["sym_exp_hit10"])
    return {"rebuilt": rebuilt, "g2": g2,
            "gate": {"_label": LABEL,
                     "G1_differing_bits": int(diff), "G1_total_bits": int(tot),
                     "G1_max_abs_diff": float(maxabs), "G1_pass": g1_pass,
                     "per_archive": per_arch, "G2_cached_replay": g2,
                     "G2_reference": PQ_REF, "G2_pass": g2_pass,
                     "n_queries": int(len(QDAT))}}


# ================= ARMS =================
def apply_arms(C, QC):
    """Transform production (C, QC) into each arm's coding. Documents only for fits.

    Returns {arm: {Db, Dpm, Qc, thr, sig, fit_s, qrot_s, extra}} where Db is the
    (N,96) bool doc-code matrix, Qc the (Q,96) continuous query matrix in the
    arm's frame, thr the per-column query/doc threshold for sym bits, and sig
    the DOCUMENTS-ONLY per-column std of the arm's doc frame.
    """
    C = np.asarray(C, dtype=np.float64)
    QC = np.asarray(QC, dtype=np.float64)
    zero_frac = float(np.mean(C == 0.0))
    arms = {}
    arms["FULL"] = {"Db": (C >= 0), "Dpm": np.where(C >= 0, 1.0, -1.0),
                    "Qc": QC, "thr": np.zeros(96), "sig": sigma_docs(C),
                    "fit_s": 0.0, "qrot_s": 0.0, "extra": {}}
    # family C: ITQ
    R, fit_s, l0, l1 = fit_itq(C)
    t0 = time.perf_counter()
    QCr = QC @ R
    qrot_s = time.perf_counter() - t0
    Cr = C @ R
    arms["ITQ_C"] = {"Db": (Cr >= 0), "Dpm": np.where(Cr >= 0, 1.0, -1.0),
                     "Qc": QCr, "thr": np.zeros(96), "sig": sigma_docs(Cr),
                     "fit_s": fit_s, "qrot_s": qrot_s,
                     "extra": {"loss_init": l0, "loss_final": l1,
                               "orth_err": float(np.max(np.abs(R.T @ R - np.eye(96)))),
                               "iters": ITQ_ITERS, "seed": ITQ_SEED}}
    # family D: random-rotation controls
    for s in RAND_SEEDS:
        t0 = time.perf_counter()
        Rr = random_orthogonal(96, s)
        gen_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        QCr2 = QC @ Rr
        qrot_s2 = time.perf_counter() - t0
        Cr2 = C @ Rr
        arms[f"RAND_{s}"] = {"Db": (Cr2 >= 0), "Dpm": np.where(Cr2 >= 0, 1.0, -1.0),
                             "Qc": QCr2, "thr": np.zeros(96), "sig": sigma_docs(Cr2),
                             "fit_s": gen_s, "qrot_s": qrot_s2,
                             "extra": {"orth_err": float(np.max(np.abs(Rr.T @ Rr - np.eye(96)))),
                                       "seed": s}}
    # family E: median thresholds (documents only)
    t0 = time.perf_counter()
    med = np.median(C, axis=0)
    fit_s = time.perf_counter() - t0
    Dbm = (C >= med[None, :])
    arms["MED"] = {"Db": Dbm, "Dpm": np.where(Dbm, 1.0, -1.0),
                   "Qc": QC, "thr": med, "sig": sigma_docs(C),
                   "fit_s": fit_s, "qrot_s": 0.0,
                   "extra": {"median_abs_max": float(np.max(np.abs(med)))}}
    for a in arms:
        assert arms[a]["Db"].shape[1] == 96 and arms[a]["Dpm"].shape[1] == 96
        packed = np.packbits(arms[a]["Db"], axis=-1, bitorder="big")
        assert packed.shape == (C.shape[0], 12), f"{a} payload {packed.shape} != 12B/doc"
    return arms, zero_frac


def bit_balance(Db):
    f = np.asarray(Db, dtype=bool).mean(axis=0)
    return {"mean_frac1": float(f.mean()), "min_frac1": float(f.min()),
            "max_frac1": float(f.max())}


def cluster_contrast(diffs, clusters, ordered_clusters, rng, reps=BOOT_REPS):
    """Paired archive-clustered bootstrap of mean(diffs).

    Per-cluster sums; weights ~ Multinomial(K, 1/K). Single-rng-stream draws.
    """
    diffs = np.asarray(diffs, dtype=np.float64)
    K = len(ordered_clusters)
    cs = np.array([diffs[np.array([c == cl for c in clusters])].sum()
                   for cl in ordered_clusters])
    ns = np.array([sum(1 for c in clusters if c == cl) for cl in ordered_clusters],
                  dtype=np.float64)
    counts = rng.multinomial(K, [1.0 / K] * K, size=reps).astype(np.float64)
    boots = (counts @ cs) / (counts @ ns)
    return {"mean_diff_pp": float(diffs.mean() * 100.0),
            "ci95_lo_pp": float(np.percentile(boots, 2.5) * 100.0),
            "ci95_hi_pp": float(np.percentile(boots, 97.5) * 100.0),
            "excludes_zero": bool(np.percentile(boots, 2.5) > 0 or np.percentile(boots, 97.5) < 0),
            "reps": reps, "seed": BOOT_SEED, "clusters": K}


def pq_collect_questions(qa, mem, ORD, arch, QDAT):
    SEC = {"profile": "PRF", "social_relationship": "SOC", "events": "EVE",
           "dialogues": "DLG"}
    out = {}
    for entry in qa:
        for char, d in entry.items():
            if char not in mem or char not in arch:
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
    assert set(QDAT) <= set(out), "missing question texts"
    return out


# ================= MAIN =================
def score_archive(archive_id, C, QC, qkeys, golds, fout, bench, store,
                  meta, strat_queries=None):
    """Apply all arms, score all queries x scorers, stream per_query rows.

    store[(arm, scorer)][(archive_id, qkey)] = metrics dict. meta collects
    per-archive balance/timing/payload/zero-fraction.
    """
    tA = time.perf_counter()
    arms, zero_frac = apply_arms(C, QC)
    QC = np.asarray(QC, dtype=np.float64)
    n_docs = int(C.shape[0])
    bal, extra, timing = {}, {}, {}
    for arm, A in arms.items():
        bal[arm] = bit_balance(A["Db"])
        extra[arm] = A["extra"]
        timing[arm] = {"fit_s": float(A["fit_s"]),
                       "qrot_s": float(A["qrot_s"]),
                       "qrot_us_per_query": float(A["qrot_s"] / max(QC.shape[0], 1) * 1e6)}
    # vectorized scores per arm/scorer, then per-query metrics
    for arm, A in arms.items():
        Db, Dpm, QcA, thr, sig = A["Db"], A["Dpm"], A["Qc"], A["thr"], A["sig"]
        Qb = (QcA >= thr[None, :])
        S_sym = -np.count_nonzero(Db[None, :, :] != Qb[:, None, :], axis=2).astype(np.float64)
        S_q = Dpm @ (QcA / sig).T  # (N, Q)
        for scorer, S in (("sym", S_sym), ("qscale", S_q.T)):
            # S_sym is (Q,N) already; S_q.T is (N,Q)->(Q,N). S[j] = query j over docs.
            for j, qk in enumerate(qkeys):
                m = query_metrics(np.ascontiguousarray(S[j]), golds[j], archive_id)
                store[(arm, scorer)][(archive_id, qk)] = m
                fout.write(json.dumps({
                    "_label": LABEL, "benchmark": bench, "archive_id": archive_id,
                    "qid": qk, "arm": arm, "scorer": scorer,
                    "gold": [int(g) for g in np.asarray(golds[j]).ravel().tolist()],
                    "hit10": m["hit10"], "fr3": m["fr3"], "hit3": m["hit3"],
                    "exp_hit10": m["exp_hit10"], "top10": m["top10"]}) + "\n")
    fout.flush()
    meta[archive_id] = {"n_docs": n_docs, "n_queries": int(len(qkeys)),
                        "zero_frac_C": zero_frac, "bit_balance": bal,
                        "arm_extra": extra, "timing": timing,
                        "arch_wall_s": float(time.perf_counter() - tA)}
    print(f"[arms/{bench}] {archive_id}: N={n_docs} nq={len(qkeys)} "
          f"zero={zero_frac:.2e} wall={time.perf_counter()-tA:.1f}s", flush=True)


def summarize(bench, ordered_clusters, store):
    n = sum(1 for k in store[("FULL", "sym")] if k[0] in set(ordered_clusters))
    summary, by_archive = {}, {}
    for arm in ARMS:
        for scorer in SCORERS:
            d = store[(arm, scorer)]
            keys = sorted(d.keys())
            vals = {m: np.array([d[k][m] for k in keys]) for m in METRICS}
            s = {"n": int(len(keys)),
                 "hit10_pct": float(vals["hit10"].mean() * 100),
                 "fr3_pct": float(vals["fr3"].mean() * 100),
                 "hit3_pct": float(vals["hit3"].mean() * 100),
                 "exp_hit10_pct": float(vals["exp_hit10"].mean() * 100)}
            summary[f"{arm}/{scorer}"] = s
            by_archive[f"{arm}/{scorer}"] = {}
            for cl in ordered_clusters:
                kk = [k for k in keys if k[0] == cl]
                by_archive[f"{arm}/{scorer}"][cl] = {
                    "n": int(len(kk)),
                    "hit10_pct": float(np.mean([d[k]["hit10"] for k in kk]) * 100),
                    "fr3_pct": float(np.mean([d[k]["fr3"] for k in kk]) * 100),
                    "hit3_pct": float(np.mean([d[k]["hit3"] for k in kk]) * 100),
                    "exp_hit10_pct": float(np.mean([d[k]["exp_hit10"] for k in kk]) * 100)}
    return summary, by_archive


def run_contrasts(bench, ordered_clusters, store, rng):
    keys = sorted(store[("FULL", "sym")].keys())
    clusters = [k[0] for k in keys]
    vs_full, itq_rand = {}, {}
    pairs = [((arm, s), ("FULL", s), f"{arm}-FULL/{s}")
             for arm in NEW_ARMS for s in SCORERS]
    pairs += [((("ITQ_C", s)), ((f"RAND_{sd}", s)), f"ITQ_C-RAND_{sd}/{s}")
              for sd in RAND_SEEDS for s in SCORERS]
    for (aa, sa), (ab, sb), name in pairs:
        da, db = store[(aa, sa)], store[(ab, sb)]
        entry = {}
        for m in METRICS:
            diffs = np.array([da[k][m] - db[k][m] for k in keys])
            entry[m] = cluster_contrast(diffs, clusters, ordered_clusters, rng)
        (itq_rand if name.startswith("ITQ_C-") else vs_full)[name] = entry
    return vs_full, itq_rand


def main():
    t_all = time.perf_counter()
    print(f"[init] {LABEL}", flush=True)

    # ---- load + rebuild RealTalk ----
    print("[rt] loading raw + cache", flush=True)
    rt_raw = rt_load_raw()
    nq_rt = sum(len(rt_raw[a]["queries"]) for a in RT_ARCHIVES)
    print(f"[rt] 10 archives, {nq_rt} queries; rebuilding FULL...", flush=True)
    rt = rt_fidelity(rt_raw)
    g = rt["gate"]
    print(f"[gate/rt] G1 diffbits={g['G1_differing_ge0_bits']}/{g['G1_total_bits']} "
          f"qc={g['G1_differing_qc_signs']} maxabs={g['G1_max_abs_C_diff']:.3e} pass={g['G1_pass']}",
          flush=True)
    for s in SCORERS:
        v = g["G2_rebuilt"][s]
        print(f"[gate/rt] G2 rebuilt {s}: Hit@10={v['hit10_pct']:.4f} FR@3={v['fr3_pct']:.4f} "
              f"Hit@3={v['hit3_pct']:.4f} expHit@10={v['exp_hit10_pct']:.4f} n={v['n']}", flush=True)

    # ---- load + rebuild PerLTQA ----
    print("[pq] loading raw + caches", flush=True)
    qa, mem, ORD, arch, QDAT = pq_load()
    print("[pq] 30 archives; rebuilding FULL C...", flush=True)
    pq = pq_fidelity(mem, ORD, arch, QDAT)
    g2 = pq["gate"]
    print(f"[gate/pq] G1 diffbits={g2['G1_differing_bits']}/{g2['G1_total_bits']} "
          f"maxabs={g2['G1_max_abs_diff']:.3e} pass={g2['G1_pass']}", flush=True)
    for s in SCORERS:
        v = g2["G2_cached_replay"][s]
        print(f"[gate/pq] G2 replay {s}: Hit@10={v['hit10_pct']:.4f} FR@3={v['fr3_pct']:.4f} "
              f"Hit@3={v['hit3_pct']:.4f} expHit@10={v['exp_hit10_pct']:.4f} n={v['n']}", flush=True)

    gate_doc = {"_label": LABEL,
                "stage": "FIDELITY_GATE (written BEFORE any new arm)",
                "seeds": {"LSA32_random_state": 5101, "SVD96_random_state": 5204},
                "realtalk": rt["gate"], "perltqa": pq["gate"],
                "gate_pass": bool(rt["gate"]["G1_pass"] and rt["gate"]["G2_pass"]
                                  and pq["gate"]["G1_pass"] and pq["gate"]["G2_pass"])}
    with open(os.path.join(HERE, "FIDELITY_GATE.json"), "w") as f:
        json.dump(gate_doc, f, indent=2)
    print(f"[gate] OVERALL pass={gate_doc['gate_pass']} -> FIDELITY_GATE.json written",
          flush=True)
    if not gate_doc["gate_pass"]:
        print("[gate] FAIL -> STOP. No new arms.", flush=True)
        sys.exit(1)

    # ---- sign-invariance proof (RT01) ----
    C0, QC0 = rt["rebuilt"]["RT01"]
    sig0 = sigma_docs(C0)
    assert np.all(sig0 > 0)
    doc_changed = int(np.count_nonzero((C0 / sig0[None, :] >= 0) != (C0 >= 0)))
    q_changed = int(np.count_nonzero((QC0 / sig0[None, :] >= 0) != (QC0 >= 0)))
    proof = {"archive": "RT01", "N": int(C0.shape[0]),
             "doc_elements": int(C0.size), "doc_bits_changed_by_rescale": doc_changed,
             "query_elements": int(QC0.size), "query_bits_changed_by_rescale": q_changed,
             "statement": "for sigma_j > 0, sign(C_ij/sigma_j) == sign(C_ij) elementwise; "
                          "per-axis scaling CANNOT change a code bit. Only rotation (or a "
                          "shifted threshold) changes bits.",
             "holds": bool(doc_changed == 0 and q_changed == 0)}
    print(f"[proof] rescale bit changes: docs {doc_changed}/{C0.size}, "
          f"queries {q_changed}/{QC0.size} -> holds={proof['holds']}", flush=True)
    assert proof["holds"]

    # ---- top-K equivalence check ----
    verify_topk(RT_ARCHIVES,
                [rt["rebuilt"][a][0].shape[0] for a in RT_ARCHIVES])
    pq_chars = sorted(arch.keys())
    verify_topk(pq_chars[:3], [arch[c]["N"] for c in pq_chars[:3]])

    # ---- arms x scorers, streamed ----
    store_rt = {(a, s): {} for a in ARMS for s in SCORERS}
    store_pq = {(a, s): {} for a in ARMS for s in SCORERS}
    meta_rt, meta_pq = {}, {}
    fout = open(os.path.join(HERE, "per_query.jsonl"), "w")
    for a in RT_ARCHIVES:
        C, QC = rt["rebuilt"][a]
        qs = rt_raw[a]["queries"]
        score_archive(a, C, QC, [q["qid"] for q in qs],
                      [np.asarray(q["gold"]).ravel() for q in qs],
                      fout, "RealTalk", store_rt, meta_rt)
    qtext = pq_collect_questions(qa, mem, ORD, arch, QDAT)
    for ch in pq_chars:
        C = pq["rebuilt"][ch]
        qids = sorted([q for q, r in QDAT.items() if r["char"] == ch])
        QC = np.array([np.asarray(QDAT[q]["qC"], dtype=np.float64) for q in qids])
        golds = [np.asarray(QDAT[q]["gold"]).ravel() for q in qids]
        score_archive(ch, C, QC, qids, golds, fout, "PerLTQA", store_pq, meta_pq)
    fout.close()
    print("[arms] per_query.jsonl closed", flush=True)

    # ---- aggregates + contrasts ----
    rng = np.random.default_rng(BOOT_SEED)
    results = {"_label": LABEL,
               "note": "Per-benchmark only. NEVER averaged across benchmarks. "
                       "Paired archive-clustered bootstrap, 20000 reps, seed 20260916.",
               "seeds": {"LSA32": 5101, "SVD96": 5204, "ITQ_init": ITQ_SEED,
                         "ITQ_iters": ITQ_ITERS, "RAND": RAND_SEEDS,
                         "bootstrap": BOOT_SEED, "bootstrap_reps": BOOT_REPS},
               "sign_invariance_proof": proof,
               "benchmarks": {}}
    for bench, ordered, store, meta in (
            ("RealTalk", RT_ARCHIVES, store_rt, meta_rt),
            ("PerLTQA", pq_chars, store_pq, meta_pq)):
        summary, by_archive = summarize(bench, ordered, store)
        vs_full, itq_rand = run_contrasts(bench, ordered, store, rng)
        # best arm by qscale Hit@10 (production's primary scorer), FULL excluded
        best = max(NEW_ARMS, key=lambda a: summary[f"{a}/qscale"]["hit10_pct"])
        # stratification: best vs FULL, both scorers
        if bench == "RealTalk":
            doctext = {a: rt_raw[a]["texts"] for a in ordered}
            qq = {a: [(q["qid"], q["text"], q["gold"]) for q in rt_raw[a]["queries"]]
                  for a in ordered}
        else:
            doctext = {c: [t for _, t in pq_build_items(c, mem, ORD)] for c in ordered}
            qq = {c: [(q, qtext[q], np.asarray(QDAT[q]["gold"]).ravel().tolist())
                      for q in sorted([x for x, r in QDAT.items() if r["char"] == c])]
                  for c in ordered}
        bands = {}
        for cl in ordered:
            bands[cl] = idf_bands(doctext[cl], qq[cl])
        strat = {"best_arm": best, "rule": "max IDF among query-gold shared terms "
                 "(documents-only BM25-style IDF); bands no_shared/common(<2)/mid(2-4)/rare(>=4)",
                 "bands": {}}
        for arm in ["FULL", best]:
            for scorer in SCORERS:
                d = store[(arm, scorer)]
                for band in ["no_shared", "common", "mid", "rare"]:
                    kk = [k for k in d if bands[k[0]][k[1]][0] == band]
                    key = f"{arm}/{scorer}/{band}"
                    if kk:
                        strat["bands"][key] = {
                            "n": int(len(kk)),
                            "hit10_pct": float(np.mean([d[k]["hit10"] for k in kk]) * 100),
                            "fr3_pct": float(np.mean([d[k]["fr3"] for k in kk]) * 100)}
                    else:
                        strat["bands"][key] = {"n": 0, "hit10_pct": None, "fr3_pct": None}
        # cost accounting
        n_docs = sum(meta[c]["n_docs"] for c in ordered)
        R32, R64 = 96 * 96 * 4, 96 * 96 * 8
        M32, M64 = 96 * 4, 96 * 8
        K = len(ordered)
        cost = {"n_docs": int(n_docs), "payload_bytes_total": int(n_docs * 12),
                "rotation_R_bytes": {"float32_per_archive": R32, "float64_per_archive": R64,
                                     "float32_total": R32 * K, "float64_total": R64 * K},
                "median_thr_bytes": {"float32_per_archive": M32, "float64_per_archive": M64,
                                     "float32_total": M32 * K, "float64_total": M64 * K},
                "fit_s_per_archive": {c: {a: meta[c]["timing"][a]["fit_s"] for a in ARMS}
                                       for c in ordered},
                "qrot_us_per_query": {c: {a: meta[c]["timing"][a]["qrot_us_per_query"]
                                          for a in ARMS} for c in ordered}}
        bal_sum = {}
        for arm in ARMS:
            mm = np.array([meta[c]["bit_balance"][arm]["mean_frac1"] for c in ordered])
            mn = np.array([meta[c]["bit_balance"][arm]["min_frac1"] for c in ordered])
            mx = np.array([meta[c]["bit_balance"][arm]["max_frac1"] for c in ordered])
            bal_sum[arm] = {"mean_of_mean_frac1": float(mm.mean()),
                            "min_of_min_frac1": float(mn.min()),
                            "max_of_max_frac1": float(mx.max())}
        itq_diag = {c: {"loss_init": meta[c]["arm_extra"]["ITQ_C"]["loss_init"],
                        "loss_final": meta[c]["arm_extra"]["ITQ_C"]["loss_final"],
                        "orth_err": meta[c]["arm_extra"]["ITQ_C"]["orth_err"]}
                    for c in ordered}
        results["benchmarks"][bench] = {
            "n_archives": K, "n_queries": summary["FULL/qscale"]["n"],
            "n_docs": int(n_docs), "summary": summary, "by_archive": by_archive,
            "contrasts_vs_FULL_pp": vs_full, "itq_minus_rand_pp": itq_rand,
            "stratification_best_vs_FULL": strat, "bit_balance": bal_sum,
            "itq_diagnostics": itq_diag, "cost": cost,
            "per_archive_meta": meta}
        print(f"=== {bench} (best non-FULL by qscale Hit@10: {best}) ===", flush=True)
        for arm in ARMS:
            for scorer in SCORERS:
                s = summary[f"{arm}/{scorer}"]
                print(f"  {arm:14s} {scorer:6s} Hit@10={s['hit10_pct']:.4f} "
                      f"FR@3={s['fr3_pct']:.4f} Hit@3={s['hit3_pct']:.4f} "
                      f"expHit@10={s['exp_hit10_pct']:.4f} n={s['n']}", flush=True)
        for name, entry in list(vs_full.items()) + list(itq_rand.items()):
            print(f"  [{name}] " + "; ".join(
                f"{m}={entry[m]['mean_diff_pp']:+.2f}"
                f"[{entry[m]['ci95_lo_pp']:+.2f},{entry[m]['ci95_hi_pp']:+.2f}]"
                for m in ["hit10", "fr3"]), flush=True)
    # internal consistency: arms-stage FULL must EXACTLY reproduce gate G2 numbers
    # (same rebuilt C/QC, same scorers). Catches orientation/indexing bugs like the
    # S_sym.T defect caught in run 1.
    g2r = rt["gate"]["G2_rebuilt"]
    srt = results["benchmarks"]["RealTalk"]["summary"]
    for k in ["hit10_pct", "fr3_pct", "hit3_pct", "exp_hit10_pct"]:
        assert abs(srt[f"FULL/sym"][k] - g2r["sym"][k]) < 1e-9, (k, srt[f"FULL/sym"][k])
        assert abs(srt[f"FULL/qscale"][k] - g2r["qscale"][k]) < 1e-9, (k, srt[f"FULL/qscale"][k])
    g2p = pq["gate"]["G2_cached_replay"]
    spq = results["benchmarks"]["PerLTQA"]["summary"]
    for k in ["hit10_pct", "fr3_pct", "hit3_pct", "exp_hit10_pct"]:
        assert abs(spq[f"FULL/sym"][k] - g2p["sym"][k]) < 1e-9, (k, spq[f"FULL/sym"][k])
        assert abs(spq[f"FULL/qscale"][k] - g2p["qscale"][k]) < 1e-9, (k, spq[f"FULL/qscale"][k])
    print("[check] arms-stage FULL reproduces gate G2 on both benchmarks exactly", flush=True)
    results["total_wall_s"] = float(time.perf_counter() - t_all)
    with open(os.path.join(HERE, "RESULTS.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"[done] total {time.perf_counter()-t_all:.1f}s", flush=True)


if __name__ == "__main__":
    main()
