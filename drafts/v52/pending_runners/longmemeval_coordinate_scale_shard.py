"""LongMemEval coordinate-scale participation runner, deterministic sharded — PENDING AUTHORIZATION.

Deliberately NOT placed at research/v52/ and its workflow is NOT under .github/workflows/, so it
cannot be picked up or triggered. On authorization it moves into the sealed package unchanged.

Design values are frozen by the candidate preregistration; every constant below is quoted from it.
Sharding mirrors the audited boundary-localization shard runner exactly: shard membership is
`i % num_shards == shard_index` over the sorted primary cohort, nuisance priorities are keyed on the
global lexical ordinal, and the aggregate step re-checks 470/470 coverage, native reproduction and
the invariance maxima before computing any preregistered quantity.

Every function that does not touch the corpus is kept pure so that it can be tested on synthetic
data; the corpus-bound parts (`eval_one`, `run_shard`) only wire those functions to the frozen base.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "longmemeval_spectral_band_haar_causal.py"   # resolved inside the sealed package
BASE_GIT_BLOB = "79dd4a5ec462102da5d82530088a4b7e89bef437"
ROTATION_SEEDS = list(range(59001, 59011))
EXPECTED_PRIMARY = 470
EPS_SIGMA = 1e-12
DEGENERATE_FLAG_THRESHOLD = 4
TOL = 1e-12
ARMS = ["NATIVE", "SCALED_NATIVE", "FULLHAAR_FRESH", "SCALED_FULLHAAR", "BLOCK32_FRESH", "SCALED_BLOCK32"]
ROTATED_ARMS = ["FULLHAAR_FRESH", "SCALED_FULLHAAR", "BLOCK32_FRESH", "SCALED_BLOCK32"]


def load_base():
    spec = importlib.util.spec_from_file_location("lm_scale_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen LongMemEval base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------------------------
# Pure functions (no corpus). Bodies are identical to the LoCoMo runner's; the test asserts it.
# ---------------------------------------------------------------------------------------------

def haar_q(rng: np.random.Generator, d: int) -> np.ndarray:
    """Same construction as the frozen bases and the audited shard runners."""
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    sg = np.where(np.diag(R) < 0, -1.0, 1.0)
    return Q * sg[None, :]


def full_matrix(seed: int) -> np.ndarray:
    return haar_q(np.random.default_rng(seed), 96)


def block_matrix(seed: int, b: int = 32) -> np.ndarray:
    """Head block drawn FIRST from one stream, exactly as the audited stages do."""
    rng = np.random.default_rng(seed)
    qh = haar_q(rng, b)
    qt = haar_q(rng, 96 - b)
    R = np.zeros((96, 96), dtype=float)
    R[:b, :b] = qh
    R[b:, b:] = qt
    return R


def build_transforms() -> dict:
    """All rotation matrices for the seed panel, orthogonality-checked at TOL."""
    transforms = {}
    for s in ROTATION_SEEDS:
        for name, R in (("FULL", full_matrix(s)), ("BLOCK", block_matrix(s))):
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality failure {name} seed={s}: {err}")
            transforms[(s, name)] = R
    return transforms


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
    same quantities the audited boundary-localization stage checked. No full Gram matrix is built.
    """
    Xr, XQr = X @ R, XQ @ R
    n = max(float(np.max(np.abs(np.linalg.norm(Xr, axis=1) - np.linalg.norm(X, axis=1)))),
            float(np.max(np.abs(np.linalg.norm(XQr, axis=1) - np.linalg.norm(XQ, axis=1)))))
    d = float(np.max(np.abs(XQr @ Xr.T - XQ @ X.T)))
    return n, d


def hamming_dist(C: np.ndarray, qC: np.ndarray) -> np.ndarray:
    """Zero-threshold sign code, Hamming distance from one query to every archive row (int16)."""
    return np.count_nonzero((C >= 0) != (qC >= 0)[None, :], axis=1).astype(np.int16)


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


def seed_dispersion(values: list[float]) -> dict:
    """Per-seed dispersion of a quantity measured inside this experiment (prereg section 8)."""
    x = np.asarray(values, dtype=float)
    return {"per_seed": [float(v) for v in x], "mean": float(x.mean()),
            "sample_sd": float(x.std(ddof=1)), "se": float(x.std(ddof=1) / np.sqrt(len(x))),
            "min": float(x.min()), "max": float(x.max())}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def evaluate_representation(C: np.ndarray, qC: np.ndarray, gold: np.ndarray, priorities: list,
                            transforms: dict, mean_r3) -> dict:
    """Everything the experiment computes for ONE archive/question, given a scoring callable.

    Pure: no corpus, no base module. `mean_r3(dist, priorities, gold) -> float` is injected so that
    this function can be exercised end-to-end on synthetic data. The design premises are enforced as
    aborts here, not assumed.
    """
    if not (np.all(np.isfinite(C)) and np.all(np.isfinite(qC))):
        raise RuntimeError("non-finite value in the centered representation; aborting, not repairing")
    D, n_degen, cv_before = scale_matrix(C)
    check_identity(C, qC[None, :], D)
    Cs, qCs = C @ D, qC @ D
    if not (np.all(np.isfinite(Cs)) and np.all(np.isfinite(qCs))):
        raise RuntimeError("non-finite value in the rescaled representation C D; aborting, not repairing")
    sigma_after = Cs.std(axis=0)
    cv_after = float(sigma_after.std() / sigma_after.mean())

    d_native = hamming_dist(C, qC)
    d_scaled_native = hamming_dist(Cs, qCs)
    if not np.array_equal(d_scaled_native, d_native):
        raise RuntimeError("SCALED_NATIVE distance vector differs from NATIVE; aborting")
    native = float(mean_r3(d_native, priorities, gold))

    rows = []
    max_norm = max_dot = 0.0
    for s in ROTATION_SEEDS:
        for arm, X, xq, R in (("FULLHAAR_FRESH", C, qC, transforms[(s, "FULL")]),
                              ("SCALED_FULLHAAR", Cs, qCs, transforms[(s, "FULL")]),
                              ("BLOCK32_FRESH", C, qC, transforms[(s, "BLOCK")]),
                              ("SCALED_BLOCK32", Cs, qCs, transforms[(s, "BLOCK")])):
            n, d = check_rotation_invariance(X, xq[None, :], R)
            max_norm, max_dot = max(max_norm, n), max(max_dot, d)
            rows.append({"arm": arm, "rotation_seed": s,
                         "fractional_R3": float(mean_r3(hamming_dist(X @ R, xq @ R), priorities, gold))})
        for arm in ("NATIVE", "SCALED_NATIVE"):
            rows.append({"arm": arm, "rotation_seed": s, "fractional_R3": native})
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError(f"within-representation invariance failure norm={max_norm} dot={max_dot}")
    return {"native": native, "rows": rows, "max_norm": max_norm, "max_dot": max_dot,
            "diagnostics": {"degenerate_coords": n_degen, "cv_sigma_before": cv_before,
                            "cv_sigma_after": cv_after, "flagged": bool(n_degen > DEGENERATE_FLAG_THRESHOLD)}}


def summarize(results: list[dict], frozen_native: float, n_expected: int) -> tuple[pd.DataFrame, dict]:
    """Pure aggregate over per-question results (each as returned by evaluate_representation, plus
    'qid' and 'lex'). Re-checks coverage, native reproduction and invariance maxima, then computes
    the preregistered quantities. Returns the per-question table and the summary dict."""
    results = sorted(results, key=lambda z: z["qid"])
    qids = [z["qid"] for z in results]
    if len(results) != n_expected or len(set(qids)) != n_expected:
        raise RuntimeError(f"{n_expected}/{n_expected} integrity failure: {len(results)} results, {len(set(qids))} unique")
    native = float(np.mean([z["native"] for z in results]))
    repro = abs(native - frozen_native)
    if repro > TOL:
        raise RuntimeError(f"native reproduction failure got={native} err={repro}")
    max_norm = max(z["max_norm"] for z in results)
    max_dot = max(z["max_dot"] for z in results)
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError("within-representation invariance aggregate failure")

    perq = []
    for z in results:
        tie = f"global_lex={z['lex']};nuisance=20;5100000+lex*100000+t*100+99"
        for r in z["rows"]:
            perq.append({"dataset": "LongMemEval", "question_id": z["qid"], "rotation_seed": r["rotation_seed"],
                         "arm": r["arm"], "fractional_R3": r["fractional_R3"],
                         "native_fractional_R3": z["native"], "tie_identity": tie})
    pdf = pd.DataFrame(perq).sort_values(["question_id", "rotation_seed", "arm"], kind="mergesort").reset_index(drop=True)
    expected = n_expected * len(ROTATION_SEEDS) * len(ARMS)
    if len(pdf) != expected or pdf.duplicated(["question_id", "rotation_seed", "arm"]).any():
        raise RuntimeError(f"per-question completeness failure {len(pdf)} != {expected}")

    arm_seed = {}
    for arm in ARMS:
        for s in ROTATION_SEEDS:
            vals = pdf[(pdf.arm == arm) & (pdf.rotation_seed == s)].fractional_R3.to_numpy(float)
            if len(vals) != n_expected:
                raise RuntimeError(f"seed coverage failure arm={arm} seed={s}")
            arm_seed[(arm, s)] = float(vals.mean())
    means = {arm: float(np.mean([arm_seed[(arm, s)] for s in ROTATION_SEEDS])) for arm in ARMS}
    if means["SCALED_NATIVE"] != means["NATIVE"]:
        raise RuntimeError("SCALED_NATIVE mean differs from NATIVE after aggregation")

    per_seed_frac = {
        "full": [frac(means["NATIVE"], arm_seed[("FULLHAAR_FRESH", s)], arm_seed[("SCALED_FULLHAAR", s)]) for s in ROTATION_SEEDS],
        "block": [frac(means["NATIVE"], arm_seed[("BLOCK32_FRESH", s)], arm_seed[("SCALED_BLOCK32", s)]) for s in ROTATION_SEEDS],
    }
    frac_full = frac(means["NATIVE"], means["FULLHAAR_FRESH"], means["SCALED_FULLHAAR"])
    frac_block = frac(means["NATIVE"], means["BLOCK32_FRESH"], means["SCALED_BLOCK32"])
    diagnostics = [{"question_id": z["qid"], **z["diagnostics"]} for z in results]

    summary = {
        "status": "PREREGISTERED_COORDINATE_SCALE_RESULT",
        "execution": "DETERMINISTIC_SHARDED_SEMANTICS_INVARIANT",
        "benchmark": "LongMemEval",
        "base_git_blob": BASE_GIT_BLOB,
        "identity": {"primary_questions": n_expected, "rotation_seeds": ROTATION_SEEDS, "arms": ARMS,
                     "scale_rule": "d_i = 1/sigma_i on the centered archive representation, per archive, eps=1e-12"},
        "controls": {
            "native_reproduction": native, "frozen_native": frozen_native,
            "absolute_reproduction_error": repro,
            "scaled_native_bit_identical": True,
            "within_representation_norm_max_abs_error": max_norm,
            "within_representation_dot_max_abs_error": max_dot,
            "per_question_expected_rows": expected, "per_question_actual_rows": int(len(pdf)),
            "archives_flagged_degenerate": int(sum(1 for d in diagnostics if d["flagged"])),
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
    return pdf, summary


# ---------------------------------------------------------------------------------------------
# Corpus-bound wiring (never executed outside an authorized, sealed run).
# ---------------------------------------------------------------------------------------------

def eval_one(item, lex: int, transforms: dict) -> dict:
    b = load_base()
    a2 = b.load_module(b.A2_PATH, f"lm_scale_v2_{os.getpid()}_{lex}")
    qid, C, qC, gold = b.build_rep(item, a2)
    priorities = [np.random.default_rng(5_100_000 + lex * 100_000 + t * 100 + 99).random(len(C))
                  for t in range(b.N_NUISANCE)]
    z = evaluate_representation(C, qC, gold, priorities, transforms, b.mean_r3)
    return {"qid": str(qid), "lex": int(lex), **z}


def run_shard(dataset: Path, idx: int, nshards: int, out: Path) -> None:
    b = load_base()
    if dataset.stat().st_size != b.DATASET_BYTES or b.sha256_file(dataset) != b.DATASET_SHA256:
        raise RuntimeError("dataset identity mismatch")
    if b.sha256_file(b.A1_PATH) != b.A1_SHA256 or b.sha256_file(b.A2_PATH) != b.A2_SHA256:
        raise RuntimeError("adapter identity mismatch")
    data = json.loads(dataset.read_text(encoding="utf-8"))
    prim = [x for x in data if not str(x["question_id"]).endswith("_abs")]
    if len(data) != 500 or len(prim) != EXPECTED_PRIMARY or b.EXPECTED_PRIMARY != EXPECTED_PRIMARY:
        raise RuntimeError("cohort mismatch")
    allq = sorted(str(x["question_id"]) for x in data)
    lexmap = {q: i for i, q in enumerate(allq)}
    chosen = [x for i, x in enumerate(prim) if i % nshards == idx]
    transforms = build_transforms()
    results = [eval_one(x, lexmap[str(x["question_id"])], transforms) for x in chosen]
    qids = [z["qid"] for z in results]
    if len(qids) != len(set(qids)) or len(qids) != len(chosen):
        raise RuntimeError("shard integrity failure")
    payload = {"shard_index": idx, "num_shards": nshards, "count": len(results),
               "rotation_seeds": ROTATION_SEEDS, "results": results}
    out.write_bytes(pickle.dumps(payload, pickle.HIGHEST_PROTOCOL))
    print(json.dumps({"shard": idx, "count": len(results),
                      "max_norm": max(z["max_norm"] for z in results) if results else 0.0,
                      "max_dot": max(z["max_dot"] for z in results) if results else 0.0}))


def aggregate(shard_dir: Path, out: Path) -> None:
    b = load_base()
    files = sorted(shard_dir.rglob("shard_*.pkl"))
    payloads = [pickle.loads(p.read_bytes()) for p in files]
    ns = {int(p["num_shards"]) for p in payloads}
    if len(ns) != 1:
        raise RuntimeError("mixed shard counts")
    nshards = ns.pop()
    inds = sorted(int(p["shard_index"]) for p in payloads)
    if inds != list(range(nshards)):
        raise RuntimeError(f"missing/duplicate shard indices: {inds}")
    if any(p["rotation_seeds"] != ROTATION_SEEDS for p in payloads):
        raise RuntimeError("rotation seed panel differs across shards")
    results = [z for p in payloads for z in p["results"]]
    pdf, summary = summarize(results, b.FROZEN_NATIVE_R3, EXPECTED_PRIMARY)
    summary["identity"].update({"dataset_sha256": b.DATASET_SHA256, "dataset_bytes": b.DATASET_BYTES,
                                "adapter_v1_sha256": b.A1_SHA256, "adapter_v2_sha256": b.A2_SHA256,
                                "shards": nshards})
    out.mkdir(parents=True, exist_ok=True)
    perq_path = out / "longmemeval_scale_per_question.csv.gz"
    pdf.to_csv(perq_path, index=False, compression="gzip")
    summary["artifacts"] = {"per_question_file": perq_path.name, "per_question_sha256": sha256_file(perq_path)}
    (out / "longmemeval_scale_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shard")
    s.add_argument("--dataset", type=Path, required=True)
    s.add_argument("--shard-index", type=int, required=True)
    s.add_argument("--num-shards", type=int, required=True)
    s.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--shard-dir", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.cmd == "shard":
        run_shard(args.dataset, args.shard_index, args.num_shards, args.out)
    else:
        aggregate(args.shard_dir, args.out)
