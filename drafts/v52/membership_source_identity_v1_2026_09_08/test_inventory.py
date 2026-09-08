import json
from pathlib import Path
import unittest
from unittest.mock import patch

import verify_inventory as v


class InventoryTests(unittest.TestCase):
    def test_record_matches_pinned_source(self):
        recorded = json.loads(Path(__file__).with_name('EXPECTED_CORRECTION_IDENTITIES.json').read_text())
        self.assertEqual(recorded, v.expected_inventory())

    def test_wrong_source_bytes_rejected(self):
        with patch.object(v.subprocess, 'check_output', return_value=b'not the source'):
            with self.assertRaisesRegex(RuntimeError, '^SOURCE_IDENTITY_MISMATCH$'):
                v.expected_inventory()

    def test_wrong_full_inventory_rejected(self):
        with patch.object(v, 'FULL_HASH', '0' * 64):
            with self.assertRaisesRegex(RuntimeError, '^FULL_INVENTORY_MISMATCH$'):
                v.expected_inventory()

    def test_wrong_subset_inventory_rejected(self):
        with patch.object(v, 'SUBSET_HASH', '0' * 64):
            with self.assertRaisesRegex(RuntimeError, '^SUBSET_INVENTORY_MISMATCH$'):
                v.expected_inventory()


if __name__ == '__main__':
    unittest.main(verbosity=2)
