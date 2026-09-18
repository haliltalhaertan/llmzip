[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# MECHANISM_FINDINGS — what E1 actually claimed about why SIGN beats float

Work is PREPARED, NOT ACCEPTED. Nothing here is sealed, ratified, or closed.
Status words are the line's own: "established" never appears in E1's vocabulary for the
mechanism; the strongest licensed words are "survived", "descriptive marker", "candidate".
Locator form `origin/<branch>:<path>` (§/quote where useful). VERIFIED = I read the bytes.

## One-paragraph answer

E1 did not produce a causal mechanism. It produced a *narrowed* one: after refuting or
nulling six simpler stories, the line's surviving, independently audited claim is that
SIGN advantage is a **query–archive ranking-regime interaction**, for which joint
`BOT64−TOP64` retrieval polarity (P64) and per-gold TOP-vs-BOT ranking-competition gaps are
**descriptive regime markers** — weak per query, materially stronger aggregated by
archive/chat. The single strongest structural fact E1 established is universal *in its
recovered sample*: in all 520 archives, high-variance TOP64 sign bits are more mutually
redundant and low-variance BOT64 bits carry higher binary effective dimension — but the
line itself shows this asymmetry does **not** determine SIGN-vs-float direction (LME
archive-level association ≈ null). The "signal-versus-redundancy tradeoff" is a working
hypothesis, explicitly not causal proof. The final Claim-D numbers rest on corrected
audit rows whose full lead rerun + re-audit are still pending.

## (a) SUPPORTED by the line's evidence (all descriptive, none causal)

### S1. P64 (BOT−TOP retrieval polarity) tracks SIGN−float direction — regime marker, not law
- Bridge (post-hoc discovery, 6/6 sign concordance, Pearson r=0.855 descriptive only):
  `origin/research/e1-sign-float-mechanism-2026-09-13:campaign_2026_09_13/e1_mechanism/E1_BRIDGE_REPORT.md`:
  > "Observed sign concordance: **6/6**. Descriptive Pearson `r=0.855`; Spearman `rho=0.829`."
  > "These are **not hypothesis-test p-values** and must not be presented as such."
  (VERIFIED read, 66 lines.)
- Checkpoint query-level (weak) and regime-level (stronger) Spearman `rho(Delta_q, P64_q)`
  (CLAIM, `origin/research/e1-mechanism-checkpoint-frozen-2026-09-13:…/E1_MECHANISM_CHECKPOINT.md` §§3–4,
  VERIFIED read): LME **+0.108**, PerLTQA **+0.109**, REALTALK **+0.075**; PerLTQA by character
  ≈ **+0.319** with same sign in **29/30** characters; REALTALK by chat ≈ **+0.418**, 9/10 chats.
- Raw-cache recovery extends this to LoCoMo +0.2495 (CLAIM, `…/E1_V2_RAW_CACHE_RECOVERY_REPORT.md` §A).
  Independent checkpoint audit recomputed: LME +0.1084, PerLTQA +0.1092, REALTALK +0.0746,
  character +0.3188, chat +0.4182, all leave-one-unit-out ranges positive (CLAIM, checkpoint
  audit report §Claim D, VERIFIED read).
- LIMIT (line's own): rank-tie-method sensitive (REALTALK +0.0746 average-rank vs +0.1266
  dense-rank diagnostic; CLAIM, audit §Claim D) → "licensed only as a descriptive regime
  marker, never as a router" (CLAIM, R2 disposition F4).
- My cross-check (VERIFIED): the checkpoint's §3 figures (+0.108/+0.109/+0.075) match the
  recovery's §A (+0.1086/+0.1092/+0.0745) and both audits' recomputation — three-way
  agreement on P64 point estimates.

### S2. Structural binary asymmetry: TOP64 more redundant / BOT64 higher binary effdim — 520/520
- Recovery report §B (CLAIM, VERIFIED read):
  > "TOP64 sign bits are more mutually correlated than BOT64 and BOT64 has higher binary
  > effective dimension in **every recovered archive**: `PHI_GAP > 0`: **520/520**,
  > `EFFDIM_GAP > 0`: **520/520**."
- Independently confirmed including disjoint TOP32/BOT32 robustness at 520/520, no exact-zero
  C entries, no duplicate archives (CLAIM, raw-cache audit §B, VERIFIED read).
- LIMIT (line's own): archive-level association with Delta is null on LME (−0.0140/+0.0001)
  and fragile elsewhere (n=10 sets); "structural redundancy asymmetry is therefore not
  sufficient to determine retrieval outcome" (CLAIM, R2 report §Structural binary asymmetry).
  Wording restricted to sample scope: "In all 520 recovered archives…" (CLAIM, R2 disposition F5).

### S3. Per-gold ranking-competition gaps track Delta positively on all four benchmarks — PROVISIONAL
- Corrected (audit-computed) average-rank Spearman, strict / tie (CLAIM, R2 disposition F1,
  VERIFIED read): LME +0.1417/+0.1405, REALTALK +0.0979/+0.1228, PerLTQA +0.2542/+0.2798,
  LoCoMo +0.0949/+0.1038. PerLTQA events strongest (strict +0.3979); profile weak under the
  corrected metric (+0.0573/+0.0187) — a material interpretation change from R1 (CLAIM, R2 report).
- STATUS: `CORRECTED_SUMMARY_FROM_INDEPENDENT_AUDIT / FULL_PAYLOAD_PENDING` — the lead's full
  per-query rerun under `R2_COMPETITION_RERUN_CONTRACT.md` is "NOT YET EXECUTED BY LEAD"
  (CLAIM). Treat S3 as the leading *unconfirmed* quantitative leg, not as established.

## (b) REFUTED or NOT SUPPORTED (line's own verdicts)

### R1. "Low-variance axes are individually more informative" — REFUTED (pre-run, by old evidence)
- `origin/research/e1-sign-float-mechanism-v2-2026-09-13:…/E1_V1_DISPOSITION.md` (VERIFIED read):
  > "the V1 verbal mechanism — that task-relevant discrimination is carried
  > disproportionately by lower-variance coordinates — is too strong and is contradicted by
  > an older LongMemEval pilot… all 96 axes have positive marginal gold-vs-nongold signal
  > and… the strongest individual axes are high-variance axes."
- Checkpoint §2A concurs (CLAIM, VERIFIED read). This is the pivot on which V1→V2 turned.

### R2. "Scalar archive heterogeneity explains SIGN advantage" — NOT SUPPORTED on LME
- 470/470 exact join; Spearman vs Delta_q: `cv_sigma` −0.0096, top32 share +0.0213, sign
  entropy +0.0336, archive N +0.0084, correlation summaries ≈ −0.07…−0.10
  (CLAIM, `…/E1_LME_SECONDARY_REPORT.md`, VERIFIED read; checkpoint §2B reproduces).
- Audit: PASS_WITH_FINDING; adversarial note — post-hoc strata (e.g. single-session-preference
  n=30, rho −0.3877) are leads for a frozen test, not overturns (CLAIM, audit §Claim A).
- Note for the programme: this is a *within-LME query-level* null, distinct from the already-
  rejected cross-seed variance-heterogeneity story (`audit_v52_t4c3`, Q5>Q1 3/5) — E1 did not
  re-litigate that audit; it killed the scalar story on a second front.

### R3. "Marginal-axis signal concentration explains Delta" — NOT SUPPORTED on LME
- Positive-signal effdim rho ≈ +0.037, top-16/32 share ≈ −0.03, total positive mass ≈ +0.030,
  largest |·| ≈ −0.114 (negative mass) (CLAIM, checkpoint §2C, VERIFIED read; audit §Claim B: PASS).

### R4. "Differential contextual complementarity (BOT−TOP drop-loss)" — NOT SUPPORTED
- `rho(Delta_q, drop_loss_BOT − drop_loss_TOP) ≈ +0.030`, practically null — while absolute
  TOP/BOT drop losses are non-null (+0.108/+0.254 pp means; rho +0.25/+0.20 with Delta)
  (CLAIM, checkpoint §2D; audit §Claim C: PASS, VERIFIED read).

### R5. "Aggregate boundary-tie rate causes the PerLTQA reversal" — REFUTED
- Events tie rate 27.08% < profile 31.23%, yet events Delta −12.41pp vs profile +20.44pp;
  untied subsets preserve the reversal (−9.81pp / +19.65pp) (CLAIM, checkpoint §2E; audit
  §Claim G: PASS_WITH_FINDING with guardrail that ties matter in social_relationship).
- Bridge report already falsified the scalar tie story at benchmark level (LME 23.4% /
  REALTALK 35.46% / PerLTQA 29.20% vs Delta signs) (CLAIM, bridge report, VERIFIED read).

### R6. Q_ABS_CV and Q_EFF as two signals — REFUTED as independent evidence (audit)
- `Q_EFF = 96/(1+Q_ABS_CV²)` exactly (residual ≤ 2.84e-14, rank corr −1, all four benchmarks);
  one degree of evidence, not two (CLAIM, R2 disposition F3; audit §F, VERIFIED read).

### R7. Duplicate-code collapse as broad mechanism — NOT SUPPORTED
- DUP_GAP = 0 in every PerLTQA and LoCoMo archive; REALTALK mean ≈ 0.000642; LME mean
  ≈ 0.007856 with rho −0.0273 (CLAIM, recovery §D; audit §E, VERIFIED read).

## (c) RESTATED without new evidence (hypotheses the line carries but did not test)

- **Signal-versus-redundancy tradeoff** ("high-variance coordinates carry stronger marginal
  signal but more redundant binary information; query semantics decides which side matters"):
  working hypothesis only, in every document that states it (recovery §V2 disposition, R2
  report, checkpoint §7 — all VERIFIED read). No experiment in the line manipulates redundancy
  independently of variance rank, so the tradeoff is named, not evidenced.
- **Query–archive interaction as causal story**: the checkpoint's §5 same-archive flip
  (22/30 characters flip both Delta and P64 profile→events; 87/115 pairs same sign) shows
  archive-only geometry is *insufficient* — a valid descriptive control — but sections are not
  exchangeable interventions, so no causal interaction is identified (the audit §Claim F says
  exactly this: "not a causal identification result", CLAIM).
- **Haar-mixing damage as heterogeneity evidence** (bridge report's unification list): cited as
  consistent-with, never re-tested inside E1. Restatement.

## The surviving explanation, carefully, with limits

> **Licensed narrow claim (checkpoint §7, VERIFIED):** "SIGN advantage is a query–archive
> regime interaction. `BOT−TOP` retrieval polarity is a descriptive marker of that regime,
> not an individual-query law. The underlying cause is not explained by scalar variance
> concentration, marginal axis strength, simple low-variance complementarity, or aggregate
> boundary-tie incidence. Joint sign-bit redundancy/effective binary dimension and
> query-specific ranking competition remain the main unresolved candidates."

- What would most damage this conclusion: the P64 regime-level aggregation rests on n=30
  characters / n=10 chats with post-hoc strata everywhere (the audit's own "main epistemic
  risk is selection/narrative inflation", §5, CLAIM). I tested this assumption by checking
  the audit's leave-one-unit-out ranges (PerLTQA char +0.2626…+0.4094; REALTALK chat
  +0.3333…+0.7500 — all positive, CLAIM) and the within-section replication (all four PerLTQA
  sections positive, +0.142…+0.313, CLAIM, checkpoint §4 / audit §Claim E). It survives those
  attacks but has never faced a frozen unseen benchmark — that is precisely DELIVER 4.
- Single most valuable thing in the repository right now: the **520/520 structural asymmetry
  (S2) + the per-gold competition direction (S3)** are the only two mechanism legs that live
  at the *bit level* rather than the scoreboard level. If S3's rerun confirms, the programme
  finally has a measurable quantity (TOP−BOT strictly-closer/gold-tie gap) that moves with
  Delta inside every benchmark — the first candidate of that kind.
