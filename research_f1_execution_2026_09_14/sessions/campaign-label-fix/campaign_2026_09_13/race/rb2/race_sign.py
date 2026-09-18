#!/usr/bin/env python3
"""RACE-2: SIGN-ARM family race runner (DRAFT v2, LOCAL BUILD + SMOKE).

Read-only data mount; writes only to the runner output dir.
numpy + stdlib only. Single constants block below; everything else derives from it.

Data root resolution (no drive-letter or mount literals anywhere in this file):
  env RB2_DATA_ROOT, else a relative "llmzip-work" resolved from the cwd.
Output dir: env RB2_OUT_DIR, else "/tmp/rb2".
"""
import os as _os
for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")

import csv
import hashlib
import json
import pickle
import platform
import re
import sys
import time
from pathlib import Path

import numpy as np

# ================= SINGLE CONSTANTS BLOCK =================
K = 3                       # top-K for fractional evidence R@K
NT = 20                     # frozen tie trials per question
TOL = 1e-12                 # W/T/L tolerance and gate tolerance
DIM = 96                    # sign-code width
LME_ANCHOR = 0.5419751773049645        # LME-470 NATIVE SIGN96 aggregate (CSV-canonical)
LOCOMO_ANCHOR = 0.23654714666441054   # LoCoMo-1535 NATIVE SIGN96 aggregate
GATE_TOP48 = 0.34949468085106383      # LME pilot spot: TOP48, per-archive construction
GATE_RAND48 = 0.47292553191489356     # LME pilot spot: RAND48, single global seed-12000 subset
GATE_BOT48 = 0.4284574468085106       # LME pilot spot: BOT48, per-archive construction
LOCOMO_R2C_TOP48 = 0.13182630371268042
LOCOMO_R2C_BOT48 = 0.18112226499522918
LOCOMO_R2C_RAND48 = (0.15912137829171744, 0.15982848141724365, 0.16834543640770885)
WIDTHS = (48, 64, 80)                 # race bit-widths
WIDTH_IDX = {48: 0, 64: 1, 80: 2}     # width_idx for the 93000-series panel literals
RAND_BASE = 93000                     # panel seed literal base: 93000 + 10*width_idx + j
N_PANEL_SEEDS = 10                    # j = 0..9
GATE_RAND48_SEED = 12000              # pilot-definition RAND48 seed (LME gate only)
LOCOMO_PILOT_RAND_SEEDS = (12000, 12001, 12002)  # R2C 3-seed comparison (LoCoMo, informational gate)
BOOT_B = 5000                         # bootstrap resamples (machinery deferred; literal recorded)
BOOT_SEED = 94301                     # bootstrap seed (machinery deferred; literal recorded)
CONTROL_MARGIN_PP = 5.0               # TOP-control prespecified margin (loses to random-mean by >=5pp)
DATA_ROOT = Path(_os.environ.get("RB2_DATA_ROOT", "llmzip-work")).expanduser()
OUT_DIR = Path(_os.environ.get("RB2_OUT_DIR", "/tmp/rb2")).expanduser()
# ================= END CONSTANTS =================

SMOKE = []  # smoke log lines


def log(msg):
    SMOKE.append(msg)
    print(msg, flush=True)


def rand_panel_seed(width, j):
    return RAND_BASE + 10 * WIDTH_IDX[width] + j


def tie_seed(idx_key, t):
    """Frozen tie-draw seed. LME: idx_key = question lex rank (0..499 over all 500
    cleaned questions). LoCoMo: idx_key = conversation ordinal ci (stable_archive_seed+99)."""
    return 5_100_000 + idx_key * 100_000 + t * 100 + 99


def trial_priorities(idx_key, n):
    return [np.random.default_rng(tie_seed(idx_key, t)).random(n) for t in range(NT)]


def linspace_positions(k, dim=DIM):
    """Repaired rank-linspace positions: round-half-up of linspace(0, dim-1, k).
    (For k in {48,64,80}, dim=96 no fractional part is exactly 0.5, so every
    rounding convention agrees; the choice is documented, not load-bearing.)"""
    return np.floor(np.linspace(0, dim - 1, k) + 0.5).astype(int)


def per_archive_subsets(var, k, dim=DIM):
    """R2C/pilot convention: order_desc = argsort(var, stable)[::-1];
    TOP = order_desc[:k]; BOT = order_desc[-k:]; SPREAD = order_desc[linspace].
    Asserts eff_k == k (no sentinels, in-range). Returns SORTED index arrays
    (sort order is irrelevant to Hamming subsets; sorted form is canonical)."""
    var = np.asarray(var, dtype=float)
    assert var.shape == (dim,), ("variance shape", var.shape)
    order_desc = np.argsort(var, kind="stable")[::-1]
    assert order_desc.shape == (dim,)
    parts = {
        "TOP": order_desc[:k],
        "BOT": order_desc[-k:],
        "SPREAD": order_desc[linspace_positions(k, dim)],
    }
    out = {}
    for name, s in parts.items():
        u = np.unique(s)
        assert len(u) == k, ("eff_k != k", name, k, len(u))
        assert int(s.min()) >= 0 and int(s.max()) < dim, ("index range", name)
        out[name] = np.sort(s)
    return out


def global_spread_subset(var_list, k, dim=DIM):
    """Sensitivity variant: axes ranked by mean per-archive rank (rank 0 = top
    variance in that archive), then rank-linspace SPREAD on the global order.
    Same subset applied to every archive of the benchmark."""
    m = len(var_list)
    ranks = np.empty((m, dim), dtype=float)
    for i, var in enumerate(var_list):
        od = np.argsort(np.asarray(var, dtype=float), kind="stable")[::-1]
        r = np.empty(dim, dtype=int)
        r[od] = np.arange(dim)
        ranks[i] = r
    mean_rank = ranks.mean(axis=0)
    gorder = np.argsort(mean_rank, kind="stable")
    spread = gorder[linspace_positions(k, dim)]
    assert len(np.unique(spread)) == k, ("global eff_k != k", k)
    return np.sort(spread), mean_rank


def random_subset(seed, k, dim=DIM):
    s = np.sort(np.random.default_rng(seed).choice(dim, k, replace=False))
    assert len(np.unique(s)) == k, ("random eff_k != k", seed, k)
    return s


def measured_fr(d, gold, pris, k=K):
    """Frozen scheme: per trial, order = lexsort((priority, distance)), top-k
    fractional gold recall; mean over the NT trials."""
    d = np.asarray(d)
    gset = set(map(int, np.asarray(gold).ravel()))
    ng = len(gset)
    tot = 0.0
    trials = []
    for p in pris:
        order = np.lexsort((p, d))
        f = len(set(map(int, order[:k])) & gset) / ng
        trials.append(f)
        tot += f
    return tot / len(pris), trials


def model_fr(d, gold, k=K):
    """MATH-1 exact identity P(top-k) = f(S, T): per gold with S strictly-closer
    and T tied docs, P = 0 if S>=k; 1 if S+T<=k; else (k-S)/T; mean over golds."""
    d = np.asarray(d)
    g = np.asarray(gold).ravel()
    tot = 0.0
    for gg in g:
        dg = d[int(gg)]
        s = int(np.count_nonzero(d < dg))
        t = int(np.count_nonzero(d == dg))
        if s >= k:
            p = 0.0
        elif s + t <= k:
            p = 1.0
        else:
            p = (k - s) / t
        tot += p
    return tot / len(g)


def pearson_r(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


class GateAbort(SystemExit):
    pass


def gate_or_abort(name, recomputed, expected, tol=TOL):
    diff = recomputed - expected
    ok = abs(diff) <= tol
    log(f"GATE {name}: recomputed={recomputed!r} expected={expected!r} diff={diff!r} -> {'PASS' if ok else 'ABORT'}")
    if not ok:
        raise GateAbort(f"gate {name} breached: diff={diff!r} > tol={tol}")
    return diff


# ---------- loaders (same loaders/protocol as pilots) ----------
def load_lme(root):
    data = json.load(open(root / "drive" / "longmemeval_s_cleaned.json"))
    allq = sorted(str(x["question_id"]) for x in data)
    assert len(allq) == 500, len(allq)
    lex = {q: i for i, q in enumerate(allq)}
    del data
    meta = {}
    with open(root / "drive" / "t4c3" / "V52_T4C3_question_level.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            meta[row["question_id"]] = row
    stored = json.load(open(root / "pilots" / "axis_attack_2026-09-12" / "pilot_results.json"))[
        "per_question_native_FR"
    ]
    assert len(stored) == 470, len(stored)
    pkls = sorted((root / "regen" / "lme" / "cache_repr").glob("*.pkl"))
    assert len(pkls) == 470, len(pkls)
    return lex, meta, stored, pkls


def norm_evidence(x):
    if x is None:
        return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def load_audit_corrections(audit_dir):
    corrections = {}
    for f in sorted(audit_dir.glob("errors_conv_*.json")):
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            qid = r.get("question_id")
            if not qid:
                continue
            corrections[str(qid)] = {
                "error_type": r.get("error_type"),
                "has_correct_evidence": "correct_evidence" in r,
                "correct_evidence": norm_evidence(r.get("correct_evidence")),
                "correct_answer": r.get("correct_answer"),
            }
    return corrections


def evidence_rows(ids, id_to_row):
    out = []
    for x in ids:
        if x in id_to_row:
            out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))


def load_locomo(root):
    raw = json.loads((root / "drive" / "locomo10.json").read_text(encoding="utf-8"))
    corr = load_audit_corrections(root / "drive" / "audit_layer")
    convs = []
    for idx, item in enumerate(raw):
        qas = []
        for qi, q in enumerate(item.get("qa", []) or []):
            cat = int(q.get("category")) if q.get("category") is not None else None
            if cat not in (1, 2, 3, 4):
                continue
            qid = q.get("question_id") or f"locomo_{idx}_qa{qi}"
            z = corr.get(str(qid))
            if z:
                ce = (
                    list(z["correct_evidence"])
                    if z.get("has_correct_evidence", False)
                    else list(norm_evidence(q.get("evidence")))
                )
            else:
                ce = list(norm_evidence(q.get("evidence")))
            qas.append(
                {
                    "question_id": str(qid),
                    "category": cat,
                    "raw_evidence": norm_evidence(q.get("evidence")),
                    "correct_evidence": ce,
                }
            )
        convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
    reps = []
    for ci in range(10):
        d = pickle.load(open(root / "regen" / "locomo" / f"locomo_{ci}.pkl", "rb"))
        assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
        raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
        pkl_ids = [q["question_id"] for q in d["qas"]]
        assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
        assert d["QC"].shape[0] == len(d["qas"]), (ci, d["QC"].shape)
        reps.append(d)
    return convs, reps


def sign_dist_matrix(C, QC, subset=None):
    if subset is None:
        D = C >= 0
        Qm = QC >= 0
    else:
        D = C[:, subset] >= 0
        Qm = QC[:, subset] >= 0
    return np.count_nonzero(Qm[:, None, :] != D[None, :, :], axis=2).astype(np.int16)


# ---------- arm evaluation ----------
def arm_labels():
    labels = ["NATIVE96"]
    for k in WIDTHS:
        for fam in ("TOP", "BOT", "SPREAD"):
            labels.append(f"{fam}{k}")
    labels.append("SPREAD64_GLOBAL")
    for k in WIDTHS:
        for j in range(N_PANEL_SEEDS):
            labels.append(f"RAND{k}_s{j}")
    return labels


def summarize_arm(fr, model, native_fr, eff_k, construction, seed=None):
    fr = np.asarray(fr, dtype=float)
    model = np.asarray(model, dtype=float)
    gap = fr - np.asarray(native_fr, dtype=float)
    w = int(np.sum(gap > TOL))
    t = int(np.sum(np.abs(gap) <= TOL))
    l = int(np.sum(gap < -TOL))
    resid = fr - model
    return {
        "fr": [float(v) for v in fr],
        "model": [float(v) for v in model],
        "mean": float(fr.mean()),
        "median": float(np.median(fr)),
        "model_mean": float(model.mean()),
        "model_mae": float(np.mean(np.abs(resid))),
        "model_r": pearson_r(fr, model),
        "W": w,
        "T": t,
        "L": l,
        "tie_frac": float(t / len(fr)),
        "gap_mean": float(gap.mean()),
        "gap_median": float(np.median(gap)),
        "eff_k": eff_k,
        "construction": construction,
        "seed": seed,
    }


def run_lme(root):
    lex, meta, stored, pkls = load_lme(root)
    log(f"LME: 470 archives; lex over {len(lex)} cleaned questions")
    arch = []
    for p in pkls:
        o = pickle.loads(p.read_bytes())
        qid = o["question_id"]
        arch.append(
            {
                "qid": qid,
                "lex": lex[qid],
                "C": o["C"],
                "qC": o["qC"],
                "gold": np.asarray(o["gold"]).ravel(),
                "qtype": meta[qid]["question_type"],
                "stored_nat": float(stored[qid]),
            }
        )
    qids = [a["qid"] for a in arch]
    var_list = [a["C"].var(axis=0) for a in arch]
    subsets = {}  # (qid, label) -> array or None for native
    gspread, gmean_rank = global_spread_subset(var_list, 64)
    log(f"LME SPREAD64_GLOBAL subset head: {gspread[:8].tolist()} ... (k=64, benchmark-global)")
    rand_subs = {}
    for k in WIDTHS:
        for j in range(N_PANEL_SEEDS):
            rand_subs[(k, rand_panel_seed(k, j))] = random_subset(rand_panel_seed(k, j), k)
    gate_rand = random_subset(GATE_RAND48_SEED, 48)
    per_arch_sub = [per_archive_subsets(v, k) for v in var_list for k in WIDTHS]
    log(f"LME construction asserts: {len(arch)} archives x {len(WIDTHS)} widths x 3 fams = "
        f"{len(per_arch_sub)} per-archive subset triples, all eff_k==k")
    fr = {lab: [] for lab in arm_labels()}
    mo = {lab: [] for lab in arm_labels()}
    gate_fr_rand12000 = []
    demo = None
    for i, a in enumerate(arch):
        C, qC, g = a["C"], a["qC"], a["gold"]
        n = C.shape[0]
        D0 = C >= 0
        Q0 = qC >= 0
        pris = trial_priorities(a["lex"], n)
        dnat = np.count_nonzero(D0 != Q0[None, :], axis=1).astype(np.int16)
        nfr, ntrials = measured_fr(dnat, g, pris)
        fr["NATIVE96"].append(nfr)
        mo["NATIVE96"].append(model_fr(dnat, g))
        if i == 0:
            demo = {"qid": a["qid"], "lex": a["lex"], "N": n, "native_trials": ntrials,
                    "native_mean": nfr, "seeds": [tie_seed(a["lex"], t) for t in range(NT)]}
        for wi, k in enumerate(WIDTHS):
            ps = per_arch_sub[i * len(WIDTHS) + wi]
            for fam in ("TOP", "BOT", "SPREAD"):
                sub = ps[fam]
                d = np.count_nonzero(D0[:, sub] != Q0[sub][None, :], axis=1).astype(np.int16)
                f, _ = measured_fr(d, g, pris)
                fr[f"{fam}{k}"].append(f)
                mo[f"{fam}{k}"].append(model_fr(d, g))
            for j in range(N_PANEL_SEEDS):
                sub = rand_subs[(k, rand_panel_seed(k, j))]
                d = np.count_nonzero(D0[:, sub] != Q0[sub][None, :], axis=1).astype(np.int16)
                f, _ = measured_fr(d, g, pris)
                fr[f"RAND{k}_s{j}"].append(f)
                mo[f"RAND{k}_s{j}"].append(model_fr(d, g))
        dg = np.count_nonzero(D0[:, gspread] != Q0[gspread][None, :], axis=1).astype(np.int16)
        f, _ = measured_fr(dg, g, pris)
        fr["SPREAD64_GLOBAL"].append(f)
        mo["SPREAD64_GLOBAL"].append(model_fr(dg, g))
        dgr = np.count_nonzero(D0[:, gate_rand] != Q0[gate_rand][None, :], axis=1).astype(np.int16)
        fgr, _ = measured_fr(dgr, g, pris)
        gate_fr_rand12000.append(fgr)
        if (i + 1) % 100 == 0:
            log(f"  LME {i + 1}/470")
    arms = {}
    for lab in arm_labels():
        if lab == "NATIVE96":
            eff, con, seed = DIM, "reference full 96-bit sign code", None
        elif lab == "SPREAD64_GLOBAL":
            eff, con, seed = 64, "global-ordering rank-linspace (mean per-archive rank)", None
        elif lab.startswith("RAND"):
            k = int(lab.split("_")[0][4:])
            j = int(lab.split("_s")[1])
            eff, con, seed = k, "global random draw shared across archives", rand_panel_seed(k, j)
        else:
            k = int(lab[-2:])
            eff, con, seed = k, "per-archive variance " + lab[:-2], None
        arms[lab] = summarize_arm(fr[lab], mo[lab], fr["NATIVE96"], eff, con, seed)
    types = sorted(set(a["qtype"] for a in arch))
    per_type = []
    for t in types:
        idx = [i for i, a in enumerate(arch) if a["qtype"] == t]
        per_type.append({"type": t, "n": len(idx),
                         "means": {lab: float(np.mean([fr[lab][i] for i in idx])) for lab in arm_labels()},
                         "model_means": {lab: float(np.mean([mo[lab][i] for i in idx])) for lab in arm_labels()}})
    nat_maxdiff = float(max(abs(fr["NATIVE96"][i] - arch[i]["stored_nat"]) for i in range(len(arch))))
    log(f"LME native vs stored pilot per-q max abs diff = {nat_maxdiff!r}")
    return {"qids": qids, "arms": arms, "per_type": per_type,
            "native_maxdiff_vs_stored": nat_maxdiff,
            "gate_rand12000": [float(v) for v in gate_fr_rand12000],
            "spread64_global_subset": [int(v) for v in gspread],
            "demo_archive": demo}


def run_locomo(root):
    convs, reps = load_locomo(root)
    qinfo = {}
    for ci, c in enumerate(convs):
        id_to_row = reps[ci]["id_to_row"]
        for qi, q in enumerate(c["qas"]):
            ag = evidence_rows(q["correct_evidence"], id_to_row)
            qinfo[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
    valid = [qid for qid, v in qinfo.items() if len(v["ag"]) > 0]
    log(f"LoCoMo: {sum(len(c['qas']) for c in convs)} Cat1-4 questions, {len(valid)} audit-valid")
    var_list = [r["C"].var(axis=0) for r in reps]
    gspread, gmean_rank = global_spread_subset(var_list, 64)
    log(f"LoCoMo SPREAD64_GLOBAL subset head: {gspread[:8].tolist()} ... (k=64, benchmark-global)")
    rand_subs = {}
    for k in WIDTHS:
        for j in range(N_PANEL_SEEDS):
            rand_subs[(k, rand_panel_seed(k, j))] = random_subset(rand_panel_seed(k, j), k)
    pilot_rand = {s: random_subset(s, 48) for s in LOCOMO_PILOT_RAND_SEEDS}
    arch_sub = {}
    n_asserts = 0
    for ci, r in enumerate(reps):
        arch_sub[ci] = {}
        for k in WIDTHS:
            arch_sub[ci][k] = per_archive_subsets(r["C"].var(axis=0), k)
            n_asserts += 1
    log(f"LoCoMo construction asserts: 10 convs x {len(WIDTHS)} widths x 3 fams = "
        f"{n_asserts} per-archive subset triples, all eff_k==k")
    labels = arm_labels()
    fr = {lab: {} for lab in labels}
    mo = {lab: {} for lab in labels}
    pilot_fr = {f"RAND48_pilot_s{s}": {} for s in LOCOMO_PILOT_RAND_SEEDS}
    pilot_mo = {f"RAND48_pilot_s{s}": {} for s in LOCOMO_PILOT_RAND_SEEDS}
    demo = None
    for ci, (c, r) in enumerate(zip(convs, reps)):
        n = r["C"].shape[0]
        pris = trial_priorities(ci, n)
        dist_nat = sign_dist_matrix(r["C"], r["QC"])
        dists = {"NATIVE96": dist_nat}
        for k in WIDTHS:
            for fam in ("TOP", "BOT", "SPREAD"):
                dists[f"{fam}{k}"] = sign_dist_matrix(r["C"], r["QC"], arch_sub[ci][k][fam])
            for j in range(N_PANEL_SEEDS):
                dists[f"RAND{k}_s{j}"] = sign_dist_matrix(r["C"], r["QC"], rand_subs[(k, rand_panel_seed(k, j))])
        dists["SPREAD64_GLOBAL"] = sign_dist_matrix(r["C"], r["QC"], gspread)
        for s in LOCOMO_PILOT_RAND_SEEDS:
            dp = sign_dist_matrix(r["C"], r["QC"], pilot_rand[s])
            for qi, q in enumerate(c["qas"]):
                qid = q["question_id"]
                ag = qinfo[qid]["ag"]
                if not ag:
                    continue
                f, _ = measured_fr(dp[qi], ag, pris)
                pilot_fr[f"RAND48_pilot_s{s}"][qid] = f
                pilot_mo[f"RAND48_pilot_s{s}"][qid] = model_fr(dp[qi], ag)
        for qi, q in enumerate(c["qas"]):
            qid = q["question_id"]
            ag = qinfo[qid]["ag"]
            if not ag:
                continue
            for lab in labels:
                f, trials = measured_fr(dists[lab][qi], ag, pris)
                fr[lab][qid] = f
                mo[lab][qid] = model_fr(dists[lab][qi], ag)
                if demo is None and lab == "NATIVE96":
                    demo = {"qid": qid, "ci": ci, "N": n, "native_trials": trials,
                            "native_mean": f, "seeds": [tie_seed(ci, t) for t in range(NT)]}
        log(f"  LoCoMo conv {ci + 1}/10")
    arms = {}
    for lab in labels:
        if lab == "NATIVE96":
            eff, con, seed = DIM, "reference full 96-bit sign code", None
        elif lab == "SPREAD64_GLOBAL":
            eff, con, seed = 64, "global-ordering rank-linspace (mean per-archive rank)", None
        elif lab.startswith("RAND"):
            k = int(lab.split("_")[0][4:])
            j = int(lab.split("_s")[1])
            eff, con, seed = k, "global random draw shared across archives", rand_panel_seed(k, j)
        else:
            k = int(lab[-2:])
            eff, con, seed = k, "per-archive variance " + lab[:-2], None
        f = [fr[lab][qid] for qid in valid]
        m = [mo[lab][qid] for qid in valid]
        arms[lab] = summarize_arm(f, m, [fr["NATIVE96"][qid] for qid in valid], eff, con, seed)
    pilot_arms = {}
    for key in pilot_fr:
        f = [pilot_fr[key][qid] for qid in valid]
        m = [pilot_mo[key][qid] for qid in valid]
        pilot_arms[key] = summarize_arm(f, m, [fr["NATIVE96"][qid] for qid in valid],
                                        48, "R2C pilot-definition global draw (comparison only)",
                                        int(key.rsplit("_s", 1)[1]))
    per_cat = []
    for cat in (1, 2, 3, 4):
        idx = [qid for qid in valid if qinfo[qid]["cat"] == cat]
        per_cat.append({"cat": cat, "n": len(idx),
                        "means": {lab: float(np.mean([fr[lab][qid] for qid in idx])) for lab in labels},
                        "model_means": {lab: float(np.mean([mo[lab][qid] for qid in idx])) for lab in labels}})
    return {"qids": valid, "arms": arms, "per_cat": per_cat, "pilot_arms": pilot_arms,
            "spread64_global_subset": [int(v) for v in gspread], "demo_conv": demo,
            "cats": {qid: qinfo[qid]["cat"] for qid in valid}}


# ---------- native pre-pass (anchor gates fire before any arm runs) ----------
def native_prepass_lme(root):
    lex, meta, stored, pkls = load_lme(root)
    fr = []
    for p in pkls:
        o = pickle.loads(p.read_bytes())
        C, qC, g = o["C"], o["qC"], np.asarray(o["gold"]).ravel()
        d = np.count_nonzero((C >= 0) != (qC >= 0)[None, :], axis=1).astype(np.int16)
        f, _ = measured_fr(d, g, trial_priorities(lex[o["question_id"]], C.shape[0]))
        fr.append(f)
    return fr


def native_prepass_locomo(root):
    convs, reps = load_locomo(root)
    out = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        id_to_row = r["id_to_row"]
        pris = trial_priorities(ci, r["C"].shape[0])
        dist = sign_dist_matrix(r["C"], r["QC"])
        for qi, q in enumerate(c["qas"]):
            z_ag = evidence_rows(q["correct_evidence"], id_to_row)
            if not z_ag:
                continue
            f, _ = measured_fr(dist[qi], z_ag, pris)
            out[q["question_id"]] = f
    return out


# ---------- TOP-variance negative control ----------
def control_verdict(top48_mean, seed_means, label):
    randmean = float(np.mean(seed_means))
    diff_pp = (top48_mean - randmean) * 100.0
    expectation_met = diff_pp <= -CONTROL_MARGIN_PP
    won = diff_pp > 0.0
    verdict = "FAIL (validity FAIL flag: TOP control won)" if won else "OK"
    log(f"CONTROL {label}: TOP48={top48_mean!r} random-mean={randmean!r} diff={diff_pp:+.4f}pp "
        f"(expect <= -{CONTROL_MARGIN_PP}pp) -> expectation_met={expectation_met} validity={verdict}")
    return {"TOP48_mean": float(top48_mean), "random_panel_mean": randmean,
            "random_panel_seed_means": [float(v) for v in seed_means],
            "diff_pp": float(diff_pp), "margin_pp": CONTROL_MARGIN_PP,
            "expectation_met": bool(expectation_met), "validity": verdict}


# ---------- smokes ----------
def smoke_s1_abort_demo():
    try:
        gate_or_abort("S1-DEMO(tampered anchor)", LME_ANCHOR, LME_ANCHOR + 1e-6)
        return {"fired": False, "note": "ERROR: tampered gate did not abort"}
    except GateAbort as e:
        log(f"S1 abort demo: tampered anchor correctly raised GateAbort ({e})")
        return {"fired": True, "note": str(e)}


def smoke_s6_tie_demo(root, demo):
    seed0 = demo["seeds"][0]
    p0a = np.random.default_rng(seed0).random(demo["N"])
    p0b = np.random.default_rng(seed0).random(demo["N"])
    deter = bool(np.array_equal(p0a, p0b))
    pris = [np.random.default_rng(s).random(demo["N"]) for s in demo["seeds"]]
    distinct = len({hashlib.sha256(p.tobytes()).hexdigest() for p in pris}) == NT
    log(f"S6 tie demo on archive qid={demo['qid']} (N={demo['N']}): "
        f"same-seed redraw identical={deter}; {NT} trial priorities pairwise-distinct={distinct}")
    return {"qid": demo["qid"], "N": demo["N"], "deterministic_redraw": deter,
            "priorities_distinct": distinct, "per_trial_fr": demo["native_trials"],
            "ordering": "lexsort((priority, distance)) top-3 per trial; per-question record persisted"}


def smoke_s8_construction_demo(var_sample):
    order = np.argsort(np.asarray(var_sample, dtype=float))
    broken = order[::-1][::2][:64]  # stride-2 cap erratum style: yields 48, not 64
    try:
        assert len(np.unique(broken)) == 64, ("eff_k != k", "SPREAD-broken", 64, len(np.unique(broken)))
        return {"fired": False, "note": "ERROR: broken construction did not trip the assert"}
    except AssertionError as e:
        log(f"S8 broken-construction control: eff_k assert fired as designed {e}")
        return {"fired": True, "note": str(e)}


def smoke_s10_no_hardcode_and_pins(src_path):
    src = Path(src_path).read_text(encoding="utf-8").lower()
    pats = ["c:" + chr(47), "c:" + chr(92), chr(47) + "mnt" + chr(47) + "c"]
    hits = {p: src.count(p) for p in pats}
    pins = {k: _os.environ.get(k) for k in
            ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")}
    log(f"S10 hardcode scan: {hits} (all must be 0); thread pins: {pins}")
    return {"hardcode_hits": hits, "clean": all(v == 0 for v in hits.values()), "thread_pins": pins,
            "data_root": str(DATA_ROOT.resolve() if DATA_ROOT.exists() else DATA_ROOT),
            "data_root_from": "env RB2_DATA_ROOT" if "RB2_DATA_ROOT" in _os.environ else "relative default",
            "numpy": np.__version__, "python": platform.python_version(),
            "platform": platform.platform()}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    root = DATA_ROOT
    log(f"RB2 start: DATA_ROOT={root} (exists={root.exists()}) OUT_DIR={OUT_DIR}")
    if not root.exists():
        print("RB2_VERDICT: ABORT (data root missing)")
        return 2
    # S1: both anchors recomputed in THIS runner, before any arm.
    pre_lme = native_prepass_lme(root)
    gate_or_abort("LME NATIVE anchor (pre-pass, before arms)", float(np.mean(pre_lme)), LME_ANCHOR)
    pre_loc = native_prepass_locomo(root)
    gate_or_abort("LoCoMo NATIVE anchor (pre-pass, before arms)", float(np.mean(list(pre_loc.values()))),
                  LOCOMO_ANCHOR)
    s1 = smoke_s1_abort_demo()
    # Full race.
    lme = run_lme(root)
    assert max(abs(a - b) for a, b in zip(pre_lme, lme["arms"]["NATIVE96"]["fr"])) == 0.0
    log("LME pre-pass native == full-run native exactly (determinism pin holds)")
    loc = run_locomo(root)
    assert max(abs(pre_loc[q] - loc["arms"]["NATIVE96"]["fr"][i]) for i, q in enumerate(loc["qids"])) == 0.0
    log("LoCoMo pre-pass native == full-run native exactly (determinism pin holds)")
    # Pilot spot gates (matching definitions).
    gate_or_abort("LME TOP48 pilot spot", lme["arms"]["TOP48"]["mean"], GATE_TOP48)
    gate_or_abort("LME RAND48 seed-12000 pilot spot", float(np.mean(lme["gate_rand12000"])), GATE_RAND48)
    gate_or_abort("LME BOT48 pilot spot", lme["arms"]["BOT48"]["mean"], GATE_BOT48)
    gate_or_abort("LoCoMo TOP48 vs R2C", loc["arms"]["TOP48"]["mean"], LOCOMO_R2C_TOP48)
    gate_or_abort("LoCoMo BOT48 vs R2C", loc["arms"]["BOT48"]["mean"], LOCOMO_R2C_BOT48)
    for i, s in enumerate(LOCOMO_PILOT_RAND_SEEDS):
        gate_or_abort(f"LoCoMo RAND48 pilot seed {s} vs R2C",
                      loc["pilot_arms"][f"RAND48_pilot_s{s}"]["mean"], LOCOMO_R2C_RAND48[i])
    # TOP-variance negative controls.
    ctl_lme = control_verdict(lme["arms"]["TOP48"]["mean"],
                              [lme["arms"][f"RAND48_s{j}"]["mean"] for j in range(N_PANEL_SEEDS)], "LME k=48")
    ctl_lme64 = control_verdict(lme["arms"]["TOP64"]["mean"],
                                [lme["arms"][f"RAND64_s{j}"]["mean"] for j in range(N_PANEL_SEEDS)],
                                "LME k=64 (optional)")
    ctl_loc = control_verdict(loc["arms"]["TOP48"]["mean"],
                              [loc["arms"][f"RAND48_s{j}"]["mean"] for j in range(N_PANEL_SEEDS)], "LoCoMo k=48")
    # Smokes.
    s6l = smoke_s6_tie_demo(root, lme["demo_archive"])
    s6c = smoke_s6_tie_demo(root, loc["demo_conv"])
    s8 = smoke_s8_construction_demo(np.asarray(
        pickle.loads(sorted((root / "regen" / "lme" / "cache_repr").glob("*.pkl"))[0].read_bytes())["C"].var(axis=0)))
    s10 = smoke_s10_no_hardcode_and_pins(__file__)
    # Details JSON.
    details = {
        "meta": {"runner": Path(__file__).name, "K": K, "NT": NT, "tol": TOL, "dim": DIM,
                 "widths": list(WIDTHS), "panel_seeds": "93000+10*width_idx+j, j=0..9, width_idx={48:0,64:1,80:2}",
                 "gate_rand48_seed": GATE_RAND48_SEED, "bootstrap": {"produced": False, "B": BOOT_B, "seed": BOOT_SEED,
                     "note": "stopped at per-question arrays + aggregates per session scope; per-q fr/model arrays ready"},
                 "thread_pins": s10["thread_pins"], "numpy": s10["numpy"], "python": s10["python"],
                 "platform": s10["platform"], "data_root": s10["data_root"],
                 "elapsed_s": None},
        "protocol": {"distance": "hamming on sign bits (C>=0, QC>=0), K=3",
                     "priorities": "5_100_000+lex*100_000+t*100+99 (LME) / stable_archive_seed(ci,t)+99 (LoCoMo), 20 trials",
                     "ordering": "lexsort((priority, distance)) top-3 per trial",
                     "aggregation": "per-question mean over 20 trials, then mean over questions",
                     "LME_cohort": "470 non-_abs primary questions", "LoCoMo_cohort": "1535 audit-valid Cat1-4",
                     "construction": "per-archive variance: order_desc=argsort(var,stable)[::-1]; "
                                     "TOP=order_desc[:k]; BOT=order_desc[-k:]; SPREAD=order_desc[round(linspace(0,95,k))]; "
                                     "eff_k==k asserted; RANDOM global draws shared across archives",
                     "SPREAD64_GLOBAL": "axes ranked by mean per-archive rank, rank-linspace, one subset per benchmark"},
        "columns": {"fr": "measured per-question fractional R@3 (mean over 20 frozen tie trials)",
                    "model": "MATH-1 exact-identity predicted per-question FR P(top3)=f(S,T), descriptive annex"},
        "LME": {"qids": lme["qids"], "anchor": {"recomputed": lme["arms"]["NATIVE96"]["mean"],
                                                "expected": LME_ANCHOR,
                                                "diff": lme["arms"]["NATIVE96"]["mean"] - LME_ANCHOR},
                "native_maxdiff_vs_stored": lme["native_maxdiff_vs_stored"],
                "gate_rand12000_mean": float(np.mean(lme["gate_rand12000"])),
                "arms": lme["arms"], "per_type": lme["per_type"],
                "control_TOP48": ctl_lme, "control_TOP64": ctl_lme64,
                "spread64_global_subset": lme["spread64_global_subset"],
                "demo_archive": lme["demo_archive"]},
        "LoCoMo": {"qids": loc["qids"], "cats": loc["cats"],
                   "anchor": {"recomputed": loc["arms"]["NATIVE96"]["mean"], "expected": LOCOMO_ANCHOR,
                              "diff": loc["arms"]["NATIVE96"]["mean"] - LOCOMO_ANCHOR},
                   "r2c_comparison": {k: {"recomputed": v["mean"]} for k, v in loc["pilot_arms"].items()},
                   "arms": loc["arms"], "per_cat": loc["per_cat"], "pilot_arms": loc["pilot_arms"],
                   "control_TOP48": ctl_loc, "spread64_global_subset": loc["spread64_global_subset"],
                   "demo_conv": loc["demo_conv"]},
        "A3_learned_arm": {"status": "EXCLUDED", "basis": "Design-1 kill",
                           "record": {"LME_pp": -1.25, "LME_wins": "2-of-10", "LoCoMo_pp": -0.15},
                           "runner_code": "none"},
        "smokes": {"S1_anchor_abort_demo": s1,
                   "S6_tie_rule_LME": s6l, "S6_tie_rule_LoCoMo": s6c,
                   "S8_construction_asserts": {"per_archive_triples_LME": 470 * len(WIDTHS),
                                               "per_archive_triples_LoCoMo": 10 * len(WIDTHS),
                                               "broken_control": s8},
                   "S10_no_hardcode_pins": s10},
    }
    details["meta"]["elapsed_s"] = time.time() - t0
    det_path = OUT_DIR / "race_sign_details.json"
    det_path.write_text(json.dumps(details, indent=1), encoding="utf-8")
    log(f"DETAILS_WRITTEN {det_path} ({det_path.stat().st_size} bytes)")
    # S9-lite: manifest hashing of its own outputs.
    log_path = OUT_DIR / "smoke_log.txt"
    run_path = Path(__file__)
    h_run = sha256_of(run_path)
    h_det = sha256_of(det_path)
    log(f"S9-lite hashes: race_sign.py sha256={h_run}")
    log(f"S9-lite hashes: race_sign_details.json sha256={h_det}")
    log_path.write_text("\n".join(SMOKE) + "\n", encoding="utf-8")
    h_log = sha256_of(log_path)
    man_path = OUT_DIR / "rb2_manifest.sha256"
    man_path.write_text(f"{h_run}  race_sign.py\n{h_det}  race_sign_details.json\n{h_log}  smoke_log.txt\n",
                        encoding="utf-8")
    print(f"MANIFEST_WRITTEN {man_path}", flush=True)
    # RB2 verdict.
    lines = ["RB2_VERDICT:"]
    lines.append(f"gates: LMEanchor diff={details['LME']['anchor']['diff']!r} "
                 f"LoCoMoanchor diff={details['LoCoMo']['anchor']['diff']!r} (tol 1e-12, all PASS else abort)")
    for bench, res in (("LME", lme), ("LoCoMo", loc)):
        lines.append(f"-- {bench} arm aggregates (mean | gap_pp vs SIGN | W/T/L | tie_frac | model_MAE | model_r) --")
        nat = res["arms"]["NATIVE96"]["mean"]
        order = ["NATIVE96"] + [f"{f}{k}" for k in WIDTHS for f in ("TOP", "BOT", "SPREAD")] + ["SPREAD64_GLOBAL"]
        for lab in order:
            a = res["arms"][lab]
            lines.append(f"  {lab:15s} {a['mean']:.6f} | {(a['mean'] - nat) * 100:+.3f}pp | "
                         f"{a['W']}/{a['T']}/{a['L']} | {a['tie_frac']:.3f} | {a['model_mae']:.4f} | {a['model_r']}")
        for k in WIDTHS:
            ms = [res["arms"][f"RAND{k}_s{j}"]["mean"] for j in range(N_PANEL_SEEDS)]
            lines.append(f"  RAND{k}_x10      mean={np.mean(ms):.6f} min={min(ms):.6f} max={max(ms):.6f} "
                         f"| gap_pp={(np.mean(ms) - nat) * 100:+.3f}")
    for name, ctl in (("LME TOP48", ctl_lme), ("LME TOP64", ctl_lme64), ("LoCoMo TOP48", ctl_loc)):
        lines.append(f"TOP-control {name}: diff={ctl['diff_pp']:+.3f}pp expectation_met={ctl['expectation_met']} "
                     f"validity={ctl['validity']}")
    lines.append(f"asserts: LME {470 * len(WIDTHS)} + LoCoMo {10 * len(WIDTHS)} per-archive triples eff_k==k; "
                 f"S1 abort demo fired={s1['fired']}; S8 broken-control fired={s8['fired']}; "
                 f"S10 clean={s10['clean']}")
    print("\n".join(lines), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
