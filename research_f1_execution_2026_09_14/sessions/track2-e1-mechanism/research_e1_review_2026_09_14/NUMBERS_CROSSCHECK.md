[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# NUMBERS_CROSSCHECK — E1 figures versus the programme's frozen canon

Work is PREPARED, NOT ACCEPTED. Nothing here is sealed, ratified, or closed.
I report every agreement and discrepancy without choosing the convenient number.
VERIFIED = I ran/read the bytes. CLAIM = a document states it.

## Programme canon (baselines I check against)

| figure | value | main-branch locator (VERIFIED present via `git grep` on `5ec3db60`) |
|---|---|---|
| LongMemEval SIGN96 | 54.197517730496 (%) | `5ec3db60:README.md`, `5ec3db60:audit_v52_t4c3/AUDIT_REPORT.md`, `5ec3db60:docs/v52/task4c3/TASK4C3_ACCEPTED_CHECKPOINT_2026-08-28.md` |
| LongMemEval centered float96 | 44.159574 | `5ec3db60:docs/v52/task4c2/V52_T4C2_COMPUTE_REPORT.md`, `5ec3db60:docs/PROJECT_STATUS_2026-08-27.md` |
| LME SIGN−float (CONCENTRATED) | +10.037943 pp | task text; reproduced by E1 join as +10.037943262411346 (below) |
| LoCoMo SIGN96 | 23.654714666441 (%) | `5ec3db60:README.md`, `5ec3db60:docs/CONTINUITY_LEDGER.md`, `5ec3db60:docs/v52/task4d/TASK4D_ACCEPTED_CHECKPOINT_2026-08-29.md` |
| D96 vs Haar | −15.925851063830 | task text (no separate main locator sought; taken as given) |
| LoCoMo centered float (programme) | *no canon value given* | — |

I did not re-derive any canon figure (that would need sealed/outcome surfaces); I checked
*presence* of the locators and *agreement* with E1's reproduced gates.

## E1 headline gates vs canon — AGREEMENTS

1. **LME SIGN / float reproduced to gate precision.** E1 recovery gates (CLAIM, `origin/research/e1-v2-raw-cache-recovery-2026-09-13:campaign_2026_09_13/e1_v2_raw_recovery_2026_09_13/E1_V2_RAW_CACHE_RECOVERY_REPORT.md` §Headline gates, VERIFIED read): SIGN `0.5419751773049645`, float `0.4415957446808511` — i.e. 54.1975…% / 44.1595…%, matching canon to the quoted decimals. The independent audit recomputed PASS on both (CLAIM, raw-cache audit §Headline gates, VERIFIED read). The LME secondary join independently reproduced the Delta headline `+10.037943262411346 pp` (CLAIM, `…/E1_LME_SECONDARY_REPORT.md`, VERIFIED read). **Agreement: exact.**
2. **REALTALK gates reproduced.** SIGN `0.2247750759878419(4)`, float `0.1725340538106495(4)` — lead and audit agree to all shown digits; audit verdict PASS (CLAIM, both reports). **Agreement: exact lead↔audit.**
3. **PerLTQA gates reproduced.** SIGN `0.4889419949308170`, float `0.5516920745288530`; audit PASS (CLAIM, both reports). Implied overall Delta ≈ −6.275 pp (my arithmetic from the published gates: 48.894 − 55.169 = −6.275; VERIFIED computation, not a published figure) — sign-consistent with the line's "PerLTQA reverses the ordering" claim. **Agreement: exact lead↔audit; sign consistent with canon narrative.**
4. **LoCoMo SIGN anchor reproduced.** `0.2365471466644105(4)` — lead, R2, and audit agree to all shown digits (CLAIM, all three reports, VERIFIED read). Against canon 23.654714666441%: matches to quoted decimals. **Agreement: exact.**
5. **P64 point estimates replicate three ways.** Checkpoint §3, recovery §A, and both audits agree: LME +0.108(6), REALTALK +0.0745, PerLTQA +0.1092, LoCoMo +0.2495 (CLAIM, VERIFIED read in all four documents). **Agreement: exact across line and audits.**
6. **520/520 structural asymmetry confirmed independently.** Lead and audit both report PHI_GAP>0 and EFFDIM_GAP>0 in 520/520 archives (CLAIM, recovery §B + audit §B). **Agreement: exact.**

## The LoCoMo float discrepancy — NOT resolved by choosing

- E1's newly derived LoCoMo centered float: **`0.16826334541318252`** (CLAIM, recovery §Headline gates; repeated in R2 report and R2 disposition F2; independently recomputed by the audit — "lead `0.16826334541318252` is independently confirmed", CLAIM, audit §A; all VERIFIED read).
- Implied gap: SIGN − float = **+6.828380125122796 pp** (R2, CLAIM) / **+6.82838013 pp** (audit headline, CLAIM). My check: 0.23654714666441054 − 0.16826334541318252 = 0.06828380122228002 → 6.828380122228002 pp, consistent to display rounding (VERIFIED arithmetic; the 8th-decimal difference vs 6.82838012512 is rounding of the published inputs, not a discrepancy).
- The old programme line: "≈+12.0pp programme-reported; not re-derived" — **no frozen centered-float source found** in committed campaign surface or recovered transcripts (CLAIM, recovery §Headline gates; audit: "No frozen centered-float source supporting ~12pp was found, so it is not an anchor", CLAIM).
- Consistency question from the task: is +6.83 pp consistent with the programme's other numbers? What I can say from verified material: (i) it uses the programme's own LoCoMo SIGN anchor (exact match, above), so the *difference* comes entirely from the float leg; (ii) no programme-canon LoCoMo centered-float value exists on main that I was asked to check against (the task's canon list gives only LoCoMo SIGN), so there is **no direct arithmetic contradiction with any frozen programme figure** — the conflict is with an unsourced ~12pp recollection, which the line demotes to `PROGRAMME_REPORTED_NOT_RECOMPUTED / NOT_AN_ANCHOR` (CLAIM, R2 disposition F2). The audit additionally bounds variants (raw/fractional/any/all) at about +5.899…+7.681 pp (CLAIM, audit §Headline gates) — the +6.83 figure sits inside that band, the ~12 figure sits far outside it.
- **Disposition: genuine discrepancy between E1's auditable +6.83pp and the historical ~12pp wording; the line refuses to "fix" it by fiat and leaves ~12pp UNRESOLVED/NOT_AN_ANCHOR. I do the same.** A programme LoCoMo centered-float canon, if one exists anywhere outside the listed locators, is UNAVAILABLE-UNDER-SEAL to this review (would need the LoCoMo evaluator output or its manifest binding — I did not go looking, per the seal).

## R1 vs corrected (R2/audit) competition numbers — supersession recorded, not hidden

| benchmark | R1 strict (lead, min-gold — SUPERSEDED) | corrected strict (per-gold D2) | R1 tie (SUPERSEDED) | corrected tie |
|---|---|---|---|---|
| LME | 0.099657 | 0.141686 | 0.098959 | 0.140454 |
| REALTALK | 0.061183 | 0.097939 | 0.087153 | 0.122820 |
| PerLTQA | 0.277387 | 0.254168 | 0.285059 | 0.279788 |
| LoCoMo | 0.093706 | 0.094920 | 0.095332 | 0.103760 |

(CLAIM, raw-cache audit §D table, VERIFIED read; R2 disposition F1 reproduces the corrected
columns.) Direction stays positive on all four either way — the audit judged the defect
"repairable rather than fatal" (CLAIM) — but every R1 competition number, bootstrap, and
derived sentence is superseded, and the corrected full payload is still pending (CLAIM, R2 status).

## What I could NOT check (seal / absent material)

- Any per-query retrieval outcome, distance, recall, or arm-level value: never opened, per the Task4F1 seal. All figures above are *published summary gates/coefficients* from the line's own documents, which the task explicitly permits reading.
- The BEAM corpus: absent, not fetched (never attempted).
- Programme D96 −15.925851063830 vs Haar: no E1 branch re-tests Haar mixing; nothing to cross-check against (the bridge report cites Haar damage only as consistent-with background).
- LoCoMo centered-float provenance beyond the E1 frozen cache: would need the historical evaluator output the ~12pp claim came from — not located by the line, not sought by me.
