# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Independent LoCoMo baseline-provenance recompute (diagnostic only, NOT a review).

Reads (read-only): regen/locomo_{ci}.pkl (original C/QC cache), drive/locomo10.json,
drive/audit_layer/errors_conv_*.json, pilots/.../deney1_loco_peraxis.npz,
audit1_cont/taskC_LoCoMo_perq.json, theory_benchmark_test_v1/locomo/gate_native_arrays.npz.
Writes (this workspace only): results.json (via --write) + stdout.
Env contract: threads=1, PYTHONDONTWRITEBYTECODE=1; run with ml-python -B.
"""
import sys, os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import hashlib, json, pickle, re
from fractions import Fraction
from pathlib import Path

import numpy as np

W = Path("/mnt/c/Users/MDP/dev/llmzip-work")
T = W / "theory_benchmark_test_v1" / "locomo"
ANCHOR = 0.23654714666441054
K = 3
NT = 20

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def norm_ev(ids):
    if ids is None:
        return []
    if isinstance(ids, str):
        m = re.findall(r"D\d+:\d+", ids)
        return m if m else [ids]
    out = []
    for z in ids:
        if isinstance(z, str):
            m = re.findall(r"D\d+:\d+", z)
            out.extend(m if m else [z])
        elif isinstance(z, dict):
            d = z.get("dia_id") or z.get("id")
            if d:
                out.append(str(d))
    seen, res = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res

def frac_recall_exact(dvec, gold, k=K):
    d = list(dvec)
    g = list(map(int, np.ravel(gold)))
    tot = 0.0
    for gg in g:
        dg = d[int(gg)]
        s = sum(1 for v in d if v < dg)
        t = sum(1 for v in d if v == dg)
        if s >= k:
            p = 0.0
        elif s + t <= k:
            p = 1.0
        else:
            p = (k - s) / t
        tot += p
    return tot / len(g)

def frac_recall_mc(dvec, gold, pris, k=K):
    d = np.asarray(dvec)
    gs = set(map(int, np.ravel(gold)))
    tot = 0.0
    for p in pris:
        order = np.lexsort((np.asarray(p), d))
        tot += len(set(map(int, order[:k])) & gs) / len(gs)
    return tot / len(pris)

def cosine_dist_unit(C, q):
    """Independent formulation: pre-normalize to unit vectors, then dot."""
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    cn = np.sqrt((C * C).sum(axis=1))
    qn = float(np.sqrt((q * q).sum()))
    if qn == 0.0:
        return np.zeros(C.shape[0])
    U = np.where(cn[:, None] == 0.0, 0.0, C / np.where(cn[:, None] == 0.0, 1.0, cn[:, None]))
    v = q / qn
    return -(U @ v)

def main():
    read_hashes = {}
    def track(p):
        p = Path(p)
        read_hashes[str(p)] = sha256(p)
        return p
    raw = json.loads(track(W / "drive" / "locomo10.json").read_text(encoding="utf-8"))
    corr = {}
    for f in sorted((W / "drive" / "audit_layer").glob("errors_conv_*.json")):
        track(f)
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            qid = r.get("question_id")
            if qid:
                corr[str(qid)] = norm_ev(r.get("correct_evidence")) if "correct_evidence" in r \
                    else norm_ev(None) if False else None
    # rebuild QA table: cat1-4 only, evidence ids -> row idx via pkl id_to_row
    convs, reps = [], []
    ncat14 = 0
    for ci in range(10):
        pk = track(W / "regen" / "locomo" / f"locomo_{ci}.pkl")
        d = pickle.load(open(pk, "rb"))
        reps.append(d)
        item = raw[ci]
        assert d["conv_id"] == f"locomo_{ci}"
        id2r = d["id_to_row"]
        qas = []
        for qi, q in enumerate(item.get("qa", []) or []):
            if q.get("category") not in (1, 2, 3, 4):
                continue
            qid = str(q.get("question_id") or f"locomo_{ci}_qa{qi}")
            ce = corr.get(qid)
            ev = ce if ce is not None else norm_ev(q.get("evidence"))
            ag = []
            for x in ev:
                if x in id2r and int(id2r[x]) not in ag:
                    ag.append(int(id2r[x]))
            qas.append({"qid": qid, "ci": ci, "qi": len(qas), "ag": ag})
        assert [q["qid"] for q in qas] == [q["question_id"] for q in d["qas"]], \
            f"order mismatch conv {ci}"
        ncat14 += len(qas)
        convs.append(qas)
    # flatten preserving order
    valid = []
    for ci, ql in enumerate(convs):
        for q in ql:
            if q["ag"]:
                valid.append(q)
    n_valid = len(valid)
    # Hamming gate (stored convention sign(x)=+1 iff x>=0) + fresh centered cosine
    s_mc, s_exp, f_mc, f_exp = [], [], [], []
    per_archive = {}
    for ci in range(10):
        C = np.asarray(reps[ci]["C"], dtype=np.float64)
        QC = np.asarray(reps[ci]["QC"], dtype=np.float64)
        Cb = C >= 0
        Qb = QC >= 0
        D = np.count_nonzero(Qb[:, None, :] != Cb[None, :, :], axis=2)
        n = C.shape[0]
        pris = [np.random.default_rng(5_100_000 + ci * 100_000 + t * 100 + 99).random(n)
                for t in range(NT)]
        for q in convs[ci]:
            if not q["ag"]:
                continue
            dv = D[q["qi"]]
            s_mc.append(frac_recall_mc(dv, q["ag"], pris))
            s_exp.append(frac_recall_exact(dv, q["ag"]))
            fd = cosine_dist_unit(C, QC[q["qi"]])
            f_mc.append(frac_recall_mc(fd, q["ag"], pris))
            f_exp.append(frac_recall_exact(fd, q["ag"]))
            per_archive.setdefault(ci, []).append((s_mc[-1], f_mc[-1], len(q["ag"])))
    s_mc = np.array(s_mc)
    s_exp = np.array(s_exp)
    f_mc = np.array(f_mc)
    f_exp = np.array(f_exp)
    # compare vs worker gate arrays + historical anchors
    gpath = track(T / "gate_native_arrays.npz")
    g = np.load(gpath)
    w_smc = np.asarray(g["sign_mc"], float)
    w_smc_mean = float(w_smc.mean())
    npz = np.load(track(W / "pilots" / "axis_attack_2026-09-12" / "round3" / "deney1_loco_peraxis.npz"))
    perq = json.loads(track(W / "audit_2026-09-13" / "audit1_cont" / "taskC_LoCoMo_perq.json").read_text())
    res = {
        "ncat14": ncat14,
        "n_valid": n_valid,
        "n_excluded": ncat14 - n_valid,
        "sign_mc_mean": float(s_mc.mean()),
        "sign_exp_mean": float(s_exp.mean()),
        "float_mc_mean": float(f_mc.mean()),
        "float_exp_mean": float(f_exp.mean()),
        "sign_minus_float_mc_pp": float((s_mc - f_mc).mean() * 100),
        "sign_minus_float_exp_pp": float((s_exp - f_exp).mean() * 100),
        "anchor_diff": float(s_mc.mean() - ANCHOR),
        "maxabs_sign_mc_vs_worker": float(np.abs(s_mc - w_smc).max()),
        "maxabs_sign_mc_vs_npz": float(np.abs(s_mc - np.asarray(npz["native"], float)).max()),
        "worker_sign_mc_mean": w_smc_mean,
        "worker_float_mc_mean": float(np.asarray(g["float_mc"], float).mean()),
        "maxabs_float_mc_vs_worker": float(np.abs(f_mc - np.asarray(g["float_mc"], float)).max()),
        "float_mc_minus_exp_maxabs": float(np.abs(f_mc - f_exp).max()),
        "perq_arms": sorted(list(perq.get("per_arm", {}).keys())),
        "perq_has_float_arm": any("FLOAT" in a.upper() or "COS" in a.upper()
                                  for a in perq.get("per_arm", {}).keys()),
        "macro_sign_mc": float(np.mean([np.mean([r[0] for r in v]) for v in per_archive.values()])),
        "macro_float_mc": float(np.mean([np.mean([r[1] for r in v]) for v in per_archive.values()])),
        "single_gold_n": int(sum(1 for q in valid if len(q["ag"]) == 1)),
        "multi_gold_n": int(sum(1 for q in valid if len(q["ag"]) > 1)),
        "any_hit_sign_mc": float(np.mean(s_mc > 0)),
        "any_hit_float_mc": float(np.mean(f_mc > 0)),
    }
    # exact rational synthetic: positive diagonal scale => SIGN invariant, float moves
    q = [Fraction(1), Fraction(1)]
    R = [Fraction(1), Fraction(1, 10)]
    I = [Fraction(-1), Fraction(5)]
    def sgn(x):
        return 1 if x >= 0 else -1
    def ham(D, qq):
        return sum(1 for a, b in zip([sgn(v) for v in D], [sgn(v) for v in qq]) if a != b)
    t = Fraction(4)
    qs = [t * v for v in q]
    Rs = [t * R[0], R[1]]
    inv = (ham(R, q) == ham(Rs, qs)) and (ham(I, q) == ham([t * I[0], I[1]], qs))
    # cosine strictly changes on this exhibit (cross-multiplied, root-free)
    def cos_order(a, b, qq):
        da = (sum(x * y for x, y in zip(a, qq))) ** 2, sum(x * x for x in a)
        db = (sum(x * y for x, y in zip(b, qq))) ** 2, sum(x * x for x in b)
        sa = 1 if sum(x * y for x, y in zip(a, qq)) > 0 else (-1 if sum(x * y for x, y in zip(a, qq)) < 0 else 0)
        sb = 1 if sum(x * y for x, y in zip(b, qq)) > 0 else (-1 if sum(x * y for x, y in zip(b, qq)) < 0 else 0)
        return sa, sb, da, db
    res["synthetic_sign_invariant_under_pos_scale"] = bool(inv)
    # E1 rational exhibit (sign wins, cosine loses) root-free check
    q3 = [Fraction(1)] * 3
    R3 = [Fraction(1), Fraction(1, 10), Fraction(1, 10)]
    I3 = [Fraction(-1), Fraction(5), Fraction(5)]
    hR = ham(R3, q3)
    hI = ham(I3, q3)
    dR = sum(x * y for x, y in zip(R3, q3))
    dI = sum(x * y for x, y in zip(I3, q3))
    nR = sum(x * x for x in R3)
    nI = sum(x * x for x in I3)
    # cos(I) > cos(R) <=> dI^2*nR > dR^2*nI (both dots positive)
    res["synthetic_E1"] = {"ham_gold": hR, "ham_distr": hI, "sign_wins": hR < hI,
                           "dots_positive": bool(dR > 0 and dI > 0),
                           "cos_distr_beats_gold": bool(dI * dI * nR > dR * dR * nI)}
    res["source_hashes_before"] = read_hashes
    out = {"results": res, "note": "diagnostic recompute only; not an independent review"}
    print(json.dumps(res, indent=1))
    if "--write" in sys.argv:
        Path(__file__).resolve().parent.joinpath("results.json").write_text(
            json.dumps(out, indent=1), encoding="utf-8")
    # re-hash after (read-only check)
    after = {str(p): sha256(p) for p in read_hashes}
    assert after == read_hashes, "source bytes changed during run"
    print("SOURCE_HASHES_STABLE " + str(len(read_hashes)))

if __name__ == "__main__":
    main()
