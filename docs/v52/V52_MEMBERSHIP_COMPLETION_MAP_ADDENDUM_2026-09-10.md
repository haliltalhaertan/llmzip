# V52 — Membership completion map: additive status correction

**Date:** 2026-09-10
**Corrects:** `docs/v52/V52_MEMBERSHIP_COMPLETION_MAP_2026-09-08.md`
**Authority:** `docs/v52/V52_OBLIGATION_1_AND_F3_N1_DECISION_2026-09-09.md`, Decision 3
**Method:** additive. The map's bytes are **not rewritten**; this file supersedes the
rows named below and nothing else.

All line references are on `origin/main` at `0a79017`. `map:` is the completion map,
`ledger:` is `docs/CONTINUITY_LEDGER.md`.

---

## Row `map:58` and row `map:105` — G-1

**Recorded:** "in progress — commissioned 2026-09-08".
**Corrected:** **review complete; disposition of its output is open.**

G-1 is the independent runner+ingestion review. Its chain runs L-076 (FAIL, scoped
only to the runner and ingestion wiring at `22e44608` — `ledger:1595`,
`ledger:1602`) through the successive fix packages and their independent
delta-closure checks recorded in L-077, L-078 and L-079, and terminates at L-080,
the audit of the Codex v5 repair package, verdict PASS WITH FINDINGS limited to that
repair package (`ledger:1703`, `ledger:1710`, `ledger:1718`).

**G-1's findings are the four non-blocking findings at `ledger:1713`** — `F-1`
(int-subclass diagnostic loss in `verify_source_identity`), `F-2` (a suite probe
passing for the wrong reason), `F-3` (cohort-size site with no local type gate), and
`F-4` (one README sentence wider than the code). The two items at `ledger:1714` are
recorded but **not reopened** and are not among the four.

**Naming hazard.** L-080's findings are `F-1`…`F-4` (hyphenated); L-081's are
`F1`…`F7` (unhyphenated). They are different sets from different reviews. Any
reference must name the ledger entry, not the bare label.

## Row `map:106` — G-2

**Recorded:** "not reached".
**Corrected:** **reachable and pending.**

L-080 awaits the Head Researcher's disposition of the four non-blocking findings
(`ledger:1719`), and disposition of whatever G-1 found is exactly G-2's own
definition (`map:106`). The map defines no intermediate label for this state; the
wording of the replacement label is the Head Researcher's to choose and is **not**
invented here.

**A second item is open alongside the four.** In the same sentence at `ledger:1719`,
L-080 also awaits disposition of **whether the Codex v5 package becomes the working
candidate line in place of v4**. No later entry disposes of either item: L-081
reviews a different package (`ledger:1728`) and L-082 decides different obligations
(`ledger:1755`, `ledger:1769`). L-082 is the final ledger entry — the file ends at
line 1770 — so both stand open.

## Rows `map:107` and `map:108` — G-3 and G-4 are unchanged, and L-081 maps to neither

**Recorded and unchanged:** G-3, the authorization to write M-1/M-2/M-3, is
**"not granted; no design or code authority exists for them"** (`map:107`); G-4, the
independent review of *those components once written*, is "not reached" (`map:108`).

L-081 records a review of the execution-preparation package — *"the first M-1, M-2
and M-3 code in this programme"* — with verdict PASS WITH FINDINGS scoped to the
prepared functions only (`ledger:1728`, `ledger:1733`). Its seven findings
(`ledger:1735`) and nine named test gaps (`ledger:1736`) belong to that review.

**That review corresponds to no gate in this map.** It is **not** an early instance
of G-4: G-4 reviews components written under G-3, and G-3 has not been granted.
L-080's own closing clause is explicit that a scope-limited PASS on the v5 repair
*"does not authorize the experiment, does not open M-1/M-2/M-3, and does not license
a seal or a run"* (`ledger:1719`).

The prepared code is therefore **a candidate for review once G-3 is granted, never an
inheritance that substitutes for it.** G-3's status is unchanged by this addendum.

---

## What this addendum does NOT do

- It disposes of **no** finding: not L-080's four, not the v5-versus-v4 candidate
  question, not L-081's seven findings or nine test gaps, and not integration
  obligations 1, 4 and 5, all of which remain open per L-082 (`ledger:1766`,
  `ledger:1769`).
- It grants **no** authorization, opens **no** gate, and changes G-3, G-4, G-5, G-6,
  G-7, G-8 and G-9 in no respect.
- It does not rewrite the completion map.

Task 4F1 remains **SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN**.

---

*Prepared by the Continuity Lead under the authority named above.*
