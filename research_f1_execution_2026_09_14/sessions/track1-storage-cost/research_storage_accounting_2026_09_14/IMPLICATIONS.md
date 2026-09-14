[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# IMPLICATIONS.md — what the accounting does to programme claims (PREPARED, NOT ACCEPTED)

Status: PREPARED, NOT ACCEPTED. Labels per COST_MODEL.md. I compute STORAGE
only. Nothing here re-measures retrieval quality, and a storage result cannot
by itself refute a retrieval result — the recall deltas below are cited
programme context I did NOT re-verify.

## 1. Symmetric statement

- CASE THE 12-BYTE FRAMING SURVIVES: as the definition of a MATCHED retrieval
  contest. The budget decision (`ops/CURRENT_STATE.json`
  `twelve_byte_budget_decision_2026_09_11`, VERIFIED) defines the cap as
  marginal-only, requires shared state to be reported separately, and mandates
  archive-local fitting. Under that contract the pilot's 44 MB is common
  preprocessing charged to every arm equally (COST_MODEL.md §5: index-only
  SIGN96 12.067 vs PQ96 211.664 vs OPQ 286.616 B/vec at mean N — ranking
  intact), the arms genuinely differ in the marginals the decision adjudicates
  (SIGN96 12, RaBitQ96 20, EXT 44, PQ96 12 — VERIFIED in EVIDENCE.json and the
  `9cd3f54` replay), and the retrieval deltas (+16.5834 pp broad vs ITQ96;
  +10.037943 pp concentrated vs centered FLOAT96) stand or fall on their own
  statistical evidence, untouched by byte counts. The 88,886 number then reads
  as the decision's own "reported separately" term, made mandatory by the
  prereg revision §3 — the system working as designed.
- CASE IT DOES NOT: as any claim about what it COSTS to store an archive. At
  programme scale the SIGN96 side stores ~20.8 GB against ~88.9 MB of raw
  float32 (~234×, recomputed in verify_cost.py, 9/9 PASS). The codes that are
  the entire subject of the "race" are ~0.013% of the persisted bytes. Any
  reader who hears "twelve bytes per vector" as a deployment fact has been
  misled, and the programme's own outward-facing sentences invite exactly that
  reading (§2). The only deployment rescuing the framing — one global projector
  amortized over all vectors (202.9 B/vec, recomputed) — is the deployment the
  preregistration forbids ("Never amortize state over all benchmark questions",
  `a73393a` §2, VERIFIED).
- EVIDENCE SUPPORTS: both cases simultaneously, at different scopes — which is
  the RECONCILIATION.md verdict. The contest survives; the deployment story
  fails at programme scale. Concretely: keep running the marginal-budget
  retrieval comparison (its logic is intact), but stop presenting it as a
  storage win, and do not expect scale-up to rescue the absolute numbers until
  ~119K vectors per archive (float32 projector) — ~240× current archive sizes,
  with the 100K BEAM tier (declared size only) still below break-even at
  454 > 384 B/vec ceteris paribus.

## 2. Claims that need re-wording if the framing is read at scope B (with locators)

"Re-wording" here means adding the decision's own qualifier
("marginal; plus measured shared state per archive"), not retracting results.
I did NOT modify any of these files (pure-additive rule); line numbers below
are where the Head Researcher (sole writer of ledger/state) would act.

1. "whether SIGN96 is competitive at twelve bytes" / "run the twelve-byte
   baseline race first" — docs/CONTINUITY_LEDGER.md lines ~1811, ~1830
   (VERIFIED present on main). Needs: "at twelve MARGINAL bytes per vector
   (plus ~44 MB shared projector state per archive at LongMemEval scale)."
2. The preregistration title and arm table equation of "96 bit with 12 byte"
   — `origin/draft/v52-twelve-byte-baseline-prereg-2026-09-10`
   (`d2cfbaa`):docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md; the
   equation is quoted in `ops/CURRENT_STATE.json`
   `twelve_byte_budget_finding_2026_09_11.why_it_matters` (VERIFIED): "the
   preregistration's title and arm table equate 96 bit with 12 byte." Needs the
   marginal qualifier in the title or its first paragraph.
3. `twelve_byte_budget_decision_2026_09_11.reporting` — "effective… is optional
   and derived" (VERIFIED). Directly superseded by prereg revision §3
   ("Effective cost is mandatory…", VERIFIED). The older text should be amended
   additively to point at the stricter rule; the two currently disagree (§4 of
   RECONCILIATION.md).
4. Any future sentence of the form "the ≈7400× ratio" (pilot report tables;
   audit F-06, CLAIM) — keep the number, keep the two disclaimers, and add the
   third sentence the audit implies is missing: "this ratio compares effective
   against marginal; it is not a ceiling test and not an arm ranking."
5. The "twelve-byte race" shorthand wherever it appears in prompts/ledger
   (e.g. prompts/V52_TWELVE_BYTE_BUDGET_MUSE_AUDIT_TASK_2026-09-11.md,
   VERIFIED present on main) — fine as internal shorthand among readers who
   know the decision; each outward-facing use needs the qualifier.

## 3. What this pilot does NOT change (do-not-overclaim list)

- The retrieval deltas (+16.5834 pp broad; +10.037943 pp concentrated, 64.7%
  ties) — unexamined here; storage arithmetic has no vote on them.
- The mechanism question (variance-heterogeneity rejected; heavy-tails/hubness
  refuted) — untouched; shared-state size explains cost, not recall.
- The RaBitQ 20B/44B and PQ 12B marginal findings (EVIDENCE.json + `9cd3f54`
  replay, VERIFIED equal) — confirmed as cited constants, independent of S.
- The Task4F1 BLOCKED status — this pilot opens nothing; seal discipline held
  (receipts: no run/finalize modes invoked, no HMAC key set, no corpus, query,
  gold, embedding, distance, or recall bytes opened; BEAM corpus not fetched).
- LoCoMo per-archive effective costs and float16+zlib raw baselines —
  UNAVAILABLE (COST_MODEL.md §2); the "10× larger archives still 23× over raw"
  sensitivity covers scale directionally, not these cohorts specifically.
