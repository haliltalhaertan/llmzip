# Muse session — BENCH-3A: REALTALK (real-world third benchmark) — frozen-pipeline port

You are porting the programme's FROZEN representation+eval pipeline to a NEW dataset, REALTALK
(real-world messaging conversations with message-level gold evidence). LOCAL work only:
read-only /mnt/c; write ONLY /tmp/b3a/; no network; interpreter `$HOME/muse-work/faiss-python`
(numpy/scipy/sklearn/faiss available). Label every output [LOCAL EXPLORATORY PILOT].

## What the frozen pipeline is (read these; do not guess)

- Canonical items: `llmzip/adapters/longmemeval_v52_adapter.py` + `_v2.py` (build_archive;
  memory_text = "[{date}] {role}: {content}"; fit receives memory_text strings ONLY).
- Producer (SIGN96 source of truth): `llmzip-work/drive/v52_t4c3_coordinate_axis_probe.py` —
  its `buildrep`: C96 = Y96 − mu96, Y96 = L2-normalize(TruncatedSVD(96, seed=5204) over
  [latent32|word|char] archive features); query path transforms question after archive fit;
  sign(C96) = native 96-bit code.
- Regeneration harness: `llmzip-work/harness/lme_regen.py` (re-executes producer's buildrep;
  describes exact gates). Ground truth for port fidelity: `llmzip-work/regen/lme/cache_repr/*.pkl`
  (fields include C, qC, gold, hetero).
- Arm + eval semantics reference: `llmzip-work/harness/deney1_lme.py` (fractional R@3, K=3,
  20 tie draws, per-budget arms SPREAD/RANDOM×10/TOP/BOT, tie protocol details) and
  `llmzip-work/harness/deney1_loco.py` (dialogue-benchmark variant; LoCoMo formatting choices).
- float96 baseline definition: see `llmzip-work/` task1 extension materials
  (`regen/task1_RESULTS_extended.json`, `harness/task1_extend_lme.py`) — mirror it exactly.

## Data (already downloaded, do not re-download)

`llmzip-work/bench3/REALTALK/data/Chat_*.json` — 10 real chats. Fields per chat: `name`
(speaker_1/speaker_2), `session_i` (list of messages: clean_text, speaker, date_time, dia_id
like "D1:6", img_*), `session_i_date_time`, `events_session_i` (annotations; NOT used for
retrieval), `qa` = [{question, answer, evidence: [dia_id...], category 1-3}]. Totals: 728 QA,
categories 301/319/108, ~410–1548 messages per chat. NOTE: repo has NO license file — record
this fact in the report; local research use only, cite the REALTALK paper (arXiv:2502.13270).

## STEP 0 — PORT FIDELITY GATE (mandatory, before any REALTALK number)

Write `port.py` that reconstructs C96 for a given LME question using ONLY the producer's frozen
logic (import the producer's buildrep directly if feasible; else replicate it bit-exactly and
justify). Gate: for ≥5 sampled LME qids (include e.g. the first 5 lexical), recompute C96 from
the canonical dataset and compare to regen/lme/cache_repr/<qid>.pkl:
  max|diff| ≤ 1e-10 AND sign(C96) identical 100%. Also reproduce qC for the same qids.
Write `port_gate.json` with per-qid results. DO NOT proceed past this gate if it fails; debug first.

## STEP 1 — REALTALK canonical items

`bench3_realtalk_adapter.py`: per chat, per QA item:
- qid: `RT{chat:02d}_q{idx:03d}` (chat = 1..10 by lexical filename order; state it).
- archive: ALL messages of the chat (across sessions); memory_id = dia_id; memory_text mirrors
  the LoCoMo formatting decision for dialogues (inspect deney1_loco.py / locomo_regen.py and
  MATCH its "[date] speaker: text" convention; document exactly what you chose).
- gold: evidence dia_ids resolved to memory_ids; assert 100% resolution (else stop and report).
- fit input = archive texts only (leakage barrier: never the question/gold).
Validate: every chat; counts (728 QA total); per-category tally 301/319/108; any anomalies.

## STEP 2 — Run + measurements

Using the ported pipeline (same seeds/definitions as LME where derivable):
- native SIGN96 FR@3 (this is THE headline: compare float96 vs sign96 delta with LME's +10.0pp
  and LoCoMo's +12.0pp pattern).
- float96 FR@3 (baseline, per frozen definition).
- Ladder arms at 80/64/48 bits: {SPREAD, RANDOM×10 (same seed formula, RT lexical ordinals),
  TOP, BOT} — construction EXACTLY as deney1 arm definitions (spread = repaired rank-linspace;
  random = 10 draws; top = top-variance; bot = bottom-variance).
  Wait: state clearly in the report which construction you used for each arm and why.
- Tie diagnostics (light): per-QA top-3 boundary tie count under native code (ties at 3rd vs
  4th Hamming distance), mean top3-tail gap; ties share overall.
- Per-category means (cats 1-3) for native/float + best ladder arm at 64b.
- Determinism: rerun the exact same commands; outputs bit-identical (or explain).

## STEP 3 — Report

`/tmp/b3a/report.md`: every number with n and decimals; a checklist comparing the SAME pattern
claims as LME/LoCoMo: (1) sign96 > float96? delta; (2) ladder monotone in bits, with costs at
80/64/48; (3) SPREAD ≈ RANDOM vs TOP penalty (sign + size); (4) BOT position; (5) category
profile; (6) anomalies/limits. Also `details.json` with per-QA FRs per arm. End stdout with
`REALTALK_VERDICT:` line: headline deltas + gate results + any DIFF/anomaly + coverage.

Harsh honesty: if something can't be checked, say so; if a choice was forced, log it. Do not
touch any race_2026-09-13 artifacts, prereg files, or the sealed programme state; do not run
faiss; do not use network.
