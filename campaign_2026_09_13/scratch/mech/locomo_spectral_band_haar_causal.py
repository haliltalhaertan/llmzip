from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
COMMON_PATH = HERE / "locomo_sign_mechanism_replication.py"

PREREG_GIT_BLOB = "02aa91a12b4052bbb2f0a6617167c8851e4f71f7"
COMMON_GIT_BLOB = "6700454915176854a55b0b5cf6ffe922a22e35f2"

CAUSAL_SEEDS = [55001, 55002, 55003, 55004, 55005]
FROZEN_NATIVE_R3 = 0.23654714666441054
FROZEN_FULL_HAAR_R3 = 0.13770827054136
REPRO_TOL = 1e-12
ORTH_TOL = 1e-12

BAND_MAP = {
    "High32": np.arange(0, 32, dtype=int),
    "Mid32": np.arange(32, 64, dtype=int),
    "Low32": np.arange(64, 96, dtype=int),
    "HighMid64": np.arange(0, 64, dtype=int),
    "HighLow64": np.r_[0:32, 64:96].astype(int),
    "MidLow64": np.arange(32, 96, dtype=int),
    "Full96": np.arange(0, 96, dtype=int),
}

def load_common():
    spec = importlib.util.spec_from_file_location("locomo_common", COMMON_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen mechanism source")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def haar_q(rng: np.random.Generator, d: int) -> np.ndarray:
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    sg = np.where(np.diag(R) < 0, -1.0, 1.0)
    return Q * sg[None, :]

def within_band_matrix(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    R = np.zeros((96, 96), dtype=float)
    for lo, hi in [(0, 32), (32, 64), (64, 96)]:
        R[lo:hi, lo:hi] = haar_q(rng, 32)
    return R

def selected_subspace_matrix(seed: int, idx: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(seed)
    Q = haar_q(rng, len(idx))
    R = np.eye(96, dtype=float)
    R[np.ix_(idx, idx)] = Q
    return R

def intervention_matrices(seed: int) -> dict[str, np.ndarray]:
    return {
        "WITHIN_SPECTRAL_BAND_HAAR": within_band_matrix(seed),
        "HAAR_HIGH_MID64": selected_subspace_matrix(seed, BAND_MAP["HighMid64"]),
        "HAAR_HIGH_LOW64": selected_subspace_matrix(seed, BAND_MAP["HighLow64"]),
        "HAAR_MID_LOW64": selected_subspace_matrix(seed, BAND_MAP["MidLow64"]),
    }

def gold_rows(q, id_to_row):
    return list(dict.fromkeys(int(id_to_row[x]) for x in q["correct_evidence"] if x in id_to_row))

def mean_fractional_for_dist(common, dist: np.ndarray, priorities: list[np.ndarray], gold: list[int]) -> float:
    tops = common.topks_by_hamming(dist, priorities)
    return float(np.mean([common.fractional(t, gold) for t in tops]))

def signs_and_dist(C: np.ndarray, Q: np.ndarray):
    D = C >= 0
    QB = Q >= 0
    dist = np.count_nonzero(QB[:, None, :] != D[None, :, :], axis=2).astype(np.int16)
    return D, QB, dist

def band_r3_for_question(common, D: np.ndarray, QB: np.ndarray, priorities: list[np.ndarray], gold: list[int], idx: np.ndarray) -> float:
    dist = np.count_nonzero(QB[None, idx] != D[:, idx], axis=1).astype(np.int16)
    return mean_fractional_for_dist(common, dist, priorities, gold)

def pairwise_counts(D: np.ndarray, QB: np.ndarray, gold: list[int], idx: np.ndarray):
    if not gold:
        return 0, 0.0, 0.0, 0.0
    G = np.asarray(gold, dtype=int)
    mask = np.ones(len(D), dtype=bool)
    mask[G] = False
    NG = np.flatnonzero(mask)
    if len(NG) == 0:
        return 0, 0.0, 0.0, 0.0
    dg = np.count_nonzero(D[G][:, idx] != QB[None, idx], axis=1)
    dn = np.count_nonzero(D[NG][:, idx] != QB[None, idx], axis=1)
    comp = dg[:, None] - dn[None, :]
    correct = float(np.sum(comp < 0))
    tie = float(np.sum(comp == 0))
    n = int(comp.size)
    discr = correct + 0.5 * tie
    adv_sum = (float(dn.mean()) - float(dg.mean())) / len(idx) * n
    return n, discr, adv_sum, tie

def hard_pair_flags(D: np.ndarray, QB: np.ndarray, gold: list[int], idx: np.ndarray):
    G = np.asarray(gold, dtype=int)
    mask = np.ones(len(D), dtype=bool)
    mask[G] = False
    NG = np.flatnonzero(mask)
    if len(G) == 0 or len(NG) == 0:
        return None
    dg = np.count_nonzero(D[G][:, idx] != QB[None, idx], axis=1)
    dn = np.count_nonzero(D[NG][:, idx] != QB[None, idx], axis=1)
    return int(dg.min()), int(dn.min())

def run(out: Path):
    common = load_common()
    out.mkdir(parents=True, exist_ok=True)
    source_dir = out / "source_bytes"
    raw, audit, audit_rows = common.acquire_and_verify(source_dir)
    convs, corr = common.load_dataset(raw, audit)

    reps = [common.build_representation(c) for c in convs]

    native_qvals = []
    seed_rows = []
    band_rows = []
    pair_rows = []
    rescue_acc = {s: {"high_bad": 0, "high_bad_full_good": 0, "high_good": 0, "high_good_full_bad": 0,
                      "hm_bad": 0, "hm_bad_full_good": 0} for s in CAUSAL_SEEDS}
    inv_rows = []
    signed_perm_pass = True
    valid_questions = 0

    transforms: dict[int, dict[str, np.ndarray]] = {}
    for seed in CAUSAL_SEEDS:
        transforms[seed] = intervention_matrices(seed)
        for method, R in transforms[seed].items():
            oe = float(np.max(np.abs(R.T @ R - np.eye(96))))
            inv_rows.append({"seed": seed, "method": method, "orthogonality_max_abs_error": oe})
            if oe > ORTH_TOL:
                raise RuntimeError(f"orthogonality failure {method} seed={seed} err={oe}")

    per_seed_q = {s: [] for s in CAUSAL_SEEDS}
    per_seed_method_q = {(s, m): [] for s in CAUSAL_SEEDS for m in [
        "WITHIN_SPECTRAL_BAND_HAAR", "HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"
    ]}

    max_norm_err = 0.0
    max_dot_err = 0.0

    for ci, (conv, rep) in enumerate(zip(convs, reps)):
        C, QC = rep["C"], rep["QC"]
        D0, QB0, dist0_all = signs_and_dist(C, QC)
        priorities = [np.random.default_rng(common.stable_archive_seed(ci, t) + 99).random(len(C))
                      for t in range(common.N_NUISANCE)]

        rngsp = np.random.default_rng(CAUSAL_SEEDS[0])
        perm = rngsp.permutation(96)
        sg = rngsp.choice(np.array([-1.0, 1.0]), 96)
        Ds = (C[:, perm] * sg) >= 0
        Qs = (QC[:, perm] * sg) >= 0
        dsp = np.count_nonzero(Qs[:, None, :] != Ds[None, :, :], axis=2).astype(np.int16)
        if not np.array_equal(dsp, dist0_all):
            signed_perm_pass = False
            raise RuntimeError("signed-permutation Hamming invariance failed")

        method_cache = {}
        for seed in CAUSAL_SEEDS:
            for method, R in transforms[seed].items():
                Cr = C @ R
                Qr = QC @ R
                max_norm_err = max(
                    max_norm_err,
                    float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                    float(np.max(np.abs(np.linalg.norm(Qr, axis=1) - np.linalg.norm(QC, axis=1)))),
                )
                max_dot_err = max(max_dot_err, float(np.max(np.abs(Qr @ Cr.T - QC @ C.T))))
                D, QB, dist = signs_and_dist(Cr, Qr)
                method_cache[(seed, method)] = (D, QB, dist)

        if max_norm_err > ORTH_TOL or max_dot_err > ORTH_TOL:
            raise RuntimeError(f"continuous invariance failure norm={max_norm_err} dot={max_dot_err}")

        for qi, q in enumerate(rep["qas"]):
            gold = gold_rows(q, rep["id_to_row"])
            if not gold:
                continue
            valid_questions += 1
            native_val = mean_fractional_for_dist(common, dist0_all[qi], priorities, gold)
            native_qvals.append(native_val)

            for seed in CAUSAL_SEEDS:
                for method in ["WITHIN_SPECTRAL_BAND_HAAR", "HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]:
                    D, QB, dist = method_cache[(seed, method)]
                    v = mean_fractional_for_dist(common, dist[qi], priorities, gold)
                    per_seed_method_q[(seed, method)].append(v)

                D, QB, dist = method_cache[(seed, "WITHIN_SPECTRAL_BAND_HAAR")]
                per_seed_q[seed].append(per_seed_method_q[(seed, "WITHIN_SPECTRAL_BAND_HAAR")][-1])

                for bname, idx in BAND_MAP.items():
                    v = band_r3_for_question(common, D, QB[qi], priorities, gold, idx)
                    band_rows.append({"seed": seed, "conv_id": conv["conv_id"], "question_id": q["question_id"],
                                      "band": bname, "fractional_R3": v})
                    if bname in ("High32", "Mid32", "Low32", "Full96"):
                        n, discr, adv, tie = pairwise_counts(D, QB[qi], gold, idx)
                        pair_rows.append({"seed": seed, "band": bname, "pair_count": n,
                                          "discrimination_sum": discr, "same_sign_adv_sum": adv,
                                          "tie_count": tie})

                hf = hard_pair_flags(D, QB[qi], gold, BAND_MAP["High32"])
                ff = hard_pair_flags(D, QB[qi], gold, BAND_MAP["Full96"])
                hmf = hard_pair_flags(D, QB[qi], gold, BAND_MAP["HighMid64"])
                if hf and ff and hmf:
                    hg, hn = hf
                    fg, fn = ff
                    hmg, hmn = hmf
                    high_good = hg < hn
                    full_good = fg < fn
                    hm_good = hmg < hmn
                    a = rescue_acc[seed]
                    if high_good:
                        a["high_good"] += 1
                        if not full_good:
                            a["high_good_full_bad"] += 1
                    else:
                        a["high_bad"] += 1
                        if full_good:
                            a["high_bad_full_good"] += 1
                    if not hm_good:
                        a["hm_bad"] += 1
                        if full_good:
                            a["hm_bad_full_good"] += 1

    native = float(np.mean(native_qvals))
    if valid_questions != 1535:
        raise RuntimeError(f"valid denominator changed: {valid_questions}")
    repro_err = abs(native - FROZEN_NATIVE_R3)
    if repro_err > REPRO_TOL:
        raise RuntimeError(f"native reproduction failed: got={native} frozen={FROZEN_NATIVE_R3} err={repro_err}")

    for seed in CAUSAL_SEEDS:
        for method in ["WITHIN_SPECTRAL_BAND_HAAR", "HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]:
            r3 = float(np.mean(per_seed_method_q[(seed, method)]))
            seed_rows.append({"seed": seed, "method": method, "Fractional_R3": r3,
                              "native_minus_intervention_pp": (native - r3) * 100.0})

    sdf = pd.DataFrame(seed_rows)
    sdf.to_csv(out / "locomo_causal_seed_results.csv", index=False)

    within = sdf[sdf.method == "WITHIN_SPECTRAL_BAND_HAAR"]
    mean_band = float(within.Fractional_R3.mean())
    L_full = native - FROZEN_FULL_HAAR_R3
    L_band = native - mean_band
    rho = L_band / L_full

    if rho <= 0.25:
        regime = "[SPECTRAL-SUBSPACE PRESERVATION LEAD]"
    elif rho >= 0.75:
        regime = "[INDIVIDUAL-AXIS ORIENTATION LEAD]"
    else:
        regime = "[MIXED / BOTH LEVELS MATTER]"

    bdf = pd.DataFrame(band_rows)
    bagg = bdf.groupby(["seed", "band"], as_index=False).fractional_R3.mean()
    bagg.to_csv(out / "locomo_within_band_subset_r3.csv", index=False)

    pdf = pd.DataFrame(pair_rows)
    pagg = pdf.groupby(["seed", "band"], as_index=False).agg(
        pair_count=("pair_count", "sum"),
        discrimination_sum=("discrimination_sum", "sum"),
        same_sign_adv_sum=("same_sign_adv_sum", "sum"),
        tie_count=("tie_count", "sum"),
    )
    pagg["pairwise_gold_vs_nongold_discrimination"] = pagg.discrimination_sum / pagg.pair_count
    pagg["gold_minus_nongold_same_sign_advantage"] = pagg.same_sign_adv_sum / pagg.pair_count
    pagg.to_csv(out / "locomo_within_band_pairwise.csv", index=False)

    rescue_rows = []
    for seed, a in rescue_acc.items():
        rescue_rows.append({
            "seed": seed,
            **a,
            "high_wrong_or_tie_to_full_rescue": a["high_bad_full_good"] / a["high_bad"] if a["high_bad"] else math.nan,
            "high_correct_to_full_degrade": a["high_good_full_bad"] / a["high_good"] if a["high_good"] else math.nan,
            "highmid_wrong_or_tie_to_full_rescue": a["hm_bad_full_good"] / a["hm_bad"] if a["hm_bad"] else math.nan,
        })
    rdf = pd.DataFrame(rescue_rows)
    rdf.to_csv(out / "locomo_within_band_hard_negative_rescue.csv", index=False)

    summary = {
        "status": "PREREGISTERED_CAUSAL_INTERVENTION_RESULT",
        "benchmark": "LoCoMo",
        "prereg_git_blob": PREREG_GIT_BLOB,
        "common_source_git_blob": COMMON_GIT_BLOB,
        "identity": {
            "dataset_sha256": common.DATASET_SHA256,
            "audit_manifest_sha256": common.AUDIT_MANIFEST_SHA256,
            "audit_file_count": len(audit_rows),
            "valid_questions": valid_questions,
        },
        "controls": {
            "native_reproduction": native,
            "frozen_native": FROZEN_NATIVE_R3,
            "absolute_reproduction_error": repro_err,
            "signed_permutation_exact_pass": signed_perm_pass,
            "continuous_norm_max_abs_error": max_norm_err,
            "continuous_dot_max_abs_error": max_dot_err,
        },
        "primary": {
            "native_R3": native,
            "frozen_full_haar_R3": FROZEN_FULL_HAAR_R3,
            "within_band_haar_mean_R3": mean_band,
            "L_full": L_full,
            "L_band": L_band,
            "rho": rho,
            "regime": regime,
            "seed_R3": {str(int(r.seed)): float(r.Fractional_R3) for r in within.itertuples()},
        },
        "secondary_arm_means": {
            m: float(sdf[sdf.method == m].Fractional_R3.mean())
            for m in ["HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]
        },
        "interpretation_ceiling": "Fixed-benchmark preregistered causal-intervention evidence; no population-level generalization.",
    }
    (out / "locomo_causal_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# V52 LoCoMo Causal Spectral-Band Haar Result",
        "",
        f"Preregistered primary regime: `{regime}`",
        "",
        "## Integrity / stop rules",
        f"- audit-clean denominator: {valid_questions}",
        f"- native reproduction: {native*100:.12f}% (frozen {FROZEN_NATIVE_R3*100:.12f}%; abs error {repro_err:.3e})",
        f"- signed permutation exact control: {'PASS' if signed_perm_pass else 'FAIL'}",
        f"- continuous norm max abs error: {max_norm_err:.3e}",
        f"- continuous dot max abs error: {max_dot_err:.3e}",
        "",
        "## Primary causal estimand",
        f"- Native R@3: {native*100:.6f}%",
        f"- Frozen Full-Haar mean R@3: {FROZEN_FULL_HAAR_R3*100:.6f}%",
        f"- Within-band Haar mean R@3: {mean_band*100:.6f}%",
        f"- L_full: {L_full*100:.6f} pp",
        f"- L_band: {L_band*100:.6f} pp",
        f"- rho = L_band/L_full: {rho:.6f}",
        f"- verdict: `{regime}`",
        "",
        "## Per-seed within-band R@3",
    ]
    for r in within.itertuples():
        md.append(f"- {int(r.seed)}: {r.Fractional_R3*100:.6f}%")
    md += ["", "## Secondary cross-band arm means"]
    for m, v in summary["secondary_arm_means"].items():
        md.append(f"- {m}: {v*100:.6f}%")
    md += [
        "",
        "## Interpretation ceiling",
        "This is a preregistered fixed-benchmark causal intervention. Secondary arms and diagnostics do not alter the primary rho decision bands. Cross-benchmark adjudication must wait for the corresponding LongMemEval arm.",
    ]
    (out / "LOCOMO_CAUSAL_CHECKPOINT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("locomo_causal_outputs"))
    args = ap.parse_args()
    run(args.out)
