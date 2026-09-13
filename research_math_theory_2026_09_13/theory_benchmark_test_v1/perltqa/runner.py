#!/usr/bin/env python3
"""PerLTQA Model-H proxy-transfer runner (workspace-isolated).

Stages: gate | run | boot | all
- gate: reproduce native SIGN96 + centered-float96 20-seed fractional R@3 per-QA
        arrays from results_rerun.json at 1e-12 using eval caches + verbatim
        producer conventions. Writes gate.json. Abort on FAIL.
- run:  gold-free LOW48/HIGH48 (by (abs(q),j)) x t grid + FULL96 t=4 control.
        Exact tie-bucket expectation (primary) + 20-seed MC at t=1/endpoints.
        Writes per_query.jsonl with workspace-local checkpoints.
- boot: archive-cluster bootstrap (2000 reps, seed 20260913), curves,
        monotonicity violations, exploratory sections. Writes summary.json.

Reads ONLY from source root; writes ONLY to workspace.
"""
import sys
import json
import pickle
import hashlib
import os
from collections import defaultdict

import numpy as np

SRC_ARCH = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
SRC_Q = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
SRC_ORD = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/resolution.json"
SRC_RERUN = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_fin/results_rerun.json"
WS = "/home/mdp/muse-work/theorybench-perltqa"

K = 3
NT = 20
T_GRID = [0.25, 0.5, 1.0, 2.0, 4.0]
GROUPS = ["LOW48", "HIGH48"]
BOOT_REPS = 2000
BOOT_SEED = 20260913
TOL = 1e-12


def rh(d, p):
    return np.lexsort((p, np.asarray(d)))


def rf(s, p):
    return np.lexsort((p, -np.asarray(s, dtype=np.float64)))


def cos(C, q):
    dn = np.linalg.norm(C, axis=1)
    qn = np.linalg.norm(q)
    return (C @ q) / (dn * qn)


def mc_frac_rank(d_or_s, gold, pr_list, higher_better):
    g = np.asarray(gold).ravel()
    m = len(g)
    tot = 0.0
    for p in pr_list:
        top = (rf(d_or_s, p) if higher_better else rh(d_or_s, p))[:K]
        tot += len(set(map(int, top)) & set(map(int, g))) / m
    return tot / len(pr_list)


def exact_frac(scores, gold, higher_better):
    """Expected fractional R@K under uniform random within-bucket tiebreak."""
    s = np.asarray(scores, dtype=np.float64)
    s = np.where(np.isfinite(s), s, (-np.inf if higher_better else np.inf))
    g = np.asarray(gold).ravel()
    m = int(len(g))
    assert m > 0
    gset = set(map(int, g))
    uniq = np.unique(s)
    levels = uniq[::-1] if higher_better else uniq
    better = 0
    exp = 0.0
    for lv in levels:
        idx = np.nonzero(s == lv)[0]
        B = len(idx)
        if B == 0:
            continue
        if better >= K:
            break
        gb = sum(1 for i in idx if int(i) in gset)
        if better + B <= K:
            exp += gb
        else:
            exp += (K - better) * gb / B
            break
        better += B
    return exp / m


def load_inputs():
    arch = pickle.load(open(SRC_ARCH, "rb"))
    qdat = pickle.load(open(SRC_Q, "rb"))
    ORD = json.load(open(SRC_ORD))["ordinals"]
    return arch, qdat, ORD


def priorities_for(char, N, ORD):
    return [np.random.default_rng(5_100_000 + ORD[char] * 100_000 + t * 100 + 99).random(N)
            for t in range(NT)]


def stage_gate():
    arch, qdat, ORD = load_inputs()
    rerun = json.load(open(SRC_RERUN))
    per_q = rerun["per_q"]
    exp_nat_mean = rerun["aggregate"]["native"]["mean"]
    exp_flt_mean = rerun["aggregate"]["float"]["mean"]
    assert rerun["n_qa"] == 8265 and rerun["K"] == 3 and rerun["NT"] == 20
    assert len(qdat) == 8265 and len(arch) == 30
    assert set(qdat.keys()) == set(per_q.keys()), "qid universe mismatch vs results_rerun.json"

    pr_cache = {}
    maxd_nat = 0.0
    maxd_flt = 0.0
    worst = []
    sum_nat = 0.0
    sum_flt = 0.0
    sec_counts = defaultdict(int)
    arch_qa = defaultdict(int)
    nan_cos = 0
    for n, (qid, q) in enumerate(qdat.items()):
        if n % 2000 == 0:
            print(f"  gate {n}/{len(qdat)}", flush=True)
        char = q["char"]
        sec = q["section"]
        g = np.asarray(q["gold"]).ravel()
        assert len(g) > 0, f"empty gold {qid}"
        qC = np.asarray(q["qC"], float)
        assert qC.shape == (96,)
        sec_counts[sec] += 1
        arch_qa[char] += 1
        a = arch[char]
        C = np.asarray(a["C"], float)
        assert C.shape == (a["N"], 96)
        key = (char, a["N"])
        if key not in pr_cache:
            pr_cache[key] = priorities_for(char, a["N"], ORD)
        pr = pr_cache[key]
        D0 = C >= 0
        Q0 = qC >= 0
        d0 = np.count_nonzero(D0 != Q0[None, :], axis=1)
        base = cos(C, qC)
        if not np.all(np.isfinite(base)):
            nan_cos += 1
        nat = mc_frac_rank(d0, g, pr, False)
        flt = mc_frac_rank(base, g, pr, True)
        sum_nat += nat
        sum_flt += flt
        dn = abs(nat - float(per_q[qid]["native"]))
        df = abs(flt - float(per_q[qid]["float"]))
        maxd_nat = max(maxd_nat, dn)
        maxd_flt = max(maxd_flt, df)
        if dn > TOL or df > TOL:
            worst.append((qid, dn, df))
    mean_nat = sum_nat / len(qdat)
    mean_flt = sum_flt / len(qdat)
    gate = {
        "result": "PASS" if (not worst and abs(mean_nat - exp_nat_mean) <= TOL
                             and abs(mean_flt - exp_flt_mean) <= TOL) else "FAIL",
        "tolerance": TOL,
        "n_qa": len(qdat),
        "n_archives": len(arch),
        "sections": dict(sec_counts),
        "per_archive_qa": {c: int(v) for c, v in sorted(arch_qa.items())},
        "expected_native_mean": exp_nat_mean,
        "recomputed_native_mean": mean_nat,
        "expected_float_mean": exp_flt_mean,
        "recomputed_float_mean": mean_flt,
        "max_abs_diff_perqa_native": maxd_nat,
        "max_abs_diff_perqa_float": maxd_flt,
        "n_violations": len(worst),
        "worst_violations": [{"qid": w[0], "d_nat": w[1], "d_flt": w[2]} for w in worst[:20]],
        "nonfinite_cos_qas": nan_cos,
        "unit_counts": {"expanded": 8593, "resolved": 8305, "measured": 8265,
                        "excluded_Chen_Zhi": 40, "archives": 30},
    }
    json.dump(gate, open(os.path.join(WS, "gate.json"), "w"), indent=2)
    print("GATE " + gate["result"] + f" maxd_nat={maxd_nat:.3e} maxd_flt={maxd_flt:.3e}", flush=True)
    print(f"means nat {mean_nat:.15f} vs {exp_nat_mean:.15f}; flt {mean_flt:.15f} vs {exp_flt_mean:.15f}", flush=True)
    if gate["result"] != "PASS":
        raise SystemExit("GATE FAILED: aborting before intervention")
    return gate


def group_indices(qC):
    order = sorted(range(96), key=lambda j: (abs(float(qC[j])), j))
    low = np.array(sorted(order[:48]), dtype=int)
    high = np.array(sorted(order[48:]), dtype=int)
    return low, high


def stage_run():
    arch, qdat, ORD = load_inputs()
    by_arch = defaultdict(list)
    for qid, q in qdat.items():
        by_arch[q["char"]].append(qid)
    out_path = os.path.join(WS, "per_query.jsonl")
    n_expected_rows = len(qdat) * (len(GROUPS) * len(T_GRID) + 1)
    if os.path.exists(out_path):
        with open(out_path) as f:
            have = sum(1 for _ in f)
        if have == n_expected_rows:
            print(f"run: per_query.jsonl already complete ({have} rows), skipping", flush=True)
            return {"rows": have, "skipped": True}
        print(f"run: resuming ({have}/{n_expected_rows} rows present); rewriting", flush=True)
    fout = open(out_path, "w")
    n_rows = 0
    sign_mismatch = 0
    t1_maxdiff = 0.0
    full_maxdiff = 0.0
    full_rank_changes = 0
    full_top3_gold_changes = 0
    for ai, (char, qids) in enumerate(sorted(by_arch.items())):
        a = arch[char]
        C = np.asarray(a["C"], float)
        N = a["N"]
        assert C.shape == (N, 96)
        pr = priorities_for(char, N, ORD)
        D0 = C >= 0
        ckpt_path = os.path.join(WS, f"ckpt_{ai:02d}_{char.replace(' ', '_')}.jsonl")
        ckpt = open(ckpt_path, "w")
        for qid in qids:
            q = qdat[qid]
            sec = q["section"]
            g = np.asarray(q["gold"]).ravel()
            m = int(len(g))
            qC = np.asarray(q["qC"], float)
            low, high = group_indices(qC)
            assert len(low) == 48 and len(high) == 48
            assert set(low) | set(high) == set(range(96))
            s2 = float(np.sum(qC ** 2))
            conc = float(np.sum(qC ** 4) / (s2 ** 2)) if s2 > 0 else 0.0
            Q0 = qC >= 0
            d0 = np.count_nonzero(D0 != Q0[None, :], axis=1)
            base = cos(C, qC)
            nat_exact = exact_frac(d0, g, False)
            nat_mc = mc_frac_rank(d0, g, pr, False)
            flt_exact_base = exact_frac(base, g, True)
            flt_mc_base = mc_frac_rank(base, g, pr, True)
            arms = []
            for grp, idx in (("LOW48", low), ("HIGH48", high)):
                rms_g = float(np.sqrt(np.mean(C[:, idx] ** 2)))
                compl = np.array([j for j in range(96) if j not in set(idx.tolist())], dtype=int)
                rms_c = float(np.sqrt(np.mean(C[:, compl] ** 2)))
                ratio = float(rms_g / rms_c) if rms_c > 0 else None
                for t in T_GRID:
                    Ct = C.copy()
                    Ct[:, idx] *= t
                    qt = qC.copy()
                    qt[idx] *= t
                    Dt = Ct >= 0
                    Qt = qt >= 0
                    dt = np.count_nonzero(Dt != Qt[None, :], axis=1)
                    if not np.array_equal(dt, d0):
                        sign_mismatch += 1
                    st = cos(Ct, qt)
                    if t == 1.0:
                        t1_maxdiff = max(t1_maxdiff, float(np.max(np.abs(st - base))))
                    fe = exact_frac(st, g, True)
                    fm = None
                    if t in (0.25, 1.0, 4.0):
                        fm = mc_frac_rank(st, g, pr, True)
                    arms.append((grp, t, idx, ratio, fe, fm))
            Cf = C * 4.0
            qf = qC * 4.0
            sf = cos(Cf, qf)
            dfull = float(np.max(np.abs(sf - base)))
            full_maxdiff = max(full_maxdiff, dfull)
            fe_full = exact_frac(sf, g, True)
            fm_full = mc_frac_rank(sf, g, pr, True)
            if not np.array_equal(np.argsort(-np.asarray(sf)), np.argsort(-np.asarray(base))):
                full_rank_changes += 1
            topb = set(map(int, np.lexsort((pr[0], -np.asarray(base, dtype=np.float64)))[:K]))
            topf = set(map(int, np.lexsort((pr[0], -np.asarray(sf, dtype=np.float64)))[:K]))
            if (len(topb & set(map(int, g))) != len(topf & set(map(int, g)))):
                full_top3_gold_changes += 1
            for (grp, t, idx, ratio, fe, fm) in arms:
                row = {"qid": qid, "char": char, "section": sec, "gold_size": m,
                       "group": grp, "t": t, "group_idx": sorted(map(int, idx.tolist())),
                       "native_exact": nat_exact, "native_mc20": nat_mc,
                       "float_exact": fe, "float_mc20": fm,
                       "delta_exact": nat_exact - fe,
                       "delta_mc20": (nat_mc - fm) if fm is not None else None,
                       "q_concentration": conc, "doc_rms_ratio": ratio}
                fout.write(json.dumps(row) + "\n")
                ckpt.write(json.dumps({"qid": qid, "group": grp, "t": t}) + "\n")
                n_rows += 1
            row = {"qid": qid, "char": char, "section": sec, "gold_size": m,
                   "group": "FULL96", "t": 4.0, "group_idx": list(range(96)),
                   "native_exact": nat_exact, "native_mc20": nat_mc,
                   "float_exact": fe_full, "float_mc20": fm_full,
                   "delta_exact": nat_exact - fe_full,
                   "delta_mc20": nat_mc - fm_full,
                   "q_concentration": conc, "doc_rms_ratio": None}
            fout.write(json.dumps(row) + "\n")
            ckpt.write(json.dumps({"qid": qid, "group": "FULL96", "t": 4.0}) + "\n")
            n_rows += 1
        ckpt.close()
        print(f"  run archive {ai + 1}/{len(by_arch)} {char} done (rows={n_rows})", flush=True)
    fout.close()
    assert n_rows == n_expected_rows, f"row count {n_rows} != expected {n_expected_rows}"
    diag = {"rows": n_rows, "expected_rows": n_expected_rows,
            "sign_invariance_mismatches": sign_mismatch,
            "t1_max_abs_score_diff": t1_maxdiff,
            "full96_t4_max_abs_score_diff": full_maxdiff,
            "full96_rank_order_changes": full_rank_changes,
            "full96_top3_gold_count_changes_seed0": full_top3_gold_changes}
    json.dump(diag, open(os.path.join(WS, "run_diag.json"), "w"), indent=2)
    print("RUN done rows=%d sign_mismatch=%d t1_maxdiff=%.3e full_maxdiff=%.3e" %
          (n_rows, sign_mismatch, t1_maxdiff, full_maxdiff), flush=True)
    return diag


def stage_boot():
    rows = []
    with open(os.path.join(WS, "per_query.jsonl")) as f:
        for line in f:
            rows.append(json.loads(line))
    assert len(rows) == 8265 * 11, f"per_query rows {len(rows)}"
    by_q = defaultdict(dict)
    for r in rows:
        by_q[r["qid"]][(r["group"], r["t"])] = r
    assert all(len(v) == 11 for v in by_q.values()), "incomplete (qid,group,t) cells"
    qids = sorted(by_q.keys())
    arch_of = {q: by_q[q][("LOW48", 1.0)]["char"] for q in qids}
    archives = sorted(set(arch_of.values()))
    assert len(archives) == 30, f"clusters {len(archives)}"
    members = {c: [q for q in qids if arch_of[q] == c] for c in archives}

    def curve(stat):
        out = {}
        for grp in ("LOW48", "HIGH48"):
            for t in T_GRID:
                vals = np.array([v for v in (by_q[q][(grp, t)][stat] for q in qids)
                                 if v is not None], dtype=float)
                out[f"{grp}@{t}"] = float(vals.mean()) if len(vals) else None
        return out

    curves = {"float_exact": curve("float_exact"), "delta_exact": curve("delta_exact"),
              "float_mc20_endpoint": {k: v for k, v in curve("float_mc20").items()
                                      if k.split("@")[1] in ("0.25", "1.0", "4.0")},
              "delta_mc20_endpoint": {k: v for k, v in curve("delta_mc20").items()
                                      if k.split("@")[1] in ("0.25", "1.0", "4.0")}}
    full_drift = float(np.mean([by_q[q][("FULL96", 4.0)]["float_exact"]
                                - by_q[q][("LOW48", 1.0)]["float_exact"] for q in qids]))

    def contrast_vec(grp):
        return np.array([by_q[q][(grp, 4.0)]["delta_exact"] - by_q[q][(grp, 0.25)]["delta_exact"]
                         for q in qids])

    c_low = contrast_vec("LOW48")
    c_high = contrast_vec("HIGH48")
    rng = np.random.default_rng(BOOT_SEED)
    per_arch_low = {c: c_low[[i for i, q in enumerate(qids) if arch_of[q] == c]] for c in archives}
    per_arch_high = {c: c_high[[i for i, q in enumerate(qids) if arch_of[q] == c]] for c in archives}

    def boot_ci(per_arch, vec):
        arch_list = archives
        obs = float(vec.mean())
        reps = np.empty(BOOT_REPS)
        for b in range(BOOT_REPS):
            pick = rng.integers(0, len(arch_list), len(arch_list))
            pool = np.concatenate([per_arch[arch_list[i]] for i in pick])
            reps[b] = pool.mean()
        return obs, float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5)), reps.std()

    low_obs, low_lo, low_hi, low_sd = boot_ci(per_arch_low, c_low)
    high_obs, high_lo, high_hi, high_sd = boot_ci(per_arch_high, c_high)

    def viol_frac(grp):
        ts = T_GRID
        n_viol = 0
        for q in qids:
            ds = [by_q[q][(grp, t)]["delta_exact"] for t in ts]
            if any(b < a for a, b in zip(ds, ds[1:])):
                n_viol += 1
        return n_viol / len(qids), n_viol
    viol_low, viol_low_n = viol_frac("LOW48")
    viol_high, viol_high_n = viol_frac("HIGH48")

    secs = sorted(set(by_q[q][("LOW48", 1.0)]["section"] for q in qids))
    sec_curves = {}
    sec_contrast = {}
    for s in secs:
        sq = [q for q in qids if by_q[q][("LOW48", 1.0)]["section"] == s]
        sc = {}
        for grp in ("LOW48", "HIGH48"):
            for t in T_GRID:
                sc[f"{grp}@{t}"] = float(np.mean([by_q[q][(grp, t)]["delta_exact"] for q in sq]))
        sec_curves[s] = {"n": len(sq), **sc}
        sec_contrast[s] = {
            "n": len(sq),
            "LOW48_contrast": float(np.mean([by_q[q][("LOW48", 4.0)]["delta_exact"]
                                             - by_q[q][("LOW48", 0.25)]["delta_exact"] for q in sq])),
            "HIGH48_contrast": float(np.mean([by_q[q][("HIGH48", 4.0)]["delta_exact"]
                                              - by_q[q][("HIGH48", 0.25)]["delta_exact"] for q in sq]))}
    g1 = [q for q in qids if by_q[q][("LOW48", 1.0)]["gold_size"] == 1]
    gm = [q for q in qids if by_q[q][("LOW48", 1.0)]["gold_size"] > 1]
    gold_split = {
        "single_gold": {"n": len(g1), "LOW48_contrast": float(np.mean(
            [by_q[q][("LOW48", 4.0)]["delta_exact"] - by_q[q][("LOW48", 0.25)]["delta_exact"] for q in g1]))},
        "multi_gold": {"n": len(gm), "LOW48_contrast": float(np.mean(
            [by_q[q][("LOW48", 4.0)]["delta_exact"] - by_q[q][("LOW48", 0.25)]["delta_exact"] for q in gm]))}}

    mc_low = float(np.mean([by_q[q][("LOW48", 4.0)]["delta_mc20"]
                            - by_q[q][("LOW48", 0.25)]["delta_mc20"] for q in qids]))
    mc_high = float(np.mean([by_q[q][("HIGH48", 4.0)]["delta_mc20"]
                             - by_q[q][("HIGH48", 0.25)]["delta_mc20"] for q in qids]))
    summary = {
        "labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
                   "DISCLOSE-BEFORE-USE"],
        "n_qa": len(qids),
        "n_rows": len(rows),
        "n_clusters": len(archives),
        "bootstrap": {"reps": BOOT_REPS, "seed": BOOT_SEED, "level": "archive-cluster",
                      "weighting": "question-weighted replicate means"},
        "curves_exact": curves,
        "primary_LOW48_endpoint_contrast_exact": {
            "obs": low_obs, "ci95_lo": low_lo, "ci95_hi": low_hi, "boot_sd": low_sd,
            "verdict": ("consistent with this proxy transfer" if low_lo > 0
                        else ("negative (nonpositive)" if low_obs <= 0 else "inconclusive"))},
        "HIGH48_endpoint_contrast_exact": {
            "obs": high_obs, "ci95_lo": high_lo, "ci95_hi": high_hi, "boot_sd": high_sd},
        "endpoint_contrast_mc20_sensitivity": {"LOW48": mc_low, "HIGH48": mc_high},
        "FULL96_t4_mean_float_drift_vs_base": full_drift,
        "pointwise_monotonicity_violation": {
            "LOW48_frac_any_adjacent_delta_decrease": viol_low, "LOW48_n": viol_low_n,
            "HIGH48_frac_any_adjacent_delta_decrease": viol_high, "HIGH48_n": viol_high_n,
            "denominator": len(qids)},
        "sections_exploratory": {"curves_delta_exact": sec_curves, "contrasts": sec_contrast},
        "gold_split_exploratory": gold_split,
    }
    json.dump(summary, open(os.path.join(WS, "summary.json"), "w"), indent=2)
    print(f"BOOT done LOW48 contrast={low_obs:.5f} [{low_lo:.5f},{low_hi:.5f}] "
          f"HIGH48={high_obs:.5f} [{high_lo:.5f},{high_hi:.5f}]", flush=True)
    print(f"  viol LOW48={viol_low:.4f} HIGH48={viol_high:.4f} FULL96drift={full_drift:.3e}", flush=True)
    return summary


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "gate":
        stage_gate()
    elif stage == "run":
        stage_run()
    elif stage == "boot":
        stage_boot()
    elif stage == "all":
        stage_gate()
        stage_run()
        stage_boot()
    else:
        raise SystemExit(f"unknown stage {stage}")
