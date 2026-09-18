"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# verify_cost.py — stdlib-only recomputation of COST_MODEL.md (PREPARED, NOT ACCEPTED)

Recomputes every storage number from DECLARED inputs only. No sealed data, no
corpus, no embeddings, no faiss. faiss-runtime figures enter as CITED CONSTANTS
with locators; nothing here re-runs them.

Inputs and locators:
- S_* (median per-archive shared projector bytes, 4 encodings): CITED from
  `origin/findings/representation-geometry-2026-09-13:research_representation_geometry_2026_09_13/measurements/projector/PROJECTOR_BYTES.json`
  key `aggregate` (VERIFIED by reading the bytes of that JSON via git show).
- EFFECTIVE_MED_A_RAW=88886.36234817814, SHARED_PV_MED=88874.36234817814,
  TO12_MED=3685020: CITED from the same JSON `aggregate.ratios_median.a_raw`
  and `aggregate.breakeven_median.a_raw` (VERIFIED).
- Programme archive sizes N_MIN=396, N_MAX=616, N_MEAN=492.77872340425535,
  N_ARCH=470: CITED from `origin/evidence/twelve-byte-cost-2026-09-11`
  (`8217704`):evidence/twelve_byte_cost_2026_09_11/EVIDENCE.json key
  `archive_cost` (VERIFIED). Total vectors 231606.0 = 470 * mean (recomputed).
- Index-only shared state (faiss runtime replay, CITED CONSTANTS, not recomputed):
  SIGN96 BinaryFlat S0=33, PQ96=98390, OPQ=135325, marginal 12/12/12/20/44 —
  CITED from EVIDENCE.json `serialization_S_of_N` + `rabitq_code_sizes`, exactly
  reproduced on Windows in `origin/codex/twelve-byte-runtime-replay-2026-09-12`
  (`9cd3f54`):evidence/runtime_replay_2026_09_12/REPLAY.json (VERIFIED equal).
- BEAM tiers 100K/500K/1M/10M: DECLARED SIZES ONLY, CITED from
  `origin/draft/v52-twelve-byte-baseline-prereg-2026-09-10`
  (`d2cfbaa`):docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md lines
  ~41-42, which name these tiers as scale explicitly NOT approached (VERIFIED).
- Baselines B_F32=384 (96*4), B_F16=192 (96*2): arithmetic identities for the
  frozen 96-D representation (see prereg revision arm table entry
  FLOAT96_CENTERED 384 B, CITED from
  `origin/codex/twelve-byte-prereg-revision-2026-09-12`
  (`a73393a`):drafts/v52/twelve_byte_prereg_revision_2026_09_12/PREREG_DRAFT.md
  section 3 arm table — VERIFIED).
- float16+zlib raw-vector baseline: NOT AVAILABLE in any cited source
  (no source stores zlib-compressed raw float vectors). Reported as None;
  the script states exactly what would be needed.

Model (see COST_MODEL.md):
  total(N)     = S + m*N,  m = 12 marginal B/vector
  effective(N) = m + S/N
  N_star(B)    = S / (B - m)   # N where SIGN96+projector ties raw baseline B
  N_par        = S / m         # N where shared/N == m (effective == 2m); this is
                               # what PROJECTOR_BYTES.json calls breakeven.to_12
"""

import json
import math
import os

# ---------------- declared inputs (see header for locators) ----------------
M = 12  # marginal persistent bytes per vector (SIGN96 code)
S_MED = {  # median per-archive shared projector bytes, by encoding
    "a_raw_f32_struct": 44220235.0,
    "b_raw_f16_struct": 22686111.0,
    "a_zlib_f32": 23733327.0,
    "b_zlib_f16": 16941200.0,
}
CITED_MEDIAN_EFFECTIVE_A_RAW = 88886.36234817814
CITED_MEDIAN_SHARED_PV_A_RAW = 88874.36234817814
CITED_TO12_MED_A_RAW = 3685020
N_MIN, N_MAX, N_MEAN, N_ARCH = 396, 616, 492.77872340425535, 470
B_F32, B_F16 = 384, 192  # 96-D float32 / float16 raw vector bytes
B_F16_ZLIB = None  # UNAVAILABLE: no cited source measures it
BEAM_TIERS = [100_000, 500_000, 1_000_000, 10_000_000]  # declared sizes only
# Index-only faiss shared state, CITED CONSTANTS from runtime replay:
S0 = {"SIGN96_BinaryFlat": 33.0, "PQ96_m12x8": 98390.0, "OPQ_PQ96": 135325.0}


def effective(S, N):
    return M + S / N


def n_star(S, B):
    return S / (B - M)


def n_parity(S):
    return S / M


def main():
    checks = []
    out = {"inputs": {"marginal": M, "S_median": S_MED,
                      "N_programme": {"min": N_MIN, "max": N_MAX,
                                      "mean": N_MEAN, "n_archives": N_ARCH},
                      "baselines": {"float32": B_F32, "float16": B_F16,
                                    "float16_zlib": B_F16_ZLIB},
                      "beam_tiers_declared_only": BEAM_TIERS, "S0": S0},
           "checks": checks, "tables": {}}

    total_vectors = N_ARCH * N_MEAN  # 231606.0
    out["inputs"]["total_vectors_longmemeval"] = total_vectors
    assert total_vectors == 231606.0, total_vectors

    # --- identity checks against cited pilot medians ---
    checks.append({"name": "median effective a_raw == 12 + cited shared/vec",
                   "pass": abs(CITED_MEDIAN_EFFECTIVE_A_RAW
                               - (M + CITED_MEDIAN_SHARED_PV_A_RAW)) < 1e-9,
                   "detail": CITED_MEDIAN_EFFECTIVE_A_RAW})
    checks.append({"name": "round(S_med_f32/12) == cited breakeven.to_12",
                   "pass": round(S_MED["a_raw_f32_struct"] / M)
                   == CITED_TO12_MED_A_RAW,
                   "detail": round(S_MED["a_raw_f32_struct"] / M)})

    # --- break-evens: N where SIGN96+projector ties raw storage ---
    be = {}
    for enc, S in S_MED.items():
        be[enc] = {"vs_float32": n_star(S, B_F32),
                   "vs_float16": n_star(S, B_F16),
                   "vs_float16_zlib": None,  # UNAVAILABLE baseline
                   "marginal_parity_S_over_12": n_parity(S)}
    out["tables"]["breakeven_N"] = be
    checks.append({"name": "f32-projector beats raw f32 only above ~118.9K",
                   "pass": 100_000 < be["a_raw_f32_struct"]["vs_float32"]
                   < 500_000,
                   "detail": be["a_raw_f32_struct"]["vs_float32"]})
    checks.append({"name": "BEAM-100K tier below f32 break-even; 500K above",
                   "pass": (BEAM_TIERS[0]
                             < be["a_raw_f32_struct"]["vs_float32"]
                             < BEAM_TIERS[1]),
                   "detail": be["a_raw_f32_struct"]["vs_float32"]})

    # --- real programme scale: effective B/vec at LongMemEval N ---
    prog = {}
    for N in (N_MIN, N_MEAN, N_MAX):
        prog[str(N)] = {enc: effective(S, N) for enc, S in S_MED.items()}
    out["tables"]["effective_at_programme_N"] = prog
    checks.append({"name": "at mean N, f32 effective exceeds raw f32 by >200x",
                   "pass": prog[str(N_MEAN)]["a_raw_f32_struct"] / B_F32 > 200,
                   "detail": prog[str(N_MEAN)]["a_raw_f32_struct"] / B_F32})

    # --- whole-benchmark totals (shared approximated as 470 x median S) ---
    S = S_MED["a_raw_f32_struct"]
    shared_all = N_ARCH * S
    codes_all = total_vectors * M
    raw_all = total_vectors * B_F32
    out["tables"]["longmemeval_totals_bytes"] = {
        "shared_approx_470x_median_S": shared_all,
        "codes_12B": codes_all,
        "sign_total": shared_all + codes_all,
        "raw_float32_total": raw_all,
        "ratio_sign_over_raw": (shared_all + codes_all) / raw_all,
        "note": "shared uses median S x 470 (approximation; per-archive S varies "
                "41785637..46272067 B). Codes and raw totals are exact.",
    }
    checks.append({"name": "whole-LongMemEval SIGN96+projector >> raw float32",
                   "pass": (shared_all + codes_all) / raw_all > 200,
                   "detail": (shared_all + codes_all) / raw_all})

    # --- declared-size-only BEAM projection (ceteris-paribus S) ---
    out["tables"]["beam_projection_ceteris_paribus_S"] = {
        str(N): effective(S_MED["a_raw_f32_struct"], N) for N in BEAM_TIERS}
    out["tables"]["beam_projection_caveat"] = (
        "BEAM tiers are DECLARED SIZES ONLY (old prereg L41-42: scale not "
        "approached). A BEAM-fit projector would have its own S; reusing the "
        "LongMemEval median S is a ceteris-paribus projection, not a measurement.")

    # --- sensitivity ---
    sens = {}
    sens["projector_float16"] = {
        "S": S_MED["b_raw_f16_struct"],
        "vs_float32": n_star(S_MED["b_raw_f16_struct"], B_F32),
        "vs_float16": n_star(S_MED["b_raw_f16_struct"], B_F16),
        "effective_at_mean_N": effective(S_MED["b_raw_f16_struct"], N_MEAN)}
    # Forbidden-by-prereg case: one global projector amortized over all vectors
    sens["global_shared_forbidden"] = {
        "effective_over_all_vectors": M + S / total_vectors,
        "beats_raw_float32": (M + S / total_vectors) < B_F32,
        "status": "PREREG-EXCLUDED deployment (archive-local fitting required; "
                  "never amortize across questions). Shown to test the "
                  "assumption most damaging to the headline.",
    }
    sens["archives_10x_larger"] = {
        str(N_MEAN * 10): {enc: effective(S, N_MEAN * 10)
                           for enc, S in S_MED.items()}}
    sens["index_only_arms_at_mean_N"] = {
        arm: M + s / N_MEAN for arm, s in S0.items()}
    out["tables"]["sensitivity"] = sens
    checks.append({"name": "global-shared (forbidden) case beats raw f32",
                   "pass": sens["global_shared_forbidden"]
                   ["effective_over_all_vectors"] < B_F32,
                   "detail": sens["global_shared_forbidden"]
                   ["effective_over_all_vectors"]})
    checks.append({"name": "10x archives still leave f32 effective above raw",
                   "pass": sens["archives_10x_larger"][str(N_MEAN * 10)]
                   ["a_raw_f32_struct"] > B_F32,
                   "detail": sens["archives_10x_larger"][str(N_MEAN * 10)]
                   ["a_raw_f32_struct"]})
    checks.append({"name": "index-only: SIGN96(33B) << PQ(98390B) at mean N",
                   "pass": sens["index_only_arms_at_mean_N"]
                   ["SIGN96_BinaryFlat"] < sens["index_only_arms_at_mean_N"]
                   ["PQ96_m12x8"],
                   "detail": sens["index_only_arms_at_mean_N"]})

    out["pass"] = all(c["pass"] for c in checks)
    here = os.path.dirname(os.path.abspath(__file__))
    evdir = os.path.join(here, "evidence")
    os.makedirs(evdir, exist_ok=True)
    with open(os.path.join(evdir, "cost_results.json"), "w") as f:
        json.dump(out, f, indent=1)

    print("verify_cost: %d/%d checks passed"
          % (sum(1 for c in checks if c["pass"]), len(checks)))
    for c in checks:
        print(("PASS " if c["pass"] else "FAIL ") + c["name"]
              + "  [" + str(c["detail"]) + "]")
    print("OVERALL: " + ("PASS" if out["pass"] else "FAIL"))
    print("float16+zlib raw baseline: UNAVAILABLE (no cited source); "
          "needed: zlib bytes of 96-D float16 vectors on programme archives.")


if __name__ == "__main__":
    main()

