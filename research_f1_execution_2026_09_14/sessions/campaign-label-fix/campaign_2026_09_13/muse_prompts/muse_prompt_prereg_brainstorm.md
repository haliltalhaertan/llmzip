# Muse session — PREREG DRAFT BRAINSTORM: make the twelve-byte race more decisive

You are a constructive research designer. The docket draft below is functional but was written
fast; your job: **brainstorm concrete, high-value changes** that increase the DECISIVENESS of the
race without scope-creeping it. Read-only on /mnt/c; writes only /tmp/pre2/. No network.

## Materials

- THE DRAFT: /mnt/c/Users/MDP/dev/llmzip-work/DRAFT_PREREG_TWELVE_BYTE_RACE.md
- Context: strategy/roadmap_2026-09-13/muse_strategy_roadmap.md (§3 Design 2) +
  review_transfer/EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13/pilots/axis_attack_2026-09-12/
  round3/{ROUND3_REPORT.md, missing_analyses/}, round2/ROUND2_REPORT.md, and the technical-ideas
  report strategy/roadmap_2026-09-13/muse_ideas_technical.md (its top-5 list + A1 hetero idea).
- Known facts to respect: learned-selection arm is EXCLUDED (killed); spread/random ≈ best simple
  arms; top-variance is anti-optimal; LoCoMo prefers bottom-tail (benchmark-local nuance);
  m1 null: no-edge ≈ −1.62/−1.20pp vs-best.

## Brainstorm targets

1. **Arm table.** Anything cheap and within-budget worth adding or re-specifying? (e.g., the
   LoCoMo bottom-tail arm already flagged; anything else from rounds 1–3 that deserves a seat?)
   Anything worth REMOVING to keep the race clean?
2. **Analyses that make the result more decisive.** e.g.: presenting results also as "premium vs
   no-edge null (m1)" alongside vs-best; per-question W/T/L matrices between competitors;
   recall-vs-bytes curve parameters; per-type/per-category breakdowns; seed-range reporting;
   what would make a NULL result still publishable and a POSITIVE result credible.
3. **Evaluation-semantics proposals** (for the draft's biggest hole): your recommended fixed
   choices for scoring non-sign codecs (estimator, ties, K), and a fairness argument for
   comparing FR across codecs.
4. **Operational hardening** you would insist on before seal: smoke tests, environment pins,
   artifact manifest, negative controls — phrased as a minimal checklist.
5. **Future-work notes**: what to mention as out-of-scope-but-noted (hetero-precision from
   muse_ideas A1; adaptive routing is now closed — anything salvageable as a descriptive arm?).

## Output

/tmp/pre2/pre2_report.md: (a) proposed changes table — change | why | cost | risk (ordered by
value/cost); (b) "do NOT add" list (scope creep the draft should resist); (c) the evaluation-
semantics recommendation; (d) pre-seal checklist proposal. Plus /tmp/pre2/pre2_details.json.
Print a compact summary to stdout (PRE2_BEGIN/PRE2_END). ~1-2 hours scale. No /mnt/c writes.
