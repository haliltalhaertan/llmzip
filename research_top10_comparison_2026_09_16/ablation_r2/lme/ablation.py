"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
LME channel-ablation worker (top10_comparison_r1 / ablation_r2 / lme).

Rebuilds the frozen V52 representation per archive under 4 channel arms
(FULL / NO_LSA / NO_CHAR / WORD_ONLY; final SVD96 seed 5204, 96 dims, 12-byte
sign coding) and scores every arm under sym + qscale with deterministic top-K.

Usage:
  $HOME/muse-work/ml-python ablation.py
  Single-pass flow: rebuilds all archives (gate fields streamed to
  PARTIAL_archive_results.jsonl), writes FIDELITY_GATE.json, STOPS unless the
  gate passes, then writes per_query.jsonl + RESULTS.json.

Reads (read-only): regen/lme/items/*.json, regen/lme/cache_repr/*.pkl,
  top10_comparison_r1/audit/audit_baseline_lib.py (imported, never modified).
Writes (own dir only): FIDELITY_GATE.json, PARTIAL_archive_results.jsonl,
  per_query.jsonl, RESULTS.json.
"""
from __future__ import annotations

import argparse
import glob
import json
import multiprocessing as mp
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

MP_CTX = mp.get_context("fork")  # sandbox forbids forkserver listener sockets


def _worker_init():
    # One BLAS thread per worker: 3 workers share ~3 CPUs, so multithreaded
    # BLAS would oversubscribe. Deterministic output is unaffected (fixed seeds).
    try:
        from threadpoolctl import threadpool_limits
        threadpool_limits(limits=1)
    except Exception:
        pass

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

sys.path.insert(0, "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/audit")
import audit_baseline_lib as abl

LABEL = "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"
HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS_GLOB = "/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/items/*.json"
CACHE_GLOB = "/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl"
LSA_SEED = 5101
SVD_SEED = 5204
ARMS = ("FULL", "NO_LSA", "NO_CHAR", "WORD_ONLY")
ARM_BLOCKS = {"FULL": ("l", "w", "c"), "NO_LSA": ("w", "c"),
              "NO_CHAR": ("l", "w"), "WORD_ONLY": ("w",)}
SCORERS = ("sym", "qscale")
N_BOOT = 20000
BOOT_SEED = 20260916
# G2 frozen production targets (fractions).
TGT = {"qscale_hit10": 0.885106, "sym_hit10_det": 0.863830, "sym_hit10_exp": 0.860773}


def build_memory_texts(item):
    """Exact v1/v2 adapter payload recipe: '[{date}] {role}: {content}' in flat (session, turn) order."""
    texts, gold_rows = [], []
    row = 0
    for date, sess in zip(item["haystack_dates"], item["haystack_sessions"]):
        for turn in sess:
            role = turn.get("role")
            content = turn.get("content")
            if not isinstance(content, str):
                content = "" if content is None else str(content)
            texts.append(f"[{date}] {role}: {content}")
            hv = turn.get("has_answer", False)
            if bool(hv) if isinstance(hv, bool) else False:
                gold_rows.append(row)
            row += 1
    return texts, np.asarray(gold_rows, dtype=np.int64)


def fit_sources(texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2),
                         stop_words="english", sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    if d < 24:
        raise ValueError(f"latent dimension {d}<24; frozen source family unsupported")
    svd = TruncatedSVD(n_components=d, random_state=LSA_SEED)
    Xl = normalize(svd.fit_transform(Xw))
    return wv, cv, svd, Xw, Xc, Xl


def build_arm(blocks, Xl, Xw, Xc, Ql, Qw, Qc):
    parts = {"l": sparse.csr_matrix(Xl), "w": Xw, "c": Xc}
    qparts = {"l": sparse.csr_matrix(Ql), "w": Qw, "c": Qc}
    Z = sparse.hstack([parts[b] for b in blocks], format="csr")
    Zq = sparse.hstack([qparts[b] for b in blocks], format="csr")
    if min(Z.shape) <= 96:
        raise ValueError(f"arm {blocks}: Z shape {Z.shape} violates min(Z.shape)>96")
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    t0 = time.time()
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    QY = normalize(s96.transform(Zq))
    QC = (QY - mu).astype(np.float64).reshape(-1)
    dt = time.time() - t0
    return C, QC, tuple(int(x) for x in Z.shape), dt


def score_archive(C, qC, gold, archive_id):
    Db = (C >= 0)
    Qb = (qC >= 0)
    s_sym = -np.count_nonzero(Db != Qb[None, :], axis=1).astype(np.float64)
    std = np.std(C, axis=0, ddof=0).astype(np.float64)
    sigma = np.where(std < 1e-12, 1e-12, std)
    Dpm = np.where(Db, 1.0, -1.0)
    s_q = Dpm @ (qC / sigma)
    out = {}
    for name, s in (("sym", s_sym), ("qscale", s_q)):
        top10 = [int(x) for x in abl.det_top10(s, archive_id, 10).tolist()]
        top3 = [int(x) for x in abl.det_top10(s, archive_id, 3).tolist()]
        hit10, _, _ = abl.hrn(top10, gold, 10)
        hit3, fr3, _ = abl.hrn(top3, gold, 3)
        out[name] = {"scores_mean": float(np.mean(s)),
                     "top10": top10, "top3": top3,
                     "hit10": float(hit10), "fr3": float(fr3), "hit3": float(hit3),
                     "exp_hit10": float(abl.expected_hit(s, gold, 10))}
    payload_shape = tuple(int(x) for x in abl.pack_signs_bool(Db).shape)
    return out, payload_shape


def process_archive(qid):
    """Full per-archive work unit. Returns JSON-serializable dict (gate + ablation)."""
    t_start = time.time()
    item = json.load(open(f"/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/items/{qid}.json"))
    cached = pickle.load(open(f"/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/{qid}.pkl", "rb"))
    Cc = np.asarray(cached["C"], dtype=np.float64)
    qCc = np.asarray(cached["qC"], dtype=np.float64).reshape(-1)
    gold_cached = [int(x) for x in np.asarray(cached["gold"]).ravel().tolist()]
    texts, gold_rebuilt = build_memory_texts(item)
    gold_match = ([int(x) for x in gold_rebuilt.tolist()] == gold_cached)
    assert len(texts) == Cc.shape[0], f"{qid}: N {len(texts)} vs cached {Cc.shape[0]}"
    assert len(gold_cached) > 0, f"{qid}: empty cached gold"

    t_src = time.time()
    wv, cv, svd, Xw, Xc, Xl = fit_sources(texts)
    Qw = normalize(wv.transform([item["question"]]))
    Qc = normalize(cv.transform([item["question"]]))
    Ql = normalize(svd.transform(Qw))
    src_time = time.time() - t_src

    arms_out, z_shapes, arm_times = {}, {}, {}
    imposs = {}
    g1 = None
    for arm in ARMS:
        try:
            C, QC, zshape, dt = build_arm(ARM_BLOCKS[arm], Xl, Xw, Xc, Ql, Qw, Qc)
        except ValueError as e:
            imposs[arm] = str(e)
            continue
        z_shapes[arm] = list(zshape)
        arm_times[arm] = dt
        res, pshape = score_archive(C, QC, np.asarray(gold_cached), qid)
        arms_out[arm] = {"metrics": res, "payload_packed_shape": list(pshape),
                         "payload_bytes_per_doc": int(pshape[1])}
        if arm == "FULL":
            # G1: sign equality of the rebuilt FULL C/qC vs cached C/qC.
            g1 = {"differing_bits": int(np.count_nonzero((C >= 0) != (Cc >= 0))),
                  "n_bits": int(C.size),
                  "max_abs_diff": float(np.max(np.abs(C - Cc))),
                  "qC_differing_bits": int(np.count_nonzero((QC >= 0) != (qCc >= 0))),
                  "qC_max_abs_diff": float(np.max(np.abs(QC - qCc))),
                  "N": int(Cc.shape[0])}
    return {"question_id": qid, "N": int(Cc.shape[0]),
            "gold": gold_cached, "gold_rebuilt_match": bool(gold_match),
            "n_gold": len(gold_cached),
            "source_features": {"word": int(Xw.shape[1]), "char": int(Xc.shape[1]),
                                "latent": int(Xl.shape[1])},
            "source_fit_time_s": src_time, "total_time_s": time.time() - t_start,
            "g1": g1, "z_shapes": z_shapes, "arm_times": arm_times,
            "impossible_arms": imposs, "arms": arms_out}


def phase_gate():
    # Unified single-pass flow: per-archive results are held in memory; the gate
    # file is written (and must PASS) BEFORE any ablation artifact is written.
    qids = sorted(os.path.basename(p)[:-5] for p in glob.glob(ITEMS_GLOB))
    assert len(qids) == 470, f"expected 470 archives, got {len(qids)}"
    partial_path = os.path.join(HERE, "PARTIAL_archive_results.jsonl")
    # COORDINATOR PATCH (resumability only; no change to any recipe/metric code):
    # the original run held `arms` in memory and wrote only gate fields, so a timeout
    # discarded every completed archive. Full per-archive results are now cached and
    # reloaded, making the run resumable across restarts.
    cache_path = os.path.join(HERE, "ARCHIVE_CACHE.jsonl")
    t0 = time.time()
    done = {}
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as cf:
            for line in cf:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue  # tolerate a torn final line from a killed run
                if r.get("question_id") and "worker_error" not in r:
                    done[r["question_id"]] = r
        print(f"  resumed {len(done)}/{len(qids)} archives from cache", flush=True)
    todo = [q for q in qids if q not in done]
    with ProcessPoolExecutor(max_workers=8, mp_context=MP_CTX,
                             initializer=_worker_init) as ex:
        futs = {ex.submit(process_archive, q): q for q in todo}
        n = 0
        with open(partial_path, "w", encoding="utf-8") as f, \
                open(cache_path, "a", encoding="utf-8") as cf:
            # PARTIAL stores gate fields only (no ablation numbers) as archives complete.
            for fut in as_completed(futs):
                q = futs[fut]
                try:
                    r = fut.result()
                except Exception as e:  # noqa: BLE001 -- must not lose the failing qid
                    r = {"question_id": q, "worker_error": repr(e)}
                done[q] = r
                if "worker_error" not in r:
                    cf.write(json.dumps(r) + "\n")
                    cf.flush()
                    f.write(json.dumps({k: v for k, v in r.items() if k != "arms"}) + "\n")
                else:
                    f.write(json.dumps(r) + "\n")
                f.flush()
                n += 1
                if n % 25 == 0:
                    print(f"  progress {n}/{len(todo)} (total {len(done)}/{len(qids)})", flush=True)
        for q, r in done.items():
            if "worker_error" not in r and q not in set(todo):
                f_line = json.dumps({k: v for k, v in r.items() if k != "arms"})
                with open(partial_path, "a", encoding="utf-8") as f2:
                    f2.write(f_line + "\n")
    errs = {q: r.get("worker_error") for q, r in done.items() if "worker_error" in r}
    assert not errs, f"worker failures: {list(errs.items())[:3]}"
    assert set(done) == set(qids), "missing archives"
    assert all(r.get("gold_rebuilt_match") for r in done.values()), "gold mapping mismatch"
    assert all(not r.get("impossible_arms") for r in done.values()), \
        f"protocol violation min(Z)>96: {[ (q, r['impossible_arms']) for q, r in done.items() if r.get('impossible_arms')][:3]}"

    tot_bits = sum(r["g1"]["n_bits"] for r in done.values())
    tot_diff = sum(r["g1"]["differing_bits"] for r in done.values())
    max_abs = max(r["g1"]["max_abs_diff"] for r in done.values())
    clean = sum(1 for r in done.values() if r["g1"]["differing_bits"] == 0)

    # G2: replay cached production metrics with the shared scorer definitions.
    order = sorted(qids)
    H = {s: np.zeros(470) for s in ("sym_hit", "q_hit", "sym_exp", "q_exp",
                                    "sym_fr3", "q_fr3", "sym_hit3", "q_hit3")}
    for i, q in enumerate(order):
        cached = pickle.load(open(
            f"/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/{q}.pkl", "rb"))
        C = np.asarray(cached["C"], dtype=np.float64)
        qC = np.asarray(cached["qC"], dtype=np.float64).reshape(-1)
        gold = np.asarray(cached["gold"]).ravel()
        res, _ = score_archive(C, qC, gold, q)
        H["sym_hit"][i] = res["sym"]["hit10"]
        H["q_hit"][i] = res["qscale"]["hit10"]
        H["sym_exp"][i] = res["sym"]["exp_hit10"]
        H["q_exp"][i] = res["qscale"]["exp_hit10"]
        H["sym_fr3"][i] = res["sym"]["fr3"]
        H["q_fr3"][i] = res["qscale"]["fr3"]
        H["sym_hit3"][i] = res["sym"]["hit3"]
        H["q_hit3"][i] = res["qscale"]["hit3"]
    g2 = {k: float(v.mean()) for k, v in H.items()}
    g1_pass = (tot_diff == 0)
    g2_pass = (abs(g2["q_hit"] - TGT["qscale_hit10"]) < 1e-9
               and abs(g2["sym_hit"] - TGT["sym_hit10_det"]) < 1e-9
               and abs(g2["sym_exp"] - TGT["sym_hit10_exp"]) < 1e-9)
    gate = {
        "label": LABEL,
        "recipe": "adapter v1/v2 payload '[date] role: content'; word TFIDF(1,2;english;sublinear) + "
                  "char_wb TFIDF(3,5;sublinear) + LSA32 SVD(random_state=5101); Z=[LSA|word|char] -> "
                  "SVD96(random_state=5204) -> L2 normalize -> archive-mean centering; query=question text only",
        "adapter_version": "v1 and v2 produce bit-identical payloads (v2 patch is identity-only: "
                           "memory_id gains session_position; memory_text/order/fit unchanged; v2 code proves "
                           "payload_identical_to_v1). cache_repr carries no memory IDs, so the rebuild is "
                           "consistent with both; determined by the v2 payload-identity proof + bit-exact G1.",
        "seeds": {"LSA32": LSA_SEED, "SVD96": SVD_SEED},
        "n_archives": 470,
        "G1_total_differing_bits": tot_diff,
        "G1_total_bits": tot_bits,
        "G1_max_abs_diff": max_abs,
        "G1_clean_archives": clean,
        "G1_pass": bool(g1_pass),
        "G2_recomputed": {k: round(v * 100, 4) for k, v in g2.items()},
        "G2_targets_pct": {"qscale_hit10": 88.5106, "sym_hit10_det": 86.383,
                           "sym_hit10_exp": 86.0773, "qscale_fr3_approx": 54.27},
        "G2_pass": bool(g2_pass),
        "gold_rebuilt_match_all": True,
        "gate_wall_time_s": time.time() - t0,
    }
    with open(os.path.join(HERE, "FIDELITY_GATE.json"), "w", encoding="utf-8") as f:
        json.dump(gate, f, indent=2)
    print("G1 diffbits=%d/%d maxabs=%.3e clean=%d/470 pass=%s"
          % (tot_diff, tot_bits, max_abs, clean, g1_pass), flush=True)
    print("G2 " + json.dumps(gate["G2_recomputed"]), flush=True)
    print("GATE", "PASS" if (g1_pass and g2_pass) else "FAIL", flush=True)
    if not (g1_pass and g2_pass):
        raise SystemExit("FIDELITY GATE FAILED -- STOPPING before any ablation number.")
    phase_ablate(done, time.time())


def phase_ablate(results, t_gate_end):
    # Called only after FIDELITY_GATE.json has been written with G1+G2 PASS.
    # Uses the in-memory single-pass results; no second compute.
    gate = json.load(open(os.path.join(HERE, "FIDELITY_GATE.json"), encoding="utf-8"))
    assert gate.get("G1_pass") and gate.get("G2_pass"), \
        "refusing to compute ablation numbers on a failing gate"
    t0 = t_gate_end
    order = sorted(results)

    metrics = {}
    with open(os.path.join(HERE, "per_query.jsonl"), "w", encoding="utf-8") as f:
        for q in order:
            r = results[q]
            for arm in ARMS:
                for sc in SCORERS:
                    m = r["arms"][arm]["metrics"][sc]
                    metrics.setdefault((arm, sc), {}).setdefault("hit10", []).append(m["hit10"])
                    metrics[(arm, sc)].setdefault("fr3", []).append(m["fr3"])
                    metrics[(arm, sc)].setdefault("hit3", []).append(m["hit3"])
                    metrics[(arm, sc)].setdefault("exp_hit10", []).append(m["exp_hit10"])
                    f.write(json.dumps({
                        "label": LABEL, "question_id": q, "archive_id": q,
                        "arm": arm, "scorer": sc, "N": r["N"], "gold": r["gold"],
                        "top10": m["top10"], "top3": m["top3"],
                        "hit10": m["hit10"], "fr3": m["fr3"], "hit3": m["hit3"],
                        "exp_hit10": m["exp_hit10"]}) + "\n")
    for k in metrics:
        for mk in metrics[k]:
            metrics[k][mk] = np.asarray(metrics[k][mk], dtype=np.float64)

    # Contrasts: each arm MINUS FULL, paired archive-clustered bootstrap.
    rng = np.random.default_rng(BOOT_SEED)
    boot_idx = rng.integers(0, 470, size=(N_BOOT, 470))
    summary, contrasts = {}, []
    for arm in ARMS:
        for sc in SCORERS:
            row = {}
            for mk in ("hit10", "fr3", "hit3", "exp_hit10"):
                row[mk] = float(metrics[(arm, sc)][mk].mean())
            summary[f"{arm}/{sc}"] = row
    for arm in ("NO_LSA", "NO_CHAR", "WORD_ONLY"):
        for sc in SCORERS:
            for mk in ("hit10", "fr3", "hit3", "exp_hit10"):
                d = metrics[(arm, sc)][mk] - metrics[("FULL", sc)][mk]
                est = float(d.mean())
                boots = d[boot_idx].mean(axis=1)
                lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
                contrasts.append({"arm": arm, "scorer": sc, "metric": mk,
                                  "est_pp": est * 100, "ci_lo_pp": lo * 100,
                                  "ci_hi_pp": hi * 100,
                                  "ci_includes_zero": bool(lo <= 0 <= hi),
                                  "n_boot": N_BOOT, "seed": BOOT_SEED})
    cost = {}
    for arm in ARMS:
        zf = [results[q]["z_shapes"][arm][1] for q in order]
        bt = [results[q]["arm_times"][arm] for q in order]
        cost[arm] = {"Z_features_min": int(min(zf)), "Z_features_mean": float(np.mean(zf)),
                     "Z_features_max": int(max(zf)),
                     "build_time_s_mean": float(np.mean(bt)),
                     "build_time_s_total": float(sum(bt)),
                     "payload_bytes_per_doc": int(results[order[0]]["arms"][arm]["payload_bytes_per_doc"])}
    res = {"label": LABEL, "n_queries": 470, "n_archives": 470,
           "arms": list(ARMS), "scorers": list(SCORERS),
           "summary_means_pct": {k: {mk: v * 100 for mk, v in row.items()}
                                 for k, row in summary.items()},
           "contrasts_vs_FULL_pp": contrasts,
           "bootstrap": {"method": "paired archive-clustered (cluster==question for LME)",
                         "reps": N_BOOT, "seed": BOOT_SEED,
                         "caveat": "assumes archive independence; LME questions may share source "
                                   "sessions, so CIs are descriptive, NOT confirmatory"},
           "cost": cost,
           "seeds": {"LSA32": LSA_SEED, "SVD96": SVD_SEED},
           "ablate_wall_time_s": time.time() - t0}
    with open(os.path.join(HERE, "RESULTS.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res["summary_means_pct"], indent=1), flush=True)
    for c in contrasts:
        if c["metric"] in ("hit10", "fr3"):
            print("%s %s %s: %+.2fpp [%.2f, %+.2f] zero=%s"
                  % (c["arm"], c["scorer"], c["metric"], c["est_pp"],
                     c["ci_lo_pp"], c["ci_hi_pp"], c["ci_includes_zero"]), flush=True)


def main():
    phase_gate()


if __name__ == "__main__":
    main()
