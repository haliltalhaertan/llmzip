# V52 — Coordinate-Scale Stage: Deviation and Limitation Register

Date: 2026-09-07
Status: `[REGISTER — RECORDS DEVIATIONS, ADJUDICATES NONE]`
Author: Continuity Lead / co-chair. Additive. Nothing frozen is edited, no verdict is chosen, no
deviation is resolved here. Every entry names the bytes it rests on so the Head Researcher can rule
on each item separately.

This register exists because the stage's limitations are currently spread across a preregistration,
a result checkpoint, five Codex branches and two ledger entries. A reader cannot cite the stage
safely without all of them. One item below (D7) is new: it is settled here from committed bytes.

## Index

| id | subject | source | state |
|---|---|---|---|
| D1 | Aggregation order A vs B | Codex review `1aa6184` | OPEN — needs adjudication |
| D2 | Preregistration §7 / §9 interpretation conflict | prereg `de667211` | OPEN — needs an explicit deviation ruling |
| D3 | Uncertainty analysis is post-outcome | Codex bootstrap `540580cf` | RECORDED — scope must travel with any citation |
| D4 | Block denominator instability | checkpoint `1c725a56`, bootstrap `540580cf` | RECORDED — bars the comparative claim |
| D5 | Seal gate did not cover the transitive LoCoMo dependency | Codex review `1aa6184` | RECORDED — retrospectively unchanged |
| D6 | Result combiner accepted malformed synthetic records | Codex review `1aa6184` | RECORDED — real records separately verified |
| D7 | LongMemEval cluster bootstrap | this document | **SETTLED — ill-posed, not merely undone** |
| D8 | Signed-permutation control not re-executed in this stage | LoCoMo audit `692f599e` | RECORDED |
| D9 | Top-3 document IDs not persisted | LoCoMo audit `692f599e` | RECORDED — bars a selection-identity claim |
| D10 | Stale sentence in the frozen preregistration | prereg `de667211` | RECORDED — deliberately not edited |
| D11 | No Drive backup for this stage | this session | OPEN — owed |

---

## D1 — Aggregation order: A and B are different statistics

`A` is the mean of the ten per-seed gain/loss ratios. `B` is the ratio of the seed-mean gain to the
seed-mean loss. The sealed runner's headline output is `B`. A natural reading of preregistration §7
is `A`. They are not the same statistic and the outcome was known before anyone noticed.

Both are already recoverable from the published bytes: the runner persists `frac_*_per_seed`
alongside the seed-mean ratio, so no file needs to change to preserve both. Recomputed from the
summaries at `591e5d0f`:

| | LoCoMo B | LoCoMo A | LongMemEval B | LongMemEval A |
|---|---:|---:|---:|---:|
| full arm | 0.726107 | 0.727186 | 0.656334 | 0.656978 |
| block arm | 0.651643 | 0.445443 | 0.308459 | 0.316511 |
| interaction | 0.074464 | 0.281744 | 0.347876 | 0.340467 |

The divergence is a block-arm phenomenon. On the full-mixing arm the two definitions agree to
0.0011 (LoCoMo) and 0.0006 (LongMemEval); on the block arm they differ by 0.206 and 0.008. The
headline full-mixing observation is therefore insensitive to the choice; the comparative
block/interaction claim is sensitive to it, and neither definition rescues that claim (see D4).

**Not adjudicated.** Do not declare either definition *the* preregistered estimand after the fact.
Whichever is ruled primary, both must remain published.

## D2 — The frozen preregistration contradicts itself on interpretation

§7 makes the per-arm fraction primary and the interaction secondary. §9 still ties the positive
mechanism reading to an undefined "large `I`". A reader can satisfy one clause and violate the
other. The document is frozen and must not be edited; this is the deviation record §2 of the
chain-of-custody rules requires. **Not adjudicated.** Closing this by selecting the clause that
favours the observed outcome would be exactly the post-outcome tuning the program forbids.

## D3 — The uncertainty analysis is post-outcome

The bootstrap plan and code were committed before the bootstrap ran (`54605e28` precedes
`398c2ea4`), but the original experiment's results were already known. It is therefore a post-hoc
sensitivity analysis, not part of the preregistered design, and it is conditional on the same fixed
ten rotation seeds. Three schemes, 10,000 replicates each. **Must not be presented as pre-outcome
preregistration.**

## D4 — Block denominators are unstable, and not only on LoCoMo

The block arm loses very little, so the fraction divides by a near-zero quantity. On LoCoMo the
per-seed denominator changes sign inside its own envelope (−0.0066 to +0.0164) and per-seed
fractions run from −3.40 to +2.64. The L-055 checkpoint already declared the LoCoMo block fraction
non-interpretable. The independent bootstrap review extends the problem to LongMemEval: replicates
containing at least one non-positive seed denominator number 8,910/10,000 (LoCoMo question),
8,410/10,000 (LoCoMo cluster) and 3,306/10,000 (LongMemEval question).

Consequence, recorded not adjudicated: under both aggregation definitions and all three schemes,
every interaction percentile interval spans zero, and every full-arm interval crosses the 0.70 band
boundary (`B_full`: LoCoMo question [0.6354, 0.8372], LoCoMo cluster [0.6197, 0.9041], LongMemEval
question [0.5679, 0.7618]). The `MOST` versus `PARTIAL` band difference cannot be carried as a
population-level category difference. **This is not a significance test and not evidence that no
mechanism exists.**

Evidence limit that travels with these counts: the bootstrap CSVs store each replicate's
denominator min/max/mean, not every seed's denominator, so some within-seed exact-zero counts
cannot be independently re-derived.

## D5 — The seal gate did not cover the transitive LoCoMo dependency

The automatic pre-run gate hashed the bound files but not the LoCoMo common source reached through
them. A retrospective check found that source unchanged (blob `67004549`), and the LoCoMo
reproduction audit verified it independently. This is a **control-coverage defect, not observed
manipulation**, and it must be described that way. A future seal should bind the transitive closure.

## D6 — The result combiner accepted some malformed synthetic records

Found by review of the combiner, not by any real record failing. The real records were then
verified separately: 92,100 LoCoMo + 28,200 LongMemEval rows PASS on full question×seed×arm
coverage, score range and finiteness, native repeats, paired Native/Scaled-Native **metric**
equality, and summary means; 18 deliberately corrupted samples were rejected. Metric equality is
not top-3 ID or bit-code equality. This narrows current record risk; it does not repair the
combiner.

## D7 — The LongMemEval cluster bootstrap is ill-posed, not merely undone (SETTLED HERE)

The handover carries this as an open item: no shared conversation mapping was established for
LongMemEval, so its conversation-clustered bootstrap was not run, and a successor is warned not to
mistake a question or archive id for a conversation.

It is stronger than that, and the answer is already in committed, hash-pinned bytes:

- `docs/v52/task3/V52_T3A1_PROTOCOL_PATCH.md` on `main` records: *"Dependency graph: 1
  component(s), largest=470/470. question-level bootstrap cannot be interpreted as independent
  underlying-memory population inference."*
- The same finding is stated inside `adapters/longmemeval_v52_adapter_v2.py`, whose SHA256
  `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` is the exact value pinned as
  `A2_SHA256` by the frozen LongMemEval base, verified here. The adapter is therefore the artifact
  the pipeline actually runs, not a stale note.

All 470 primary questions lie in **one** shared-session connected component. A cluster bootstrap
needs at least two exchangeable clusters; with a single component, cluster resampling either
returns the identical dataset every replicate (zero variability, no information) or requires an
arbitrary partition that violates the very independence assumption the scheme exists to respect.

**Therefore:** the missing LongMemEval cluster bootstrap should not be scheduled as outstanding
work. What is genuinely absent is a *different* dependency-aware inference scheme for a single
connected component, which is a design question, not a re-run. The asymmetry with LoCoMo is
explained rather than anomalous: LoCoMo's ten clusters were recovered from producer archive-ordinal
metadata, and ten is not one.

This also means the LongMemEval question-level bootstrap that was run inherits the T3A1 warning
verbatim: it is a sensitivity analysis, never a population inference.

## D8 — The signed-permutation control was not re-executed in this stage

The preregistration lists signed-permutation Hamming invariance. The frozen base implements it in
its own `run` function and retained upstream output records it passing. The scale runner calls base
helpers rather than `base.run`, so this stage's invocation did not re-execute it. **Retained
upstream evidence is not a control verified during this run.**

## D9 — Top-3 document IDs were not persisted

The saved rows carry question scores and tie-scheme metadata, not selected document IDs. Identical
scores therefore cannot certify identical document selection. No such claim is made anywhere, and
none may be added later.

## D10 — A stale sentence remains inside the frozen preregistration

The preregistration's header still reads "No runner exists, no workflow exists". That was true when
v3 was written and false by the time it was sealed. It is left byte-unchanged deliberately: the
document is the object that was reviewed and sealed, and corrections in this program are additive.
This register is the correction.

## D11 — No Drive backup exists for this stage

The boundary-localization stage required a Drive content backup before its trigger. This stage's
seal recorded that no Drive access was available and set the requirement false with the reason
stated. The backup is **owed** and has never been performed for the coordinate-scale outputs or for
the five Codex packages. Do not describe any of it as backed up.

---

## What a citation of this stage must carry

> `[LOCOMO COMPUTATIONAL REPRODUCTION PASS — SAME METHOD, NOT INDEPENDENT REPLICATION]`
> `[COMPARATIVE MECHANISM CLAIM NOT ESTABLISHED — DENOMINATOR INSTABILITY AND PREREGISTRATION DEVIATIONS]`
> `[UNCERTAINTY ANALYSIS IS POST-OUTCOME]`
> `[NOT INDEPENDENTLY AUDITED AS A WHOLE STAGE]`

## Outcome boundary

LoCoMo/LongMemEval mechanism track only. No corpus was read, no experiment run, no benchmark
outcome computed for this register. No Task 4F1 artifact, candidate, seal, authorization or HMAC
material was touched; Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
FORBIDDEN`.
