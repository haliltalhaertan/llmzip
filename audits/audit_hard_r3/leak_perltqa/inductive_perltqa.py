"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
PerLTQA inductive (honest) leak probe — round-3 leak_perltqa role.

Method mirrors round-2 t_inductive_all10.py (RealTalk k=96), adapted to PerLTQA:
  TRANS: projector (TFIDF word1-2 + char_wb3-5 -> LSA32 -> SVD96 -> L2 -> mean-center)
         FITTED ON the held-out archive's own item texts (= production recipe).
  INDEP: same projector FITTED ON pooled item texts of the OTHER 29 archives.
  Both arms encode the held-out archive's docs + its questions; sigma = std of the
  held-out archive's encoded docs under that arm (as in ablation.py / round-2 score()).

READS (read-only): raw PerLTQA jsons, cache_arch_eval.pkl, cache_q_eval.pkl,
  ablation_r2/perltqa/RESULTS.json (per-archive FULL targets for TRANS validation).
WRITES: INDUCTIVE_PERLTQA.json in this directory only (merged incrementally).

Usage: ml-python inductive_perltqa.py [START] [END]   (archive index slice; default all 30)
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

HERE = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r3/leak_perltqa"
BASE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/PerLTQA/Dataset/en_v2"
ARCH_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
Q_PKL = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
PUB = json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ablation_r2/perltqa/RESULTS.json"))
OUT = HERE + "/INDUCTIVE_PERLTQA.json"
SEC = {"profile": "PRF", "social_relationship": "SOC", "events": "EVE", "dialogues": "DLG"}

qa = json.load(open(BASE + "/perltqa_en_v2.json"))
mem = json.load(open(BASE + "/perltmem_en_v2.json"))
qachars = [list(e.keys())[0] for e in qa]
BANKED = sorted([c for c in qachars if c in mem])
ORD = {c: i for i, c in enumerate(BANKED)}


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


def fit_projector(fit_texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
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


def encode(P, texts):
    wv, cv, sv, s96, mu = P
    Qw = normalize(wv.transform(texts))
    Qc = normalize(cv.transform(texts))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(s96.transform(Zq)) - mu).astype(np.float64)


def score_arm(C, QC, golds, char):
    Db = (C >= 0)
    Dpm = np.where(Db, 1.0, -1.0)
    Qpm = np.where(QC >= 0, 1.0, -1.0)
    sig = np.std(C, axis=0, ddof=0)
    sig = np.where(sig < 1e-12, 1e-12, sig)
    S_sym = -(96.0 - Dpm @ Qpm.T) / 2.0
    S_q = Dpm @ (QC / sig).T
    out = {}
    for name, S in (("sym", S_sym), ("qscale", S_q)):
        h10, f3, h3 = [], [], []
        for j in range(len(golds)):
            col = np.asarray(S[:, j]).ravel()
            top10 = abl.det_top10(col, char, 10)
            top3 = abl.det_top10(col, char, 3)
            hit10, _, _ = abl.hrn(top10, golds[j], 10)
            _, rec3, _ = abl.hrn(top3, golds[j], 3)
            hit3, _, _ = abl.hrn(top3, golds[j], 3)
            h10.append(hit10)
            f3.append(rec3)
            h3.append(hit3)
        out[name] = {"hit10": h10, "fr3": f3, "hit3": h3}
    return out


arch_cache = pickle.load(open(ARCH_PKL, "rb"))
QDAT = pickle.load(open(Q_PKL, "rb"))
chars = sorted(arch_cache.keys())
assert len(chars) == 30
QTEXT = collect_questions(arch_cache)
assert set(QDAT) <= set(QTEXT)

TEXTS = {}
for char in chars:
    items = build_items(char)
    assert len(items) == arch_cache[char]["N"], char
    TEXTS[char] = [t for _, t in items]

try:
    results = json.load(open(OUT))
except (FileNotFoundError, json.JSONDecodeError):
    results = {}

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end = int(sys.argv[2]) if len(sys.argv) > 2 else len(chars)

t_all = time.time()
for idx in range(start, end):
    held = chars[idx]
    if held in results and "INDEP" in results[held]:
        print(f"[{idx}] {held}: cached, skip", flush=True)
        continue
    t_a = time.time()
    docs_h = TEXTS[held]
    qids = sorted([q for q, r in QDAT.items() if r["char"] == held])
    questions = [QTEXT[q] for q in qids]
    golds = [np.asarray(QDAT[q]["gold"]).ravel() for q in qids]

    P_t = fit_projector(docs_h)
    C_t = encode(P_t, docs_h)
    Q_t = encode(P_t, questions)

    bg = []
    for c in chars:
        if c != held:
            bg.extend(TEXTS[c])
    P_i = fit_projector(bg)
    C_i = encode(P_i, docs_h)
    Q_i = encode(P_i, questions)

    # per-archive production-identity check on TRANS arm
    Cc = np.asarray(arch_cache[held]["C"], dtype=np.float64)
    dbits = int(np.count_nonzero((C_t >= 0) != (Cc >= 0)))
    qC_cached = np.array([np.asarray(QDAT[q]["qC"], dtype=np.float64) for q in qids])
    qbits = int(np.count_nonzero((Q_t >= 0) != (qC_cached >= 0)))

    rt = score_arm(C_t, Q_t, golds, held)
    ri = score_arm(C_i, Q_i, golds, held)

    # validate TRANS against published per-archive FULL numbers (must match ~exactly)
    pub_sym = PUB["per_archive"]["FULL"]["sym"][held]
    pub_q = PUB["per_archive"]["FULL"]["qscale"][held]
    chk = {"sym_hit10": float(np.mean(rt["sym"]["hit10"])) - pub_sym["hit10"],
           "sym_fr3": float(np.mean(rt["sym"]["fr3"])) - pub_sym["fr3"],
           "q_hit10": float(np.mean(rt["qscale"]["hit10"])) - pub_q["hit10"],
           "q_fr3": float(np.mean(rt["qscale"]["fr3"])) - pub_q["fr3"]}

    results[held] = {
        "idx": idx, "N": len(docs_h), "n_q": len(qids), "bg_docs": len(bg),
        "gate_doc_sign_diffs": dbits, "gate_doc_total": int(Cc.size),
        "gate_q_sign_diffs": qbits, "gate_q_total": int(qC_cached.size),
        "trans_vs_published_deltas": chk,
        "TRANS": {s: {m: float(np.mean(v)) for m, v in d.items()} for s, d in rt.items()},
        "INDEP": {s: {m: float(np.mean(v)) for m, v in d.items()} for s, d in ri.items()},
        "perq": {"trans_sym_h10": rt["sym"]["hit10"], "trans_sym_fr3": rt["sym"]["fr3"],
                 "trans_q_h10": rt["qscale"]["hit10"], "trans_q_fr3": rt["qscale"]["fr3"],
                 "indep_sym_h10": ri["sym"]["hit10"], "indep_sym_fr3": ri["sym"]["fr3"],
                 "indep_q_h10": ri["qscale"]["hit10"], "indep_q_fr3": ri["qscale"]["fr3"]},
        "qids": qids,
    }
    json.dump(results, open(OUT, "w"))
    dt = time.time() - t_a
    print(f"[{idx}] {held} N={len(docs_h)} nq={len(qids)} bg={len(bg)} "
          f"gate={dbits}/{Cc.size} qgate={qbits}/{qC_cached.size} "
          f"maxpubdelta={max(abs(v) for v in chk.values()):.2e} "
          f"| TRANS sym={results[held]['TRANS']['sym']['hit10']*100:.2f}/{results[held]['TRANS']['qscale']['hit10']*100:.2f} "
          f"| INDEP sym={results[held]['INDEP']['sym']['hit10']*100:.2f}/{results[held]['INDEP']['qscale']['hit10']*100:.2f} "
          f"({dt:.0f}s)", flush=True)
print(f"done slice [{start},{end}) in {time.time()-t_all:.0f}s -> {OUT}", flush=True)
