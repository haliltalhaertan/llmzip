[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — E1 mechanism-line audit review (PREPARED, NOT ACCEPTED)

Namespace `research_e1_audit_review_2026_09_14/`. Work is PREPARED, NOT ACCEPTED: I
cannot accept, seal, ratify or close anything. All branch reads via
`git show origin/<branch>:<path>`; no checkout, no push, no main touched, purely
additive (5 new files + STATUS.md, this namespace only). Task4F1 SEAL honoured
throughout: no run/finalize modes, no HMAC key, no retrieval IDs/distances/recall/
arm outcomes, no corpora/queries/labels/embeddings opened; the BEAM corpus was not
fetched. VERIFIED = I ran/read the bytes; CLAIM = a document says it.

## What I produced (all VERIFIED written to this namespace)

1. `AUDIT_VERDICTS.md` — both verdicts quoted verbatim from bytes: Audit 1
   (`010bcbb`) **`REQUEST_CHANGES`** (report line 3); Audit 2 (`ec40dc3`)
   **`PASS_WITH_FINDINGS`**. All findings with severities (Audit 1: 1 HIGH F1,
   3 MEDIUM F2–F4, 2 LOW F5–F6; Audit 2: INFO/LOW/MEDIUM only, claims
   A–H PASS/PASS_WITH_FINDING), verified-vs-relayed split, and each auditor's own
   stated limitations.
2. `FINDINGS_DISPOSITION.md` — per-finding table. **F1 (HIGH, blocking) is not
   closed**: corrected numbers were adopted from the auditor but the demanded
   executable regeneration was frozen as a contract and never executed on any branch
   (contract status `NOT YET EXECUTED BY LEAD`; corrected-result status
   `FULL_PAYLOAD_PENDING`; no descendant of R2 tip `d5edeb3`; no re-audit). F2–F6
   closed in wording only, without re-audit. Main records nothing: 0 hits for `e1-`
   and for `010bcbb|ec40dc3|REQUEST_CHANGES|PASS_WITH_FINDINGS` in both
   `docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json`.
3. `PERLTQA_ANOMALY.md` — SIGN loses PerLTQA by −6.2750 pp while winning the other
   three benchmarks. Reproduced in three places; composition-checked by my own
   arithmetic (section-weighted −6.2747 pp ≈ headline −6.2750 pp: events, 52.6% of
   queries at −12.41 pp, swamps profile +20.44 pp on 4%). Composition does not
   explain the within-archive 22/30 joint Delta/P64 flip or the lower tie rate on the
   losing section. The line acknowledges it — the reversal *is* the E1 research
   question — but no causal explanation is licensed by either audit.
4. `INDEPENDENCE_ASSESSMENT.md` — Audit 1: true from-raw re-derivation with own code,
   self-disclosed imperfect blinding. Audit 2: clean-room reproduction of lead scripts
   (≤1e-12) plus genuinely adversarial own diagnostics. Neither states executor/model
   separation (zero grep hits); neither fully demonstrates cold-start as the
   programme's `docs/CONTINUITY_PROTOCOL.md:31-34` bar requires.

## What I could NOT do and why

- Sealed-adjacent checks are UNAVAILABLE-UNDER-SEAL: anything requiring real Task4F1
  retrieval outcomes, corpora, or embeddings was out of scope by the Task4F1 SEAL; I
  stopped at committed E1 aggregates and record exactly that boundary.
- No re-audit or repair: my mandate is review-only; closing F1 needs the lead to
  execute the frozen R2 contract and commission a re-audit, then the Head Researcher
  to record it (the sole writer of the ledger and `ops/CURRENT_STATE.json`).
- Commit-message search for later fixes has a known blind spot (a fix with an
  unrelated message), mitigated by the no-descendant branch check and R2's own
  `FULL_PAYLOAD_PENDING` status.

## Highest-value surfacing (for the skeptic)

Quoted Claim-D competition numbers anywhere downstream are auditor-computed values the
lead adopted but never reproduced and never got re-audited — R2 says so itself
("R2 is not PASS yet"). And main has no record that either audit happened. Those two
facts together are the disposition headline.

Local commit: (see stdout summary; `git log --oneline -1` on `muse/track2-e1-audit`).
