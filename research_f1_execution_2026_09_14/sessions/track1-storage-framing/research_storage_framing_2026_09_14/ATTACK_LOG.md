[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 3 — Attack log

PREPARED, NOT ACCEPTED. All arithmetic below was executed locally in this session (VERIFIED) on committed bytes; no sealed material touched, no faiss installed, no corpus opened beyond archive-cardinality CSV (the same input the cost script itself uses). FAILED attacks (claim survived) strengthen the claim; PASSED attacks (claim broke) are marked.

## Attack 1 — Recompute the 88,886 median from raw JSON (target: HONEST-side provenance)

- Method: independent median of per_archive `ratios.a_raw.effective` from `PROJECTOR_BYTES.json` (15 values).
- Result: 88886.36234817814, exact match to full float precision. Min 80266.51, max 104463.62; N range 443–551. **ATTACK FAILED — figure's arithmetic is correct.**

## Attack 2 — Median-of-ratios vs ratio-of-medians (target: the figure's uniqueness)

- Method: 44220235 (median total) / 490 (median N) + 12 = 90257.38 vs quoted 88886.36.
- Result: conventions differ by 1,371 B (~1.5%). The pilot never states its convention — the same class of error the cost package explicitly corrected for 287.69 (mean-of-costs vs cost-at-mean, Jensen gap 1.07 B). **ATTACK PASSED (weakly) — the figure is convention-dependent; damage is small (~1.5%) but the undisclosed convention is a genuine provenance gap.**

## Attack 3 — Recompute break-evens under all four projector dtypes (target: "millions needed" claim)

- Method: ceil(median_total/12) for a/b/c1/c2.
- Result: 3685020 / 1890510 / 1977778 / 1411767 — all match the report exactly. Cheapest (f16+zlib, 1.41M) is still ~2,560× the largest measured archive (551) and ~2,290× the frozen max (616). **ATTACK FAILED — no measured format rescues the framing.**

## Attack 4 — Global-sharing rescue: one projector for all 470 archives (target: MISLEADS-side "no scale fixes it")

- Method: 231,606 total vectors (summed from frozen geometry CSV on main — VERIFIED n=470, min 396, max 616, mean 492.78, matching EVIDENCE.json exactly); effective = 12 + total/231606.
- Result: 202.93 / 109.95 / 114.47 / 85.15 B/vector — still 7–17× the cap. **ATTACK FAILED — even maximal sharing within the benchmark does not reach 12.** (Plus the revision forbids this amortization by rule, PREREG_DRAFT.md lines 79-81.)

## Attack 5 — Find an archive size where the conclusion flips (target: both sides' generality)

- Method: solve N for effective ≤ 384 (float parity) and ≤ 24 (2× marginal) under format (a).
- Result: N ≥ 118,872 for float parity (193× largest archive); N ≥ 3,685,020 for 2× marginal. No real archive (396–616) is within a factor of ~190 of flipping. **ATTACK FAILED — the conclusion is robust over 2+ orders of magnitude of N.**

## Attack 6 — Verify faiss code_size values from the replay receipt (target: HONEST-side cost basis)

- What I could check without installing faiss: (i) replay `COMPARISON.json` records `strict_non_environment_equal: true`, `differences: []`, exit 0 across Linux→Windows with faiss 1.15.0 pinned (CLAIM, read from receipt); (ii) arithmetic structure of EVIDENCE.json: nb1 overhead = code_size − d/8 = 8 exactly for all six d values (VERIFIED); **additionally found: nb2 overhead = code_size − d·2/8 = 20 exactly for all six d values (VERIFIED — the evidence text never states this; it generalizes the "fixed overhead" structural claim to the 2-bit form).**
- Result: structure VERIFIED from bytes; cross-platform exactness RELAYED from the receipt (I did not execute faiss — installs forbidden). **ATTACK FAILED on structure; execution leg remains receipt-backed, not independently reproduced by me.**

## Attack 7 — Test the "8-byte fixed overhead" across d (target: RaBitQ ineligibility, the HONEST side's showpiece correction)

- Method: above arithmetic + functional note: EVIDENCE + OPEN_ITEMS_CLOSED.md show decoded norms tracking input scale (1.029→1.268, 9.144→11.656, 114.544→143.054), which a sign-only code cannot do (CLAIM, read; the numbers are in the committed doc).
- Result: overhead constancy holds exactly (8 for nb1, 20 for nb2 — VERIFIED). The ineligibility ruling (20 B, not 12) survives. **ATTACK FAILED.**

## Attack 8 — Recompute the 287.69 OPQ panel figure from the frozen CSV (target: HONEST-side disclosure number)

- Method: mean over all 470 frozen N of (12 + 135325/N).
- Result: 287.6889713064122 — matches EVIDENCE.json to all 16 decimal digits; cost-at-mean 286.6161584760326 also matches. **ATTACK FAILED — the quotable figure is exactly reproducible from the frozen cardinality column.**

## Attack 9 — Quote-hunt: find the 12-byte figure used where total footprint is the natural reading (target: HONEST side)

- Hit 1 (VERIFIED): pushed prereg §1: "At a fixed 96-bit (12-byte) budget, is SIGN96 competitive…" + arms table headed "budget" with "96 bit" entries — no "marginal" qualifier anywhere in the question or table. A storage-reader's natural parse is total footprint. The qualifier arrived 2 days later (L-088).
- Hit 2 (VERIFIED): revision arm table gives SIGN96 as "12" marginal with "BinaryFlat S0 33 B; add external preprocessing/centering state" — the preprocessing addendum is named but unmeasured, so even the qualified table cell is "12 + unknown."
- Counter-weight found (honest-side defense, VERIFIED): HR decision + L-088 + revision §3 make the marginal/shared/effective split explicit and mandatory; the original contrast was cancelled. The programme fixed the language going forward.
- Result: **ATTACK PASSED on the original draft; correctly-scoped thereafter. Net: the misleading quotation exists in a pushed (unmerged) draft, not in current binding text.**

## Attack 10 — Component-share audit of the headline (target: "dominated by s96" and double-counting)

- Method: median archive 078150f1 (total 44,220,235): s96 37,634,304 (85.11%), sv 5,041,664 (11.40%), vocab 1,151,987 (2.61%), IDFs 0.89%, mu 384 B (~0%). d_lex = 32 on all 15 archives (VERIFIED).
- Result: shares match the report's "s96 %85,1, sv %11,4, vocab %2,6" (VERIFIED). No double-counting found; inventory matches the query path per the auditor's source check (RELAYED). **ATTACK FAILED.**

## Attack 11 — Common-mode projector: does FLOAT96 need the same machinery? (target: MISLEADS-side sign-inversion)

- Method: searched the projector report, revision draft, HR decision, and cost README for any accounting of query-encoding state for the float reference arm.
- Result: nothing found. The revision's FLOAT96 row says "384 float32 payload B, plus any auxiliary" with "actual shared headers/state" — unmeasured. **ATTACK INCONCLUSIVE — neither side has the common-mode analysis; the sign-inversion point stands only if the 88 kB is SIGN96-specific, which is currently unproven in both directions.** This is the load-bearing gap behind the verdict's damaging assumption.

## Summary scorecard

Failed (claim survived, strengthened): 1, 3, 4, 5, 7, 8, 10. Passed (claim broke): 2 (weakly, 1.5% convention gap), 9 (original draft quotation). Inconclusive: 6-execution-leg (receipt-backed), 11 (missing common-mode analysis — the most important unresolved attack).
