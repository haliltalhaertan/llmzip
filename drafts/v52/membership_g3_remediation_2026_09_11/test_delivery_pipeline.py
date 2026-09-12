"""Synthetic unittest regressions for audit 5126766, gaps 1-7,9/F1,F2,F4,F5,F7.

Run from the delivery checkout, with PYTHONHASHSEED=0 and
OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1:
  ../.venvs/g3-lock-20260912/Scripts/python.exe -B -m unittest discover \
      -s drafts/v52/membership_g3_remediation_2026_09_11 \
      -p test_delivery_pipeline.py -v

Only the pinned historical Python SOURCE is read from Git. Only its extracted
topks_by_hamming function is compiled; the historical module is never executed.
No ingestion, corpus, outcomes, experiment, certificate, seal or writer is run.
Selection order is a historical arithmetic contract; fractional recall consumes
sets, and does not interpret that order as a rank. The LME connector ordinal
contract is sorted question identifiers, as directed by the lead (L082).
"""
from __future__ import annotations

import ast
from collections import Counter
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import itertools
import os
from pathlib import Path
import subprocess
import sys
import traceback
import unittest
from unittest import mock

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
THREAD_VARIABLES = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
PINNED_SOURCE = (
    "692f599eedeb7e7a649443f24ff507e8c4d1c17d:"
    "research/v52/locomo_sign_mechanism_replication.py"
)
PINNED_SHA256 = "a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b"
ARMS = (
    "NATIVE", "SCALED_NATIVE", "B32_FRESH", "SCALED_B32",
    "RANDOM32_FRESH", "SCALED_RANDOM32",
)
ROTATION_SEEDS = tuple(range(60001, 60011))
PARTITION_SEEDS = tuple(range(70001, 70011))

# Load this sibling explicitly, avoiding same-name modules in another checkout.
_spec = importlib.util.spec_from_file_location("delivery_pipeline_under_test", HERE / "pipeline_g3.py")
pipe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pipe)


def setUpModule():
    expected = ROOT.parent / ".venvs/g3-lock-20260912/Scripts/python.exe"
    if Path(sys.executable).resolve() != expected.resolve():
        raise RuntimeError("Use the exact g3-lock-20260912 interpreter")
    if not sys.dont_write_bytecode:
        raise RuntimeError("The synthetic delivery suite requires -B")
    if any(os.environ.get(name) != "1" for name in THREAD_VARIABLES):
        raise RuntimeError("All four numerical thread variables must be 1")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("PYTHONHASHSEED must be 0")


def independent_priorities(ordinal, rows):
    """Do not call either production seed or production priority helper."""
    return np.stack([
        np.random.default_rng(5_100_000 + ordinal * 100_000 + trial * 100 + 99).random(rows)
        for trial in range(20)
    ])


def semantic_picks(distances, priorities, k=3):
    return [np.lexsort((p, distances))[:k] for p in priorities]


class SyntheticRep:
    def __init__(self, texts=None):
        rows = 100 if texts is None else len(texts)
        rng = np.random.default_rng(91817)
        self.C = rng.normal(size=(rows, 96))
        self.D = np.diag(np.linspace(0.4, 1.9, 96))
        self.Q = rng.normal(size=(1, 96))
        self.diagnostics = {"synthetic": 1}

    def queries(self, texts):
        return np.repeat(self.Q, len(texts), axis=0)


def anchor_for(rep, ordinal, gold):
    d = np.count_nonzero((rep.C >= 0) != (rep.Q[0] >= 0), axis=1)
    picks = semantic_picks(d, independent_priorities(ordinal, len(rep.C)))
    return float(np.mean([len(set(p) & set(gold)) / len(gold) for p in picks]))


def score(rep=None, ordinal=3, anchor=None):
    rep = SyntheticRep() if rep is None else rep
    gold = [0, 1, 2, 3, 4]
    anchor = [anchor_for(rep, ordinal, gold)] if anchor is None else anchor
    return pipe.score_archive(rep, ["synthetic query"], [gold], ["synthetic-q0"], ordinal, anchor)


def schema(benchmark):
    units = [{"text": "synthetic memory"} for _ in range(100)]
    question = {"text": "synthetic query", "gold_rows": [0, 1, 2, 3, 4]}
    result = {"benchmark": benchmark, "cohort_ids": ["q0"], "questions_with_empty_gold": []}
    if benchmark == "LoCoMo":
        result["conversations"] = {"c0": {"index": 7, "units": units, "questions": {"q0": question}}}
    else:
        result["questions"] = {"q0": dict(question, units=units)}
    return result


# The hook is dormant except inside a checked in-memory call. It records and
# blocks write-capable opens and filesystem mutations BEFORE any file is changed.
_active_writes = None


def _write_audit(event, args):
    if _active_writes is None:
        return
    write = False
    if event == "open":
        _, mode, flags = args
        write = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int) and bool(flags & (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            ))
        )
    elif event in {
        "os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.link",
        "os.symlink", "os.truncate", "os.chmod", "os.utime",
    }:
        write = True
    if write:
        _active_writes.append((event, repr(args)))
        raise AssertionError("unexpected filesystem write during in-memory pipeline call")


sys.addaudithook(_write_audit)


@contextmanager
def captured_surfaces():
    global _active_writes
    stdout, stderr, writes, fd_output = io.StringIO(), io.StringIO(), [], []
    previous = _active_writes
    _active_writes = writes

    def fd_write(fd, data):
        fd_output.append((fd, bytes(data)))
        if fd not in (1, 2):
            writes.append(("os.write", fd, bytes(data)))
        return len(data)

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr), mock.patch.object(os, "write", fd_write):
            yield stdout, stderr, writes, fd_output
    finally:
        _active_writes = previous


def exception_surfaces(exc):
    """Traverse even suppressed context and both branches of the chain graph."""
    pending, seen, surfaces = [exc], set(), []
    while pending:
        item = pending.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        surfaces.extend((str(item), repr(item), "".join(traceback.format_exception(item))))
        pending.extend(x for x in (item.__cause__, item.__context__) if x is not None)
    return surfaces


def leaking_exception(payload):
    """Attach both a cause and a different context, to defeat from-None masking."""
    try:
        raise LookupError(payload + "-context")
    except LookupError:
        raise RuntimeError(payload) from ValueError(payload + "-cause")


class DeliveryPipelineTests(unittest.TestCase):
    def setUp(self):
        # The lead owns the separately tested certificate. These regressions
        # isolate delivery behavior; identity/norm/dot controls remain real.
        patcher = mock.patch.object(pipe, "coordinatewise_signed_certificate", return_value=None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def assert_refused(self, action, code=None, canaries=()):
        with captured_surfaces() as captured:
            try:
                action()
            except Exception as exc:
                error = exc
            else:
                error = None
        stdout, stderr, writes, fd_output = captured
        self.assertEqual(writes, [], "in-memory call attempted a filesystem write")
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(fd_output, [])
        self.assertIsNotNone(error, "invalid input was silently accepted")
        surfaces = exception_surfaces(error)
        for canary in canaries:
            for surface in surfaces + [stdout.getvalue(), stderr.getvalue(), repr(writes), repr(fd_output)]:
                self.assertNotIn(canary, surface)
        self.assertIsInstance(error, pipe.PipelineError)
        self.assertRegex(str(error), r"^E-M-\d{3}: ")
        if code is not None:
            self.assertTrue(str(error).startswith(code + ":"), str(error))
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        return error

    def assert_schema_refused(self, data, anchors=None, code=None, canaries=()):
        with mock.patch.object(pipe, "Representation", side_effect=AssertionError("fitting reached before schema refusal")) as fit:
            self.assert_refused(lambda: pipe.assemble_in_memory(data, {"q0": 0.0} if anchors is None else anchors), code, canaries)
            fit.assert_not_called()

    def test_gap_01_every_topks_call_reuses_identical_immutable_priorities(self):
        rep, ordinal = SyntheticRep(), 3
        expected = independent_priorities(ordinal, len(rep.C))
        anchor = anchor_for(rep, ordinal, [0, 1, 2, 3, 4])
        original_rng, original_topks = np.random.default_rng, pipe.topks_by_hamming
        rng_calls, priority_calls = [], []

        def rng_spy(seed=None):
            rng_calls.append(seed)
            return original_rng(seed)

        def topks_spy(dist, priorities, k=3):
            # Keep actual references, preventing id reuse from disguising redraws.
            before = priorities.tobytes()
            np.testing.assert_array_equal(priorities, expected)
            self.assertEqual(before, expected.tobytes())
            result = original_topks(dist, priorities, k)
            self.assertEqual(priorities.tobytes(), before)
            priority_calls.append((priorities, before))
            return result

        with mock.patch.object(np.random, "default_rng", side_effect=rng_spy), mock.patch.object(pipe, "topks_by_hamming", side_effect=topks_spy):
            records, _ = score(rep, ordinal, [anchor])
        self.assertEqual(len(records), 60)
        self.assertEqual(len(priority_calls), 60)
        first = priority_calls[0][0]
        for priorities, original_bytes in priority_calls:
            self.assertIs(priorities, first)
            self.assertEqual(priorities.tobytes(), original_bytes)
        nuisance_seeds = [5_100_000 + ordinal * 100_000 + t * 100 + 99 for t in range(20)]
        self.assertEqual(rng_calls[:20], nuisance_seeds)
        self.assertEqual([s for s in rng_calls if s not in ROTATION_SEEDS + PARTITION_SEEDS], nuisance_seeds)
        self.assertEqual(Counter(rng_calls), Counter(nuisance_seeds + list(ROTATION_SEEDS) * 2 + list(PARTITION_SEEDS)))

    def test_gap_01_observer_rejects_per_arm_priority_row_reversal_mutation(self):
        # First establish that the exact existing observer accepts production.
        self.test_gap_01_every_topks_call_reuses_identical_immutable_priorities()
        original = pipe.score_archive
        tree = ast.parse((HERE / "pipeline_g3.py").read_bytes())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "score_archive"]
        self.assertEqual(len(functions), 1)
        function = deepcopy(functions[0])
        selectors = [node for node in ast.walk(function) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name) and node.func.id == "topks_by_hamming"]
        self.assertEqual(len(selectors), 1)
        selector = selectors[0]
        self.assertEqual(len(selector.args), 2)
        self.assertIsInstance(selector.args[1], ast.Name)
        self.assertEqual(selector.args[1].id, "P")
        # Mutate the CALLER, leaving the observer and topks implementation intact.
        # Reordering nuisance rows preserves mean recall, so score-only checks
        # would miss this per-arm violation of the common-priority contract.
        selector.args[1] = ast.parse(
            "P[::-1] if arm == 'SCALED_NATIVE' else P", mode="eval"
        ).body
        namespace = dict(original.__globals__)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                     "<delivery-gap-01-mutant>", "exec"), namespace)
        compiled = namespace["score_archive"]
        # Use LIVE production globals: a copied namespace would bypass the
        # existing test's temporary topks observer and make this probe vacuous.
        mutant = type(original)(compiled.__code__, original.__globals__,
                                original.__name__, original.__defaults__)
        with mock.patch.object(pipe, "score_archive", mutant):
            try:
                self.test_gap_01_every_topks_call_reuses_identical_immutable_priorities()
            except AssertionError as error:
                frames = []
                tb = error.__traceback__
                while tb is not None:
                    frames.append(tb.tb_frame)
                    tb = tb.tb_next
                observers = [f for f in frames if f.f_code.co_name == "topks_spy"]
                self.assertEqual(len(observers), 1, "failure must come from the existing priority observer")
                observed = observers[0].f_locals
                # The native call succeeded; the observer then saw and rejected
                # the reversed matrix on the first scaled-native call itself.
                self.assertEqual(len(observed["priority_calls"]), 1)
                np.testing.assert_array_equal(observed["priorities"], observed["expected"][::-1])
                self.assertFalse(np.array_equal(observed["priorities"], observed["expected"]))
                callers = [f for f in frames if f.f_code is mutant.__code__]
                self.assertEqual(len(callers), 1)
                caller = callers[0].f_locals
                self.assertEqual((caller["seed"], caller["arm"]), (60001, "SCALED_NATIVE"))
                self.assertIs(observed["priority_calls"][0][0], caller["P"])
                self.assertIsNot(observed["priorities"], caller["P"])
                self.assertTrue(np.shares_memory(observed["priorities"], caller["P"]))
            else:
                self.fail("existing gap-1 observer accepted per-arm priority divergence")
        self.assertIs(pipe.score_archive, original)

    def test_gap_01_nuisance_stream_independent_formula_all_twenty_trials(self):
        for ordinal, rows in ((0, 1), (1, 11), (3, 100), (17, 23)):
            with self.subTest(ordinal=ordinal, rows=rows):
                expected = independent_priorities(ordinal, rows)
                for trial in range(20):
                    self.assertEqual(pipe.stable_archive_seed(ordinal, trial), 5_100_000 + ordinal * 100_000 + trial * 100)
                actual = pipe._nuisance_priorities(ordinal, rows)
                self.assertEqual(actual.shape, (20, rows))
                self.assertEqual(actual.tobytes(), expected.tobytes())
                self.assertEqual(pipe._nuisance_priorities(ordinal, rows).tobytes(), expected.tobytes())

    def test_F4_matched_blocks_independent_redraw_and_shared_build_inputs(self):
        original_draw = pipe.core.draw_rotation_blocks
        original_check = pipe.core.assert_matched_blocks
        original_build = pipe.core.build_rotation
        draws, checks, builds = [], [], []

        def draw(seed):
            blocks = original_draw(seed)
            draws.append((seed, blocks))
            return blocks

        def check(a, b, ac, bc):
            self.assertIsNot(a, ac)
            self.assertIsNot(b, bc)
            self.assertFalse(np.shares_memory(a, ac))
            self.assertFalse(np.shares_memory(b, bc))
            np.testing.assert_array_equal(a, ac)
            np.testing.assert_array_equal(b, bc)
            checks.append((a, b, ac, bc))
            return original_check(a, b, ac, bc)

        def build(a, b, members):
            builds.append((a, b, members.copy()))
            return original_build(a, b, members)

        with mock.patch.object(pipe.core, "draw_rotation_blocks", side_effect=draw), mock.patch.object(pipe.core, "assert_matched_blocks", side_effect=check), mock.patch.object(pipe.core, "build_rotation", side_effect=build):
            score()
        self.assertEqual([seed for seed, _ in draws], [s for s in ROTATION_SEEDS for _ in range(2)])
        self.assertEqual(len(checks), 30)  # redraw plus two actual-embedding checks per seed
        self.assertEqual(len(builds), 20)
        for i, (_, blocks) in enumerate(draws[::2]):
            for built in builds[2 * i:2 * i + 2]:
                self.assertIs(built[0], blocks[0])
                self.assertIs(built[1], blocks[1])
            np.testing.assert_array_equal(builds[2 * i][2], np.arange(32))
            expected_members = np.random.default_rng(PARTITION_SEEDS[i]).permutation(96)[:32]
            np.testing.assert_array_equal(builds[2 * i + 1][2], expected_members)

    def test_F4_upstream_second_redraw_mutation_must_abort_each_block(self):
        for block_index in (0, 1):
            with self.subTest(block=block_index):
                original = pipe.core.draw_rotation_blocks
                calls = []

                def mutated_draw(seed):
                    pair = list(original(seed))
                    calls.append(seed)
                    if len(calls) == 2:
                        pair[block_index] = pair[block_index].copy()
                        # Still orthogonal: failure must be the matched-Q control.
                        pair[block_index][:, 0] *= -1
                    return tuple(pair)

                with mock.patch.object(pipe.core, "draw_rotation_blocks", side_effect=mutated_draw), mock.patch.object(pipe.core, "assert_matched_blocks", wraps=pipe.core.assert_matched_blocks) as check, mock.patch.object(pipe.core, "build_rotation", wraps=pipe.core.build_rotation) as build, mock.patch.object(pipe, "topks_by_hamming", wraps=pipe.topks_by_hamming) as topks:
                    with self.assertRaisesRegex(pipe.core.DesignViolation, "matched-Q control failed"):
                        score()
                    self.assertEqual(calls, [60001, 60001])
                    self.assertEqual(check.call_count, 1)
                    build.assert_not_called()
                    topks.assert_not_called()

    def test_F4_wrong_orthogonal_identity_embedding_refused_for_both_memberships(self):
        rep = SyntheticRep()
        identity = np.eye(96)
        # Identity passes both geometric invariants EXACTLY. They cannot detect
        # replacement of the intended random blocks by this wrong embedding.
        for X, Q in ((rep.C, rep.Q), (rep.C @ rep.D, rep.Q @ rep.D)):
            self.assertEqual(pipe.core.check_rotation_invariance(X, Q, identity), (0.0, 0.0))
        for replace_call in (1, 2):
            with self.subTest(membership="spectral" if replace_call == 1 else "random"):
                original, calls = pipe.core.build_rotation, []

                def wrong_embedding(a, b, membership):
                    intended = original(a, b, membership)
                    calls.append(membership.copy())
                    if len(calls) == replace_call:
                        self.assertFalse(np.array_equal(intended, identity))
                        return identity.copy()
                    return intended

                with mock.patch.object(pipe.core, "build_rotation", side_effect=wrong_embedding), mock.patch.object(pipe, "topks_by_hamming", wraps=pipe.topks_by_hamming) as topks:
                    self.assert_refused(lambda: score(rep), "E-M-044")
                    self.assertEqual(len(calls), 2)
                    topks.assert_not_called()

    def test_gap_02_F7_all_required_top_level_and_nested_keys_missing(self):
        common = [(key,) for key in ("benchmark", "cohort_ids", "questions_with_empty_gold")]
        paths = {
            "LoCoMo": common + [("conversations",), ("conversations", "c0", "index"),
                ("conversations", "c0", "units"), ("conversations", "c0", "units", 0, "text"),
                ("conversations", "c0", "questions"), ("conversations", "c0", "questions", "q0", "text"),
                ("conversations", "c0", "questions", "q0", "gold_rows")],
            "LongMemEval": common + [("questions",), ("questions", "q0", "text"),
                ("questions", "q0", "gold_rows"), ("questions", "q0", "units"),
                ("questions", "q0", "units", 0, "text")],
        }
        for benchmark, missing_paths in paths.items():
            for path in missing_paths:
                with self.subTest(benchmark=benchmark, missing=path):
                    data = schema(benchmark)
                    parent = data
                    for part in path[:-1]:
                        parent = parent[part]
                    del parent[path[-1]]
                    self.assert_schema_refused(data)

    def test_gap_02_F7_wrong_types_and_cohort_coverage(self):
        for value in (None, [], "schema", 0, True):
            with self.subTest(top_level=type(value).__name__):
                self.assert_schema_refused(value)
        mutations = [
            (("benchmark",), None), (("questions_with_empty_gold",), None),
            (("cohort_ids",), "q0"), (("cohort_ids",), [1]),
            (("cohort_ids",), ["q0", "q0"]),
        ]
        for benchmark in ("LoCoMo", "LongMemEval"):
            prefix = ("conversations", "c0") if benchmark == "LoCoMo" else ("questions", "q0")
            question = prefix + ("questions", "q0") if benchmark == "LoCoMo" else prefix
            cases = mutations + [(prefix, None), (prefix + ("units",), {}),
                (prefix + ("units", 0), None), (prefix + ("units", 0, "text"), 7),
                (question, None), (question + ("text",), []), (question + ("gold_rows",), "0")]
            if benchmark == "LoCoMo":
                cases += [(("conversations",), []), (prefix + ("questions",), []),
                          (prefix + ("index",), True), (prefix + ("index",), -1),
                          (prefix + ("index",), np.int64(7))]
            else:
                cases += [(("questions",), []), (("questions",), {})]
            for path, value in cases:
                with self.subTest(benchmark=benchmark, path=path, value=value):
                    data, parent = schema(benchmark), None
                    parent = data
                    for part in path[:-1]:
                        parent = parent[part]
                    parent[path[-1]] = value
                    self.assert_schema_refused(data)

    def test_gap_02_F1_F7_multi_archive_duplicate_question_ids_refused_upfront(self):
        data = schema("LoCoMo")
        data["conversations"]["c1"] = deepcopy(data["conversations"]["c0"])
        data["conversations"]["c1"]["index"] = 8
        self.assert_schema_refused(data, code="E-M-040")

    def test_gap_02_F7_multi_archive_duplicate_ordinals_refused_upfront(self):
        data = schema("LoCoMo")
        second = deepcopy(data["conversations"]["c0"])
        second["questions"]["q1"] = second["questions"].pop("q0")
        data["conversations"]["c1"] = second
        data["cohort_ids"].append("q1")
        self.assert_schema_refused(data, {"q0": 0.0, "q1": 0.0})

    def test_gap_02_F7_invalid_gold_rows_refused_before_fit_in_both_schemas(self):
        invalid = [[], [True], [np.int64(0)], [0.0], [-1], [100], [0, 0], [None]]
        for benchmark in ("LoCoMo", "LongMemEval"):
            for gold in invalid:
                with self.subTest(benchmark=benchmark, gold=gold):
                    data = schema(benchmark)
                    questions = data["conversations"]["c0"]["questions"] if benchmark == "LoCoMo" else data["questions"]
                    questions["q0"]["gold_rows"] = gold
                    self.assert_schema_refused(data)

    def test_gap_03_M3_all_three_declared_refusals(self):
        for benchmark in ("LoCoMo", "LongMemEval"):
            with self.subTest(benchmark=benchmark, code="E-M-026"):
                data = schema(benchmark)
                data["questions_with_empty_gold"] = ["q0"]
                self.assert_schema_refused(data, code="E-M-026")
            for anchors in ({}, {"extra": 0.0}, {"q0": 0.0, "extra": 0.0}, None, []):
                with self.subTest(benchmark=benchmark, code="E-M-027", anchors=anchors):
                    with mock.patch.object(pipe, "Representation") as fit:
                        self.assert_refused(lambda: pipe.assemble_in_memory(schema(benchmark), anchors), "E-M-027")
                        fit.assert_not_called()
        data = schema("LongMemEval")
        data["benchmark"] = "unknown-synthetic-benchmark"
        self.assert_schema_refused(data, code="E-M-028")

    def test_gap_04_F2_empty_cohorts_archives_and_records_refused(self):
        for benchmark in ("LoCoMo", "LongMemEval"):
            for retain_archives in (False, True):
                with self.subTest(benchmark=benchmark, retain_archives=retain_archives):
                    data = schema(benchmark)
                    data["cohort_ids"] = []
                    if not retain_archives:
                        data["conversations" if benchmark == "LoCoMo" else "questions"] = {}
                    self.assert_schema_refused(data, {}, "E-M-037")
        for benchmark in ("LoCoMo", "LongMemEval"):
            with self.subTest(empty_archives=benchmark):
                data = schema(benchmark)
                data["conversations" if benchmark == "LoCoMo" else "questions"] = {}
                self.assert_schema_refused(data)
            with self.subTest(empty_records=benchmark):
                with mock.patch.object(pipe, "Representation", SyntheticRep), mock.patch.object(pipe, "score_archive", return_value=([], {})):
                    self.assert_refused(lambda: pipe.assemble_in_memory(schema(benchmark), {"q0": 0.0}), "E-M-042")

    def test_gap_05_F1_all_three_identifier_leak_paths_all_surfaces(self):
        canary = "SYNTHETIC_ID_ZQ8"
        extra = schema("LoCoMo")
        extra["conversations"]["c0"]["questions"][canary] = {"text": "query", "gold_rows": [0]}
        missing_lme = schema("LongMemEval")
        missing_lme["cohort_ids"].append(canary)
        unscored_locomo = schema("LoCoMo")
        unscored_locomo["cohort_ids"].append(canary)
        for name, data, anchors in (
            ("outside_cohort_locomo", extra, {"q0": 0.0}),
            ("missing_question_lme", missing_lme, {"q0": 0.0, canary: 0.0}),
            ("never_scored_locomo", unscored_locomo, {"q0": 0.0, canary: 0.0}),
        ):
            with self.subTest(path=name):
                self.assert_schema_refused(data, anchors, canaries=(canary,))

    def test_gap_05_text_fit_failures_all_exception_output_and_write_surfaces(self):
        payload = "SYNTHETIC_PRIVATE_FIT_941"
        texts = [f"{payload} token{i} memory topic{i % 13}" for i in range(100)]
        # Real transforms up to each fault point; no blanket fake successful fit.
        targets = [
            (pipe.TfidfVectorizer, "fit_transform", 1),
            (pipe.TfidfVectorizer, "fit_transform", 2),
            (pipe.TruncatedSVD, "fit_transform", 1),
            (pipe.TruncatedSVD, "fit_transform", 2),
            (pipe, "normalize", 1), (pipe, "normalize", 2),
            (pipe, "normalize", 3), (pipe, "normalize", 4),
            (pipe.sparse, "hstack", 1),
        ]
        for owner, name, fail_at in targets:
            with self.subTest(stage=name, occurrence=fail_at, owner=getattr(owner, "__name__", "module")):
                original, calls = getattr(owner, name), []

                def fail(*args, **kwargs):
                    calls.append(1)
                    if len(calls) == fail_at:
                        leaking_exception(payload)
                    return original(*args, **kwargs)

                with mock.patch.object(owner, name, autospec=True, side_effect=fail):
                    self.assert_refused(lambda: pipe.Representation(texts), "E-M-006", (payload,))
                self.assertEqual(len(calls), fail_at)

    def test_gap_05_query_failures_all_exception_output_and_write_surfaces(self):
        rep = pipe.Representation([f"memory word{i} topic{i % 13}" for i in range(100)])
        payload = "SYNTHETIC_PRIVATE_QUERY_713"
        targets = [(rep.word, "transform", 1), (rep.char, "transform", 1),
            (rep.lsa, "transform", 1), (rep.svd, "transform", 1),
            (pipe, "normalize", 1), (pipe, "normalize", 2),
            (pipe, "normalize", 3), (pipe, "normalize", 4),
            (pipe.sparse, "hstack", 1)]
        for index, (owner, name, fail_at) in enumerate(targets):
            with self.subTest(stage=index, method=name, occurrence=fail_at):
                original, calls = getattr(owner, name), []

                def fail(*args, **kwargs):
                    calls.append(1)
                    if len(calls) == fail_at:
                        leaking_exception(payload)
                    return original(*args, **kwargs)

                with mock.patch.object(owner, name, side_effect=fail):
                    self.assert_refused(lambda: rep.queries([payload]), "E-M-008", (payload,))
                self.assertEqual(len(calls), fail_at)

    def test_gap_05_F1_E_M_043_core_exception_wrapper_at_both_validation_sites(self):
        payload = "SYNTHETIC_CORE_ID_LEAK_187"
        rep = SyntheticRep()
        original = pipe.core.validate_per_question_records
        for fail_at in (1, 2):
            with self.subTest(validation="archive" if fail_at == 1 else "cohort"):
                calls = []

                def fail(*args, **kwargs):
                    calls.append(1)
                    if len(calls) == fail_at:
                        leaking_exception(payload)
                    return original(*args, **kwargs)

                anchors = {"q0": anchor_for(rep, 0, [0, 1, 2, 3, 4])}
                with mock.patch.object(pipe, "Representation", SyntheticRep), mock.patch.object(pipe.core, "validate_per_question_records", side_effect=fail):
                    self.assert_refused(lambda: pipe.assemble_in_memory(schema("LongMemEval"), anchors), "E-M-043", (payload,))
                self.assertEqual(len(calls), fail_at)

    def test_gap_05_F1_E_M_043_malformed_records_do_not_expose_identifiers(self):
        payload = "SYNTHETIC_RECORD_ID_611"
        rows, _ = score()
        mutations = [rows + [deepcopy(rows[0])], rows[:-1], deepcopy(rows)]
        mutations[-1][0]["question_id"] = payload
        for index, records in enumerate(mutations):
            with self.subTest(malformed=index):
                self.assert_refused(lambda: pipe.validate_records(records, ["synthetic-q0"]), "E-M-043", (payload,))

    def test_F5_insufficient_features_retains_specific_E_M_005(self):
        self.assert_refused(lambda: pipe.Representation(["alpha"] * 100), "E-M-005")

    def test_gap_06_anchor_types_ranges_and_container_refusals(self):
        class FloatSubclass(float):
            pass

        rep = SyntheticRep()
        invalid = [True, False, 0, 1, np.int64(0), np.float16(0.5),
            np.float32(0.5), np.float64(0.5), FloatSubclass(0.5),
            float("nan"), float("inf"), -float("inf"), -0.01, 1.01,
            float(np.nextafter(0.0, -1.0)), float(np.nextafter(1.0, 2.0)),
            None, "0.5", complex(0.5), [], {}, np.array(0.5)]
        for index, value in enumerate(invalid):
            with self.subTest(case=index, type=type(value).__name__):
                with mock.patch.object(rep, "queries", wraps=rep.queries) as query:
                    self.assert_refused(lambda: score(rep, anchor=[value]), "E-M-022")
                    query.assert_not_called()
        for value in (None, [], [0.0, 0.0], (0.0,), np.array([0.0]), "0.0"):
            with self.subTest(container=type(value).__name__, value=value):
                self.assert_refused(lambda: pipe.score_archive(rep, ["q"], [[0]], ["q0"], 0, value), "E-M-021")

    def test_gap_06_anchor_valid_endpoints_and_tolerance(self):
        rep = SyntheticRep()
        for anchor, picks in ((0.0, [5, 6, 7]), (1.0, [0, 1, 2])):
            with self.subTest(endpoint=anchor):
                with mock.patch.object(pipe, "topks_by_hamming", return_value=[np.array(picks)] * 20):
                    rows, _ = pipe.score_archive(rep, ["q"], [[0, 1, 2]], ["q0"], 0, [anchor])
                self.assertEqual(len(rows), 60)
        # Interior score 1/2, find the adjacent representable anchors bracketing TOL.
        self.assertEqual(pipe.core.TOL, 1e-12)
        for direction in (-1, 1):
            near = 0.5 + direction * 1e-12
            while abs(near - 0.5) > 1e-12:
                near = float(np.nextafter(near, 0.5))
            far = float(np.nextafter(near, -np.inf if direction < 0 else np.inf))
            self.assertLessEqual(abs(near - 0.5), 1e-12)
            self.assertGreater(abs(far - 0.5), 1e-12)
            with mock.patch.object(pipe, "topks_by_hamming", return_value=[np.array([0, 5, 6])] * 20):
                rows, _ = pipe.score_archive(rep, ["q"], [[0, 1]], ["q0"], 0, [near])
                self.assertEqual(len(rows), 60)
                self.assert_refused(lambda: pipe.score_archive(rep, ["q"], [[0, 1]], ["q0"], 0, [far]), "E-M-025")

    def test_gap_07_gap_09_4000_exact_order_cases_against_raw_AST_function(self):
        raw = subprocess.run(["git", "show", PINNED_SOURCE], cwd=ROOT,
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PINNED_SHA256)
        tree = ast.parse(raw, filename=PINNED_SOURCE)
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "topks_by_hamming"]
        self.assertEqual(len(functions), 1)
        # Compile ONLY this source function. No imports or other top-level source
        # expressions can run; np and TOPK are explicitly supplied dependencies.
        node = deepcopy(functions[0])
        self.assertEqual(node.decorator_list, [])
        namespace = {"np": np, "TOPK": 3}
        exec(compile(ast.Module(body=[node], type_ignores=[]), PINNED_SOURCE, "exec"), namespace)
        reference = namespace["topks_by_hamming"]
        rng = np.random.default_rng(9040912)
        branches = Counter()
        rounded_cases = all_equal_cases = unsorted_selections = 0
        for case in range(4000):
            n = int(rng.choice([1, 2, 3, 4, 5, 17, 110]))
            hi = int(rng.choice([1, 2, 3, 5, 97]))
            k = 3 if case % 4 else int(rng.choice([1, 2, 3, 5]))
            dist = rng.integers(0, hi, size=n)
            priorities = rng.random((4, n))
            if case % 2 == 0:
                priorities = np.round(priorities, 1)
                rounded_cases += 1
            all_equal_cases += int(np.all(dist == dist[0]))
            if n <= k:
                branch = "small"
            else:
                kth = sorted(dist.tolist())[k - 1]
                need = k - sum(int(d < kth) for d in dist)
                self.assertGreater(need, 0, "historical need<=0 branch is unreachable for valid distances")
                branch = "all_boundary" if need == sum(int(d == kth) for d in dist) else "partial_boundary"
            branches[branch] += 1
            with self.subTest(case=case, branch=branch):
                before = (dist.tobytes(), priorities.tobytes())
                actual, expected = pipe.topks_by_hamming(dist, priorities, k), reference(dist, priorities, k)
                self.assertEqual(len(actual), 4)
                for a, e, p in zip(actual, expected, priorities):
                    np.testing.assert_array_equal(a, e)
                    self.assertEqual(len(a), min(k, n))
                    self.assertEqual(len(set(a)), len(a))
                    unsorted_selections += int(not np.array_equal(a, np.lexsort((p, dist))[:k]))
                self.assertEqual((dist.tobytes(), priorities.tobytes()), before)
        self.assertEqual(sum(branches.values()), 4000)
        self.assertEqual(set(branches), {"small", "all_boundary", "partial_boundary"})
        self.assertTrue(all(count > 100 for count in branches.values()), branches)
        self.assertEqual(rounded_cases, 2000)
        self.assertGreater(all_equal_cases, 100)
        self.assertGreater(unsorted_selections, 100)

    def test_gap_07_semantic_lexsort_set_oracle_unique_priorities(self):
        rng = np.random.default_rng(90917)
        for case in range(1000):
            n = int(rng.choice([1, 2, 3, 4, 5, 17, 110]))
            k = int(rng.choice([1, 2, 3, 5]))
            dist = rng.integers(0, int(rng.choice([1, 2, 3, 5, 97])), n)
            # Permutations guarantee uniqueness; no ambiguous rounded-priority ties.
            priorities = np.stack([rng.permutation(n).astype(float) for _ in range(4)])
            with self.subTest(case=case):
                actual = pipe.topks_by_hamming(dist, priorities, k)
                for p, top, expected in zip(priorities, actual, semantic_picks(dist, priorities, k)):
                    self.assertEqual(len(set(p)), n)
                    self.assertEqual(set(top), set(expected))
                    self.assertEqual(len(top), min(k, n))

    def test_gap_09_selection_order_is_not_rank_and_recall_is_set_based(self):
        dist = np.array([2, 0, 1, 9])
        priorities = np.array([[0.1, 0.4, 0.3, 0.2]])
        top = pipe.topks_by_hamming(dist, priorities)[0]
        np.testing.assert_array_equal(top, [1, 2, 0])
        # strict indices occur in archive order, even when distances disagree.
        dist = np.array([1, 0, 2, 9])
        top = pipe.topks_by_hamming(dist, priorities)[0]
        np.testing.assert_array_equal(top, [0, 1, 2])
        self.assertFalse(np.array_equal(top, np.lexsort((priorities[0], dist))[:3]))
        gold = [0, 2, 7, 8]
        for permutation in itertools.permutations(top):
            self.assertEqual(pipe.fractional(permutation, gold), 0.5)
        self.assertEqual(pipe.fractional([0, 0, 0], gold), 0.25)
        self.assertEqual(pipe.fractional([0, 2, 7], gold), 0.75)

    def test_gap_09_six_arm_seed_order_scaling_before_rotation_and_metric(self):
        rep, ordinal, gold = SyntheticRep(), 3, [0, 1, 2, 3, 4]
        rows, diagnostics = score(rep, ordinal)
        self.assertEqual(tuple(pipe.core.ARMS), ARMS)
        self.assertEqual(tuple(pipe.core.ROTATION_SEEDS), ROTATION_SEEDS)
        self.assertEqual(tuple(pipe.core.PARTITION_SEEDS), PARTITION_SEEDS)
        self.assertEqual([(r["rotation_seed"], r["arm"]) for r in rows], [(s, a) for s in ROTATION_SEEDS for a in ARMS])
        self.assertEqual(diagnostics, rep.diagnostics)
        priorities = independent_priorities(ordinal, len(rep.C))
        wrong_order_changes = 0
        for offset, (seed, partition) in enumerate(zip(ROTATION_SEEDS, PARTITION_SEEDS)):
            a, b = pipe.core.draw_rotation_blocks(seed)
            rs = pipe.core.build_rotation(a, b, np.arange(32))
            rr = pipe.core.build_rotation(a, b, np.random.default_rng(partition).permutation(96)[:32])
            C, Q, D = rep.C, rep.Q, rep.D
            cells = [(C, Q), (C @ D, Q @ D), (C @ rs, Q @ rs),
                ((C @ D) @ rs, (Q @ D) @ rs), (C @ rr, Q @ rr), ((C @ D) @ rr, (Q @ D) @ rr)]
            for arm_index, (X, V) in enumerate(cells):
                distances = np.count_nonzero((X >= 0) != (V[0] >= 0), axis=1)
                expected = float(np.mean([len(set(p) & set(gold)) / len(gold) for p in semantic_picks(distances, priorities)]))
                record = rows[offset * 6 + arm_index]
                self.assertEqual(set(record), {"question_id", "rotation_seed", "arm", "fractional_R3"})
                self.assertIs(type(record["fractional_R3"]), float)
                self.assertEqual(record["fractional_R3"], expected)
                self.assertLessEqual(expected, 3 / len(gold))
            self.assertEqual(rows[offset * 6]["fractional_R3"], rows[offset * 6 + 1]["fractional_R3"])
            for R, index in ((rs, 3), (rr, 5)):
                wrong_dist = np.count_nonzero(((C @ R) @ D >= 0) != (((Q @ R) @ D)[0] >= 0), axis=1)
                wrong = float(np.mean([len(set(p) & set(gold)) / len(gold) for p in semantic_picks(wrong_dist, priorities)]))
                wrong_order_changes += int(wrong != rows[offset * 6 + index]["fractional_R3"])
        self.assertGreater(wrong_order_changes, 0, "fixture must discriminate rotate-before-scale")

    def test_gap_02_gap_09_connector_order_and_per_archive_ordinals(self):
        for benchmark in ("LoCoMo", "LongMemEval"):
            with self.subTest(benchmark=benchmark):
                data = schema(benchmark)
                data["cohort_ids"] = ["q1", "q0"]
                if benchmark == "LoCoMo":
                    other = deepcopy(data["conversations"]["c0"])
                    other["index"] = 2
                    other["questions"]["q1"] = other["questions"].pop("q0")
                    data["conversations"]["c1"] = other
                    expected = [(7, "q0"), (2, "q1")]
                else:
                    data["questions"]["q1"] = deepcopy(data["questions"]["q0"])
                    expected = [(0, "q0"), (1, "q1")]
                rep = SyntheticRep()
                anchors = {qid: anchor_for(rep, ordinal, [0, 1, 2, 3, 4]) for ordinal, qid in expected}
                with mock.patch.object(pipe, "Representation", SyntheticRep), mock.patch.object(pipe, "score_archive", wraps=pipe.score_archive) as scorer, captured_surfaces() as captured:
                    result = pipe.assemble_in_memory(data, anchors)
                self.assertEqual([(call.args[4], call.args[3][0]) for call in scorer.call_args_list], expected)
                self.assertEqual([d["archive_ordinal"] for d in result["diagnostics"]], [o for o, _ in expected])
                self.assertEqual([(r["question_id"], r["rotation_seed"], r["arm"]) for r in result["records"]], [(q, s, a) for _, q in expected for s in ROTATION_SEEDS for a in ARMS])
                self.assertEqual(len(result["records"]), 120)
                stdout, stderr, writes, fd_output = captured
                self.assertEqual((stdout.getvalue(), stderr.getvalue(), writes, fd_output), ("", "", [], []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
