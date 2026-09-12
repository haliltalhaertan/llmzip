"""Decision 2: exact images, each member's negative, and mutation discrimination."""
import ast
from fractions import Fraction
from pathlib import Path
import unittest
from unittest import mock

import numpy as np
import pipeline_g3 as p


def independent_image(rows, permutation, mask):
    # Deliberately not p.exact_oracle, p._signs_from_mask, or p.signed_code_images.
    images = []
    for row in rows:
        image = []
        for output in range(96):
            original = Fraction(float(row[permutation[output]]))
            source_bit = int(original >= Fraction(0, 1))
            negative = (mask // (2 ** output)) % 2
            image.append(bool(1 - source_bit if negative else source_bit))
        images.append(image)
    return np.asarray(images, dtype=bool)


def distinguishing_rows():
    # 7 binary-index rows distinguish all source columns; mixed signs, no zeros.
    return np.asarray([[(-1.0 if (j >> bit) & 1 else 1.0) * (j + 1)
                        for j in range(96)] for bit in range(7)])


class CertificateTests(unittest.TestCase):
    def assert_negative_member(self, mask, direction='archive', zero=0.0):
        target = next(i for i in range(96) if mask & (1 << i))
        source = p.SIGNED_CANARY_PERMUTATION[target]
        x, q = distinguishing_rows(), -distinguishing_rows()
        if direction in ('archive', 'both'):
            x[:, source] = zero
        if direction in ('query', 'both'):
            q[:, source] = zero
        with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
            p.assert_signed_member(x, q, mask)

    def test_F3_gap8_family_literal_seed_and_total_coverage(self):
        tree = ast.parse(Path(p.__file__).read_text(encoding='utf-8'))
        definitions = {n.targets[0].id: n.value for n in tree.body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
        for name in ('SIGNED_CANARY_MASKS', 'SIGNED_CANARY_PERMUTATION'):
            value = definitions[name]
            self.assertIsInstance(value, ast.Tuple)
            self.assertTrue(all(isinstance(x, ast.Constant) and type(x.value) is int for x in value.elts))
        self.assertEqual(p.SIGNED_CANARY_MASKS, tuple(2 ** j for j in range(96)) + (2 ** 96 - 1,))
        self.assertEqual(p.SIGNED_CANARY_SEED, 52003107)
        self.assertEqual(p.SIGNED_CANARY_PERMUTATION,
                         tuple(np.random.default_rng(52003107).permutation(96)))
        self.assertEqual(set(p.SIGNED_CANARY_PERMUTATION), set(range(96)))
        self.assertNotEqual(p.SIGNED_CANARY_PERMUTATION, tuple(range(96)))

    def test_Decision2_exact_images_every_member_every_bit(self):
        archive = distinguishing_rows()
        queries = -archive[::-1].copy()
        visited = []
        actual_member = p._assert_member_codes
        def observed(x, q, mask, permutation, codes):
            visited.append(mask)
            return actual_member(x, q, mask, permutation, codes)
        with mock.patch.object(p, '_assert_member_codes', side_effect=observed):
            p.coordinatewise_signed_certificate(archive, queries)
        self.assertEqual(visited, list(p.SIGNED_CANARY_MASKS))
        for mask in p.SIGNED_CANARY_MASKS:
            with self.subTest(member=f'{mask:024x}'):
                for rows in (archive, queries):
                    np.testing.assert_array_equal(
                        p.signed_code_images(rows, p.SIGNED_CANARY_PERMUTATION, mask),
                        independent_image(rows, p.SIGNED_CANARY_PERMUTATION, mask))

    def test_Decision2_each_member_has_own_negative_both_directions_and_joint_zero(self):
        # Call THAT member directly: no earlier member may supply the failure.
        for mask in p.SIGNED_CANARY_MASKS:
            for direction in ('archive', 'query', 'both'):
                for zero in (0.0, -0.0):
                    with self.subTest(member=f'{mask:024x}', direction=direction, zero=str(zero)):
                        self.assert_negative_member(mask, direction, zero)

    def test_Decision2_exact_zero_semantics_explicit(self):
        self.assertTrue(0.0 >= 0)
        self.assertTrue(-0.0 >= 0)
        self.assertTrue(np.signbit(-0.0))
        self.assertFalse(np.signbit(0.0))
        self.assertEqual(Fraction(-0.0), Fraction(0.0))
        x = np.zeros((96, 96))
        for mask in p.SIGNED_CANARY_MASKS:
            with self.subTest(member=f'{mask:024x}'):
                with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
                    p.assert_signed_member(x, x[:1], mask)

    def test_N1_exact_adopted_centered_96_by_96_witness(self):
        x = np.tile(np.r_[np.ones(48), -np.ones(48)][:, None], (1, 96))
        x[:, (0, 2)] = 0.0
        q = np.ones((1, 96)); q[0, 2] = -1.0
        self.assertEqual(x.shape, (96, 96))
        np.testing.assert_array_equal(x.mean(axis=0), np.zeros(96))
        p.legacy_signed_canary(x, q)
        np.testing.assert_array_equal(p.core.hamming_dist(x, q[0]),
                                      p.core.hamming_dist(-x, -q[0]))
        with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
            p.coordinatewise_signed_certificate(x, q)
        with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
            p.assert_signed_member(x, q, p.SIGNED_CANARY_MASKS[-1])

    def test_Decision2_legacy_canary_retained_half_coverage_regression(self):
        for coordinate, rejects in ((0, True), (1, False)):
            x, q = np.ones((2, 96)), np.ones((1, 96))
            x[:, coordinate] = 0
            if rejects:
                with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
                    p.legacy_signed_canary(x, q)
            else:
                p.legacy_signed_canary(x, q)
        p.legacy_signed_canary(np.zeros((2, 96)), np.zeros((1, 96)))

    def test_mutation_each_member_skipped_assertion_is_detected(self):
        real = p._assert_member_codes
        # 97 independent mutants: only one selected member's assertion is removed.
        for omitted in p.SIGNED_CANARY_MASKS:
            def mutant(x, q, mask, permutation, codes, omitted=omitted):
                if mask != omitted:
                    return real(x, q, mask, permutation, codes)
            with mock.patch.object(p, '_assert_member_codes', side_effect=mutant):
                with self.assertRaises(AssertionError, msg=f'surviving member {omitted:024x}'):
                    self.assert_negative_member(omitted)

    def test_mutation_wrong_sign_and_wrong_permutation_are_detected(self):
        x, q = distinguishing_rows(), -distinguishing_rows()
        mutants = (
            lambda rows, perm, mask: rows[:, perm] >= 0,
            lambda rows, perm, mask: (rows * p._signs_from_mask(mask)) >= 0,
            lambda rows, perm, mask: np.ones_like(rows, dtype=bool),
        )
        for mutation in mutants:
            with self.subTest(mutation=mutants.index(mutation)):
                with mock.patch.object(p, 'signed_code_images', side_effect=mutation):
                    with self.assertRaisesRegex(p.PipelineError, 'E-M-031'):
                        p.coordinatewise_signed_certificate(x, q)


if __name__ == '__main__':
    unittest.main(verbosity=2)
