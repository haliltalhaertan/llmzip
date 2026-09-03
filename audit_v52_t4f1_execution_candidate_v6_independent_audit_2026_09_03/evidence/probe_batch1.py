import json, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from probe_rig import stage, rebind, gate, verdict

DEP = "25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025"  # declared deprecated V3 canary
COHORT = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"  # live, NOT permitted in README
NOVEL64 = "a" * 63 + "b"
NOVEL40 = "c" * 39 + "d"
results = []

def probe(name, mutate, expect_block=True):
    root = stage()
    mutate(root)
    rebind(root)
    rc, out = gate(root)
    results.append(verdict(name, rc, out, expect_block))
    shutil.rmtree(root.parent, ignore_errors=True)

def append(root, fname, text):
    p = root / fname
    p.write_text(p.read_text() + text)

# --- 3.1 genuine discovery: novel tokens in fresh locations -----------------------
probe("3.1a novel 64-hex planted in README.md",
      lambda r: append(r, "README.md", f"\n\nAudit probe digest {NOVEL64}\n"))
probe("3.1b novel 40-hex planted in EXECUTION_SPEC.md",
      lambda r: append(r, "EXECUTION_SPEC.md", f"\n\nAudit probe commit {NOVEL40}\n"))
probe("3.1c novel v52_t4f identifier planted in README.md",
      lambda r: append(r, "README.md", "\n\nAudit probe v52_t4f9_fabricated_identifier\n"))
def json_novel(r):
    p = r / "RUN_AUTHORIZATION_TEMPLATE.json"
    d = json.loads(p.read_text()); d["audit_probe_field"] = NOVEL64
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
probe("3.1d novel 64-hex planted in a JSON value", json_novel)
def novel_in_new_bound_file(r):
    (r / "AUDIT_PROBE.md").write_text(f"probe {NOVEL64}\n")
probe("3.1e novel 64-hex in a NEW file added to the closure", novel_in_new_bound_file)

# --- 3.1f live token relocated to a path its concept does not permit ---------------
probe("3.1f live cohort digest relocated to README.md (undeclared repetition)",
      lambda r: append(r, "README.md", f"\n\nCohort {COHORT}\n"))

# --- 3.2 the exact V5 escapes -----------------------------------------------------
probe("3.2a V5 escape: deprecated literal WRAPPED across two lines",
      lambda r: append(r, "README.md", f"\n\nSuperseded canary {DEP[:32]}\n{DEP[32:]}\n"))
probe("3.2b V5 escape: deprecated literal in UPPERCASE",
      lambda r: append(r, "README.md", f"\n\nSuperseded canary {DEP.upper()}\n"))
probe("3.2c V5 escape combined: wrapped AND uppercase",
      lambda r: append(r, "README.md", f"\n\nSuperseded canary {DEP.upper()[:20]}\n{DEP.upper()[20:]}\n"))
probe("3.2d live cohort digest wrapped+uppercase at a non-permitted path",
      lambda r: append(r, "README.md", f"\n\n{COHORT.upper()[:30]}\n  {COHORT.upper()[30:]}\n"))

Path(__file__).parent.joinpath("probe_batch1.json").write_text(json.dumps(results, indent=2) + "\n")
bad = [r for r in results if not r["gate_behaved_as_required"]]
print(f"\n{len(results)-len(bad)}/{len(results)} probes behaved as required")
