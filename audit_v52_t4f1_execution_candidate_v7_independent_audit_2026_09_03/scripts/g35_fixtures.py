#!/usr/bin/env python3
"""Independent negative/positive fixtures against the V7 package checker.

Every fixture is built in a throwaway copy under the scratch tree. The real candidate
is never written to. No fixture invokes the runner; only the out-of-band checker runs,
and only through the refusing harness.
"""
from __future__ import annotations
import hashlib, json, shutil, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safe_harness as H

REAL = Path("/home/user/llmzip/task4f1_execution_candidate_v7_2026_09_03")
WORK = Path(sys.argv[1])
PY = sys.argv[2]
CHECKER = "candidate_package_preflight.py"

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def reseal(root: Path) -> None:
    """Recompute the inventory over on-disk payload and re-point the seal at it.

    This models an adversary who controls every file in the package, which is exactly
    the adversary the V5/V6 audits faced (the gate's own configuration lived inside
    the package). It shows what the checker can and cannot detect on its own.
    """
    manifest = json.loads((root / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if rel in ("PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"):
            continue
        files.append({"bytes": p.stat().st_size, "name": rel, "sha256": sha(p)})
    manifest["files"] = files
    manifest["file_count_excluding_inventory_and_seal"] = len(files)
    (root / "PAYLOAD_HASHES.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    seal = json.loads((root / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    seal["payload_inventory"]["sha256"] = sha(root / "PAYLOAD_HASHES.json")
    seal["payload_inventory"]["bytes"] = (root / "PAYLOAD_HASHES.json").stat().st_size
    (root / "CANDIDATE_EXECUTION_SEAL.json").write_text(
        json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")


RESULTS = []


def fixture(fid: str, gate: str, desc: str, expect: str, mutate, do_reseal=False):
    root = WORK / fid
    if root.exists():
        shutil.rmtree(root)
    shutil.copytree(REAL, root)
    note = mutate(root) or ""
    if do_reseal:
        reseal(root)
    rec = H.run([PY, "-B", CHECKER], cwd=str(root))
    blocked = rec.get("returncode", 1) != 0
    outcome = "BLOCKED" if blocked else "PASSED"
    RESULTS.append({
        "id": fid, "gate": gate, "description": desc, "resealed": do_reseal,
        "expected": expect, "observed": outcome,
        "agrees_with_expectation": outcome == expect,
        "note": note,
        "checker_returncode": rec.get("returncode"),
        "checker_stdout": (rec.get("stdout") or "").strip(),
        "checker_error": (rec.get("stderr") or "").strip().splitlines()[-1] if rec.get("stderr") else "",
    })
    shutil.rmtree(root, ignore_errors=True)


# ---------- positive control ----------
fixture("F00_pristine", "5", "Unmodified copy of the real candidate", "PASSED", lambda r: "positive control")

# ---------- Gate 1: closure ----------
fixture("F01_nested_unbound", "1", "Nested unbound file in a subdirectory", "BLOCKED",
        lambda r: (r / "sub").mkdir() or (r / "sub" / "extra.txt").write_text("unbound\n") and "")
fixture("F02_toplevel_unbound", "1", "Top-level unbound file", "BLOCKED",
        lambda r: (r / "EXTRA.md").write_text("unbound narrative\n") and "")
fixture("F03_hidden_unbound", "1", "Hidden dotfile unbound at top level", "BLOCKED",
        lambda r: (r / ".hidden.md").write_text("hidden narrative\n") and "")
fixture("F04_pycache", "1", "Generated __pycache__ directory present", "BLOCKED",
        lambda r: (r / "__pycache__").mkdir() or (r / "__pycache__" / "x.pyc").write_bytes(b"\x00") and "")

# ---------- Gate 3.3: attack the set equality ----------
def _narrative_named_functional(r: Path):
    (r / "DEPENDENCY_LOCK.txt").write_text(
        "V52 Task 4F1 EXECUTION SPECIFICATION\n"
        "The canary acceptance criterion is digest aaaa...; the cohort is 1712 questions.\n"
        "Required archives: 95\n", encoding="utf-8")
    return "narrative prose written into a bound FUNCTIONAL name"
fixture("F05_narrative_in_functional_name", "3.3",
        "Narrative document content placed under a bound functional file name (no reseal)",
        "BLOCKED", _narrative_named_functional)
fixture("F06_narrative_in_functional_name_resealed", "3.3",
        "Same, but inventory and seal recomputed by the adversary", "PASSED",
        _narrative_named_functional, do_reseal=True)

def _embed_narrative_in_template(r: Path):
    t = json.loads((r / "RUN_AUTHORIZATION_TEMPLATE.json").read_text())
    t["note"] = ("SPECIFICATION: the run requires exactly 95 archives and seed 43009. "
                 "This restates a requirement inside a bound functional file.")
    (r / "RUN_AUTHORIZATION_TEMPLATE.json").write_text(json.dumps(t, indent=2) + "\n")
    return "requirement-stating prose embedded in a bound functional JSON"
fixture("F07_narrative_embedded_template", "3.3",
        "Narrative requirement embedded inside a bound functional file (no reseal)",
        "BLOCKED", _embed_narrative_in_template)
fixture("F08_narrative_embedded_template_resealed", "3.3",
        "Same, adversary recomputes inventory and seal", "PASSED",
        _embed_narrative_in_template, do_reseal=True)

fixture("F09_case_differing_name", "3.3", "Case-differing duplicate name added", "BLOCKED",
        lambda r: (r / "dependency_lock.txt").write_text("shadow\n") and "")
fixture("F10_unicode_confusable", "3.3", "Unicode-confusable Cyrillic name added", "BLOCKED",
        lambda r: (r / "DEPENDENCY_LOСK.txt").write_text("confusable\n") and "")

def _symlink(r: Path):
    tgt = r.parent / f"{r.name}_outside_narrative.md"
    tgt.write_text("outside narrative stating a requirement: 95 archives\n")
    (r / "DEPENDENCY_LOCK.txt").unlink()
    (r / "DEPENDENCY_LOCK.txt").symlink_to(tgt)
    return "bound name replaced by a symlink to an outside narrative file"
fixture("F11_symlink_bound_name", "3.3", "Bound functional name replaced by a symlink", "BLOCKED", _symlink)

def _declared_ne_ondisk(r: Path):
    m = json.loads((r / "PAYLOAD_HASHES.json").read_text())
    for i in m["files"]:
        if i["name"] == "DEPENDENCY_LOCK.txt":
            i["name"] = "DEPENDENCY_LOCK_RENAMED.txt"
    (r / "PAYLOAD_HASHES.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return "declared name differs from on-disk name"
fixture("F12_declared_name_mismatch", "3.3", "Declared payload name differs from on-disk name",
        "BLOCKED", _declared_ne_ondisk)

def _extra_declared(r: Path):
    m = json.loads((r / "PAYLOAD_HASHES.json").read_text())
    m["files"].append({"bytes": 10, "name": "EXECUTION_SPEC.md", "sha256": "00" * 32})
    (r / "PAYLOAD_HASHES.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return "narrative document declared in the inventory"
fixture("F13_narrative_declared", "3.3", "Narrative document added to the declared bound set",
        "BLOCKED", _extra_declared)

def _empty_inventory(r: Path):
    m = json.loads((r / "PAYLOAD_HASHES.json").read_text())
    m["files"] = []
    (r / "PAYLOAD_HASHES.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return "inventory declares nothing"
fixture("F14_empty_inventory", "7", "Malformed/empty inventory - vacuous pass check", "BLOCKED",
        _empty_inventory)

def _dup_entries(r: Path):
    m = json.loads((r / "PAYLOAD_HASHES.json").read_text())
    m["files"].append(dict(m["files"][0]))
    (r / "PAYLOAD_HASHES.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return "duplicate inventory entry; name set collapses"
fixture("F15_duplicate_entry", "7", "Duplicate inventory entry (set collapse)", "PASSED", _dup_entries)

# ---------- Gate 4: status / attestation ----------
def _seal_status(r: Path):
    s = json.loads((r / "CANDIDATE_EXECUTION_SEAL.json").read_text())
    s["status"] = "ACCEPTED"
    (r / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
    return "seal claims post-audit status"
fixture("F16_seal_status_field", "4", "Seal carries a post-audit 'status' field", "BLOCKED", _seal_status)

for field in ("accepted", "sealed", "acceptance_state"):
    def _mk(fld):
        def f(r: Path):
            s = json.loads((r / "CANDIDATE_EXECUTION_SEAL.json").read_text())
            s[fld] = True
            (r / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
            return f"seal carries '{fld}'"
        return f
    fixture(f"F17_seal_{field}", "4", f"Seal carries a '{field}' field", "BLOCKED", _mk(field))

def _inv_status(r: Path):
    m = json.loads((r / "PAYLOAD_HASHES.json").read_text())
    m["status"] = "ACCEPTED"
    (r / "PAYLOAD_HASHES.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return "inventory carries a status field"
fixture("F18_inventory_status", "4", "Inventory carries a status field", "BLOCKED", _inv_status, do_reseal=False)

def _submission_status(r: Path):
    s = json.loads((r / "CANDIDATE_EXECUTION_SEAL.json").read_text())
    s["status_at_audit_submission"] = "INDEPENDENTLY_AUDITED_AND_ACCEPTED"
    (r / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
    return "submission status rewritten"
fixture("F19_submission_status", "4", "Submission status claims acceptance", "BLOCKED", _submission_status)

# ---------- Gate 5/7: safety-critical fields ----------
def _runner_mod(r: Path):
    p = r / "v52_t4f1_beam_retrieval.py"
    p.write_text(p.read_text(encoding="utf-8").replace("EXPECTED_ARCHIVES = 96", "EXPECTED_ARCHIVES = 95"),
                 encoding="utf-8")
    return "runner constant changed"
fixture("F20_runner_modified", "2", "Runner modified (byte-identity broken, no reseal)", "BLOCKED", _runner_mod)
fixture("F21_runner_modified_resealed", "2", "Runner modified, adversary reseals inventory+seal",
        "BLOCKED", _runner_mod, do_reseal=True)

def _key_commitment(r: Path):
    s = json.loads((r / "CANDIDATE_EXECUTION_SEAL.json").read_text())
    s["authorization_control"]["key_commitment_sha256"] = "ab" * 32
    (r / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
    return "fail-closed commitment replaced"
fixture("F22_key_commitment_replaced", "7", "Fail-closed key commitment replaced", "BLOCKED", _key_commitment)

def _template_signed(r: Path):
    t = json.loads((r / "RUN_AUTHORIZATION_TEMPLATE.json").read_text())
    t["authorization_hmac_sha256"] = "cd" * 32
    (r / "RUN_AUTHORIZATION_TEMPLATE.json").write_text(json.dumps(t, indent=2) + "\n")
    return "template carries a signature"
fixture("F23_template_signed", "7", "Template carries an HMAC signature (no reseal)", "BLOCKED", _template_signed)
fixture("F24_template_signed_resealed", "7", "Template carries an HMAC signature, resealed",
        "BLOCKED", _template_signed, do_reseal=True)

def _template_authorized(r: Path):
    t = json.loads((r / "RUN_AUTHORIZATION_TEMPLATE.json").read_text())
    t["status"] = "AUTHORIZED_FOR_TASK_4F1_EXECUTION"
    (r / "RUN_AUTHORIZATION_TEMPLATE.json").write_text(json.dumps(t, indent=2) + "\n")
    return "template flipped to authorized"
fixture("F25_template_authorized_resealed", "7", "Template status flipped to AUTHORIZED, resealed",
        "BLOCKED", _template_authorized, do_reseal=True)

def _auth_block(r: Path):
    s = json.loads((r / "CANDIDATE_EXECUTION_SEAL.json").read_text())
    s["authorization"]["task_4f1_run"] = "AUTHORIZED"
    (r / "CANDIDATE_EXECUTION_SEAL.json").write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
    return "authorization boundary relaxed"
fixture("F26_auth_boundary", "7", "Seal authorization boundary relaxed", "BLOCKED", _auth_block)

out = Path(sys.argv[3])
out.write_text(json.dumps({
    "fixture_count": len(RESULTS),
    "disagreements": [r["id"] for r in RESULTS if not r["agrees_with_expectation"]],
    "results": RESULTS,
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
for r in RESULTS:
    flag = "  " if r["agrees_with_expectation"] else "!!"
    print(f"{flag} {r['id']:42s} gate{r['gate']:5s} expect={r['expected']:8s} observed={r['observed']}")
