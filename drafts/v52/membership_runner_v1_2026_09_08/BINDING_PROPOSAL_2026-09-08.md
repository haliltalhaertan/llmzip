# Binding proposal — mapping source, environment lock, bootstrap seeds

**Nothing in this document is bound.** Every artifact it proposes carries
`binding_status: "PROPOSED"`. No raw corpus was read or downloaded, no retrieval, fitting, ranking or
real-data bootstrap was run, no package or interpreter was installed or changed, no seal was made, and
the independent runner review is not commissioned. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`. The v3 core and every hash-bound
document are untouched.

Everything below was obtained by **read-only inspection of committed records**, each read as a **raw
Git blob** and hash-checked before use.

---

## 1. The expected-mapping source — FOUND for LoCoMo, and only a cohort is needed for LongMemEval

### What was rejected first

`audit_v52_t4f0_codex_2026_08_31/conversation_inventory.csv` is **not** usable and was not bound. Two
independent reasons:

- it is the **wrong benchmark** — its rows are BEAM (`tier=100K`, `chats/100K/1/chat.json`), not LoCoMo;
- it is a **conversation inventory**, which is not a question→conversation mapping. The same applies to
  `estimand_primary_cohort.csv` in that namespace, whose ids are BEAM (`100K::1::abstention::1`).

### What was found — LoCoMo

The producer encodes the conversation in the question id itself: **`locomo_<conversation_index>_qa<n>`**.
Two committed per-question records carry it, and they agree **exactly**:

| record | commit | blob sha256 |
|---|---|---|
| original research output `research/v52/locomo_scale_outputs/locomo_scale_per_question.csv.gz` | `692f599eedeb7e7a649443f24ff507e8c4d1c17d` | `b7abd942c13cf9ce1b1c4a13e3ff39fb26a26e8b2f2749dd92d76f0b2a474602` |
| independent bit-exact reproduction `audit_v52_locomo_reproduction_2026_09_07/reproduced_outputs/locomo_scale_per_question.csv.gz` | same | `efed0c46cd0f34e45daa5fcdf5d08fc51a61ffaafd6ca1d522c6c4c98fc7834f` |

The second reproduced the first with `max_absolute_numeric_difference = 0.0`, `changed_numeric_cells = 0`,
positive control PASS and six negative controls all rejected (`comparison.json`), and its
`original_sha256` field matches the first record's blob hash exactly.

**The mapping agrees between them, question for question**, and it covers the expected cohort:

- **1535 questions**, **10 conversations**, every id matching the scheme — 0 exceptions;
- per-conversation: 150, 81, 152, 199, 178, 123, 149, 191, 156, 156 — **sum 1535**;
- **independent cross-check:** `actual_source_identity.json` (blob `ecb8384624aee0cc…`) lists exactly
  **ten** conversation files `audit/conv_0.json … audit/conv_9.json`, agreeing with the ten indices the
  id scheme yields. It also fixes the corpus: `locomo10.json`, 2,805,274 bytes, sha256
  `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`, which is the `source_sha256` the
  proposed manifest carries.

**Provenance label — this is the distinction you asked to be kept explicit.**
This mapping is **INHERITED FROM PRODUCER METADATA**, not independently derived from the raw corpus.
The two records are independent of each other in the way that catches a transcription or pipeline
error — different agents, different runs — but both descend from the same labelling decision made when
the ids were generated. **If the producer assigned a question to the wrong conversation at generation
time, this mapping inherits that error and cannot detect it.** An independent derivation would have to
parse `locomo10.json`, which is a separate task (§4).

### What was found — LongMemEval, and why less is needed

Its question ids are opaque (`001be529`, …) and **carry no session or conversation component**. No
committed record supplies one. **None is invented, and no other benchmark's inventory is substituted.**

That gap does not block the experiment, because **R2 line 141** defines no conversation-cluster
bootstrap for LongMemEval — the only scheme is the question-level bootstrap, which needs the cohort and
not a grouping. Two committed records agree **exactly** on the **470-question cohort**:

| record | commit | blob sha256 |
|---|---|---|
| `research/v52/longmemeval_scale_outputs/longmemeval_scale_per_question.csv.gz` | `692f599e…` | `1db682a277b8fe7f0b3aa7cf02831bf07f0d5c4c340796a57c93df5441df3157` |
| `docs/v52/task4c2/V52_T4C2_question_level.csv` (on `main`) | `origin/main` | `69c21b2ffaea1e92923bf3f0e83287e12d07a5f34b4b42afde1752d6b50b3b51` |

The second's hash **matches the hash recorded for it in `V52_T4C2_POST_RUN_MANIFEST.json`**, so its
identity is confirmed against that stage's own record rather than assumed.

The proposed manifest therefore assigns all 470 questions to **one explicitly named sentinel cluster**,
`longmemeval_single_connected_component_inherited_task3a1`, which records the inherited single connected
component and which the runner refuses to resample. It does not claim a conversation structure.

### The proposed artifacts

| file | sha256 | contents |
|---|---|---|
| `binding/PROPOSED_mapping_locomo.json` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` | 1535 questions → 10 conversations |
| `binding/PROPOSED_mapping_longmemeval.json` | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` | 470-question cohort, one sentinel cluster |

Each has a `.provenance.json` sidecar recording `binding_status: PROPOSED`, `raw_corpus_read: false`,
every input blob hash, and the manifest hash. `binding/derive_expected_mappings.py` regenerates both and
**aborts** if any input blob hash differs or any LoCoMo id fails the scheme — it guesses nothing.
`binding/validate_proposed_manifests.py` puts both through the runner's own contract: **19 checks, ALL
PASS**, including that the count-preserving swap corruption is still caught on the **real** 1535-question
cohort, and that a LongMemEval cluster bootstrap is refused before any seed is read.

That validation proves schema, internal consistency and gate behaviour. It does **not** prove the cohort
matches the corpus — feeding a manifest its own columns is consistent by construction. The cohort
evidence is the cross-record agreement above, not that script.

---

## 2. Environment — the recommendation is **not** the BEAM-adjacent stack

The new experiment gets its own lock; Task 4F1's is not inherited. Three environments compared from
committed records:

| | Task 4F1 V7 (BEAM) | this session's dev env | **LoCoMo / LongMemEval representation pipeline** |
|---|---|---|---|
| source | `task4f1_execution_candidate_v7_2026_09_03/DEPENDENCY_LOCK.txt` | measured | `audit_v52_locomo_reproduction_2026_09_07/preflight.json` (`134acfc1…`), `environment.txt` (`52efac89…`) |
| Python | 3.12.13 | 3.12.14 | **3.13.15** |
| numpy | 2.3.2 | 2.3.2 | **2.3.5** |
| scipy | 1.16.1 | 1.16.1 | **1.17.0** |
| scikit-learn | 1.7.1 | 1.7.1 | **1.8.0** |
| pandas | — | — | **2.2.3** |
| psutil | 7.0.0 | 7.0.0 | — |

**This changes the recommendation.** My previous note offered only "adopt the 4F1 lock" or "bind
3.12.14", and both were chosen for closeness to BEAM — which you correctly said should not be the sole
justification. The relevant environment is the one that **produced and bit-exactly reproduced the
LoCoMo and LongMemEval representations this experiment builds on**, and it is neither of those: it is
the `3.13.15 / numpy 2.3.5 / scipy 1.17.0 / scikit-learn 1.8.0 / pandas 2.2.3` stack. The pipeline runs
word and char TF-IDF plus LSA through **scikit-learn**, so `1.7.1` vs `1.8.0` is a difference in the
library that computes the representation, not a cosmetic one; and `pandas` is required there and absent
from the BEAM lock entirely.

**Two things were measured rather than assumed:**

1. **Bootstrap draws are unaffected by the choice.** `default_rng(seed).integers(0, n, size=n)` for
   seeds 424242 / 515151 / 606060 / 717171 and `n ∈ {1535, 470, 10}` gives byte-identical streams under
   both stacks — sha256 `83c5a58a0b9d3bfe7451ed1635a2233bd56baf49e2b7c9ae27d19a0214a82ca7` in each. So
   the lock decision does not move the uncertainty intervals. It says nothing about the representation
   pipeline, where the two stacks genuinely differ.
2. **Both suites pass on both stacks.** 85 runner checks and 99 core regression checks, `ALL PASS`
   under 3.12.14/numpy 2.3.2 and again under 3.13.15/numpy 2.3.5 — see
   `evidence/*_py313_stack.txt`. All four results remain labelled
   **`DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS`**: not lock conformance, not a seal, not authorization.

### Proposed lock (requires your approval; not adopted)

```
V52 membership-under-scaling follow-up experiment
Python==3.13.15
numpy==2.3.5
scipy==1.17.0
scikit-learn==1.8.0
pandas==2.2.3
OMP_NUM_THREADS=1  MKL_NUM_THREADS=1  OPENBLAS_NUM_THREADS=1  NUMEXPR_NUM_THREADS=1
PYTHONHASHSEED=0
UTF-8 source/data decoding required
Thread policy: one process; one worker; no implicit BLAS parallelism
```

Rationale, in order: it is the stack that produced the representations; it reproduced them bit-exactly
under independent audit; it already exists on this machine at
`work/locomo_reproduction_tmp_20260907/venv` with versions matching the committed record exactly, so
**adopting it requires no installation**; and the bootstrap draws are provably unchanged by the choice.

**Against it:** it diverges from the sealed BEAM lineage on four of five components. If cross-lineage
comparability matters more than fidelity to the representation pipeline, that is a scientific judgement
and it is yours, not mine. The thread and hash policy above is copied from the V7 lock because that part
is about determinism, not about which stack.

**Limitations of the evidence offered:** the two suites are synthetic and exercise no representation
code, so they cannot detect a scikit-learn behavioural difference. Nothing here demonstrates that the
representation pipeline gives identical output on the two stacks, and I did not run it — that would
require the corpus.

---

## 3. Bootstrap seeds

`binding/PROPOSED_bootstrap_seeds.json`:

| benchmark | scheme | seed | replicates |
|---|---|---|---|
| LoCoMo | question | `52001107` | 10000 |
| LoCoMo | cluster | `52001207` | 10000 |
| LongMemEval | question | `52002107` | 10000 |

No seed is proposed for LongMemEval × cluster: R2 line 141 defines no such scheme and the runner
refuses it, so proposing a seed would imply it exists.

**Generator:** `numpy.random.default_rng(seed)` → PCG64. Question scheme:
`rng.integers(0, n_questions, size=n_questions)` once per replicate, one index set shared by all six
arms and all ten rotation seeds (R1 §6). Cluster scheme: `rng.integers(0, n_clusters, size=n_clusters)`
once per replicate, each drawn cluster contributing **all** its questions with multiplicity preserved
and the mean divided by the total selected question **slots** (acceptance record §4). Replicates 10000,
percentiles 2.5 / 97.5, both taken from the closed core's constants.

**How the values were chosen — and how you can see no search happened.** By an announced arithmetic
rule, before any real result exists: `52000000 + 1000·benchmark + 100·scheme + 7`, with LoCoMo=1,
LongMemEval=2, question=1, cluster=2, and `7` tagging the fixed ten-seed rotation panel. No value was
tried, compared or selected against any computed quantity. The rule is machine-checkable against the
three values and was verified.

**Your point, recorded in the file itself:** writing a seed to a file immediately before a run is **not**
preregistration. `freeze_bootstrap_seed` enforces write-once and no-reuse-across-schemes; it cannot
establish that the value was chosen before the outcome. These values become preregistered only when
they are **carried inside the design/configuration document that is accepted and hashed before any real
outcome is accessible**. That binding is the decision put to you here, not something the runner can do.

---

## 4. What is still genuinely missing — information or permission

1. **An independent derivation of the LoCoMo mapping from `locomo10.json`.** The proposed mapping is
   inherited from producer metadata and cannot detect a producer-side mis-assignment. Closing that gap
   needs a **narrow, separately authorized task**: read `locomo10.json` (sha256 `79fa87e9…`) and the ten
   `audit/conv_*.json` files, emit **only** question ids and their conversation, compare against
   `PROPOSED_mapping_locomo.json`, and report agreement or disagreement. It must emit **no** scores, no
   retrieval, no representations and no outcome of any kind, and it must not be given the arms, the
   seeds or the estimand. I am **not** requesting that authority now; I am naming the task so the gap is
   not silently accepted.
2. **A LongMemEval corpus source hash.** The proposed manifest's `source_sha256` is the placeholder
   `UNRESOLVED-see-BINDING_PROPOSAL-section-1`. No committed record I inspected pins the LongMemEval
   dataset file the way `actual_source_identity.json` pins `locomo10.json`. `V52_T4C2_POST_RUN_MANIFEST.json`
   carries a `dataset_sha256` of `d6f21ea9…`, but nothing I read states which file that is over, so I
   did not bind it. **You or the adapter owner must supply it.**
3. **Your decision on the environment lock**, given the trade-off in §2.
4. **Your decision to bind the three seed values into the accepted configuration identity** — §3.
5. **Authorization to write a real ingestion path.** `run_on_real_corpus` is still a refusing stub.
6. **The independent runner review**, still not commissioned; its scope note is written and waiting.
7. **A rerun of both suites under the approved lock**, once one exists.

Items 1–4 are decisions or inputs only you can supply. Items 5–7 are permissions, not gaps in the work.
