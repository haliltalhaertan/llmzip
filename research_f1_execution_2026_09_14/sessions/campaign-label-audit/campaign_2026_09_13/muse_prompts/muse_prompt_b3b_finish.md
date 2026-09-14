# Muse session — BENCH-3B FINISH (PerLTQA port; killed-run salvage + verification)

You are FINISHING a killed run. A previous session ported the frozen pipeline to PerLTQA and was
externally SIGTERM-killed at ~13:50 after completing STEP 0–2 computation but BEFORE writing its
report. All artifacts survive in `/tmp/b3b/` (WSL) and a read-only salvage copy is at
`/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/`.

LOCAL only: read-only /mnt/c; write ONLY `/tmp/b3b_fin/` (do NOT overwrite /tmp/b3b originals);
no network; interpreter `$HOME/muse-work/ml-python` (numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1).
Original brief (read it): `/mnt/c/Users/MDP/dev/llmzip-work/muse_prompt_bench3_perltqa.md`.
Labels: [LOCAL EXPLORATORY PILOT]. End stdout with `B3B_FIN_VERDICT:`.

## Salvaged artifacts (verify hashes; do not modify)
`step0_gate.py` + `port_gate.json` (PASS, 6 samples), `step1_audit.py step1b step1c`,
`step2_build.py`, `step2_eval.py`, `step2_exclude.py`, `cache_*.pkl/json`, `resolution.json`,
`exclusions.json`, `dialogue_gold_split.json`, `results.json` (8,265 per-QA rows).

## Tasks

1. **Unit reconciliation (FIRST).** Coordinator has now counted directly from the file: the
   nested QA groups EXPAND to **8593 QAs** (profile 357 / social 897 / events 4501 / dialogues
   2838); resolved **8305** (345/867/4349/2744); evaluated **8265** (Chen Zhi −40). The brief's
   "1905" was a top-level-keys miscount by the coordinator — DOCUMENTED DIFF (coordinator error,
   not run error). VERIFY all three layers yourself from the dataset file + resolution.json +
   exclusions.json; **reconcile 32 chars → 30 archives** in cache_arch_eval (coordinator found the two: Chen Zhi
   [excluded, documented] and "dragon beautiful" [no bank in perltmem_en_v2 → no archive];
   confirm both).
   Also read `step1*.py` and state exactly what ONE evaluated unit is and every itemization choice.
2. **Headline under suspicion:** native sign FR@3 = 0.48894 vs float FR@3 = 0.55169 →
   **sign LOSES by −6.275pp** — this REVERSES the LME/LoCoMo/REALTALK pattern (+10.0/+12.0/+5.2).
   Verify it is not a bug: (a) re-run `step2_eval.py` verbatim with OUT=/tmp/b3b_fin/results_rerun.json
   → bit-compare vs salvaged results.json; (b) independent spot-check: 5 QAs across sections,
   recompute top-3 by a pure-python `sorted()` path (no lexsort), compare per-q values to 1e-12;
   (c) quote code lines proving native = Hamming on sign(C) ALL-96 cols, query sign = qC>=0,
   float = cosine on CENTERED C; (d) print top-5 native & float items for 3 QAs for eyeball.
3. **Structure probes** from stored per_q: exact per-section native−float deltas (profile/social/
   events/dialogues); per-character N vs delta (small-archive effect?); gold_size vs delta;
   tie stats. Quantify where the negative delta concentrates.
4. **Convention audit:** step2_eval.py RANDOM seeds = 91000+j ("deney1 split-0"), priorities =
   5_100_000+ORD[char]·100_000+t·100+99, SPREAD = np.round(linspace(0,95,k)) over
   descending-variance order. Compare vs the brief's "deney1 constructions" and the REALTALK
   port's choices (93000-series). If a sensitivity rerun with 93000-series is <~10 min, do it
   (report both; primary = as-run). Disclose all deviations.
5. **Size flags:** N per character from `cache_arch_eval` (coordinator's quick check: range
   293–546, median 407 — no small-N instability expected beyond the excluded Chen Zhi (N=35);
   confirm and disclose per-char N table).
6. **Write** `/tmp/b3b_fin/report.md` + `/tmp/b3b_fin/summary.json`: every number with n; pattern
   checklist vs LME/LoCoMo/REALTALK: (1) sign vs float — **FAIL (negative)**; (2) ladder costs;
   (3) SPREAD≈RANDOM vs TOP; (4) BOT; (5) section profile; (6) anomalies/limits + itemization
   decisions + resolution rules/counts + exclusions. Harsh honesty. Include an explicit
   "what this means for generalization" paragraph (one benchmark fails the sign>float pattern).
