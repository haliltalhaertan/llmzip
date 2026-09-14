#!/usr/bin/env python3
"""D4: fresh-Q confirmatory check of mixing-disparity ordering. Mirrors r2c_replicate.py LoCoMo machinery EXACTLY."""
import json, re, pickle
from pathlib import Path
import numpy as np

RAW = Path("/mnt/c/Users/MDP/dev/llmzip-work/drive/locomo10.json")
AUDIT = Path("/mnt/c/Users/MDP/dev/llmzip-work/drive/audit_layer")
REGEN = Path("/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo")

NATIVE_ANCHOR = 0.23654714666441054
MATCHED_ORIG_EXPECT = {43001: 0.23565226250405402, 43002: 0.23022749129263786, 43003: 0.24242457144737273}
TOPK = 3
N_NUISANCE = 20
ORIG_SEEDS = [43001, 43002, 43003]
FRESH_SEEDS = [43004, 43005]
ALL_SEEDS = ORIG_SEEDS + FRESH_SEEDS

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
    r = np.random.default_rng(seed)
    _ = r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return np.asarray(perm), qs

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

reps = []
for ci in range(10):
    d = pickle.load(open(REGEN / f"locomo_{ci}.pkl", "rb"))
    assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
    raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
    pkl_ids = [q["question_id"] for q in d["qas"]]
    assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
    assert d["QC"].shape[0] == len(d["qas"]), (ci, d["QC"].shape)
    reps.append(d)
print("alignment: OK")

_p, _q = hspec(ORIG_SEEDS[0], 2)
_p2, _q2 = hspec_blocks_for_perm(ORIG_SEEDS[0], _p, 2)
assert all(np.array_equal(a, b) for a, b in zip(_q, _q2)), "Q-block identity broken"
print("qblock_identity: OK")

def q_fractional(dist_q, priorities, gold):
    tops = topks_by_hamming(dist_q, priorities)
    return mean_or_nan([retrieval_metrics(t, gold)["fractional"] for t in tops])

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

native_dist = {ci: sign_dist(r["C"], r["QC"]) for ci, r in enumerate(reps)}
native_vals = run_method(native_dist)
native = aggregate(native_vals)
print(f"NATIVE fractional R@3 = {native!r}")
print(f"NATIVE anchor        = {NATIVE_ANCHOR!r}")
print(f"NATIVE diff          = {native - NATIVE_ANCHOR!r}")
print("NATIVE_GATE_PASS" if abs(native - NATIVE_ANCHOR) <= 1e-12 else "NATIVE_GATE_FAIL")

arm_vals = {}
for scheme in ["RANDPAIR", "MATCHED", "ANTIMATCHED"]:
    for seed in ALL_SEEDS:
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
        print(f"ARM {key}: {agg!r} gap_pp={(agg - native) * 100:+.6f}", flush=True)

print("---- replication-of-machinery check (MATCHED orig seeds) ----")
rep_ok = True
for s in ORIG_SEEDS:
    got = aggregate(arm_vals[f"MATCHED_seed{s}"])
    exp = MATCHED_ORIG_EXPECT[s]
    d = got - exp
    ok = abs(d) <= 1e-12
    rep_ok = rep_ok and ok
    print(f"MATCHED_seed{s}: got={got!r} exp={exp!r} diff={d!r} {'PASS' if ok else 'FAIL'}")
print("REPLICATION_PASS" if rep_ok else "REPLICATION_FAIL")

for scheme in ["RANDPAIR", "MATCHED", "ANTIMATCHED"]:
    m_orig = float(np.mean([aggregate(arm_vals[f"{scheme}_seed{s}"]) for s in ORIG_SEEDS]))
    m_fresh = float(np.mean([aggregate(arm_vals[f"{scheme}_seed{s}"]) for s in FRESH_SEEDS]))
    m_all = float(np.mean([aggregate(arm_vals[f"{scheme}_seed{s}"]) for s in ALL_SEEDS]))
    print(f"{scheme} orig_mean={m_orig!r} gap_pp={(m_orig-native)*100:+.6f} | fresh_mean={m_fresh!r} gap_pp={(m_fresh-native)*100:+.6f} | all5_mean={m_all!r}")

# strict separation on fresh
mf = {s: aggregate(arm_vals[f"MATCHED_seed{s}"]) for s in FRESH_SEEDS}
rf = {s: aggregate(arm_vals[f"RANDPAIR_seed{s}"]) for s in FRESH_SEEDS}
af = {s: aggregate(arm_vals[f"ANTIMATCHED_seed{s}"]) for s in FRESH_SEEDS}
mo = {s: aggregate(arm_vals[f"MATCHED_seed{s}"]) for s in ORIG_SEEDS}
ro = {s: aggregate(arm_vals[f"RANDPAIR_seed{s}"]) for s in ORIG_SEEDS}
ao = {s: aggregate(arm_vals[f"ANTIMATCHED_seed{s}"]) for s in ORIG_SEEDS}
c1 = min(mf.values()) > max(rf.values())
c2 = min(rf.values()) > max(af.values())
c3 = min(mf.values()) > max(af.values())
print(f"STRICT fresh: min(MATCHED)={min(mf.values())!r} max(RANDPAIR)={max(rf.values())!r} min(RANDPAIR)={min(rf.values())!r} max(ANTI)={max(af.values())!r}")
print(f"  min(MATCHED_fresh) > max(RANDPAIR_fresh): {c1}")
print(f"  min(RANDPAIR_fresh) > max(ANTIMATCHED_fresh): {c2}")
print(f"  min(MATCHED_fresh) > max(ANTIMATCHED_fresh): {c3}")

details = {
    "native": native, "native_anchor": NATIVE_ANCHOR, "native_diff": native - NATIVE_ANCHOR,
    "native_gate_pass": bool(abs(native - NATIVE_ANCHOR) <= 1e-12),
    "arm_per_seed": {k: aggregate(v) for k, v in arm_vals.items()},
    "arm_gap_pp": {k: (aggregate(v) - native) * 100.0 for k, v in arm_vals.items()},
    "replication": {str(s): {"got": aggregate(arm_vals[f"MATCHED_seed{s}"]), "expected": MATCHED_ORIG_EXPECT[s],
                    "diff": aggregate(arm_vals[f"MATCHED_seed{s}"]) - MATCHED_ORIG_EXPECT[s]} for s in ORIG_SEEDS},
    "replication_pass": bool(rep_ok),
    "valid_audit_questions": len(valid_qids),
    "fresh_strict": {"min_matched_gt_max_randpair": bool(c1), "min_randpair_gt_max_anti": bool(c2),
                     "min_matched_gt_max_anti": bool(c3)},
}
Path("/tmp/d4/d4_details.json").write_text(json.dumps(details, indent=2, sort_keys=True), encoding="utf-8")
print("DETAILS_WRITTEN /tmp/d4/d4_details.json")
print("FINAL_JSON_BEGIN")
print(json.dumps(details, sort_keys=True))
print("FINAL_JSON_END")
