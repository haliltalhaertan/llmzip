# Two open items closed, with their evidence

Additive to `f1149831`. Closes two items this session had assigned to itself and
then carried on a list for three days instead of doing.

## 1. The SIMHASH positive control is NOT sourceless — it is derivable

The twelve-byte preregistration declares
`SIMHASH96 LongMemEval mean over 5 seeds == 0.38271667`.
That literal string occurs nowhere else in the repository, which is why two
reviewers independently graded it as lacking provenance. Both were right about the
string and wrong about the provenance: **the value is derivable from a committed,
independently audited artifact.**

`audit_v52_t4c3/AUDIT_REPORT.md` on `main`, sha256
`8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238`, lines 88–93,
publishes the five per-seed full-Haar values for rotation seeds `43001..43005`:

```
43001  36.1395390%
43002  39.1393617%
43003  37.9320922%
43004  38.0195035%
43005  40.1278369%
```

Their mean is `0.38271666660000003`, which rounded to eight decimal places is
exactly `0.38271667`.

**The fix is therefore not to find a source but to cite the derivation.** The
preregistration should carry the artifact, its digest, the seed set, and the
rounding rule, instead of a bare literal. A hand-typed decimal with a derivation
behind it is still a hand-typed decimal until the derivation is written down.

## 2. C4's interpretation half — the operative claim is now functionally verified

The claim was that RaBitQ's fixed 8-byte overhead carries per-vector scalars its
estimator depends on, and is therefore not removable without the method ceasing to
be RaBitQ. Both the commissioned auditor and this session graded that
`UNVERIFIABLE`, because neither read the C++ source.

It can be settled functionally instead. Encode three vectors whose norms differ by
two orders of magnitude, then decode:

```
input norms    1.029      9.144    114.544
code_size      20 B  (12 B of sign bits + 8 B)
decoded norms  1.268     11.656    143.054
```

The decoded magnitudes track the input scale. **A sign-only code cannot do this** —
every decoded vector would have the same norm. So the extra bytes demonstrably
carry per-vector scale that reconstruction consumes.

**What this does and does not establish.** It establishes the operative half: the
8 bytes are not padding, and dropping them would lose magnitude information the
decoder uses. It does **not** establish the theoretical attribution — that these
are specifically the correction terms of RaBitQ's unbiased estimator and its error
bound. That still needs the paper or the C++ source, and remains ungraded.

## Reproduce

```bash
pip install faiss-cpu==1.15.0
python3 - <<'PY'
import faiss, numpy as np
rng = np.random.default_rng(0); d = 96
q = faiss.RaBitQuantizer(d); q.train(rng.standard_normal((2000, d)).astype('float32'))
x = (rng.standard_normal((3, d)) * np.array([[0.1], [1.0], [10.0]])).astype('float32')
rec = q.decode(q.compute_codes(x))
print(np.linalg.norm(x, axis=1), np.linalg.norm(rec, axis=1), q.code_size)
PY
```

Task 4F1 untouched: SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
FORBIDDEN. No corpus read, no gold read, no benchmark retrieval computed.
