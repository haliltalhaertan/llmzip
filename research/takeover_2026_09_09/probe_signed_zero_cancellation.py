#!/usr/bin/env python3
"""Outcome-free diagnostic; NOT a package audit or execution authorization.

The three numerical functions below reproduce the source control expressions in:
  ed4e22c520b7dc0ae2f43f915e0c621070c72a87
  drafts/v52/membership_execution_prep_v1_2026_09_08/pipeline.py (controls)
  drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py
  (check_identity and hamming_dist).
Only these isolated functions run. No package import, corpus, network, fit, ranking,
scoring, bootstrap, finalizer, authorization, or seed-panel change is involved.
The separate Fraction oracle does not depend on NumPy or floating-point arithmetic.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
import platform
from types import SimpleNamespace
import unittest

import numpy as np


class PipelineError(ValueError):
    pass


class DesignViolation(RuntimeError):
    pass


def require(condition, code):
    if not condition:
        raise PipelineError(code)


# Isolated source expressions; the original module/import prologue is not executed.
def check_identity(C: np.ndarray, Q: np.ndarray, D: np.ndarray) -> None:
    """sign(xD) = sign(x) must hold BIT-IDENTICALLY for archive and query, or the run aborts."""
    Cs, Qs = C @ D, Q @ D
    if not (np.all(np.isfinite(Cs)) and np.all(np.isfinite(Qs))):
        raise DesignViolation("non-finite value in the rescaled representation C D; aborting, not repairing")
    if not np.array_equal(Cs >= 0, C >= 0) or not np.array_equal(Qs >= 0, Q >= 0):
        raise DesignViolation("IDENTITY VIOLATION: sign(xD) != sign(x); the design premise fails")


def hamming_dist(C: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Zero-threshold sign code, Hamming distance from one query to every archive row."""
    return np.count_nonzero((C >= 0) != (q >= 0)[None, :], axis=1).astype(np.int16)


core = SimpleNamespace(check_identity=check_identity, hamming_dist=hamming_dist)


def controls(C, Q, D):
    require(D.shape == (96, 96) and np.array_equal(D, np.diag(np.diag(D)))
            and np.isfinite(D).all() and (np.diag(D) > 0).all(), 'E-M-030: positive diagonal required')
    core.check_identity(C, Q, D)
    # Deterministic canary, not a new experimental arm or a seed panel.
    # At exact zero, signed real coordinates need not preserve >=0 codes;
    # an observed failure aborts rather than silently changing zero convention.
    perm = np.arange(95, -1, -1)
    signs = np.where(np.arange(96) % 2, -1, 1)
    for X, V in ((C, Q), (C @ D, Q @ D)):
        for q in V:
            require(np.array_equal(core.hamming_dist(X, q),
                                   core.hamming_dist(X[:, perm] * signs, q[perm] * signs)),
                    'E-M-031: signed permutation control')


def fixture(zero_columns=()):
    """96 finite synthetic rows; archive is column-centered; D=I is positive."""
    row = np.ones(96, dtype=np.float64)
    row[list(zero_columns)] = 0.0
    C = np.tile(np.stack([row, -row]), (48, 1))
    Q = np.ones((1, 96), dtype=np.float64)
    return C, Q, np.eye(96)


def exact_distance(x, y):
    return sum((a >= 0) != (b >= 0) for a, b in zip(x, y))


def transformed(values, perm, signs):
    return tuple(values[p] * s for p, s in zip(perm, signs))


class DiagnosticTests(unittest.TestCase):
    def test_no_zero_control_passes(self):
        controls(*fixture())

    def test_covered_single_zero_is_detected(self):
        with self.assertRaisesRegex(PipelineError, 'E-M-031'):
            controls(*fixture([0]))

    def test_uncovered_single_zero_passes(self):
        controls(*fixture([1]))

    def test_two_covered_zero_changes_cancel(self):
        C, Q, D = fixture([0, 2])
        Q[0, 2] = -1.0
        self.assertTrue(np.array_equal(C.mean(axis=0), np.zeros(96)))
        controls(C, Q, D)  # Existing gate accepts, even at TWO negated coordinates.
        perm = np.arange(95, -1, -1)
        signs = np.where(np.arange(96) % 2, -1, 1)
        before = (C >= 0) != (Q[0] >= 0)
        after = (C[:, perm] * signs >= 0) != (Q[0, perm] * signs >= 0)
        changed = np.count_nonzero(before[:, perm] != after, axis=1)
        self.assertTrue(np.all(changed == 2))
        self.assertTrue(np.array_equal(before.sum(axis=1), after.sum(axis=1)))

    def test_all_negative_alternative_also_misses_cancellation(self):
        C, Q, _ = fixture([0, 2])
        Q[0, 2] = -1.0
        perm = np.arange(95, -1, -1)
        self.assertTrue(np.array_equal(hamming_dist(C, Q[0]),
                                       hamming_dist(-C[:, perm], -Q[0, perm])))

    def test_separate_coordinate_flips_reveal_both_changes(self):
        C, Q, _ = fixture([0, 2])
        Q[0, 2] = -1.0
        base = hamming_dist(C, Q[0])
        for col, delta in ((0, 1), (2, -1)):
            signs = np.ones(96)
            signs[col] = -1
            self.assertTrue(np.all(hamming_dist(C * signs, Q[0] * signs) - base == delta))

    def test_exact_fraction_counterexample(self):
        x = (Fraction(0), Fraction(0))
        y = (Fraction(1), Fraction(-1))
        self.assertEqual(exact_distance(x, y), 1)
        self.assertEqual(exact_distance(tuple(-v for v in x), tuple(-v for v in y)), 1)
        self.assertEqual(exact_distance((-x[0], x[1]), (-y[0], y[1])), 2)
        self.assertEqual(exact_distance((x[0], -x[1]), (y[0], -y[1])), 0)

    def test_zero_mask_characterization_exhaustive_small_domain(self):
        values = tuple(itertools.product(map(Fraction, (-1, 0, 1)), repeat=2))
        permutations = tuple(itertools.permutations(range(2)))
        signs = tuple(itertools.product((-1, 1), repeat=2))
        checked = 0
        for x, y in itertools.product(values, repeat=2):
            invariant = all(exact_distance(transformed(x, p, s), transformed(y, p, s))
                            == exact_distance(x, y) for p in permutations for s in signs)
            same_zero_mask = all((a == 0) == (b == 0) for a, b in zip(x, y))
            self.assertEqual(invariant, same_zero_mask)
            checked += 1
        self.assertEqual(checked, 81)

    def test_positive_diagonal_refusal_preserved(self):
        C, Q, D = fixture()
        D[0, 0] = 0.0
        with self.assertRaisesRegex(PipelineError, 'E-M-030'):
            controls(C, Q, D)


if __name__ == '__main__':
    import sys
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DiagnosticTests)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    report = {
        'status': 'SYNTHETIC_DIAGNOSTIC_ONLY_NOT_PACKAGE_ACCEPTANCE',
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'python': platform.python_version(),
        'numpy': np.__version__,
        'accepted_environment_replay': False,
        'full_continuity_verifier_run': False,
        'candidate_commit': 'ed4e22c520b7dc0ae2f43f915e0c621070c72a87',
        'candidate_pipeline_git_blob': '6b41a4242ec7de5018537f4be5f4835d16ed03fd',
        'core_git_blob': 'b0f8183ec53d590abd765afe5a301ca906fb6a35',
        'execution_scope': 'isolated copied control functions and independent exact-rational oracle',
        'original_canary_two_covered_coordinate_cancellation': True,
        'all_negative_canary_cancellation': True,
        'exact_two_dimensional_distances': {'native': 1, 'negate_both': 1, 'negate_first': 2, 'negate_second': 0},
        'exact_domain_vector_pairs_checked': 81,
        'real_corpus_accessed': False,
        'real_outcomes_accessed': False,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
