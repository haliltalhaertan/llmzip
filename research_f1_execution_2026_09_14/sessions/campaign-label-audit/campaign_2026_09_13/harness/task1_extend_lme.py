#!/usr/bin/env python3
"""Task1 extension statistics — LongMemEval, computed from the certified regeneration.

Uses the frozen diagnostics script's OWN functions (imported verbatim from
harness/ref/measure_representation_diagnostics.py) so D1/D2/D3/D4 definitions are identical.
Extends the Task1 receipt with the three previously-missing components:
  D1_gt  — strict >0 mean sign entropy
  zero_mass — fraction of exact zeros in each frozen C matrix
  D4     — correlation-matrix statistics (off_mass, median |r|, p95 |r|) on active coordinates

Writes:
  regen/lme/task1_extension_lme.json  (per-archive rows + summaries + controls + cross-checks)
  regen/lme/task1_extension_lme.csv   (compact per-archive table)
"""
import csv
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
REGEN = WORK / "regen" / "lme"
sys.path.insert(0, str(WORK / "harness" / "ref"))
import measure_representation_diagnostics as diag  # noqa: E402


def extension_controls():
    # A: exact zero_mass on a ones matrix with a punched zero pattern
    y = np.ones((4, 96))
    y[:, 0] = [-1, 0, 0, 1]      # exactly two zeros in this column
    y[:, 1] = [-2, 2, 2, 2]      # no zeros
    d = diag.matrix_diagnostics(y)
    assert abs(d["zero_mass"] - 2 / (4 * 96)) < 1e-15, d["zero_mass"]

    # B: strict >0 vs >=0 separation with hand-computable entropies
    z = np.ones((4, 96))
    z[:, 0] = [-1, -1, 0, 0]     # p_gt = 0 -> H=0 ; p_ge = 0.5 -> H=1
    dz = diag.matrix_diagnostics(z)
    assert dz["sign_entropy_gt"] == 0.0
    assert abs(dz["sign_entropy_ge"] - (1.0 / 96.0)) < 1e-15

    # C: D4 wiring — replicate the definition inline and compare
    rng = np.random.default_rng(7)
    a = rng.standard_normal((100, 1))
    b = np.hstack([a, a, a] + [rng.standard_normal((100, 93))])
    dc = diag.matrix_diagnostics(b)
    r = np.corrcoef(b, rowvar=False)
    iu = np.triu_indices(96, 1)
    pairs = np.abs(r[iu])
    off = r - np.diag(np.diag(r))
    expected = {"off_mass": float(np.linalg.norm(off) / np.linalg.norm(r)),
                "median_abs": float(np.median(pairs)),
                "p95_abs": float(np.quantile(pairs, 0.95, method="linear"))}
    for k, v in expected.items():
        assert abs(dc["correlation_proxy"][k] - v) < 1e-12, (k, dc["correlation_proxy"][k], v)
    assert dc["correlation_proxy"]["p95_abs"] >= dc["correlation_proxy"]["median_abs"]

    # D: zero-free equivalence
    w = rng.standard_normal((50, 96))
    dw = diag.matrix_diagnostics(w)
    assert dw["zero_mass"] == 0.0
    assert abs(dw["sign_entropy_gt"] - dw["sign_entropy_ge"]) < 1e-15
    return {"status": "PASS", "cases": ["exact zero_mass", "gt vs ge separation (hand values)",
                                        "D4 definition replication", "zero-free equivalence"]}


def main():
    pkls = sorted((REGEN / "cache_repr").glob("*.pkl"))
    if len(pkls) != 470:
        print(f"need 470 pkls, have {len(pkls)}"); sys.exit(1)

    # published-D1/D2/D3 reference values for cross-checks
    ref = json.loads((WORK / "harness" / "ref" / "task1_RESULTS.json").read_text())
    ref_d1_mean = ref["longmemeval"]["D1_ge"]["mean"]
    ref_d2_mean = ref["longmemeval"]["D2_cv_sigma"]["mean"]

    rows = []
    for p in pkls:
        o = pickle.loads(p.read_bytes())
        C = o["C"]
        d = diag.matrix_diagnostics(C)
        v = np.asarray(C, dtype=np.float64).var(axis=0, ddof=0)
        d2 = diag.variance_diagnostics(v)
        rec = {
            "question_id": o["question_id"],
            "N": int(C.shape[0]),
            "sign_entropy_gt": d["sign_entropy_gt"],
            "sign_entropy_ge": d["sign_entropy_ge"],
            "zero_mass": d["zero_mass"],
            "active_coordinates": d["active_coordinates"],
            "cv_sigma": d2["cv_sigma"],
            "zero_variance_coordinates": d2["zero_variance_coordinates"],
            "top32_share": d2["top_variance_fraction"]["32"],
            "first32_share": d2["ordered_prefix_fraction"]["32"],
            "first32_top32_intersection": d2["first32_top32_intersection"],
            "corr_off_mass": (d["correlation_proxy"] or {}).get("off_mass"),
            "corr_median_abs": (d["correlation_proxy"] or {}).get("median_abs"),
            "corr_p95_abs": (d["correlation_proxy"] or {}).get("p95_abs"),
            "residual_mean_max_abs": d["residual_mean_max_abs"],
        }
        rows.append(rec)

    def summary(key):
        vals = [r[key] for r in rows if r[key] is not None]
        a = np.asarray(vals, dtype=np.float64)
        return {"valid_archives": len(a), "missing_archives": len(rows) - len(a),
                "mean": float(a.mean()), "sd_ddof1": float(a.std(ddof=1)) if len(a) > 1 else None,
                "min": float(a.min()), "max": float(a.max())}

    d1_ge_regen = summary("sign_entropy_ge")
    d2_regen = summary("cv_sigma")
    cross = {
        "D1_ge_regen_mean": d1_ge_regen["mean"],
        "D1_ge_published_mean": ref_d1_mean,
        "D1_ge_abs_diff": abs(d1_ge_regen["mean"] - ref_d1_mean),
        "D2_regen_mean": d2_regen["mean"],
        "D2_published_mean": ref_d2_mean,
        "D2_abs_diff": abs(d2_regen["mean"] - ref_d2_mean),
    }
    out = {
        "status": "LOCAL SESSION — Task1 extension computed from certified regeneration",
        "source": "cache_repr from frozen producer re-execution; certification_report.json beside it",
        "labels": ["[LOCAL SESSION — NOT AN AUDIT]", "[CERTIFIED REGENERATION]",
                    "Strict >0 and zero-mass resolved by bit-faithful re-execution, not assumed."],
        "controls": extension_controls(),
        "cross_checks_vs_published": cross,
        "archive_count": len(rows), "dimensions": 96,
        "D1_gt": summary("sign_entropy_gt"),
        "D1_ge": d1_ge_regen,
        "zero_mass": summary("zero_mass"),
        "D2_cv_sigma": d2_regen,
        "D3_top32_share": summary("top32_share"),
        "D3_first32_share": summary("first32_share"),
        "D4_off_mass": summary("corr_off_mass"),
        "D4_median_abs": summary("corr_median_abs"),
        "D4_p95_abs": summary("corr_p95_abs"),
        "active_coordinates": summary("active_coordinates"),
        "zero_variance_coordinates_total": int(sum(r["zero_variance_coordinates"] for r in rows)),
        "archives": rows,
    }
    (REGEN / "task1_extension_lme.json").write_text(json.dumps(out, indent=2))
    with open(REGEN / "task1_extension_lme.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(json.dumps({k: v for k, v in out.items() if k not in ("archives",)}, indent=2)[:4000])
    print("wrote", REGEN / "task1_extension_lme.json")


if __name__ == "__main__":
    main()
