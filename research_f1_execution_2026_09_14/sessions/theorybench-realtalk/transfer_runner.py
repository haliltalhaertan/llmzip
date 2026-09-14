#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Model-H proxy transfer runner (REAL TALK only). Gate passed BEFORE this ran.

Per valid QA (705 of 728; 23 excluded with FR=null):
- groups from query only: order=rank by (abs(q_j), j); LOW48=first48,
  HIGH48=last48, FULL96=all. No gold inspected for grouping.
- t in {0.25,0.5,1,2,4}: scale BOTH doc and query coords in group by t.
  No refit/recenter. Cosine recomputes full norms (producer convention;
  RuntimeError on zero norm, same as producer).
- primary: EXACT expected fractional R@3 under uniform tie priorities:
  per gold g, P(g in top3)=min(1,(K-S_g)/(T_g+1)) for S_g<K else 0,
  S_g=#strictly-better, T_g=#tied-others (ties by exact ==: int Hamming,
  float64 scores). Per-QA score = mean over gold. Shared-gold formula;
  no independent-pair multinomial.
- MC 20-seed (producer seeds) native+float: at t=1 (gate identity; identical
  across groups) and at endpoints t=.25/4 per group (sensitivity).
- diagnostics: query_concentration=sum q^4/(sum q^2)^2;
  doc_rms_group/rms_complement over C entries (FULL96 complement=null).

Writes per_query.jsonl (705*3*5 rows), checkpoints/ per-chat pickle,
summary.json. Reads sources READ-ONLY.
"""
import json
import os
import pickle
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk")
REPRDIR = SRC / "rt_repr"
CKPT = HERE / "checkpoints"
K = 3
NT = 20
T_GRID = [0.25, 0.5, 1.0, 2.0, 4.0]
GROUPS = ["LOW48", "HIGH48", "FULL96"]
BOOT_SEED = 20260913
BOOT_REPS = 2000


def tie_seed(ci, t):
    return 5_100_000 + ci * 100_000 + t * 100 + 99


def cosine_centered(C, q):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if qn <= 0 or np.any(dn <= 0):
        raise RuntimeError("[BUG] zero centered vector norm in cosine")
    return (C @ q) / (dn * qn)


def frac_r3(order, gold):
    gset = set(map(int, gold))
    return len(set(map(int, order[:K])) & gset) / len(gset)


def exact_frac_r3_hamming(dnat, gold):
    dnat = np.asarray(dnat)
    tot = 0.0
    for g in gold:
        dg = dnat[g]
        s = int(np.count_nonzero(dnat < dg))
        t_ = int(np.count_nonzero(dnat == dg)) - 1
        tot += 0.0 if s >= K else min(1.0, (K - s) / (t_ + 1))
    return tot / len(gold)


def exact_frac_r3_float(scores, gold):
    scores = np.asarray(scores, dtype=np.float64)
    tot = 0.0
    for g in gold:
        sg = scores[g]
        s = int(np.count_nonzero(scores > sg))
        t_ = int(np.count_nonzero(scores == sg)) - 1
        tot += 0.0 if s >= K else min(1.0, (K - s) / (t_ + 1))
    return tot / len(gold)


def mc_scores(dnat, sscores, gold, pris):
    nat = sum(frac_r3(np.lexsort((p, dnat)), gold) for p in pris) / NT
    flt = sum(frac_r3(np.lexsort((p, -sscores)), gold) for p in pris) / NT
    return float(nat), float(flt)


def main():
    t0 = time.time()
    CKPT.mkdir(exist_ok=True)
    pkls = sorted(REPRDIR.glob("RT*.pkl"))
    assert len(pkls) == 10, len(pkls)
    details = json.loads((SRC / "details.json").read_text())
    exp_by_qid = {r["qid"]: r for r in details["per_qa"]}

    rows = []
    n_valid = 0
    n_excluded = 0
    for ci, p in enumerate(pkls):
        ck = CKPT / f"chat{ci:02d}.pkl"
        if ck.exists():
            chat_rows = pickle.loads(ck.read_bytes())
            rows.extend(chat_rows)
            n_valid += sum(1 for r in chat_rows if r["t"] == 1.0 and r["group"] == "LOW48")
            n_excluded += 0  # recomputed below from cache directly
            print(f"chat {ci}: loaded {len(chat_rows)} rows from checkpoint", flush=True)
            continue
        o = pickle.loads(p.read_bytes())
        C = np.asarray(o["C"], float)
        QC = np.asarray(o["QC"], float)
        n = C.shape[0]
        D0 = C >= 0
        pris = [np.random.default_rng(tie_seed(ci, t)).random(n) for t in range(NT)]
        chat_rows = []
        for qi, qid in enumerate(o["qids"]):
            gold = [int(g) for g in o["gold_rows"][qi]]
            if not gold:
                continue
            n_valid += 1
            q = QC[qi].astype(float)
            order = np.lexsort((np.arange(96), np.abs(q)))
            low = np.sort(order[:48])
            high = np.sort(order[48:])
            full = np.arange(96)
            gmap = {"LOW48": low, "HIGH48": high, "FULL96": full}
            q2 = float(q @ q)
            qconc = float(np.sum(q ** 4) / (q2 ** 2)) if q2 > 0 else None
            rms = {}
            for gn, cols in gmap.items():
                comp = np.delete(full, cols) if gn != "FULL96" else np.array([], dtype=int)
                rms[gn] = (float(np.sqrt(np.mean(C[:, cols] ** 2))),
                           (float(np.sqrt(np.mean(C[:, comp] ** 2))) if comp.size else None))
            # baseline (unscaled) MC once: identical for all groups at t=1
            Q0 = q >= 0
            dnat0 = np.count_nonzero(D0 != Q0[None, :], axis=1)
            s0 = cosine_centered(C, q)
            mc_nat1, mc_flt1 = mc_scores(dnat0, s0, gold, pris)
            for gn, cols in gmap.items():
                sgn = np.array_equal(cols, full)
                for t in T_GRID:
                    if t == 1.0:
                        Ct, qt = C, q
                    else:
                        Ct = C.copy()
                        Ct[:, cols] = Ct[:, cols] * t
                        qt = q.copy()
                        qt[cols] = qt[cols] * t
                    Q0t = qt >= 0
                    dnatt = np.count_nonzero((Ct >= 0) != Q0t[None, :], axis=1)
                    st = cosine_centered(Ct, qt)
                    se = exact_frac_r3_hamming(dnatt, gold)
                    fe = exact_frac_r3_float(st, gold)
                    rec = {
                        "qid": qid, "chat": o["chat_no"], "file": o["file"],
                        "cat": int(o["cats"][qi]), "N": n,
                        "gold_count": len(gold), "group": gn, "t": t,
                        "group_idx": sorted(map(int, cols)) if (t == 1.0 and not sgn) else ([] if sgn else None),
                        "sign_exact": se, "float_exact": fe,
                        "delta_exact": se - fe,
                        "sign_mc": None, "float_mc": None,
                        "query_concentration": qconc,
                        "doc_rms_group": rms[gn][0],
                        "doc_rms_complement": rms[gn][1],
                    }
                    if t == 1.0:
                        rec["sign_mc"] = mc_nat1
                        rec["float_mc"] = mc_flt1
                    elif t in (0.25, 4.0):
                        mn, mf = mc_scores(dnatt, st, gold, pris)
                        rec["sign_mc"] = mn
                        rec["float_mc"] = mf
                    chat_rows.append(rec)
        with open(ck, "wb") as f:
            pickle.dump(chat_rows, f, protocol=4)
        rows.extend(chat_rows)
        print(f"chat {ci}: computed {len(chat_rows)} rows ({time.time()-t0:.1f}s)", flush=True)

    assert n_valid == 705, n_valid
    assert len(rows) == 705 * 3 * 5, len(rows)
    # excluded count from code (caches), not memory
    n_tot = sum(len(pickle.loads(p.read_bytes())["qids"]) for p in pkls)
    assert n_tot == 728, n_tot

    with open(HERE / "per_query.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # ---- summary ----
    arr = {(g, t): [] for g in GROUPS for t in T_GRID}
    for r in rows:
        arr[(r["group"], r["t"])].append(r)
    curves = {}
    for key, rs in arr.items():
        s = np.array([r["sign_exact"] for r in rs])
        fl = np.array([r["float_exact"] for r in rs])
        d = s - fl
        curves[f"{key[0]}@t={key[1]}"] = {
            "n": len(rs), "sign_mean": float(s.mean()),
            "float_mean": float(fl.mean()), "delta_mean": float(d.mean())}

    def endpoint_contrast(group):
        lo = np.array([r["delta_exact"] for r in rows if r["group"] == group and r["t"] == 0.25])
        hi = np.array([r["delta_exact"] for r in rows if r["group"] == group and r["t"] == 4.0])
        return hi - lo

    rng = np.random.default_rng(BOOT_SEED)
    chats = sorted(set(r["chat"] for r in rows if r["group"] == "LOW48" and r["t"] == 0.25))
    by_chat_low = {c: endpoint_contrast("LOW48")[
        np.array([r["chat"] for r in rows if r["group"] == "LOW48" and r["t"] == 0.25]) == c] for c in chats}
    by_chat_high = {c: endpoint_contrast("HIGH48")[
        np.array([r["chat"] for r in rows if r["group"] == "HIGH48" and r["t"] == 0.25]) == c] for c in chats}

    def cluster_boot(by_chat, reps=BOOT_REPS):
        per = []
        cs = list(by_chat)
        for _ in range(reps):
            samp = [by_chat[c] for c in rng.choice(cs, size=len(cs), replace=True)]
            cat = np.concatenate(samp)
            per.append(float(cat.mean()))
        return per

    boot_low = cluster_boot(by_chat_low)
    boot_high = cluster_boot(by_chat_high)
    eff_low = float(np.mean(boot_low))
    eff_high = float(np.mean(boot_high))
    ci_low = [float(np.percentile(boot_low, 2.5)), float(np.percentile(boot_low, 97.5))]
    ci_high = [float(np.percentile(boot_high, 2.5)), float(np.percentile(boot_high, 97.5))]

    # fraction with any decreasing adjacent delta
    dec = {}
    for gn in GROUPS:
        qs = set(r["qid"] for r in rows if r["group"] == gn)
        nd = 0
        for qid in qs:
            d = [next(r["delta_exact"] for r in rows
                      if r["qid"] == qid and r["group"] == gn and r["t"] == t) for t in T_GRID]
            if any(b < a for a, b in zip(d, d[1:])):
                nd += 1
        dec[gn] = {"n_qa": len(qs), "n_decreasing": nd, "frac": nd / len(qs)}

    # invariance diagnostics
    sign_inv_viol = 0
    full_cos_ulpmax = 0.0
    full_rank_changed = 0
    t1_viol = 0
    for qid in set(r["qid"] for r in rows):
        for gn in GROUPS:
            ss = [next(r["sign_exact"] for r in rows
                       if r["qid"] == qid and r["group"] == gn and r["t"] == t) for t in T_GRID]
            if not all(v == ss[2] for v in ss):
                sign_inv_viol += 1
        fl = [next(r["float_exact"] for r in rows
                   if r["qid"] == qid and r["group"] == "FULL96" and r["t"] == t) for t in T_GRID]
        full_cos_ulpmax = max(full_cos_ulpmax, max(abs(v - fl[2]) for v in fl))
        base = [next(r["sign_exact"] for r in rows
                     if r["qid"] == qid and r["group"] == gn and r["t"] == 1.0) for gn in GROUPS]
        if not (base[0] == base[1] == base[2]):
            t1_viol += 1

    # per-category endpoint contrast (secondary)
    cats = {}
    for c in (1, 2, 3):
        l = np.array([r["delta_exact"] for r in rows
                      if r["group"] == "LOW48" and r["t"] == 4.0 and r["cat"] == c]) - \
            np.array([r["delta_exact"] for r in rows
                      if r["group"] == "LOW48" and r["t"] == 0.25 and r["cat"] == c])
        cats[str(c)] = {"n": int(l.size), "contrast_mean": float(l.mean())}

    # MC sensitivity at endpoints
    mc_sens = {}
    for gn in GROUPS:
        for t in (0.25, 1.0, 4.0):
            s = np.mean([r["sign_mc"] for r in rows if r["group"] == gn and r["t"] == t])
            fl = np.mean([r["float_mc"] for r in rows if r["group"] == gn and r["t"] == t])
            mc_sens[f"{gn}@t={t}"] = {"sign_mc_mean": float(s), "float_mc_mean": float(fl),
                                      "delta_mc_mean": float(s - fl)}

    summary = {
        "label": "[LOCAL EXPLORATORY PILOT]",
        "n_valid": 705, "n_total": 728, "n_excluded": 23,
        "n_clusters": len(chats), "clusters": chats,
        "t_grid": T_GRID, "groups": GROUPS,
        "curves_exact": curves,
        "primary": {"group": "LOW48", "effect": eff_low, "ci95": ci_low,
                    "rule": "effect>0 with CI excluding zero = consistent with proxy transfer",
                    "assessment": ("consistent with proxy transfer" if (eff_low > 0 and ci_low[0] > 0)
                                   else ("negative" if eff_low <= 0 else "inconclusive"))},
        "high48_comparison": {"effect": eff_high, "ci95": ci_high},
        "decreasing_adjacent_frac": dec,
        "invariance": {"sign_t_invariance_violations": sign_inv_viol,
                       "t1_identity_violations": t1_viol,
                       "full96_float_maxabs_vs_t1": full_cos_ulpmax},
        "per_category_low48_contrast_secondary": cats,
        "mc_sensitivity": mc_sens,
        "bootstrap": {"reps": BOOT_REPS, "seed": BOOT_SEED,
                      "note": "10 clusters: few-cluster bootstrap is approximate; raw effects reported"},
        "elapsed_s": time.time() - t0,
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"rows": len(rows), "primary": summary["primary"],
                      "high48": summary["high48_comparison"],
                      "decreasing": dec, "invariance": summary["invariance"],
                      "elapsed_s": summary["elapsed_s"]}, indent=2))


if __name__ == "__main__":
    main()
