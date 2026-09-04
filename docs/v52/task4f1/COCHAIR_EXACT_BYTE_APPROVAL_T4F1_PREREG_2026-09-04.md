# Scientific Co-Chair — Exact-Byte Re-Review of the Task 4F1 Preregistration

Reviewer role: **Scientific co-chair**, cold start, session-independent.
Review date: 2026-09-04
Review type: Byte-exact re-review of the amended draft, bound to a commit and a digest.

---

## 0. Review target and the digest I measured myself

| Field | Value |
| --- | --- |
| Repository | `https://github.com/haliltalhaertan/llmzip` |
| Reviewed commit | `c0133fce9b755d13d9be3016e8e06f493d6b275b` |
| Path | `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` |
| Required SHA256 | `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` |
| **SHA256 I measured** | `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` |
| **Match** | **YES — proceeding with review** |
| Measured size | 14688 bytes, 285 lines |
| Method | `git cat-file -p c0133fce…:docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md \| sha256sum`, repeated against the checked-out working-tree file with `sha256sum` |

The repository default branch does not point at `main`; `main` was fetched by name and the commit
addressed directly. The digest was measured before any line of the draft was read.

### 0.1 Context anchors — each verified before use

| Artifact | Anchor | Measured | Match |
| --- | --- | --- | --- |
| Governing prompt for this review | `prompts/V52_TASK_4F1_EXACT_BYTE_COCHAIR_REREVIEW_PROMPT_2026-09-04.md` | `7e048be7c3728db70bbe771ebf4d01fd073d774a4fc2dd2c1df29be7565a27fd` | YES |
| Predecessor draft (what the first review saw) | at `c0133fc^` = `d0b650d6a3dd17fdf73f23a5757f44e4f0c9eca1` | `ec3443ed4c60eb12e098192abf7b414e034d89fc63a9f42f9d0a02c36a696e45` | YES |
| First co-chair review (the A1–A6 source) | `cochair/review-t4f1-prereg-2026-09-03` @ `ecbf765e7f0ef06ae903d5aba6d2e9a835cdf3c2` | `6493000b205126bc7826536d03b9b97fb9f92fd84c5387c1461fbb07b447a970` | YES |
| Head Researcher re-review decision | `hr/rereview-t4f1-prereg-2026-09-04` @ `19d9cbbfcbc48f80dc63ac179f2aa67e7eed490d` | `8795abc7b58b3bae8f2333ba630f95642e9d2e653a31478d221ceb9d71272f3f` | YES |
| Sealed 4F0 restricted cohort | `audit_v52_t4f0_restricted_refreeze_2026_08_31/estimand_primary_cohort.csv` | `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` | YES |

The predecessor draft carried by `c0133fc^` hashes to exactly the `ec3443ed…` bytes the first review
recorded as its target. The amendment commit therefore transforms the reviewed predecessor into the
reviewed successor with no intervening substitution.

The Head Researcher branch carries the draft at `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44`
— the same bytes reviewed here. That is recorded as a **byte-provenance fact only**. No verdict,
gate result or conclusion from that artifact, from any commit message, from
`docs/CONTINUITY_LEDGER.md` or from `ops/CURRENT_STATE.json` was read as evidence or relied upon at
any point. The A1–A6 text was read from the first review's file, not from any summary of it.

---

## 1. Verdict

`APPROVE WITH NOTES`

A1–A6 are all adequately discharged on the exact amended bytes; the amendments introduce no new
scientific inconsistency; the draft remains outcome-free with respect to Task 4F1.

**None of the notes in §5 requires an amendment, and none requires new bytes.** This approval is
given on `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` as it stands and is
intended to close the co-chair condition in the draft's header and its §9, unblocking sealing of
these exact bytes.

---

## 2. Per-amendment findings

Each amendment was located as a **mechanism in the file**, not as a claim about the file. The diff
`d0b650d..c0133fc` restricted to the draft contains exactly five hunks, and every hunk maps onto one
or more of A1–A6; no other section of the draft was touched.

| # | Amendment | Discharged | Mechanism located at |
| --- | --- | :---: | --- |
| **A1.1** | Ceiling-free stratified contrast added as the **primary** cross-tier comparability instrument; `D_t` restricted to `\|gold\| ≤ 3`; denominators 259 / 461 / 300 / 105; additionally reported within `4–6` and `7+` | **YES** | §3.2 lines 121–134 (definition l. 127; ceiling-1.000 rationale l. 130; denominators l. 131; remaining strata l. 133) |
| **A1.2** | `D_t^norm` demoted to a declared sensitivity statistic; stated as a `\|gold\|`-weighted mean with weights `w_i = max(1, \|gold_i\|/3)`; weights differ in distribution across tiers; **not** a rescaling of `D_t` and **not** a cross-tier comparability device | **YES** | §3.2 lines 136–147 (demotion l. 136; weight form l. 143; per-tier weight divergence l. 144–145; both negations l. 142; "sensitivity statistic only" l. 146–147) |
| **A1.3** | §2.2/§6 conflict resolved: §6 category from `D_t` alone; discordance a labelled sensitivity flag that never overrides or vetoes | **YES** | §2.2 lines 92–95. The predecessor's "interpreted jointly" / "A conclusion supported by only one of the two is not reported as supported" is **removed** — 0 occurrences remain |
| **A2** | Sign-boundary arithmetic pre-specified: exact rational arithmetic, denominator dividing `5 · n_t · lcm_i(\|gold_i\|)`, `> 0` / `= 0` / `< 0` exactly decidable, no tolerance, no threshold; recorded as a numerical-representation rule, not a practical-significance threshold | **YES** | §6 lines 239–243 |
| **A3** | `D_t = 0` descriptor corrected: reversal restricted to `D_t < 0`, "tier-local null" added for `D_t = 0`, both subordinate to the single global category | **YES** | §6 lines 245–246. Predecessor's "`D_t ≤ 0` … tier-local direction reversal" is removed |
| **A4** | One descriptive stability statistic pre-specified: leave-one-archive-out min–max range per `D_t` over 20 / 35 / 31 / 10 archives, alongside per-seed min–max; explicitly not a CI, not an SE, no coverage or population semantics | **YES** | §4 lines 188–193 |
| **A5** | Win/tie/loss scoped: same cross-tier bar as ALL@3; tie structure driven by `\|gold\|` composition (29.0% at 100K vs 17.9% at 1M); reported within gold-cardinality strata for cross-tier reading; `W / (W + L)` added | **YES** | §3.3 lines 154–160 |
| **A6** | §4 aligned with §3.1 on the Haar comparator: seeds constitutive of the comparator's definition, not a sample from it; spread licenses no claim about unenumerated rotations | **YES** | §4 lines 181–184. Predecessor's "The only genuine stochastic element is seed choice" is removed — 0 occurrences remain |

### 2.1 Independent recomputation of every structural fact the amendments introduce

Cohort composition facts are not outcomes and were recomputed from the sealed cohort CSV
(digest verified above) over its 1,712 rows with `primary_evidence_cohort_eligible == True`.
Every value the amended text asserts reproduces **exactly**:

| Quantity | Draft (line) | Recomputed | Match |
| --- | --- | --- | :---: |
| `\|gold\| ≤ 3` denominators (A1.1) | 259 / 461 / 300 / 105 (l. 131) | 259 / 461 / 300 / 105 | ✓ |
| Ceiling on that stratum | exactly 1.000 (l. 130) | `min(1, 3/\|gold\|) = 1` for every `\|gold\| ∈ {1,2,3}` | ✓ |
| Mean `\|gold\|` per tier (A1.2) | 3.08 / 4.26 / 8.59 / 7.47 (l. 145) | 3.08 / 4.26 / 8.59 / 7.47 | ✓ |
| Archive counts (A4) | 20 / 35 / 31 / 10 (l. 190) | 20 / 35 / 31 / 10 (pooled 96) | ✓ |
| Share `\|gold\| = 1` (A5) | 29.0% at 100K, 17.9% at 1M (l. 158) | 29.0% (103/355), 17.9% (99/553) | ✓ |
| Tier denominators (untouched §3.1) | 355 / 629 / 553 / 175 (l. 109) | 355 / 629 / 553 / 175, pooled 1712 | ✓ |
| Excluded archives (untouched §2) | `1M::5, 1M::26, 1M::33, 1M::34` (l. 56) | absent from the eligible set | ✓ |
| Strata `4–6` / `7+` occupancy (A1.1) | reported as strata (l. 133) | 66/30, 56/112, 116/137, 37/33 — non-empty in all four tiers | ✓ |

The `|gold| ≤ 3` denominators are identical, tier by tier, to the CSV's
`all_at_3_structurally_possible == True` counts. The stratum A1 designates is therefore exactly the
ALL@3-structurally-possible subpopulation. This is consistent, not contradictory — see §3.4.

**A2 verified as mathematics, not as prose.** With `FracRecall@3_i = a_i / |gold_i|`, `a_i ∈ {0,1,2,3}`
integer — the form implied by the untouched ceiling `min(1, 3/|gold|)` at §2.2 l. 71–72 and its
worked value `3/8 = 0.375` at l. 72 — the five-seed mean has denominator `5|gold_i|`, so
`D_t = (1/(5 n_t)) · Σ_i (5a_i − Σ_s b_{i,s})/|gold_i|`, whose denominator divides
`5 · n_t · lcm_i(|gold_i|)`. The claim is correct as written. The minimum `|gold_i|` among eligible
rows is 1 (recomputed), so the `lcm` is well-defined, no eligible row divides by zero in `3/|gold_i|`,
and the exact-decidability guarantee has no degenerate case.

---

## 3. New scientific inconsistency — finding

**Finding: none.** The four pairings the review scope singles out were checked directly against the
amended bytes.

**3.1 §2.2's interpretation rule against §6's decision rule.** This was the blocking conflict.
§2.2 l. 93 now states "The §6 global category is assigned from `D_t` alone", and §6 l. 233–235
assigns the three categories on the sign of `D_t` and on nothing else. The two now agree on a single
decision input. The predecessor's competing joint-interpretation veto is gone. Discordance is given a
defined, non-overriding role (§2.2 l. 94–95), so the case that previously had two incompatible
resolutions now has exactly one.

**3.2 §3.1's estimand definition against §3.2's new instrument.** No contradiction, and the two
"primary" usages do not collide. §3.1 l. 111 keeps the primary estimand family as the four `D_t` on
denominators 355 / 629 / 553 / 175; §3.2 l. 123 designates a primary *cross-tier comparability
instrument*, scoped by that noun phrase, on its own separately frozen denominators 259 / 461 / 300 /
105. §6 draws the category from the §3.1 quantity. The decision input is unambiguous on the bytes.

**3.3 §6's partition after A3.** `{all D_t > 0}`, `{some > 0 and some ≤ 0}`, `{all ≤ 0}` remains
exhaustive and mutually exclusive, and A3 did not alter the predicates — it corrected only the
per-tier descriptor vocabulary attached beneath them. A tier at `D_t = 0` is now named a tier-local
null rather than mislabelled a reversal, while still falling inside the `≤ 0` predicate the global
category uses. That subordination is what A3 asked for, and §6 l. 245 states it.

**3.4 §3.3's descriptive statistics against §2.2 and §3.2.** A5 imports the ALL@3 cross-tier bar onto
W/T/L and supplies the stratified route and the tie-excluded summary, matching §2.2's composition
argument and §5 l. 211's mandated buckets. The domain coincidence noted in §2.1 — the new primary
instrument is computed on exactly the ALL@3-structurally-possible set — is not a contradiction: the
§3.3 bar is on the ALL@3 **metric**, which gold cardinality drives directly, whereas §3.2 l. 127
computes the **§3.1 FracRecall@3 contrast** restricted to a stratum. Different statistics, one shared
domain. Restricting to a composition-matched stratum is the standard remedy for the confound §3.3
bars ALL@3 for.

**3.5 Residual role of `D_t^norm`.** `D_t^norm` occurs at exactly three lines — 94, 136, 139 — plus
its prose at 142–147. §2.2 l. 94 casts it as one input to a labelled, non-overriding sensitivity
flag; §3.2 casts it as a declared sensitivity statistic. §4, §5 and §6 do not mention it at all, so
no section assigns it a decision, headline or comparability role. **No section still refers to a role
`D_t^norm` no longer has.**

**3.6 Cross-references and residue.** All five section references in the draft (§1, §2.2, §3.1, §3.2,
§6) resolve to existing headings, including l. 93's forward reference to the retitled §3.2. All six
predecessor phrases the amendments were required to displace return zero occurrences.

**3.7 Blast radius.** The amendment commit touched four files; within the draft it touched only
§2.2, §3.2, §3.3, §4 and §6, exactly the sections A1–A6 name. §1, §2, §2.1, §3.1, §3.4, §3.5, §5,
§7, §8 and §9 are byte-identical to the predecessor. In particular the runner, the cohort, the
denominators, the seeds, the negative control, the stop rule and the §8 binding execution conditions
are untouched, as the first review required of these amendments.

---

## 4. Outcome-freeness — finding

**Finding: the draft is outcome-free with respect to Task 4F1.**

Every numeric literal in the amended bytes was enumerated and classified. They fall into exactly
four classes, none of which is a Task 4F1 retrieval-quality outcome:

1. **Structural cohort facts** — tier counts, archive counts, mean `|gold|`, ceilings, stratum
   denominators, gold-cardinality shares. Every one independently recomputed from the sealed CSV
   (§2.1). These are composition, not results.
2. **Previously accepted results from other benchmarks** — the LongMemEval and LoCoMo figures at
   §1 l. 18–22. Byte-identical to the predecessor, introduced by no amendment, and covered by the
   draft's own header disclosure at l. 11–12.
3. **Design constants** — the five enumerated seeds `43001–43005`, the 20 nuisance trials, bucket
   boundaries, the constant 5 in A2's denominator, the `V4` schema and condition numbering.
4. **Sign predicates** — the `0` in `D_t > 0`, `D_t = 0`, `D_t ≤ 0`. Placeholders in a decision rule,
   carrying no measured value.

Every number the **amendments themselves** introduced (259/461/300/105, 20/35/31/10,
3.08/4.26/8.59/7.47, 29.0%, 17.9%, the weight form `max(1, |gold_i|/3)`, the denominator
`5 · n_t · lcm_i(|gold_i|)`) is in class 1 or 3 and was reproduced by me from the sealed cohort or
from arithmetic. No amendment introduced a retrieval-quality value, and none names any tier's
expected direction or magnitude. The draft's §9 l. 284–285 still declares Task 4F1 `BLOCKED` and
outcome access `FORBIDDEN`.

`python3 -B tools/verify_continuity_state.py` was run — a read-only checker that imports no
outcome-capable candidate — and returned `CONTINUITY_STATE: PASS`. Its source was inspected before
execution to confirm it neither runs nor imports the candidate. It is reported here as a
reproducibility observation about anchor binding, **not** as evidence for any finding above; every
finding in this artifact rests on bytes I hashed and recomputed myself.

---

## 5. Notes — none requires an amendment

Recorded so they cannot later be cited as unexamined, and so none is read as a condition on sealing.

**N1 — "Directly comparable" is exact with respect to the ceiling, and only that.** §3.2 l. 130
says the `|gold| ≤ 3` stratum has ceiling exactly 1.000 "so it is directly comparable across tiers
with no normalisation and no reweighting". The ceiling claim is exactly right and I verified it.
The composition *within* the stratum still differs across tiers: the share at `|gold| = 3` runs
9.7% / 14.3% / 30.0% / 26.7% and the within-stratum mean `|gold|` runs 1.70 / 1.78 / 1.97 / 1.90,
so the residual confound is reduced rather than removed. **No amendment is required**, for three
reasons on the bytes: §5 l. 211 independently mandates reporting at buckets 1, 2 and 3 separately,
which exposes exactly this mix; §2.2 l. 87–91 and §5 l. 201–202 already forbid describing the
confound as removed; and the wording is A1's own, adopted faithfully. The draft nowhere claims the
confound is removed.

**N2 — A4's stability statistic is scoped to `D_t`.** §4 l. 188–191 mandates leave-one-archive-out
for each `D_t` and does not extend it to §3.2's stratified contrasts. That is A4 exactly as written;
extending it would be new scope, and its absence creates no contradiction.

**N3 — A2 is a property of the estimand and a decision rule, not a §8 execution condition.** The
exact-rational claim is true of `D_t` as defined regardless of any implementation's internal
representation (§2.1), and §6 l. 241–243 correctly frames it as a numerical-representation rule.
It does not appear among §8's four binding execution conditions. Whether the execution package
realises the sign decision exactly is a matter for the execution-package track, which has its own
auditor; **it is not a defect in these bytes** and I take no position on it.

**N4 — §6 does not itself cross-reference the §2.2 sensitivity flag.** The reporting requirement
sits in §2.2, which is where A1.3 directed it. Not a contradiction; a cross-reference would be a
stylistic edit, which this review is instructed not to propose.

---

## 6. Scope discipline

- The V7 execution-package audit was **not** reopened. §9 l. 276–280 describes an open
  documentation-consistency question inside the candidate; that is an implementation-audit matter on
  a separate track and this review takes no position on it. It is untouched by A1–A6.
- No design choice the first review accepted was re-litigated. The tier-primary family, the pooled
  secondary, the negative control, the stop rule, the outcome partition, the interpretation boundary
  and the §8 execution conditions all stand as written.
- No stylistic edit is proposed.
- **No defect outside the requested scope was found.** Had one been found it would appear here,
  labelled as out of scope and separated from the A1–A6 verdict.

---

## 7. Outcome-boundary declaration

Declared explicitly and without qualification, for this review in its entirety:

- **Zero** invocations of the candidate with `--mode run`.
- **Zero** invocations of the candidate with `--mode finalize`.
- **No** call to `run_archives`, `evaluate_archive` or `finalize_results`, on real BEAM data or
  otherwise.
- **No** authorization constructed, and none attempted.
- `V52_T4F1_AUTH_HMAC_KEY_HEX` was **never set, never read, never inspected and never sought**. No
  HMAC key material was accessed in any form.
- **No** BEAM retrieval was performed.
- **No** retrieval top-three ID, Hamming distance, or Native / signed / Haar / ITQ outcome was seen,
  computed, written or interpreted.
- **No** retrieval-quality outcome or metric was computed, read or reported.
- **No** candidate, sealed payload, manifest, pinned corpus, historical audit namespace, or the
  draft itself was modified. This review edited nothing it reviewed.

Only two classes of computation were performed: SHA-256 digests over files, and recomputation of
cohort **composition** facts from the sealed structural CSV — counts, denominators, gold-cardinality
shares and ceilings — which carry no retrieval-quality outcome. No point in this review required an
outcome value; had one been required, that requirement would be reported here as the finding and the
review would have stopped.

---

## 8. Reviewer independence

I am a session-independent, cold-start reviewer. **I did not author the amendments** and I did not
author the document under review, its predecessor, the first co-chair review, or any Head Researcher
artifact. No prior chat context, commit message, continuity ledger entry or state file was accepted
as evidence for any statement above; each is treated as narrative, and every claim in this artifact
is derived from bytes whose digest I measured myself or from a recomputation I performed. No verdict
or gate result from any other session was supplied to me, and none was inferred.

---

## 9. Persistence record

| Field | Value |
| --- | --- |
| Verdict | `APPROVE WITH NOTES` — none of the notes requires an amendment or new bytes |
| Approved bytes | `5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` |
| Approved at commit | `c0133fce9b755d13d9be3016e8e06f493d6b275b` |
| Approved path | `docs/v52/task4f1/TASK4F1_PREREGISTRATION_DRAFT_2026-09-03.md` |
| Effect | Closes the co-chair approval condition in the draft's header and §9 for these exact bytes |
| Not granted by this artifact | Preregistration sealing itself, run authorization, outcome access, or any position on the V7 execution package |

Task 4F1 execution and retrieval-quality outcome access remain `BLOCKED` / `FORBIDDEN` until the
remaining §9 conditions are discharged by the parties who own them.

---

### Kısa Türkçe özet

Karar: **`APPROVE WITH NOTES`** — onay, değişiklik gerektirmeyen notlarla.

Özeti: İncelenen belgenin SHA256 değerini kendim hesapladım ve
`5e61898193421a3a18791202668c0974f23d2fb4080a107069e7b7127e35ea44` beklenen değerle eşleşti (14688
bayt, commit `c0133fc`). Altı düzeltmenin (A1–A6) tamamı, belgenin tam da o baytları üzerinde
yeterince yerine getirilmiş durumda; her birinin mekanizmasını dosyada bölüm ve satır numarasıyla
buldum. Düzeltmelerin yarattığı **yeni bir bilimsel tutarsızlık yok**: §2.2'nin yorum kuralı ile
§6'nın karar kuralı artık tek bir karar girdisinde (`D_t`) uyuşuyor ve `D_t^norm` hiçbir bölümde
artık sahip olmadığı bir role sahip değil. Belge Task 4F1 açısından **sonuçtan arındırılmış**
durumda; metindeki her sayıyı sınıflandırdım ve düzeltmelerin getirdiği tüm yapısal sayıları mühürlü
kohort CSV'sinden yeniden hesapladım — hepsi birebir tuttu.

§5'teki dört not yalnızca kayda geçmesi içindir; **hiçbiri değişiklik ya da yeni bayt
gerektirmiyor**. Bu onay, mühürleme önündeki eş-başkan koşulunu bu baytlar için kaldırır. Hiçbir
çalıştırma yapılmadı, hiçbir yetkilendirme üretilmedi, hiçbir HMAC anahtarına dokunulmadı ve hiçbir
geri getirme sonucu görülmedi veya hesaplanmadı.
