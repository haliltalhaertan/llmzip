#!/usr/bin/env python3
"""Local-session harness — LoCoMo frozen representation regeneration + Task1 statistics.

Imports the byte-frozen T4D module (extracted from V52_T4D_ALL_OUTPUTS.zip) and calls its own
build_representation() to regenerate the 10 per-conversation native matrices
C = normalize(SVD96(seed 5204)([latent32|word|char])) − archive mean. No retrieval is run;
no top-3 IDs, distances or recalls are touched.

Cross-validation: the regenerated per-conversation feature counts (N, word/char/latent/mixed
feature counts, query counts) are compared against V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt,
which is a measurement output of the original seal-stage run.

Modes: gate | run | stats
"""
import argparse
import hashlib
import importlib.util
import io
import json
import pickle
import sys
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
DRIVE = WORK / "drive"
OUT = WORK / "regen" / "locomo"

T4D_SCRIPT = DRIVE / "v52_t4d_locomo_frozen_cross_benchmark.py"
RAW = DRIVE / "locomo10.json"
AUDIT = DRIVE / "audit_layer"
PROOF = DRIVE / "t4d" / "V52_T4D_REPRESENTATION_TRANSFER_PROOF.txt"

RAW_SHA = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
RAW_BYTES = 2805274
AUDIT_MANIFEST_SHA = "90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06"
EXPECTED_CONVS = 10
EXPECTED_QUESTIONS = 1540


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_t4d():
    spec = importlib.util.spec_from_file_location("frozen_t4d", str(T4D_SCRIPT))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def gate():
    m = load_t4d()
    problems = []
    got = sha256_file(RAW)
    if got != RAW_SHA or RAW.stat().st_size != RAW_BYTES:
        problems.append(f"raw: {got} {RAW.stat().st_size}")
    print(f"  [{'OK' if got == RAW_SHA else 'BAD'}] raw locomo10.json sha256 + bytes")
    rows, manifest = m.audit_layer_manifest(AUDIT)
    if manifest != AUDIT_MANIFEST_SHA:
        problems.append(f"audit manifest: {manifest}")
    print(f"  [{'OK' if manifest == AUDIT_MANIFEST_SHA else 'BAD'}] audit layer manifest ({len(rows)} files)")
    # frozen script identity: check against the T4D pre-run seal's sealed_compute_script_sha256
    seal = json.loads((DRIVE / "t4d" / "V52_T4D_PRE_RUN_SEAL.json").read_text())
    want = seal.get("sealed_compute_script_sha256")
    got = sha256_file(T4D_SCRIPT)
    if want != got:
        problems.append(f"t4d script sha: got {got} seal-says {want}")
    print(f"  [{'OK' if want == got else 'BAD'}] T4D script sha256 == seal sealed_compute_script_sha256")
    arr = json.loads(RAW.read_text(encoding="utf-8"))
    convs = [m.raw_item_to_conv(x, i) for i, x in enumerate(arr)]
    nq_all = sum(len(c["qas"]) for c in convs)
    cat_counts = {}
    for c in convs:
        for q in c["qas"]:
            cat_counts[q["category"]] = cat_counts.get(q["category"], 0) + 1
    nq14 = sum(v for k, v in cat_counts.items() if k in (1, 2, 3, 4))
    ok_cohort = len(convs) == EXPECTED_CONVS and nq14 == EXPECTED_QUESTIONS
    if not ok_cohort:
        problems.append(f"cohort: convs {len(convs)} cat1-4 questions {nq14} (raw total {nq_all})")
    print(f"  [{'OK' if ok_cohort else 'BAD'}] cohort {len(convs)} convs / cat1-4 {nq14} (raw total incl cat5: {nq_all})")
    corr = m.load_audit_corrections(AUDIT)
    want_cats = {1: 282, 2: 321, 3: 96, 4: 841}
    cats14 = {k: v for k, v in cat_counts.items() if k in (1, 2, 3, 4)}
    if cats14 != want_cats:
        problems.append(f"category counts: {cats14}")
    print(f"  [{'OK' if cats14==want_cats else 'BAD'}] category counts 1-4 {cats14}")
    print(f"  [info] audit corrections loaded: {len(corr)} questions (expected 156)")
    if problems:
        print("GATE FAILED:"); [print("  -", p) for p in problems]; sys.exit(1)
    print("GATE: PASS")


def proof_targets():
    txt = PROOF.read_text(encoding="utf-8")
    rows = {}
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("{") and "conv_id" in line:
            r = json.loads(line)
            rows[r["conv_id"]] = r
    return rows


def run():
    m = load_t4d()
    OUT.mkdir(parents=True, exist_ok=True)
    arr = json.loads(RAW.read_text(encoding="utf-8"))
    convs = [m.raw_item_to_conv(x, i) for i, x in enumerate(arr)]
    targets = proof_targets()
    report = []
    for c in convs:
        rep = m.build_representation(c)
        cid = c["conv_id"]
        rec = {
            "conv_id": cid,
            "N": rep["N"],
            "archive_fit_docs": rep["archive_fit_docs"],
            "query_count": rep["query_count"],
            "source_word_features": rep["source_word_features"],
            "source_char_features": rep["source_char_features"],
            "source_latent_dim": rep["source_latent_dim"],
            "mixed_concat_features": rep["mixed_concat_features"],
            "mixed96_dim": rep["mixed96_dim"],
            "no_nan": rep["no_nan"],
        }
        t = targets.get(cid)
        if t:
            keys = ["N", "archive_fit_docs", "query_count", "source_word_features",
                    "source_char_features", "source_latent_dim", "mixed_concat_features", "mixed96_dim"]
            rec["counts_match_transfer_proof"] = all(rec[k] == t[k] for k in keys)
            rec["counts_mismatch_keys"] = [k for k in keys if rec[k] != t[k]]
        else:
            rec["counts_match_transfer_proof"] = None
            rec["counts_mismatch_keys"] = ["no target row"]
        C = rep["C"]
        ch = hashlib.sha256(np.ascontiguousarray(C, dtype=np.float64).tobytes()).hexdigest()
        with open(OUT / f"{cid}.pkl", "wb") as f:
            pickle.dump({"conv_id": cid, "C": C, "QC": rep["QC"], "qas": rep["qas"],
                         "id_to_row": rep["id_to_row"], "C_sha256": ch}, f, protocol=4)
        rec["C_sha256"] = ch
        rec["C_shape"] = list(C.shape)
        report.append(rec)
        print(json.dumps(rec, sort_keys=True), flush=True)
    (OUT / "counts_report.json").write_text(json.dumps(report, indent=2))
    n_match = sum(1 for r in report if r.get("counts_match_transfer_proof"))
    print(f"counts matched vs transfer proof: {n_match}/{len(report)}")
    if n_match != len(report):
        print("COUNT MISMATCH — investigate"); sys.exit(1)


def stats():
    sys.path.insert(0, str(WORK / "harness" / "ref"))
    import measure_representation_diagnostics as diag  # frozen diagnostics functions

    OUT.mkdir(parents=True, exist_ok=True)
    pkls = sorted(OUT.glob("locomo_*.pkl"))
    if len(pkls) != 10:
        print(f"stats: expected 10 conversation pkls, have {len(pkls)}"); sys.exit(1)
    rows = []
    for p in pkls:
        o = pickle.loads(p.read_bytes())
        C = o["C"]
        d = diag.matrix_diagnostics(C)
        d2 = diag.variance_diagnostics(diag.np.asarray(C).var(axis=0, ddof=0))
        v = diag.np.asarray(C, dtype=diag.np.float64).var(axis=0, ddof=0)
        occ = (diag.np.asarray(C) >= 0).mean(axis=0)
        rec = {
            "conv_id": o["conv_id"], "N": int(C.shape[0]), "dims": int(C.shape[1]),
            "zero_mass": d["zero_mass"], "sign_entropy_gt": d["sign_entropy_gt"],
            "sign_entropy_ge": d["sign_entropy_ge"], "active_coordinates": d["active_coordinates"],
            "cv_sigma": d2["cv_sigma"], "zero_variance_coordinates": d2["zero_variance_coordinates"],
            "top16_share": d2["top_variance_fraction"]["16"], "top32_share": d2["top_variance_fraction"]["32"],
            "top48_share": d2["top_variance_fraction"]["48"],
            "first32_share": d2["ordered_prefix_fraction"]["32"],
            "corr_off_mass": d["correlation_proxy"]["off_mass"] if d["correlation_proxy"] else None,
            "corr_median_abs": d["correlation_proxy"]["median_abs"] if d["correlation_proxy"] else None,
            "corr_p95_abs": d["correlation_proxy"]["p95_abs"] if d["correlation_proxy"] else None,
            "residual_mean_max_abs": d["residual_mean_max_abs"],
            "variance_vector": ";".join(f"{float(x):.17g}" for x in v),
            "occupancy_vector": ";".join(f"{float(x):.17g}" for x in occ),
            "C_sha256_self_computed": o.get("C_sha256"),
            "C_sha256_note": "self-computed from the regenerated bytes at write time; NOT a match against any external artifact",
        }
        rows.append(rec)
        print(json.dumps({k: v for k, v in rec.items() if not k.endswith("_vector")}), flush=True)
    # summaries in the same shape as the frozen diagnostics script
    def summary(key):
        vals = [r[key] for r in rows if r[key] is not None]
        a = np.asarray(vals, dtype=np.float64)
        return {"valid_archives": len(a), "missing_archives": len(rows) - len(a),
                "mean": float(a.mean()), "sd_ddof1": float(a.std(ddof=1)) if len(a) > 1 else None,
                "min": float(a.min()), "max": float(a.max())}
    out = {
        "status": "LOCAL SESSION — LoCoMo frozen-representation regeneration statistics (certified construction)",
        "source": {"raw_sha256": RAW_SHA, "audit_manifest_sha256": AUDIT_MANIFEST_SHA,
                    "producer_sha256": sha256_file(T4D_SCRIPT)},
        "archive_count": len(rows), "dimensions": 96,
        "D1_ge": summary("sign_entropy_ge"), "D1_gt": summary("sign_entropy_gt"),
        "zero_mass": summary("zero_mass"), "D2_cv_sigma": summary("cv_sigma"),
        "D3_top16": summary("top16_share"), "D3_top32": summary("top32_share"), "D3_top48": summary("top48_share"),
        "D3_first32": summary("first32_share"),
        "D4_off_mass": summary("corr_off_mass"), "D4_median_abs": summary("corr_median_abs"),
        "D4_p95_abs": summary("corr_p95_abs"),
        "archives": rows,
        "labels": ["[LOCAL SESSION — NOT AN AUDIT]", "[CERTIFIED CONSTRUCTION REGENERATION]",
                    "LoCoMo has no frozen value-level artifact; these are the first value-level "
                    "outputs (vectors included) from a re-execution certified by 10/10 counts."],
    }
    (OUT / "task1_locoMo_stats.json").write_text(json.dumps(out, indent=2))
    print("wrote", OUT / "task1_locoMo_stats.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["gate", "run", "stats"])
    a = ap.parse_args()
    if a.mode == "gate":
        gate()
    elif a.mode == "run":
        run()
    elif a.mode == "stats":
        stats()


if __name__ == "__main__":
    main()
