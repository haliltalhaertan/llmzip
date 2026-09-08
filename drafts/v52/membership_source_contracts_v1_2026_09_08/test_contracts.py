"""Pure synthetic contracts; no corpus, ranking, fitting or bootstrap."""
import copy
import unittest
import traceback
import contracts as c


class Tests(unittest.TestCase):
    def setUp(self):
        self.ids = ['q1', 'q2']
        self.raw = {'q1': ['a'], 'q2': ['b']}
        self.rows = {q: {'a': 0, 'b': 1} for q in self.ids}

    def resolve(self, corrections):
        return c.resolve_locomo_gold(self.ids, self.raw, corrections, self.rows)

    def test_correction_replaces_not_unions(self):
        out = self.resolve({'q1': {'correct_evidence': ['b']}})
        self.assertEqual(out['q1']['gold_rows'], [1])
        self.assertNotEqual(out['q1']['gold_rows'], [0])  # raw-only mutant
        self.assertNotEqual(out['q1']['gold_rows'], [0, 1])  # union mutant
        self.assertEqual(out['q2']['gold_rows'], [1])

    def test_empty_present_never_falls_back_or_drops(self):
        with self.assertRaisesRegex(c.ContractError, 'E-S-009'):
            self.resolve({'q1': {'correct_evidence': []}})
        with self.assertRaisesRegex(c.ContractError, 'E-S-004'):
            self.resolve({'q1': {'correct_evidence': None}})

    def test_missing_field_fallback_and_no_cohort_reselection(self):
        out = self.resolve({'q1': {'error_type': 'synthetic'},
                            'outside': {'correct_evidence': []}})
        self.assertEqual(list(out), self.ids)
        self.assertEqual(out['q1']['gold_rows'], [0])
        self.assertFalse(out['q1']['correction_applied'])

    def test_partial_and_total_unresolved_fail(self):
        for refs in (['a', 'missing'], ['missing']):
            with self.assertRaisesRegex(c.ContractError, 'E-S-014'):
                self.resolve({'q1': {'correct_evidence': refs}})

    def test_dedup_and_nonmutation(self):
        correction = {'q1': {'correct_evidence': ['b', 'b']}}
        before = copy.deepcopy((self.ids, self.raw, correction, self.rows))
        self.assertEqual(self.resolve(correction)['q1']['gold_rows'], [1])
        self.assertEqual(before, (self.ids, self.raw, correction, self.rows))

    def test_lme_distinct_orders_and_bound_order_invariance(self):
        source, bound = ['z', 'a_abs', 'b'], ['b', 'z']
        expected = [{'question_id': 'z', 'archive_ordinal': 2, 'primary_position': 0, 'shard_index': 0},
                    {'question_id': 'b', 'archive_ordinal': 1, 'primary_position': 1, 'shard_index': 1}]
        for ids in (bound, list(reversed(bound))):
            self.assertEqual(c.longmemeval_plan(source, ids, expected_source=3, expected_primary=2), expected)
        # Rejects the behavioral outputs of cohort-enumeration and primary-only lexical mutants.
        self.assertNotEqual([r['archive_ordinal'] for r in expected], [0, 1])
        self.assertNotEqual([r['archive_ordinal'] for r in expected], [1, 0])

    def test_ten_shards_complete(self):
        source = [f'q{i:03}' for i in reversed(range(470))] + [f'abs{i}_abs' for i in range(30)]
        plan = c.longmemeval_plan(source, sorted(source[:470]))
        self.assertEqual(len(plan), 470)
        self.assertEqual([sum(r['shard_index'] == s for r in plan) for s in range(10)], [47] * 10)
        self.assertEqual(plan[0]['archive_ordinal'], 499)
        self.assertEqual(plan[0]['question_id'], 'q469')

    def test_invalid_coverage_types_and_empty(self):
        for ids in ([], ['q1', 'q1'], ['q1', True]):
            with self.assertRaises(c.ContractError):
                c.resolve_locomo_gold(ids, self.raw, {}, self.rows)
        for source, bound in ((['q', 'q'], ['q']), (['q', 'x_abs'], ['missing']), (['q'], ['q'])):
            with self.assertRaises(c.ContractError):
                c.longmemeval_plan(source, bound, expected_source=2, expected_primary=1)

    def test_identifier_not_in_error_surfaces(self):
        marker = 'PRIVATE_QID_CANARY'
        try:
            c.resolve_locomo_gold([marker], {}, {}, {})
        except c.ContractError as exc:
            self.assertEqual(str(exc), 'E-S-007')
            self.assertNotIn(marker, str(exc) + repr(exc) + ''.join(traceback.format_exception(exc)))
            self.assertIsNone(exc.__context__)
        else:
            self.fail('missing rejection')

    def test_real_entry_refuses(self):
        with self.assertRaisesRegex(c.ContractError, 'E-S-018'):
            c.run_on_real_corpus(enabled=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
