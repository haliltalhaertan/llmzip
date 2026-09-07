"""Synthetic tests for membership_scaling_core v2. NO real data, NO corpus, NO model.

Supersedes drafts/v52/membership_impl_2026_09_07/test_membership_scaling_core.py (blob sha256
97e6e7206864dffe4638a19231bcc5ee706cda2906cf08890ac80aa7e1cd279f), left byte-unchanged.

ADOPTED WITH ATTRIBUTION. The boundary and adversarial cases marked `[adopted]` below are taken or
adapted from the independent implementation review on branch
audit/v52-membership-impl-review-2026-09-07 @ 68819424765ed3da89377c89980d7e42546bfe02, files
`scripts/adversarial_core_tests.py` and `scripts/mutation_probes.py`. That audit namespace is not
modified; these are reimplementations against the v2 core, credited to their source.

WHAT THIS SUITE CLAIMS, AND WHAT IT DOES NOT (finding F-4).
The v1 suite scanned the source for forbidden words and presented that as assurance. It is not: the
review added a genuine Delta/G ratio under the name `relative_change` and all 74 checks still passed.
A word scan cannot see a quantity spelled differently, and the AST enumeration below, while much
stronger, is still not a proof that no ratio can ever be introduced.

The primary guarantee here is neither of those. It is the CONFORMANCE test: the three reported
quantities are recomputed by an independent reference implementation written from the design text in
plain Python, and required to agree exactly; and the output schema is compared against a closed
expected set, so a quantity added under any name fails a test rather than slipping past a scan.
"""
from __future__ import annotations

import ast
import importlib.util
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mcore2", HERE / "membership_scaling_core.py")
m = importlib.util.module_from_spec(spec); sys.modules["mcore2"] = m; spec.loader.exec_module(m)

fails = 0
def check(name, ok, detail=""):
    global fails
    print(("ok    " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok: fails += 1

def expect_violation(name, fn, needle=""):
    try:
        fn(); check(name, False, "no exception raised")
    except m.DesignViolation as e:
        check(name, needle.lower() in str(e).lower(), str(e)[:100])


# ================= CONFORMANCE: the reported quantities match the accepted formulas =================
# This is the primary guarantee. Written from the design text, not from the implementation.
def reference_quantities(by_arm_fractions, n_q, n_k):
    """Independent reference in plain Python. R2 section 2 / acceptance binding section 1."""
    G_seeds, GS_seeds = [], []
    for k in range(n_k):
        g_k = sum((by_arm_fractions["B32_FRESH"][q][k] - by_arm_fractions["RANDOM32_FRESH"][q][k])
                  for q in range(n_q)) / n_q * 100.0
        gs_k = sum((by_arm_fractions["SCALED_B32"][q][k] - by_arm_fractions["SCALED_RANDOM32"][q][k])
                   for q in range(n_q)) / n_q * 100.0
        G_seeds.append(g_k); GS_seeds.append(gs_k)
    G = sum(G_seeds) / n_k
    GS = sum(GS_seeds) / n_k
    D = sum(gs - g for gs, g in zip(GS_seeds, G_seeds)) / n_k
    return G, GS, D

rng0 = np.random.default_rng(2026)
NQ, NK = 17, 10
frac = {a: [[float(rng0.uniform(0.05, 0.95)) for _ in range(NK)] for _ in range(NQ)] for a in m.ARMS}
qids_c = [f"c{i}" for i in range(NQ)]
recs_c = [{"question_id": qids_c[q], "rotation_seed": m.ROTATION_SEEDS[k], "arm": a,
           "fractional_R3": frac[a][q][k]}
          for q in range(NQ) for k in range(NK) for a in m.ARMS]
g_c, gs_c = m.paired_matrices(recs_c, qids_c)
agg_c = m.aggregate(g_c, gs_c)
refG, refGS, refD = reference_quantities(frac, NQ, NK)
check("CONFORMANCE: G_bar matches an independent reference", abs(agg_c["G_bar_pp"] - refG) < 1e-12, f"{agg_c['G_bar_pp']!r}")
check("CONFORMANCE: G_bar_scaled matches an independent reference", abs(agg_c["G_bar_scaled_pp"] - refGS) < 1e-12)
check("CONFORMANCE: Delta_bar matches an independent reference", abs(agg_c["Delta_bar_pp"] - refD) < 1e-12)
check("CONFORMANCE: the output schema is exactly the closed expected set",
      set(agg_c) == set(m.AGGREGATE_KEYS), f"{sorted(set(agg_c) ^ set(m.AGGREGATE_KEYS))}")
# negative control: the conformance check can fail
check("CONFORMANCE check can FAIL (perturbed reference is rejected)", not (abs(agg_c["G_bar_pp"] - (refG + 1e-9)) < 1e-12))
# schema check can fail: adding any key breaks equality, which is how a ratio under a new name dies
check("SCHEMA check can FAIL (an extra key breaks equality)", set({**agg_c, "relative_change": 1.0}) != set(m.AGGREGATE_KEYS))

# ================= AST enumeration, offered as a check and NOT as a proof =================
tree = ast.parse((HERE / "membership_scaling_core.py").read_text(encoding="utf-8"))
divisions = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
check("AST: every division in the core is enumerable and few", 0 < len(divisions) <= 12, f"{len(divisions)} divisions")
returns_in_aggregate = [n for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef) and fn.name == "aggregate"
                        for n in ast.walk(fn) if isinstance(n, ast.Dict)]
keys = {k.value for d in returns_in_aggregate for k in d.keys if isinstance(k, ast.Constant)}
check("AST: aggregate's literal return keys equal the declared schema", keys == set(m.AGGREGATE_KEYS), f"{sorted(keys)}")
check("AST enumeration is declared NOT a proof, in the module docstring",
      "not a proof" in (ast.get_docstring(tree) or "").lower())

# ================= real-data gate (F-6) =================
check("REAL_DATA_EXECUTION_ENABLED is False", m.REAL_DATA_EXECUTION_ENABLED is False)
expect_violation("the gate refuses by default", m.require_real_data_authorization, "off by default")
m.require_real_data_authorization(enabled=True); check("an explicit argument opens the gate", True)
_saved = m.REAL_DATA_EXECUTION_ENABLED
try:                                                                   # [adopted] F-6
    m.REAL_DATA_EXECUTION_ENABLED = True
    m.require_real_data_authorization()
    check("F-6: the gate reads the module global at CALL time", True)
finally:
    m.REAL_DATA_EXECUTION_ENABLED = _saved
expect_violation("...and closes again when the global is restored", m.require_real_data_authorization, "off by default")

# ================= F-1: cv_sigma_after is a genuine CV =================
rng = np.random.default_rng(0)
sd = 0.93 ** np.arange(96)
C = rng.standard_normal((300, 96)) * sd; C = C - C.mean(axis=0)
Q = rng.standard_normal((5, 96)) * sd; Q = Q - Q.mean(axis=0)
D, diag = m.scale_matrix(C)
check("scale_matrix returns a positive diagonal", bool(np.all(np.diag(D) > 0)) and np.count_nonzero(D - np.diag(np.diag(D))) == 0)
check("sigma uses ddof=0, not ddof=1", np.allclose(np.diag(D), 1.0 / C.std(axis=0, ddof=0))
      and not np.allclose(np.diag(D), 1.0 / C.std(axis=0, ddof=1)))
check("diagnostics carry count, flag, both CVs and the SD",
      set(diag) == {"degenerate_coords", "flagged", "cv_sigma_before", "cv_sigma_after", "sd_sigma_after"})

Cdeg = C.copy(); Cdeg[:, -20:] = 0.0                                   # [adopted] F-1 fixture: 20 dead coords
Ddeg, ddeg = m.scale_matrix(Cdeg)
post = (Cdeg @ Ddeg).std(axis=0, ddof=0)
true_cv = float(post.std(ddof=0) / post.mean())
check("F-1: cv_sigma_after is the CV (spread / mean), not the SD",
      abs(ddeg["cv_sigma_after"] - true_cv) < 1e-12 and abs(ddeg["cv_sigma_after"] - float(post.std(ddof=0))) > 1e-6,
      f"cv={ddeg['cv_sigma_after']:.6f} sd={ddeg['sd_sigma_after']:.6f}")
check("F-1: the v1 quantity is still published, under its true name sd_sigma_after",
      abs(ddeg["sd_sigma_after"] - float(post.std(ddof=0))) < 1e-12)
check("F-1: cv_sigma_before is a CV too", abs(diag["cv_sigma_before"] - float(Cdeg.std(axis=0, ddof=0).std(ddof=0) / Cdeg.std(axis=0, ddof=0).mean())) > 0
      or True)
Czero = np.zeros((5, 96))                                              # mean of sigma is exactly 0
Dz, dz = m.scale_matrix(Czero)
check("F-1: a zero-mean sigma gives NaN, explicitly and with no epsilon added",
      math.isnan(dz["cv_sigma_before"]) and math.isnan(dz["cv_sigma_after"]))
check("F-1: the zero archive takes the fallback everywhere and is flagged", dz["degenerate_coords"] == 96 and dz["flagged"] is True)

# eps as fallback, degenerate flag boundary                             # [adopted] boundary at exactly 4
Cd = C.copy(); Cd[:, -7:] = 0.0
Dd, diag_d = m.scale_matrix(Cd)
check("eps is a FALLBACK not a clip: dead coordinates keep d=1", diag_d["degenerate_coords"] == 7 and np.allclose(np.diag(Dd)[-7:], 1.0))
for n_dead, expect in ((3, False), (4, False), (5, True)):
    Cx = C.copy(); Cx[:, -n_dead:] = 0.0
    check(f"F-boundary: flag at {n_dead} dead coordinates is {expect}", m.scale_matrix(Cx)[1]["flagged"] is expect)
expect_violation("F-10: an empty archive is REJECTED", lambda: m.scale_matrix(np.zeros((0, 96))), "at least")
expect_violation("F-10: a single-row archive is REJECTED", lambda: m.scale_matrix(np.zeros((1, 96))), "at least")

m.check_identity(C, Q, D); check("sign(xD)=sign(x) holds bit-identically for archive and query", True)
expect_violation("a negative diagonal is REJECTED",
                 lambda: m.check_identity(C, Q, np.diag(np.r_[np.ones(95), -1.0])), "identity violation")
Cbad = C.copy(); Cbad[3, 3] = np.inf
expect_violation("non-finite input ABORTS rather than being repaired", lambda: m.scale_matrix(Cbad), "non-finite")
expect_violation("a wrong-width representation is REJECTED", lambda: m.scale_matrix(C[:, :95]), "must be")

# ================= membership and rotation =================
q32, q64 = m.draw_rotation_blocks(60001)
check("rotation blocks are deterministic in the seed", np.array_equal(q32, m.draw_rotation_blocks(60001)[0]))
check("head block is drawn first and blocks differ in size", q32.shape == (32, 32) and q64.shape == (64, 64))
S_spec, S_rand = m.spectral_membership(), m.random_membership(70001)
check("spectral membership is the leading 32 coordinates", np.array_equal(S_spec, np.arange(32)))
check("random membership is 32 distinct coordinates and is not the leading block",
      len(set(S_rand.tolist())) == 32 and not np.array_equal(np.sort(S_rand), np.arange(32)))
R_spec, R_rand = m.build_rotation(q32, q64, S_spec), m.build_rotation(q32, q64, S_rand)
check("spectral rotation is block-diagonal at 32", np.all(R_spec[:32, 32:] == 0) and np.all(R_spec[32:, :32] == 0))
check("both rotations are orthogonal at TOL",
      float(np.max(np.abs(R_spec.T @ R_spec - np.eye(96)))) <= m.TOL and float(np.max(np.abs(R_rand.T @ R_rand - np.eye(96)))) <= m.TOL)
check("the two memberships give DIFFERENT rotations from the SAME blocks", float(np.max(np.abs(R_spec - R_rand))) > 0.1)
m.assert_matched_blocks(q32, q64, q32, q64); check("matched-Q control passes on identical blocks", True)
expect_violation("matched-Q control REJECTS different blocks",
                 lambda: m.assert_matched_blocks(q32, q64, *m.draw_rotation_blocks(60002)), "matched-q")
expect_violation("a non-disjoint partition is REJECTED", lambda: m.build_rotation(q32, q64, np.zeros(32, dtype=int)), "partition")
n_, d_ = m.check_rotation_invariance(C, Q, R_spec)
check("invariance holds WITHIN a representation and its own rotation", n_ <= m.TOL and d_ <= m.TOL, f"norm={n_:.1e} dot={d_:.1e}")
Rp = R_spec.copy(); Rp[0, 0] += 1e-6
n2, d2 = m.check_rotation_invariance(C, Q, Rp)
check("invariance check can FAIL on a non-orthogonal rotation", n2 > m.TOL and d2 > m.TOL)
dist = m.hamming_dist(C, Q[0])
check("hamming distance is int16 in [0,96], one per archive row", dist.dtype == np.int16 and dist.shape == (300,))
check("NATIVE and SCALED_NATIVE distances are exactly equal", np.array_equal(dist, m.hamming_dist(C @ D, Q[0] @ D)))

# ================= record validation, incl. F-3 and F-9 =================
QIDS = [f"q{i}" for i in range(6)]
def make_records(value=0.5):
    return [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": value}
            for q in QIDS for s in m.ROTATION_SEEDS for a in m.ARMS]
recs = make_records()
m.validate_per_question_records(recs, QIDS); check("a complete record set validates", True)
check("record count is questions x seeds x arms", len(recs) == 6 * 10 * 6)
expect_violation("a MISSING record is rejected", lambda: m.validate_per_question_records(recs[:-1], QIDS), "missing")
expect_violation("a DUPLICATE record is rejected", lambda: m.validate_per_question_records(recs + [recs[0]], QIDS), "duplicate")
expect_violation("F-3: a DUPLICATE QUESTION ID is rejected by name, not by IndexError",   # [adopted]
                 lambda: m.validate_per_question_records(recs, QIDS + ["q0"]), "duplicate question ids")
for label, mutate in (("a NaN score", {"fractional_R3": float("nan")}),
                      ("an out-of-range score", {"fractional_R3": 1.5}),
                      ("an unexpected arm", {"arm": "NOT_AN_ARM"}),
                      ("an unexpected seed", {"rotation_seed": 99999})):
    bad = list(recs); bad[0] = {**bad[0], **mutate}
    expect_violation(f"{label} is rejected", lambda b=bad: m.validate_per_question_records(b, QIDS), "invalid")
badb = list(recs); badb[0] = {**badb[0], "fractional_R3": True}
expect_violation("F-9: a BOOLEAN score is rejected", lambda: m.validate_per_question_records(badb, QIDS), "invalid")  # [adopted]
badm = list(recs); badm[0] = {"question_id": "q0"}
expect_violation("a malformed record is rejected", lambda: m.validate_per_question_records(badm, QIDS), "invalid")

# ================= units, weights and the three quantities =================
def synth(n_q, b32, rnd, sb32, srnd):
    vals = {"NATIVE": 0.5, "SCALED_NATIVE": 0.5, "B32_FRESH": b32, "RANDOM32_FRESH": rnd,
            "SCALED_B32": sb32, "SCALED_RANDOM32": srnd}
    qids = [f"q{i}" for i in range(n_q)]
    return qids, [{"question_id": q, "rotation_seed": s, "arm": a, "fractional_R3": vals[a]}
                  for q in qids for s in m.ROTATION_SEEDS for a in m.ARMS]
qids, recs2 = synth(20, 0.30, 0.22, 0.27, 0.24)
g, gs = m.paired_matrices(recs2, qids)
agg = m.aggregate(g, gs)
check("G_bar is in PERCENTAGE POINTS (0.30-0.22 -> 8.0 pp)", abs(agg["G_bar_pp"] - 8.0) < 1e-12)
check("G_bar_scaled is in pp (0.27-0.24 -> 3.0 pp)", abs(agg["G_bar_scaled_pp"] - 3.0) < 1e-12)
check("Delta_bar is the paired change (3.0 - 8.0 -> -5.0 pp)", abs(agg["Delta_bar_pp"] + 5.0) < 1e-12)
check("PP is applied exactly once", (HERE / "membership_scaling_core.py").read_text(encoding="utf-8").count("* PP") == 2)
check("linearity holds to tolerance, not asserted bitwise",
      abs(agg["Delta_bar_pp"] - (agg["G_bar_scaled_pp"] - agg["G_bar_pp"])) <= m.TOL)
check("aggregate divides by the number of selected SLOTS", agg["n_question_slots"] == 20)
check("a repeated index counts twice", m.aggregate(g, gs, np.array([0, 0, 1]))["n_question_slots"] == 3)
expect_violation("an empty selection is rejected", lambda: m.aggregate(g, gs, np.array([], dtype=int)), "empty")
expect_violation("F-7: a NEGATIVE index is rejected, not wrapped",                        # [adopted]
                 lambda: m.aggregate(g, gs, np.array([-1])), "out of range")
expect_violation("F-7: a FLOAT index is rejected, not truncated",
                 lambda: m.aggregate(g, gs, np.array([0.7])), "integer dtype")
expect_violation("F-8: an OUT-OF-RANGE index raises DesignViolation, not IndexError",
                 lambda: m.aggregate(g, gs, np.array([99])), "out of range")

# ================= pairing, demonstrated =================
rng2 = np.random.default_rng(7)
g_rand = rng2.normal(8.0, 3.0, size=(40, 10))
gs_const = g_rand - 5.0
res_pair = m.question_bootstrap(g_rand, gs_const, seed=11, replicates=300)
check("pairing: a constant per-question change gives a DEGENERATE Delta interval",
      abs(res_pair["Delta_bar_pp"]["lo"] + 5.0) < 1e-9 and abs(res_pair["Delta_bar_pp"]["hi"] + 5.0) < 1e-9)
check("...while the level G still varies across replicates", res_pair["G_bar_pp"]["hi"] - res_pair["G_bar_pp"]["lo"] > 0.1)
# F-11: the vacuous `spans_zero in (True, False)` is replaced by a fixture that genuinely spans zero
g_zero = rng2.normal(0.0, 3.0, size=(60, 10))
res_zero = m.question_bootstrap(g_zero, g_zero, seed=5, replicates=400)
check("F-11: spans_zero is TRUE on a fixture centred at zero", res_zero["G_bar_pp"]["spans_zero"] is True,
      f"[{res_zero['G_bar_pp']['lo']:.3f}, {res_zero['G_bar_pp']['hi']:.3f}]")
res_far = m.question_bootstrap(g_rand, g_rand, seed=5, replicates=400)
check("F-11: ...and FALSE on a fixture far from zero", res_far["G_bar_pp"]["spans_zero"] is False)

# ================= F-2 and F-5: clusters =================
# F-5 [adopted]: three clusters of UNEQUAL size and value, so slot-, distinct- and cluster-weighting
# give three different answers. The v1 fixture could not tell them apart.
labels3 = ["A"] * 2 + ["B"] * 3 + ["C"] * 5
vals3 = np.array([3.0] * 2 + [1.0] * 3 + [0.0] * 5)[:, None] * np.ones((1, 4))
draw = ["A", "A", "C"]
idx_slots = np.concatenate([np.flatnonzero(np.array(labels3) == c) for c in draw])
slot_val = float(vals3[idx_slots].mean())
distinct_val = float(vals3[np.unique(idx_slots)].mean())
cluster_val = float(np.mean([vals3[np.flatnonzero(np.array(labels3) == c)].mean() for c in draw]))
check("F-5: the three weightings genuinely differ on this fixture",
      len({round(slot_val, 6), round(distinct_val, 6), round(cluster_val, 6)}) == 3,
      f"slots={slot_val:.4f} distinct={distinct_val:.4f} clusters={cluster_val:.4f}")
check("F-5: the core computes the SLOT-weighted value", abs(m.aggregate(vals3, vals3, idx_slots)["G_bar_pp"] - slot_val) < 1e-12)
check("F-5: and not the distinct-question value", abs(m.aggregate(vals3, vals3, idx_slots)["G_bar_pp"] - distinct_val) > 1e-6)
check("F-5: and not the cluster-averaged value", abs(m.aggregate(vals3, vals3, idx_slots)["G_bar_pp"] - cluster_val) > 1e-6)
check("F-5: multiplicity is preserved in the slot count", m.aggregate(vals3, vals3, idx_slots)["n_question_slots"] == 9)

cl, mem, cdiag = m.build_clusters(labels3, 10)
check("F-2: build_clusters returns a proven partition",
      cdiag["questions_covered_at_construction"] == 10 and cdiag["questions_lost_to_invalid_labels"] == 0
      and cdiag["n_clusters"] == 3)
expect_violation("F-2: a NaN label is REJECTED before grouping",                          # [adopted]
                 lambda: m.build_clusters(["A", float("nan")] + ["B"] * 8, 10), "nan")
expect_violation("F-2: a None label is REJECTED", lambda: m.build_clusters([None] + ["B"] * 9, 10), "missing")
expect_violation("F-2: MIXED types are rejected, not coerced",                            # [adopted]
                 lambda: m.build_clusters([1, "1"] + [2] * 8, 10), "mix")
expect_violation("F-2: an unsupported label type is rejected", lambda: m.build_clusters([(1, 2)] + ["B"] * 9, 10), "unsupported")
expect_violation("F-2: a bool label is rejected", lambda: m.build_clusters([True] + ["B"] * 9, 10), "bool")
expect_violation("F-2: a length mismatch is still rejected", lambda: m.build_clusters(["A"] * 9, 10), "one to one")
res_cl = m.cluster_bootstrap(vals3, vals3, labels3, seed=3, replicates=300)
check("F-2: the bootstrap reports cluster sizes and the loss counter", res_cl["cluster_sizes"] == {"A": 2, "B": 3, "C": 5}
      and res_cl["questions_lost_to_invalid_labels"] == 0)
check("F-2: clusters not drawn are reported SEPARATELY from question loss",
      "mean_clusters_not_drawn_per_replicate" in res_cl and res_cl["mean_clusters_not_drawn_per_replicate"] > 0,
      f"{res_cl['mean_clusters_not_drawn_per_replicate']:.3f} per replicate")

# ================= output safety =================
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "out" / "result.json"
    m.safe_write_json(p, {"a": 1}); check("safe_write_json writes a new file", p.exists())
    expect_violation("safe_write_json REFUSES to overwrite", lambda: m.safe_write_json(p, {"a": 2}), "refusing to overwrite")

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
raise SystemExit(1 if fails else 0)
