"""Related L-080 findings, strict record wrapper, and byte identity regressions."""
import contextlib
import inspect
import io
import traceback
import unittest
from unittest import mock
import numpy as np
import errors
import corpus_ingest_g3 as ingest
import membership_runner_g3 as runner
import pipeline_g3 as pipe
import record_boundary


class IntSubclass(int):
    def __repr__(self):
        return 'SYNTHETIC_INT_CANARY'
    __str__ = __repr__


class FakeCode:
    @property
    def __class__(self):
        return errors.Code
    value = 'SYNTHETIC_CODE_CANARY'


def capture(fn):
    output, stderr = io.StringIO(), io.StringIO()
    caught = None
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(stderr):
        try:
            fn()
        except Exception as exc:
            caught = exc
    pieces = [output.getvalue(), stderr.getvalue()]
    pending, seen = [caught] if caught else [], set()
    while pending:
        e = pending.pop()
        if id(e) in seen:
            continue
        seen.add(id(e))
        pieces.extend((str(e), repr(e), ''.join(traceback.format_exception(e))))
        pending.extend(x for x in (e.__cause__, e.__context__) if x)
    return caught, '\n'.join(pieces)


def mapping(n=1):
    return dict(source_id='synthetic', source_sha256='0' * 64, benchmark='LoCoMo',
                expected_cluster_ids=['c0'], expected_question_to_cluster={'q0': 'c0'}, n_questions=n)


class RelatedG2Tests(unittest.TestCase):
    def assert_count_refusal(self, fn):
        e, surface = capture(fn)
        self.assertIsInstance(e, runner.DesignViolation)
        self.assertNotIsInstance(e, errors.UnsafeErrorField)
        self.assertIn(errors.Code.MANIFEST_FIELD_TYPE.value, str(e))
        self.assertNotIn('SYNTHETIC_INT_CANARY', surface)
        self.assertIsNone(e.__context__)

    def test_L080_F1_and_F3_exact_count_gates(self):
        for bad in (IntSubclass(5), True, 1.0, np.int64(1), None, '5'):
            with self.subTest(type=type(bad).__name__):
                self.assert_count_refusal(lambda: runner.verify_source_identity(['q0'], ['c0'], mapping(bad)))
                self.assert_count_refusal(lambda: ingest._manifest_n_questions(mapping(bad)))
        self.assertEqual(ingest._manifest_n_questions(mapping()), 1)
        self.assertEqual(runner.verify_source_identity(['q0'], ['c0'], mapping())['n_questions'], 1)

    def assert_spoof_refusal(self, fn):
        e, surface = capture(fn)
        self.assertIsInstance(e, errors.UnsafeErrorField)
        self.assertNotIn('SYNTHETIC_CODE_CANARY', surface)

    def test_L080_F2_spoof_exception_type_discriminates(self):
        self.assert_spoof_refusal(lambda: errors.message(FakeCode()))

    def test_L080_F2_historical_surviving_mutant_is_killed(self):
        source = inspect.getsource(errors.message)
        old = 'type(code) is not Code or not any(code is member for member in Code)'
        self.assertEqual(source.count(old), 1)
        namespace = dict(vars(errors))
        exec(source.replace(old, 'not isinstance(code, Code)'), namespace)
        with self.assertRaises(AssertionError):
            self.assert_spoof_refusal(lambda: namespace['message'](FakeCode()))

    def test_L080_F1_gate_regression_mutant_is_killed(self):
        source = inspect.getsource(runner.verify_source_identity)
        self.assertEqual(source.count('if type(n_declared) is not int:'), 1)
        namespace = dict(vars(runner))
        exec(source.replace('if type(n_declared) is not int:',
                            'if isinstance(n_declared, bool) or not isinstance(n_declared, int):'), namespace)
        with self.assertRaises(AssertionError):
            self.assert_count_refusal(lambda: namespace['verify_source_identity'](['q0'], ['c0'], mapping(IntSubclass(5))))

    def test_L080_F3_missing_local_gate_mutant_is_killed(self):
        with mock.patch.object(ingest, '_manifest_n_questions', side_effect=lambda m: m['n_questions']):
            with self.assertRaises(AssertionError):
                self.assert_count_refusal(lambda: ingest._manifest_n_questions(mapping(IntSubclass(5))))

    def test_F6_exact_blob_refuses_crlf_and_byte_mutation(self):
        raw = pipe.CORE_PATH.read_bytes()
        self.assertEqual(pipe._verified_core_bytes(raw), raw)
        for changed in (raw.replace(b'\n', b'\r\n'), raw + b'x'):
            with self.assertRaisesRegex(RuntimeError, 'E-M-001'):
                pipe._verified_core_bytes(changed)

    def test_F1_F2_record_boundary_before_immutable_core(self):
        rows = [dict(question_id='q0', rotation_seed=int(seed), arm=arm, fractional_R3=0.5)
                for seed in runner.core.ROTATION_SEEDS for arm in runner.core.ARMS]
        self.assertTrue(record_boundary.valid_records(rows, ['q0'], runner.core.ROTATION_SEEDS, runner.core.ARMS))
        variants = [[], rows[:-1], rows + [rows[0]], [None] + rows[1:]]
        for key, value in [('question_id', 'ID_' + 'CANARY_581'), ('rotation_seed', 60001.9),
                           ('rotation_seed', True), ('rotation_seed', '60001'),
                           ('fractional_R3', float('nan')), ('fractional_R3', float('inf')),
                           ('fractional_R3', True), ('fractional_R3', -0.1), ('arm', 'bogus')]:
            variants.append([dict(rows[0], **{key: value})] + rows[1:])
        variants.append([dict(rows[0], extra='ID_' + 'CANARY_581')] + rows[1:])
        for bad in variants:
            with mock.patch.object(runner.core, 'paired_matrices') as core_call:
                e, surface = capture(lambda: runner.compute_results(bad, ['q0'], ['c0'], {}, 'unused',
                                     benchmark='LoCoMo', scheme='question'))
            self.assertIsInstance(e, runner.DesignViolation)
            self.assertIn('E-G3-R01', str(e))
            self.assertNotIn('ID_' + 'CANARY_581', surface)
            self.assertIsNone(e.__context__)
            core_call.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
