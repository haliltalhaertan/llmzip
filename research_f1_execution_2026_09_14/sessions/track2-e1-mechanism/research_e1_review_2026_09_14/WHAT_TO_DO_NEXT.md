[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# WHAT_TO_DO_NEXT — the one experiment that would most efficiently settle the mechanism

Work is PREPARED, NOT ACCEPTED. Nothing here is sealed, ratified, or closed.

## Prerequisite gate (mechanical, not the experiment)

Execute `R2_COMPETITION_RERUN_CONTRACT.md` (`origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:…/R2_COMPETITION_RERUN_CONTRACT.md`)
and re-audit it. Until Claim D's corrected per-query rows exist, any new test of the
competition leg builds on `CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT` rather than a persisted
payload. This is days-cheap (caches and contract both frozen) and unblocks everything below.

## The experiment: frozen fifth-benchmark regime-marker test (E1-C1)

**Rationale.** E1's entire surviving structure (P64 regime marking, S2 asymmetry, S3 competition
direction) was measured on the same four benchmarks that generated it. The audit's stated
"main epistemic risk is selection/narrative inflation" (checkpoint audit §5, CLAIM). The only
efficient settler is a *confirmatory* run on an unseen fifth retrieval benchmark with every
rule frozen before outcomes are observed — exactly what the checkpoint (§9), the recovery
(§Next step), and the audit (§7, guardrail 1) all prescribe.

**Design (frozen before any fifth-benchmark outcome is observed).**

1. *Inputs.* One unseen benchmark with a frozen C96/qC/gold cache in the same pipeline family
   (centered C96, same K=3/tie convention, same evidence mapping). Refit of representations is
   forbidden. Minimum scale: ≥20 archives (the n=10 REALTALK/LoCoMo archive sets were too small
   for stable archive-level inference — audit §§Claim D/E, CLAIM) and ≥500 queries.
2. *Gate.* Reproduce the benchmark's accepted SIGN96 headline to ≤1e-12 from the frozen cache;
   else stop. (Centered-float leg: derive from the same frozen cache exactly as the E1 V2 spec
   prescribes; if no accepted float output exists, the float leg is labeled NEW-derivation as
   with LoCoMo, never silently promoted.)
3. *Frozen metrics* (all definitions byte-identical to `E1_PREANALYSIS_SPEC_V2.md`):
   per-query `Delta_q`, `P64_q`, per-gold `STRICT_GAP_q`/`TIE_GAP_q` (per-gold D2 aggregation —
   the min-gold variant is forbidden), archive `PHI_GAP`, `EFFDIM_GAP`, `Delta_archive`.
   Average-rank Spearman throughout.
4. *Predeclared predictions* (directional, from E1): rho(Delta_q,P64_q) > 0;
   rho(Delta_q,STRICT_GAP_q) > 0; rho(Delta_q,TIE_GAP_q) > 0; PHI_GAP > 0 and EFFDIM_GAP > 0
   in ≥95% of archives; sign(Delta_archive) == sign(P64_archive) in ≥75% of archives
   (E1's observed rates: 29/30 PerLTQA chars, 9/10 REALTALK chats, 87/115 pairs).

**Falsification condition (written here, before the experiment).** The regime-marker hypothesis
FAILS if *any* of: (i) query-level rho(Delta,P64) ≤ 0; (ii) both competition gaps ≤ 0;
(iii) archive sign-concordance < 60% (i.e. within noise of coin-flip given ≥20 archives);
(iv) PHI/EFFDIM gaps ≤ 0 in >25% of archives. Meeting all four predictions does not *prove*
the mechanism — it promotes the tradeoff model to "generalized once, still non-causal" and
licenses the causal test below as E1-C2 (per-archive bit-ablation: zero out TOP64 vs BOT64
sign bits and check that Delta moves with the competition gap, the manipulation E1 never ran).

**What "support" vs "refute" would mean.** Support (all four pass): the programme may treat
P64 + per-gold competition gaps as *generalized* descriptive markers and spend the causal
budget (E1-C2) with confidence. Refute (any condition trips): the E1 structure is declared
benchmark-family-specific; the mechanism question re-opens from the surviving structural fact
(S2) rather than from P64, and no E2/codec promotion may cite E1.

**Cost note.** No new codec race, no refit, no Task4F1 contact — one benchmark's frozen cache
through frozen scripts, then independent re-audit. That is the cheapest run that can actually
shrink the mechanism uncertainty instead of re-measuring it.
