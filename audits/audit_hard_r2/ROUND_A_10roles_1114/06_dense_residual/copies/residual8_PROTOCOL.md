[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Residual8 pilot R1 — prospective specification

User explicitly requested Muse benchmark testing of 96-bit SIGN + a small FLOAT-derived tail, prioritizing losing benchmarks. This authorizes a separate local exploratory pilot only, not the sealed F1/BEAM/R@100 contest. No main changes. Existing data already informed selection; NOT confirmatory or unseen-data evaluation. Plan written before these candidate outcomes. LoCoMo EXCLUDED due to known gold-protocol mismatch; no selective post-outcome exclusion.

## Fixed scope and primary outcomes

Primary benchmark PerLTQA: all 8265 original valid queries, 30 archive clusters; especially report events separately, plus dialogues/profile/social_relationship without changing the pooled-within-benchmark query weighting. Other benchmarks LME (470 queries/archives) and REALTALK (705 valid queries, 10 archives) are prespecified preservation checks. Never combine benchmarks. No subsampling, no gold-based threshold/coordinate selection, no retuning after seeing outcomes.

Metric: exact expected fractional gold recall at K=3 under uniform ties, not finite 20-trial legacy means. BASE is Hamming on the unchanged centered 96D cache vectors (>=0). FLOAT raw cosine and standardized cosine are uncompressed contextual references, not equal-budget methods. FLOAT is a baseline gate; standardized cosine optional context only, never a new optimized arm. No new cache fits.

## Shared fixed encoding

For each archive use float64 document C only. Select 8 axes by descending population variance (ddof=0); break equal variance by increasing original axis index: np.lexsort((np.arange(96), -np.var(C,axis=0,ddof=0)))[:8]. This is an explicitly disclosed document-fitted selection rule, not a novel mechanism or supervised selector. No alternate selection sweep.
Threshold on each selected axis is median(abs(C[:,j])), persisted float64. Magnitude bit is STRICT abs(value)>threshold, for both documents and queries using the same stored thresholds. Sign convention >=0. Query participates in encoding/scoring, NEVER fit/selection. Finite/shape/gold-index validation fail closed.

Payload: pack original signs into 12 bytes/doc and eight magnitude flags into 1 extra byte, using np.packbits with explicit bitorder=big. Write/decode the real uint8 [N,13] payload and require equality with original encoded bits. Do not report boolean-array nbytes as a packed code. Coordinate map uint8[8] and thresholds float64[8] are shared state (8+64 bytes content per archive); persist and measure container/header overhead separately. Common TF-IDF/SVD pipeline and application IDs/text are outside the code payload and must be disclosed separately, not called 13-byte total deployment. No per-document float residuals may be retained for MAG8 scoring after encoding. Query float state is allowed and reported.

## Fixed arms and attribution control

1 BASE: score -H96, exact expected FR@3.
2 SIGN_ONLY8: lexicographic (-H96, sum_j s_doc_j*s_query_j on the eight selected axes). Uses existing sign bits ONLY, no extra per-document bits. Shared axis map charged. This is required to distinguish benefits of magnitudes from merely reweighting existing signs.
3 MAG8 (primary): lexicographic (-H96, sum_j (1+m_doc_j)*(1+m_query_j)*s_doc_j*s_query_j). Selected signs come from the ORIGINAL packed sign code; magnitude bits from the extra byte. This is a hybrid exploratory construction inspired by weighted signed products, NOT a faithful 96D two-bit paper replication. Main Hamming ordering must never change.
4 RANDOM8: stored independently sampled uniform 8-bit suffixes for docs and query; tie score -Hamming(suffix_doc,suffix_query). Twenty fixed seeds in constants.json. This controls a purely random extra byte, not semantics. Report seed-mean AND best seed (descriptive optimism bar, not a selected deployable model). Uniform random tie resolution already has BASE as its expectation; the finite seeded random panel is a diagnostic, not 20 independent datasets. Never reuse evaluation gold to select a seed.

Equivalent exact integer encoding of MAG8 lexicographic order may use stride 2*4*8+1 for -H96: the residual is bounded in [-4*8,+4*8]. Test strictly different Hamming distances cannot invert. Retain uniform expected tie averaging for ties remaining on BOTH scores; do not resolve them by input order/doc ID. Prove via tiny brute-force enumeration that the scoring function equals the intended lexicographic-tie expectation.

## Baseline and input gates BEFORE candidate outcomes

For each assigned benchmark recover native t=1 rows from C:/Users/MDP/dev/llmzip-work/theory_benchmark_test_v1/{lme,perltqa,realtalk}/per_query.jsonl; source hashes/provenance in next_route_round1/control_inventory_verified.json. LME identity (archive_id,qa_id), others qid with archive ID validated from original source/cache. PerLTQA native_exact is SIGN; others sign_exact; FLOAT float_exact. Deduplicate native t=1 cross-group repeats only after verifying values identical. Preserve original scores unmodified.

Bind IDs using cache-native question_id (LME), dictionary qid plus char (PerLTQA), qids plus chat/file (REALTALK). Verify full key coverage/unique keys, gold count, archive N, original cache hashes where available, and source scorer/mapping. Recompute unchanged BASE SIGN and FLOAT with source-compatible zero-norm policy; compare EVERY per-query value to historical exact native rows at <=1e-12, not rounded aggregate targets. Source archived producer tie law and zero-vector conventions take precedence over a convenient helper. If a benchmark fails, report gate mismatch with IDs/maxdiff and STOP THAT BENCHMARK before computing MAG8/random/ablation outcomes. Do not fix labels, replace historical controls or relax tolerance to pass. This gate belongs to this fresh pilot, not a claim of closure of the separate sealed F1 contract.

## Tests and analysis

Strict test-first implementation: run failing synthetic tests before each behavior, then pass; archive logs. Tests cover packed roundtrip/payload bytes, zero/sign/magnitude equality boundaries, float64 threshold serialization consistency, primary-distance non-inversion, exact remaining-tie expectation, input-order permutation invariance, no-query/gold fit, and MAG8=SIGN_ONLY8 when all magnitudes are zero. Compute best/worst possible BASE boundary tie resolution from known gold sets as DIAGNOSTIC ORACLE BOUNDS only (no deployable arm, no gold access in encoder). Residual FR must lie in these bounds; derive available tie-only recovery headroom versus the raw FLOAT gap. Count identical full-code collisions separately from query-distance boundary ties; neither alone proves semantic improvement.

Primary contrasts: MAG8-BASE and MAG8-SIGN_ONLY8 on PerLTQA overall, paired query-weighted estimates. Archive-cluster bootstrap: fixed seed 63001, 2000 replicates; 95% intervals for both contrasts are exploratory, unadjusted, not two formal significance claims. Use observed raw mean as point estimate, NEVER the mean of bootstrap means. Also report a conservative 97.5% interval for each of the TWO PerLTQA overall primary contrasts (Bonferroni familywise caveat: cluster-bootstrap coverage approximate). Events/other sections and LME/REALTALK are descriptive diagnostics, not additional confirmatory wins. Report few-cluster limits, query counts, cluster counts, and all failures. No automatic non-inferiority/kill/promote rule, no arbitrary 2pp tolerance. Fixed 8 bits only; do NOT sweep 4/16, alternatives or new mechanisms in this run.

## Output contract

Per-query CSV/JSONL includes benchmark, archive_id, qid, section, gold_count, N, original_control_sign/float, recomputed_sign/float, SIGN_ONLY8, MAG8, all RANDOM8 seed results, BASE boundary sizes, best/worst tie bounds. Keep fitted state/payloads and state hashes per archive, input file hash manifest, gate report, tests/run logs, summary JSON and English REPORT.md. Save progress per archive; stop/report after 25 minutes if unfinished. Every detachable report carries four disclosure labels. No commit/push by workers. Two execution workers own disjoint benchmark namespaces; a separate reviewer owns only its oracle tests. Coordinator will verify and reaggregate results; no worker self-certification.
