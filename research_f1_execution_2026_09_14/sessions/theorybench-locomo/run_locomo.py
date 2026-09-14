#!/usr/bin/env python3
"""LoCoMo Model-H proxy-transfer runner (exploratory, isolated outputs only).
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Phases: gate | intervene | bootstrap. Adapters copied from frozen producers
(harness/deney1_loco.py, race_2026-09-13/rb2/race_sign.py, audit taskC_real_locomo.py)
with BASE read-only; all outputs go to OUTDIR (this workspace).
"""
import hashlib, json, os, pickle, re, sys, time
from pathlib import Path
import numpy as np

SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work")
RAW = SRC / "drive" / "locomo10.json"
AUDIT = SRC / "drive" / "audit_layer"
REGEN = SRC / "regen" / "locomo"
PERQ = SRC / "audit_2026-09-13" / "audit1_cont" / "taskC_LoCoMo_perq.json"
NPZ = SRC / "pilots" / "axis_attack_2026-09-12" / "round3" / "deney1_loco_peraxis.npz"
OUTDIR = Path(__file__).resolve().parent
CKPT = OUTDIR / "ckpt"

ANCHOR = 0.23654714666441054
TOPK = 3
NT = 20
TGRID = [0.25, 0.5, 1.0, 2.0, 4.0]
GROUPS = ["LOW48", "HIGH48", "FULL96"]

def stable_archive_seed(ci, t):
    return 5_100_000 + ci * 100_000 + t * 100

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
                "has_correct_evidence": "correct_evidence" in r,
                "correct_evidence": norm_evidence(r.get("correct_evidence")),
            }
    return corrections

def evidence_rows(ids, id_to_row):
    out = []
    for x in ids:
        if x in id_to_row:
            out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))

def exact_exp(dvec, gold, k=TOPK):
    """MATH-1 tie law: mean over golds of P(gold in top-k | uniform tie priorities)."""
    d = np.asarray(dvec)
    tot = 0.0
    for gg in np.asarray(gold).ravel():
        dg = d[int(gg)]
        s = int(np.count_nonzero(d < dg))
        t = int(np.count_nonzero(d == dg))
        if s >= k:
            p = 0.0
        elif s + t <= k:
            p = 1.0
        else:
            p = (k - s) / t
        tot += p
    return tot / len(np.asarray(gold).ravel())

def mc_fr(dvec, gold, pris, k=TOPK):
    """Frozen 20-trial scheme: lexsort((priority, distance)) top-k fractional recall."""
    d = np.asarray(dvec)
    gset = set(map(int, np.asarray(gold).ravel()))
    ng = len(gset)
    tot = 0.0
    for p in pris:
        order = np.lexsort((np.asarray(p), d))
        tot += len(set(map(int, order[:k])) & gset) / ng
    return tot / len(pris)

def cosine_dists(C, q):
    """Negative-cosine distances of docs C (N,96) to query q (96,). Exact float64."""
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    cn = np.sqrt((C ** 2).sum(axis=1))
    qn = float(np.sqrt((q ** 2).sum()))
    if qn == 0.0:
        return np.zeros(C.shape[0])
    denom = cn * qn
    sim = np.where(denom == 0.0, 0.0, (C @ q) / np.where(denom == 0.0, 1.0, denom))
    return -sim

def load_all():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    corr = load_audit_corrections(AUDIT)
    convs = []
    ncat14 = 0
    for idx, item in enumerate(raw):
        qas = []
        for qi, q in enumerate(item.get("qa", []) or []):
            cat = int(q.get("category")) if q.get("category") is not None else None
            if cat not in (1, 2, 3, 4):
                continue
            qid = q.get("question_id") or f"locomo_{idx}_qa{qi}"
            z = corr.get(str(qid))
            if z:
                ce = list(z["correct_evidence"]) if z.get("has_correct_evidence", False) \
                    else list(norm_evidence(q.get("evidence")))
            else:
                ce = list(norm_evidence(q.get("evidence")))
            qas.append({"question_id": str(qid), "category": cat, "correct_evidence": ce})
        ncat14 += len(qas)
        convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
    reps = []
    for ci in range(10):
        d = pickle.load(open(REGEN / f"locomo_{ci}.pkl", "rb"))
        assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
        raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
        pkl_ids = [q["question_id"] for q in d["qas"]]
        assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
        assert np.asarray(d["QC"]).shape[0] == len(d["qas"]), (ci,)
        reps.append(d)
    Q = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        id_to_row = r["id_to_row"]
        for qi, q in enumerate(c["qas"]):
            ag = evidence_rows(q["correct_evidence"], id_to_row)
            Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
    valid = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
    return convs, reps, Q, valid, ncat14


def phase_gate():
    t0 = time.time()
    convs, reps, Q, valid, ncat14 = load_all()
    perq = json.loads(PERQ.read_text(encoding="utf-8"))
    z = np.load(NPZ)
    npz_qids = [str(q) for q in z["qids"]]
    npz_nat = np.asarray(z["native"], dtype=float)
    perq_exp = dict(zip(perq["qids"], perq["per_arm"]["NATIVE96"]["exp"]))
    perq_mc = dict(zip(perq["qids"], perq["per_arm"]["NATIVE96"]["fr_off"]))
    assert ncat14 == 1540, ncat14
    assert len(valid) == 1535, len(valid)
    assert valid == [str(q) for q in perq["qids"]], "qid order mismatch vs perq"
    assert valid == npz_qids, "qid order mismatch vs npz"
    gold_counts = {}
    for qid in valid:
        gold_counts[len(Q[qid]["ag"])] = gold_counts.get(len(Q[qid]["ag"]), 0) + 1
    s_mc, s_exp, f_mc, f_exp = [], [], [], []
    min_cnorm = np.inf
    min_qnorm = np.inf
    for ci, r in enumerate(reps):
        C = np.asarray(r["C"], dtype=np.float64)
        QC = np.asarray(r["QC"], dtype=np.float64)
        min_cnorm = min(min_cnorm, float(np.sqrt((C ** 2).sum(axis=1)).min()))
        min_qnorm = min(min_qnorm, float(np.sqrt((QC ** 2).sum(axis=1)).min()))
        Cb = (C >= 0)
        Qb = (QC >= 0)
        D = np.count_nonzero(Qb[:, None, :] != Cb[None, :, :], axis=2).astype(np.int16)
        n = C.shape[0]
        pris = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(n)
                for t in range(NT)]
        for qi, q in enumerate(convs[ci]["qas"]):
            qid = q["question_id"]
            if not Q[qid]["ag"]:
                continue
            ag = Q[qid]["ag"]
            dv = D[qi]
            s_mc.append(mc_fr(dv, ag, pris))
            s_exp.append(exact_exp(dv, ag))
            fd = cosine_dists(C, QC[qi])
            f_mc.append(mc_fr(fd, ag, pris))
            f_exp.append(exact_exp(fd, ag))
    s_mc = np.array(s_mc)
    s_exp = np.array(s_exp)
    f_mc = np.array(f_mc)
    f_exp = np.array(f_exp)
    ref_mc = npz_nat
    ref_exp = np.array([perq_exp[q] for q in valid])
    ref_mco = np.array([perq_mc[q] for q in valid])
    checks = {}
    checks["counts_cat14"] = int(ncat14)
    checks["counts_valid"] = int(len(valid))
    checks["counts_excluded"] = int(ncat14 - len(valid))
    checks["gold_count_dist"] = {str(k): int(v) for k, v in sorted(gold_counts.items())}
    checks["sign_mc_mean"] = float(s_mc.mean())
    checks["anchor_diff"] = float(s_mc.mean() - ANCHOR)
    checks["gate_anchor_1e12"] = bool(abs(s_mc.mean() - ANCHOR) < 1e-12)
    checks["maxabs_mc_vs_npz"] = float(np.max(np.abs(s_mc - ref_mc)))
    checks["gate_npz_1e12"] = bool(np.max(np.abs(s_mc - ref_mc)) < 1e-12)
    checks["maxabs_exp_vs_perq"] = float(np.max(np.abs(s_exp - ref_exp)))
    checks["gate_perq_1e12"] = bool(np.max(np.abs(s_exp - ref_exp)) < 1e-12)
    checks["maxabs_mc_vs_perq_mc"] = float(np.max(np.abs(s_mc - ref_mco)))
    checks["float_exp_mean"] = float(f_exp.mean())
    checks["float_mc_mean"] = float(f_mc.mean())
    checks["float_mc_minus_exp_mean"] = float((f_mc - f_exp).mean())
    checks["float_maxabs_mc_vs_exp"] = float(np.max(np.abs(f_mc - f_exp)))
    checks["sign_exp_mean"] = float(s_exp.mean())
    checks["min_cnorm"] = float(min_cnorm)
    checks["min_qnorm"] = float(min_qnorm)
    checks["qid_match_perq"] = True
    checks["qid_match_npz"] = True
    ok = checks["gate_anchor_1e12"] and checks["gate_npz_1e12"] and checks["gate_perq_1e12"]
    checks["GATE_PASS"] = bool(ok)
    checks["elapsed_s"] = round(time.time() - t0, 1)
    (OUTDIR / "gate.json").write_text(json.dumps(checks, indent=1), encoding="utf-8")
    np.savez_compressed(OUTDIR / "gate_native_arrays.npz", qids=np.array(valid),
                        sign_mc=s_mc, sign_exp=s_exp, float_mc=f_mc, float_exp=f_exp)
    print("GATE " + json.dumps({k: checks[k] for k in
          ["counts_cat14", "counts_valid", "counts_excluded", "sign_mc_mean",
           "anchor_diff", "gate_anchor_1e12", "maxabs_mc_vs_npz", "gate_npz_1e12",
           "maxabs_exp_vs_perq", "gate_perq_1e12", "maxabs_mc_vs_perq_mc",
           "float_exp_mean", "float_mc_mean", "sign_exp_mean", "GATE_PASS"]}, indent=1),
          flush=True)
    if not ok:
        print("GATE FAILED — aborting before interventions", flush=True)
        sys.exit(3)
    print("GATE PASS", flush=True)


def q_groups(q):
    """Gold-free magnitude order: indices by (abs(q_j), j) ascending."""
    q = np.asarray(q, dtype=np.float64)
    order = np.lexsort((np.arange(96), np.abs(q)))
    return order[:48], order[48:]


def phase_intervene():
    t0 = time.time()
    CKPT.mkdir(parents=True, exist_ok=True)
    convs, reps, Q, valid, ncat14 = load_all()
    assert ncat14 == 1540 and len(valid) == 1535
    g = np.load(OUTDIR / "gate_native_arrays.npz")
    gate_lu = {str(q): i for i, q in enumerate(g["qids"])}
    all_rows = []
    for ci, r in enumerate(reps):
        ck = CKPT / f"ci_{ci}.json"
        if ck.exists():
            rows = json.loads(ck.read_text(encoding="utf-8"))
            print(f"ci {ci}: loaded {len(rows)} checkpointed rows", flush=True)
            all_rows.extend(rows)
            continue
        C = np.asarray(r["C"], dtype=np.float64)
        QC = np.asarray(r["QC"], dtype=np.float64)
        n = C.shape[0]
        pris = [np.random.default_rng(stable_archive_seed(ci, t) + 99).random(n)
                for t in range(NT)]
        Cb = (C >= 0)
        Qb = (QC >= 0)
        Dnat = np.count_nonzero(Qb[:, None, :] != Cb[None, :, :], axis=2).astype(np.int16)
        rows = []
        for qi, q in enumerate(convs[ci]["qas"]):
            qid = q["question_id"]
            if not Q[qid]["ag"]:
                continue
            ag = Q[qid]["ag"]
            qv = QC[qi]
            lo, hi = q_groups(qv)
            q2 = float((qv ** 2).sum())
            qconc = float((qv ** 4).sum() / (q2 ** 2))
            rms_lo = float(np.sqrt((C[:, lo] ** 2).mean()))
            rms_hi = float(np.sqrt((C[:, hi] ** 2).mean()))
            gi = gate_lu[qid]
            nat = {"s_exp": float(g["sign_exp"][gi]), "s_mc": float(g["sign_mc"][gi]),
                   "f_exp": float(g["float_exp"][gi]), "f_mc": float(g["float_mc"][gi])}
            cfg = {}
            sign_maxdiff = 0.0
            for gname, G in (("LOW48", lo), ("HIGH48", hi), ("FULL96", np.arange(96))):
                G = np.asarray(G)
                trows = {}
                for t in TGRID:
                    s = np.ones(96)
                    s[G] = t
                    Cs = C * s[None, :]
                    qs = qv * s
                    Ds = np.count_nonzero((qs[None, :] >= 0) != (Cs >= 0), axis=1
                                          ).astype(np.int16)
                    sign_maxdiff = max(sign_maxdiff, float(np.abs(Ds - Dnat[qi]).max()))
                    se = exact_exp(Ds, ag)
                    sm = mc_fr(Ds, ag, pris)
                    fd = cosine_dists(Cs, qs)
                    fe = exact_exp(fd, ag)
                    fm = mc_fr(fd, ag, pris)
                    trows[str(t)] = {"s_exp": se, "s_mc": sm, "f_exp": fe, "f_mc": fm,
                                     "d_exp": se - fe, "d_mc": sm - fm}
                cfg[gname] = trows
            row = {"qid": qid, "ci": ci, "qi": qi, "cat": Q[qid]["cat"],
                   "gold_count": len(ag), "N_docs": int(n),
                   "low48": [int(i) for i in lo], "qconc": qconc,
                   "doc_rms_low": rms_lo, "doc_rms_high": rms_hi,
                   "native": nat, "cfg": cfg, "sign_inv_maxdiff": sign_maxdiff}
            rows.append(row)
        ck.write_text(json.dumps(rows), encoding="utf-8")
        print(f"ci {ci}: computed {len(rows)} rows "
              f"({time.time()-t0:.0f}s elapsed)", flush=True)
        all_rows.extend(rows)
    with open(OUTDIR / "per_query.jsonl", "w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")
    print(f"INTERVENE done: {len(all_rows)} rows -> per_query.jsonl", flush=True)
    assert len(all_rows) == 1535, len(all_rows)


def phase_bootstrap():
    rows = [json.loads(l) for l in
            (OUTDIR / "per_query.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1535, len(rows)
    by_ci = {}
    for r in rows:
        by_ci.setdefault(r["ci"], []).append(r)
    assert len(by_ci) == 10
    rng = np.random.default_rng(20260913)
    out = {"n_qa": 1535, "n_clusters": 10, "B": 2000, "seed": 20260913,
           "curves": {}, "contrasts": {}, "decreasing_frac": {},
           "invariance": {}, "t1_identity": {}}
    for gname in GROUPS:
        for key in ("s_exp", "s_mc", "f_exp", "f_mc", "d_exp", "d_mc"):
            out["curves"][f"{gname}.{key}"] = {
                str(t): float(np.mean([r["cfg"][gname][str(t)][key] for r in rows]))
                for t in TGRID}
    for gname in GROUPS:
        for key in ("d_exp", "d_mc"):
            vals = np.array([r["cfg"][gname]["4.0"][key] - r["cfg"][gname]["0.25"][key]
                             for r in rows])
            ci_lists = [by_ci[c] for c in sorted(by_ci)]
            boots = np.empty(2000)
            for b in range(2000):
                pick = rng.integers(0, 10, 10)
                samp = [q for c in pick for q in ci_lists[c]]
                boots[b] = np.mean([q["cfg"][gname]["4.0"][key] -
                                    q["cfg"][gname]["0.25"][key] for q in samp])
            lo, hi = np.percentile(boots, [2.5, 97.5])
            out["contrasts"][f"{gname}.{key}"] = {
                "mean": float(vals.mean()), "ci95": [float(lo), float(hi)],
                "excludes_zero_positive": bool(lo > 0)}
    for gname in GROUPS:
        for key in ("d_exp", "d_mc"):
            ndec = 0
            for r in rows:
                ds = [r["cfg"][gname][str(t)][key] for t in TGRID]
                if any(b < a for a, b in zip(ds, ds[1:])):
                    ndec += 1
            out["decreasing_frac"][f"{gname}.{key}"] = {
                "n": int(ndec), "frac": float(ndec / len(rows))}
    se = np.array([r["sign_inv_maxdiff"] for r in rows])
    out["invariance"]["sign_maxdiff_over_all_t"] = float(se.max())
    for key in ("f_exp", "f_mc", "s_exp", "s_mc"):
        dev = np.array([max(abs(r["cfg"]["FULL96"][str(t)][key] - r["native"][key])
                             for t in TGRID) for r in rows])
        out["invariance"][f"FULL96.{key}.maxabs"] = float(dev.max())
        out["invariance"][f"FULL96.{key}.mean"] = float(
            np.mean([r["cfg"]["FULL96"]["1.0"][key] - r["native"][key] for r in rows]))
    def nat_delta(r, key):
        if key == "d_exp":
            return r["native"]["s_exp"] - r["native"]["f_exp"]
        if key == "d_mc":
            return r["native"]["s_mc"] - r["native"]["f_mc"]
        return r["native"][key]
    for gname in GROUPS:
        for key in ("s_exp", "s_mc", "f_exp", "f_mc", "d_exp", "d_mc"):
            dev = np.array([r["cfg"][gname]["1.0"][key] - nat_delta(r, key)
                            for r in rows])
            out["t1_identity"][f"{gname}.{key}.maxabs"] = float(np.abs(dev).max())
    out["float_baseline"] = {
        "exp_mean": float(np.mean([r["native"]["f_exp"] for r in rows])),
        "mc_mean": float(np.mean([r["native"]["f_mc"] for r in rows]))}
    out["sign_baseline"] = {
        "exp_mean": float(np.mean([r["native"]["s_exp"] for r in rows])),
        "mc_mean": float(np.mean([r["native"]["s_mc"] for r in rows]))}
    (OUTDIR / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("BOOTSTRAP " + json.dumps({
        "contrasts": out["contrasts"], "decreasing_frac": out["decreasing_frac"],
        "invariance": out["invariance"],
        "float_baseline": out["float_baseline"]}, indent=1), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "gate"
    if which == "gate":
        phase_gate()
    elif which == "intervene":
        phase_intervene()
    elif which == "bootstrap":
        phase_bootstrap()
    else:
        sys.exit(f"unknown phase {which}")
