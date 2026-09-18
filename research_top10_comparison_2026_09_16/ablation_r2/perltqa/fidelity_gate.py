"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Fidelity gate: rebuild FULL-arm C per archive from raw texts using the exact frozen
recipe (bench3/runs/b3b_perltqa/step2_build.py build_items + fit_archive, verbatim),
compare sign(C) vs cached C, and replay cached production metrics.

Reads (read-only): raw PerLTQA jsons, cache_arch_eval.pkl, cache_q_eval.pkl.
Writes: FIDELITY_GATE.json only. No ablation numbers here.
"""
import ast
import hashlib
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
RES_JSON = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/resolution.json"
SVD_SEED = 5204

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
    return C, Z.shape


arch = pickle.load(open(ARCH_PKL, "rb"))
QDAT = pickle.load(open(Q_PKL, "rb"))
chars = sorted(arch.keys())
assert len(chars) == 30, f"expected 30 eval archives, got {len(chars)}"

t0 = time.time()
total_bits = 0
total_diff = 0
max_abs = 0.0
per_arch = []
for char in chars:
    items = build_items(char)
    texts = [t for _, t in items]
    C_new, zshape = fit_archive(texts)
    C_cached = np.asarray(arch[char]["C"], dtype=np.float64)
    assert C_new.shape == C_cached.shape, f"{char}: shape {C_new.shape} vs cached {C_cached.shape}"
    assert len(items) == arch[char]["N"], f"{char}: N {len(items)} vs cached {arch[char]['N']}"
    diff = int(np.count_nonzero((C_new >= 0) != (C_cached >= 0)))
    mad = float(np.max(np.abs(C_new - C_cached)))
    total_bits += C_new.size
    total_diff += diff
    max_abs = max(max_abs, mad)
    per_arch.append({"char": char, "N": len(items), "Z_shape": list(zshape),
                     "differing_bits": diff, "n_bits": int(C_new.size), "max_abs_diff": mad})
    print(f"{char}: N={len(items)} Z={zshape} diffbits={diff}/{C_new.size} maxabs={mad:.3e}", flush=True)
build_time = time.time() - t0

# G2: replay production metrics from CACHED C/qC with shared scorer definitions
n = len(QDAT)
hits_sym = np.zeros(n)
hits_q = np.zeros(n)
fr3_sym = np.zeros(n)
fr3_q = np.zeros(n)
hit3_sym = np.zeros(n)
hit3_q = np.zeros(n)
exp_sym = np.zeros(n)
exp_q = np.zeros(n)
sigmas = {}
for char in chars:
    C = np.asarray(arch[char]["C"], dtype=np.float64)
    std = np.std(C, axis=0, ddof=0)
    std = np.where(std < 1e-12, 1e-12, std)
    sigmas[char] = std
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
    for tag, s, H, F, H3, E in (("sym", s_sym, hits_sym, fr3_sym, hit3_sym, exp_sym),
                                ("qscale", s_q, hits_q, fr3_q, hit3_q, exp_q)):
        top10 = abl.det_top10(s, char, 10)
        top3 = abl.det_top10(s, char, 3)
        hit, rec, _ = abl.hrn(top10, gold, 10)
        hit3, rec3, _ = abl.hrn(top3, gold, 3)
        H[i] = hit
        F[i] = rec3
        H3[i] = hit3
        E[i] = abl.expected_hit(s, gold, 10)

g2 = {
    "n_queries": n,
    "sym_hit10": float(hits_sym.mean()),
    "sym_exphit10": float(exp_sym.mean()),
    "sym_fr3": float(fr3_sym.mean()),
    "sym_hit3": float(hit3_sym.mean()),
    "qscale_hit10": float(hits_q.mean()),
    "qscale_exphit10": float(exp_q.mean()),
    "qscale_fr3": float(fr3_q.mean()),
    "qscale_hit3": float(hit3_q.mean()),
}
print("G2 replay:", json.dumps({k: round(v * 100, 4) for k, v in g2.items() if k != "n_queries"}, indent=1), flush=True)

gate = {
    "label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
    "recipe": "bench3/runs/b3b_perltqa/step2_build.py build_items+fit_archive verbatim; LSA32 seed 5101, SVD96 seed 5204",
    "n_archives": len(chars),
    "G1_total_differing_bits": total_diff,
    "G1_total_bits": total_bits,
    "G1_bit_diff_rate": total_diff / total_bits,
    "G1_max_abs_diff": max_abs,
    "G1_pass": bool(total_diff == 0),
    "G1_per_archive": per_arch,
    "G2_targets": {"qscale_hit10": 0.80, "sym_hit10_det": 0.756806, "sym_hit10_exp": 0.757612, "qscale_fr3": 0.5324},
    "G2_recomputed": g2,
    "G2_deltas_pp": {
        "qscale_hit10": (g2["qscale_hit10"] - 0.80) * 100,
        "sym_hit10_det": (g2["sym_hit10"] - 0.756806) * 100,
        "sym_hit10_exp": (g2["sym_exphit10"] - 0.757612) * 100,
        "qscale_fr3": (g2["qscale_fr3"] - 0.5324) * 100,
    },
    "G2_pass": bool(abs(g2["qscale_hit10"] - 0.80) < 1e-9 and abs(g2["sym_hit10"] - 0.756806) < 5e-7
                    and abs(g2["sym_exphit10"] - 0.757612) < 5e-7 and abs(g2["qscale_fr3"] - 0.5324) < 1e-4),
    "rebuild_time_s": build_time,
    "seeds": {"LSA32": 5101, "SVD96": 5204},
}
json.dump(gate, open("FIDELITY_GATE.json", "w"), indent=2)
print("GATE", "PASS" if (gate["G1_pass"] and gate["G2_pass"]) else "FAIL", flush=True)
