# V52 Cross-Benchmark Matched Random-Partition Null Checkpoint

Date: 2026-09-04
Branch: `research/v52-sign-mechanism-locomo-2026-09-04`
Preregistration Git blob: `2d6a14f254399327f59db1958a0b5c0dfb9ea8e0`
Pre-run seal Git blob: `df309826982504c5ea0ff3917d67cf2da632bac4`
Trigger commit: `9fd60f60f3ecb407f9a0547853d88e487dabd05b`

## Preregistered cross-benchmark verdict

**`[CROSS-BENCHMARK SPECTRAL POSITION CAUSAL LEAD]`**

Shared benchmark-level regime:

**`[SPECTRAL POSITION LOAD-BEARING LEAD]`**

This verdict follows mechanically from the preregistered rule. Both benchmarks first passed the new-seed spectral Head32/Tail64 replication gate (`rho_spec <= 0.25`) and then exceeded the frozen matched-null contrast threshold (`Delta >= 0.25`).

## Scientific question

The previous Head32-vs-Tail64 experiment showed that preserving the spectral Head32/Tail64 split while scrambling directions within each block retains most of Native SIGN96's advantage over unrestricted Full-Haar mixing. It did not establish whether the spectral position of those coordinates mattered, because any arbitrary 32/64 block-diagonal structure might conceivably have had the same effect.

The present preregistered null control therefore compared, seed-for-seed:

1. `SPECTRAL_HEAD32_TAIL64_HAAR_NEW`: coordinates `0..31` versus `32..95`;
2. `RANDOM32_COMPLEMENT64_HAAR`: a uniformly permuted 32-coordinate subset versus its 64-coordinate complement.

For each seed, the two arms used the same numeric `Q32` and `Q64` Haar matrices. The coordinate partition was the primary experimental difference.

## Primary results

| Benchmark | Native R@3 | Frozen Full-Haar R@3 | Spectral 32/64 R@3 | Random 32/64 R@3 | rho_spec | rho_rand | Delta | Regime |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| LoCoMo | 0.23654714666441054 | 0.13770827054136000 | 0.23012794124632070 | 0.14298280722884044 | **0.06494615954655526** | **0.9466349993608402** | **0.8816888398142849** | SPECTRAL POSITION LOAD-BEARING LEAD |
| LongMemEval | 0.54197517730496460 | 0.38271666666667000 | 0.51480301418439710 | 0.38202482269503546 | **0.1706167099746428** | **1.0043441569864096** | **0.8337274470117668** | SPECTRAL POSITION LOAD-BEARING LEAD |

Interpretation of the scale: `rho ≈ 0` means the intervention preserves nearly all of the Native-vs-Full-Haar advantage; `rho ≈ 1` means it loses approximately as much as unrestricted Full-Haar mixing.

On both benchmarks the matched random partition is approximately Full-Haar-level, while the contiguous leading-vs-tail spectral partition preserves most of the Native advantage.

## Robustness across the frozen 10-seed panel

### LoCoMo

- spectral `rho_spec` range: `-0.0507579399107387` to `0.20039806569479987`
- random `rho_rand` range: `0.8141824047038358` to `1.0548909044217007`
- paired `Delta` mean: `0.881688839814285`
- paired `Delta` sample SD: `0.12128537114222615`
- paired `Delta` range: `0.613784339009036` to `1.0465011549547585`

Every spectral seed independently passed the `rho_spec <= 0.25` replication gate. Every paired `Delta` independently exceeded the preregistered `0.25` load-bearing threshold.

### LongMemEval

- spectral `rho_spec` range: `0.08387718794324094` to `0.23679106853793233`
- random `rho_rand` range: `0.9039453673829926` to `1.0989537061159105`
- paired `Delta` mean: `0.8337274470117668`
- paired `Delta` sample SD: `0.09614763309727813`
- paired `Delta` range: `0.6893760757410925` to `0.9759768786642199`

Every spectral seed independently passed the replication gate and every paired `Delta` independently exceeded `0.25`.

## Integrity controls

LoCoMo:
- evidence-valid denominator: `1535`
- native reproduction error: `0.0`
- signed-permutation Hamming invariance: `PASS`
- continuous norm max abs error: `4.440892098500626e-16`
- continuous dot max abs error: `1.7763568394002505e-15`
- random partition cardinality/disjointness/exhaustiveness checks: `PASS`

LongMemEval:
- primary questions: `470/470` unique
- deterministic shards: `10/10` successful
- native reproduction error: `0.0`
- signed-permutation Hamming invariance: `PASS`
- continuous norm max abs error: `6.661338147750939e-16`
- continuous dot max abs error: `7.771561172376096e-16`
- random partition cardinality/disjointness/exhaustiveness checks: `PASS`

Pre-run governance:
- preregistration was committed before runner/workflow outcome execution;
- exact preregistration + two runner + two workflow blobs were bound by the pre-run seal before the trigger file existed;
- both Actions workflows independently rechecked those blob identities before computation;
- the preregistration and pre-run seal were also copied to Google Drive before the trigger commit;
- Task 4F1 execution and outcomes were not touched.

## Licensed causal interpretation

The matched null control strongly rejects the simplest generic-block explanation on these two frozen benchmarks. Merely splitting 96 coordinates into an arbitrary 32-dimensional block and a 64-dimensional complement does not reproduce the preservation effect of the leading-vs-tail spectral split.

The strongest current causal mechanism lead is therefore:

> **Spectral coordinate position matters: preserving the separation between the leading 32-dimensional archive-local SVD subspace and the remaining 64-dimensional tail preserves most of SIGN96's Native-vs-Full-Haar retrieval advantage, whereas matched-size random 32/64 partitions lose approximately as much as unrestricted Full-Haar mixing on both frozen benchmarks.**

This is stronger than the previous statement that only a two-block structure is sufficient. The random-partition null has now falsified that generic explanation under the preregistered decision rule.

## What this does NOT establish

This result does not establish:
- that the boundary at exactly coordinate 32 is uniquely optimal or necessary;
- that every individual coordinate in Head32 is intrinsically special;
- a universal theorem about PCA/SVD hashing;
- population-level generalization beyond these two benchmarks;
- production superiority of SIGN hashing;
- transfer to arbitrary encoders, corpora, bit widths, retrieval metrics, or Task 4F1;
- correspondence between archive-local SVD coordinates and neural-network neuron axes.

The next scientific question, conditional on independent audit, is boundary localization. No boundary scan is authorized by this checkpoint.

## Audit threshold

This result crosses the project's load-bearing mechanism threshold because:

1. it survives a preregistered falsification/null experiment;
2. the same regime appears on both frozen benchmarks;
3. all 10 paired seeds on both benchmarks point to the same side of the decision boundary by a wide margin;
4. future boundary-localization work would directly build on this conclusion.

Therefore the required governance decision is:

**`[AUDIT NOW — LOAD-BEARING RESULT]`**

Boundary localization must wait until a cold-start independent audit checks the preregistration ancestry, exact matched-matrix construction, random partition generation, frozen data identities, sharding/tie semantics, raw aggregation, artifact provenance, arithmetic, and interpretation ceiling.

## Provenance anchors

- LoCoMo summary Git blob: `205c2b72e87eec6e441604120ab1bf50e65ff4e5`
- LongMemEval summary Git blob: `999f6f16c56d96b074b4968ca8d33fec95a82a95`
- LoCoMo Actions run: `33907122988`
- LoCoMo immutable artifact ID: `9949936324`
- LoCoMo artifact digest: `sha256:5b306f7874fe5bd441a3fb045bc776de8e538fb0507dff8fe4317180d26bd1e3`
- LoCoMo Drive artifact ID: `19zuaMJeF32BAdG7dSKOmovjGzhSmvzT7`
- LongMemEval Actions run: `33907122993`
- LongMemEval aggregate job: `101135639725`
- LongMemEval immutable final artifact ID: `9950032044`
- LongMemEval artifact digest: `sha256:87069e0f6dfe2f47833518ef8bf719b1bb692f7c71c3664e3c6cca808cee124e`
- LongMemEval Drive artifact ID: `1YHi5QT1cX4T_qXHzaXRtxNUw5m5DP7R4`

Research branch output base after CI persistence: `7903848604f5b2f1ed2b9ca1ff16896c12afad0f`.
