#!/usr/bin/env python3
"""Temporary-copy negative/positive fixtures for the V5 package preflight.

Every experiment operates on a fresh copy under a scratch root. The real candidate
namespace is never written to. Outcome-free: no retrieval, no ranking, no metrics.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

SRC = Path(sys.argv[1]).resolve()
PY = sys.argv[2]
SCRATCH = Path(sys.argv[3]).resolve()
SCRATCH.mkdir(parents=True, exist_ok=True)


def digest_tree(root: Path):
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


BASELINE = digest_tree(SRC)


def run_preflight(pkg: Path):
    env = {k: v for k, v in os.environ.items() if k != "V52_T4F1_AUTH_HMAC_KEY_HEX"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run([PY, "-B", str(pkg / "candidate_package_preflight.py")],
                          capture_output=True, text=True, env=env, cwd=str(pkg))
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def fresh(name):
    dst = SCRATCH / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    return dst


RESULTS = []


def record(exp_id, description, expectation, rc, out, err):
    blocked = rc != 0
    verdict = "AS_EXPECTED" if blocked == (expectation == "BLOCK") else "UNEXPECTED"
    tail = (err or out).strip().splitlines()
    RESULTS.append({
        "id": exp_id, "description": description, "expected": expectation,
        "returncode": rc, "blocked": blocked, "verdict": verdict,
        "message_tail": tail[-1][:400] if tail else "",
    })


# --- F0 positive control: untouched copy must pass -------------------------------
p = fresh("F0_untouched")
record("F0", "untouched copy of the V5 package", "PASS", *run_preflight(p))

# --- F1 Gate 1: nested unbound file must be rejected ------------------------------
p = fresh("F1_nested_unbound")
(p / "nested").mkdir()
(p / "nested" / "extra_note.txt").write_text("unbound nested payload\n", encoding="utf-8")
record("F1", "nested unbound file added under nested/", "BLOCK", *run_preflight(p))

# --- F1b Gate 1: top-level unbound file must be rejected --------------------------
p = fresh("F1b_toplevel_unbound")
(p / "UNBOUND.txt").write_text("unbound top-level payload\n", encoding="utf-8")
record("F1b", "unbound top-level file added", "BLOCK", *run_preflight(p))

# --- F1c Gate 1: __pycache__ bytecode must be rejected ----------------------------
p = fresh("F1c_pycache")
(p / "__pycache__").mkdir()
(p / "__pycache__" / "v52_t4f1_beam_retrieval.cpython-312.pyc").write_bytes(b"\x00fake bytecode")
record("F1c", "generated __pycache__ bytecode present", "BLOCK", *run_preflight(p))

# --- F1d Gate 1: payload byte mutation must be rejected ---------------------------
p = fresh("F1d_mutated_payload")
spec = p / "EXECUTION_SPEC.md"
spec.write_text(spec.read_text(encoding="utf-8") + "\nmutation\n", encoding="utf-8")
record("F1d", "one bound payload mutated without updating PAYLOAD_HASHES.json", "BLOCK", *run_preflight(p))

# --- F2 Gate 2: runner byte change must void the delta route ----------------------
p = fresh("F2_runner_changed")
runner = p / "v52_t4f1_beam_retrieval.py"
body = runner.read_text(encoding="utf-8") + "\n# benign trailing comment\n"
runner.write_text(body, encoding="utf-8")
man = json.loads((p / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
for item in man["files"]:
    if item["name"] == "v52_t4f1_beam_retrieval.py":
        item["sha256"] = hashlib.sha256(runner.read_bytes()).hexdigest()
        item["bytes"] = runner.stat().st_size
(p / "PAYLOAD_HASHES.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", encoding="utf-8")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["payload_inventory"]["sha256"] = hashlib.sha256((p / "PAYLOAD_HASHES.json").read_bytes()).hexdigest()
seal["payload_inventory"]["bytes"] = (p / "PAYLOAD_HASHES.json").stat().st_size
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
record("F2", "runner byte-changed with inventory+seal consistently updated", "BLOCK", *run_preflight(p))

# --- F3 Gate 3.7: reintroduce CC-01 (second normative canary definition) ----------
CC01 = """
## Canary specification (raw-float digests)

The canary on `100K::12` additionally asserts that `sha256(centered96.tobytes())` equals
`25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025` and that
`sha256(query.tobytes())` equals
`e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`.
"""
p = fresh("F3_cc01_reintroduced")
spec = p / "EXECUTION_SPEC.md"
spec.write_text(spec.read_text(encoding="utf-8") + CC01, encoding="utf-8")
man = json.loads((p / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
for item in man["files"]:
    if item["name"] == "EXECUTION_SPEC.md":
        item["sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
        item["bytes"] = spec.stat().st_size
(p / "PAYLOAD_HASHES.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", encoding="utf-8")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["payload_inventory"]["sha256"] = hashlib.sha256((p / "PAYLOAD_HASHES.json").read_bytes()).hexdigest()
seal["payload_inventory"]["bytes"] = (p / "PAYLOAD_HASHES.json").stat().st_size
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
record("F3", "CC-01 reintroduced verbatim: second normative canary with V3 raw-float digests",
       "BLOCK", *run_preflight(p))

# --- F3b Gate 7: same CC-01 with the digests split across lines -------------------
CC01_SPLIT = """
## Canary specification (raw-float digests, wrapped)

The canary on `100K::12` additionally asserts that `sha256(centered96.tobytes())` equals
`25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f5
80025` and that `sha256(query.tobytes())` equals
`e422490a26d0934f31b06f808391d545e50282642af8997a2
4cb1d4e94fab869`.
"""
p = fresh("F3b_cc01_line_split")
spec = p / "EXECUTION_SPEC.md"
spec.write_text(spec.read_text(encoding="utf-8") + CC01_SPLIT, encoding="utf-8")
man = json.loads((p / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
for item in man["files"]:
    if item["name"] == "EXECUTION_SPEC.md":
        item["sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
        item["bytes"] = spec.stat().st_size
(p / "PAYLOAD_HASHES.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", encoding="utf-8")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["payload_inventory"]["sha256"] = hashlib.sha256((p / "PAYLOAD_HASHES.json").read_bytes()).hexdigest()
seal["payload_inventory"]["bytes"] = (p / "PAYLOAD_HASHES.json").stat().st_size
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
record("F3b", "CC-01 reintroduced with each V3 digest wrapped across two prose lines",
       "BLOCK", *run_preflight(p))

# --- F3c Gate 7: same CC-01 with uppercase hex digests ----------------------------
CC01_UPPER = CC01.replace("25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025",
                          "25089A07760A08D816F9AE0C8AF2F02B284E1217807AF4D0270ACBB58F580025").replace(
                          "e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869",
                          "E422490A26D0934F31B06F808391D545E50282642AF8997A24CB1D4E94FAB869")
p = fresh("F3c_cc01_uppercase")
spec = p / "EXECUTION_SPEC.md"
spec.write_text(spec.read_text(encoding="utf-8") + CC01_UPPER, encoding="utf-8")
man = json.loads((p / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
for item in man["files"]:
    if item["name"] == "EXECUTION_SPEC.md":
        item["sha256"] = hashlib.sha256(spec.read_bytes()).hexdigest()
        item["bytes"] = spec.stat().st_size
(p / "PAYLOAD_HASHES.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", encoding="utf-8")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["payload_inventory"]["sha256"] = hashlib.sha256((p / "PAYLOAD_HASHES.json").read_bytes()).hexdigest()
seal["payload_inventory"]["bytes"] = (p / "PAYLOAD_HASHES.json").stat().st_size
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
record("F3c", "CC-01 reintroduced with the V3 digests in uppercase hex", "BLOCK", *run_preflight(p))

# --- F4 Gate 4: seal claiming post-audit acceptance via `status` -------------------
def reseal(p):
    man = json.loads((p / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    for item in man["files"]:
        f = p / item["name"]
        item["sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
        item["bytes"] = f.stat().st_size
    (p / "PAYLOAD_HASHES.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    seal["payload_inventory"]["sha256"] = hashlib.sha256((p / "PAYLOAD_HASHES.json").read_bytes()).hexdigest()
    seal["payload_inventory"]["bytes"] = (p / "PAYLOAD_HASHES.json").stat().st_size
    (p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")

p = fresh("F4_seal_status_accepted")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["status"] = "ACCEPTED_BY_HEAD_RESEARCHER_AND_CO_CHAIR"
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F4", "seal adds status = ACCEPTED_BY_HEAD_RESEARCHER_AND_CO_CHAIR", "BLOCK", *run_preflight(p))

# --- F4b Gate 4: submission status edited to express acceptance --------------------
p = fresh("F4b_submission_status_accepted")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["status_at_audit_submission"] = "INDEPENDENTLY_AUDITED_AND_ACCEPTED"
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F4b", "status_at_audit_submission edited to INDEPENDENTLY_AUDITED_AND_ACCEPTED", "BLOCK", *run_preflight(p))

# --- F4c Gate 7: acceptance re-enters under a DIFFERENT field name -----------------
p = fresh("F4c_acceptance_alias_field")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["current_acceptance_state"] = "ACCEPTED_BY_HEAD_RESEARCHER_AND_CO_CHAIR_2026_09_02"
seal["independent_audit_result"] = "PASS"
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F4c", "seal carries acceptance under new field names current_acceptance_state / independent_audit_result",
       "BLOCK", *run_preflight(p))

# --- F5 Gate 3/7: authorization commitment filled in (fail-closed removed) ---------
p = fresh("F5_commitment_filled")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["authorization_control"]["key_commitment_sha256"] = "0" * 64
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F5", "seal key commitment replaced by a concrete 64-hex value (fail-closed removed)", "BLOCK", *run_preflight(p))

# --- F6 Gate 7: vacuous map - deprecated registry emptied --------------------------
p = fresh("F6_empty_deprecated_registry")
sm = json.loads((p / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
sm["deprecated_literals"] = []
(p / "NORMATIVE_SOURCE_MAP.json").write_text(json.dumps(sm, indent=2, sort_keys=True) + "\n", encoding="utf-8")
spec = p / "EXECUTION_SPEC.md"
spec.write_text(spec.read_text(encoding="utf-8") + CC01, encoding="utf-8")
reseal(p)
record("F6", "deprecated-literal registry emptied AND CC-01 raw-float canary re-added", "BLOCK", *run_preflight(p))

# --- F7 Gate 7: vacuous map - concept list emptied of a load-bearing concept -------
p = fresh("F7_concept_dropped")
sm = json.loads((p / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
sm["fields"] = [f for f in sm["fields"] if f["concept"] != "canary_algorithm_and_digests"]
(p / "NORMATIVE_SOURCE_MAP.json").write_text(json.dumps(sm, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F7", "canary_algorithm_and_digests concept deleted from the source map", "BLOCK", *run_preflight(p))

# --- F8 Gate 7: mirror typed as derived but disagreeing with authoritative value ----
p = fresh("F8_mirror_disagrees")
seal = json.loads((p / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
seal["authorization_control"]["signed_fields"] = seal["authorization_control"]["signed_fields"][:-1]
(p / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F8", "typed mirror seal.authorization_control.signed_fields drops a signed field", "BLOCK", *run_preflight(p))

# --- F9 Gate 7: duplicate normative concept ----------------------------------------
p = fresh("F9_duplicate_concept")
sm = json.loads((p / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
dup = dict(next(f for f in sm["fields"] if f["concept"] == "canary_algorithm_and_digests"))
dup["authoritative_path"] = "README.md"
sm["fields"].append(dup)
(p / "NORMATIVE_SOURCE_MAP.json").write_text(json.dumps(sm, indent=2, sort_keys=True) + "\n", encoding="utf-8")
reseal(p)
record("F9", "canary concept declared twice with a second authoritative path", "BLOCK", *run_preflight(p))

# --- F10 Gate 7: new untyped normative source added for an existing concept ---------
p = fresh("F10_untyped_second_source")
spec = p / "EXECUTION_SPEC.md"
spec.write_text(spec.read_text(encoding="utf-8") +
                "\n## Aggregation (normative)\n\nEqual question weighting over 1712 questions; "
                "seeds and trials are independent statistical units.\n", encoding="utf-8")
reseal(p)
record("F10", "a NEW second normative statement contradicting aggregation_rule added to EXECUTION_SPEC.md",
       "BLOCK", *run_preflight(p))

# --- integrity: source namespace untouched ------------------------------------------
AFTER = digest_tree(SRC)
print(json.dumps({
    "source_namespace": str(SRC),
    "source_unchanged": AFTER == BASELINE,
    "source_file_count": len(AFTER),
    "experiments": RESULTS,
}, indent=2))
