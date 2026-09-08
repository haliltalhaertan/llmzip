import copy
import unittest
from unittest.mock import patch

import exception as e
import preflight as p


class ExceptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = p.module('56e67018b61c32fd0392f0d8f4234e731faf8ce9',
            'drafts/v52/membership_source_contracts_v1_2026_09_08/contracts.py',
            '15d5f102d6207755d180ca0477d02b1e8bb41a5985fd091bded4771503e99ae4')

    def setUp(self):
        self.mapping = {f'm{i}': i for i in range(680)}
        self.refs = [f'm{i}' for i in range(6)] + ['missing']
        self.raw = {e.QID: self.refs, 'other': ['m0']}
        self.maps = {e.QID: self.mapping, 'other': self.mapping}
        self.corrections = {}
        self.patch = patch.multiple(e, REFS_HASH=e.digest(self.refs),
            MISSING_HASH=e.digest(['missing']), ARCHIVE_HASH=e.digest(list(self.mapping)))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def run_contract(self):
        return e.resolve_with_exception(self.contract, list(self.raw), self.raw, self.corrections, self.maps)

    def test_only_target_changed_without_mutation(self):
        before = copy.deepcopy((self.raw, self.maps, self.corrections))
        result = self.run_contract()
        self.assertEqual(result[e.QID]['gold_rows'], list(range(6)))
        self.assertEqual(result[e.QID]['evidence_declared_original'], 7)
        self.assertEqual(result['other']['gold_rows'], [0])
        self.assertNotIn('gold_exception', result['other'])
        self.assertEqual((self.raw, self.maps, self.corrections), before)

    def test_other_question_still_strict(self):
        self.raw['other'] = ['m0', 'missing']
        with self.assertRaisesRegex(self.contract.ContractError, '^E-S-014$'):
            self.run_contract()

    def test_correction_record_refused(self):
        self.corrections[e.QID] = {}
        with self.assertRaisesRegex(self.contract.ContractError, '^E-X-003$'):
            self.run_contract()

    def test_changed_seven_references_refused(self):
        self.raw[e.QID] = self.refs[:-1] + ['different']
        with self.assertRaisesRegex(self.contract.ContractError, '^E-X-006$'):
            self.run_contract()

    def test_changed_archive_refused(self):
        self.mapping['m0'], self.mapping['m1'] = self.mapping['m1'], self.mapping['m0']
        with self.assertRaisesRegex(self.contract.ContractError, '^E-X-005$'):
            self.run_contract()

    def test_wrong_missing_hash_refused(self):
        with patch.object(e, 'MISSING_HASH', '0' * 64):
            with self.assertRaisesRegex(self.contract.ContractError, '^E-X-007$'):
                self.run_contract()

    def test_target_absent_refused(self):
        self.raw.pop(e.QID)
        self.maps.pop(e.QID)
        with self.assertRaisesRegex(self.contract.ContractError, '^E-X-002$'):
            self.run_contract()


if __name__ == '__main__':
    unittest.main(verbosity=2)
