# E1 V1 disposition — pre-run mechanism refinement

Status: **SUPERSEDED BEFORE E1 EXECUTION / NO OUTCOME FROM THE FROZEN E1 RUN WAS SEEN**.

V1 commit: `d1e429ccc227f233389dfc97c368cbea3752b1ec`.

The V1 bridge finding remains valid as a descriptive observation: across the six already-observed units, the sign of `BOT−TOP` matches the sign of `SIGN−float` 6/6. However, the V1 verbal mechanism — that task-relevant discrimination is carried disproportionately by lower-variance coordinates — is too strong and is contradicted by an older LongMemEval pilot already present before E1 was designed.

`pilots_round1/REPORT.md` says all 96 axes have positive marginal gold-vs-nongold signal and that the strongest individual axes are high-variance axes. Yet TOP48 performs much worse jointly than BOT48/random/spread. The same old diagnostics show TOP48 vs BOT48:

- `mean_abs_phi`: 0.05926 vs 0.03726;
- duplicate-code fraction: 0.02352 vs 0.00579;
- top-3 boundary tie rate: 0.45957 vs 0.42340.

Therefore the licensed pre-run hypothesis must move from “low variance carries more semantic signal” to a joint-geometry hypothesis: high-variance axes may be individually informative but jointly redundant / tie-producing, while heterogeneous mixtures preserve complementary ranking information.

No raw E1 C96/qC analysis had been run when this refinement was written. V1 files remain immutable history; V2 is additive.

Task4F1 remains untouched.
