# V52 LongMemEval causal spectral-band checkpoint — 2026-09-04

## Status

`[SPECTRAL-SUBSPACE PRESERVATION LEAD]`

This checkpoint is based on the preregistered LongMemEval causal intervention executed in GitHub Actions run `33864691367`, job `100996750402`.

The compute step completed successfully. The later persist-to-branch step failed only because the research branch had advanced concurrently, causing a non-fast-forward push rejection. The primary result below was printed by the successful compute step and is preserved separately in `longmemeval_causal_summary.json`.

## Identity and gates

- preregistration Git blob: `02aa91a12b4052bbb2f0a6617167c8851e4f71f7`
- dataset SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- dataset bytes: `277383467`
- adapter v1 SHA-256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- adapter v2 SHA-256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
- primary cohort: `470`
- native reproduction error: `1.1102230246251565e-16`
- signed-permutation exact control: `PASS`
- continuous norm max abs error: `5.551115123125783e-16`
- continuous dot max abs error: `8.881784197001252e-16`

## Primary causal result

| Quantity | Value |
|---|---:|
| Native SIGN96 Fractional R@3 | 0.5419751773049645 |
| Frozen Full-Haar96 mean Fractional R@3 | 0.3827166666666700 |
| Within-band Haar mean Fractional R@3 | 0.5192287234042553 |
| Full-mixing loss `L_full` | 0.1592585106382945 |
| Within-band loss `L_band` | 0.022746453900709174 |
| `rho = L_band / L_full` | **0.14282724238436822** |

Preregistered regime: **`[SPECTRAL-SUBSPACE PRESERVATION LEAD]`**.

Within-band seed results:

- 55001: 0.5301950354609929
- 55002: 0.5144609929078013
- 55003: 0.5152553191489362
- 55004: 0.5178049645390072
- 55005: 0.5184273049645390

Secondary 64D mixing arms:

- `HAAR_HIGH_MID64`: 0.4923985815602837
- `HAAR_HIGH_LOW64`: 0.4509716312056738
- `HAAR_MID_LOW64`: 0.5138542553191490

## Interpretation

The large degradation caused by unrestricted 96D Haar mixing is mostly avoided when orthogonal mixing is constrained to the frozen High32/Mid32/Low32 spectral bands. On this frozen LongMemEval benchmark, exact individual coordinate directions inside each band therefore do not appear to account for most of the native SIGN96 advantage. The evidence instead points toward preservation of spectral subspace separation as the load-bearing structure.

This is fixed-benchmark causal-intervention evidence only. It is not a population-level statistical claim.

## Provenance caution

The first full runner produced the result successfully but failed to push its complete output directory because another valid research commit reached the same branch while it was running. An exact sharded rerun is retained as the artifact-recovery / equivalence check. Until that full artifact package is persisted, this checkpoint should be treated as numerically established from the successful Actions log but still awaiting redundant artifact-level reproduction.
