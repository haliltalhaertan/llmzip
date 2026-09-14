"""Task 2 only: persistent-state accounting on synthetic arrays.

The only real-data statistic used is N_archive from a pinned Git blob. No corpus,
gold, query, distance, ranking, recall, ITQ fit, OPQ fit, or other task is run.
Writes only the sibling task2/ directory. Run from any working directory.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import statistics
import subprocess
import sys
import urllib.request
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import faiss
import numpy as np

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[3]
OUT = SCRIPT.parent / "task2"
BASE = "ae9175676b840ae6a80a31eba9836187dc1b7491"
CARDINALITY_PATH = "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"
CARDINALITY_BLOB = "b4336dd47fcf14e4b39f65bed3377d56ea9e77c7"
FAISS_SOURCE_COMMIT = "20f14b31a6d54e243a3d1de6ae193fc4c3ec18ed"
TRAIN_NS = (256, 257, 1000)
ADD_NS = (0, 1, 256, 257, 1000)
SEEDS = {"synthetic_data": 73001, "random_rotation32": 73002,
         "itq96_surrogate_matrix": 73003, "pq_training": 73004}
SOURCE_PATHS = (
    "faiss/IndexRaBitQ.h", "faiss/IndexRaBitQ.cpp",
    "faiss/impl/RaBitQuantizer.cpp", "faiss/impl/RaBitQUtils.h",
    "faiss/impl/index_write.cpp", "faiss/impl/io_macros.h",
    "faiss/VectorTransform.cpp",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(name: str, value: object) -> None:
    (OUT / name).write_bytes(
        (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    )


def cardinalities() -> tuple[list[int], dict]:
    resolved = git("rev-parse", f"{BASE}:{CARDINALITY_PATH}").decode().strip()
    check(resolved == CARDINALITY_BLOB, "Wrong cardinality source blob")
    raw = git("cat-file", "blob", CARDINALITY_BLOB)
    raw_git_hash = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    check(raw_git_hash == CARDINALITY_BLOB, "Raw source object mismatch")
    # Access ONLY the N_archive field. Other columns are neither analyzed nor
    # included in outputs. Raw bytes above are used only for provenance hashing.
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    cells = [row["N_archive"] for row in reader]
    check(len(cells) == 470 and all(v.isdecimal() for v in cells),
          "Expected exactly 470 integer cardinalities; do not silently drop rows")
    ns = [int(v) for v in cells]
    check(all(n > 0 for n in ns), "Nonpositive archive cardinality")
    return ns, {"commit": BASE, "path": CARDINALITY_PATH,
                "git_blob_sha1": resolved, "sha256": sha(raw),
                "raw_bytes": len(raw), "accessed_statistic_column": "N_archive",
                "rows": len(ns), "minimum": min(ns), "maximum": max(ns),
                "mean": statistics.fmean(ns),
                "cohort": "470 archive cardinalities in pinned T4C2 source; not a LoCoMo claim"}


def environment() -> dict:
    runtime_files = []
    for distribution_name in ("faiss-cpu", "numpy"):
        dist = importlib.metadata.distribution(distribution_name)
        for item in dist.files or []:
            rel = str(item).replace("\\", "/")
            if rel.endswith((".pyd", ".dll", "/METADATA", "/WHEEL", "/RECORD")):
                p = Path(dist.locate_file(item))
                if p.is_file():
                    data = p.read_bytes()
                    runtime_files.append({"distribution": distribution_name, "path": rel,
                                          "bytes": len(data), "sha256": sha(data)})
    return {"scope": "TASK2 SYNTHETIC STORAGE ONLY; NO SEAL/RUN/OUTCOME AUTHORIZATION",
            "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "machine": platform.machine(),
            "faiss": faiss.__version__, "numpy": np.__version__,
            "faiss_compile_options": str(faiss.get_compile_options()),
            "faiss_omp_threads": faiss.omp_get_max_threads(),
            "thread_environment": {k: os.environ[k] for k in
                                   ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
            "runtime_files": runtime_files,
            "note": "Installed binary hashes identify this runtime; they do not prove a wheel was built from the referenced upstream commit."}


def source_references(cardinality_ref: dict) -> dict:
    refs = []
    for path in SOURCE_PATHS:
        url = f"https://raw.githubusercontent.com/facebookresearch/faiss/{FAISS_SOURCE_COMMIT}/{path}"
        request = urllib.request.Request(url, headers={"User-Agent": "V52-Task2-source-provenance"})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        check(len(raw) > 100, f"Empty upstream source: {path}")
        refs.append({"commit": FAISS_SOURCE_COMMIT, "path": path, "url": url,
                     "bytes": len(raw), "sha256": sha(raw)})
    return {"producer_script": {"path": str(SCRIPT.relative_to(ROOT)).replace("\\", "/"),
                                "sha256": sha(SCRIPT.read_bytes())},
            "base_commit": BASE, "cardinality_source": cardinality_ref,
            "faiss_tag": "v1.15.0", "faiss_upstream_commit": FAISS_SOURCE_COMMIT,
            "official_sources": refs,
            "literature_urls": ["https://arxiv.org/html/2605.02171v3#S3.SS1",
                                "https://arxiv.org/html/2405.12497v1#S3"],
            "identity_limits": "No upstream-source hash is a runtime replay or theorem certificate."}


def pack_quiver48(x: np.ndarray) -> np.ndarray:
    """Two six-byte planes PER ROW, sign >0 and magnitude > own mean(abs).

    Only a QuIVer-style code serializer. No scoring, graph, or rerank function.
    """
    check(x.ndim == 2 and x.shape[1] == 48 and np.isfinite(x).all(), "Expected finite n x 48")
    sign = np.packbits(x > 0, axis=1, bitorder="big")
    magnitude = np.packbits(np.abs(x) > np.abs(x).mean(axis=1, keepdims=True),
                            axis=1, bitorder="big")
    return np.ascontiguousarray(np.concatenate((sign, magnitude), axis=1))


def validate_size(s0: int, sn: int, n: int, marginal: int) -> None:
    check(all(type(v) is int for v in (s0, sn, n, marginal)), "Noninteger accounting")
    check(0 < marginal <= 12 and n >= 0 and s0 >= 0, "Budget/declaration invalid")
    check(sn - s0 == n * marginal, "Serialized integer differencing disagrees with declaration")


def packing_controls() -> dict:
    probe = np.array([[0.] * 48, [1.] * 48, [-1.] * 48,
                      [0., 1., -1., 4., -4., 0.] * 8], dtype=np.float32)
    packed = pack_quiver48(probe)
    check(packed.shape == (4, 12) and packed.dtype == np.uint8 and packed.nbytes == 48,
          "QuIVer compact layout failed")
    got_sign = np.unpackbits(packed[:, :6], axis=1, bitorder="big")
    got_mag = np.unpackbits(packed[:, 6:], axis=1, bitorder="big")
    check(np.array_equal(got_sign, probe > 0), "Sign bits failed round trip")
    check(np.array_equal(got_mag, np.abs(probe) > np.abs(probe).mean(axis=1, keepdims=True)),
          "Magnitude bits failed round trip")
    check(packed[0].tobytes() == bytes(12), "Zero convention failed")
    check(packed[1].tobytes() == b"\xff" * 6 + bytes(6), "Strict threshold equality failed")
    rejected = []
    for label, args in [("two_uint64_planes_16B", (0, 16, 1, 12)),
                        ("silent_extra_byte", (33, 46, 1, 12)),
                        ("declared_over_cap", (0, 20, 1, 20)),
                        ("noninteger_slope", (0, 12, 1, 12.0))]:
        try:
            validate_size(*args)
        except RuntimeError:
            rejected.append(label)
        else:
            raise RuntimeError(f"Negative byte control did not reject: {label}")
    return {"known_vectors_and_zero_equality_roundtrip": "PASS",
            "compact_plane_bytes": [6, 6], "negative_controls_rejected": rejected}


def index_bytes(index, binary=False) -> bytes:
    return (faiss.serialize_index_binary(index) if binary else faiss.serialize_index(index)).tobytes()


def transform_bytes(transform) -> bytes:
    writer = faiss.VectorIOWriter()
    faiss.write_VectorTransform(transform, writer)
    array = faiss.vector_to_array(writer.data)
    reader = faiss.VectorIOReader()
    faiss.copy_array_to_vector(array, reader.data)
    restored = faiss.read_VectorTransform(reader)
    writer2 = faiss.VectorIOWriter()
    faiss.write_VectorTransform(restored, writer2)
    check(np.array_equal(array, faiss.vector_to_array(writer2.data)),
          "Transform serialization roundtrip changed stored bytes")
    return array.tobytes()


def part_record(parts: dict[str, bytes]) -> dict:
    return {"total_bytes": sum(map(len, parts.values())),
            "parts": {name: {"bytes": len(data), "sha256": sha(data)}
                      for name, data in parts.items()}}


def save_example(arm: str, n: int, parts: dict[str, bytes]) -> None:
    # These are evidence copies of one storage package, not extra deployed state.
    directory = OUT / "serialized_examples" / arm / f"add_{n}"
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in parts.items():
        (directory / name).write_bytes(data)


def measure_arm(name: str, marginal: int, x96: np.ndarray) -> dict:
    trials = []
    shared_values = []
    for train_n in TRAIN_NS:
        auxiliary = {}
        fixed_parts = {}
        binary = name in ("SIGN96", "SIGN32", "ITQ96_MATRIX_SURROGATE")
        rotation = None
        fitted_content = 0
        nonfitted_content = 0
        raw_centroid = 0
        if name == "QUIVER_STYLE48X2_COMPACT":
            code_array = pack_quiver48(x96[:, :48])
            before = after = b""
            mode = "Pure code bytes; no Faiss index/header, fit, graph, or float rerank"
        elif binary:
            dim = 32 if name == "SIGN32" else 96
            index = faiss.IndexBinaryFlat(dim)
            if name == "ITQ96_MATRIX_SURROGATE":
                rng = np.random.default_rng(SEEDS["itq96_surrogate_matrix"])
                q, r = np.linalg.qr(rng.standard_normal((96, 96)))
                matrix = np.ascontiguousarray(q * np.where(np.diag(r) < 0, -1., 1.), dtype=np.float32)
                transform = faiss.ITQMatrix(96)
                faiss.copy_array_to_vector(matrix.ravel(), transform.A)
                # This flag allows serialization of a complete A. NO ITQ train call.
                transform.is_trained = True
                transform.is_orthonormal = True
                fixed_parts["synthetic_itq_transform.bin"] = transform_bytes(transform)
                nonfitted_content = matrix.nbytes
                orth_error = float(np.max(np.abs(matrix.astype(float).T @ matrix.astype(float) - np.eye(96))))
                check(orth_error < 1e-6, "Surrogate matrix not numerically orthogonal")
                auxiliary = {"actual_itq_fit_performed": False, "serialized_is_trained_flag": True,
                             "matrix_identity": "Seeded synthetic orthogonal A installed in ITQMatrix; NOT fitted ITQ",
                             "surrogate_for_future_fitted_matrix_content_bytes": matrix.nbytes,
                             "matrix_sha256": sha(matrix.tobytes()), "orthogonality_max_abs": orth_error,
                             "transform_serialized_bytes": len(fixed_parts["synthetic_itq_transform.bin"]),
                             "transform_serialization_overhead_bytes": len(fixed_parts["synthetic_itq_transform.bin"]) - matrix.nbytes,
                             "fit_sample_count": None, "feasibility_or_stability_claim": False}
                code_input = x96 @ matrix.T  # Faiss LinearTransform stores output rows in A.
                mode = "ITQMatrix serialization surrogate plus BinaryFlat code store; no ITQ fit"
            else:
                code_input = x96[:, :dim]
                mode = "Deterministic sign >=0, packed big-endian, BinaryFlat store; no learned quantizer state"
            code_array = np.ascontiguousarray(np.packbits(code_input >= 0, axis=1, bitorder="big"))
            before = index_bytes(index, True)
            index.train(code_array[:train_n])  # BinaryFlat no-op, NOT ITQ training.
            after = index_bytes(index, True)
        elif name == "PQ96_M12X8":
            index = faiss.IndexPQ(96, 12, 8, faiss.METRIC_L2)
            index.pq.cp.seed = SEEDS["pq_training"]
            index.pq.cp.niter = 10  # storage probe only; not a retrieval training prescription
            before = index_bytes(index)
            index.train(np.ascontiguousarray(x96[:train_n]))
            after = index_bytes(index)
            fitted_content = faiss.vector_to_array(index.pq.centroids).nbytes
            check(fitted_content == 12 * 256 * 8 * 4, "Unexpected PQ centroid layout")
            auxiliary = {"m": 12, "nbits": 8, "centroid_content_bytes": fitted_content,
                         "training_iterations": 10, "training_seed": SEEDS["pq_training"],
                         "min_points_per_centroid_recommendation": int(index.pq.cp.min_points_per_centroid),
                         "recommended_training_points": int(index.pq.cp.min_points_per_centroid) * 256,
                         "recommendation_met": train_n >= int(index.pq.cp.min_points_per_centroid) * 256,
                         "training_status": "COMPLETED; reliability recommendation is distinct from hard trainability",
                         "quality_claim": False}
            mode = "Actual synthetic archive-local PQ training and serialization"
        else:
            plain = faiss.IndexRaBitQ(32, faiss.METRIC_L2, 1)
            if name == "RQ32_RANDOM_ROTATION_WRAPPER":
                rotation = faiss.RandomRotationMatrix(32, 32)
                rotation.init(SEEDS["random_rotation32"])
                rotation_before = faiss.vector_to_array(rotation.A).tobytes()
                index = faiss.IndexPreTransform(rotation, plain)
                mode = "Explicit random rotation then IndexRaBitQ; actual Faiss IndexPreTransform serializer"
                nonfitted_content = faiss.vector_to_array(rotation.A).nbytes
            else:
                index = plain
                mode = "Plain IndexRaBitQ: fits centroid only; no internal rotation and no rotation seed"
            before = index_bytes(index)
            index.train(np.ascontiguousarray(x96[:train_n, :32]))
            after = index_bytes(index)
            raw_centroid = faiss.vector_to_array(plain.center).nbytes
            fitted_content = raw_centroid
            check(raw_centroid == 32 * 4 and plain.code_size == 12, "Unexpected RQ32 layout")
            auxiliary = {"centroid_content_bytes": raw_centroid, "nb_bits": 1,
                         "sign_code_bytes": 4, "per_vector_factors_bytes": 8,
                         "factor_fields": ["or_minus_c_l2sqr:float32", "dp_multiplier:float32"],
                         "plain_index_internal_rotation": False,
                         "plain_index_rotation_seed": None,
                         "query_quantization_qb_setting_only_no_queries": int(plain.qb)}
            if rotation is not None:
                check(faiss.vector_to_array(rotation.A).tobytes() == rotation_before,
                      "Training silently replaced explicit random matrix")
                rot_bytes = transform_bytes(rotation)
                plain_bytes = index_bytes(plain)
                auxiliary.update({"explicit_rotation_seed": SEEDS["random_rotation32"],
                                  "rotation_A_content_bytes": nonfitted_content,
                                  "rotation_A_sha256": sha(rotation_before),
                                  "rotation_bias_content_bytes": faiss.vector_to_array(rotation.b).nbytes,
                                  "rotation_serialized_bytes": len(rot_bytes),
                                  "rotation_serialization_overhead_bytes": len(rot_bytes) - nonfitted_content,
                                  "inner_plain_index_trained_empty_bytes": len(plain_bytes),
                                  "pretransform_wrapper_overhead_bytes": len(after) - len(rot_bytes) - len(plain_bytes),
                                  "rotation_state_representation": "Full float32 matrix A, NOT seed-only"})

        if name == "QUIVER_STYLE48X2_COMPACT":
            zero_parts = {"codes.bin": b""}
        else:
            zero_parts = {"index.bin": after, **fixed_parts}
            actual_code_size = index.code_size if binary or name == "PQ96_M12X8" else plain.code_size
            check(actual_code_size == marginal, "Library code_size differs from marginal declaration")
        s0 = sum(map(len, zero_parts.values()))
        shared_values.append(s0)
        samples = []
        for n in ADD_NS:
            if name == "QUIVER_STYLE48X2_COMPACT":
                parts = {"codes.bin": code_array[:n].tobytes()}
                check(code_array[:n].nbytes == n * marginal, "Actual packed stride mismatch")
            else:
                array = np.frombuffer(after, dtype=np.uint8).copy()
                clone = faiss.deserialize_index_binary(array) if binary else faiss.deserialize_index(array)
                if n:
                    data = code_array[:n] if binary else np.ascontiguousarray(x96[:n, :32] if name.startswith("RQ32") else x96[:n])
                    clone.add(data)
                check(clone.ntotal == n, "Deserialized clone/add count mismatch")
                parts = {"index.bin": index_bytes(clone, binary), **fixed_parts}
                # Roundtrip validates serialization, count and size only. No distances.
                fresh = np.frombuffer(parts["index.bin"], dtype=np.uint8).copy()
                roundtrip = faiss.deserialize_index_binary(fresh) if binary else faiss.deserialize_index(fresh)
                check(roundtrip.ntotal == n and index_bytes(roundtrip, binary) == parts["index.bin"],
                      "Index serialization roundtrip changed stored bytes")
            rec = part_record(parts)
            validate_size(s0, rec["total_bytes"], n, marginal)
            samples.append({"added_vectors": n, **rec, "integer_difference": rec["total_bytes"] - s0,
                            "expected_difference": n * marginal, "integer_difference_pass": True})
            if train_n == 1000 and n in (0, 1000):
                save_example(name, n, parts)
        overhead = s0 - fitted_content - nonfitted_content
        check(overhead >= 0, "Negative serialization overhead")
        trials.append({"synthetic_training_input_rows": train_n, "training_identity": mode,
                       "before_training_empty_index_bytes": len(before),
                       "after_training_empty_index_bytes": len(after),
                       "shared_package_bytes": s0,
                       "algorithm_specific_fitted_content_bytes": fitted_content,
                       "algorithm_specific_nonfitted_content_bytes": nonfitted_content,
                       "serializer_headers_and_configuration_bytes": overhead,
                       "common_preprocessing_bytes": None,
                       "common_preprocessing_status": "NOT MEASURED; these synthetic inputs already represent the archive feature matrix",
                       "auxiliary": auxiliary, "samples": samples})
    check(len(set(shared_values)) == 1, "Shared cost varies by training sample; do not pool without explanation")
    return {"arm": name, "marginal_bytes_per_vector": marginal,
            "marginal_cap_pass": marginal <= 12, "shared_state_bytes_per_archive": shared_values[0],
            "storage_boundary": "Serialized quantizer/transform/code package only; common preprocessing excluded and explicitly unknown; not a full deployed system total",
            "actual_itq_fit_performed": False, "training_trials": trials}


def archive_ratios(arms: list[dict], ns: list[int]) -> None:
    columns = ["source_row_ordinal_1based", "N_archive", "arm", "marginal_bytes_per_vector",
               "shared_state_bytes_per_archive", "effective_package_bytes_per_vector",
               "shared_to_code_volume_ratio"]
    with (OUT / "ARCHIVE_COST_RATIOS.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(columns)
        for arm in arms:
            marginal, shared = arm["marginal_bytes_per_vector"], arm["shared_state_bytes_per_archive"]
            effective = [marginal + shared / n for n in ns]
            ratios = [shared / (n * marginal) for n in ns]
            arm["archive_ratio_summary"] = {
                "n_archives": len(ns), "denominator": "Each archive's own N_archive * marginal_bytes_per_vector",
                "effective_package_bytes_mean_over_archives": statistics.fmean(effective),
                "effective_package_bytes_min": min(effective), "effective_package_bytes_max": max(effective),
                "effective_package_cost_at_mean_N_separate": marginal + shared / statistics.fmean(ns),
                "shared_to_code_volume_ratio_mean": statistics.fmean(ratios),
                "shared_to_code_volume_ratio_min": min(ratios), "shared_to_code_volume_ratio_max": max(ratios),
                "common_preprocessing_included": False}
            for i, (n, e, r) in enumerate(zip(ns, effective, ratios), start=1):
                writer.writerow([i, n, arm["arm"], marginal, shared, format(e, ".17g"), format(r, ".17g")])


def output_hashes() -> None:
    paths = [SCRIPT] + sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "HASHES.txt")
    lines = [f"{sha(p.read_bytes())}  {p.relative_to(SCRIPT.parent).as_posix()}\n" for p in paths]
    (OUT / "HASHES.txt").write_bytes("".join(lines).encode("utf-8"))


def main() -> None:
    check(faiss.__version__ == "1.15.0" and np.__version__ == "2.4.6", "Wrong locked library versions")
    faiss.omp_set_num_threads(1)
    OUT.mkdir(parents=True, exist_ok=True)
    ns, cardinality_ref = cardinalities()
    env = environment()
    write_json("ENVIRONMENT.json", env)
    write_json("SOURCE_REFERENCES.json", source_references(cardinality_ref))
    controls = packing_controls()
    x96 = np.random.default_rng(SEEDS["synthetic_data"]).standard_normal((1000, 96)).astype(np.float32)
    arms = []
    for name, marginal in (("SIGN96", 12), ("SIGN32", 4), ("QUIVER_STYLE48X2_COMPACT", 12),
                           ("ITQ96_MATRIX_SURROGATE", 12), ("PQ96_M12X8", 12),
                           ("RQ32_PLAIN_NO_ROTATION", 12), ("RQ32_RANDOM_ROTATION_WRAPPER", 12)):
        print(f"Measuring {name}", flush=True)
        arm = measure_arm(name, marginal, x96)
        arms.append(arm)
        # Persist completed measurements before advancing to the next arm.
        write_json("RESULTS.json", {"status": "IN_PROGRESS", "environment": env, "completed_arms": arms})
    archive_ratios(arms, ns)
    write_json("RESULTS.json", {
        "status": "COMPLETE", "scope": "TASK2 SYNTHETIC STORAGE ACCOUNTING ONLY",
        "environment": env,
        "authorization_scope": "No corpus, gold, queries, distances, rankings, quality, seal, HMAC, Task1, Task3 or OPQ",
        "base_commit": BASE, "script_sha256": sha(SCRIPT.read_bytes()), "seeds": SEEDS,
        "train_sample_sizes": list(TRAIN_NS), "add_sample_sizes": list(ADD_NS),
        "cardinality_source": cardinality_ref, "controls": controls, "arms": arms,
        "assertion_summary": {"measured_arms": len(arms), "training_cases": len(arms) * len(TRAIN_NS),
                              "exact_integer_serialization_checks": len(arms) * len(TRAIN_NS) * len(ADD_NS),
                              "noninteger_regression_or_tolerance_used": False,
                              "all_measured_cap_and_roundtrip_checks_pass": True},
        "limits": ["ITQ is matrix serialization surrogate only, never a fitted ITQ result.",
                   "Plain RQ32 has no rotation; explicit rotated wrapper is a different package.",
                   "QuIVer-style compact codec is not the complete QuIVer graph/rerank system.",
                   "Common preprocessing is unknown, not zero; effective costs are package-only.",
                   "Synthetic successful training is not real-archive training reliability or retrieval evidence.",
                   "This is not a future retrieval runner integration pass or seal authorization."]})
    print("PASS: Task2 complete; exact integer byte checks passed; no quality/ITQ-fit execution.")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    # Capture native Faiss stderr warnings as evidence, without hiding their
    # reliability meaning in the results. Close the log before hashing it.
    saved_stderr = os.dup(2)
    try:
        with (OUT / "FAISS_TRAINING_WARNINGS.log").open("wb") as warning_log:
            os.dup2(warning_log.fileno(), 2)
            try:
                main()
            finally:
                os.dup2(saved_stderr, 2)
    finally:
        os.close(saved_stderr)
    output_hashes()
