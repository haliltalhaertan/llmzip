"""V5 repair tests. Each case states what V3 did and asserts what V4 does.

Run from a directory holding both storage_adapter_preflight_v3.py and
storage_adapter_preflight_v4.py so the differential cases can execute. Synthetic data
only; no corpus, query, gold, outcome, model fit, seal or run.
"""
import hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from storage_adapter_preflight_v5 import preflight, PreflightError, PHYSICAL_BINDING_VERSION

CONTRACT_BYTES = b"# frozen measurement contract\n"
CONTRACT = hashlib.sha256(CONTRACT_BYTES).hexdigest()


def h(r):
    return hashlib.sha256(r).hexdigest()


def fixture_obj(byte_offset=0):
    return {"schema": "V52_SYNTHETIC_FIXTURE_BUNDLE_V3",
            "transform": {"input_utf8": "hello"},
            "id_mapping": {"rows": [{"logical_id": "a", "offset": 0, "payload_utf8": "A"},
                                    {"logical_id": "b", "offset": 1, "payload_utf8": "B"}]},
            "corruption": {"strategy": "XOR_SINGLE_BYTE", "byte_offset": byte_offset, "xor_mask": 1}}


def dump(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def build(root, plan_mut=None, fb_mut=None, pb_mut=None, fx=None, phys=b"PHYS", extra=None):
    root = Path(root)
    fr = dump(fx if fx is not None else fixture_obj())
    (root / "fx.json").write_bytes(fr)
    (root / "phys.bin").write_bytes(phys)
    (root / "contract.md").write_bytes(CONTRACT_BYTES)
    if extra:
        extra(root)
    plan = {"schema": "v52.static-storage-plan", "version": 1, "contract_sha256": CONTRACT,
            "fixtures": [{"id": "fx1", "sha256": h(fr)}],
            "physical_copies": [{"id": "pc1", "artifact_sha256": h(phys), "population_ids": ["p1"]}],
            "populations": [{"id": "p1", "count": 4}]}
    if plan_mut:
        plan_mut(plan)
    fb = {"schema": "v52.fixture-bindings", "version": 3,
          "fixtures": [{"fixture_id": "fx1", "relative_path": "fx.json", "byte_length": len(fr),
                        "sha256": h(fr), "content_schema": "V52_SYNTHETIC_FIXTURE_BUNDLE_V3",
                        "consumer_sections": {"TRANSFORM": "transform", "ID_MAPPING": "id_mapping",
                                              "CORRUPT": "corruption"}}]}
    if fb_mut:
        fb_mut(fb)
    pb = {"schema": "v52.physical-copy-bindings", "version": PHYSICAL_BINDING_VERSION,
          "physical_copies": [{"physical_copy_id": "pc1", "physical_locator": "phys.bin",
                               "source_raw_byte_length": len(phys), "artifact_sha256": h(phys),
                               "sharing_denominator_rule": "POPULATION_COUNT",
                               "absence_basis": None}]}
    if pb_mut:
        pb_mut(pb)

    def w(n, o):
        raw = dump(o)
        (root / n).write_bytes(raw)
        return h(raw)

    return w("plan.json", plan), w("fb.json", fb), w("pb.json", pb)


def run(root, hs, **kw):
    root = Path(root)
    kw.setdefault("guarded_plan_sha256", hs[0])
    kw.setdefault("guarded_contract_sha256", CONTRACT)
    return preflight(root / "plan.json", hs[0], root / "contract.md", CONTRACT,
                     root / "fb.json", hs[1], root / "pb.json", hs[2], **kw)


class V4RepairTests(unittest.TestCase):

    def test_baseline_still_accepts(self):
        with tempfile.TemporaryDirectory() as td:
            out = run(td, build(td))
            self.assertEqual(len(out.fixtures), 1)
            self.assertEqual(out.physical_copies[0].denominator_states, (("p1", "POSITIVE", 4),))
            self.assertEqual(out.contract_sha256, CONTRACT)

    # AUD-006 -- V3 hung forever here. V4 must refuse.
    def test_aud006_fifo_is_refused_not_hung(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, extra=lambda r: os.mkfifo(r / "pipe"),
                       pb_mut=lambda d: d["physical_copies"][0].update(physical_locator="pipe"))
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("regular file", str(cm.exception))

    def test_aud006_v3_really_hangs_on_the_same_input(self):
        """Differential evidence: the same fixture kills V3. Skipped if V3 is absent."""
        if not Path("storage_adapter_preflight_v3.py").exists():
            self.skipTest("V3 module not present next to V4")
        script = (
            "import os,json,hashlib,tempfile,sys\n"
            "from pathlib import Path\n"
            "from storage_adapter_preflight_v3 import preflight\n"
            "h=lambda r: hashlib.sha256(r).hexdigest()\n"
            "d=lambda o: json.dumps(o,sort_keys=True,separators=(',',':')).encode()\n"
            "td=tempfile.mkdtemp(); r=Path(td)\n"
            "fx=" + repr(fixture_obj()) + "\n"
            "fr=d(fx); (r/'fx.json').write_bytes(fr); os.mkfifo(r/'pipe')\n"
            "plan={'schema':'v52.static-storage-plan','version':1,"
            "'fixtures':[{'id':'fx1','sha256':h(fr)}],"
            "'physical_copies':[{'id':'pc1','artifact_sha256':h(b'X'),'population_ids':['p1']}],"
            "'populations':[{'id':'p1','count':4}]}\n"
            "fb={'schema':'v52.fixture-bindings','version':3,'fixtures':[{'fixture_id':'fx1',"
            "'relative_path':'fx.json','byte_length':len(fr),'sha256':h(fr),"
            "'content_schema':'V52_SYNTHETIC_FIXTURE_BUNDLE_V3','consumer_sections':"
            "{'TRANSFORM':'transform','ID_MAPPING':'id_mapping','CORRUPT':'corruption'}}]}\n"
            "pb={'schema':'v52.physical-copy-bindings','version':3,'physical_copies':[{"
            "'physical_copy_id':'pc1','physical_locator':'pipe','source_raw_byte_length':1,"
            "'artifact_sha256':h(b'X'),'sharing_denominator_rule':'POPULATION_COUNT'}]}\n"
            "w=lambda n,o:( (r/n).write_bytes(d(o)), h(d(o)) )[1]\n"
            "hp,hf,hb=w('plan.json',plan),w('fb.json',fb),w('pb.json',pb)\n"
            "preflight(r/'plan.json',hp,r/'fb.json',hf,r/'pb.json',hb)\n"
        )
        try:
            subprocess.run([sys.executable, "-B", "-c", script], timeout=6,
                           capture_output=True, cwd=os.getcwd())
        except subprocess.TimeoutExpired:
            return  # V3 hung, which is the finding
        self.fail("expected V3 to hang on a FIFO locator; it did not")

    # AUD-007 -- V3 had no way to know which plan the guard validated.
    def test_aud007_guarded_plan_must_match(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td)
            run(td, hs)                                            # matching is fine
            with self.assertRaises(PreflightError) as cm:
                run(td, hs, guarded_plan_sha256="d" * 64)
            self.assertIn("guarded plan digest", str(cm.exception))

    def test_aud007_binding_cannot_be_skipped(self):
        """V4 defaulted the guard digests to None and skipped the check entirely."""
        with tempfile.TemporaryDirectory() as td:
            hs = build(td)
            root = Path(td)
            with self.assertRaises(TypeError):
                preflight(root / "plan.json", hs[0], root / "contract.md", CONTRACT,
                          root / "fb.json", hs[1], root / "pb.json", hs[2])

    def test_aud007_contract_is_authenticated_from_its_own_bytes(self):
        """V4 compared a bare string that no file had to match."""
        with tempfile.TemporaryDirectory() as td:
            hs = build(td)
            Path(td, "contract.md").write_bytes(b"tampered contract\n")
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("contract: SHA256 mismatch", str(cm.exception))

    def test_aud007_guarded_contract_must_match(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td)
            with self.assertRaises(PreflightError) as cm:
                run(td, hs, guarded_contract_sha256="e" * 64)
            self.assertIn("guarded contract digest", str(cm.exception))

    def test_aud007_plan_must_name_the_expected_contract(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, plan_mut=lambda p: p.update(contract_sha256="e" * 64))
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("contract digest", str(cm.exception))

    # AUD-002 -- V3 accepted byte_offset = 10**12 against a 274-byte artifact.
    def test_aud002_corruption_offset_is_bounded_by_the_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, fx=fixture_obj(byte_offset=10**12))
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("byte_offset", str(cm.exception))

    def test_aud002_offset_inside_the_artifact_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            run(td, build(td, fx=fixture_obj(byte_offset=3)))

    # AUD-005 -- V3 accepted a zero-byte artifact with no evidence of absence.
    def test_aud005_zero_byte_artifact_needs_an_absence_basis(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, phys=b"")
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("absence basis", str(cm.exception))

    def test_aud005_zero_byte_artifact_with_basis_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, phys=b"",
                       pb_mut=lambda d: d["physical_copies"][0].update(
                           absence_basis="no persistent rotation exists for this arm"))
            run(td, hs)

    def test_aud005_nonempty_artifact_must_not_claim_absence(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, pb_mut=lambda d: d["physical_copies"][0].update(absence_basis="x"))
            with self.assertRaises(PreflightError):
                run(td, hs)

    # AUD-009 -- V3 leaked IsADirectoryError and ValueError.
    def test_aud009_directory_locator_is_a_preflight_error(self):
        for mut in (lambda d: d["fixtures"][0].update(relative_path="."),):
            with tempfile.TemporaryDirectory() as td:
                hs = build(td, fb_mut=mut)
                with self.assertRaises(PreflightError):
                    run(td, hs)

    def test_aud009_nul_in_path_is_a_preflight_error(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, fb_mut=lambda d: d["fixtures"][0].update(relative_path="a\x00b"))
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("NUL", str(cm.exception))

    def test_aud009_missing_plan_subfield_is_a_preflight_error(self):
        for mut in (lambda p: p["fixtures"][0].pop("sha256"),
                    lambda p: p["physical_copies"][0].pop("population_ids"),
                    lambda p: p["populations"][0].pop("count")):
            with tempfile.TemporaryDirectory() as td:
                hs = build(td, plan_mut=mut)
                with self.assertRaises(PreflightError) as cm:
                    run(td, hs)
                self.assertIn("missing field", str(cm.exception))

    # AUD-010 -- V3 accepted version True and 1.0.
    def test_aud010_version_must_be_a_real_int(self):
        for bad in (True, 1.0):
            with tempfile.TemporaryDirectory() as td:
                hs = build(td, plan_mut=lambda p, b=bad: p.update(version=b))
                with self.assertRaises(PreflightError):
                    run(td, hs)

    # AUD-011 -- V3 accepted two declared copies resolving to one file.
    def test_aud011_two_copies_must_not_be_one_file(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(
                td,
                plan_mut=lambda p: p["physical_copies"].append(
                    {"id": "pc2", "artifact_sha256": h(b"PHYS"), "population_ids": ["p1"]}),
                pb_mut=lambda d: d["physical_copies"].append(
                    {"physical_copy_id": "pc2", "physical_locator": "phys.bin",
                     "source_raw_byte_length": 4, "artifact_sha256": h(b"PHYS"),
                     "sharing_denominator_rule": "POPULATION_COUNT", "absence_basis": None}))
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("one file", str(cm.exception))

    def test_aud011_symlinked_duplicate_is_also_refused(self):
        def add_link(r):
            os.symlink(r / "phys.bin", r / "alias.bin")
        with tempfile.TemporaryDirectory() as td:
            hs = build(
                td, extra=add_link,
                plan_mut=lambda p: p["physical_copies"].append(
                    {"id": "pc2", "artifact_sha256": h(b"PHYS"), "population_ids": ["p1"]}),
                pb_mut=lambda d: d["physical_copies"].append(
                    {"physical_copy_id": "pc2", "physical_locator": "alias.bin",
                     "source_raw_byte_length": 4, "artifact_sha256": h(b"PHYS"),
                     "sharing_denominator_rule": "POPULATION_COUNT", "absence_basis": None}))
            with self.assertRaises(PreflightError):
                run(td, hs)

    # Preserved from V3: the closures that must not regress.
    def test_preserved_authenticated_bytes_survive_source_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            out = run(td, build(td))
            before = out.fixtures[0].raw_bytes
            Path(td, "fx.json").write_bytes(b'{"mutated":true}')
            self.assertEqual(before, out.fixtures[0].raw_bytes)
            self.assertEqual(out.fixtures[0].reverify(), before)

    def test_reverify_catches_an_in_process_swap(self):
        """The caveat CORRECTION_01 recorded: frozen blocks rebinding only."""
        with tempfile.TemporaryDirectory() as td:
            out = run(td, build(td))
            object.__setattr__(out.fixtures[0], "raw_bytes", b"EVIL")
            with self.assertRaises(PreflightError):
                out.fixtures[0].reverify()

    def test_preserved_zero_population_yields_no_denominator(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, plan_mut=lambda p: (
                p["physical_copies"][0].update(population_ids=["p0", "p1"]),
                p.update(populations=[{"id": "p0", "count": 0}, {"id": "p1", "count": 4}])))
            out = run(td, hs)
            self.assertEqual(out.physical_copies[0].denominator_states[0], ("p0", "EMPTY_NO_AMORTIZATION", None))
            self.assertEqual(out.physical_copies[0].denominator_states[1], ("p1", "POSITIVE", 4))

    def test_preserved_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            hs = list(build(td))
            raw = b'{"schema":"v52.fixture-bindings","schema":"v52.fixture-bindings","version":3,"fixtures":[]}'
            Path(td, "fb.json").write_bytes(raw)
            hs[1] = h(raw)
            with self.assertRaises(PreflightError):
                run(td, hs)

    def test_preserved_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            hs = list(build(td))
            raw = b'{"schema":"v52.fixture-bindings","version":3,"fixtures":NaN}'
            Path(td, "fb.json").write_bytes(raw)
            hs[1] = h(raw)
            with self.assertRaises(PreflightError):
                run(td, hs)

    def test_preserved_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, fb_mut=lambda d: d["fixtures"][0].update(relative_path="../escape.json"))
            with self.assertRaises(PreflightError):
                run(td, hs)


    # --- V5: what the V4 audit found ------------------------------------------
    def test_v5_lone_surrogate_in_locator_is_a_preflight_error(self):
        """V4 leaked UnicodeEncodeError from Path.resolve(), which is a ValueError."""
        for mut, key in ((lambda d: d["physical_copies"][0].update(physical_locator="\ud800"), "pb"),
                         (lambda d: d["fixtures"][0].update(relative_path="\ud800"), "fb")):
            with tempfile.TemporaryDirectory() as td:
                hs = build(td, pb_mut=mut if key == "pb" else None,
                           fb_mut=mut if key == "fb" else None)
                with self.assertRaises(PreflightError):
                    run(td, hs)

    def test_v5_array_bound_matches_the_parent_guard(self):
        """V4 used 1024 for arrays where the parent guard allows 4096."""
        from storage_adapter_preflight_v5 import MAX_ENTITIES, MAX_ARRAY_ENTRIES
        self.assertEqual(MAX_ENTITIES, 1024)
        self.assertEqual(MAX_ARRAY_ENTRIES, 4096)

    def test_v5_physical_bindings_version_moved_off_the_collision(self):
        """V4 changed the field set while keeping version 3."""
        self.assertEqual(PHYSICAL_BINDING_VERSION, 4)
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, pb_mut=lambda d: d.update(version=3))
            with self.assertRaises(PreflightError):
                run(td, hs)

    def test_v5_fixture_and_copy_may_not_share_one_file(self):
        """V4 deduplicated physical copies only."""
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, pb_mut=lambda d: d["physical_copies"][0].update(
                physical_locator="fx.json", source_raw_byte_length=None))
            with self.assertRaises(PreflightError):
                run(td, hs)

    def test_v5_empty_physical_copy_roster_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            hs = build(td, plan_mut=lambda p: p.update(physical_copies=[]),
                       pb_mut=lambda d: d.update(physical_copies=[]))
            with self.assertRaises(PreflightError) as cm:
                run(td, hs)
            self.assertIn("at least one required", str(cm.exception))

    def test_v5_read_is_linear_not_quadratic(self):
        import time
        from storage_adapter_preflight_v5 import read_bytes, MAX_ARTIFACT_BYTES
        with tempfile.TemporaryDirectory() as td:
            p = Path(td, "big.bin")
            p.write_bytes(b"x" * (32 * 1024 * 1024))
            t = time.perf_counter(); read_bytes(p, MAX_ARTIFACT_BYTES, "perf"); loop = time.perf_counter() - t
            t = time.perf_counter(); p.read_bytes(); plain = time.perf_counter() - t
            self.assertLess(loop, max(plain * 8, 0.5), f"read loop {loop:.3f}s vs plain {plain:.3f}s")


if __name__ == "__main__":
    unittest.main()
