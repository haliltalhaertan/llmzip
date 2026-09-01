# V52 Task 4F0 — Restricted-Cohort Refreeze Independent Audit

Date: 2026-08-31
Role: cold-start independent auditor (this audit supersedes the 17:16 same-day attempt in this folder — see §6)
Candidate namespace: `../audit_v52_t4f0_restricted_refreeze_2026_08_31/`
Candidate status audited: `PREPARED_NOT_INDEPENDENTLY_SEALED` (unchanged by this audit)

## Final verdict

`PASS WITH CONDITIONS — CANDIDATE MAY BE SEALED BY HEAD RESEARCHER`

All byte, cohort, leakage, invariance and raw-corpus gates passed in a locked environment that satisfies `DEPENDENCY_LOCK.txt` exactly. The independent sign-off is recorded here and in `INDEPENDENT_AUDIT_HASHES.json`. No retrieval-quality result, Native/Haar value, ANY@3/ALL@3/R@3 outcome, answer, rubric or evaluator output was opened, computed or used. The candidate namespace and every frozen 4C3/4D/4F0 artifact were left untouched. This audit does NOT authorize Task 4F1 preregistration or execution; that decision belongs to the Head Researcher.

## 1. Byte and scope gates — PASS

- Repository HEAD = `d3c7aa09c9553cd5ac100e668923abab602e4257` (branch `codex/research-lead-takeover-2026-08-31`), exactly the seal's `parent_llmzip_commit`. Working tree is dirty with the user-supplied audit/prompt/doc artifacts; recorded, not repaired.
- Pinned BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9` re-verified at the checkout used by this audit: HEAD match plus all four tier tree blob IDs equal to the values pinned in the original `V52_T4F0_INPUT_MANIFEST.json` (`a4c80e00…`, `4cb01a40…`, `ec11c8c9…`, `7023fb01…`).
- All 9 payload files re-hashed independently: sizes and SHA256 match `PAYLOAD_HASHES.json` and `CANDIDATE_SEAL.json` bindings (cohort `9b70e16f…`, protocol `f75e6c93…`, lock `86a4db44…`, preflight `185140ff…`, summary, composition, cardinality, exclusion list, README). `PAYLOAD_HASHES.json` itself hashes to the seal's `01298be2…` binding.
- Candidate namespace contains exactly the 11 declared files; no unbound payload.
- Accepted audit package inventory `../audit_v52_t4f0_codex_2026_08_31/AUDIT_OUTPUT_HASHES.json` hashes to `3b3bb1a25cd9c8b7a56e1c29afbe8b3589f0c5c5f4705c000b7625da6f64fa65`; its 33 payloads were verified byte-for-byte by the preflight.
- Candidate seal status is exactly `PREPARED_NOT_INDEPENDENTLY_SEALED`; unchanged.

## 2. Preflight — PASS (expected semantics)

Bundled runtime invocation (command log entry C4): exit 0, printed
`PASS: exact audit inventory, local payload closure, restricted cohort, exclusion rule, and no-outcome declarations verified`
followed by the expected `BLOCKED: independent sign-off and raw-corpus representation self-tests are still required`.

## 3. Cohort and estimand gates — PASS

Independent verification of `estimand_primary_cohort.csv` (not trusting the preflight):
- 2,000 rows, all `audit_question_id` unique; exactly 1,712 rows `primary_evidence_cohort_eligible=True`; denominator 1,712.
- Every eligible row: `audit_category=EXACT_SOURCE_IDS`, non-abstention `ability`, archive not in {`1M::5`, `1M::26`, `1M::33`, `1M::34`}, `gold_source_unit_count > 0`.
- Exclusion reason census: abstention 192, archive-duplicate 80, coarse 1, malformed 1, ambiguous 14 (2,000 − 288 = 1,712).
- 587 eligible questions with `gold_source_unit_count > 3`; all 587 carry `all_at_3_structurally_possible=False` (structural zero rule for ALL@3).
- Cardinality distribution in the CSV matches `estimand_summary.json` exactly; `tier_ability_composition.csv` sums to 1,712 and matches the summary per tier×ability; `gold_source_ids` lists are consistent with their counts (0 mismatches).
- CSV schema contains no question/answer/rubric/evaluator/outcome columns.

**Independent recomputation from the raw pinned corpus (chat.json + probing_questions.json):** eligibility bit and audit category reproduced for **2,000/2,000 rows**; `gold_source_ids` reproduced exactly for every row where a gold set is defined (1,928 rows). The remaining 72 rows are exactly the answerable questions of the four excluded 1M archives, for which the candidate deliberately zeroes the gold payload (`gold_source_ids=[]`) — the protocol forbids selecting an occurrence from divergent duplicate IDs, so no gold set is defined there. This is conservative, outcome-independent, and does not affect the denominator. Metric definitions in `REFREEZE_PROTOCOL.md` (§Metrics) are verbatim-consistent with the audit brief; aggregation is the arithmetic mean over 1,712 questions with seed/nuisance trials collapsed within question.

## 4. Memory key and data-defect boundary — PASS

The protocol preserves `BEAM_MESSAGE_ID_V1 = (tier, conversation_id, raw_message_id)` with memory text exactly `role + ': ' + content` and keys excluded from fitted text. Divergent duplicate keys in `1M::5/26/33/34` are handled by hard archive exclusion; no occurrence selection by lexical similarity, answer text, outcome, or first/last-seen rule exists anywhere in the candidate. An occurrence-qualified key is explicitly deferred to a separate data-repair task and is not silently merged into this estimand (protocol §Memory-unit, line 27).

## 5. Representation, environment, raw-corpus and invariance gates — PASS

Audit environment: isolated venv, Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, `PYTHONHASHSEED=0` — exact match to `DEPENDENCY_LOCK.txt` (asserted in-script). Note: the bundled Codex runtime does NOT satisfy the lock (NumPy 2.3.5; SciPy/scikit-learn/psutil absent); all compute gates therefore ran in the lock-satisfying isolated environment.

Raw-corpus access: the remediation workspace corpus copies of `100K/12`, `500K/12`, `1M/12`, `10M/1` `chat.json` were proven byte-identical to the pinned commit's raw git blobs (`git cat-file blob` extraction compared by SHA256, 4/4). Self-tests ran on those raw bytes only.

- **Raw-corpus archive-only self-test (sealed 4F0 implementation, SHA256-verified before import):** 4/4 PASS — `100K/12` 392 units, `500K/12` 1,120, `1M/12` 2,214, `10M/1` 19,895; mixed shape N×96, rank 96, zero NaN/Inf, correct query shape (1×96). Two independent repeats per archive: max abs archive diff 0.0, max abs query diff 0.0, and **SHA256 digests of C96 and query byte-identical across repeats**.
- **Signed-permutation control (synthetic, pre-outcome):** Hamming distance vectors exactly invariant; tie equivalence sets invariant; ranking under `(distance, tie_priority)` invariant; tie priority (SHA256 `V52_T4F0_TIE_PRIORITY_V1` construction) deterministic, label-independent, and independent of archive row order and source-list order by construction.
- **Centered continuous orthogonal invariance (real 100K/12 C96, Haar seed 43001):** max |Δdot| = 4.16e-16, max |Δnorm| ≤ 1e-12, max |Δgram| ≤ 1e-12 — within the 1e-12 tolerance.
- **Static/runtime leakage audit:** AST of the candidate's only Python file (`v52_t4f0_restricted_preflight.py`) shows no forbidden identifier and no fitting/ranking call; the candidate contains no fitting code. My audit scripts read `chat.json` structure and cohort metadata only — no gold, answers, rubrics, or source payload text entered any fit; the canary query is a fixed synthetic string.
- **Stop rule:** present in both `REFREEZE_PROTOCOL.md` (§Stop rule) and the seal (`stop_rule` field), forbidding every post-outcome change class listed in the brief.

## 6. Superseded prior attempt

A prior same-day audit attempt existed in this folder (files created 17:16–17:17, SHA256s recorded in `INDEPENDENT_AUDIT_HASHES.json` under `superseded_prior_attempt`). It concluded `BLOCKED` because its runtime lacked the locked dependencies (NumPy 2.3.5, no SciPy/scikit-learn/psutil, env vars unset). That environment blocker is remediated here by the isolated locked environment; its structural findings (inventory, cohort consistency) are consistent with this audit. Its files were replaced by the present, complete audit; nothing outside this folder was modified.

## 7. Conditions

1. **C1 — Execution implementation binding.** The candidate contains only the no-outcome preflight. Before any outcome-bearing 4F1 run, the fitting/ranking implementation must be produced and byte-bound (new seal/manifest update), per protocol line 40.
2. **C2 — Seal act belongs to the Head Researcher.** This audit produces the independent sign-off only; changing `CANDIDATE_SEAL.json` status is the Head Researcher's act.
3. **C3 — Lock-compliant environment.** Any future execution must run in a lock-satisfying environment (the bundled runtime is not lock-compliant).
4. **C4 — Authorization untouched.** `TASK 4F1 PREREGISTRATION` and `TASK 4F1 RUN` remain Head Researcher decisions; this audit grants neither.

## Evidence files (this folder)

- `GATE_TABLE.csv` — per-gate verdicts and evidence pointers
- `INDEPENDENT_AUDIT_HASHES.json` — SHA256 manifest of candidate payloads, evidence files and superseded prior attempt
- `COMMAND_LOG.txt` — audit command transcript
- `01_cohort_corpus_verify.py` + `audit_cohort_corpus_verify.json` — cohort/corpus verification
- `02_selftest_invariance.py` + `audit_selftest_invariance.json` + `selftest_console_log.txt` — raw-corpus self-test and invariance gates
- `03_leakage_ast.py` + `audit_leakage_ast.json` — static leakage audit
