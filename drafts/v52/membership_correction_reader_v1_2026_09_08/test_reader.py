"""Synthetic-only tests for the identity-first correction reader."""
import hashlib
import json
import unittest
from unittest.mock import patch

import reader


def encoded(rows):
    return json.dumps(rows, ensure_ascii=False).encode("utf-8")


def identities(payloads):
    return [dict(file=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            for name, raw in payloads.items()]


class ReaderTests(unittest.TestCase):
    def parse(self, rows):
        payloads = {"synthetic.json": encoded(rows)}
        return reader.parse_verified(payloads, identities(payloads))

    def rejected(self, payloads, expected=None):
        with self.assertRaises(reader.ReaderError) as caught:
            reader.parse_verified(payloads, identities(payloads) if expected is None else expected)
        error = caught.exception
        self.assertRegex(str(error), r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn("PRIVATE", str(error))

    def bad_rows(self, rows):
        self.rejected({"synthetic.json": encoded(rows)})

    def test_absent_evidence_and_metadata(self):
        self.assertEqual(self.parse([dict(question_id="q1", error_type="PRIVATE", correct_answer="PRIVATE")]), {"q1": {}})

    def test_present_empty_and_null_preserved(self):
        self.assertEqual(self.parse([dict(question_id="q1", correct_evidence=[]), dict(question_id="q2", correct_evidence=None)]),
                         {"q1": {"correct_evidence": []}, "q2": {"correct_evidence": []}})

    def test_regex_and_literal(self):
        self.assertEqual(self.parse([dict(question_id="q1", correct_evidence="D12:3 then D1:9 and D12:3"),
                                    dict(question_id="q2", correct_evidence="literal-reference")]),
                         {"q1": {"correct_evidence": ["D12:3", "D1:9"]}, "q2": {"correct_evidence": ["literal-reference"]}})

    def test_mixed_list_and_dedup(self):
        self.assertEqual(self.parse([dict(question_id="q1", correct_evidence=["D1:2", {"dia_id": "D2:3"}, {"id": "D1:2"}, {"dia_id": "D3:4", "id": "D3:4"}])]),
                         {"q1": {"correct_evidence": ["D1:2", "D2:3", "D3:4"]}})

    def test_missing_and_extra_files(self):
        p = {"one.json": encoded([])}
        self.rejected({}, identities(p))
        self.rejected(p, [])

    def test_duplicate_expected_names(self):
        p = {"one.json": encoded([])}
        self.rejected(p, identities(p) * 2)

    def test_size_and_hash_mismatch(self):
        p = {"one.json": encoded([])}
        for field, value in [("bytes", 999), ("sha256", "0" * 64)]:
            with self.subTest(field=field):
                expected = identities(p)
                expected[0][field] = value
                self.rejected(p, expected)

    def test_all_identities_before_any_parse(self):
        p = {"first.json": b"PRIVATE invalid JSON", "second.json": encoded([])}
        expected = identities(p)
        expected[1]["sha256"] = "0" * 64
        with patch.object(reader, "_parse_json", side_effect=AssertionError("parser must not run")) as parser:
            self.rejected(p, expected)
            parser.assert_not_called()

    def test_invalid_json_utf8_and_nonfinite(self):
        for raw in [b"PRIVATE broken", b"\xff", b'[{"question_id":"q","correct_evidence":NaN}]',
                    b'[{"question_id":"q","correct_evidence":Infinity}]']:
            with self.subTest(raw=raw):
                self.rejected({"synthetic.json": raw})

    def test_duplicate_json_keys(self):
        for raw in [b'[{"question_id":"q","question_id":"q"}]',
                    b'[{"question_id":"q","correct_evidence":[{"id":"D1:2","id":"D1:2"}]}]']:
            with self.subTest(raw=raw):
                self.rejected({"synthetic.json": raw})

    def test_top_level_and_rows(self):
        for rows in [{}, None, "PRIVATE", [None], [[]], [True], [12]]:
            with self.subTest(rows=rows):
                self.bad_rows(rows)

    def test_question_id_required_strict(self):
        self.bad_rows([{}])
        for qid in [None, "", " ", " q", "q ", 1, True, []]:
            with self.subTest(qid=qid):
                self.bad_rows([dict(question_id=qid)])

    def test_duplicate_question_within_file(self):
        self.bad_rows([dict(question_id="PRIVATE"), dict(question_id="PRIVATE")])

    def test_duplicate_question_across_files(self):
        p = {"one.json": encoded([dict(question_id="PRIVATE")]), "two.json": encoded([dict(question_id="PRIVATE")])}
        self.rejected(p)

    def test_distinct_questions_across_files(self):
        p = {"one.json": encoded([dict(question_id="q1")]), "two.json": encoded([dict(question_id="q2")])}
        self.assertEqual(reader.parse_verified(p, identities(p)), {"q1": {}, "q2": {}})

    def test_unsupported_evidence(self):
        for value in [True, False, 1, 1.5, {}, "", " ", [[]], [True], [1], [None], [""], [" "]]:
            with self.subTest(value=value):
                self.bad_rows([dict(question_id="q", correct_evidence=value)])

    def test_invalid_evidence_dict_entries(self):
        for entry in [{}, {"id": None}, {"dia_id": 1}, {"id": " "}, {"dia_id": ""},
                      {"dia_id": "D1:2", "id": "D3:4"}]:
            with self.subTest(entry=entry):
                self.bad_rows([dict(question_id="q", correct_evidence=[entry])])


if __name__ == "__main__":
    unittest.main()
