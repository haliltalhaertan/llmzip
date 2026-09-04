#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import pickle
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "longmemeval_spectral_band_haar_causal.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("lm_causal_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import causal runner")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify_dataset(p: Path, r):
    if p.stat().st_size != r.DATASET_BYTES:
        raise RuntimeError(f"dataset byte mismatch {p.stat().st_size}")
    got = r.sha256_file(p)
    if got != r.DATASET_SHA256:
        raise RuntimeError(f"dataset sha mismatch {got}")


def run_shard(dataset: Path, shard_index: int, num_shards: int, out: Path, workers: int):
    r = load_runner()
    verify_dataset(dataset, r)
    if r.sha256_file(r.A1_PATH) != r.A1_SHA256 or r.sha256_file(r.A2_PATH) != r.A2_SHA256:
        raise RuntimeError("adapter identity mismatch")
    data = json.loads(dataset.read_text(encoding="utf-8"))
    if len(data) != 500:
        raise RuntimeError(f"question count mismatch {len(data)}")
    prim = [x for x in data if not str(x["question_id"]).endswith("_abs")]
    if len(prim) != r.EXPECTED_PRIMARY:
        raise RuntimeError(f"primary count mismatch {len(prim)}")
    allq = sorted(str(x["question_id"]) for x in data)
    lex = {q: i for i, q in enumerate(allq)}
    chosen = [x for i, x in enumerate(prim) if i % num_shards == shard_index]
    tforms = {s: r.transforms(s) for s in r.CAUSAL_SEEDS}
    tasks = [(x, lex[str(x["question_id"])], tforms) for x in chosen]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(r.evaluate_one, tasks))
    qids = [z["qid"] for z in results]
    if len(qids) != len(set(qids)) or len(qids) != len(chosen):
        raise RuntimeError("shard qid integrity failure")
    payload = {
        "shard_index": shard_index,
        "num_shards": num_shards,
        "count": len(results),
        "qids": qids,
        "results": results,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL))
    print(json.dumps({"shard": shard_index, "count": len(results), "max_norm": max(z["max_norm"] for z in results), "max_dot": max(z["max_dot"] for z in results)}))


def aggregate(shard_dir: Path, out: Path):
    r = load_runner()
    files = sorted(shard_dir.rglob("shard_*.pkl"))
    if not files:
        raise RuntimeError("no shard files")
    payloads = [pickle.loads(p.read_bytes()) for p in files]
    nts = {int(p["num_shards"]) for p in payloads}
    if len(nts) != 1:
        raise RuntimeError(f"mixed num_shards {nts}")
    n = nts.pop()
    idxs = sorted(int(p["shard_index"]) for p in payloads)
    if idxs != list(range(n)):
        raise RuntimeError(f"missing/duplicate shards {idxs} expected 0..{n-1}")
    results = [z for p in payloads for z in p["results"]]
    qids = [z["qid"] for z in results]
    if len(results) != r.EXPECTED_PRIMARY or len(set(qids)) != r.EXPECTED_PRIMARY:
        raise RuntimeError(f"470/470 integrity failure count={len(results)} unique={len(set(qids))}")

    native = float(np.mean([z["native"] for z in results]))
    repro = abs(native - r.FROZEN_NATIVE_R3)
    if repro > r.TOL:
        raise RuntimeError(f"native reproduction failed got={native} frozen={r.FROZEN_NATIVE_R3} err={repro}")
    max_norm = max(z["max_norm"] for z in results)
    max_dot = max(z["max_dot"] for z in results)
    if max_norm > r.TOL or max_dot > r.TOL:
        raise RuntimeError(f"continuous invariance failure norm={max_norm} dot={max_dot}")

    seed_rows = []
    for seed in r.CAUSAL_SEEDS:
        for method in ["WITHIN_SPECTRAL_BAND_HAAR", "HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]:
            vals = [v for z in results for s, m, v in z["rows"] if s == seed and m == method]
            if len(vals) != r.EXPECTED_PRIMARY:
                raise RuntimeError(f"metric row count failure {seed} {method}: {len(vals)}")
            seed_rows.append({"seed": seed, "method": method, "Fractional_R3": float(np.mean(vals))})
    sdf = pd.DataFrame(seed_rows)
    sdf["native_minus_intervention_pp"] = (native - sdf.Fractional_R3) * 100.0

    within = sdf[sdf.method == "WITHIN_SPECTRAL_BAND_HAAR"].copy()
    mean_band = float(within.Fractional_R3.mean())
    L_full = native - r.FROZEN_FULL_HAAR_R3
    L_band = native - mean_band
    rho = L_band / L_full
    if rho <= 0.25:
        regime = "[SPECTRAL-SUBSPACE PRESERVATION LEAD]"
    elif rho >= 0.75:
        regime = "[INDIVIDUAL-AXIS ORIENTATION LEAD]"
    else:
        regime = "[MIXED / BOTH LEVELS MATTER]"

    out.mkdir(parents=True, exist_ok=True)
    sdf.to_csv(out / "longmemeval_causal_seed_results.csv", index=False)

    brows = []
    for seed in r.CAUSAL_SEEDS:
        for band in r.BANDS:
            vals = [v for z in results for s, b, v in z["bands"] if s == seed and b == band]
            if len(vals) != r.EXPECTED_PRIMARY:
                raise RuntimeError(f"band row count failure {seed} {band}: {len(vals)}")
            brows.append({"seed": seed, "band": band, "Fractional_R3": float(np.mean(vals))})
    pd.DataFrame(brows).to_csv(out / "longmemeval_within_band_subset_r3.csv", index=False)

    racc = []
    for seed in r.CAUSAL_SEEDS:
        flags = [(hg, hmg, fg) for z in results for s, hg, hmg, fg in z["rescue"] if s == seed]
        if len(flags) != r.EXPECTED_PRIMARY:
            raise RuntimeError(f"rescue row count failure seed {seed}: {len(flags)}")
        high_bad = sum(not hg for hg, _, _ in flags)
        high_bad_full_good = sum((not hg) and fg for hg, _, fg in flags)
        high_good = sum(hg for hg, _, _ in flags)
        high_good_full_bad = sum(hg and (not fg) for hg, _, fg in flags)
        hm_bad = sum(not hmg for _, hmg, _ in flags)
        hm_bad_full_good = sum((not hmg) and fg for _, hmg, fg in flags)
        racc.append({
            "seed": seed,
            "high_wrong_or_tie_to_full_rescue": high_bad_full_good / high_bad if high_bad else math.nan,
            "high_correct_to_full_degrade": high_good_full_bad / high_good if high_good else math.nan,
            "highmid_wrong_or_tie_to_full_rescue": hm_bad_full_good / hm_bad if hm_bad else math.nan,
            "high_bad": high_bad, "high_good": high_good, "hm_bad": hm_bad,
        })
    pd.DataFrame(racc).to_csv(out / "longmemeval_within_band_hard_negative_rescue.csv", index=False)

    summary = {
        "status": "PREREGISTERED_CAUSAL_INTERVENTION_RESULT",
        "execution": "SHARDED_EXACT_EQUIVALENT",
        "benchmark": "LongMemEval",
        "prereg_git_blob": r.PREREG_GIT_BLOB,
        "identity": {
            "dataset_sha256": r.DATASET_SHA256,
            "dataset_bytes": r.DATASET_BYTES,
            "adapter_v1_sha256": r.A1_SHA256,
            "adapter_v2_sha256": r.A2_SHA256,
            "primary_questions": len(results),
            "shards": n,
        },
        "controls": {
            "native_reproduction": native,
            "frozen_native": r.FROZEN_NATIVE_R3,
            "absolute_reproduction_error": repro,
            "signed_permutation_exact_pass": True,
            "continuous_norm_max_abs_error": max_norm,
            "continuous_dot_max_abs_error": max_dot,
        },
        "primary": {
            "native_R3": native,
            "frozen_full_haar_R3": r.FROZEN_FULL_HAAR_R3,
            "within_band_haar_mean_R3": mean_band,
            "L_full": L_full,
            "L_band": L_band,
            "rho": rho,
            "regime": regime,
            "seed_R3": {str(int(x.seed)): float(x.Fractional_R3) for x in within.itertuples()},
        },
        "secondary_arm_means": {
            m: float(sdf[sdf.method == m].Fractional_R3.mean())
            for m in ["HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]
        },
        "interpretation_ceiling": "Fixed-benchmark preregistered causal-intervention evidence; no population-level generalization.",
    }
    (out / "longmemeval_causal_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# V52 LongMemEval Causal Spectral-Band Haar Result (Sharded Exact Execution)", "",
        f"Preregistered primary regime: `{regime}`", "",
        "## Integrity / stop rules",
        f"- primary questions: {len(results)} / 470 unique",
        f"- shards: {n} complete",
        f"- dataset SHA-256: `{r.DATASET_SHA256}`",
        f"- native reproduction: {native*100:.12f}% (frozen {r.FROZEN_NATIVE_R3*100:.12f}%; abs error {repro:.3e})",
        "- signed permutation exact control: PASS (per question before each shard result)",
        f"- continuous norm max abs error: {max_norm:.3e}",
        f"- continuous dot max abs error: {max_dot:.3e}", "",
        "## Primary causal estimand",
        f"- Native R@3: {native*100:.6f}%",
        f"- Frozen Full-Haar mean R@3: {r.FROZEN_FULL_HAAR_R3*100:.6f}%",
        f"- Within-band Haar mean R@3: {mean_band*100:.6f}%",
        f"- L_full: {L_full*100:.6f} pp",
        f"- L_band: {L_band*100:.6f} pp",
        f"- rho: {rho:.6f}",
        f"- verdict: `{regime}`", "", "## Per-seed within-band R@3",
    ]
    for x in within.itertuples():
        lines.append(f"- {int(x.seed)}: {x.Fractional_R3*100:.6f}%")
    lines += ["", "## Secondary cross-band arm means"]
    for m, v in summary["secondary_arm_means"].items():
        lines.append(f"- {m}: {v*100:.6f}%")
    lines += ["", "## Interpretation ceiling",
              "This sharded execution is mathematically identical to the preregistered single-runner execution; shard assignment changes only scheduling. Secondary arms do not alter the primary rho decision bands."]
    (out / "LONGMEMEVAL_CAUSAL_CHECKPOINT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path)
    ap.add_argument("--shard-index", type=int)
    ap.add_argument("--num-shards", type=int)
    ap.add_argument("--shard-out", type=Path)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--aggregate-dir", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.aggregate_dir is not None:
        if a.out is None:
            ap.error("--out required for aggregate")
        aggregate(a.aggregate_dir, a.out)
    else:
        if None in (a.dataset, a.shard_index, a.num_shards, a.shard_out):
            ap.error("dataset/shard-index/num-shards/shard-out required")
        run_shard(a.dataset, a.shard_index, a.num_shards, a.shard_out, a.workers)


if __name__ == "__main__":
    main()
