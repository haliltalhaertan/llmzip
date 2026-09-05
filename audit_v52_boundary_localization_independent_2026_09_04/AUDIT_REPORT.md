# V52 Head/Tail Boundary Localization — Independent Cold-Start Audit Report

**Date:** 2026-09-05
**Auditor:** cold-start, session-independent. Did not produce the result, did not write its
preregistration, and received no verdict, gate result, number or finding from any other session.
**Audited target:** commit `1a33ef0d1a2715257920201f7a3db8ab4677a007` on
`research/v52-sign-mechanism-locomo-2026-09-04` (repository `haliltalhaertan/llmzip`).
The branch head equals the audited commit; the branch had **not** moved.

---

## 1. Verdict

> ## `AUDIT PASS WITH CAVEATS`

The experiment is honestly conducted, correctly sealed, correctly executed, and correctly
reported against its own preregistered rules. Every one of gates A–R passes, and each passes as
**established** — positively demonstrated from bytes or from computation — not merely as
*not falsified*. I found no defect of integrity, no undisclosed run, no post-hoc tuning, no
threshold or seed alteration, and no Task 4F1 contact.

The caveat is not about integrity. It is about **what the package's own uncertainty accounting
licenses**. The reported standard errors are seed-panel-only. When I add the question-sampling
component — which is 3–5× larger and which the per-question persistence finally makes
computable — the *mechanism* claim survives overwhelmingly, but the *uniqueness* claim that
this stage newly adds does not survive at the confidence its presentation implies.

### The exact narrowed claim I would accept

> Under one shared SIGN96 / archive-local-SVD / Hamming retrieval pipeline, on two frozen
> datasets, preservation of the Native-vs-Full-Haar retrieval advantage is **strongly and
> reproducibly dependent on where the contiguous spectral boundary is placed**, and a matched
> random coordinate partition using the identical numeric Q32/Q64 destroys almost all of that
> advantage (Δ32 ≈ 0.85 LoCoMo, ≈ 0.83 LongMemEval). Among the five preregistered boundaries,
> 32/64 is sufficient on both datasets (ρ₃₂ = 0.082 LoCoMo, 0.162 LongMemEval, threshold 0.25),
> and 16/80, 24/72 and 64/32 are sufficient on neither.
>
> `S_common = {32}` **as computed on the frozen ten-seed panel**. But the *uniqueness* of 32
> within the tested grid rests entirely on a single exclusion — LoCoMo 48/48 at ρ = 0.303 — whose
> reversal probability under question resampling is ≈ 0.21. `S_common = {32}` is therefore a
> **≈ 73 % event**, not a settled fact, and LongMemEval already admits 48/48 outright.
>
> Accordingly: `[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]` and
> `[BOUNDARY-SET HETEROGENEITY PRESENT]` remain the correct paired labels, but the *localization*
> half should be reported as **a lead conditional on the ten-seed panel and the inherited
> denominator**, not as an established property of the grid. The position-dependence half needs
> no such hedge.

Nothing here transfers to Task 4F1, to other encoders or corpora, to necessity, or to a global
optimum — and the package itself already says so.

---

## 2. Identity verification — digests I measured myself

The handoff bound eleven git blob ids and three content digests. **All fourteen matched.** I also
verified the handoff document itself before reading it:

```
handoff  V52_BOUNDARY_LOCALIZATION_COLD_START_AUDIT_HANDOFF_2026-09-04.md
         sha256 a14e29e1557e4aece9a215fa9c92ae1b3b6a02469584876686a70df2eedd0822   MATCH
         (equals both the value stated in the tasking and the committed .sha256 sidecar)
```

Git blob ids measured with `git hash-object` at the audited commit:

| Artifact | Measured blob | Match |
|---|---|---|
| Preregistration | `b8acebedd49497a62ec637beabbcef6720460d15` | ✔ |
| Pre-run seal | `cd3ad221ed66816a7b36c1edc746016ca73f9188` | ✔ |
| Post-audit addendum | `456b3b51f49a0238cd936bc3f639988fb0d673af` | ✔ |
| LoCoMo runner | `0e66431449ad48b5f24049e0c05d65c917d8b893` | ✔ |
| LongMemEval runner | `26c1fe89ca025747b47f3fa6daf80326a8864747` | ✔ |
| LoCoMo workflow | `1de6c8abad80976c51843592801b53b18a998541` | ✔ |
| LongMemEval workflow | `128987f7402a71160981f8f0cd28677e6c931710` | ✔ |
| LoCoMo summary | `89c30a2a58fd638809477ded0d41b996f051c0f1` | ✔ |
| LongMemEval summary | `2d6e3a4b5f5bfdfd2b3b93bbc068a4fcc685b954` | ✔ |
| Checkpoint | `b5a8ed6542c78cde14f608b9b23b51eb6e34b917` | ✔ |
| Provenance manifest | `2751b51aea4ce43fbe08ac3ddfbafdc534d56dd0` | ✔ |

SHA-256 of file bytes, computed by me:

```
87e7ae969403b0bb06efcd726d317fb08427cce7c29f221dd0e520ff8722fd1b  locomo_boundary_per_question.csv.gz          MATCH
e73576039cb1c9b76ceb4b440148b90f3caa044ca082585d1a0f4d23ac08eaba  longmemeval_boundary_per_question.csv.gz     MATCH
232ffa300d832188ad0fc1fdb5fcd38d6ae7745922d5e8350080d845ed5bb791  locomo_boundary_random_partitions.json       MATCH
232ffa300d832188ad0fc1fdb5fcd38d6ae7745922d5e8350080d845ed5bb791  longmemeval_boundary_random_partitions.json  MATCH
```

Full 20-file measurement set, including the two frozen base modules and both per-seed CSVs, is in
`AUDIT_HASHES.json` (`all_declared_identities_match: true`).

### The two identically-hashing partition files

The handoff asked which of two explanations the bytes support: legitimate seed-determinism, or a
copy of the wrong file. **The bytes support legitimate seed-determinism, and I established this
without comparing the two files to each other.** I regenerated all ten partitions from the
partition seed integers alone — `numpy.random.default_rng(6800i).permutation(96)`, split 32/64 —
and the result matched *each* persisted file byte-for-byte including array order. A file copied
from the wrong dataset could not reproduce from seeds; a file that reproduces from seeds is
necessarily dataset-independent, because the construction depends only on the seeds and the 96
coordinate indices. The identity is expected, intentional, and verified.

---

## 3. Gate K — the reconstruction that this audit turns on

The handoff was explicit that recomputing the headline ratios from the summary JSON's own per-seed
values, or from the per-seed CSVs, proves only internal consistency. I therefore rebuilt every
primary aggregate **from the per-question records only**. `scripts/reconstruct_from_per_question.py`
opens the two `*_per_question.csv.gz` files and nothing else; the summaries and per-seed CSVs were
loaded afterwards, by a separate script, purely as comparison targets.

Reconstructed independently: all 120 seed-level R@3 values, all 120 seed-level ρ values, and for
each of the twelve dataset×arm cells the mean, sample SD, SE, ρ-min, ρ-max, sign-inversion list
and threshold-exceedance list.

**Worst absolute deviation from the declared values across everything: `2.04e-15`.**
Against the per-seed CSVs: `≤ 2.22e-16`. These are float64 summation-order magnitudes — the
aggregates are reproducible, not merely self-consistent.

My reconstruction, computed cold:

| | LoCoMo ρ | LongMemEval ρ |
|---|---:|---:|
| B16 | 0.823038 | 0.804840 |
| B24 | 0.526758 | 0.576501 |
| **B32** | **0.082396** | **0.161883** |
| B48 | 0.303437 | **0.193872** |
| B64 | 0.530851 | 0.360014 |
| RANDOM32 | 0.937182 | 0.990920 |
| | `S = {32}` | `S = {32,48}` |

`S_common = {32}`; P1 passes on both; Δ32 = 0.854786 / 0.829037, both ≥ 0.25 ⇒ P2
`SPECTRAL_POSITION_CONFIRMED` on both; L1 fires; heterogeneity flag fires. This matches the
checkpoint's mechanical verdict, derived without reference to it.

All 120 per-seed ρ values printed in checkpoint §3 match my reconstruction **exactly at the
printed 6 dp** — worst deviation `0.0`.

---

## 4. What the other gates found

Full detail in `GATE_TABLE.md`. The load-bearing findings:

- **Sealing is structurally sound, not merely asserted (A).** The stage is a strictly linear commit
  chain. `git merge-base --is-ancestor` confirms every forward edge prereg → runners → workflows →
  seal → trigger → outputs → checkpoint → manifest, and refutes every reverse edge. No
  `*_boundary_outputs/` file exists in the tree at the prereg, seal or trigger commits. The seal's
  self-declared `package_head_before_seal` equals the actual first parent of the seal commit — a
  check the author cannot satisfy retroactively without rewriting sealed history.

- **Exactly one execution, one attempt (D).** From the Actions API, not from prose: each workflow
  has `total_count = 1`, `run_number = 1`, `run_attempt = 1`, event `push`, head SHA equal to the
  trigger commit. LongMemEval's eleven jobs are each `run_attempt = 1`. Neither workflow declares
  `workflow_dispatch`, `repository_dispatch` or `schedule`, so no manual re-trigger path exists at
  all. Run ids match those declared in the checkpoint. There was no re-dispatch, no re-run, and no
  partial shard retry.

- **The intervention family is what the prose says it is (G, H).** I retyped the construction from
  preregistration §5 and rebuilt all 50 matrices in isolation: worst `‖RᵀR − I‖∞ = 1.55e-15`,
  off-block entries exactly zero, head block drawn first from a single RNG stream. The matched arm
  genuinely places the *same* numeric Q32/Q64 (`0.0` error) at *different* coordinates
  (`‖R_rand − R_spec‖∞ ≥ 0.667`; no partition is trivially the leading 32).

- **Sharding is genuinely shard-invariant (N).** The tie-break seed derives from `lex`, the global
  lexicographic rank over all 500 dataset ids computed *before* sharding — not from within-shard
  position. Confirmed from the persisted `tie_identity` strings: 470 unique lex values, strictly
  increasing in sorted-qid order, spanning 0–498 with exactly 30 unused slots (the `_abs` items).
  The summary's `DETERMINISTIC_SHARDED_SEMANTICS_INVARIANT` is precisely the claim the evidence
  supports, and the package correctly declines the stronger bitwise-exactness claim.

- **Adverse facts are disclosed, not buried (O, P, Q).** The two individually threshold-exceeding
  seeds are named — LongMemEval B32/58004 (ρ≈0.267) and B48/58009 (ρ≈0.302) — and my independent
  scan returns exactly and only those two. The historical LoCoMo seed 56001 sign inversion survives
  in the binding addendum; I recomputed it (`L₂ = −0.00664384767564943`, `ρ₂ = −0.067219`) and
  confirmed the new checkpoint carries it forward explicitly rather than dropping it now that the
  new panel shows no inversions. Both mandatory labels co-occur in every artifact where either
  appears. The checkpoint volunteers LongMemEval's 48/48 admission against its own headline.

- **Task 4F1 was not touched (R).** Zero occurrences of `4F1`, `BEAM`, `HMAC`, `run_archives`,
  `evaluate_archive` or `finalize_results` in either runner or either workflow; every mention
  anywhere in the stage is an explicit exclusion; no commit in the stage touches a 4F1 path.

---

## 5. Gate S — the strongest case against, and my adjudication

Required, and it produced the most consequential finding in this audit.

### 5.1 The attack

`ρ_b` is a ratio of two differences of means over questions. The package reports only
**seed-panel** dispersion: the SD across the ten rotation draws, with the question set held fixed.
That is one variance component of two, and it is the smaller one. Every ρ is also a mean over 1535
or 470 questions, and *that* sampling is not accounted for anywhere.

This stage persisted per-question records — so, for the first time, the omitted component is
computable. I computed it.

The naive bootstrap would overstate it, because `native_q` and `R_b,q` are strongly positively
correlated across questions (r ≈ 0.65–0.80). The correct object is the **paired** per-question loss
`δ_q = native_q − R_b,q`, resampled directly. I did that, 20 000 resamples, holding the denominator
fixed — every interval below is explicitly conditional on the inherited Full-Haar denominator,
exactly the limitation the package declares.

### 5.2 What it shows

| | reported SE (seed panel) | bootstrap SE (questions, paired) | P(ρ ≤ 0.25) |
|---|---:|---:|---:|
| LoCoMo B32 | 0.018 | 0.063 | 0.9958 |
| **LoCoMo B48** | **0.015** | **0.066** | **0.2103** |
| LoCoMo RANDOM32 | 0.014 | 0.078 | 0.0000 |
| LongMemEval B32 | 0.020 | 0.070 | 0.8929 |
| LongMemEval B48 | 0.016 | 0.070 | 0.7822 |
| LongMemEval B64 | 0.030 | 0.075 | 0.0692 |
| LongMemEval RANDOM32 | 0.023 | 0.088 | 0.0000 |

The question-sampling component is **3–5× larger** than the dispersion the package reports.

Resampling questions on both datasets and recomputing `S_common`:

```
S_common = {32}      72.95 %      <-- the reported result
S_common = {32,48}   16.57 %      would have fired L2, and NO heterogeneity flag
S_common = {}        10.17 %      would have fired L5
S_common = {48}       0.31 %
```

The whole L1 verdict hangs on one exclusion: LoCoMo B48 at ρ = 0.303, which is only 3.57 seed-panel
SE above threshold but has a **21 % chance of falling below it** under question resampling. Were it
to fall, `S_LoCoMo = S_LongMemEval = {32,48}`, the verdict would become L2
`[BROAD CONTIGUOUS SUFFICIENCY PLATEAU — NO UNIQUE PC32]`, and the heterogeneity flag would not
fire at all. Two of the package's three headline assertions would invert.

The inherited denominator supplies the same fragility through a second, independent channel: LoCoMo
B48 needs only a **−15.3 %** shift in `R_full` to become sufficient, LongMemEval B48 only **+9.3 %**.
`R_full` is itself an unquantified estimate over the same questions, so a shift of that order cannot
be excluded — and this package cannot bound it, as it states.

A third channel: on LongMemEval the paired per-seed contrast between B32 and B48 is
`+0.032, t = 1.02`, with 3 of 10 seeds favouring B48. On that dataset 32 and 48 are statistically
indistinguishable; only LoCoMo separates them (B48 worse on 10/10 seeds, t = 10.7).

### 5.3 My adjudication: it **weakens** the result. It does not defeat it.

**What survives untouched.** Position dependence is not close to marginal. RANDOM32 sits 50.0
(LoCoMo) and 32.3 (LongMemEval) seed-panel SE *above* the threshold, with bootstrap
P(sufficient) = 0.0000 on both datasets and 95 % CIs of [0.786, 1.092] and [0.819, 1.168]. Δ32 ≈
0.85 / 0.83 is enormous relative to every uncertainty I can construct. Since the spectral and random
arms use *identical* numeric Q32/Q64 matrices — which I re-derived to exactly 0.0 — the contrast
isolates coordinate membership and nothing else. No sampling argument touches this. P1 is likewise
robust (P = 0.996 / 0.893), as is the exclusion of 16, 24 and 64 (P ≈ 0 throughout; LongMemEval B64
at 0.069 is the weakest and still excluded).

**What does not survive.** The claim this stage newly adds — that 32 is *uniquely* sufficient on the
tested grid — is a ≈ 73 % event, not a fact. It is not wrong, and it was derived by a mechanically
correct application of the preregistered rule to the frozen panel; that rule was fixed in advance
and I verified it was not altered. But a preregistered decision rule applied to a noisy estimate
yields a decision with the estimate's noise, and the package's reported SEs do not expose that noise
because they condition on the question set.

**Why this is not a finding against the researchers.** The preregistration explicitly declines to
quantify the denominator's uncertainty (§8), explicitly frames SEs as conditional (§2.5), explicitly
warns the grid is coarse and cannot establish uniqueness (§4, §18), and the checkpoint volunteers
LongMemEval's 48/48 admission. And it was *this stage's own* decision to persist per-question
records — the reason I could compute the missing component at all. The gap is a disclosed
limitation that I have now measured, not a concealed one.

**Practical consequence.** The standing stop rule should be released, because the mechanism result
is sound and the localization lead is real. But a finer boundary scan, if preregistered later,
should treat `S_common = {32}` as a hypothesis to test rather than a premise to build on, should
budget for question-level uncertainty rather than seed-panel-only SEs, and should quantify the
Full-Haar denominator — the single unquantified input on which every ρ in this package depends.

---

## 6. Established vs. not falsified

Gates A–R are **established**: each was positively demonstrated from bytes or from computation, not
inferred from the absence of contrary evidence. Specifically, sealing order was established by DAG
ancestry rather than by author-controlled timestamps; single execution by the Actions API rather
than by workflow-trigger inference; the transformation family, the matched arm and the partitions by
independent reconstruction rather than by reading the runner's own self-checks; and every headline
aggregate by rebuilding it from per-question records.

I record **nothing** as merely *not falsified*, and **no** gate as `NOT ESTABLISHED`.

One boundary on scope, stated plainly: I verified that the persisted per-question records
reconstruct every primary aggregate exactly, and that the runners implement the preregistered recipe.
I did **not** re-execute the full representation pipeline from the raw datasets — that was neither
required (the per-question layer exists precisely to make it unnecessary) nor possible to do
meaningfully here, since the LongMemEval source is a 277 MB external download. The claim
"the persisted per-question values are the ones the frozen pipeline would produce from the raw
corpora" therefore rests on the CI pre-run gate — which re-verified the dataset SHA-256, byte count,
adapter digests and all eight sealed blobs inside every job, and which I confirmed succeeded in all
eleven — rather than on my own end-to-end re-execution.

---

## 7. Outcome-boundary declaration

- Audited only the LoCoMo and LongMemEval boundary-localization track, which the handoff places in
  scope.
- **No Task 4F1 execution candidate was invoked in any mode**, `--mode run` and `--mode finalize`
  included. `run_archives`, `evaluate_archive` and `finalize_results` were never called.
  `V52_T4F1_AUTH_HMAC_KEY_HEX` was never set and no authorization was constructed. **No Task 4F1
  (BEAM) retrieval outcome was accessed or sought.** Task 4F1 remains
  `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
- The research branch, checkpoints, seals, manifests, outputs and preregistration were **read only**.
  I made no commit to `research/v52-sign-mechanism-locomo-2026-09-04` and modified no file under
  `research/v52/`. All my writes are confined to
  `audit_v52_boundary_localization_independent_2026_09_04/` on the audit branch.
- I ran **no new experimental arm**: no additional boundary, no seed tuning, no threshold change, no
  knee search, no finer scan. Gate S is re-arithmetic (bootstrap resampling and sensitivity
  inversion) over frozen persisted outcomes — it introduces no new intervention, no new seed and no
  new data.
- I re-derived transformation matrices and partitions with numpy, which is verification of the
  existing frozen construction, expressly in scope.
- I built no generalized prose scanner.
- The earlier matched random-partition null stage at `410bcf5` was **not** audited; it remains
  independently unaudited, and I make no claim about it. The fresh matched-null arms here are
  stronger than that stage in three respects I verified — both datasets rather than LoCoMo only,
  fresh seeds, and exact Q32/Q64 matching — but a superseding judgement is outside what I was asked
  to establish.

---

## 8. Files

```
audit_v52_boundary_localization_independent_2026_09_04/
  AUDIT_REPORT.md                     this report
  AUDIT_REPORT.md.sha256              sidecar
  GATE_TABLE.md                       gates A-S with verdict, strength, evidence
  AUDIT_HASHES.json                   20 files, digests measured by the auditor
  scripts/
    reconstruct_from_per_question.py  Gate K/L/M - rebuild from per-question records only
    compare_to_declared.py            Gate K - reconstruction vs summaries and per-seed CSVs
    verify_transforms_and_partitions.py  Gates G/H/I - rebuilt from prereg prose
    verify_matched_arm_strict.py      Gate H strict - block placement and non-triviality
    verify_shard_invariance.py        Gate N - shard-invariance from persisted bytes
    verify_checkpoint_tables.py       Gate O - all 120 printed per-seed rho values
    gate_s_adversarial.py             Gate S - margins, sensitivity, paired contrast
    gate_s_bootstrap_paired.py        Gate S - paired question bootstrap, joint S_common
  evidence/
    reconstruction.json               full independent reconstruction
    declared_vs_reconstructed.json    deviations (worst 2.04e-15)
    transforms_and_partitions.json    orthogonality, block structure, partition checks
    matched_arm_strict.json           matched-arm strict results
    shard_invariance.json             lex-rank evidence
    checkpoint_table_check.json       120/120 printed values verified
    gate_s_adversarial.json           Gate S attacks S1-S5
    gate_s_bootstrap_paired.json      paired bootstrap + joint S_common distribution
    actions_run_history.json          Actions API run/job history
```

Every number in this report was computed by me in this session from the audited bytes. No value was
taken from the checkpoint, the summaries, the provenance manifest, any commit message, or the
handoff's own factual claims; those were treated throughout as claims under test.

---

## 9. Kısa Türkçe özet

**Karar: `AUDIT PASS WITH CAVEATS` (çekincelerle geçti).**

A–R arası on sekiz kapının tamamı geçti ve hepsi *kanıtlandı* — sadece "çürütülemedi" değil.
Bağlayıcı on bir git blob kimliği ile üç içerik özeti bizzat tarafımdan ölçüldü ve tamamı uyuştu.
Kapı K için birincil toplamların hepsini yalnızca soru-bazlı kayıtlardan yeniden kurdum; en büyük
sapma `2.04e-15` (float64 gürültüsü). Mühürleme sırası commit grafiğinden, tek çalıştırma ise
Actions API'sinden doğrulandı: her iş akışı için tam olarak bir çalışma, bir deneme. Task 4F1'e
hiçbir şekilde dokunulmadı; ben de dokunmadım.

Çekince şudur: paket yalnızca **tohum panelinden** kaynaklanan belirsizliği raporluyor. Soru
örneklemesinden gelen bileşen 3–5 kat daha büyük. Eşleştirilmiş bootstrap ile `S_common = {32}`
sonucu yalnızca **%72.95** olasılıkla tekrarlanıyor; `{32,48}` %16.57. Sonucun tamamı tek bir
dışlamaya — LoCoMo B48, ρ = 0.303 — dayanıyor ve bunun tersine dönme olasılığı %21.

Yani: **konum bağımlılığı** (Δ32 ≈ 0.85 / 0.83) sarsılmaz biçimde sağlam. Ancak bu aşamanın yeni
kattığı **"32 tek başına yeterlidir"** iddiası, sunumunun ima ettiği kesinlikte değil. Durdurma
kuralı kaldırılabilir; fakat daha ince bir tarama yapılacaksa `S_common = {32}` bir öncül değil,
sınanacak bir hipotez olarak alınmalı ve Full-Haar paydasının belirsizliği nihayet ölçülmelidir.
