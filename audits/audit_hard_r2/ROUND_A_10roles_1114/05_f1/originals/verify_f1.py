# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
#!/usr/bin/env python3
"""verify_f1.py — runnable PASS/FAIL verification for the F1 repair execution.

Covers what is checkable WITHOUT the sealed/absent Drive caches:
  A. implementation correctness vs HAND-COMPUTED fixtures (oracle = arithmetic
     done by hand in F1_EXECUTION_REPORT.md, Sec 3 — not any lead/auditor code)
  B. theorems: single-gold => per-gold IDENTICAL to min-gold (explains why the
     bug hides in single-gold strata); average-rank Spearman properties +
     scipy cross-check when scipy is importable (else SKIP)
  C. three-reference pin consistency to FULL precision, re-extracted live from
     branch bytes via `git show` (FINDINGS.json vs CORRECTED_RESULT.json vs
     contract table vs EXECUTION_LOG.txt vs CLAIM_MATRIX.json vs R1 prose)
  D. cache-presence probe: real-data rerun possible? (expected: BLOCKED)
  E. bootstrap machinery: determinism + invalid-replicate ledger on synthetic data

Exit code 0 iff no FAIL (BLOCKED/SKIP do not fail). Overall verdict printed.
Run:  python3 verify_f1.py
"""
import json
import math
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f1_competition as F

RESULTS = []


def check(name, status, detail=""):
    assert status in ("PASS", "FAIL", "SKIP", "BLOCKED")
    RESULTS.append((name, status, detail))
    print("[%s] %s %s" % (status, name, detail))


def approx(a, b, tol=1e-12):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- A. fixtures
# Hand-computed fixture (see F1_EXECUTION_REPORT.md Sec 3 for the arithmetic):
#   C = [[2,-1,1,-3],[-1,2,-2,1],[1,1,-1,-1],[-2,-2,2,2],[0,3,-3,0]], D=4, k=2
#   v = [2.0, 3.8, 3.8, 3.0] -> stable-desc order [1,2,3,0], TOP=[1,2], BOT=[3,0]
#   qC = [1,-2,3,-1]; d_TOP=[0,2,2,0,2]; d_BOT=[0,2,0,2,1]
C_FIX = [[2, -1, 1, -3], [-1, 2, -2, 1], [1, 1, -1, -1],
         [-2, -2, 2, 2], [0, 3, -3, 0]]
Q_FIX = [1, -2, 3, -1]


def test_geometry():
    v = F.col_mean_squares(C_FIX)
    check("A1 col means", "PASS" if v == [2.0, 3.8, 3.8, 3.0] else "FAIL",
          "v=%s" % (v,))
    top, bot = F.topbot_axes(v, 2)
    # stable descending: j1(3.8) keeps priority over j2(3.8)
    check("A2 stable-desc TOP/BOT",
          "PASS" if (top, bot) == ([1, 2], [3, 0]) else "FAIL",
          "top=%s bot=%s" % (top, bot))
    dt = F.hamming_distances(C_FIX, Q_FIX, top)
    db = F.hamming_distances(C_FIX, Q_FIX, bot)
    check("A3 hamming",
          "PASS" if (dt, db) == ([0, 2, 2, 0, 2], [0, 2, 0, 2, 1]) else "FAIL",
          "dT=%s dB=%s" % (dt, db))


def test_multigold_rows():
    r1 = F.competition_row([0, 2, 2, 0, 2], [0, 2, 0, 2, 1], [0, 2])  # Q1
    exp1 = {"strict_top": 1.0, "tie_top": 2.5, "strict_bot": 0.0,
            "tie_bot": 2.0, "strict_gap": 1.0, "tie_gap": 0.5,
            "strict_top_ng": 0.5, "tie_top_ng": 1.5, "strict_bot_ng": 0.0,
            "tie_bot_ng": 0.0, "strict_gap_ng": 0.5, "tie_gap_ng": 1.5,
            "min_strict_gap": 0.0, "min_tie_gap": 0.0, "gold_n": 2}
    ok = all(r1[k] == e for k, e in exp1.items())
    check("A4 Q1 multi-gold row", "PASS" if ok else "FAIL",
          "row=%s" % ({k: r1[k] for k in exp1},))
    r3 = F.competition_row([0, 2, 2, 0, 2], [0, 2, 0, 2, 1], [1, 3])  # Q3
    exp3 = {"strict_gap": -2.0, "tie_gap": 0.5,
            "min_strict_gap": -3.0, "min_tie_gap": 0.0}
    ok = all(r3[k] == e for k, e in exp3.items())
    check("A5 Q3 multi-gold row", "PASS" if ok else "FAIL",
          "gaps=%s" % ({k: r3[k] for k in exp3},))
    # BUG DEMONSTRATED (not asserted away): correct vs min-gold differ Q1/Q3
    check("A6 bug visible Q1",
          "PASS" if (r1["strict_gap"], r1["tie_gap"]) !=
          (r1["min_strict_gap"], r1["min_tie_gap"]) else "FAIL",
          "correct=(1.0,0.5) min-gold=(0.0,0.0)")
    check("A7 bug visible Q3",
          "PASS" if (r3["strict_gap"], r3["tie_gap"]) !=
          (r3["min_strict_gap"], r3["min_tie_gap"]) else "FAIL",
          "correct=(-2.0,0.5) min-gold=(-3.0,0.0)")


def test_singlegold_equivalence():
    r2 = F.competition_row([0, 2, 2, 0, 2], [0, 2, 0, 2, 1], [4])  # Q2
    exp2 = {"strict_top": 2.0, "tie_top": 3.0, "strict_bot": 2.0,
            "tie_bot": 1.0, "strict_gap": 0.0, "tie_gap": 2.0,
            "min_strict_gap": 0.0, "min_tie_gap": 2.0}
    ok = all(r2[k] == e for k, e in exp2.items())
    check("A8 Q2 single-gold row", "PASS" if ok else "FAIL",
          "row=%s" % ({k: r2[k] for k in exp2},))
    # THEOREM on random 96-D data: gold_n==1 => per-gold == min-gold exactly
    rng = random.Random(20260914)
    bad = 0
    for _ in range(300):
        n = rng.randint(2, 40)
        C = [[rng.uniform(-3, 3) for _ in range(96)] for _ in range(n)]
        q = [rng.uniform(-3, 3) for _ in range(96)]
        v = F.col_mean_squares(C)
        t, b = F.topbot_axes(v, 64)
        dt = F.hamming_distances(C, q, t)
        db = F.hamming_distances(C, q, b)
        g = [rng.randrange(n)]
        r = F.competition_row(dt, db, g)
        if not (r["strict_top"] == r["min_strict_gap"] + r["strict_bot"]
                and r["tie_top"] == r["min_tie_gap"] + r["tie_bot"]
                and r["strict_gap"] == r["min_strict_gap"]
                and r["tie_gap"] == r["min_tie_gap"]):
            bad += 1
    check("A9 single-gold theorem x300", "PASS" if bad == 0 else "FAIL",
          "mismatches=%d" % bad)


def test_spearman():
    rho = F.spearman_rho([0.5, -0.25, 0.1], [1.0, 0.0, -2.0])
    check("B1 hand rho=0.5", "PASS" if rho == 0.5 else "FAIL", "rho=%r" % rho)
    rho2 = F.spearman_rho([0.5, -0.25, 0.1], [0.5, 2.0, 0.5])
    check("B2 hand rho=-sqrt(3)/2",
          "PASS" if approx(rho2, -math.sqrt(3) / 2, 1e-15) else "FAIL",
          "rho=%r" % rho2)
    check("B3 monotone=1.0",
          "PASS" if F.spearman_rho([1, 2, 3, 4], [5, 6, 7, 8]) == 1.0 else "FAIL")
    check("B4 constant=undefined",
          "PASS" if F.spearman_rho([1, 1, 1], [1, 2, 3]) is None else "FAIL")
    check("B5 n<2 undefined",
          "PASS" if F.spearman_rho([1.0], [2.0]) is None else "FAIL")
    try:
        from scipy.stats import spearmanr
        rng = random.Random(7)
        worst = 0.0
        for _ in range(50):
            xs = [rng.choice([1.0, 2.0, 2.0, 3.5, -1.0]) for _ in range(30)]
            ys = [rng.gauss(0, 1) for _ in range(30)]
            mine = F.spearman_rho(xs, ys)
            theirs = float(spearmanr(xs, ys).statistic)
            worst = max(worst, abs(mine - theirs))
        check("B6 scipy cross-check x50",
              "PASS" if worst < 1e-12 else "FAIL", "maxdiff=%.2g" % worst)
    except ImportError:
        check("B6 scipy cross-check x50", "SKIP", "scipy not importable")


def test_gates_and_bootstrap():
    ok = F.check_headline_gates(
        {b: F.HEADLINE_GATES[b][0] for b in F.HEADLINE_GATES},
        {b: F.HEADLINE_GATES[b][1] for b in F.HEADLINE_GATES})
    check("C1 gates pass on pins",
          "PASS" if all(v[0] for v in ok.values()) else "FAIL")
    bad = dict(F.HEADLINE_GATES)
    bad["LME"] = (0.54, 0.44)
    ok2 = F.check_headline_gates(
        {b: bad[b][0] for b in bad}, {b: bad[b][1] for b in bad})
    check("C2 gates catch drift",
          "PASS" if not ok2["LME"][0] else "FAIL", ok2["LME"][1])
    # synthetic multi-cluster rows: determinism + ledger
    rng = random.Random(99)
    rows = []
    for c in range(4):
        for i in range(25):
            rows.append({"qid": "%d:%d" % (c, i), "cluster": "c%d" % c,
                         "delta": rng.gauss(0, 1),
                         "strict_gap": rng.gauss(0, 2), "gold_n": 1,
                         "tie_gap": rng.gauss(0, 2)})
    b1 = F.cluster_bootstrap(rows, seed=96013, n_boot=2000)
    b2 = F.cluster_bootstrap(rows, seed=96013, n_boot=2000)
    check("C3 bootstrap deterministic",
          "PASS" if b1 == b2 else "FAIL")
    led = b1["strict_gap"]
    check("C4 bootstrap ledger",
          "PASS" if led["attempted"] == 2000
          and led["valid"] + led["invalid"] == 2000 else "FAIL",
          "valid=%d invalid=%d" % (led["valid"], led["invalid"]))
    const = [dict(r, delta=0.0) for r in rows]
    bc = F.cluster_bootstrap(const, seed=96013, n_boot=200)
    check("C5 invalid replicates recorded",
          "PASS" if bc["strict_gap"]["invalid"] == 200
          and bc["strict_gap"]["invalid_reasons"].get(
              "undefined_spearman") == 200 else "FAIL",
          "%s" % bc["strict_gap"]["invalid_reasons"])


# ------------------------------------------------- C. live pin re-extraction
def git_show(ref):
    p = subprocess.run(["git", "show", ref], capture_output=True, text=True,
                       cwd=os.path.join(HERE, ".."))
    if p.returncode != 0:
        raise RuntimeError("git show failed: " + ref + " " + p.stderr[:200])
    return p.stdout


AUDIT = "origin/audit/e1-v2-raw-cache-recovery-independent-2026-09-13"
R2 = "origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13"
R1 = "origin/research/e1-v2-raw-cache-recovery-2026-09-13"


def test_pins():
    try:
        findings = json.loads(git_show(
            AUDIT + ":audit_e1_v2_raw_cache_recovery_2026_09_13/FINDINGS.json"))
        corrected = json.loads(git_show(
            R2 + ":campaign_2026_09_13/e1_v2_raw_recovery_r2_2026_09_13/"
            "E1_V2_COMPETITION_CORRECTED_RESULT.json"))
        contract = git_show(
            R2 + ":campaign_2026_09_13/e1_v2_raw_recovery_r2_2026_09_13/"
            "R2_COMPETITION_RERUN_CONTRACT.md")
        execlog = git_show(
            AUDIT + ":audit_e1_v2_raw_cache_recovery_2026_09_13/EXECUTION_LOG.txt")
        matrix = json.loads(git_show(
            AUDIT + ":audit_e1_v2_raw_cache_recovery_2026_09_13/CLAIM_MATRIX.json"))
    except RuntimeError as e:
        check("D0 branch bytes readable", "SKIP", str(e))
        return
    check("D0 branch bytes readable", "PASS")
    f1 = findings["findings"][0]
    amap = {"LME": "LME", "REALTALK": "REALTALK", "PERLTQA": "PERLTQA",
            "LOCOMO": "LOCOMO"}
    # D1: FINDINGS corrected == CORRECTED_RESULT primary, full precision
    allok, det = True, []
    for src, dst in amap.items():
        for arm, ckey in (("strict", "rho_delta_vs_strict_gap"),
                          ("tie", "rho_delta_vs_gold_tie_gap")):
            a = f1["evidence"]["corrected_rho"][src][arm]
            b = corrected["benchmarks"][dst][ckey]
            if not (a == b):
                allok, det = False, det + ["%s.%s %r!=%r" % (src, arm, a, b)]
    check("D1 FINDINGS==CORRECTED_RESULT", "PASS" if allok else "FAIL",
          "; ".join(det))
    # D2: contract table values identical
    import re
    cvals = {}
    for m in re.finditer(r"\| (LME|REALTALK|PerLTQA|LoCoMo) \| "
                         r"([0-9.]+) \| ([0-9.]+) \|", contract):
        cvals[m.group(1).upper()] = (float(m.group(2)), float(m.group(3)))
    allok, det = True, []
    for src, dst in amap.items():
        a = f1["evidence"]["corrected_rho"][src]
        if cvals.get(src) != (a["strict"], a["tie"]):
            allok, det = False, det + [src]
    check("D2 contract table identical", "PASS" if allok else "FAIL",
          "mismatch=%s" % det)
    # D3: EXECUTION_LOG CLAIM-D d2/lead/sensitivity + counts match CORRECTED_RESULT
    logsec = execlog[execlog.index("CLAIM D COMPETITION"):]
    logsec = logsec[:logsec.index("LEAD COMPARISON")]
    allok, det = True, []
    for src, dst in (("LME", "LME"), ("LOCOMO", "LOCOMO"), ("PERLTQA", "PERLTQA"),
                     ("REALTALK", "REALTALK")):
        blk = logsec[logsec.index('"%s"' % src):]
        blk = blk[:blk.index("}},") + 3] if src != "REALTALK" else blk
        for key, cpath in (
                ("d2_per_gold_all_rows_strict", ("rho_delta_vs_strict_gap",)),
                ("d2_per_gold_all_rows_tie", ("rho_delta_vs_gold_tie_gap",)),
                ("lead_min_gold_strict", ("r1_min_gold_strict",)),
                ("lead_min_gold_tie", ("r1_min_gold_tie",)),
                ("non_gold_only_sensitivity_strict",
                 ("non_gold_sensitivity_strict",)),
                ("non_gold_only_sensitivity_tie",
                 ("non_gold_sensitivity_tie",))):
            m = re.search(r'"%s": ([0-9.e+-]+)' % key, blk)
            if not m or float(m.group(1)) != corrected["benchmarks"][dst][cpath[0]]:
                allok, det = False, det + ["%s.%s" % (src, key)]
        for key in ("multi_gold_n", "n"):
            m = re.search(r'"%s": ([0-9]+)' % key, blk)
            if not m or int(m.group(1)) != corrected["benchmarks"][dst][key]:
                allok, det = False, det + ["%s.%s" % (src, key)]
    check("D3 EXECUTION_LOG==CORRECTED_RESULT", "PASS" if allok else "FAIL",
          "mismatch=%s" % det)
    # D4: single-gold sections hide the bug — lead==d2 exactly (events/profile/social)
    allok, det = True, []
    for sec in ("events", "profile", "social_relationship"):
        blk = logsec[logsec.index('"%s"' % sec):]
        blk = blk[:500]
        for key in ("lead_min_gold_strict", "lead_min_gold_tie",
                    "d2_per_gold_all_rows_strict", "d2_per_gold_all_rows_tie"):
            pass
        ls = float(re.search(r'"lead_min_gold_strict": ([0-9.e+-]+)', blk).group(1))
        ds = float(re.search(r'"d2_per_gold_all_rows_strict": ([0-9.e+-]+)', blk).group(1))
        lt = float(re.search(r'"lead_min_gold_tie": ([0-9.e+-]+)', blk).group(1))
        dt = float(re.search(r'"d2_per_gold_all_rows_tie": ([0-9.e+-]+)', blk).group(1))
        if not (ls == ds and lt == dt):
            allok, det = False, det + [sec]
    check("D4 single-gold sections lead==d2", "PASS" if allok else "FAIL",
          "mismatch=%s" % det)
    # D5: CLAIM_MATRIX D agrees; D6: R1 prose values are the rounded lead values
    dm = matrix["claims"]["D_RANKING_COMPETITION"]["corrected_d2_per_gold_rho"]
    allok = all(dm[k][a] == f1["evidence"]["corrected_rho"][k][a]
                for k in amap for a in ("strict", "tie"))
    check("D5 CLAIM_MATRIX agrees", "PASS" if allok else "FAIL")
    r1rep = git_show(R1 + ":campaign_2026_09_13/e1_v2_raw_recovery_2026_09_13/"
                     "E1_V2_RAW_CACHE_RECOVERY_REPORT.md")
    r1clean = r1rep.replace("**", "")
    r1rows = re.findall(r"\| (?:LongMemEval|LME|REALTALK|PerLTQA|LoCoMo) \| "
                        r"\+([0-9.]+) \| \+([0-9.]+) \|", r1clean)
    # cross-check: each prose value rounds the corresponding lead_min_gold_*
    # from CORRECTED_RESULT.json (lead = buggy min-gold implementation)
    leads = [("LME", "r1_min_gold_strict", "r1_min_gold_tie"),
             ("REALTALK", "r1_min_gold_strict", "r1_min_gold_tie"),
             ("PERLTQA", "r1_min_gold_strict", "r1_min_gold_tie"),
             ("LOCOMO", "r1_min_gold_strict", "r1_min_gold_tie")]
    roundok = len(r1rows) == 4 and all(
        abs(float(p[0]) - corrected["benchmarks"][b][ks]) < 5e-5
        and abs(float(p[1]) - corrected["benchmarks"][b][kt]) < 5e-5
        for p, (b, ks, kt) in zip(r1rows, leads))
    check("D6 R1 prose rounds lead values",
          "PASS" if roundok else "FAIL", "rows=%s" % (r1rows,))


def test_cache_probe():
    try:
        tree = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", R2], capture_output=True,
            text=True, cwd=os.path.join(HERE, ".."))
        heavy = [l for l in tree.stdout.splitlines()
                 if l.endswith((".tar.gz", ".pkl", ".npz", ".npy",
                                ".json.gz"))]
        pilot_only = all("pilots_" in l for l in heavy)
        local = [p for p in ("03_regen_caches.tar.gz",
                             "04_bench3_runs_caches.tar.gz",
                             "07_drive_frozen.tar.gz")
                 if os.path.exists(os.path.join(HERE, "..", p))]
        mnt = os.path.exists("/mnt/data")
    except Exception as e:
        check("E0 cache probe", "SKIP", str(e))
        return
    check("E0 real-data rerun",
          "BLOCKED" if (pilot_only and not local and not mnt) else "FAIL",
          "git-heavy=%s local=%s /mnt/data=%s" % (heavy, local, mnt))


if __name__ == "__main__":
    test_geometry()
    test_multigold_rows()
    test_singlegold_equivalence()
    test_spearman()
    test_gates_and_bootstrap()
    test_pins()
    test_cache_probe()
    fails = [r for r in RESULTS if r[1] == "FAIL"]
    print("----")
    print("counts: %s" % ", ".join(
        "%s=%d" % (s, sum(1 for r in RESULTS if r[1] == s))
        for s in ("PASS", "FAIL", "SKIP", "BLOCKED")))
    if fails:
        print("OVERALL: FAIL (%d failing checks)" % len(fails))
        sys.exit(1)
    blocked = any(r[1] == "BLOCKED" for r in RESULTS)
    print("OVERALL: %s" % ("PARTIAL — implementation PASS, real-data BLOCKED "
                           "(caches absent, no network)" if blocked
                           else "PASS"))
    sys.exit(0)
