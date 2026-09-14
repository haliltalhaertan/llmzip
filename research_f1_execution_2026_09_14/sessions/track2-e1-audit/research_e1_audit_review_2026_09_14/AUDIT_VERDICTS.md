[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 1 — Audit verdicts, read first-hand (PREPARED, NOT ACCEPTED)

I read both reports byte-for-byte via `git show origin/<branch>:<path>` without checkout.
No file was modified. This document is PREPARED, NOT ACCEPTED: I cannot accept, seal,
ratify or close anything. Labels: VERIFIED = I ran/read the bytes; CLAIM = a document
says it; RELAYED = second-hand.

## Audit 1 — raw-cache recovery independent audit

- Branch (VERIFIED): `origin/audit/e1-v2-raw-cache-recovery-independent-2026-09-13`, tip `010bcbb`.
- Report path (VERIFIED): `audit_e1_v2_raw_cache_recovery_2026_09_13/INDEPENDENT_E1_V2_RAW_AUDIT_REPORT.md` (64 lines).
- Target audited (CLAIM, stated in report): `d5441698fa8fb8404873af47233569803b887376` (parent `4bfdb82`), one additive commit in `campaign_2026_09_13/e1_v2_raw_recovery_2026_09_13/`.

### Verdict — quoted verbatim (VERIFIED, line 3 of the report)

> **`Verdict: `REQUEST_CHANGES``**

Closing line (VERIFIED): "Final verdict: **`REQUEST_CHANGES`**. The recovery and most
reported results are sound; Claim D's frozen-metric implementation must be repaired
before a PASS."

### Findings with severity — quoted titles, from FINDINGS.json (VERIFIED)

FINDINGS.json schema `INDEPENDENT_E1_V2_RAW_AUDIT_FINDINGS_V1`, verdict field
`REQUEST_CHANGES`, severity summary `{critical:0, high:1, low:2, medium:3}` (VERIFIED):

| ID | Severity | Status | Title (verbatim) |
|----|----------|--------|------------------|
| F1 | HIGH | CONFIRMED | Claim D competition implementation violates frozen per-gold D2 convention |
| F2 | MEDIUM | CONFIRMED | LoCoMo ~12pp historical statement is not an anchor |
| F3 | MEDIUM | CONFIRMED | Q_ABS_CV and Q_EFF are exactly redundant at fixed dimension |
| F4 | MEDIUM | CONFIRMED | P64 Spearman magnitude is tie-rank-method sensitive |
| F5 | LOW | CONFIRMED | 520/520 structural inequality is sample-wide, not universal law |
| F6 | LOW | DISCLOSED | Cold-start independence protocol had unavoidable early prose exposure during Git scope verification |

Required changes before PASS (VERIFIED, report's own 6-item list): (1) replace min-gold
competition with frozen per-gold D2 aggregation and regenerate all competition-derived
rows/correlations/bootstraps/prose; (2) keep bootstrap inference explicitly
descriptive/post-hoc; (3) disclose Q_ABS_CV/Q_EFF exact algebraic redundancy;
(4) replace universal wording with sample-scoped "all 520 recovered archives";
(5) keep LoCoMo centered float `0.16826334541318252`, do not anchor old ~12pp;
(6) no refit/remap/E2/Task4F1.

### What the auditor VERIFIED itself (VERIFIED from EXECUTION_LOG.txt + report)

- Byte hashes of 3 heavy archives + analysis ZIP matched before computation (VERIFIED:
  `a16bdf95…`, `87d6312e…`, `370ea409…`, `b6b7923f…`, all `match=True`).
- Cache inventory: 470 LME + 10 LoCoMo + 10 REALTALK + 2 PerLTQA files (VERIFIED).
- Headline gates re-derived from raw caches: LME SIGN `0.5419751773049645` / float
  `0.4415957446808511` (float diff `-5.55e-17`); REALTALK `0.22477507598784194` /
  `0.17253405381064954`; PerLTQA `0.488941994930817` / `0.551692074528853`;
  LoCoMo SIGN `0.23654714666441054` with independently derived float
  `0.16826334541318252` ⇒ `+6.82838013 pp` (VERIFIED).
- Corrected per-gold D2 recomputation with its own code (`competition_variants.py`,
  95 lines; `locomo_variants.py`, 60 lines — VERIFIED line counts via `git show | wc -l`).
- Non-competition lead rows and PHI/EFFDIM/DUP geometry matched exactly (VERIFIED:
  all `max_abs_diff: 0`).
- Multi-gold rates it computed: LME `296/470`, REALTALK `386/705`, PerLTQA `2322/8265`,
  LoCoMo `432/1535` (VERIFIED).

### What the auditor RELAYED rather than recomputed (VERIFIED from report text)

- The old LoCoMo `~+12pp` line: "recovered only as 'programme-reported; not recomputed'"
  (report's own words); FINDINGS.json F2: `old_approx_12pp_status: PROGRAMME_REPORTED_NOT_RECOMPUTED`.
- Lead package hash manifest/sidecar "rehashed cleanly" — a check of the lead's artifact,
  not an independent derivation (report §"Lead cross-check after Stage-1 freeze").

### Auditor's own stated limitations (verbatim in substance, VERIFIED)

- "Independence limitation: the mandatory Git scope query returned target diff prose
  before Stage-1… This is an independently recomputed review, but not a perfectly
  blind one." (report §Integrity; FINDINGS.json F6.)
- "bootstraps are descriptive/post-hoc only" (report Claim C).
- "licenses 'all 520 recovered archives', not a universal law" (report Claim B).

## Audit 2 — mechanism checkpoint independent audit

- Branch (VERIFIED): `origin/audit/e1-mechanism-checkpoint-independent-2026-09-13`, tip `ec40dc3`.
- Report path (VERIFIED): `audit_e1_mechanism_checkpoint_2026_09_13/INDEPENDENT_E1_AUDIT_REPORT.md` (179 lines).
- Target audited (CLAIM, stated in report): frozen `4bfdb820904ead1b6378b00bd5bf71c1ab2fe138`
  (V2 parent `775a09c`), clean-runner head `87641ca`, Actions run `34764744784`, artifact `10320205400`.

### Verdict — quoted verbatim (VERIFIED, report §Verdict)

> **`PASS_WITH_FINDINGS`**

With the auditor's own guardrail (VERIFIED): "This verdict does **not** upgrade E1 into
causal, confirmatory, deployable, publishable, or Task4F1-authorized evidence."

### Findings with severity — from FINDINGS.json (VERIFIED)

FINDINGS.json schema `LLMZIP_INDEPENDENT_E1_AUDIT_FINDINGS_V1`, verdict
`PASS_WITH_FINDINGS`. No HIGH/CRITICAL; 4×INFO, 2×MEDIUM, 2×LOW (VERIFIED):

| ID | Severity | Finding (verbatim, truncated only for length) |
|----|----------|-----------------------------------------------|
| F01 | INFO | Exact main/frozen/V2/evidence commits verified; V2→target is 36 commits and 33 added files. Frozen target/main untouched. |
| F02 | INFO | All 7 required source SHA-256 values match exactly… |
| F03 | INFO | All 10 required scripts reran successfully in Actions run 34764744784; no compared common scalar field differed by >1e-12. |
| F04 | LOW | Claim A is a global weak/null result, not universal subgroup null… Post-hoc only. |
| F05 | MEDIUM | P64 … Rank-tie handling changes some query-level magnitudes; no router claim. |
| F06 | MEDIUM | REALTALK within-category evidence is small-n (10 chats)… |
| F07 | LOW | Simple tie rate does not explain profile/events reversal… Ties can matter in secondary strata… |
| F08 | INFO | No Task4F1 reference, result-as-input reuse, or obvious representation refit detected in inspected E1 scripts. |
| F09 | INFO | PHI/EFFDIM/query-magnitude and LoCoMo per-query centered-float remain NOT_RUN/NOT_AVAILABLE; no refit or invented substitute. |
| F10 | INFO | V2 spec/freeze predates E1 result commits, but campaign remains post-hoc to already-observed benchmark outcomes. |

Claim-by-claim (VERIFIED, CLAIM_MATRIX.json + report §4): A PASS_WITH_FINDING, B PASS,
C PASS, D PASS_WITH_FINDING, E PASS_WITH_FINDING, F PASS, G PASS_WITH_FINDING, H PASS.
No "required changes" section exists; §7 gives three guardrails for the *next*
experiment only (freeze hypothesis first; P64 as descriptive marker; target joint
redundancy / ranking competition).

### What the auditor VERIFIED itself (VERIFIED)

- 7 source SHA-256 gates matched byte-for-byte (VERIFIED table, report §2).
- All 10 E1 scripts reran on a clean GitHub runner; committed-vs-fresh scalars agree
  to ≤1e-12 (VERIFIED: EXECUTION_LOG.txt names runs `34764532566` infra-stop,
  `34764638660` partial, `34764744784` SUCCESS).
- Own adversarial recomputation in `independent_diagnostics.py` (260 lines, VERIFIED):
  exact-join checks, leave-one-type/character/chat-out, tie-rank variants, same-archive
  verification (events Delta− 30/30, joint flip 22/30, same-sign 87/115 — VERIFIED §4F/4G).

### What the auditor RELAYED / explicitly did NOT do (VERIFIED, report §5–§6)

- RELAYED nothing as a positive claim; instead marked `PHI/EFFDIM/query-magnitude` and
  `LoCoMo per-query centered-float E1` as **NOT_RUN / NOT_AVAILABLE** — "No value was
  invented." (The frozen raw C96/qC caches were absent from the campaign snapshot.)
- Commit-chronology check (V1 disposition → V2 spec → V2 parent → first E1 result) is
  presented as evidence against spec-after-results, with the explicit caveat that it
  "does **not** make E1 preregistered" (report §2).

### Auditor's own stated limitations (VERIFIED)

- "The main epistemic risk is **selection/narrative inflation**, not a mechanical
  reproducibility defect" (report §5).
- E1 is "a post-hoc narrowing campaign over already-observed benchmarks" (report §5).
- NOT_RUN/NOT_AVAILABLE items listed above (report §6 + CLAIM_MATRIX.json `limitations`).
