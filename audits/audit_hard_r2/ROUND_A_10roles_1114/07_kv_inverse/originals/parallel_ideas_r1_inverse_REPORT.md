# REPORT — Tasks C (ledger + checkpoints) and D (matrix-free inverter)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Pretrained SmolLM2-135M (rev 93efa2f0, FP32 executed / BF16 native), author-written
feasibility fixtures (NOT a benchmark), single-thread CPU, peak RSS 1310 MB (< 3 GB budget).

## Statuses (separate)

- **Task D (bounded matrix-free inverter): TESTED — 0/12 single-block + 0/4 segment successes.**
  All cases ran inside budget; failures retained, none hidden. The 8-correction bound is
  infeasible for exact block inversion on this model.
- **Task C (ledger + checkpoints): TESTED (math + storage + continuation all executed).**
  4-bit packed ledger decodes and beats no-ledger everywhere; L14 continuation quality ≈ full
  cache. Full-cache deployment budget fails (see accounting); bounded single-layer probe
  reported separately below — deployability gate NOT bypassed.

## D results (thresholds: fwd-res ≤1e-5 AND recon ≤1e-3; flags derived, never hardcoded)

| case | direct | D2 fixed-pt (8 eval) | D3 Newton-GMRES (8 outer, ≤20 inner) |
|---|---|---|---|
| L0 ×4 | ~3.4 ms | res 0.55–1.2, recon ~20 (DIVERGES) ~0.03 s | res ~2.4e-2, recon ~19, ~143 JVP, ~1.8 s |
| L14 ×4 | ~3.6 ms | res 7–10e-2, recon 4–7e-2, ~0.03 s | res 1–4e-2, recon 1–12e-2, ~167 JVP, ~2.0 s |
| L29 ×4 | ~3.6 ms | res 0.3–0.5, recon ~1.5, ~0.03 s | res 0.2–1.2, recon 1.3–2.0, ~163 JVP, ~2.0 s |
| seg 14–15, T=64 ×4 | ~18 ms | res ~0.37, recon ~0.25 | res 3–7e-2, recon 3–8e-2, ~175 JVP, GMRES saturates at 20/20 |

Newton-GMRES beats fixed-point on L0/L14 (fewer outer illusions aside, ~150 operator
applications vs 8) yet stays >1000× above the residual threshold while costing ~500× a
direct forward (~2 s vs ~3.5 ms). A JVP is an operator application, not a solve: fewer
outer steps ≠ less work. Plain prefix replay = one block forward (~3.5 ms, bit-exact).

## C results

- Recon rel-error (median over all 12 layer×text cases): no-ledger C1 0.89, ledger C3
  0.33, direct-4bit-input C2 0.39 (median mixes regimes — per-layer below is the honest
  cut); generic 4-bit KV C5: K ~0.18 / V ~0.13 (NOT KIVI). Per layer: L14 C3 ~1.8e-3
  (good), L29 C3 ~0.3, L0 C3 ~5.8 (layer-0 residual norm ~19× input norm — nothing cheap
  recovers it; C1 there = 19).
- Real attention continuation (L14, teacher-forced 8 tokens, reconstructed K/V, mean over
  4 texts): C3 ΔNLL ≈ −0.006, KL ≈ 0.002, top-1 agree 1.00; C1 KL ≈ 0.02, agree 0.63–1.0;
  C2 KL ≈ 4.8, agree ≈ 0.06 (destroyed). No fake zero-loss: C2/C1 reported as measured.
- Mutations: M1 omission ⇒ bit-exact C1 (True ×12); M2 nibble flip ⇒ reconstruction changes
  (maxabs 4.4–3000, larger at L29 where per-token scales are wide) — payload is live, not
  passthrough. Counterfactual arrays in per_case.jsonl + `*.npz` allow independent re-decode.
- Segment (14–15, T=64): ledger recon ~7e-3 at 18 944 measured bytes/segment.

## Budget (measured vs hypothetical, FP32 vs BF16 kept separate)

Measured per 16-token case/layer: ledger packed 4608 B + FP32 scales/mins 128 B = 4736 B;
full FP32 K+V = 24 576 B; anchors every 2 layers = 15 × 36 864 B = 552 960 B total.
Hypothetical (NOT measured): BF16 K+V = 12 288 B/layer; ideal formula 16d+30·4d bits/token.
Ledger+anchors exceed the BF16 KV baseline once anchors are amortized over short segments —
full-cache deployment gate FAILS on storage; the single-layer math probe above stands alone.

## Limitations & next test

Exploratory pilot: 4 short authored texts, 3 layers, teacher-forced (not open generation),
timing on shared CPU, FP32 only. Layer-29 harness trap found and fixed (post-norm state is
not a block output; hook truth now, parity bit-exact 12/12). **Next smallest discriminating
test:** L14 Newton-GMRES with 40 outer × 100 inner (one text) to test whether failure is
budget or basin; if res stalls ~1e-2 again, close the inversion line and pursue partial-KV
reconstruction (EchoKV-style) instead.

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$HOME/muse-work/fpylibs:$HOME/muse-work/mlpy OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 run.py`
then `python3 tests.py`. Files: PROTOCOL.md + protocol.sha256 (frozen pre-outcome),
inverse_lib.py, run.py, tests.py, test_log.txt (red→green), per_case.jsonl (20 rows),
continuation.json, segment.json, summary.json, source_hashes.json, progress.json, *.npz.
