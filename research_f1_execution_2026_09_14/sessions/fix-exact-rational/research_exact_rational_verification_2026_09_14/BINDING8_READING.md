[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Binding 8 reading — PREPARED, NOT ACCEPTED

All statements below are VERIFIED (bytes read this session) unless marked CLAIM (a document
asserts it) or RELAYED (second-hand). File hashes observed this session via `sha256sum`:
Seal V3 `e906c6d2b68b103c6c21906cbdf44acba10e31b7e5e17ffd2c7d1bbfb7a95cf4`,
Draft `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`.

## 1. The binding, verbatim (VERIFIED)

Source: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_SEAL_V3_2026-09-04.json`,
key `bindings.8_exact_rational_sign_classification_condition` (key line: loc line 112;
full object read via python `json.load` this session — VERIFIED).

Implementation condition (seal line 122, JSON key `implementation_condition_verbatim`):

> "Implementation note, not a defect in this preregistration: before any run authorization, the
> outcome-analysis implementation must honor this exact-rational rule rather than classify the sign
> from a rounded or floating aggregate. That implementation requirement belongs to the later
> execution/authorization gate and does not require changing the approved scientific draft."

Preregistered rule carried by the binding (seal line 126, JSON key `preregistered_rule_verbatim`):

> "**Sign-boundary arithmetic.** `D_t` is computed in exact rational arithmetic — every value is a
> rational with denominator dividing `5 · n_t · lcm_i(|gold_i|)` — so `D_t > 0`, `D_t = 0` and
> `D_t < 0` are exactly decidable with no tolerance and no threshold. This is a numerical-representation
> rule fixed before outcome access; it is not a practical-significance threshold and must not be read
> as one."

Binding metadata (VERIFIED, same object): `type` is "PRE-RUN IMPLEMENTATION CONDITION on the
execution/authorization gate"; `owner` is "execution/authorization track";
`not_a_scientific_amendment: true`; `no_restated_wording` (seal line 129) states the binding
carries no hand-written paraphrase — every text field is extracted from source bytes and checked
by the verifier. Condition source (CLAIM of the seal): Head Researcher re-review decision
2026-09-04 on branch `hr/rereview-t4f1-prereg-2026-09-04` commit `19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d`
(RELAYED — branch not inspected this session). Rule source (CLAIM of the seal): section 6 of the
approved draft; `source_section_sha256` `09247bce4deb5372887aa1f7ae3b79bc0c9c9dd56b35c9618d391488f5d28e62`
(seal line 125; hash NOT recomputed here — recorded as CLAIM).

## 2. The preregistered rule in the draft, verbatim (VERIFIED)

Source: `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md`.

The `D_t` definition (§3.1, lines 103–109):

> ```
> D_t = mean_i [ FracRecall@3( Native SIGN96 )_i  −  mean over 5 Haar seeds FracRecall@3( HAAR96_SIGN )_i ]
> ```
>
> Positive means Native better. Denominators are the frozen 355 / 629 / 553 / 175.

The comparator is fixed (lines 113–119): exactly five preregistered seeds
`43001, 43002, 43003, 43004, 43005`, a fixed enumerated comparator, not an inference target.

The sign-classification rule (§6, lines 229–243):

> Step 2 — only if integrity holds, exactly one of:
>
> | Category | Definition |
> | --- | --- |
> | **Full replication** | `D_t > 0` at all four tiers |
> | **Heterogeneous (partial) replication** | at least one `D_t > 0` **and** at least one `D_t ≤ 0` |
> | **No replication** | `D_t ≤ 0` at all four tiers |
>
> These three are exhaustive and non-overlapping by construction.
>
> **Sign-boundary arithmetic.** `D_t` is computed in exact rational arithmetic — every value is a
> rational with denominator dividing `5 · n_t · lcm_i(|gold_i|)` — so `D_t > 0`, `D_t = 0` and
> `D_t < 0` are exactly decidable with no tolerance and no threshold. This is a numerical-representation
> rule fixed before outcome access; it is not a practical-significance threshold and must not be read
> as one.
>
> Per-tier descriptors, subordinate to the single global category and never overriding it:
> `D_t < 0` is a **tier-local direction reversal**; `D_t = 0` is a **tier-local null**.

Integrity gate precedence (§6 lines 221–227, VERIFIED): if the signed-permutation control diverges
or nuisance trials vary, no replication category is assigned at all.

## 3. Precise restatement — what an implementation must do (my reading; NOT authoritative)

An implementation satisfies binding 8 only if ALL of the following hold on the real path:

1. **Exact inputs.** Each question's `FracRecall@3` values entering `D_t` must be reconstructed
   from discrete integers (hit counts, `|gold_i|`), never taken from a rounded or floating
   aggregate produced by the runner. Any float present in the pipeline may be integrity-checked
   against recomputation, but must not feed the sign decision.
2. **Exact arithmetic end to end.** The per-question difference, the 5-seed Haar mean, and the
   tier mean over `n_t` questions must all be computed in exact rational arithmetic
   (e.g. `fractions.Fraction`), so summation order cannot affect the result and no rounding
   error accumulates at any stage.
3. **No tolerance, no threshold, no epsilon anywhere on the decision path.** No `isclose`,
   no `abs(D) < eps` nudge, no threshold parameter, no conversion to `float`/`Decimal`-rounded
   form before comparison. Display rounding (e.g. a decimal string for humans) is permitted only
   if the sign is decided before and independently of it.
4. **Ties decided as ties.** `D_t == 0` must classify as zero: it joins the `≤ 0` side in the
   global category (so all-zero is No replication, and a zero alongside a positive is
   Heterogeneous), and it is labelled "tier-local null", never nudged to either sign.
5. **Category boundaries exact.** Full replication ⟺ all four `D_t > 0` strictly;
   No replication ⟺ all four `D_t ≤ 0`; Heterogeneous ⟺ mixed. A single exact-zero tier flips
   Full → Heterogeneous; that flip must actually happen in code.
6. **Denominator discipline.** Each tier's `D_t` must be a rational whose denominator divides
   `5 · n_t · lcm_i(|gold_i|)` where: `5` = the five fixed Haar seeds (§3.1 lines 113–114);
   `n_t` = the frozen tier question count (see §4 below); `lcm_i(|gold_i|)` = the least common
   multiple of the gold cardinalities in that tier. An implementation may additionally assert
   this divisibility as a fail-closed check.

## 4. The four tier denominators and where they come from (VERIFIED)

From the frozen cohort table (§2, lines 48–54) and confirmed at §3.1 line 109
("Denominators are the frozen 355 / 629 / 553 / 175"):

| Tier | n_t (questions) | Archives | Source lines |
| --- | ---: | ---: | --- |
| 100K | 355 | 20 | draft lines 50, 109 |
| 500K | 629 | 35 | draft lines 51, 109 |
| 1M | 553 | 31 | draft lines 52, 109 (minus exactly `1M::5, 1M::26, 1M::33, 1M::34`, line 56) |
| 10M | 175 | 10 | draft lines 53, 109 |
| Pooled (secondary, §3.5) | 1712 | 96 | draft line 54 |

Related frozen families the implementation must also respect (VERIFIED, draft §3.2 line 131
and §4 lines 189–191): ceiling-free stratum denominators **259 / 461 / 300 / 105**
(questions with `|gold| ≤ 3` per tier) and leave-one-archive-out archive counts
**20 / 35 / 31 / 10**. Both appear as `CEILING_FREE_DENOMINATORS` and `TIER_ARCHIVE_COUNTS`
in the implementation (see `PROVENANCE.md`).

## 5. What this reading does NOT do

This file interprets no outcome, authorizes no run, and discharges nothing. The verdict on whether
any implementation satisfies the above is in `DISPOSITION.md` (PREPARED, NOT ACCEPTED), based only
on synthetic inputs.
