#!/usr/bin/env python3
"""Independent-result-audit entrypoint for Task 4F1 exact-rational analysis.

This is the FIRST post-run component permitted to parse retrieval-quality values, and only after the
secret-free provenance gate has verified the pre-run HR authorization release, frozen analysis bundle,
runner post-run manifest, and all bound output/archive hashes.

The exact analysis JSON contains the preregistered category because the independent auditor must audit
it, but this program deliberately does NOT print that category to stdout. Before a PASS result-audit
attestation, the analysis artifact is audit-confidential and not authorized for substantive release.
"""

from __future__ import annotations

import argparse
import importlib.util
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
    parser.add_argument("--authorization-release", type=Path, required=True)
    parser.add_argument("--analysis-bundle-manifest", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    args = parser.parse_args()

    if args.audit_output.exists():
        raise RuntimeError(f"[BLOCKED - REFUSE AUDIT OUTPUT OVERWRITE] {args.audit_output}")

    provenance = load_module(PROVENANCE_PATH, "t4f1_post_run_provenance")
    core = load_module(CORE_PATH, "t4f1_exact_rational_core")

    # No retrieval-quality CSV is parsed before this returns PASS.
    provenance_report = provenance.verify(
        args.cohort,
        args.prereg_seal,
        args.execution_seal,
        args.authorization,
        args.authorization_release,
        args.analysis_bundle_manifest,
        args.results_dir,
    )

    cohort = core.load_cohort(args.cohort)
    rows, input_manifest = core.read_trial_rows(args.results_dir)
    representative = core.validate_integrity_and_reduce(rows, cohort)
    records = core.question_records(representative, cohort)
    report = core.build_report(records, input_manifest)
    report["production_provenance"] = provenance_report
    report["analysis_role"] = "INDEPENDENT_RESULT_AUDIT_ONLY"
    report["interpretation_release_authorized"] = False
    report["audit_entrypoint"] = "tools/t4f1_independent_result_audit_exact_analysis.py"

    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.audit_output.with_name(args.audit_output.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    temporary.write_bytes(core.canonical_json_bytes(report))
    temporary.replace(args.audit_output)

    print("T4F1_INDEPENDENT_RESULT_AUDIT_EXACT_ANALYSIS: PASS")
    print(f"audit_output={args.audit_output}")
    print(f"audit_output_sha256={core.sha256_file(args.audit_output)}")
    print("global_category_emitted_to_console=False")
    print("interpretation_release_authorized=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
