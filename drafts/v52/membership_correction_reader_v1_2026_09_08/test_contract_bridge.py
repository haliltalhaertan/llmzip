"""Generated files and pinned contract only; no actual correction corpus."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest

import reader
from test_reader import identities


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[3]
        raw = subprocess.check_output(['git', '-C', str(root), 'cat-file', 'blob',
            '56e67018b61c32fd0392f0d8f4234e731faf8ce9:drafts/v52/membership_source_contracts_v1_2026_09_08/contracts.py'])
        if hashlib.sha256(raw).hexdigest() != '15d5f102d6207755d180ca0477d02b1e8bb41a5985fd091bded4771503e99ae4':
            raise RuntimeError('CONTRACT_HASH_MISMATCH')
        cls.contract = types.ModuleType('pinned_contract_bridge')
        exec(compile(raw, '<pinned-contract>', 'exec'), cls.contract.__dict__)

    def from_fake_file(self, row):
        data = json.dumps([row]).encode()
        with tempfile.TemporaryDirectory(prefix='synthetic_correction_') as temp:
            file = Path(temp) / 'fake.json'
            file.write_bytes(data)
            payloads = {'fake.json': file.read_bytes()}
            return reader.parse_verified(payloads, identities({'fake.json': data}))

    def resolve(self, corrections):
        return self.contract.resolve_locomo_gold(['q1'], {'q1': ['D1:1']}, corrections,
                                                 {'q1': {'D1:1': 0, 'D1:2': 1}})

    def test_replacement_and_absence(self):
        corrected = self.from_fake_file(dict(question_id='q1', correct_evidence='D1:2'))
        self.assertEqual(self.resolve(corrected)['q1']['gold_rows'], [1])
        absent = self.from_fake_file(dict(question_id='q1'))
        self.assertEqual(self.resolve(absent)['q1']['gold_rows'], [0])

    def test_empty_never_falls_back(self):
        for value in (None, []):
            corrected = self.from_fake_file(dict(question_id='q1', correct_evidence=value))
            with self.assertRaisesRegex(self.contract.ContractError, '^E-S-009$'):
                self.resolve(corrected)

    def test_partial_never_drops_reference(self):
        corrected = self.from_fake_file(dict(question_id='q1', correct_evidence=['D1:2', 'D9:9']))
        with self.assertRaisesRegex(self.contract.ContractError, '^E-S-014$'):
            self.resolve(corrected)

    def test_dictionary_labels_are_literal(self):
        text = ' see D1:2 and D9:9 '
        corrected = self.from_fake_file(dict(question_id='q1', correct_evidence=[{'dia_id': text}]))
        self.assertEqual(corrected['q1']['correct_evidence'], [text])

    def test_real_entry_stays_disabled(self):
        with self.assertRaisesRegex(reader.ReaderError, '^E-R-016$'):
            reader.run_on_real_corpus()

    def test_float_overflow_in_ignored_metadata_rejected(self):
        for token in (b'1e999', b'-1e999'):
            raw = b'[{"question_id":"q1","metadata":' + token + b'}]'
            payloads = {'fake.json': raw}
            with self.assertRaisesRegex(reader.ReaderError, '^E-R-008$'):
                reader.parse_verified(payloads, identities(payloads))


if __name__ == '__main__':
    unittest.main(verbosity=2)
