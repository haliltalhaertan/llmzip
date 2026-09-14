"""Corrections pass per Muse design review (muse_pilot_review.md findings F7/F9/F10/F14/F15).

Adds (all gold-free unless tagged):
1. extra_arms2: RAND48 s3,s4 / RAND64 s1,s2 / RANKSPREAD64,32 (uniform rank-linspace spread),
   replacing the mislabeled IDXSTRIDE64 (was a 48-axis duplicate).
2. e4_seeds5: block-2, seeds 43001..43005 x {random, matched-variance, antimatched} pairing.
3. per_axis_v2.csv: adds agree_pool_mean (tie-pool size for the 1-bit arm) + alone_fr_norm
   (tie-pool-normalized alone-FR = alone_FR_mean * pool_mean / K, approx P(gold agrees)).
4. W/T/L vs NATIVE for TOP48/BOT48 per-question.
5. pilot_results_corrections.json: labels_v2 (analysis-only gold-informed block), seed scatter,
   correction log, pkl provenance note. (Kept separate from pilot_results.json to preserve the
   byte state the reviewer session read.)
LOCAL EXPLORATORY PILOT — NOT PREREGISTERED — NOT FOR CITATION.
"""
import json
import pickle
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
PIL = WORK / "pilots" / "axis_attack_2026-09-12"
PKL_DIR = WORK / "regen" / "lme" / "cache_repr"
K, NT = 3, 20
RSEEDS5 = [43001, 43002, 43003, 43004, 43005]


def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100


def met(idx, g):
    s = set(map(int, idx)); gg = set(map(int, g)); x = len(s & gg)
    return float(x > 0), float(x == len(gg) and len(gg) > 0), float(x / len(gg))


def hspec_qs(seed, b):
    r = np.random.default_rng(seed)
    r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return qs


def happly(X, perm, qs, b):
    xp = np.asarray(X, float)[..., perm]
    o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b)
        o[..., sl] = xp[..., sl] @ Q
    return o


def main():
    data = json.loads((WORK / "drive" / "longmemeval_s_cleaned.json").read_text())
    lex = {q: i for i, q in enumerate(sorted(str(x["question_id"]) for x in data))}
    del data

    pkls = sorted(PKL_DIR.glob("*.pkl"))
    assert len(pkls) == 470

    # ---- read existing per-question values for W/T/L ----
    probe = json.loads((PIL / "probe48.json").read_text())     # has mean FR for TOP48/BOT48
    pilot = json.loads((PIL / "pilot_results.json").read_text())
    nat_by_q = pilot["per_question_native_FR"]

    acc = {}
    for key in ["RAND48_s3", "RAND48_s4", "RAND64_s1", "RAND64_s2", "RANKSPREAD64", "RANKSPREAD32"]:
        acc[key] = []
    for s in RSEEDS5:
        for arm in ["random", "matched", "antimatched"]:
            acc[f"E4_{arm}_{s}"] = []
    perq_top48, perq_bot48 = {}, {}

    for qi, p in enumerate(pkls):
        with open(p, "rb") as f:
            o = pickle.loads(f.read())
        qid = o["question_id"]; C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
        n = len(C); D0 = C >= 0; Q0 = qC >= 0
        var = C.var(axis=0)
        rank_desc = np.argsort(var, kind="stable")[::-1]
        pr = [np.random.default_rng(stable_archive_seed(lex[qid], t) + 99).random(n) for t in range(NT)]

        # extra arms
        for key, k, s in [("RAND48_s3", 48, 3), ("RAND48_s4", 48, 4), ("RAND64_s1", 64, 1), ("RAND64_s2", 64, 2)]:
            idx = np.random.default_rng(12000 + s).choice(96, k, replace=False)
            d = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1)
            acc[key].append(float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr])))
        for key, k in [("RANKSPREAD64", 64), ("RANKSPREAD32", 32)]:
            idx = rank_desc[np.linspace(0, 95, k).astype(int)]
            d = np.count_nonzero(D0[:, idx] != Q0[idx][None, :], axis=1)
            acc[key].append(float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr])))

        # W/T/L vs native for TOP48/BOT48
        for nm, order in [("top48", rank_desc[:48]), ("bot48", rank_desc[::-1][:48])]:
            d = np.count_nonzero(D0[:, order] != Q0[order][None, :], axis=1)
            fr = float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr]))
            (perq_top48 if nm == "top48" else perq_bot48)[qid] = fr

        # E4 arms, seeds x3
        for s in RSEEDS5:
            qs = hspec_qs(s, 2)
            perms = {
                "random": np.random.default_rng(s).permutation(96),
                "matched": np.argsort(var, kind="stable"),
            }
            am = np.empty(96, dtype=int)
            am[0::2] = rank_desc[:48]; am[1::2] = rank_desc[::-1][:48]
            perms["antimatched"] = am
            for arm, perm in perms.items():
                Cr = happly(C, perm, qs, 2); qr = happly(qC, perm, qs, 2)
                d = np.count_nonzero((Cr >= 0) != (qr >= 0)[None, :], axis=1)
                acc[f"E4_{arm}_{s}"].append(float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr])))
        if (qi + 1) % 100 == 0:
            print(f"  {qi+1}/470", flush=True)

    nat = float(np.mean(list(nat_by_q.values())))
    out = {"labels": pilot["labels"], "native_FR": nat}
    out["extra_arms2"] = {k: float(np.mean(v)) for k, v in acc.items() if not k.startswith("E4_")}
    e4 = {}
    for s in RSEEDS5:
        e4[str(s)] = {arm: {"FR": float(np.mean(acc[f"E4_{arm}_{s}"])),
                            "gap_pp": (float(np.mean(acc[f"E4_{arm}_{s}"])) - nat) * 100}
                      for arm in ["random", "matched", "antimatched"]}
    out["E4_seeds5"] = e4
    # W/T/L vs native
    for nm, store in [("TOP48", perq_top48), ("BOT48", perq_bot48)]:
        garr = np.array([store[q] - nat_by_q[q] for q in store])
        out[f"{nm}_vs_native"] = {"W_T_L": [int((garr > 1e-12).sum()), int((np.abs(garr) <= 1e-12).sum()),
                                            int((garr < -1e-12).sum())],
                                  "median_gap": float(np.median(garr))}
    # per-axis pool + normalized alone
    import csv as _csv
    rows = list(_csv.DictReader((PIL / "per_axis.csv").open(encoding="utf-8")))
    pools = np.zeros(96)
    for qi, p in enumerate(sorted(PKL_DIR.glob("*.pkl"))):
        with open(p, "rb") as f:
            o = pickle.loads(f.read())
        C = o["C"]; qC = o["qC"]
        pools += ((C >= 0) == ((qC >= 0)[None, :])).sum(axis=0)
    pools /= len(pkls)
    with (PIL / "per_axis_v2.csv").open("w", newline="", encoding="utf-8") as f:
        w = _csv.writer(f)
        w.writerow(list(rows[0].keys()) + ["agree_pool_mean", "alone_fr_norm"])
        for r in rows:
            j = int(r["axis"])
            norm = float(r["alone_FR_mean"]) * pools[j] / K
            w.writerow(list(r.values()) + [f"{pools[j]:.4f}", f"{norm:.6f}"])
    out["analysis_only_gold_informed"] = {
        "fields": ["E2.*", "E3.* (delta_gold_mean, gold_agree_mean, delta_positive_axes, goldrate_overall)",
                   "per_axis.alone_FR_mean / drop_loss_mean / drop_FR_mean", "per_axis_v2.alone_fr_norm",
                   "TOP48_vs_native / BOT48_vs_native (derived from gold-scored FRs)"],
        "gold_free": ["E0 (pure reproduction)", "E1 arms (variance/seed selection only)",
                      "E4 arms (variance ordering only; gold only inside the metric)",
                      "extra_arms2", "diagnostics.json (dup/tie/phi need no gold; gold_gap column uses gold)"],
        "note": "alone_fr_norm is tie-pool-normalized (alone_FR * pool / K, approx P(gold agrees)); "
                "corr(delta_vs_alone)=0.77 in pilot_results.json is inflated by shared pool-size term.",
        "pkl_provenance": "cache_repr pkls are byte-governed by certification_report.json "
                          "pkl_sha256_manifest (470 entries), verified in the closure review.",
    }
    (PIL / "pilot_results_corrections.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
