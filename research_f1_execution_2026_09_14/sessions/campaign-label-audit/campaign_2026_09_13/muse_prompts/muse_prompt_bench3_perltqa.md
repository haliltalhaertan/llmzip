# Muse session — BENCH-3B: PerLTQA (structural generalization) — frozen-pipeline port

You are porting the programme's FROZEN representation+eval pipeline to PerLTQA (personal
long-term memory: profile/social/episodic banks + reference-memory QA). LOCAL work only:
read-only /mnt/c; write ONLY /tmp/b3b/; no network; interpreter `$HOME/muse-work/faiss-python`.

## What the frozen pipeline is (read; do not guess)

- Producer (SIGN96 source of truth): `llmzip-work/drive/v52_t4c3_coordinate_axis_probe.py`
  buildrep: C96 = Y96 − mu96, Y96 = L2-normalize(TruncatedSVD(96, seed=5204) over
  [latent32|word|char] archive features); sign(C96) = native code; query transformed after fit.
- Adapter conventions: `llmzip/adapters/longmemeval_v52_adapter.py` (+v2): memory_text strings
  only into fit; no gold/question leakage; per-archive fit.
- Eval/arm semantics: `llmzip-work/harness/deney1_lme.py` + `deney1_loco.py` (fractional R@3,
  K=3, 20 tie draws; arms SPREAD/RANDOM×10/TOP/BOT at 80/64/48 bits; tie protocol).
- float96 baseline: mirror its frozen definition (see task1 extension materials).
- Ground truth for the port gate: `llmzip-work/regen/lme/cache_repr/*.pkl` (C, qC, gold).

## Data (already downloaded)

`llmzip-work/bench3/PerLTQA/Dataset/en_v2/perltqa_en_v2.json` — list of 32 characters; each:
{char: {profile: [QA...], social_relationship: [...], events: [...], dialogues: [...]}} where
QA = {Question, Answer, Reference Memory, Memory Anchors}. 1905 QA total (357/294/628/626).
`llmzip-work/bench3/PerLTQA/Dataset/en_v2/perltmem_en_v2.json` — 141 chars' memory banks:
{char: {profile: dict fields, profile_description: str, social_relationship: dict,
events: dict, dialogues: dict}}. License: CC BY-NC 4.0 (non-commercial research; record it).

## STEP 0 — PORT FIDELITY GATE (mandatory)

Same as the LME port gate: reconstruct C96 + qC for ≥5 sampled LME qids via producer's frozen
logic; compare against regen/lme/cache_repr pkls: max|diff| ≤1e-10, sign codes identical.
Write `port_gate.json`. Do not proceed if it fails; debug first.

## STEP 1 — Itemization (the key design decision — document precisely)

Define the archive itemization for a character's memory bank, e.g.:
- profile: one item per field ("{field}: {value}" → memory_text mirroring LME style, e.g.
  "[profile] {field}: {value}"); profile_description: decide (one item, or split into
  sentences — pick ONE, justify, apply uniformly);
- social_relationship: one item per entry;
- events: one item per event narrative; dialogues: decide granularity (per-turn vs
  per-dialogue; justify; must let anchors/refs map).
- memory_id scheme: stable, e.g. `PQ{char:03d}_{section}_{idx:03d}`.
- qid: `PQ{char:03d}_{section}_q{idx:03d}`.
Gold mapping: resolve each QA's "Reference Memory" (+ anchors) to bank item(s):
- profile/social/events/dialogues QA → the referenced item(s); use field name for profile,
  index/name fields for others; for narratives use the anchors as substring checks where
  available (anchors may be [-1,-1] — then rely on the section's reference field).
- Count resolved/unresolved per section; if unresolved >0, state exact counts and the RULE
  used; proceed with resolved-only (report n_resolved/n_total).
Validate totals: 32 chars, 1905 QA, section tallies 357/294/628/626.
Some banks may be small (N<25): handle per frozen logic where possible; if a char's archive
can't support SVD96, report it explicitly and exclude with the reason (do not silently shrink).

## STEP 2 — Run + measurements

Ported pipeline; same seeds/definitions as derivable. Measure:
- native SIGN96 FR@3 vs float96 FR@3 (headline delta; compare to LME +10.0pp / LoCoMo +12.0pp).
- Ladder arms at 80/64/48: {SPREAD, RANDOM×10, TOP, BOT} exactly per deney1 constructions
  (state them). NOTE: PerLTQA banks are small; effective-M caps apply — report N per archive
  and any cap effect explicitly.
- Tie diagnostics (light): top-3 boundary tie counts, mean gap.
- Per-section means (profile/social/events/dialogues) for native/float + best 64b arm.
- Determinism rerun check.

## STEP 3 — Report

`/tmp/b3b/report.md` + `details.json`: every number with n; the SAME pattern checklist as
LME/LoCoMo: (1) sign96 vs float96; (2) ladder costs; (3) SPREAD≈RANDOM vs TOP; (4) BOT;
(5) section profile; (6) anomalies/limits + the itemization decisions + resolution counts.
End stdout with `PERLTQA_VERDICT:` line: headline deltas + gate + coverage + anomalies.

Harsh honesty; no race/prereg/faiss/network touching; write only /tmp/b3b and print to stdout.
