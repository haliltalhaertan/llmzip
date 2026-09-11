#!/usr/bin/env python3
"""Measure the twelve-byte cost claims. Synthetic data only; no corpus is read.

The one repository input is the committed metric CSV named in ARCHIVE_SIZE_SOURCE,
read for its N_archive column alone. That column is archive cardinality, not a
retrieval outcome.

Run:  python3 evidence/twelve_byte_cost_2026_09_11/measure_twelve_byte_cost.py
Emits JSON on stdout. Deterministic: all randomness is seeded.
"""
from __future__ import annotations
import csv, json, platform, statistics as st, subprocess, sys
from pathlib import Path

import faiss, numpy as np

SEED = 0
D = 96
ARCHIVE_SIZE_SOURCE = "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"
ARCHIVE_SIZE_BLOB = "b4336dd47fcf14e4b39f65bed3377d56ea9e77c7"
ROOT = Path(__file__).resolve().parents[2]


def rng():
    return np.random.default_rng(SEED)


def rabitq_code_sizes() -> dict:
    """code_size by dimension and bits; isolate the fixed overhead."""
    out = {"nb1": {}, "nb2": {}, "overhead_nb1": {}}
    for d in (32, 64, 96, 128, 256, 1024):
        q1 = faiss.RaBitQuantizer(d)
        out["nb1"][d] = q1.code_size
        out["overhead_nb1"][d] = q1.code_size - -(-d // 8)
        out["nb2"][d] = faiss.RaBitQuantizer(d, faiss.METRIC_L2, 2).code_size
    out["overhead_is_constant"] = len(set(out["overhead_nb1"].values())) == 1
    out["largest_d_within_12B_nb1"] = max(
        d for d in range(8, 200, 8) if faiss.RaBitQuantizer(d).code_size <= 12
    )
    return out


def nb_bits_silent_trap() -> dict:
    """Assigning nb_bits after construction is ignored; the constructor form is not."""
    q = faiss.RaBitQuantizer(D)
    q.nb_bits = 2
    return {
        "post_construction_assignment_code_size": q.code_size,
        "post_construction_nb_bits_reads_back": q.nb_bits,
        "constructor_form_code_size": faiss.RaBitQuantizer(D, faiss.METRIC_L2, 2).code_size,
        "assignment_is_silently_ignored": q.code_size == faiss.RaBitQuantizer(D).code_size,
    }


def serialization_S_of_N() -> dict:
    """S(N) = a + bN from five points, with residuals so linearity is checked, not assumed."""
    pts = (0, 1, 100, 1000, 10000)
    train = rng().standard_normal((20000, D)).astype("float32")
    out = {}

    def fit(name, build, dim=D, binary=False):
        sizes = {}
        r = rng()
        for n in pts:
            ix = build()
            if not binary:
                ix.train(train[:, :dim] if dim != D else train)
            if n:
                x = (r.integers(0, 256, (n, dim // 8), dtype="uint8") if binary
                     else r.standard_normal((n, dim)).astype("float32"))
                ix.add(x)
            ser = faiss.serialize_index_binary(ix) if binary else faiss.serialize_index(ix)
            sizes[n] = len(ser)
        ns = np.array(pts, dtype=float)
        ss = np.array([sizes[n] for n in pts], dtype=float)
        a, b = np.linalg.lstsq(np.vstack([np.ones_like(ns), ns]).T, ss, rcond=None)[0]
        resid = ss - (a + b * ns)
        out[name] = {
            "points": sizes,
            "shared_bytes": float(a),
            "marginal_bytes_per_vector": float(b),
            "max_abs_residual": float(np.abs(resid).max()),
            "linear": bool(np.abs(resid).max() < 1.0),
        }

    fit("SIGN96_BinaryFlat", lambda: faiss.IndexBinaryFlat(D), binary=True)
    fit("TOP32_RABITQ32", lambda: faiss.IndexRaBitQ(32), dim=32)
    fit("RABITQ96", lambda: faiss.IndexRaBitQ(D))
    fit("PQ96_m12x8", lambda: faiss.IndexPQ(D, 12, 8))
    fit("OPQ_PQ96_m12x8", lambda: faiss.index_factory(D, "OPQ12_96,PQ12"))
    return out


def serialized_versus_analytic() -> dict:
    """The two numbers are different objects: a storage budget counts what is written."""
    ix = faiss.index_factory(D, "OPQ12_96,PQ12")
    ix.train(rng().standard_normal((20000, D)).astype("float32"))
    ser = len(faiss.serialize_index(ix))
    analytic = D * D * 4 + 12 * 256 * 8 * 4
    pq = faiss.IndexPQ(D, 12, 8)
    pq.train(rng().standard_normal((20000, D)).astype("float32"))
    return {
        "OPQ_PQ96_serialized": ser,
        "OPQ_PQ96_analytic_content": analytic,
        "OPQ_PQ96_header": ser - analytic,
        "PQ96_serialized": len(faiss.serialize_index(pq)),
        "PQ96_analytic_content": 12 * 256 * 8 * 4,
        "note": "A storage budget counts the serialized object, not the analytic content.",
    }


def pq_trainability() -> dict:
    """39*k is faiss's points-per-centroid WARNING threshold, not a trainability gate.

    The hard bound is points < centroids.
    """
    cp = faiss.ClusteringParameters()
    hard = {}
    r = rng()
    for n in (300, 256, 255, 100):
        try:
            faiss.ProductQuantizer(D, 12, 8).train(r.standard_normal((n, D)).astype("float32"))
            hard[n] = "trains"
        except RuntimeError:
            hard[n] = "RuntimeError"
    configs = {}
    for m, b in ((12, 8), (16, 6), (24, 4), (48, 2)):
        k = 2 ** b
        configs[f"m{m}x{b}bit"] = {
            "k": k,
            "code_size": faiss.ProductQuantizer(D, m, b).code_size,
            "recommended_points": int(cp.min_points_per_centroid) * k,
            "meets_recommendation_at_min_archive_396": int(cp.min_points_per_centroid) * k <= 396,
        }
    return {
        "min_points_per_centroid": int(cp.min_points_per_centroid),
        "max_points_per_centroid": int(cp.max_points_per_centroid),
        "hard_bound_probe": hard,
        "hard_bound_is": "points < centroids",
        "twelve_byte_configs": configs,
        "correction": (
            "An earlier statement called 39*k a trainability limit. It is not. "
            "m=12x8 does train at 396-616 points, with a faiss reliability warning."
        ),
    }


def archive_cost() -> dict:
    """Amortise the shared state over N_archive, not over the question count."""
    path = ROOT / ARCHIVE_SIZE_SOURCE
    with path.open() as fh:
        rows = [r for r in csv.DictReader(fh) if "__SUMMARY__" not in r["question_id"]]
    ns = [int(r["N_archive"]) for r in rows]
    ix = faiss.index_factory(D, "OPQ12_96,PQ12")
    ix.train(rng().standard_normal((20000, D)).astype("float32"))
    shared = len(faiss.serialize_index(ix))
    marginal = 12
    at_mean = marginal + shared / st.mean(ns)
    mean_of = st.mean([marginal + shared / n for n in ns])
    return {
        "source": ARCHIVE_SIZE_SOURCE,
        "source_blob": ARCHIVE_SIZE_BLOB,
        "n_archives": len(ns),
        "N_archive_min": min(ns),
        "N_archive_max": max(ns),
        "N_archive_mean": st.mean(ns),
        "shared_bytes_serialized": shared,
        "cost_at_min": marginal + shared / min(ns),
        "cost_at_mean_N": at_mean,
        "cost_at_max": marginal + shared / max(ns),
        "mean_cost_over_archives": mean_of,
        "jensen_gap": mean_of - at_mean,
        "quotable_figure": mean_of,
        "note": (
            "1/N is convex, so the mean of the costs exceeds the cost at the mean. "
            "The panel figure to quote is mean_cost_over_archives."
        ),
    }


def environment() -> dict:
    try:
        blob = subprocess.run(
            ["git", "rev-parse", f"HEAD:{ARCHIVE_SIZE_SOURCE}"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        blob = "unavailable"
    return {
        "faiss": faiss.__version__,
        "numpy": np.__version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "seed": SEED,
        "archive_size_blob_resolved_here": blob,
        "archive_size_blob_expected": ARCHIVE_SIZE_BLOB,
        "blob_matches": blob == ARCHIVE_SIZE_BLOB,
    }


def main() -> int:
    report = {
        "what_this_is": (
            "Measurements behind the twelve-byte cost claims, so they stop being relayed. "
            "Synthetic data only; the single repository input is one metric CSV's "
            "N_archive column, which is archive cardinality and not a retrieval outcome."
        ),
        "environment": environment(),
        "rabitq_code_sizes": rabitq_code_sizes(),
        "nb_bits_silent_trap": nb_bits_silent_trap(),
        "serialized_versus_analytic": serialized_versus_analytic(),
        "serialization_S_of_N": serialization_S_of_N(),
        "pq_trainability": pq_trainability(),
        "archive_cost": archive_cost(),
        "task_4f1": "untouched: SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN",
    }
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
