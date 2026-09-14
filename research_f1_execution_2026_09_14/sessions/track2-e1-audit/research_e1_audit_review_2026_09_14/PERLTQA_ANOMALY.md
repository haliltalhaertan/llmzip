[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 3 — The PerLTQA anomaly: SIGN loses where it wins everywhere else (PREPARED, NOT ACCEPTED)

This document is PREPARED, NOT ACCEPTED. VERIFIED = I read/ran the bytes. I treat the
reversal as the mechanism story's most informative clue, not as a footnote.

## The anomaly, stated exactly (VERIFIED)

Audit 1's independently re-derived headline gates
(`origin/audit/e1-v2-raw-cache-recovery-independent-2026-09-13:…/EXECUTION_LOG.txt`,
"HEADLINE GATES" section):

- PerLTQA SIGN `0.488941994930817` vs centered float `0.551692074528853`
  ⇒ SIGN − float = **−6.275007959803602 pp** (my `python3` subtraction on the two
  quoted constants — VERIFIED arithmetic).
- Every other benchmark goes the other way: LME `+10.03794326 pp` (0.5419751773049645 −
  0.4415957446808511), REALTALK `+5.22410218 pp`, LoCoMo `+6.82838013 pp`.

## Is it reproduced elsewhere? Yes — three independent sightings (VERIFIED)

1. The `bench3` campaign surface predating E1: `campaign_2026_09_13/bench3/b3b_perltqa/results.json`
   (one of the 7 SHA-gated inputs the mechanism auditor byte-verified in report §2).
2. The frozen checkpoint's own §1: "The campaign already established that SIGN96 can
   beat centered float96 strongly on LongMemEval and REALTALK, **while verified PerLTQA
   reverses the ordering**." (`origin/research/e1-mechanism-checkpoint-frozen-2026-09-13:campaign_2026_09_13/e1_mechanism/E1_MECHANISM_CHECKPOINT.md`).
3. The R2 corrected report reproduces the identical pair (`0.4889419949308170` /
   `0.5516920745288530`, status "reproduced") — so the reversal survived the raw-cache
   recovery and the competition-metric correction untouched.

It is not a metric-implementation artefact: F1 (min-gold bug) moves *competition
correlations*, not headline retrieval scores, and the R2 report confirms headlines
unchanged.

## Is it a benchmark-composition effect? Partly — and I checked the arithmetic (VERIFIED)

The bridge report (`…/e1_mechanism/E1_BRIDGE_REPORT.md`, "Existing-result bridge table")
splits PerLTQA into sections (SIGN−float, pp): profile **+20.435**, social **−0.806**,
events **−12.411**, dialogues **−1.476** — with sign concordance 6/6 against BOT−TOP
polarity. Section n's from the v2 audit's EXECUTION_LOG: profile 333, social 844,
events 4346, dialogues 2742 (total 8265).

My composition check (VERIFIED `python3` run):
`(20.435×333 − 0.806×844 − 12.411×4346 − 1.476×2742)/8265 = −6.2747 pp`,
vs the headline −6.2750 pp — consistent to the rounding of the published section values.
**The headline "SIGN loses on PerLTQA" is therefore dominated by events** (52.6% of
queries at −12.41 pp) swamping profile (+20.44 pp on only 4.0% of queries).

But composition alone does NOT explain it away, for two auditor-verified reasons:

- **Same-archive sign flip** (mechanism audit §4F, independently recomputed): profile,
  events, social and dialogue queries for one character share the *same* archive and
  document matrix, yet events Delta is negative in **30/30** characters while profile
  Delta is positive in **23/30**, with **22/30** characters showing a joint
  Delta-and-P64 flip. A pure "different archives" composition story is refuted; the
  residual is a query/semantic-regime × archive interaction (checkpoint §5, licensed).
- **Ties don't rescue it either** (mechanism audit §4G): events loses despite a *lower*
  native tie rate (27.08%) than profile (31.23%); untied events still lose −9.81 pp
  while untied profile wins +19.65 pp.

## Is it acknowledged? Yes — it is the pivot of the whole E1 line (VERIFIED)

- Bridge report: "**The new PerLTQA reversal changes the research question.** The useful
  question is no longer 'does SIGN96 beat float96?' but 'what property changes the sign
  of that comparison?'"
- Checkpoint §1 makes the re-framed target "`what changes the sign of SIGN96 −
  centered-float96 across retrieval regimes?`" and checkpoint §8 keeps LoCoMo out of
  the E1 Delta/P64 synthesis for lack of a per-query float surface.
- R2 report notes the sharp edge honestly: "Archive-level relationships … PerLTQA is
  weakly positive **while SIGN loses overall**. Structural redundancy asymmetry is
  therefore not sufficient to determine retrieval outcome."

## Threat or clue? Both — and the dangerous reading is specified

- **As threat:** any universal or deployable-router telling of SIGN ("~12-byte codes
  replace float vectors") is falsified by a full benchmark running −6.3 pp, and the
  section split shows the sign flips *within one archive* across semantic regimes.
  Both audits correctly refuse universal wording (v2 Claim H; mechanism Claim H PASS).
- **As clue:** the 6/6 sign concordance between SIGN−float and BOT−TOP polarity across
  LME/REALTALK/sections, plus the 22/30 within-archive joint flip, is exactly what
  makes P64 a regime marker worth a frozen follow-up — descriptive only, per both audits.
- **Assumption that would most damage my conclusion:** that the section labels
  (profile/events/social/dialogues) are exchangeable or that events' dominance reflects
  query-count weighting rather than a real regime difference. I tested the weighting
  half (arithmetic above: it *is* partly weighting). The regime half is carried by the
  within-archive flip, which holds archive fixed — but sections are still not
  randomized interventions (mechanism audit §4F says so explicitly), so a causal
  section-effect claim remains unlicensed. A follow-up must freeze the regime
  hypothesis *before* observing outcomes on an unseen benchmark (both audits' guardrails).
