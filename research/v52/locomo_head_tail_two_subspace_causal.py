from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "locomo_spectral_band_haar_causal.py"

PREREG_GIT_BLOB = "0d34207be55a75194b585789c7139cbc8aeb264d"
BASE_GIT_BLOB = "7c4140252fb7f846d617189925cdf534515743f4"
SEEDS = [56001, 56002, 56003, 56004, 56005]
FROZEN_NATIVE_R3 = 0.23654714666441054
FROZEN_FULL_HAAR_R3 = 0.13770827054136
TOL = 1e-12
HEAD = np.arange(0, 32, dtype=int)
TAIL = np.arange(32, 96, dtype=int)
FULL = np.arange(0, 96, dtype=int)


def load_base():
    spec = importlib.util.spec_from_file_location("locomo_band_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import spectral-band base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def head_tail_matrix(base, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    R = np.zeros((96, 96), dtype=float)
    R[:32, :32] = base.haar_q(rng, 32)
    R[32:, 32:] = base.haar_q(rng, 64)
    return R


def run(out: Path):
    base = load_base()
    common = base.load_common()
    out.mkdir(parents=True, exist_ok=True)
    raw, audit, _ = common.acquire_and_verify(out / "source_bytes")
    convs, _ = common.load_dataset(raw, audit)
    reps = [common.build_representation(c) for c in convs]

    transforms = {s: head_tail_matrix(base, s) for s in SEEDS}
    for s, R in transforms.items():
        err = float(np.max(np.abs(R.T @ R - np.eye(96))))
        if err > TOL:
            raise RuntimeError(f"orthogonality failure {s}: {err}")

    native_vals = []
    seed_vals = {s: [] for s in SEEDS}
    subset = []
    pair = []
    rescue = {s: {"head_bad": 0, "head_bad_full_good": 0, "head_good": 0, "head_good_full_bad": 0} for s in SEEDS}
    max_norm = 0.0
    max_dot = 0.0
    valid = 0

    for ci, rep in enumerate(reps):
        C, QC = rep["C"], rep["QC"]
        D0, QB0, dist0 = base.signs_and_dist(C, QC)
        priorities = [np.random.default_rng(common.stable_archive_seed(ci, t) + 99).random(len(C)) for t in range(common.N_NUISANCE)]

        # Exact Hamming-invariant control.
        rsp = np.random.default_rng(SEEDS[0])
        perm = rsp.permutation(96)
        sg = rsp.choice(np.array([-1.0, 1.0]), 96)
        Ds = (C[:, perm] * sg) >= 0
        Qs = (QC[:, perm] * sg) >= 0
        dsp = np.count_nonzero(Qs[:, None, :] != Ds[None, :, :], axis=2).astype(np.int16)
        if not np.array_equal(dsp, dist0):
            raise RuntimeError("signed permutation Hamming invariance failed")

        cache = {}
        for s, R in transforms.items():
            Cr, Qr = C @ R, QC @ R
            max_norm = max(max_norm,
                           float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                           float(np.max(np.abs(np.linalg.norm(Qr, axis=1) - np.linalg.norm(QC, axis=1)))))
            max_dot = max(max_dot, float(np.max(np.abs(Qr @ Cr.T - QC @ C.T))))
            D, QB, dist = base.signs_and_dist(Cr, Qr)
            cache[s] = (D, QB, dist)

        if max_norm > TOL or max_dot > TOL:
            raise RuntimeError(f"continuous invariance failure norm={max_norm} dot={max_dot}")

        for qi, q in enumerate(rep["qas"]):
            gold = base.gold_rows(q, rep["id_to_row"])
            if not gold:
                continue
            valid += 1
            native_vals.append(base.mean_fractional_for_dist(common, dist0[qi], priorities, gold))
            for s in SEEDS:
                D, QB, dist = cache[s]
                full_r3 = base.mean_fractional_for_dist(common, dist[qi], priorities, gold)
                seed_vals[s].append(full_r3)
                for name, idx in [("Head32", HEAD), ("Tail64", TAIL), ("Full96", FULL)]:
                    subset.append({"seed": s, "question_id": q["question_id"], "subset": name,
                                   "Fractional_R3": base.band_r3_for_question(common, D, QB[qi], priorities, gold, idx)})
                    n, discr, adv, tie = base.pairwise_counts(D, QB[qi], gold, idx)
                    pair.append({"seed": s, "subset": name, "pair_count": n, "discrimination_sum": discr,
                                 "same_sign_adv_sum": adv, "tie_count": tie})
                hf = base.hard_pair_flags(D, QB[qi], gold, HEAD)
                ff = base.hard_pair_flags(D, QB[qi], gold, FULL)
                if hf and ff:
                    head_good = hf[0] < hf[1]
                    full_good = ff[0] < ff[1]
                    a = rescue[s]
                    if head_good:
                        a["head_good"] += 1
                        if not full_good:
                            a["head_good_full_bad"] += 1
                    else:
                        a["head_bad"] += 1
                        if full_good:
                            a["head_bad_full_good"] += 1

    if valid != 1535:
        raise RuntimeError(f"valid denominator changed {valid}")
    native = float(np.mean(native_vals))
    repro = abs(native - FROZEN_NATIVE_R3)
    if repro > TOL:
        raise RuntimeError(f"native reproduction failure {native} {repro}")

    seed_rows = []
    for s in SEEDS:
        v = float(np.mean(seed_vals[s]))
        seed_rows.append({"seed": s, "Fractional_R3": v, "native_minus_intervention_pp": (native-v)*100.0})
    sdf = pd.DataFrame(seed_rows)
    sdf.to_csv(out / "locomo_head_tail_seed_results.csv", index=False)

    mean_two = float(sdf.Fractional_R3.mean())
    L_full = native - FROZEN_FULL_HAAR_R3
    L_two = native - mean_two
    rho_two = L_two / L_full
    if rho_two <= 0.25:
        regime = "[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]"
    elif rho_two >= 0.75:
        regime = "[THREE-BAND OR FINER STRUCTURE REQUIRED LEAD]"
    else:
        regime = "[MIXED TWO-SUBSPACE / FINER-STRUCTURE REGIME]"

    subdf = pd.DataFrame(subset)
    subagg = subdf.groupby(["seed", "subset"], as_index=False).Fractional_R3.mean()
    subagg.to_csv(out / "locomo_head_tail_subset_r3.csv", index=False)

    pdf = pd.DataFrame(pair)
    pagg = pdf.groupby(["seed", "subset"], as_index=False).agg(pair_count=("pair_count","sum"),
        discrimination_sum=("discrimination_sum","sum"), same_sign_adv_sum=("same_sign_adv_sum","sum"), tie_count=("tie_count","sum"))
    pagg["pairwise_gold_vs_nongold_discrimination"] = pagg.discrimination_sum / pagg.pair_count
    pagg["gold_minus_nongold_same_sign_advantage"] = pagg.same_sign_adv_sum / pagg.pair_count
    pagg.to_csv(out / "locomo_head_tail_pairwise.csv", index=False)

    rr=[]
    for s,a in rescue.items():
        rr.append({"seed":s,**a,
            "head_wrong_or_tie_to_full_rescue": a["head_bad_full_good"]/a["head_bad"] if a["head_bad"] else math.nan,
            "head_correct_to_full_degrade": a["head_good_full_bad"]/a["head_good"] if a["head_good"] else math.nan})
    pd.DataFrame(rr).to_csv(out / "locomo_head_tail_hard_negative_rescue.csv", index=False)

    summary = {
        "status":"PREREGISTERED_HEAD_TAIL_CAUSAL_RESULT",
        "benchmark":"LoCoMo",
        "prereg_git_blob":PREREG_GIT_BLOB,
        "base_runner_git_blob":BASE_GIT_BLOB,
        "identity":{"dataset_sha256":common.DATASET_SHA256,"audit_manifest_sha256":common.AUDIT_MANIFEST_SHA256,"valid_questions":valid},
        "controls":{"native_reproduction":native,"frozen_native":FROZEN_NATIVE_R3,"absolute_reproduction_error":repro,
                    "signed_permutation_exact_pass":True,"continuous_norm_max_abs_error":max_norm,"continuous_dot_max_abs_error":max_dot},
        "primary":{"native_R3":native,"frozen_full_haar_R3":FROZEN_FULL_HAAR_R3,"head_tail_haar_mean_R3":mean_two,
                   "L_full":L_full,"L_2":L_two,"rho_2":rho_two,"regime":regime,
                   "seed_R3":{str(int(x.seed)):float(x.Fractional_R3) for x in sdf.itertuples()}},
        "interpretation_ceiling":"Fixed-benchmark preregistered causal-intervention evidence; no population-level generalization."
    }
    (out/"locomo_head_tail_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    lines=["# V52 LoCoMo Head32 vs Tail64 Causal Result","",f"Verdict: `{regime}`","",
           f"Native R@3: {native*100:.12f}%",f"Head32⊕Tail64 Haar mean R@3: {mean_two*100:.12f}%",
           f"Frozen Full-Haar R@3: {FROZEN_FULL_HAAR_R3*100:.12f}%",f"L_full: {L_full*100:.6f} pp",
           f"L_2: {L_two*100:.6f} pp",f"rho_2: {rho_two:.9f}","",
           f"Native reproduction error: {repro:.3e}","Signed permutation: PASS",
           f"Continuous norm max abs error: {max_norm:.3e}",f"Continuous dot max abs error: {max_dot:.3e}"]
    (out/"LOCOMO_HEAD_TAIL_CAUSAL_CHECKPOINT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,default=Path("locomo_head_tail_outputs"));a=ap.parse_args();run(a.out)
