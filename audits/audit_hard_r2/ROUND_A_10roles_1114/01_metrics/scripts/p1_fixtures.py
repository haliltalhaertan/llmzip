"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
01_metrics probe P1 — harmless numeric fixtures (stdlib + numpy only).
Own code; source files only read. Tests:
 F1 det tie contract: exact-10 at boundary ties, gold-unaware, hash-seed stable.
 F2 exact expected-hit (any-gold) vs producer formula (expected recall) on CE fixture.
 F3 Hit@10 vs FR@3 divergence on multi-gold fixture.
 F4 gate mismatch: point-estimate C1 (code impl) vs documented C1 (CI + both benchmarks).
"""
import hashlib
import itertools
import json
import math
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                   "p1_fixtures.json")
TIE_SALT = "top10-r1"


def det_top10(scores, archive_id, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{TIE_SALT}|{archive_id}|{r}".encode()).hexdigest()
          for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])


def correct_expected_hit(scores, gold, k=10):
    s = [float(x) if math.isfinite(float(x)) else float("-inf") for x in scores]
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
            take = int(k - better)
            if gb == 0:
                return 0.0
            denom = math.comb(B, take)
            numer = math.comb(B - gb, take) if (B - gb) >= take else 0
            return float(1.0 - numer / denom)
    return 0.0


def producer_expected_hit(scores, gold, k=10):
    # verbatim formula of data/run_lexical.py::expected_hit (returns exp/|gold|)
    s = [x if math.isfinite(x) else float("-inf") for x in scores]
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


def brute_expected_hit(scores, gold, k=10):
    s = list(scores)
    gset = set(int(g) for g in gold)
    uniq = sorted(set(s), reverse=True)
    buckets = [[i for i in range(len(s)) if s[i] == lv] for lv in uniq]
    total = hits = 0
    for combo in itertools.product(*[list(itertools.permutations(b)) for b in buckets]):
        order = [x for b in combo for x in b][:k]
        total += 1
        if any(int(x) in gset for x in order):
            hits += 1
    return hits / total


res = {}

# F1: boundary tie — 12 docs share the cutoff score, k=10 must return exactly 10,
# gold-unaware (re-run with gold elsewhere gives identical top10), stable across runs.
scores = [9.0, 8.0] + [5.0] * 12 + [1.0] * 6  # N=20
t1 = det_top10(scores, "RT99", 10).tolist()
t2 = det_top10(scores, "RT99", 10).tolist()
t_other_arch = det_top10(scores, "RT07", 10).tolist()
res["F1_exactly_ten_at_boundary"] = {
    "n": 20, "k": 10, "len_top": len(t1),
    "all_cutoff_tied": bool(all(scores[r] == 5.0 for r in t1[2:])),
    "deterministic_repeat": t1 == t2,
    "archive_salt_matters": t1 != t_other_arch,
    "top": t1,
}

# F2: CE fixture N=15 K=10, 8 above / 5 boundary w/ 2 gold / 2 below.
CE_SCORES = [2.0] * 8 + [1.0] * 5 + [0.0] * 2
CE_GOLD = [8, 9]
ce_correct = correct_expected_hit(CE_SCORES, CE_GOLD, k=10)
ce_producer = producer_expected_hit(CE_SCORES, CE_GOLD, k=10)
ce_brute = brute_expected_hit(CE_SCORES, CE_GOLD, k=10)
res["F2_expected_hit_vs_producer"] = {
    "correct_any_gold": ce_correct, "brute_oracle": ce_brute,
    "producer_value": ce_producer,
    "producer_equals_expected_recall": abs(ce_producer - (2 * 2 / 5) / 2) < 1e-12,
    "verdict": "producer formula returns expected RECALL (0.4), true expected HIT is 0.7",
}
# single-gold sanity: both coincide at s/B
sg = correct_expected_hit([5.0, 1.0, 1.0, 1.0], [1], k=2)
sgp = producer_expected_hit([5.0, 1.0, 1.0, 1.0], [1], k=2)
res["F2_single_gold_coincide"] = {"correct": sg, "producer": sgp}

# F3: multi-gold query, gold split across ranks 1 and 9 of top10.
top = [4, 11, 12, 13, 14, 15, 16, 17, 7, 19]
gold = {4, 5, 6, 7}  # 2 of 4 in top10 (ranks 1,9), 2 missed
hit = 1.0 if (set(top) & gold) else 0.0
fr3 = len(set(top[:3]) & gold) / len(gold)
res["F3_hit_vs_fr3_diverge"] = {
    "hit10": hit, "fr3": fr3,
    "verdict": "same ranking reads 100% on Hit@10 but 25% on FR@3",
}

# F4: synthetic paired diff, 10 clusters, point +2.0pp but CI includes 0.
# Between-cluster heterogeneity (half +0.19, half -0.15) keeps the point at the
# gate while the 10-cluster resample distribution straddles zero.
rng = np.random.default_rng(7)
diffs, cl = [], {}
i = 0
for c in range(10):
    n = 70
    mu = 0.21 if c < 5 else -0.15
    v = rng.normal(mu, 0.02, n)
    for x in v:
        diffs.append(x)
        cl.setdefault(f"C{c}", []).append(i)
        i += 1
diff = np.asarray(diffs)
cls = [np.asarray(v) for v in cl.values()]
est = 100 * diff.mean()
B = 20000
r2 = np.random.default_rng(20260916)
outs = np.empty(B)
for t in range(B):
    pick = r2.integers(0, len(cls), len(cls))
    outs[t] = diff[np.concatenate([cls[j] for j in pick])].mean()
lo, hi = (float(np.percentile(outs, 2.5)) * 100, float(np.percentile(outs, 97.5)) * 100)
code_gate = bool(est >= 2.0)  # decision_tests.py T1 impl: point only, one benchmark
doc_gate = bool(est >= 2.0 and (lo > 0 or hi < 0))  # documented: +CI (both-benchmark part not testable here)
res["F4_gate_mismatch_demo"] = {
    "est_pp": est, "ci_lo": lo, "ci_hi": hi,
    "code_impl_C1_point_only": code_gate,
    "documented_C1_point_plus_CI": doc_gate,
    "verdict": "point passes while CI-including-zero fails" if (code_gate and not doc_gate)
    else "fixture did not separate (see numbers)",
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
