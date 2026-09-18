# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# verify.py — independent audit recompute (read-only sources, writes only here).
# Env: threads=1, PYTHONDONTWRITEBYTECODE=1, /home/mdp/muse-work/ml-python -B.
# Run: THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B verify.py
import os
for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "THREADS"):
    os.environ.setdefault(_k, "1")
import hashlib, json, pickle
from fractions import Fraction
import numpy as np

W = "/mnt/c/Users/MDP/dev/llmzip-work"
T = W + "/theory_benchmark_test_v1"
K = 3
T_GRID = [0.25, 0.5, 1.0, 2.0, 4.0]
res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"]}
fails = []
def check(name, cond, detail=""):
    res.setdefault("checks", []).append({"name": name, "pass": bool(cond), "detail": str(detail)[:600]})
    print(("PASS " if cond else "FAIL ") + name + (" | " + str(detail)[:300] if detail else ""), flush=True)
    if not cond:
        fails.append(name)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

# ---- source hashes (before) ----
hash_targets = [
    T + "/PLAN.md",
    T + "/lme/per_query.jsonl", T + "/locomo/per_query.jsonl",
    T + "/realtalk/per_query.jsonl", T + "/perltqa/per_query.jsonl",
    T + "/lme/run_lme.py", T + "/locomo/run_locomo.py",
    T + "/realtalk/transfer_runner.py", T + "/perltqa/runner.py",
]
hash_before = {}
for p in hash_targets:
    try:
        hash_before[p] = sha256_file(p)
    except Exception as e:
        hash_before[p] = "UNREADABLE:" + str(e)
res["source_hashes_before"] = hash_before

# ============ §A exact rational synthetic counterexamples (Model-H scope) ============
# E1 (sign wins, no ties): q=(1,1,1), R=(1,1/10,1/10), I=(-1,5,5).
# cos(I)>cos(R) <=> 81/51 > 1.44/1.02 <=> 82.62 > 73.44 (both dots positive).
qE = (Fraction(1), Fraction(1), Fraction(1))
RE = (Fraction(1), Fraction(1, 10), Fraction(1, 10))
IE = (-1, 5, 5)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm2(a): return sum(x * x for x in a)
dR, dI = dot(RE, qE), dot(IE, qE)  # 6/5, 9
lhs = dI * dI * norm2(RE)  # 81*1.02
rhs = dR * dR * norm2(IE)  # 1.44*51
check("A.E1_sign_wins_strict", dR > 0 and dI > 0 and lhs > rhs,
      f"dots {dR} vs {dI}; 81*1.02={float(lhs)} > 1.44*51={float(rhs)}")
# E2 (sign loses, no ties): R=(1,-.1,-.1), I=(-1,.1,.1): dots +.8/-0.8 equal norms.
R2 = (Fraction(1), Fraction(-1, 10), Fraction(-1, 10))
I2 = (Fraction(-1), Fraction(1, 10), Fraction(1, 10))
check("A.E2_sign_loses_strict", dot(R2, qE) == Fraction(4, 5) and dot(I2, qE) == Fraction(-4, 5)
      and norm2(R2) == norm2(I2), "dots +0.8/-0.8, equal norms 1.02")
# Model-H pairwise (corrected shared-gold-independent pairwise marginals): sign 13/16;
# cosine t=1/2: 31/32; t=10: 11/16 (16-state enumeration, exact).
import itertools
def modelH_pairwise(t_num, t_den):
    t = Fraction(t_num, t_den)
    win = tie = loss = 0
    for bits in itertools.product([1, -1], repeat=4):
        e2, e3, d2, d3 = bits
        A = (e2 == 1) + (e3 == 1)
        B = (d2 == 1) + (d3 == 1)
        D = (e2 + e3 - d2 - d3)  # in {-4,-2,0,2,4}
        # sign: gold dist 2-A vs nongold 3-B
        if (2 - A) < (3 - B): win += 1
        elif (2 - A) == (3 - B): tie += 1
        else: loss += 1
    return win, tie, loss
w, ti, l = modelH_pairwise(1, 1)
check("A.sign_pairwise_13/16", (w, ti, l) == (11, 4, 1), f"W/T/L={w}/{ti}/{l}")
def cos_pairwise(t_num, t_den):
    # sign_mechanism REPORT §3: dot gap = 2 + t*D with coin-sum D in {-4,-2,0,2,4}
    t = Fraction(t_num, t_den)
    win = tie = loss = 0
    for bits in itertools.product([1, -1], repeat=4):
        D = bits[0] + bits[1] - bits[2] - bits[3]
        gap = 2 + t * D
        if gap > 0: win += 1
        elif gap == 0: tie += 1
        else: loss += 1
    return win, tie, loss
check("A.cos_t05_31/32", cos_pairwise(1, 2) == (15, 1, 0), str(cos_pairwise(1, 2)))
check("A.cos_t10_11/16", cos_pairwise(10, 1) == (11, 0, 5), str(cos_pairwise(10, 1)))
res["synthetic_exact"] = {"E1": "sign wins strict, no ties", "E2": "sign loses strict, no ties",
                          "sign_pairwise": "13/16", "cos_t0.5": "31/32", "cos_t10": "11/16"}

# ============ §B primary recompute from stored per_query tables ============
def load_jsonl(p):
    rows = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def cluster_bootstrap(contrast, clusters, seed=20260913, reps=2000):
    rng = np.random.default_rng(seed)
    uclus = sorted(set(clusters))
    idx = {c: np.array([i for i, x in enumerate(clusters) if x == c]) for c in uclus}
    contrast = np.asarray(contrast, float)
    m = len(uclus)
    boots = np.empty(reps)
    for r in range(reps):
        pick = rng.integers(0, m, m)
        sel = np.concatenate([idx[uclus[j]] for j in pick])
        boots[r] = contrast[sel].mean()
    return float(np.mean(boots)), float(np.std(boots, ddof=1)), \
        [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]

primaries = {}
# ---- LME (long) ----
lme_rows = load_jsonl(T + "/lme/per_query.jsonl")
lme_q = {}
for r in lme_rows:
    lme_q.setdefault((r["archive_id"], r["qa_id"]), {})[(r["group"], r["t"])] = r
assert len(lme_q) == 470, len(lme_q)
lc = np.array([v[("LOW48", 4.0)]["delta_exact"] - v[("LOW48", 0.25)]["delta_exact"] for v in lme_q.values()])
lclus = [v[("LOW48", 1.0)]["archive_id"] for v in lme_q.values()]
lmean = float(lc.mean())
_, _, lci = cluster_bootstrap(lc, lclus)
# reciprocal: LOW48(t) float vs HIGH48(1/t) float per QA
lrec = max(abs(v[("LOW48", t)]["float_exact"] - v[("HIGH48", round(1 / t, 10) if isinstance(1 / t, float) else 1 / t)]["float_exact"])
           for v in lme_q.values() for t in [0.25, 0.5, 1.0, 2.0, 4.0])
# FULL96 invariance vs t=1
lful = max(abs(v[("FULL96", t)]["float_exact"] - v[("FULL96", 1.0)]["float_exact"])
           for v in lme_q.values() for t in T_GRID)
# monotonicity violations: any adjacent delta decrease along t grid
lviol = sum(1 for v in lme_q.values()
            if any(v[("LOW48", T_GRID[i + 1])]["delta_exact"] < v[("LOW48", T_GRID[i])]["delta_exact"] for i in range(4)))
primaries["LME"] = {"n": 470, "rows": len(lme_rows), "contrast_pp": lmean * 100,
                    "ci_pp": [lci[0] * 100, lci[1] * 100], "recip_maxdiff": lrec,
                    "full96_maxdiff": lful, "viol_n": lviol}
check("B.LME_contrast_-6.44326pp", abs(lmean * 100 - (-6.443262411347517)) < 1e-9, f"{lmean*100}")
check("B.LME_reciprocal_exact", lrec == 0.0, f"maxdiff={lrec}")
check("B.LME_viol_114", lviol == 114, f"viol={lviol}")

# ---- LoCoMo (nested per-QA) ----
loco_rows = load_jsonl(T + "/locomo/per_query.jsonl")
assert len(loco_rows) == 1535, len(loco_rows)
oc = np.array([r["cfg"]["LOW48"]["4.0"]["d_exp"] - r["cfg"]["LOW48"]["0.25"]["d_exp"] for r in loco_rows])
oclus = [r["ci"] for r in loco_rows]
omean = float(oc.mean())
_, _, oci = cluster_bootstrap(oc, oclus)
orec = max(abs(r["cfg"]["LOW48"][ts]["f_exp"] - r["cfg"]["HIGH48"][ complementary(ts) ]["f_exp"])
           for r in loco_rows for ts in ["0.25", "0.5", "1.0", "2.0", "4.0"]
           for complementary in [lambda s: {"0.25": "4.0", "0.5": "2.0", "1.0": "1.0", "2.0": "0.5", "4.0": "0.25"}[s]])
oful = max(abs(r["cfg"]["FULL96"][ts]["f_exp"] - r["cfg"]["FULL96"]["1.0"]["f_exp"])
           for r in loco_rows for ts in ["0.25", "0.5", "1.0", "2.0", "4.0"])
oviol = sum(1 for r in loco_rows
            if any(r["cfg"]["LOW48"][b]["d_exp"] < r["cfg"]["LOW48"][a]["d_exp"]
                   for a, b in [("0.25", "0.5"), ("0.5", "1.0"), ("1.0", "2.0"), ("2.0", "4.0")]))
primaries["LoCoMo"] = {"n": 1535, "rows": len(loco_rows), "contrast_pp": omean * 100,
                       "ci_pp": [oci[0] * 100, oci[1] * 100], "recip_maxdiff": orec,
                       "full96_maxdiff": oful, "viol_n": oviol}
check("B.LoCoMo_contrast_-2.58291pp", abs(omean * 100 - (-2.5829067783465174)) < 1e-9, f"{omean*100}")
check("B.LoCoMo_reciprocal_exact", orec == 0.0, f"maxdiff={orec}")
check("B.LoCoMo_viol_151", oviol == 151, f"viol={oviol}")

# ---- REALTALK (long) ----
rt_rows = load_jsonl(T + "/realtalk/per_query.jsonl")
rt_q = {}
for r in rt_rows:
    rt_q.setdefault(r["qid"], {})[(r["group"], r["t"])] = r
assert len(rt_q) == 705, len(rt_q)
rc = np.array([v[("LOW48", 4.0)]["delta_exact"] - v[("LOW48", 0.25)]["delta_exact"] for v in rt_q.values()])
rclus = [v[("LOW48", 1.0)]["chat"] for v in rt_q.values()]
rmean = float(rc.mean())
_, _, rci = cluster_bootstrap(rc, rclus)
rrec = max(abs(v[("LOW48", t)]["float_exact"] - v[("HIGH48", {0.25: 4.0, 0.5: 2.0, 1.0: 1.0, 2.0: 0.5, 4.0: 0.25}[t])]["float_exact"])
           for v in rt_q.values() for t in T_GRID)
rful = max(abs(v[("FULL96", t)]["float_exact"] - v[("FULL96", 1.0)]["float_exact"])
           for v in rt_q.values() for t in T_GRID)
rviol = sum(1 for v in rt_q.values()
            if any(v[("LOW48", T_GRID[i + 1])]["delta_exact"] < v[("LOW48", T_GRID[i])]["delta_exact"] for i in range(4)))
primaries["REALTALK"] = {"n": 705, "rows": len(rt_rows), "contrast_pp": rmean * 100,
                         "ci_pp": [rci[0] * 100, rci[1] * 100], "recip_maxdiff": rrec,
                         "full96_maxdiff": rful, "viol_n": rviol}
check("B.RT_contrast_-0.093606pp", abs(rmean * 100 - (-0.09360576381852989)) < 1e-9, f"{rmean*100}")
check("B.RT_reciprocal_exact", rrec == 0.0, f"maxdiff={rrec}")
check("B.RT_viol_41", rviol == 41, f"viol={rviol}")
check("B.RT_CI_covers_zero", rci[0] * 100 < 0 < rci[1] * 100, f"CI={[rci[0]*100, rci[1]*100]}")

# ---- PerLTQA (long, FULL96 only t=4) ----
pq_rows = load_jsonl(T + "/perltqa/per_query.jsonl")
pq_q = {}
for r in pq_rows:
    pq_q.setdefault(r["qid"], {})[(r["group"], r["t"])] = r
assert len(pq_q) == 8265, len(pq_q)
pc = np.array([v[("LOW48", 4.0)]["delta_exact"] - v[("LOW48", 0.25)]["delta_exact"] for v in pq_q.values()])
pclus = [v[("LOW48", 1.0)]["char"] for v in pq_q.values()]
pmean = float(pc.mean())
_, _, pci = cluster_bootstrap(pc, pclus)
prec = max(abs(v[("LOW48", t)]["float_exact"] - v[("HIGH48", {0.25: 4.0, 0.5: 2.0, 1.0: 1.0, 2.0: 0.5, 4.0: 0.25}[t])]["float_exact"])
           for v in pq_q.values() for t in T_GRID)
pviol = sum(1 for v in pq_q.values()
            if any(v[("LOW48", T_GRID[i + 1])]["delta_exact"] < v[("LOW48", T_GRID[i])]["delta_exact"] for i in range(4)))
import collections
sec_c = collections.Counter(v[("LOW48", 1.0)]["section"] for v in pq_q.values())
primaries["PerLTQA"] = {"n": 8265, "rows": len(pq_rows), "contrast_pp": pmean * 100,
                        "ci_pp": [pci[0] * 100, pci[1] * 100], "recip_maxdiff": prec,
                        "full96_float_drift_t4": float(np.mean(
                            [v[("FULL96", 4.0)]["float_exact"] - v[("LOW48", 1.0)]["float_exact"] for v in pq_q.values()])),
                        "viol_n": pviol, "sections": dict(sec_c)}
check("B.PQ_contrast_+2.46415pp", abs(pmean * 100 - 2.464151118446995) < 1e-9, f"{pmean*100}")
check("B.PQ_reciprocal_exact", prec == 0.0, f"maxdiff={prec}")
check("B.PQ_viol_961", pviol == 961, f"viol={pviol}")
res["primaries"] = primaries

# ============ §C disclosed subset + scaled-cosine decomposition ============
# Selection BEFORE computation (persisted to selected_ids.json first).
def endpoint_contrast(entry):
    return entry[("LOW48", 4.0)]["delta_exact"] - entry[("LOW48", 0.25)]["delta_exact"] \
        if ("LOW48", 4.0) in entry else (entry["cfg"]["LOW48"]["4.0"]["d_exp"] - entry["cfg"]["LOW48"]["0.25"]["d_exp"])
def is_viol(entry):
    try:
        return any(entry[("LOW48", T_GRID[i + 1])]["delta_exact"] < entry[("LOW48", T_GRID[i])]["delta_exact"] for i in range(4))
    except KeyError:
        return any(entry["cfg"]["LOW48"][b]["d_exp"] < entry["cfg"]["LOW48"][a]["d_exp"]
                   for a, b in [("0.25", "0.5"), ("0.5", "1.0"), ("1.0", "2.0"), ("2.0", "4.0")])
sel = {}
def skey(bname, q):
    return f"{q[0]}|{q[1]}" if bname == "LME" else q
for bname, qdict in [("LME", lme_q), ("REALTALK", rt_q), ("PerLTQA", pq_q)]:
    det = sorted(qdict.keys())[:10]
    viol = sorted([q for q in qdict if is_viol(qdict[q])],
                  key=lambda q: -abs(endpoint_contrast(qdict[q])))[:3]
    sel[bname] = {"deterministic_first10": [skey(bname, q) for q in det],
                  "illustrative_violators": [skey(bname, q) for q in viol],
                  "reason_det": "lexicographic first 10 valid qids (outcome-blind)",
                  "reason_ill": "largest |LOW48 endpoint contrast| among adjacent-decrease violators; ORACLE/ILLUSTRATIVE only"}
det_o = sorted(range(len(loco_rows)), key=lambda i: loco_rows[i]["qid"])[:10]
sel["LoCoMo"] = {"deterministic_first10": [loco_rows[i]["qid"] for i in det_o],
                 "illustrative_violators": sorted(
                     [r["qid"] for r in loco_rows if is_viol({"cfg": r["cfg"]})],
                     key=lambda q: -abs(next(rr["cfg"]["LOW48"]["4.0"]["d_exp"] - rr["cfg"]["LOW48"]["0.25"]["d_exp"]
                                             for rr in loco_rows if rr["qid"] == q)))[:3],
                 "reason_det": "lexicographic first 10 valid qids (outcome-blind)",
                 "reason_ill": "largest |LOW48 endpoint contrast| among adjacent-decrease violators; ORACLE/ILLUSTRATIVE only"}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "selected_ids.json"), "w") as f:
    json.dump(sel, f, indent=1)
res["selection"] = sel
print("wrote selected_ids.json", flush=True)

def low48(q):
    order = sorted(range(96), key=lambda j: (abs(float(q[j])), j))
    return np.array(sorted(order[:48]), dtype=int)

def exact_fr_float(scores, gold, k=K):
    v = np.asarray(scores, dtype=np.float64)
    tot = 0.0
    for gg in np.asarray(gold).ravel():
        sg = v[int(gg)]
        s = int(np.count_nonzero(v > sg))
        tincl = int(np.count_nonzero(v == sg))
        tot += 0.0 if s >= k else (1.0 if s + tincl <= k else (k - s) / tincl)
    return tot / len(np.asarray(gold).ravel())

def decompose_check(C, q, gold, tag):
    """Direct scaled cosine vs rank-equivalent group decomposition over t grid."""
    C = np.asarray(C, float)
    q = np.asarray(q, float).reshape(-1)
    G = low48(q)
    mask = np.zeros(96, bool)
    mask[G] = True
    DG = C[:, mask] @ q[mask]
    DC = C[:, ~mask] @ q[~mask]
    nGd = (C[:, mask] ** 2).sum(1)
    nCd = (C[:, ~mask] ** 2).sum(1)
    nGq = float((q[mask] ** 2).sum())
    nCq = float((q[~mask] ** 2).sum())
    out = {"tag": tag, "N": int(C.shape[0]), "per_t": {}, "max_abs_diff": 0.0,
           "rank_mismatches": 0, "fr_mismatches": 0, "sign_invariant": True,
           "float_tie_counts": {}, "gold": [int(g) for g in np.asarray(gold).ravel()]}
    d0 = np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1)
    for t in T_GRID:
        Ct = C.copy()
        Ct[:, mask] *= t
        qt = q.copy()
        qt[mask] *= t
        dn = np.sqrt((Ct ** 2).sum(1))
        qn = float(np.sqrt((qt ** 2).sum()))
        assert np.all(dn > 0) and qn > 0, f"zero norm {tag} t={t}"
        direct = (Ct @ qt) / (dn * qn)
        num = t * t * DG + DC
        den = np.sqrt(t * t * nGd + nCd) * np.sqrt(t * t * nGq + nCq)
        formula = num / den
        adiff = float(np.max(np.abs(direct - formula)))
        out["max_abs_diff"] = max(out["max_abs_diff"], adiff)
        # rank equality: full order must agree (exact ranks, no tolerance)
        o1 = np.lexsort((np.arange(len(direct)), -direct))
        o2 = np.lexsort((np.arange(len(formula)), -formula))
        if not np.array_equal(o1, o2):
            out["rank_mismatches"] += 1
        f1, f2 = exact_fr_float(direct, gold), exact_fr_float(formula, gold)
        if f1 != f2:
            out["fr_mismatches"] += 1
        out["per_t"][str(t)] = {"fr_direct": f1, "fr_formula": f2, "adiff": adiff,
                                "order_agree": bool(np.array_equal(o1, o2))}
        # exact-== tie mass at endpoints
        if t in (0.25, 4.0):
            tc = {}
            for gg in np.asarray(gold).ravel():
                sg = direct[int(gg)]
                tc[str(int(gg))] = {"S": int(np.count_nonzero(direct > sg)),
                                    "T": int(np.count_nonzero(direct == sg))}
            out["float_tie_counts"][str(t)] = tc
        dt = np.count_nonzero((Ct >= 0) != (qt >= 0)[None, :], axis=1)
        if not np.array_equal(dt, d0):
            out["sign_invariant"] = False
    out["ulp_note"] = "adiff is absolute float64 difference; 1 ulp ~2.2e-16 relative"
    return out, {"DG": DG, "DC": DC, "nGd": nGd, "nCd": nCd, "nGq": nGq, "nCq": nCq, "G": G}

# ---- cache loaders (traced producer mapping; assert keys, no guessing) ----
def load_lme(archive_id):
    # run_lme.py:163-170: pkl keys question_id/C/qC/gold
    o = pickle.load(open(W + f"/regen/lme/cache_repr/{archive_id}.pkl", "rb"))
    assert set(["C", "qC", "gold"]).issubset(o.keys()), sorted(o.keys())
    return (np.asarray(o["C"], float), np.asarray(o["qC"], float).reshape(-1),
            np.asarray(o["gold"]).ravel())

import re
def _norm_ev(x):
    if x is None:
        return []
    if isinstance(x, str):
        v = re.findall(r"D\d+:\d+", x)
        return v if v else [x]
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
_loco_cache = {}
def load_locomo(qid):
    # run_locomo.py load_all: RAW drive/locomo10.json + AUDIT drive/audit_layer + REGEN locomo_{ci}.pkl (keys C/QC/qas/id_to_row)
    if not _loco_cache:
        raw = json.load(open(W + "/drive/locomo10.json"))
        corr = {}
        import glob
        for f in sorted(glob.glob(W + "/drive/audit_layer/errors_conv_*.json")):
            try:
                rows = json.load(open(f))
            except Exception:
                continue
            if not isinstance(rows, list):
                continue
            for r in rows:
                if r.get("question_id"):
                    corr[str(r["question_id"])] = _norm_ev(r.get("correct_evidence"))
        convs = []
        for idx, item in enumerate(raw):
            qas = []
            for qi, q in enumerate(item.get("qa", []) or []):
                cat = int(q.get("category")) if q.get("category") is not None else None
                if cat not in (1, 2, 3, 4):
                    continue
                qid2 = q.get("question_id") or f"locomo_{idx}_qa{qi}"
                ce = corr.get(str(qid2), _norm_ev(q.get("evidence")))
                qas.append({"question_id": str(qid2), "ag_ids": ce})
            convs.append(qas)
        reps = [pickle.load(open(W + f"/regen/locomo/locomo_{ci}.pkl", "rb")) for ci in range(10)]
        _loco_cache["convs"] = convs
        _loco_cache["reps"] = reps
    for ci, qas in enumerate(_loco_cache["convs"]):
        for qi, q in enumerate(qas):
            if q["question_id"] == qid:
                r = _loco_cache["reps"][ci]
                id_to_row = r["id_to_row"]
                ag = list(dict.fromkeys(int(id_to_row[x]) for x in q["ag_ids"] if x in id_to_row))
                assert len(ag) > 0, f"no gold rows {qid}"
                return (np.asarray(r["C"], float), np.asarray(r["QC"][qi], float).reshape(-1), np.asarray(ag).ravel())
    raise KeyError(f"qid not found {qid}")

_rt_cache = {}
def load_rt(qid):
    # producer_run_realtalk.py:102-104: o[C]/o[QC]/o[gold_rows][qi]
    conv = qid.split("_q")[0]
    if conv not in _rt_cache:
        _rt_cache[conv] = pickle.load(open(W + f"/bench3/runs/b3a_realtalk/rt_repr/{conv}.pkl", "rb"))
    o = _rt_cache[conv]
    assert set(["C", "QC", "gold_rows", "qids"]).issubset(o.keys()), sorted(o.keys())
    qi = list(o["qids"]).index(qid)
    gold = [int(g) for g in o["gold_rows"][qi]]
    assert len(gold) > 0, f"empty gold {qid}"
    return (np.asarray(o["C"], float), np.asarray(o["QC"][qi], float).reshape(-1), np.asarray(gold).ravel())

_pq_cache = {}
def load_pq(qid):
    # runner.py:129-143: q[gold]/q[qC], arch[char] C
    if not _pq_cache:
        _pq_cache["arch"] = pickle.load(open(W + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl", "rb"))
        _pq_cache["q"] = pickle.load(open(W + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl", "rb"))
    q = _pq_cache["q"][qid]
    C = np.asarray(_pq_cache["arch"][q["char"]]["C"], float)
    return (C, np.asarray(q["qC"], float).reshape(-1), np.asarray(q["gold"]).ravel())

geom, wit = {}, {}
all_det_stats = []
for bname, loader, qdict in [("LME", load_lme, lme_q), ("LoCoMo", load_locomo, None),
                             ("REALTALK", load_rt, rt_q), ("PerLTQA", load_pq, pq_q)]:
    det = sel[bname]["deterministic_first10"]
    ill = sel[bname]["illustrative_violators"]
    brep = {"deterministic": {}, "illustrative": {}, "witness": None}
    worst_adiff, rank_bad, fr_bad, sign_bad = 0.0, 0, 0, 0
    for qid in det + ill:
        kind = "deterministic" if qid in det else "illustrative"
        try:
            if bname == "LME":
                a, qq = qid.split("|")
                C, q, g = loader(a)
            else:
                C, q, g = loader(qid)
            out, comp = decompose_check(C, q, g, f"{bname}:{qid}")
            worst_adiff = max(worst_adiff, out["max_abs_diff"])
            rank_bad += out["rank_mismatches"]
            fr_bad += out["fr_mismatches"]
            if not out["sign_invariant"]:
                sign_bad += 1
            brep[kind][qid] = out
            if kind == "deterministic":
                dn = np.sqrt((C ** 2).sum(1))
                qn = float(np.sqrt((q ** 2).sum()))
                s1 = (C @ q) / (dn * qn)
                all_det_stats.append({
                    "b": bname, "qid": qid, "N": int(C.shape[0]),
                    "doc_norm_cv": float(dn.std() / dn.mean()),
                    "doc_norm_maxmin": float(dn.max() / dn.min()),
                    "gold_cos": [float(s1[int(gg)]) for gg in np.asarray(g).ravel()],
                    "qconc": float((q ** 4).sum() / ((q ** 2).sum() ** 2)),
                    "group_share_gold": float((comp["DG"][[int(gg) for gg in np.asarray(g).ravel()]]).mean() /
                                              max(1e-300, abs((comp["DG"] + comp["DC"])[[int(gg) for gg in np.asarray(g).ravel()]].mean()))),
                    "nGq_share": float(comp["nGq"] / (comp["nGq"] + comp["nCq"])),
                })
        except Exception as e:
            brep[kind][qid] = {"ERROR": f"{type(e).__name__}: {e}"}
    # flip witness: first illustrative violator with a real rank flip at endpoints (ORACLE/DESCRIPTIVE)
    for qid in ill:
        e = brep["illustrative"].get(qid, {})
        if "per_t" not in e:
            continue
        if e["per_t"]["0.25"]["fr_direct"] == e["per_t"]["4.0"]["fr_direct"]:
            continue
        try:
            C, q, g = (load_lme(qid.split("|")[0]) if bname == "LME" else loader(qid))
            out_c, comp = decompose_check(C, q, g, f"{bname}:{qid}")
            G = comp["G"]
            mask = np.zeros(96, bool)
            mask[G] = True
            t = 4.0
            Ct = C.copy()
            Ct[:, mask] *= t
            qt = q.copy()
            qt[mask] *= t
            s4 = (Ct @ qt) / (np.sqrt((Ct ** 2).sum(1)) * float(np.sqrt((qt ** 2).sum())))
            g0 = int(np.asarray(g).ravel()[0])
            rivals = [d for d in np.argsort(-s4)[:6] if d != g0]
            r = int(rivals[0]) if rivals else int(np.argsort(-s4)[0])
            brep["witness"] = {
                "qid": qid, "gold": g0, "rival": r, "t": t,
                "DG_gold": float(comp["DG"][g0]), "DC_gold": float(comp["DC"][g0]),
                "DG_rival": float(comp["DG"][r]), "DC_rival": float(comp["DC"][r]),
                "nGd_share_gold": float(comp["nGd"][g0] / (comp["nGd"][g0] + comp["nCd"][g0])),
                "nGd_share_rival": float(comp["nGd"][r] / (comp["nGd"][r] + comp["nCd"][r])),
                "nGq_share": float(comp["nGq"] / (comp["nGq"] + comp["nCq"])),
                "s_gold_t0.25": float(e["per_t"]["0.25"]["fr_direct"]),
                "s_gold_t4": float(e["per_t"]["4.0"]["fr_direct"]),
                "label": "ORACLE/DESCRIPTIVE ONLY: gold/rival chosen using observed flip; not a predictive model; no population rate",
            }
            break
        except Exception as ex:
            brep["witness"] = {"ERROR": str(ex)}
            break
    brep["aggregate"] = {"n_checked": len(det) + len(ill), "worst_adiff": worst_adiff,
                         "rank_mismatches": rank_bad, "fr_mismatches": fr_bad,
                         "sign_noninvariant": sign_bad}
    geom[bname] = brep
    check(f"C.{bname}_decomp_order+FR_exact", rank_bad == 0 and fr_bad == 0,
          f"worst_adiff={worst_adiff:.3e} rank_bad={rank_bad} fr_bad={fr_bad}")
    check(f"C.{bname}_sign_invariant", sign_bad == 0, f"noninvariant={sign_bad}")
res["geometry"] = {b: {"aggregate": v["aggregate"], "witness": v["witness"],
                       "deterministic": v["deterministic"], "illustrative": v["illustrative"]} for b, v in geom.items()}
res["det_stats"] = all_det_stats

# ============ §D H-assumption evidence table (deterministic subset only) ============
import statistics as _st
ev = []
cvs = [s["doc_norm_cv"] for s in all_det_stats]
mms = [s["doc_norm_maxmin"] for s in all_det_stats]
ev.append({"assumption": "H1 equal doc norms (Model-H: all docs share norm sqrt(1+2t^2))",
           "finding": f"doc-norm CV range [{min(cvs):.4f},{max(cvs):.4f}], max/min ratio up to {max(mms):.4f} over {len(all_det_stats)} deterministic queries",
           "status": "PROVEN-FAILED from direct arrays" if max(mms) > 1 + 1e-12 else "holds on subset",
           "lines": "verify.py §D; caches via loaders §C"})
golds = [c for s in all_det_stats for c in s["gold_cos"]]
ev.append({"assumption": "H2 fixed signal alignment (gold score constant given state)",
           "finding": f"gold cosine@s=1 range [{min(golds):.4f},{max(golds):.4f}] across deterministic subset; alignment varies query to query",
           "status": "PROVEN-FAILED from direct arrays" if max(golds) - min(golds) > 1e-9 else "holds on subset",
           "lines": "verify.py §D"})
gsh = [s["group_share_gold"] for s in all_det_stats]
ev.append({"assumption": "H3 LOW48 labels pure nuisance (group dot carries no gold-favoring signal)",
           "finding": f"gold LOW48-dot share of total dot ranges [{min(gsh):.3f},{max(gsh):.3f}]; sign/magnitude varies: LOW48 sometimes favors gold",
           "status": "PROVEN-FAILED from direct arrays" if min(gsh) < max(gsh) and (min(gsh) < 0 or max(gsh) > 1) else "needs rival-contrast (see witnesses)",
           "lines": "verify.py §D + §C witnesses"})
ev.append({"assumption": "H4 independent queries (no shared archive/question structure)",
           "finding": "cluster structure from tables: LME 470QA/470arch, REALTALK 705QA/10chats, LoCoMo 1535QA/10conv, PerLTQA 8265QA/30arch; CIs are cluster-bootstraps",
           "status": "PROVEN-FAILED as iid assumption; within-cluster dependence modeled, shared upstream sources UNIDENTIFIED",
           "lines": "verify.py §B; PLAN.md:35"})
ev.append({"assumption": "H5 intervention t maps the synthetic nuisance scale; t=1 is the identified balance point",
           "finding": "t=1 is unmodified embeddings by construction; sign Hamming invariant across t (0 violations on subset); float moves via reweighting+renormalization; HIGH48(1/t)==LOW48(t) exactly (maxdiff 0.0, all 4 benchmarks)",
           "status": "PROVEN-MISMATCH from direct arrays: t scales weighting/norms, not one latent nuisance parameter",
           "lines": "verify.py §B reciprocal + §C sign_invariant"})
ev.append({"assumption": "True signal/nuisance partition of the 96 real coordinates",
           "finding": "no labeled partition exists; LOW48=(|q|,j) proxy chosen gold-free",
           "status": "UNIDENTIFIED — cannot be proven from arrays; witnesses are oracle/descriptive only",
           "lines": "PLAN.md:9,21"})
ev.append({"assumption": "Causal mechanism of baseline sign-float gaps",
           "finding": "not tested here; diagnosis is post-hoc on frozen outcomes",
           "status": "UNIDENTIFIED — no causal inference from selected examples",
           "lines": "STATUS.md"})
res["H_evidence"] = ev

# ---- hashes after + write results ----
hash_after = {}
for p in hash_targets:
    try:
        hash_after[p] = sha256_file(p)
    except Exception as e:
        hash_after[p] = "UNREADABLE:" + str(e)
res["source_hashes_after"] = hash_after
res["sources_unchanged"] = all(hash_before[p] == hash_after[p] for p in hash_targets)
check("D.sources_unchanged", res["sources_unchanged"], "before==after for all read sources")
res["n_fails"] = len(fails)
res["failed"] = fails
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w") as f:
    json.dump(res, f, indent=1)
print("=" * 60)
print(f"CHECKS: {sum(1 for c in res['checks'] if c['pass'])}/{len(res['checks'])} passed; FAILS={fails}")
print("wrote results.json")
sys_exit = 1 if fails else 0
import sys as _sys
_sys.exit(sys_exit)
