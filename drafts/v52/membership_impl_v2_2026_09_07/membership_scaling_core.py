"""Membership-under-scaling: pure core, CANDIDATE v2. IMPLEMENTATION PREPARATION ONLY.

Supersedes drafts/v52/membership_impl_2026_09_07/membership_scaling_core.py (blob sha256
707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00), which is left byte-unchanged.

v2 answers the independent implementation review on branch
audit/v52-membership-impl-review-2026-09-07 @ 68819424765ed3da89377c89980d7e42546bfe02. Every change
is tagged with the finding it closes:

  F-1  cv_sigma_after was a standard deviation, not a CV. Now a genuine CV, with the mean-zero case
       explicit and tested; no epsilon is added and the definition is not silently changed. The old
       quantity is still published, under the honest name sd_sigma_after.
  F-2  cluster labels were checked only for length, so a NaN label produced an EMPTY cluster that
       silently removed questions from both numerator and slot denominator. Labels are now validated
       before any grouping, and coverage is proved rather than assumed.
  F-3  duplicate question ids reached an IndexError instead of a named DesignViolation.
  F-6  the real-data gate read a default bound at import, so setting the module constant did not
       open it. It now reads the module global at call time.
  F-7  aggregate accepted negative indices, which wrap, and truncated float indices.
  F-8  an out-of-range index raised IndexError rather than DesignViolation.
  F-9  a boolean score passed validation as float(True) = 1.0.
  F-10 an empty or single-row archive was accepted silently.
  F-12 NOT changed: binding section 6 fixes the linearity tolerance at an absolute 1e-12 and says a
       relative tolerance needs a new decision. The measured worst-case headroom the review reports
       (about 19.5x, worst absolute difference 5.116e-14) is recorded here and nowhere acted on.

Deliberately ABSENT, because the acceptance record lists them as dead and forbidden: any ratio of
Delta to G under any name; the four cut points of the withdrawn categorical scheme; any categorical
verdict label; the floor that protected that ratio's denominator; the RELATIVE SCALE UNSUITABLE
state; the INDETERMINATE overlay; the three-band rule; any band on the remaining gap; the per-seed
positivity gate.

HOW THAT ABSENCE IS EVIDENCED, stated honestly because the review found the previous claim unsound
(F-4): a token scan cannot see a forbidden quantity spelled under another name, and an AST
enumeration of divisions and output keys is a strong check but is not a proof that no ratio can ever
be introduced. The primary guarantee is neither: it is the conformance test, which recomputes the
three reported quantities from an independent reference implementation written from the design text
and requires exact agreement, and which enumerates the output schema against a closed expected set.

Real-data execution is off by default. This module reads no corpus, downloads nothing, and imports
nothing that does.
"""
from __future__ import annotations

import json
import math
import numbers
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------------------------
# Frozen design constants (draft sections 6, 12; R1 sections 1, 2)
# --------------------------------------------------------------------------------------------
ARMS = ("NATIVE", "SCALED_NATIVE", "B32_FRESH", "SCALED_B32", "RANDOM32_FRESH", "SCALED_RANDOM32")
GAP_ARMS = ("B32_FRESH", "RANDOM32_FRESH", "SCALED_B32", "SCALED_RANDOM32")
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
MIN_ARCHIVE_ROWS = 2                            # F-10

# The exact output schema of aggregate(). The conformance test asserts equality against this set, so
# a quantity added under any name - including a ratio - fails a test rather than passing a word scan.
AGGREGATE_KEYS = frozenset({
    "G_bar_pp", "G_bar_scaled_pp", "Delta_bar_pp",
    "per_seed_G_pp", "per_seed_G_scaled_pp", "per_seed_Delta_pp", "n_question_slots"})

# Real-data execution is off by default and stays off until a separate authorization exists.
REAL_DATA_EXECUTION_ENABLED = False

# F-12, recorded and not acted on: under an adversarial worst case (gaps of +/-100 pp, 4,000 slots,
# 400 replicates) the review measured a worst absolute difference of 5.116e-14 between the two sides
# of the linearity identity, about 19.5x of headroom against this absolute tolerance. Changing TOL to
# a relative form would need a new decision under binding section 6 and is not done here.
LINEARITY_HEADROOM_NOTE = "worst measured |mean-of-differences - difference-of-means| = 5.116e-14 against TOL = 1e-12"


class DesignViolation(RuntimeError):
    """Raised when an input or an intermediate result violates the accepted design."""


def require_real_data_authorization(enabled: bool | None = None) -> None:
    """Every corpus-touching path must call this first. It refuses by default.

    F-6: the module global is read at CALL time. Passing `enabled` overrides it explicitly. This gate
    is declarative until a runner calls it, and no runner exists; that is stated rather than implied.
    """
    live = REAL_DATA_EXECUTION_ENABLED if enabled is None else enabled
    if not live:
        raise DesignViolation(
            "real-data execution is OFF by default and is not authorized at this stage; "
            "no corpus may be read, and no fitting, retrieval, ranking or bootstrap may run on real data")


# --------------------------------------------------------------------------------------------
# Step 1 - the scaling operator (R1 section 1)
# --------------------------------------------------------------------------------------------
def _cv(values: np.ndarray) -> float:
    """Coefficient of variation: spread divided by mean. Undefined when the mean is zero.

    F-1. No epsilon is added to the denominator and the definition is not weakened: a zero mean
    yields NaN, which is reported as NaN. The only way the mean of a non-negative sigma vector is
    zero is that every sigma is zero, i.e. a constant archive, and that case is tested.
    """
    mean = float(values.mean())
    if mean == 0.0:
        return float("nan")
    return float(values.std(ddof=0) / mean)


def scale_matrix(C: np.ndarray, eps: float = EPS_SIGMA):
    """D = diag(1/sigma) on the centered archive representation, per archive, archive content only.

    sigma uses ddof = 0 (the population form). The sample form differs by sqrt(n/(n-1)) and would
    define a different intervention, so the choice is explicit rather than inherited from a default.
    eps is a FALLBACK, not a clip: a coordinate below it keeps d = 1, is never divided by eps and is
    never dropped, so the transform stays total and the coordinate stays in the sign code.

    Returns (D, diagnostics). Diagnostics carry the per-archive degenerate count AND the flag the
    design requires, so recording one without the other is impossible. They gate nothing.
    """
    if C.ndim != 2 or C.shape[1] != DIM:
        raise DesignViolation(f"representation must be (n, {DIM}), got {C.shape}")
    if C.shape[0] < MIN_ARCHIVE_ROWS:                                            # F-10
        raise DesignViolation(
            f"an archive needs at least {MIN_ARCHIVE_ROWS} rows for a dispersion to be defined, got {C.shape[0]}")
    if not np.all(np.isfinite(C)):
        raise DesignViolation("non-finite value in the centered representation; aborting, not repairing")
    sigma = C.std(axis=0, ddof=0)
    ok = sigma >= eps
    d = np.where(ok, 1.0 / np.where(ok, sigma, 1.0), 1.0)
    post_sigma = (C @ np.diag(d)).std(axis=0, ddof=0)
    n_degenerate = int((~ok).sum())
    diagnostics = {
        "degenerate_coords": n_degenerate,
        "flagged": bool(n_degenerate > DEGENERATE_FLAG_THRESHOLD),
        "cv_sigma_before": _cv(sigma),
        "cv_sigma_after": _cv(post_sigma),        # F-1: a genuine CV, not a standard deviation
        "sd_sigma_after": float(post_sigma.std(ddof=0)),   # the quantity v1 mislabelled, kept under its true name
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
    qset = [str(q) for q in question_ids]
    if len(set(qset)) != len(qset):                                              # F-3
        dupes = sorted({q for q in qset if qset.count(q) > 1})
        raise DesignViolation(f"duplicate question ids in the cohort: {dupes[:5]}")
    sset, aset = list(seeds), list(arms)
    expected = {(q, int(s), str(a)) for q in qset for s in sset for a in aset}
    seen, duplicates, invalid = set(), [], []
    for r in records:
        try:
            key = (str(r["question_id"]), int(r["rotation_seed"]), str(r["arm"]))
            raw = r["fractional_R3"]
            if isinstance(raw, bool):                                            # F-9
                raise TypeError("a boolean is not a score")
            if not isinstance(raw, numbers.Real):
                raise TypeError(f"score must be a real number, got {type(raw).__name__}")
            v = float(raw)
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
def _check_index(idx: np.ndarray, n_rows: int) -> np.ndarray:
    """F-7, F-8: integer dtype, in range, non-empty. Negative indices wrap in numpy and must not."""
    arr = np.asarray(idx)
    if arr.size == 0:
        raise DesignViolation("empty question selection")
    if not np.issubdtype(arr.dtype, np.integer):
        raise DesignViolation(f"question selection must have an integer dtype, got {arr.dtype}")
    if int(arr.min()) < 0 or int(arr.max()) >= n_rows:
        raise DesignViolation(
            f"question selection out of range: [{int(arr.min())}, {int(arr.max())}] against {n_rows} questions")
    return arr


def aggregate(g: np.ndarray, gs: np.ndarray, idx: np.ndarray | None = None) -> dict:
    """G_bar, G_bar_scaled and Delta_bar in percentage points, over the FIXED seed panel.

    `idx` selects question slots and may contain repeats; the mean divides by len(idx), i.e. by the
    number of selected SLOTS, which is what makes a cluster resample question-weighted.
    """
    if idx is None:
        idx = np.arange(g.shape[0])
    idx = _check_index(idx, g.shape[0])
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
# Cluster construction - F-2: validated before grouping, coverage proved rather than assumed
# --------------------------------------------------------------------------------------------
def build_clusters(cluster_of_question, n_questions: int):
    """Validate cluster labels, then group. Returns (ordered_labels, members, diagnostics).

    F-2. The previous version checked only length, so a NaN label produced a cluster whose member set
    was EMPTY - `labels == nan` is false everywhere - and every replicate that drew it silently
    dropped those questions from the numerator AND from the slot denominator.

    Rules, each enforced with a named error rather than a silent repair:
      * length must equal the number of questions;
      * no label may be missing, None, or a NaN float;
      * labels must be of ONE supported kind - all integer-like, or all strings. Mixing them is
        rejected rather than coerced, because coercion would merge 1 and "1" into one conversation
        or split one conversation into two;
      * every cluster must be non-empty;
      * the member sets must partition the questions exactly: every question in exactly one cluster,
        and the total membership count must equal n_questions.

    The last rule is the one that matters. A question can only be absent from the returned grouping
    if a label was invalid, and that is now impossible because validation precedes grouping. This is
    a DIFFERENT thing from a cluster simply not being drawn during a bootstrap replicate, which is
    normal resampling and is reported separately in the bootstrap diagnostics.
    """
    labels = list(cluster_of_question)
    if len(labels) != n_questions:
        raise DesignViolation(
            f"cluster labels do not cover the questions one to one: {len(labels)} labels, {n_questions} questions")

    kinds = set()
    for i, lab in enumerate(labels):
        if lab is None:
            raise DesignViolation(f"cluster label at position {i} is missing (None)")
        if isinstance(lab, float) and math.isnan(lab):
            raise DesignViolation(f"cluster label at position {i} is NaN")
        if isinstance(lab, (np.floating,)) and math.isnan(float(lab)):
            raise DesignViolation(f"cluster label at position {i} is NaN")
        if isinstance(lab, bool):
            raise DesignViolation(f"cluster label at position {i} is a bool, which is not a supported label type")
        if isinstance(lab, (str, np.str_)):
            kinds.add("str")
        elif isinstance(lab, numbers.Integral) or isinstance(lab, np.integer):
            kinds.add("int")
        else:
            raise DesignViolation(
                f"cluster label at position {i} has unsupported type {type(lab).__name__}; "
                "labels must be all strings or all integers")
    if len(kinds) > 1:
        raise DesignViolation(
            f"cluster labels mix types {sorted(kinds)}; mixed labels would merge or split conversations under "
            "coercion, so they are rejected rather than coerced")

    key = (lambda x: str(x)) if kinds == {"str"} else (lambda x: int(x))
    ordered, members = [], {}
    for i, lab in enumerate(labels):
        k = key(lab)
        if k not in members:
            ordered.append(k)
            members[k] = []
        members[k].append(i)
    members = {k: np.asarray(v, dtype=int) for k, v in members.items()}

    empty = [k for k in ordered if members[k].size == 0]
    if empty:
        raise DesignViolation(f"empty cluster(s) after grouping: {empty[:5]}")
    covered = sum(int(members[k].size) for k in ordered)
    if covered != n_questions:
        raise DesignViolation(
            f"cluster membership does not partition the questions: {covered} assigned of {n_questions}")
    all_idx = np.sort(np.concatenate([members[k] for k in ordered]))
    if not np.array_equal(all_idx, np.arange(n_questions)):
        raise DesignViolation("cluster membership is not a partition: a question is missing or repeated")

    diagnostics = {"n_clusters": len(ordered),
                   "cluster_sizes": {str(k): int(members[k].size) for k in ordered},
                   "questions_covered_at_construction": covered,
                   "questions_lost_to_invalid_labels": 0}
    return ordered, members, diagnostics


# --------------------------------------------------------------------------------------------
# Uncertainty (R2 section 4; acceptance binding section 4)
# --------------------------------------------------------------------------------------------
def question_bootstrap(g, gs, seed, replicates=BOOTSTRAP_REPLICATES) -> dict:
    """Question-level paired bootstrap.

    ONE resampled index set per replicate is applied to all arms and to the fixed seed panel, so every
    pairing the design establishes survives inside each replicate.

    Limitation, in the accepted wording: this scheme does not model within-conversation dependence
    and may therefore understate uncertainty. No claim is made about the interval's width.
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

    F-2: labels are validated and the partition proved BEFORE any grouping, so no question can be
    lost to a bad label. Clusters that a given replicate does not draw are a normal consequence of
    resampling; that is reported as a diagnostic and is a different thing from question loss.
    """
    clusters, members, cdiag = build_clusters(cluster_of_question, g.shape[0])
    rng = np.random.default_rng(seed)
    out = {"G_bar_pp": [], "G_bar_scaled_pp": [], "Delta_bar_pp": []}
    never_drawn_counts = []
    for _ in range(replicates):
        drawn = rng.integers(0, len(clusters), size=len(clusters))
        idx = np.concatenate([members[clusters[j]] for j in drawn])   # multiplicity preserved
        never_drawn_counts.append(len(clusters) - len(set(drawn.tolist())))
        a = aggregate(g, gs, idx)
        for k in out:
            out[k].append(a[k])
    res = _percentiles(out, replicates, scheme="conversation-cluster")
    res.update(cdiag)
    res["mean_clusters_not_drawn_per_replicate"] = float(np.mean(never_drawn_counts))
    res["not_drawn_is_not_loss"] = ("clusters absent from a replicate are ordinary resampling; question loss to an "
                                    "invalid label is impossible because labels are validated before grouping")
    res["limit"] = (f"built on {cdiag['n_clusters']} units; a resampling estimate over that few clusters has "
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
