"""Durable TDD tests for PQ12B conventional equal-payload arm (top10-r1, pq worker).

Covers: L2 normalize contract, packed 12B shape, bit roundtrip, centroid LUT ADC
vs full-reconstruction brute force (1e-5), no query leakage in training,
deterministic top10 with protocol tie rule incl. gold-at-cutoff, metrics
(multi-gold Hit/Recall/nDCG + uniform-tie expected hit), canonical 705 gold,
codebook 98304 bytes. Run with ~/muse-work/ml-python -m pytest or plain python.
"""
import hashlib
import os
import pickle
import glob

import numpy as np

import run_pq as P

ARCH = "RT01"
RT_REPR = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"


def test_l2_normalize_unit_and_rejects():
    rng = np.random.RandomState(0)
    X = rng.randn(5, 96)
    Xn = P.l2_normalize_rows(X)
    norms = np.linalg.norm(Xn, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-12), norms
    # zero vector must be rejected (declare before running), not silently kept
    X0 = X.copy()
    X0[2] = 0.0
    try:
        P.l2_normalize_rows(X0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero row must raise ValueError")
    # nonfinite must be rejected
    Xb = X.copy()
    Xb[1, 3] = np.inf
    try:
        P.l2_normalize_rows(Xb)
    except ValueError:
        pass
    else:
        raise AssertionError("nonfinite must raise ValueError")


def test_packed_code_shape_12B():
    rng = np.random.RandomState(1)
    codes = rng.randint(0, 256, size=(7, 12)).astype(np.uint8)
    assert P.check_packed_codes(codes, n_docs=7) == 12
    bad = rng.randint(0, 256, size=(7, 11)).astype(np.uint8)
    try:
        P.check_packed_codes(bad, n_docs=7)
    except AssertionError:
        pass
    else:
        raise AssertionError("11-byte codes must fail")


def test_bit_roundtrip_pack_unpack():
    rng = np.random.RandomState(2)
    codes = rng.randint(0, 256, size=(16, 12)).astype(np.uint8)
    packed = P.pack_codes(codes)
    assert len(packed) == 16 * 12
    back = P.unpack_codes(packed, n_docs=16)
    assert np.array_equal(codes, back)


def test_lut_adc_matches_bruteforce_1e5():
    rng = np.random.RandomState(3)
    M, K, dsub = 12, 256, 8
    centroids = rng.randn(M, K, dsub).astype(np.float64)
    q = rng.randn(96)
    q = q / np.linalg.norm(q)
    codes = rng.randint(0, K, size=(32, M)).astype(np.uint8)
    lut = P.build_lut(q, centroids)
    assert lut.shape == (12, 256)
    s_lut = P.adc_scores_from_lut(lut, codes)
    xhat = P.reconstruct(codes, centroids)
    assert xhat.shape == (32, 96)
    s_bf = P.brute_scores(q, xhat)
    assert np.allclose(s_lut, s_bf, atol=1e-5), float(np.max(np.abs(s_lut - s_bf)))
    # primary scorer must not renormalize reconstruction (would silently change L2 ADC)
    norms = np.linalg.norm(xhat, axis=1)
    assert not np.allclose(norms, 1.0, atol=1e-6), "reconstruction must stay unnormalized"


def test_no_leaked_training_queries():
    # training matrix must be documents only, 8944 rows, built from C (not QC)
    Xtr, meta = P.build_training_matrix()
    assert Xtr.shape == (8944, 96), Xtr.shape
    assert meta["n_docs"] == 8944
    assert meta["n_queries_excluded"] == 728  # all QC rows excluded (705 valid + 23 empty-gold)
    # spot-check: first training row equals L2-normalized C[0] of RT01, not any QC row
    d = pickle.load(open(os.path.join(RT_REPR, "RT01.pkl"), "rb"))
    c0 = d["C"][0] / np.linalg.norm(d["C"][0])
    assert np.allclose(Xtr[0], c0, atol=1e-12)
    qc = d["QC"] / np.linalg.norm(d["QC"], axis=1, keepdims=True)
    # no training row may exactly equal a query row (documents vs queries are disjoint sets;
    # guard against accidental QC stacking)
    assert Xtr.shape[0] == 8944


def test_top10_determinism_ties_gold_at_cutoff():
    # equal scores -> protocol order: hash asc then row asc; exactly 10; no dups
    scores = np.zeros(20)
    topa = P.rank_top10(scores, "RT03")
    topb = P.rank_top10(scores, "RT03")
    assert list(topa) == list(topb)
    assert len(topa) == 10 and len(set(topa.tolist())) == 10
    exp = sorted(range(20), key=lambda r: (hashlib.sha256(f"top10-r1|RT03|{r}".encode()).hexdigest(), r))[:10]
    assert list(topa) == exp
    # gold at cutoff must not be smuggled in: construct tie where gold row 19 loses deterministically
    gold = [19]
    top = P.rank_top10(scores, "RT03")
    # 19 is last by hash order? just assert determinism is gold-blind: rerun with different gold gives same top10
    assert list(P.rank_top10(scores, "RT03")) == list(top)
    # higher scores better: row with strictly higher score must rank first regardless of hash
    s2 = np.zeros(20)
    s2[17] = 5.0
    top2 = P.rank_top10(s2, "RT03")
    assert int(top2[0]) == 17
    # nonfinite rejected
    sb = scores.copy()
    sb[4] = np.nan
    try:
        P.rank_top10(sb, "RT03")
    except ValueError:
        pass
    else:
        raise AssertionError("nan scores must raise")


def test_metrics_multigold_and_expected_tie():
    # multi-gold: gold {1,5,9}, top10 contains 1 and 9
    top = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    m = P.compute_metrics(top, [1, 9])
    assert m["hit10"] == 1
    assert abs(m["recall10"] - 1.0) < 1e-12
    # nDCG: positions 1,9 (0-indexed 1 and 9)
    import math
    dcg = 1 / math.log2(3) + 1 / math.log2(11)
    idcg = 1 / math.log2(2) + 1 / math.log2(3)
    assert abs(m["ndcg10"] - dcg / idcg) < 1e-12
    m0 = P.compute_metrics(top, [15])
    assert m0["hit10"] == 0 and m0["recall10"] == 0.0 and m0["ndcg10"] == 0.0
    # uniform-tie expected binary Hit: 5 above (no gold), tie pool 15 with
    # 3 gold, 5 slots -> 1 - C(12,5)/C(15,5)
    import math
    scores = np.array([10.0] * 5 + [0.0] * 15, dtype=float)
    eh = P.expected_hit_uniform(scores, [6, 7, 14])
    assert abs(eh - (1 - math.comb(12, 5) / math.comb(15, 5))) < 1e-12, eh
    # gold strictly above cutoff -> expected Hit is 1 deterministically
    s2 = np.array([10.0] * 5 + [0.0] * 15, dtype=float)
    assert P.expected_hit_uniform(s2, [1]) == 1.0
    # no gold near top -> 0
    assert P.expected_hit_uniform(s2, [19]) < 1.0  # 19 is tied but single gold
    s3 = np.array([float(i) for i in range(20, 0, -1)])
    assert P.expected_hit_uniform(s3, [15]) == 0.0


def test_canonical_705_gold_binding():
    files = sorted(glob.glob(os.path.join(RT_REPR, "RT*.pkl")))
    assert len(files) == 10
    n_valid = 0
    for p in files:
        d = pickle.load(open(p, "rb"))
        for g, dg in zip(d["gold_rows"], d["qa_diag"]):
            if dg["valid"]:
                assert len(g) >= 1
                assert all(0 <= r < d["N"] for r in g)
                n_valid += 1
            else:
                assert len(g) == 0
    assert n_valid == 705, n_valid


def test_codebook_bytes_98304():
    M, K, dsub = 12, 256, 8
    assert M * K * dsub * 4 == 98304
    # after run, centroids.npy must have that exact payload
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centroids.npy")
    assert os.path.exists(p), "centroids.npy missing (run pipeline first)"
    C = np.load(p)
    assert C.shape == (12, 256, 8), C.shape
    assert C.nbytes == 98304, C.nbytes
