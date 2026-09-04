from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "longmemeval_spectral_band_haar_causal.py"
PREREG_GIT_BLOB = "b8acebedd49497a62ec637beabbcef6720460d15"
ADDENDUM_GIT_BLOB = "456b3b51f49a0238cd936bc3f639988fb0d673af"
BASE_GIT_BLOB = "79dd4a5ec462102da5d82530088a4b7e89bef437"
BOUNDARIES = [16, 24, 32, 48, 64]
ROTATION_SEEDS = list(range(58001, 58011))
PARTITION_SEEDS = list(range(68001, 68011))
TOL = 1e-12


def load_base():
    spec = importlib.util.spec_from_file_location("lm_boundary_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen LongMemEval base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def haar_q(rng, d):
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    sg = np.where(np.diag(R) < 0, -1.0, 1.0)
    return Q * sg[None, :]


def boundary_matrix(seed: int, b: int):
    rng = np.random.default_rng(seed)
    qh = haar_q(rng, b)
    qt = haar_q(rng, 96 - b)
    R = np.zeros((96, 96), dtype=float)
    R[:b, :b] = qh
    R[b:, b:] = qt
    return R, qh, qt


def matched_random32_matrix(rotation_seed: int, partition_seed: int):
    _, q32, q64 = boundary_matrix(rotation_seed, 32)
    perm = np.random.default_rng(partition_seed).permutation(96).astype(int)
    S = perm[:32]
    T = perm[32:]
    if len(S) != 32 or len(T) != 64 or len(np.unique(S)) != 32 or len(np.unique(T)) != 64:
        raise RuntimeError("random partition cardinality/uniqueness failure")
    if np.intersect1d(S, T).size or not np.array_equal(np.sort(np.r_[S, T]), np.arange(96)):
        raise RuntimeError("random partition disjointness/exhaustiveness failure")
    R = np.zeros((96, 96), dtype=float)
    R[np.ix_(S, S)] = q32
    R[np.ix_(T, T)] = q64
    return R, S, T, q32, q64


def build_transforms():
    transforms = {}
    partitions = []
    q_pair_max = 0.0
    for seed in ROTATION_SEEDS:
        for b in BOUNDARIES:
            R, _, _ = boundary_matrix(seed, b)
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality failure b={b} seed={seed}: {err}")
            transforms[(seed, f"B{b}")] = R
        pseed = PARTITION_SEEDS[ROTATION_SEEDS.index(seed)]
        Rr, S, T, q32r, q64r = matched_random32_matrix(seed, pseed)
        _, q32s, q64s = boundary_matrix(seed, 32)
        qerr = max(float(np.max(np.abs(q32r - q32s))), float(np.max(np.abs(q64r - q64s))))
        q_pair_max = max(q_pair_max, qerr)
        if qerr != 0.0:
            raise RuntimeError(f"matched Q32/Q64 failure seed={seed}: {qerr}")
        err = float(np.max(np.abs(Rr.T @ Rr - np.eye(96))))
        if err > TOL:
            raise RuntimeError(f"random orthogonality failure seed={seed}: {err}")
        transforms[(seed, "RANDOM32")] = Rr
        partitions.append({"rotation_seed": seed, "partition_seed": pseed, "S32": S.tolist(), "T64": T.tolist()})
    return transforms, partitions, q_pair_max


def eval_one(item, lex: int, transforms):
    b = load_base()
    a2 = b.load_module(b.A2_PATH, f"lm_boundary_v2_{os.getpid()}_{lex}")
    qid, C, qC, gold = b.build_rep(item, a2)
    n = len(C)
    priorities = [np.random.default_rng(5_100_000 + lex * 100_000 + t * 100 + 99).random(n)
                  for t in range(b.N_NUISANCE)]
    D0 = C >= 0
    qb0 = qC >= 0
    d0 = np.count_nonzero(D0 != qb0[None, :], axis=1).astype(np.int16)
    native = b.mean_r3(d0, priorities, gold)

    rsp = np.random.default_rng(ROTATION_SEEDS[0])
    perm = rsp.permutation(96)
    sg = rsp.choice(np.array([-1.0, 1.0]), 96)
    Ds = (C[:, perm] * sg) >= 0
    qs = (qC[perm] * sg) >= 0
    dsp = np.count_nonzero(Ds != qs[None, :], axis=1).astype(np.int16)
    if not np.array_equal(d0, dsp):
        raise RuntimeError(f"signed permutation failure {qid}")

    arms = [f"B{x}" for x in BOUNDARIES] + ["RANDOM32"]
    rows = []
    max_norm = 0.0
    max_dot = 0.0
    for seed in ROTATION_SEEDS:
        for arm in arms:
            R = transforms[(seed, arm)]
            Cr, qr = C @ R, qC @ R
            max_norm = max(max_norm,
                           float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                           abs(float(np.linalg.norm(qr) - np.linalg.norm(qC))))
            max_dot = max(max_dot, float(np.max(np.abs(Cr @ qr - C @ qC))))
            D = Cr >= 0
            qb = qr >= 0
            dist = np.count_nonzero(D != qb[None, :], axis=1).astype(np.int16)
            rows.append({"arm": arm, "rotation_seed": seed,
                         "partition_seed": PARTITION_SEEDS[ROTATION_SEEDS.index(seed)] if arm == "RANDOM32" else "",
                         "fractional_R3": b.mean_r3(dist, priorities, gold)})
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError(f"continuous invariance {qid}: norm={max_norm} dot={max_dot}")
    return {"qid": str(qid), "lex": int(lex), "native": float(native), "rows": rows,
            "max_norm": max_norm, "max_dot": max_dot}


def run_shard(dataset: Path, idx: int, nshards: int, out: Path):
    b = load_base()
    if dataset.stat().st_size != b.DATASET_BYTES or b.sha256_file(dataset) != b.DATASET_SHA256:
        raise RuntimeError("dataset identity mismatch")
    if b.sha256_file(b.A1_PATH) != b.A1_SHA256 or b.sha256_file(b.A2_PATH) != b.A2_SHA256:
        raise RuntimeError("adapter identity mismatch")
    data = json.loads(dataset.read_text(encoding="utf-8"))
    prim = [x for x in data if not str(x["question_id"]).endswith("_abs")]
    if len(data) != 500 or len(prim) != b.EXPECTED_PRIMARY:
        raise RuntimeError("cohort mismatch")
    allq = sorted(str(x["question_id"]) for x in data)
    lexmap = {q: i for i, q in enumerate(allq)}
    chosen = [x for i, x in enumerate(prim) if i % nshards == idx]
    transforms, partitions, q_pair_max = build_transforms()
    results = [eval_one(x, lexmap[str(x["question_id"])], transforms) for x in chosen]
    qids = [z["qid"] for z in results]
    if len(qids) != len(set(qids)) or len(qids) != len(chosen):
        raise RuntimeError("shard integrity failure")
    payload = {"shard_index": idx, "num_shards": nshards, "count": len(results),
               "partitions": partitions, "matched_q32_q64_max_abs_error": q_pair_max,
               "results": results}
    out.write_bytes(pickle.dumps(payload, pickle.HIGHEST_PROTOCOL))
    print(json.dumps({"shard": idx, "count": len(results),
                      "max_norm": max(z["max_norm"] for z in results) if results else 0.0,
                      "max_dot": max(z["max_dot"] for z in results) if results else 0.0}))


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stats_from_seed_rows(seed_rows, native, l_full):
    x = np.asarray([r["R3"] for r in seed_rows], dtype=float)
    rho = (native - x) / l_full
    return {
        "mean_R3": float(x.mean()), "rho": float((native - x.mean()) / l_full),
        "sample_sd_R3": float(x.std(ddof=1)), "se_R3": float(x.std(ddof=1) / np.sqrt(len(x))),
        "sample_sd_rho": float(rho.std(ddof=1)), "se_rho": float(rho.std(ddof=1) / np.sqrt(len(rho))),
        "rho_min": float(rho.min()), "rho_max": float(rho.max()),
        "sign_inverting_rotation_seeds": [int(seed_rows[i]["rotation_seed"]) for i in range(len(seed_rows)) if x[i] > native],
    }


def aggregate(shard_dir: Path, out: Path):
    b = load_base()
    files = sorted(shard_dir.rglob("shard_*.pkl"))
    payloads = [pickle.loads(p.read_bytes()) for p in files]
    ns = {int(p["num_shards"]) for p in payloads}
    if len(ns) != 1:
        raise RuntimeError("mixed shard counts")
    nshards = ns.pop()
    inds = sorted(int(p["shard_index"]) for p in payloads)
    if inds != list(range(nshards)):
        raise RuntimeError(f"missing/duplicate shard indices: {inds}")
    refparts = payloads[0]["partitions"]
    if any(p["partitions"] != refparts for p in payloads[1:]):
        raise RuntimeError("partition definitions differ across shards")
    q_pair_max = max(float(p["matched_q32_q64_max_abs_error"]) for p in payloads)
    if q_pair_max != 0.0:
        raise RuntimeError("matched Q32/Q64 check failed")
    results = [z for p in payloads for z in p["results"]]
    qids = [z["qid"] for z in results]
    if len(results) != 470 or len(set(qids)) != 470:
        raise RuntimeError("470/470 integrity failure")

    results = sorted(results, key=lambda z: z["qid"])
    native = float(np.mean([z["native"] for z in results]))
    repro = abs(native - b.FROZEN_NATIVE_R3)
    if repro > TOL:
        raise RuntimeError(f"native reproduction failure got={native} err={repro}")
    max_norm = max(z["max_norm"] for z in results)
    max_dot = max(z["max_dot"] for z in results)
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError("continuous invariance aggregate failure")

    out.mkdir(parents=True, exist_ok=True)
    (out / "longmemeval_boundary_random_partitions.json").write_text(json.dumps(refparts, indent=2), encoding="utf-8")
    perq = []
    for z in results:
        tie_identity = f"global_lex={z['lex']};nuisance=20;5100000+lex*100000+t*100+99"
        for r in z["rows"]:
            perq.append({"dataset": "LongMemEval", "question_id": z["qid"], "arm": r["arm"],
                         "rotation_seed": r["rotation_seed"], "partition_seed": r["partition_seed"],
                         "fractional_R3": r["fractional_R3"], "native_fractional_R3": z["native"],
                         "tie_identity": tie_identity})
    pdf = pd.DataFrame(perq).sort_values(["question_id", "rotation_seed", "arm"], kind="mergesort").reset_index(drop=True)
    arms = [f"B{x}" for x in BOUNDARIES] + ["RANDOM32"]
    expected = 470 * len(ROTATION_SEEDS) * len(arms)
    if len(pdf) != expected or pdf.duplicated(["question_id", "rotation_seed", "arm"]).any():
        raise RuntimeError(f"per-question coverage/duplicate failure rows={len(pdf)} expected={expected}")
    perq_path = out / "longmemeval_boundary_per_question.csv.gz"
    pdf.to_csv(perq_path, index=False, compression="gzip")

    l_full = native - b.FROZEN_FULL_HAAR_R3
    seed_rows = []
    arm_stats = {}
    for arm in arms:
        rows = []
        for seed in ROTATION_SEEDS:
            vals = pdf[(pdf.arm == arm) & (pdf.rotation_seed == seed)].fractional_R3.to_numpy(float)
            if len(vals) != 470:
                raise RuntimeError(f"seed coverage failure arm={arm} seed={seed}")
            r3 = float(vals.mean())
            bd = int(arm[1:]) if arm.startswith("B") else None
            row = {"arm": arm, "boundary": bd, "rotation_seed": seed, "R3": r3,
                   "rho": float((native - r3) / l_full)}
            rows.append(row)
            seed_rows.append(row)
        arm_stats[arm] = stats_from_seed_rows(rows, native, l_full)
    pd.DataFrame(seed_rows).to_csv(out / "longmemeval_boundary_seed_results.csv", index=False)

    suff = [bd for bd in BOUNDARIES if arm_stats[f"B{bd}"]["rho"] <= 0.25]
    rho32 = arm_stats["B32"]["rho"]
    rhorand = arm_stats["RANDOM32"]["rho"]
    delta = rhorand - rho32
    p1 = rho32 <= 0.25
    p2 = "SPECTRAL_POSITION_CONFIRMED" if delta >= 0.25 else ("SPECTRAL_POSITION_FALSIFIED" if delta <= 0.05 else "MIXED")

    summary = {
        "status": "PREREGISTERED_BOUNDARY_LOCALIZATION_RESULT",
        "execution": "DETERMINISTIC_SHARDED_SEMANTICS_INVARIANT",
        "benchmark": "LongMemEval",
        "prereg_git_blob": PREREG_GIT_BLOB,
        "post_audit_addendum_git_blob": ADDENDUM_GIT_BLOB,
        "base_git_blob": BASE_GIT_BLOB,
        "identity": {"dataset_sha256": b.DATASET_SHA256, "dataset_bytes": b.DATASET_BYTES,
                     "adapter_v1_sha256": b.A1_SHA256, "adapter_v2_sha256": b.A2_SHA256,
                     "primary_questions": 470, "boundaries": BOUNDARIES,
                     "rotation_seeds": ROTATION_SEEDS, "partition_seeds": PARTITION_SEEDS,
                     "shards": nshards},
        "controls": {"native_reproduction": native, "frozen_native": b.FROZEN_NATIVE_R3,
                     "absolute_reproduction_error": repro, "signed_permutation_exact_pass": True,
                     "continuous_norm_max_abs_error": max_norm, "continuous_dot_max_abs_error": max_dot,
                     "partition_checks_pass": True, "matched_q32_q64_max_abs_error": q_pair_max,
                     "per_question_expected_rows": expected, "per_question_actual_rows": len(pdf)},
        "primary": {"native_R3": native, "frozen_full_haar_R3": b.FROZEN_FULL_HAAR_R3,
                    "L_full": l_full, "arm_stats": arm_stats, "S_dataset": suff,
                    "P1_rho32_pass": p1, "rho32": rho32, "rho_random32": rhorand,
                    "Delta32": delta, "P2": p2},
        "artifacts": {"per_question_file": perq_path.name, "per_question_sha256": sha256_file(perq_path),
                      "partitions_file": "longmemeval_boundary_random_partitions.json",
                      "partitions_sha256": sha256_file(out / "longmemeval_boundary_random_partitions.json")},
        "interpretation_ceiling": "Fixed-grid fixed-dataset causal localization under one shared pipeline; no independent-replication, universal, or globally optimal-boundary claim."
    }
    (out / "longmemeval_boundary_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shard")
    s.add_argument("--dataset", type=Path, required=True)
    s.add_argument("--shard-index", type=int, required=True)
    s.add_argument("--num-shards", type=int, required=True)
    s.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--shard-dir", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.cmd == "shard":
        run_shard(args.dataset, args.shard_index, args.num_shards, args.out)
    else:
        aggregate(args.shard_dir, args.out)
