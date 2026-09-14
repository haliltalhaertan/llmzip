[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# RECONCILIATION.md — 12 B vs 88,886 B: contradiction or different scopes? (PREPARED, NOT ACCEPTED)

Status: PREPARED, NOT ACCEPTED. Verdict below is a recommendation for the Head
Researcher, not a decision. Labels: VERIFIED / CLAIM / RELAYED as in COST_MODEL.md.

## Verdict (one paragraph)

The two numbers do NOT contradict — they are different accounting scopes of the
same bill, and both scopes are explicitly defined in the cited sources. The
12-byte figure is the MARGINAL cap the preregistration enforces; the 88,886
figure is the EFFECTIVE cost the same decision requires to be reported
alongside it. The pilot measured exactly the second number the decision asked
for. The honest reading is therefore narrower than either camp's slogan: the
12-byte framing is HONEST as a statement of the matched-budget retrieval
contest the preregistration defines, and MISLEADING as a statement of what it
costs to store a SIGN96 archive. Which reading the programme's language
currently invites is documented in §4.

## 1. The two definitions, verbatim

A. The budget (marginal). From `ops/CURRENT_STATE.json` on main (VERIFIED —
read 2026-09-14), key `twelve_byte_budget_decision_2026_09_11`:

> "decision": "twelve bytes = at most twelve MARGINAL PERSISTENT BYTES PER VECTOR"
> "inside_the_cap": "everything written once per stored memory: the code, any
> norm or scale, any correction scalar, any per-vector metadata"
> "outside_the_cap": "shared model state - codebooks, OPQ rotation, centroid
> tables - NOT counted against the marginal cap but ALWAYS reported separately
> in bytes"

and the reporting rule in the same key (VERIFIED):

> "reporting": "marginal_bytes_per_vector and shared_state_bytes_per_archive are
> always carried; effective_bytes_per_vector = marginal + shared/N_archive is
> optional and derived. The FIRST number alone decides whether a comparison is
> twelve-byte matched."

B. The measurement (effective). From PROJECTOR_BYTES.json `aggregate`
(VERIFIED), `ratios_median.a_raw`: shared_total 44,220,235.0,
shared_per_vector 88,874.36234817814, effective 88,886.36234817814; and the
pilot's own scope sentence from PROJECTOR_REPORT_TR.md (VERIFIED): the report
measures ONLY the shared projector ("Bu rapor o ayrı sayıdır; yalnızca
paylaşılan projektörü ölçer" — "this report is that separate number; it
measures only the shared projector"), under the L-088 rule that "12 tavanı
yalnızca `marjinal` değere uygulanır… `etkin` değer… ayrı raporlanır ve tavana
karşı test edilmez" ("the 12 ceiling applies only to the marginal value… the
effective value… is reported separately and is not tested against the ceiling").

The audit confirms compatibility explicitly (CLAIM,
AUDIT_MEASUREMENTS_TR.md §Projector): "L-088: etkin değer tavana karşı test
edilmiyor — iki açık feragat + JSON'da PASS/FAIL/cap/tavan/violation sözcüğü
yok… Uyumlu." I VERIFIED the checkable part: the JSON contains no
PASS/FAIL/cap/violation key at top level (keys are `_labels, _refit_notice,
task_boundary, config, vocab_encoding, numeric_encoding, compression,
unavoidable_vs_choices, excluded_with_reason, per_archive, aggregate,
not_checked`).

Arithmetic linking the two (recomputed in verify_cost.py, 9/9 PASS):
12 (marginal, scope A) + 44,220,235/N (shared, scope B) = effective.
At the median archive this equals the cited 88,886.36. There is no missing
money and no double counting: scope A counts `m`, scope B counts `S`, the
effective counts both. 12 ≠ 88,886 is the statement "the shared projector
dominates," not "someone is wrong."

## 2. Why the confusion is nevertheless the programme's own fault

Compatibility on paper is not clarity in practice. Three facts, each verified:

1. The decision's own reporting rule makes the effective number OPTIONAL
   ("effective_bytes_per_vector… is optional and derived", VERIFIED quote
   above) while the prereg revision's §3 makes it MANDATORY ("Effective cost
   is mandatory in this revision so small-archive costs stay visible" —
   `a73393a`:PREREG_DRAFT.md §3, VERIFIED). The two governing texts disagree on
   whether the 88,886 number must appear. The revision is newer and stricter;
   the decision text was not updated to match.
2. The audit's P2 observation stands (CLAIM, F-06): the "≈7400×12" ratio
   sentence, though fenced by two disclaimers, "tavan-testi gibi okunmaya
   müsait" ("reads like a ceiling test"). A compatible number presented in a
   way readers systematically misread is a communication defect, not a math
   defect.
3. Programme-facing language — "whether SIGN96 is competitive at twelve bytes,"
   "the twelve-byte baseline race" (docs/CONTINUITY_LEDGER.md lines ~1811,
   ~1830, VERIFIED present on main) — states scope A while inviting scope-B
   inferences about deployment cost. No ledger line I read carries the
   "marginal, plus ~90KB/vector shared state at programme scale" qualifier.

## 3. Under what condition each framing is honest

- The 12-byte framing is HONEST iff every use carries, in the same breath, the
  decision's own qualifier: "12 MARGINAL bytes per vector, plus [measured S]
  shared bytes per archive under archive-local fitting." In that form it
  describes the matched retrieval contest correctly: all arms share the same
  ~44 MB preprocessing (see COST_MODEL.md §5 — common state moves absolute
  framing, not arm ranking), and the arms differ in exactly the 12-vs-20-vs-44
  marginals the decision adjudicates.
- The 12-byte framing MISLEADS whenever the shared state is selectable,
  unmeasured, or amortized without being shown: any sentence of the form
  "SIGN96 stores each vector in 12 bytes" without the per-archive S term; any
  comparison that amortizes S over pooled benchmark vectors (the prereg
  revision §2 explicitly forbids this: "Never amortize state over all benchmark
  questions", VERIFIED); any deployment-cost claim extrapolated from marginals.
- The 88,886 framing MISLEADS in the opposite direction if read as an
  arm-level verdict: the 44 MB is pipeline state common to SIGN96, PQ, OPQ,
  ITQ, and the float reference alike. It cannot by itself rank methods, and a
  storage result cannot refute the retrieval results (+16.58 pp broad,
  +10.04 pp concentrated — cited programme context, NOT re-verified here).

## 4. What the Head Researcher should act on (recommendation, not decision)

1. Adopt the prereg revision's stricter rule (effective cost mandatory) over the
   decision's "optional and derived" — the pilot has now produced exactly the
   number that rule needs, and optionality is what let the two framings drift.
2. Require the one-sentence qualifier on every "twelve-byte" programme claim
   (re-wording list in IMPLICATIONS.md).
3. Note the boundary result from COST_MODEL.md §4–5: under the mandated
   archive-local deployment, SIGN96+projector stores ~234× MORE bytes than raw
   float32 at LongMemEval scale (20.8 GB vs 88.9 MB, recomputed). The ONLY
   deployment in which the 12-byte framing survives total-accounting is the
   globally-shared projector (202.9 B/vec) — the deployment the preregistration
   excludes. The Head Researcher priority order (accounting → mechanism →
   scale) therefore points at a scoping question, not a measurement question:
   is the programme buying a marginal-bits retrieval contest (keep the framing,
   qualify it) or a deployable storage win (the framing fails at programme
   scale, and scale-up does not rescue it until ~119K vectors/archive).
