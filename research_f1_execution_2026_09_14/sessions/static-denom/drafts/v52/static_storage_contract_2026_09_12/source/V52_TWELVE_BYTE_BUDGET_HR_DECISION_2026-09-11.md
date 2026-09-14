# V52 — Head Researcher Decision: what "twelve bytes" means

**Date:** 2026-09-11
**Authority:** Head Researcher (repository owner)
**Prepared by:** Continuity Lead (prepares only; does not seal, does not self-approve)
**Binding scope:** the twelve-byte baseline comparison track. Task 4F1 is a separate
BEAM line and nothing here touches it.

Relayed as chat text and recorded as such — **not** as a Head-Researcher-signed
artifact — the same standing as the 2026-09-07 authorization at L-054 and the
2026-09-10 dependency decision at L-086.

---

## The decision

> **"Twelve bytes" means at most twelve MARGINAL PERSISTENT BYTES PER VECTOR.**

### What counts inside the cap

Everything stored **per vector**: the code, any norm or scale value, any correction
scalar, any per-vector metadata. If the index writes it once for every stored
memory, it is inside the twelve bytes.

### What sits outside the cap

Shared model state — codebooks, the OPQ rotation matrix, centroid tables — is
**not** counted against the marginal cap. It is **reported separately, in bytes,
and never omitted.**

### What the preregistration must now say about itself

The preregistration will state explicitly that it tests **archive-local fitting**.
Where each archive carries its own rotation, codebook or centroid state, that cost
is shown **per archive**, separately.

A cross-archive or globally shared codebook is a **different deployment
configuration**. It is not tested here and its properties may not be presented as
a result of this experiment.

---

## Direct consequences, from the measurements at `f1149831`

| arm | marginal B/vector | status under the cap |
|---|---|---|
| `SIGN96` | 12 | **stays** |
| `RABITQ96` (d=96, 1 bit) | **20** | **not a matched comparator** |
| `EXT_RABITQ96` (d=96, 2 bit) | **44** | **cannot enter the twelve-byte race** |
| `PQ96` m=12 × 8 bit | 12 | fits the marginal cap |
| `TOP32_RABITQ32` (d=32, 1 bit) | 12 | natural candidate |

**The primary contrast `SIGN96 − RABITQ96` is cancelled as written.** RaBitQ must
enter with a configuration that genuinely satisfies `≤ 12 B/vector`; on the present
measurements `d = 32` at one bit is the natural candidate.

For `OPQ_PQ96` the rotation and codebook state is reported separately, and where
fitting is archive-local **the very large effective cost on small archives is not
to be hidden**.

---

## Mandatory pre-seal assertion

The runner asserts, before computing anything:

```
measured_persistent_bytes_per_vector <= 12
```

and **aborts** when the library's actual `code_size` or serialization output
disagrees with the declaration. This exists to catch exactly the class of failure
already measured: assigning `nb_bits` after construction is silently ignored, which
would run the extended arm as an undetected duplicate of the one-bit arm.

## Reporting

Two numbers are always carried:

```
marginal_bytes_per_vector
shared_state_bytes_per_archive
```

and optionally a third, derived:

```
effective_bytes_per_vector
  = marginal_bytes_per_vector + shared_state_bytes_per_archive / N_archive
```

**The first number alone decides whether a comparison is "twelve-byte matched."**

---

## Bound in the same revision, so the bytes change once

- primary metric **`Recall@100`**
- secondary **`Recall@3 / 10 / 1000`**
- **≥ 20 seeds** for Haar and within-96 arms
- paired bootstrap, **10,000** replicates
- gold-evidence **cardinality strata**
- the actual **`code_size` abort** above
- **archive-local state accounting** as defined above

## Two closures accepted, with their epistemic limits preserved

- **SIMHASH `0.38271667`** is accepted as a control, but **not as a bare literal**.
  It is bound as *derived from the `43001..43005` seed panel published in
  `audit_v52_t4c3/AUDIT_REPORT.md` (sha256 `8f6b3105…`), rounded to eight decimal
  places.* The artifact, its digest, the seed set and the rounding rule travel with
  it.
- **The RaBitQ 8-byte overhead** is accepted as carrying scale information that
  reconstruction consumes — shown functionally by decode. The stronger reading,
  that these are specifically the correction terms of the unbiased estimator and
  its error bound, **is not to be written until a separate source supports it.**

---

## What this decision does NOT do

- It authorizes no execution, seal, pilot or run on any track.
- It grants no retrieval-quality outcome access and does not set or request
  `V52_T4F1_AUTH_HMAC_KEY_HEX`.
- It disposes of nothing else: G-2's content, L-081's seven findings and nine named
  test gaps, and integration obligations 4 and 5 remain open.
- It does not modify any sealed byte, accepted audit, or frozen result.

Task 4F1 remains **SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN**. This line is
retained deliberately: this decision is scoped away from Task 4F1, and scoping away
relaxes no Task 4F1 prohibition.
