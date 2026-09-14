#!/usr/bin/env python3
"""Independent verification for theorybench-lme: artifact checks + manual recompute
via a deliberately different code path (Python sorted() with tuple keys, explicit
loops) rather than the runner's np.lexsort path."""
import os as _os
for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    _os.environ.setdefault(_k, "1")

import csv
import json
import pickle
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work")
K = 3
NT = 20
TOL = 1e-12
N_CHECKS = 0


def check(name, cond, detail=""):
    global N_CHECKS
    N_CHECKS += 1
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        raise SystemExit(f"verification FAILED at: {name} {detail}")


def manual_exact_sign(d, gold):
    tot = 0.0
    for gg in list(gold):
        dg = d[int(gg)]
        s = sum(1 for x in d if x < dg)
        t = sum(1 for x in d if x == dg)
        tot += 0.0 if s >= K else (1.0 if s + t <= K else (K - s) / t)
    return tot / len(list(gold))


def manual_exact_float(s, gold):
    tot = 0.0
    for gg in list(gold):
        sg = s[int(gg)]
        a = sum(1 for x in s if x > sg)
        t = sum(1 for x in s if x == sg)
        tot += 0.0 if a >= K else (1.0 if a + t <= K else (K - a) / t)
    return tot / len(list(gold))


def manual_mc(d_or_s, gold, pris, is_float):
    tot = 0.0
    for p in pris:
        keyed = [((float(-d_or_s[i]) if is_float else int(d_or_s[i])), float(p[i]), i)
                 for i in range(len(d_or_s))]
        order = [i for _, _, i in sorted(keyed)]
        top = set(order[:K])
        g = set(map(int, np.asarray(gold).ravel()))
        tot += len(top & g) / len(g)
    return tot / NT


gate = json.loads((HERE / "gate.json").read_text())
check("gate.json pass flag", gate["pass"] is True)
check("gate 5 checks present", len(gate["checks"]) == 5, str(sorted(gate["checks"])))
for n, c in gate["checks"].items():
    check(f"gate {n} within 1e-12", c["max_abs_diff"] <= TOL, f"maxdiff={c['max_abs_diff']:.3e}")
check("gate counts 470/470/0/0", (gate["n_expected"], gate["n_evaluated"],
      gate["n_unresolved"], gate["n_excluded"]) == (470, 470, 0, 0))
check("gate native anchor", abs(gate["native_mc_mean"] - 0.5419751773049645) <= TOL)

rows = [json.loads(l) for l in open(HERE / "per_query.jsonl", encoding="utf-8")]
check("per_query row count 7050", len(rows) == 470 * 3 * 5, str(len(rows)))
need_cols = {"archive_id", "qa_id", "lex", "N_archive", "gold_count", "section", "group", "t",
             "sign_exact", "float_exact", "delta_exact", "sign_mc20", "float_mc20",
             "delta_mc20", "qconc", "doc_rms_group", "doc_rms_complement"}
check("per_query schema", all(need_cols <= set(r) for r in rows))
per_arch = {}
for r in rows:
    per_arch.setdefault(r["archive_id"], []).append(r)
check("470 archives in table", len(per_arch) == 470)
for qid, rs in per_arch.items():
    keys = {(r["group"], r["t"]) for r in rs}
    if len(rs) != 15 or len(keys) != 15:
        check(f"coverage {qid}", False, f"{len(rs)} rows")
check("all archives have 15 group/t rows", True)
n_mc = sum(1 for r in rows if r["sign_mc20"] is not None)
check("mc20 present exactly for t in {.25,1,4}", n_mc == 470 * 3 * 3, str(n_mc))
check("delta_exact == sign-float", all(abs(r["delta_exact"] - (r["sign_exact"] - r["float_exact"])) == 0.0 for r in rows))

groups = json.loads((HERE / "groups.json").read_text())
check("groups 470 entries", len(groups) == 470)

data = json.loads((SRC / "drive" / "longmemeval_s_cleaned.json").read_bytes())
allq = sorted(str(x["question_id"]) for x in data)
lex = {q: i for i, q in enumerate(allq)}
del data
pkls = {p.stem: p for p in sorted((SRC / "regen" / "lme" / "cache_repr").glob("*.pkl"))}
check("470 source pkls", len(pkls) == 470)

# representative QAs: first sorted, one multi-gold, last sorted
qids = sorted(per_arch)
multi = [q for q in qids if per_arch[q][0]["gold_count"] > 1]
reps = [qids[0], multi[len(multi) // 2], qids[-1]]
print("representative QAs:", [(q, per_arch[q][0]["gold_count"]) for q in reps])
n_outcome = 0
for qid in reps:
    o = pickle.loads(pkls[qid].read_bytes())
    C = np.asarray(o["C"], dtype=np.float64)
    q = np.asarray(o["qC"], dtype=np.float64).reshape(-1)
    g = np.asarray(o["gold"]).ravel()
    lx = lex[qid]
    pris = [np.random.default_rng(5_100_000 + lx * 100_000 + t * 100 + 99).random(C.shape[0])
            for t in range(NT)]
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    s = (C @ q) / (dn * qn)
    d = np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1)
    me_s, me_f = manual_exact_sign(d, g), manual_exact_float(s, g)
    mm_s, mm_f = manual_mc(d, g, pris, False), manual_mc(s, g, pris, True)
    base_r = [r for r in per_arch[qid] if r["group"] == "LOW48" and r["t"] == 1.0][0]
    check(f"manual sign_exact {qid}", abs(me_s - base_r["sign_exact"]) <= TOL, f"{me_s!r}")
    check(f"manual float_exact {qid}", abs(me_f - base_r["float_exact"]) <= 1e-12, f"{me_f!r}")
    check(f"manual sign_mc {qid}", abs(mm_s - base_r["sign_mc20"]) <= TOL, f"{mm_s!r}")
    check(f"manual float_mc {qid}", abs(mm_f - base_r["float_mc20"]) <= TOL, f"{mm_f!r}")
    # LOW48@t=4 intervention via independent path
    low = groups[qid]["LOW48"]
    Ct, qt = C.copy(), q.copy()
    Ct[:, low] = Ct[:, low] * 4.0
    qt[low] = qt[low] * 4.0
    dd = np.count_nonzero((Ct >= 0) != (qt >= 0)[None, :], axis=1)
    ssn = (Ct @ qt) / (np.linalg.norm(Ct, axis=1) * float(np.linalg.norm(qt)))
    iv_r = [r for r in per_arch[qid] if r["group"] == "LOW48" and r["t"] == 4.0][0]
    check(f"manual LOW48@t4 sign {qid}", abs(manual_exact_sign(dd, g) - iv_r["sign_exact"]) <= TOL)
    check(f"manual LOW48@t4 float {qid}", abs(manual_exact_float(ssn, g) - iv_r["float_exact"]) <= 1e-12)
    check(f"manual LOW48@t4 signmc {qid}",
          abs(manual_mc(dd, g, pris, False) - iv_r["sign_mc20"]) <= TOL)
    # group-index rule recompute for this QA
    order = sorted(range(96), key=lambda j: (abs(float(q[j])), j))
    check(f"group rule {qid}", groups[qid]["LOW48"] == order[:48]
          and groups[qid]["HIGH48"] == order[48:])
    n_outcome += 8

# full groups.json rule recompute (all 470) + sign constancy + FULL96 float constancy
for qid in qids:
    o = pickle.loads(pkls[qid].read_bytes())
    qq = np.asarray(o["qC"], dtype=np.float64).reshape(-1)
    order = sorted(range(96), key=lambda j: (abs(float(qq[j])), j))
    if groups[qid]["LOW48"] != order[:48] or groups[qid]["HIGH48"] != order[48:]:
        check(f"group rule all {qid}", False)
    rs = per_arch[qid]
    if len({r["sign_exact"] for r in rs}) != 1:
        check(f"sign constancy {qid}", False)
    full_f = {r["float_exact"] for r in rs if r["group"] == "FULL96"}
    if len(full_f) != 1:
        check(f"FULL96 float constancy {qid}", False)
check("group rule + sign constancy + FULL96 constancy over all 470", True)

summary = json.loads((HERE / "summary.json").read_text())
lo = np.array([r["delta_exact"] for r in rows if r["group"] == "LOW48" and r["t"] == 0.25])
hi = np.array([r["delta_exact"] for r in rows if r["group"] == "LOW48" and r["t"] == 4.0])
contrast = hi - lo
rng = np.random.default_rng(20260913)
reps_b = np.array([float(contrast[rng.integers(0, 470, 470)].mean()) for _ in range(2000)])
m, clo, chi = float(contrast.mean()), float(np.percentile(reps_b, 2.5)), float(np.percentile(reps_b, 97.5))
p = summary["primary_endpoint_contrast"]["LOW48"]
check("bootstrap LOW48 contrast reproduced", abs(m - p["endpoint_contrast_mean"]) == 0.0, f"{m!r}")
check("bootstrap LOW48 CI reproduced", abs(clo - p["ci95"][0]) == 0.0 and abs(chi - p["ci95"][1]) == 0.0)
check("summary row count", summary["n_rows"] == 7050 and summary["n_qa"] == 470)

print(f"\nVERIFICATION COMPLETE: {N_CHECKS} gate/artifact checks + {n_outcome} manual outcome recomputes, all PASS")
print(f"counts: gate_checks={len(gate['checks'])} archives=470 rows=7050 "
      f"manual_recomputes={n_outcome} bootstrap_repro=1")
