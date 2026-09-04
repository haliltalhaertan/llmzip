#!/usr/bin/env python3
"""Authorized production entrypoint for Task 4F1 exact-rational outcome analysis.

Order is deliberate: cryptographic/provenance verification completes before any retrieval-quality
CSV is parsed. Only after that gate passes are discrete retrieved IDs read and D_t computed exactly.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PROVENANCE_PATH = TOOLS / "t4f1_verify_post_run_provenance.py"
CORE_PATH = TOOLS / "t4f1_exact_rational_outcome_analysis.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--prereg-seal", type=Path, required=True)
    parser.add_argument("--execution-seal", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise RuntimeError(f"[BLOCKED - REFUSE OUTPUT OVERWRITE] {args.output}")

    provenance = load_module(PROVENANCE_PATH, "t4f1_post_run_provenance")
    core = load_module(CORE_PATH, "t4f1_exact_rational_core")

    # This gate hashes outcome files but parses no retrieval-quality value. It also verifies the
    # HMAC authorization using the non-persisted Head Researcher key before the core sees CSV rows.
    provenance_report = provenance.verify(
        args.cohort,
        args.prereg_seal,
        args.execution_seal,
        args.authorization,
        args.results_dir,
    )

    cohort = core.load_cohort(args.cohort)
    rows, input_manifest = core.read_trial_rows(args.results_dir)
    representative = core.validate_integrity_and_reduce(rows, cohort)
    records = core.question_records(representative, cohort)
    report = core.build_report(records, input_manifest)
    report["production_provenance"] = provenance_report
    report["production_entrypoint"] = "tools/t4f1_authorized_exact_rational_analysis.py"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    temporary.write_bytes(core.canonical_json_bytes(report))
    temporary.replace(args.output)

    print("T4F1_AUTHORIZED_EXACT_RATIONAL_ANALYSIS: PASS")
    print(f"output={args.output}")
    print(f"output_sha256={core.sha256_file(args.output)}")
    print(f"global_category={report['global_category']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
