[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Coordinator review of integrity worker — interim

Worker report: integrity/HARD_AUDIT_INTEGRITY.md. This review is not independent of the commissioning coordinator. Other workers have not yet been consolidated. No source edits made.

## Directly checked
- Rehashed all 821 entries of SOURCE_SHA256_BEFORE.json: zero changed/missing files at this checkpoint. This detects changes; it does not prove write prevention or coverage of other source trees.
- LADDER_REALTALK.md still labels rank overflow as the cause, while DECISION_TESTS.md retracts it. Supersession pointer missing.
- Actual executed T3 script ablation_r2/perltqa/t3_ladder.py lines 186–188: sym uses signs on both sides; only qscale divides QC by sigma. Therefore sigma division cannot directly explain sym's decline. A specific causal mechanism remains unestablished.

## Worker conclusions not accepted without correction
- BM25: FINAL_STATE.md lines 117–118 explicitly says it needs raw text at query time. Standard indexed BM25 scoring needs postings/statistics, not original raw text. Returning document text or text-based reranking is a separate dependency. Worker section 6 item 4's OK does not resolve this false general claim.
- Cross-dataset correction: DECISION_TESTS.md lines 116–117 explicitly applies the 10.35 pp correction to every historical comparison table. A RealTalk delta cannot be transported to other cohorts or protocols. Worker item 5's 'NOT DONE' overlooks the sentence.
- Rerank: small post-rerank spread among tested first stages is not evidence that candidate recall is irrelevant; omitted relevant documents cannot be recovered by a reranker restricted to the pool. Worker item 3's broad acceptance is too permissive.
- Novelty: FINAL_STATE.md heading 'What is genuinely ours' and prior categorical claims are stronger than a bounded unsuccessful literature search licenses. Worker novelty acceptance is too permissive.
- A maximized BM25 result on seen labels needs selection caveats; conservative direction for a challenger does not establish correctness of a whole-program STOP decision.

## Pending
Worker reports 30/30 sampled manifest hashes and 14/14 blob matches, but these exact samples have not been independently rerun here. Manifest reportedly omits new decision files; quantify exact missing coverage in consolidation. Worker explicitly leaves roughly 130 remote refs and bulk historical code unreviewed. Its completion is not whole-project certification. Source artifacts remain unchanged until remaining audits are reconciled.
