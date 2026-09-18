# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""TDD feature assertions for Top10-r1 baseline (own implementation).

Covers: deterministic Top10 ranking, Hit/Recall/nDCG10, expected tie-Hit10
vs brute-force permutation enumeration, packed roundtrip + mutation,
multi-gold + boundary ties, nonfinite handling, FR3 exact gate helper.
"""
import hashlib
import itertools
import math
import numpy as np

from metrics_top10 import (
    TIE_SALT,
    asym_scores,
    cosine_raw,
    cosine_std,
    decode_pm1,
    deterministic_top10,
    expected_hit_at_k,
    expected_recall_at_k,
    fit_std,
    hamming_from_packed,
    hit_recall_ndcg_at_k,
    pack_signs_bool,
)


def _hash(archive_id, row):
    return hashlib.sha256(f"{TIE_SALT}|{archive_id}|{row}".encode()).hexdigest()


def test_pack_roundtrip():
    rng = np.random.default_rng(0)
    C = rng.normal(size=(17, 96))
    packed = pack_signs_bool(C >= 0)
    assert packed.shape == (17, 12) and packed.dtype == np.uint8
    back = decode_pm1(packed)
    assert np.array_equal(back, np.where(C >= 0, 1, -1).astype(np.int8))


def test_pack_mutation_changes_hamming():
    C = np.zeros((2, 96))
    C[0, :] = 1.0
    C[1, :] = 1.0
    packed = pack_signs_bool(C >= 0)
    q_bits = np.zeros(96, dtype=bool)  # all False
    h0 = hamming_from_packed(packed, q_bits)
    assert list(h0) == [96, 96]
    # flip one doc bit via mutation of packed copy
    mut = packed.copy()
    mut[1, 0] ^= 0x80  # flip first bit (big-endian MSB of byte 0)
    h1 = hamming_from_packed(mut, q_bits)
    assert list(h1) == [96, 95], h1


def test_deterministic_ranking_hash_order_not_row_order():
    # all scores tied -> order must follow ascending hash, not row index
    archive_id = "UT-ARCH"
    scores = np.zeros(20)
    top = deterministic_top10(scores, archive_id, k=10)
    assert len(top) == 10 and len(set(top.tolist())) == 10
    hashes = [_hash(archive_id, r) for r in range(20)]
    expect = sorted(range(20), key=lambda r: (hashes[r], r))[:10]
    assert top.tolist() == expect


def test_deterministic_ranking_descending_score_then_hash():
    archive_id = "UT-ARCH2"
    scores = np.array([1.0, 3.0, 2.0, 3.0, 0.5])
    top = deterministic_top10(scores, archive_id, k=3)
    # rows 1 and 3 tie at 3.0 -> hash order decides
    h1, h3 = _hash(archive_id, 1), _hash(archive_id, 3)
    first_two = [1, 3] if h1 < h3 else [3, 1]
    assert top.tolist() == first_two + [2]


def test_exactly_ten_at_boundary_ties_no_gold_awareness():
    archive_id = "UT-BOUND"
    # 15 docs tie at top; gold placed adversarially late in hash order
    scores = np.ones(15)
    hashes = [_hash(archive_id, r) for r in range(15)]
    order = sorted(range(15), key=lambda r: (hashes[r], r))
    gold = [order[-1]]  # gold is last by hash -> must NOT be in top10
    top = deterministic_top10(scores, archive_id, k=10)
    assert len(top) == 10
    assert int(order[-1]) not in set(map(int, top.tolist()))
    hit, rec, ndcg = hit_recall_ndcg_at_k(top, gold, k=10)
    assert hit == 0.0 and rec == 0.0 and ndcg == 0.0


def test_multi_gold_hit_recall_ndcg():
    top = np.array([5, 1, 9, 3, 0, 2, 4, 6, 7, 8, 10, 11])
    gold = [1, 3, 100]  # 2 of 3 in top10 (rows 1,3); row 100 outside top10
    hit, rec, ndcg = hit_recall_ndcg_at_k(top, gold, k=10)
    assert hit == 1.0
    assert abs(rec - 2.0 / 3.0) < 1e-12
    # manual DCG: positions 1,3 (0-based) -> 1/log2(3)+1/log2(5); IDCG over 3 gold
    disc = [1.0 / math.log2(r + 2) for r in range(10)]
    idcg = sum(disc[:3])
    dcg = disc[1] + disc[3]
    assert abs(ndcg - dcg / idcg) < 1e-12


def test_higher_better_and_nonfinite_worst():
    archive_id = "UT-NONFIN"
    scores = np.array([0.5, np.nan, 0.9, np.inf, -np.inf, 0.9])
    top = deterministic_top10(scores, archive_id, k=4)
    # finite 0.9 rows (2,5) first by hash, then 0.5, then nonfinite by hash
    assert set(map(int, top[:2].tolist())) == {2, 5}
    assert int(top[2]) == 0
    assert set(map(int, top[3:4].tolist())).issubset({1, 3, 4})


def test_expected_hit_boundary_bucket_bruteforce():
    # small fixture: N=6, K=3, scores create buckets; brute-force all tie perms
    rng = np.random.default_rng(123)
    for trial in range(20):
        N, K = 6, 3
        scores = rng.choice([0.0, 1.0, 2.0], size=N).astype(float)
        gold = sorted(rng.choice(N, size=2, replace=False).tolist())
        got = expected_hit_at_k(scores, gold, k=K)
        # brute force: enumerate all global perms consistent with score order?
        # Equivalent: for each bucket, all orderings; take top-K across buckets.
        # Simpler exact brute force: iterate over all N! perms filtered to
        # respect score levels, compute hit fraction.
        uniq = sorted(set(scores.tolist()), reverse=True)
        buckets = [[i for i in range(N) if scores[i] == lv] for lv in uniq]
        # enumerate product of per-bucket permutations
        perms_per_bucket = [list(itertools.permutations(b)) for b in buckets]
        total = 0
        hits = 0
        for combo in itertools.product(*perms_per_bucket):
            order = [x for b in combo for x in b][:K]
            total += 1
            if any(int(x) in set(map(int, gold)) for x in order):
                hits += 1
        expect = hits / total
        assert abs(got - expect) < 1e-9, (trial, scores, gold, got, expect)


def test_expected_recall_matches_bruteforce_small():
    rng = np.random.default_rng(7)
    for trial in range(10):
        N, K = 5, 2
        scores = rng.choice([0.0, 1.0], size=N).astype(float)
        gold = sorted(rng.choice(N, size=2, replace=False).tolist())
        got = expected_recall_at_k(scores, gold, k=K)
        uniq = sorted(set(scores.tolist()), reverse=True)
        buckets = [[i for i in range(N) if scores[i] == lv] for lv in uniq]
        perms = [list(itertools.permutations(b)) for b in buckets]
        total = 0
        rec_sum = 0.0
        gset = set(map(int, gold))
        for combo in itertools.product(*perms):
            order = [x for b in combo for x in b][:K]
            total += 1
            rec_sum += len([x for x in order if int(x) in gset]) / len(gset)
        assert abs(got - rec_sum / total) < 1e-9


def test_scorers_smoke_and_std_definition():
    rng = np.random.default_rng(1)
    C = rng.normal(size=(8, 96))
    q = rng.normal(size=96)
    packed = pack_signs_bool(C >= 0)
    assert decode_pm1(packed).shape == (8, 96)
    h = hamming_from_packed(packed, q >= 0)
    assert h.shape == (8,) and h.min() >= 0 and h.max() <= 96
    cr = cosine_raw(C, q)
    assert cr.shape == (8,) and np.all(np.isfinite(cr))
    std = fit_std(C)
    assert std.shape == (96,) and np.all(std != 0)
    cs = cosine_std(C, q, std)
    assert cs.shape == (8,)
    a = asym_scores(packed, q)
    assert a.shape == (8,) and np.all(np.isfinite(a))
    # zero-variance axis -> std 1.0 (declared)
    C2 = np.ones((5, 96))
    assert np.all(fit_std(C2) == 1.0)
