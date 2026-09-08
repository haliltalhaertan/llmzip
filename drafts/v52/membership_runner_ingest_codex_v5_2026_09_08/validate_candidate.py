"""Replay synthetic suites and bind outputs. No corpus or previous experiment is run.

Run using the accepted interpreter: python -B validate_candidate.py --output NEW_DIRECTORY
The destination must not exist. Default invocation writes nothing and verifies checked-in evidence.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = "86a8fd7a73a0d4e045666e692cd7e2016f134885"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        inventory = json.loads((HERE / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
        for entry in inventory["files"]:
            raw = (HERE / entry["path"]).read_bytes()
            assert sha(raw) == entry["sha256"] and len(raw) == entry["bytes"], entry["path"]
        print(f"PAYLOAD PASS {len(inventory['files'])} files (working bytes; use LF checkout)")
        return
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    required = {"numpy": "2.3.5", "scipy": "1.17.0", "scikit-learn": "1.8.0", "pandas": "2.2.3"}
    measured = {name: importlib.metadata.version(name) for name in required}
    assert platform.python_version() == "3.13.15" and measured == required, (platform.python_version(), measured)
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1",
               OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    suites = [HERE / "test_runner_ingest_v4.py", HERE / "test_codex_v5.py",
              HERE.parent / "membership_impl_v3_2026_09_07" / "test_membership_scaling_core.py"]
    results = []
    for suite in suites:
        completed = subprocess.run([sys.executable, "-B", str(HERE / "guarded_suite.py"), str(suite)],
                                   cwd=REPO, env=env, capture_output=True)
        (output / (suite.stem + ".stdout.txt")).write_bytes(completed.stdout)
        (output / (suite.stem + ".stderr.txt")).write_bytes(completed.stderr)
        results.append({"suite": suite.relative_to(REPO).as_posix(), "exit_code": completed.returncode,
                        "stdout_sha256": sha(completed.stdout), "stderr_sha256": sha(completed.stderr)})
    # Verify inherited scientific/configuration files from Git bytes, never source corpora.
    paths = ["drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py",
             "drafts/v52/membership_runner_ingest_v4_2026_09_08/membership_runner_v4.py",
             "drafts/v52/membership_runner_ingest_v4_2026_09_08/corpus_ingest_v4.py",
             "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_bootstrap_seeds.json"]
    preserved = []
    for path in paths:
        raw = subprocess.check_output(["git", "-C", str(REPO), "cat-file", "blob", BASE + ":" + path])
        assert (REPO / path).read_bytes() == raw, path
        preserved.append({"path": path, "base_commit": BASE, "sha256": sha(raw), "bytes": len(raw)})
    summary = {"status": "PASS" if all(r["exit_code"] == 0 for r in results) else "FAIL",
               "evidence_kind": "implementation-team synthetic tests; NOT independent audit",
               "python": platform.python_version(), "packages": measured,
               "platform": platform.platform(), "thread_settings": {k: env[k] for k in
               ("PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
               "suites": results, "preserved": preserved, "real_corpus_access_authorized": False,
               "real_experiment_run": False, "seal": False, "claude_independent_audit": "PENDING"}
    (output / "RESULTS.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
