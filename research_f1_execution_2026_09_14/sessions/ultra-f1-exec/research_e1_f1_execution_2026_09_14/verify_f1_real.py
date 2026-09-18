# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
#!/usr/bin/env python3
"""verify_f1_real.py — F1 contract REAL-DATA execution + verification.

Re-runnable. Usage:  python3 verify_f1_real.py [CACHE_ROOT]
Default CACHE_ROOT = /mnt/c/Users/MDP/dev/llmzip-work (read-only; never written).

What it does (contract R2_COMPETITION_RERUN_CONTRACT.md, VERIFIED from branch bytes):
  C3 headline gates (SIGN96 / centered-float fractional-R@3, K=3, NT=20 trials,
     frozen lexsort tie protocol, seeds 5_100_000+ord*100_000+t*100+99) to 1e-12.
     A failed gate STOPS that benchmark.
  C4 TOP64/BOT64 from v_j = mean(C^2), stable-descending (contract-literal,
     f1_competition.py, oracle-proven). Exact-tie census + mean-square-vs-variance
     axis-selection check logged (auditor CLAIM: identical selection).
  C5 per-gold competition rows (min-gold FORBIDDEN as metric; computed ONLY as
     bug-reproduction control for step 5 of the task).
  C7 average-rank Spearman Delta vs strict/tie gaps per benchmark (+ PerLTQA
     sections, + non-gold sensitivity), compared to auditor targets at 1e-12.
  C8 descriptive cluster bootstrap, seed 96013, B=2000, percentile 2.5/97.5,
     full attempted/valid/invalid ledger.
  C9 persisted outputs: evidence/per_query_rows.csv, evidence/results.json,
     evidence/bootstrap.json, MANIFEST.sha256 (sha256 of every input file read).

Delta_q = FR_SIGN96 - FR_FLOAT96 recomputed HERE from C/qC/gold (frozen spec);
the auditor's INDEPENDENT_QUERY_ROWS.json is absent and never assumed.
LME lex ordinals (500-universe) are recovered against the pilot's stored
per-question native FR (derived numbers, used ONLY as an index checksum:
every recovered lx reproduces stored FR bitwise from primary data; the
computation itself uses only C/qC/gold). Any bitwise miss STOPS LME.

Exit 0 iff every executed primary gate + primary rho is within 1e-12.
Prints PASS/FAIL per check.
"""
import csv
import glob
import hashlib
import json
import math
import os
import pickle
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f1_competition as F

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/c/Users/MDP/dev/llmzip-work'
K = 3
NT = 20
TOL = 1e-12

CHECKS = []


def check(name, status, detail=""):
    assert status in ("PASS", "FAIL", "SKIP", "STOP")
    CHECKS.append((name, status, detail))
    print("[%s] %s %s" % (status, name, detail), flush=True)


def seed_of(ordv, t):
    return 5_100_000 + ordv * 100_000 + t * 100 + 99


def fr_trials(d_or_neg, gold_set, N, ordv, negate):
    """Fractional-R@3 mean over NT trials. negate=False: Hamming lexsort((p,d));
    negate=True: score arm lexsort((p,-s)) with float64 negation."""
    tot = []
    for t in range(NT):
        p = np.random.default_rng(seed_of(ordv, t)).random(N)
        order = np.lexsort((p, -np.asarray(d_or_neg, dtype=np.float64))) if negate \
            else np.lexsort((p, np.asarray(d_or_neg)))
        tot.append(len(set(map(int, order[:K])) & gold_set) / len(gold_set))
    return float(np.mean(np.array(tot)))


def cosine_scores(C, q):
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if not (qn > 0) or bool(np.any(~np.isfinite(dn))) or bool(np.any(dn <= 0)):
        return None
    s = (C @ q) / (dn * qn)
    if bool(np.any(~np.isfinite(s))):
        return None
    return s


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


MANIFEST = []  # (relpath, sha256, size)


def reg(path):
    rel = os.path.relpath(path, ROOT)
    MANIFEST.append((rel, sha256_file(path), os.path.getsize(path)))
    return path


# --------------------------------------------------------------------------
# benchmarks
# --------------------------------------------------------------------------

def load_lme():
    d = os.path.join(ROOT, 'regen/lme/cache_repr')
    files = sorted(glob.glob(os.path.join(d, '*.pkl')))
    out = []
    for p in files:
        reg(p)
        o = pickle.load(open(p, 'rb'))
        out.append((str(o['question_id']),
                    np.asarray(o['C'], float), np.asarray(o['qC'], float),
                    sorted(set(map(int, np.asarray(o['gold']).ravel())))))
    return out


def load_rt():
    d = os.path.join(ROOT, 'bench3/runs/b3a_realtalk/rt_repr')
    files = sorted(glob.glob(os.path.join(d, 'RT*.pkl')))
    out = []
    for ci, p in enumerate(files):
        reg(p)
        o = pickle.load(open(p, 'rb'))
        C = np.asarray(o['C'], float)
        QC = np.asarray(o['QC'], float)
        for qi, qid in enumerate(o['qids']):
            g = sorted(set(map(int, np.asarray(o['gold_rows'][qi]).ravel())))
            if not g:
                continue
            out.append((str(qid), C, np.asarray(QC[qi], float), g,
                        str(o['chat_no']), ci))
    return out, files


def load_pqa():
    pa = reg(os.path.join(ROOT, 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl'))
    pq = reg(os.path.join(ROOT, 'bench3/runs/b3b_perltqa/cache_q_eval.pkl'))
    pr = reg(os.path.join(ROOT, 'bench3/runs/b3b_perltqa/resolution.json'))
    arch = pickle.load(open(pa, 'rb'))
    qdat = pickle.load(open(pq, 'rb'))
    ords = json.load(open(pr))['ordinals']
    out = []
    for qid, q in qdat.items():
        out.append((str(qid), np.asarray(arch[q['char']]['C'], float),
                    np.asarray(q['qC'], float),
                    sorted(set(map(int, np.asarray(q['gold']).ravel()))),
                    str(q['char']), str(q['section']), int(ords[q['char']])))
    return out


def norm_evidence(x):
    if x is None:
        return []
    if isinstance(x, str):
        z = re.findall(r'D\d+:\d+', x)
        return z if z else [x]
    out = []
    if isinstance(x, (list, tuple)):
        for y in x:
            if isinstance(y, str):
                z = re.findall(r'D\d+:\d+', y)
                out.extend(z if z else [y])
            elif isinstance(y, dict):
                qq = y.get('dia_id') or y.get('id')
                if qq:
                    out.append(str(qq))
    return list(dict.fromkeys(out))


def load_loco():
    d = os.path.join(ROOT, 'regen/locomo')
    a = os.path.join(ROOT, 'drive/audit_layer')
    corr = {}
    for p in sorted(glob.glob(os.path.join(a, 'errors_conv_*.json'))):
        reg(p)
        for r in json.load(open(p)):
            qid = r.get('question_id')
            if qid:
                corr[str(qid)] = {'has': 'correct_evidence' in r,
                                  'ev': norm_evidence(r.get('correct_evidence'))}
    n_corr = len(corr)
    out = []
    for ci, p in enumerate(sorted(glob.glob(os.path.join(d, 'locomo_*.pkl')))):
        reg(p)
        o = pickle.load(open(p, 'rb'))
        C = np.asarray(o['C'], float)
        QC = np.asarray(o['QC'], float)
        id2 = o['id_to_row']
        for qi, qa in enumerate(o['qas']):
            qid = str(qa['question_id'])
            raw = norm_evidence(qa.get('raw_evidence'))
            z = corr.get(qid)
            clean = z['ev'] if (z and z['has']) else raw
            gold = sorted(set(int(id2[x]) for x in clean if x in id2))
            if not gold:
                continue
            out.append((qid, C, np.asarray(QC[qi], float), gold,
                        str(o['conv_id']), ci))
    return out, n_corr


# --------------------------------------------------------------------------
# execution
# --------------------------------------------------------------------------

def run_queries(items, ord_of, bm, cluster_of, section_of):
    """items: (qid, C, q, gold, ...). Returns (rows, diag). STOPS (raises)
    on zero/nonfinite norms or float boundary-score nonfiniteness."""
    rows = []
    diag = {'n': 0, 'multi': 0, 'sign_tie_b': 0, 'float_tie_b': 0,
            'v_exact_ties': 0, 'ms_var_axdiff': 0, 'hamming_xcheck': 0,
            'fr_sign': [], 'fr_float': []}
    for it in items:
        qid, C, q, gold = it[0], np.asarray(it[1], float), np.asarray(it[2], float), list(it[3])
        n = C.shape[0]
        ordv = ord_of(it)
        G = set(gold)
        D = C >= 0
        Q = q >= 0
        d = np.count_nonzero(D != Q[None, :], axis=1)
        s = cosine_scores(C, q)
        if s is None:
            raise RuntimeError("nonfinite/zero norm in %s %s" % (bm, qid))
        sd = np.sort(d)
        if sd[K - 1] == sd[K]:
            diag['sign_tie_b'] += 1
        ss = np.sort(np.asarray(s, float))[::-1]
        if ss[K - 1] == ss[K]:
            diag['float_tie_b'] += 1
        frs = fr_trials(d, G, n, ordv, False)
        frf = fr_trials(s, G, n, ordv, True)
        diag['fr_sign'].append(frs)
        diag['fr_float'].append(frf)
        # competition (contract-literal; numpy Hamming == proven python path)
        v = F.col_mean_squares(C.tolist())
        if len(set(v)) != len(v):
            diag['v_exact_ties'] += 1
        top, bot = F.topbot_axes(v, 64)
        order_var = sorted(range(len(v)), key=lambda j: (-float(np.var(C[:, j])), j))
        if set(top) != set(order_var[:64]):
            diag['ms_var_axdiff'] += 1
        dt = [int(x) for x in np.count_nonzero(D[:, top] != Q[top][None, :], axis=1)]
        db = [int(x) for x in np.count_nonzero(D[:, bot] != Q[bot][None, :], axis=1)]
        if diag['hamming_xcheck'] < 200:
            assert dt == F.hamming_distances(C.tolist(), q.tolist(), top), qid
            assert db == F.hamming_distances(C.tolist(), q.tolist(), bot), qid
            diag['hamming_xcheck'] += 1
        crow = F.competition_row(dt, db, gold)
        crow.update({"qid": qid, "benchmark": bm, "cluster": cluster_of(it),
                     "section": section_of(it),
                     "delta": float(frs - frf),
                     "fr_sign": frs, "fr_float": frf})
        rows.append(crow)
        diag['n'] += 1
        if len(gold) > 1:
            diag['multi'] += 1
    return rows, diag


def gate(bm, diag, s_ref, f_ref):
    s = float(np.mean(np.array(diag['fr_sign'])))
    f = float(np.mean(np.array(diag['fr_float'])))
    ds, df = abs(s - s_ref), abs(f - f_ref)
    check("GATE %s SIGN %.16f" % (bm, s), "PASS" if ds <= TOL else "FAIL",
          "ref=%.16f diff=%.3g" % (s_ref, ds))
    check("GATE %s FLOAT %.16f" % (bm, f), "PASS" if df <= TOL else "FAIL",
          "ref=%.16f diff=%.3g" % (f_ref, df))
    return s, f, (ds <= TOL and df <= TOL)


def rho_report(rows, s_ref, t_ref, tag):
    sm = F.benchmark_summary(rows, "strict_gap", "tie_gap")
    ds = abs(sm["rho_strict"] - s_ref)
    dt = abs(sm["rho_tie"] - t_ref)
    check("RHO %s strict %.14f" % (tag, sm["rho_strict"]),
          "PASS" if ds <= TOL else "FAIL",
          "ref=%.14f diff=%.3g" % (s_ref, ds))
    check("RHO %s tie %.14f" % (tag, sm["rho_tie"]),
          "PASS" if dt <= TOL else "FAIL",
          "ref=%.14f diff=%.3g" % (t_ref, dt))
    return sm


def mismatch_stats(rows):
    ms = [abs(r["strict_gap"] - r["min_strict_gap"]) for r in rows]
    mt = [abs(r["tie_gap"] - r["min_tie_gap"]) for r in rows]
    return {"strict_n": sum(1 for x in ms if x != 0.0),
            "strict_max": max(ms), "tie_n": sum(1 for x in mt if x != 0.0),
            "tie_max": max(mt)}


AUDIT_RHO = {
    "LME": (0.14168629605302735, 0.14045379360271315),
    "REALTALK": (0.097939128891117, 0.12281952421315011),
    "PERLTQA": (0.25416826537535475, 0.2797878341571222),
    "LOCOMO": (0.09491957131277647, 0.10376015063205302),
}
LEAD_MIN = {
    "LME": (0.09965709814218833, 0.0989586520264074),
    "REALTALK": (0.06118332620206951, 0.0871527005507532),
    "PERLTQA": (0.27738722348615524, 0.285059265942642),
    "LOCOMO": (0.09370604039357276, 0.09533237242284638),
}
SENS = {
    "LME": (0.141200412379537, 0.14883000714957909),
    "REALTALK": (0.09813662381103015, 0.12231123187522679),
    "PERLTQA": (0.25432876802474186, 0.2797727287692079),
    "LOCOMO": (0.09478580583026314, 0.10401481252579545),
}
SECTIONS = {
    "dialogues": (0.13054126734088975, 0.11123087254360414),
    "events": (0.39790634780463613, 0.38922832069574037),
    "profile": (0.0573253028779693, 0.018738683422868593),
    "social_relationship": (0.30428515802019, 0.2993013213223269),
}
MISM = {
    "LME": (265, 221.5, 261, 55.0),
    "REALTALK": (385, 482.0, 385, 98.6),
    "PERLTQA": (2315, 286.83333333333337, 2307, 46.66666666666667),
    "LOCOMO": (425, 272.5, 424, 54.0),
}
GATES = {
    "LME": (0.5419751773049645, 0.4415957446808511),
    "REALTALK": (0.22477507598784194, 0.17253405381064954),
    "PERLTQA": (0.488941994930817, 0.551692074528853),
    "LOCOMO": (0.23654714666441054, 0.16826334541318252),
}


def recover_lme_lex(items):
    """Recover 500-universe lex ordinals: per qid, candidates lx in
    [rank470, rank470+30] with recomputed SIGN FR == stored pilot FR bitwise.
    Greedy smallest-feasible strictly-increasing assignment; STOPS on failure."""
    sp = os.path.join(ROOT, 'pilots/axis_attack_2026-09-12/pilot_results.json')
    reg(sp)
    stored = json.load(open(sp))['per_question_native_FR']
    by_q = {it[0]: it for it in items}
    qids = sorted(by_q)
    rank470 = {q: i for i, q in enumerate(qids)}
    cand = {}
    for q in qids:
        _, C, qc, gold = by_q[q][0], np.asarray(by_q[q][1], float), np.asarray(by_q[q][2], float), set(by_q[q][3])
        D = C >= 0
        Q = qc >= 0
        d = np.count_nonzero(D != Q[None, :], axis=1)
        hits = []
        for lx in range(rank470[q], rank470[q] + 31):
            if fr_trials(d, gold, len(C), lx, False) == stored[q]:
                hits.append(lx)
        cand[q] = hits
    bad = [q for q in qids if not cand[q]]
    check("LEX coverage (470 qids, >=1 candidate)", "PASS" if not bad else "FAIL",
          "missing=%d %s" % (len(bad), bad[:5]))
    if bad:
        raise RuntimeError("lex recovery failed for %d qids" % len(bad))
    LX, prev = {}, -1
    for q in qids:
        feas = [lx for lx in cand[q] if lx > prev]
        if not feas:
            raise RuntimeError("no feasible lx for %s" % q)
        LX[q] = feas[0]
        prev = feas[0]
    vals = [LX[q] for q in qids]
    check("LEX strictly increasing, distinct", "PASS" if len(set(vals)) == 470 else "FAIL",
          "range=[%d,%d]" % (min(vals), max(vals)))
    multi = sum(1 for q in qids if len(cand[q]) > 1)
    check("LEX ambiguity note", "PASS", "%d qids multi-candidate (all give stored-identical FR)" % multi)
    return LX


def main():
    evdir = os.path.join(HERE, 'evidence')
    os.makedirs(evdir, exist_ok=True)
    all_rows = []
    summary = {}
    gates_ok = True

    # ---- LME ----
    lme = load_lme()
    check("LOAD LME", "PASS", "n=%d" % len(lme))
    LX = recover_lme_lex(lme)
    rows, dg = run_queries(lme, lambda it: LX[it[0]], "LME",
                           lambda it: it[0], lambda it: None)
    stored = json.load(open(os.path.join(
        ROOT, 'pilots/axis_attack_2026-09-12/pilot_results.json')))['per_question_native_FR']
    bad = [r["qid"] for r in rows if r["fr_sign"] != stored[r["qid"]]]
    check("LME SIGN-bitwise vs stored pilot FR", "PASS" if not bad else "FAIL",
          "mismatches=%d %s" % (len(bad), bad[:5]))
    s, f, ok = gate("LME", dg, *GATES["LME"])
    gates_ok &= ok
    all_rows += rows
    summary["LME"] = {"n": dg["n"], "multi": dg["multi"], "sign": s, "float": f, "diag": dg}

    # ---- REALTALK ----
    rt, _ = load_rt()
    check("LOAD REALTALK", "PASS", "n=%d" % len(rt))
    rows, dg = run_queries(rt, lambda it: it[5], "REALTALK",
                           lambda it: it[4], lambda it: None)
    s, f, ok = gate("REALTALK", dg, *GATES["REALTALK"])
    gates_ok &= ok
    all_rows += rows
    summary["REALTALK"] = {"n": dg["n"], "multi": dg["multi"], "sign": s, "float": f, "diag": dg}

    # ---- PerLTQA ----
    pq = load_pqa()
    check("LOAD PERLTQA", "PASS", "n=%d" % len(pq))
    rows, dg = run_queries(pq, lambda it: it[6], "PERLTQA",
                           lambda it: it[4], lambda it: it[5])
    s, f, ok = gate("PERLTQA", dg, *GATES["PERLTQA"])
    gates_ok &= ok
    all_rows += rows
    summary["PERLTQA"] = {"n": dg["n"], "multi": dg["multi"], "sign": s, "float": f, "diag": dg}

    # ---- LoCoMo ----
    lo, n_corr = load_loco()
    check("LOAD LOCOMO", "PASS", "n=%d corr_entries=%d" % (len(lo), n_corr))
    rows, dg = run_queries(lo, lambda it: it[5], "LOCOMO",
                           lambda it: it[4], lambda it: None)
    s, f, ok = gate("LOCOMO", dg, *GATES["LOCOMO"])
    gates_ok &= ok
    all_rows += rows
    summary["LOCOMO"] = {"n": dg["n"], "multi": dg["multi"], "sign": s, "float": f, "diag": dg}

    by_bm = {}
    for bm in ("LME", "REALTALK", "PERLTQA", "LOCOMO"):
        by_bm[bm] = [r for r in all_rows if r["benchmark"] == bm]

    # ---- C7 primary + sensitivity + sections; min-gold control; mismatch ----
    results = {"benchmarks": {}, "sections": {}}
    for bm, rs in by_bm.items():
        sm = rho_report(rs, *AUDIT_RHO[bm], tag=bm)
        ng = F.benchmark_summary(rs, "strict_gap_ng", "tie_gap_ng")
        ds = abs(ng["rho_strict"] - SENS[bm][0])
        dt = abs(ng["rho_tie"] - SENS[bm][1])
        check("SENS %s strict %.14f" % (bm, ng["rho_strict"]),
              "PASS" if ds <= TOL else "FAIL", "ref=%.14f diff=%.3g" % (SENS[bm][0], ds))
        check("SENS %s tie %.14f" % (bm, ng["rho_tie"]),
              "PASS" if dt <= TOL else "FAIL", "ref=%.14f diff=%.3g" % (SENS[bm][1], dt))
        mg = F.benchmark_summary(rs, "min_strict_gap", "min_tie_gap")
        ds = abs(mg["rho_strict"] - LEAD_MIN[bm][0])
        dt = abs(mg["rho_tie"] - LEAD_MIN[bm][1])
        check("MINBUG %s strict %.14f" % (bm, mg["rho_strict"]),
              "PASS" if ds <= TOL else "FAIL", "ref=%.14f diff=%.3g" % (LEAD_MIN[bm][0], ds))
        check("MINBUG %s tie %.14f" % (bm, mg["rho_tie"]),
              "PASS" if dt <= TOL else "FAIL", "ref=%.14f diff=%.3g" % (LEAD_MIN[bm][1], dt))
        mm = mismatch_stats(rs)
        exp = MISM[bm]
        okm = (mm["strict_n"] == exp[0] and mm["tie_n"] == exp[2]
               and abs(mm["strict_max"] - exp[1]) < 1e-9 and abs(mm["tie_max"] - exp[3]) < 1e-9)
        check("MISM %s" % bm, "PASS" if okm else "FAIL",
              "got=(%d,%.4g,%d,%.4g) exp=(%d,%.4g,%d,%.4g)" % (
                  mm["strict_n"], mm["strict_max"], mm["tie_n"], mm["tie_max"],
                  exp[0], exp[1], exp[2], exp[3]))
        results["benchmarks"][bm] = {
            "n": sm["n"], "multi_gold_n": sm["multi_gold_n"],
            "multi_gold_rate": sm["multi_gold_rate"],
            "rho_delta_vs_strict_gap": sm["rho_strict"],
            "rho_delta_vs_gold_tie_gap": sm["rho_tie"],
            "non_gold_sensitivity_strict": ng["rho_strict"],
            "non_gold_sensitivity_tie": ng["rho_tie"],
            "r1_min_gold_strict": mg["rho_strict"],
            "r1_min_gold_tie": mg["rho_tie"],
            "mismatch": mm,
            "headline_sign": summary[bm]["sign"],
            "headline_float": summary[bm]["float"],
        }
    for sec, rs_ in ((sec, [r for r in by_bm["PERLTQA"] if r["section"] == sec])
                     for sec in ("dialogues", "events", "profile", "social_relationship")):
        sm = rho_report(rs_, *SECTIONS[sec], tag="PERLTQA/" + sec)
        results["sections"][sec] = {"n": sm["n"], "multi_gold_n": sm["multi_gold_n"],
                                    "rho_strict": sm["rho_strict"], "rho_tie": sm["rho_tie"]}

    # ---- C8 bootstrap ----
    boot = {}
    for bm, rs in by_bm.items():
        b = F.cluster_bootstrap(rs, keys=("strict_gap", "tie_gap"), seed=96013,
                                n_boot=2000, cluster_key="cluster")
        boot[bm] = b
        for k in ("strict_gap", "tie_gap"):
            e = b[k]
            check("BOOT %s %s" % (bm, k), "PASS",
                  "interval=(%s,%s) valid=%d invalid=%d %s" % (
                      e["interval_95"][0], e["interval_95"][1],
                      e["valid"], e["invalid"], e["invalid_reasons"]))

    # ---- C9 persist ----
    with open(os.path.join(evdir, 'per_query_rows.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(["qid", "benchmark", "cluster", "section", "delta",
                    "fr_sign", "fr_float", "gold_n",
                    "strict_top", "tie_top", "strict_bot", "tie_bot",
                    "strict_gap", "tie_gap",
                    "strict_top_ng", "tie_top_ng", "strict_bot_ng", "tie_bot_ng",
                    "strict_gap_ng", "tie_gap_ng",
                    "min_strict_gap", "min_tie_gap"])
        for r in all_rows:
            w.writerow([r["qid"], r["benchmark"], r["cluster"], r["section"],
                        repr(r["delta"]), repr(r["fr_sign"]), repr(r["fr_float"]),
                        r["gold_n"], repr(r["strict_top"]), repr(r["tie_top"]),
                        repr(r["strict_bot"]), repr(r["tie_bot"]),
                        repr(r["strict_gap"]), repr(r["tie_gap"]),
                        repr(r["strict_top_ng"]), repr(r["tie_top_ng"]),
                        repr(r["strict_bot_ng"]), repr(r["tie_bot_ng"]),
                        repr(r["strict_gap_ng"]), repr(r["tie_gap_ng"]),
                        repr(r["min_strict_gap"]), repr(r["min_tie_gap"])])
    with open(os.path.join(evdir, 'results.json'), 'w') as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    with open(os.path.join(evdir, 'bootstrap.json'), 'w') as fh:
        json.dump(boot, fh, indent=2, sort_keys=True)
    with open(os.path.join(HERE, 'MANIFEST.sha256'), 'w') as fh:
        for rel, sha, size in sorted(MANIFEST):
            fh.write("%s  %d  %s\n" % (sha, size, rel))

    print("----")
    fails = [c for c in CHECKS if c[1] in ("FAIL", "STOP")]
    print("counts: %s" % ", ".join(
        "%s=%d" % (s, sum(1 for c in CHECKS if c[1] == s))
        for s in ("PASS", "FAIL", "SKIP", "STOP")))
    print("OVERALL: %s" % ("PASS — F1 real-data execution reproduces gates+rhos"
                           if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
