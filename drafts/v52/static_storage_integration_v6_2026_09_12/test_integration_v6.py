"""V6 integration tests: the two guards are now mechanically linked.

The gap this closes survived three versions. V3 had no binding between the plan guard
and the preflight. V4 added one that defaulted off. V5 split the anchoring into a second
module and connected them with a sentence in a docstring - no code called it. The five
findings the Head Researcher reproduced on Windows are also covered here.

Synthetic data only, plus one committed metric table's archive-cardinality column. No
corpus, query, gold, outcome, model fit, seal or run. Platform-independent: the repo root
is discovered, never hardcoded.
"""
import hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

# The anchor guard is imported from its OWN namespace, never copied here. A copy would
# let the two drift and would test bytes nobody audited.
_ANCHOR_NS = Path(__file__).resolve().parent.parent / "static_storage_anchor_guard_2026_09_12"
if str(_ANCHOR_NS) not in sys.path:
    sys.path.insert(0, str(_ANCHOR_NS))

from archive_anchor_guard import (AnchorValidationError, load_anchor,
                                  verify_plan_against_anchor)
from storage_adapter_preflight_v6 import (PreflightError, preflight,
                                          SYMLINK_FLAG_AVAILABLE, NONBLOCK_FLAG_AVAILABLE)

CONTRACT_BYTES = b"# frozen measurement contract\n"
CONTRACT = hashlib.sha256(CONTRACT_BYTES).hexdigest()
ANCHOR_CSV = b"question_id,N_archive\na1,10\n"
ANCHOR_SHA = hashlib.sha256(ANCHOR_CSV).hexdigest()


def h(r):
    return hashlib.sha256(r).hexdigest()


def dump(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def repo_root():
    """Find the repository without hardcoding anyone's home directory.

    The anchor guard's own test pinned /home/user/llmzip, so it could only ever have run
    on its author's machine. Discovery, then an explicit skip.
    """
    env = os.environ.get("LLMZIP_REPO")
    if env and (Path(env) / ".git").exists():
        return Path(env)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
    return None


def scenario(root, n_i=10, probe_n=None, extra_pop=None):
    """A one-archive plan plus its companion records and artifacts."""
    root = Path(root)
    probe_n = n_i if probe_n is None else probe_n
    fx = {"schema": "V52_SYNTHETIC_FIXTURE_BUNDLE_V3",
          "transform": {"input_utf8": "hello"},
          "id_mapping": {"rows": [{"logical_id": "a", "offset": 0, "payload_utf8": "A"},
                                  {"logical_id": "b", "offset": 1, "payload_utf8": "B"}]},
          "corruption": {"strategy": "XOR_SINGLE_BYTE", "byte_offset": 0, "xor_mask": 1}}
    fr = dump(fx)
    (root / "fx.json").write_bytes(fr)
    (root / "phys.bin").write_bytes(b"PHYS")
    (root / "contract.md").write_bytes(CONTRACT_BYTES)
    (root / "anchor.csv").write_bytes(ANCHOR_CSV)

    pops = [{"id": "po_b", "archive_id": "a1", "probe_id": "pr1", "phase": "BEFORE", "count": probe_n},
            {"id": "po_a", "archive_id": "a1", "probe_id": "pr1", "phase": "AFTER", "count": probe_n + 1}]
    pop_ids = ["po_b", "po_a"]
    if extra_pop:
        pops.append(extra_pop[0])
        pop_ids.append(extra_pop[0]["id"])
    plan = {"schema": "v52.static-storage-plan", "version": 1, "contract_sha256": CONTRACT,
            "archives": [{"id": "a1", "N_i": n_i}],
            "probes": ([{"id": "pr1", "archive_id": "a1", "N": probe_n, "q": 1, "fixture_id": "fx1"}]
                       + (extra_pop[1] if extra_pop else [])),
            "populations": pops,
            "fixtures": [{"id": "fx1", "sha256": h(fr)}],
            "physical_copies": [{"id": "pc1", "artifact_sha256": h(b"PHYS"), "population_ids": pop_ids}]}
    fb = {"schema": "v52.fixture-bindings", "version": 3,
          "fixtures": [{"fixture_id": "fx1", "relative_path": "fx.json", "byte_length": len(fr),
                        "sha256": h(fr), "content_schema": "V52_SYNTHETIC_FIXTURE_BUNDLE_V3",
                        "consumer_sections": {"TRANSFORM": "transform", "ID_MAPPING": "id_mapping",
                                              "CORRUPT": "corruption"}}]}
    pb = {"schema": "v52.physical-copy-bindings", "version": 4,
          "physical_copies": [{"physical_copy_id": "pc1", "physical_locator": "phys.bin",
                               "source_raw_byte_length": 4, "artifact_sha256": h(b"PHYS"),
                               "sharing_denominator_rule": "POPULATION_COUNT",
                               "absence_basis": None}]}

    def w(name, obj):
        raw = dump(obj)
        (root / name).write_bytes(raw)
        return h(raw)

    return plan, (w("plan.json", plan), w("fb.json", fb), w("pb.json", pb))


def run(root, plan, hs, anchored):
    root = Path(root)
    return preflight(root / "plan.json", hs[0], root / "contract.md", CONTRACT,
                     root / "fb.json", hs[1], root / "pb.json", hs[2],
                     hs[0], CONTRACT, anchored)


class IntegrationTests(unittest.TestCase):

    def test_the_two_guards_now_work_together(self):
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td)
            anchor = load_anchor(ANCHOR_CSV, ANCHOR_SHA, "anchor.csv", "question_id", "N_archive")
            _, _, _, anchored = verify_plan_against_anchor(plan, anchor)
            out = run(td, plan, hs, anchored)
            self.assertEqual(out.physical_copies[0].denominator, ("po_b", 10))

    def test_preflight_cannot_be_called_without_the_anchor_result(self):
        """V5 documented that the anchor guard must run and enforced nothing."""
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td)
            root = Path(td)
            with self.assertRaises(TypeError):
                preflight(root / "plan.json", hs[0], root / "contract.md", CONTRACT,
                          root / "fb.json", hs[1], root / "pb.json", hs[2], hs[0], CONTRACT)

    def test_the_original_dilution_is_refused_end_to_end(self):
        """Inflate the archive size: the anchor guard refuses before preflight runs."""
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td, n_i=10 ** 9, probe_n=10 ** 9)
            anchor = load_anchor(ANCHOR_CSV, ANCHOR_SHA, "anchor.csv", "question_id", "N_archive")
            with self.assertRaises(AnchorValidationError) as cm:
                verify_plan_against_anchor(plan, anchor)
            self.assertIn("disagrees with the frozen anchor", str(cm.exception))

    def test_a_forged_anchor_mapping_is_refused_by_the_preflight(self):
        """A caller that fabricates the mapping instead of deriving it."""
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td)
            for forged, fragment in ((("po_b", 10 ** 9), "disagrees with the plan"),
                                     (("po_ghost", 10), "not bound to this copy"),
                                     (("po_b", 0), "integer in [1")):
                with self.assertRaises(PreflightError) as cm:
                    run(td, plan, hs, {"pc1": forged})
                self.assertIn(fragment, str(cm.exception))

    def test_missing_copy_in_the_mapping_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td)
            with self.assertRaises(PreflightError) as cm:
                run(td, plan, hs, {})
            self.assertIn("anchored denominator coverage", str(cm.exception))

    def test_diagnostic_population_cannot_become_the_denominator(self):
        """A staircase probe at 10^9 bound to the same copy is ignored, not chosen."""
        extra = ({"id": "po_x", "archive_id": "a1", "probe_id": "pr_x", "phase": "BEFORE",
                  "count": 10 ** 9},
                 [{"id": "pr_x", "archive_id": "a1", "N": 10 ** 9, "q": 1, "fixture_id": "fx1"}])
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td, extra_pop=extra)
            anchor = load_anchor(ANCHOR_CSV, ANCHOR_SHA, "anchor.csv", "question_id", "N_archive")
            _, roles, _, anchored = verify_plan_against_anchor(plan, anchor)
            self.assertEqual(roles["pr_x"], "DIAGNOSTIC")
            out = run(td, plan, hs, anchored)
            self.assertEqual(out.physical_copies[0].denominator, ("po_b", 10))

    # --- the Windows findings ------------------------------------------------------
    def test_open_flags_are_platform_optional(self):
        """V5 used os.O_NOFOLLOW bare; on Windows that is an AttributeError."""
        import storage_adapter_preflight_v6 as m
        src = Path(m.__file__).read_text()
        self.assertNotIn("os.O_NOFOLLOW", src.split("# Platform-optional", 1)[1].split("\n\n", 1)[1])
        self.assertIsInstance(SYMLINK_FLAG_AVAILABLE, bool)
        self.assertIsInstance(NONBLOCK_FLAG_AVAILABLE, bool)

    def test_fifo_refusal_does_not_depend_on_the_flags(self):
        """S_ISREG is what refuses a FIFO, and it is platform-independent."""
        if not hasattr(os, "mkfifo"):
            self.skipTest("platform has no mkfifo")
        with tempfile.TemporaryDirectory() as td:
            plan, hs = scenario(td)
            os.mkfifo(Path(td, "pipe"))
            pb = json.loads(Path(td, "pb.json").read_text())
            pb["physical_copies"][0]["physical_locator"] = "pipe"
            raw = dump(pb)
            Path(td, "pb.json").write_bytes(raw)
            anchor = load_anchor(ANCHOR_CSV, ANCHOR_SHA, "anchor.csv", "question_id", "N_archive")
            _, _, _, anchored = verify_plan_against_anchor(plan, anchor)
            with self.assertRaises(PreflightError) as cm:
                run(td, plan, (hs[0], hs[1], h(raw)), anchored)
            self.assertIn("regular file", str(cm.exception))

    def test_real_anchor_table_without_a_hardcoded_path(self):
        """The anchor guard's own test pinned /home/user/llmzip and could not travel."""
        root = repo_root()
        if root is None:
            self.skipTest("repository not found; set LLMZIP_REPO to run this case")
        try:
            raw = subprocess.run(
                ["git", "-C", str(root), "show",
                 "origin/main:docs/v52/task4c2/V52_T4C2_feature_geometry.csv"],
                capture_output=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError) as e:
            self.skipTest(f"git unavailable or ref missing: {e.__class__.__name__}")
        a = load_anchor(raw, h(raw), "V52_T4C2_feature_geometry.csv", "question_id", "N_archive")
        self.assertEqual(len(a.as_map()), 470)


if __name__ == "__main__":
    print(f"platform={sys.platform} python={sys.version.split()[0]} "
          f"O_NOFOLLOW={SYMLINK_FLAG_AVAILABLE} O_NONBLOCK={NONBLOCK_FLAG_AVAILABLE}")
    unittest.main()
