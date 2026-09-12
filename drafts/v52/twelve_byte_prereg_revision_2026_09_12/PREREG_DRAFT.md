# V52 twelve-byte baseline preregistration revision

**NOT SEALED / NOT AUTHORIZED. Research-design proposal for parent and Head Researcher review.**

Date: 2026-09-12. Base: `4f2429b257546d6899f3ed48f605cd18210aeae0`.
Owned branch: `codex/twelve-byte-prereg-revision-2026-09-12`.
Owned namespace: `drafts/v52/twelve_byte_prereg_revision_2026_09_12/` only.

This draft incorporates the recorded HR budget decision at
`89d3169adb65a9a2ab7f289997d7c49eb8ccf25c` and proposes the remaining design
details. The HR record itself describes relayed chat authority, not an HR-signed
artifact. It does not approve the new proposals below. This revision does not
overwrite the old draft at `d2cfbaacdfc52af2ac2077ffa1d87b719a7d0779`, seal it,
or change any main ledger/state, G3 work, accepted audit, or frozen result.
Digests and branch publication establish reviewable byte identity, not approval.

Source IDs below resolve to exact commit/path/blob/SHA256 entries in
`SOURCE_VERIFICATION.json`; `SOURCE_EVIDENCE_MAP.md` separates authority,
published measurements, provenance checks, and unverified runtime behavior.
Every decision marked **PROPOSED** requires explicit HR or authorized lead
disposition of this draft's digest, or a digest-bound amendment, before it becomes
an accepted design choice. The user has delegated routine design decisions to the
lead; the new primary, literal seed mapping, and strata remain proposals ready
for that disposition. Design acceptance is not a seal or execution authorization.

## 1. Question, scope, and estimand

The design asks how methods perform on the existing frozen evidence-retrieval
panels when each stores **at most 12 marginal persistent bytes per vector,
including all per-vector auxiliary data**, with **archive-local fitting**.
It characterizes retrieval and storage economics; it does not establish a
mechanism theorem, large-scale behavior, or globally shared-codebook deployment.
There is no new corpus, gold, encoder, distractor inflation, or BEAM contact.
Task 4F1 remains **SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN**.

The old primary contrast `SIGN96 - RABITQ96` is **CANCELLED AS WRITTEN** by HR:
the measured 96-dimensional one-bit RaBitQ code consumes 20 B/vector.
There is currently **NO APPROVED REPLACEMENT PRIMARY CONTRAST**.

**P1 PROPOSED:** choose `SIGN96 - PQ96` as the one primary contrast, on
Fractional Evidence Recall@100, separately for corrected LoCoMo and LongMemEval.
Both retain the full 96-dimensional input and have published 12 B/vector storage
measurements. This proposal compares complete methods with their declared query
scoring; it does not isolate quantizer geometry or symmetric-versus-asymmetric
scoring as a causal effect. OPQ_PQ96 and the other eligible arms are descriptive.
HR may reject this choice or choose another explicitly defined estimand; until
then no primary verdict can be issued and no fallback may be substituted.

`TOP32_RABITQ32` is an HR-recognized natural 12-byte candidate, not an approved
new primary. It uses the first 32 coordinates of the same frozen, ordered 96-D
representation. Its comparison with SIGN96 changes both retained dimension and
coding/scoring. **P2 PROPOSED:** retain it as a descriptive deployment candidate
with that confound printed next to its results. It cannot silently replace
RABITQ96 or support a fixed-dimension method/mechanism claim. A dimension-matched
factorial study would require a separate approved design; it is not added here.

## 2. Representation, cohorts, and fitting boundary

Retain the old draft's archive-only centered representation contract:

```text
Z = hstack([LSA32(word-TFIDF), word-TFIDF, char-TFIDF])
Y = normalize(TruncatedSVD(96).fit_transform(Z))
C = Y - archive_mean(Y)
```

This is a description, not a new executable specification. Before sealing,
the runner must bind exact frozen feature/tokenization/normalization code,
versions, fit seeds, query transform, memory identity/order, and tie algorithm
to source digests. No default may be inferred from this snippet. Every arm
consumes the same C/qC pair, except for the explicitly declared coordinate
truncations. All learned preprocessing, rotations, centroids, codebooks, and
int8 calibration use that archive's memory text/features only. No query, gold,
answer, question type, or question metadata enters a fit or hyperparameter choice.
Query transformation begins only after fitting. Fit functions and their dataflow
must enter the leakage audit; seed/RNG metadata and identity-only keys cannot
become features.

Archive-local state is fitted and charged to each archive separately. No reuse
across archives is assumed, even where memory overlaps. A global codebook is a
different, untested deployment. Never amortize state over all benchmark questions.

Retain the old corrected LoCoMo (1535) and raw LoCoMo (1540) dual-report contract,
with their divergence. The corrected cohort is the primary analysis, raw is a
separate sensitivity report and is not pooled with it. Exact interpretation of
these frozen cohort labels and their adapter mappings must be source-bound in the
runner review; this revision does not open cohort rows. LongMemEval retains the
470 non-`_abs` primary questions; all 30 `_abs` are excluded from retrieval recall,
including those with residual positive turns (LME_PROTOCOL).

## 3. Persistent-byte accounting and arms

**HR-BOUND:** the cap includes code bits plus every stored per-vector norm, scale,
correction scalar, residual, ID, metadata field, wrapper entry, or lookup auxiliary.
Calling such storage a sidecar does not exempt it. A common per-vector ID is still
a per-vector cost if this index package persists it. An implicit ordinal costs
zero only when no per-vector mapping is written. The retrieval-code budget boundary
must name externally held corpus payload separately; hiding extra retrieval state
in that payload is prohibited.

Report, per arm and archive:

```text
marginal_bytes_per_vector                    # decides <=12 eligibility
shared_state_bytes_per_archive               # all actual serialized shared state
effective_bytes_per_vector = marginal_bytes_per_vector
                           + shared_state_bytes_per_archive / N_archive
```

Effective cost is mandatory in this revision so small-archive costs stay visible.
Report common archive preprocessing and arm-specific shared state as separate
components and their total, including matrices, centroids, codebooks, calibration,
serialization headers, and any stored RNG/transform description needed for queries.
Count each component once in an arm's total. Report query transform/scoring and
query-side temporary memory/time separately; temporary query RAM is not persistent
vector storage. A float reconstruction retained for every archive vector is
persistent auxiliary storage and must be charged, even if produced by decode.

Published Faiss 1.15.0 values below are evidence baselines, **not a replay in this
revision**. S0 is the empty **trained** serialized index, not a claim that all
archive preprocessing fits inside that object. Additional shared state must be
added; unknown size is never zero. Eligibility remains conditional on real runner
measurements for the complete stored package.

| Arm | Marginal B/vector | Published index S0 / further shared state | Role and query handling |
|---|---:|---|---|
| SIGN96 | 12 | BinaryFlat S0 33 B; add external preprocessing/centering state | Reference; binarize archive and query, Hamming scoring |
| ITQ96 | 12 code bytes, complete package must pass gate | A stored float32 96x96 rotation has analytic content 36,864 B; actual headers/state unmeasured here | Within-96 rotation then sign on both sides; descriptive |
| SIMHASH96 | 12 code bytes, complete package must pass gate | Stored full-Haar float32 matrix has analytic content 36,864 B, or explicitly validated deterministic regeneration state; not free | Full-Haar rotation then sign on both sides; descriptive |
| PQ96 (m=12, 8 bits) | 12 | S0 **98,390 B** = 98,304 B codebook content + 86 B serialization overhead; add external preprocessing | P1 proposed primary comparator; float query against decoded-code centroid distances (native ADC), scoring contract must be bound |
| OPQ_PQ96 (OPQ12_96,PQ12) | 12 | S0 **135,325 B** = 135,168 B analytic rotation/codebook content + 157 B overhead; add external preprocessing | Descriptive; archive-trained OPQ transform plus native PQ ADC |
| TOP32_RABITQ32 (one bit) | 12 = 4 code + 8 auxiliary | Index S0 202 B; add external preprocessing | P2 descriptive candidate only; top32 query and archive, bound native estimator; dimension confounded |
| TRUNC12_INT8 | 12 code bytes, complete package must pass gate | Archive-calibrated shared quantization scale/offset and headers measured explicitly | Descriptive, top12 archive at int8 and float query; any per-vector scale would exceed a bare 12-byte code budget |
| RANDOM96 | 12 code bytes, complete package must pass gate | Actual binary index header and any persisted seed/state | Descriptive random-code floor; independently generated query code, no ID/gold encoding |
| FLOAT96_CENTERED | 384 float32 payload B, plus any auxiliary | Actual shared headers/state | Uncompressed reference only, outside matched-budget set; do not assume a proven quality upper bound |
| RABITQ96 (one bit) | **20** = 12 + 8 | Index S0 458 B | **INELIGIBLE matched comparator**; historical cost evidence only, not scheduled for retrieval here |
| EXT_RABITQ96 (two bit) | **44** | Complete index S0 not measured in cited package | **INELIGIBLE matched comparator**; historical cost evidence only, not scheduled for retrieval here |

**P2 PROPOSED:** the eligible descriptive set above, including adding plain PQ96,
and excluding the two oversized RaBitQ arms from retrieval. No dimension or PQ
configuration may be changed automatically to make an arm fit/train.
TRUNC12_INT8 is a simple coordinate-truncation baseline, not a Matryoshka-trained
encoder or validated proxy for one. Exact int8 calibration, clipping, rounding,
zero-range rule, and scoring remain an implementation/HR gate.

The published OPQ index-only effective panel mean is **287.6889713064122 B/vector**
(287.69 rounded), not 286.6161584760326, the cost at mean N. These numbers are
quoted from COST, not recomputed from archive rows here. Report the mean of
per-archive costs and archive range; a pooled-byte/vector-weighted aggregate, if
also shown, must be separately labeled. Additional preprocessing would increase
these index-only costs. For SIGN96/PQ96/OPQ_PQ96 the corresponding index-only
formulas are 12+33/N, 12+98390/N, and 12+135325/N.

PQ training: the cited package reports 256 centroids require at least 256 training
points for the measured quantizer; 255 fails. `39*256 = 9984` is the default
reliability recommendation, **not** the hard trainability bound. OPQ's internal
training must be checked separately. Insufficient training points or any training
failure blocks the arm/analysis under the approved failure policy; no padding,
cross-archive fitting, centroid reduction, dropped archives, or silent substitution.
Warnings are recorded. A warning alone is not relabeled a proven failure or success
of retrieval quality.

## 4. Mandatory real-library storage gate (not implemented or satisfied here)

Before any new retrieval scoring, the reviewed runner must instantiate the exact
adopted implementation and validate real `code_size`, emitted code-array layout,
full serializer output, and every auxiliary file. A declared bit count, Python
attribute readback, analytic size, or approximately fitted regression slope does
not pass this gate. The gate has two phases: synthetic locked-runtime validation
before seal consideration; then archive-specific validation after separately
authorized fitting and before any retrieval quality is computed/released.

The implementation contract is:

1. Lock package/build/wheel or vendored source hashes and constructor signatures.
   Capture each arm's dimension, bit width, metric, training controls, and actual
   library code_size. Check the code buffer's per-row byte stride and shape.
2. Train once, freeze that fitted state, and serialize the **complete** package with
   zero vectors: S0. Clone the same state to serialize at n=1,100,1000,10000 on
   synthetic vectors. Add any external persistent vector/shared files to each size.
   Require exact integer identities `S(n) - S0 == n * declared_marginal_bytes`.
   Do not use the old evidence's least-squares slope/one-byte residual threshold as
   the acceptance assertion. Variable-size, capacity-rounded, or unexplained bytes
   fail closed until an explicitly approved accounting rule replaces this contract.
3. Require `actual_code_size + measured_per_vector_auxiliary == declared_marginal`
   with no double-counting of auxiliary data already inside code_size. Require
   `measured_persistent_bytes_per_vector <= 12` for **each matched arm**. A
   non-matched float reference is explicitly tagged, cannot enter the primary or
   any matched-budget verdict, and still has its declared size checked.
4. Round-trip the serializer; verify dimensions, metric, code size, vector count,
   fitted state, auxiliary values, and synthetic scores/reconstructions against
   the pinned implementation. On authorized archives, also check the actual
   full-package S(N) and shared state before scoring. An unmeasured sidecar or
   opaque wrapper is a blocking failure, not an exemption.
5. Negative checks must demonstrate rejection of 20/44-byte arms labeled as 12,
   post-construction `nb_bits` mutation that reads back 2 while retaining a one-bit
   code, wrong metric/constructor overload, missing auxiliary storage, serialization
   disagreement, and a failed training or RNG-binding check. Capture nonzero
   child-process exits/timeouts as failures; do not allow a crash to bypass checks.

These are required tests for the future implementation; this design-only branch
does not claim to contain or pass them. A primary-arm failure blocks primary
inference and any new outcome release; no substitute or question omission is
allowed. Any alternative failure/missingness policy needs a pre-outcome amendment.

**C7 portable statement:** positional arguments must be interpreted using the
installed wrapper/C++ signature. In the cited claim, IndexRaBitQ's second argument
selects the metric, not bit width; `IndexRaBitQ(96, 2)` is not a portable declaration
of a two-bit quantizer. Require explicitly validated constructor/metric/bit-width
binding and observed code_size. The claimed METRIC_L1/heap-corruption manifestation
is environment-specific and is not a guaranteed outcome of that call. Its behavior
in the parent's environment remains a replay gate. Do not run an unsafe overload
in-process merely to test whether it crashes.

**C4 limit:** the published decode probe supports only the functional attribution
that the extra eight bytes contain scale information reconstruction consumes; it
is not removable as mere padding without losing that information. Attribution to
the unbiased estimator's theoretical correction terms/error bound is **NOT
ESTABLISHED** by those measurements. No unsupported MRQ or JQ/JHQ attribution,
comparative claim, or arm is introduced. This draft makes no minimum-version claim
for multi-bit support; adopted implementation availability must be directly checked.

## 5. Seeds and nuisance averaging

**HR-BOUND:** at least 20 seeds for Haar and within-96 arms, source-literal before
any run. The old five-seed panel remains a historical R@3 control only.
**P3 PROPOSED, NOT HR-APPROVED:** use the explicit 20-element panels in
`PROPOSED_CONSTANTS.json`, paired by panel index across stochastic arms. The Haar
panel is 43001 through 43020, listed literally. The ITQ panel retains 101,202,303,
404,505 and extends to 2020 in 101 increments, also listed literally. Every
within-96 stochastic rotation, including OPQ training, gets at least 20 literal
seeds. PQ standalone, OPQ rotation-internal quantizer training, and final PQ
training have separately named panels; no undocumented library default counts
as a seeded training. RANDOM96 has a separately named panel.

The implementation audit must enumerate every actual random operation (including
initialization, sampling, training, and any RaBitQ random transform) and map it to
a literal panel and version-bound RNG call. The RaBitQ RNG panel in the constants
is conditional: apply it only to randomness verified in the selected implementation.
Deterministic arms, including deterministic int8 calibration if adopted, must not
be presented as independently seed-averaged. An inability to control an active
training RNG is a blocking gate. OPQ internal and final PQ seeds are distinct;
setting a top-level field that is ignored does not suffice. Any additional
within-96 stochastic operation must be explicitly added to the reviewed mapping.

Retain nuisance trials 0..19 and one shared tie priority per (question, trial)
across all arms, from the source-bound frozen tie algorithm. Do not invent a new
tie-seed rule. Archive/query random-code draws must be independent streams and
must not accidentally match by reinitializing the same seed. No best-seed
selection, tuning, early stopping, or replacement based on recall is permitted.

## 6. Metrics, k>N, and gold-count strata

**HR-BOUND:** primary Fractional Evidence Recall@100; secondary @3, @10, @1000.
For question q, let Gq be the nonempty set of unique eligible gold memory IDs and
Tq(k) the first `min(k,Nq)` unique IDs in the full archive ranking. Define

```text
R_q(k) = |Gq intersect Tq(k)| / |Gq|
```

**P4 PROPOSED implementation convention:** when k>N, return all N unique archive
IDs; no padding, repeated IDs, replacement, or denominator truncation. Thus full
recall is 1 only when all gold IDs are represented. Report the number/fraction of
questions with N<k for every k. In COST's published 470-archive geometry panel,
N ranges from 396 to 616: **R@1000 is necessarily 1 for every method with valid
gold membership and a complete ranking**, so it is a descriptive saturation
diagnostic and cannot show a method advantage. Do not extend that archive-size
range to a different cohort without evidence; apply the same min(k,N) rule there.
Require Gq to be a
subset of the eligible archive; missing gold, duplicate ranked IDs, N=0, or an
unexpected zero-gold question in the primary cohort aborts validation. Do not hide
a missing gold ID by shrinking the denominator or recoding an undefined recall
as 0 or 1. Keep intentional exclusions prescribed by frozen cohort adapters.

Each question carries equal weight in the benchmark mean, after averaging its
nuisance trials and stochastic seed panel. Do not weight by number of gold items,
archive size, or number of memories. Gold IDs are deduplicated by the frozen
identity contract before cardinality is counted. Scores and differences are
reported in fractions and explicitly labeled absolute percentage points (100*delta).

**HR-BOUND:** preregister gold-evidence cardinality strata.
**P4 PROPOSED exact bins:** `|G|=1`, `|G|=2`, `3<=|G|<=5`, `|G|>=6`.
Choose these boundaries now without inspecting gold distributions. At authorized
evaluation, report counts and all declared recalls for each bin and benchmark,
and the raw/corrected LoCoMo separation. Empty bins are NA, never silently merged;
do not define sample quantiles or change boundaries after seeing data. Strata
are descriptive; they do not replace or reweight the primary aggregate. Proposed
stratum bootstrap resamples the same benchmark-level units then filters to the
bin; intervals require a nonempty bin in every replicate and at least two distinct
resampling units contributing to that bin, otherwise report CI unavailable and
the reason. This is a reporting convention, not a guarantee of adequate precision.

Report distinct-code fraction, duplicate-code fraction, and exact query/code-match
fraction where an arm has a meaningful same-space query code. Native float-query
ADC arms use NA for query-code match, not a manufactured binarized query. These
diagnostics are descriptive. No full recall curve, @50 primary, or weighted recall
is silently inherited from the old draft. Weighted retrieval and new asymmetric
SIGN96/ITQ/SIMHASH scoring are **follow-up only**, requiring a separate design and
authorization. Native PQ/RaBitQ query scoring declared in the arm definition is
part of that method; it is not a new SIGN96 asymmetric follow-up.

## 7. Statistics and proposed decision language

**HR-BOUND:** paired bootstrap, **10,000 replicates**. **P5 PROPOSED details:**
use the literal bootstrap seed 61001 in the constants and a pinned RNG/version.
Average trials within each seed/question, then average the 20 seeds per question;
pair reference/comparator values on the same question and use identical resampled
units for both arms, metrics, and declared contrasts. Never treat 20 seeds x 20
trials as independent questions. Report mean and sample SD across seed-level
benchmark means for stochastic arms, with the number of seeds/trials completed.
The bootstrap CI is conditional on the fixed seed panel; it is not a population
CI over all possible rotations or training seeds. No missing seed can be dropped.

For LoCoMo, draw 10 conversation clusters with replacement and include all their
questions, preserving sampled multiplicity; compute the question-weighted mean
inside that replicate. Use the same sampled conversation IDs for raw/corrected
reports. Ten clusters is a limitation, not evidence of asymptotic reliability.
For LongMemEval, resample the 470 questions with replacement. Per LME_PROTOCOL,
all questions form one connected memory component, so question-bootstrap intervals
are conditional descriptive uncertainty, **not independent-memory population
inference**. No pooled cross-benchmark CI or generalization claim is authorized.

Use 2.5th/97.5th empirical percentiles with linear interpolation (implementation
method/source version bound before sealing). The sole proposed primary contrast
gets a 95% interval on each benchmark. Other contrasts and strata are descriptive
estimates/intervals with no significance claims. Remove the old internally mixed
"descriptive comparisons + Holm" instruction: an inferential secondary family,
if desired, needs explicit hypotheses, tests, family membership, and HR amendment.

**P5 PROPOSED decision language:** for the approved primary comparator M, define
delta_b = 100*(SIGN96_R100 - M_R100). Mark practical evidence favoring SIGN96 if
delta_b>=+2.0 pp and the 95% interval excludes 0; practical evidence favoring M if
delta_b<=-2.0 pp and the interval excludes 0. Otherwise mark **INCONCLUSIVE AT
THE PROPOSED 2-PP RULE**, not proven parity/equivalence. The 2-pp threshold is
inherited as a proposal from the old R@3 rule: **a pre-outcome convention, not an
empirically calibrated R@100 threshold**. Its suitability for R@100 is not
approved by the HR metric change. Print both benchmark states; concordant signs
describe only these panels, opposing states indicate benchmark disagreement,
and one inconclusive state leaves the joint conclusion inconclusive. This does
not establish superiority over untested methods or issue a mechanism-line kill.
The authorized lead/HR must explicitly dispose of these rules; any wider program
decision requires the appropriate separate authority. The old
RaBitQ B1-B5 verdicts/kill rule are not automatically retargeted to PQ or R@100.
Commit to reporting negative, mixed, and inconclusive outcomes with the same
tables and qualifications as favorable outcomes, if execution is later authorized.

## 8. Historical positive controls and provenance limits

Retain the old draft's R@3 control targets, separately from the new R@100 primary:

| Control | Target | Tolerance | Provenance status in this revision |
|---|---:|---:|---|
| SIGN96 LongMemEval fractional R@3 | 0.5419751773049646 | 1e-9 | Retained from digest-verified OLD; original frozen-native source binding still required in implementation review |
| SIGN96 corrected LoCoMo fractional R@3 | 0.23654714666441054 | 1e-9 | Retained from digest-verified OLD; original frozen-native source binding still required in implementation review |
| ITQ96 LongMemEval fractional R@3 | 0.3761411347517731 | 1e-9 | Historical five-seed configuration only; exact frozen aggregation must be bound |
| SIMHASH96 LongMemEval fractional R@3 | 0.38271667 | 1e-6 | Derived from SIMHASH_AUDIT's published 43001..43005 scalars as below |

SIMHASH_AUDIT is `audit_v52_t4c3/AUDIT_REPORT.md` at the base commit, SHA256
`8f6b31050c6e211b7c34ba8214405cff91251d33bd590be97c996ce17f2be238`.
It publishes percentages 36.1395390, 39.1393617, 37.9320922, 38.0195035,
40.1278369 for seeds 43001,43002,43003,43004,43005 respectively. Divide each
percentage by 100 and take their arithmetic mean: exact decimal **0.3827166666**
from the printed scalars. Round to nearest eight fractional decimal places
(HALF_EVEN; no tie here) to obtain **0.38271667**. The closure's binary-float display
0.38271666660000003 is consistent with that decimal provenance. No underlying
per-question outcome was read or recomputed for this derivation.

Do not assert this five-seed control against the new 20-seed mean. Execute any
eventually authorized historical control in its exact historical configuration,
including fit/ties/cohort/aggregation; a passing control does not validate R@100
or an expanded seed panel. Preserve frozen_native versus native_reproduction
distinction and old tolerances, rather than requiring bit-exact floating equality.
The raw LoCoMo report has no frozen target in OLD and remains ungated by a
manufactured scalar. Control failures stop before any new result release;
no old row-level result recomputation or corpus control execution is performed here.

## 9. Approval and execution gates

The exact unresolved choices and accountable reviewers are in
`UNRESOLVED_DECISIONS.md`. All gates are presently **OPEN**:

1. HR or the lead acting under delegated design authority explicitly accepts/revises
   P1-P5 and the exact draft/constants digests, including the
   new primary contrast, candidate arm set, seed/RNG mapping, strata/k>N semantics,
   bootstrap details, threshold/decision language, and failure policy.
2. Parent supplies a digest-bound **historical cost-script runtime replay** receipt
   in the declared Faiss 1.15.0 / NumPy 2.4.6 environment, binding the historical
   script, inputs, command/exit, raw output and comparison with COST. Its scope is
   the historical probes: quantizer code sizes, bit-assignment trap, synthetic
   index serialization, training-bound probes and published cost aggregation.
   A complete, reviewed replay **can close this specific historical-reproduction
   gate**. Supplementary constructor/C4 checks have separately stated scope.
   Environment readiness or partial checks alone do not close full replay. This
   parent-owned gate is mandatory and is not duplicated here; it does not require
   the historical script to prove a future runner's behavior.
3. **Future runner integration remains a separate OPEN gate:** reviewed code and
   environment/source locks must implement section 4's real complete-package
   storage/auxiliary/serialization checks and negative cases, verify RNG propagation
   and seed-control, and bind exact frozen adapters/controls, leakage audit,
   training/scoring and archive accounting. Historical replay can close gate 2
   while this gate stays OPEN. Missing implementation evidence means BLOCKED, not
   conditionally passed by a historical receipt or a written requirement.
4. A separate explicit HR decision authorizes any future sealing. Another explicit
   scope-appropriate authorization is needed for corpus/control execution and
   outcome access. This publication requests or supplies none of those permissions.

No seal, pilot, corpus read, retrieval, `run`/`finalize`, outcome access, or HMAC
operation is authorized by this document. No current publication or checksum can
be used as a substitute for those gates. Parent review is the next action.
