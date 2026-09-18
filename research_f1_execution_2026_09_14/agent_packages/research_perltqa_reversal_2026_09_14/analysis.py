# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""PerLTQA reversal characterisation — first-hand re-derivation from E1/campaign caches.

PREPARED, NOT ACCEPTED. Reads ONLY committed E1/campaign benchmark caches via
`git show origin/<branch>:<path>` (no checkout, no network, no BEAM/Task4F1 material).
Stdlib only. Writes evidence/results.json inside this namespace.

Usage:
  python3 analysis.py --parts facts,geometry,h1
  python3 analysis.py --parts xbench
  python3 analysis.py --parts all
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import defaultdict

BRANCH = "origin/research/e1-mechanism-checkpoint-frozen-2026-09-13"
P_PERLTQA = "campaign_2026_09_13/bench3/b3b_perltqa/results.json"
P_RT = "campaign_2026_09_13/bench3/b3a_realtalk/details.json"
P_LME_Q = "docs/v52/task4c2/V52_T4C2_question_level.csv"
P_LME_TIE = "docs/v52/task4c2/V52_T4C2_tie_diagnostics.csv"

# E1-claimed input hashes (to verify we read the same bytes E1 used).
E1_PERLTQA_SHA256 = "ec9b8b2c7f384fe2f56c72fdc7a7216930a9db35eda2c4441496c8ad401bf958"
E1_RT_SHA256 = "8bae1d380240adc856f8a787b142286efc16fd1d30dfc03bed7e5074769d1757"


def git_show(branch, path):
    p = subprocess.run(["git", "show", "%s:%s" % (branch, path)],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git show failed for %s:%s: %s"
                           % (branch, path, p.stderr.decode()[:300]))
    return p.stdout


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def quantile_sorted(s, q):
    # linear interpolation on sorted list; q in [0,1]
    n = len(s)
    if n == 0:
        return None
    if n == 1:
        return float(s[0])
    pos = q * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def dist(xs):
    s = sorted(float(x) for x in xs)
    n = len(s)
    return {
        "n": n,
        "mean": mean(s),
        "min": s[0] if s else None,
        "max": s[-1] if s else None,
        "p10": quantile_sorted(s, 0.10),
        "p25": quantile_sorted(s, 0.25),
        "p50": quantile_sorted(s, 0.50),
        "p75": quantile_sorted(s, 0.75),
        "p90": quantile_sorted(s, 0.90),
    }


def _avg_ranks(xs):
    # average ranks for ties, 1-based
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx ** 0.5 * syy ** 0.5)


def spearman(xs, ys):
    return pearson(_avg_ranks(list(xs)), _avg_ranks(list(ys)))


def sgn(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def load_perltqa():
    raw = git_show(BRANCH, P_PERLTQA)
    return sha256_hex(raw), json.loads(raw.decode("utf-8"))


def perltqa_facts(doc):
    """Re-derive headline + section deltas + composition sum (full precision)."""
    pq = doc["per_q"]
    out = {"n_qa": len(pq), "K": doc.get("K"), "NT": doc.get("NT")}
    secs = defaultdict(list)
    for qid, r in pq.items():
        secs[r["section"]].append(r)
    by_section = {}
    for s in sorted(secs):
        rs = secs[s]
        n = len(rs)
        mn = mean([r["native"] for r in rs])
        mf = mean([r["float"] for r in rs])
        by_section[s] = {
            "n": n,
            "mean_native": mn,
            "mean_float": mf,
            "delta_pp": 100.0 * (mn - mf),
        }
    all_n = mean([r["native"] for r in pq.values()])
    all_f = mean([r["float"] for r in pq.values()])
    out["overall"] = {"n": len(pq), "mean_native": all_n, "mean_float": all_f,
                      "delta_pp": 100.0 * (all_n - all_f)}
    out["by_section"] = by_section
    # composition: sum over sections of n_s * delta_s / N
    comp = sum(v["n"] * v["delta_pp"] for v in by_section.values()) / len(pq)
    out["composition_recomputed_pp"] = comp
    out["composition_residual_vs_overall"] = comp - out["overall"]["delta_pp"]
    # W/T/L on per-query Delta sign (fractional-recall means over NT perms)
    wtl = {}
    for s in sorted(secs):
        w = sum(1 for r in secs[s] if r["native"] - r["float"] > 0)
        t = sum(1 for r in secs[s] if r["native"] - r["float"] == 0)
        lo = sum(1 for r in secs[s] if r["native"] - r["float"] < 0)
        wtl[s] = {"W": w, "T": t, "L": lo}
    w = sum(1 for r in pq.values() if r["native"] - r["float"] > 0)
    t = sum(1 for r in pq.values() if r["native"] - r["float"] == 0)
    lo = sum(1 for r in pq.values() if r["native"] - r["float"] < 0)
    wtl["_overall"] = {"W": w, "T": t, "L": lo}
    out["wtl"] = wtl
    return out


def perltqa_geometry(doc):
    """Distributions per section for every committed per-q geometric field."""
    pq = doc["per_q"]
    secs = defaultdict(list)
    for qid, r in pq.items():
        secs[r["section"]].append((qid, r))
    geo = {}
    for s in sorted(secs):
        rows = [r for _, r in secs[s]]
        deltas = [100.0 * (r["native"] - r["float"]) for r in rows]
        p64 = [float(r["BOT64"]) - float(r["TOP64"]) for r in rows]
        ties = [int(r["tie"]) for r in rows]
        tbcs = [int(r["tie_bc"]) for r in rows]
        gaps = [float(r["gap"]) for r in rows]
        gsizes = [int(r["gold_size"]) for r in rows]
        g = {
            "n": len(rows),
            "delta_pp": dist(deltas),
            "p64": dist(p64),
            "tie_rate": mean(ties),
            "tie_n": sum(ties),
            "tie_bc": dist(tbcs),
            "gap": dist(gaps),
            "p_gap_eq_0": mean([1 if x == 0 else 0 for x in gaps]),
            "p_tiebc_ge_3": mean([1 if x >= 3 else 0 for x in tbcs]),
            "native": dist([r["native"] for r in rows]),
            "float": dist([r["float"] for r in rows]),
            "top64": dist([r["TOP64"] for r in rows]),
            "bot64": dist([r["BOT64"] for r in rows]),
            "gold_size_values": sorted(set(gsizes)),
            "gold_size_mean": mean(gsizes),
        }
        if len(set(gsizes)) <= 12:
            g["gold_size_counts"] = {str(k): gsizes.count(k) for k in sorted(set(gsizes))}
        else:
            hist = defaultdict(int)
            for v in gsizes:
                hist[v] += 1
            g["gold_size_counts"] = {str(k): hist[k] for k in sorted(hist)}
        # sign fractions (nonzero-Delta queries)
        nz = [d for d in deltas if d != 0]
        g["frac_delta_pos_nz"] = (sum(1 for d in nz if d > 0) / len(nz)) if nz else None
        nzp = [v for v in p64 if v != 0]
        g["frac_p64_pos_nz"] = (sum(1 for v in nzp if v > 0) / len(nzp)) if nzp else None
        geo[s] = g
    return geo


def perltqa_within_archive(doc):
    """Character x section means; joint Delta/P64 flip counts (E1 replication)."""
    pq = doc["per_q"]
    cell = defaultdict(list)
    for qid, r in pq.items():
        cell[(r["char"], r["section"])].append(r)
    chars = sorted({c for c, _ in cell})
    sections = ["profile", "social_relationship", "events", "dialogues"]
    rows = []
    for c in chars:
        rec = {"char": c}
        for s in sections:
            rr = cell.get((c, s), [])
            if rr:
                rec[s] = {"n": len(rr),
                          "delta_pp": 100.0 * (mean([r["native"] for r in rr])
                                               - mean([r["float"] for r in rr])),
                          "p64": mean([r["BOT64"] - r["TOP64"] for r in rr]),
                          "tie_rate": mean([r["tie"] for r in rr]),
                          "mean_gap": mean([r["gap"] for r in rr]),
                          "mean_tiebc": mean([r["tie_bc"] for r in rr])}
            else:
                rec[s] = None
        rows.append(rec)
    valid = [r for r in rows if r["profile"] and r["events"]]
    counts = {
        "n_chars": len(chars),
        "n_archives_profile_and_events": len(valid),
        "profile_delta_positive": sum(sgn(r["profile"]["delta_pp"]) > 0 for r in valid),
        "events_delta_negative": sum(sgn(r["events"]["delta_pp"]) < 0 for r in valid),
        "profile_p64_positive": sum(sgn(r["profile"]["p64"]) > 0 for r in valid),
        "events_p64_negative": sum(sgn(r["events"]["p64"]) < 0 for r in valid),
        "delta_profile_pos_events_neg":
            sum(sgn(r["profile"]["delta_pp"]) > 0 and sgn(r["events"]["delta_pp"]) < 0
                for r in valid),
        "p64_profile_pos_events_neg":
            sum(sgn(r["profile"]["p64"]) > 0 and sgn(r["events"]["p64"]) < 0
                for r in valid),
        "both_joint_flip":
            sum(sgn(r["profile"]["delta_pp"]) > 0 and sgn(r["events"]["delta_pp"]) < 0
                and sgn(r["profile"]["p64"]) > 0 and sgn(r["events"]["p64"]) < 0
                for r in valid),
    }
    pairs = []
    for r in rows:
        for s in sections:
            x = r[s]
            if x and x["delta_pp"] != 0 and x["p64"] != 0:
                pairs.append((sgn(x["delta_pp"]), sgn(x["p64"])))
    counts["char_section_nonzero_pairs"] = len(pairs)
    counts["char_section_same_sign"] = sum(a == b for a, b in pairs)
    counts["char_section_same_sign_fraction"] = (
        sum(a == b for a, b in pairs) / len(pairs)) if pairs else None
    return {"rows": rows, "counts": counts}


def h1_competition_test_perltqa(doc):
    """H1: denser native Hamming boundary competition -> SIGN loses.

    Predictors use ONLY native-ranking fields (tie/tie_bc/gap), never Delta.
    Rules predict per-query Delta sign; rhos measure association strength.
    """
    pq = doc["per_q"]
    secs = defaultdict(list)
    for qid, r in pq.items():
        secs[r["section"]].append(r)
    out = {}
    # section-mean ordering test: does sparser competition go with winning?
    out["section_means"] = {
        s: {"delta_pp": 100.0 * (mean([r["native"] for r in rs])
                                 - mean([r["float"] for r in rs])),
            "tie_rate": mean([r["tie"] for r in rs]),
            "mean_tiebc": mean([r["tie_bc"] for r in rs]),
            "mean_gap": mean([r["gap"] for r in rs])}
        for s, rs in secs.items()
    }
    # per-query rules -> accuracy predicting sign(Delta)
    all_rows = list(pq.values())
    out["rules_overall"] = h1_rule_accuracies(all_rows)
    out["rules_by_section"] = {s: h1_rule_accuracies(rs) for s, rs in secs.items()}
    # rank associations (Delta vs competition), overall + by section
    out["spearman_overall"] = h1_spear(all_rows)
    out["spearman_by_section"] = {s: h1_spear(rs) for s, rs in secs.items()}
    return out


def h1_rule_accuracies(rows):
    def acc(pred, actual):
        ok = sum(1 for p, a in zip(pred, actual) if p == a)
        n = len(actual)
        return {"n": n, "acc": ok / n if n else None, "ok": ok}
    delta_sgn = [sgn(100.0 * (r["native"] - r["float"])) for r in rows]
    # rule A: predict Delta<0 iff native boundary tie
    pred_a = [-1 if int(r["tie"]) == 1 else 1 for r in rows]
    # rule B: predict Delta<0 iff Hamming gap == 0
    pred_b = [-1 if float(r["gap"]) == 0 else 1 for r in rows]
    # rule C: predict Delta<0 iff tie_bc >= 3 (heavy boundary mass)
    pred_c = [-1 if int(r["tie_bc"]) >= 3 else 1 for r in rows]
    # baseline (non-causal retrieval contrast): predict sign(Delta)=sign(P64)
    p64 = [float(r["BOT64"]) - float(r["TOP64"]) for r in rows]
    nz = [(p, d) for p, d in zip(p64, delta_sgn) if p != 0 and d != 0]
    base_acc = (sum(1 for p, d in nz if sgn(p) == d) / len(nz)) if nz else None

    def acc_nz(pred):
        pairs = [(p, d) for p, d in zip(pred, delta_sgn) if d != 0]
        ok = sum(1 for p, d in pairs if p == d)
        return {"n_nonzero_delta": len(pairs), "acc": ok / len(pairs) if pairs else None,
                "ok": ok}
    out = {
        "ruleA_tie_predicts_loss": acc(pred_a, delta_sgn),
        "ruleB_gap0_predicts_loss": acc(pred_b, delta_sgn),
        "ruleC_tiebc_ge3_predicts_loss": acc(pred_c, delta_sgn),
        "baseline_signP64_predicts_signDelta": {"n_nonzero_both": len(nz), "acc": base_acc},
    }
    out["ruleA_nonzero_cond"] = acc_nz(pred_a)
    out["ruleB_nonzero_cond"] = acc_nz(pred_b)
    out["ruleC_nonzero_cond"] = acc_nz(pred_c)
    return out


def h1_spear(rows):
    d = [100.0 * (r["native"] - r["float"]) for r in rows]
    return {
        "n": len(rows),
        "rho_delta_vs_tiebc": spearman(d, [int(r["tie_bc"]) for r in rows]),
        "rho_delta_vs_gap": spearman(d, [float(r["gap"]) for r in rows]),
        "rho_delta_vs_p64": spearman(
            d, [float(r["BOT64"]) - float(r["TOP64"]) for r in rows]),
    }


def xbench_realtalk():
    """H1 adversarial test on REALTALK (committed per-qa arms + tie fields)."""
    raw = git_show(BRANCH, P_RT)
    doc = json.loads(raw.decode("utf-8"))
    rows = [r for r in doc["per_qa"] if r.get("valid") == 1]
    rec = {"n_qa": doc.get("n_qa"), "n_valid": len(rows),
           "sha256_match_e1": sha256_hex(raw) == E1_RT_SHA256}
    for r in rows:
        r["_delta"] = float(r["arms"]["NATIVE96"]) - float(r["arms"]["FLOAT96"])
        r["_p64"] = float(r["arms"]["BOT64"]) - float(r["arms"]["TOP64"])
        r["_tie"] = int(r["tie"]["boundary_tie"])
        r["_gap"] = float(r["tie"]["tail_gap"])
    rec["overall"] = {"mean_delta_pp": 100.0 * mean([r["_delta"] for r in rows]),
                      "mean_p64": mean([r["_p64"] for r in rows]),
                      "tie_rate": mean([r["_tie"] for r in rows]),
                      "mean_gap": mean([r["_gap"] for r in rows])}
    ds = [sgn(r["_delta"]) for r in rows]
    pred_a = [-1 if r["_tie"] == 1 else 1 for r in rows]
    pred_b = [-1 if r["_gap"] == 0 else 1 for r in rows]
    rec["ruleA_tie_predicts_loss_acc"] = (
        sum(1 for p, d in zip(pred_a, ds) if p == d) / len(ds))
    rec["ruleB_gap0_predicts_loss_acc"] = (
        sum(1 for p, d in zip(pred_b, ds) if p == d) / len(ds))
    nz_idx = [i for i, d in enumerate(ds) if d != 0]
    for nm, pr in (("ruleA_nonzero_cond", pred_a), ("ruleB_nonzero_cond", pred_b)):
        ok = sum(1 for i in nz_idx if pr[i] == ds[i])
        rec[nm] = {"n_nonzero_delta": len(nz_idx),
                   "acc": ok / len(nz_idx) if nz_idx else None}
    nz = [(r["_p64"], d) for r, d in zip(rows, ds) if r["_p64"] != 0 and d != 0]
    rec["baseline_signP64_acc"] = {"n_nonzero_both": len(nz),
                                   "acc": (sum(1 for p, d in nz if sgn(p) == d) / len(nz)
                                           if nz else None)}
    rec["spearman"] = {
        "rho_delta_vs_tie": spearman([r["_delta"] for r in rows],
                                     [r["_tie"] for r in rows]),
        "rho_delta_vs_gap": spearman([r["_delta"] for r in rows],
                                     [r["_gap"] for r in rows]),
        "rho_delta_vs_p64": spearman([r["_delta"] for r in rows],
                                     [r["_p64"] for r in rows]),
    }
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[str(r["cat"])].append(r)
    rec["by_category"] = {
        c: {"n": len(rs),
            "mean_delta_pp": 100.0 * mean([r["_delta"] for r in rs]),
            "mean_p64": mean([r["_p64"] for r in rs]),
            "tie_rate": mean([r["_tie"] for r in rs]),
            "mean_gap": mean([r["_gap"] for r in rs])}
        for c, rs in sorted(by_cat.items())
    }
    # gold-count control
    gc = defaultdict(list)
    for r in rows:
        gc[int(r["gold_count"])].append(r["_delta"])
    rec["gold_count_groups"] = {str(k): {"n": len(v), "mean_delta_pp": 100.0 * mean(v)}
                                for k, v in sorted(gc.items())}
    return rec


def xbench_lme():
    """H1 adversarial test on LongMemEval (T4C2 question_level + tie_diagnostics)."""
    q_raw = git_show(BRANCH, P_LME_Q)
    t_raw = git_show(BRANCH, P_LME_TIE)
    q_rows = list(csv.DictReader(io.StringIO(q_raw.decode("utf-8"))))
    t_rows = list(csv.DictReader(io.StringIO(t_raw.decode("utf-8"))))
    tie = {}
    for r in t_rows:
        if r.get("method") == "SIGN96_CENTERED":
            tie[r["question_id"]] = r
    rec = {"n_question_level": len(q_rows), "n_tie_sign_rows": len(tie)}
    joined = []
    for r in q_rows:
        qid = r["question_id"]
        if qid not in tie:
            continue
        t = tie[qid]
        joined.append({
            "qid": qid,
            "qtype": r.get("question_type"),
            "delta_pp": float(r["sign_minus_centered_float_fractional_pp"]),
            "gold_count": int(float(r.get("gold_count") or 0)),
            "top3_tie": int(float(t.get("top3_boundary_tie") or 0)),
            "cand_at_bnd": float(t.get("candidates_at_top3_boundary_distance") or 0),
            "slots": float(t.get("slots_remaining_at_boundary") or 0),
            "min_d": float(t.get("min_hamming_distance") or 0),
        })
    rec["n_joined"] = len(joined)
    rec["overall"] = {"mean_delta_pp": mean([j["delta_pp"] for j in joined]),
                      "tie_rate": mean([j["top3_tie"] for j in joined]),
                      "mean_cand_at_bnd": mean([j["cand_at_bnd"] for j in joined])}
    ds = [sgn(j["delta_pp"]) for j in joined]
    pred_a = [-1 if j["top3_tie"] == 1 else 1 for j in joined]
    pred_c = [-1 if j["cand_at_bnd"] >= 3 else 1 for j in joined]
    rec["ruleA_tie_predicts_loss_acc"] = (
        sum(1 for p, d in zip(pred_a, ds) if p == d) / len(ds))
    rec["ruleC_cand_ge3_predicts_loss_acc"] = (
        sum(1 for p, d in zip(pred_c, ds) if p == d) / len(ds))
    nz_idx = [i for i, d in enumerate(ds) if d != 0]
    for nm, pr in (("ruleA_nonzero_cond", pred_a), ("ruleC_nonzero_cond", pred_c)):
        ok = sum(1 for i in nz_idx if pr[i] == ds[i])
        rec[nm] = {"n_nonzero_delta": len(nz_idx),
                   "acc": ok / len(nz_idx) if nz_idx else None}
    rec["spearman"] = {
        "rho_delta_vs_cand_at_bnd": spearman([j["delta_pp"] for j in joined],
                                             [j["cand_at_bnd"] for j in joined]),
        "rho_delta_vs_top3_tie": spearman([j["delta_pp"] for j in joined],
                                          [j["top3_tie"] for j in joined]),
    }
    by_qt = defaultdict(list)
    for j in joined:
        by_qt[j["qtype"]].append(j)
    rec["by_question_type"] = {
        k: {"n": len(v), "mean_delta_pp": mean([j["delta_pp"] for j in v]),
            "tie_rate": mean([j["top3_tie"] for j in v])}
        for k, v in sorted(by_qt.items())
    }
    gc = defaultdict(list)
    for j in joined:
        gc[j["gold_count"]].append(j["delta_pp"])
    rec["gold_count_groups"] = {str(k): {"n": len(v), "mean_delta_pp": mean(v)}
                                for k, v in sorted(gc.items())}
    return rec


def xbench_locomo_availability():
    """Probe: is any committed per-query LoCoMo Delta surface present in git?

    Expected outcome per E1 checkpoint S8: no committed per-query centered-float
    surface for LoCoMo (R2 numbers are Drive-backed, not in git). Record exactly
    what was checked so the gap is auditable.
    """
    checks = []
    # 1. taskC_LoCoMo_perq arms (same 5-arm layout as LME: no FLOAT expected)
    try:
        raw = git_show(
            BRANCH, "campaign_2026_09_13/audits/audit1_cont/taskC_LoCoMo_perq.json")
        doc = json.loads(raw.decode("utf-8"))
        arms = sorted(doc.get("per_arm", {}).keys())
        checks.append({"file": "audits/audit1_cont/taskC_LoCoMo_perq.json",
                       "present": True,
                       "arms": arms,
                       "has_float_arm": any("FLOAT" in a.upper() for a in arms),
                       "n_qids": len(doc.get("qids", []))})
    except Exception as e:
        checks.append({"file": "audits/audit1_cont/taskC_LoCoMo_perq.json",
                       "present": False, "error": str(e)[:200]})
    # 2. regen locomo stats
    for path in ("campaign_2026_09_13/regen/locomo/counts_report.json",
                 "campaign_2026_09_13/regen/locomo/task1_locoMo_stats.json"):
        try:
            raw = git_show(BRANCH, path)
            doc = json.loads(raw.decode("utf-8"))
            keys = list(doc.keys())[:10] if isinstance(doc, dict) else ["list:%d" % len(doc)]
            checks.append({"file": path, "present": True, "top_keys": keys})
        except Exception as e:
            checks.append({"file": path, "present": False, "error": str(e)[:200]})
    return {"checks": checks,
            "verdict": "NO committed per-query LoCoMo SIGN-minus-float surface "
                       "found in git under the frozen E1 branch; cross-benchmark "
                       "H1 recomputation for LoCoMo is UNAVAILABLE-UNDER-CACHE-GAP."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="all")
    ap.add_argument("--out", default="evidence/results.json")
    args = ap.parse_args()
    parts = set(args.parts.split(","))
    if "all" in parts:
        parts = {"facts", "geometry", "h1", "xbench"}
    res = {"provenance": {"branch": BRANCH,
                          "inputs": [P_PERLTQA, P_RT, P_LME_Q, P_LME_TIE],
                          "label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] "
                                   "[NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
                          "status": "PREPARED, NOT ACCEPTED"}}
    if parts & {"facts", "geometry", "h1"}:
        sha, doc = load_perltqa()
        res["perltqa_sha256"] = sha
        res["perltqa_sha256_match_e1"] = (sha == E1_PERLTQA_SHA256)
        if "facts" in parts:
            res["facts"] = perltqa_facts(doc)
            res["within_archive"] = perltqa_within_archive(doc)
        if "geometry" in parts:
            res["geometry"] = perltqa_geometry(doc)
        if "h1" in parts:
            res["h1_perltqa"] = h1_competition_test_perltqa(doc)
    if "xbench" in parts:
        res["xbench_realtalk"] = xbench_realtalk()
        res["xbench_lme"] = xbench_lme()
        res["xbench_locomo"] = xbench_locomo_availability()
    import os
    os.makedirs("evidence", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    print("wrote %s parts=%s" % (args.out, sorted(parts)))
    if "facts" in res:
        print("perltqa sha_match_e1=%s overall_delta_pp=%.10f composition=%.10f" % (
            res["perltqa_sha256_match_e1"], res["facts"]["overall"]["delta_pp"],
            res["facts"]["composition_recomputed_pp"]))
        for s, v in sorted(res["facts"]["by_section"].items()):
            print("  %-18s n=%5d native=%.6f float=%.6f delta_pp=%+.6f" % (
                s, v["n"], v["mean_native"], v["mean_float"], v["delta_pp"]))


if __name__ == "__main__":
    main()

