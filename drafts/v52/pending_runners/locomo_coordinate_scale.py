"""LoCoMo coordinate-scale participation runner — PENDING AUTHORIZATION.

Deliberately NOT placed at research/v52/ and its workflow is NOT under .github/workflows/, so it
cannot be picked up or triggered. On authorization it moves into the sealed package unchanged.

Design values are frozen by the candidate preregistration; every constant below is quoted from it.

Revision 2026-09-07 (pre-authorization, disclosed here and in README_PENDING.md): the rotation
invariance check no longer builds the full archive Gram matrix X X^T. It compares query-to-archive
dot products and row norms exactly as the audited boundary-localization stage does. This is the
narrowing that L-049 recorded in advance as the correct fix for the check's cost; TOL is unchanged.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "locomo_spectral_band_haar_causal.py"   # resolved inside the sealed package
BASE_GIT_BLOB = "7c4140252fb7f846d617189925cdf534515743f4"
ROTATION_SEEDS = list(range(59001, 59011))
FROZEN_NATIVE_R3 = 0.23654714666441054
EPS_SIGMA = 1e-12
DEGENERATE_FLAG_THRESHOLD = 4
TOL = 1e-12
ARMS = ["NATIVE", "SCALED_NATIVE", "FULLHAAR_FRESH", "SCALED_FULLHAAR", "BLOCK32_FRESH", "SCALED_BLOCK32"]


def load_base():
    spec = importlib.util.spec_from_file_location("locomo_scale_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen LoCoMo base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def full_matrix(base, seed: int) -> np.ndarray:
    return base.haar_q(np.random.default_rng(seed), 96)


def block_matrix(base, seed: int, b: int = 32) -> np.ndarray:
    """Head block drawn FIRST from one stream, exactly as the audited stages do."""
    rng = np.random.default_rng(seed)
    qh = base.haar_q(rng, b)
    qt = base.haar_q(rng, 96 - b)
    R = np.zeros((96, 96), dtype=float)
    R[:b, :b] = qh
    R[b:, b:] = qt
    return R


def scale_matrix(C: np.ndarray):
    """D = diag(1/sigma) on the EXACT centered archive representation; per-archive; archive content only.

    Never derived from queries, gold sets or outcomes. Degenerate coordinates fall back to 1.0.
    """
    sigma = C.std(axis=0)
    ok = sigma >= EPS_SIGMA
    d = np.where(ok, 1.0 / np.where(ok, sigma, 1.0), 1.0)
    cv = float(sigma.std() / sigma.mean()) if sigma.mean() > 0 else float("nan")
    return np.diag(d), int((~ok).sum()), cv


def check_identity(C: np.ndarray, QC: np.ndarray, D: np.ndarray) -> None:
    """sign(xD) = sign(x) must hold BIT-IDENTICALLY, not within tolerance."""
    if not np.array_equal((C @ D) >= 0, C >= 0) or not np.array_equal((QC @ D) >= 0, QC >= 0):
        raise RuntimeError("IDENTITY VIOLATION: sign(xD) != sign(x); the design premise fails, aborting")


def check_rotation_invariance(X: np.ndarray, XQ: np.ndarray, R: np.ndarray) -> tuple[float, float]:
    """Norm/dot equality is asserted WITHIN a representation and its own rotation, never between
    the original and the rescaled representation, where it is not expected to hold.

    Scope: archive row norms, query row norms, and the query-to-archive dot products XQ X^T - the
    same quantities the audited boundary-localization stage checked. The full Gram matrix X X^T is
    deliberately NOT built (quadratic in archive rows; see module docstring).
    """
    Xr, XQr = X @ R, XQ @ R
    n = max(float(np.max(np.abs(np.linalg.norm(Xr, axis=1) - np.linalg.norm(X, axis=1)))),
            float(np.max(np.abs(np.linalg.norm(XQr, axis=1) - np.linalg.norm(XQ, axis=1)))))
    d = float(np.max(np.abs(XQr @ Xr.T - XQ @ X.T)))
    return n, d


def seed_dispersion(values: list[float]) -> dict:
    """Per-seed dispersion of a quantity measured inside this experiment (prereg section 8)."""
    x = np.asarray(values, dtype=float)
    return {"per_seed": [float(v) for v in x], "mean": float(x.mean()),
            "sample_sd": float(x.std(ddof=1)), "se": float(x.std(ddof=1) / np.sqrt(len(x))),
            "min": float(x.min()), "max": float(x.max())}


def frac(native: float, unscaled: float, scaled: float) -> float:
    """Share of an arm's OWN loss recovered by rescaling. Denominator measured in this experiment."""
    denom = native - unscaled
    if denom == 0.0:
        return float("nan")
    return (scaled - unscaled) / denom


def band(f: float) -> str:
    if not np.isfinite(f):
        return "[UNDEFINED]"
    if f >= 0.70:
        return "[SCALE ACCOUNTS FOR MOST OF THIS ARM'S DAMAGE]"
    if f <= 0.20:
        return "[SCALE ACCOUNTS FOR LITTLE OF THIS ARM'S DAMAGE]"
    return "[PARTIAL]"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(out: Path) -> None:
    base = load_base()
    common = base.load_common()
    out.mkdir(parents=True, exist_ok=True)
    raw, audit, _ = common.acquire_and_verify(out / "source_bytes")
    convs, _ = common.load_dataset(raw, audit)
    reps = [common.build_representation(c) for c in convs]

    fulls = {s: full_matrix(base, s) for s in ROTATION_SEEDS}
    blocks = {s: block_matrix(base, s) for s in ROTATION_SEEDS}
    for s in ROTATION_SEEDS:
        for name, R in (("FULL", fulls[s]), ("BLOCK", blocks[s])):
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality failure {name} seed={s}: {err}")

    perq, native_vals, diagnostics = [], [], []
    max_norm = max_dot = 0.0
    valid = 0

    for ci, rep in enumerate(reps):
        C, QC = rep["C"], rep["QC"]
        if not (np.all(np.isfinite(C)) and np.all(np.isfinite(QC))):
            raise RuntimeError("non-finite value in the centered representation; aborting, not repairing")
        D, n_degen, cv_before = scale_matrix(C)
        check_identity(C, QC, D)
        Cs, QCs = C @ D, QC @ D
        if not (np.all(np.isfinite(Cs)) and np.all(np.isfinite(QCs))):
            raise RuntimeError("non-finite value in the rescaled representation C D; aborting, not repairing")
        sigma_after = Cs.std(axis=0)
        cv_after = float(sigma_after.std() / sigma_after.mean())
        diagnostics.append({"archive_ordinal": ci, "degenerate_coords": n_degen,
                            "cv_sigma_before": cv_before, "cv_sigma_after": cv_after,
                            "flagged": bool(n_degen > DEGENERATE_FLAG_THRESHOLD)})

        _, _, dist_native = base.signs_and_dist(C, QC)
        _, _, dist_scaled_native = base.signs_and_dist(Cs, QCs)
        if not np.array_equal(dist_scaled_native, dist_native):
            raise RuntimeError("SCALED_NATIVE distance matrix differs from NATIVE; aborting")

        priorities = [np.random.default_rng(common.stable_archive_seed(ci, t) + 99).random(len(C))
                      for t in range(common.N_NUISANCE)]

        cache = {}
        for s in ROTATION_SEEDS:
            for arm, X, XQ, R in (("FULLHAAR_FRESH", C, QC, fulls[s]),
                                  ("SCALED_FULLHAAR", Cs, QCs, fulls[s]),
                                  ("BLOCK32_FRESH", C, QC, blocks[s]),
                                  ("SCALED_BLOCK32", Cs, QCs, blocks[s])):
                n, d = check_rotation_invariance(X, XQ, R)
                max_norm, max_dot = max(max_norm, n), max(max_dot, d)
                _, _, dist = base.signs_and_dist(X @ R, XQ @ R)
                cache[(s, arm)] = dist
        if max_norm > TOL or max_dot > TOL:
            raise RuntimeError(f"within-representation invariance failure norm={max_norm} dot={max_dot}")

        for qi, q in enumerate(rep["qas"]):
            gold = base.gold_rows(q, rep["id_to_row"])
            if not gold:
                continue
            valid += 1
            qid = str(q["question_id"])
            nat = base.mean_fractional_for_dist(common, dist_native[qi], priorities, gold)
            native_vals.append(nat)
            tie = f"archive_ordinal={ci};nuisance=20;stable_archive_seed(ci,t)+99"
            for s in ROTATION_SEEDS:
                row = {"dataset": "LoCoMo", "question_id": qid, "rotation_seed": s,
                       "native_fractional_R3": nat, "tie_identity": tie}
                for arm in ("NATIVE", "SCALED_NATIVE"):
                    perq.append({**row, "arm": arm, "fractional_R3": nat})
                for arm in ("FULLHAAR_FRESH", "SCALED_FULLHAAR", "BLOCK32_FRESH", "SCALED_BLOCK32"):
                    v = base.mean_fractional_for_dist(common, cache[(s, arm)][qi], priorities, gold)
                    perq.append({**row, "arm": arm, "fractional_R3": v})

    if valid != 1535:
        raise RuntimeError(f"valid denominator changed: {valid}")
    native = float(np.mean(native_vals))
    if abs(native - FROZEN_NATIVE_R3) > TOL:
        raise RuntimeError(f"native reproduction failure {native}")

    pdf = pd.DataFrame(perq).sort_values(["question_id", "rotation_seed", "arm"], kind="mergesort").reset_index(drop=True)
    expected = valid * len(ROTATION_SEEDS) * len(ARMS)
    if len(pdf) != expected or pdf.duplicated(["question_id", "rotation_seed", "arm"]).any():
        raise RuntimeError(f"per-question completeness failure {len(pdf)} != {expected}")
    pdf.to_csv(out / "locomo_scale_per_question.csv.gz", index=False, compression="gzip")

    arm_seed = {}
    for arm in ARMS:
        for s in ROTATION_SEEDS:
            arm_seed[(arm, s)] = float(pdf[(pdf.arm == arm) & (pdf.rotation_seed == s)].fractional_R3.mean())
    means = {arm: float(np.mean([arm_seed[(arm, s)] for s in ROTATION_SEEDS])) for arm in ARMS}

    per_seed_frac = {
        "full": [frac(means["NATIVE"], arm_seed[("FULLHAAR_FRESH", s)], arm_seed[("SCALED_FULLHAAR", s)]) for s in ROTATION_SEEDS],
        "block": [frac(means["NATIVE"], arm_seed[("BLOCK32_FRESH", s)], arm_seed[("SCALED_BLOCK32", s)]) for s in ROTATION_SEEDS],
    }
    frac_full = frac(means["NATIVE"], means["FULLHAAR_FRESH"], means["SCALED_FULLHAAR"])
    frac_block = frac(means["NATIVE"], means["BLOCK32_FRESH"], means["SCALED_BLOCK32"])

    summary = {
        "status": "PREREGISTERED_COORDINATE_SCALE_RESULT",
        "benchmark": "LoCoMo",
        "base_git_blob": BASE_GIT_BLOB,
        "identity": {"valid_questions": valid, "rotation_seeds": ROTATION_SEEDS, "arms": ARMS,
                     "scale_rule": "d_i = 1/sigma_i on the centered archive representation, per archive, eps=1e-12"},
        "controls": {
            "native_reproduction": native, "frozen_native": FROZEN_NATIVE_R3,
            "absolute_reproduction_error": abs(native - FROZEN_NATIVE_R3),
            "scaled_native_bit_identical": True,
            "within_representation_norm_max_abs_error": max_norm,
            "within_representation_dot_max_abs_error": max_dot,
            "per_question_expected_rows": expected, "per_question_actual_rows": int(len(pdf)),
        },
        "primary": {
            "arm_means": means,
            "denominator_full": means["NATIVE"] - means["FULLHAAR_FRESH"],
            "denominator_block": means["NATIVE"] - means["BLOCK32_FRESH"],
            "denominator_full_dispersion": seed_dispersion([means["NATIVE"] - arm_seed[("FULLHAAR_FRESH", s)] for s in ROTATION_SEEDS]),
            "denominator_block_dispersion": seed_dispersion([means["NATIVE"] - arm_seed[("BLOCK32_FRESH", s)] for s in ROTATION_SEEDS]),
            "fullhaar_fresh_R3_dispersion": seed_dispersion([arm_seed[("FULLHAAR_FRESH", s)] for s in ROTATION_SEEDS]),
            "frac_full": frac_full, "frac_block": frac_block,
            "frac_full_band": band(frac_full), "frac_block_band": band(frac_block),
            "frac_full_per_seed": per_seed_frac["full"], "frac_block_per_seed": per_seed_frac["block"],
            "I_frac_secondary": frac_full - frac_block,
            "descriptive_pp_only": {
                "delta_full_pp": (means["SCALED_FULLHAAR"] - means["FULLHAAR_FRESH"]) * 100.0,
                "delta_block_pp": (means["SCALED_BLOCK32"] - means["BLOCK32_FRESH"]) * 100.0,
                "note": "descriptive only; barred from carrying the verdict (floor-confounded)",
            },
        },
        "diagnostics": {"cv_sigma_per_archive": diagnostics},
        "interpretation_ceiling": ("Fixed-benchmark preregistered causal-intervention evidence under one shared pipeline. "
                                   "Not necessity, not a global claim, not independent replication, nothing about Task 4F1."),
    }
    (out / "locomo_scale_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    run(ap.parse_args().out)
