"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
PerLTQA production-identity gate (auditor rebuild, round-3 leak_perltqa role).

Copies build_items + fit_archive verbatim from
  top10_comparison_r1/ablation_r2/perltqa/fidelity_gate.py (lines 38-83)
and question-text mapping from ablation.py collect_questions (lines 73-88).
READS (read-only): raw PerLTQA jsons, cache_arch_eval.pkl, cache_q_eval.pkl,
  ablation_r2/perltqa/{FIDELITY_GATE.json,RESULTS.json} (as targets only).
WRITES: GATE_REBUILD.json in this directory only.

G1 : sign(C_rebuilt)==sign(C_cached) elementwise, all 30 archives (target 0/1179648).
G1b: sign(QC_rebuilt)==sign(QC_cached) elementwise, all 8265 queries (new: validates the
     query-side rebuild the TRANS arm of the leak experiment depends on).
G2 : replay pooled metrics from CACHED C/qC with shared scorers (targets from REPORT.md).
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
SVD_SEED = 5204
SEC = {"profile": "PRF", "social_relationship": "SOC", "events": "EVE", "dialogues": "DLG"}

qa = json.load(open(BASE + "/perltqa_en_v2.json"))
mem = json.load(open(BASE + "/perltmem_en_v2.json"))
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem])
ORD = {c: i for i, c in enumerate(BANKED)}


def parse_social(v):
    if isinstance(v, dict):
        return v
    return ast.literal_eval(v)


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


def collect_questions(arch_cache):
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


def fit_archive(texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(svd.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    return wv, cv, svd, s96, mu, C


arch = pickle.load(open(ARCH_PKL, "rb"))
QDAT = pickle.load(open(Q_PKL, "rb"))
chars = sorted(arch.keys())
assert len(chars) == 30, f"expected 30 eval archives, got {len(chars)}"
QTEXT = collect_questions(arch)
assert set(QDAT) <= set(QTEXT), "missing question texts"

t0 = time.time()
total_bits = 0
total_diff = 0
max_abs = 0.0
per_arch = []
fits = {}
for char in chars:
    items = build_items(char)
    texts = [t for _, t in items]
    wv, cv, svd, s96, mu, C_new = fit_archive(texts)
    fits[char] = (wv, cv, svd, s96, mu)
    C_cached = np.asarray(arch[char]["C"], dtype=np.float64)
    assert C_new.shape == C_cached.shape, f"{char}: shape {C_new.shape} vs cached {C_cached.shape}"
    assert len(items) == arch[char]["N"], f"{char}: N {len(items)} vs cached {arch[char]['N']}"
    diff = int(np.count_nonzero((C_new >= 0) != (C_cached >= 0)))
    mad = float(np.max(np.abs(C_new - C_cached)))
    total_bits += C_new.size
    total_diff += diff
    max_abs = max(max_abs, mad)
    per_arch.append({"char": char, "N": len(items), "differing_bits": diff,
                     "n_bits": int(C_new.size), "max_abs_diff": mad})
    print(f"{char}: N={len(items)} diffbits={diff}/{C_new.size} maxabs={mad:.3e}", flush=True)

# G1b: query-side rebuild vs cached qC (sign agreement; max abs diff informational only,
# since queries pass through normalize() of a single row - deterministic, should match)
q_tot = 0
q_diff = 0
q_maxabs = 0.0
for qid, q in QDAT.items():
    char = q["char"]
    wv, cv, svd, s96, mu = fits[char]
    w = normalize(wv.transform([QTEXT[qid]]))
    c = normalize(cv.transform([QTEXT[qid]]))
    ql = normalize(svd.transform(w))
    zq = sparse.hstack([sparse.csr_matrix(ql), w, c], format="csr")
    qC_new = (normalize(s96.transform(zq)) - mu)[0].astype(np.float64)
    qC_cached = np.asarray(q["qC"], dtype=np.float64)
    assert qC_new.shape == qC_cached.shape, f"{qid}: shape mismatch"
    q_diff += int(np.count_nonzero((qC_new >= 0) != (qC_cached >= 0)))
    q_tot += qC_new.size
    q_maxabs = max(q_maxabs, float(np.max(np.abs(qC_new - qC_cached))))
print(f"G1b queries: {q_diff}/{q_tot} sign diffs, maxabs={q_maxabs:.3e}", flush=True)

# G2: replay production metrics from CACHED C/qC with shared scorer definitions
n = len(QDAT)
hits_sym = np.zeros(n)
hits_q = np.zeros(n)
fr3_sym = np.zeros(n)
fr3_q = np.zeros(n)
sigmas = {}
for char in chars:
    C = np.asarray(arch[char]["C"], dtype=np.float64)
    std = np.std(C, axis=0, ddof=0)
    sigmas[char] = np.where(std < 1e-12, 1e-12, std)
for i, (qid, q) in enumerate(QDAT.items()):
    char = q["char"]
    C = np.asarray(arch[char]["C"], dtype=np.float64)
    qC = np.asarray(q["qC"], dtype=np.float64)
    gold = np.asarray(q["gold"]).ravel()
    Db = (C >= 0)
    Qb = (qC >= 0)
    s_sym = -np.count_nonzero(Db != Qb[None, :], axis=1).astype(np.float64)
    Dpm = np.where(Db, 1.0, -1.0)
    s_q = Dpm @ (qC / sigmas[char])
    for s, H, F in ((s_sym, hits_sym, fr3_sym), (s_q, hits_q, fr3_q)):
        top10 = abl.det_top10(s, char, 10)
        top3 = abl.det_top10(s, char, 3)
        hit, rec, _ = abl.hrn(top10, gold, 10)
        _, rec3, _ = abl.hrn(top3, gold, 3)
        H[i] = hit
        F[i] = rec3

g2 = {"n_queries": n, "sym_hit10": float(hits_sym.mean()), "qscale_hit10": float(hits_q.mean()),
      "sym_fr3": float(fr3_sym.mean()), "qscale_fr3": float(fr3_q.mean())}
print("G2 replay:", json.dumps({k: round(v * 100, 4) for k, v in g2.items() if k != "n_queries"}), flush=True)

gate = {
    "G1_total_differing_bits": total_diff, "G1_total_bits": total_bits,
    "G1_max_abs_diff": max_abs, "G1_pass": bool(total_diff == 0),
    "G1_target": "0/1179648",
    "G1b_query_sign_diffs": q_diff, "G1b_query_total": q_tot, "G1b_max_abs_diff": q_maxabs,
    "G1_per_archive": per_arch,
    "G2_recomputed": g2,
    "G2_targets": {"qscale_hit10": 0.80, "sym_hit10_det": 0.756806, "qscale_fr3": 0.5324},
    "rebuild_time_s": time.time() - t0,
}
json.dump(gate, open("GATE_REBUILD.json", "w"), indent=2)
g1ok = total_diff == 0
g2ok = (abs(g2["qscale_hit10"] - 0.80) < 1e-9 and abs(g2["sym_hit10"] - 0.756806) < 5e-7
        and abs(g2["qscale_fr3"] - 0.5324) < 1e-4)
print("GATE", "PASS" if (g1ok and g2ok) else "FAIL", f"(G1b_signdiffs={q_diff})", flush=True)
