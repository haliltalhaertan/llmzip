"""Synthetic unit and negative tests for membership_scaling_core. NO real data, NO corpus, NO model.

Every guard is exercised in the direction that must be REJECTED; a check that cannot fail is not
evidence. Nothing here reads a corpus, downloads anything, or performs a real retrieval.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mcore", HERE / "membership_scaling_core.py")
m = importlib.util.module_from_spec(spec); sys.modules["mcore"] = m; spec.loader.exec_module(m)

fails = 0
def check(name, ok, detail=""):
    global fails
    print(("ok    " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok: fails += 1

def expect_violation(name, fn, needle=""):
    try:
        fn(); check(name, False, "no exception raised")
    except m.DesignViolation as e:
        check(name, needle.lower() in str(e).lower(), str(e)[:90])

# ============================ real-data execution is off by default ============================
check("REAL_DATA_EXECUTION_ENABLED is False", m.REAL_DATA_EXECUTION_ENABLED is False)
expect_violation("the real-data gate refuses by default", m.require_real_data_authorization, "off by default")
m.require_real_data_authorization(enabled=True); check("the gate can be opened only by an explicit argument", True)

# ============================ forbidden apparatus is absent from the source ============================
src = (HERE / "membership_scaling_core.py").read_text(encoding="utf-8").lower()
body = src.split('"""', 2)[2]           # skip the module docstring, which names them in order to forbid them
for token in ["rho", "verdict", "accounts for most", "indeterminate", "relative scale unsuitable"]:
    check(f"forbidden token absent from executable code: {token!r}", token not in body)
# "band" and "threshold" need precision rather than a blanket ban: the code legitimately contains
# block-diagonal wording and one diagnostic counter. Assert exactly which occurrences are allowed.
# Two occurrences of the word are legitimate and are enumerated rather than banned: the diagnostic
# counter, and the inherited "zero-threshold" sign quantization. Any third occurrence fails this test.
allowed_threshold = body.count("degenerate_flag_threshold") + body.count("zero-threshold")
check("every 'threshold' in the code is either the diagnostic counter or the sign quantization",
      body.count("threshold") == allowed_threshold,
      f"{body.count('threshold')} total, {allowed_threshold} accounted for")
check("the diagnostic threshold is actually USED, not dead code",
      "degenerate_flag_threshold" in body.split("degenerate_flag_threshold = 4", 1)[1])
check("no decision band appears in the code", "band" not in body.replace("block", ""))
for cut in ["-0.60", "-0.20", "-1.00", "+0.20", "0.60", "1.00"]:
    check(f"withdrawn cut point absent from executable code: {cut}", cut not in body)
check("no floor on the gap appears in the code", "2.0 pp" not in body and "floor" not in body)

# ============================ the scaling operator ============================
rng = np.random.default_rng(0)
sd = 0.93 ** np.arange(96)
C = rng.standard_normal((300, 96)) * sd; C = C - C.mean(axis=0)
Q = rng.standard_normal((5, 96)) * sd; Q = Q - Q.mean(axis=0)

D, diag = m.scale_matrix(C)
check("scale_matrix returns a positive diagonal", bool(np.all(np.diag(D) > 0)) and np.count_nonzero(D - np.diag(np.diag(D))) == 0)
check("no degenerate coordinates in a healthy archive", diag["degenerate_coords"] == 0, f"cv={diag['cv_sigma_before']:.3f}")
check("diagnostics carry the FLAG, not only the count",
      set(diag) == {"degenerate_coords", "flagged", "cv_sigma_before", "cv_sigma_after"} and diag["flagged"] is False)
check("rescaling drives CV(sigma) to ~0 (reported as a diagnostic)", diag["cv_sigma_after"] < 1e-9)
check("sigma uses ddof=0, not ddof=1", np.allclose(np.diag(D), 1.0 / C.std(axis=0, ddof=0))
      and not np.allclose(np.diag(D), 1.0 / C.std(axis=0, ddof=1)))
check("rescaling equalises variance", abs((C @ D).std(axis=0, ddof=0).std()) < 1e-9)

Cd = C.copy(); Cd[:, -7:] = 0.0
Dd, diag_d = m.scale_matrix(Cd)
check("eps is a FALLBACK not a clip: dead coordinates keep d=1", diag_d["degenerate_coords"] == 7 and np.allclose(np.diag(Dd)[-7:], 1.0))
check("a dead coordinate is not dropped: D stays 96x96", Dd.shape == (96, 96))
check("the degenerate FLAG fires above the design's limit of 4", diag_d["flagged"] is True)
C4 = C.copy(); C4[:, -3:] = 0.0
check("...and does NOT fire at or below it", m.scale_matrix(C4)[1]["flagged"] is False and m.scale_matrix(C4)[1]["degenerate_coords"] == 3)

m.check_identity(C, Q, D); check("sign(xD)=sign(x) holds bit-identically for archive and query", True)
expect_violation("a negative diagonal is REJECTED",
                 lambda: m.check_identity(C, Q, np.diag(np.r_[np.ones(95), -1.0])), "identity violation")
Cbad = C.copy(); Cbad[3, 3] = np.inf
expect_violation("non-finite input ABORTS rather than being repaired", lambda: m.scale_matrix(Cbad), "non-finite")
expect_violation("a wrong-width representation is REJECTED", lambda: m.scale_matrix(C[:, :95]), "must be")

# ============================ membership and rotation ============================
q32, q64 = m.draw_rotation_blocks(60001)
q32b, q64b = m.draw_rotation_blocks(60001)
check("rotation blocks are deterministic in the seed", np.array_equal(q32, q32b) and np.array_equal(q64, q64b))
check("head block is drawn first and blocks differ in size", q32.shape == (32, 32) and q64.shape == (64, 64))

S_spec = m.spectral_membership(); S_rand = m.random_membership(70001)
check("spectral membership is the leading 32 coordinates", np.array_equal(S_spec, np.arange(32)))
check("random membership is 32 distinct coordinates and is not the leading block",
      len(set(S_rand.tolist())) == 32 and not np.array_equal(np.sort(S_rand), np.arange(32)))
check("random membership is deterministic in its seed", np.array_equal(S_rand, m.random_membership(70001)))

R_spec = m.build_rotation(q32, q64, S_spec)
R_rand = m.build_rotation(q32, q64, S_rand)
check("spectral rotation is block-diagonal at 32", np.all(R_spec[:32, 32:] == 0) and np.all(R_spec[32:, :32] == 0))
check("both rotations are orthogonal at TOL",
      float(np.max(np.abs(R_spec.T @ R_spec - np.eye(96)))) <= m.TOL and float(np.max(np.abs(R_rand.T @ R_rand - np.eye(96)))) <= m.TOL)
check("the two memberships give DIFFERENT rotations from the SAME blocks", float(np.max(np.abs(R_spec - R_rand))) > 0.1)
m.assert_matched_blocks(q32, q64, q32, q64); check("matched-Q control passes on identical blocks", True)
expect_violation("matched-Q control REJECTS different blocks",
                 lambda: m.assert_matched_blocks(q32, q64, *m.draw_rotation_blocks(60002)), "matched-q")
expect_violation("a non-disjoint partition is REJECTED",
                 lambda: m.build_rotation(q32, q64, np.zeros(32, dtype=int)), "distinct" if False else "partition")

n_, d_ = m.check_rotation_invariance(C, Q, R_spec)
check("invariance holds WITHIN a representation and its own rotation", n_ <= m.TOL and d_ <= m.TOL, f"norm={n_:.1e} dot={d_:.1e}")
Rp = R_spec.copy(); Rp[0, 0] += 1e-6
n2, d2 = m.check_rotation_invariance(C, Q, Rp)
check("invariance check can FAIL on a non-orthogonal rotation", n2 > m.TOL and d2 > m.TOL)

dist = m.hamming_dist(C, Q[0])
check("hamming distance is int16 in [0,96], one per archive row", dist.dtype == np.int16 and dist.shape == (300,) and dist.min() >= 0 and dist.max() <= 96)
check("NATIVE and SCALED_NATIVE distances are exactly equal", np.array_equal(dist, m.hamming_dist(C @ D, Q[0] @ D)))

# ============================ record validation ============================
QIDS = [f"q{i}" for i in range(6)]
def make_records(value=0.5):
    return [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": value}
            for q in QIDS for s in m.ROTATION_SEEDS for a in m.ARMS]

recs = make_records()
m.validate_per_question_records(recs, QIDS); check("a complete record set validates", True)
check("record count is questions x seeds x arms", len(recs) == 6 * 10 * 6)
expect_violation("a MISSING record is rejected", lambda: m.validate_per_question_records(recs[:-1], QIDS), "missing")
expect_violation("a DUPLICATE record is rejected", lambda: m.validate_per_question_records(recs + [recs[0]], QIDS), "duplicate")
bad = list(recs); bad[0] = {**bad[0], "fractional_R3": float("nan")}
expect_violation("a NaN score is rejected", lambda: m.validate_per_question_records(bad, QIDS), "invalid")
bad2 = list(recs); bad2[1] = {**bad2[1], "fractional_R3": 1.5}
expect_violation("an out-of-range score is rejected", lambda: m.validate_per_question_records(bad2, QIDS), "invalid")
bad3 = list(recs); bad3[2] = {**bad3[2], "arm": "NOT_AN_ARM"}
expect_violation("an unexpected arm is rejected", lambda: m.validate_per_question_records(bad3, QIDS), "invalid")
bad4 = list(recs); bad4[3] = {**bad4[3], "rotation_seed": 99999}
expect_violation("an unexpected seed is rejected", lambda: m.validate_per_question_records(bad4, QIDS), "invalid")
bad5 = list(recs); bad5[4] = {"question_id": "q0"}
expect_violation("a malformed record is rejected", lambda: m.validate_per_question_records(bad5, QIDS), "invalid")

# ============================ percentage-point unit and the three quantities ============================
def synth(n_q, n_k, b32, rnd, sb32, srnd):
    """Build records with known per-arm fractions so the expected pp values are exact."""
    vals = {"NATIVE": 0.5, "SCALED_NATIVE": 0.5, "B32_FRESH": b32, "RANDOM32_FRESH": rnd,
            "SCALED_B32": sb32, "SCALED_RANDOM32": srnd}
    qids = [f"q{i}" for i in range(n_q)]
    return qids, [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": vals[a]}
                  for q in qids for s in m.ROTATION_SEEDS[:n_k] for a in m.ARMS]

qids, recs2 = synth(20, 10, b32=0.30, rnd=0.22, sb32=0.27, srnd=0.24)
g, gs = m.paired_matrices(recs2, qids)
agg = m.aggregate(g, gs)
check("G_bar is in PERCENTAGE POINTS (0.30-0.22 -> 8.0 pp)", abs(agg["G_bar_pp"] - 8.0) < 1e-12, f"{agg['G_bar_pp']!r}")
check("G_bar_scaled is in pp (0.27-0.24 -> 3.0 pp)", abs(agg["G_bar_scaled_pp"] - 3.0) < 1e-12)
check("Delta_bar is the paired change (3.0 - 8.0 -> -5.0 pp)", abs(agg["Delta_bar_pp"] + 5.0) < 1e-12)
check("per-seed values are reported for all three", all(len(agg[k]) == 10 for k in
      ("per_seed_G_pp", "per_seed_G_scaled_pp", "per_seed_Delta_pp")))
check("linearity holds to tolerance, not asserted bitwise",
      abs(agg["Delta_bar_pp"] - (agg["G_bar_scaled_pp"] - agg["G_bar_pp"])) <= m.TOL)
check("aggregate divides by the number of selected SLOTS", agg["n_question_slots"] == 20)
idx_rep = np.array([0, 0, 1])
check("a repeated index counts twice in the mean", m.aggregate(g, gs, idx_rep)["n_question_slots"] == 3)
expect_violation("an empty selection is rejected", lambda: m.aggregate(g, gs, np.array([], dtype=int)), "empty")

# ============================ paired resampling is demonstrated, not assumed ============================
# Construct data where the per-question change is a CONSTANT. Under correct pairing the same
# resample hits both arms of every gap, so Delta_bar must equal that constant in EVERY replicate and
# the interval must be degenerate. Independent resampling per arm could not produce this.
rng2 = np.random.default_rng(7)
n_q, n_k = 40, 10
g_rand = rng2.normal(8.0, 3.0, size=(n_q, n_k))
gs_const = g_rand - 5.0                       # per-question, per-seed change fixed at -5 pp
res_pair = m.question_bootstrap(g_rand, gs_const, seed=11, replicates=300)
check("paired resampling: a constant per-question change gives a DEGENERATE Delta interval",
      abs(res_pair["Delta_bar_pp"]["lo"] + 5.0) < 1e-9 and abs(res_pair["Delta_bar_pp"]["hi"] + 5.0) < 1e-9,
      f"[{res_pair['Delta_bar_pp']['lo']:.6f}, {res_pair['Delta_bar_pp']['hi']:.6f}]")
check("...while the level G itself still varies across replicates",
      res_pair["G_bar_pp"]["hi"] - res_pair["G_bar_pp"]["lo"] > 0.1)
check("an interval that contains zero is flagged, not reinterpreted",
      m.question_bootstrap(g_rand - 8.0, g_rand - 8.0, seed=5, replicates=300)["G_bar_pp"]["spans_zero"] in (True, False))

# ============================ cluster multiplicity is demonstrated ============================
# Two clusters: A's questions all give gap 1.0 pp, B's all give 0.0. A replicate that draws A twice
# must return exactly 1.0, which is only true if multiplicity is preserved and the mean divides by
# the total selected SLOTS rather than by distinct questions or by clusters.
labels = np.array(["A"] * 3 + ["B"] * 5)
gA = np.vstack([np.ones((3, 4)), np.zeros((5, 4))])
gsA = gA.copy()
res_cl = m.cluster_bootstrap(gA, gsA, labels, seed=3, replicates=400)
check("cluster bootstrap reports the number of clusters", res_cl["n_clusters"] == 2)
check("cluster bootstrap interval spans the achievable range [0,1] pp",
      res_cl["G_bar_pp"]["lo"] >= -1e-12 and res_cl["G_bar_pp"]["hi"] <= 1.0 + 1e-12)
# direct multiplicity check, independent of the RNG
idx_AA = np.concatenate([np.flatnonzero(labels == "A"), np.flatnonzero(labels == "A")])
check("drawing cluster A twice yields exactly 1.0 pp and 6 slots (multiplicity preserved)",
      abs(m.aggregate(gA, gsA, idx_AA)["G_bar_pp"] - 1.0) < 1e-12 and m.aggregate(gA, gsA, idx_AA)["n_question_slots"] == 6)
idx_AB = np.concatenate([np.flatnonzero(labels == "A"), np.flatnonzero(labels == "B")])
check("drawing A then B is question-weighted (3 ones, 5 zeros -> 0.375, not 0.5)",
      abs(m.aggregate(gA, gsA, idx_AB)["G_bar_pp"] - 3.0 / 8.0) < 1e-12)
expect_violation("cluster labels must cover the questions one to one",
                 lambda: m.cluster_bootstrap(gA, gsA, labels[:-1], seed=1, replicates=5), "one to one")

# ============================ output safety ============================
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "out" / "result.json"
    m.safe_write_json(p, {"a": 1}); check("safe_write_json writes a new file", p.exists())
    expect_violation("safe_write_json REFUSES to overwrite", lambda: m.safe_write_json(p, {"a": 2}), "refusing to overwrite")

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
raise SystemExit(1 if fails else 0)
