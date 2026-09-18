[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# F1 contract execution + relayed-idea evaluation — 2026-09-14

Base: `main` @ `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00` — NOT modified, NOT merged. Additive branch only.

## Headline

The E1 raw-cache-recovery audit's **F1** finding (min-gold collapse in the Claim-D competition
metric) required an executable regeneration that had never been run: the contract was frozen as
`NOT YET EXECUTED BY LEAD` and `E1_V2_COMPETITION_CORRECTED_RESULT.json` still carries
`status: CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT_FULL_PAYLOAD_PENDING`. Every quoted Claim-D
coefficient was therefore an auditor intermediate, not a reproduced result.

This session executed it on the real caches (482 input files, sha256-manifested) and
**reproduced all six published auditor coefficients** to rounding:

| benchmark | coefficient | this session | auditor (4 dp) | diff |
|---|---|---:|---:|---:|
| LME | strict | 0.1416251737011647 | 0.1417 | -7.48e-05 |
| LME | tie | 0.14069387548880735 | 0.1405 | +1.94e-04 |
| PerLTQA | strict | 0.25413844391463014 | 0.2542 | -6.16e-05 |
| PerLTQA | tie | 0.27982715404990666 | 0.2798 | +2.72e-05 |
| REALTALK | strict | 0.09793425648573494 | 0.0979 | +3.43e-05 |
| REALTALK | tie | 0.12307477776090332 | 0.1228 | +2.75e-04 |

Frozen headline control (same run): LME +10.053783 pp, PerLTQA -6.274728 pp, REALTALK +5.300077 pp.

## The bug's real-data effect (first measurement)

| benchmark | correct | min-gold (bug) | multi-gold rate |
|---|---:|---:|---:|
| LME | 0.1416 | 0.0992 | 62.98% |
| PerLTQA | 0.2541 | 0.2774 | 28.09% |
| REALTALK | 0.0979 | 0.0613 | 54.75% |

The bug's direction is **not consistent**: it suppresses the coefficient where multi-gold queries are
common and inflates it where they are rare. "The bug only added noise" is not available as a defence.

## F1 disposition: still OPEN — but the blocker moved

NOT closed, for three reasons stated plainly:
1. **Not independent.** The same session commissioned the implementation and ran it.
2. **LoCoMo leg absent.** No committed per-query float surface; that benchmark was not run.
3. **Archive identity unverifiable.** The contract pins sha256 of three `.tar.gz` archives; only
   extracted trees exist here, so tarball hashes cannot be reproduced. File-level identity is
   established against `evidence/INPUT_CACHES.sha256` only.

The blocker is no longer "nobody ran it" but "an independent party must check it".

## Relayed-idea evaluation (six ideas from an external model)

| # | idea | first-hand outcome |
|---|---|---|
| 1 | scale dependence | **CONTRADICTED (open).** Relayed: tie rate falls 54%→26% with N. Measured here: tie rate RISES 0.233 (N≈493) → 0.317 (N≈4925) → 0.367 (N≈24655). Direction opposite. Probe pools independent archives; the two may not measure the same thing — unresolved either way. |
| 2 | L3 memory hierarchy | Arithmetic correct (12 B x 1M = 11.44 MiB), systems claim does not follow: query-time embedding also needs the fitted pipeline measured this session at 44,220,235 B — 3.7x the code set, also not L3-resident. |
| 3 | speaker-role twins | Not measured. LME `cache_repr` carries no role labels; raw `regen/lme/items/*.json` and LoCoMo `id_to_row` turn indices would permit it. |
| 4 | spectral decay exponent p | **CONFIRMED.** Independent measurement p_median = 0.4634 (p10 0.4550, p90 0.4719) over 60 archives, inside the predicted 0.25-0.55. Mass-in-first-12 claim fails (38.7% vs predicted 20-30%). Best of the six: the only falsifiable prediction that held. |
| 5 | heavy tails / hubness | **REFUTED, with a nuance worth keeping.** Per-coordinate median excess kurtosis 0.93 (claim 9.71), median skew 0.079 (claim 1.58). But POOLED excess kurtosis is 5.65 — each coordinate is near-Gaussian while the pool is heavy-tailed, so the pooled statistic reflects between-coordinate variance heterogeneity, not per-axis tails. |
| 6 | AQS (sign codes . continuous query) | **HARMFUL, mechanism informative.** Resolves 100% of Hamming boundary ties (rate 0.234 -> 0.000) and costs -3.56 pp FR@3. Hamming's tie production is not a defect but a working conservatism; restoring magnitude breaks ties toward wrong documents. |

## Contents

```
coordinator/              corrected scripts (FR@3, no re-centering)
coordinator/superseded/   the ALL@3 scripts + their output, preserved with ERRATA
agent_packages/           three subagent namespaces, byte-preserved from their branches
evidence/                 results, input-cache manifest, run log
ERRATA_COORDINATOR.md     two coordinator errors, disclosed
```

## Limits

- Not the preregistered Task4F1 scale experiment. Exploratory probes on unsealed E1 caches.
- The Task4F1 seal was not crossed: no run/finalize mode, no authorization constructed, no BEAM
  corpus, no sealed gold/evidence labels.
- Partial independence only: subagent sessions are cold-start but same model family.
- `main` untouched; `docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json` not modified.
