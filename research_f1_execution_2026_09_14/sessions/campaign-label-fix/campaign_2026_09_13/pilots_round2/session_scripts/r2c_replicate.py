#!/usr/bin/env python3
"""R2C: LoCoMo replication of axis-attack findings. Mirrors frozen T4D protocol verbatim."""
import json, re, pickle
from pathlib import Path
import numpy as np

RAW = Path("/mnt/c/Users/MDP/dev/llmzip-work/drive/locomo10.json")
AUDIT = Path("/mnt/c/Users/MDP/dev/llmzip-work/drive/audit_layer")
REGEN = Path("/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo")
OUT = Path("/tmp/r2c/details.json")

NATIVE_ANCHOR = 0.23654714666441054
HAAR_ANCHOR = 0.13770827054136
TOPK = 3
N_NUISANCE = 20
ROTATION_SEEDS = [43001, 43002, 43003, 43004, 43005]
BLOCK_SEEDS = [43001, 43002, 43003]
KS = [16, 32, 48, 64, 80]

# ---- verbatim frozen protocol functions ----
def norm_evidence(x):
    if x is None:
        return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []

def load_audit_corrections(audit_dir):
    corrections = {}
    for f in sorted(audit_dir.glob("errors_conv_*.json")):
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            qid = r.get("question_id")
            if not qid:
                continue
            corrections[str(qid)] = {
                "error_type": r.get("error_type"),
                "has_correct_evidence": "correct_evidence" in r,
                "correct_evidence": norm_evidence(r.get("correct_evidence")),
                "correct_answer": r.get("correct_answer"),
            }
    return corrections

def stable_archive_seed(archive_ordinal, trial=0):
    return 5_100_000 + archive_ordinal * 100_000 + trial * 100

def hspec(seed, b=96):
    r = np.random.default_rng(seed)
    perm = r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return perm, qs

def happly(X, perm, qs, b=96):
    xp = np.asarray(X, float)[..., perm]
    o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b)
        o[..., sl] = xp[..., sl] @ Q
    return o

def topks_by_hamming(dist, priorities, k=TOPK):
    dist = np.asarray(dist)
    P = np.asarray(priorities, dtype=float)
    if len(dist) <= k:
        return [np.lexsort((P[t], dist))[:k] for t in range(len(P))]
    kth = np.partition(dist, k - 1)[k - 1]
    strict = np.flatnonzero(dist < kth)
    boundary = np.flatnonzero(dist == kth)
    need = k - len(strict)
    if need <= 0:
        return [strict[np.lexsort((P[t, strict], dist[strict]))][:k] for t in range(len(P))]
    BP = P[:, boundary]
    if need == len(boundary):
        picks = np.tile(boundary, (len(P), 1))
    else:
        loc = np.argpartition(BP, need - 1, axis=1)[:, :need]
        picks = boundary[loc]
    return [np.concatenate([strict, picks[t]]) for t in range(len(P))]

def evidence_rows(ids, id_to_row):
    out = []
    for x in ids:
        if x in id_to_row:
            out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))

def retrieval_metrics(top, gold_rows):
    if not gold_rows:
        return {"valid": 0, "any": np.nan, "all": np.nan, "fractional": np.nan, "gold_count": 0}
    R = set(map(int, top))
    G = set(map(int, gold_rows))
    inter = len(R & G)
    return {"valid": 1, "any": float(inter > 0), "all": float(G.issubset(R)),
            "fractional": float(inter / len(G)), "gold_count": len(G)}

def mean_or_nan(xs):
    a = np.asarray(xs, dtype=float)
    return float(np.nanmean(a)) if np.isfinite(a).any() else np.nan

def hspec_blocks_for_perm(seed, perm, b=2):
    """Same rng draw order as hspec (perm draw first, then per-block QR + sign fix),
    but with caller-supplied pairing perm so Q blocks stay bit-identical across arms."""
    r = np.random.default_rng(seed)
    _ = r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return np.asarray(perm), qs

# ---- load raw + corrections (read-only) ----
raw = json.loads(RAW.read_text(encoding="utf-8"))
corr = load_audit_corrections(AUDIT)
convs = []
for idx, item in enumerate(raw):
    c = item.get("conversation", {})
    qas = []
    for qi, q in enumerate(item.get("qa", []) or []):
        cat = int(q.get("category")) if q.get("category") is not None else None
        if cat not in (1, 2, 3, 4):
            continue
        qid = q.get("question_id") or f"locomo_{idx}_qa{qi}"
        z = corr.get(str(qid))
        if z:
            ce = list(z["correct_evidence"]) if z.get("has_correct_evidence", False) else list(norm_evidence(q.get("evidence")))
        else:
            ce = list(norm_evidence(q.get("evidence")))
        qas.append({"question_id": str(qid), "category": cat,
                    "raw_evidence": norm_evidence(q.get("evidence")), "correct_evidence": ce})
    convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
print("raw_convs:", len(convs), "cat14_questions:", sum(len(c['qas']) for c in convs), "corrections:", len(corr))

# ---- load regen matrices, verify alignment ----
reps = []
for ci in range(10):
    d = pickle.load(open(REGEN / f"locomo_{ci}.pkl", "rb"))
    assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
    raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
    pkl_ids = [q["question_id"] for q in d["qas"]]
    assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
    assert d["QC"].shape[0] == len(d["qas"]), (ci, d["QC"].shape)
    reps.append(d)
print("alignment: OK (pkl qas order == raw Cat1-4 order for all 10 convs)")

# sanity: helper Q blocks bit-identical to hspec Q blocks
_p, _q = hspec(BLOCK_SEEDS[0], 2)
_p2, _q2 = hspec_blocks_for_perm(BLOCK_SEEDS[0], _p, 2)
assert all(np.array_equal(a, b) for a, b in zip(_q, _q2)), "Q-block identity broken"
print("qblock_identity: OK")

def q_fractional(dist_q, priorities, gold):
    tops = topks_by_hamming(dist_q, priorities)
    return mean_or_nan([retrieval_metrics(t, gold)["fractional"] for t in tops])

# per-question store: qid -> {cat, audit_gold_len, per-method values}
Q = {}
for ci, (c, r) in enumerate(zip(convs, reps)):
    id_to_row = r["id_to_row"]
    for qi, q in enumerate(c["qas"]):
        ag = evidence_rows(q["correct_evidence"], id_to_row)
        Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
valid_qids = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
print("valid_audit_questions:", len(valid_qids), "(frozen expects 1535)")

def aggregate(valdict):
    xs = [valdict[qid] for qid in valid_qids]
    return float(np.mean(xs))

def run_method(dist_all):
    """dist_all: dict ci -> dist (nQ, N). Returns {qid: value}."""
    out = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        N = r["C"].shape[0]
        dist = dist_all[ci]
        priorities = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(N) for t in range(N_NUISANCE)]
        for qi, q in enumerate(c["qas"]):
            out[q["question_id"]] = q_fractional(dist[qi], priorities, Q[q["question_id"]]["ag"])
    return out

def sign_dist(C, QC, subset=None):
    if subset is None:
        D = C >= 0; Qm = QC >= 0
    else:
        D = C[:, subset] >= 0; Qm = QC[:, subset] >= 0
    return np.count_nonzero(Qm[:, None, :] != D[None, :, :], axis=2).astype(np.int16)

# ---- GATE: native ----
native_dist = {ci: sign_dist(r["C"], r["QC"]) for ci, r in enumerate(reps)}
native_vals = run_method(native_dist)
native = aggregate(native_vals)
print(f"NATIVE fractional R@3 = {native!r}")
print(f"NATIVE anchor        = {NATIVE_ANCHOR!r}")
print(f"NATIVE diff          = {native - NATIVE_ANCHOR!r}")

# ---- Full-Haar96 ----
haar_seed_vals = {}
for seed in ROTATION_SEEDS:
    dd = {}
    for ci, r in enumerate(reps):
        perm, qs = hspec(seed, 96)
        Cr = happly(r["C"], perm, qs, 96); Qr = happly(r["QC"], perm, qs, 96)
        dd[ci] = sign_dist(Cr, Qr)
    haar_seed_vals[seed] = run_method(dd)
    print(f"HAAR seed {seed}: {aggregate(haar_seed_vals[seed])!r}")
haar_mean_vals = {qid: float(np.mean([haar_seed_vals[s][qid] for s in ROTATION_SEEDS])) for qid in Q}
haar_mean = aggregate(haar_mean_vals)
print(f"HAAR mean = {haar_mean!r} anchor = {HAAR_ANCHOR!r} diff = {haar_mean - HAAR_ANCHOR!r}")

# ---- ARMS: bit-budget selection (per-archive variance) ----
arm_vals = {}   # label -> {qid: value}
arm_meta = {}   # label -> dict
for k in KS:
    subsets = {}
    subsets["TOP"] = None  # per-archive computed below
    for s in range(3):
        subsets[f"RANDOM_s{s}"] = np.sort(np.random.default_rng(12000 + s).choice(96, k, replace=False))
    # BOT/SPREAD/TOP are per-archive (variance-dependent)
    per_seed_labels = [f"RANDOM_s{s}" for s in range(3)]
    # precompute per-archive variance subsets
    arch_sub = {}
    for ci, r in enumerate(reps):
        var = r["C"].var(axis=0)
        order = np.argsort(var)  # ascending; ties broken by index (stable, deterministic)
        arch_sub[ci] = {
            "TOP": np.sort(order[96 - k:]),
            "BOT": np.sort(order[:k]),
            "SPREAD": np.sort(order[::-1][::2][:k]),
        }
    eff_spread = len(arch_sub[0]["SPREAD"])
    for label in ["TOP"] + per_seed_labels + ["BOT", "SPREAD"]:
        if label.startswith("RANDOM"):
            dd = {ci: sign_dist(r["C"], r["QC"], subsets[label]) for ci, r in enumerate(reps)}
        else:
            dd = {ci: sign_dist(r["C"], r["QC"], arch_sub[ci][label]) for ci, r in enumerate(reps)}
        key = f"{label}_k{k}"
        arm_vals[key] = run_method(dd)
        agg = aggregate(arm_vals[key])
        eff = eff_spread if label == "SPREAD" else k
        arm_meta[key] = {"family": label.split("_")[0], "k": k, "eff_k": eff, "seeds": None}
        print(f"ARM {key} (eff_k={eff}): {agg!r} gap_pp={(agg - native) * 100:+.6f}", flush=True)

# ---- ARMS: block-2 pairing contrast ----
for scheme in ["RANDPAIR", "MATCHED", "ANTIMATCHED"]:
    for seed in BLOCK_SEEDS:
        dd = {}
        for ci, r in enumerate(reps):
            var = r["C"].var(axis=0)
            if scheme == "RANDPAIR":
                perm, qs = hspec(seed, 2)
            else:
                desc = np.argsort(var)[::-1]
                if scheme == "MATCHED":
                    pairing = desc
                else:
                    pairing = np.empty(96, dtype=int)
                    pairing[0::2] = desc[:48]
                    pairing[1::2] = desc[::-1][:48]
                perm, qs = hspec_blocks_for_perm(seed, pairing, 2)
            Cr = happly(r["C"], perm, qs, 2); Qr = happly(r["QC"], perm, qs, 2)
            dd[ci] = sign_dist(Cr, Qr)
        key = f"{scheme}_seed{seed}"
        arm_vals[key] = run_method(dd)
        agg = aggregate(arm_vals[key])
        arm_meta[key] = {"family": scheme, "k": 96, "eff_k": 96, "seeds": seed}
        print(f"ARM {key}: {agg!r} gap_pp={(agg - native) * 100:+.6f}", flush=True)
for scheme in ["RANDPAIR", "MATCHED", "ANTIMATCHED"]:
    m = float(np.mean([aggregate(arm_vals[f"{scheme}_seed{s}"]) for s in BLOCK_SEEDS]))
    print(f"ARM {scheme}_mean: {m!r} gap_pp={(m - native) * 100:+.6f}", flush=True)

# ---- per-category native vs best ----
agg_all = {k: aggregate(v) for k, v in arm_vals.items()}
agg_all["NATIVE"] = native
agg_all["HAAR96_MEAN"] = haar_mean
best_arm = max((k for k in agg_all if k != "NATIVE"), key=lambda k: agg_all[k])
print("BEST_ARM:", best_arm, repr(agg_all[best_arm]))
cat_rows = []
for cat in [1, 2, 3, 4]:
    qids = [qid for qid in valid_qids if Q[qid]["cat"] == cat]
    n = float(np.mean([native_vals[qid] for qid in qids]))
    b = float(np.mean([arm_vals[best_arm][qid] if best_arm in arm_vals else haar_mean_vals[qid] for qid in qids]))
    h = float(np.mean([haar_mean_vals[qid] for qid in qids]))
    cat_rows.append({"cat": cat, "n": len(qids), "native": n, best_arm: b, "HAAR96_MEAN": h})
    print(f"CAT{cat} n={len(qids)} native={n!r} {best_arm}={b!r} haar_mean={h!r}")

# ---- details.json ----
details = {
    "protocol": {
        "distance": "hamming on sign bits (C>=0, QC>=0), K=3",
        "priorities": "stable_archive_seed(ci,t)+99, default_rng().random(N), 20 nuisance trials",
        "aggregation": "per-question mean over 20 trials, then mean over audit-valid questions",
        "inclusion": "Cat1-4 (1540 q), audit corrections applied (156, explicit-empty preserved)",
        "valid_audit_questions": len(valid_qids),
        "note": "verbatim mirror of v52_t4d_locomo_frozen_cross_benchmark.py; representations reused from regen pkls (no re-fit)",
    },
    "gate": {
        "native": native, "native_anchor": NATIVE_ANCHOR, "native_diff": native - NATIVE_ANCHOR,
        "haar_mean": haar_mean, "haar_anchor": HAAR_ANCHOR, "haar_diff": haar_mean - HAAR_ANCHOR,
        "haar_seeds": {str(s): aggregate(haar_seed_vals[s]) for s in ROTATION_SEEDS},
    },
    "arms": {k: {"fractional_R3": agg_all[k], "gap_pp_vs_native": (agg_all[k] - native) * 100.0,
                 **arm_meta.get(k, {})} for k in arm_vals},
    "arm_per_seed": {},
    "block_means": {},
    "per_category": cat_rows,
    "best_arm": best_arm,
}
for k in KS:
    for s in range(3):
        details["arm_per_seed"][f"RANDOM_k{k}_s{s}"] = aggregate(arm_vals[f"RANDOM_s{s}_k{k}"])
for scheme in ["RANDPAIR", "MATCHED", "ANTIMATCHED"]:
    details["arm_per_seed"].update({f"{scheme}_seed{s}": aggregate(arm_vals[f"{scheme}_seed{s}"]) for s in BLOCK_SEEDS})
    details["block_means"][scheme] = float(np.mean([aggregate(arm_vals[f"{scheme}_seed{s}"]) for s in BLOCK_SEEDS]))
OUT.write_text(json.dumps(details, indent=2, sort_keys=True), encoding="utf-8")
print("DETAILS_WRITTEN", OUT)
print("FINAL_JSON_BEGIN")
print(json.dumps(details, sort_keys=True))
print("FINAL_JSON_END")
