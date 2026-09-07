"""Self-test for the LongMemEval sharded runner, on synthetic data only.

Covers every pure function, an end-to-end synthetic pass through `evaluate_representation` and
`summarize` (with an injected scorer), the negative controls that prove each guard can FAIL, and a
cross-runner consistency control against the LoCoMo runner's pure functions.
No corpus, no benchmark outcome, no Task 4F1 contact.
"""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent

def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, HERE / fn)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

r = load("lm_runner", "longmemeval_coordinate_scale_shard.py")
lc = load("locomo_runner", "locomo_coordinate_scale.py")

fails = 0
def check(name, ok, detail=""):
    global fails
    print(("ok    " if ok else "FAIL  ") + name + (f"   {detail}" if detail else ""))
    if not ok: fails += 1

def expect_raise(name, fn, needle=""):
    try:
        fn(); check(name, False, "no exception raised")
    except RuntimeError as e:
        check(name, needle in str(e), str(e)[:80])

# --- synthetic archive: geometric per-coordinate sd, one query per archive, as LongMemEval has ---
rng = np.random.default_rng(1)
sd = 0.93 ** np.arange(96)
C = rng.standard_normal((250, 96)) * sd
C = C - C.mean(axis=0)
qC = C[7] + 0.3 * rng.standard_normal(96) * sd
gold = np.asarray([7, 11], dtype=np.int32)

# --- scale rule and identity ---
D, ndeg, cv = r.scale_matrix(C)
check("scale_matrix positive diagonal, no degenerate coords", bool(np.all(np.diag(D) > 0)) and ndeg == 0, f"cv_before={cv:.3f}")
r.check_identity(C, qC[None, :], D); check("sign(xD)=sign(x) bit-identical (archive and query)", True)
expect_raise("negative diagonal rejected", lambda: r.check_identity(C, qC[None, :], np.diag(np.r_[np.ones(95), -1.0])), "IDENTITY")
Cd = C.copy(); Cd[:, -5:] = 0.0
Dd, ndeg_d, _ = r.scale_matrix(Cd)
check("degenerate coords fall back to d=1", ndeg_d == 5 and np.allclose(np.diag(Dd)[-5:], 1.0))

# --- transforms ---
T = r.build_transforms()
check("transform panel: 10 seeds x {FULL, BLOCK}", len(T) == 20 and all((s, k) in T for s in r.ROTATION_SEEDS for k in ("FULL", "BLOCK")))
check("all transforms orthogonal at TOL", all(float(np.max(np.abs(R.T @ R - np.eye(96)))) <= r.TOL for R in T.values()))
Rb = T[(59001, "BLOCK")]
check("BLOCK is block-diagonal at 32", np.all(Rb[:32, 32:] == 0) and np.all(Rb[32:, :32] == 0))
check("FULL is not block-diagonal", float(np.max(np.abs(T[(59001, "FULL")][:32, 32:]))) > 0.01)
check("transforms deterministic in seed", np.array_equal(r.full_matrix(59003), r.full_matrix(59003)) and np.array_equal(r.block_matrix(59003), r.block_matrix(59003)))
check("seed panel is 59001..59010 (fresh, not the audited 58001..58010)", r.ROTATION_SEEDS == list(range(59001, 59011)))

# --- invariance check: narrowed scope, must be able to fail ---
Rf = T[(59001, "FULL")]
n, d = r.check_rotation_invariance(C @ D, (qC @ D)[None, :], Rf)
check("invariance WITHIN rescaled representation at TOL", n <= r.TOL and d <= r.TOL, f"norm={n:.2e} dot={d:.2e}")
n2, d2 = r.check_rotation_invariance(C, qC[None, :], Rf)
check("invariance WITHIN original representation at TOL", n2 <= r.TOL and d2 <= r.TOL, f"norm={n2:.2e} dot={d2:.2e}")
check("invariance NOT claimed between original and rescaled", float(np.max(np.abs(np.linalg.norm(C @ D, axis=1) - np.linalg.norm(C, axis=1)))) > 1e-6)
Rp = Rf.copy(); Rp[0, 0] += 1e-6
n3, d3 = r.check_rotation_invariance(C, qC[None, :], Rp)
check("invariance check REJECTS non-orthogonal rotation", n3 > r.TOL and d3 > r.TOL, f"norm={n3:.2e} dot={d3:.2e}")

# --- hamming distance ---
dist = r.hamming_dist(C, qC)
check("hamming_dist: int16, one entry per archive row, in [0,96]", dist.dtype == np.int16 and dist.shape == (250,) and dist.min() >= 0 and dist.max() <= 96)
check("hamming_dist: signed permutation invariance exact",
      np.array_equal(dist, r.hamming_dist(C[:, ::-1] * -1.0, qC[::-1] * -1.0)))
check("hamming_dist: NATIVE == SCALED_NATIVE exactly", np.array_equal(dist, r.hamming_dist(C @ D, qC @ D)))

# --- end-to-end on synthetic data with an injected scorer ---
def mean_r3(dist, priorities, gold):
    return float(np.mean([len(set(np.lexsort((p, dist))[:3].tolist()) & set(gold.tolist())) / len(gold) for p in priorities]))
priorities = [np.random.default_rng(100 + t).random(len(C)) for t in range(20)]
z = r.evaluate_representation(C, qC, gold, priorities, T, mean_r3)
check("evaluate_representation: 10 seeds x 6 arms rows", len(z["rows"]) == 60 and sorted({x["arm"] for x in z["rows"]}) == sorted(r.ARMS))
check("evaluate_representation: NATIVE and SCALED_NATIVE rows carry the native value", all(x["fractional_R3"] == z["native"] for x in z["rows"] if x["arm"] in ("NATIVE", "SCALED_NATIVE")))
check("evaluate_representation: invariance maxima within TOL", z["max_norm"] <= r.TOL and z["max_dot"] <= r.TOL, f"norm={z['max_norm']:.2e} dot={z['max_dot']:.2e}")
check("evaluate_representation: diagnostics present", set(z["diagnostics"]) == {"degenerate_coords", "cv_sigma_before", "cv_sigma_after", "flagged"} and z["diagnostics"]["flagged"] is False)
# Negative control: a non-finite value must abort, not be repaired.
Cbad = C.copy(); Cbad[3, 3] = np.inf
expect_raise("non-finite representation aborts with the non-finite message (not a downstream symptom)",
             lambda: r.evaluate_representation(Cbad, qC, gold, priorities, T, mean_r3), "non-finite")
Cbig = C.copy(); Cbig[:, 5] *= 1e-300                 # sigma underflows below eps -> fallback d=1, must NOT abort
zb = r.evaluate_representation(Cbig, qC, gold, priorities, T, mean_r3)
check("underflowing coordinate falls back (degenerate=1), run continues", zb["diagnostics"]["degenerate_coords"] == 1)
# Negative control: a scorer that is not sign-invariant cannot smuggle a SCALED_NATIVE != NATIVE
# past the distance identity - the identity is checked on distances BEFORE scoring.
Tbad = dict(T); Tbad[(59001, "FULL")] = Rp
expect_raise("evaluate_representation aborts on a bad transform (invariance)", lambda: r.evaluate_representation(C, qC, gold, priorities, Tbad, mean_r3), "invariance")

# --- summarize: synthetic results with KNOWN fractions ---
def synth_result(qid, lex, native, full, sfull, block, sblock):
    rows = []
    for s in r.ROTATION_SEEDS:
        rows += [{"arm": "NATIVE", "rotation_seed": s, "fractional_R3": native},
                 {"arm": "SCALED_NATIVE", "rotation_seed": s, "fractional_R3": native},
                 {"arm": "FULLHAAR_FRESH", "rotation_seed": s, "fractional_R3": full},
                 {"arm": "SCALED_FULLHAAR", "rotation_seed": s, "fractional_R3": sfull},
                 {"arm": "BLOCK32_FRESH", "rotation_seed": s, "fractional_R3": block},
                 {"arm": "SCALED_BLOCK32", "rotation_seed": s, "fractional_R3": sblock}]
    return {"qid": qid, "lex": lex, "native": native, "rows": rows, "max_norm": 0.0, "max_dot": 0.0,
            "diagnostics": {"degenerate_coords": 0, "cv_sigma_before": 1.0, "cv_sigma_after": 0.0, "flagged": False}}
N = 4
res = [synth_result(f"q{i}", i, 0.6, 0.2, 0.5, 0.4, 0.45) for i in range(N)]   # frac_full=0.75, frac_block=0.25
pdf, summ = r.summarize(res, 0.6, N)
check("summarize: row count N x 10 x 6", len(pdf) == N * 10 * 6)
check("summarize: frac_full = 0.75 exactly", abs(summ["primary"]["frac_full"] - 0.75) < 1e-12)
check("summarize: frac_block = 0.25 exactly", abs(summ["primary"]["frac_block"] - 0.25) < 1e-12)
check("summarize: bands follow the preregistered thresholds", summ["primary"]["frac_full_band"].startswith("[SCALE ACCOUNTS FOR MOST") and summ["primary"]["frac_block_band"] == "[PARTIAL]")
check("summarize: I_frac secondary = 0.5", abs(summ["primary"]["I_frac_secondary"] - 0.5) < 1e-12)
check("summarize: denominator dispersion reported (sd=0 on identical seeds)", summ["primary"]["denominator_full_dispersion"]["sample_sd"] == 0.0 and len(summ["primary"]["fullhaar_fresh_R3_dispersion"]["per_seed"]) == 10)
check("summarize: pp quantities present but labelled descriptive only", "descriptive only" in summ["primary"]["descriptive_pp_only"]["note"])
expect_raise("summarize rejects a missing question", lambda: r.summarize(res[:-1], 0.6, N), "integrity")
expect_raise("summarize rejects a duplicated question", lambda: r.summarize(res + [res[0]], 0.6, N), "integrity")
expect_raise("summarize rejects native reproduction failure", lambda: r.summarize(res, 0.6 + 1e-9, N), "reproduction")
bad = [dict(z) for z in res]; bad[0] = dict(bad[0]); bad[0]["max_dot"] = 1e-9
expect_raise("summarize rejects an invariance excursion carried in a shard", lambda: r.summarize(bad, 0.6, N), "invariance")
tamper = [dict(z) for z in res]; tamper[1] = dict(tamper[1]); tamper[1]["rows"] = [dict(x) for x in tamper[1]["rows"]]
tamper[1]["rows"][1]["fractional_R3"] = 0.61          # SCALED_NATIVE row != NATIVE
expect_raise("summarize rejects SCALED_NATIVE != NATIVE", lambda: r.summarize(tamper, 0.6, N), "SCALED_NATIVE")

# --- cross-runner consistency: the two runners' pure functions must agree on the same input ---
class FakeBase:
    haar_q = staticmethod(r.haar_q)
Dl, ndl, cvl = lc.scale_matrix(C)
check("cross-runner: scale_matrix identical", np.array_equal(D, Dl) and ndeg == ndl and cv == cvl)
check("cross-runner: block matrix identical for the same seed", np.array_equal(r.block_matrix(59002), lc.block_matrix(FakeBase, 59002)))
check("cross-runner: full matrix identical for the same seed", np.array_equal(r.full_matrix(59002), lc.full_matrix(FakeBase, 59002)))
check("cross-runner: invariance check identical", r.check_rotation_invariance(C, qC[None, :], Rf) == lc.check_rotation_invariance(C, qC[None, :], Rf))
check("cross-runner: frac/band identical", r.frac(0.5, 0.3, 0.45) == lc.frac(0.5, 0.3, 0.45) and r.band(0.71) == lc.band(0.71) and r.band(0.2) == lc.band(0.2))
check("cross-runner: constants identical", (r.ROTATION_SEEDS, r.EPS_SIGMA, r.DEGENERATE_FLAG_THRESHOLD, r.TOL, r.ARMS) == (lc.ROTATION_SEEDS, lc.EPS_SIGMA, lc.DEGENERATE_FLAG_THRESHOLD, lc.TOL, lc.ARMS))

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
raise SystemExit(1 if fails else 0)
