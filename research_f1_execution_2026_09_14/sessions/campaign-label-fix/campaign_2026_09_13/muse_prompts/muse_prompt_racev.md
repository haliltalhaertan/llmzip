# Muse session — RACE-V: INDEPENDENT RECOMPUTATION of the official race run

You are an independent verifier (D1V-pattern). Recompute key numbers from RAW ARTIFACTS; never
trust stored values. Read-only /mnt/c; write only /tmp/racev/. No network. Use the WSL
`~/muse-work/faiss-python` interpreter (faiss 1.15.0 available) where needed.

## Materials

- Official run: /mnt/c/Users/MDP/dev/llmzip-work/race_2026-09-13/official_run/{sign,faiss}/
  (race_sign_details.json, race_faiss_details.json, smoke logs, manifests, consoles).
- Seal: race_2026-09-13/PRE_RUN_SEAL_local.json. Runner sources: race_2026-09-13/rb2/race_sign.py,
  rb3/race_faiss.py (read for exact definitions; do NOT execute as authority).
- Frozen data: regen/lme/cache_repr/*.pkl; regen/locomo/*.pkl + drive/audit_layer; anchors
  0.5419751773049645 (LME) / 0.23654714666441054 (LoCoMo); tie protocols as always
  (5_100_000+lex*100_000+t*100+99; stable_archive_seed(ci,t)+99; 20 trials; K=3; fractional R@3).

## Checks (all; report EXACT/DIFF with numbers)

1. **Seal integrity:** sha256 of the two runner files vs the sealed hashes (state match).
2. **Sign side (RB2):**
   a. Native anchors recomputed in your own implementation (both benchmarks) ≤1e-12.
   b. Spot-check FRs: pick 12 (qid, arm) pairs spanning {NATIVE96, SPREAD80, BOT80,
      RAND80_s2, TOP48, BOT48} × both benchmarks from the official JSON; recompute each FR from
      the pkls with your own tie-protocol implementation; ≤1e-12.
   c. Aggregates: recompute 6 arm means from stored per-question arrays; compare to stored
      aggregates; also verify the MATH-1 model column for 5 (qid, arm) pairs against the exact
      f(S,T) identity.
   d. Validity callouts: TOP48 LME = 0.34949468…, SPREAD80 LME = 0.52526…, BOT80 LoCoMo =
      0.23546… — confirm to the digits (state tolerance).
3. **Faiss side (RB3):**
   a. Byte replay: reproduce RQ96=20, RQ32=12, IndexPQ(96,12,8)=12, ext-2bit=44 via the pinned API.
   b. Determinstic retrain: retrain PQ on 2 archives (1 LME + locomo_1) with the runner's exact
      call sequence; compare code hashes vs the runner's run if codes are persisted in JSON
      (else state not-checkable) — and recompute 5 A6 FRs on those archives to ≤1e-12 if codes
      match / or document.
   c. JSON self-consistency: arms_summary vs arms_per_q means (all arms, both benchmarks);
      W/T/L counts recomputed vs stored; mask stats 0.
   d. Spot-check one RaBitQ32 arm: recompute 3 FRs from the stored per-q arrays' inputs if
      feasible via the runner's persisted artifacts; if not checkable, say so explicitly.
4. **Official-vs-build comparison reproduction:** re-run the numeric-tree diff (build copies at
   race_2026-09-13/rb2/race_sign_details.json and rb3/race_faiss_details.json vs the official
   copies); confirm the OFFICIAL_RUN.md claims (RB2 one timing diff; RB3 last-ulp + timings +
   byte_worksheet annotation-only).
5. **Disposition arithmetic:** from official numbers recompute the primary contrast per benchmark
   (SIGN − max competitor over the sealed set, using the sealed K=40/41 membership list from
   rb1/frozen_literals.json — state the max competitor and its value); compare to +2.0 / −6.4 /
   −3.7 lines; state the zone.

## Output

/tmp/racev/racev_report.md + racev_details.json; stdout ends with RACEV_VERDICT:
<n_exact/n_checks; any diffs; official-run numbers verified: yes/no-partially>. Harsh honesty;
list everything not checkable and why. ~2-3 hours scale.
