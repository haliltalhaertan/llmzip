"""LOCAL EXPLORATORY PILOT — axis-structure attack on the frozen LongMemEval 470 benchmark.

[LOCAL PILOT — NOT PREREGISTERED — NOT FOR CITATION — DISCLOSE-BEFORE-USE]
This computes exploratory retrieval outcomes on the frozen benchmark, locally, to inform
(not to replace) any future preregistered experiment. If these outcomes ever inform a
preregistration, this pilot must be disclosed (standard exploratory->confirmatory hygiene).

Method fidelity: the evaluation protocol (codes, Hamming distance, tie priorities, metric)
is taken VERBATIM from the byte-frozen Task4C3 producer (sha256 8dce37b1...):
  - codes: D = (C >= 0), Q = (qC >= 0); d = count_nonzero(D != Q, axis=1)
  - tie protocol: priority_t = default_rng(stable_archive_seed(lex, t) + 99).random(n), t=0..19
    with stable_archive_seed(lex, t) = 5_100_000 + lex*100_000 + t*100 (adapter v1, frozen)
  - ranking: np.lexsort((priority, distance)); metric: (ANY, ALL, Fractional) evidence R@3
  - K=3, NT=20; lex = lexical ordinal of the question_id among ALL 500 dataset qids
GATE E0: our per-question native Fractional R@3 must reproduce the frozen
V52_T4C3_question_level.csv per-question values (470/470 within 1e-12) and the aggregate
0.5419751773049646.

Experiments:
  E1  budget curve: native sign restricted to the top-k variance axes (k=8..96, archive-local,
      gold-free), plus random-subset and bottom-k baselines.
  E2  per-axis: drop-one-bit loss and alone (1-bit) FR for each of the 96 axes.
  E3  per-axis gold discrimination: P(sign agrees with query | gold) - P(...| non-gold).
  E4  block-2 mixing, matched-variance-adjacent pairing vs the frozen random pairing
      (same rotation matrices; only the axis order differs) — mechanism discriminator.

Outputs -> pilots/axis_attack_2026-09-12/
"""
import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
DATASET = WORK / "drive" / "longmemeval_s_cleaned.json"
PKL_DIR = WORK / "regen" / "lme" / "cache_repr"
OUT = WORK / "pilots" / "axis_attack_2026-09-12"
FROZEN_QL = WORK / "drive" / "t4c3" / "V52_T4C3_question_level.csv"

K = 3
NT = 20
RSEEDS = [43001, 43002, 43003]          # 3 of the frozen 5 rotation seeds
K_LIST = [8, 16, 24, 32, 48, 64, 80, 96]
PUB_NATIVE_FR = 0.5419751773049646


def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100


def met(idx, g):
    s = set(map(int, idx)); gg = set(map(int, g)); x = len(s & gg)
    return float(x > 0), float(x == len(gg) and len(gg) > 0), float(x / len(gg))


def rh(d, p):
    return np.lexsort((p, np.asarray(d)))


def frac_r3(d, g, pr):
    return float(np.mean([met(rh(d, p)[:K], g)[2] for p in pr]))


def hspec_qs_only(seed, b):
    """Re-derive the block rotations exactly as the frozen hspec, but only qs (same rng draw
    sequence: permutation first, then one QR per block)."""
    r = np.random.default_rng(seed)
    r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return qs


def hspec(seed, b):
    r = np.random.default_rng(seed)
    perm = r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return perm, qs


def happly(X, perm, qs, b):
    xp = np.asarray(X, float)[..., perm]
    o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b)
        o[..., sl] = xp[..., sl] @ Q
    return o


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- lex ordinals over ALL 500 dataset qids ----
    data = json.loads(DATASET.read_text())
    allq = sorted(str(x["question_id"]) for x in data)
    lex = {q: i for i, q in enumerate(allq)}
    del data

    pkls = sorted(PKL_DIR.glob("*.pkl"))
    assert len(pkls) == 470, len(pkls)

    # frozen per-question reference
    frozen_q = {}
    if FROZEN_QL.exists():
        import csv
        with FROZEN_QL.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                frozen_q[row["question_id"]] = float(row["native_fractional_r3"])

    per_q_native = {}
    per_q_native_any = {}
    per_q_native_all = {}
    # aggregate accumulators
    e1_var = {k: [] for k in K_LIST}          # top-k variance
    e1_rnd = {k: [] for k in [16, 48]}        # random subsets
    e1_bot = {k: [] for k in [16, 48]}        # bottom-k variance
    e2_alone = np.zeros((470, 96))            # FR when ONLY axis j used
    e2_drop = np.zeros((470, 96))             # FR when axis j is dropped from the 96
    e3_delta = np.zeros((470, 96))            # gold-vs-nongold agreement gap per axis
    e3_goldrate = np.zeros((470, 96))
    var_rank = np.zeros((470, 96), dtype=np.int16)  # rank of variance per axis (0 = highest)
    e4_matched = {s: [] for s in RSEEDS}
    e4_random = {s: [] for s in RSEEDS}
    qids = []

    for qi, p in enumerate(pkls):
        with open(p, "rb") as f:
            o = pickle.loads(f.read())
        qid = o["question_id"]; C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
        n = len(C)
        qids.append(qid)
        D0 = C >= 0; Q0 = qC >= 0
        d0 = np.count_nonzero(D0 != Q0[None, :], axis=1).astype(np.int16)
        lx = lex[qid]
        pr = [np.random.default_rng(stable_archive_seed(lx, t) + 99).random(n) for t in range(NT)]

        # ---- E0: native ----
        m0 = [met(rh(d0, pz)[:K], g) for pz in pr]
        per_q_native[qid] = float(np.mean([m[2] for m in m0]))
        per_q_native_any[qid] = float(np.mean([m[0] for m in m0]))
        per_q_native_all[qid] = float(np.mean([m[1] for m in m0]))

        # ---- variance + ranks ----
        var = C.var(axis=0)
        order_desc = np.argsort(var, kind="stable")[::-1]
        var_rank[qi, order_desc] = np.arange(96)

        # ---- E1 ----
        for k in K_LIST:
            idx = order_desc[:k]
            dk = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1).astype(np.int16)
            e1_var[k].append(frac_r3(dk, g, pr))
        for k in [16, 48]:
            for s in range(3):
                idx = np.random.default_rng(12000 + s).choice(96, k, replace=False)
                dk = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1).astype(np.int16)
                e1_rnd[k].append(frac_r3(dk, g, pr))
            idx = order_desc[::-1][:k]
            dk = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1).astype(np.int16)
            e1_bot[k].append(frac_r3(dk, g, pr))

        # ---- E2 ----
        for j in range(96):
            bitj = (D0[:, j] != Q0[j])
            d_alone = bitj.astype(np.int16)
            e2_alone[qi, j] = frac_r3(d_alone, g, pr)
            d_drop = d0 - bitj.astype(np.int16)
            e2_drop[qi, j] = frac_r3(d_drop, g, pr)

        # ---- E3 ----
        gm = np.zeros(n, dtype=bool); gm[g] = True
        for j in range(96):
            agree = (D0[:, j] == Q0[j])
            e3_goldrate[qi, j] = float(agree[gm].mean())
            e3_delta[qi, j] = float(agree[gm].mean() - agree[~gm].mean())

        # ---- E4 ----
        for s in RSEEDS:
            perm_r, qs = hspec(s, 2)
            Cr = happly(C, perm_r, qs, 2); qr = happly(qC, perm_r, qs, 2)
            d = np.count_nonzero((Cr >= 0) != (qr >= 0)[None, :], axis=1).astype(np.int16)
            e4_random[s].append(frac_r3(d, g, pr))
            perm_v = np.argsort(var, kind="stable")   # ascending -> adjacent pairs = matched variance
            Cv = happly(C, perm_v, qs, 2); qv = happly(qC, perm_v, qs, 2)
            d = np.count_nonzero((Cv >= 0) != (qv >= 0)[None, :], axis=1).astype(np.int16)
            e4_matched[s].append(frac_r3(d, g, pr))

        if (qi + 1) % 50 == 0:
            print(f"  {qi+1}/470  ({time.time()-t0:.0f}s)", flush=True)

    # ---------- aggregate ----------
    nat = float(np.mean(list(per_q_native.values())))
    res = {"labels": ["[LOCAL EXPLORATORY PILOT]", "[NOT PREREGISTERED]", "[NOT FOR CITATION]",
                      "[DISCLOSE-BEFORE-USE]"],
           "protocol": "verbatim T4C3 eval (codes/threshold/tie/lexsort/metric); script 8dce37b1...; K=3 NT=20",
           "gate": {"native_fr_recomputed": nat, "native_fr_published": PUB_NATIVE_FR,
                    "abs_diff": abs(nat - PUB_NATIVE_FR)}}
    # per-question gate
    if frozen_q:
        diffs = [abs(per_q_native[q] - frozen_q[q]) for q in per_q_native if q in frozen_q]
        res["gate"]["per_question_compared"] = len(diffs)
        res["gate"]["per_question_max_abs_diff"] = max(diffs) if diffs else None
    res["E0_native"] = {"FR": nat,
                        "ANY": float(np.mean(list(per_q_native_any.values()))),
                        "ALL": float(np.mean(list(per_q_native_all.values())))}
    res["E1_budget_curve_topk_variance"] = {str(k): float(np.mean(v)) for k, v in e1_var.items()}
    res["E1_random_subset"] = {str(k): float(np.mean(e1_rnd[k])) for k in e1_rnd}
    res["E1_bottomk_variance"] = {str(k): float(np.mean(e1_bot[k])) for k in e1_bot}
    alone_mean = e2_alone.mean(axis=0); drop_mean = e2_drop.mean(axis=0)
    loss_mean = nat - drop_mean
    res["E2"] = {"alone_top10_axes": np.argsort(alone_mean)[::-1][:10].tolist(),
                 "alone_bottom10_axes": np.argsort(alone_mean)[:10].tolist(),
                 "alone_mean_min": float(alone_mean.min()), "alone_mean_max": float(alone_mean.max()),
                 "drop_loss_mean_min": float(loss_mean.min()), "drop_loss_mean_max": float(loss_mean.max()),
                 "n_axes_with_zero_or_negative_loss": int((loss_mean <= 0).sum()),
                 "pearson_mean_variance_rank_vs_neg_alone": float(np.corrcoef(var_rank.mean(axis=0), -alone_mean)[0, 1])}
    vals = []
    for qi in range(470):
        a = e2_alone[qi]
        if np.std(a) == 0:
            continue
        vals.append(np.corrcoef(var_rank[qi], -a)[0, 1])
    res["E2"]["within_question_corr_variance_rank_vs_neg_alone_mean"] = float(np.mean(vals)) if vals else None
    res["E3"] = {"delta_mean_over_axes": float(e3_delta.mean()),
                 "delta_positive_axes": int((e3_delta.mean(axis=0) > 0).sum()),
                 "goldrate_overall": float(e3_goldrate.mean())}
    # E3 vs E2 correlation across axes (aggregate level)
    res["E3"]["corr_delta_vs_alone"] = float(np.corrcoef(e3_delta.mean(axis=0), alone_mean)[0, 1])
    e4r, e4m, gaps_r, gaps_m = {}, {}, {}, {}
    for s in RSEEDS:
        e4r[s] = float(np.mean(e4_random[s])); e4m[s] = float(np.mean(e4_matched[s]))
        gaps_r[s] = (e4r[s] - nat) * 100; gaps_m[s] = (e4m[s] - nat) * 100
    res["E4_block2"] = {"random_pairing_FR": e4r, "random_pairing_gap_pp": gaps_r,
                        "matched_variance_pairing_FR": e4m, "matched_variance_gap_pp": gaps_m,
                        "frozen_reference_gaps_pp": {43001: -3.4844, 43002: -5.06277, 43003: -2.31986}}
    res["per_question_native_FR"] = per_q_native

    (OUT / "pilot_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    np.savez_compressed(OUT / "per_axis_matrices.npz",
                        alone=e2_alone, drop=e2_drop, delta=e3_delta,
                        goldrate=e3_goldrate, var_rank=var_rank, qids=np.array(qids))
    import csv as _csv
    with (OUT / "per_axis.csv").open("w", newline="", encoding="utf-8") as f:
        w = _csv.writer(f)
        w.writerow(["axis", "mean_var_rank", "alone_FR_mean", "drop_FR_mean", "drop_loss_mean", "delta_gold_mean", "gold_agree_mean"])
        for j in range(96):
            w.writerow([j, f"{var_rank[:,j].mean():.6f}", f"{alone_mean[j]:.10f}", f"{drop_mean[j]:.10f}",
                        f"{loss_mean[j]:.10f}", f"{e3_delta[:,j].mean():.10f}", f"{e3_goldrate[:,j].mean():.10f}"])

    print(json.dumps({k: res[k] for k in ["gate", "E0_native", "E1_budget_curve_topk_variance",
                                          "E1_random_subset", "E1_bottomk_variance", "E4_block2"]}, indent=2))
    print("E2 alone top10:", res["E2"]["alone_top10_axes"])
    print("E2 corr varrank-vs-alone:", res["E2"]["pearson_mean_variance_rank_vs_neg_alone"])
    print("E3 delta vs alone corr:", res["E3"]["corr_delta_vs_alone"])
    print(f"done in {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
