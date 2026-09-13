# Muse session — RACE-3: FAISS-ARM race runner (RaBitQ32 + PQ), build + smoke

You are implementing the race runner for the FAISS arms (RaBitQ32 primary/secondary; PQ plain),
per the v2 prereg draft. Read-only /mnt/c; write ONLY /tmp/rb3/. No network. Use the WSL
faiss-python env (faiss 1.15.0; confirm import + version first; record python/numpy/faiss/BLAS
versions for the manifest).

## Spec (read DRAFT_PREREG_TWELVE_BYTE_RACE_v2.md §3/§5/§6 first)

Data: same frozen pkls (LME: regen/lme/cache_repr/*.pkl C(N,96), qC(96), gold; LoCoMo:
regen/locomo/*.pkl + audit corrections; valid 1535; same tie priorities/trials/K/FR rules as
pilots; anchors 0.5419751773049645 / 0.23654714666441054 ≤1e-12 abort — implement the sign-arm
native eval inside THIS runner too as the anchor check).

Arms:
- A4 RaBitQ32 PRIMARY: spread-32 axes (per-archive variance rank-linspace; same construction as
  RACE-2), rotation panel = 3 seeds [94101,94102,94103]; freeze the exact faiss call sequence
  (constructor + transform + query path) as constants; ALSO random-32 secondary axes variant
  (seeds [94201,94202,94203]) — report both; measure bytes.
- A5 RaBitQ32 + rotation-wrapper naming: implement per the pinned faiss semantics; if it is a
  no-op/variant, DOCUMENT what the wrapper actually does (acceptance criterion, S7-style log).
- A6 PQ m=12×8bit plain, archive-local; NO OPQ. Mask policy: if train fails for an archive →
  mask that archive (count + FR-over-available reported), never substitute; measure LoCoMo min-N.
- Scoring: codec-native distances; top-3 via lexsort((distance, trial_priority)) using the frozen
  20 draws; tie := exact float equality; per-question FR persisted (tol nothing — floats stored).
- Byte accounting: per-arm declared vs measured serialized bytes; shared-state bytes (rotation,
  PQ codebooks ≈98,304 B/archive) recorded; asserts: reproduce the pre-seal probe numbers
  RQ96=20B, RQ32=12B, IndexPQ(96,12,8)=12B, extended-2bit=44B (S2); `code_size`-vs-serialization
  disagreement = abort; document IndexRaBitQ lacking `nb_bits` (S3 trap negative control).
- Determinism (S5): retrain/rerun with fixed seeds/threads → bit-identical codes + FR; if PQ
  training is nondeterministic under the pinned API, find and fix (fixed clustering seed) or
  document + policy.
- Smokes: S2, S3, S4 (PQ min-N per benchmark incl. LoCoMo measurement), S5, S7 (rotation chain
  acceptance criterion executed + logged), S1-equivalent (anchors in-runner).
- Evaluate on BOTH benchmarks; per-arm per-rotation/seed records; W/T/L vs SIGN native.
- Runtime watch: PQ trains per archive (LME 470 × ~small; threads=1). If total > ~40 min, batch
  and checkpoint; report timing.

## Outputs

/tmp/rb3/race_faiss.py (constants block), race_faiss_details.json (per-q FRs, bytes, smokes,
per-seed records, mask stats), smoke_log.txt, environment.txt (versions), hash manifest.
Print RB3_VERDICT: <byte asserts; LoCoMo min-N + mask stats; determinism; per-arm aggregates;
rotation-chain finding>. ~2-3 hours.
