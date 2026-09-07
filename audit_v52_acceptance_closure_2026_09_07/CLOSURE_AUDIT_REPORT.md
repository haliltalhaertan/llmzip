# V52 — Narrow Closure Audit of the Coordinate-Scale Acceptance Record

Auditor: cold-start independent session, no prior context, commissioned to audit a **record**.
Date: 2026-09-07.
Branch: `audit/v52-acceptance-closure-2026-09-07`. Namespace: `audit_v52_acceptance_closure_2026_09_07/`.
Anchors: `main` @ `ed2b2f74347da6be68beae2c22d5c3d22992f1a3` (carries L-060);
research @ `0c9916bd7786d7ddb332f5b6da3d96d61a6223f0`.
Environment: Python 3.14.3 (stdlib only — `hashlib`, `csv`, `gzip`, `fractions`, `decimal`, `re`,
`subprocess`); no third-party package installed, no virtualenv created.

**Controlling prompt.** `prompts/V52_ACCEPTANCE_CLOSURE_NARROW_AUDIT_PROMPT_2026-09-07.md`,
raw git blob sha256 `c6a0da6a3076793b5b3cc0b0d0796b3fe30a1a21644e539c3b4f9a0bd1649faf` —
**matches the declared prefix `c6a0da6a`.** Hashed via `git show <commit>:<path>`, not the checkout.

**Verdict: `CLOSURE PASS WITH CAVEATS`.**
Nothing found requires the stage to be reopened.

---

## 0. Method, and how I made each check falsifiable

Every value below is derived from raw git blobs or from my own execution. Nothing is taken from
chat, commit messages, ledger prose, or `ops/CURRENT_STATE.json` as evidence — the state file is
audited, not trusted.

Every check carries a negative control that is shown *actually failing*. The controls live in
`scripts/` and their outputs in `evidence/`. Summarised:

| control | what it proves | result |
|---|---|---|
| `NC1` perturb one per-question cell by 1e-9 | the C4 comparison is sensitive to the input rows | A no longer matches ✔ |
| `NC2` substitute B where A is claimed | the C4 comparison distinguishes the two definitions | LoCoMo block no longer matches (0.6516 vs 0.4454) ✔ |
| `NC3` recompute A on 9 of 10 seeds | the C4 comparison is sensitive to the seed panel | 0.6619 vs 0.7272, no match ✔ |
| `NC4` / `NC5` last-digit-wrong document value | the comparison is not vacuously true | flagged at 9.7e-15 ✔ |
| `NC_C1` append one byte to the decision document | the sidecar check can fail | sidecar no longer matches ✔ |
| `NC_C2` collapse-pattern on synthetic definition-B prose | the "§7 nowhere says this" search can fire | fires on 3 phrases ✔ |
| `NC_C2` number detector on a synthetic reasoning line | the outcome-free check can fire | fires ✔ |
| `NC_C3` altered quote (`frac_full + frac_block`) | the verbatim check can fail | not found ✔ |
| `NC_C3` search for the `frac_arm` bands that *do* exist | the threshold search is not blind | finds `frac >= 0.70` ✔ |
| `NC_C5` compare the `A2_SHA256` pin to evidence **A** | the pin check can fail | does not match ✔ |
| `NC_C5` recomputation regex on synthetic positive prose | the "no recomputation claimed" scan can fire | fires ✔ |
| `NC_C6` shadow tree, one byte appended to a checked adapter | `verify_frozen_artifacts.py` can fail | clean exit 0, perturbed exit 1 ✔ |
| `NC_C6` default Windows (CRLF) checkout | `verify_continuity_state.py` can fail | BLOCKED with 29 mismatches, then PASS under LF ✔ |
| `NC_C7` classify a synthetic `M` on the preregistration | the additivity check can fail | detected as non-addition in a frozen namespace ✔ |
| `NC_C8` synthetic `--mode run … $V52_T4F1_AUTH_HMAC_KEY_HEX` | the boundary scan can fire | fires ✔ |

### 0.1 The blob-versus-checkout question, settled rather than assumed

The prompt warns that two earlier auditor sessions reported hash mismatches and neither confirmed
their cause. I reproduced the mismatch and then **proved** its cause.

The repository ships **no `.gitattributes`** (`git ls-tree -r ed2b2f74 | grep -c gitattributes` = 0).
On a default Windows clone, `core.autocrlf=true`, so every text blob is rewritten with CRLF on
checkout. Under that checkout:

- `tools/verify_continuity_state.py` → `CONTINUITY_STATE: BLOCKED`, **29** SHA256 mismatches;
- `tools/verify_frozen_artifacts.py` → `match=0 mismatch=26`, "CHAIN-OF-CUSTODY DEFECT".

The proof that this is a checkout artifact and not a byte defect: taking the raw blob of
`adapters/longmemeval_v52_adapter_v2.py` and replacing every `\n` with `\r\n` yields
`db71d95be809de856acac90de5498d08e9bf06fec06f753269e8c20a98c47450` — **bit-for-bit the value the
failing verifier reported.** The blob itself hashes to `643082d6…`, the declared value.

After `git config core.autocrlf false` and a fresh checkout, **both verifiers PASS** (exit 0).

> **I1 — infrastructure finding.** Every future auditor on Windows will hit this and may report a
> chain-of-custody defect that does not exist. A one-line `.gitattributes` (`* -text`, or
> `* text=auto eol=lf`) would end it permanently. This is not a defect in the acceptance record and
> does not bear on any gate verdict; it is reported because the record's own commissioning prompt
> asks the auditor to distinguish the two, and the distinction is now settled.

---

## C1 — Document identity · **ESTABLISHED**

All six in-scope objects hashed from raw blobs. Every sidecar matches, every value declared in
`ops/CURRENT_STATE.json` or in the commissioning prompt matches, and every sidecar names the correct
basename.

| object | commit | blob sha256 | bytes | sidecar | declared |
|---|---|---|---|---|---|
| `docs/v52/V52_COORDINATE_SCALE_ACCEPTANCE_DECISION_2026-09-07.md` | `ed2b2f74` | `8ba55a616c33f23fd3e8cc6daf4565830b7e993f4749e8440c9c62e082d31d3f` | 12122 | ✔ | ✔ |
| `…ACCEPTANCE_DECISION_2026-09-07.md.sha256` | `ed2b2f74` | — | — | names basename ✔ | — |
| `docs/v52/V52_ACCEPTANCE_DECISION_CLARIFICATION_2026-09-07.md` | `ed2b2f74` | `52a37695e34b693f668e2fc36b4425b6aab22919912cca871de8271dffe42aae` | 5362 | ✔ | ✔ (state file) |
| `docs/v52/V52_NEXT_QUESTION_DESIGN_PROPOSAL_2026-09-07.md` | `ed2b2f74` | `c0828c5debf64d6a1d39e67dc6ecb9b57fff6746cb327ad1e794df3db47466bb` | 7239 | ✔ | ✔ (ledger L-060) |
| `prompts/V52_ACCEPTANCE_CLOSURE_NARROW_AUDIT_PROMPT_2026-09-07.md` | `ed2b2f74` | `c6a0da6a3076793b5b3cc0b0d0796b3fe30a1a21644e539c3b4f9a0bd1649faf` | 7044 | ✔ | ✔ |
| `research/v52/V52_COORDINATE_SCALE_DEVIATION_REGISTER_2026-09-07.md` | `0c9916bd` | `4f70340774624b0bcdc4e519f6c42f0733b549a2b065a3a4e0b939c5aa5f22dc` | 10828 | ✔ | ✔ |
| `research/v52/V52_COORDINATE_SCALE_PARTICIPATION_PREREG_2026-09-05.md` | `0c9916bd` | `de6672119010bf561179014748e21836bff5c0ebf6efa10379213c59de5203fe` | 14495 | (none in tree) | ✔ |

Blob-versus-checkout: identical for all seven under an LF checkout; divergent under CRLF for reasons
proved in §0.1. Reported separately, as required.

**Note, not a defect:** the preregistration has no `.sha256` sidecar in the tree. Its hash is
declared in the decision document, the register and the state file, and all three agree with the
blob. The gate asks that each document hash to "the value its sidecar **and** the state file
declare"; for this one object only the latter exists.

---

## C2 — The A/B ruling follows from the preregistration text · **ESTABLISHED**

I formed my own reading of §7 at its verified hash before comparing it with the decision's.

### My reading

§7 opens with the governing clause **"For each dataset independently, per rotation seed, paired at
the question level:"** and the two `frac_*` formulas sit under it. `frac_arm` is therefore a
per-seed quantity. The decision bands are then applied to **"the seed-panel mean"** — the mean over
the seed panel of the quantity §7 has just defined, and `frac_arm` is the only estimand §7 defines
(the only other named quantities, `delta_full`/`delta_block`, are explicitly "barred from carrying
any verdict"). Finally the denominators "must be reported with their **per-seed dispersion**", which
presupposes a denominator that exists per seed and has not been collapsed.

Compose those and you get: form `frac_arm` per seed, then average over seeds. **That is definition A.
I reach the same conclusion the decision reaches, independently.**

### Could B be defended from the text? — I say no

The converse claim is checked, not asserted. Across the whole preregistration:

- the string `seed-mean` occurs **0 times**;
- a deliberately broad pattern for collapse-language (`mean|average|aggregate|pool|collapse|combine`
  + `arms|across seeds|over seeds|seed-mean`, or `before forming the ratio`) returns **zero matches
  in §7 and zero in the entire document** — while firing on three phrases of synthetic prose that
  does describe B, so the search is not blind.

The only textual hook I can find for B is §8's "Report the seed-panel mean **and** the per-seed range
for every arm", which does contemplate per-arm seed means. But §8 is a *reporting* requirement, it
is not §7, and it does not define the estimand. Reading it as the estimand would require the §7
formulas to be evaluated on seed-collapsed arms, in direct contradiction of the "per rotation seed"
clause that governs them. **I do not find B defensible from the text**, and I record that as my own
reading rather than as deference.

### Is the reasoning outcome-free, as asserted?

Yes, for the derivation. §2.1–2.3 contain no decimal number at all except the section numbers
`2.1/2.2/2.3`; the band values `0.70`/`0.20` are elided from the quoted §7 block with an explicit
`…` marker.

### Findings

> **F1 — the block labelled "verbatim" is not byte-verbatim.** Of the seven quoted lines in §2.1,
> four differ from the preregistration bytes:
>
> - `For each dataset independently, **per rotation seed**, paired at the question level:` — the
>   source has **no bold** on `per rotation seed`. Emphasis was added, without an "emphasis added"
>   note, to the exact phrase the ruling turns on. The phrase is genuinely present, in that position,
>   governing the formulas — the substance is unaffected — but adding emphasis to the load-bearing
>   phrase and then calling the block "verbatim" is the kind of small liberty an adversarial reader
>   would seize on.
> - `— they are not inherited —` — the source uses ASCII hyphens, not em dashes.
> - the trailing `…` elision marker (conventional, correctly used).
>
> The two passages that C3 puts under a verbatim requirement are, by contrast, byte-exact.

> **F2 — the outcome-free assertion is scoped more loosely than the bytes.** The document says "no
> outcome value appears in this section's reasoning". §2.4, inside the same numbered section, carries
> the full A/B table. The reading that §2.4 is the applied correction rather than the derivation is
> defensible and is how the document presents it — but the sentence as written invites a challenge
> that "§2.1–2.3" would not have.

> **F8 — an unstated consequence of the ruling.** Definition A is the mean of ten per-seed ratios.
> On the block arm the record's own D4 reports per-seed denominators running from −0.0066 to +0.0164
> — i.e. changing sign inside their own envelope — and per-seed fractions from −3.40 to +2.64.
> Averaging ten such ratios is *less* numerically stable than B's ratio-of-means, which my exact
> arithmetic confirms (§C4: the block-arm float error is ~1e-14, three orders worse than the full
> arm's ~1e-16). Ruling A the preregistered estimand is textually correct and I endorse it, but the
> record nowhere notes that its own ruling selects the more fragile estimator precisely where the
> instability it elsewhere cites bites hardest. This is a gap in the account of consequences, not an
> error in the ruling, and it strengthens rather than weakens the decision's refusal of the
> comparative claim.

---

## C3 — The §7/§9 deviation is accurately stated · **ESTABLISHED**

**Both quoted passages are byte-verbatim** against the preregistration blob:

- §7: `**Secondary:** the interaction on the fraction scale, `I_frac = frac_full - frac_block`. It is\nsecondary precisely because the pilot showed it nearly vanishes once the floor effect is removed.` — exact ✔
- §9: `**Positive (`I` large).** Supports that relative coordinate scale *participates* in the damage from\ncross-band mixing.` — exact ✔

**Defect 1 — a demoted statistic carries the licence.** Confirmed independently. §7 states the
per-arm fraction "is the primary quantity, reported **per arm**" and labels the interaction
`**Secondary:**`; §9's only positive-licence clause is keyed to the interaction. Both facts hold.

**Defect 2 — "large" is never defined.** Confirmed by searching the *whole* document, not §7 and §9.
Every occurrence of `I` or `I_frac` in the preregistration:

| line | context | carries a cut? |
|---|---|---|
| 85 | "a global `σ` … flips the sign of `I_frac` between settings" | no (design rationale) |
| 142–143 | §7 `**Secondary:**` definition | no |
| 152 | §8 "Report the seed-panel mean and the per-seed range … for `I`" | no (reporting) |
| 153 | §8 "question-level paired bootstrap on `I`" | no (reporting) |
| 165 | §9 "**Positive (`I` large).**" | no threshold |
| 170 | §9 "**Null (`I ≈ 0`).**" | no threshold |
| 216 | §13 "Global overshoots and flips `I_frac`" | no |

No numeric band, threshold or operational cut for `I_frac` exists anywhere. The same search *does*
find the bands that exist for `frac_arm` (`frac >= 0.70`, `frac <= 0.20`), so its silence is evidence.

**Neither clause is selected.** The decision states "**No clause is selected by this decision.**";
the register states "**Not adjudicated.**" Both verified in the bytes.

> **F7 — a small identification the record makes silently.** §9 writes `I`, never `I_frac`. The
> decision says §9 "attaches the positive interpretation licence to **that same secondary
> quantity**". The identification is supportable — §7 bars the percentage-point interaction from
> carrying any verdict, leaving `I_frac` as the only interaction that can license anything — but the
> record asserts the identity rather than deriving it.
>
> **Nuance on the same sentence.** The decision says the document supplies "no band, threshold or
> **direction** test for `I_frac` anywhere". On band and threshold this is exactly right. On
> *direction*, §9 does supply a qualitative dichotomy (`I` large versus `I ≈ 0`) — undefined and
> non-operational, which is the decision's actual point, but not literally absent. The claim is
> marginally stronger than the bytes.

---

## C4 — The numerical correction is exact and complete · **ESTABLISHED**

I recomputed A and B for all four benchmark/arm combinations **from the persisted per-question rows**
at research `0c9916bd` — `locomo_scale_per_question.csv.gz` (92,100 rows, 1,535 questions × 10 seeds
× 6 arms) and `longmemeval_scale_per_question.csv.gz` (28,200 rows, 470 × 10 × 6). Every
(arm, seed) cell is complete and balanced; `NATIVE` is seed-invariant, as the sealed runner's use of
a grand `NATIVE` mean in the per-seed numerator requires.

Two independent passes: float64, and **exact rational arithmetic** over the decimal strings in the
CSV (every operation downstream of the rows is a sum, a division and a mean, so the true value is
computable exactly in ℚ).

| benchmark | arm | exact value (30 sf) | document value | |exact − document| |
|---|---|---|---|---:|
| LoCoMo | full | A `0.727186134288477954174255904877` | `0.7271861342884777` | 2.54e-16 |
| | | B `0.726106907590136485776267640691` | `0.7261069075901362` | 2.86e-16 |
| LoCoMo | block | A `0.445442578678786318446745824993` | `0.4454425786787960` | 9.68e-15 |
| | | B `0.651642919568052923284818634783` | `0.6516429195680419` | 1.10e-14 |
| LongMemEval | full | A `0.656978166471495789182660227462` | `0.6569781664714960` | 2.11e-16 |
| | | B `0.656334297095720765497525680344` | `0.6563342970957214` | 6.35e-16 |
| LongMemEval | block | A `0.316511162188282627722377391028` | `0.3165111621882831` | 4.72e-16 |
| | | B `0.308458584454238070011564640710` | `0.3084585844542308` | 7.27e-15 |

**All eight values are confirmed.** The residual is at most 1.1e-14 and is float64 accumulation in
the sealed runner, not an error in the record. Note that the block-arm residuals are ~40× the
full-arm residuals — catastrophic cancellation against a near-zero denominator, which is the same
instability D4 records, surfacing here through a third route.

The document is honest about its own method: it says the table was "recomputed from the persisted
summaries at `0c9916bd`", and indeed each document value reproduces the summary JSON exactly
(A = the mean of the persisted `frac_*_per_seed` list, B = the persisted `frac_*`). My per-question
recomputation independently confirms those summaries.

**No rounded restatement of the A/B difference survives.** The phrase `within 0.001` occurs in
exactly three places across `main` and the research branch — the ledger L-059, the decision §2.4, and
`ops/CURRENT_STATE.json` — and in **all three** it appears only inside an explicit withdrawal
("is WITHDRAWN as a rounded paraphrase"). The surviving statement, "approximately **0.001079**", is
flagged as approximate and sits directly beneath the full-precision table.

> **F3 — "The exact differences" is not exact.** The A−B column is introduced as "The exact
> differences". It is not:
>
> | cell | document A−B | float(docA)−float(docB) | exact A−B | doc vs exact |
> |---|---|---|---|---:|
> | LoCoMo full | `0.0010792266983414844` | identical | `0.001079226698341468…` | 1.60e-17 |
> | LoCoMo block | `-0.2062003408892458` | `-0.20620034088924588` | `-0.20620034088926660…` | **2.08e-14** |
> | LongMemEval full | `0.0006438693757745` | `0.0006438693757745417` | `0.000643869375775023…` | 5.24e-16 |
> | LongMemEval block | `0.0080525777340523` | `0.008052577734052324` | `0.008052577734044557…` | 7.74e-15 |
>
> Three of the four are truncated decimal renderings of a float subtraction, and none equals the
> exactly-computed difference. `ops/CURRENT_STATE.json` carries the *higher*-precision float values
> for three of them, so the document is the less precise of the two records of the same correction.
> The magnitudes are physically irrelevant — but a correction whose entire purpose was to withdraw a
> rounded paraphrase should not itself round while calling the result "exact". Correctable with a
> one-line erratum; it changes nothing.

---

## C5 — Provenance versus recomputation, honestly separated · **ESTABLISHED**

Every hash in the LongMemEval evidence binding re-derived from blobs at
`e97fbe052306e9042e994d2e83031c6e8edd6b3d` and `0c9916bd`:

| item | declared | recomputed | ✔ |
|---|---|---|---|
| evidence A git blob | `36505bcffd7d1ce983a71c5ec4d000a2c94ae1ac` | same | ✔ |
| evidence A sha256 | `930db8e923652319f169ba0701febdc07a8cebc49b21c978960384682b37bef1` | same | ✔ |
| evidence A size | 744 bytes | 744 | ✔ |
| evidence A decisive sentence | quoted in §4 | present verbatim | ✔ |
| evidence B git blob | `aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1` | same | ✔ |
| evidence B sha256 | `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` | same | ✔ |
| evidence B states the same finding | asserted | confirmed in the adapter source | ✔ |
| base source blob | `79dd4a5ec462102da5d82530088a4b7e89bef437` | same | ✔ |
| **`A2_SHA256` pin = evidence B sha256** | "verified" | **equal** | ✔ |

The pin check is not vacuous: comparing the same pin against *evidence A*'s sha256 fails, as the
negative control shows.

**The harder question — does anything claim the graph was recomputed here?** I ran a two-directional
regex (recompute/recount/rebuild/re-derive within 120 characters of "dependency graph"/"component"/
"470"/"haystack", and the reverse) over the acceptance decision, the clarification note, the
deviation register, ledger L-057…L-060 and `ops/CURRENT_STATE.json`, and read every hit in context.
There are eight hits and **every one sits inside a negative statement** — "the dependency graph …
was **not recomputed**", "its components were **not** recounted", "the figures were **not**
re-derived". The acceptance decision and the register produce zero hits of any polarity. The scan is
not blind: it fires on synthetic prose that does claim recomputation.

The clarification note carries the required elements explicitly: "was **not recomputed**",
"inherited from the Task 3A.1 stage", and the sharpest sentence in the whole record —
"Confirming that a file contains a number is not confirming the number."

**Is §4's consequence stronger than provenance warrants? — No.** §4.1's argument is analytic, not
empirical: *given* one connected component, cluster resampling either returns the identical dataset
in every replicate or requires an arbitrary partition that violates its own independence assumption.
That reasoning needs the "1 component" figure to be *true*, and the record is explicit that the
figure is inherited with Task 3A.1's standing and no more. §4.2 keeps the alternative design
unauthorized. I judge the consequence proportionate to the evidence claimed for it.

> **F4 — the label is not attached where the consequence is drawn.** The required citation label
> `[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE VERIFIED, NOT
> RECOMPUTED HERE]` is present in the clarification note and in `ops/CURRENT_STATE.json`. It is
> **absent from the acceptance decision** — whose §4 states the consequence — and absent from the
> deviation register, whose D7 is marked `SETTLED`. A reader who cites the decision document alone,
> or the register alone, carries the consequence without the label. The clarification note is bound
> to the decision by sha256 and states the requirement, so the record as a whole is honest; the
> failure mode is a citer who does not follow the binding. Correctable additively by naming the label
> in a future citation-block, without editing anything.

---

## C6 — Current-state consistency · **NOT ESTABLISHED** (one clause of four)

| clause | result |
|---|---|
| `ledger_entry` matches the newest ledger entry | ✔ `L-060`, which is both the highest-numbered and the last in file order |
| both verifiers pass when I run them myself | ✔ exit 0 both, under an LF checkout; see §0.1 and the negative controls |
| no surviving "awaiting adjudication" text | ✔ zero matches in the state file and zero in the acceptance decision |
| the label set is identical across state file, acceptance decision and register | ✘ **it is not** |

The state file and the acceptance decision carry an identical five-label set. The register does not:

| label | decision | state | register |
|---|:--:|:--:|:--:|
| `[LOCOMO COMPUTATIONAL REPRODUCTION PASS — SAME METHOD, NOT INDEPENDENT REPLICATION]` | ✔ | ✔ | ✔ |
| `[COMPARATIVE MECHANISM CLAIM **NOT ACCEPTED** — …]` | ✔ | ✔ | ✘ |
| `[COMPARATIVE MECHANISM CLAIM **NOT ESTABLISHED** — …]` | ✘ | ✘ | ✔ |
| `[UNCERTAINTY ANALYSIS IS POST-OUTCOME]` | ✔ | ✔ | ✔ |
| `[NOT INDEPENDENTLY AUDITED AS A WHOLE STAGE]` | ✔ | ✔ | ✔ |
| `[MOST / PARTIAL ARE POINT CLASSIFICATIONS ON THE FROZEN PANEL — …]` | ✔ | ✔ | ✘ |

> **F5.** The divergence has an innocent cause: the register was written at research `0c9916bd`
> *before* the acceptance decision, and the program's rule is that corrections are additive, so the
> register was correctly left unedited. But the consequence is real — two citation-label sets are in
> circulation for the same stage, differing on the central claim's verb. There is a second-order
> irony: the clarification note §1 records that the Head Researcher required the claim to read
> "**not established** on current evidence", which is the register's wording, not the decision's.
> Both are semantically compatible and neither is wrong; nothing in the record reconciles them.
> Fix additively: a one-line note stating that the two label strings denote the same status and that
> the decision's set is canonical.

> **F6 — the accepted-conclusion text differs between the decision and the state file.** The final
> sentence reads "This is not a general mechanism result, not a production claim, and does not
> generalise to other encoders or corpora" in the decision, and "Not a general mechanism result, not
> a production claim, and not a generalisation to other encoders or corpora" in
> `ops/CURRENT_STATE.json` — whose own key asserts "the text itself is unchanged from the version
> that was proposed". Same meaning, different bytes; the assertion of textual identity is not quite
> true. The decision document is the normative object and should be the one copied.

No key contradicts the decision. `task_4f1_run = BLOCKED`, `retrieval_quality_outcome_access =
FORBIDDEN`, `state_id = V52_4F1_SCIENTIFIC_PREREGISTRATION_SEALED_V3`, and the state file's
`next_single_action` correctly describes this audit as commissioned-pending rather than performed.

**Why "NOT ESTABLISHED" rather than "FAIL":** the gate's label-identity clause is factually false in
the bytes, so I cannot mark it established. Nothing about it undermines the decision, contradicts a
verdict, or touches a frozen artifact — hence a caveat, not a failure of the closure.

---

## C7 — Additivity · **ESTABLISHED**

`main`, `a0944522` (L-056) → `ed2b2f74` (L-060), five commits:

```
37a39a4 L-057  integrate the five published Codex packages by identity verification
e97fbe0 L-058  record the coordinate-scale deviation register; LongMemEval cluster bootstrap settled
9271341 L-059  record the Head Researcher acceptance decision; rule A vs B from the preregistration text
cf03007        correct a stale state label left by L-059
ed2b2f7 L-060  apply the two wording constraints, prepare the narrow closure audit, propose the next question
```

Ten files changed. **Eight are pure additions** (three documents + three `.sha256` sidecars + the
audit prompt + its sidecar). The only two non-additions are `docs/CONTINUITY_LEDGER.md` (append-only
by design) and `ops/CURRENT_STATE.json` (the live state file).

Research branch, `591e5d0` → `0c9916bd`: **two files, both pure additions** — the deviation register
and its sidecar. The research tip *is* `0c9916bd`, so nothing was written there afterwards.

**No frozen artifact was edited.** No seal, no preregistration, no checkpoint, no result package, no
adapter, and nothing under any historical `audit_*` or `task4f1_*` namespace appears in either diff.
Independently corroborated by `tools/verify_frozen_artifacts.py` (`match=26 mismatch=0`) and by
`tools/verify_continuity_state.py` re-hashing all 32 declared anchors.

**Register D1/D2 left in place and superseded in writing.** At the research tip both rows still read
`OPEN — needs adjudication` / `OPEN — needs an explicit deviation ruling`. The decision supersedes
them in prose in §2, §3 and §6 ("They are **superseded by §2 and §3 of this document** and are
deliberately left unedited"), the ledger L-059 records the same, and the state file's
`register_rows_left_stale_deliberately` key records it a third time. Correct additive treatment,
consistent with how D10 handles the stale sentence inside the frozen preregistration.

### The one deliberate in-place state change — is the disclosure adequate?

`cf03007` renamed `proposed_narrow_conclusion_not_adopted` → `narrow_conclusion_text_ACCEPTED_2026_09_07`
and replaced the trailing sentence "AWAITING HEAD RESEARCHER ADJUDICATION." with an acceptance
pointer. I verified the commit's own claim: the conclusion text up to and including "…other encoders
or corpora." is **byte-identical** across the change; only the trailing sentence differs.

Disclosure exists in three independent places: (1) its own single-file commit with an explanatory
message; (2) ledger L-060's predecessor line, "L-059 / 9271341 (state-hygiene follow-up cf03007)";
(3) the commissioning prompt itself, which names the change and asks an auditor to judge it.

**My judgment: the disclosure is adequate and the change should not have been forced to be
additive.** The object is an operational state file, not a frozen artifact or a decision document,
and leaving a key literally asserting "AWAITING HEAD RESEARCHER ADJUDICATION" after the adjudication
had happened would have been a worse defect than the rename — a successor reading state would have
been actively misled. The one residue worth naming: the old key name and its trailing sentence now
exist only in git history; no current document records what the state used to say. For a state file
that is acceptable. For a decision document it would not have been, and I would flag it if the
pattern migrated there.

---

## C8 — Boundary · **ESTABLISHED**

Over the whole audited range on both branches:

- **no corpus read** — no path under `data/`, no corpus file, no `.csv.gz` result package in either diff;
- **no experiment or bootstrap re-run** — the research branch adds only a markdown register and its sidecar; no runner, workflow, seal or output was created or modified;
- **no new authorization created** — `hard_stops` is **byte-identical** from L-056 to L-060, `task_4f1_run` remains `BLOCKED`, `retrieval_quality_outcome_access` remains `FORBIDDEN`;
- **no Task 4F1 artifact, candidate, seal, HMAC material or outcome touched** — zero paths under any `task4f1*` or candidate/seal namespace in either diff. The only occurrences of `--mode run`, `--mode finalize` or `V52_T4F1_AUTH_HMAC_KEY_HEX` in the added documents are inside prohibition sentences, listed in `evidence/` so the context is checkable.

**My own conduct.** I re-ran no completed experiment, no bootstrap and no reproduction; started no
experiment; read no benchmark corpus and computed no retrieval outcome; did not recompute the
LongMemEval dependency graph; performed no Task 4F1 action of any kind — no `--mode run`, no
`--mode finalize`, no `run_archives`/`evaluate_archive`/`finalize_results`, no HMAC key set, no BEAM
outcome read or inferred; ran no literature scan; proposed no experiment. I read the persisted
per-question **result rows**, which are the aggregate-rebuild artifact the preregistration §10.9
exists to provide to an auditor, and which C4 requires. I ran two read-only repository verifiers.
I committed only under my own namespace and pushed only my own branch.

---

## Verdict

# `CLOSURE PASS WITH CAVEATS`

The acceptance record is sound. Every substantive claim I could test from bytes holds: the document
identities, the A/B ruling and its textual derivation, the accuracy of the §7/§9 deviation, the
numerical correction to within 1.1e-14 of exact rational arithmetic, the evidence bindings including
the `A2_SHA256` pin, the honest separation of provenance from recomputation, the additivity of every
change, and the boundary.

### Findings that would require the stage to be reopened

**None.**

### Findings that would not — all correctable additively

F1 (a "verbatim" block carrying added emphasis on the phrase the ruling turns on, plus dash
substitution); F2 (the outcome-free assertion scoped to "this section" while §2.4 carries the table);
F3 ("The exact differences" are truncated float renderings, ≤2.08e-14 from exact); F4 (the inherited/
not-recomputed label absent from the decision that draws the consequence and from the register);
F5 (two citation-label sets in circulation, `NOT ACCEPTED` vs `NOT ESTABLISHED`); F6 (accepted-
conclusion final sentence differs between decision and state file, under a key asserting it does
not); F7 (§9 writes `I`, not `I_frac`; and "no direction test" is marginally stronger than the
bytes); F8 (the record does not note that ruling A primary selects the less stable estimator on the
block arm); I1 (no `.gitattributes`, so both shipped verifiers fail on any default Windows clone —
proven, and the cause of the two earlier auditor reports).

### Where I judge the record claims more than it verified

Three places, all small and all presentational:

1. **"verbatim"** in §2.1, for a block with emphasis added to `per rotation seed` (F1).
2. **"The exact differences"** in §2.4, for values that are neither exact nor, in three of four
   cells, the document's own float subtraction (F3).
3. **"no band, threshold or direction test"** for `I_frac` — right on band and threshold, marginally
   overstated on direction, since §9 does draw a qualitative direction distinction (F7).

Against that, two places where the record is *more* careful than it needed to be and I want it on
the record: it says plainly that the A/B table came "from the persisted summaries" rather than
claiming a per-question re-derivation it did not do; and the clarification note's separation of
provenance from computation is exemplary, including the sentence "Confirming that a file contains a
number is not confirming the number." Both survived adversarial checking.

### What I could not do

Nothing in scope was blocked. I did not attempt anything the prompt placed out of scope, and no gate
required data I could not reach. The preregistration's absence of a `.sha256` sidecar meant C1 could
verify it against the state file and the two documents rather than against a sidecar; its blob hash
matches all three.
