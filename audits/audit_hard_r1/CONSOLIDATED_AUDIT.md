[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Hard audit consolidation — four Muse workers

## Verdict
The examined recent-pilot numerical results largely reproduce. Interpretation, causal attribution, comparison fairness, documentation and portability require correction. The evidence does NOT justify closing the whole llmzip project. A recommendation to pause this specific TF-IDF/SVD-sign-versus-lexical optimization line is distinct from owner approval or a verdict on other research lines. This is a sampled audit, NOT a whole-project certificate.

All four worker reports exist: numbers/HARD_AUDIT_NUMBERS.md, integrity/HARD_AUDIT_INTEGRITY.md, repro/HARD_AUDIT_REPRO.md, claims/HARD_AUDIT_CLAIMS.md. Preserve them unchanged alongside coordinator reviews. Same-CLI workers provide partial independence, not independent-family certification.

## Evidence and scope
- Numbers worker reports 101/101 checks exact/within tolerance: all four RealTalk BM25 variants (705 queries), 164256 T2 rows and 15 bootstrap contrasts, 2/10 RealTalk archives freshly rebuilt plus full cache reaggregation, all eight small PerLTQA archives rebuilt.
- Coordinator independently reaggregated eight T3 worker outputs: 2217 queries, 18 scalar values; max discrepancy 2.1316282072803006e-14 pp.
- Reproduction worker reports T1 20/20 exact cells, two-archive T3 sign gate 0/61056, and 38/38 sampled seal negative controls. These do not certify F1/KV/inverse/core code generally.
- Latest rehash of the original publication snapshot: 821 files; zero changed or missing. No claim of immutability enforcement or coverage of other trees. No production repairs or remote publication performed by this audit consolidation.

## Priority findings
1. Project-wide STOP was an overreach. Local measured deficits cannot dispose unreviewed dense/E1/residual/F1/KV/inverse lines. The user has not approved closure.
2. SIGN-versus-FLOAT headline depends on comparator. Claims worker measures standardized float Hit@10 48.51 versus sign about 46.81 under its alternate tie rule. Historical protocol reports sign 46.52. Do not mix those as exact matched-protocol differences. The roughly +10 pp advantage over unstandardized float is not a general benefit of losing magnitudes; standardized float must accompany the claim.
3. Sigma division is absent from sym. Its falling high-width result cannot be explained directly by sigma division. Near-singular/noisy directions and query binarization remain hypotheses, not established causal replacements.
4. Rerank retains a candidate-recall bottleneck at depth 50. Similar post-rerank means do not prove first-stage optimization irrelevant.
5. BM25 indexed scoring does not require original raw text at query time. Text return and text reranking are separate dependencies.
6. The RealTalk +10.35 pp setting difference cannot be applied to other benchmarks. Best-of-four IDF-only lexical maximum 65.67 is in-sample selection; textbook-parameter BM25 with frozen tokenizer is 61.70 and still exceeds 48-byte qscale 57.87 in RealTalk Hit@10. The observed 3.97 pp setting difference is not an estimate of statistical selection bias.
7. C1 implementation checks only a +2 pp point estimate; its description additionally requires CI and both benchmarks. This cannot certify PASS as written; current negative differences already fail a necessary condition. Joint gate/results commit does not establish pre-registration; labels explicitly say NOT PREREGISTERED.
8. Stale rank-overflow explanation lacks a supersession banner. Historical manifest omits new decision artifacts. Actual T3 producer exists and is named in DECISION_TESTS.md; the retained failed producer needs a noncanonical label, not a claim that the true producer is missing.
9. Hard-coded paths/output destinations and missing setup instructions undermine portability. Some corresponding inputs DO exist in the package. No clean-room package-only execution was performed: do not report an executed universal package failure.
10. Literature absence does not prove novelty; six 'genuinely new' labels are unsupported by this audit.

## Claims-worker review and limits
The claims worker's code au_c1_itq.py explicitly changes tie handling to stable document index and calibrates sym only approximately. It fits ITQ once with default seed 20260916, then varies seven RANDOM-rotation seeds; it does NOT vary seven ITQ initializations. Its phrase 'pre-registered-fresh seeds' is unsupported and inconsistent with exploratory labels. Treat this as one ITQ solution versus a fresh random-control distribution, not a completed multi-initialization ITQ robustness study.

Reported direction: RealTalk qscale ITQ remains below all seven fresh random controls; PerLTQA qscale small deficit is comparable to random-control seed variation, while sym reverses direction under the worker's alternative tie protocol. Do not quote 'ITQ always loses' or treat changed-protocol numbers as exact replications. An alternative seed result alone is not a population inference.

Size/harm association remains negative in the worker's Hit@10 sensitivity analyses but is weaker for FR@3. Pearson differs with aggregation (-0.80 vs cited -0.78); balance extrema likewise differ by seed/aggregation. Preserve these discrepancies rather than calling every anchor exact. Median threshold balancing did not yield retrieval gains, but it also changes query thresholds; it is not a pure causal balance intervention.

Reject worker causal wording that asserts trailing directions are noise without an identifying test. Reject its unresolved raw-text requirement as a deployment question: scoring from postings/statistics is a separate technical dependency from document display. Reject universal-history claims based on RealTalk alone. A correct local failure does not settle the broader stopping decision.

## Coverage still open
Approximately 130 remote-tracking refs and bulk historical bodies were not reviewed in depth. E1/geometry/residual/F1/dense bodies, KV/inverse internals, complete frozen contracts, cost/latency reproduction, and primary literature verification remain unreviewed or only named. Full fresh RealTalk ladder reconstruction covered 2/10 archives. LME completion/liveness not established in this audit. Reports contain incremental pending checklists; final coverage sections, actual artifacts and explicit NOT RUN entries govern.

## Recommended disposition
Freeze claims at the demonstrated scope. Next work, if commissioned, should first correct documentation and make an isolated portable replay package, then cover unreviewed project branches before deciding project-wide direction. Do not silently rewrite historical evidence. No new optimization sweep or source modification was authorized by this report itself.
