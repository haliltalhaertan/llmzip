import json, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from probe_rig import stage, rebind, gate, verdict

NOVEL = "a"*63 + "b"
results = []

def probe(name, mutate, expect_block=True):
    root = stage(); mutate(root); rebind(root)
    rc, out = gate(root)
    results.append(verdict(name, rc, out, expect_block))
    shutil.rmtree(root.parent, ignore_errors=True)

def sub(fname, old, new):
    def _m(r):
        p = r / fname; t = p.read_text()
        assert old in t, f"{old!r} absent from {fname}"
        p.write_text(t.replace(old, new))
    return _m

def edit_json(root, fname, fn):
    p = root / fname; d = json.loads(p.read_text()); fn(d)
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")

# ---- D. load-bearing values outside the three token shapes ------------------------
probe("D1 estimand denominator eligible_questions 1712 -> 1713 (seal)",
      sub("CANDIDATE_EXECUTION_SEAL.json", '"eligible_questions": 1712', '"eligible_questions": 1713'))
probe("D2 excluded archive 1M::5 -> 1M::7 (seal)",
      sub("CANDIDATE_EXECUTION_SEAL.json", '"1M::5"', '"1M::7"'))
probe("D3 arm identifier NATIVE_SIGN96 -> NATIVE_SIGN97 (spec)",
      sub("EXECUTION_SPEC.md", "NATIVE_SIGN96", "NATIVE_SIGN97"))
probe("D4 Haar seed 43001 -> 43011 (spec)", sub("EXECUTION_SPEC.md", "43001", "43011"))
probe("D5 invariance tolerance 1e-12 -> 1e-10 (spec)", sub("EXECUTION_SPEC.md", "1e-12", "1e-10"))
probe("D6 latent seed 5101 -> 5102 (spec)", sub("EXECUTION_SPEC.md", "`5101`", "`5102`"))
probe("D7 canary threshold '>= 0' -> '> 0' (spec)", sub("EXECUTION_SPEC.md", "threshold at `>= 0`", "threshold at `> 0`"))

# ---- E. structural rules on the map ------------------------------------------------
def dup_concept(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json",
              lambda d: d["fields"].append(dict(d["fields"][0])))
probe("E1 duplicate normative concept declared twice", dup_concept)
def bad_path(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json",
              lambda d: d["fields"][0].update({"authoritative_path": "NO_SUCH_FILE.md"}))
probe("E2 concept pointing at a non-existent path", bad_path)
def no_locator(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json",
              lambda d: d["fields"][0].pop("locator"))
probe("E3 concept with no locator (no single source)", no_locator)
def empty_fields(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", lambda d: d.update({"fields": []}))
probe("E4 VACUITY: fields list emptied entirely", empty_fields)
def allowlist_everything(r):
    def _f(d):
        lits = []
        for f in d["fields"]:
            lits += f.get("scannable_literals", [])
        d["non_normative_token_classes"].append({
            "class": "audit_probe_blanket", "rationale": "probe",
            "files": ["README.md", "EXECUTION_SPEC.md", "CANDIDATE_EXECUTION_SEAL.json",
                      "PAYLOAD_HASHES.json", "RUN_AUTHORIZATION_TEMPLATE.json",
                      "NORMATIVE_SOURCE_MAP.json", "v52_t4f1_beam_retrieval.py",
                      "candidate_package_preflight.py", "DEPENDENCY_LOCK.txt"],
            "token_allowlist": lits + [NOVEL]})
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", _f)
    p = r / "README.md"; p.write_text(p.read_text() + f"\n\nDigest {NOVEL} planted\n")
probe("E5 a new blanket exempt class silently excuses everything", allowlist_everything)
def prose_widen(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json",
              lambda d: d.update({"purpose": d["purpose"] + f" Exempt everything including {NOVEL}."}))
probe("E6 declaration-site: unattributed digest added to map PROSE (must be swept)", prose_widen)
def in_fields_block(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json",
              lambda d: d["fields"][0].update({"audit_probe_note": f"unattributed {NOVEL}"}))
probe("E7 declaration-site: unattributed digest hidden inside the fields block", in_fields_block)
def dep_disarm(r):
    def _f(d):
        d["deprecated_literals"][0]["must_not_appear_as_requirement"] = False
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", _f)
    p = r / "README.md"
    p.write_text(p.read_text() + "\n\nCanary 25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025\n")
probe("E8 deprecated literal disarmed via must_not_appear_as_requirement=false", dep_disarm)

# ---- F. attestation and submission-status semantics (Gate 4) ----------------------
def rm_attest(r):
    (r.parent / "docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json").unlink()
probe("F1 attestation file removed", rm_attest)
def bad_state(r):
    p = r.parent / "docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json"
    d = json.loads(p.read_text()); d["acceptance_state"] = "ACCEPTED_FOR_V6"
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
probe("F2 attestation disagrees with declared acceptance state", bad_state)
def seal_status(r):
    edit_json(r, "CANDIDATE_EXECUTION_SEAL.json", lambda d: d.update({"status": "ACCEPTED"}))
probe("F3 seal claims a post-audit state via a second status field", seal_status)
def inv_status(r):
    edit_json(r, "PAYLOAD_HASHES.json", lambda d: d.update({"status": "ACCEPTED"}))
probe("F4 inventory carries a status field", inv_status)
def self_attest(r):
    (r / "SELF_ATTESTATION.json").write_text(json.dumps(
        {"acceptance_state": "NOT_YET_ACCEPTED_FOR_V6", "note": "written inside the candidate"},
        indent=2) + "\n")
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", lambda d: [
        f.update({"authoritative_path": "task4f1_execution_candidate_v6_2026_09_03/SELF_ATTESTATION.json"})
        for f in d["fields"] if f["concept"] == "post_audit_acceptance_state"])
probe("F5 attestation redirected to a file INSIDE the candidate namespace", self_attest)

Path(__file__).parent.joinpath("probe_batch3.json").write_text(json.dumps(results, indent=2) + "\n")
bad = [r for r in results if not r["gate_behaved_as_required"]]
print(f"\n{len(results)-len(bad)}/{len(results)} behaved as required; {len(bad)} gaps")
