"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Durable counterexample: producer expected_hit() is expected-Recall, not expected-Hit.

RED: producer data/run_lexical.py::expected_hit fails multi-gold boundary-tie case.
GREEN: audit correct_expected_hit passes (brute-force enumeration oracle).
Mutation guard: wrong variants (fractional recall, s/B shortcut) must fail.

Run: $HOME/muse-work/ml-python test_expected_hit.py
     $HOME/muse-work/ml-python -m pytest test_expected_hit.py -v
Stdlib only.
"""
import importlib.util
import itertools
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRODUCER = os.path.join(HERE, "..", "data", "run_lexical.py")


def _load_producer_expected_hit():
    spec = importlib.util.spec_from_file_location("producer_lexical", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.expected_hit


def correct_expected_hit(scores, gold, k=10):
    """Independent correct any-gold probability under uniform within-bucket tiebreak."""
    s = [float(x) if math.isfinite(float(x)) else float("-inf") for x in scores]
    gset = set(int(g) for g in gold)
    assert gset
    buckets = {}
    for i, v in enumerate(s):
        buckets.setdefault(v, []).append(i)
    better = 0
    for lv in sorted(buckets.keys(), reverse=True):
        idx = buckets[lv]
        B = len(idx)
        if better >= k:
            break
        gb = sum(1 for i in idx if i in gset)
        if better + B <= k:
            if gb > 0:
                return 1.0
            better += B
        else:
            take = int(k - better)
            if gb == 0:
                return 0.0
            denom = math.comb(B, take)
            numer = math.comb(B - gb, take) if (B - gb) >= take else 0
            return float(1.0 - numer / denom)
    return 0.0


def brute_expected_hit(scores, gold, k=10):
    """Independent oracle: enumerate product of per-bucket permutations."""
    s = list(scores)
    gset = set(int(g) for g in gold)
    uniq = sorted(set(s), reverse=True)
    buckets = [[i for i in range(len(s)) if s[i] == lv] for lv in uniq]
    perms = [list(itertools.permutations(b)) for b in buckets]
    total = 0
    hits = 0
    for combo in itertools.product(*perms):
        order = [x for b in combo for x in b][:k]
        total += 1
        if any(int(x) in gset for x in order):
            hits += 1
    return hits / total


# Fixed counterexample: N=15, K=10.
# 8 docs score 2.0 (above), 5 docs score 1.0 (boundary, 2 gold), 2 docs score 0.0.
CE_SCORES = [2.0] * 8 + [1.0] * 5 + [0.0] * 2
CE_GOLD = [8, 9]  # both in boundary bucket
CE_K = 10
# better=8, B=5, G=2, s=2 -> 1 - C(3,2)/C(5,2) = 1 - 3/10 = 0.7
CE_CORRECT = 0.7
# producer computes (s*G/B)/|gold| = (2*2/5)/2 = 0.4
CE_PRODUCER_WRONG = 0.4


def test_counterexample_red_on_producer():
    prod = _load_producer_expected_hit()
    got = float(prod(CE_SCORES, CE_GOLD))
    assert abs(got - CE_PRODUCER_WRONG) < 1e-12, (got, CE_PRODUCER_WRONG)
    # producer does NOT equal the true any-gold probability
    assert abs(got - CE_CORRECT) > 0.2, f"producer unexpectedly correct: {got}"


def test_counterexample_green_on_correct():
    got = correct_expected_hit(CE_SCORES, CE_GOLD, k=CE_K)
    assert abs(got - CE_CORRECT) < 1e-12, (got, CE_CORRECT)
    oracle = brute_expected_hit(CE_SCORES, CE_GOLD, k=CE_K)
    assert abs(got - oracle) < 1e-9, (got, oracle)


def test_correct_matches_bruteforce_random():
    import random
    rng = random.Random(20260915)
    for _ in range(20):
        N = 6
        K = 3
        scores = [rng.choice([0.0, 1.0, 2.0]) for _ in range(N)]
        gold = sorted(rng.sample(range(N), 2))
        got = correct_expected_hit(scores, gold, k=K)
        exp = brute_expected_hit(scores, gold, k=K)
        assert abs(got - exp) < 1e-9, (scores, gold, got, exp)


def test_edge_cases():
    # gold strictly above cutoff -> 1.0
    assert correct_expected_hit([5.0, 5.0, 1.0, 1.0, 1.0], [0], k=2) == 1.0
    assert correct_expected_hit([5.0, 5.0, 1.0, 1.0, 1.0], [0, 3], k=2) == 1.0
    # no gold in boundary and none above -> 0.0
    assert correct_expected_hit([5.0, 5.0, 1.0, 1.0, 1.0], [3], k=2) == 0.0
    # single gold in boundary: s/B
    assert abs(correct_expected_hit([5.0, 1.0, 1.0, 1.0], [1], k=2) - 1 / 3) < 1e-12
    # pigeonhole: B-G < s -> must hit -> 1.0
    assert correct_expected_hit([1.0, 1.0, 1.0], [0, 1], k=2) == 1.0


def test_mutation_guard_fractional_recall_fails():
    """A mutated formula returning expected-recall must NOT pass the counterexample."""
    def mutated(scores, gold, k=10):
        s = list(scores)
        gset = set(int(g) for g in gold)
        buckets = {}
        for i, v in enumerate(s):
            buckets.setdefault(v, []).append(i)
        better, exp = 0, 0.0
        for lv in sorted(buckets.keys(), reverse=True):
            idx = buckets[lv]
            if better >= k:
                break
            gb = sum(1 for i in idx if i in gset)
            if better + len(idx) <= k:
                exp += gb
            else:
                exp += (k - better) * gb / len(idx)
                break
            better += len(idx)
        return exp / len(gset)
    assert abs(mutated(CE_SCORES, CE_GOLD) - CE_CORRECT) > 0.2


def test_mutation_guard_single_slot_shortcut_fails():
    """Mutant using G/B instead of hypergeometric must fail when s>1."""
    def mutated2(scores, gold, k=10):
        s = list(scores)
        gset = set(int(g) for g in gold)
        buckets = {}
        for i, v in enumerate(s):
            buckets.setdefault(v, []).append(i)
        better = 0
        for lv in sorted(buckets.keys(), reverse=True):
            idx = buckets[lv]
            B = len(idx)
            if better >= k:
                break
            gb = sum(1 for i in idx if i in gset)
            if better + B <= k:
                if gb > 0:
                    return 1.0
                better += B
            else:
                if gb == 0:
                    return 0.0
                return gb / B  # WRONG when s != 1
        return 0.0
    # G/B = 2/5 = 0.4, correct 0.7
    assert abs(mutated2(CE_SCORES, CE_GOLD) - CE_CORRECT) > 0.2


if __name__ == "__main__":
    test_counterexample_red_on_producer()
    print("RED confirmed: producer returns fractional recall (0.4), not true Hit prob (0.7)")
    test_counterexample_green_on_correct()
    print("GREEN: correct_expected_hit == 0.7 == brute-force oracle")
    test_correct_matches_bruteforce_random()
    print("GREEN: 20 random brute-force trials match")
    test_edge_cases()
    print("GREEN: edge cases pass")
    test_mutation_guard_fractional_recall_fails()
    test_mutation_guard_single_slot_shortcut_fails()
    print("GREEN: mutation guards catch wrong variants")
    print("ALL GREEN (test_expected_hit.py): 6 checks passed")
