from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "locomo_spectral_band_haar_causal.py"

PREREG_GIT_BLOB = "2d6a14f254399327f59db1958a0b5c0dfb9ea8e0"
BASE_GIT_BLOB = "7c4140252fb7f846d617189925cdf534515743f4"
SEEDS = list(range(57001, 57011))
FROZEN_NATIVE_R3 = 0.23654714666441054
FROZEN_FULL_HAAR_R3 = 0.13770827054136
TOL = 1e-12
HEAD = np.arange(0, 32, dtype=int)
TAIL = np.arange(32, 96, dtype=int)
FULL = np.arange(0, 96, dtype=int)
ARM_SPEC = "SPECTRAL_HEAD32_TAIL64_HAAR_NEW"
ARM_RAND = "RANDOM32_COMPLEMENT64_HAAR"


def load_base():
    spec = importlib.util.spec_from_file_location("locomo_null_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import spectral-band base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def paired_matrices(base, seed: int):
    prng = np.random.default_rng(seed)
    perm = prng.permutation(96)
    S = np.sort(perm[:32].astype(int))
    T = np.sort(perm[32:].astype(int))
    if len(S) != 32 or len(T) != 64 or len(np.unique(S)) != 32 or len(np.unique(T)) != 64:
        raise RuntimeError(f"partition cardinality failure seed={seed}")
    if np.intersect1d(S, T).size or not np.array_equal(np.sort(np.r_[S, T]), np.arange(96)):
        raise RuntimeError(f"partition coverage failure seed={seed}")

    rrng = np.random.default_rng(1_000_000 + seed)
    Q32 = base.haar_q(rrng, 32)
    Q64 = base.haar_q(rrng, 64)

    Rspec = np.zeros((96, 96), dtype=float)
    Rspec[:32, :32] = Q32
    Rspec[32:, 32:] = Q64

    Rrand = np.zeros((96, 96), dtype=float)
    Rrand[np.ix_(S, S)] = Q32
    Rrand[np.ix_(T, T)] = Q64
    return S, T, Rspec, Rrand


def run(out: Path):
    base = load_base()
    common = base.load_common()
    out.mkdir(parents=True, exist_ok=True)
    raw, audit, _ = common.acquire_and_verify(out / "source_bytes")
    convs, _ = common.load_dataset(raw, audit)
    reps = [common.build_representation(c) for c in convs]

    transforms = {}
    partitions = []
    for seed in SEEDS:
        S, T, Rspec, Rrand = paired_matrices(base, seed)
        transforms[seed] = {ARM_SPEC: Rspec, ARM_RAND: Rrand, "S": S, "T": T}
        partitions.append({"seed": seed, "S32": S.tolist(), "T64": T.tolist()})
        for arm, R in [(ARM_SPEC, Rspec), (ARM_RAND, Rrand)]:
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality failure seed={seed} arm={arm} err={err}")
    (out / "locomo_random_partitions.json").write_text(json.dumps(partitions, indent=2), encoding="utf-8")

    native_vals = []
    arm_vals = {(s, a): [] for s in SEEDS for a in [ARM_SPEC, ARM_RAND]}
    subset_rows = []
    pair_rows = []
    rescue = {(s, a): {"block32_bad": 0, "block32_bad_full_good": 0, "block32_good": 0, "block32_good_full_bad": 0}
              for s in SEEDS for a in [ARM_SPEC, ARM_RAND]}
    max_norm = 0.0
    max_dot = 0.0
    valid = 0

    for ci, rep in enumerate(reps):
        C, QC = rep["C"], rep["QC"]
        D0, QB0, dist0 = base.signs_and_dist(C, QC)
        priorities = [np.random.default_rng(common.stable_archive_seed(ci, t) + 99).random(len(C))
                      for t in range(common.N_NUISANCE)]

        # Exact signed-permutation Hamming control, independent of the primary arms.
        rsp = np.random.default_rng(SEEDS[0])
        perm = rsp.permutation(96)
        sg = rsp.choice(np.array([-1.0, 1.0]), 96)
        Ds = (C[:, perm] * sg) >= 0
        Qs = (QC[:, perm] * sg) >= 0
        dsp = np.count_nonzero(Qs[:, None, :] != Ds[None, :, :], axis=2).astype(np.int16)
        if not np.array_equal(dsp, dist0):
            raise RuntimeError("signed permutation Hamming invariance failed")

        cache = {}
        for seed in SEEDS:
            for arm in [ARM_SPEC, ARM_RAND]:
                R = transforms[seed][arm]
                Cr, Qr = C @ R, QC @ R
                max_norm = max(max_norm,
                               float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                               float(np.max(np.abs(np.linalg.norm(Qr, axis=1) - np.linalg.norm(QC, axis=1)))))
                max_dot = max(max_dot, float(np.max(np.abs(Qr @ Cr.T - QC @ C.T))))
                D, QB, dist = base.signs_and_dist(Cr, Qr)
                cache[(seed, arm)] = (D, QB, dist)
        if max_norm > TOL or max_dot > TOL:
            raise RuntimeError(f"continuous invariance failure norm={max_norm} dot={max_dot}")

        for qi, q in enumerate(rep["qas"]):
            gold = base.gold_rows(q, rep["id_to_row"])
            if not gold:
                continue
            valid += 1
            native_vals.append(base.mean_fractional_for_dist(common, dist0[qi], priorities, gold))
            for seed in SEEDS:
                S = transforms[seed]["S"]
                T = transforms[seed]["T"]
                for arm in [ARM_SPEC, ARM_RAND]:
                    D, QB, dist = cache[(seed, arm)]
                    full_r3 = base.mean_fractional_for_dist(common, dist[qi], priorities, gold)
                    arm_vals[(seed, arm)].append(full_r3)
                    subset_defs = [("Head32", HEAD), ("Tail64", TAIL), ("Full96", FULL)] if arm == ARM_SPEC else [("Random32", S), ("Random64", T), ("Full96", FULL)]
                    for name, idx in subset_defs:
                        subset_rows.append({"seed": seed, "arm": arm, "question_id": q["question_id"], "subset": name,
                                            "Fractional_R3": base.band_r3_for_question(common, D, QB[qi], priorities, gold, idx)})
                        n, discr, adv, tie = base.pairwise_counts(D, QB[qi], gold, idx)
                        pair_rows.append({"seed": seed, "arm": arm, "subset": name, "pair_count": n,
                                          "discrimination_sum": discr, "same_sign_adv_sum": adv, "tie_count": tie})
                    block32 = HEAD if arm == ARM_SPEC else S
                    bf = base.hard_pair_flags(D, QB[qi], gold, block32)
                    ff = base.hard_pair_flags(D, QB[qi], gold, FULL)
                    if bf and ff:
                        block_good = bf[0] < bf[1]
                        full_good = ff[0] < ff[1]
                        a = rescue[(seed, arm)]
                        if block_good:
                            a["block32_good"] += 1
                            if not full_good:
                                a["block32_good_full_bad"] += 1
                        else:
                            a["block32_bad"] += 1
                            if full_good:
                                a["block32_bad_full_good"] += 1

    if valid != 1535:
        raise RuntimeError(f"valid denominator changed {valid}")
    native = float(np.mean(native_vals))
    repro = abs(native - FROZEN_NATIVE_R3)
    if repro > TOL:
        raise RuntimeError(f"native reproduction failure got={native} err={repro}")

    L_full = native - FROZEN_FULL_HAAR_R3
    seed_rows = []
    for seed in SEEDS:
        spec_r3 = float(np.mean(arm_vals[(seed, ARM_SPEC)]))
        rand_r3 = float(np.mean(arm_vals[(seed, ARM_RAND)]))
        rho_spec_seed = (native - spec_r3) / L_full
        rho_rand_seed = (native - rand_r3) / L_full
        seed_rows.append({"seed": seed, "spectral_R3": spec_r3, "random_R3": rand_r3,
                          "rho_spec": rho_spec_seed, "rho_rand": rho_rand_seed,
                          "Delta": rho_rand_seed - rho_spec_seed})
    sdf = pd.DataFrame(seed_rows)
    sdf.to_csv(out / "locomo_random_partition_seed_results.csv", index=False)

    R_spec = float(sdf.spectral_R3.mean())
    R_rand = float(sdf.random_R3.mean())
    rho_spec = (native - R_spec) / L_full
    rho_rand = (native - R_rand) / L_full
    Delta = rho_rand - rho_spec

    if rho_spec > 0.25:
        regime = "[HEAD-TAIL REPLICATION FAILURE — SPECTRAL POSITION CLAIM NOT ADVANCED]"
    elif Delta <= 0.05:
        regime = "[GENERIC BLOCK-STRUCTURE SUFFICIENCY LEAD — SPECTRAL POSITION CLAIM FALSIFIED]"
    elif Delta >= 0.25:
        regime = "[SPECTRAL POSITION LOAD-BEARING LEAD]"
    else:
        regime = "[MIXED / PARTIAL SPECTRAL POSITION CONTRIBUTION]"

    subdf = pd.DataFrame(subset_rows)
    subagg = subdf.groupby(["seed", "arm", "subset"], as_index=False).Fractional_R3.mean()
    subagg.to_csv(out / "locomo_random_partition_subset_r3.csv", index=False)

    pdf = pd.DataFrame(pair_rows)
    pagg = pdf.groupby(["seed", "arm", "subset"], as_index=False).agg(
        pair_count=("pair_count", "sum"), discrimination_sum=("discrimination_sum", "sum"),
        same_sign_adv_sum=("same_sign_adv_sum", "sum"), tie_count=("tie_count", "sum"))
    pagg["pairwise_gold_vs_nongold_discrimination"] = pagg.discrimination_sum / pagg.pair_count
    pagg["gold_minus_nongold_same_sign_advantage"] = pagg.same_sign_adv_sum / pagg.pair_count
    pagg["tie_fraction"] = pagg.tie_count / pagg.pair_count
    pagg.to_csv(out / "locomo_random_partition_pairwise.csv", index=False)

    rr = []
    for seed in SEEDS:
        for arm in [ARM_SPEC, ARM_RAND]:
            a = rescue[(seed, arm)]
            rr.append({"seed": seed, "arm": arm, **a,
                       "block32_wrong_or_tie_to_full_rescue": a["block32_bad_full_good"] / a["block32_bad"] if a["block32_bad"] else math.nan,
                       "block32_correct_to_full_degrade": a["block32_good_full_bad"] / a["block32_good"] if a["block32_good"] else math.nan})
    pd.DataFrame(rr).to_csv(out / "locomo_random_partition_hard_negative_rescue.csv", index=False)

    def disp(series):
        x = np.asarray(series, dtype=float)
        return {"mean": float(x.mean()), "sample_sd": float(x.std(ddof=1)), "population_sd": float(x.std(ddof=0)),
                "min": float(x.min()), "max": float(x.max())}

    summary = {
        "status": "PREREGISTERED_MATCHED_RANDOM_PARTITION_NULL_RESULT",
        "benchmark": "LoCoMo",
        "prereg_git_blob": PREREG_GIT_BLOB,
        "base_runner_git_blob": BASE_GIT_BLOB,
        "identity": {"dataset_sha256": common.DATASET_SHA256, "audit_manifest_sha256": common.AUDIT_MANIFEST_SHA256,
                     "valid_questions": valid, "seeds": SEEDS},
        "controls": {"native_reproduction": native, "frozen_native": FROZEN_NATIVE_R3,
                     "absolute_reproduction_error": repro, "signed_permutation_exact_pass": True,
                     "continuous_norm_max_abs_error": max_norm, "continuous_dot_max_abs_error": max_dot,
                     "partition_checks_pass": True},
        "primary": {"native_R3": native, "frozen_full_haar_R3": FROZEN_FULL_HAAR_R3, "L_full": L_full,
                    "spectral_mean_R3": R_spec, "random_mean_R3": R_rand,
                    "rho_spec": rho_spec, "rho_rand": rho_rand, "Delta": Delta, "regime": regime,
                    "seed_rows": seed_rows,
                    "dispersion": {"spectral_R3": disp(sdf.spectral_R3), "random_R3": disp(sdf.random_R3),
                                   "rho_spec": disp(sdf.rho_spec), "rho_rand": disp(sdf.rho_rand), "Delta": disp(sdf.Delta)}},
        "partitions": partitions,
        "interpretation_ceiling": "Fixed-benchmark preregistered matched null control; no population-level generalization."
    }
    (out / "locomo_random_partition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = ["# V52 LoCoMo Matched Random-Partition Null Control", "", f"Verdict: `{regime}`", "",
             f"Native R@3: {native*100:.12f}%", f"Spectral Head32/Tail64 mean R@3: {R_spec*100:.12f}%",
             f"Random32/complement64 mean R@3: {R_rand*100:.12f}%", f"Frozen Full-Haar R@3: {FROZEN_FULL_HAAR_R3*100:.12f}%",
             f"rho_spec: {rho_spec:.9f}", f"rho_rand: {rho_rand:.9f}", f"Delta: {Delta:.9f}", "",
             f"Native reproduction error: {repro:.3e}", "Signed permutation: PASS",
             f"Continuous norm max abs error: {max_norm:.3e}", f"Continuous dot max abs error: {max_dot:.3e}",
             "Partition checks: PASS"]
    (out / "LOCOMO_RANDOM_PARTITION_NULL_CHECKPOINT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("locomo_random_partition_outputs"))
    args = ap.parse_args()
    run(args.out)
