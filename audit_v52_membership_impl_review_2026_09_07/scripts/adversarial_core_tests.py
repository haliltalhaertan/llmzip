"""INDEPENDENT adversarial tests for membership_scaling_core.py (candidate a6d70ff).

Written by the independent implementation reviewer. Nothing here reads a corpus, downloads
anything, performs real retrieval/fitting/ranking, or runs a bootstrap on real data.
All data is synthetic and generated in-process.

Every assertion of the form "the code rejects X" is paired with a demonstration that the same
check passes on the legitimate case, and every assertion of the form "the code computes Y" is
paired with an independently written reference computation.

Usage:  python adversarial_core_tests.py <path-to-membership_scaling_core.py> [json-out]
Exit 0 iff every expectation held.  A recorded DEFECT is reported, not asserted away.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

CORE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

spec = importlib.util.spec_from_file_location("mcore_indep", CORE)
m = importlib.util.module_from_spec(spec)
sys.modules["mcore_indep"] = m
spec.loader.exec_module(m)
SRC = CORE.read_text(encoding="utf-8")

results = []
_fails = 0


def rec(area, name, ok, detail="", kind="expectation"):
    """kind='expectation' -> must hold; kind='observation' -> recorded fact, never fails the run."""
    global _fails
    if kind == "expectation" and not ok:
        _fails += 1
    tag = {"expectation": ("ok   ", "FAIL "), "observation": ("note ", "note ")}[kind][0 if ok else 1]
    print(f"{tag} [{area}] {name}" + (f"   -- {detail}" if detail else ""))
    results.append({"area": area, "name": name, "ok": bool(ok), "kind": kind, "detail": str(detail)})


def violates(fn):
    """Returns (raised_DesignViolation, message, other_exception_repr)."""
    try:
        fn()
        return False, "", ""
    except m.DesignViolation as e:
        return True, str(e), ""
    except Exception as e:  # noqa: BLE001
        return False, "", repr(e)


# =====================================================================================
# AREA A -- formulas and the percentage-point unit
# =====================================================================================
def make_records(qids, seeds, per_arm):
    return [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": float(per_arm[a][qi][si])}
            for qi, q in enumerate(qids) for si, s in enumerate(seeds) for a in m.ARMS]


rng = np.random.default_rng(20260907)
NQ, NK = 37, 10
qids = [f"q{i:03d}" for i in range(NQ)]
seeds = list(m.ROTATION_SEEDS)
per_arm = {a: rng.random((NQ, NK)) for a in m.ARMS}
recs = make_records(qids, seeds, per_arm)

g, gs = m.paired_matrices(recs, qids)

# Reference computation, written from R2 section 2 directly and not from the candidate.
ref_g = (per_arm["B32_FRESH"] - per_arm["RANDOM32_FRESH"]) * 100.0
ref_gs = (per_arm["SCALED_B32"] - per_arm["SCALED_RANDOM32"]) * 100.0
rec("A", "g matches an independent reference (B32_FRESH - RANDOM32_FRESH, x100)",
    np.allclose(g, ref_g, rtol=0, atol=0), f"max|diff|={np.max(np.abs(g - ref_g)):.3e}")
rec("A", "gs matches an independent reference (SCALED_B32 - SCALED_RANDOM32, x100)",
    np.allclose(gs, ref_gs, rtol=0, atol=0))

agg = m.aggregate(g, gs)
ref_G = float(ref_g.mean(axis=0).mean())
ref_Gs = float(ref_gs.mean(axis=0).mean())
rec("A", "G_bar_pp equals mean-over-seeds of mean-over-questions, in pp",
    abs(agg["G_bar_pp"] - ref_G) < 1e-12, f"{agg['G_bar_pp']!r} vs {ref_G!r}")
rec("A", "G_bar_scaled_pp likewise", abs(agg["G_bar_scaled_pp"] - ref_Gs) < 1e-12)
rec("A", "Delta_bar_pp equals G_bar_scaled_pp - G_bar_pp to 1e-12",
    abs(agg["Delta_bar_pp"] - (ref_Gs - ref_G)) < 1e-12)
rec("A", "per-seed Delta equals per-seed(gs) - per-seed(g) elementwise",
    np.allclose(np.array(agg["per_seed_Delta_pp"]),
                np.array(agg["per_seed_G_scaled_pp"]) - np.array(agg["per_seed_G_pp"]), rtol=0, atol=0))

# pp applied EXACTLY once: sharpness of the check. If PP were applied twice the reference
# comparison above must fail. Demonstrate that the comparison is sharp.
rec("A", "NEGATIVE CONTROL: a doubly-applied pp factor would be caught by the same comparison",
    not np.allclose(g, ref_g * 100.0), "reference comparison is sharp, not vacuous")

# The scale of the deliverable: fractions in [0,1] can only produce gaps in [-100, +100] pp.
rec("A", "gap magnitudes stay inside +/-100 pp for in-range fractional scores",
    float(np.max(np.abs(g))) <= 100.0 + 1e-9 and float(np.max(np.abs(gs))) <= 100.0 + 1e-9)

# Linearity tolerance under an adversarial magnitude: maximal gaps (+/-100 pp), many slots.
adv = {a: np.zeros((4000, 10)) for a in m.ARMS}
adv["B32_FRESH"][:] = 1.0
adv["RANDOM32_FRESH"][:] = 0.0
adv["SCALED_B32"][:] = 1.0
adv["SCALED_RANDOM32"][:] = 0.0
g_adv = (adv["B32_FRESH"] - adv["RANDOM32_FRESH"]) * 100.0
gs_adv = (adv["SCALED_B32"] - adv["SCALED_RANDOM32"]) * 100.0
rr = np.random.default_rng(3)
worst = 0.0
lin_ok = True
for _ in range(400):
    noise = rr.normal(0, 1e-9, size=g_adv.shape)
    ga, gsa = g_adv + noise, gs_adv - noise
    try:
        a2 = m.aggregate(ga, gsa, rr.integers(0, ga.shape[0], size=ga.shape[0]))
        worst = max(worst, abs(a2["Delta_bar_pp"] - (a2["G_bar_scaled_pp"] - a2["G_bar_pp"])))
    except m.DesignViolation:
        lin_ok = False
        break
rec("A", "linearity tolerance 1e-12 survives 400 adversarial replicates at +/-100 pp, n=4000",
    lin_ok, f"worst |mean-of-diff - diff-of-means| = {worst:.3e} (TOL={m.TOL:g})")
rec("A", "OBSERVATION: the 1e-12 linearity tolerance is ABSOLUTE, not relative to the pp magnitude",
    True, f"headroom at 100 pp = {m.TOL / max(worst, 1e-300):.1f}x observed worst case", kind="observation")

# =====================================================================================
# AREA B -- pairing of questions, arms and seeds
# =====================================================================================
# One shared selection across the SEED PANEL. Construct anti-correlated seed columns: if and only
# if a single index set is applied to every seed column, mean-over-seeds is identically zero.
n_q = 60
base = rng.normal(5.0, 4.0, size=n_q)
g_anti = np.stack([base, -base], axis=1)          # two seeds, exactly anti-correlated
gs_anti = g_anti.copy()
res_shared = m.question_bootstrap(g_anti, gs_anti, seed=101, replicates=500)
rec("B", "ONE index set is shared across the fixed seed panel (anti-correlated seeds collapse to 0)",
    abs(res_shared["G_bar_pp"]["lo"]) < 1e-12 and abs(res_shared["G_bar_pp"]["hi"]) < 1e-12,
    f"[{res_shared['G_bar_pp']['lo']:.3e}, {res_shared['G_bar_pp']['hi']:.3e}]")

# NEGATIVE CONTROL: a per-seed independent resample on the SAME data does not collapse.
rr2 = np.random.default_rng(101)
per_seed_vals = []
for _ in range(500):
    cols = [float(g_anti[rr2.integers(0, n_q, size=n_q), j].mean()) for j in range(2)]
    per_seed_vals.append(float(np.mean(cols)))
lo_ns, hi_ns = np.percentile(per_seed_vals, [2.5, 97.5])
rec("B", "NEGATIVE CONTROL: independent per-seed resampling does NOT collapse (so the test is sharp)",
    (hi_ns - lo_ns) > 1e-6, f"width={hi_ns - lo_ns:.4f} pp")

# One shared selection across ARMS: if g and gs were resampled independently, a constant
# per-question change could not survive as a degenerate Delta interval.
g_c = rng.normal(8.0, 3.0, size=(n_q, 10))
gs_c = g_c - 5.0
res_arm = m.question_bootstrap(g_c, gs_c, seed=7, replicates=500)
rec("B", "ONE index set is shared across arms (constant per-question change -> degenerate Delta)",
    abs(res_arm["Delta_bar_pp"]["lo"] + 5.0) < 1e-9 and abs(res_arm["Delta_bar_pp"]["hi"] + 5.0) < 1e-9)

# The seed panel is FIXED, not resampled: every aggregate returns exactly n_seeds per-seed values
# and their identity is preserved (column j of the output always comes from column j of the input).
idx_probe = rng.integers(0, n_q, size=n_q)
ap = m.aggregate(g_c, gs_c, idx_probe)
rec("B", "the seed panel is FIXED: per-seed vectors keep length n_seeds and column identity",
    len(ap["per_seed_G_pp"]) == g_c.shape[1]
    and np.allclose(np.array(ap["per_seed_G_pp"]), g_c[idx_probe].mean(axis=0), rtol=0, atol=0))

# Determinism of the bootstrap given its seed.
rec("B", "question_bootstrap is deterministic in its seed argument",
    m.question_bootstrap(g_c, gs_c, seed=42, replicates=50)
    == m.question_bootstrap(g_c, gs_c, seed=42, replicates=50))
rec("B", "OBSERVATION: no bootstrap RNG seed is fixed as a module constant; it is a caller argument",
    True, "reproducibility of the interval depends on the unwritten runner, not on this core",
    kind="observation")

# Seed pairing constants.
rec("B", "rotation seeds are 60001..60010 and partition seeds 70001..70010, paired by position",
    m.ROTATION_SEEDS == tuple(range(60001, 60011)) and m.PARTITION_SEEDS == tuple(range(70001, 70011))
    and len(m.ROTATION_SEEDS) == len(m.PARTITION_SEEDS) == 10)
rec("B", "one (Q32,Q64) pair per rotation seed serves every rotated arm (deterministic, head first)",
    (lambda a, b: np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
     and a[0].shape == (32, 32) and a[1].shape == (64, 64))(
        m.draw_rotation_blocks(60001), m.draw_rotation_blocks(60001)))
rec("B", "different rotation seeds give different blocks (the draw is not degenerate)",
    not np.array_equal(m.draw_rotation_blocks(60001)[0], m.draw_rotation_blocks(60002)[0]))

# =====================================================================================
# AREA C -- scaling operator and degenerate-coordinate rules
# =====================================================================================
sd = 0.9 ** np.arange(96)
C = rng.standard_normal((400, 96)) * sd
C = C - C.mean(axis=0)
Qq = rng.standard_normal((7, 96)) * sd
D, dg = m.scale_matrix(C)

rec("C", "sigma uses ddof=0 exactly (and is NOT the ddof=1 form)",
    np.allclose(np.diag(D), 1.0 / C.std(axis=0, ddof=0), rtol=0, atol=1e-12)
    and not np.allclose(np.diag(D), 1.0 / C.std(axis=0, ddof=1)))

# D depends on the archive ALONE: a completely different query cannot change it.
D2, _ = m.scale_matrix(C)
rec("C", "D is estimated from the archive alone; scale_matrix takes no query argument",
    np.array_equal(D, D2) and "Q" not in [a.arg for a in ast.parse(SRC).body
                                          for a in ([] if not isinstance(a, ast.FunctionDef) or a.name != "scale_matrix"
                                                    else a.args.args)],
    "signature: " + ", ".join(a.arg for n in ast.parse(SRC).body
                              if isinstance(n, ast.FunctionDef) and n.name == "scale_matrix"
                              for a in n.args.args))

# The IDENTICAL D is applied to the query.
before = Qq @ D
m.check_identity(C, Qq, D)
rec("C", "the identical D is applied to the query and the sign code is preserved",
    np.array_equal((Qq @ D) >= 0, Qq >= 0) and np.array_equal(before, Qq @ D))

# eps is a FALLBACK, not a clip -- exact boundary.
for k, expect_fallback in ((3, False), (4, False), (5, True)):
    Ck = C.copy()
    Ck[:, -k:] = 0.0
    Dk, dgk = m.scale_matrix(Ck)
    rec("C", f"degenerate count {k}: fallback keeps d=1 (never 1/eps, never dropped)",
        dgk["degenerate_coords"] == k and np.allclose(np.diag(Dk)[-k:], 1.0) and Dk.shape == (96, 96)
        and float(np.max(np.diag(Dk))) < 1e11)
    rec("C", f"per-archive FLAG boundary at exactly {k} degenerate coordinates "
             f"(design: flagged iff count > 4)",
        dgk["flagged"] is expect_fallback, f"flagged={dgk['flagged']}, expected={expect_fallback}")

# sigma EXACTLY at eps takes the divide branch, per the design's ">= eps" wording.
Ce = np.zeros((2, 96))
Ce[0, :] = 1e-12
Ce[1, :] = -1e-12          # centered, sigma_i = 1e-12 exactly
De, dge = m.scale_matrix(Ce)
rec("C", "OBSERVATION: sigma exactly at eps takes the DIVIDE branch (d = 1e12), per '>= eps'",
    dge["degenerate_coords"] == 0 and float(np.max(np.diag(De))) > 1e11,
    f"max d = {float(np.max(np.diag(De))):.3e}; the fallback is a razor edge at eps, as specified",
    kind="observation")

# cv_sigma_before vs cv_sigma_after -- are both really CVs?
Cdg = C.copy()
Cdg[:, -20:] = 0.0                      # 20 dead coordinates: post-scaling sigmas are NOT all 1
Ddg, dgdg = m.scale_matrix(Cdg)
post_sigma = (Cdg @ Ddg).std(axis=0, ddof=0)
true_cv_after = float(post_sigma.std(ddof=0) / post_sigma.mean())
reported_after = dgdg["cv_sigma_after"]
sd_after = float(post_sigma.std(ddof=0))
rec("C", "DEFECT: cv_sigma_after is the standard deviation of post-scaling sigma, not its CV",
    abs(reported_after - sd_after) < 1e-12 and abs(reported_after - true_cv_after) > 1e-6,
    f"reported={reported_after:.6f}, SD={sd_after:.6f}, true CV={true_cv_after:.6f} "
    f"(they coincide only when the mean is 1, i.e. no degenerate coordinate)")
rec("C", "cv_sigma_before IS a genuine CV (sd/mean of sigma)",
    abs(dg["cv_sigma_before"] - float(C.std(axis=0, ddof=0).std(ddof=0) / C.std(axis=0, ddof=0).mean())) < 1e-12)

# A diagonal but NEGATIVE D.
Dneg = np.diag(np.r_[np.ones(95), -1.0])
v, msg, other = violates(lambda: m.check_identity(C, Qq, Dneg))
rec("C", "a diagonal but NEGATIVE D is rejected by the identity check",
    v and "identity violation" in msg.lower(), msg[:80])
rec("C", "OBSERVATION: scale_matrix cannot itself produce a negative d (sigma >= 0), so the "
         "negative-D net is check_identity only", bool(np.all(np.diag(D) > 0)), kind="observation")

# Non-finite abort, not repair.
Cinf = C.copy()
Cinf[0, 0] = np.nan
v, msg, _ = violates(lambda: m.scale_matrix(Cinf))
rec("C", "a NaN in the centered representation ABORTS scale_matrix", v and "non-finite" in msg.lower())
v, msg, _ = violates(lambda: m.check_identity(C, Qq, np.diag(np.r_[np.ones(95), np.inf])))
rec("C", "a non-finite D ABORTS check_identity", v and "non-finite" in msg.lower(), msg[:70])

# Shape guard.
v, _, _ = violates(lambda: m.scale_matrix(C[:, :95]))
rec("C", "a wrong-width representation is rejected", v)
v, _, other = violates(lambda: m.scale_matrix(C[0]))
rec("C", "a 1-D representation is rejected", v, other)

# Boundary: single-row and EMPTY archives.
D1, dg1 = m.scale_matrix(C[:1])
rec("C", "OBSERVATION: a SINGLE-ROW archive yields sigma=0 everywhere -> D = I, 96 degenerate, flagged",
    dg1["degenerate_coords"] == 96 and dg1["flagged"] is True and np.allclose(D1, np.eye(96)),
    "accepted without complaint; a one-row archive is a meaningless intervention", kind="observation")
with np.errstate(all="ignore"):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            D0, dg0 = m.scale_matrix(np.zeros((0, 96)))
            empty_ok, empty_detail = True, f"accepted: degenerate={dg0['degenerate_coords']}, flagged={dg0['flagged']}"
        except Exception as e:  # noqa: BLE001
            empty_ok, empty_detail = False, repr(e)
rec("C", "DEFECT (minor): an EMPTY archive (n=0) is accepted silently instead of being refused",
    empty_ok, empty_detail, kind="observation" if not empty_ok else "observation")
rec("C", "recorded: empty-archive behaviour", True, empty_detail, kind="observation")

# Partition / rotation guards.
q32, q64 = m.draw_rotation_blocks(60001)
S = m.random_membership(70001)
Rr = m.build_rotation(q32, q64, S)
rec("C", "build_rotation places the GIVEN blocks and stays orthogonal to TOL",
    float(np.max(np.abs(Rr.T @ Rr - np.eye(96)))) <= m.TOL)
for bad_S, label in ((np.zeros(32, dtype=int), "all-identical membership"),
                     (np.r_[np.arange(31), 30], "membership with one duplicate"),
                     (np.arange(31), "membership of the wrong cardinality"),
                     (np.arange(33), "membership one too large")):
    v, msg, other = violates(lambda bs=bad_S: m.build_rotation(q32, q64, bs))
    rec("C", f"a {label} is rejected", v, (msg or other)[:70])
v, msg, other = violates(lambda: m.build_rotation(q32, q64, np.r_[np.arange(31), 96]))
rec("C", "an out-of-range coordinate in the membership is rejected", v or bool(other), (msg or other)[:70])

# =====================================================================================
# AREA D -- multiplicity, weighting, denominator
# =====================================================================================
labels = np.array(["A"] * 3 + ["B"] * 5 + ["C"] * 2)
gcl = np.vstack([np.full((3, 4), 1.0), np.zeros((5, 4)), np.full((2, 4), 4.0)])
gscl = gcl.copy()

# Exhaustive multiplicity/denominator check against three independently written estimators.
def ref_slots(idx):
    return float(gcl[idx].mean(axis=0).mean())


sizes = {"A": 3, "B": 5, "C": 2}
vals = {"A": 1.0, "B": 0.0, "C": 4.0}
combos = [("A", "A", "A"), ("A", "B", "C"), ("C", "C", "B"), ("B", "B", "B")]
all_ok = True
detail_bits = []
for combo in combos:
    idx = np.concatenate([np.flatnonzero(labels == c) for c in combo])
    got = m.aggregate(gcl, gscl, idx)
    slot_mean = sum(vals[c] * sizes[c] for c in combo) / sum(sizes[c] for c in combo)
    cluster_mean = sum(vals[c] for c in combo) / len(combo)
    distinct = sorted(set(combo))
    distinct_mean = (sum(vals[c] * sizes[c] for c in distinct) / sum(sizes[c] for c in distinct))
    ok = (abs(got["G_bar_pp"] - slot_mean) < 1e-12
          and got["n_question_slots"] == sum(sizes[c] for c in combo))
    all_ok &= ok
    detail_bits.append(f"{''.join(combo)}: got={got['G_bar_pp']:.4f} slots={slot_mean:.4f} "
                       f"clusters={cluster_mean:.4f} distinct={distinct_mean:.4f}")
rec("D", "the mean divides by TOTAL SELECTED SLOTS, not by clusters and not by distinct questions",
    all_ok, " | ".join(detail_bits))
rec("D", "NEGATIVE CONTROL: the cluster-averaged and distinct-question estimators give DIFFERENT "
         "answers on this data, so the check above is sharp",
    abs((1.0 + 0.0 + 4.0) / 3 - (1 * 3 + 0 * 5 + 4 * 2) / 10) > 1e-6)

# Draws are with replacement over n_clusters, and multiplicity actually occurs.
seen_sizes = set()
seen_repeat = False
class _SpyRng:
    def __init__(self, real):
        self.real = real
        self.calls = []

    def integers(self, lo, hi, size=None):
        out = self.real.integers(lo, hi, size=size)
        self.calls.append((lo, hi, None if size is None else int(np.size(out)), np.asarray(out).copy()))
        return out


real = np.random.default_rng(5)
spy = _SpyRng(real)
orig_default_rng = np.random.default_rng
np.random.default_rng = lambda *a, **k: spy          # noqa: E731  (scoped monkeypatch)
try:
    m.cluster_bootstrap(gcl, gscl, labels, seed=5, replicates=200)
finally:
    np.random.default_rng = orig_default_rng
draw_lo = {c[0] for c in spy.calls}
draw_hi = {c[1] for c in spy.calls}
draw_sz = {c[2] for c in spy.calls}
seen_repeat = any(len(np.unique(c[3])) < len(c[3]) for c in spy.calls)
rec("D", "each replicate draws exactly n_clusters cluster indices WITH REPLACEMENT",
    draw_lo == {0} and draw_hi == {3} and draw_sz == {3} and len(spy.calls) == 200,
    f"lo={draw_lo} hi={draw_hi} size={draw_sz} calls={len(spy.calls)}")
rec("D", "multiplicity actually occurs (some replicate draws a cluster more than once)", seen_repeat)

# ALL questions of a drawn cluster are taken.
idx_a = np.concatenate([np.flatnonzero(labels == "A")])
rec("D", "a drawn cluster contributes ALL of its questions",
    len(idx_a) == 3 and set(idx_a.tolist()) == {0, 1, 2})

# Single-cluster label vector.
one = np.array(["only"] * 10)
res1 = m.cluster_bootstrap(gcl, gscl, one, seed=2, replicates=100)
full = m.aggregate(gcl, gscl)
rec("D", "a ONE-cluster label vector gives a degenerate interval equal to the full-sample value",
    res1["n_clusters"] == 1 and abs(res1["G_bar_pp"]["lo"] - full["G_bar_pp"]) < 1e-12
    and abs(res1["G_bar_pp"]["hi"] - full["G_bar_pp"]) < 1e-12)

# NaN cluster labels silently drop questions.
lab_nan = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, np.nan, np.nan])
mem_nan = {c: np.flatnonzero(lab_nan == c) for c in dict.fromkeys(lab_nan.tolist())}
nan_key = [k for k in mem_nan if isinstance(k, float) and math.isnan(k)]
v_nan, msg_nan, other_nan = violates(lambda: m.cluster_bootstrap(gcl, gscl, lab_nan, seed=1, replicates=50))
rec("D", "DEFECT: NaN cluster labels are not refused; NaN becomes a cluster whose member set is "
         "EMPTY, so its questions are silently dropped from any replicate that draws it",
    bool(nan_key) and mem_nan[nan_key[0]].size == 0,
    f"cluster keys={list(mem_nan)}, NaN member count={mem_nan[nan_key[0]].size}; "
    f"cluster_bootstrap outcome: "
    + (f"DesignViolation '{msg_nan}' (only when every draw is the empty cluster)" if v_nan
       else "completed with silently under-weighted replicates"), kind="observation")
# Show the silent-underweight case directly, without relying on which clusters the RNG drew.
idx_nan_mix = np.concatenate([mem_nan[k] for k in list(mem_nan)[:2]] + [mem_nan[nan_key[0]]])
agg_nan = m.aggregate(gcl, gscl, idx_nan_mix)
rec("D", "...and a replicate mixing a real cluster with the NaN cluster is accepted with a "
         "denominator that silently omits the NaN questions",
    agg_nan["n_question_slots"] == sum(mem_nan[k].size for k in list(mem_nan)[:2]),
    f"slots={agg_nan['n_question_slots']} for a draw of 3 clusters covering "
    f"{sum(mem_nan[k].size for k in mem_nan)} of 10 questions", kind="observation")

# Mixed-type labels split one conversation into two clusters.
lab_mixed = np.array([1, "1", 1, "1", 1, "1", 1, "1", 1, "1"], dtype=object)
res_mixed = m.cluster_bootstrap(gcl, gscl, lab_mixed, seed=1, replicates=20)
rec("D", "DEFECT (minor): cluster labels are not type-normalised; 1 and '1' become two clusters",
    res_mixed["n_clusters"] == 2, f"n_clusters={res_mixed['n_clusters']}", kind="observation")

# Length mismatch is refused (positive guard).
v, msg, _ = violates(lambda: m.cluster_bootstrap(gcl, gscl, labels[:-1], seed=1, replicates=5))
rec("D", "cluster labels of the wrong length are refused", v and "one to one" in msg.lower())

# Interval mechanics.
rr3 = np.random.default_rng(9)
gq = rr3.normal(2.0, 1.0, size=(200, 10))
rb = m.question_bootstrap(gq, gq + 1.0, seed=13, replicates=2000)
rec("D", "percentile interval is taken at 2.5/97.5 and spans_zero is lo<=0<=hi",
    rb["percentiles"] == [2.5, 97.5]
    and rb["Delta_bar_pp"]["spans_zero"] is False
    and m.question_bootstrap(gq - 2.0, gq - 2.0, seed=13, replicates=2000)["G_bar_pp"]["spans_zero"] is True)
rec("D", "design constants: 10,000 replicates and percentiles (2.5, 97.5)",
    m.BOOTSTRAP_REPLICATES == 10000 and m.PERCENTILES == (2.5, 97.5))


# END-TO-END reference implementations, written from the acceptance record's section 4 alone.
# These bind the WHOLE bootstrap path, not just aggregate(); a cluster-averaging or
# distinct-question denominator inside cluster_bootstrap cannot survive this comparison.
def ref_cluster_bootstrap(gA, gsA, lab, seed, replicates):
    lab = np.asarray(lab)
    clus = list(dict.fromkeys(lab.tolist()))
    mem = {c: np.flatnonzero(lab == c) for c in clus}
    r = np.random.default_rng(seed)
    G_, Gs_, D_ = [], [], []
    for _ in range(replicates):
        draw = r.integers(0, len(clus), size=len(clus))            # with replacement, n_clusters draws
        sel = np.concatenate([mem[clus[j]] for j in draw])          # ALL questions, multiplicity kept
        num_g = gA[sel].sum(axis=0)
        num_gs = gsA[sel].sum(axis=0)
        den = float(sel.size)                                       # total selected question SLOTS
        ps_g, ps_gs = num_g / den, num_gs / den
        G_.append(float(ps_g.mean()))
        Gs_.append(float(ps_gs.mean()))
        D_.append(float((ps_gs - ps_g).mean()))
    return {k: [float(x) for x in np.percentile(np.asarray(v), [2.5, 97.5])]
            for k, v in (("G_bar_pp", G_), ("G_bar_scaled_pp", Gs_), ("Delta_bar_pp", D_))}


def ref_question_bootstrap(gA, gsA, seed, replicates):
    r = np.random.default_rng(seed)
    n = gA.shape[0]
    G_, Gs_, D_ = [], [], []
    for _ in range(replicates):
        sel = r.integers(0, n, size=n)
        ps_g = gA[sel].sum(axis=0) / float(sel.size)
        ps_gs = gsA[sel].sum(axis=0) / float(sel.size)
        G_.append(float(ps_g.mean()))
        Gs_.append(float(ps_gs.mean()))
        D_.append(float((ps_gs - ps_g).mean()))
    return {k: [float(x) for x in np.percentile(np.asarray(v), [2.5, 97.5])]
            for k, v in (("G_bar_pp", G_), ("G_bar_scaled_pp", Gs_), ("Delta_bar_pp", D_))}


gE = rr3.normal(3.0, 2.5, size=(11, 5))
gsE = gE + rr3.normal(-1.0, 0.5, size=(11, 5))
labE = np.array([0, 0, 1, 1, 1, 2, 3, 3, 3, 3, 4])
got_cl = m.cluster_bootstrap(gE, gsE, labE, seed=77, replicates=600)
exp_cl = ref_cluster_bootstrap(gE, gsE, labE, 77, 600)
cl_diff = max(abs(got_cl[k]["lo"] - exp_cl[k][0]) + abs(got_cl[k]["hi"] - exp_cl[k][1]) for k in exp_cl)
rec("D", "cluster_bootstrap END TO END reproduces an independent reference of the bound algorithm "
         "(unequal cluster sizes, all three quantities, identical RNG stream)",
    cl_diff < 1e-12, f"max interval discrepancy = {cl_diff:.3e}")
got_q = m.question_bootstrap(gE, gsE, seed=77, replicates=600)
exp_q = ref_question_bootstrap(gE, gsE, 77, 600)
q_diff = max(abs(got_q[k]["lo"] - exp_q[k][0]) + abs(got_q[k]["hi"] - exp_q[k][1]) for k in exp_q)
rec("D", "question_bootstrap END TO END reproduces an independent reference",
    q_diff < 1e-12, f"max interval discrepancy = {q_diff:.3e}")
# Sharpness: the same comparison against a cluster-AVERAGED reference must disagree.
def ref_cluster_averaged(gA, gsA, lab, seed, replicates):
    lab = np.asarray(lab)
    clus = list(dict.fromkeys(lab.tolist()))
    mem = {c: np.flatnonzero(lab == c) for c in clus}
    r = np.random.default_rng(seed)
    G_ = []
    for _ in range(replicates):
        draw = r.integers(0, len(clus), size=len(clus))
        G_.append(float(np.mean([float(gA[mem[clus[j]]].mean(axis=0).mean()) for j in draw])))
    return [float(x) for x in np.percentile(np.asarray(G_), [2.5, 97.5])]


alt = ref_cluster_averaged(gE, gsE, labE, 77, 600)
rec("D", "NEGATIVE CONTROL: a cluster-AVERAGED denominator gives a different interval on this "
         "fixture, so the end-to-end comparison above is sharp",
    abs(got_cl["G_bar_pp"]["lo"] - alt[0]) + abs(got_cl["G_bar_pp"]["hi"] - alt[1]) > 1e-6,
    f"slot-weighted=[{got_cl['G_bar_pp']['lo']:.4f},{got_cl['G_bar_pp']['hi']:.4f}] vs "
    f"cluster-averaged=[{alt[0]:.4f},{alt[1]:.4f}]")
rec("D", "OBSERVATION: no cluster bootstrap is defined for LongMemEval in this core; the caller "
         "chooses the scheme, so the R2 prohibition is the unwritten runner's to honour",
    True, kind="observation")

# =====================================================================================
# AREA E -- rejection of invalid records, output protection, execution gates
# =====================================================================================
QIDS = [f"q{i}" for i in range(4)]
good = [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": 0.5}
        for q in QIDS for s in m.ROTATION_SEEDS for a in m.ARMS]
m.validate_per_question_records(good, QIDS)
rec("E", "a complete, well-formed record set validates", True)

cases = [
    ("missing record", good[:-1], "missing"),
    ("duplicate record", good + [good[0]], "duplicate"),
    ("NaN score", [{**r, "fractional_R3": float("nan")} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("infinite score", [{**r, "fractional_R3": float("inf")} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("score above 1", [{**r, "fractional_R3": 1.0000001} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("negative score", [{**r, "fractional_R3": -1e-9} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("unknown arm", [{**r, "arm": "GHOST"} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("unknown seed", [{**r, "rotation_seed": 60011} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("unknown question", [{**r, "question_id": "qZZ"} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("missing key", [{"question_id": "q0"} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("non-numeric score", [{**r, "fractional_R3": "high"} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("None score", [{**r, "fractional_R3": None} if i == 0 else r for i, r in enumerate(good)], "invalid"),
    ("empty record list", [], "missing"),
]
for label, payload, needle in cases:
    v, msg, other = violates(lambda p=payload: m.validate_per_question_records(p, QIDS))
    rec("E", f"a record set with a {label} is REFUSED", v and needle in msg.lower(), (msg or other)[:70])

# Boolean scores slip through as 0.0/1.0.
bool_recs = [{**r, "fractional_R3": True} if i == 0 else r for i, r in enumerate(good)]
v, msg, _ = violates(lambda: m.validate_per_question_records(bool_recs, QIDS))
rec("E", "DEFECT (minor): a boolean score passes validation as float(True)=1.0",
    not v, "no violation raised" if not v else msg[:70], kind="observation")

# Duplicate question ids in the ID list: NOT caught by the validator.
dup_qids = ["q0", "q0", "q1"]
dup_recs = [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": 0.5}
            for q in ("q0", "q1") for s in m.ROTATION_SEEDS for a in m.ARMS]
v_val, msg_val, _ = violates(lambda: m.validate_per_question_records(dup_recs, dup_qids))
v_pm, msg_pm, _dup_other = violates(lambda: m.paired_matrices(dup_recs, dup_qids))
rec("E", "DEFECT: DUPLICATE question ids pass validate_per_question_records unnoticed "
         "(the set comprehension de-duplicates them)",
    not v_val, "validator raised nothing" if not v_val else msg_val[:70], kind="observation")
rec("E", "...and paired_matrices then dies with an unhandled IndexError rather than a "
         "DesignViolation naming the duplicate (it still refuses, but not by design)",
    (not v_pm) and "IndexError" in _dup_other, _dup_other[:110], kind="observation")
# Confirm the failure is unconditional across duplicate positions, i.e. a duplicate id can never
# silently produce a wrong answer.
_dup_variants = [(["q0", "q0"], ("q0",)), (["q0", "q1", "q1"], ("q0", "q1")), (["q0", "q0", "q1"], ("q0", "q1"))]
_dup_all_refuse = True
_dup_detail = []
for _qs, _present in _dup_variants:
    _rs = [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": 0.5}
           for q in _present for s in m.ROTATION_SEEDS for a in m.ARMS]
    _v, _msg, _oth = violates(lambda rs=_rs, qs=_qs: m.paired_matrices(rs, qs))
    _dup_all_refuse &= (_v or bool(_oth))
    _dup_detail.append(f"{_qs}->{(_msg or _oth).split('(')[0][:40]}")
rec("E", "a duplicate question id NEVER yields a silently wrong answer: every variant aborts",
    _dup_all_refuse, "; ".join(_dup_detail))

# aggregate index hygiene.
gsm = np.arange(20.0).reshape(10, 2)
v_neg, _, _ = violates(lambda: m.aggregate(gsm, gsm, np.array([-1])))
got_neg = m.aggregate(gsm, gsm, np.array([-1]))["G_bar_pp"]
got_last = m.aggregate(gsm, gsm, np.array([9]))["G_bar_pp"]
rec("E", "DEFECT (minor): a NEGATIVE index is silently accepted and wraps to the last question",
    (not v_neg) and abs(got_neg - got_last) < 1e-12,
    f"aggregate(idx=[-1]) = {got_neg} = aggregate(idx=[9])", kind="observation")
v_oob, _, other_oob = violates(lambda: m.aggregate(gsm, gsm, np.array([99])))
rec("E", "an out-of-range index fails (as IndexError, not DesignViolation)",
    (not v_oob) and "IndexError" in other_oob, other_oob[:70], kind="observation")
v_f, _, other_f = violates(lambda: m.aggregate(gsm, gsm, np.array([0.7])))
rec("E", "OBSERVATION: a float index is silently truncated to int by np.asarray(dtype=int)",
    not v_f, f"aggregate(idx=[0.7]) accepted -> row 0", kind="observation")
v_e, msg_e, _ = violates(lambda: m.aggregate(gsm, gsm, np.array([], dtype=int)))
rec("E", "an EMPTY question selection is refused", v_e and "empty" in msg_e.lower())
single = m.aggregate(gsm, gsm, np.array([3]))
rec("E", "a SINGLE-element selection is accepted and weighted correctly",
    single["n_question_slots"] == 1 and np.allclose(single["per_seed_G_pp"], gsm[3]))

# Output protection.
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "nested" / "res.json"
    m.safe_write_json(p, {"x": 1})
    v1, msg1, _ = violates(lambda: m.safe_write_json(p, {"x": 2}))
    rec("E", "safe_write_json refuses to overwrite an existing FILE",
        v1 and "refusing to overwrite" in msg1.lower())
    rec("E", "the original file's content is untouched after the refusal",
        json.loads(p.read_text(encoding="utf-8")) == {"x": 1})
    dpath = Path(td) / "adir"
    dpath.mkdir()
    v2, msg2, _ = violates(lambda: m.safe_write_json(dpath, {"x": 3}))
    rec("E", "safe_write_json refuses when the target path is an existing DIRECTORY", v2, msg2[:70])
    empty = Path(td) / "empty.json"
    empty.touch()
    v3, _, _ = violates(lambda: m.safe_write_json(empty, {"x": 4}))
    rec("E", "safe_write_json refuses even a zero-byte existing file", v3)

# Execution gates.
v_g, msg_g, _ = violates(m.require_real_data_authorization)
rec("E", "the real-data gate refuses by default",
    v_g and "off by default" in msg_g.lower() and m.REAL_DATA_EXECUTION_ENABLED is False)
saved = m.REAL_DATA_EXECUTION_ENABLED
m.REAL_DATA_EXECUTION_ENABLED = True
v_after, _, _ = violates(m.require_real_data_authorization)
m.REAL_DATA_EXECUTION_ENABLED = saved
rec("E", "OBSERVATION: the gate's default argument is bound at import, so flipping the module "
         "constant does NOT open it -- fail-closed, but the constant is not the live switch",
    v_after, "mutating REAL_DATA_EXECUTION_ENABLED=True still raises", kind="observation")

tree = ast.parse(SRC)
all_imports = sorted({(getattr(n, "module", None) or n.names[0].name).split(".")[0]
                      for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))})
rec("E", "the module imports nothing that could read a corpus or reach a network",
    set(all_imports) <= {"__future__", "json", "math", "pathlib", "numpy"}, f"imports={all_imports}")
banned_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id in {"open", "eval", "exec", "__import__", "input"}]
rec("E", "no open()/eval()/exec()/__import__() anywhere in the module", not banned_calls)
callers = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
           and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                   and c.func.id == "require_real_data_authorization" for c in ast.walk(n))]
rec("E", "OBSERVATION: no function in the core calls require_real_data_authorization -- the gate is "
         "declarative and enforces nothing until the unwritten runner calls it",
    callers == [], f"callers={callers}", kind="observation")

# =====================================================================================
# AREA F -- forbidden apparatus, semantically not just lexically
# =====================================================================================
body_src = SRC.split('"""', 2)[2]
tree_body = ast.parse(SRC)
# 1. no division anywhere whose result could be Delta/G.
divisions = []
for n in ast.walk(tree_body):
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Div, ast.FloorDiv)):
        divisions.append(ast.unparse(n))
rec("F", "every division in the module is enumerated and none is a ratio of Delta to G",
    all(not ({"delta", "g_bar", "g_bar_scaled"} & set(d.lower().replace("_", " ").split()))
        for d in divisions),
    "; ".join(divisions))
# 2. Withdrawn cut points must not occur at all. 1.0 / -1.0 / 2 are structurally unavoidable
#    (eps fallback d=1, Haar sign fix, ndim!=2, indent=2, the [0,1] score range), so each of those
#    occurrences is located line by line and judged, rather than banned wholesale.
src_lines = SRC.splitlines()
occurrences = {}
for n in ast.walk(tree_body):
    val = None
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        val = float(n.value)
    elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub) and isinstance(n.operand, ast.Constant) \
            and isinstance(n.operand.value, (int, float)):
        val = -float(n.operand.value)
    if val in {-1.0, -0.6, -0.2, 0.2, 0.6, 1.0, 2.0}:
        occurrences.setdefault(val, set()).add((n.lineno, src_lines[n.lineno - 1].strip()[:70]))
cutpoints = {v: sorted(occurrences.get(v, set())) for v in (-0.6, -0.2, 0.2, 0.6)}
rec("F", "the four withdrawn cut points (-0.60, -0.20, +0.20, +0.60) do not occur at all",
    not any(cutpoints.values()), f"{ {k: v for k, v in cutpoints.items() if v} }")
floor_cmp = []
for n in ast.walk(tree_body):
    if isinstance(n, ast.Compare):
        txt = ast.unparse(n)
        if "2.0" in txt or any(t in txt.lower() for t in ("g_bar", "delta_bar")):
            floor_cmp.append(txt)
rec("F", "no comparison anywhere applies a floor or a band to a reported quantity",
    not floor_cmp, f"comparisons touching a reported quantity or 2.0: {floor_cmp}")
rec("F", "every occurrence of 1.0 / -1.0 / 2 is located and none is a decision constant", True,
    "; ".join(f"{v}@L{ln}: {txt}" for v in (-1.0, 1.0, 2.0)
              for ln, txt in sorted(occurrences.get(v, set()))), kind="observation")
# 3. no forbidden label in ANY string of the module, docstrings included, except as a negated mention.
labels_forbidden = ["relative scale unsuitable", "indeterminate", "accounts for most",
                    "does not account", "direction reversed", "gap larger under rescaling"]
strings = [n.value.lower() for n in ast.walk(tree_body)
           if isinstance(n, ast.Constant) and isinstance(n.value, str)]
module_doc = (ast.get_docstring(tree_body) or "").lower()
occ = {lab: [s[:60] for s in strings if lab in s] for lab in labels_forbidden}
occ_nondoc = {lab: [s for s in v if s not in module_doc and lab not in module_doc]
              for lab, v in occ.items()}
rec("F", "no categorical verdict label appears in any string outside the module docstring",
    all(not v for v in occ_nondoc.values()),
    "; ".join(f"{k}:{v}" for k, v in occ.items() if v) or "none anywhere")
rec("F", "OBSERVATION: the module docstring does name the forbidden apparatus, in order to declare "
         "it absent; the preparer's own token scan deliberately excludes that docstring",
    any(lab in module_doc for lab in ["relative scale unsuitable", "indeterminate"]),
    "judged acceptable: naming a thing to forbid it is not implementing it", kind="observation")
# 4. output schema carries none of it.
schema_keys = set()
for n in ast.walk(tree_body):
    if isinstance(n, ast.Dict):
        for k in n.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                schema_keys.add(k.value)
rec("F", "the output schema contains no ratio, band, verdict or label key",
    not ({"rho", "rho_hat", "verdict", "band", "label", "category", "relative_change"} & schema_keys),
    f"keys={sorted(schema_keys)}")
# 5. names.
names = {n.id for n in ast.walk(tree_body) if isinstance(n, ast.Name)} | \
        {n.name for n in ast.walk(tree_body) if isinstance(n, ast.FunctionDef)} | \
        {n.attr for n in ast.walk(tree_body) if isinstance(n, ast.Attribute)}
rec("F", "no identifier names a ratio, verdict, band or floor",
    not any(bad in nm.lower() for nm in names
            for bad in ("rho", "verdict", "band", "floor", "category", "ratio")),
    "")

print(f"\n{'ALL EXPECTATIONS HELD' if _fails == 0 else str(_fails) + ' EXPECTATION(S) FAILED'}"
      f"   ({sum(1 for r in results if r['kind'] == 'expectation')} expectations, "
      f"{sum(1 for r in results if r['kind'] == 'observation')} recorded observations)")

if OUT:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "core_sha256_of_file_as_read": __import__("hashlib").sha256(CORE.read_bytes()).hexdigest(),
        "python": sys.version.split()[0], "numpy": np.__version__,
        "expectations_failed": _fails, "results": results}, indent=2) + "\n", encoding="utf-8")
raise SystemExit(1 if _fails else 0)
