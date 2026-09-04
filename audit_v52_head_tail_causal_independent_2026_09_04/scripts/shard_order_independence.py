"""G8: the LongMemEval aggregate is a float mean over 470 per-question values whose ORDER
is shard-interleaved (shard0 = indices 0,5,10,...; then shard1; ...) rather than 0,1,2,...
The set of values is shard-invariant by construction (tie-break priorities are seeded from a
GLOBAL lexicographic ordinal over all 500 question_ids, not from shard membership), but float
summation is not associative, so "SHARDED_EXACT" is not guaranteed bit-for-bit. This bounds it."""
import numpy as np
rng = np.random.default_rng(12345)
base = np.arange(470)
shard = np.concatenate([base[i::5] for i in range(5)])
v = rng.choice([0.0, 0.25, 1/3, 0.5, 2/3, 0.75, 1.0], 470)
print("representative R@3-like vector:")
print("  monolithic-order mean :", repr(float(np.mean(v[base]))))
print("  shard-order mean      :", repr(float(np.mean(v[shard]))))
print("  |diff|                :", abs(float(np.mean(v[base])) - float(np.mean(v[shard]))))
worst = max(abs(float(np.mean(x[base])) - float(np.mean(x[shard])))
            for x in (rng.random(470) for _ in range(3000)))
print("worst |diff| over 3000 random 470-vectors:", worst)
print("runner tolerance TOL      : 1e-12")
print("decision-band width       : 0.50 (rho_2 bands 0.25 / 0.75)")
