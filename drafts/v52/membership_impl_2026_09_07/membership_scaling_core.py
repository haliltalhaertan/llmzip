"""Membership-under-scaling: pure core. IMPLEMENTATION PREPARATION ONLY.

Implements the design accepted at docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md,
whose precedence is R2 -> R1 -> draft. Real-data execution is OFF by default and this module reads no
corpus, downloads nothing, and imports nothing that does.

Deliberately ABSENT, because the binding record lists them as dead and forbidden: any ratio of Delta
to G under any name; the four cut points of the withdrawn categorical scheme; any categorical verdict
label; the floor that existed to protect that ratio's denominator; the RELATIVE SCALE UNSUITABLE
state; the INDETERMINATE overlay; the three-band rule; any band on the remaining gap; the per-seed
positivity gate.

The executable code below contains none of them. One word needs a caveat so the claim stays exactly
true: DEGENERATE_FLAG_THRESHOLD is a per-archive DIAGNOSTIC counter inherited from the accepted
design (R1 section 1) and is not a decision threshold - it gates nothing, and no result depends on
it. The test suite asserts that this is the only occurrence of the word.

The deliverable is three quantities in PERCENTAGE POINTS: the gap before the intervention, the gap
remaining after it, and their paired change - each with per-seed values and a resampling interval.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------------------------
# Frozen design constants (draft sections 6, 12; R1 sections 1, 2)
# --------------------------------------------------------------------------------------------
ARMS = ("NATIVE", "SCALED_NATIVE", "B32_FRESH", "SCALED_B32", "RANDOM32_FRESH", "SCALED_RANDOM32")
ROTATION_SEEDS = tuple(range(60001, 60011))
PARTITION_SEEDS = tuple(range(70001, 70011))   # paired one-to-one by position, NOT crossed
DIM = 96
BLOCK = 32
EPS_SIGMA = 1e-12
DEGENERATE_FLAG_THRESHOLD = 4
TOL = 1e-12
BOOTSTRAP_REPLICATES = 10_000
PERCENTILES = (2.5, 97.5)
PP = 100.0                                      # the single place a fraction becomes a percentage point

# Real-data execution is off by default and stays off until a separate authorization exists.
REAL_DATA_EXECUTION_ENABLED = False


class DesignViolation(RuntimeError):
    """Raised when an input or an intermediate result violates the accepted design."""


def require_real_data_authorization(enabled: bool = REAL_DATA_EXECUTION_ENABLED) -> None:
    """Every corpus-touching path must call this first. It refuses by default."""
    if not enabled:
        raise DesignViolation(
            "real-data execution is OFF by default and is not authorized at this stage; "
            "no corpus may be read, and no fitting, retrieval, ranking or bootstrap may run on real data")


# --------------------------------------------------------------------------------------------
# Step 1 - the scaling operator (R1 section 1)
# --------------------------------------------------------------------------------------------
def scale_matrix(C: np.ndarray, eps: float = EPS_SIGMA):
    """D = diag(1/sigma) on the centered archive representation, per archive, archive content only.

    sigma uses ddof = 0 (the population form). The sample form differs by sqrt(n/(n-1)) and would
    define a different intervention, so the choice is explicit rather than inherited from a default.
    eps is a FALLBACK, not a clip: a coordinate below it keeps d = 1, is never divided by eps and is
    never dropped, so the transform stays total and the coordinate stays in the sign code.

    Returns (D, diagnostics). The diagnostics carry the per-archive degenerate count AND the flag the
    design requires, so that recording one without the other is not possible. They are declared
    diagnostics and gate nothing.
    """
    if C.ndim != 2 or C.shape[1] != DIM:
        raise DesignViolation(f"representation must be (n, {DIM}), got {C.shape}")
    if not np.all(np.isfinite(C)):
        raise DesignViolation("non-finite value in the centered representation; aborting, not repairing")
    sigma = C.std(axis=0, ddof=0)
    ok = sigma >= eps
    d = np.where(ok, 1.0 / np.where(ok, sigma, 1.0), 1.0)
    mean_sigma = float(sigma.mean())
    cv = float(sigma.std(ddof=0) / mean_sigma) if mean_sigma > 0 else float("nan")
    n_degenerate = int((~ok).sum())
    # R1 section 1 requires the per-archive flag, not merely the count. Returning it inside the
    # diagnostics makes it impossible for a caller to record the count and forget the flag.
    diagnostics = {
        "degenerate_coords": n_degenerate,
        "flagged": bool(n_degenerate > DEGENERATE_FLAG_THRESHOLD),
        "cv_sigma_before": cv,
        "cv_sigma_after": float((C @ np.diag(d)).std(axis=0, ddof=0).std(ddof=0)),
    }
    return np.diag(d), diagnostics


def check_identity(C: np.ndarray, Q: np.ndarray, D: np.ndarray) -> None:
    """sign(xD) = sign(x) must hold BIT-IDENTICALLY for archive and query, or the run aborts."""
    Cs, Qs = C @ D, Q @ D
    if not (np.all(np.isfinite(Cs)) and np.all(np.isfinite(Qs))):
        raise DesignViolation("non-finite value in the rescaled representation C D; aborting, not repairing")
    if not np.array_equal(Cs >= 0, C >= 0) or not np.array_equal(Qs >= 0, Q >= 0):
        raise DesignViolation("IDENTITY VIOLATION: sign(xD) != sign(x); the design premise fails")


# --------------------------------------------------------------------------------------------
# Steps 2 and 3 - membership and rotation (R1 section 2)
# --------------------------------------------------------------------------------------------
def haar_q(rng: np.random.Generator, d: int) -> np.ndarray:
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    return Q * np.where(np.diag(R) < 0, -1.0, 1.0)[None, :]


def draw_rotation_blocks(rotation_seed: int):
    """One (Q32, Q64) pair per seed, head block FIRST from a single stream, as the audited stages do.

    The same pair serves all four rotated arms at that seed; it is never redrawn per arm.
    """
    rng = np.random.default_rng(rotation_seed)
    q32 = haar_q(rng, BLOCK)
    q64 = haar_q(rng, DIM - BLOCK)
    return q32, q64


def spectral_membership() -> np.ndarray:
    """S = the leading BLOCK coordinates in SVD variance order. Fixed by the representation."""
    return np.arange(BLOCK, dtype=int)


def random_membership(partition_seed: int) -> np.ndarray:
    """S = the first BLOCK entries of a permutation. Fixed by the seed; NO data enters this choice."""
    S = np.random.default_rng(partition_seed).permutation(DIM).astype(int)[:BLOCK]
    if len(np.unique(S)) != BLOCK:
        raise DesignViolation("random membership is not a set of distinct coordinates")
    return S


def build_rotation(q32: np.ndarray, q64: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Place the GIVEN q32 at ix(S,S) and the GIVEN q64 at ix(T,T). Membership is the only variable."""
    S = np.asarray(S, dtype=int)
    T = np.setdiff1d(np.arange(DIM, dtype=int), S, assume_unique=False)
    if len(S) != BLOCK or len(T) != DIM - BLOCK or np.intersect1d(S, T).size:
        raise DesignViolation("partition is not a disjoint exhaustive split of the coordinates")
    R = np.zeros((DIM, DIM), dtype=float)
    R[np.ix_(S, S)] = q32
    R[np.ix_(T, T)] = q64
    err = float(np.max(np.abs(R.T @ R - np.eye(DIM))))
    if err > TOL:
        raise DesignViolation(f"rotation is not orthogonal to {TOL:g}: {err:g}")
    return R


def assert_matched_blocks(q32_a, q64_a, q32_b, q64_b) -> None:
    """The matched-Q control: the two memberships must use the IDENTICAL numeric blocks, exactly."""
    if float(np.max(np.abs(q32_a - q32_b))) != 0.0 or float(np.max(np.abs(q64_a - q64_b))) != 0.0:
        raise DesignViolation("matched-Q control failed: the two memberships do not share identical blocks")


def check_rotation_invariance(X: np.ndarray, XQ: np.ndarray, R: np.ndarray):
    """Row norms and query-to-archive dots, WITHIN a representation and its own rotation only."""
    Xr, XQr = X @ R, XQ @ R
    n = max(float(np.max(np.abs(np.linalg.norm(Xr, axis=1) - np.linalg.norm(X, axis=1)))),
            float(np.max(np.abs(np.linalg.norm(XQr, axis=1) - np.linalg.norm(XQ, axis=1)))))
    d = float(np.max(np.abs(XQr @ Xr.T - XQ @ X.T)))
    return n, d


def hamming_dist(C: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Zero-threshold sign code, Hamming distance from one query to every archive row."""
    return np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1).astype(np.int16)


# --------------------------------------------------------------------------------------------
# Record validation - nothing missing, duplicated or invalid is accepted silently
# --------------------------------------------------------------------------------------------
def validate_per_question_records(records, question_ids, seeds=ROTATION_SEEDS, arms=ARMS) -> None:
    """Every (question, seed, arm) present exactly once, with a finite score in [0, 1]."""
    qset, sset, aset = list(question_ids), list(seeds), list(arms)
    expected = {(str(q), int(s), str(a)) for q in qset for s in sset for a in aset}
    seen, duplicates, invalid = set(), [], []
    for r in records:
        try:
            key = (str(r["question_id"]), int(r["rotation_seed"]), str(r["arm"]))
            v = float(r["fractional_R3"])
        except (KeyError, TypeError, ValueError) as exc:
            invalid.append(("malformed record", repr(r)[:120], str(exc)))
            continue
        if key not in expected:
            invalid.append(("unexpected key", key, ""))
            continue
        if not math.isfinite(v) or not (0.0 <= v <= 1.0):
            invalid.append(("score out of range or non-finite", key, v))
            continue
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    missing = expected - seen
    problems = []
    if missing:
        problems.append(f"{len(missing)} missing record(s), e.g. {sorted(missing)[:3]}")
    if duplicates:
        problems.append(f"{len(duplicates)} duplicate record(s), e.g. {duplicates[:3]}")
    if invalid:
        problems.append(f"{len(invalid)} invalid record(s), e.g. {invalid[:3]}")
    if problems:
        raise DesignViolation("record validation failed: " + "; ".join(problems))


def paired_matrices(records, question_ids, seeds=ROTATION_SEEDS):
    """Build the per-question, per-seed paired quantities, in PERCENTAGE POINTS.

    g[q, k]  = B32_FRESH  - RANDOM32_FRESH    the gap before the intervention
    gs[q, k] = SCALED_B32 - SCALED_RANDOM32   the gap remaining after it

    Differencing at the question level is what makes the pairing real: the same question contributes
    to both arms of a gap, so a resample that selects it selects it for both.
    """
    validate_per_question_records(records, question_ids, seeds)
    qi = {str(q): i for i, q in enumerate(question_ids)}
    ki = {int(s): j for j, s in enumerate(seeds)}
    by_arm = {a: np.full((len(qi), len(ki)), np.nan) for a in ARMS}
    for r in records:
        by_arm[str(r["arm"])][qi[str(r["question_id"])], ki[int(r["rotation_seed"])]] = float(r["fractional_R3"])
    g = (by_arm["B32_FRESH"] - by_arm["RANDOM32_FRESH"]) * PP
    gs = (by_arm["SCALED_B32"] - by_arm["SCALED_RANDOM32"]) * PP
    if not (np.all(np.isfinite(g)) and np.all(np.isfinite(gs))):
        raise DesignViolation("non-finite value while assembling the paired matrices")
    return g, gs


# --------------------------------------------------------------------------------------------
# The three reported quantities (R2 section 2)
# --------------------------------------------------------------------------------------------
def aggregate(g: np.ndarray, gs: np.ndarray, idx: np.ndarray | None = None) -> dict:
    """G_bar, G_bar_scaled and Delta_bar in percentage points, over the FIXED seed panel.

    `idx` selects question slots and may contain repeats; the mean divides by len(idx), i.e. by the
    number of selected SLOTS, which is what makes a cluster resample question-weighted.
    """
    if idx is None:
        idx = np.arange(g.shape[0])
    idx = np.asarray(idx, dtype=int)
    if idx.size == 0:
        raise DesignViolation("empty question selection")
    per_seed_g = g[idx].mean(axis=0)          # divide by the number of selected slots
    per_seed_gs = gs[idx].mean(axis=0)
    per_seed_d = per_seed_gs - per_seed_g
    G, G_scaled, D_ = float(per_seed_g.mean()), float(per_seed_gs.mean()), float(per_seed_d.mean())
    # Linearity consistency, as a TOLERANCE check. Bitwise equality is not required and would be
    # wrong to demand: floating-point summation is order-dependent in its last digits.
    if abs(D_ - (G_scaled - G)) > TOL:
        raise DesignViolation(
            f"linearity consistency failed beyond {TOL:g}: mean-of-differences {D_!r} vs "
            f"difference-of-means {G_scaled - G!r}")
    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,
            "per_seed_G_pp": per_seed_g.tolist(), "per_seed_G_scaled_pp": per_seed_gs.tolist(),
            "per_seed_Delta_pp": per_seed_d.tolist(), "n_question_slots": int(idx.size)}


# --------------------------------------------------------------------------------------------
# Uncertainty (R2 section 4; acceptance binding section 4)
# --------------------------------------------------------------------------------------------
def question_bootstrap(g, gs, seed, replicates=BOOTSTRAP_REPLICATES) -> dict:
    """Question-level paired bootstrap.

    ONE resampled index set per replicate is applied to all arms and to the fixed seed panel, so every
    pairing the design establishes survives inside each replicate.

    Limitation, stated in the accepted wording: this scheme does NOT model within-conversation
    dependence and may therefore understate uncertainty. No claim is made about interval width.
    """
    rng = np.random.default_rng(seed)
    n = g.shape[0]
    out = {"G_bar_pp": [], "G_bar_scaled_pp": [], "Delta_bar_pp": []}
    for _ in range(replicates):
        idx = rng.integers(0, n, size=n)          # one selection, shared by every arm and seed
        a = aggregate(g, gs, idx)
        for k in out:
            out[k].append(a[k])
    return _percentiles(out, replicates, scheme="question-level")


def cluster_bootstrap(g, gs, cluster_of_question, seed, replicates=BOOTSTRAP_REPLICATES) -> dict:
    """LoCoMo conversation-cluster bootstrap, exactly as bound in the acceptance record section 4.

    Draw n_clusters conversations WITH REPLACEMENT; take ALL questions of each draw; preserve
    multiplicity, so a conversation drawn twice contributes its questions twice; concatenate into the
    replicate's question multiset; divide by the total number of selected question SLOTS. The same
    selection applies to all arms and to the fixed seed panel.

    Question-weighting is not an automatic property of a cluster bootstrap - it follows only from
    steps 2, 3 and 5 above.
    """
    labels = np.asarray(cluster_of_question)
    if labels.shape[0] != g.shape[0]:
        raise DesignViolation("cluster labels do not cover the questions one to one")
    clusters = list(dict.fromkeys(labels.tolist()))
    members = {c: np.flatnonzero(labels == c) for c in clusters}
    rng = np.random.default_rng(seed)
    out = {"G_bar_pp": [], "G_bar_scaled_pp": [], "Delta_bar_pp": []}
    for _ in range(replicates):
        drawn = rng.integers(0, len(clusters), size=len(clusters))
        idx = np.concatenate([members[clusters[j]] for j in drawn])   # multiplicity preserved
        a = aggregate(g, gs, idx)
        for k in out:
            out[k].append(a[k])
    res = _percentiles(out, replicates, scheme="conversation-cluster")
    res["n_clusters"] = len(clusters)
    res["limit"] = (f"built on {len(clusters)} units; a resampling estimate over that few clusters has "
                    "limited reliability. Its width is an outcome and is not forecast.")
    return res


def _percentiles(samples: dict, replicates: int, scheme: str) -> dict:
    res = {"scheme": scheme, "replicates": replicates, "percentiles": list(PERCENTILES),
           "note": ("a sensitivity analysis, not a certified sampling interval. The point estimate on the "
                    "fixed panel is a computed number whose sign is known; an interval spanning zero means "
                    "both directions are supported under resampling and the interpretation is unresolved. "
                    "It is not evidence of absence of effect and not a claim of practical equivalence.")}
    for k, v in samples.items():
        arr = np.asarray(v, dtype=float)
        lo, hi = (float(x) for x in np.percentile(arr, PERCENTILES))
        res[k] = {"lo": lo, "hi": hi, "spans_zero": bool(lo <= 0.0 <= hi)}
    return res


# --------------------------------------------------------------------------------------------
# Output safety - never overwrite silently
# --------------------------------------------------------------------------------------------
def safe_write_json(path: Path, payload: dict) -> Path:
    path = Path(path)
    if path.exists():
        raise DesignViolation(f"refusing to overwrite an existing result file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
