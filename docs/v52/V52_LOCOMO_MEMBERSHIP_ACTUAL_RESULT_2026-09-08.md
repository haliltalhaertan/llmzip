# LoCoMo membership-under-scaling: actual execution result

Actual run completed exit0, elapsed274.7503778000246 seconds. Launch candidate
1b88957 on codex/v52-membership-integration-v2-2026-09-08 was committed and pushed
before execution. User explicitly authorized the run and exact57167bc gold exception.
This is the LoCoMo leg, NOT completion of the two-benchmark study or BEAM Task4F1.

Artifacts: membership_actual_locomo_run_2026_09_08/. Ten archives,1535questions,
92100 complete per-question/arm/seed records. Candidate and dependency bindings,
source identity, per-archive records, result and output inventory are retained.
Source/correction files and question/answer text were not uploaded.

## Results, percentage points

| Quantity | Point estimate | Conversation-cluster bootstrap2.5/97.5 percentiles |
|---|---:|---:|
| G: B32 minus RANDOM32 before scaling | 8.230868478053235 | [6.93403971850814,9.4875400756564] |
| G_scaled: same membership gap after scaling | 1.592174659098349 | [0.5568980950201291,2.7915434113657245] |
| Delta: paired G_scaled minus G | -6.638693818954884 | [-7.537673072441288,-5.678272756056388] |

Both question and conversation-cluster bootstrap use10000replicates; all outputs
are retained in RESULT.json. These percentile ranges are sensitivity summaries,
not certified population confidence intervals. Only ten conversation clusters
are available; the fixed ten-seed panel is not a population of random encoders.
No ratio, categorical threshold or significance declaration is introduced.

All ten native per-seed means equal the historical aggregate at the run's
floating arithmetic:0.23654714666441054. ScaledNative and Native records are exact
matches. Mandatory controls passed; no seed/pilot/retry or convention adjustment.

## Bounded independent post-run verification

The fresh-context pre-run reviewer performed a separate post-run artifact and
arithmetic check without importing the experiment aggregation implementation.
Returned verdict: PASS, no finding within requested scope. This parent-persisted
account is not a cryptographic reviewer signature or a full scientific cold-start
audit. Original RESULT status COMPUTED_PENDING_POSTRUN_AUDIT is left unchanged;
this additive record supplies the newer bounded-check status.

-13/13 output payload SHA256s and byte counts match; directory contains those
 payloads plus their manifest.
-Five reviewed Python identities match pre-run binding and current bytes.
-92100uniquecompletecells, no missing/duplicate/unexpected cells, all finite[0,1].
-Native/ScaledNative exact per cell; independent math.fsum Native maximum error
 5.551115123125783e-17 versus frozen reference, within1e-12.
-Independent per-seed and panel gap arithmetic maximum absolute difference
 3.552713678800501e-15 percentage points, within1e-12.
-Cluster sizes match accepted mapping; uncertainty endpoints finite/ordered and
 metadata consistent,10000replicates, zero questions lost to invalid labels.

Reviewer did NOT recompute bootstrap interval endpoints, rerun representation or
retrieval, or rederive individual scores from the corpus. Implementation replay
and independent synthetic pre-run checks remain separate evidence.

## Interpretation ceiling and remaining work

On this LoCoMo cohort and fixed panel, the specified rescaling intervention makes
the B32-versus-random-membership gap substantially smaller, but the observed gap
does not disappear. This is evidence about this particular computational
intervention; it does not prove one unique mechanism, universal axis ordering,
generalization across representations, or a working persistent-memory system.
No256x end-to-end efficiency or compression benefit was measured.

The exact one-question gold exception remains disclosed: locomo_4_qa18 had seven
original references, one absent from its archive, and six historically resolvable
references were used after explicit outcome-before-run user approval. No question
was excluded. Other questions remained subject to the strict gold contract.

LongMemEval has NOT run. Its named raw source was not found in the current
workspace; this is not a machine-wide absence claim. Its data acquisition/location
and separately bound execution leg remain outstanding. Main/state/ledger were not
mutated; this branch is the explicit continuation anchor for the executed leg.
