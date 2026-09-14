[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# EVASION COUNT SCOPE NOTE (PREPARED, NOT ACCEPTED — explanatory only; no existing file touched)

## The apparent conflict (all three statements VERIFIED)

- CLAIM (V6 report §1, `/tmp` copy lines 38–39 of `origin/audit/v52-t4f1-v6-independent-2026-09-03:…/INDEPENDENT_V6_EXECUTION_AUDIT_REPORT.md`): "Of 36 adversarial probes, **25 evasions succeeded**".
- CLAIM (V6 report §6, line 300): "Tested with 36 fixtures of my own construction (`evidence/probe_batch1-4.json`), including a positive control".
- VERIFIED (independent count): `GATE_TABLE.csv` has 82 rows, of which **31** carry result `FAIL - EVASION SUCCEEDED` (receipt: `receipts/V6_GATE_TABLE.csv`).
- CLAIM (`ops/CURRENT_STATE.json:36`): "31 evasions succeeded against the inverted-burden gate".
- CLAIM (L-018, `docs/CONTINUITY_LEDGER.md:332`): "31 evasions were reported."

## Evidence denominator (VERIFIED from the audit's own JSONs)

`evidence/probe_batch{1,2,3,4}.json` contain 10 + 15 + 20 + 7 = **52** fixtures. Counting `expected_block=true AND blocked=false` per file: batch1 1, batch2 14, batch3 11, batch4 5 → **31**, exactly the GATE_TABLE evasion rows. So the table's 31 is the union over all four batches.

## Reconciliation: both numbers are correct in their own scope

"36 adversarial probes / 25 evasions" scopes to **batches 2+3 plus the positive control**: batch2 (15 fixtures) + batch3 (20 fixtures) = 35 adversarial + G1 control = **36 fixtures**; evasions therein = 14 (batch2) + 11 (batch3) = **25**. Remainder: batch1's 10 V5-regression/closure-confirmation fixtures (9 blocked, 1 evasion: 3.1e) + batch4-minus-G1's 6 declaration-integrity fixtures (1 blocked: G4; 5 evasions: G2, G3, G5, G6, G7) = 16 fixtures, 6 evasions. Check with zero remainder: 36 + 16 = **52** total; 25 + 6 = **31** table evasions; non-evasions 21 = 10 (B2 + E1, E2, E3, E4, E6, F1, F2, F3, F4) + 9 (batch1 blocked) + G1 + G4. Every fixture is accounted for exactly once.

Scope reading (inference, labelled): the report's "adversarial probes" = the auditor's novel attacks on the sweep and its configuration (hex-adjacency, re-encodings, exempt-class abuse, short-value drifts, disarms, attestation redirect — batches 2–3); batches 1 and 4 are regression/confirmation (V5 escapes now caught, novel-token closure checks) and declaration-integrity checks (mirror/value/claim verification). Alternative hypothesis recorded honestly: the prose "36" may be stale relative to extended batches — but the exact zero-remainder partition above is the reason to prefer the scoping reading. A competing check the Head Researcher can run: re-derive the partition from `evidence/probe_batch*.json` (`blocked` / `expected_block` fields).

## All 31 rows, classified (P = probe-evasion: planted/mutated content passes undetected; M = mechanism-level defect: the gate's own configuration/trust permits it)

| # | row (gate | check) | class | batch |
|---|---|---|---|
| 1 | G3 | 3.1e novel 64-hex in a NEW file added to the closure | P (closure-scope expansion) | 1 |
| 2 | G3 | A1 novel 64-hex preceded by hex-ending word ('probe') | P (normalisation/lookaround) | 2 |
| 3 | G3 | A2 novel 64-hex followed by hex-starting word ('and') | P | 2 |
| 4 | G3 | A3 LIVE cohort digest relocated, hidden by hex-adjacent prose | P | 2 |
| 5 | G3 | B1 deprecated literal split by ZERO WIDTH SPACE | P (re-encoding) | 2 |
| 6 | G3 | B3 deprecated literal interleaved with HTML comment markup | P (re-encoding) | 2 |
| 7 | G3 | B4 deprecated literal re-encoded as base64 | P (re-encoding) | 2 |
| 8 | G3 | B5 deprecated literal re-encoded as decimal integer | P (re-encoding) | 2 |
| 9 | G3 | B6 deprecated literal split across two JSON keys | P (re-encoding) | 2 |
| 10 | G3 | B7 deprecated literal inside bound non-UTF-8 payload (silent skip) | P (skip without counting) | 2 |
| 11 | G3 | B8 literals inside DETACHED ATTESTATION (outside closure) | P (unswept location) | 2 |
| 12 | G3 | C1 digest smuggled into PAYLOAD_HASHES files[] non-digest key | M (exempt-class overbreadth) | 2 |
| 13 | G3 | C2 digest under `supersedes_candidate_addendum` (prefix widening) | M (string-prefix matching) | 2 |
| 14 | G3 | C3 digest under payload_inventory.smuggled (exempt subtree) | M (exempt-class overbreadth) | 2 |
| 15 | G3 | C4 sealed-4F0 namespace swapped via identifier allowlist | M (allowlist overbreadth) | 2 |
| 16 | G3/G4/G7 | D1 denominator 1712 → 1713 | P (short value outside token shapes) | 3 |
| 17 | G3/G4/G7 | D2 excluded archive 1M::5 → 1M::7 | P | 3 |
| 18 | G3/G4/G7 | D3 arm NATIVE_SIGN96 → NATIVE_SIGN97 | P | 3 |
| 19 | G3/G4/G7 | D4 Haar seed 43001 → 43011 | P | 3 |
| 20 | G3/G4/G7 | D5 tolerance 1e-12 → 1e-10 | P | 3 |
| 21 | G3/G4/G7 | D6 latent seed 5101 → 5102 | P | 3 |
| 22 | G3/G4/G7 | D7 canary threshold '>= 0' → '> 0' | P | 3 |
| 23 | G3/G4/G7 | E5 blanket exempt class excuses everything | M (self-disarmable config) | 3 |
| 24 | G3/G4/G7 | E7 unattributed digest hidden inside fields block | M (declaration-site hiding) | 3 |
| 25 | G3/G4/G7 | E8 deprecated disarmed via must_not_appear_as_requirement=false | M (disarm by declaration) | 3 |
| 26 | G3/G4/G7 | F5 attestation redirected INSIDE candidate namespace | M (unbound, redirectable attestation) | 3 |
| 27 | G5/G7 | G2 declared mirror emptied of its value | M (mirrors unverified) | 4 |
| 28 | G5/G7 | G3 phantom mirror on file that never held the value | M (mirrors unverified) | 4 |
| 29 | G5/G7 | G5 concept value drifts, scannable_literals stay correct | M (declaration unverified) | 4 |
| 30 | G5/G7 | G6 gate_claim prose inflated, self-description unverified | M (claim exceeds mechanism) | 4 |
| 31 | G5/G7 | G7 historical_provenance widened to EXECUTION_SPEC.md | M (exempt-class widening) | 4 |

Rows 2–26 (minus none) = the report's 25. Rows 1 + 27–31 = the 6 mechanism/regression-level evasions the prose scope excludes. 19 P + 12 M = 31.

## What the Head Researcher should carry forward

Quote the count WITH its scope: "25 of 36 auditor-constructed adversarial probes (batches 2–3) evaded; 31 evasions across the full 52-fixture table including regression and declaration-integrity checks." The state file's "31 evasions" (`ops/CURRENT_STATE.json:36`) and L-018's "31 evasions were reported" (`docs/CONTINUITY_LEDGER.md:332`) are the table-wide scope and need no correction — only this scoping gloss, which is why this note exists as a separate file.
