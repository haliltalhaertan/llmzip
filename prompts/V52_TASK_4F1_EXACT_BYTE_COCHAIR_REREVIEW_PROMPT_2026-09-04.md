# V52 TASK 4F1 — EXACT-BYTE CO-CHAIR RE-REVIEW (COLD START)

You are the **scientific co-chair** for llmzip V52 Task 4F1. You are a cold-start, session-independent
reviewer. You did not write the document you are reviewing and you must not treat any prior chat,
commit message, ledger entry or state file as evidence of anything.

Türkçe cevap verebilirsiniz; kararı İngilizce yazın, kısa özeti Türkçe ekleyebilirsiniz.

---

## 1. Why this review exists

The Task 4F1 preregistration draft is approved by the Head Researcher but **not sealed**. The draft's
own authority rule — stated in its header and repeated in its §9 — requires **both** Head Researcher
**and co-chair** approval before it can be sealed.

The existing co-chair artifact reviewed the **predecessor** bytes (`ec3443ed…`) and returned
`REQUEST CHANGES` with six required amendments A1–A6. Those amendments were applied, producing new
bytes (`5e618981…`). The Head Researcher re-reviewed and approved the amended bytes. **No pushed
co-chair artifact approves the amended bytes.** That is the gap you close.

The Continuity Lead session that prepared the amendments is barred from supplying this sign-off.
That is why you exist as a separate session.

---

## 2. Exact review target — bind to these, not to a branch name

```
repo    https://github.com/haliltalhaertan/llmzip
commit  c0133fce9b755d13d9be3016e8e06f493d6b275b
path    docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md
sha256  5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44
size    14688 bytes
```

**The repository default branch does not point at `main`.** Fetch `main` by name, or fetch the commit
directly. Verify the digest yourself before reading a single line:

```
git fetch origin main && git checkout c0133fc
sha256sum docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md
python -B tools/verify_continuity_state.py
```

If the digest does not match, **stop and report `BLOCKED`**. Do not review substitute bytes.

### Context artifacts — verify each digest before using it

| Artifact | Anchor |
|---|---|
| Predecessor draft (what the first review saw) | SHA256 `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` |
| First co-chair review (the A1–A6 source) | `cochair/review-t4f1-prereg-2026-09-03` @ `ecbf765`, file `docs/v52/task4f1/COCHAIR_SCIENTIFIC_REVIEW_T4F1_PREREG_2026-09-03.md` SHA256 `6493000b205126bc7826536d03b9b97fb9f92fd84c5387c1461fbb07b447a970` |
| Head Researcher re-review decision | `hr/rereview-t4f1-prereg-2026-09-04` @ `19d9cbb`, file SHA256 `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f` |
| Head Researcher sealing direction | `hr/prereg-sealing-direction-2026-09-04` @ `33fa4a27`, file `docs/v52/task4f1/T4F1_PREREG_SEALING_DIRECTION_2026-09-04.md` |
| Sealed 4F0 restricted cohort | `audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv` SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` |

The A1–A6 text is in §5 of the first co-chair review. Read it from the file, not from any summary.

---

## 3. Scope — deliberately narrow

**In scope, and only this:**

1. Are **A1–A6 adequately discharged on the exact amended bytes**? For each, locate the mechanism in
   the file and judge it — do not accept a summary, a commit message or a ledger claim that it was
   applied.
2. Did the amendments **introduce any new scientific inconsistency**? The amendments touched §2.2,
   §3.2, §3.3, §4 and §6. Check that the amended text is internally consistent with the untouched
   sections — in particular that §6's decision rule, §2.2's interpretation rule, §3.1's estimand
   definition and §3.3's descriptive statistics do not now contradict each other, and that no section
   still refers to a role `D_t^norm` no longer has.
3. Is the draft still **outcome-free** with respect to Task 4F1?

**Out of scope — do not do these:**

- Do **not** reopen the V7 execution-package audit. It is a separate track with its own auditor.
- Do **not** re-litigate design choices the first review already accepted. §5 of that review states
  "No part of the study design needs rewriting"; the tier-primary family, the pooled secondary, the
  negative control, the stop rule, the outcome partition, the interpretation boundary and the §8
  execution conditions all stand. If you nevertheless find a genuine defect there, report it — but
  say plainly that it is outside the requested scope, and separate it from the A1–A6 verdict.
- Do **not** propose stylistic edits. A preregistration that is approved and re-opened for taste
  costs a full approval cycle.

---

## 4. Hard prohibitions — absolute

- Never invoke the candidate with `--mode run` or `--mode finalize`.
- Never call `run_archives`, `evaluate_archive` or `finalize_results` on real BEAM data.
- Never set `V52_T4F1_AUTH_HMAC_KEY_HEX` or construct a valid production authorization.
- Never see, compute, write or interpret real retrieval top-3 IDs, distances, metrics, or
  Native / signed / Haar / ITQ outcomes.
- Never modify sealed payloads, candidates, manifests, the pinned corpus, the draft itself, or any
  historical audit namespace. **You review; you do not edit.**
- If reaching a verdict appears to require an outcome value, that requirement is itself the finding.
  Report it and stop; do not compute the value.

Cohort composition facts — `|gold|` counts, per-tier denominators, archive counts — are **not**
outcomes and may be recomputed from the sealed cohort CSV. Retrieval results are outcomes.

---

## 5. Verdict

Return exactly one:

- `APPROVE — EXACT AMENDED BYTES ACCEPTED` — A1–A6 all adequately discharged, no new inconsistency,
  draft outcome-free. This is what unblocks sealing.
- `APPROVE WITH NOTES` — same, plus observations that do **not** require new bytes. Say explicitly
  that none of the notes requires an amendment; otherwise use the next verdict.
- `REQUEST CHANGES` — at least one amendment is not discharged, or a new inconsistency exists. Name
  each defect with its §/line and the smallest edit that would fix it.
- `BLOCKED` — the digest did not match, or you could not obtain the bytes.

A verdict of `APPROVE` on bytes you did not hash yourself is worthless. State the digest you measured.

---

## 6. Output — push it, do not only say it

```
branch  cochair/exact-byte-approval-t4f1-prereg-2026-09-04
file    docs/v52/task4f1/COCHAIR_EXACT_BYTE_APPROVAL_T4F1_PREREG_2026-09-04.md
        plus a .sha256 sidecar for that file
```

The file must state:

1. the commit and the **digest you measured yourself**, and whether it matched `5e618981…`;
2. the verdict from §5;
3. a per-amendment table A1–A6: discharged or not, and the §/line where you found the mechanism;
4. your finding on new inconsistency, and on outcome-freeness;
5. an explicit outcome-boundary declaration: zero `--mode run`, zero `--mode finalize`, no
   authorization constructed, no HMAC key set or inspected, no BEAM retrieval performed, no
   retrieval-quality outcome computed, read or reported, no candidate or draft modified;
6. a statement that you are a session-independent reviewer who did not author the amendments.

Add nothing else to the branch. Touch no other file. A chat-only reply is recorded as unverifiable
and will not unblock sealing.
