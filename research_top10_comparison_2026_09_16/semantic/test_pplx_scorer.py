"""TDD tests for PPLX semantic scorer (pure, no model weights needed).

Covers: official INT8/BIN formulas, near-zero counterexample, packed
roundtrip, masked mean pooling, length-bucket reorder, deterministic
ties/exact-10, multi-gold metrics, nonfinite rejection, no gold leakage,
zero-vector handling.
"""
import hashlib
import inspect
import unittest

import numpy as np


class TestOfficialQuant(unittest.TestCase):
    def test_int8_formula_matches_official(self):
        from pplx_scorer import official_int8
        rng = np.random.RandomState(0)
        x = rng.randn(4, 16).astype(np.float64) * 2.0
        got = official_int8(x)
        # Official: round(127*tanh(x)), clip[-128,127] (torch.round semantics)
        expected = np.clip(np.round(127.0 * np.tanh(x)), -128, 127).astype(np.int8)
        np.testing.assert_array_equal(got, expected)
        self.assertEqual(got.dtype, np.int8)

    def test_int8_matches_torch_reference_when_available(self):
        try:
            import torch
        except ImportError:
            self.skipTest("torch unavailable")
        from pplx_scorer import official_int8
        x = np.array([[-0.001, -0.5, 0.0, 0.5, 2.0, -3.0]], dtype=np.float32)
        got = official_int8(x)
        with torch.no_grad():
            t = torch.tensor(x)
            ref = torch.clamp(torch.round(torch.tanh(t) * 127), -128, 127).numpy().astype(np.int8)
        np.testing.assert_array_equal(got, ref)

    def test_binary_uses_unquantized_sign(self):
        from pplx_scorer import official_binary
        x = np.array([[-0.001, -0.0, 0.0, 0.004, -2.0, 1.5]], dtype=np.float32)
        got = official_binary(x)
        expected = np.where(x >= 0, np.int8(1), np.int8(-1))
        np.testing.assert_array_equal(got, expected)

    def test_nearzero_counterexample(self):
        """Negative small pooled values round to INT8 0 but native BIN is -1.

        This is the load-bearing distinction: NATIVE BINARY = sign of
        UNQUANTIZED pooled >= 0, NOT sign of rounded INT8.
        """
        from pplx_scorer import official_binary, official_int8
        x = np.array([[-0.001]], dtype=np.float32)
        self.assertEqual(int(official_int8(x)[0, 0]), 0)
        self.assertEqual(int(official_binary(x)[0, 0]), -1)
        # sign(INT8)= +1 (0>=0) would be WRONG here; native is -1
        self.assertNotEqual(int(official_binary(x)[0, 0]),
                            1 if int(official_int8(x)[0, 0]) >= 0 else -1)

    def test_packed_roundtrip_1024(self):
        from pplx_scorer import pack_sign, unpack_sign
        rng = np.random.RandomState(1)
        s = np.where(rng.rand(3, 1024) >= 0.5, np.int8(1), np.int8(-1))
        packed = pack_sign(s)
        self.assertEqual(packed.shape, (3, 128))
        self.assertEqual(packed.dtype, np.uint8)
        np.testing.assert_array_equal(unpack_sign(packed, 1024), s)

    def test_packed_roundtrip_96(self):
        from pplx_scorer import pack_sign, unpack_sign
        rng = np.random.RandomState(2)
        s = np.where(rng.rand(5, 96) >= 0.5, np.int8(1), np.int8(-1))
        packed = pack_sign(s)
        self.assertEqual(packed.shape, (5, 12))
        np.testing.assert_array_equal(unpack_sign(packed, 96), s)

    def test_pack_uses_nonneg_convention(self):
        from pplx_scorer import pack_sign
        s = np.array([[1, -1, 1, -1, 1, -1, 1, -1]], dtype=np.int8)
        packed = pack_sign(s)
        # bits [1,0,1,0,1,0,1,0] -> 0b10101010 = 0xAA
        self.assertEqual(int(packed[0, 0]), 0xAA)


class TestPooling(unittest.TestCase):
    def test_masked_mean_pool(self):
        from pplx_scorer import masked_mean_pool
        hidden = np.array([[[1.0, 2.0], [3.0, 4.0], [100.0, 200.0]]])
        mask = np.array([[1, 1, 0]])
        got = masked_mean_pool(hidden, mask)
        np.testing.assert_allclose(got, np.array([[2.0, 3.0]]))

    def test_masked_mean_pool_allpad_gives_zeros(self):
        from pplx_scorer import masked_mean_pool
        hidden = np.ones((1, 4, 3))
        mask = np.zeros((1, 4), dtype=np.int64)
        got = masked_mean_pool(hidden, mask)
        np.testing.assert_array_equal(got, np.zeros((1, 3)))

    def test_batch_plan_preserves_rows(self):
        from pplx_scorer import plan_batches
        lengths = [10, 3, 7, 3, 20, 1, 15]
        batches = plan_batches(lengths, batch_size=3)
        flat = [i for b in batches for i in b]
        self.assertEqual(sorted(flat), list(range(len(lengths))))
        # within each batch, lengths nondecreasing (length-sorted bucketing)
        for b in batches:
            bl = [lengths[i] for i in b]
            self.assertEqual(bl, sorted(bl))

    def test_text_hash_stable(self):
        from pplx_scorer import text_hash
        self.assertEqual(text_hash("hello"), hashlib.sha256("hello".encode()).hexdigest())
        self.assertNotEqual(text_hash("a"), text_hash("b"))


class TestRanking(unittest.TestCase):
    def test_exact_ten_and_no_duplicates(self):
        from pplx_scorer import rank_top10
        rng = np.random.RandomState(3)
        scores = rng.randn(50)
        top = rank_top10(scores, "RT01", list(range(50)))
        self.assertEqual(len(top), 10)
        self.assertEqual(len(set(top)), 10)

    def test_descending_score_order(self):
        from pplx_scorer import rank_top10
        scores = np.array([1.0, 3.0, 2.0, 3.0])
        top = rank_top10(scores, "RT01", [0, 1, 2, 3])
        # top-2 must be the two 3.0 rows (order between them by hash tiebreak)
        self.assertEqual(set(top[:2]), {1, 3})
        self.assertEqual(top[2], 2)
        self.assertEqual(top[3], 0)

    def test_protocol_tiebreak_hash_then_row(self):
        import hashlib as hl
        from pplx_scorer import rank_top10
        scores = np.array([5.0, 5.0, 5.0])
        rows = [10, 20, 30]
        keys = [(hl.sha256(f"top10-r1|RT02|{r}".encode()).hexdigest(), r) for r in rows]
        expected = [r for _, r in sorted(zip(keys, rows), key=lambda z: (z[0][0], z[0][1]))]
        self.assertEqual(rank_top10(scores, "RT02", rows), expected)

    def test_boundary_tie_exactly_ten(self):
        from pplx_scorer import rank_top10
        scores = np.zeros(20)  # full tie: must still return exactly 10 by hash order
        top = rank_top10(scores, "RT03", list(range(20)))
        self.assertEqual(len(top), 10)
        import hashlib as hl
        keys = sorted(range(20), key=lambda r: (hl.sha256(f"top10-r1|RT03|{r}".encode()).hexdigest(), r))
        self.assertEqual(top, keys[:10])

    def test_rejects_nonfinite(self):
        from pplx_scorer import rank_top10
        with self.assertRaises(ValueError):
            rank_top10(np.array([1.0, np.nan, 0.5]), "RT01", [0, 1, 2])
        with self.assertRaises(ValueError):
            rank_top10(np.array([1.0, np.inf, 0.5]), "RT01", [0, 1, 2])

    def test_no_gold_leakage_in_scorers(self):
        import pplx_scorer as m
        for fn_name in ["cosine_scores_int8", "hamming_scores_bin", "asym_scores_int8xbin",
                        "cosine_scores_float", "rank_top10"]:
            sig = inspect.signature(getattr(m, fn_name))
            self.assertNotIn("gold", sig.parameters, fn_name)
            self.assertNotIn("qid", sig.parameters, fn_name)

    def test_zero_vector_scores_finite(self):
        from pplx_scorer import cosine_scores_int8, hamming_scores_bin, asym_scores_int8xbin
        q = np.zeros((1, 8), dtype=np.int8)
        d = np.zeros((4, 8), dtype=np.int8)
        for fn in (cosine_scores_int8,):
            s = fn(q, d)
            self.assertTrue(np.all(np.isfinite(s)))
        qb = np.ones((1, 8), dtype=np.int8)
        sb = np.where(np.zeros((4, 8)) >= 0, np.int8(1), np.int8(-1))
        db = np.where(np.zeros((4, 8)) >= 0, np.int8(1), np.int8(-1))
        self.assertTrue(np.all(np.isfinite(hamming_scores_bin(qb, sb))))
        self.assertTrue(np.all(np.isfinite(asym_scores_int8xbin(q, db))))


class TestMetrics(unittest.TestCase):
    def test_multigold_metrics(self):
        from pplx_scorer import prf_metrics
        # gold {1,5}; top10 puts 1 at rank1, 5 at rank3
        top10 = [1, 2, 5, 3, 4, 6, 7, 8, 9, 10]
        m = prf_metrics(top10, [1, 5])
        self.assertEqual(m["hit10"], 1)
        self.assertAlmostEqual(m["recall10"], 1.0)
        import math as _math
        _dcg = 1.0 / _math.log2(2) + 1.0 / _math.log2(4)  # ranks 1 and 3
        _idcg = 1.0 / _math.log2(2) + 1.0 / _math.log2(3)  # ideal ranks 1,2
        self.assertAlmostEqual(m["ndcg10"], _dcg / _idcg)

    def test_miss_and_partial(self):
        from pplx_scorer import prf_metrics
        m = prf_metrics([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [99])
        self.assertEqual(m["hit10"], 0)
        self.assertEqual(m["recall10"], 0.0)
        self.assertEqual(m["ndcg10"], 0.0)
        m2 = prf_metrics([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 99])
        self.assertEqual(m2["hit10"], 1)
        self.assertAlmostEqual(m2["recall10"], 0.5)
        import math
        self.assertAlmostEqual(m2["ndcg10"], 1.0 / (1.0 + 1.0 / math.log2(3)))

    def test_single_gold_rank_k(self):
        import math
        from pplx_scorer import prf_metrics
        # gold at rank 2 (index 1) -> ndcg = (1/log2(3)) / 1
        m = prf_metrics([7, 42, 1, 2, 3, 4, 5, 6, 8, 9], [42])
        self.assertAlmostEqual(m["ndcg10"], 1.0 / math.log2(3))


if __name__ == "__main__":
    unittest.main()
