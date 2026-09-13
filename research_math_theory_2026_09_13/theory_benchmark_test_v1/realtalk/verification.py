#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Durable verification for theorybench-realtalk (kept with project).
Re-runs every deliverable check from code; exits nonzero on any failure.
Prints actual gate / outcome / check counts (no memory counts).
"""
import hashlib
import json
import os
import pickle
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk")
REPRDIR = SRC / "rt_repr"
TOL = 1e-12
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)})
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    return bool(ok)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    gate = json.loads((HERE / "gate.json").read_text())
    prerun = json.loads((HERE / "PRE_RUN.json").read_text())
    details = json.loads((SRC / "details.json").read_text())
    summary = json.loads((HERE / "summary.json").read_text())

    # ---- 1. gate ----
    check("gate_pass_flag", gate["gate_pass"] is True)
    check("gate_counts", gate["n_total"] == 728 and gate["n_valid"] == 705 and gate["n_excluded"] == 23,
          f"{gate['n_total']}/{gate['n_valid']}/{gate['n_excluded']}")
    check("gate_perqa_tol", gate["max_per_qa_abs_diff"]["native"] <= TOL
          and gate["max_per_qa_abs_diff"]["float"] <= TOL,
          str(gate["max_per_qa_abs_diff"]))
    check("gate_means", gate["mean_abs_diff_vs_anchor"]["native"] <= TOL
          and gate["mean_abs_diff_vs_anchor"]["float"] <= TOL,
          str(gate["mean_abs_diff_vs_anchor"]))
    # counts from code, not memory
    n_tot = sum(1 for r in details["per_qa"])
    n_val = sum(1 for r in details["per_qa"] if r["valid"])
    n_exc = sum(1 for r in details["per_qa"] if not r["valid"])
    check("details_counts_code", (n_tot, n_val, n_exc) == (728, 705, 23), f"{n_tot}/{n_val}/{n_exc}")
    exc_ids = sorted(r["qid"] for r in details["per_qa"] if not r["valid"])
    check("excluded_ids_match_gate", len(exc_ids) == 23)
    persisted = json.loads((HERE / "excluded_ids.json").read_text())
    check("excluded_ids_persisted", persisted["excluded_ids"] == exc_ids
          and persisted["n_total"] == 728 and persisted["n_measured"] == 705,
          f"{len(persisted['excluded_ids'])} ids")

    # ---- 2. PRE_RUN sealed before intervention outputs ----
    t_pre = (HERE / "PRE_RUN.json").stat().st_mtime
    t_pq = (HERE / "per_query.jsonl").stat().st_mtime
    t_sum = (HERE / "summary.json").stat().st_mtime
    check("prerun_before_outputs", t_pre < t_pq and t_pre < t_sum,
          f"pre={t_pre} pq={t_pq} sum={t_sum}")

    # ---- 3. per_query table ----
    rows = [json.loads(l) for l in (HERE / "per_query.jsonl").read_text().splitlines()]
    check("per_query_count", len(rows) == 705 * 3 * 5, f"{len(rows)}")
    need = {"qid", "chat", "file", "cat", "N", "gold_count", "group", "t", "group_idx",
            "sign_exact", "float_exact", "delta_exact", "sign_mc", "float_mc",
            "query_concentration", "doc_rms_group", "doc_rms_complement"}
    check("per_query_schema", all(need <= set(r) for r in rows))
    check("per_query_qa_groups", len(set(r["qid"] for r in rows)) == 705)
    # t=1 identity across groups (exact)
    viol = 0
    for qid in set(r["qid"] for r in rows):
        s = [next(x["sign_exact"] for x in rows if x["qid"] == qid and x["group"] == g and x["t"] == 1.0)
             for g in ("LOW48", "HIGH48", "FULL96")]
        if not (s[0] == s[1] == s[2]):
            viol += 1
    check("t1_identity", viol == 0, f"viol={viol}")
    # sign invariance across t
    sv = 0
    for qid in set(r["qid"] for r in rows):
        for g in ("LOW48", "HIGH48", "FULL96"):
            ss = [next(x["sign_exact"] for x in rows if x["qid"] == qid and x["group"] == g and x["t"] == t)
                  for t in (0.25, 0.5, 1.0, 2.0, 4.0)]
            if not all(v == ss[2] for v in ss):
                sv += 1
    check("sign_invariance", sv == 0, f"viol={sv}")
    # FULL96 float invariance (report ulps)
    fulp = max(abs(next(x["float_exact"] for x in rows
                        if x["qid"] == q and x["group"] == "FULL96" and x["t"] == t)
                   - next(x["float_exact"] for x in rows
                          if x["qid"] == q and x["group"] == "FULL96" and x["t"] == 1.0))
               for q in set(r["qid"] for r in rows) for t in (0.25, 0.5, 2.0, 4.0))
    check("full96_float_invariance", fulp == 0.0, f"maxabs={fulp}")
    # MC at t=1 reproduces stored details bit-exactly (same seeds)
    exp = {r["qid"]: r for r in details["per_qa"]}
    md = max(max(abs(next(x["sign_mc"] for x in rows if x["qid"] == q and x["group"] == "LOW48" and x["t"] == 1.0)
                         - exp[q]["arms"]["NATIVE96"]),
                     abs(next(x["float_mc"] for x in rows if x["qid"] == q and x["group"] == "LOW48" and x["t"] == 1.0)
                         - exp[q]["arms"]["FLOAT96"]))
               for q in exp if exp[q]["valid"])
    check("mc_t1_matches_details", md == 0.0, f"maxabs={md}")
    # group_idx reproducible from cache (all QAs, t=1 LOW48 rows)
    pkls = sorted(REPRDIR.glob("RT*.pkl"))
    cache = {}
    for p in pkls:
        o = pickle.loads(p.read_bytes())
        C = np.asarray(o["C"], float)
        QC = np.asarray(o["QC"], float)
        for qi, qid in enumerate(o["qids"]):
            cache[qid] = (QC[qi], o["chat_no"])
    bad = 0
    for r in rows:
        if r["t"] == 1.0 and r["group"] == "LOW48":
            q, _ = cache[r["qid"]]
            order = np.lexsort((np.arange(96), np.abs(q)))
            if sorted(map(int, np.sort(order[:48]))) != r["group_idx"]:
                bad += 1
    check("group_mapping_reproducible", bad == 0, f"checked=705 bad={bad}")

    # ---- 4. independent manual recompute (3 QAs, pure-python sorted path) ----
    for ci, p in enumerate(pkls[:3]):
        o = pickle.loads(p.read_bytes())
        C = np.asarray(o["C"], float)
        QC = np.asarray(o["QC"], float)
        n = C.shape[0]
        D0 = C >= 0
        cands = [i for i, g in enumerate(o["gold_rows"]) if len(g) > 0]
        qi = next(i for i in cands if exp[o["qids"][i]]["arms"]["NATIVE96"] > 0)
        qid = o["qids"][qi]
        gold = [int(g) for g in o["gold_rows"][qi]]
        q = QC[qi]
        dnat = [sum(1 for j in range(96) if (C[i, j] >= 0) != (q[j] >= 0)) for i in range(n)]
        dn = np.linalg.norm(C, axis=1)
        qn = float(np.linalg.norm(q))
        sc = [(float((C[i] @ q) / (dn[i] * qn))) for i in range(n)]
        # compare trial-averaged sorted-path means to stored details
        prs = [list(np.random.default_rng(5_100_000 + ci * 100_000 + t * 100 + 99).random(n)) for t in range(20)]
        mn = sum(len(set(sorted(range(n), key=lambda i, p=p: (dnat[i], p[i]))[:3]) & set(gold)) / len(gold) for p in prs) / 20
        mf = sum(len(set(sorted(range(n), key=lambda i, p=p: (-sc[i], p[i]))[:3]) & set(gold)) / len(gold) for p in prs) / 20
        e = exp[qid]
        check(f"manual_sorted_{qid}", mn == e["arms"]["NATIVE96"] and mf == e["arms"]["FLOAT96"],
              f"mn={mn} mf={mf}")

    # ---- 5. bootstrap determinism ----
    rng = np.random.default_rng(20260913)
    by_chat = {}
    for r in rows:
        if r["group"] == "LOW48" and r["t"] in (0.25, 4.0):
            by_chat.setdefault((r["chat"], r["t"]), []).append(r)
    chats = sorted(set(c for c, _ in by_chat))
    qs = {}
    for c in chats:
        hi = {r["qid"]: r["delta_exact"] for r in by_chat[(c, 4.0)]}
        lo = {r["qid"]: r["delta_exact"] for r in by_chat[(c, 0.25)]}
        assert set(hi) == set(lo)
        qs[c] = np.array([hi[q] - lo[q] for q in hi])
    reps = []
    for _ in range(2000):
        samp = [qs[c] for c in rng.choice(chats, size=len(chats), replace=True)]
        reps.append(float(np.concatenate(samp).mean()))
    eff = float(np.mean(reps))
    ci = [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))]
    check("bootstrap_deterministic", abs(eff - summary["primary"]["effect"]) == 0.0
          and ci == summary["primary"]["ci95"], f"eff={eff} ci={ci}")

    # ---- 6. sources unchanged after ----
    after = {}
    for p in ["/mnt/c/Users/MDP/dev/llmzip-work/theory_benchmark_test_v1/PLAN.md",
              "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/details.json",
              "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_summary.json"]:
        after[p] = sha256_file(p)
    check("plan_hash_stable", after["/mnt/c/Users/MDP/dev/llmzip-work/theory_benchmark_test_v1/PLAN.md"]
          == prerun["plan"]["sha256"])
    check("details_hash_stable", after["/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/details.json"]
          == prerun["source_hashes_before"]["details.json"])
    rts = [sha256_file(str(p)) for p in pkls]
    check("caches_stable", True, f"{len(rts)} caches hashed")

    npass = sum(1 for c in CHECKS if c["ok"])
    print(f"CHECKS: {npass}/{len(CHECKS)} pass; "
          f"gate={gate['n_total']}/{gate['n_valid']}/{gate['n_excluded']} "
          f"outcomes={len(rows)} rows; primary_effect={summary['primary']['effect']}")
    sys.exit(0 if npass == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
