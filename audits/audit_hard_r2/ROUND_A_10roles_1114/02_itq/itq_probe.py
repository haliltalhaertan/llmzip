"""02_itq probe: exact-protocol ITQ vs paired random rotation.

READ-ONLY sources; writes only to CWD (own audit dir).
Protocol copied VERBATIM from top10_comparison_r1/math_r1/quant/quant_math.py
(copy at ./quant_math_ORIG.py):
  random_orthogonal: default_rng(seed).standard_normal((d,d)) -> U@Vt float64
  fit_itq: 50 iters B<-sign(CR>=0), R<-U Vt from SVD(C^T B), docs only
  sigma_docs: max(std ddof=0, 1e-12) on THAT ARM's rotated docs
  sym: -Hamming((Cr>=0),(QCr>=thr)); qscale: Dpm @ (Qc/sig).T
  ties: audit.det_top10 via cached fast_topk (verified equivalent on samples)
Scoring entrypoint is the COPIED audit lib (./audit_baseline_lib_ORIG.py):
  det_top10 / hrn / expected_hit imported from the copy, never reimplemented.
Quartet per (archive, arm, scorer): hit10, fr3, hit3, exp_hit10.

Usage: ml-python itq_probe.py --bench rt|pq
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = "/mnt/c/Users/MDP/dev/llmzip-work"
RT_DATA = R + "/top10_comparison_r1/data"
RT_CACHE = R + "/bench3/runs/b3a_realtalk/rt_repr"
PQ_ARCH = R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PQ_Q = R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl"

ITQ_ITERS = 50
ITQ_SEEDS = [20260916, 20260917, 20260918, 7, 42]  # 5 ITQ inits; RAND paired per seed
RT_ARCHIVES = ["RT%02d" % i for i in range(1, 11)]
SUBSET_PQ = ["Cai Xiuying", "Cao Lili", "Feng Wei", "Han Gang", "He Feng"]  # deterministic: first 5 alphabetical


def load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_copy", os.path.join(HERE, "audit_baseline_lib_ORIG.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert getattr(mod, "TIE_SALT", None) == "top10-r1", "tie salt mismatch"
    return mod


audit = load_audit()

# ---- verbatim rotation machinery (cf. quant_math_ORIG.py:133-162) ----
def random_orthogonal(d, seed):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((d, d))
    U, _, Vt = np.linalg.svd(A, full_matrices=False)
    return (U @ Vt).astype(np.float64)


def fit_itq(C, n_iter=ITQ_ITERS, seed=20260916):
    t0 = time.perf_counter()
    C = np.asarray(C, dtype=np.float64)
    R = random_orthogonal(C.shape[1], seed)
    B = np.where(C @ R >= 0, 1.0, -1.0)
    loss_init = float(np.sum((B - C @ R) ** 2))
    haar_init = float(np.mean((np.abs(C @ R) - 1.0) ** 2))
    for _ in range(n_iter):
        B = np.where(C @ R >= 0, 1.0, -1.0)
        M = C.T @ B
        U, _, Vt = np.linalg.svd(M, full_matrices=False)
        R = U @ Vt
    B = np.where(C @ R >= 0, 1.0, -1.0)
    loss_final = float(np.sum((B - C @ R) ** 2))
    haar_final = float(np.mean((np.abs(C @ R) - 1.0) ** 2))
    return (R.astype(np.float64), time.perf_counter() - t0, loss_init, loss_final,
            haar_init, haar_final)


def sigma_docs(C):
    return np.maximum(np.std(np.asarray(C, dtype=np.float64), axis=0, ddof=0), 1e-12)


# ---- cached exact top-K (cf. quant_math_ORIG.py:90-118) ----
_tie_cache = {}


def fast_topk(scores, archive_id, k):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    key = (archive_id, len(s))
    tb = _tie_cache.get(key)
    if tb is None:
        hs = [hashlib.sha256(("top10-r1|%s|%d" % (archive_id, r)).encode()).hexdigest()
              for r in range(len(s))]
        tb = np.array(sorted(range(len(s)), key=lambda r: (hs[r], r)))
        _tie_cache[key] = tb
    return tb[np.argsort(-m[tb], kind="stable")][:k]


def verify_topk(archives, sizes):
    n = 0
    rng = np.random.default_rng(0)
    for a, N in zip(archives, sizes):
        for _ in range(3):
            s = rng.normal(size=N)
            s[rng.random(N) < 0.3] = s[0]
            for k in (3, 10):
                x = np.asarray(audit.det_top10(s, a, k)).tolist()
                y = np.asarray(fast_topk(s, a, k)).tolist()
                assert x == y, "fast_topk mismatch %s k=%d" % (a, k)
                n += 1
    print("[topk] verified equivalent on %d samples" % n, flush=True)


def query_metrics(scores, gold, archive_id):
    top10 = fast_topk(scores, archive_id, 10)
    hit10, _, _ = audit.hrn(top10, gold, 10)
    top3 = fast_topk(scores, archive_id, 3)
    hit3, fr3, _ = audit.hrn(top3, gold, 3)
    exp10 = audit.expected_hit(np.asarray(scores, dtype=np.float64), gold, 10)
    return {"hit10": float(hit10), "fr3": float(fr3), "hit3": float(hit3),
            "exp_hit10": float(exp10)}


def score_frame(archive_id, Cr, QCr):
    """Exact doc/query pipeline per arm frame (cf. score_archive in ORIG)."""
    Cr = np.asarray(Cr, dtype=np.float64)
    QCr = np.asarray(QCr, dtype=np.float64)
    Db = (Cr >= 0)
    Dpm = np.where(Db, 1.0, -1.0)
    sig = sigma_docs(Cr)
    packed = np.packbits(Db, axis=-1, bitorder="big")
    assert packed.shape == (Cr.shape[0], 12), "payload != 12B/doc"
    Qb = (QCr >= 0)
    S_sym = -np.count_nonzero(Db[None, :, :] != Qb[:, None, :], axis=2).astype(np.float64)
    S_q = (Dpm @ (QCr / sig).T).T  # (Q, N)
    return S_sym, S_q


def load_rt():
    """Raw qids/gold (like rt_load_raw) + cached C/QC matched by qid (like rt_fidelity)."""
    out = {}
    for a in RT_ARCHIVES:
        with open(os.path.join(RT_DATA, a + ".json")) as f:
            d = json.load(f)
        docs = sorted(d["docs"], key=lambda r: r["row"])
        assert [r["row"] for r in docs] == list(range(len(docs)))
        queries = [{"qid": q["qid"], "text": q["text"],
                    "gold": [int(g) for g in q["gold"]]} for q in d["queries"]]
        with open(os.path.join(RT_CACHE, a + ".pkl"), "rb") as f:
            c = pickle.load(f)
        C = np.asarray(c["C"], dtype=np.float64)
        QCc = np.asarray(c["QC"], dtype=np.float64)
        pos = {q: i for i, q in enumerate(c["qids"])}
        qi = [pos[q["qid"]] for q in queries]
        assert len(set(qi)) == len(qi)
        assert all(c["questions"][i] == q["text"] for i, q in zip(qi, queries))
        assert all(sorted(map(int, c["gold_rows"][i])) == sorted(q["gold"])
                   for i, q in zip(qi, queries))
        out[a] = {"C": C, "QC": QCc[np.array(qi)],
                  "qids": [q["qid"] for q in queries],
                  "golds": [np.asarray(q["gold"]).ravel() for q in queries]}
    return out


def load_pq(subset):
    arch = pickle.load(open(PQ_ARCH, "rb"))
    qd = pickle.load(open(PQ_Q, "rb"))
    by = {}
    for qk, v in qd.items():
        by.setdefault(v["char"], []).append(
            (qk, np.asarray(v["qC"], dtype=np.float64),
             np.asarray(v["gold"]).ravel()))
    out = {}
    for ch in subset:
        assert ch in arch, "missing C for %s" % ch
        C = np.asarray(arch[ch]["C"], dtype=np.float64)
        rows = sorted(by[ch], key=lambda r: r[0])
        QC = np.array([r[1] for r in rows])
        assert QC.shape[1] == 96 and C.shape[1] == 96
        out[ch] = {"C": C, "QC": QC,
                   "qids": [r[0] for r in rows],
                   "golds": [r[2] for r in rows]}
    return out


def run_bench(bench, archives, tag):
    res = json.load(open(os.path.join(HERE, "RESULTS_ORIG.json")))
    key = "RealTalk" if bench == "rt" else "PerLTQA"
    orig_by = res["benchmarks"][key]["by_archive"]
    verify_topk(list(archives.keys())[:3],
                [archives[a]["C"].shape[0] for a in list(archives.keys())[:3]])
    rows = []
    gate_maxdiff = 0.0
    for aid, D in archives.items():
        C, QC, qids, golds = D["C"], D["QC"], D["qids"], D["golds"]
        nq = len(qids)
        # ---- P2 gate: FULL with exact ties vs stored per-archive rows ----
        S_sym, S_q = score_frame(aid, C, QC)
        full = {}
        for scorer, S in (("sym", S_sym), ("qscale", S_q)):
            mh = np.array([query_metrics(np.ascontiguousarray(S[j]), golds[j], aid)["hit10"]
                           for j in range(nq)])
            mf = np.array([query_metrics(np.ascontiguousarray(S[j]), golds[j], aid)["fr3"]
                           for j in range(nq)])
            me = np.array([query_metrics(np.ascontiguousarray(S[j]), golds[j], aid)["exp_hit10"]
                           for j in range(nq)])
            full[scorer] = {"hit10": float(mh.mean() * 100), "fr3": float(mf.mean() * 100),
                            "exp": float(me.mean() * 100)}
        for scorer in ("sym", "qscale"):
            o = orig_by["FULL/%s" % scorer][aid]
            for m, mine in (("hit10_pct", full[scorer]["hit10"]),
                            ("fr3_pct", full[scorer]["fr3"]),
                            ("exp_hit10_pct", full[scorer]["exp"])):
                d = abs(mine - o[m])
                gate_maxdiff = max(gate_maxdiff, d)
                assert d < 1e-9, "GATE MISMATCH %s %s %s: mine=%.12f orig=%.12f" % (
                    aid, scorer, m, mine, o[m])
        # ---- P3: five ITQ inits + paired RAND, identical pipeline/ties ----
        frames = {"FULL": (C, QC, {})}
        for s in ITQ_SEEDS:
            R, fs, l0, l1, h0, h1 = fit_itq(C, seed=s)
            assert l1 <= l0 + 1e-6 * max(1.0, abs(l0)), "ITQ loss did not decrease %s s=%d" % (aid, s)
            Rr = random_orthogonal(96, s)
            assert float(np.max(np.abs(Rr - random_orthogonal(96, s)))) == 0.0
            orth = float(np.max(np.abs(R.T @ R - np.eye(96))))
            assert orth < 1e-10, "ITQ R not orthogonal: %g" % orth
            orthr = float(np.max(np.abs(Rr.T @ Rr - np.eye(96))))
            assert orthr < 1e-10
            frames["ITQ_%d" % s] = (
                C @ R, QC @ R,
                {"loss_init": l0, "loss_final": l1, "haar_init": h0,
                 "haar_final": h1, "orth_err": orth, "fit_s": fs})
            frames["RAND_%d" % s] = (C @ Rr, QC @ Rr, {"orth_err": orthr})
        for arm, (Cr, QCr, extra) in frames.items():
            S_sym, S_q = score_frame(aid, Cr, QCr)
            for scorer, S in (("sym", S_sym), ("qscale", S_q)):
                mh = np.zeros(nq)
                mf = np.zeros(nq)
                m3 = np.zeros(nq)
                me = np.zeros(nq)
                for j in range(nq):
                    m = query_metrics(np.ascontiguousarray(S[j]), golds[j], aid)
                    mh[j], mf[j], m3[j], me[j] = m["hit10"], m["fr3"], m["hit3"], m["exp_hit10"]
                rows.append({"bench": key, "archive": aid, "arm": arm, "scorer": scorer,
                             "n": nq, "hit10_pct": float(mh.mean() * 100),
                             "fr3_pct": float(mf.mean() * 100),
                             "hit3_pct": float(m3.mean() * 100),
                             "exp_hit10_pct": float(me.mean() * 100),
                             "loss_init": extra.get("loss_init", ""),
                             "loss_final": extra.get("loss_final", ""),
                             "haar_init": extra.get("haar_init", ""),
                             "haar_final": extra.get("haar_final", "")})
        print("[%s] %s: nq=%d FULL sym=%.4f qscale=%.4f gate_ok" % (
            tag, aid, nq, full["sym"]["hit10"], full["qscale"]["hit10"]), flush=True)
    fn = os.path.join(HERE, "per_archive_rows_%s.csv" % tag)
    with open(fn, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    # cohort means (query-weighted like summarize: flat mean over rows' queries)
    summ = {}
    for arm in sorted(set(r["arm"] for r in rows)):
        for scorer in ("sym", "qscale"):
            sel = [r for r in rows if r["arm"] == arm and r["scorer"] == scorer]
            n = sum(r["n"] for r in sel)
            for m in ("hit10_pct", "fr3_pct", "hit3_pct", "exp_hit10_pct"):
                summ["%s/%s/%s" % (arm, scorer, m)] = sum(r[m] * r["n"] for r in sel) / n
            summ["%s/%s/n" % (arm, scorer)] = n
    summ["gate_max_abs_diff_vs_RESULTS_ORIG_pp"] = gate_maxdiff
    with open(os.path.join(HERE, "summary_%s.json" % tag), "w") as f:
        json.dump({"bench": key, "archives": sorted(archives.keys()),
                   "itq_seeds": ITQ_SEEDS, "itq_iters": ITQ_ITERS,
                   "tie": "audit.det_top10 via verified fast_topk (TIE_SALT top10-r1)",
                   "summary": summ}, f, indent=2)
    print("[%s] wrote %d rows gate_maxdiff=%.3e" % (tag, len(rows), gate_maxdiff), flush=True)
    for s in ITQ_SEEDS:
        for scorer in ("sym", "qscale"):
            a = summ["ITQ_%d/%s/hit10_pct" % (s, scorer)]
            b = summ["RAND_%d/%s/hit10_pct" % (s, scorer)]
            print("  seed %d %s: ITQ=%.4f RAND=%.4f ITQ-RAND=%+.4f" % (s, scorer, a, b, a - b),
                  flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True, choices=["rt", "pq"])
    args = ap.parse_args()
    t0 = time.time()
    if args.bench == "rt":
        archives = load_rt()
        n = sum(len(v["qids"]) for v in archives.values())
        assert n == 705, "RT cohort n=%d != 705" % n
        run_bench("rt", archives, "rt")
    else:
        archives = load_pq(SUBSET_PQ)
        run_bench("pq", archives, "pqsub5")
    print("wall=%.1fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()

