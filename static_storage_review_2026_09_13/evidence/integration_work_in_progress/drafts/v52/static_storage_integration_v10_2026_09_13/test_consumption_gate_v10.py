"""V10 hardened consumption-gate tests, incl. deterministic concurrency repro.

Selection: ``V52_LOADER_UNDER_TEST`` chooses the loader under strict test
(``v10`` default, ``v9`` to demonstrate the frozen defect). The V9
documentation test always targets frozen V9 and passes while V9 is vulnerable.

All concurrency is rendezvous-driven (threading.Event/Barrier); numeric
timeouts are hang guards only, never ordering assumptions.
"""
import builtins
import hashlib
import inspect
import os
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_V9_DIR = _HERE.parent / "static_storage_integration_v9_2026_09_13"
sys.path.insert(0, str(_V9_DIR))
sys.path.insert(0, str(_HERE))

import consumption_gate_v9 as v9
import consumption_gate_v10 as v10

LOADER_NAME = os.environ.get("V52_LOADER_UNDER_TEST", "v10")
if LOADER_NAME == "v9":
    G = v9
    PREFLIGHT = v9.preflight_longmemeval_v9
    CONTEXT = v9.V9Context
    VErr = v9.V9ValidationError
    PREFIX = "_v52_v9_"
    LOAD_CHAIN = v9._load_v8_exact
    EXEC_FN = v9._exec_exact
else:
    G = v10
    PREFLIGHT = v10.preflight_longmemeval_v10
    CONTEXT = v10.V10Context
    VErr = v10.V10ValidationError
    PREFIX = "_v52_v10_"
    LOAD_CHAIN = v10.load_pinned_v8_chain
    EXEC_FN = v10._exec_private

REAL_EXEC = builtins.exec
GUARD_TIMEOUT = 60

CASES = [
    ("malformed plan sha", "ZZZ", "1" * 64, "2" * 64),
    ("uppercase plan sha", "A" * 64, "1" * 64, "2" * 64),
    ("short fixture sha", "1" * 64, "abc", "2" * 64),
    ("nonhex physical sha", "1" * 64, "2" * 64, "g" * 64),
    ("missing plan file", "1" * 64, "2" * 64, "3" * 64),
    ("plan sha mismatch", "4" * 64, "2" * 64, "3" * 64),
    ("fixture sha mismatch", "1" * 64, "5" * 64, "3" * 64),
    ("physical sha mismatch", "1" * 64, "2" * 64, "6" * 64),
    ("empty plan path", "1" * 64, "2" * 64, "3" * 64),
    ("missing fixture path", "1" * 64, "2" * 64, "3" * 64),
    ("missing physical path", "1" * 64, "2" * 64, "3" * 64),
    ("all zero hashes", "0" * 64, "0" * 64, "0" * 64),
]


def case_paths(label, tmpdir):
    if label == "empty plan path":
        return ("", str(Path(tmpdir) / "f"), str(Path(tmpdir) / "b"))
    if label == "missing fixture path":
        return (str(Path(tmpdir) / "p"), str(Path(tmpdir) / "no-fix"), str(Path(tmpdir) / "b"))
    if label == "missing physical path":
        return (str(Path(tmpdir) / "p"), str(Path(tmpdir) / "f"), str(Path(tmpdir) / "no-phys"))
    return (str(Path(tmpdir) / "no-plan"), str(Path(tmpdir) / "no-fix"), str(Path(tmpdir) / "no-phys"))


class Poison:
    """Permissive fake ``v8_runtime``: every check passes; canned chain feeds
    the real snapshot freezer, so invalid inputs yield a snapshot (bypass)."""

    class V8ValidationError(ValueError):
        pass

    class _Plan:
        def __init__(self):
            self.sha256 = "1" * 64
            self.contract_sha256 = "0" * 64
            self.data = {}

    class _Guard:
        Plan = None

        @staticmethod
        def load_plan(*a):
            return Poison._Plan()

    class _V7:
        @staticmethod
        def load_longmemeval_anchor():
            return object()

        @staticmethod
        def _verify_plan_data_against_anchor(data, anchor):
            ns = types.SimpleNamespace(
                anchor_sha256="a" * 64, source_identity="x",
                archive_ids=("a",), authoritative_probe_ids=(("a", "q"),),
                denominators=(("c", "p", 10),))
            ns.denominator_map = lambda: {"c": ("p", 10)}
            return ns

    class _Row:
        physical_copy_id = "c"
        sha256 = hashlib.sha256(b"p").hexdigest()
        source_byte_length = 1
        denominator = ("p", 10)

        def reverify(self):
            return b"p"

    class _V6:
        @staticmethod
        def preflight(*a):
            return types.SimpleNamespace(fixtures=(), physical_copies=(Poison._Row(),))

    @staticmethod
    def _fake_exec(label, path, expected):
        return {"v7_semantic_gate": Poison._V7,
                "measurement_plan_guard": Poison._Guard,
                "storage_adapter_preflight_v6": Poison._V6}[label]


Poison._Guard.Plan = Poison._Plan


def make_poison_module():
    mod = types.ModuleType("v8_runtime")

    def _getattr(name):
        if name in ("need", "digest"):
            return lambda *a: None
        if name == "authenticate_fixed":
            return lambda *a: b""
        if name == "exec_pinned_module":
            return Poison._fake_exec
        return object()

    mod.__getattr__ = _getattr
    mod.V8ValidationError = Poison.V8ValidationError
    return mod


GATE_FILENAME = str(G._V8_GATE_PATH.resolve())
V9_GATE_FILENAME = str(v9._V8_GATE_PATH.resolve())


class ExecHook:
    """Wrap builtins.exec; rendezvous exactly on gate-module exec windows.

    The gate exec is identified by the loader namespace prefix plus the
    compiled filename (the pinned gate source path) -- no per-thread
    counting, so overlapping hook installations cannot split the count."""

    def __init__(self, prefix, gate_filename, on_gate_window):
        self.prefix = prefix
        self.gate_filename = gate_filename
        self.on_gate_window = on_gate_window

    def _hooked(self, code, g, loc=None):
        name = g.get("__name__", "") if isinstance(g, dict) else ""
        if (isinstance(name, str) and name.startswith(self.prefix)
                and getattr(code, "co_filename", None) == self.gate_filename):
            self.on_gate_window()
        if loc is None:
            return REAL_EXEC(code, g)
        return REAL_EXEC(code, g, loc)

    def __enter__(self):
        builtins.exec = lambda code, g, *rest: self._hooked(code, g, *rest)
        return self

    def __exit__(self, *a):
        builtins.exec = REAL_EXEC
        return False


def run_case_against(loader_preflight, label, tmpdir):
    p, f, b = case_paths(label, tmpdir)
    _, psha, fsha, bsha = next(c for c in CASES if c[0] == label)
    try:
        loader_preflight(p, psha, f, fsha, b, bsha)
        return "BYPASSED"
    except (v9.V9ValidationError, v10.V10ValidationError):
        return "rejected"


class ParityTests(unittest.TestCase):
    def test_context_exposes_no_snapshot_field(self):
        c = CONTEXT("p", "1" * 64, "f", "2" * 64, "b", "3" * 64)
        self.assertFalse(hasattr(c, "initial_snapshot"))
        self.assertEqual(c._fields, ("plan_path", "expected_plan_sha256", "fixture_bindings_path",
                                     "expected_fixture_bindings_sha256", "physical_bindings_path",
                                     "expected_physical_bindings_sha256"))

    def test_preflight_discards_validation_snapshot(self):
        old = G._fresh_v8
        calls = []
        marker = object()
        G._fresh_v8 = lambda *a: (calls.append(a) or marker)
        try:
            c = PREFLIGHT("p", "1" * 64, "f", "2" * 64, "b", "3" * 64)
            self.assertEqual(len(calls), 1)
            self.assertNotIn(marker, tuple(c))
        finally:
            G._fresh_v8 = old

    def test_fresh_snapshot_reruns_each_access(self):
        old = G._fresh_v8
        calls = []
        G._fresh_v8 = lambda *a: calls.append(a) or len(calls)
        try:
            c = CONTEXT("p", "1" * 64, "f", "2" * 64, "b", "3" * 64)
            self.assertEqual(c.fresh_snapshot(), 1)
            self.assertEqual(c.fresh_snapshot(), 2)
            self.assertEqual(len(calls), 2)
        finally:
            G._fresh_v8 = old

    def test_public_signature(self):
        self.assertEqual(
            tuple(inspect.signature(PREFLIGHT).parameters),
            ("plan_path", "expected_plan_sha256", "fixture_bindings_path",
             "expected_fixture_bindings_sha256", "physical_bindings_path",
             "expected_physical_bindings_sha256"))

    def test_private_binding_ignores_ambient_same_name(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "victim.py"
            p.write_text("import helper_dep\nRESULT = helper_dep.MARKER\n")
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            good = types.ModuleType("helper_dep")
            good.MARKER = "good"
            ambient = types.ModuleType("helper_dep")
            ambient.MARKER = "poison"
            sys.modules["helper_dep"] = ambient
            try:
                fresh = EXEC_FN("victim", p, h, (("helper_dep", good),))
                self.assertEqual(fresh.RESULT, "good")
                self.assertIs(sys.modules["helper_dep"], ambient)
            finally:
                sys.modules.pop("helper_dep", None)
            leftovers = [k for k in sys.modules if k.startswith(("_v52_v9_", "_v52_v10_"))]
            self.assertEqual(leftovers, [])


class RejectionTests(unittest.TestCase):
    def test_twelve_rejections_healthy(self):
        with tempfile.TemporaryDirectory() as td:
            for label, _, _, _ in CASES:
                self.assertEqual(run_case_against(PREFLIGHT, label, td), "rejected", label)

    def test_twelve_rejections_hold_under_concurrent_poison(self):
        """Core regression: a concurrent sys.modules publisher must not flip
        any rejection. Deterministic rendezvous on the gate exec window."""
        poison = make_poison_module()
        with tempfile.TemporaryDirectory() as td:
            for label, _, _, _ in CASES:
                in_window = threading.Event()
                release = threading.Event()

                def on_window():
                    in_window.set()
                    self.assertTrue(release.wait(timeout=GUARD_TIMEOUT), f"deadlock guard: {label}")

                def publisher():
                    self.assertTrue(in_window.wait(timeout=GUARD_TIMEOUT), f"deadlock guard: {label}")
                    sys.modules["v8_runtime"] = poison
                    release.set()

                with ExecHook(PREFIX, GATE_FILENAME, on_window):
                    t = threading.Thread(target=publisher, daemon=True)
                    t.start()
                    try:
                        outcome = run_case_against(PREFLIGHT, label, td)
                    finally:
                        t.join(timeout=GUARD_TIMEOUT)
                        if sys.modules.get("v8_runtime") is poison:
                            sys.modules.pop("v8_runtime", None)
                self.assertEqual(outcome, "rejected", f"{label}: bypassed on {LOADER_NAME}")
        self.assertNotIn("v8_runtime", [k for k in sys.modules if k == "v8_runtime" and sys.modules[k] is poison])


class ConcurrencyTests(unittest.TestCase):
    def test_two_concurrent_valid_chain_loads(self):
        """Two overlapping valid chain loads; one poison publication lands in
        both gate windows (two-phase barrier). Both gates must stay genuine."""
        poison = make_poison_module()
        # Per-worker gate-window rendezvous with one foreign publisher. No
        # worker-worker barrier: the repair serializes transactions by design.
        windows = {}
        win_lock = threading.Lock()
        results = {}

        def on_window():
            ident = threading.get_ident()
            with win_lock:
                pair = windows.get(ident)
            if pair is not None:
                entered, release = pair
                entered.set()
                self.assertTrue(release.wait(timeout=GUARD_TIMEOUT), "deadlock guard tripped")

        def worker(idx, slot):
            with win_lock:
                slot["ident"] = threading.get_ident()
                slot["entered"] = threading.Event()
                slot["release"] = threading.Event()
                windows[slot["ident"]] = (slot["entered"], slot["release"])
                slot["registered"].set()
            gate = LOAD_CHAIN()
            results[idx] = gate

        def publisher(slots):
            for slot in slots:
                self.assertTrue(slot["registered"].wait(timeout=GUARD_TIMEOUT),
                                "deadlock guard tripped")
                with win_lock:
                    entered, release = windows[slot["ident"]]
                self.assertTrue(entered.wait(timeout=GUARD_TIMEOUT), "deadlock guard tripped")
                sys.modules["v8_runtime"] = poison
                release.set()

        slots = [{"registered": threading.Event()} for _ in range(2)]
        threads = [threading.Thread(target=worker, args=(i, slots[i]), daemon=True) for i in (0, 1)]
        pub = threading.Thread(target=publisher, args=(slots,), daemon=True)
        with ExecHook(PREFIX, GATE_FILENAME, on_window):
            for t in (*threads, pub):
                t.start()
            for t in (*threads, pub):
                t.join(timeout=GUARD_TIMEOUT)
                self.assertFalse(t.is_alive(), "deadlock guard tripped")
        self.assertEqual(sorted(results), [0, 1])
        if sys.modules.get("v8_runtime") is poison:
            sys.modules.pop("v8_runtime", None)
        with tempfile.TemporaryDirectory() as td:
            for idx, gate in results.items():
                with self.assertRaises(Exception, msg=f"worker {idx}: gate not genuine"):
                    gate._fresh_preflight(str(Path(td) / "no-plan"), "1" * 64,
                                          str(Path(td) / "f"), "2" * 64,
                                          str(Path(td) / "b"), "3" * 64)
        self.assertEqual([k for k in sys.modules if k.startswith(("_v52_v9_", "_v52_v10_"))], [])

    def test_concurrent_poisoned_ambient_module(self):
        """Static ambient poison (as V8 test setup leaves) must be preserved
        untouched and must not leak into the loaded chain."""
        ambient_rt = types.ModuleType("v8_runtime")
        ambient_rt.MARKER = "ambient"
        ambient_snap = types.ModuleType("v8_snapshot")
        sys.modules["v8_runtime"] = ambient_rt
        sys.modules["v8_snapshot"] = ambient_snap
        try:
            gate = LOAD_CHAIN()
            self.assertIs(sys.modules["v8_runtime"], ambient_rt)
            self.assertIs(sys.modules["v8_snapshot"], ambient_snap)
            self.assertIsNot(gate.rt, ambient_rt)
            with tempfile.TemporaryDirectory() as td:
                with self.assertRaises(Exception):
                    gate._fresh_preflight(str(Path(td) / "no-plan"), "1" * 64,
                                          str(Path(td) / "f"), "2" * 64,
                                          str(Path(td) / "b"), "3" * 64)
        finally:
            sys.modules.pop("v8_runtime", None)
            sys.modules.pop("v8_snapshot", None)

    def test_exception_restoration_under_concurrency(self):
        """A failing transaction overlapping a valid load: error type kept,
        namespace exactly restored."""
        ambient = types.ModuleType("v8_runtime")
        ambient.MARKER = "keep"
        sys.modules["v8_runtime"] = ambient
        # Deterministic overlap without lock inversion: B signals it is inside
        # its transaction attempt BEFORE it can block on the chain lock, and
        # the failing transaction waits for that signal while holding its own
        # gate window open. B therefore provably overlaps A's transaction.
        b_started = threading.Event()
        outcome, errors = {}, []

        def on_window():
            self.assertTrue(b_started.wait(timeout=GUARD_TIMEOUT), "deadlock guard tripped")

        def failing():
            with tempfile.TemporaryDirectory() as td:
                try:
                    PREFLIGHT(str(Path(td) / "no-plan"), "1" * 64,
                              str(Path(td) / "f"), "2" * 64,
                              str(Path(td) / "b"), "3" * 64)
                    outcome["a"] = "BYPASSED"
                except VErr:
                    outcome["a"] = "rejected"

        def valid():
            b_started.set()
            try:
                outcome["b"] = LOAD_CHAIN()
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        ta = threading.Thread(target=failing, daemon=True)
        tb = threading.Thread(target=valid, daemon=True)
        with ExecHook(PREFIX, GATE_FILENAME, on_window):
            ta.start()
            tb.start()
            ta.join(timeout=GUARD_TIMEOUT)
            tb.join(timeout=GUARD_TIMEOUT)
        self.assertFalse(ta.is_alive() or tb.is_alive(), "deadlock guard tripped")
        self.assertEqual(outcome.get("a"), "rejected")
        self.assertEqual(errors, [])
        self.assertIsInstance(outcome.get("b"), types.ModuleType)
        self.assertIs(sys.modules.get("v8_runtime"), ambient)
        self.assertEqual([k for k in sys.modules if k.startswith(("_v52_v9_", "_v52_v10_"))], [])
        sys.modules.pop("v8_runtime", None)

    def test_repeated_fresh_snapshot_reruns_chain(self):
        gate_windows = []

        def on_window():
            gate_windows.append(1)

        with tempfile.TemporaryDirectory() as td:
            ctx = CONTEXT(str(Path(td) / "no-plan"), "1" * 64,
                          str(Path(td) / "f"), "2" * 64,
                          str(Path(td) / "b"), "3" * 64)
            with ExecHook(PREFIX, GATE_FILENAME, on_window):
                for _ in range(3):
                    with self.assertRaises(VErr):
                        ctx.fresh_snapshot()
        self.assertEqual(len(gate_windows), 3)
        self.assertFalse(hasattr(ctx, "initial_snapshot"))

    def test_sysmodules_exactly_restored(self):
        LOAD_CHAIN()
        with tempfile.TemporaryDirectory() as td:
            try:
                PREFLIGHT(str(Path(td) / "no-plan"), "1" * 64,
                          str(Path(td) / "f"), "2" * 64,
                          str(Path(td) / "b"), "3" * 64)
            except VErr:
                pass
        before = dict(sys.modules)
        LOAD_CHAIN()
        with tempfile.TemporaryDirectory() as td:
            try:
                PREFLIGHT(str(Path(td) / "no-plan"), "1" * 64,
                          str(Path(td) / "f"), "2" * 64,
                          str(Path(td) / "b"), "3" * 64)
            except VErr:
                pass
        self.assertEqual(set(sys.modules), set(before))
        for k, mod in before.items():
            self.assertIs(sys.modules[k], mod, k)


class V9DefectDocumentation(unittest.TestCase):
    def test_v9_binds_concurrent_poison_silently(self):
        """Exact reproduction against frozen V9: deterministic poison
        publication in the gate window flips a rejection into acceptance."""
        poison = make_poison_module()
        in_window = threading.Event()
        release = threading.Event()

        def on_window():
            in_window.set()
            self.assertTrue(release.wait(timeout=GUARD_TIMEOUT))

        def publisher():
            self.assertTrue(in_window.wait(timeout=GUARD_TIMEOUT))
            sys.modules["v8_runtime"] = poison
            release.set()

        with tempfile.TemporaryDirectory() as td:
            with ExecHook("_v52_v9_", V9_GATE_FILENAME, on_window):
                t = threading.Thread(target=publisher, daemon=True)
                t.start()
                try:
                    outcome = run_case_against(v9.preflight_longmemeval_v9, "missing plan file", td)
                finally:
                    t.join(timeout=GUARD_TIMEOUT)
        self.assertEqual(outcome, "BYPASSED")


if __name__ == "__main__":
    unittest.main()

