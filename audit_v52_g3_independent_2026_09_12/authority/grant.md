# V52 — Head Researcher Decision: G-3 is granted

**Date:** 2026-09-11
**Authority:** Head Researcher (repository owner)
**Prepared by:** Continuity Lead (prepares only; does not seal, does not self-approve)
**Predecessor:** the twelve-byte budget decision of the same day, sha256
`1832f4b368024edba4a7f5d2d3f925e9c9b1c53367f1a4ed54b7586b2ec8cc26`.

Relayed as chat text and recorded as such — **not** a Head-Researcher-signed
artifact — the same standing as L-054, L-086 and L-088.

---

## The decision

> **G-3 IS GRANTED.**

The authority is defined as **one single controlled remediation package**, not as a
standing licence.

## What the package covers

- the **seven findings** of L-081;
- the **nine named test gaps** of L-081;
- **integration obligations 4 and 5**;
- and, **to the extent they are directly related**, the four non-blocking findings
  of L-080 that constitute G-2's content, together with the question of whether
  `v5` becomes the working candidate line in place of `v4` — handled **inside this
  same package**.

## The boundary of the authority

**Permitted.** Code changes. Adding and changing tests. Fail-closed controls.
Provenance and state-hygiene corrections. Verifying all of the above.

**Not permitted.** Running the Task 4F1 experiment. Sealing, finalizing, or any HMAC
operation. Granting production authorization. Access to real retrieval-quality
outcome data.

> **G-3 is a fix-and-test authorization. It is not an authorization to run an
> experiment.**

## Acceptance criterion

**One commit passing does not close G-3.**

G-3 is closed only when

1. a **traceable test and evidence matrix** exists covering the seven findings, the
   nine test gaps, and obligations 4 and 5; and
2. the **disposition of the G-2 items taken into this package is explicitly
   written**.

Every finding leaves at minimum this triple:

```
finding  ->  code/test change  ->  verification result
```

## What is preserved and may not be undone

The coordinatewise certificate decision stands. **There is no return to an
aggregate-distance control.** The fixed family including the **all-96-negation
vector** remains mandatory, and so does the negative-control test that the new
check must reject and the old aggregate control accepts.

---

## What this decision does NOT do

- It does not authorize any execution, seal, pilot or run on any track.
- It does not grant retrieval-quality outcome access, and does not set or request
  `V52_T4F1_AUTH_HMAC_KEY_HEX`.
- It does not alter the twelve-byte budget decision, and does not license the
  baseline preregistration to be sealed.

Task 4F1 remains **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
FORBIDDEN**. This line is retained deliberately: G-3 grants code authority and
nothing else, and granting it relaxes no Task 4F1 prohibition.
