# Narrow data-identity task — results

Authorized scope: identity and mapping checks only. **Not done anywhere in this task:** representation
learning, fitting, retrieval, ranking, evaluation, real-data bootstrap, pilot, or any download. No
producer adapter or shard module was imported or called. **No question, answer, dialogue or session
content was printed, logged, written to a file, or uploaded** — only identifiers, integer indices,
categories, counts and set sizes left the scripts. Both scripts are committed and replayable:
`identity/verify_locomo_mapping.py`, `identity/verify_longmemeval_identity.py`.

---

## A. LoCoMo — mapping **CONFIRMED AGAINST THE RAW SOURCE**

**Source identity verified first.** `locomo10.json`, **2,805,274 bytes**, sha256
`79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` — matching the pinned value from
`actual_source_identity.json`. The script aborts before reading anything if that fails. Local copy:
`work/locomo_reproduction_tmp_20260907/preflight_source_bytes/locomo10.json` (a second identical copy
exists under `reproduction_output/source_bytes/`).

### The identity rule, written out, because it is positional

The producer's id `locomo_<c>_qa<n>` carries **two positions, not two stored keys**:

- **`c`** — the 0-based index of the conversation in the **top-level JSON list**. It is **not** the
  conversation's own `sample_id`. Index 0 is `conv-26`; index 9 is `conv-50`. Reordering the top-level
  list would silently change what every id means.
- **`n`** — the 0-based index of the question in that conversation's **raw `qa` list**, before any
  cohort filtering.

That `n` indexes the **raw** list is **proved, not assumed**: in conversations 0, 1, 6 and 9 the
cohort's index set is non-contiguous and its maximum exceeds the cohort size (e.g. conversation 1 has
81 questions but a maximum index of 81), which a filtered index cannot produce.

### Checks — 8 of 8 pass

| check | result |
|---|---|
| raw conversations vs mapping clusters | **10 vs 10** |
| every conversation index exists in the source | pass |
| every question index resolves to a real question of the conversation its id names | **0 out-of-range** |
| the index is into the raw `qa` list, not a filtered one | **proved** via conversations 0, 1, 6, 9 |
| no cohort question sits on a category-5 position | **446** category-5 questions in the source, **none** selected |
| the rule `category != 5 AND evidence non-empty` reproduces the cohort | **9 of 10** conversations exactly |
| range + category structure narrow the assignment | 2 candidates of 3,628,800 |
| with the selection rule the assignment is **uniquely determined** | **1** perfect matching — the identity permutation |

Raw `qa` lengths `[199, 105, 193, 260, 242, 158, 190, 239, 196, 204]`, total **1986**; cohort
`[150, 81, 152, 199, 178, 123, 149, 191, 156, 156]`, total **1535**.

**Why this is genuinely independent.** Treating the assignment as a permutation problem: the raw file's
own structure — per-conversation length, category-5 positions, empty-evidence positions — leaves
exactly **one** consistent assignment of the ten cohort index sets to the ten raw conversations, and it
is the identity. The producer's labelling is therefore confirmed by the corpus rather than trusted.

**One residual, disclosed rather than smoothed.** The reconstructed selection rule leaves **one**
position unexplained: conversation 6, raw index 11 — a category-2 question with one resolvable evidence
id that is nevertheless absent from the cohort. 1 of 1986. I did not guess a rule to cover it; a
narrower hypothesis I tested (evidence pointing only at image turns) was **wrong** and is not reported
as a finding. This residual does **not** affect the mapping: every one of the 1535 accepted questions
is confirmed to sit in the conversation its id names. It affects only the reconstruction of *why* those
1535 were chosen, which was not the authorized question.

## B. LongMemEval — source identity **RESOLVED AND VERIFIED**

### What `dataset_sha256` covers — resolved from committed source, not assumed

| step | evidence |
|---|---|
| the value is computed as | `docs/v52/task4c2/v52_t4c2_centering_geometry.py:127` — `'dataset_sha256': sha256_file(args.dataset)` |
| `sha256_file` hashes | `…:57` — the file streamed in 8 MiB blocks, i.e. **raw file bytes** |
| the expected values are pinned at | `…:23-24` — `EXPECTED_DATASET_SHA = d6f21ea9…`, `EXPECTED_DATASET_BYTES = 277383467` |
| the hash is bound to a path by | `tools/verify_frozen_artifacts.py`, `DATASET_EXTERNAL` → `data/longmemeval_s_cleaned.json` |
| corroborated by | `README.md` (file, hash, bytes, "470 non-`_abs` questions"), `DATASETS_AND_LARGE_ARTIFACTS.md`, `PROJECT_DOCUMENTATION_MANIFEST.md` |
| acquisition path | `adapters/longmemeval_v52_adapter.py:11` — HuggingFace `xiaowu0162/longmemeval-cleaned`, `longmemeval_s_cleaned.json` |

**Raw file, not transformed data.** The hash is taken over the bytes on disk before any parsing,
normalisation or adapter transformation. Nothing derived enters it.

### The file is present and verified

`C:\Users\MDP\Downloads\longmemeval_s_cleaned.json` — **277,383,467 bytes**, sha256
`d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`. Size, hash and basename all match
the bound values. **No download was performed**; the file was already on this machine.

### Cohort — 7 of 7 checks pass

500 items, all `question_id`s unique; **470** of them do not end in `_abs`, and that set is **exactly**
the accepted 470-question cohort — 0 in the cohort but absent from the file, 0 non-`_abs` missing from
the cohort.

### What the file does not supply

**No conversation grouping**, and none was inferred. The accepted manifest's single sentinel cluster
stays a **technical placeholder** — not real conversation membership, and not a dependency component
recomputed here. The conversation-cluster bootstrap remains refused for LongMemEval (R2 line 141).

### The placeholder is now resolved, additively

`binding/PROPOSED_mapping_longmemeval.json` is left **byte-unchanged**, placeholder and all.
`binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` supersedes it, changing **only**
`source_id` and `source_sha256`. Both remain `PROPOSED`; neither is bound.

---

## Answers

- **LoCoMo mapping vs the raw source:** **yes** — confirmed, and the assignment is uniquely determined
  by the corpus rather than merely consistent with it. One unexplained *cohort-selection* position
  (conv 6, index 11) is disclosed; it does not touch the mapping.
- **LongMemEval source identity:** **resolved** — raw file bytes of `longmemeval_s_cleaned.json`,
  present locally, hash and size verified, and the 470-question cohort matches the file exactly.
