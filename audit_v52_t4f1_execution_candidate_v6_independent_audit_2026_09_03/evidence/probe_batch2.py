import base64, json, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from probe_rig import stage, rebind, gate, verdict

DEP  = "25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025"
DEP2 = "e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869"
COHORT = "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"
NOVEL = "a"*63 + "b"
results = []

def probe(name, mutate, expect_block=True):
    root = stage(); mutate(root); rebind(root)
    rc, out = gate(root)
    results.append(verdict(name, rc, out, expect_block))
    shutil.rmtree(root.parent, ignore_errors=True)

def append(root, fname, text):
    p = root / fname; p.write_text(p.read_text() + text)

def edit_json(root, fname, fn):
    p = root / fname; d = json.loads(p.read_text()); fn(d)
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")

# ---- A. the normalisation/lookaround defect -------------------------------------
probe("A1 novel 64-hex preceded by a word ending in a hex char ('probe')",
      lambda r: append(r, "README.md", f"\n\nprobe {NOVEL}\n"))
probe("A2 novel 64-hex followed by a word starting with a hex char ('and')",
      lambda r: append(r, "README.md", f"\n\nDigest {NOVEL} and more\n"))
probe("A3 LIVE cohort digest relocated to README.md, hidden by hex-adjacent prose",
      lambda r: append(r, "README.md", f"\n\nThe cohort digest be {COHORT} and it is pinned\n"))

# ---- B. normalisation evasions of my own devising --------------------------------
probe("B1 deprecated literal split by a ZERO WIDTH SPACE",
      lambda r: append(r, "README.md", f"\n\nCanary {DEP[:32]}​{DEP[32:]}\n"))
probe("B2 deprecated literal with Cyrillic look-alike characters",
      lambda r: append(r, "README.md", "\n\nCanary " + DEP.replace("a","а",1).replace("c","с",1) + "\n"))
probe("B3 deprecated literal interleaved with HTML comment markup",
      lambda r: append(r, "README.md", f"\n\nCanary {DEP[:20]}<!---->{DEP[20:]}\n"))
probe("B4 deprecated literal re-encoded as base64",
      lambda r: append(r, "README.md", "\n\nCanary " + base64.b64encode(bytes.fromhex(DEP)).decode() + "\n"))
probe("B5 deprecated literal re-encoded as a decimal integer",
      lambda r: append(r, "README.md", f"\n\nCanary {int(DEP,16)}\n"))
def split_keys(r):
    edit_json(r, "RUN_AUTHORIZATION_TEMPLATE.json",
              lambda d: d.update({"probe_hi": DEP[:32], "probe_lo": DEP[32:]}))
probe("B6 deprecated literal split across two JSON keys", split_keys)
def non_utf8(r):
    (r / "AUDIT_PROBE.bin").write_bytes(b"\xff\xfe superseded canary " + DEP.encode() + b"\n")
probe("B7 deprecated literal inside a bound but non-UTF-8 payload", non_utf8)
def in_attestation(r):
    p = r.parent / "docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json"
    d = json.loads(p.read_text()); d["probe_note"] = f"superseded canary {DEP} and novel {NOVEL}"
    p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
probe("B8 deprecated + novel literal inside the DETACHED ATTESTATION (outside closure)", in_attestation)

# ---- C. exempt-class scope --------------------------------------------------------
def files_subtree(r):
    edit_json(r, "PAYLOAD_HASHES.json",
              lambda d: d["files"][0].update({"provenance_digest": NOVEL}))
probe("C1 novel digest smuggled into PAYLOAD_HASHES files[] (non-digest key)", files_subtree)
def prefix_widen(r):
    edit_json(r, "CANDIDATE_EXECUTION_SEAL.json",
              lambda d: d.update({"supersedes_candidate_addendum": {"x": NOVEL}}))
probe("C2 novel digest under key 'supersedes_candidate_addendum' (startswith widening)", prefix_widen)
def payload_inv_widen(r):
    edit_json(r, "CANDIDATE_EXECUTION_SEAL.json",
              lambda d: d["payload_inventory"].update({"smuggled": NOVEL}))
probe("C3 novel digest under payload_inventory.smuggled (exempt subtree)", payload_inv_widen)
def ns_swap(r):
    p = r / "EXECUTION_SPEC.md"
    p.write_text(p.read_text().replace("v52_t4f0_restricted_refreeze_2026_08_31",
                                       "v52_t4f0_codex_2026_08_31"))
probe("C4 sealed-4F0 namespace identifier SWAPPED (restricted_refreeze -> codex)", ns_swap)

# (blind-spot drift probes D* moved to probe_batch3.py)

Path(__file__).parent.joinpath("probe_batch2.json").write_text(json.dumps(results, indent=2) + "\n")
bad = [r for r in results if not r["gate_behaved_as_required"]]
print(f"\n{len(results)-len(bad)}/{len(results)} behaved as required; {len(bad)} evasions succeeded")
