from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "longmemeval_spectral_band_haar_causal.py"
PREREG_GIT_BLOB = "2d6a14f254399327f59db1958a0b5c0dfb9ea8e0"
BASE_GIT_BLOB = "79dd4a5ec462102da5d82530088a4b7e89bef437"
SEEDS = list(range(57001, 57011))
HEAD = np.arange(0, 32, dtype=int)
TAIL = np.arange(32, 96, dtype=int)
FULL = np.arange(0, 96, dtype=int)
ARM_SPEC = "SPECTRAL_HEAD32_TAIL64_HAAR_NEW"
ARM_RAND = "RANDOM32_COMPLEMENT64_HAAR"
TOL = 1e-12


def load_base():
    spec = importlib.util.spec_from_file_location("lm_random_null_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import LongMemEval base")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def haar_q(rng, d):
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    sg = np.where(np.diag(R) < 0, -1.0, 1.0)
    return Q * sg[None, :]


def paired_matrices(seed):
    prng = np.random.default_rng(seed)
    perm = prng.permutation(96)
    S = np.sort(perm[:32].astype(int))
    T = np.sort(perm[32:].astype(int))
    if len(S) != 32 or len(T) != 64 or len(np.unique(S)) != 32 or len(np.unique(T)) != 64:
        raise RuntimeError(f"partition cardinality failure seed={seed}")
    if np.intersect1d(S, T).size or not np.array_equal(np.sort(np.r_[S, T]), np.arange(96)):
        raise RuntimeError(f"partition coverage failure seed={seed}")

    rrng = np.random.default_rng(1_000_000 + seed)
    Q32 = haar_q(rrng, 32)
    Q64 = haar_q(rrng, 64)
    Rspec = np.zeros((96, 96), dtype=float)
    Rspec[:32, :32] = Q32
    Rspec[32:, 32:] = Q64
    Rrand = np.zeros((96, 96), dtype=float)
    Rrand[np.ix_(S, S)] = Q32
    Rrand[np.ix_(T, T)] = Q64
    return S, T, Rspec, Rrand


def subset_r3(base, D, qb, priorities, gold, idx):
    d = np.count_nonzero(D[:, idx] != qb[None, idx], axis=1).astype(np.int16)
    return base.mean_r3(d, priorities, gold)


def pairwise(D, qb, gold, idx):
    G = np.asarray(gold, dtype=int)
    mask = np.ones(len(D), dtype=bool)
    mask[G] = False
    NG = np.flatnonzero(mask)
    if len(G) == 0 or len(NG) == 0:
        return 0, 0.0, 0.0, 0.0
    dg = np.count_nonzero(D[G][:, idx] != qb[None, idx], axis=1)
    dn = np.count_nonzero(D[NG][:, idx] != qb[None, idx], axis=1)
    comp = dg[:, None] - dn[None, :]
    n = int(comp.size)
    disc = float(np.sum(comp < 0) + 0.5 * np.sum(comp == 0))
    adv = (float(dn.mean()) - float(dg.mean())) / len(idx) * n
    return n, disc, adv, float(np.sum(comp == 0))


def eval_one(item, lex, transforms):
    b = load_base()
    a2 = b.load_module(b.A2_PATH, f"lm_rnull_v2_{os.getpid()}_{lex}")
    qid, C, qC, gold = b.build_rep(item, a2)
    n = len(C)
    priorities = [np.random.default_rng(5_100_000 + lex * 100_000 + t * 100 + 99).random(n)
                  for t in range(b.N_NUISANCE)]
    D0 = C >= 0
    qb0 = qC >= 0
    d0 = np.count_nonzero(D0 != qb0[None, :], axis=1).astype(np.int16)
    native = b.mean_r3(d0, priorities, gold)

    rsp = np.random.default_rng(SEEDS[0])
    perm = rsp.permutation(96)
    sg = rsp.choice(np.array([-1.0, 1.0]), 96)
    Ds = (C[:, perm] * sg) >= 0
    qs = (qC[perm] * sg) >= 0
    dsp = np.count_nonzero(Ds != qs[None, :], axis=1).astype(np.int16)
    if not np.array_equal(d0, dsp):
        raise RuntimeError(f"signed permutation failure {qid}")

    rows = []
    subs = []
    pairs = []
    rescue = []
    max_norm = 0.0
    max_dot = 0.0
    for seed in SEEDS:
        S = transforms[seed]["S"]
        T = transforms[seed]["T"]
        for arm in [ARM_SPEC, ARM_RAND]:
            R = transforms[seed][arm]
            Cr = C @ R
            qr = qC @ R
            max_norm = max(max_norm,
                           float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                           abs(float(np.linalg.norm(qr) - np.linalg.norm(qC))))
            max_dot = max(max_dot, float(np.max(np.abs(Cr @ qr - C @ qC))))
            D = Cr >= 0
            qb = qr >= 0
            dist = np.count_nonzero(D != qb[None, :], axis=1).astype(np.int16)
            rows.append((seed, arm, b.mean_r3(dist, priorities, gold)))
            defs = [("Head32", HEAD), ("Tail64", TAIL), ("Full96", FULL)] if arm == ARM_SPEC else [("Random32", S), ("Random64", T), ("Full96", FULL)]
            for name, idx in defs:
                subs.append((seed, arm, name, subset_r3(b, D, qb, priorities, gold, idx)))
                pc = pairwise(D, qb, gold, idx)
                pairs.append((seed, arm, name, *pc))
            block32 = HEAD if arm == ARM_SPEC else S
            bf = b.hard_pair(D, qb, gold, block32)
            ff = b.hard_pair(D, qb, gold, FULL)
            if bf and ff:
                rescue.append((seed, arm, bf[0] < bf[1], ff[0] < ff[1]))
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError(f"continuous invariance {qid} norm={max_norm} dot={max_dot}")
    return {"qid": qid, "native": native, "rows": rows, "subs": subs, "pairs": pairs,
            "rescue": rescue, "max_norm": max_norm, "max_dot": max_dot}


def build_transforms():
    transforms = {}
    partitions = []
    for seed in SEEDS:
        S, T, Rspec, Rrand = paired_matrices(seed)
        transforms[seed] = {"S": S, "T": T, ARM_SPEC: Rspec, ARM_RAND: Rrand}
        partitions.append({"seed": seed, "S32": S.tolist(), "T64": T.tolist()})
        for arm, R in [(ARM_SPEC, Rspec), (ARM_RAND, Rrand)]:
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality seed={seed} arm={arm} err={err}")
    return transforms, partitions


def run_shard(dataset, idx, nshards, out):
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
    lex = {q: i for i, q in enumerate(allq)}
    chosen = [x for i, x in enumerate(prim) if i % nshards == idx]
    transforms, partitions = build_transforms()
    results = [eval_one(x, lex[str(x["question_id"])], transforms) for x in chosen]
    qids = [z["qid"] for z in results]
    if len(qids) != len(set(qids)) or len(qids) != len(chosen):
        raise RuntimeError("shard integrity")
    payload = {"shard_index": idx, "num_shards": nshards, "count": len(results), "partitions": partitions, "results": results}
    out.write_bytes(pickle.dumps(payload, pickle.HIGHEST_PROTOCOL))
    print(json.dumps({"shard": idx, "count": len(results),
                      "max_norm": max(z["max_norm"] for z in results),
                      "max_dot": max(z["max_dot"] for z in results)}))


def aggregate(shard_dir, out):
    b = load_base()
    files = sorted(shard_dir.rglob("shard_*.pkl"))
    ps = [pickle.loads(p.read_bytes()) for p in files]
    ns = {int(p["num_shards"]) for p in ps}
    if len(ns) != 1:
        raise RuntimeError("mixed shard counts")
    n = ns.pop()
    inds = sorted(int(p["shard_index"]) for p in ps)
    if inds != list(range(n)):
        raise RuntimeError(f"missing shards {inds}")
    reference_partitions = ps[0]["partitions"]
    if any(p["partitions"] != reference_partitions for p in ps[1:]):
        raise RuntimeError("partition definitions differ across shards")
    results = [z for p in ps for z in p["results"]]
    qids = [z["qid"] for z in results]
    if len(results) != 470 or len(set(qids)) != 470:
        raise RuntimeError("470/470 integrity failure")

    native = float(np.mean([z["native"] for z in results]))
    repro = abs(native - b.FROZEN_NATIVE_R3)
    if repro > TOL:
        raise RuntimeError(f"native reproduction got={native} err={repro}")
    max_norm = max(z["max_norm"] for z in results)
    max_dot = max(z["max_dot"] for z in results)
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError("continuous invariance aggregate")

    L_full = native - b.FROZEN_FULL_HAAR_R3
    seed_rows = []
    for seed in SEEDS:
        spec_vals = [v for z in results for ss, arm, v in z["rows"] if ss == seed and arm == ARM_SPEC]
        rand_vals = [v for z in results for ss, arm, v in z["rows"] if ss == seed and arm == ARM_RAND]
        if len(spec_vals) != 470 or len(rand_vals) != 470:
            raise RuntimeError(f"seed row count failure seed={seed}")
        spec_r3 = float(np.mean(spec_vals))
        rand_r3 = float(np.mean(rand_vals))
        rho_spec_seed = (native - spec_r3) / L_full
        rho_rand_seed = (native - rand_r3) / L_full
        seed_rows.append({"seed": seed, "spectral_R3": spec_r3, "random_R3": rand_r3,
                          "rho_spec": rho_spec_seed, "rho_rand": rho_rand_seed,
                          "Delta": rho_rand_seed - rho_spec_seed})
    sdf = pd.DataFrame(seed_rows)
    out.mkdir(parents=True, exist_ok=True)
    sdf.to_csv(out / "longmemeval_random_partition_seed_results.csv", index=False)
    (out / "longmemeval_random_partitions.json").write_text(json.dumps(reference_partitions, indent=2), encoding="utf-8")

    R_spec = float(sdf.spectral_R3.mean())
    R_rand = float(sdf.random_R3.mean())
    rho_spec = (native - R_spec) / L_full
    rho_rand = (native - R_rand) / L_full
    Delta = rho_rand - rho_spec
    if rho_spec > 0.25:
        regime = "[HEAD-TAIL REPLICATION FAILURE — SPECTRAL POSITION CLAIM NOT ADVANCED]"
    elif Delta <= 0.05:
        regime = "[GENERIC BLOCK-STRUCTURE SUFFICIENCY LEAD — SPECTRAL POSITION CLAIM FALSIFIED]"
    elif Delta >= 0.25:
        regime = "[SPECTRAL POSITION LOAD-BEARING LEAD]"
    else:
        regime = "[MIXED / PARTIAL SPECTRAL POSITION CONTRIBUTION]"

    sub = []
    for seed in SEEDS:
        for arm, names in [(ARM_SPEC, ["Head32", "Tail64", "Full96"]), (ARM_RAND, ["Random32", "Random64", "Full96"])]:
            for name in names:
                vals = [v for z in results for ss, aa, nn, v in z["subs"] if ss == seed and aa == arm and nn == name]
                sub.append({"seed": seed, "arm": arm, "subset": name, "Fractional_R3": float(np.mean(vals))})
    pd.DataFrame(sub).to_csv(out / "longmemeval_random_partition_subset_r3.csv", index=False)

    prows = []
    for seed in SEEDS:
        for arm, names in [(ARM_SPEC, ["Head32", "Tail64", "Full96"]), (ARM_RAND, ["Random32", "Random64", "Full96"])]:
            for name in names:
                vals = [r for z in results for r in z["pairs"] if r[0] == seed and r[1] == arm and r[2] == name]
                N = sum(r[3] for r in vals)
                disc = sum(r[4] for r in vals)
                adv = sum(r[5] for r in vals)
                tie = sum(r[6] for r in vals)
                prows.append({"seed": seed, "arm": arm, "subset": name, "pair_count": N,
                              "pairwise_gold_vs_nongold_discrimination": disc / N,
                              "gold_minus_nongold_same_sign_advantage": adv / N, "tie_fraction": tie / N})
    pd.DataFrame(prows).to_csv(out / "longmemeval_random_partition_pairwise.csv", index=False)

    rr = []
    for seed in SEEDS:
        for arm in [ARM_SPEC, ARM_RAND]:
            flags = [(bg, fg) for z in results for ss, aa, bg, fg in z["rescue"] if ss == seed and aa == arm]
            bad = sum(not bg for bg, _ in flags)
            badgood = sum((not bg) and fg for bg, fg in flags)
            good = sum(bg for bg, _ in flags)
            goodbad = sum(bg and (not fg) for bg, fg in flags)
            rr.append({"seed": seed, "arm": arm, "block32_bad": bad, "block32_good": good,
                       "block32_wrong_or_tie_to_full_rescue": badgood / bad if bad else math.nan,
                       "block32_correct_to_full_degrade": goodbad / good if good else math.nan})
    pd.DataFrame(rr).to_csv(out / "longmemeval_random_partition_hard_negative_rescue.csv", index=False)

    def disp(series):
        x = np.asarray(series, dtype=float)
        return {"mean": float(x.mean()), "sample_sd": float(x.std(ddof=1)), "population_sd": float(x.std(ddof=0)),
                "min": float(x.min()), "max": float(x.max())}

    summary = {
        "status": "PREREGISTERED_MATCHED_RANDOM_PARTITION_NULL_RESULT",
        "execution": "SHARDED_EXACT",
        "benchmark": "LongMemEval",
        "prereg_git_blob": PREREG_GIT_BLOB,
        "base_runner_git_blob": BASE_GIT_BLOB,
        "identity": {"dataset_sha256": b.DATASET_SHA256, "dataset_bytes": b.DATASET_BYTES,
                     "adapter_v1_sha256": b.A1_SHA256, "adapter_v2_sha256": b.A2_SHA256,
                     "primary_questions": 470, "shards": n, "seeds": SEEDS},
        "controls": {"native_reproduction": native, "frozen_native": b.FROZEN_NATIVE_R3,
                     "absolute_reproduction_error": repro, "signed_permutation_exact_pass": True,
                     "continuous_norm_max_abs_error": max_norm, "continuous_dot_max_abs_error": max_dot,
                     "partition_checks_pass": True},
        "primary": {"native_R3": native, "frozen_full_haar_R3": b.FROZEN_FULL_HAAR_R3, "L_full": L_full,
                    "spectral_mean_R3": R_spec, "random_mean_R3": R_rand,
                    "rho_spec": rho_spec, "rho_rand": rho_rand, "Delta": Delta, "regime": regime,
                    "seed_rows": seed_rows,
                    "dispersion": {"spectral_R3": disp(sdf.spectral_R3), "random_R3": disp(sdf.random_R3),
                                   "rho_spec": disp(sdf.rho_spec), "rho_rand": disp(sdf.rho_rand), "Delta": disp(sdf.Delta)}},
        "partitions": reference_partitions,
        "interpretation_ceiling": "Fixed-benchmark preregistered matched null control; no population-level generalization."
    }
    (out / "longmemeval_random_partition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "LONGMEMEVAL_RANDOM_PARTITION_NULL_CHECKPOINT.md").write_text(
        f"# V52 LongMemEval Matched Random-Partition Null Control\n\nVerdict: `{regime}`\n\n"
        f"Native R@3: {native*100:.12f}%\nSpectral Head32/Tail64 mean R@3: {R_spec*100:.12f}%\n"
        f"Random32/complement64 mean R@3: {R_rand*100:.12f}%\nFrozen Full-Haar R@3: {b.FROZEN_FULL_HAAR_R3*100:.12f}%\n"
        f"rho_spec: {rho_spec:.9f}\nrho_rand: {rho_rand:.9f}\nDelta: {Delta:.9f}\n\n"
        f"Native reproduction error: {repro:.3e}\nSigned permutation: PASS\n"
        f"Continuous norm max abs error: {max_norm:.3e}\nContinuous dot max abs error: {max_dot:.3e}\nPartition checks: PASS\n",
        encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path)
    ap.add_argument("--shard-index", type=int)
    ap.add_argument("--num-shards", type=int)
    ap.add_argument("--shard-out", type=Path)
    ap.add_argument("--aggregate-dir", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    if args.aggregate_dir is not None:
        aggregate(args.aggregate_dir, args.out)
    else:
        run_shard(args.dataset, args.shard_index, args.num_shards, args.shard_out)


if __name__ == "__main__":
    main()
