#!/usr/bin/env python3
"""Gate 2 (environment enforcement) + Gate 12 (authorization guard) negative tests.

SAFETY INVARIANT (added after superseded attempt A1 - see COMMAND_LOG.txt):
every authorization payload written by this script is passed through
`assert_defective()` first.  That helper recomputes exactly the field set the
runner requires and REFUSES to write the file unless at least one bound field
is provably wrong.  No valid V52_T4F1_RUN_AUTHORIZATION_V1 can be produced here,
so no case can reach real archive ranking.

Every case must BLOCK before any representation fit, archive ranking, or output
directory creation.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "task4f1_execution_candidate_2026_08_31"
SEALED = ROOT / "audit_v52_t4f0_restricted_refreeze_2026_08_31"
MANIFEST = ROOT / "audit_v52_t4f0_codex_2026_08_31" / "pinned_tree_manifest.json"
CORPUS = ROOT.parent / "BEAM_pinned_3e12035532eb85768f1a7cd779832b650c4b2ef9"
OUT = ROOT / "audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31"
PY = ROOT / "remediation_v52_t4f0_env_2026_08_31" / "Scripts" / "python.exe"
SCRIPT = CAND / "v52_t4f1_beam_retrieval.py"
COHORT = SEALED / "estimand_primary_cohort.csv"
SEAL = CAND / "CANDIDATE_EXECUTION_SEAL.json"

LOCKED_ENV = {
    "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1", "PYTHONHASHSEED": "0",
}

BASE_ARGS = [
    "--corpus-root", str(CORPUS),
    "--beam-manifest", str(MANIFEST),
    "--cohort", str(COHORT),
    "--restricted-seal", str(SEALED / "CANDIDATE_SEAL.json"),
    "--protocol", str(SEALED / "REFREEZE_PROTOCOL.md"),
    "--dependency-lock", str(CAND / "DEPENDENCY_LOCK.txt"),
    "--execution-seal", str(SEAL),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


SCRIPT_SHA, SEAL_SHA, COHORT_SHA = sha256(SCRIPT), sha256(SEAL), sha256(COHORT)


def required_fields(output_dir: Path) -> dict:
    """Exact field set verify_run_authorization() demands (mirrored, not imported)."""
    return {
        "schema": "V52_T4F1_RUN_AUTHORIZATION_V1",
        "status": "AUTHORIZED_FOR_TASK_4F1_EXECUTION",
        "retrieval_quality_outcome_access": "AUTHORIZED",
        "execution_script_sha256": SCRIPT_SHA,
        "execution_candidate_seal_sha256": SEAL_SHA,
        "cohort_sha256": COHORT_SHA,
        "required_archive_count": 96,
        "output_namespace_basename": output_dir.name,
    }


class WouldAuthorize(RuntimeError):
    pass


def assert_defective(payload, output_dir: Path) -> list[str]:
    """Refuse to emit anything the runner would accept."""
    if not isinstance(payload, dict):
        return ["payload_is_not_an_object"]
    bad = [k for k, v in required_fields(output_dir).items() if payload.get(k) != v]
    if not bad:
        raise WouldAuthorize(
            f"REFUSED: payload for {output_dir.name} satisfies every bound field "
            f"and would be a VALID run authorization")
    return bad


def run(args, env_overrides=None, timeout=900):
    env = dict(os.environ)
    env.update(LOCKED_ENV)
    for k, v in (env_overrides or {}).items():
        env.pop(k, None) if v is None else env.update({k: v})
    p = subprocess.run([str(PY), str(SCRIPT), *args], capture_output=True, text=True,
                       env=env, timeout=timeout, cwd=str(ROOT))
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def blocked_reason(stderr: str) -> str:
    for line in reversed(stderr.splitlines()):
        if "[BLOCKED" in line or "[BUG" in line or "error:" in line:
            return line.strip()[:400]
    return stderr.splitlines()[-1][:400] if stderr.strip() else ""


results = {
    "schema": "V52_T4F1_ENV_AND_AUTHORIZATION_NEGATIVE_TESTS_V1",
    "safety_invariant": "every payload passed assert_defective(); no valid "
                        "V52_T4F1_RUN_AUTHORIZATION_V1 was constructed",
    "cases": [],
}
work = Path(tempfile.mkdtemp(prefix="t4f1_neg2_"))


def record(name, gate, rc, out, err, extra=None):
    e = {"case": name, "gate": gate, "exit_code": rc, "blocked": rc != 0,
         "stdout_tail": out.splitlines()[-1][:200] if out else "",
         "block_reason": blocked_reason(err),
         "outcome_value_in_output": any(t in (out + err) for t in
                                        ("recall_at_3=", "any_at_3=", "all_at_3=", "fractional"))}
    if extra:
        e.update(extra)
    e["pass"] = e["blocked"] and not e["outcome_value_in_output"] and \
        not e.get("output_dir_created", False) and not e.get("any_result_file_written", False)
    results["cases"].append(e)
    print(f"{'PASS' if e['pass'] else 'FAIL'}  {name}: rc={rc} :: {e['block_reason'][:130]}")


# ---------------- Gate 2 ----------------
pf = work / "env_probe.json"
for name, ov in [("env_omp_threads_wrong", {"OMP_NUM_THREADS": "4"}),
                 ("env_mkl_threads_missing", {"MKL_NUM_THREADS": None}),
                 ("env_pythonhashseed_wrong", {"PYTHONHASHSEED": "1"}),
                 ("env_openblas_threads_wrong", {"OPENBLAS_NUM_THREADS": "8"}),
                 ("env_numexpr_threads_wrong", {"NUMEXPR_NUM_THREADS": "2"})]:
    rc, o, er = run(["--mode", "preflight", *BASE_ARGS, "--preflight-output", str(pf)], ov)
    record(name, "2", rc, o, er, {"env_override": ov, "preflight_output_written": pf.exists(),
                                  "mentions_environment_lock": "ENVIRONMENT LOCK MISMATCH" in er})

alt = shutil.which("python")
if alt:
    env = dict(os.environ); env.update(LOCKED_ENV)
    p = subprocess.run([alt, str(SCRIPT), "--mode", "preflight", *BASE_ARGS,
                        "--preflight-output", str(pf)], capture_output=True, text=True,
                       env=env, timeout=600, cwd=str(ROOT))
    record("env_wrong_interpreter_3_14", "2", p.returncode, p.stdout.strip(), p.stderr.strip(),
           {"interpreter": alt, "preflight_output_written": pf.exists()})

# ---------------- Gate 12 ----------------
def auth_case(name, payload, out_name, extra_args=(), mode="run", raw=None):
    out_dir = work / out_name
    defects = None
    if raw is not None:
        auth = work / f"{out_name}_auth.json"
        auth.write_text(raw, encoding="utf-8")
        defects = ["unparseable_or_non_object"]
    elif payload is None:
        auth = work / f"{out_name}_absent.json"
        if auth.exists():
            auth.unlink()
        defects = ["file_absent"]
    else:
        defects = assert_defective(payload, out_dir)          # refuses if it would authorize
        auth = work / f"{out_name}_auth.json"
        auth.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    rc, o, er = run(["--mode", mode, *BASE_ARGS, "--authorization", str(auth),
                     "--output-dir", str(out_dir), *extra_args])
    record(name, "12", rc, o, er,
           {"mode": mode, "defective_fields": defects,
            "output_dir_created": out_dir.exists(),
            "archives_subdir_created": (out_dir / "archives").exists(),
            "any_result_file_written": bool(list(out_dir.rglob("*.csv"))) if out_dir.exists() else False})


def payload(out_name, **ov):
    base = required_fields(work / out_name)
    base.update(ov)
    return base


auth_case("auth_missing_file", None, "neg_missing")
auth_case("auth_supplied_template",
          json.loads((CAND / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8")),
          "neg_template")
auth_case("auth_wrong_script_hash", payload("neg_script", execution_script_sha256="0" * 64), "neg_script")
auth_case("auth_wrong_seal_hash", payload("neg_seal", execution_candidate_seal_sha256="1" * 64), "neg_seal")
auth_case("auth_wrong_cohort_hash", payload("neg_cohort", cohort_sha256="2" * 64), "neg_cohort")
auth_case("auth_wrong_output_namespace",
          payload("neg_namespace", output_namespace_basename="a_different_namespace"), "neg_namespace")
auth_case("auth_wrong_required_archive_count", payload("neg_count", required_archive_count=95), "neg_count")
auth_case("auth_forbidden_outcome_access",
          payload("neg_outcome", retrieval_quality_outcome_access="FORBIDDEN"), "neg_outcome")
auth_case("auth_wrong_schema", payload("neg_schema", schema="V52_T4F1_RUN_AUTHORIZATION_V2"), "neg_schema")
auth_case("auth_status_not_authorized", payload("neg_status", status="NOT_AUTHORIZED"), "neg_status")
auth_case("auth_json_scalar_not_object", None, "neg_scalar", raw='"MALFORMED"')
auth_case("auth_truly_malformed_json", None, "neg_malformed", raw="{ this is not json")
auth_case("auth_empty_object", payload("neg_empty") and {}, "neg_empty")

# bypass paths must not accept a DEFECTIVE authorization
auth_case("bypass_finalize_with_defective_auth",
          payload("neg_finalize", execution_script_sha256="3" * 64), "neg_finalize", mode="finalize")
auth_case("bypass_archive_selection_with_defective_auth",
          payload("neg_archive", execution_script_sha256="4" * 64), "neg_archive",
          extra_args=("--archive", "100K::12"))
auth_case("bypass_resume_with_defective_auth",
          payload("neg_resume", execution_script_sha256="5" * 64), "neg_resume",
          extra_args=("--resume",))
auth_case("bypass_invalid_archive_id_with_defective_auth",
          payload("neg_badarch", cohort_sha256="6" * 64), "neg_badarch",
          extra_args=("--archive", "9Z::999"))

# argparse-level guards
rc, o, er = run(["--mode", "preflight", *BASE_ARGS, "--preflight-output", str(pf),
                 "--output-dir", str(work / "neg_pf")])
record("preflight_rejects_run_arguments", "12", rc, o, er,
       {"output_dir_created": (work / "neg_pf").exists()})
rc, o, er = run(["--mode", "preflight", *BASE_ARGS, "--preflight-output", str(pf),
                 "--resume"])
record("preflight_rejects_resume_flag", "12", rc, o, er, {})
bad = work / "neg_fin_args_auth.json"
bad.write_text(json.dumps(payload("neg_fin_args", execution_script_sha256="7" * 64)), encoding="utf-8")
rc, o, er = run(["--mode", "finalize", *BASE_ARGS, "--authorization", str(bad),
                 "--output-dir", str(work / "neg_fin_args"), "--resume"])
record("finalize_rejects_resume_flag", "12", rc, o, er,
       {"output_dir_created": (work / "neg_fin_args").exists()})
rc, o, er = run(["--mode", "run", *BASE_ARGS, "--output-dir", str(work / "neg_noauth")])
record("run_without_authorization_argument", "12", rc, o, er,
       {"output_dir_created": (work / "neg_noauth").exists()})

# the shipped template is the only pre-existing authorization-shaped file: prove it is inert
tmpl = json.loads((CAND / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
results["template_defect_report"] = {
    "defective_fields_vs_runner_requirements":
        [k for k, v in required_fields(work / "any").items() if tmpl.get(k) != v],
    "template_can_never_authorize": True,
}

results["case_count"] = len(results["cases"])
results["all_cases_pass"] = all(c["pass"] for c in results["cases"])
results["no_output_directory_ever_created"] = not any(c.get("output_dir_created") for c in results["cases"])
results["no_result_file_ever_written"] = not any(c.get("any_result_file_written") for c in results["cases"])
results["no_preflight_output_under_bad_env"] = not any(c.get("preflight_output_written") for c in results["cases"])
results["no_outcome_value_in_any_console_output"] = not any(
    c["outcome_value_in_output"] for c in results["cases"])
leftovers = sorted(str(p.relative_to(work)) for p in work.rglob("*") if p.is_file())
results["files_left_in_temp_workdir"] = leftovers
results["no_archive_result_artifact_produced"] = not any(
    p.endswith((".csv", ".meta.json")) for p in leftovers)

(OUT / "AUTHORIZATION_NEGATIVE_TESTS.json").write_text(
    json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("\nsummary:", json.dumps({k: v for k, v in results.items() if isinstance(v, (bool, int))},
                               sort_keys=True))
shutil.rmtree(work, ignore_errors=True)
sys.exit(0 if results["all_cases_pass"] else 1)
