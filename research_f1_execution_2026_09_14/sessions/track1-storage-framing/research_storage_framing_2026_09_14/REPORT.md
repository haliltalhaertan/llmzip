[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — adversarial storage-framing audit

PREPARED, NOT ACCEPTED. I cannot accept, seal, ratify, or close anything.

## What I produced (all in `research_storage_framing_2026_09_14/`)

- `STATUS.md` — receipt, written first.
- `MEASUREMENT_PROVENANCE.md` — audit of the 88,886 figure: median of 15 per-archive (12 + shared/N) for float32+structured-vocab re-fit; declared re-fit, not frozen artifact; all 7 audit observations enumerated; 4 own observations (median-convention gap, float32-as-choice, scope tails, component shares).
- `STEELMAN_BOTH_SIDES.md` — strongest HONEST case (binding L-088 definition, exact S(N) linearity, mandatory disclosure, self-cancelled overreach, SIGN96's own index state is ~12.06 not 88 kB) and strongest MISLEADS case (shared dominates 3–4 OOM, break-even 1.4–3.7M vs ~500, global rescue fails and is forbidden, original question unqualified, reported costs are lower bounds, auditor's own F-06), plus where both stories are weak.
- `VERDICT.md` — unqualified framing misleads (bytes refute the 32× inference, sign-inverted for full pipeline); qualified marginal accounting is honest-but-incomplete (rules exist, complete numbers don't). Single settler: an HR definition ruling on the referent of "12 bytes" (marginal vs index-effective vs full-pipeline), plus the §4 complete-package measurement.
- `ATTACK_LOG.md` — 11 attacks: 7 failed (claims strengthened), 2 passed (median-convention 1.5% gap; misleading quotation in the original pushed draft), 2 inconclusive/receipt-backed (faiss execution leg; common-mode projector gap — the most important unresolved attack).
- `OPEN_QUESTIONS.md` — 8 questions, each with settler and seal status (2 seal-blocked: Q-3, Q-8b; rest merely not done).

## What I verified (ran/read the bytes myself)

- 88,886.36 median recomputed exactly from `PROJECTOR_BYTES.json`; spread 80,266–104,464; N 443–551; component shares s96 85.11 / sv 11.40 / vocab 2.61; d_lex=32 all 15; native f64 median 87,288,483.
- Break-evens 3685020/1890510/1977778/1411767 recomputed exactly; nb1 overhead exactly 8 across all d; nb2 overhead exactly 20 across all d (new, unstated in evidence).
- OPQ 287.6889713064122 mean-of-costs recomputed from the frozen CSV to all 16 digits (n=470, min 396, max 616, mean 492.78); global-sharing rescue gives 85–203 B/vector, still 7–17× cap; float-parity needs N≥118,872.
- Read in full: pilot README, projector report + README + script, audit report (F-01..F-07), cost README + EVIDENCE.json + OPEN_ITEMS_CLOSED.md, replay README + COMPARISON.json, both preregs' storage sections, HR decision artifact, L-088, CURRENT_STATE.json twelve-byte keys.

## What I could NOT do and why

- Execute faiss code_size measurements (no installs allowed) — cross-platform exactness is RELAYED from the replay receipt (`strict_non_environment_equal: true`, zero diffs), structure VERIFIED arithmetically.
- Re-derive the auditor's sklearn-source inventory check — RELAYED from the audit report.
- The common-mode analysis (does FLOAT96 need the same projector?) — no document contains it; needs the unbuilt runner, not sealed data.
- Anything retrieval-quality (Q-3, Q-8b): UNAVAILABLE-UNDER-SEAL — Task4F1 BLOCKED, 804MB BEAM corpus absent and not fetched.
- Did not read the parallel session's branch/worktree (task forbids it); all conclusions from primary sources with locators.

## Commit

Local commit sha to be recorded here after committing (see stdout summary).
