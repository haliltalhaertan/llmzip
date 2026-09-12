"""Replay the pinned synthetic byte-cost script; never run retrieval experiments."""
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "evidence/twelve_byte_cost_2026_09_11"
PINS = {
    "measure_twelve_byte_cost.py": "0eb472ebd14585f677c340fb54a4b5ae6eeb980373e75507678ea0b378ed8028",
    "EVIDENCE.json": "4925ba839f79143847c86f94b7d66a81d0b08dc89a2ccbc27e6fcb0f67c8b9f2",
}
# Chosen before replay: strict equality is reported separately. Only finite float
# roundoff can pass this tolerance; integers, strings and structure stay exact.
ABS_TOL = 1e-8
REL_TOL = 1e-12


def compare(a, b, path=""):
    differences = []
    if type(a) is not type(b):
        return [{"path": path, "reference": a, "replay": b, "within_tolerance": False}]
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return [{"path": path, "error": "keys differ", "within_tolerance": False}]
        for key in a:
            differences.extend(compare(a[key], b[key], path + "/" + key))
    elif isinstance(a, list):
        if len(a) != len(b):
            return [{"path": path, "error": "length differs", "within_tolerance": False}]
        for i, (x, y) in enumerate(zip(a, b)):
            differences.extend(compare(x, y, path + "/" + str(i)))
    elif a != b:
        close = (type(a) is float and math.isfinite(a) and math.isfinite(b)
                 and math.isclose(a, b, abs_tol=ABS_TOL, rel_tol=REL_TOL))
        differences.append({"path": path, "reference": a, "replay": b,
                            "within_tolerance": close})
    return differences


def main():
    for name, expected in PINS.items():
        actual = hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError("Pinned source mismatch: " + name)
    blob = subprocess.check_output(["git", "hash-object", "--no-filters",
        "docs/v52/task4c2/V52_T4C2_feature_geometry.csv"], cwd=ROOT, text=True).strip()
    if blob != "b4336dd47fcf14e4b39f65bed3377d56ea9e77c7":
        raise RuntimeError("Archive-size source blob mismatch")
    env = dict(os.environ, OMP_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4",
               MKL_NUM_THREADS="4", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    started = time.time()
    with (OUT / "REPLAY.json").open("wb") as stdout, (OUT / "STDERR.txt").open("wb") as stderr:
        completed = subprocess.run([sys.executable, "-B", str(SOURCE / "measure_twelve_byte_cost.py")],
                                   cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    if completed.returncode:
        raise RuntimeError("Replay failed; inspect STDERR.txt")
    expected = json.loads((SOURCE / "EVIDENCE.json").read_text())
    actual = json.loads((OUT / "REPLAY.json").read_text())
    old_env, new_env = expected.pop("environment"), actual.pop("environment")
    differences = compare(expected, actual)
    result = {
        "source_commit": "8217704700d793862a6c43130b88236da551f010",
        "source_pins": PINS,
        "archive_size_blob": blob,
        "reference_environment": old_env, "replay_environment": new_env,
        "executor_platform": platform.platform(),
        "packages": {p: importlib.metadata.version(p) for p in ("faiss-cpu", "numpy")},
        "threads": 4, "elapsed_seconds": time.time() - started,
        "returncode": completed.returncode,
        "strict_non_environment_equal": not differences,
        "float_tolerant_equal": all(d["within_tolerance"] for d in differences),
        "predeclared_float_tolerance": {"absolute": ABS_TOL, "relative": REL_TOL},
        "differences": differences,
        "boundary": "Synthetic byte-cost replay plus frozen archive cardinalities only; no retrieval outcome computed.",
        "independence": "Separate Windows execution environment from Linux producer; executor did not author pinned measurement script. This is not a cold-start scientific audit.",
    }
    (OUT / "COMPARISON.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["float_tolerant_equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
