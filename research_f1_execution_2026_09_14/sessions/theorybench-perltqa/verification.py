#!/usr/bin/env python3
"""Independent verification for the PerLTQA Model-H proxy-transfer pilot.

Re-reads gate.json / run_diag.json / per_query.jsonl / summary.json / PRE_RUN.json
plus read-only sources; checks counts, schema, invariances, an independent
recompute path (pure-python sorted + random.Random tiebreak MC), bootstrap
reproduction, and source-hash stability. Prints actual gate/outcome/check counts.
"""
import json
import pickle
import hashlib
import os
import random
from collections import defaultdict

import numpy as np

SRC = "/mnt/c/Users/MDP/dev/llmzip-work"
WS = "/home/mdp/muse-work/theorybench-perltqa"
K = 3
TOL = 1e-12
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), str(detail)))
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if detail else ""), flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    pre = json.load(open(os.path.join(WS, "PRE_RUN.json")))
    gate = json.load(open(os.path.join(WS, "gate.json")))
    diag = json.load(open(os.path.join(WS, "run_diag.json")))
    summary = json.load(open(os.path.join(WS, "summary.json")))

    # 1. gate
    check("gate_result_PASS", gate["result"] == "PASS", gate["result"])
    check("gate_tol_is_1e-12", gate["tolerance"] == 1e-12, repr(gate["tolerance"]))
    check("gate_maxdiff_native_le_tol", gate["max_abs_diff_perqa_native"] <= 1e-12,
          f"{gate['max_abs_diff_perqa_native']:.3e}")
    check("gate_maxdiff_float_le_tol", gate["max_abs_diff_perqa_float"] <= 1e-12,
          f"{gate['max_abs_diff_perqa_float']:.3e}")
    check("gate_no_violations", gate["n_violations"] == 0, str(gate["n_violations"]))
    check("gate_native_mean_exact", gate["recomputed_native_mean"] == gate["expected_native_mean"] or
          abs(gate["recomputed_native_mean"] - pre["exact_gates_derived_from_results_rerun_json"]["native_mean_exact"]) <= 1e-12,
          repr(gate["recomputed_native_mean"]))
    check("gate_float_mean_exact", abs(gate["recomputed_float_mean"] -
          pre["exact_gates_derived_from_results_rerun_json"]["float_mean_exact"]) <= 1e-12,
          repr(gate["recomputed_float_mean"]))
    check("gate_counts", gate["n_qa"] == 8265 and gate["n_archives"] == 30,
          f"qa={gate['n_qa']} arch={gate['n_archives']}")
    check("gate_sections", gate["sections"] == {"profile": 333, "social_relationship": 844,
          "events": 4346, "dialogues": 2742}, json.dumps(gate["sections"]))

    # 2. per-query table counts + schema
    rows = []
    with open(os.path.join(WS, "per_query.jsonl")) as f:
        for line in f:
            rows.append(json.loads(line))
    check("per_query_row_count", len(rows) == 8265 * 11, f"{len(rows)} vs {8265 * 11}")
    by_q = defaultdict(dict)
    for r in rows:
        by_q[r["qid"]][(r["group"], r["t"])] = r
    check("per_query_n_qid", len(by_q) == 8265, str(len(by_q)))
    check("per_query_cells_complete", all(len(v) == 11 for v in by_q.values()),
          str(sum(len(v) != 11 for v in by_q.values())) + " incomplete")
    req = {"qid", "char", "section", "gold_size", "group", "t", "group_idx", "native_exact",
           "native_mc20", "float_exact", "float_mc20", "delta_exact", "delta_mc20",
           "q_concentration", "doc_rms_ratio"}
    bad_schema = sum(1 for r in rows if set(r.keys()) != req)
    check("per_query_schema", bad_schema == 0, f"{bad_schema} bad")
    secs = defaultdict(int)
    archs = set()
    for q, cells in by_q.items():
        secs[cells[("LOW48", 1.0)]["section"]] += 1
        archs.add(cells[("LOW48", 1.0)]["char"])
    check("per_query_sections_from_ids", dict(secs) == {"profile": 333, "social_relationship": 844,
          "events": 4346, "dialogues": 2742}, json.dumps(dict(secs)))
    check("per_query_30_archives", len(archs) == 30, str(len(archs)))
    bad_idx = 0
    bad_mcnull = 0
    for r in rows:
        want = 96 if r["group"] == "FULL96" else 48
        if len(r["group_idx"]) != want:
            bad_idx += 1
        mid = r["t"] in (0.5, 2.0)
        if mid != (r["float_mc20"] is None):
            bad_mcnull += 1
        if (r["delta_mc20"] is None) != (r["float_mc20"] is None):
            bad_mcnull += 1
    check("per_query_group_idx_sizes", bad_idx == 0, f"{bad_idx} bad")
    check("per_query_mc20_null_pattern", bad_mcnull == 0, f"{bad_mcnull} bad")

    # 3. gold denominators original (vs eval cache, all QAs)
    qdat = pickle.load(open(SRC + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
    bad_gold = sum(1 for q, cells in by_q.items()
                   if cells[("LOW48", 1.0)]["gold_size"] != int(len(np.asarray(qdat[q]["gold"]).ravel())))
    check("gold_size_denominators_original", bad_gold == 0, f"{bad_gold} mismatched")

    # 4. invariances from the table itself
    max_nat_spread = 0.0
    max_t1_gap = 0.0
    max_full_drift = 0.0
    max_mirror_gap = 0.0
    for q, cells in by_q.items():
        nats = [cells[(g, t)]["native_exact"] for g in ("LOW48", "HIGH48") for t in
                (0.25, 0.5, 1.0, 2.0, 4.0)] + [cells[("FULL96", 4.0)]["native_exact"]]
        max_nat_spread = max(max_nat_spread, max(nats) - min(nats))
        max_t1_gap = max(max_t1_gap, abs(cells[("LOW48", 1.0)]["float_exact"]
                                        - cells[("HIGH48", 1.0)]["float_exact"]))
        max_full_drift = max(max_full_drift, abs(cells[("FULL96", 4.0)]["float_exact"]
                                                - cells[("LOW48", 1.0)]["float_exact"]))
        for t, tinv in ((0.25, 4.0), (0.5, 2.0), (1.0, 1.0), (2.0, 0.5), (4.0, 0.25)):
            max_mirror_gap = max(max_mirror_gap, abs(cells[("LOW48", t)]["float_exact"]
                                                    - cells[("HIGH48", tinv)]["float_exact"]))
    check("sign_invariant_across_all_cells", max_nat_spread == 0.0, f"spread={max_nat_spread:.3e}")
    check("run_diag_sign_mismatch_zero", diag["sign_invariance_mismatches"] == 0,
          str(diag["sign_invariance_mismatches"]))
    check("t1_identity_exact", max_t1_gap == 0.0 and diag["t1_max_abs_score_diff"] == 0.0,
          f"t1_gap={max_t1_gap:.3e} score={diag['t1_max_abs_score_diff']:.3e}")
    check("FULL96_t4_drift_zero", max_full_drift == 0.0 and
          summary["FULL96_t4_mean_float_drift_vs_base"] == 0.0, f"{max_full_drift:.3e}")
    check("LOW_HIGH_mirror_identity", max_mirror_gap == 0.0, f"{max_mirror_gap:.3e}")
    check("delta_is_native_minus_float",
          all(abs(r["delta_exact"] - (r["native_exact"] - r["float_exact"])) == 0.0 for r in rows),
          "all rows")

    # 5. independent manual recompute: 3 QAs (events/social/dialogues) x 3 arms,
    # pure-python sorted() ranking + random.Random permutation tiebreak MC vs exact
    arch = pickle.load(open(SRC + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
    reps = {"events": None, "social_relationship": None, "dialogues": None}
    for q, cells in by_q.items():
        s = cells[("LOW48", 1.0)]["section"]
        if s in reps and reps[s] is None:
            reps[s] = q
    assert all(reps.values()), "representative QA per section missing"
    print("representatives: " + json.dumps(reps), flush=True)
    rr = random.Random(20260913)
    worst_mc_gap = 0.0
    worst_rank_gap = 0
    for sec, qid in reps.items():
        C = np.asarray(arch[by_q[qid][("LOW48", 1.0)]["char"]]["C"], float)
        qC = np.asarray(qdat[qid]["qC"], float)
        g = set(map(int, np.asarray(qdat[qid]["gold"]).ravel()))
        for grp, t in (("LOW48", 4.0), ("HIGH48", 0.25), ("LOW48", 1.0)):
            idx = by_q[qid][(grp, t)]["group_idx"]
            Ct = C.copy()
            Ct[:, idx] *= t
            qt = qC.copy()
            qt[idx] *= t
            dn = np.linalg.norm(Ct, axis=1)
            qn = np.linalg.norm(qt)
            s_vals = [(float(Ct[i] @ qt) / float(dn[i] * qn)) for i in range(Ct.shape[0])]
            s_vals = [v if np.isfinite(v) else float("-inf") for v in s_vals]
            N = len(s_vals)
            # seed-0 top3 via pure sorted() on (score desc, priority asc), priority = fresh Random
            pri = [rr.random() for _ in range(N)]
            top = sorted(range(N), key=lambda i: (-s_vals[i], pri[i]))[:K]
            got = len(set(top) & g) / len(g)
            # exact expectation by bucket enumeration (independent loop formulation)
            levels = sorted(set(s_vals), reverse=True)
            better = 0
            exp = 0.0
            for lv in levels:
                members = [i for i in range(N) if s_vals[i] == lv]
                if better >= K:
                    break
                gb = sum(1 for i in members if i in g)
                if better + len(members) <= K:
                    exp += gb
                else:
                    exp += (K - better) * gb / len(members)
                    break
                better += len(members)
            exp /= len(g)
            stored = by_q[qid][(grp, t)]["float_exact"]
            worst_mc_gap = max(worst_mc_gap, abs(exp - stored))
            # permutation MC cross-check of the exact value (different RNG stream)
            tot = 0.0
            ND = 2000
            for _ in range(ND):
                perm = list(range(N))
                rr.shuffle(perm)
                pos = {doc: r for r, doc in enumerate(perm)}
                topm = sorted(range(N), key=lambda i: (-s_vals[i], pos[i]))[:K]
                tot += len(set(topm) & g) / len(g)
            mc = tot / ND
            if abs(mc - stored) > 0.03:
                worst_rank_gap += 1
    check("manual_exact_matches_stored", worst_mc_gap == 0.0, f"max_gap={worst_mc_gap:.3e}")
    check("permutation_MC_within_0.03_of_exact", worst_rank_gap == 0, f"{worst_rank_gap} arms off")

    # 6. bootstrap reproduction (independent loop, same seed) + summary obs
    qids = sorted(by_q.keys())
    arch_of = {q: by_q[q][("LOW48", 1.0)]["char"] for q in qids}
    archives = sorted(set(arch_of.values()))
    c_low = np.array([by_q[q][("LOW48", 4.0)]["delta_exact"]
                      - by_q[q][("LOW48", 0.25)]["delta_exact"] for q in qids])
    check("summary_primary_obs_reproduced",
          abs(float(c_low.mean()) - summary["primary_LOW48_endpoint_contrast_exact"]["obs"]) == 0.0,
          f"{float(c_low.mean()):.6f}")
    per_arch = {c: np.array([c_low[i] for i, q in enumerate(qids) if arch_of[q] == c]) for c in archives}
    rng = np.random.default_rng(20260913)
    picks = rng.integers(0, len(archives), (2000, len(archives)))
    boot = np.array([np.concatenate([per_arch[archives[i]] for i in row]).mean() for row in picks])
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    check("bootstrap_ci_reproduced",
          abs(lo - summary["primary_LOW48_endpoint_contrast_exact"]["ci95_lo"]) < 2e-3 and
          abs(hi - summary["primary_LOW48_endpoint_contrast_exact"]["ci95_hi"]) < 2e-3,
          f"[{lo:.5f},{hi:.5f}]")
    check("bootstrap_excludes_zero", lo > 0, f"lo={lo:.5f}")
    check("summary_cluster_count", summary["n_clusters"] == 30 and summary["n_qa"] == 8265,
          f"{summary['n_clusters']}/{summary['n_qa']}")

    # 7. source hashes unchanged after run
    unchanged = 0
    changed = []
    for rel, h0 in pre["source_hashes_before"].items():
        h1 = sha(os.path.join(SRC, rel))
        if h1 == h0:
            unchanged += 1
        else:
            changed.append(rel)
    check("source_files_unchanged", not changed,
          f"{unchanged}/{len(pre['source_hashes_before'])} unchanged" + (f"; CHANGED={changed}" if changed else ""))
    check("plan_copy_still_byte_exact",
          sha(os.path.join(WS, "PLAN.md")) == pre["plan"]["sha256"], "PLAN.md sha256")

    n_pass = sum(1 for _, ok, _ in CHECKS if ok)
    print(f"CHECKS {n_pass}/{len(CHECKS)} passed", flush=True)
    print(f"GATE maxd_nat={gate['max_abs_diff_perqa_native']:.3e} "
          f"maxd_flt={gate['max_abs_diff_perqa_float']:.3e} violations={gate['n_violations']}", flush=True)
    print(f"OUTCOME LOW48 contrast obs={summary['primary_LOW48_endpoint_contrast_exact']['obs']:.5f} "
          f"CI=[{summary['primary_LOW48_endpoint_contrast_exact']['ci95_lo']:.5f},"
          f"{summary['primary_LOW48_endpoint_contrast_exact']['ci95_hi']:.5f}] "
          f"verdict={summary['primary_LOW48_endpoint_contrast_exact']['verdict']}", flush=True)
    print(f"QUERIES qids={len(by_q)} rows={len(rows)} archives={len(archives)} "
          f"excluded=Chen Zhi(40, N=35) unresolved=288", flush=True)
    if n_pass != len(CHECKS):
        raise SystemExit("VERIFICATION FAILURES PRESENT")


if __name__ == "__main__":
    main()
