# REPORT — 07_kv_inverse: KV continuation and inverse-memory audit

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Independent hard review round 2. Neutral: neither STOP nor CONTINUE is the aim.
Prior worker/coordinator reports were treated as fallible claims and re-checked
from source. Coverage: **35 items — 26 reviewed, 3 sampled, 6 NOT RUN**
(mechanically counted from [COVERAGE.csv](/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/07_kv_inverse/COVERAGE.csv)).
Nothing not run is presented as a pass.

## Outcome

Both lines were previously unreviewed (audit_hard_r1 names KV/inverse NOT
REVIEWED) and both original runs contained one decisive measurement bug each,
both already found before this audit — one by the coordinator (JVP), one by a
repair worker (NLL alignment). This audit **verifies the repairs
mechanically from the raw rows** and adds two new scoped caveats of its own:

1. The repaired "KV-only" inverse continuation is a full-sequence logits
   recompute, **not** stepwise `DynamicCache` integration, and its
   generic-4bit comparator quantizes all 24 positions while ledger arms patch
   only the 16 prefix positions — the ledger-vs-generic4bit comparison is
   unmatched (withhold comparative claims).
2. Genuine `DynamicCache` consumption (install + stepwise + poison gate) is
   proven **only** in the KV-predictor line, not for the inverse ledger.

No resident memory savings are demonstrated anywhere; both lines disclose this
honestly and the byte arithmetic checks out exactly.

## Verified findings (severity, location, test, result, interpretation, limits)

### F1 — KV original ΔNLL invalid; repaired carryover proof VERIFIED (High, resolved)
- Location: `parallel_ideas_r1/kv/run.py:409-436` (`true = c["cont"][t]`
  scored against logits emitted *after* consuming `cont[t]`);
  repair `parallel_ideas_r1/kv_repair/REPORT.md`, `ERRATA.md`.
- Test performed: independent re-join of both `per_case.jsonl` files on
  `(text_id, ctx, arm, step)` ([scripts/verify_jsons.py](/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/07_kv_inverse/scripts/verify_jsons.py)).
- Observed: 320/320 rows each, unique keys, repair all `align=shifted-v2`;
  256/256 non-full ΔNLL changed (max abs shift **24.875**); original means
  all negative (e.g. ridge ctx64 −3.30) vs repaired all ≥ ~0 (ridge ctx64
  +0.57); **max|KL_old − KL_new| = 0.0 (256/256 exact), top-1 mismatches 0**.
- Interpretation: withdrawal of every original ΔNLL number is justified; KL /
  top-1 carryover is proven, not asserted. Ridge still beats zero ≪ copy on KL
  every case; q4 still beats ridge.
- Limits: acceptance tests A1/A2/A3 read, not re-executed (model load exceeds
  the 180 s probe budget). One prose slip ("0.24") corrected to 0.30–0.48
  against the rows — confirmed from the rows here.

### F2 — Inverse JVP counted identity twice; repaired 0/12 is now honest (High, resolved)
- Location: `parallel_ideas_r1/inverse/inverse_lib.py:160-178`
  (`out = v + jv` where `fn` returns full `B(x)`, so `jv` already is `JB*v`);
  same defect in segment `op` (`run.py:265` per ERRATA — sampled, line not
  opened directly); fix `inverse_repair/inverse_lib_fixed.py:161-185`
  (`out = jv`).
- Test performed: synthetic fixture with `torch.autograd.functional.jvp` on
  `B(x)=x` and affine `B(x)=Ax+b`
  ([scripts/verify_operators.py](/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/07_kv_inverse/scripts/verify_operators.py), no model).
- Observed: identity gives `jv=[3,4,5]`, original formula `[6,8,10]` — exactly
  the coordinator's `[6,8]` probe; affine `jv == A@v` exactly, original adds
  a spurious `+v`.
- Interpretation: the original "Newton beats fixed-point yet fails" inference
  was correctly withdrawn; the repaired 0/12 + 0/4 under 8-outer/20-inner is
  an honest test of the intended method. L14 is closest (res
  6.8e-4–3.3e-3) but still ~70–300× above the 1e-5 gate with GMRES saturated
  at 20/20 every outer.
- Limits: "0/12" means "not under this budget from x0=y", not
  noninvertibility; the 40×100 probe was explicitly not run (NOT RUN N03).

### F3 — `inner_ok` never meant convergence (Medium, resolved)
- Location: `inverse_lib.py:181-235` (4th GMRES return is `isfinite(relres)`).
- Test: synthetic 1-iteration 5×5 probe → finite flag true with relres 0.46
  ≫ 1e-5, demonstrating the mislabel class.
- Interpretation: original `inner_ok:true` + `failed-residual` is consistent
  with saturated inner loops; repair's separate `inner_converged_all` (all
  False) is the correct instrument. Limits: repair GMRES code read, not
  re-executed.

### F4 — Original "continuation" was hidden-state injection, not KV-only (Medium, resolved with new caveat)
- Location: `inverse_lib.py:439-478` (`continuation_scores` replaces the full
  hidden state at L14 over the whole sequence, recomputes downstream).
- Test: code read + direction check (`kl = PATCH||FULL`), repair
  `kv_continuation.py:45-73` read (Q true, K/V per-arm, residual true) +
  row verification (4/4 `cache_parity_trueKV_vs_full` bit-exact 0.0).
- **New caveat (this audit):** `kv_continuation.py:143-191` — ledger,
  no-ledger and direct-4bit arms patch only the first 16 positions
  (`src_for`), while the generic-4bit arm quantizes K/V over all 24
  positions. Ledger-vs-generic4bit KL is therefore **not a matched
  intervention**; withhold that comparative claim (coordinator closeout
  concurs). The ledger-vs-noledger and parity results are unaffected.
- Limits: NLL-shift cross-check (0.0) read from repair report, not recomputed.

### F5 — "Cache" wording overreaches for the inverse ledger (Medium, open)
- `kv_continuation.py` recomputes logits with a full-sequence forward with
  patched K/V — no stepwise `DynamicCache` stepping exists in that file.
  Its "poison" check is a ledger-vs-noledger omission ablation, not an
  installer-ignore negative control. Real cache consumption (expanded
  full-float `DynamicCache` install via `install_prefix`/`clone_cache_state`
  + stepwise `step_with_cache` + poisoned-vs-unpoisoned gate 8/8) is proven
  **only** in the KV-predictor line (`kv/run.py:140-175,270-320`,
  `kv_repair/run.py:558-572`, code-read; re-execution NOT RUN).
- Consequence: distinguish KV injection (KV line: yes; inverse ledger: not
  demonstrated) from hidden-state continuation (original inverse: yes,
  honestly relabeled).

### F6 — Storage: backing bytes honest, no resident win anywhere (Low, verified)
- KV: predictor 90·(4096+64)·4 = **1,497,600 B** (asserted in code, recomputed
  here), crossover **65.0 tokens** as the *equality* point (strict savings
  need N > 65); runtime caches are expanded full-float; `predictor.pt`
  on disk 1,548,427 B (container overhead disclosed); q4 payload 115,200 B
  backing vs 165,863 B file.
- Ledger: 4,736 B/layer/T16 vs FP32 K+V 24,576 B; same-dtype FP32 total
  695,040 vs 737,280 B (headroom, no win claimed); hypothetical BF16 KV
  368,640 B vs BF16-anchors + FP32-metadata ledger 418,560 B (exceeds —
  the original mixed-dtype comparison was correctly withdrawn).
- Generic 4-bit KV is the stronger comparator in **both** lines
  (KV: KL 0.02 vs ridge 0.30–0.48; ledger scope caveat F4 notwithstanding).
- Limits: RSS figures (~1.2 GB working set) accepted as disclosed, not
  re-measured.

### F7 — Timing equivalence honest but thin (Low)
- Original full-forward-vs-stepwise pair correctly marked NON-COMPARABLE
  (batching/work differ); matched stepwise pair (cached 0.49 s vs
  prefix-recompute 1.15 s) is exploratory, shared-CPU, single case.
  No speedup claim stands. NOT re-executed.

### F8 — GQA/layer anchors verified (Info)
- `parallel_ideas_r1/model/config.json`: 30 layers, 9 Q / 3 KV heads,
  d=576, head_dim=64 → width **192**, native **bfloat16**; executed FP32
  separation is explicit in protocol and code (`get_model`, runtime
  post-RoPE check `check_rope_convention`). No anomaly.

### F9 — Chat-literature toy results do not transfer (Info)
- `chat_literature_review_20260915/inverse/REPORT.md` (read-only; CSVs not
  re-parsed — NOT RUN N06): 4-bit ledger ≈1e-6 toy KV error and Newton
  step-reduction hold only on random-init full-MHA toys (dim ≤ 96, ≤ 24
  tokens) with dense Jacobians and no decode metric. The pretrained-line
  results (ledger works layer-locally at L14 only: recon ~1.8e-3 vs L0 ~6
  and L29 ~0.3; inversion fails under budget) are consistent with — and
  properly bounded by — those toy limits. No compression claim is supported
  from the toys.

### F10 — Provenance hygiene good, minor gaps retained (Low)
- Originals untouched: KV 12-file SHA before==after; inverse
  `hash_proof.json: unchanged=true`; model safetensors `80521b40…` matches
  manifest. Retained gaps (all disclosed): repair `summary.json::agg_D2`
  uninformative (key bug inherited); segment `x_hat` unsaved → no independent
  segment residual replay (report at most 12/12 single-block, never 16/16).

## What was NOT reviewed / outside this role's scope

- Whole-project areas outside role 07 (metrics, ITQ, geometry, retrieval,
  F1, dense/residual, storage contracts, portability, governance) — see other
  roles' reports; this report covers only KV continuation + inverse-memory.
- Model-loaded re-execution of any `run.py`/`tests.py` incl. acceptance
  RED→GREEN suites and timing (NOT RUN N01/N02: each needs a local
  SmolLM2-135M load, exceeding the ≤180 s single-probe rule).
- BF16 numerics, open-ended generation (all continuation is teacher-forced),
  natural non-repeating long contexts (the named next test), entropy coding
  of ledger codes, GPU decode latency.
- The still-running broad substring grep over the published pilot tree was
  superseded by a precise grep (one passing KV-cache mention; no KV/inverse
  experiment in the pilot). Git pickaxe (`-S make_jvp_op|kv_continuation|
  predict_odd`) over the main repo object store: 0 hits — the work is
  local-research-only, never merged.

## Method note

`compute.sh` could not be used: `flock` failed to create its lock file
(Read-only file system). Both probe scripts are light (small-JSON reads +
  tiny CPU torch ops, no model load), so they were run directly with
  single-thread BLAS env. No downloads, no paid APIs, no source writes outside
  this directory.

## Deliverables in this directory

- `REPORT.md` (this file), `STATUS.md`, `COVERAGE.csv` (35 items),
  `evidence/verify_jsons.json` + `evidence/verify_operators.json`,
  `scripts/verify_jsons.py` + `scripts/verify_operators.py`,
  `outputs/` (run artifacts), `originals/` (read-only copies).
