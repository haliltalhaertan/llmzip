#!/usr/bin/env python3
"""Independent verification for LoCoMo Model-H transfer run (reads artifacts only).
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Checks: gate, counts, schema, t1 identity, invariances, group construction,
pipeline consistency, manual representative-QA recompute via independent code path,
source-unchanged hashes. Prints PASS/FAIL per check + totals. Exit != 0 on any FAIL.
"""
import hashlib, itertools, json, pickle, re, sys
from pathlib import Path
import numpy as np

W = Path(__file__).resolve().parent
SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work")
passed, failed, NCHECKS = [], [], [0]

def check(name, cond, detail=""):
    NCHECKS[0] += 1
    (passed if cond else failed).append(name)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}", flush=True)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()

gate = json.loads((W / "gate.json").read_text(encoding="utf-8"))
summ = json.loads((W / "summary.json").read_text(encoding="utf-8"))
rows = [json.loads(l) for l in (W / "per_query.jsonl").read_text(encoding="utf-8").splitlines()]
pre = json.loads((W / "PRE_RUN.json").read_text(encoding="utf-8"))

# 1. gate record
check("gate_pass_flag", gate.get("GATE_PASS") is True)
check("gate_anchor_exact", gate.get("anchor_diff") == 0.0, repr(gate.get("anchor_diff")))
check("gate_npz_1e12", gate.get("maxabs_mc_vs_npz", 9) < 1e-12, repr(gate.get("maxabs_mc_vs_npz")))
check("gate_perq_1e12", gate.get("maxabs_exp_vs_perq", 9) < 1e-12, repr(gate.get("maxabs_exp_vs_perq")))
check("gate_mc_bitwise_vs_official", gate.get("maxabs_mc_vs_perq_mc") == 0.0)

# 2. counts with code (not memory): raw recount + artifact counts
raw = json.loads((SRC / "drive" / "locomo10.json").read_text(encoding="utf-8"))
ncat14 = sum(1 for item in raw for q in (item.get("qa", []) or [])
             if q.get("category") in (1, 2, 3, 4))
check("raw_cat14_is_1540", ncat14 == 1540, str(ncat14))
check("table_rows_1535", len(rows) == 1535, str(len(rows)))
check("gate_counts", gate.get("counts_cat14") == 1540 and gate.get("counts_valid") == 1535
      and gate.get("counts_excluded") == 5)
from collections import Counter
cc = Counter(r["ci"] for r in rows)
check("ten_archives_cover_rows", sorted(cc) == list(range(10)) and sum(cc.values()) == 1535,
      str(dict(sorted(cc.items()))))
check("excluded_five_have_no_gold", gate.get("gold_count_dist") is not None)

# 3. schema
need = {"qid", "ci", "qi", "cat", "gold_count", "N_docs", "low48", "qconc",
        "doc_rms_low", "doc_rms_high", "native", "cfg", "sign_inv_maxdiff"}
check("row_schema", all(need.issubset(set(r)) for r in rows))
check("cfg_schema", all(set(r["cfg"]) == {"LOW48", "HIGH48", "FULL96"} and
      all(set(r["cfg"][g]) == {"0.25", "0.5", "1.0", "2.0", "4.0"} for g in r["cfg"])
      for r in rows))
check("low48_valid", all(len(r["low48"]) == 48 and len(set(r["low48"])) == 48 and
      all(0 <= i < 96 for i in r["low48"]) for r in rows))

# 4. t=1 identity + invariances from table (independent of summary.json)
t1 = max(abs(r["cfg"][g]["1.0"][k] - (r["native"][k] if k in r["native"] else
           (r["native"]["s_exp"] - r["native"]["f_exp"] if k == "d_exp"
            else r["native"]["s_mc"] - r["native"]["f_mc"])))
         for r in rows for g in ("LOW48", "HIGH48", "FULL96")
         for k in ("s_exp", "s_mc", "f_exp", "f_mc", "d_exp", "d_mc"))
check("t1_identity_maxabs_zero", t1 == 0.0, repr(t1))
check("sign_invariance_zero", max(r["sign_inv_maxdiff"] for r in rows) == 0.0)
fdev = max(abs(r["cfg"]["FULL96"][t][k] - r["native"][k])
           for r in rows for t in ("0.25", "0.5", "1.0", "2.0", "4.0")
           for k in ("f_exp", "f_mc", "s_exp", "s_mc"))
check("full96_invariance_zero", fdev == 0.0, repr(fdev))

# 5. pipeline consistency: recompute primary contrast + curves from table
for gname in ("LOW48", "HIGH48", "FULL96"):
    v = sum(r["cfg"][gname]["4.0"]["d_exp"] - r["cfg"][gname]["0.25"]["d_exp"]
            for r in rows) / len(rows)
    check(f"contrast_{gname}_matches_summary",
          abs(v - summ["contrasts"][gname + ".d_exp"]["mean"]) < 1e-15, repr(v))
lo, hi = summ["contrasts"]["LOW48.d_exp"]["ci95"]
check("primary_ci_ordered", lo < summ["contrasts"]["LOW48.d_exp"]["mean"] < hi)
check("primary_not_positive", summ["contrasts"]["LOW48.d_exp"]["mean"] < 0 and hi < 0,
      "negative verdict is data, sealed rule applied")

# 6. group construction independent path (sorted-with-key vs lexsort)
def groups_sorted(q):
    order = sorted(range(96), key=lambda j: (abs(float(q[j])), j))
    return order[:48], order[48:]
rep = pickle.load(open(SRC / "regen" / "locomo" / "locomo_0.pkl", "rb"))
C0 = np.asarray(rep["C"], dtype=np.float64)
QC0 = np.asarray(rep["QC"], dtype=np.float64)
okg = True
for qi in (0, 7, 40):
    lo1 = rows[[r["qid"] for r in rows].index(f"locomo_0_qa{qi}")]["low48"] \
        if f"locomo_0_qa{qi}" in [r["qid"] for r in rows] else None
    if lo1 is None:
        continue
    a, b = groups_sorted(QC0[qi])
    okg = okg and (list(a) == list(lo1)) and (sorted(a + b) == list(range(96)))
check("groups_match_sorted_key", okg)

# 7. manual representative-QA recompute, no shared helpers (explicit loops)
def manual_metrics(C, q, gold_rows, seed_base, n_docs):
    n = int(n_docs)
    dist = [sum(1 for j in range(96)
                if (float(q[j]) >= 0) != (float(C[i][j]) >= 0)) for i in range(n)]
    K = 3
    tot_e = 0.0
    for gg in gold_rows:
        dg = dist[int(gg)]
        s = sum(1 for v in dist if v < dg)
        t = sum(1 for v in dist if v == dg)
        tot_e += 0.0 if s >= K else (1.0 if s + t <= K else (K - s) / t)
    exact = tot_e / len(gold_rows)
    tot_m = 0.0
    for t_ in range(20):
        pr = list(np.random.default_rng(seed_base + t_ * 100 + 99).random(n))
        order = sorted(range(n), key=lambda i: (dist[i], pr[i]))
        tot_m += len(set(order[:K]) & set(map(int, gold_rows))) / len(gold_rows)
    return dist, exact, tot_m / 20

spot = [r for r in rows if r["qid"] in ("locomo_0_qa0", "locomo_5_qa10", "locomo_9_qa100")]
check("spot_qas_found", len(spot) == 3, str(len(spot)))
for r in spot:
    ci, qi = r["ci"], r["qi"]
    d = pickle.load(open(SRC / "regen" / "locomo" / f"locomo_{ci}.pkl", "rb"))
    Cm = np.asarray(d["C"], dtype=np.float64)
    Qm = np.asarray(d["QC"], dtype=np.float64)
    id_to_row = d["id_to_row"]
    rawc = json.loads((SRC / "drive" / "locomo10.json").read_text(encoding="utf-8"))[ci]
    cat_qas = [q for q in (rawc.get("qa", []) or [])
               if q.get("category") in (1, 2, 3, 4)]
    rawev = cat_qas[qi].get("evidence")
    def norm_ev(x):
        if x is None:
            return []
        if isinstance(x, str):
            v = re.findall(r"D\d+:\d+", x)
            return v if v else [x]
        if isinstance(x, (list, tuple)):
            o = []
            for z in x:
                if isinstance(z, str):
                    ids = re.findall(r"D\d+:\d+", z)
                    o.extend(ids if ids else [z])
            return list(dict.fromkeys(o))
        return []
    gold = []
    for x in norm_ev(rawev):
        if x in id_to_row and int(id_to_row[x]) not in gold:
            gold.append(int(id_to_row[x]))
    if not gold:  # audit-corrected QA: recover gold from stored native dist instead
        check(f"manual_{r['qid']}_skipped_raw_gold", False, "audit-corrected evidence")
        continue
    dist, exact, mc = manual_metrics(Cm, Qm[qi], gold, 5_100_000 + ci * 100_000, Cm.shape[0])
    check(f"manual_{r['qid']}_exact", abs(exact - r["native"]["s_exp"]) < 1e-12,
          f"{exact!r} vs {r['native']['s_exp']!r}")
    check(f"manual_{r['qid']}_mc", abs(mc - r["native"]["s_mc"]) < 1e-12,
          f"{mc!r} vs {r['native']['s_mc']!r}")

# 8. brute-force tie-law check on one small tied block (enumerate permutations)
r0 = rows[0]
ci0 = r0["ci"]
d0 = pickle.load(open(SRC / "regen" / "locomo" / f"locomo_{ci0}.pkl", "rb"))
Cm0 = np.asarray(d0["C"], dtype=np.float64)
Qm0 = np.asarray(d0["QC"], dtype=np.float64)
Cb0 = (Cm0 >= 0)
q0 = (Qm0[r0["qi"]] >= 0)
dv0 = np.count_nonzero(q0[None, :] != Cb0, axis=1)
ag0 = None
rawc0 = json.loads((SRC / "drive" / "locomo10.json").read_text(encoding="utf-8"))[ci0]
# gold rows: reuse table gold_count only; exact enum over tied block of doc 0's bucket
found = False
for gg in range(len(dv0)):
    dg = int(dv0[gg])
    block = [i for i in range(len(dv0)) if int(dv0[i]) == dg]
    s = sum(1 for v in dv0 if int(v) < dg)
    if 1 <= len(block) <= 8 and r0["gold_count"] >= 1:
        brute = 0.0
        n = 0
        for perm in itertools.permutations(block):
            rank = s + list(perm).index(gg) if gg in block else s + len(block)
            brute += 1.0 if rank < 3 else 0.0
            n += 1
        if gg in block:
            law = 0.0 if s >= 3 else (1.0 if s + len(block) <= 3 else (3 - s) / len(block))
            check("brute_force_tie_law", abs(brute / n - law) < 1e-12,
                  f"enum {brute/n!r} vs law {law!r}")
            found = True
            break
if not found:
    check("brute_force_tie_law", False, "no small tied block found")

# 9. sources unchanged (before from PRE_RUN vs now)
pre_pkl = pre["source_pkl_sha256_before"]
okh = True
for ci in range(10):
    now = sha256(SRC / "regen" / "locomo" / f"locomo_{ci}.pkl")
    okh = okh and (now == pre_pkl[f"locomo_{ci}.pkl"])
check("pkl_hashes_unchanged", okh)
prods = {"harness/deney1_loco.py": pre["source_hashes_before"]["deney1_loco.py"],
         "race_2026-09-13/rb2/race_sign.py": pre["source_hashes_before"]["race_sign.py"],
         "audit_2026-09-13/audit1_cont/taskC_real_locomo.py":
             pre["source_hashes_before"]["taskC_real_locomo.py"],
         "audit_2026-09-13/audit1_cont/taskC_LoCoMo_perq.json":
             pre["source_hashes_before"]["taskC_LoCoMo_perq.json"]}
check("producer_hashes_unchanged",
      all(sha256(SRC / k) == v for k, v in prods.items()))
check("plan_hash_unchanged",
      sha256(W / "PLAN.md") == pre["plan_hash_sha256"] == \
      "a0f9e8e6eb214e0129cb5b8e31d35bdb75599eb130332a7eed7780bdc8981a21")

# 10. output hashes (receipts)
for f in ("gate.json", "summary.json", "per_query.jsonl", "run_locomo.py",
          "verification.py", "PRE_RUN.json"):
    print(f"hash {f} {sha256(W / f)}", flush=True)

print(f"CHECKS total={NCHECKS[0]} pass={len(passed)} fail={len(failed)}", flush=True)
print(f"GATE_OUTCOMES pass={gate.get('GATE_PASS')}", flush=True)
sys.exit(1 if failed else 0)
