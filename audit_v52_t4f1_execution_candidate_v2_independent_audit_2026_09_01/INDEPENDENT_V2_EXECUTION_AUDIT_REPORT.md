# V52 Task 4F1 — Execution Candidate V2 Cold-Start Independent Audit

Audit date: 2026-09-01  
Role: cold-start independent implementation auditor  
Candidate: `task4f1_execution_candidate_v2_2026_09_01/`

## Verdict

**BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1**

The V2 candidate correctly implements the D1 recursive closure and D2 HMAC authorization remediations, and it stamps and rejects mismatched D3 provenance as intended. Its retrieval representation and numerical method code are unchanged from V1, all outcome-free representation/method gates pass, and the current candidate remains fail-closed.

It may nevertheless not be sealed. Synthetic-only active tests found three unresolved checkpoint/finalization defects. Each can admit or destroy load-bearing result content while retaining the expected V2 provenance, so Gates 6–8 are blocked.

This verdict concerns only the exact audited bytes. It does not preregister, authorize, execute or interpret Task 4F1.

## Exact audited anchors

| Anchor | Independent observation | Decision |
|---|---:|---:|
| `v52_t4f1_beam_retrieval.py` | 56,142 bytes; `c50dfa7130918b8183c51edf68f5e2baac21a419f0d29bf2ec930f9de38e6139` | match |
| `PAYLOAD_HASHES.json` | 1,180 bytes; `9d7429893f50a729e4471684580660461e944e599c43df24172b2c4d1d66e22d` | match |
| `CANDIDATE_EXECUTION_SEAL.json` | 6,186 bytes; `4cc6313649da9ca4b10e64610a8ff40173c1ccacd663dda9fadabcdf059b996c` | match |
| `PREFLIGHT_HASHES.json` | 1,807 bytes; `976ef3d483e96d33177ab0287bd3665e22b7a87d3862997a7e9cde7faeb7f85b` | match |
| `IMPLEMENTATION_PREFLIGHT.json` | 3,564 bytes; `92618cf3acd3108534f7723126413f7d4664d85970eef7d05bbdc7aa7e2fee5c` | match |

The candidate status is exactly `PREPARED_NOT_INDEPENDENTLY_AUDITED`. The authorization-key commitment is exactly `PENDING_HEAD_RESEARCHER_PREREGISTRATION`.

Upstream anchors also match: llmzip HEAD `d3c7aa09c9553cd5ac100e668923abab602e4257`; BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`; accepted tree manifest `650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318`; Task 4F0 seal `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c`; protocol `f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1`; cohort `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`; and dependency lock `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`.

The cohort independently resolves to 2,000 rows, 1,712 eligible questions and 96 archives. The excluded set is exactly `1M::5`, `1M::26`, `1M::33`, `1M::34`.

## Gate decisions

### Gate 1 — recursive byte closure: PASS

Recursive enumeration found exactly eight files: six manifest payloads plus `PAYLOAD_HASHES.json` and `CANDIDATE_EXECUTION_SEAL.json`. All bytes, sizes and hashes match both bindings; there are no nested files and no `__pycache__`. The package preflight passed on the exact candidate. In a temporary copy, a nested unbound file caused `candidate_package_preflight.py` to reject the package. The temporary copy was removed.

### Gate 2 — V1-to-V2 change isolation: PASS

AST comparison shows that representation, query transformation, ranking, signed permutation, Haar, ITQ, metrics, trial emission, tie priority, canary and synthetic method functions are unchanged from V1. Changed functions are confined to HMAC authorization and V2 seal/schema handling, provenance construction/stamping/validation, and the call-site/schema wiring those changes require. No numerical or estimand change was found.

### Gate 3 — static and runtime leakage: PASS

`fit_archive_representation` accepts only `memory_texts`. The archive fit receives only archive memory text; query and gold data are loaded separately and do not enter fitting, mean, rotations, thresholds, tie priority, seeds or archive selection. ITQ receives `centered_archive` only. Tie priority accepts only archive ID and memory key and has no trial or outcome input. No runner print call emits retrieval IDs, distances or metrics.

Runtime method instrumentation used synthetic inputs only. The real preflight canary opened `chats/100K/12/chat.json` and used the fixed canary query; it opened no probing-question file, loaded no gold label, performed no ranking and computed no retrieval-quality metric.

### Gate 4 — representation and method equivalence: PASS

The exact locked environment was Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1 and psutil 7.0.0 with all four thread variables set to `1` and `PYTHONHASHSEED=0`.

The 128×96 synthetic representation was finite and rank 96. Signed permutations preserved Hamming distances and ranking exactly. The maximum independent Haar continuous/orthogonality error was `3.197442310920451e-14`, below `1e-12`. ITQ orientation matched an independent implementation byte-for-byte for every seed; maximum orthogonality error was `1.6653345369377348e-15`. Fixed tie ordering and canonical-index fallback passed. Twenty trial rows were identical except for the trial identity. The structural fixture returned fractional `0.75`, ANY `1`, ALL `0`.

The independently reconstructed outcome-free `100K::12` canary produced:

- archive: `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025`
- fixed query: `e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`

The canary query was not ranked.

### Gate 5 — authorization control D2: PASS

The authorization verifier enforces the exact closed signed-field set; canonical newline-terminated sorted compact JSON; HMAC-SHA256; constant-time `hmac.compare_digest`; exact script, candidate seal, cohort, archive count, output basename, preregistration seal, authorization ID and nonce bindings; a 32-byte key; and SHA256 key-commitment equality.

The current non-hex commitment fails closed before any key read. With `V52_T4F1_AUTH_HMAC_KEY_HEX` absent, the shipped template blocked on its invalid authorization fields and the supplied structurally complete negative fixture blocked with `[BLOCKED - HEAD RESEARCHER AUTHORITY KEY NOT SEALED]`. No passing HMAC fixture was constructed. Authorization verification occurs before corpus verification/ranking and before output-directory creation.

This is a byte-bound governance control. It is not protection against an attacker who can replace both the audited script and accepted seal outside the evidence chain.

### Gate 6 — checkpoint provenance D3: BLOCKED

The intended D3 mechanics pass in isolation. Synthetic metadata carrying the exact script, cohort, authorization and candidate-seal hashes is accepted; changing any one hash blocks. Incomplete, CSV-hash-mismatched and stale V1 checkpoints block. The final manifest repeats all four provenance values. Existing archive files and an existing post-run manifest block overwrite.

Three defects remain:

1. **B1 — blocking: derived finalization CSV overwrite.** `finalize_results` checks only whether the post-run manifest exists. `write_csv` then uses `os.replace` for the question-seed, question and aggregate CSVs without first rejecting an existing destination. A synthetic pre-existing question-seed result was silently replaced when the manifest was absent. This violates the explicit “existing results are never silently overwritten” gate and makes crash/partial-finalization recovery unsafe.

2. **B2 — blocking: metrics are not recomputed from frozen gold.** The finalizer parses three retrieved IDs and validates metric ranges and a few logical relations, but does not intersect those IDs with `gold_source_ids_parsed` and recompute fractional/ANY/ALL. A synthetic checkpoint retrieving IDs `9,8,7` while claiming `0.75/1/0` against frozen gold `1,2,3,4` was accepted and finalized. The metadata CSV hash is self-stamped and does not prevent this semantic substitution.

3. **B3 — blocking: exact Native/signed-control equality is not revalidated.** Archive evaluation checks exact signed-permutation distance/ranking invariance, but the finalizer checks only equality of question-level metrics. A synthetic signed-control top-three order different from Native, with unchanged metrics, was accepted and finalized. Thus a resumed checkpoint can bypass the load-bearing exact-control invariant.

### Gate 7 — aggregation and interpretation: BLOCKED

The synthetic structural path correctly enforced a 320-row question, 20 trial identities per method/seed, 16 question-seed rows, four question-method rows, four aggregate rows, three unique IDs, sorted integer Hamming distances, metric ranges, structural ALL@3 zero and equal weighting at the question level. Native/signed metric equality passed.

Gate 7 is still blocked by B2 and B3: structural validity is not sufficient when the finalizer can accept metrics inconsistent with the frozen gold and can accept exact-control top-three divergence. The future preregistration must explicitly state that trials 0–19 are deterministic replication identities, not independent samples, but no preregistration may be created until a repaired candidate passes a fresh audit.

### Gate 8 — active bug hunt: BLOCKED

B1–B3 are reproducible sealing blockers. One non-blocking defense-in-depth observation remains: the protocol deliberately binds the output basename rather than a full normalized path, and concurrent external mutation between verification and later reads is outside the byte-chain assumption. This should be documented and, if practical, reduced by holding verified bytes or descriptors. It does not replace the three blocking repairs.

No cross-archive fit cache exists; each archive representation is local to one `evaluate_archive` call. No denominator, seed, threshold, arm, rotation, ITQ or tie drift was found.

## Required remediation before another audit

A new candidate must, without changing scientific semantics:

1. refuse finalization if any derived output destination or temporary path already exists, or implement a separately sealed atomic staging/commit protocol that never silently replaces prior results;
2. recompute all three metrics from the frozen per-question gold set and retrieved IDs during finalization, and reject any mismatch;
3. enforce exact Native-versus-each-signed-control equality for retrieved top-three IDs and distances at every question/seed/trial cell during finalization;
4. regenerate the recursive inventory, candidate seal and preparation evidence for the new bytes, then undergo a fresh cold-start independent audit.

The current candidate, seal and all upstream namespaces were left unmodified.

## No-outcome boundary accounting

- `--mode run` invocation count: `0`
- `--mode finalize` invocation count: `0`
- HMAC key environment variable set count: `0`
- valid production authorization constructed: `false`
- real retrieval ranking performed: `false`
- retrieval-quality computed/read/reported: `false/false/false`
- candidate bytes modified: `false`

The prior auditor’s accidental partial execution and its “26 archives” observation were not used as evidence for any gate.

## Final decision

**BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1**
