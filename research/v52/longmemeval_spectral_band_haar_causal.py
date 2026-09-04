#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

ROOT = Path(__file__).resolve().parents[2]
A1_PATH = ROOT / "adapters/longmemeval_v52_adapter.py"
A2_PATH = ROOT / "adapters/longmemeval_v52_adapter_v2.py"

PREREG_GIT_BLOB = "02aa91a12b4052bbb2f0a6617167c8851e4f71f7"
A1_SHA256 = "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722"
A2_SHA256 = "643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218"
DATASET_URL = "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json"
DATASET_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
DATASET_BYTES = 277383467
FROZEN_NATIVE_R3 = 0.5419751773049646
FROZEN_FULL_HAAR_R3 = 0.38271666666667
EXPECTED_PRIMARY = 470
SVD_SEED = 5204
CAUSAL_SEEDS = [55001, 55002, 55003, 55004, 55005]
N_NUISANCE = 20
TOPK = 3
TOL = 1e-12

BANDS = {
    "High32": np.arange(0, 32, dtype=int),
    "Mid32": np.arange(32, 64, dtype=int),
    "Low32": np.arange(64, 96, dtype=int),
    "HighMid64": np.arange(0, 64, dtype=int),
    "HighLow64": np.r_[0:32, 64:96].astype(int),
    "MidLow64": np.arange(32, 96, dtype=int),
    "Full96": np.arange(0, 96, dtype=int),
}


def sha256_file(path: Path, chunk: int = 8 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def acquire_dataset(work: Path) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    p = work / "longmemeval_s_cleaned.json"
    req = urllib.request.Request(DATASET_URL, headers={"User-Agent": "llmzip-v52-causal/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, p.open("wb") as f:
        while True:
            b = r.read(8 << 20)
            if not b:
                break
            f.write(b)
    if p.stat().st_size != DATASET_BYTES:
        raise RuntimeError(f"dataset byte size mismatch: {p.stat().st_size}")
    got = sha256_file(p)
    if got != DATASET_SHA256:
        raise RuntimeError(f"dataset SHA mismatch: {got}")
    return p


def haar_q(rng: np.random.Generator, d: int) -> np.ndarray:
    A = rng.standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    sg = np.where(np.diag(R) < 0, -1.0, 1.0)
    return Q * sg[None, :]


def within_band_matrix(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    R = np.zeros((96, 96), dtype=float)
    for lo, hi in [(0, 32), (32, 64), (64, 96)]:
        R[lo:hi, lo:hi] = haar_q(rng, 32)
    return R


def selected_subspace_matrix(seed: int, idx: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(seed)
    Q = haar_q(rng, len(idx))
    R = np.eye(96, dtype=float)
    R[np.ix_(idx, idx)] = Q
    return R


def transforms(seed: int) -> dict[str, np.ndarray]:
    return {
        "WITHIN_SPECTRAL_BAND_HAAR": within_band_matrix(seed),
        "HAAR_HIGH_MID64": selected_subspace_matrix(seed, BANDS["HighMid64"]),
        "HAAR_HIGH_LOW64": selected_subspace_matrix(seed, BANDS["HighLow64"]),
        "HAAR_MID_LOW64": selected_subspace_matrix(seed, BANDS["MidLow64"]),
    }


def build_rep(item: dict, a2):
    mem, gids, issues = a2.build_archive(item)
    if issues:
        blocking = [x for x in issues if x.get("code") in {"DUPLICATE_MEMORY_ID", "INVALID_ROLE", "INVALID_CONTENT"}]
        if blocking:
            raise RuntimeError(f"archive issues {item['question_id']}: {blocking[:3]}")
    texts = a2.fit_input_payload(mem)
    wv, cv, sv, Xw, Xc, Xl = a2.fit_archive_representation(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    if min(Z.shape) <= 96:
        raise RuntimeError(f"representation dimension incompatible {item['question_id']} {Z.shape}")
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    q = str(item["question"])
    Qw = normalize(wv.transform([q]))
    Qc = normalize(cv.transform([q]))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(s96.transform(Zq))
    qC = (QY - mu).astype(np.float64)[0]
    gidset = set(gids)
    gold = np.asarray([i for i, m in enumerate(mem) if m["memory_id"] in gidset], dtype=np.int32)
    if len(gold) == 0:
        raise RuntimeError(f"non-abstention without gold {item['question_id']}")
    return str(item["question_id"]), C, qC, gold


def topk_hamming(dist: np.ndarray, priority: np.ndarray) -> np.ndarray:
    return np.lexsort((priority, dist))[:TOPK]


def fractional(top: np.ndarray, gold: np.ndarray) -> float:
    return len(set(map(int, top)) & set(map(int, gold))) / len(gold)


def mean_r3(dist: np.ndarray, priorities: list[np.ndarray], gold: np.ndarray) -> float:
    return float(np.mean([fractional(topk_hamming(dist, p), gold) for p in priorities]))


def hard_pair(D: np.ndarray, qb: np.ndarray, gold: np.ndarray, idx: np.ndarray):
    mask = np.ones(len(D), dtype=bool)
    mask[gold] = False
    ng = np.flatnonzero(mask)
    if len(ng) == 0:
        return None
    dg = np.count_nonzero(D[gold][:, idx] != qb[None, idx], axis=1)
    dn = np.count_nonzero(D[ng][:, idx] != qb[None, idx], axis=1)
    return int(dg.min()), int(dn.min())


def evaluate_one(args):
    item, lexical_ordinal, tforms = args
    a2 = load_module(A2_PATH, f"longmem_v2_{os.getpid()}_{lexical_ordinal}")
    qid, C, qC, gold = build_rep(item, a2)
    n = len(C)
    priorities = [np.random.default_rng(5_100_000 + lexical_ordinal * 100_000 + t * 100 + 99).random(n)
                  for t in range(N_NUISANCE)]
    D0 = C >= 0
    qb0 = qC >= 0
    d0 = np.count_nonzero(D0 != qb0[None, :], axis=1).astype(np.int16)
    native = mean_r3(d0, priorities, gold)

    # Exact signed-permutation sanity.
    rsp = np.random.default_rng(CAUSAL_SEEDS[0])
    perm = rsp.permutation(96)
    sg = rsp.choice(np.array([-1.0, 1.0]), 96)
    Ds = (C[:, perm] * sg) >= 0
    qs = (qC[perm] * sg) >= 0
    dsp = np.count_nonzero(Ds != qs[None, :], axis=1).astype(np.int16)
    if not np.array_equal(d0, dsp):
        raise RuntimeError(f"signed permutation failed {qid}")

    rows = []
    band_rows = []
    rescue_rows = []
    max_norm = 0.0
    max_dot = 0.0
    for seed in CAUSAL_SEEDS:
        for method, R in tforms[seed].items():
            Cr = C @ R
            qr = qC @ R
            max_norm = max(max_norm,
                           float(np.max(np.abs(np.linalg.norm(Cr, axis=1) - np.linalg.norm(C, axis=1)))),
                           abs(float(np.linalg.norm(qr) - np.linalg.norm(qC))))
            max_dot = max(max_dot, float(np.max(np.abs(Cr @ qr - C @ qC))))
            D = Cr >= 0
            qb = qr >= 0
            dist = np.count_nonzero(D != qb[None, :], axis=1).astype(np.int16)
            rows.append((seed, method, mean_r3(dist, priorities, gold)))
            if method == "WITHIN_SPECTRAL_BAND_HAAR":
                for bname, idx in BANDS.items():
                    bd = np.count_nonzero(D[:, idx] != qb[None, idx], axis=1).astype(np.int16)
                    band_rows.append((seed, bname, mean_r3(bd, priorities, gold)))
                h = hard_pair(D, qb, gold, BANDS["High32"])
                hm = hard_pair(D, qb, gold, BANDS["HighMid64"])
                f = hard_pair(D, qb, gold, BANDS["Full96"])
                if h and hm and f:
                    high_good = h[0] < h[1]
                    hm_good = hm[0] < hm[1]
                    full_good = f[0] < f[1]
                    rescue_rows.append((seed, high_good, hm_good, full_good))
    if max_norm > TOL or max_dot > TOL:
        raise RuntimeError(f"continuous invariance failed {qid}: norm={max_norm} dot={max_dot}")
    return {"qid": qid, "native": native, "rows": rows, "bands": band_rows,
            "rescue": rescue_rows, "max_norm": max_norm, "max_dot": max_dot}


def run(out: Path, workers: int):
    out.mkdir(parents=True, exist_ok=True)
    if sha256_file(A1_PATH) != A1_SHA256 or sha256_file(A2_PATH) != A2_SHA256:
        raise RuntimeError("adapter byte identity mismatch")
    raw = acquire_dataset(out / "source_bytes")
    data = json.loads(raw.read_text(encoding="utf-8"))
    if len(data) != 500:
        raise RuntimeError(f"dataset question count mismatch {len(data)}")
    prim = [x for x in data if not str(x["question_id"]).endswith("_abs")]
    if len(prim) != EXPECTED_PRIMARY:
        raise RuntimeError(f"primary count mismatch {len(prim)}")
    allq = sorted(str(x["question_id"]) for x in data)
    lex = {q: i for i, q in enumerate(allq)}

    tforms = {s: transforms(s) for s in CAUSAL_SEEDS}
    for seed, dd in tforms.items():
        for method, R in dd.items():
            err = float(np.max(np.abs(R.T @ R - np.eye(96))))
            if err > TOL:
                raise RuntimeError(f"orthogonality failed {seed} {method}: {err}")

    tasks = [(x, lex[str(x["question_id"])], tforms) for x in prim]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(evaluate_one, tasks))

    native = float(np.mean([r["native"] for r in results]))
    repro = abs(native - FROZEN_NATIVE_R3)
    if repro > TOL:
        raise RuntimeError(f"native reproduction failed got={native} frozen={FROZEN_NATIVE_R3} err={repro}")

    seed_rows = []
    for seed in CAUSAL_SEEDS:
        for method in ["WITHIN_SPECTRAL_BAND_HAAR", "HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]:
            vals = [v for r in results for s, m, v in r["rows"] if s == seed and m == method]
            seed_rows.append({"seed": seed, "method": method, "Fractional_R3": float(np.mean(vals))})
    sdf = pd.DataFrame(seed_rows)
    sdf["native_minus_intervention_pp"] = (native - sdf.Fractional_R3) * 100.0
    sdf.to_csv(out / "longmemeval_causal_seed_results.csv", index=False)

    within = sdf[sdf.method == "WITHIN_SPECTRAL_BAND_HAAR"]
    mean_band = float(within.Fractional_R3.mean())
    L_full = native - FROZEN_FULL_HAAR_R3
    L_band = native - mean_band
    rho = L_band / L_full
    if rho <= 0.25:
        regime = "[SPECTRAL-SUBSPACE PRESERVATION LEAD]"
    elif rho >= 0.75:
        regime = "[INDIVIDUAL-AXIS ORIENTATION LEAD]"
    else:
        regime = "[MIXED / BOTH LEVELS MATTER]"

    brows = []
    for seed in CAUSAL_SEEDS:
        for band in BANDS:
            vals = [v for r in results for s, b, v in r["bands"] if s == seed and b == band]
            brows.append({"seed": seed, "band": band, "Fractional_R3": float(np.mean(vals))})
    pd.DataFrame(brows).to_csv(out / "longmemeval_within_band_subset_r3.csv", index=False)

    racc = []
    for seed in CAUSAL_SEEDS:
        flags = [(hg, hmg, fg) for r in results for s, hg, hmg, fg in r["rescue"] if s == seed]
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

    max_norm = max(r["max_norm"] for r in results)
    max_dot = max(r["max_dot"] for r in results)
    summary = {
        "status": "PREREGISTERED_CAUSAL_INTERVENTION_RESULT",
        "benchmark": "LongMemEval",
        "prereg_git_blob": PREREG_GIT_BLOB,
        "identity": {
            "dataset_sha256": DATASET_SHA256,
            "dataset_bytes": DATASET_BYTES,
            "adapter_v1_sha256": A1_SHA256,
            "adapter_v2_sha256": A2_SHA256,
            "primary_questions": len(results),
        },
        "controls": {
            "native_reproduction": native,
            "frozen_native": FROZEN_NATIVE_R3,
            "absolute_reproduction_error": repro,
            "signed_permutation_exact_pass": True,
            "continuous_norm_max_abs_error": max_norm,
            "continuous_dot_max_abs_error": max_dot,
        },
        "primary": {
            "native_R3": native,
            "frozen_full_haar_R3": FROZEN_FULL_HAAR_R3,
            "within_band_haar_mean_R3": mean_band,
            "L_full": L_full,
            "L_band": L_band,
            "rho": rho,
            "regime": regime,
            "seed_R3": {str(int(r.seed)): float(r.Fractional_R3) for r in within.itertuples()},
        },
        "secondary_arm_means": {
            m: float(sdf[sdf.method == m].Fractional_R3.mean())
            for m in ["HAAR_HIGH_MID64", "HAAR_HIGH_LOW64", "HAAR_MID_LOW64"]
        },
        "interpretation_ceiling": "Fixed-benchmark preregistered causal-intervention evidence; no population-level generalization.",
    }
    (out / "longmemeval_causal_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# V52 LongMemEval Causal Spectral-Band Haar Result", "",
        f"Preregistered primary regime: `{regime}`", "",
        "## Integrity / stop rules",
        f"- primary questions: {len(results)}",
        f"- dataset SHA-256: `{DATASET_SHA256}`",
        f"- native reproduction: {native*100:.12f}% (frozen {FROZEN_NATIVE_R3*100:.12f}%; abs error {repro:.3e})",
        "- signed permutation exact control: PASS",
        f"- continuous norm max abs error: {max_norm:.3e}",
        f"- continuous dot max abs error: {max_dot:.3e}", "",
        "## Primary causal estimand",
        f"- Native R@3: {native*100:.6f}%",
        f"- Frozen Full-Haar mean R@3: {FROZEN_FULL_HAAR_R3*100:.6f}%",
        f"- Within-band Haar mean R@3: {mean_band*100:.6f}%",
        f"- L_full: {L_full*100:.6f} pp",
        f"- L_band: {L_band*100:.6f} pp",
        f"- rho: {rho:.6f}",
        f"- verdict: `{regime}`", "", "## Per-seed within-band R@3",
    ]
    for r in within.itertuples():
        lines.append(f"- {int(r.seed)}: {r.Fractional_R3*100:.6f}%")
    lines += ["", "## Secondary cross-band arm means"]
    for m, v in summary["secondary_arm_means"].items():
        lines.append(f"- {m}: {v*100:.6f}%")
    lines += ["", "## Interpretation ceiling",
              "This is a preregistered fixed-benchmark causal intervention. Secondary arms do not alter the primary rho decision bands."]
    (out / "LONGMEMEVAL_CAUSAL_CHECKPOINT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("longmemeval_causal_outputs"))
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    run(args.out, args.workers)
