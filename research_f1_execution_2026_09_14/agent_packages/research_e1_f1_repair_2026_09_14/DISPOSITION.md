[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DISPOSITION — F1 (Claim-D min-gold collapse)

Question: should F1 be considered CLOSED-PENDING-REAUDIT or still OPEN?

## Verdict: still OPEN

F1's required repair is the **executable regeneration of Claim-D per-query rows + descriptive bootstrap on the
frozen caches, followed by independent re-audit** (contract §"Persisted outputs"; R2 disposition "Required before
PASS"). That regeneration did not happen here: the contract's input archives are absent and unfetchable in this
environment (`CACHE_INVENTORY.md`; verifier probe E0 = BLOCKED), so no real-data row was recomputed, no auditor
coefficient was reproduced, and nothing exists for a re-auditor to check beyond what the auditor already computed.

## What this execution DOES contribute toward closure

- A SPEC-derived, oracle-proven implementation (`f1_competition.py`) the lead can run unchanged on the real caches.
- A runnable acceptance check (`verify_f1.py`) whose real-data gates (headline C1/C2, pin rechecks D1–D6,
  cache probe E0) activate automatically once caches are present.
- A demonstrated bug reproduction and the single-gold-hiding theorem, corroborated by branch bytes (D4).
- Machine proof that all currently-quoted Claim-D numbers are mutually consistent across five branch sources —
  consistency, not reproduction.

## Reason it is not CLOSED-PENDING-REAUDIT

"CLOSED-PENDING-REAUDIT" would assert the lead's regeneration exists and only the re-audit is outstanding. No such
regeneration exists: `E1_V2_COMPETITION_CORRECTED_RESULT.json` still carries
`"status": "CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT_FULL_PAYLOAD_PENDING"` (VERIFIED), and this execution adds
synthetic-schema analogues only. Claiming otherwise would misrepresent an auditor intermediate as a reproduced result —
the exact failure mode F1 was raised to prevent. I am not the auditor and could not close F1 regardless.

## Re-audit entry conditions (for whoever holds the caches)

1. Place the four archives at pinned shas; run `verify_f1.py` (E0 goes live) and the contract pipeline via
   `f1_competition.query_row` per the auditor's cache layout (`CACHE_INVENTORY.md` §"Exact cache files").
2. Tolerance 1e-12 vs the §4 table; any mismatch = major finding, investigate, do not tune.
3. Persist the six contract outputs; this namespace's `evidence/` shows the schema, not the content.
