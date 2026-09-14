#!/usr/bin/env python3
"""RACE-3: FAISS-ARM race runner (RaBitQ32 + PQ plain) per DRAFT_PREREG_TWELVE_BYTE_RACE_v2.md.

Writes ONLY under /tmp/rb3/. Reads frozen inputs under /mnt/c (read-only).
Env: ~/muse-work/faiss-python (faiss 1.15.0, numpy 2.5.3). No network.

Pilot conventions mirrored verbatim from:
  round2/session_scripts/r2a.py  (LME lex/ties/FR)
  round2/session_scripts/r2c_replicate.py  (LoCoMo corrections/stable_archive_seed/FR)
"""

# ============================ CONSTANTS BLOCK (seal-frozen) ============================
import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")
_os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

FAISS_THREADS = 1              # S5 determinism pin: faiss.omp_set_num_threads(1)

# --- Benchmark anchors (v2 draft s2; abort if recomputed diff > tol) ---
LME_ANCHOR = 0.5419751773049645        # SIGN96 LongMemEval fractional R@3
LOCOMO_ANCHOR = 0.23654714666441054    # SIGN96 corrected-LoCoMo fractional R@3
ANCHOR_TOL = 1e-12                     # abort gate tolerance

# --- Retrieval protocol (v2 draft s3; pilot-verbatim) ---
K = 3                          # top-3
NT = 20                        # 20 frozen nuisance trials
WTL_TOL = 1e-12                # W/T/L pairing tolerance on per-question FR
LME_TIE_BASE = 5_100_000       # LME trial seed: 5_100_000+lex*100_000+t*100+99
def STABLE_ARCHIVE_SEED(ci, t):
    # LoCoMo trial seed: stable_archive_seed(ci,t)+99 (r2c verbatim)
    return 5_100_000 + ci * 100_000 + t * 100

# --- A4 RaBitQ32 arm (v2 draft s5 row A4; PRIMARY) ---
RABITQ_DIM = 32                        # 32-dim rule: only 12-byte 1-bit RaBitQ at d=32
ROTATION_SEEDS_PRIMARY = [94101, 94102, 94103]     # rotation panel, spread-32 axes
AXES_SEEDS_SECONDARY = [94201, 94202, 94203]       # random-32 axes variant seeds
# NOTE (s8.7 deviation, flagged): HR-named TOP32 is NOT used; spread-32 proposed instead.

# --- A6 PQ arm (v2 draft s5 row A6; plain, archive-local, NO OPQ) ---
PQ_M = 12
PQ_NBITS = 8
PQ_DECLARED_BYTES = 12

# --- Byte asserts: pre-seal probe numbers (S2; abort on mismatch) ---
EXP_RQ96_BYTES = 20            # RaBitQuantizer(96).code_size
EXP_RQ32_BYTES = 12            # RaBitQuantizer(32).code_size
EXP_PQ_BYTES = 12              # IndexPQ(96,12,8).code_size
EXP_EXT2BIT_BYTES = 44         # RaBitQuantizer(96, METRIC_L2, 2).code_size
EXP_RQ96_S0 = 458              # trained-empty serialized IndexRaBitQ(96)
EXP_RQ32_S0 = 202              # trained-empty serialized IndexRaBitQ(32)
EXP_PQ_S0 = 98390              # trained-empty serialized IndexPQ(96,12,8) = 98304+86
DECLARED_MARGINAL = 12         # every race arm declares 12 marginal B/vec
SIGN_MU_SHARED = 768           # sign centering state per archive: 96 float64 means
PQ_CODEBOOK_CONTENT = 98304    # 12 subquantizers x 256 centroids x 8 subdims x 4 B

# --- Frozen input paths (WORK overridable, no C:/ hardcode) ---
WORK = _os.environ.get("RB3_WORK", "/mnt/c/Users/MDP/dev/llmzip-work")
LME_PKL_DIR = "regen/lme/cache_repr"
LOCOMO_PKL_PAT = "regen/locomo/locomo_%d.pkl"
LME_CLEANED = "drive/longmemeval_s_cleaned.json"
LOCOMO_RAW = "drive/locomo10.json"
LOCOMO_AUDIT = "drive/audit_layer"

OUT_DIR = "/tmp/rb3"
# ========================== END CONSTANTS BLOCK ============================

import sys, json, time, re, pickle, hashlib
from pathlib import Path
import numpy as np

OUT = Path(OUT_DIR)
CKPT = OUT / "checkpoints"
CKPT.mkdir(parents=True, exist_ok=True)

LOG_LINES = []
def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    LOG_LINES.append(line)
    print(line, flush=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

# ---------------- Loaders (pilot-verbatim) ----------------
def load_lme():
    """Returns (items, lex): items=[{qid,C,qC,gold,N}], lex from cleaned 500-qid file."""
    W = Path(WORK)
    data = json.load(open(W / LME_CLEANED, encoding="utf-8"))
    allq = sorted(str(x["question_id"]) for x in data)
    assert len(allq) == 500, len(allq)
    lex = {q: i for i, q in enumerate(allq)}
    del data
    pkls = sorted((W / LME_PKL_DIR).glob("*.pkl"))
    assert len(pkls) == 470, len(pkls)
    items = []
    for p in pkls:
        o = pickle.loads(p.read_bytes())
        C = np.asarray(o["C"], dtype=np.float64)
        qC = np.asarray(o["qC"], dtype=np.float64)
        gold = np.asarray(o["gold"]).ravel().astype(int)
        assert C.shape[1] == 96 and qC.shape == (96,)
        items.append({"qid": str(o["question_id"]), "C": C, "qC": qC,
                      "gold": set(map(int, gold)), "N": int(C.shape[0]),
                      "lex": lex[str(o["question_id"])]})
    return items, lex

# ---- LoCoMo helpers: verbatim mirror of r2c_replicate.py ----
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
    for f in sorted(Path(audit_dir).glob("errors_conv_*.json")):
        try:
            rows = json.loads(Path(f).read_text(encoding="utf-8"))
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

def evidence_rows(ids, id_to_row):
    out = []
    for x in ids:
        if x in id_to_row:
            out.append(int(id_to_row[x]))
    return list(dict.fromkeys(out))

def load_locomo():
    """Returns dict with convs/reps/Q/valid_qids (r2c-verbatim)."""
    W = Path(WORK)
    raw = json.loads((W / LOCOMO_RAW).read_text(encoding="utf-8"))
    corr = load_audit_corrections(W / LOCOMO_AUDIT)
    convs = []
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
            qas.append({"question_id": str(qid), "category": cat,
                        "raw_evidence": norm_evidence(q.get("evidence")),
                        "correct_evidence": ce})
        convs.append({"conv_id": f"locomo_{idx}", "qas": qas})
    reps = []
    for ci in range(10):
        d = pickle.load(open(W / (LOCOMO_PKL_PAT % ci), "rb"))
        assert d["conv_id"] == f"locomo_{ci}", d["conv_id"]
        raw_ids = [q["question_id"] for q in convs[ci]["qas"]]
        pkl_ids = [q["question_id"] for q in d["qas"]]
        assert raw_ids == pkl_ids, f"order mismatch conv {ci}"
        assert d["QC"].shape[0] == len(d["qas"]), (ci, d["QC"].shape)
        reps.append(d)
    Q = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        id_to_row = r["id_to_row"]
        for qi, q in enumerate(c["qas"]):
            ag = evidence_rows(q["correct_evidence"], id_to_row)
            Q[q["question_id"]] = {"cat": q["category"], "ci": ci, "qi": qi, "ag": ag}
    valid_qids = [qid for qid, v in Q.items() if len(v["ag"]) > 0]
    return {"convs": convs, "reps": reps, "Q": Q, "valid_qids": valid_qids,
            "n_corrections": len(corr)}

# ---------------- FR core (pilot-verbatim ranking) ----------------
def trial_priorities(n, seed):
    return np.random.default_rng(seed).random(n)

def fr_from_dist(dist, gold, pris):
    """dist: (N,) codec-native float distances. tie := exact equality.
    order = lexsort((priority, distance)) i.e. distance-primary (r2a verbatim)."""
    d = np.asarray(dist, dtype=np.float64)
    gset = set(map(int, gold))
    ng = len(gset)
    assert ng > 0
    fr = []
    for p in pris:
        order = np.lexsort((np.asarray(p, dtype=np.float64), d))
        fr.append(len(set(map(int, order[:K])) & gset) / ng)
    return float(np.mean(fr)), [float(x) for x in fr]

def sign_dist_lme(C, qC):
    D0 = (np.asarray(C) >= 0)
    Q0 = (np.asarray(qC) >= 0)
    return np.count_nonzero(D0 != Q0[None, :], axis=1).astype(np.int16)

def sign_dist_matrix(C, QC, subset=None):
    C = np.asarray(C); QC = np.asarray(QC)
    if subset is None:
        D = C >= 0; Qm = QC >= 0
    else:
        D = C[:, subset] >= 0; Qm = QC[:, subset] >= 0
    return np.count_nonzero(Qm[:, None, :] != D[None, :, :], axis=2).astype(np.int16)

# ---------------- Axis constructions (RACE-2 convention) ----------------
def spread_cols(var, k=32):
    """Repaired rank-linspace: order_desc[round(linspace(0,95,k))]; assert eff_k==k."""
    order_desc = np.argsort(np.asarray(var, dtype=np.float64), kind="stable")[::-1]
    idx = np.round(np.linspace(0, 95, k)).astype(int)
    cols = order_desc[idx]
    assert len(set(map(int, cols))) == k, f"eff_k != k: {cols}"
    return np.sort(cols.astype(int))

def random_cols(seed, k=32):
    """Global draw shared across archives (deney1/R2A convention)."""
    return np.sort(np.random.default_rng(seed).choice(96, k, replace=False).astype(int))

def seeded_rotation(seed, d=32):
    """Seeded orthogonal matrix: QR with diag(R) sign fix (hspec convention)."""
    A = np.random.default_rng(seed).standard_normal((d, d))
    Q, R = np.linalg.qr(A)
    sg = np.where(np.diag(R) < 0, -1.0, 1.0)
    return (Q * sg[None, :]).astype(np.float64)

# ---------------- Frozen faiss call sequences ----------------
import faiss
faiss.omp_set_num_threads(FAISS_THREADS)

def FSEQ_A4_build(Xr32):
    """A4 primary/secondary: constructor + train + add (frozen sequence)."""
    idx = faiss.IndexRaBitQ(RABITQ_DIM)   # (d,) ctor; 2nd positional would be METRIC (trap)
    idx.train(Xr32)                        # archive-local fit (centroid)
    idx.add(Xr32)                          # codes: 12 B/vec at d=32
    return idx

def FSEQ_A4_query(idx, qr32, n):
    D, I = idx.search(qr32.reshape(1, -1).astype(np.float32), int(n))
    return D[0].astype(np.float64), I[0].astype(int)

def FSEQ_A5_build(X32):
    """A5 rotation-wrapper: faiss-native RandomRotationMatrix in IndexPreTransform."""
    rt = faiss.RandomRotationMatrix(RABITQ_DIM, RABITQ_DIM)
    rt.train(X32)                          # NOTE: exposes no seed API (S7 finding)
    inner = faiss.IndexRaBitQ(RABITQ_DIM)
    idx = faiss.IndexPreTransform(rt, inner)
    idx.train(X32)
    idx.add(X32)
    return idx

def FSEQ_A5_query(idx, q32, n):
    D, I = idx.search(q32.reshape(1, -1).astype(np.float32), int(n))
    return D[0].astype(np.float64), I[0].astype(int)

class PQMasked(Exception):
    pass

def FSEQ_A6_build(X96):
    """A6 PQ plain m=12x8bit, archive-local. Raises PQMasked on train failure."""
    idx = faiss.IndexPQ(96, PQ_M, PQ_NBITS)   # (d, m, nbits) pinned ctor
    try:
        idx.train(X96)
    except Exception as e:
        raise PQMasked(f"train raised: {type(e).__name__}: {e}")
    if not idx.is_trained:
        raise PQMasked("is_trained False after train")
    try:
        idx.add(X96)
    except Exception as e:
        raise PQMasked(f"add raised: {type(e).__name__}: {e}")
    codes = faiss.vector_to_array(idx.codes)
    if not np.all(np.isfinite(faiss.vector_to_array(idx.pq.centroids))):
        raise PQMasked("non-finite codebook")
    return idx

def FSEQ_A6_query(idx, q96, n):
    D, I = idx.search(q96.reshape(1, -1).astype(np.float32), int(n))
    return D[0].astype(np.float64), I[0].astype(int)

def codes_bytes(idx):
    return faiss.vector_to_array(idx.codes).nbytes

def full_dist_from_search(D, I, n):
    """Map faiss top-n (sorted) D/I back to per-doc distance vector for trial rerank."""
    d = np.empty(int(n), dtype=np.float64)
    d[np.asarray(I, dtype=int)] = np.asarray(D, dtype=np.float64)
    return d

# ---------------- Byte accounting ----------------
def measure_index_bytes(build_fn, Xtrain, n_list=(0, 1, 100, 1000)):
    """S0 = trained-empty serialization; marginal = (S(n)-S0)/n exact identity."""
    rec = {}
    bases = {}
    for n in n_list:
        idx = build_fn(Xtrain, n)
        s = faiss.serialize_index(idx)
        bases[n] = len(s)
    rec["S"] = bases
    rec["S0"] = bases[0]
    rec["code_size_attr"] = int(build_fn(Xtrain, 0).code_size)
    return rec

# ---------------- Smokes ----------------
SMOKE = {}

def smoke_S2(X96):
    """Byte replay: RQ96=20, RQ32=12, PQ=12, ext-2bit=44; S0 sizes; S(n) identities."""
    r = {}
    r["RaBitQuantizer96_code_size"] = int(faiss.RaBitQuantizer(96).code_size)
    r["RaBitQuantizer32_code_size"] = int(faiss.RaBitQuantizer(32).code_size)
    r["IndexPQ96_12_8_code_size"] = int(faiss.IndexPQ(96, 12, 8).code_size)
    r["RaBitQuantizer96_L2_2_code_size"] = int(faiss.RaBitQuantizer(96, faiss.METRIC_L2, 2).code_size)
    assert r["RaBitQuantizer96_code_size"] == EXP_RQ96_BYTES, r
    assert r["RaBitQuantizer32_code_size"] == EXP_RQ32_BYTES, r
    assert r["IndexPQ96_12_8_code_size"] == EXP_PQ_BYTES, r
    assert r["RaBitQuantizer96_L2_2_code_size"] == EXP_EXT2BIT_BYTES, r
    Xs = np.ascontiguousarray(X96[:1000] if X96.shape[0] >= 1000 else X96, dtype=np.float32)
    def b32(Xt, n):
        idx = faiss.IndexRaBitQ(32)
        idx.train(np.ascontiguousarray(Xt[:max(n, 32)][:, :32], dtype=np.float32))
        if n:
            idx.add(np.ascontiguousarray(Xt[:n][:, :32], dtype=np.float32))
        return idx
    def b96(Xt, n):
        idx = faiss.IndexRaBitQ(96)
        idx.train(Xt[:max(n, 96)])
        if n:
            idx.add(Xt[:n])
        return idx
    def bpq(Xt, n):
        idx = faiss.IndexPQ(96, PQ_M, PQ_NBITS)
        idx.train(Xt[:max(n, 256)])
        if n:
            idx.add(Xt[:n])
        return idx
    for name, bf, exp_s0, decl in [("RQ32", b32, EXP_RQ32_S0, 12),
                                   ("RQ96", b96, EXP_RQ96_S0, 20),
                                   ("PQ", bpq, EXP_PQ_S0, 12)]:
        m = measure_index_bytes(bf, Xs)
        r[name] = {"S0": m["S0"], "S": m["S"], "code_size": m["code_size_attr"]}
        assert m["S0"] == exp_s0, (name, m["S0"], exp_s0)          # S0 assert
        assert m["code_size_attr"] == decl, (name, m["code_size_attr"])  # code_size assert
        for n in (1, 100, 1000):
            if n > Xs.shape[0]:
                continue
            assert m["S"][n] - m["S0"] == n * decl, (name, n, m["S"][n], m["S0"])
        r[name]["marginal_identity"] = "S(n)-S0 == n*declared for n in (1,100,1000): PASS"
    # deliberate declaration-mismatch abort demo (negative control)
    try:
        assert r["RaBitQuantizer96_code_size"] == 12, "declared 12 for RQ96"
        r["mismatch_abort_demo"] = "FAIL: abort did not fire"
    except AssertionError:
        r["mismatch_abort_demo"] = "PASS: declaring RQ96 as 12B aborts"
    SMOKE["S2"] = r
    log(f"S2 byte replay PASS: RQ96={r['RaBitQuantizer96_code_size']} RQ32={r['RaBitQuantizer32_code_size']} "
        f"PQ={r['IndexPQ96_12_8_code_size']} EXT2={r['RaBitQuantizer96_L2_2_code_size']} "
        f"S0={r['RQ32']['S0']}/{r['RQ96']['S0']}/{r['PQ']['S0']}")
    return r

def smoke_S3():
    """nb_bits trap negative controls on pinned faiss 1.15.0."""
    r = {}
    r["IndexRaBitQ_has_nb_bits"] = hasattr(faiss.IndexRaBitQ(96), "nb_bits")
    assert r["IndexRaBitQ_has_nb_bits"] is False  # S3 trap documented
    idx2 = faiss.IndexRaBitQ(96, 2)   # 2nd positional = METRIC, not bits (C7)
    r["IndexRaBitQ96_2_code_size"] = int(idx2.code_size)
    r["IndexRaBitQ96_2_metric"] = int(idx2.metric_type)
    assert r["IndexRaBitQ96_2_code_size"] == 20 and r["IndexRaBitQ96_2_metric"] == int(faiss.METRIC_L1)
    q = faiss.RaBitQuantizer(96)
    q.nb_bits = 2                      # silent trap: reads back 2, still 1-bit codes
    r["assigned_nb_bits_readback"] = int(q.nb_bits)
    r["assigned_code_size"] = int(q.code_size)
    assert r["assigned_nb_bits_readback"] == 2 and r["assigned_code_size"] == 20
    ctor = faiss.RaBitQuantizer(96, faiss.METRIC_L2, 2)
    r["ctor_2bit_code_size"] = int(ctor.code_size)
    assert r["ctor_2bit_code_size"] == 44
    r["verdict"] = ("PASS: IndexRaBitQ lacks nb_bits; (96,2)=METRIC_L1@20B; attr-assign reads 2/stores 20B; "
                    "only ctor-form yields 44B")
    SMOKE["S3"] = r
    log("S3 nb_bits trap PASS: " + r["verdict"])
    return r

def smoke_S7(X32):
    """Rotation-chain acceptance criteria, executed + logged (not prose)."""
    r = {}
    X = np.ascontiguousarray(X32[:200], dtype=np.float64)
    Xf = np.ascontiguousarray(X, dtype=np.float32)
    # C1: runner-side rotation orthonormal
    R = seeded_rotation(ROTATION_SEEDS_PRIMARY[0])
    dev = float(np.max(np.abs(R @ R.T - np.eye(32))))
    r["C1_orthonormal_maxdev"] = dev
    r["C1_pass"] = bool(dev < 1e-5)
    # C1b: regeneration bit-identical (0 persisted bytes claim)
    r["C1b_regen_identical"] = bool(np.array_equal(R, seeded_rotation(ROTATION_SEEDS_PRIMARY[0])))
    # C2: rotation preserves pre-quantization pairwise distances
    Xr = X @ R
    d0 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    d1 = ((Xr[:, None, :] - Xr[None, :, :]) ** 2).sum(-1)
    r["C2_dist_preserved"] = bool(np.allclose(d0, d1, atol=1e-8))
    # C3: pinned IndexRaBitQ deterministic (no seed-bearing randomness) -> panel must be runner-side
    c0 = faiss.vector_to_array(_train_add_codes(Xf, False).codes).copy()
    c1 = faiss.vector_to_array(_train_add_codes(Xf, False).codes).copy()
    r["C3_index_deterministic"] = bool(np.array_equal(c0, c1))
    # C4: faiss wrapper rotation exposes no seed API; repeat trains identical
    w0 = FSEQ_A5_build(Xf); w1 = FSEQ_A5_build(Xf)
    cw0 = faiss.vector_to_array(faiss.downcast_index(w0.index).codes).copy()
    cw1 = faiss.vector_to_array(faiss.downcast_index(w1.index).codes).copy()
    r["C4_wrapper_repeat_identical"] = bool(np.array_equal(cw0, cw1))
    r["C4_wrapper_has_seed_api"] = bool(hasattr(faiss.RandomRotationMatrix(32, 32), "seed"))
    rt = faiss.RandomRotationMatrix(32, 32); rt.train(Xf)
    A = faiss.vector_to_array(rt.A).reshape(32, 32)
    r["C4_wrapper_orthonormal"] = bool(np.allclose(A @ A.T, np.eye(32), atol=1e-5))
    # C5: wrapper nontrivial (changes codes vs no-rotation) + query-path equivalence
    cnorot = faiss.vector_to_array(_train_add_codes(Xf, False).codes).copy()
    r["C5_wrapper_nontrivial"] = bool(not np.array_equal(cw0, cnorot))
    idx = FSEQ_A5_build(Xf)
    q = Xf[0]
    Dw, Iw = FSEQ_A5_query(idx, q, 200)
    # faiss row-vector convention: wrapper rotates by A.T (diagnosed: X@A.T allclose,
    # maxdiff ~1e-7; X@A is wrong). Manual twin matches up to fp rounding, not bit-exact.
    man = FSEQ_A4_build((Xf @ A.T).astype(np.float32))
    Dm, Im = FSEQ_A4_query(man, (q @ A.T).astype(np.float32), 200)
    dw = full_dist_from_search(Dw, Iw, 200); dm = full_dist_from_search(Dm, Im, 200)
    r["C5_manual_maxdistdiff"] = float(np.max(np.abs(dw - dm)))
    r["C5_querypath_equal"] = bool(np.allclose(dw, dm, atol=1e-4))
    r["C5_convention"] = "wrapper rotates row-vectors by stored-A-transpose (X@A.T)" 
    # C6: pinned-IndexRaBitQ query path == manual rotate + flat index (same order/distances)
    r["C6_pass"] = r["C5_querypath_equal"]
    crit = [r["C1_pass"], r["C1b_regen_identical"], r["C2_dist_preserved"],
            r["C3_index_deterministic"], r["C4_wrapper_repeat_identical"],
            r["C4_wrapper_orthonormal"], r["C5_wrapper_nontrivial"], r["C5_querypath_equal"]]
    r["criteria"] = crit
    assert all(crit), r
    r["verdict"] = ("PASS 8/8: runner rotation orthonormal+regenerable+distance-preserving; "
                    "wrapper convention X@A.T diagnosed; "
                    "pinned IndexRaBitQ deterministic (panel is runner-side by necessity); "
                    "faiss wrapper orthonormal, nontrivial, unseeded, query-path equivalent")
    SMOKE["S7"] = r
    log("S7 rotation chain PASS 8/8")
    return r

def _train_add_codes(Xf, _unused):
    idx = faiss.IndexRaBitQ(32)
    idx.train(Xf)
    idx.add(Xf)
    return idx

# ---------------- S1 anchors + full-benchmark eval ----------------
def eval_sign_lme(items):
    per_q, per_trials = {}, {}
    for it in items:
        d = sign_dist_lme(it["C"], it["qC"])
        pris = [trial_priorities(it["N"], LME_TIE_BASE + it["lex"] * 100_000 + t * 100 + 99)
                for t in range(NT)]
        m, tr = fr_from_dist(d, it["gold"], pris)
        per_q[it["qid"]] = m
        per_trials[it["qid"]] = tr
    agg = float(np.mean([per_q[it["qid"]] for it in items]))
    return agg, per_q, per_trials

def eval_sign_locomo(L):
    convs, reps, Q, valid = L["convs"], L["reps"], L["Q"], L["valid_qids"]
    dist_all = {ci: sign_dist_matrix(r["C"], np.asarray(r["QC"])) for ci, r in enumerate(reps)}
    per_q = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        N = int(r["C"].shape[0])
        dist = dist_all[ci]
        pris = [trial_priorities(N, STABLE_ARCHIVE_SEED(ci, t) + 99) for t in range(NT)]
        for qi, q in enumerate(c["qas"]):
            ag = Q[q["question_id"]]["ag"]
            if ag:
                m, _ = fr_from_dist(dist[qi], ag, pris)
            else:
                m = float("nan")   # invalid question: excluded from aggregate (r2c valid=1535)
            per_q[q["question_id"]] = m
    agg = float(np.mean([per_q[q] for q in valid]))
    return agg, per_q

def smoke_S1():
    log("loading frozen benchmarks...")
    items, _lex = load_lme()
    L = load_locomo()
    log(f"LME archives={len(items)} LoCoMo convs=10 valid_q={len(L['valid_qids'])} "
        f"corrections={L['n_corrections']}")
    assert len(items) == 470 and len(L["valid_qids"]) == 1535, "cohort mismatch -> abort"
    t0 = time.time()
    lme_agg, lme_perq, _tr = eval_sign_lme(items)
    loco_agg, loco_perq = eval_sign_locomo(L)
    dt = time.time() - t0
    r = {"lme": lme_agg, "lme_anchor": LME_ANCHOR, "lme_diff": lme_agg - LME_ANCHOR,
         "locomo": loco_agg, "locomo_anchor": LOCOMO_ANCHOR,
         "locomo_diff": loco_agg - LOCOMO_ANCHOR, "eval_s": dt}
    log(f"S1 native LME={lme_agg!r} diff={r['lme_diff']!r}; "
        f"LoCoMo={loco_agg!r} diff={r['locomo_diff']!r} ({dt:.1f}s)")
    assert abs(r["lme_diff"]) <= ANCHOR_TOL, "LME anchor abort"
    assert abs(r["locomo_diff"]) <= ANCHOR_TOL, "LoCoMo anchor abort"
    # wrong-anchor negative control demo
    try:
        assert abs(lme_agg - (LME_ANCHOR + 1e-6)) <= ANCHOR_TOL
        r["anchor_abort_demo"] = "FAIL: abort did not fire"
    except AssertionError:
        r["anchor_abort_demo"] = "PASS: wrong anchor aborts"
    SMOKE["S1"] = r
    return items, L, lme_perq, loco_perq

# ---------------- Arm evaluation engine ----------------
def ckpt_path(name):
    return CKPT / f"{name}.json"

def ckpt_load(name):
    p = ckpt_path(name)
    if p.exists():
        return json.load(open(p))
    return None

def ckpt_save(name, obj):
    json.dump(obj, open(ckpt_path(name), "w"), sort_keys=True)

def eval_queries_lme(items, dist_fn):
    """dist_fn(C, qC, ctx) -> (N,) float distances. Returns {qid: (mean, trials)}."""
    out = {}
    for it in items:
        d = dist_fn(it["C"], it["qC"])
        pris = [trial_priorities(it["N"], LME_TIE_BASE + it["lex"] * 100_000 + t * 100 + 99)
                for t in range(NT)]
        out[it["qid"]] = fr_from_dist(d, it["gold"], pris)
    return out

def eval_queries_locomo(L, dist_ctx):
    """dist_ctx(ci, r, qi, qd) -> (N,) float distances. Returns {qid: mean}."""
    convs, reps, Q = L["convs"], L["reps"], L["Q"]
    out = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        N = int(r["C"].shape[0])
        pris = [trial_priorities(N, STABLE_ARCHIVE_SEED(ci, t) + 99) for t in range(NT)]
        for qi, q in enumerate(c["qas"]):
            ag = Q[q["question_id"]]["ag"]
            if not ag:
                out[q["question_id"]] = float("nan")
                continue
            d = dist_ctx(ci, r, qi, q)
            m, _ = fr_from_dist(d, ag, pris)
            out[q["question_id"]] = m
    return out

# ---- A4 contexts ----
class CtxA4:
    """Spread-32 or random-32 axes + runner-side seeded rotation; frozen FSEQ_A4."""
    def __init__(self, axes_mode, seed):
        assert axes_mode in ("spread", "random")
        self.axes_mode = axes_mode
        self.seed = seed
        self.R = seeded_rotation(seed)
        self.gcols = random_cols(seed, 32) if axes_mode == "random" else None
        self.codes_hash = hashlib.sha256()
        self.n_arch = 0

    def cols(self, C):
        if self.axes_mode == "spread":
            return spread_cols(np.asarray(C, dtype=np.float64).var(axis=0), 32)
        return self.gcols

    def lme_dist(self, C, qC):
        cols = self.cols(C)
        Xr = (np.asarray(C, dtype=np.float64)[:, cols] @ self.R)
        qr = (np.asarray(qC, dtype=np.float64)[cols] @ self.R)
        Xf = np.ascontiguousarray(Xr, dtype=np.float32)
        idx = FSEQ_A4_build(Xf)
        self.codes_hash.update(faiss.vector_to_array(idx.codes).tobytes())
        self.n_arch += 1
        D, I = FSEQ_A4_query(idx, qr.astype(np.float32), Xf.shape[0])
        return full_dist_from_search(D, I, Xf.shape[0])

    def loco_make(self, r):
        C = np.asarray(r["C"], dtype=np.float64)
        QC = np.asarray(r["QC"], dtype=np.float64)
        cols = self.cols(C)
        Xr = C[:, cols] @ self.R
        Qr = QC[:, cols] @ self.R
        Xf = np.ascontiguousarray(Xr, dtype=np.float32)
        idx = FSEQ_A4_build(Xf)
        self.codes_hash.update(faiss.vector_to_array(idx.codes).tobytes())
        self.n_arch += 1
        return Xf, Qr.astype(np.float32), idx

def run_A4(items, L, axes_mode, seed, ckpt_name):
    hit = ckpt_load(ckpt_name)
    if hit is not None:
        log(f"{ckpt_name}: checkpoint hit")
        return hit
    ctx = CtxA4(axes_mode, seed)
    t0 = time.time()
    lme = eval_queries_lme(items, ctx.lme_dist)
    built = {}
    def locodist(ci, r, qi, q):
        if ci not in built:
            built[ci] = ctx.loco_make(r)
        Xf, Qr, idx = built[ci]
        D, I = FSEQ_A4_query(idx, Qr[qi], Xf.shape[0])
        return full_dist_from_search(D, I, Xf.shape[0])
    loco = eval_queries_locomo(L, locodist)
    rec = {"arm": "A4", "axes": axes_mode, "seed": seed,
           "lme": {q: v[0] for q, v in lme.items()},
           "locomo": loco,
           "codes_sha256": ctx.codes_hash.hexdigest(), "n_arch": ctx.n_arch,
           "seconds": time.time() - t0,
           "cols_lme0": [int(x) for x in ctx.cols(items[0]["C"])]}
    ckpt_save(ckpt_name, rec)
    log(f"{ckpt_name}: done LME={np.mean(list(rec['lme'].values())):.6f} "
        f"LoCoMo={np.nanmean(list(rec['locomo'].values())):.6f} ({rec['seconds']:.1f}s)")
    return rec

# ---- A5 context ----
class CtxA5:
    def __init__(self):
        self.codes_hash = hashlib.sha256()
        self.n_arch = 0
        self.S0 = None

    def lme_dist(self, C, qC):
        cols = spread_cols(np.asarray(C, dtype=np.float64).var(axis=0), 32)
        Xf = np.ascontiguousarray(np.asarray(C, dtype=np.float64)[:, cols], dtype=np.float32)
        idx = FSEQ_A5_build(Xf)
        if self.S0 is None:
            self.S0 = len(faiss.serialize_index(_empty_like(idx, Xf)))
        self.codes_hash.update(faiss.vector_to_array(faiss.downcast_index(idx.index).codes).tobytes())
        self.n_arch += 1
        D, I = FSEQ_A5_query(idx, np.asarray(qC, dtype=np.float64)[cols].astype(np.float32), Xf.shape[0])
        return full_dist_from_search(D, I, Xf.shape[0])

def _empty_like(idx, Xf):
    rt = faiss.RandomRotationMatrix(32, 32)
    rt.train(Xf[:32])
    return faiss.IndexPreTransform(rt, faiss.IndexRaBitQ(32))

def run_A5(items, L, ckpt_name):
    hit = ckpt_load(ckpt_name)
    if hit is not None:
        log(f"{ckpt_name}: checkpoint hit")
        return hit
    ctx = CtxA5()
    t0 = time.time()
    lme = eval_queries_lme(items, ctx.lme_dist)
    built = {}
    def locodist(ci, r, qi, q):
        if ci not in built:
            C = np.asarray(r["C"], dtype=np.float64)
            cols = spread_cols(C.var(axis=0), 32)
            Xf = np.ascontiguousarray(C[:, cols], dtype=np.float32)
            Qf = np.ascontiguousarray(np.asarray(r["QC"], dtype=np.float64)[:, cols], dtype=np.float32)
            built[ci] = (Xf, Qf, FSEQ_A5_build(Xf))
        Xf, Qf, idx = built[ci]
        D, I = FSEQ_A5_query(idx, Qf[qi], Xf.shape[0])
        return full_dist_from_search(D, I, Xf.shape[0])
    loco = eval_queries_locomo(L, locodist)
    rec = {"arm": "A5", "lme": {q: v[0] for q, v in lme.items()}, "locomo": loco,
           "codes_sha256": ctx.codes_hash.hexdigest(), "n_arch": ctx.n_arch,
           "seconds": time.time() - t0}
    ckpt_save(ckpt_name, rec)
    log(f"{ckpt_name}: done LME={np.mean(list(rec['lme'].values())):.6f} "
        f"LoCoMo={np.nanmean(list(rec['locomo'].values())):.6f} ({rec['seconds']:.1f}s)")
    return rec

# ---- A6 PQ with mask policy ----
class CtxA6:
    def __init__(self):
        self.codes_hash = hashlib.sha256()
        self.n_arch = 0
        self.masked = []

    def build_arch(self, key, Xf):
        try:
            idx = FSEQ_A6_build(Xf)
        except PQMasked as e:
            self.masked.append({"archive": key, "reason": str(e), "N": int(Xf.shape[0])})
            return None
        self.codes_hash.update(faiss.vector_to_array(idx.codes).tobytes())
        self.n_arch += 1
        return idx

def run_A6(items, L, ckpt_name):
    hit = ckpt_load(ckpt_name)
    if hit is not None:
        log(f"{ckpt_name}: checkpoint hit")
        return hit
    ctx = CtxA6()
    t0 = time.time()
    lme, masked_q = {}, 0
    for it in items:
        Xf = np.ascontiguousarray(np.asarray(it["C"], dtype=np.float64), dtype=np.float32)
        idx = ctx.build_arch(it["qid"], Xf)
        if idx is None:
            m = float("nan"); masked_q += 1
        else:
            qf = np.ascontiguousarray(np.asarray(it["qC"], dtype=np.float64), dtype=np.float32)
            D, I = FSEQ_A6_query(idx, qf, Xf.shape[0])
            d = full_dist_from_search(D, I, Xf.shape[0])
            pris = [trial_priorities(it["N"], LME_TIE_BASE + it["lex"] * 100_000 + t * 100 + 99)
                    for t in range(NT)]
            m, _ = fr_from_dist(d, it["gold"], pris)
        lme[it["qid"]] = m
    built = {}
    def locodist(ci, r, qi, q):
        if ci not in built:
            Xf = np.ascontiguousarray(np.asarray(r["C"], dtype=np.float64), dtype=np.float32)
            built[ci] = (Xf, FSEQ_A6_build_logged(ctx, ci, Xf),
                         np.ascontiguousarray(np.asarray(r["QC"], dtype=np.float64), dtype=np.float32))
        Xf, idx, Qf = built[ci]
        if idx is None:
            return None
        D, I = FSEQ_A6_query(idx, Qf[qi], Xf.shape[0])
        return full_dist_from_search(D, I, Xf.shape[0])
    convs, reps, Q = L["convs"], L["reps"], L["Q"]
    loco = {}
    for ci, (c, r) in enumerate(zip(convs, reps)):
        N = int(r["C"].shape[0])
        pris = [trial_priorities(N, STABLE_ARCHIVE_SEED(ci, t) + 99) for t in range(NT)]
        for qi, q in enumerate(c["qas"]):
            ag = Q[q["question_id"]]["ag"]
            if not ag:
                loco[q["question_id"]] = float("nan")
                continue
            d = locodist(ci, r, qi, q)
            if d is None:
                loco[q["question_id"]] = float("nan")   # masked archive
                continue
            m, _ = fr_from_dist(d, ag, pris)
            loco[q["question_id"]] = m
    rec = {"arm": "A6", "lme": lme, "locomo": loco,
           "masked_archives": ctx.masked, "masked_lme_q": masked_q,
           "codes_sha256": ctx.codes_hash.hexdigest(), "n_arch": ctx.n_arch,
           "seconds": time.time() - t0}
    ckpt_save(ckpt_name, rec)
    lv = [v for v in lme.values() if np.isfinite(v)]
    lov = [v for v in loco.values() if np.isfinite(v)]
    log(f"{ckpt_name}: done LME={np.mean(lv):.6f} (masked_q={masked_q}) "
        f"LoCoMo={np.mean(lov):.6f} masked_arch={len(ctx.masked)} ({rec['seconds']:.1f}s)")
    return rec

def FSEQ_A6_build_logged(ctx, ci, Xf):
    return ctx.build_arch(f"locomo_{ci}", Xf)

# ---------------- S4 PQ min-N + S5 determinism ----------------
def smoke_S4(items, L):
    r = {}
    lme_N = {it["qid"]: it["N"] for it in items}
    r["lme_min_N"] = int(min(lme_N.values()))
    r["lme_min_qid"] = min(lme_N, key=lme_N.get)
    r["lme_N_range"] = [int(min(lme_N.values())), int(max(lme_N.values()))]
    loco_N = {f"locomo_{ci}": int(L["reps"][ci]["C"].shape[0]) for ci in range(10)}
    r["locomo_archive_N"] = loco_N
    r["locomo_min_N"] = int(min(loco_N.values()))
    r["locomo_min_arch"] = min(loco_N, key=loco_N.get)
    # attempt PQ train on each benchmark's min-N archive (mask policy fires if it fails)
    for tag, Xf in [
        ("lme_min", np.ascontiguousarray(
            np.asarray(next(it for it in items if it["qid"] == r["lme_min_qid"])["C"],
                       dtype=np.float64), dtype=np.float32)),
        ("locomo_min", np.ascontiguousarray(
            np.asarray(L["reps"][int(r["locomo_min_arch"].split("_")[1])]["C"],
                       dtype=np.float64), dtype=np.float32)),
    ]:
        try:
            idx = FSEQ_A6_build(Xf)
            r[tag] = {"N": int(Xf.shape[0]), "train": "OK",
                      "S0_measured": len(faiss.serialize_index(_pq_empty_trained(Xf))),
                      "marginal": (len(faiss.serialize_index(idx)) -
                                   len(faiss.serialize_index(_pq_empty_trained(Xf)))) / Xf.shape[0]}
        except PQMasked as e:
            r[tag] = {"N": int(Xf.shape[0]), "train": f"MASKED: {e}"}
    SMOKE["S4"] = r
    log(f"S4 min-N: LME min={r['lme_min_N']} ({r['lme_min']['train']}); "
        f"LoCoMo min={r['locomo_min_N']} @ {r['locomo_min_arch']} ({r['locomo_min']['train']})")
    return r

def _pq_empty_trained(Xf):
    idx = faiss.IndexPQ(96, PQ_M, PQ_NBITS)
    idx.train(Xf)
    return idx

def smoke_S5(items, L):
    """Retrain+rerun fixed seeds/threads -> bit-identical codes + FR (incl. cross-process)."""
    r = {}
    it = items[0]
    C, qC = it["C"], it["qC"]
    cols = spread_cols(np.asarray(C, dtype=np.float64).var(axis=0), 32)
    # A4 repeat
    def a4_once():
        R = seeded_rotation(ROTATION_SEEDS_PRIMARY[0])
        Xf = np.ascontiguousarray((np.asarray(C, dtype=np.float64)[:, cols] @ R), dtype=np.float32)
        qf = (np.asarray(qC, dtype=np.float64)[cols] @ R).astype(np.float32)
        idx = FSEQ_A4_build(Xf)
        D, I = FSEQ_A4_query(idx, qf, Xf.shape[0])
        d = full_dist_from_search(D, I, Xf.shape[0])
        pris = [trial_priorities(it["N"], LME_TIE_BASE + it["lex"] * 100_000 + t * 100 + 99)
                for t in range(NT)]
        m, _ = fr_from_dist(d, it["gold"], pris)
        return faiss.vector_to_array(idx.codes).tobytes(), m
    c1, m1 = a4_once(); c2, m2 = a4_once()
    r["A4_codes_identical"] = bool(c1 == c2)
    r["A4_FR_identical"] = bool(m1 == m2)
    # A6 repeat (clustering seed default -> deterministic?)
    Xf96 = np.ascontiguousarray(np.asarray(C, dtype=np.float64), dtype=np.float32)
    qf96 = np.ascontiguousarray(np.asarray(it["qC"], dtype=np.float64), dtype=np.float32)
    def a6_once():
        idx = FSEQ_A6_build(Xf96)
        D, I = FSEQ_A6_query(idx, qf96, Xf96.shape[0])
        return faiss.vector_to_array(idx.codes).tobytes()
    p1, p2 = a6_once(), a6_once()
    r["A6_codes_identical"] = bool(p1 == p2)
    r["A6_codebook_policy"] = ("faiss default clustering seed is fixed -> deterministic; "
                               "no explicit seed API used; repeat-train identical")
    # cross-process check: rebuild A4 codes in a fresh interpreter, compare sha
    h1 = hashlib.sha256(c1).hexdigest()
    helper = (f"import numpy as np,pickle,faiss,hashlib;"
              f"faiss.omp_set_num_threads(1);"
              f"o=pickle.load(open('{Path(WORK)/LME_PKL_DIR}/{it['qid']}.pkl','rb'));"
              f"C=np.asarray(o['C']);qC=np.asarray(o['qC']);"
              f"od=np.argsort(C.var(axis=0),kind='stable')[::-1];"
              f"cols=od[np.round(np.linspace(0,95,32)).astype(int)];"
              f"A=np.random.default_rng({ROTATION_SEEDS_PRIMARY[0]}).standard_normal((32,32));"
              f"Q,Rm=np.linalg.qr(A);R=Q*np.where(np.diag(Rm)<0,-1.0,1.0)[None,:];"
              f"Xf=np.ascontiguousarray((C[:,np.sort(cols)]@R),dtype=np.float32);"
              f"idx=faiss.IndexRaBitQ(32);idx.train(Xf);idx.add(Xf);"
              f"print(hashlib.sha256(faiss.vector_to_array(idx.codes).tobytes()).hexdigest())")
    import subprocess as _sp
    q2 = _sp.run(["/home/mdp/muse-work/faiss-python", "-c", helper],
                 capture_output=True, text=True, timeout=300)
    r["crossproc_stdout"] = (q2.stdout or "").strip().splitlines()[-1] if q2.stdout else ""
    r["crossproc_stderr_tail"] = (q2.stderr or "").strip().splitlines()[-3:]
    r["A4_crossproc_identical"] = bool(r["crossproc_stdout"] == h1)
    assert r["A4_codes_identical"] and r["A4_FR_identical"] and r["A6_codes_identical"] \
        and r["A4_crossproc_identical"], r
    r["verdict"] = "PASS: retrain/rerun bit-identical codes+FR, incl. fresh-process A4"
    SMOKE["S5"] = r
    log("S5 determinism PASS (in-process A4/A6 + cross-process A4)")
    return r

# ---------------- Aggregates / WTL ----------------
def wtl(per_arm, per_ref):
    qs = [q for q in per_ref if np.isfinite(per_ref[q]) and q in per_arm
          and np.isfinite(per_arm[q])]
    gap = np.array([per_arm[q] - per_ref[q] for q in qs])
    W = int(np.sum(gap > WTL_TOL)); T = int(np.sum(np.abs(gap) <= WTL_TOL))
    L = int(np.sum(gap < -WTL_TOL))
    return {"n": len(qs), "W": W, "T": T, "L": L,
            "mean_gap_pp": float(np.mean(gap) * 100) if len(gap) else float("nan"),
            "tie_share": float(T / len(gap)) if len(gap) else float("nan")}

def agg_finite(d):
    v = [x for x in d.values() if np.isfinite(x)]
    return float(np.mean(v)) if v else float("nan"), len(v)

# ---------------- main ----------------
def main():
    t_all = time.time()
    log(f"faiss={faiss.__version__ if hasattr(faiss, '__version__') else '?'} "
        f"threads={FAISS_THREADS}")
    items, L, lme_nat, loco_nat = smoke_S1()          # S1 (abort gates inside)
    smoke_S3()                                         # S3 trap controls
    pool = np.vstack([np.asarray(items[i]["C"][:3], dtype=np.float64)
                      for i in range(len(items))])   # S2 pooled sample: 470x3x96
    smoke_S2(pool)
    smoke_S7(np.asarray(items[0]["C"], dtype=np.float64)[:, :32])  # S7 chain
    smoke_S4(items, L)                                 # S4 min-N
    smoke_S5(items, L)                                 # S5 determinism
    arms = {}
    for s in ROTATION_SEEDS_PRIMARY:                   # A4 primary: spread-32 x 3 rotations
        arms[f"A4_spread_rot{s}"] = run_A4(items, L, "spread", s, f"A4_spread_{s}")
    for s in AXES_SEEDS_SECONDARY:                     # A4 secondary: random-32 x 3 axes seeds
        arms[f"A4_random_axes{s}"] = run_A4(items, L, "random", s, f"A4_random_{s}")
    arms["A5_wrapper"] = run_A5(items, L, "A5_wrapper")  # A5 wrapper (unseeded, deterministic)
    arms["A6_PQ"] = run_A6(items, L, "A6_PQ")            # A6 PQ plain + mask policy
    summary = {}
    for name, rec in arms.items():
        a_lme, n_lme = agg_finite(rec["lme"])
        a_lo, n_lo = agg_finite({k: v for k, v in rec["locomo"].items()})
        summary[name] = {
            "LME_FR": a_lme, "LME_n": n_lme,
            "LoCoMo_FR": a_lo, "LoCoMo_n": n_lo,
            "WTL_vs_SIGN_LME": wtl(rec["lme"], lme_nat),
            "WTL_vs_SIGN_LoCoMo": wtl(rec["locomo"], loco_nat),
            "codes_sha256": rec["codes_sha256"], "seconds": rec["seconds"],
            "masked": rec.get("masked_archives", []),
        }
    details = {
        "constants": {
            "K": K, "NT": NT, "WTL_TOL": WTL_TOL, "ANCHOR_TOL": ANCHOR_TOL,
            "LME_ANCHOR": LME_ANCHOR, "LOCOMO_ANCHOR": LOCOMO_ANCHOR,
            "ROTATION_SEEDS_PRIMARY": ROTATION_SEEDS_PRIMARY,
            "AXES_SEEDS_SECONDARY": AXES_SEEDS_SECONDARY,
            "PQ": [96, PQ_M, PQ_NBITS], "THREADS": FAISS_THREADS,
            "faiss_calls": ["IndexRaBitQ(32).train/add/search(k=N)",
                            "IndexPreTransform(RandomRotationMatrix.train, IndexRaBitQ).train/add/search",
                            "IndexPQ(96,12,8).train/add/search(k=N)"],
            "tie": "exact float equality; lexsort((priority, distance)) distance-primary",
            "note": "HR-named TOP32 not used; spread-32 proposed (s8.7 deviation, flagged)",
        },
        "smokes": SMOKE,
        "native": {"LME_FR": SMOKE["S1"]["lme"], "LoCoMo_FR": SMOKE["S1"]["locomo"],
                   "lme_per_q": lme_nat, "locomo_per_q": loco_nat},
        "arms_summary": summary,
        "arms_per_q": {n: {"lme": r["lme"], "locomo": r["locomo"]} for n, r in arms.items()},
        "timing_s": time.time() - t_all,
    }
    json.dump(details, open(OUT / "race_faiss_details.json", "w"), sort_keys=True)
    (OUT / "smoke_log.txt").write_text("\n".join(LOG_LINES) + "\n", encoding="utf-8")
    env = env_record()
    (OUT / "environment.txt").write_text(env, encoding="utf-8")
    print(env, flush=True)
    files = ["race_faiss.py", "race_faiss_details.json", "smoke_log.txt", "environment.txt"]
    man = {f: sha256_file(OUT / f) for f in files}
    json.dump(man, open(OUT / "hash_manifest.json", "w"), indent=2, sort_keys=True)
    log("manifest: " + json.dumps(man, sort_keys=True))
    verdict(summary)
    log(f"TOTAL {time.time() - t_all:.1f}s")

def env_record():
    import numpy
    try:
        blas = numpy.show_config(mode="dicts")["Build Dependencies"]["blas"]["version"]
    except Exception:
        blas = "unknown"
    return (f"python={sys.version.split()[0]} numpy={numpy.__version__} "
            f"faiss=1.15.0 threads={FAISS_THREADS} BLAS={blas} "
            f"OS={_os.uname().sysname}-{_os.uname().release} "
            f"faiss_path={faiss.__file__ if hasattr(faiss, '__file__') else 'fpylibs'}\n")

def verdict(summary):
    print("RB3_VERDICT:", flush=True)
    s = SMOKE
    print(f" bytes: RQ96={s['S2']['RaBitQuantizer96_code_size']}B RQ32={s['S2']['RaBitQuantizer32_code_size']}B "
          f"PQ={s['S2']['IndexPQ96_12_8_code_size']}B EXT2={s['S2']['RaBitQuantizer96_L2_2_code_size']}B; "
          f"S0={s['S2']['RQ32']['S0']}/{s['S2']['RQ96']['S0']}/{s['S2']['PQ']['S0']}; "
          f"S(n)-S0==n*decl PASS; mismatch-abort {s['S2']['mismatch_abort_demo'][:4]}; "
          f"S3 {s['S3']['verdict'][:40]}...", flush=True)
    print(f" minN: LME min-N={s['S4']['lme_min_N']} train={s['S4']['lme_min']['train']}; "
          f"LoCoMo min-N={s['S4']['locomo_min_N']}@{s['S4']['locomo_min_arch']} "
          f"train={s['S4']['locomo_min']['train']}; "
          f"A6 masked_archives={summary['A6_PQ']['masked']}", flush=True)
    print(f" determinism: {s['S5']['verdict']}", flush=True)
    for name, v in summary.items():
        print(f" {name}: LME={v['LME_FR']:.6f}(n={v['LME_n']}) "
              f"LoCoMo={v['LoCoMo_FR']:.6f}(n={v['LoCoMo_n']}) "
              f"WTL_LME={v['WTL_vs_SIGN_LME']['W']}/{v['WTL_vs_SIGN_LME']['T']}/{v['WTL_vs_SIGN_LME']['L']} "
              f"WTL_LOCO={v['WTL_vs_SIGN_LoCoMo']['W']}/{v['WTL_vs_SIGN_LoCoMo']['T']}/{v['WTL_vs_SIGN_LoCoMo']['L']}",
              flush=True)
    print(f" rotation-chain: {s['S7']['verdict']}", flush=True)

if __name__ == "__main__":
    main()
