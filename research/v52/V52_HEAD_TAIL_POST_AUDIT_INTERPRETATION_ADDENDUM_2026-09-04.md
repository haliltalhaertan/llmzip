# V52 Head32/Tail64 Post-Audit Interpretation Addendum

Date: 2026-09-04
Status: `[BINDING INTERPRETATION NARROWING — PRE-LOCALIZATION]`
Research branch: `research/v52-sign-mechanism-locomo-2026-09-04`

## 1. Why this addendum exists

The cold-start independent audit of the Head32/Tail64 causal stage returned:

`AUDIT PASS WITH CAVEATS`

Audit branch:
`audit/v52-head-tail-causal-independent-2026-09-04`

Audit commit:
`f939db0238f1c348c37851aeda9958700bb06d53`

Audited research target:
`7799502bc3a157f874b4b1aa76f803ec2bf6432f`

Audit report SHA-256:
`e804936ed59ab1005d2087d171969a2d19fd437f498d29ad00b24543d1094851`

The audit established the preregistration ancestry, source identities, primary numerical reproduction on both frozen datasets, shard semantics, and the preregistered Head32/Tail64 band verdict. The auditor also supplied a matched-size random 32/64 partition control on LoCoMo and found that a random partition retained essentially none of the Native-vs-Full-Haar advantage, while the spectral Head32/Tail64 partition retained most of it.

This addendum is not a rewrite of the previously frozen checkpoint. It records the audit-mandated interpretation narrowing that all subsequent work must inherit.

## 2. Binding narrowing A — statistical precision

The previous checkpoint printed `rho_2` to more significant digits than the five-Haar-draw design can scientifically support.

Subsequent prose must report the Head/Tail magnitude approximately as:

- LoCoMo: `rho_2 ≈ 0.107 ± 0.047` (five-draw standard error conditional on the frozen Full-Haar denominator)
- LongMemEval: `rho_2 ≈ 0.157 ± 0.025` (same convention)

Machine-readable result files may retain full floating-point values for deterministic recomputation. Narrative claims must not treat those extra digits as measurement precision.

The uncertainty above does **not** include sampling uncertainty in the inherited frozen Full-Haar denominator. That denominator uncertainty is not identified by the Head/Tail package and therefore the displayed standard errors are conditional, not total.

## 3. Binding narrowing B — LoCoMo seed 56001 sign inversion

LoCoMo seed `56001` produced Head32/Tail64 R@3 above Native:

- Native R@3: `0.23654714666441054`
- seed 56001 Head/Tail R@3: `0.24319099434005997`
- per-seed `rho_2 ≈ -0.0672`

Thus the estimated LoCoMo intervention loss changes sign on one frozen draw. This is a required disclosure in any subsequent summary of the Head/Tail magnitude. It does not overturn the preregistered band verdict: every frozen seed still satisfied `rho_2 <= 0.25`.

## 4. Binding narrowing C — dataset-level replication wording

The phrase `cross-benchmark` must not be used to imply independent methodological replication.

The licensed wording is:

> a consistent finding across two frozen datasets evaluated under one shared representation recipe, estimator, Hamming retrieval rule, causal estimand, and mostly shared codebase.

The datasets differ, but the evaluation pipeline is shared. Future claims must preserve this distinction.

## 5. Binding narrowing D — sharding terminology

The LongMemEval execution must not be described generically as `SHARDED_EXACT` in scientific prose.

The established claim is:

> deterministic sharding with shard-invariant per-question semantics and aggregate numerical reproducibility far inside the frozen `1e-12` tolerance.

Bit-level equivalence to every possible monolithic aggregation order is not a theorem of the construction because floating-point summation is order-dependent.

Machine-readable historical artifacts are immutable and are not rewritten merely to rename an old execution field.

## 6. Auditor-supplied LoCoMo random-partition control

The independent auditor supplied the missing matched-size null on LoCoMo:

- preregistered spectral Head32/Tail64: `rho_2 ≈ 0.107`
- matched random 32/64 partition: `rho_2 ≈ 0.949`
- contrast: `Delta ≈ 0.841`

All five random partitions had exactly 32 unique coordinates in the 0..95 range and landed in the opposite preregistered band from the spectral split.

Licensed conclusion on LoCoMo:

> The preservation effect depends strongly on which coordinates form the 32-dimensional block; generic 32/64 block-diagonality is not an adequate explanation.

This auditor-supplied control was **not** run on LongMemEval by the auditor. Therefore independently audited position-dependence is established on LoCoMo, not yet on LongMemEval.

## 7. Scope of later researcher-produced random-null work

The research branch later contains a separately preregistered matched random-partition null stage on both frozen datasets. That later stage postdates the Head/Tail audit target and was explicitly outside the binding scope of audit commit `f939db0238f1c348c37851aeda9958700bb06d53`.

It may be cited as researcher-produced follow-on evidence, but it must not be represented as having been independently audited by the Head/Tail audit.

The boundary-localization experiment will therefore include a fresh matched random-32/64 control under new frozen seeds so that the LongMemEval position-dependence question is tested inside the new preregistered package rather than assumed from unaudited follow-on work.

## 8. Current strongest defensible claim before localization

> On two frozen memory-retrieval datasets evaluated through one shared pipeline, preserving the leading-32 versus trailing-64 archive-local SVD subspaces while allowing arbitrary within-subspace Haar rotations preserves most of the Native SIGN96-vs-Full-Haar advantage. Exact individual SVD axes are not required under this intervention. On LoCoMo, an independently supplied matched-size random-partition control shows that the effect is strongly position-dependent rather than a generic consequence of 32/64 block-diagonality. The exact location and uniqueness of the spectral boundary remain unresolved.

This remains a fixed-dataset causal lead, not a universal theorem.

## 9. Governance boundary

This addendum authorizes no Task 4F1 execution and no access to Task 4F1 outcomes.

Task 4F1 remains governed by `main` and remains blocked unless an independent valid run authorization exists.
