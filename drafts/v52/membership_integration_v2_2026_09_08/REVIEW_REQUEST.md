# Independent review request — synthetic integration v2

Request only; no independent task is dispatched by this document.

Verify commit scope, payload inventory, pinned core/contracts and governing
source approval before behavior tests. Read README's OPEN section first. Review
only synthetic behavior, not real data or historical outcome artifacts. No seal,
HMAC, pilot, corpus reading, mutation of candidate, main or prior audits.

Check F1-F7 against audit5126766 with new reproductions; especially single-bit
zero canaries (including cancellation), actual placed-block mutations, full
coverage before fitting, error context and malformed IDs. Reproduce all three
top-k branches and priority reuse across six arms and ten seeds.

Check LoCoMo replacement, no empty fallback, no partial loss, fixed cohort,
historical field-presence bridge; LME lexical rank over all source IDs versus
primary-source-order shards. No raw correction files may be opened.

Trace synthetic input -> correction/ordinal -> representation -> scores -> core
bootstrap -> create-only output. Verify source/anchor provenance is honestly
marked unverified and outputs are not execution-ready. Probe output interruption
and overwrite behavior. Distinguish missing production finalizer from a completed
synthetic harness, and aggregate versus per-question historical anchor mismatch.

Report PASS/FAIL only for examined scope, classify open production obligations,
and write your own separate audit namespace. Implementation-team regression is
not independent acceptance. Any request to open real data must return to user.
