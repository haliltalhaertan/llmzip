# V52 Task 4F0 — Codex Cold-Start Independent Audit

Audit date: 2026-08-31  
Audit posture: zero trust; scientific retrieval outcomes sealed and uninspected

TASK: V52 TASK 4F0 — CODEX INDEPENDENT AUDIT  
VERDICT: [PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE]  
AUDIT LEVEL: FULL PINNED-CORPUS MATERIALIZATION, BYTE/REVISION PROVENANCE, EXHAUSTIVE SOURCE-ID JOIN, REAL-DATA REPRESENTATION REPEATABILITY; NO RETRIEVAL-OUTCOME ACCESS  
UPSTREAM COMMIT IDENTITY: PASS  
FULL CORPUS MATERIALIZED: YES  
CONVERSATIONS ENUMERATED: 100  
PROBING QUESTIONS ENUMERATED: 2000  
EXACT SOURCE QUESTIONS: 1743  
COARSE SOURCE QUESTIONS: 1  
ABSTENTION QUESTIONS: 200  
AMBIGUOUS/MISSING SOURCE QUESTIONS: 55 (plus 1 MALFORMED/CONTRADICTORY)  
SOURCE-ID JOIN: FAIL FOR THE FULL INTENDED COHORT; PASS FOR THE FROZEN RESTRICTED COHORT  
UNMATCHED SOURCE IDS: 0  
AMBIGUOUS SOURCE IDS: 198  
DUPLICATE MEMORY KEYS: 1720  
FRACTIONAL SOURCE EVIDENCE R@3 IDENTIFIABLE: RESTRICTED  
ANY@3 IDENTIFIABLE: RESTRICTED  
ALL@3 IDENTIFIABLE: RESTRICTED  
REPRESENTATION TRANSFER: PASS ON CLEAN ARCHIVES  
LEAKAGE GATE: PASS  
100K FEASIBLE: YES  
500K FEASIBLE: YES  
1M FEASIBLE: YES ON RESTRICTED CLEAN ARCHIVES; FULL EVIDENCE COHORT SEMANTICALLY BLOCKED  
10M FEASIBLE: YES  
MAX QUANTIFIED DEFECT EFFECT: 4/100 archives contain 1,720 divergent duplicate memory keys; a safe primary cohort excludes 288/2,000 total questions (88/1,800 answerable), leaving 1,712. No Native-vs-Haar effect was computed.  
TASK 4F1 MAY BE PREREGISTERED: NO  
SCIENTIFIC NATIVE-vs-HAAR OUTCOME INSPECTED: NO

## 1. Chain of custody and temporal integrity

- Canonical project branch `main` was cloned independently. The current observed head was `d3c7aa09c9553cd5ac100e668923abab602e4257`. The Task 4F0 repository prompt first appears in commit `fe0816e1f874ff0146e29d001d4eefc3ccf1adad` (2026-08-29 19:18:44 +03:00); its parent is `599b9e7bb13fd5d9f19ea8e378fef0d7273ad2b6`. The prompt file has no later content-changing commit in the observed history.
- The pinned BEAM identity was independently matched to commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`. The recursive tree response named this commit and was not truncated. Every selected blob was also checked against its Git blob SHA-1.
- The Drive Task 4F0 folder exposed 15 artifacts. Exact fetched bytes independently reproduced the claimed input-manifest SHA-256 `5bccceb575952e541e576b65bb010708dc23e5d231b950f2b3eea779ccf3f6c3` and adapter SHA-256 `b8056aa1eb0445eef12c5a3f78d8c596d06922b2a508bbe88125e161bdb36a57`. All hashes listed in the output-hash file matched the retrieved bytes.
- Drive revision metadata showed one revision for the manifest, adapter, and output-hash artifact. The original prompt document had two revisions before the Task 4F0 folder/artifacts were created. No evidence of a post-result adapter, mapping-rule, memory-unit, or eligibility rewrite was found.
- Residual control gap: the manifest's `task_prompt_sha256` (`5d4a4f...`) could not be reproduced from the present repository prompt bytes, its LF-normalized variant, the Google Docs text export, or paragraph-join variants. This is a provenance/documentation defect, not evidence that outcome-facing code changed. Exact original prompt bytes must be preserved in any refreeze.

## 2. Full-corpus inventory

The audit materialized 205 pinned files: 100 `chat.json`, 100 `probing_questions.json`, and five relevant upstream source/documentation files. All 205 passed download SHA-256 and Git-blob SHA-1 checks; verified bytes total 804,231,963. The README's “128K” tier is stored under the repository's `100K` directory, so this report uses the on-disk tier name.

| Tier | Conversations | Questions | Raw message units | Messages min / median / mean / max | Chat bytes | Question bytes | 96-bit code bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| 100K | 20 | 400 | 5,732 | 188 / 271 / 286.600 / 392 | 13,270,456 | 625,203 | 68,784 |
| 500K | 35 | 700 | 38,058 | 772 / 1,076 / 1,087.371 / 1,424 | 84,444,964 | 1,150,522 | 456,696 |
| 1M | 35 | 700 | 74,630 | 1,556 / 2,088 / 2,132.286 / 3,008 | 173,756,699 | 1,373,024 | 895,560 |
| 10M | 10 | 200 | 208,696 | 18,760 / 20,075 / 20,869.600 / 23,716 | 528,409,169 | 369,386 | 2,504,352 |
| Total | 100 | 2,000 | 327,116 | 188 / 1,247 / 3,271.160 / 23,716 | 799,881,288 | 3,518,135 | 3,925,392 |

There are only 35 distinct raw conversation-number values because numbering resets across tiers; `(tier, conversation_id)` yields 100 unique archives. Token counts are **UNVERIFIED**: no tokenizer was frozen or used, and no estimate is presented as a fact.

The pinned files substantiate the README totals. Each of the ten public abilities occurs exactly 200 times overall and exactly twice per conversation: `abstention`, `contradiction_resolution`, `event_ordering`, `information_extraction`, `instruction_following`, `knowledge_update`, `multi_session_reasoning`, `preference_following`, `summarization`, and `temporal_reasoning`.

## 3. Evidence and source-ID census

| Tier | Exact | Coarse | Abstention | Ambiguous/missing | Malformed |
|---|---:|---:|---:|---:|---:|
| 100K | 355 | 0 | 40 | 5 | 0 |
| 500K | 629 | 1 | 70 | 0 | 0 |
| 1M | 584 | 0 | 70 | 46 | 0 |
| 10M | 175 | 0 | 20 | 4 | 1 |
| Total | 1,743 | 1 | 200 | 55 | 1 |

For the 1,743 exact-source questions, the sum of unique explicitly supplied IDs per question is 9,913. Across the raw reference occurrences, 10,240 IDs matched, none were unmatched, 198 were ambiguous, and 77 duplicate source-reference occurrences were observed. No answer text or rubric was used to infer or repair a locator.

The public `source_chat_ids` values are message-level identifiers: they join to individual message `id` fields inside the question's conversation archive. They are not globally unique. Tier plus conversation is necessary, but not sufficient for four archives.

### Confirmed upstream collision mechanism

Four 1M archives contain duplicate raw IDs:

| Archive | Duplicated ID interval | Duplicate key values |
|---|---:|---:|
| `1M::5` | 0–149 | 150 |
| `1M::26` | 0–423 | 424 |
| `1M::33` | 0–205 | 206 |
| `1M::34` | 0–939 | 940 |
| Total | — | 1,720 |

Every duplicated ID occurs twice. All 1,720 pairs have the same role but different content; zero are byte-identical duplicates. They make 198 supplied source IDs ambiguous across 41 questions.

The pinned generator explains the defect. `src/beam/main.py` lines 1796–1804 initializes `id = 0`, then loads existing messages when resuming, but does not restore `id` to a value after the loaded maximum. Lines 1920–1935 assign and increment this reset counter for new user/assistant messages. Thus resumed batches can reuse earlier IDs. Adding an audit-only ordinal would uniquely identify memory rows, but the public annotations still would not identify which duplicate occurrence was intended. Choosing by answer/lexical similarity would invent labels and violate the stop rule.

### Estimand identifiability

Result: **[PARTIALLY IDENTIFIABLE — DEFINE RESTRICTED COHORT]**.

Outcome-independent primary rule:

> Include only non-abstention questions classified `EXACT_SOURCE_IDS` whose entire conversation archive has unique `(tier, conversation_id, raw_message_id)` keys.

This yields 1,712 primary questions. Exclusions are: 192 clean-archive abstentions; all 80 questions from `1M::{5,26,33,34}`; one coarse annotation; one malformed annotation; and 14 other answerable ambiguous/missing annotations. Coverage is 95.111% of all 1,800 answerable questions and 99.074% of answerable questions in clean archives. The restriction is not perfectly representative: it removes 4/35 (11.43%) of the 1M archives and disproportionately removes some summarization/missing-source records. Tier and ability counts are frozen in `estimand_summary.json` and the row-level cohort table.

Fractional Source Evidence R@3 and ANY@3 are identifiable on this restricted cohort. ALL@3 is also mathematically identifiable, but 587/1,712 questions have more than three gold units and are therefore structurally zero at `k=3`. Any alternate cardinality restriction would be a new, separately preregistered estimand; it must not be chosen after viewing retrieval results.

## 4. Frozen representation-transfer audit

Result: **REPRESENTATION TRANSFER: PASS ON CLEAN ARCHIVES**.

The independent implementation preserved the frozen family: memory text `role + ': ' + content`; lowercase word TF-IDF 1–2 grams with English stop words and sublinear TF; `char_wb` TF-IDF 3–5 grams with sublinear TF; latent32 randomized SVD (`random_state=5101`); concatenated source block; mixed96 randomized SVD (`random_state=5204`); L2 normalization; archive mean centering; and query transform only after archive fitting.

One largest clean archive per tier was fitted twice in separate processes with `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, and psutil 7.0.0. All archive and neutral-canary query SHA-256 values matched bit-for-bit between A/B runs. All mixed matrices were `n × 96`, rank 96, finite, and free of NaN/Inf.

| Tier/archive | Units | Word matrix / nnz | Char matrix / nnz | Source block | Archive hash A=B | Query hash A=B |
|---|---:|---:|---:|---:|---|---|
| 100K/12 | 392 | 392×37,872 / 98,432 | 392×34,739 / 685,432 | 392×72,643 | `25089a07760a…` | `261cf4a8aa67…` |
| 500K/32 | 1,424 | 1,424×126,973 / 384,567 | 1,424×65,032 / 2,554,608 | 1,424×192,037 | `4316647503f2…` | `dd87a69b997d…` |
| 1M/25 | 3,008 | 3,008×202,541 / 806,791 | 3,008×76,591 / 5,324,816 | 3,008×279,164 | `c1a5603ac97a…` | `2e4a598d02c2…` |
| 10M/10 | 23,716 | 23,716×953,939 / 5,521,349 | 23,716×183,615 / 37,270,009 | 23,716×1,137,586 | `b0d157898ba1…` | `978d0f4dbd78…` |

Leakage gate: **PASS**. Archive fitting received only raw message role/content. The canary query was transformed after fit. No benchmark question, answer, rubric, type, `source_chat_ids`, source label, or retrieval outcome was supplied to representation fitting. No ranking, Native transform, Haar transform, top-k retrieval, or retrieval metric was executed.

The four defective 1M archives are excluded for memory-key/evidence semantics, not because their text cannot be vectorized. Running them in a scientific cohort would change the intended memory-unit identity and make gold joins ambiguous.

## 5. Scale feasibility

Measured values below are for the largest clean archive in each tier, not whole-tier simultaneous fitting. Code storage is the exact packed 96-bit payload only (`12 × units`); it is not a RAM estimate.

| Tier | Corpus units / exact code bytes | Measured archive | A/B time range | Peak RSS range | Feasibility |
|---|---:|---:|---:|---:|---|
| 100K | 5,732 / 68,784 | 392 | 3.399–3.600 s | 372,965,376–375,070,720 B | PASS |
| 500K | 38,058 / 456,696 | 1,424 | 13.449–17.003 s | 785,649,664–786,702,336 B | PASS |
| 1M | 74,630 / 895,560 | 3,008 | 28.605–31.328 s | 1,133,256,704–1,136,205,824 B | PASS on restricted clean archives |
| 10M | 208,696 / 2,504,352 | 23,716 | 179.768–271.995 s | 4,671,946,752–4,690,042,880 B | PASS |

At 10M, `char_wb` is the storage/RAM driver (37.27 million nonzeros), while mixed96 randomized SVD is the largest stable compute stage (about 100–102 seconds in the measured runs); char fitting varied more (about 52–113 seconds). Both must be treated as operational bottlenecks. The measurements show local feasibility, but a future seal should state a RAM floor above the observed 4.69 GB process peak and include contingency for sparse-matrix overhead.

## 6. Adversarial defect table

| Hypothesis / defect | Status | Evidence | Effect |
|---|---|---|---|
| Pinned data do not substantiate 100/2,000 | REFUTED | 100 chat files and 100 question files enumerate exactly 2,000 questions; all selected blobs verified | README claim is data-supported |
| Large tiers are publicly inaccessible | REFUTED | All 205 selected pinned files materialized; 804,231,963 bytes verified | No access blocker remains |
| Public annotations remain fundamentally insufficient for the full cohort | CONFIRMED | 55 ambiguous/missing, 1 coarse, 1 malformed; four archives have divergent ID collisions | Full-cohort evidence estimand cannot be frozen as originally keyed |
| `source_chat_ids` are conversation-level rather than message-level | REFUTED | Values join individual message `id` fields; separate conversation-reference fields are coarse | Message-level semantics confirmed |
| IDs reset/collide beyond repair by `(tier, conversation,id)` | CONFIRMED | 1,720 divergent duplicate keys in four 1M archives; upstream resume logic resets counter | 198 gold IDs / 41 questions ambiguous; exclude entire archives unless upstream publishes authoritative repair |
| Exact-source cohort exists only for a narrow taxonomy subset | REFUTED WITH QUALIFICATION | Every non-abstention ability remains represented in the 1,712-row cohort | Coverage is broad, but exclusions are tier/type-skewed |
| Restricted cohort is too small | REFUTED | 1,712 rows = 95.111% of all answerable questions | Adequate size; composition must be reported |
| Frozen representation needs a method change | REFUTED on clean archives | Real-data rank/finite/dimension checks pass; A/B hashes bitwise equal | No representation-family change needed |
| Prior “incomplete verification, no contradiction discovered” remains the final diagnosis | REFUTED BY NEW EVIDENCE | Full materialization exposed a real upstream key contradiction | Prior stopping decision remains correct; diagnosis must be updated |
| Post-outcome artifact editing compromised the method | REFUTED WITH RESIDUAL GAP | Single-revision core artifacts and matching hashes; no change found | Prompt-byte digest provenance still needs repair |

The maximum quantified data defect is not a scientific effect size. It is 1,720 divergent duplicate memory keys in 4/100 archives, producing 198 ambiguous source-ID joins over 41 questions. The safe cohort removes 288/2,000 total questions, including 88/1,800 answerable questions. Native-vs-Haar outcomes were not opened, computed, estimated, or compared.

## 7. Final scientific and governance recommendation

The original `BLOCKED — DO NOT RUN TASK 4F1` action was scientifically correct: the earlier evidence did not justify a full-cohort run. Full materialization now eliminates the access/scale uncertainty but reveals a genuine upstream identity defect, so the original full-cohort key cannot be declared ready.

The blocker is nevertheless resolvable without inventing labels: Head Researcher may prepare a new 4F0 refreeze using the exact 1,712-row restricted cohort. Before Task 4F1 may be preregistered, that refreeze must lock all of the following without inspecting outcomes:

1. exclusion of entire archives `1M::{5,26,33,34}` and the exact row-level cohort supplied here;
2. the denominator and formulas for Fractional R@3, ANY@3, and ALL@3, explicitly retaining the structural-zero behavior for gold cardinality above three unless a different estimand is separately justified in advance;
3. the memory-unit text/key, package versions, single-thread environment, random states, and audit-script hashes;
4. exact prompt bytes and a reproducible prompt SHA-256 chain;
5. reporting of tier/ability composition and the restricted-cohort qualification.

Until that governance action is completed, `TASK 4F1 MAY BE PREREGISTERED: NO`. Task 4F1 was not run. The primary verdict is therefore **[PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE]**.

