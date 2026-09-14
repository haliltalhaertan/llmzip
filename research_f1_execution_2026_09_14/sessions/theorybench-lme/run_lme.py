#!/usr/bin/env python3
"""TheoryBench-LME runner: gate (SIGN96 MC-20 + centered FLOAT96 MC-20 vs stored arrays)
then Model-H LOW48/HIGH48/FULL96 positive-scale interventions on LongMemEval.

Read-only sources under /mnt/c/... ; writes only inside this workspace.
Conventions mirror the frozen producers verbatim (see PRE_RUN.json):
  rh(d,p) = lexsort((p,d)); rf(s,p) = lexsort((p,-scores));
  cos(C,q) = (C@q)/(||C||*||q||); zero norm -> RuntimeError (T4C2 convention);
  seed(lex,trial) = 5_100_000 + lex*100_000 + trial*100, priority = rng(seed+99).random(N);
  lex = rank over ALL 500 cleaned questions; K=3, NT=20, TOL=1e-12.
"""
import os as _os
for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")

import csv
import hashlib
import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work")
LLM = Path("/mnt/c/Users/MDP/dev/llmzip")
K = 3
NT = 20
TOL = 1e-12
DIM = 96
T_GRID = [0.25, 0.5, 1.0, 2.0, 4.0]
MC_TS = {0.25, 1.0, 4.0}
GROUPS = ("LOW48", "HIGH48", "FULL96")
BOOT_B = 2000
BOOT_SEED = 20260913
NATIVE_ANCHOR = 0.5419751773049645
CKPT = HERE / "checkpoints"
RECEIPTS = HERE / "receipts"


def log(msg):
    print(msg, flush=True)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def stable_archive_seed(lex, trial=0):
    return 5_100_000 + lex * 100_000 + trial * 100


def priorities(lex, n):
    return [np.random.default_rng(stable_archive_seed(lex, t) + 99).random(n) for t in range(NT)]


def rank_hamming(d, p):
    return np.lexsort((p, np.asarray(d)))


def rank_float(s, p):
    return np.lexsort((p, -np.asarray(s, dtype=np.float64)))


def cosine_scores(C, q):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if qn <= 0 or np.any(dn <= 0):
        raise RuntimeError("[BUG] zero centered vector norm in cosine")
    return (C @ q) / (dn * qn)


def frac_recall(order_topk, gold):
    gset = set(map(int, np.asarray(gold).ravel()))
    return len(set(map(int, order_topk)) & gset) / len(gset)


def measured_sign_mc(d, gold, pris):
    tot = 0.0
    for p in pris:
        tot += frac_recall(rank_hamming(d, p)[:K], gold)
    return tot / len(pris)


def measured_float_mc(s, gold, pris):
    tot = 0.0
    for p in pris:
        tot += frac_recall(rank_float(s, p)[:K], gold)
    return tot / len(pris)


def exact_expectation(d_or_s, gold, is_float):
    """Tie-bucket expectation under uniform priorities (shared gold).
    d_or_s: int distances (sign) or float64 scores (float, higher=closer)."""
    if is_float:
        v = np.asarray(d_or_s, dtype=np.float64)
        g = np.asarray(gold).ravel()
        tot = 0.0
        for gg in g:
            sg = v[int(gg)]
            s = int(np.count_nonzero(v > sg))
            tincl = int(np.count_nonzero(v == sg))
            if s >= K:
                p = 0.0
            elif s + tincl <= K:
                p = 1.0
            else:
                p = (K - s) / tincl
            tot += p
        return tot / len(g)
    d = np.asarray(d_or_s)
    g = np.asarray(gold).ravel()
    tot = 0.0
    for gg in g:
        dg = d[int(gg)]
        s = int(np.count_nonzero(d < dg))
        tincl = int(np.count_nonzero(d == dg))
        if s >= K:
            p = 0.0
        elif s + tincl <= K:
            p = 1.0
        else:
            p = (K - s) / tincl
        tot += p
    return tot / len(g)


def load_all():
    t0 = time.time()
    data = json.loads((SRC / "drive" / "longmemeval_s_cleaned.json").read_bytes())
    allq = sorted(str(x["question_id"]) for x in data)
    assert len(allq) == 500, len(allq)
    lex = {q: i for i, q in enumerate(allq)}
    del data
    qtype = {}
    with open(SRC / "drive" / "t4c3" / "V52_T4C3_question_level.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            qtype[row["question_id"]] = row["question_type"]
    t4c2 = {}
    with open(LLM / "docs" / "v52" / "task4c2" / "V52_T4C2_question_level.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t4c2[row["question_id"]] = (float(row["sign96_centered_fractional_r3"]),
                                        float(row["float96_centered_fractional_r3"]))
    stored_pilot = json.load(open(SRC / "pilots" / "axis_attack_2026-09-12" / "pilot_results.json"))[
        "per_question_native_FR"]
    assert len(stored_pilot) == 470, len(stored_pilot)
    race = json.load(open(SRC / "race_2026-09-13" / "rb2" / "race_sign_details.json"))
    race_fr = dict(zip(race["LME"]["qids"], race["LME"]["arms"]["NATIVE96"]["fr"]))
    race_model = dict(zip(race["LME"]["qids"], race["LME"]["arms"]["NATIVE96"]["model"]))
    pkls = sorted((SRC / "regen" / "lme" / "cache_repr").glob("*.pkl"))
    assert len(pkls) == 470, len(pkls)
    CKPT.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    arch, manifest = [], {}
    for p in pkls:
        raw = p.read_bytes()
        manifest[p.name] = sha256_bytes(raw)
        o = pickle.loads(raw)
        qid = o["question_id"]
        arch.append({"qid": qid, "lex": lex[qid],
                     "C": np.asarray(o["C"], dtype=np.float64),
                     "qC": np.asarray(o["qC"], dtype=np.float64).reshape(-1),
                     "gold": np.asarray(o["gold"]).ravel(),
                     "qtype": qtype.get(qid, "unknown"),
                     "stored_pilot": float(stored_pilot[qid]),
                     "stored_t4c2_sign": t4c2[qid][0], "stored_t4c2_float": t4c2[qid][1],
                     "stored_race_fr": float(race_fr[qid]),
                     "stored_race_model": float(race_model[qid])})
    (CKPT / "pkl_manifest.json").write_text(json.dumps(manifest, indent=1))
    log(f"loaded {len(arch)} archives ({time.time()-t0:.1f}s); pkl manifest saved")
    return arch


def run_gate(arch):
    """Recompute ORIGINAL native SIGN96 MC-20 + centered FLOAT96 MC-20; compare per-QA."""
    sign_mc, float_mc, sign_ex, float_ex = [], [], [], []
    for a in arch:
        C, qC, g = a["C"], a["qC"], a["gold"]
        n = C.shape[0]
        pris = priorities(a["lex"], n)
        d = np.count_nonzero((C >= 0) != (qC >= 0)[None, :], axis=1).astype(np.int16)
        s = cosine_scores(C, qC)
        sign_mc.append(measured_sign_mc(d, g, pris))
        float_mc.append(measured_float_mc(s, g, pris))
        sign_ex.append(exact_expectation(d, g, False))
        float_ex.append(exact_expectation(s, g, True))
    sign_mc = np.array(sign_mc)
    float_mc = np.array(float_mc)
    sign_ex = np.array(sign_ex)
    float_ex = np.array(float_ex)
    stored = {
        "pilot": np.array([a["stored_pilot"] for a in arch]),
        "t4c2_sign": np.array([a["stored_t4c2_sign"] for a in arch]),
        "race_fr": np.array([a["stored_race_fr"] for a in arch]),
        "t4c2_float": np.array([a["stored_t4c2_float"] for a in arch]),
        "race_model": np.array([a["stored_race_model"] for a in arch]),
    }
    checks = {}
    for name, arr in (("native_mc_vs_pilot", stored["pilot"]),
                      ("native_mc_vs_t4c2_sign", stored["t4c2_sign"]),
                      ("native_mc_vs_race_fr", stored["race_fr"])):
        diff = np.abs(sign_mc - arr)
        checks[name] = {"max_abs_diff": float(diff.max()), "mean_recomp": float(sign_mc.mean()),
                        "mean_stored": float(arr.mean()), "pass": bool(diff.max() <= TOL)}
    diff = np.abs(float_mc - stored["t4c2_float"])
    checks["float_mc_vs_t4c2_float"] = {"max_abs_diff": float(diff.max()),
                                        "mean_recomp": float(float_mc.mean()),
                                        "mean_stored": float(stored["t4c2_float"].mean()),
                                        "pass": bool(diff.max() <= TOL)}
    diff = np.abs(sign_ex - stored["race_model"])
    checks["sign_exact_vs_race_model"] = {"max_abs_diff": float(diff.max()),
                                          "mean_exact": float(sign_ex.mean()),
                                          "mean_stored_model": float(stored["race_model"].mean()),
                                          "pass": bool(diff.max() <= TOL)}
    gate_pass = all(v["pass"] for v in checks.values())
    gate = {"n_expected": 470, "n_evaluated": len(arch), "n_unresolved": 0, "n_excluded": 0,
            "native_anchor": NATIVE_ANCHOR, "native_mc_mean": float(sign_mc.mean()),
            "float_mc_mean": float(float_mc.mean()),
            "float_t4c2_mean": float(stored["t4c2_float"].mean()),
            "sign_exact_mean": float(sign_ex.mean()), "float_exact_mean": float(float_ex.mean()),
            "checks": checks, "pass": bool(gate_pass), "tolerance": TOL}
    (HERE / "gate.json").write_text(json.dumps(gate, indent=2))
    for name, c in checks.items():
        log(f"GATE {name}: max_abs_diff={c['max_abs_diff']:.3e} -> {'PASS' if c['pass'] else 'FAIL'}")
    log(f"GATE overall: {'PASS' if gate_pass else 'ABORT'} "
        f"(native_mc={sign_mc.mean()!r} anchor={NATIVE_ANCHOR!r}; "
        f"float_mc={float_mc.mean()!r} stored={stored['t4c2_float'].mean()!r})")
    base = {"sign_mc": sign_mc, "float_mc": float_mc, "sign_ex": sign_ex, "float_ex": float_ex}
    return gate_pass, base


def group_indices(q):
    order = sorted(range(DIM), key=lambda j: (abs(float(q[j])), j))
    return np.array(order[:48], dtype=int), np.array(order[48:], dtype=int)


def run_interventions(arch, base):
    t0 = time.time()
    groups_map = {}
    rows = []
    sign_identity_max, float_identity_max, float_mc_identity_max = 0.0, 0.0, 0.0
    sign_mismatch_total = 0
    full_score_maxdiff, full_exact_changed = 0.0, 0
    n = len(arch)
    for i, a in enumerate(arch):
        C, q, g = a["C"], a["qC"], a["gold"]
        N = C.shape[0]
        pris = priorities(a["lex"], N)
        low, high = group_indices(q)
        groups_map[a["qid"]] = {"LOW48": [int(x) for x in low], "HIGH48": [int(x) for x in high]}
        q2 = float(np.sum(q ** 2))
        qconc = float(np.sum(q ** 4) / (q2 ** 2)) if q2 > 0 else float("nan")
        d0 = np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1).astype(np.int16)
        s0 = cosine_scores(C, q)
        for grp_name, cols in (("LOW48", low), ("HIGH48", high), ("FULL96", np.arange(DIM))):
            comp = np.array([j for j in range(DIM) if j not in set(cols.tolist())], dtype=int)
            rms_g = float(np.sqrt(np.mean(C[:, cols] ** 2)))
            rms_c = float(np.sqrt(np.mean(C[:, comp] ** 2))) if len(comp) else float("nan")
            for t in T_GRID:
                Ct = C.copy()
                qt = q.copy()
                Ct[:, cols] = Ct[:, cols] * t
                qt[cols] = qt[cols] * t
                d = np.count_nonzero((Ct >= 0) != (qt >= 0)[None, :], axis=1).astype(np.int16)
                if not np.array_equal(d, d0):
                    sign_mismatch_total += int(np.count_nonzero(d != d0))
                s = cosine_scores(Ct, qt)
                se = exact_expectation(d, g, False)
                fe = exact_expectation(s, g, True)
                if t in MC_TS:
                    sm = measured_sign_mc(d, g, pris)
                    fm = measured_float_mc(s, g, pris)
                else:
                    sm, fm = None, None
                if t == 1.0:
                    sign_identity_max = max(sign_identity_max, abs(se - base["sign_ex"][i]))
                    float_identity_max = max(float_identity_max, abs(fe - base["float_ex"][i]))
                    if sm is not None:
                        float_mc_identity_max = max(float_mc_identity_max, abs(fm - base["float_mc"][i]))
                if grp_name == "FULL96" and t == 4.0:
                    full_score_maxdiff = max(full_score_maxdiff, float(np.max(np.abs(s - s0))))
                    if abs(fe - base["float_ex"][i]) > 0:
                        full_exact_changed += 1
                rows.append({"archive_id": a["qid"], "qa_id": a["qid"], "lex": a["lex"],
                             "N_archive": N, "gold_count": int(np.asarray(g).size),
                             "section": a["qtype"], "group": grp_name, "t": t,
                             "sign_exact": float(se), "float_exact": float(fe),
                             "delta_exact": float(se - fe),
                             "sign_mc20": (None if sm is None else float(sm)),
                             "float_mc20": (None if fm is None else float(fm)),
                             "delta_mc20": (None if sm is None else float(sm - fm)),
                             "qconc": qconc, "doc_rms_group": rms_g,
                             "doc_rms_complement": rms_c})
        if (i + 1) % 50 == 0 or (i + 1) == n:
            (CKPT / f"ckpt_{i+1:03d}.json").write_text(json.dumps(
                {"done": i + 1, "rows": len(rows), "elapsed_s": time.time() - t0}))
            log(f"  interventions {i+1}/{n} rows={len(rows)} ({time.time()-t0:.0f}s)")
    assert n == 470, n
    assert len(rows) == 470 * len(GROUPS) * len(T_GRID), len(rows)
    with open(HERE / "per_query.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    cols = ["archive_id", "qa_id", "lex", "N_archive", "gold_count", "section", "group", "t",
            "sign_exact", "float_exact", "delta_exact", "sign_mc20", "float_mc20",
            "delta_mc20", "qconc", "doc_rms_group", "doc_rms_complement"]
    with open(HERE / "per_query.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in cols})
    (HERE / "groups.json").write_text(json.dumps(groups_map, indent=1))
    diag = {"t1_sign_exact_maxdiff": sign_identity_max, "t1_float_exact_maxdiff": float_identity_max,
            "t1_float_mc_maxdiff": float_mc_identity_max,
            "sign_byte_mismatches_total": sign_mismatch_total,
            "full96_t4_score_maxabsdiff": full_score_maxdiff,
            "full96_t4_float_exact_changed_qas": full_exact_changed}
    log(f"DIAG t1 identity: sign={sign_identity_max:.3e} float={float_identity_max:.3e} "
        f"float_mc={float_mc_identity_max:.3e}")
    log(f"DIAG sign invariance mismatches={sign_mismatch_total}; "
        f"FULL96 t=4 score maxabsdiff={full_score_maxdiff:.3e} changed_qas={full_exact_changed}")
    return rows, diag


def paired_bootstrap(contrast, B=BOOT_B, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    n = len(contrast)
    reps = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        reps[b] = float(contrast[idx].mean())
    return float(contrast.mean()), float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5)), reps


def summarize(rows, base, diag):
    table = {}
    for grp in GROUPS:
        for t in T_GRID:
            sel = [r for r in rows if r["group"] == grp and r["t"] == t]
            se = np.array([r["sign_exact"] for r in sel])
            fe = np.array([r["float_exact"] for r in sel])
            de = se - fe
            mcs = [r["sign_mc20"] for r in sel if r["sign_mc20"] is not None]
            mcf = [r["float_mc20"] for r in sel if r["float_mc20"] is not None]
            table[f"{grp}@t={t}"] = {
                "n": len(sel), "sign_exact_mean": float(se.mean()),
                "float_exact_mean": float(fe.mean()), "delta_exact_mean": float(de.mean()),
                "sign_mc20_mean": (None if not mcs else float(np.mean(mcs))),
                "float_mc20_mean": (None if not mcf else float(np.mean(mcf)))}
    prim = {}
    for grp in GROUPS:
        lo = np.array([r["delta_exact"] for r in rows if r["group"] == grp and r["t"] == 0.25])
        hi = np.array([r["delta_exact"] for r in rows if r["group"] == grp and r["t"] == 4.0])
        contrast = hi - lo
        m, clo, chi, _ = paired_bootstrap(contrast)
        prim[grp] = {"endpoint_contrast_mean": m, "ci95": [clo, chi],
                     "n_clusters": 470, "note": "470 single-QA archives; cluster bootstrap = question bootstrap"}
    dec = {}
    for grp in GROUPS:
        per_q = {}
        for r in rows:
            if r["group"] == grp:
                per_q.setdefault(r["archive_id"], {})[r["t"]] = r["delta_exact"]
        ts = sorted(T_GRID)
        nadj = sum(1 for v in per_q.values()
                   if any(v[ts[j + 1]] < v[ts[j]] for j in range(len(ts) - 1)))
        dec[grp] = {"n_qas": len(per_q),
                    "frac_any_decreasing_adjacent": nadj / len(per_q), "n_any_decreasing": nadj}
    summary = {"n_qa": 470, "n_rows": len(rows), "t_grid": T_GRID, "groups": list(GROUPS),
               "baseline": {"native_mc_mean": float(base["sign_mc"].mean()),
                            "float_mc_mean": float(base["float_mc"].mean()),
                            "sign_exact_mean": float(base["sign_ex"].mean()),
                            "float_exact_mean": float(base["float_ex"].mean())},
               "curve": table, "primary_endpoint_contrast": prim,
               "monotonicity": dec, "diagnostics": diag,
               "bootstrap": {"B": BOOT_B, "seed": BOOT_SEED, "unit": "whole archives"}}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2))
    log("PRIMARY LOW48 contrast mean[delta(t=4)-delta(t=.25)] = "
        f"{prim['LOW48']['endpoint_contrast_mean']:+.6f} "
        f"95%CI [{prim['LOW48']['ci95'][0]:+.6f},{prim['LOW48']['ci95'][1]:+.6f}]")
    for grp in GROUPS:
        log(f"  {grp}: contrast={prim[grp]['endpoint_contrast_mean']:+.6f} "
            f"CI=[{prim[grp]['ci95'][0]:+.6f},{prim[grp]['ci95'][1]:+.6f}] "
            f"decreasing_frac={dec[grp]['frac_any_decreasing_adjacent']:.4f}")
    return summary


def main():
    t0 = time.time()
    arch = load_all()
    ok, base = run_gate(arch)
    if not ok:
        log("GATE FAILED — aborting before interventions (no per_query/summary written)")
        sys.exit(1)
    rows, diag = run_interventions(arch, base)
    summarize(rows, base, diag)
    log(f"DONE {len(rows)} rows in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
