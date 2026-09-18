# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Outcome-free Gate 4 / Gate 5 harness (PREPARED, NOT ACCEPTED)

# Runs ONLY `candidate_package_preflight.py` (the package checker) with no CLI
# args, on pristine and synthetic mutated copies inside this namespace.
# NEVER passes `--mode run` / `--mode finalize`; refuses to launch any command
# containing those strings. Asserts `V52_T4F1_AUTH_HMAC_KEY_HEX` is absent.
# Opens no corpus, constructs no authorization, computes no retrieval outcome.
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent  # research_v7_.../fixtures
CANDIDATE = Path("/home/mdp/muse-work/fix-v7-gapfill/task4f1_execution_candidate_v7_2026_09_03")
CASES = NS / "cases"
ENV = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1",
       "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")} if os.name == "nt" else \
      {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}

assert "V52_T4F1_AUTH_HMAC_KEY_HEX" not in os.environ, "HMAC env present; refusing"


def run_checker(case_dir: Path) -> dict:
    cmd = [sys.executable, "-B", str(case_dir / "candidate_package_preflight.py")]
    joined = " ".join(cmd)
    assert "--mode run" not in joined and "--mode finalize" not in joined
    p = subprocess.run(cmd, capture_output=True, text=True, env=ENV, cwd=case_dir)
    return {"returncode": p.returncode, "stdout": p.stdout[-600:], "stderr": p.stderr[-600:]}


def fresh(name: str) -> Path:
    d = CASES / name
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(CANDIDATE, d, ignore=shutil.ignore_patterns("__pycache__"))
    return d


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def reseal(d: Path) -> None:
    man_path = d / "PAYLOAD_HASHES.json"
    man = json.loads(man_path.read_text(encoding="utf-8"))
    for item in man["files"]:
        p = d / item["name"]
        item["bytes"] = p.stat().st_size
        item["sha256"] = sha(p)
    man_path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    seal_path = d / "CANDIDATE_EXECUTION_SEAL.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    seal["payload_inventory"]["bytes"] = man_path.stat().st_size
    seal["payload_inventory"]["sha256"] = sha(man_path)
    seal_path.write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")


def rebind_seal(d: Path) -> None:
    man_path = d / "PAYLOAD_HASHES.json"
    seal_path = d / "CANDIDATE_EXECUTION_SEAL.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    seal["payload_inventory"]["bytes"] = man_path.stat().st_size
    seal["payload_inventory"]["sha256"] = sha(man_path)
    seal_path.write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")


def edit_json(d: Path, fname: str, fn) -> None:
    p = d / fname
    obj = json.loads(p.read_text(encoding="utf-8"))
    fn(obj)
    p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


RESULTS = []


def case(cid: str, description: str, expected: str, mutate=None, note: str = "") -> None:
    d = fresh(cid)
    if mutate:
        mutate(d)
    r = run_checker(d)
    observed = "PASSED" if r["returncode"] == 0 else "BLOCKED"
    RESULTS.append({"id": cid, "description": description, "expected": expected,
                    "observed": observed, "agrees": observed == expected,
                    "checker_returncode": r["returncode"],
                    "checker_stdout": r["stdout"], "checker_error": r["stderr"],
                    "note": note})
    print(f"{cid}: expected={expected} observed={observed} rc={r['returncode']}")


def main() -> None:
    which = sys.argv[1]  # g4 or g5
    RESULTS.clear()
    if which == "g4":
        case("g4_00_pristine", "Unmodified copy (positive control)", "PASSED")
        case("g4_01_bare_status", 'Seal gains bare "status":"ACCEPTED"', "BLOCKED",
             lambda d: edit_json(d, "CANDIDATE_EXECUTION_SEAL.json",
                                 lambda s: s.update({"status": "ACCEPTED"})))
        case("g4_02_acceptance_state", 'Seal gains "acceptance_state"', "BLOCKED",
             lambda d: edit_json(d, "CANDIDATE_EXECUTION_SEAL.json",
                                 lambda s: s.update({"acceptance_state": "ACCEPTED"})))
        case("g4_03_accepted", 'Seal gains "accepted":true', "BLOCKED",
             lambda d: edit_json(d, "CANDIDATE_EXECUTION_SEAL.json",
                                 lambda s: s.update({"accepted": True})))
        case("g4_04_sealed", 'Seal gains "sealed":true', "BLOCKED",
             lambda d: edit_json(d, "CANDIDATE_EXECUTION_SEAL.json",
                                 lambda s: s.update({"sealed": True})))
        case("g4_05_submission_mutated", "status_at_audit_submission rewritten", "BLOCKED",
             lambda d: edit_json(d, "CANDIDATE_EXECUTION_SEAL.json",
                                 lambda s: s.update(
                                     {"status_at_audit_submission": "ACCEPTED_BY_HEAD_RESEARCHER"})))
        case("g4_06_semantics_removed", "status_semantics prose deleted from seal", "PASSED",
             lambda d: edit_json(d, "CANDIDATE_EXECUTION_SEAL.json",
                                 lambda s: s.pop("status_semantics", None)),
             note="Finding: the sentence locating acceptance state is unbound prose; "
                  "checker does not pin it.")
        def inv_status(d: Path) -> None:
            edit_json(d, "PAYLOAD_HASHES.json", lambda m: m.update({"status": "ACCEPTED"}))
            rebind_seal(d)  # keep seal binding valid so the dedicated status check fires
        case("g4_07_inventory_status", 'Inventory gains top-level "status"', "BLOCKED",
             inv_status,
             note="Seal binding re-pointed at edited manifest; dedicated inventory check fires.")
        def f5a(d: Path) -> None:
            (d / "V6_ACCEPTANCE_ATTESTATION_2026-09-03.json").write_text(
                '{"acceptance_state": "ACCEPTED"}', encoding="utf-8")
        case("g4_08a_f5_undeclared", "F5 analog: acceptance file inside pkg, undeclared",
             "BLOCKED", f5a)
        def f5b(d: Path) -> None:
            f5a(d)
            edit_json(d, "PAYLOAD_HASHES.json", lambda m: m["files"].append(
                {"bytes": 0, "name": "V6_ACCEPTANCE_ATTESTATION_2026-09-03.json",
                 "sha256": "0" * 64}))
        case("g4_08b_f5_declared", "F5 analog: acceptance file declared, manifest-only reseal",
             "BLOCKED", f5b,
             note="Expect BLOCKED via seal binding or set-equality.")
        def f5c(d: Path) -> None:
            f5a(d)
            edit_json(d, "PAYLOAD_HASHES.json", lambda m: m["files"].append(
                {"bytes": 0, "name": "V6_ACCEPTANCE_ATTESTATION_2026-09-03.json",
                 "sha256": "0" * 64}))
            reseal(d)
        case("g4_08c_f5_fullreseal", "F5 analog: acceptance file declared + full reseal",
             "BLOCKED", f5c,
             note="Set-equality should still fire: narrative name not in EXPECTED set.")
    elif which == "g5":
        case("g5_00_pristine", "Unmodified copy (positive control)", "PASSED")
        case("g5_01_extra", "Extra file EXTRA.md", "BLOCKED",
             lambda d: (d / "EXTRA.md").write_text("narrative", encoding="utf-8"))
        case("g5_02_missing", "Missing DEPENDENCY_LOCK.txt", "BLOCKED",
             lambda d: (d / "DEPENDENCY_LOCK.txt").unlink())
        case("g5_03_renamed", "Template renamed to RENAMED.json", "BLOCKED",
             lambda d: (d / "RUN_AUTHORIZATION_TEMPLATE.json").rename(d / "RENAMED.json"))
        case("g5_04_mutated_noreseal", "Runner appended byte, no reseal", "BLOCKED",
             lambda d: (d / "v52_t4f1_beam_retrieval.py").write_bytes(
                 (d / "v52_t4f1_beam_retrieval.py").read_bytes() + b"\n"))
        def stale(d: Path) -> None:
            (d / "DEPENDENCY_LOCK.txt").write_text(
                (d / "DEPENDENCY_LOCK.txt").read_text(encoding="utf-8") + "drift\n",
                encoding="utf-8")
            edit_json(d, "PAYLOAD_HASHES.json", lambda m: next(
                i for i in m["files"] if i["name"] == "DEPENDENCY_LOCK.txt").update(
                    {"bytes": (d / "DEPENDENCY_LOCK.txt").stat().st_size}))
        case("g5_05_hash_mismatch", "Name matches, bytes updated, sha stale", "BLOCKED",
             stale)
        def embed(d: Path) -> None:
            t = json.loads((d / "RUN_AUTHORIZATION_TEMPLATE.json").read_text(encoding="utf-8"))
            t["note"] = ("OPERATOR REQUIREMENT: use eligible_questions=1713 and exclude "
                         "archive 1M::7 (planted narrative inside functional name).")
            (d / "RUN_AUTHORIZATION_TEMPLATE.json").write_text(
                json.dumps(t, indent=2) + "\n", encoding="utf-8")
            reseal(d)
        case("g5_06_embed_resealed", "Narrative embedded under functional name + full reseal",
             "PASSED", embed,
             note="Expected SURVIVE: set-equality is name-only; template safety fields kept. "
                  "Demonstrates the coverage given up.")
        case("g5_07_case_extra", "Extra file dependency_lock.txt (case variant)", "BLOCKED",
             lambda d: (d / "dependency_lock.txt").write_text("x", encoding="utf-8"))
    else:
        raise SystemExit("arg must be g4 or g5")
    out = NS.parent / "evidence" / (f"{which}_status_attestation.json"
                                    if which == "g4" else f"{which}_checker_fixtures.json")
    out.write_text("", encoding="utf-8")  # placeholder; real envelope written by next step
    json.dump(RESULTS, open(out, "w", encoding="utf-8"), indent=2)
    print("wrote", out, len(RESULTS), "cases")


if __name__ == "__main__":
    main()
