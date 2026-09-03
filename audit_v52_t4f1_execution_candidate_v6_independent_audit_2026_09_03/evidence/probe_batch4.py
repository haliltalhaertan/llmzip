import json, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from probe_rig import stage, rebind, gate, verdict

results = []
def probe(name, mutate, expect_block=True):
    root = stage()
    if mutate: mutate(root)
    rebind(root)
    rc, out = gate(root)
    results.append(verdict(name, rc, out, expect_block))
    shutil.rmtree(root.parent, ignore_errors=True)

def edit_json(root, fname, fn):
    p = root / fname; d = json.loads(p.read_text()); fn(d)
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")

# G1 positive control: an unmodified staged copy must PASS
probe("G1 POSITIVE CONTROL: unmodified V6 copy passes", None, expect_block=False)

# G2 a declared mirror that no longer contains the value
def drop_mirror(r):
    p = r / "EXECUTION_SPEC.md"
    p.write_text(p.read_text().replace(
        "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a", "(removed)"))
probe("G2 declared mirror emptied of its value (cohort digest deleted from spec)", drop_mirror)

# G3 a mirror declared for a file that never contained the value
def phantom_mirror(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", lambda d: [
        f["mirrors"].append({"path": "DEPENDENCY_LOCK.txt", "locator": "phantom"})
        for f in d["fields"] if f["concept"] == "cohort_anchor"])
probe("G3 phantom mirror declared on a file that never held the value", phantom_mirror)

# G4 scannable_literals emptied for a hex concept (concept removes itself from the sweep)
def unlist(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", lambda d: [
        f.update({"scannable_literals": []})
        for f in d["fields"] if f["concept"] == "cohort_anchor"])
probe("G4 hex concept removes itself from the sweep (scannable_literals emptied)", unlist)

# G5 concept value silently changed while scannable_literals keeps the old literal
def value_drift(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", lambda d: [
        f["value"].update({"eligible_questions": 9999})
        for f in d["fields"] if f["concept"] == "cohort_anchor"])
probe("G5 concept 'value' drifts while scannable_literals stays correct", value_drift)

# G6 gate_claim prose rewritten to claim more than the gate does
def claim_inflation(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json",
              lambda d: d.update({"gate_claim": "Every literal of every kind is verified exhaustively."}))
probe("G6 gate_claim prose inflated (self-description not verified)", claim_inflation)

# G7 exempt class files[] list extended to cover a file it has no business covering
def widen_files(r):
    edit_json(r, "NORMATIVE_SOURCE_MAP.json", lambda d:
        d["non_normative_token_classes"][1]["files"].append("EXECUTION_SPEC.md"))
    p = r / "EXECUTION_SPEC.md"
    p.write_text(p.read_text() + "\n\nAudit probe " + "a"*63 + "b\n")
probe("G7 historical_provenance class widened to cover EXECUTION_SPEC.md", widen_files)

Path(__file__).parent.joinpath("probe_batch4.json").write_text(json.dumps(results, indent=2) + "\n")
bad = [r for r in results if not r["gate_behaved_as_required"]]
print(f"\n{len(results)-len(bad)}/{len(results)} behaved as required")
