"""Focused follow-up: declared frozen shared model bytes versus record bytes.

Uses only the independent review's toy fixtures. One regression deliberately
requires rejection of a frozen model size change; no model artifacts are read.
"""

import unittest

import test_independent_guard as fixtures


class FrozenSharedReview(unittest.TestCase):
    def setUp(self):
        self.case = fixtures.IndependentGuardChecks()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def shared_model(self):
        self.case.data["items"][0].update(
            cost_scope="SHARED",
            role="frozen shared model state; not a container or record-count header",
            reason="same declared physical model bytes and fixed format across N and N+q",
        )
        self.case.write_plan()

    @staticmethod
    def model_callback(after):
        def callback(request):
            row = fixtures.declaration_echo(request)
            row["items"][0].update(bytes_before=32, bytes_after=after)
            return row
        return callback

    def test_unchanged_shared_model_is_accepted(self):
        self.shared_model()
        rows = [self.case.probe(r, self.model_callback(32))
                for r in fixtures.guard.expected_requests(self.case.load())]
        self.assertEqual(self.case.finish(rows)["status"], "COMPLETE")

    def test_record_bytes_can_change_with_population(self):
        rows = [self.case.probe(r) for r in fixtures.guard.expected_requests(self.case.load())]
        self.assertTrue(all(row["items"][0]["bytes_after"] > row["items"][0]["bytes_before"]
                            for row in rows))
        self.assertEqual(self.case.finish(rows)["status"], "COMPLETE")

    def test_frozen_shared_model_growth_must_not_complete(self):
        self.shared_model()
        try:
            rows = [self.case.probe(r, self.model_callback(33))
                    for r in fixtures.guard.expected_requests(self.case.load())]
            result = self.case.finish(rows)
        except fixtures.guard.PlanValidationError:
            return
        print("FROZEN_SHARED_COUNTEREXAMPLE: before=32 after=33; status=" + result["status"], flush=True)
        self.assertNotEqual(result["status"], "COMPLETE",
                            "Explicit frozen shared model growth accepted as complete coverage")


if __name__ == "__main__":
    print("FROZEN SHARED REVIEW; guard SHA256=" + fixtures.GUARD_SHA256, flush=True)
    unittest.main(verbosity=2)
