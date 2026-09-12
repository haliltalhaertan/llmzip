# Independent narrow replay review — 2026-09-12

**Disposition: PASS for the recorded synthetic Haar-objective replay and historical-value transcription only.** I am the independent review agent who actually executed this verification. Parent preparation is not scientific approval; this review grants no arm acceptance, preregistration approval, seal or experiment authorization.

## Exact tested identity

Historical source commit: `4001fc9d8ea2c932042de7823713c6efce8e56d0`.

| File | SHA256 |
|---|---|
| `replay_objectives.py` actually executed | `3f87cc5c8a573fae578f9cba9741d04b66142d481017677028403effc8a8b74b` |
| `source/itq_feasibility_synthetic.py` | `18ddc99dfe57e93f949ea55b2e1c9cae402c9204d1db99bb82d0a2014a30973d` |
| `source/PLAN.json` | `e56ea0d6858e06211fa9eb82d6d255724a3d0e23016b77d28f8d8ff10923c53f` |
| `source/RESULTS.json` | `0c2cf96553dbf448d22def0538c8993ada038d1fdac52665f759c08e5a304214` |

I compared all three source files directly against raw `git cat-file blob` bytes at that commit: producer under `research/v52/preseal_diagnostics_2026_09_12/`, PLAN and RESULTS under its `task3/`. All matched exactly. Source/plan cross-links passed. Before/after hashes confirm the replay script, pinned inputs and all four parent replay outputs remained unchanged.

## Executed validation

From the designated replay worktree, I ran:

```powershell
& 'C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\.venvs\g3-lock-20260912\Scripts\python.exe' -B 'research\v52\itq_haar_objective_comparison_2026_09_12\replay_objectives.py' --output review_agent
```

The output directory was absent beforehand. Exit code was 0. Observed Python 3.13.15, NumPy 2.3.5, SciPy 1.17.0; both recorded OpenBLAS pools used one thread. Static review confirmed the source producer is hashed, not imported or executed; there is no ITQ optimization call. Synthetic generation, centering, variance scaling and QR sign correction agree with the pinned producer. The replay expression `(abs(t)-1)^2` equals the producer's squared residual from its sign code, including at zero.

- All 480 initial/null objective values matched their stored scalars exactly: 12 panels, 20 initialization rotations and 20 separate null rotations per panel. All 12 regenerated data identities, initialization identities, 20 null rotation identities and the rotated-heterogeneity orientation identity passed the script's raw-byte checks.
- Zero, binary, scalar-oracle, signed-permutation and wrong-sign-negative objective controls passed.
- A separate review-side validator checked all 480 unique expected CSV keys, 24 groups of exactly 20 rows, finite values, exact-match flags and direct equality to historical per-seed records. It independently checked every exported summary statistic for all three objective families in all 12 panels, plus every reduction and range-comparison field.
- Review and parent `RESULTS.json` are byte-identical: SHA256 `f0ac1ef0dab530fe44c15ffbe7025f1fc8d1a66c3fe71a5fb6555a60feda50ca`. Their `objectives.csv` files are byte-identical: SHA256 `e98ce727da8ef93ab25aa66996967c3a5bb29fa6f2277f3935f8b4a76f504b44`. ENVIRONMENT matches; PLAN differs only in `created_utc`.

Detailed validation record and output identities: `review_agent/VALIDATION.json`.

## Historical values, interpretation and limits

The 240 final ITQ objectives were read from pinned historical RESULTS and summarized; **zero new ITQ fits occurred**. PLAN explicitly says not refitted, RESULTS uses `historical_itq_fitted` and `new_itq_fits: 0`, and README_TR labels the table historical and explains the distinction. Their provenance and arithmetic are verified here; final fitted matrices, optimization traces and final objectives were not independently regenerated. The terminal's abbreviated `ITQ=` label needs the accompanying historical context and should not be reused alone as evidence of a new fit.

For heterogeneous n=500, the verified Haar-null mean is 0.4089874653954597; the historical final mean is 0.266277022388954. The comparison is descriptive training quantization error. Shared seeds and one realization per n do not establish sampling generalization, equivalence, a theorem, a unique mechanism, retrieval benefit or arm inclusion. The replay records environment versions rather than enforcing a version lock itself; this review used and verified the requested locked interpreter, so exact reproducibility elsewhere is not established.

I read README_TR.md and CONFIGURATION_PROPOSAL.md. `RABITQ32_PLAIN` → `RQ32_PLAIN_NO_ROTATION` and `RABITQ32_ROTATED` → `RQ32_RANDOM_ROTATION_WRAPPER` remain **proposed, unapproved names/configurations**. No new RaBitQ serialization or theorem audit was performed in this task.

Read-only `git ls-remote --heads origin` confirmed legacy `refs/heads/fix/g3-membership-remediation-2026-09-11` at `077474013d95d6f343d31385d8a57d42fb72f721` and replacement `refs/heads/codex/g3-remediation-delivery-2026-09-12` at `7266160ac03bdd064fe75f058eae3430fbe14496`. Legacy deprecation concerns the delivery route only. Replacement acceptance under L-094 is user-supplied context also stated in the parent README; I did not re-audit that ledger entry.

No corpus/query/gold, real representation or outcome files were opened; no real experiment, ITQ fit, branch deletion, commit or push was performed. The original worktree was not modified. Review writes are confined to `review_agent/`, this review and `LEDGER_RECEIPT_BODY.txt`. This is a pre-landing review of exact bytes, not a receipt for a future published commit or manifest.
