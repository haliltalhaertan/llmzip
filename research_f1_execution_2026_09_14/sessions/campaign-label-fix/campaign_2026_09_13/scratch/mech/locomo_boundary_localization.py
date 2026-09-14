from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "locomo_spectral_band_haar_causal.py"
PREREG_GIT_BLOB = "b8acebedd49497a62ec637beabbcef6720460d15"
ADDENDUM_GIT_BLOB = "456b3b51f49a0238cd936bc3f639988fb0d673af"
BASE_GIT_BLOB = "7c4140252fb7f846d617189925cdf534515743f4"
BOUNDARIES = [16, 24, 32, 48, 64]
ROTATION_SEEDS = list(range(58001, 58011))
PARTITION_SEEDS = list(range(68001, 68011))
FROZEN_NATIVE_R3 = 0.23654714666441054
FROZEN_FULL_HAAR_R3 = 0.13770827054136
TOL = 1e-12


def load_base():
    spec = importlib.util.spec_from_file_location("locomo_boundary_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen LoCoMo base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def boundary_matrix(base, seed: int, b: int):
    rng = np.random.default_rng(seed)
    qh = base.haar_q(rng, b)
    qt = base.haar_q(rng, 96 - b)
    R = np.zeros((96, 96), dtype=float)
    R[:b, :b] = qh
    R[b:, b:] = qt
    return R, qh, qt


def matched_random32_matrix(base, rotation_seed: int, partition_seed: int):
    _, q32, q64 = boundary_matrix(base, rotation_seed, 32)
    perm = np.random.default_rng(partition_seed).permutation(96).astype(int)
    S = perm[:32]
    T = perm[32:]
    if len(S) != 32 or len(T) != 64 or len(np.unique(S)) != 32 or len(np.unique(T)) != 64:
        raise RuntimeError("random partition cardinality/uniqueness failure")
    if np.intersect1d(S, T).size or not np.array_equal(np.sort(np.r_[S, T]), np.arange(96)):
        raise RuntimeError("random partition disjointness/exhaustiveness failure")
    R = np.zeros((96, 96), dtype=float)
    R[np.ix_(S, S)] = q32
    R[np.ix_(T, T)] = q64
    return R, S, T, q32, q64


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stats_from_seed_rows(seed_rows, native, l_full):
    x = np.asarray([r["R3"] for r in seed_rows], dtype=float)
    rho = (native - x) / l_full
    return {
        "mean_R3": float(x.mean()),
        "rho": float((native - x.mean()) / l_full),
        "sample_sd_R3": float(x.std(ddof=1)),
        "se_R3": float(x.std(ddof=1) / np.sqrt(len(x))),
        "sample_sd_rho": float(rho.std(ddof=1)),
        "se_rho": float(rho.std(ddof=1) / np.sqrt(len(rho))),
        "rho_min": float(rho.min()),
        "rho_max": float(rho.max()),
        "sign_inverting_rotation_seeds": [int(seed_rows[i]["rotation_seed"]) for i in range(len(seed_rows)) if x[i] > native],
    }


def run(out: Path):
    base = load_base()
    common = base.load_common()
    out.mkdir(parents=True, exist_ok=True)
    raw, audit, _ = common.acquire_and_verify(out / "source_bytes")
    convs, _ = common.load_dataset(raw, audit)
    reps = [common.build_representation(c) for c in convs]

    transforms = {}
    partitions = []
    q_pair_max = 0.0
    for seed in ROTATION_SEEDS:
        for b in BOUNDARIES:
            R, _, _ = boundary_matrix(base, seed, b)
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality failure b={b} seed={seed}: {err}")
            transforms[(seed, f"B{b}")] = R
        pseed = PARTITION_SEEDS[ROTATION_SEEDS.index(seed)]
        Rr, S, T, q32r, q64r = matched_random32_matrix(base, seed, pseed)
        _, q32s, q64s = boundary_matrix(base, seed, 32)
        qerr = max(float(np.max(np.abs(q32r - q32s))), float(np.max(np.abs(q64r - q64s))))
        q_pair_max = max(q_pair_max, qerr)
        if qerr != 0.0:
            raise RuntimeError(f"matched Q32/Q64 failure seed={seed}: {qerr}")
        err = float(np.max(np.abs(Rr.T @ Rr - np.eye(96))))
        if err > TOL:
            raise RuntimeError(f"random orthogonality failure seed={seed}: {err}")
        transforms[(seed, "RANDOM32")] = Rr
        partitions.append({"rotation_seed": seed, "partition_seed": pseed, "S32": S.tolist(), "T64": T.tolist()})
    (out / "locomo_boundary_random_partitions.json").write_text(json.dumps(partitions, indent=2), encoding="utf-8")

    native_vals = []
    perq = []
    max_norm = 0.0
    max_dot = 0.0
    valid = 0
    signed_perm_pass = True

    arms = [f"B{b}" for b in BOUNDARIES] + ["RANDOM32"]
    for ci, rep in enumerate(reps):
        C, QC = rep["C"], rep["QC"]
        D0, QB0, dist0 = base.signs_and_dist(C, QC)
        priorities = [np.random.default_rng(common.stable_archive_seed(ci, t) + 99).random(len(C))
                      for t in range(common.N_NUISANCE)]

        rsp = np.random.default_rng(ROTATION_SEEDS[0])
        perm = rsp.permutation(96)
        sg = rsp.choice(np.array([-1.0, 1.0]), 96)
        Ds = (C[:, perm] * sg) >= 0
        Qs = (QC[:, perm] * sg) >= 0
        dsp = np.count_nonzero(Qs[:, None, :] != Ds[None, :, :], axis=2).astype(np.int16)
        if not np.array_equal(dsp, dist0):
            signed_perm_pass = False
            raise RuntimeError("signed-permutation Hamming invariance failure")

        cache = {}
        for seed in ROTATION_SEEDS:
            for arm in arms:
                R = transforms[(seed, arm)]
                Cr, Qr = C @ R, QC @ R
                max_norm = max(max_norm,
                               float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                               float(np.max(np.abs(np.linalg.norm(Qr, axis=1) - np.linalg.norm(QC, axis=1)))))
                max_dot = max(max_dot, float(np.max(np.abs(Qr @ Cr.T - QC @ C.T))))
                _, _, dist = base.signs_and_dist(Cr, Qr)
                cache[(seed, arm)] = dist
        if max_norm > TOL or max_dot > TOL:
            raise RuntimeError(f"continuous invariance failure norm={max_norm} dot={max_dot}")

        for qi, q in enumerate(rep["qas"]):
            gold = base.gold_rows(q, rep["id_to_row"])
            if not gold:
                continue
            valid += 1
            qid = str(q["question_id"])
            native = base.mean_fractional_for_dist(common, dist0[qi], priorities, gold)
            native_vals.append(native)
            tie_identity = f"archive_ordinal={ci};nuisance=20;stable_archive_seed(ci,t)+99"
            for seed in ROTATION_SEEDS:
                for arm in arms:
                    v = base.mean_fractional_for_dist(common, cache[(seed, arm)][qi], priorities, gold)
                    perq.append({
                        "dataset": "LoCoMo", "question_id": qid, "arm": arm,
                        "rotation_seed": seed,
                        "partition_seed": PARTITION_SEEDS[ROTATION_SEEDS.index(seed)] if arm == "RANDOM32" else "",
                        "fractional_R3": v, "native_fractional_R3": native,
                        "tie_identity": tie_identity,
                    })

    if valid != 1535:
        raise RuntimeError(f"valid denominator changed: {valid}")
    native = float(np.mean(native_vals))
    repro = abs(native - FROZEN_NATIVE_R3)
    if repro > TOL:
        raise RuntimeError(f"native reproduction failure {native} err={repro}")

    pdf = pd.DataFrame(perq).sort_values(["question_id", "rotation_seed", "arm"], kind="mergesort").reset_index(drop=True)
    expected = valid * len(ROTATION_SEEDS) * len(arms)
    if len(pdf) != expected:
        raise RuntimeError(f"per-question row count failure {len(pdf)} != {expected}")
    keys = ["question_id", "rotation_seed", "arm"]
    if pdf.duplicated(keys).any():
        raise RuntimeError("duplicate primary per-question records")
    if pdf[keys].drop_duplicates().shape[0] != expected:
        raise RuntimeError("primary coverage failure")
    perq_path = out / "locomo_boundary_per_question.csv.gz"
    pdf.to_csv(perq_path, index=False, compression="gzip")

    l_full = native - FROZEN_FULL_HAAR_R3
    seed_rows = []
    arm_stats = {}
    for arm in arms:
        rows = []
        for seed in ROTATION_SEEDS:
            vals = pdf[(pdf.arm == arm) & (pdf.rotation_seed == seed)].fractional_R3.to_numpy(float)
            if len(vals) != valid:
                raise RuntimeError(f"seed coverage failure arm={arm} seed={seed}")
            r3 = float(vals.mean())
            b = int(arm[1:]) if arm.startswith("B") else None
            row = {"arm": arm, "boundary": b, "rotation_seed": seed, "R3": r3,
                   "rho": float((native - r3) / l_full)}
            rows.append(row)
            seed_rows.append(row)
        arm_stats[arm] = stats_from_seed_rows(rows, native, l_full)
    sdf = pd.DataFrame(seed_rows)
    sdf.to_csv(out / "locomo_boundary_seed_results.csv", index=False)

    suff = [b for b in BOUNDARIES if arm_stats[f"B{b}"]["rho"] <= 0.25]
    rho32 = arm_stats["B32"]["rho"]
    rhorand = arm_stats["RANDOM32"]["rho"]
    delta = rhorand - rho32
    p1 = rho32 <= 0.25
    p2 = "SPECTRAL_POSITION_CONFIRMED" if delta >= 0.25 else ("SPECTRAL_POSITION_FALSIFIED" if delta <= 0.05 else "MIXED")

    summary = {
        "status": "PREREGISTERED_BOUNDARY_LOCALIZATION_RESULT",
        "benchmark": "LoCoMo",
        "prereg_git_blob": PREREG_GIT_BLOB,
        "post_audit_addendum_git_blob": ADDENDUM_GIT_BLOB,
        "base_git_blob": BASE_GIT_BLOB,
        "identity": {"dataset_sha256": common.DATASET_SHA256, "audit_manifest_sha256": common.AUDIT_MANIFEST_SHA256,
                     "valid_questions": valid, "boundaries": BOUNDARIES, "rotation_seeds": ROTATION_SEEDS,
                     "partition_seeds": PARTITION_SEEDS},
        "controls": {"native_reproduction": native, "frozen_native": FROZEN_NATIVE_R3,
                     "absolute_reproduction_error": repro, "signed_permutation_exact_pass": signed_perm_pass,
                     "continuous_norm_max_abs_error": max_norm, "continuous_dot_max_abs_error": max_dot,
                     "partition_checks_pass": True, "matched_q32_q64_max_abs_error": q_pair_max,
                     "per_question_expected_rows": expected, "per_question_actual_rows": len(pdf)},
        "primary": {"native_R3": native, "frozen_full_haar_R3": FROZEN_FULL_HAAR_R3, "L_full": l_full,
                    "arm_stats": arm_stats, "S_dataset": suff, "P1_rho32_pass": p1,
                    "rho32": rho32, "rho_random32": rhorand, "Delta32": delta, "P2": p2},
        "artifacts": {"per_question_file": perq_path.name, "per_question_sha256": sha256_file(perq_path),
                      "partitions_file": "locomo_boundary_random_partitions.json",
                      "partitions_sha256": sha256_file(out / "locomo_boundary_random_partitions.json")},
        "interpretation_ceiling": "Fixed-grid fixed-dataset causal localization under one shared pipeline; no universal or globally optimal-boundary claim."
    }
    (out / "locomo_boundary_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    run(args.out)
