[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# COST_MODEL.md — honest total storage accounting (PREPARED, NOT ACCEPTED)

Status: this artifact is PREPARED, NOT ACCEPTED. It cannot seal, ratify, or
close anything. Assertion labels: VERIFIED = I ran/read the bytes;
CLAIM = a cited document says it; RELAYED = second-hand. Task4F1 SEAL obeyed:
no retrieval outcomes, no corpora/queries/labels/embeddings touched.

## 1. The model

For one archive holding N vectors under archive-local fitting:

```text
total(N)     = S + m * N          # bytes persisted for the archive
effective(N) = m + S / N          # bytes per vector, all-in
```

- `m` = marginal per-vector bytes: everything written once per stored memory
  (code bits, norms/scales, per-vector metadata). For SIGN96, m = 12.
  VERIFIED: `origin/evidence/twelve-byte-cost-2026-09-11`
  (`8217704`):evidence/twelve_byte_cost_2026_09_11/EVIDENCE.json,
  `serialization_S_of_N.SIGN96_BinaryFlat.marginal_bytes_per_vector` = 12.0
  (slope over N = 0..10000, residual ~8e-12), exactly reproduced in
  `origin/codex/twelve-byte-runtime-replay-2026-09-12`
  (`9cd3f54`):evidence/runtime_replay_2026_09_12/REPLAY.json.
- `S` = shared per-archive state: every persisted object needed to encode
  queries and decode vectors that is NOT per-vector (vocabularies, IDF tables,
  SVD components, centering vector, codebooks, rotations, serializers' headers).
- Break-even against storing raw baseline vectors at B bytes each (no shared
  state): `N* = S / (B - m)`. Below N*, the "compressed" scheme stores MORE
  bytes than the raw baseline; above it, fewer.
- Marginal-parity point `Np = S / m`: the N at which the shared component alone
  costs m bytes/vector (effective = 2m). This is what PROJECTOR_BYTES.json calls
  `breakeven.to_12` — it is NOT a beats-float break-even (see §4).

## 2. Inputs (every number carries a locator)

| Symbol | Value | Locator |
|---|---|---|
| m (SIGN96) | 12 B/vec | EVIDENCE.json `serialization_S_of_N` (VERIFIED, §1) |
| S med, float32+struct vocab (a_raw) | 44,220,235 B | PROJECTOR_BYTES.json `aggregate.totals.a_raw_f32_struct.median` (VERIFIED — read via git show) |
| S med, float16+struct vocab (b_raw) | 22,686,111 B | same JSON `aggregate.totals.b_raw_f16_struct.median` (VERIFIED) |
| S med, zlib float32 (a_zlib) | 23,733,327 B | same JSON `aggregate.totals.a_zlib.median` (VERIFIED) |
| S med, zlib float16 (b_zlib) | 16,941,200 B | same JSON `aggregate.totals.b_zlib.median` (VERIFIED) |
| Cited median effective (a_raw) | 88,886.362… B/vec | same JSON `aggregate.ratios_median.a_raw.effective` (VERIFIED; equals 12 + 88,874.362…, rechecked in verify_cost.py) |
| S range over 15 archives | 41,785,637 – 46,272,067 B | same JSON `aggregate.totals.a_raw_f32_struct.min/max` (VERIFIED) |
| LongMemEval N | min 396, max 616, mean 492.77872340425535; 470 archives; 231,606 vectors total | EVIDENCE.json `archive_cost` (VERIFIED; 470 × mean = 231,606.0 exactly, recomputed) |
| LoCoMo per-archive N | UNAVAILABLE-UNDER-SCOPE (only question counts 1535 corrected / 1540 raw are declared in the prereg revision §2; no per-archive vector counts in any cited source) | — |
| BEAM tiers | 100K / 500K / 1M / 10M DECLARED SIZES ONLY | old prereg `d2cfbaa`:docs/v52/V52_TWELVE_BYTE_BASELINE_PREREG_2026-09-09.md lines ~41–42: these tiers are named as scale explicitly NOT approached (VERIFIED) |
| B float32 (96-D) | 384 B/vec = 96 × 4 | arithmetic identity; 384 B FLOAT96 reference bound in prereg revision §3 arm table (VERIFIED present) |
| B float16 (96-D) | 192 B/vec = 96 × 2 | arithmetic identity |
| B float16+zlib | UNAVAILABLE — no cited source stores zlib-compressed raw float vectors | needed: zlib bytes of 96-D float16 archive vectors on programme archives |
| Index-only S0 (faiss, CITED CONSTANTS) | SIGN96 33 B; PQ96 98,390 B; OPQ 135,325 B | EVIDENCE.json `serialization_S_of_N.*.shared_bytes` + `serialized_versus_analytic` (VERIFIED; replay-equal) |
| Projector composition (median archive) | s96.components_ 85.1%, sv.components_ 11.4%, vocabs 2.6%, IDFs 0.9%, mu ~0% | PROJECTOR_REPORT_TR.md Results note (CLAIM — I did not re-derive the shares; the byte totals they sum to are VERIFIED) |
| Inventory completeness | 7 items, nothing missing or extra; `TruncatedSVD.transform` uses only `components_` (no mean/offset) | AUDIT_MEASUREMENTS_TR.md §Projector (CLAIM — independent audit, verdict PASS WITH OBSERVATIONS; I verified the two byte totals it re-derived, not its sklearn-source reading) |

What S contains (VERIFIED from PROJECTOR_BYTES.json `config` +
`unavoidable_vs_choices`): per-archive word vocab + IDF, char vocab + IDF,
`sv.components_` (32 × word-columns), `s96.components_` (96 × combined-columns),
`mu` (96). Deliberately excluded with reasons: `singular_values_` etc.
(transform never reads them), stop-word list (code constant), ITQ/random
projections (absent from the local SIGN96 query path), priority (regenerated).
These exclusions are CLAIM (pilot + audit); the audit re-derived the inventory
from the query path and the sklearn source and found it complete (CLAIM).

What S is NOT (pilot's own declared re-fit notice, VERIFIED present in JSON
`_refit_notice`): this is a declared re-fit of the representation pipeline on
the real corpus, NOT a recovery of the frozen production artifact, whose
physical serialization was never found. So S is the size of a faithful
re-fit, with the audit's P1 caveat that the gate proves shape, not pipeline
identity (AUDIT_MEASUREMENTS_TR.md F-01; CLAIM).

## 3. Instantiation at programme archive sizes

Effective bytes/vector = 12 + S/N (recomputed by verify_cost.py; see
evidence/cost_results.json):

| N (vectors/archive) | a_raw f32 | b_raw f16 | a_zlib f32 | b_zlib f16 | raw f32 baseline |
|---|---|---|---|---|---|
| 396 (programme min) | 111,679 | 57,300 | 59,945 | 42,793 | 384 |
| 492.78 (programme mean) | 89,748 | 46,049 | 48,174 | 34,391 | 384 |
| 616 (programme max) | 71,798 | 36,840 | 38,540 | 27,514 | 384 |
| 100K (BEAM tier, declared only) | 454.2 | — | — | — | 384 |
| 500K (BEAM tier, declared only) | 100.4 | — | — | — | 384 |
| 1M (BEAM tier, declared only) | 56.2 | — | — | — | 384 |
| 10M (BEAM tier, declared only) | 16.4 | — | — | — | 384 |

BEAM rows are ceteris-paribus projections reusing the LongMemEval median S;
a BEAM-fit projector would have its own S (vocab and component matrices scale
with corpus vocabulary, sublinearly). They are NOT measurements (CLAIM-scope
warning; the tiers themselves are VERIFIED as declared-only).

Whole-LongMemEval totals (shared ≈ 470 × median S — approximation, flagged in
cost_results.json; codes and raw totals exact):
SIGN96 total ≈ 20,786,289,722 B (~20.8 GB: ~20,783.5 MB shared + ~2.8 MB codes)
vs raw float32 total = 88,936,704 B (~88.9 MB). Ratio ≈ 233.7×. The codes — the
entire content of the "twelve-byte race" — are ~0.013% of the SIGN96-side bytes.

## 4. Break-evens (all recomputed; see cost_results.json `breakeven_N`)

| Projector encoding | N* vs float32 (384) | N* vs float16 (192) | N* vs float16+zlib | Np = S/12 ("to_12") |
|---|---|---|---|---|
| a_raw f32 (S=44.22M) | 118,872 | 245,668 | UNAVAILABLE baseline | 3,685,020 |
| b_raw f16 (S=22.69M) | 60,984 | 126,034 | UNAVAILABLE baseline | 1,890,510 |
| a_zlib f32 (S=23.73M) | 63,799 | 131,852 | UNAVAILABLE baseline | 1,977,778 |
| b_zlib f16 (S=16.94M) | 45,541 | 94,118 | UNAVAILABLE baseline | 1,411,767 |

Reading guide. The task brief's "~3.7M break-even" is the LAST column: the N at
which the shared component amortizes to 12 B/vector (effective = 24 B). It is a
marginal-parity figure, not a victory over floats. Victory over raw float32
needs only N* = 118,872 for the float32 projector — but programme archives hold
~500 vectors, a factor ~240 short of it. The 100K BEAM tier (declared size)
sits just BELOW the float32 break-even (454 > 384); the 500K tier sits above
(100 < 384) under the ceteris-paribus-S assumption.

## 5. Sensitivity (recomputed; see cost_results.json `sensitivity`)

- Projector in float16 instead of float32: S halves (22.69M), N* vs float32
  halves to 60,984 — still ~124× the mean programme archive. At mean N the
  effective cost is 46,049 B/vec (120× raw float32). Halving precision does not
  change the qualitative conclusion; retrieval effect of fp16 is separately
  UNMEASURED (pilot `not_checked`, VERIFIED present).
- Projector shared across archives instead of per-archive: one 44.22M projector
  amortized over all 231,606 LongMemEval vectors gives 202.9 B/vec — BEATS raw
  float32 (384). This is the assumption most damaging to the headline, and it
  is exactly the deployment the preregistration EXCLUDES ("Archive-local state
  is fitted and charged to each archive separately… Never amortize state over
  all benchmark questions" — prereg revision §2, VERIFIED). The headline
  survives only where the prereg forbids going; see RECONCILIATION.md.
- Archives 10× larger (N ≈ 4,928): effective f32 = 8,986 B/vec — still 23× raw
  float32. Even an order of magnitude of archive growth does not close the gap.
- Index-only arm comparison at mean N (faiss CITED CONSTANTS, common
  preprocessing excluded from ALL arms equally): SIGN96 12.067, PQ96 211.664,
  OPQ 286.616 B/vec. The arm RANKING under index-only accounting is unchanged
  by this pilot: SIGN96's index shared state (33 B) is ~3,000× smaller than
  PQ's (98,390 B). The pilot's 44 MB is COMMON preprocessing, charged to every
  arm equally — it moves absolute framing, not relative standing.
