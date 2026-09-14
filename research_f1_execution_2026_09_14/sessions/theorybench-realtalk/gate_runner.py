#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

GATE runner (BEFORE intervention): recompute ORIGINAL native SIGN96 and
centered-float96 fractional R@3 from read-only rt_repr caches using the EXACT
frozen conventions of producer_run_realtalk.py (copy of run_realtalk.py):

- K=3, NT=20, tie_seed(ci,t)=5_100_000+ci*100_000+t*100+99, ci=0-based chat
  ordinal in lexical file order (here RT01..RT10 file order = lexical pkl order).
- Native SIGN96: Hamming distance on sign(C)/sign(qC) i.e. C>=0 / q>=0 mismatch
  counts; rank lexsort((p, d)).
- float96: cosine_centered(C,q) float64; rank lexsort((p, -scores)).
- Invalid QAs (0 resolved gold): FR=null, EXCLUDED from means.
- Anchors: native 0.22477507598784194, float 0.17253405381064957 (705 of 728).
- Tolerance 1e-12 per-QA max abs diff vs details.json + mean anchors.

Also provenance: RT05 cache-format check (adapter keys) vs RT05_rebuild331.pkl
(raw frozen-T4D keys), and sign-stability between them.

Reads sources READ-ONLY. Writes gate.json + gate_receipt.txt in this workspace.
"""
import hashlib
import json
import os
import pickle
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk")
REPRDIR = SRC / "rt_repr"
K = 3
NT = 20
TOL = 1e-12
EXP_NATIVE = 0.22477507598784194
EXP_FLOAT = 0.17253405381064957


def tie_seed(ci, t):
    return 5_100_000 + ci * 100_000 + t * 100 + 99


def cosine_centered(C, q):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = float(np.linalg.norm(q))
    if qn <= 0 or np.any(dn <= 0):
        raise RuntimeError("[BUG] zero centered vector norm in cosine")
    return (C @ q) / (dn * qn)


def rank_hamming(dist, p):
    return np.lexsort((p, np.asarray(dist)))


def rank_float(scores, p):
    return np.lexsort((p, -np.asarray(scores, dtype=np.float64)))


def frac_r3(order, gold):
    gset = set(map(int, gold))
    return len(set(map(int, order[:K])) & gset) / len(gset)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    pkls = sorted(REPRDIR.glob("RT*.pkl"))
    assert len(pkls) == 10, len(pkls)
    details = json.loads((SRC / "details.json").read_text())
    assert details["n_qa"] == 728 and details["n_valid"] == 705
    exp_by_qid = {r["qid"]: r for r in details["per_qa"]}

    n_total = 0
    n_valid = 0
    n_excluded = 0
    max_nat_diff = 0.0
    max_flt_diff = 0.0
    nat_vals, flt_vals = [], []
    per_qa_worst = []
    file_order = []
    for ci, p in enumerate(pkls):
        o = pickle.loads(p.read_bytes())
        C = np.asarray(o["C"], float)
        QC = np.asarray(o["QC"], float)
        n = C.shape[0]
        D0 = C >= 0
        pris = [np.random.default_rng(tie_seed(ci, t)).random(n) for t in range(NT)]
        file_order.append(o["file"])
        for qi, qid in enumerate(o["qids"]):
            n_total += 1
            exp = exp_by_qid[qid]
            assert exp["chat"] == o["chat_no"], (qid, exp["chat"], o["chat_no"])
            assert exp["file"] == o["file"], (qid, exp["file"], o["file"])
            assert exp["N"] == n, (qid, exp["N"], n)
            gold = [int(g) for g in o["gold_rows"][qi]]
            assert exp["gold_count"] == len(gold), (qid,)
            assert exp["valid"] == int(len(gold) > 0), (qid,)
            if not gold:
                assert exp["arms"]["NATIVE96"] is None and exp["arms"]["FLOAT96"] is None
                n_excluded += 1
                continue
            n_valid += 1
            q = QC[qi]
            Q0 = q >= 0
            dnat = np.count_nonzero(D0 != Q0[None, :], axis=1)
            sscores = cosine_centered(C, q)
            nat = sum(frac_r3(rank_hamming(dnat, pr), gold) for pr in pris) / NT
            flt = sum(frac_r3(rank_float(sscores, pr), gold) for pr in pris) / NT
            dn = abs(nat - exp["arms"]["NATIVE96"])
            df = abs(flt - exp["arms"]["FLOAT96"])
            max_nat_diff = max(max_nat_diff, dn)
            max_flt_diff = max(max_flt_diff, df)
            nat_vals.append(nat)
            flt_vals.append(flt)
            per_qa_worst.append({"qid": qid, "dnat": dn, "dflt": df})

    mean_nat = float(np.mean(nat_vals))
    mean_flt = float(np.mean(flt_vals))
    d_mean_nat = abs(mean_nat - EXP_NATIVE)
    d_mean_flt = abs(mean_flt - EXP_FLOAT)
    # cross-check stored details means vs anchors too
    stored_nat = float(np.mean([r["arms"]["NATIVE96"] for r in details["per_qa"] if r["valid"]]))
    stored_flt = float(np.mean([r["arms"]["FLOAT96"] for r in details["per_qa"] if r["valid"]]))

    # provenance: cache-format vs scratch rebuild keys
    rt05 = pickle.loads((REPRDIR / "RT05.pkl").read_bytes())
    rb = pickle.loads((SRC / "RT05_rebuild331.pkl").read_bytes())
    adapter_keys = sorted(rt05.keys())
    rebuild_keys = sorted(rb.keys())
    cache_has_adapter_format = all(k in rt05 for k in
        ("chat_no", "file", "conv_id", "C", "QC", "qids", "gold_rows", "qa_diag", "id_to_row", "N"))
    rebuild_is_raw_t4d = ("archive_fit_docs" in rb) and ("qids" not in rb)
    C_cache = np.asarray(rt05["C"], dtype=np.float64)
    C_rb = np.asarray(rb["C"], dtype=np.float64)
    sign_match = bool(np.array_equal(C_cache >= 0, C_rb >= 0)) if C_cache.shape == C_rb.shape else False
    maxabs_rebuild = float(np.max(np.abs(C_cache - C_rb))) if C_cache.shape == C_rb.shape else None

    gate_pass = bool(
        n_total == 728 and n_valid == 705 and n_excluded == 23
        and max_nat_diff <= TOL and max_flt_diff <= TOL
        and d_mean_nat <= TOL and d_mean_flt <= TOL
        and cache_has_adapter_format and rebuild_is_raw_t4d and sign_match
    )
    per_qa_worst.sort(key=lambda r: -(r["dnat"] + r["dflt"]))
    gate = {
        "label": "[LOCAL EXPLORATORY PILOT]",
        "task": "REAL TALK gate BEFORE intervention (recompute originals from read-only caches)",
        "conventions": "K=3 NT=20 tie_seed=5_100_000+ci*100_000+t*100+99; sign Hamming lexsort((p,d)); float cosine_centered lexsort((p,-s)); invalid FR=null excluded",
        "n_total": n_total, "n_valid": n_valid, "n_excluded": n_excluded,
        "expected": {"n_total": 728, "n_valid": 705, "n_excluded": 23,
                     "native": EXP_NATIVE, "float": EXP_FLOAT},
        "recomputed": {"native_mean": mean_nat, "float_mean": mean_flt},
        "stored_details_means": {"native": stored_nat, "float": stored_flt},
        "max_per_qa_abs_diff": {"native": max_nat_diff, "float": max_flt_diff},
        "mean_abs_diff_vs_anchor": {"native": d_mean_nat, "float": d_mean_flt},
        "tolerance": TOL,
        "file_order": file_order,
        "provenance": {
            "rt05_cache_keys": adapter_keys,
            "rt05_rebuild_keys": rebuild_keys,
            "cache_is_adapter_format": cache_has_adapter_format,
            "rebuild_is_raw_frozen_t4d": rebuild_is_raw_t4d,
            "rt05_cache_vs_rebuild_sign_identical": sign_match,
            "rt05_cache_vs_rebuild_maxabs": maxabs_rebuild,
            "conclusion": "eval caches (rt_repr/RT*.pkl) produced by bench3_realtalk_adapter.py via frozen T4D build_representation; RT05_rebuild331.pkl is a scratch raw-T4D rebuild, not the eval input",
        },
        "worst_5_qa": per_qa_worst[:5],
        "gate_pass": gate_pass,
    }
    (HERE / "gate.json").write_text(json.dumps(gate, indent=2))
    print(json.dumps({"n_total": n_total, "n_valid": n_valid, "n_excluded": n_excluded,
                      "mean_nat": mean_nat, "mean_flt": mean_flt,
                      "max_nat_diff": max_nat_diff, "max_flt_diff": max_flt_diff,
                      "d_mean_nat": d_mean_nat, "d_mean_flt": d_mean_flt,
                      "sign_match": sign_match, "maxabs_rebuild": maxabs_rebuild,
                      "GATE_PASS": gate_pass}, indent=2))
    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
