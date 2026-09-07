# V52 — Claude to Codex: what changed after your handover

Date: 2026-09-07
From: Continuity Lead / co-chair (Claude), sole writer on `main`
Repo: `github.com/haliltalhaertan/llmzip`

**Verify, do not trust this document.** Every claim below names a commit, path or hash. If this
document and the repository disagree, the repository wins and you should say so. Do not treat this
text, or any chat, as evidence.

**Read this first if you only read one thing:** your five packages were verified and integrated, the
acceptance decision was taken, and an independent closure audit of that decision has already run and
returned `CLOSURE PASS WITH CAVEATS` with nothing requiring the stage to be reopened. **Do not
re-audit it, do not re-run anything, and do not re-open the coordinate-scale stage.**

---

## 1. Anchors — verify these before acting

| what | value |
|---|---|
| canonical `main` | `18bb70d5a41a3c3ce934f70e7c913d0f762223aa` (L-062) |
| research branch | `research/v52-sign-mechanism-locomo-2026-09-04` @ `0c9916bd7786d7ddb332f5b6da3d96d61a6223f0` |
| closure audit | `audit/v52-acceptance-closure-2026-09-07` @ `16e95a8035297e18891c4e51f1261bc27d64000b` |
| audit report sha256 | `669a06c9d8e0efc95fd988252c85ac6c99123cba272040e80fc7716f4c4c25a9` |
| acceptance decision sha256 | `8ba55a616c33f23fd3e8cc6daf4565830b7e993f4749e8440c9c62e082d31d3f` |
| clarification note sha256 | `52a37695e34b693f668e2fc36b4425b6aab22919912cca871de8271dffe42aae` |
| erratum sha256 | `a80262390778ac64916f619473b966e4f37cb4fe8a83a9a14995abe613b13bb2` |

**Before you hash anything: read §7 of this document first.** There is a repository-wide checkout
trap that will make every hash you compute look wrong on Windows.

New ledger entries since your handover: **L-057 … L-062**. Your handover was written when `main` was
at `a0944522` (L-056).

## 2. Your packages: verified and integrated (L-057)

All five branch tips resolved exactly as your handover claimed. The LoCoMo reproduction report
hashed to `db3274ff…` as stated. Your own `verify_evidence.py` was executed read-only at `2f9adb84`
and printed `10/10 exact source objects PASS; synthesis numeric statements PASS; altered lock
REJECTED`.

Nothing of yours was re-run. Nothing of yours was merged into `main`; the packages stay on their
branches and `main` records them by identity.

## 3. The one open question in your handover that I can answer

Your handover recorded that the target branches of the commissioned coordinate audit and the
literature scan were absent, and correctly refused to infer whether those agents were running or
dead. **Neither.** I launched both as zero-context agent sessions at L-056; the Head Researcher
instructed a full stop for quota reasons minutes later; I stopped both before either pushed
anything. Both branches remain absent and **both tasks remain undischarged**. The literature scan
(C1–C9) has still never been commissioned.

## 4. Your findings R1–R5: what was decided

**R1 (aggregation order) — RULED.** `A` is the preregistered estimand; `B` is preserved as the
historical implementation output; both are always published together. The ruling was made from the
**preregistration text only**, with no outcome value in the reasoning, at the Head Researcher's
explicit instruction: §7 defines `frac_arm` under the governing clause "per rotation seed", applies
the bands to "the seed-panel mean" of that quantity, and requires per-seed denominator dispersion.
`B` requires collapsing arms across seeds before forming the ratio, which §7 nowhere describes.

Two things you may want to fold into your own record:

- **Both statistics were already recoverable from the published bytes.** The runner persists
  `frac_*_per_seed` beside the seed-mean ratio, so R1's "preserve both" requirement needed no file
  change.
- **The A/B divergence is essentially a block-arm phenomenon.** Full arm: A−B = `+0.001079` (LoCoMo),
  `+0.000644` (LongMemEval). Block arm: `−0.206` and `+0.008`. The headline full-mixing observation
  does not depend on which definition is primary; the comparative block/interaction claim does, and
  neither definition rescues it.

**R2, R3, R4 — recorded, not adjudicated**, in a deviation register (§6 below) as D3, D5 and D6.

**R5 (§7/§9 interpretation conflict) — recorded as an explicit deviation and deliberately NOT
resolved.** Two defects named precisely: §7 demotes `I_frac` to secondary while §9 attaches the
positive licence to that same quantity; and no numeric band, threshold or cut for `I_frac` appears
anywhere in the document. The audit confirmed both and added a correction: my phrasing "no band,
threshold **or direction** test" was one word too strong, because §9 does draw a *qualitative* large
versus ≈0 distinction — with no numeric cut, so its licence remains inoperable and the conflict
stands.

## 5. The acceptance decision (L-059), and its closure audit (L-062)

**Accepted:** the LoCoMo computational reproduction of the same implementation, and the
scale-equalisation improvement on the frozen panel **as a descriptive finding**.

**Not accepted:** the comparative mechanism claim, and any population-level inference from the
`MOST` / `PARTIAL` band labels.

**Recorded at the Head Researcher's instruction:** this decision does **not** mean "there is no
mechanism". The required phrasing throughout is **not established on current evidence and therefore
outside the acceptance scope** — never *falsified*, never *scientifically rejected*.

An independent cold-start auditor then reviewed the record itself — not the science — across eight
gates, and returned **`CLOSURE PASS WITH CAVEATS`**, seven gates `ESTABLISHED`, `C6` not established
on one clause of four (label-set divergence), with **nothing requiring the stage to be reopened**.
It reached the same §7 reading independently, confirmed `seed-mean` occurs **zero** times in the
preregistration, reported it **could not construct a defensible reading of B**, recomputed A and B
in float64 **and exact rational arithmetic**, and ran 15 negative controls each shown actually
failing.

Eight defects it found in my record are accepted in full and answered additively in the erratum:
mis-labelled "verbatim" quoting, an over-broad outcome-free assertion, "exact differences" that were
float64 differences, a missing citation label, label-set divergence, a state-file text mismatch, an
unstated `I` / `I_frac` identification, and the §9 direction overstatement above.

**One finding is substantive and worth your attention (erratum E8).** Ruling `A` primary selects the
**less numerically stable** estimator exactly on the block arm, where per-seed denominators change
sign — block-arm float error ~`1e-14` against the full arm's ~`1e-16`. The textual ruling stands.
The direction matters: this **strengthens** the refusal of the comparative claim rather than
weakening it. Your R1 analysis did not carry this and it is a real addition to it.

## 6. Two things that change your open-items list

**The LongMemEval conversation-cluster bootstrap is ill-posed, not pending — but read the
qualification.** `docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md` records *"Dependency graph: 1
component(s), largest=470/470"*, and the same finding sits inside
`adapters/longmemeval_v52_adapter_v2.py`, whose sha256 `643082d6…` was verified equal to the
`A2_SHA256` pinned by the frozen LongMemEval base — so it is the adapter the pipeline executes, not
a stale note. All 470 questions form **one** connected component; a cluster bootstrap needs at least
two exchangeable clusters. Remove it from outstanding work.

**The qualification is load-bearing and was required by the Head Researcher:** this is
**provenance verification, not recomputation**. The corpus was not read, the session-sharing graph
was not rebuilt, the components were not recounted. The figures are **inherited from Task 3A.1**.
Any citation must carry:

> `[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE VERIFIED, NOT RECOMPUTED HERE]`

An independent recomputation would be a separate corpus-reading task. It is **not authorized**.

**The LoCoMo Full-Haar denominator dispersion is now measured** (L-056), which your handover listed
as needing a re-run. The coordinate-scale stage's `FULLHAAR_FRESH` arm is a fresh ten-seed panel on
the same frozen pipeline: mean `0.139131`, sd `0.0052`, se of a five-seed mean `0.002326` (1.69% of
the inherited denominator), fresh minus inherited `+0.27 sd`. Every LoCoMo boundary-localization
breakdown point lies outside the 95% interval; the tightest, the `B48` exclusion, needs `9.1 se`.
The frozen denominators are **not** replaced and no verdict was recomputed. This is not
independently audited.

## 7. Infrastructure trap — this will bite you, and it explains two earlier false alarms

**The repository ships no `.gitattributes`.** On any default Windows clone (`core.autocrlf=true`),
**both shipped verifiers report mass SHA256 mismatches**. The closure auditor proved this is a
checkout artifact rather than assuming it: CRLF-expanding the raw blob of
`longmemeval_v52_adapter_v2.py` reproduces the failing verifier's reported hash bit-for-bit, and
after `git config core.autocrlf false` with a fresh checkout both verifiers exit 0.

Two earlier auditor sessions reported exactly this and were stopped before confirming it. **Their
suspicion was correct; no chain-of-custody defect ever existed.**

**Rule until it is fixed: hash raw Git blobs (`git show <commit>:<path>`), never checked-out files.**
A one-line `.gitattributes` would end it permanently. It is deliberately **not applied**, because it
changes checkout semantics repo-wide for every future clone — a repository-owner decision.

## 8. A governance rule that now binds both of us

L-061 revised a **published, sidecar-hashed** document in place, so a hash recorded in the canonical
ledger stopped resolving on `main`. The auditor flagged it outside its own range without taking a
verdict. Accepted and repaired: the v1 bytes are restored at
`docs/v52/V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07_v1_SUPERSEDED.md`, byte-identical to
`c0828c5d…`, so the ledger's hash resolves again.

**Forward rule:** on `main`, any document carrying a `.sha256` sidecar, or whose hash has been
recorded in the ledger, is **additive-only** — supersede it with a new file and record both hashes.
In-place revision stays available for unpublished drafts on draft branches, and for
`ops/CURRENT_STATE.json`, which is a live single-writer file rewritten every entry.

## 9. Do not redo these

- The closure audit, the erratum, or the hash repairs.
- Any completed experiment, the bootstrap, or the LoCoMo reproduction.
- The acceptance decision or the A/B ruling.
- The LongMemEval dependency-graph recomputation (unauthorized, and its inherited status is
  deliberate).
- Any Task 4F1 action. It remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
  FORBIDDEN`. No run, finalize, HMAC or outcome authority exists.
- The broad literature scan — written but not commissioned, and currently paused by decision.

## 10. What is genuinely open, and who owns it

| item | owner |
|---|---|
| next research question: coordinate-membership proposal (v2), encoder-generalisation alternative, or neither | Head Researcher |
| `.gitattributes` (I1) — changes checkout semantics repo-wide | repository owner |
| Task 4F1 execution track: V8 package audit, exact-rational `D_t` analysis | Head Researcher |
| Drive backup (D11) — **never performed** for this stage or for your five packages; do not describe it as done | operator with Drive access |
| GitHub default branch still resolves away from `main` | repository owner |
| literature scan C1–C9 | Head Researcher |
| alternative dependency-aware inference for a single connected component | unauthorized design work |

## 11. Where to read the detail

On `main` at `18bb70d5`:

- `docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md` — the decision, the A/B
  derivation, the §7/§9 deviation, the LongMemEval evidence binding
- `docs/v52/V52_ACCEPTANCE_DECISION_CLARIFICATION_2026-09-07.md` — provenance versus recomputation
- `docs/v52/V52_ACCEPTANCE_RECORD_ERRATUM_2026-09-07.md` — the audit result and all ten corrections
- `docs/v52/V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07.md` — proposal v2, unauthorized
- `docs/CONTINUITY_LEDGER.md` — entries L-057 … L-062
- `ops/CURRENT_STATE.json` — machine-readable state

On the research branch at `0c9916bd`:

- `research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md` — D1–D11
- `research/v52/V52_LOCOMO_DENOMINATOR_DISPERSION_ADDENDUM_2026-09-07.md`

On the audit branch at `16e95a80`:

- `audit_v52_acceptance_closure_2026_09_07/CLOSURE_AUDIT_REPORT.md` and its gate table

Note that the deviation register's `D1` and `D2` rows still read `OPEN`. They are superseded by the
acceptance decision and left unedited deliberately, because corrections here are additive.
