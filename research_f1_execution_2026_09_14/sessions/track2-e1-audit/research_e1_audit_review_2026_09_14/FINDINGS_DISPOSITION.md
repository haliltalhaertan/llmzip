[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 2 — Disposition of every REQUEST_CHANGES finding (PREPARED, NOT ACCEPTED)

Scope rule: only Audit 1 returned REQUEST_CHANGES, so only its findings (F1–F6) need a
disposition. Audit 2 returned PASS_WITH_FINDINGS with no required changes (its F01–F10
are INFO/LOW/MEDIUM bounds and guardrails, not blockers — VERIFIED in AUDIT_VERDICTS.md).
This document is PREPARED, NOT ACCEPTED. VERIFIED = I read the bytes.

## Where I looked (VERIFIED)

- Later E1 branches: `origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13` (tip
  `d5edeb3`; 5 commits on top of the audited `d544169`) and
  `origin/research/e1-sign-float-mechanism-v2-frozen-2026-09-13` (tip `775a09c` —
  predates the audit, so it cannot contain fixes).
- Main's record: `grep -c "e1-"` → `0` in both `docs/CONTINUITY_LEDGER.md` and
  `ops/CURRENT_STATE.json` (VERIFIED); `grep -c "010bcbb|ec40dc3|REQUEST_CHANGES|PASS_WITH_FINDINGS"`
  → `0` in both files (VERIFIED). Neither audit, verdict, nor finding is recorded on main.
- All-refs search for any executed repair: `git log --all --grep="per-gold|Claim-D|competition rerun|re-audit"`
  finds only the R2 contract-freeze and correction-adoption commits, no execution
  (VERIFIED); `git branch -a --contains d5edeb3` returns only the R2 branch itself —
  no descendant ever ran the frozen contract (VERIFIED).

## Disposition table

| Finding → severity | Addressed anywhere? | Locator (VERIFIED) |
|---|---|---|
| F1 HIGH (blocking): min-gold collapse must be replaced by frozen per-gold D2 + full regeneration | PARTIALLY — corrected numbers adopted from the auditor, executable repair NOT done, no re-audit | `origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:campaign_2026_09_13/e1_v2_raw_recovery_r2_2026_09_13/E1_V2_COMPETITION_CORRECTED_RESULT.json` has `"status": "CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT_FULL_PAYLOAD_PENDING"`; `R2_COMPETITION_RERUN_CONTRACT.md` has `"Status: FROZEN R2 REPAIR CONTRACT / NOT YET EXECUTED BY LEAD / RE-AUDIT REQUIRED"`; `AUDIT_FINDINGS_DISPOSITION_R2.md` states "R2 Claim D is `CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT / FULL_PAYLOAD_PENDING`" and "R2 is not PASS yet. The only remaining blocking repair is executable regeneration … followed by independent re-audit." |
| F2 MEDIUM: LoCoMo ~12pp is not an anchor; keep `0.16826334541318252` | ADDRESSED IN WORDING (lead-accepted, not re-audited) | Same branch, `AUDIT_FINDINGS_DISPOSITION_R2.md` §F2: "ACCEPTED / CLOSED IN WORDING"; `E1_V2_RAW_CACHE_RECOVERY_REPORT_R2.md`: "The historical `~+12pp` wording has no recovered frozen centered-float source and is not an anchor." |
| F3 MEDIUM: disclose Q_ABS_CV/Q_EFF redundancy | ADDRESSED IN WORDING (lead-accepted, not re-audited) | `AUDIT_FINDINGS_DISPOSITION_R2.md` §F3: "ACCEPTED / CLOSED IN INTERPRETATION… They are one degree of evidence, not two." |
| F4 MEDIUM: P64 tie-rank sensitivity; descriptive-only scope | ADDRESSED IN WORDING (lead-accepted, not re-audited) | `AUDIT_FINDINGS_DISPOSITION_R2.md` §F4: "ACCEPTED / CLOSED IN SCOPE… never as a router or stable effect-size claim." |
| F5 LOW: 520/520 is sample-wide, not universal | ADDRESSED IN WORDING (lead-accepted, not re-audited) | `AUDIT_FINDINGS_DISPOSITION_R2.md` §F5: "ACCEPTED / CLOSED IN WORDING" with the quoted sample-scoped sentence. |
| F6 LOW: imperfect cold-start blinding | DISCLOSED, nothing to repair (lead-accepted) | `AUDIT_FINDINGS_DISPOSITION_R2.md` §F6: "ACCEPTED / DISCLOSED… independently recomputed, not perfectly blind." |

## Headline conclusion for the skeptic

The single HIGH/bocking finding (F1) is the one whose numbers are being quoted
elsewhere — and it is **not closed**. What happened:

1. The auditor's corrected per-gold coefficients (LME strict `0.141686…` vs lead
   `0.099657…`, etc. — VERIFIED in both FINDINGS.json and the R2 corrected-result JSON)
   were copied into the R2 report as auditor-derived summaries.
2. The lead's own executable regeneration of per-query competition rows + corrected
   bootstraps — the exact repair the audit demanded — was frozen as a contract and
   **never executed on any branch** (VERIFIED: contract status line + no-descendant
   check above).
3. No re-audit was ever commissioned, and main's ledger/`ops/CURRENT_STATE.json`
   contain zero record of the audit, its verdict, or any finding (VERIFIED: 0 hits).

So: anyone quoting R2 Claim-D competition numbers today is quoting
`CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT` — auditor-computed values the lead adopted
but never reproduced in its own pipeline and never got re-audited. The R2 documents say
this honestly ("R2 is not PASS yet"); the risk is downstream quoters dropping the
qualifier. F2–F6 are closed only to the strength of an un-audited self-disposition:
the lead accepted them in wording, and no independent party confirmed the wording
changes propagated to every competition-derived row, bootstrap, and prose passage.
