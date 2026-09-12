# Decisions and gates for parent disposition

**NOT SEALED / NOT AUTHORIZED. All acceptance gates below are OPEN.**

The user delegated routine research-design decisions to the lead. These are
concrete proposals for that lead to accept, amend, or route to HR; they are not
requests to pause the authorized drafting/publishing work. None of the proposal
statuses below has been silently changed to approved. A disposition must identify
the exact draft/constants SHA256, who made it and under what design authority,
which proposals are accepted or changed, and the resulting reviewed digest.
Design disposition cannot stand in for seal/run/outcome authorization.

| ID | Proposed resolution / exact issue | Required disposition and gate |
|---|---|---|
| P1 | Primary `SIGN96 - PQ96` at fractional R@100 on each benchmark; original `SIGN96 - RABITQ96` cancelled | Lead/HR explicitly chooses this or an amended primary and explains scope. No primary exists by default. Never silently choose top32 RaBitQ. |
| P2 | Plain PQ96 included; OPQ and top32 RaBitQ descriptive; d96 one/two-bit RaBitQ ineligible and not scheduled for quality evaluation; full arm/scoring table in draft | Accept exact arm set, dimensional confound wording, native scoring metrics, storage boundary, and no-fallback failure policy. Int8 calibration/rounding and random floor streams must be specified in reviewed implementation. |
| P3 | Literal 20-seed panels in constants; distinct OPQ internal-PQ/final-PQ panels; conditional RaBitQ randomness mapping | Accept panel values and index pairing; implementation review binds every RNG call/version, initialization/training stage and frozen tie scheme. Seed count is HR-bound, new literal values are proposals. No hidden defaults or pseudo-replicated deterministic arms. |
| P4 | Gold bins 1,2,3-5,6+; min(k,N) distinct retrieval with full gold denominator; unexpected zero-gold/missing gold fail; empty-bin and stratum-CI rules | Accept exact strata and metric edge semantics before inspecting distributions. HR required strata, not these boundaries. Do not optimize bins after outcomes. |
| P5 | Fixed-panel paired 10k bootstrap; seed61001, linear percentile95% CI, cluster LoCoMo/question LME with limitations; descriptive secondary intervals; proposed 2-pp practical rule with inconclusive wording | Accept the 2-pp R@100 rule as a pre-outcome convention, not an empirically calibrated threshold; no equivalence claim from a CI containing zero, no automatic retargeting of old kill/bands, no mechanism kill. Any program-level consequence needs its own explicit disposition. |
| R1 (draft gate 2) | Parent-owned **historical cost-script replay**, not run in this branch | Supply exact historical script/input/receipt commit-path-digests, platform/package locks, command/exit, raw output and comparison against COST's probes. A reviewed complete replay CAN CLOSE R1 specifically. Partial Windows checks/environment readiness cannot. Future runner RNG/auxiliary/negative checks are not requirements imposed on this historical script. Supplementary constructor/C4 checks remain separately scoped. |
| I1 (draft gate 3) | **Future actual runner integration:** code-size/complete-serialization/auxiliary checks, RNG propagation and negative cases | Reviewed code + locked implementation + synthetic integration receipt required. Remains OPEN even when R1 closes. Historical cost replay cannot replace these future-runner tests. |
| I2 | Frozen feature/query/cohort/identity/tie/control source mapping, fit-leakage audit, and precise per-arm scoring/training/RNG propagation | Bind actual source paths and hashes without changing frozen artifacts; preserve corrected/raw cohorts. Unsupported binding or uncontrolled training blocks seal consideration. This task does not inspect corpus or per-question outputs to close it. |
| I3 | Complete per-archive preprocessing/shared/index/auxiliary inventory and actual state sizes | Report shared bytes and effective B/vector; index-only published S0 is a lower component, not a complete deployment total. Require archive-specific validation after separately authorized fitting, before scoring. |
| A1 | Seal authorization | Separate explicit HR authorization after accepted design, replay and implementation review. Currently absent. Digest publication is not a seal. |
| A2 | Corpus/control execution and outcome access | Separate explicit scope-appropriate authorization. Currently absent. No run/finalize/pilot/HMAC or Task4F1 access is implied. |

The C4 theoretical interpretation remains **NOT ESTABLISHED**. It is unnecessary
for the marginal-byte decision: counted stored bytes and functional scale suffice.
Do not hold design publication waiting for a theory claim, or mark the theory
established to close a list. Likewise C7 needs a portable API-binding check, not a
promise of a particular crash. No MRQ/JQ-JHQ research claim is part of this package.

Completed and not to repeat: source clone/base verification, raw-object/digest
checks, old-draft/HR reconciliation, source map, concrete seed/strata/primary
proposals, and published-scalar SIMHASH derivation. The parent is already handling
runtime replay; do not launch a duplicate. The next action is lead review of this
branch and a digest-bound disposition. No main ledger/state update is authored here.
