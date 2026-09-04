"""AUDITOR DIAGNOSTIC (G7/G11) - NOT a repository artifact, NOT preregistered by the researcher.

Question: the checkpoint attributes the preserved advantage to SPECTRAL POSITION
(leading 32 coords vs trailing 64). The executed design contains no arm that varies
WHICH coordinates form the 32-block. This script supplies that missing contrast on LoCoMo:

  HEAD32_TAIL64_HAAR   : block-diag Haar on {0..31} and {32..95}      (the preregistered arm)
  RANDPART_32_64_HAAR  : block-diag Haar on a RANDOM 32-subset and its complement

Everything else (cohort, representation, centering, sign threshold, top-k, tie/nuisance
scheme, seeds, estimand) is taken unchanged from the committed frozen code.

If rho_2(RANDPART) ~= rho_2(HEAD/TAIL), spectral position is NOT what is doing the work.
If rho_2(RANDPART) >> rho_2(HEAD/TAIL), position is load-bearing.
"""
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path
import numpy as np

V52 = Path(sys.argv[1]).resolve()          # target research/v52 dir
OUT = Path(sys.argv[2]).resolve()
SEEDS = [56001, 56002, 56003, 56004, 56005]
FROZEN_NATIVE_R3 = 0.23654714666441054
FROZEN_FULL_HAAR_R3 = 0.13770827054136
TOL = 1e-12

def _load(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

base = _load(V52 / "locomo_spectral_band_haar_causal.py", "band_base")
common = base.load_common()

def head_tail_R(seed):
    rng = np.random.default_rng(seed)
    R = np.zeros((96, 96)); R[:32, :32] = base.haar_q(rng, 32); R[32:, 32:] = base.haar_q(rng, 64)
    return R

def randpart_R(seed, part_rng):
    """Same construction, but the 32-block is a random coordinate subset."""
    perm = part_rng.permutation(96)
    S, T = np.sort(perm[:32]), np.sort(perm[32:])
    rng = np.random.default_rng(seed)
    Q32 = base.haar_q(rng, 32); Q64 = base.haar_q(rng, 64)
    R = np.zeros((96, 96))
    R[np.ix_(S, S)] = Q32; R[np.ix_(T, T)] = Q64
    return R, S

def main():
    raw, audit, _ = common.acquire_and_verify(OUT / "source_bytes")
    convs, _ = common.load_dataset(raw, audit)
    reps = [common.build_representation(c) for c in convs]

    # 5 independent random partitions, one per seed, from a partition RNG distinct from the Haar seeds
    prng = np.random.default_rng(20260904)
    arms = {"HEAD32_TAIL64_HAAR": {s: head_tail_R(s) for s in SEEDS}}
    rp = {}; parts = {}
    for s in SEEDS:
        R, S = randpart_R(s, prng); rp[s] = R; parts[s] = S.tolist()
    arms["RANDPART_32_64_HAAR"] = rp

    for a, tf in arms.items():
        for s, R in tf.items():
            e = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if e > TOL: raise RuntimeError(f"orthogonality {a} {s} {e}")

    native_vals = []
    vals = {a: {s: [] for s in SEEDS} for a in arms}
    valid = 0
    for ci, rep in enumerate(reps):
        C, QC = rep["C"], rep["QC"]
        _, _, dist0 = base.signs_and_dist(C, QC)
        priorities = [np.random.default_rng(common.stable_archive_seed(ci, t) + 99).random(len(C))
                      for t in range(common.N_NUISANCE)]
        cache = {a: {s: base.signs_and_dist(C @ R, QC @ R)[2] for s, R in tf.items()} for a, tf in arms.items()}
        for qi, q in enumerate(rep["qas"]):
            gold = base.gold_rows(q, rep["id_to_row"])
            if not gold: continue
            valid += 1
            native_vals.append(base.mean_fractional_for_dist(common, dist0[qi], priorities, gold))
            for a in arms:
                for s in SEEDS:
                    vals[a][s].append(base.mean_fractional_for_dist(common, cache[a][s][qi], priorities, gold))

    if valid != 1535: raise RuntimeError(f"denominator {valid}")
    native = float(np.mean(native_vals))
    if abs(native - FROZEN_NATIVE_R3) > TOL: raise RuntimeError(f"native repro {native}")
    L_full = native - FROZEN_FULL_HAAR_R3

    res = {"valid_questions": valid, "native_R3": native, "L_full": L_full,
           "frozen_full_haar_R3": FROZEN_FULL_HAAR_R3, "random_partitions_used": parts, "arms": {}}
    for a in arms:
        per = {s: float(np.mean(vals[a][s])) for s in SEEDS}
        mean = float(np.mean(list(per.values())))
        res["arms"][a] = {"seed_R3": per, "mean_R3": mean, "L_2": native - mean,
                          "rho_2": (native - mean) / L_full,
                          "per_seed_rho_2": {s: (native - v) / L_full for s, v in per.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "auditor_random_partition_control.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: {"rho_2": v["rho_2"], "mean_R3": v["mean_R3"]} for k, v in res["arms"].items()}, indent=2))

main()
