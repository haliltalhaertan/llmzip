# MODEL PROVENANCE & QUANTIZATION AUDIT (Round 3, role D)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Scope (read-only): `top10_comparison_r1/model/` (configuration.py, modeling.py,
st_quantize.py, tokenizer.json, vocab.json, + siblings), `download_model.py`,
`official_st_quantize.py`, `MODEL_SOURCE.json`, `MODEL_README.md`,
`weight_headers.txt`, root `*.log`/`*.txt`, `semantic/`, `coordinator/encode_fast.py`,
and `LLMZIP_TWELVE_BYTE_PILOT_2026-09-16.zip` (at `/mnt/c/Users/MDP/dev/llmzip-work/`).
All probes used `PYTHONDONTWRITEBYTECODE=1`; no source-tree writes were made
(`semantic/__pycache__` mtimes still 2026-09-15 16:19). No internet used.

## (1) VERDICT

No published number is wrong because of model provenance or quantization code:
the vendored quantizer is byte-identical to the official copy, all 14 pinned
files hash-verify, and — decisively — no published Top10-r1 number uses the PPLX
model at all (its encoding never finished). Gaps are reproducibility-only (MED):
the publication zip cannot regenerate the PRIMARY semantic endpoint without a
2.4 GB re-download plus a multi-hour CPU re-encode.

## (2) Findings table

| ID | Severity | Claim / file audited | What was actually run | Result |
|----|----------|----------------------|-----------------------|--------|
| MP-01 | LOW (pass) | Model identity + provenance consistency (MODEL_SOURCE.json, MODEL_DOWNLOAD.json, weight_headers.txt, model/*) | sha256 re-hash of all 14 on-disk files vs MODEL_DOWNLOAD.json; safetensors header parse; README/headers cross-check | All 14 OK; model is perplexity-ai/pplx-embed-v1-0.6b @ 2c4d510d; header (310 F32 tensors, embed [151936,1024]) matches config.json |
| MP-02 | LOW (pass) | model/st_quantize.py vs official_st_quantize.py deviation | `diff` + sha256; torch numeric probe scorer-vs-official (int8/binary/packed/pool, 5x1024 random + near-zero case) | Byte-identical (diff exit 0); int8==hard-quant exact, binary/packed exact, near-zero counterexample confirmed; no numeric deviation |
| MP-03 | MED | "Which model do the numbers use?" — consistency of model use across experiments | grep for model refs in baseline/pq/data/semantic/coordinator; checked semantic outputs existence | NO published number touches model/: baseline/lexical/PQ use pre-existing caches+text; PPLX arm incomplete (no per_query/REPORT); reports correctly label PPLX NOT RUN |
| MP-04 | MED | Mid-project model/scorer change invalidating comparisons | Diffed current semantic/ vs coordinator/semantic_before_fidelity_fix/; mtime timeline; sampled old-vs-new numeric drift | No MODEL switch (single revision, all loaders local_files_only to same dir). Scorer DID change mid-flight (float64->FP32 torch + resume-bug fix) but contained: no archive payload completed under old code; sampled drift 0/20480 int8, pool <=1.2e-7 |
| MP-05 | MED | Reproducibility: published numbers depending on artifacts absent from the publication zip | Full namelist scan of LLMZIP_TWELVE_BYTE_PILOT_2026-09-16.zip (821 entries) | Zip has NO model/ weights/tokenizer and NO semantic payloads; PRIMARY PPLX endpoint not regenerable offline. No published number depends on a missing artifact (vacuous: PPLX numbers don't exist); baseline/PQ re-aggregable from zipped per-query files but source caches absent |
| MP-06 | LOW | Encoder cost accounting (progress.json weight_bytes) | Summed model/ bytes on disk vs reported 2400127479 | Reported value omits 1_Pooling/config.json (313 B); actual total 2400127792. Trivial, no conclusion affected |
| MP-07 | LOW | Orphan HF module cache dir (37bb1b653c423126, config only, no modeling.py) | diff of both cached configs vs model/configuration.py | Both identical to disk; harmless transformers AutoConfig-resolution artifact; full dir (f8498d62c9f3cb3a) also identical |

## (3) Per-finding detail

### MP-01 — provenance consistent (LOW/pass)

- Identity: `MODEL_SOURCE.json`: `id=perplexity-ai/pplx-embed-v1-0.6b`,
  `sha (revision)=2c4d510dd4a732063c31a0f70193e35067b51fd8`. `MODEL_DOWNLOAD.json`
  records the same model+revision with 14 file records (13 small + 2.38 GB weights).
- `download_model.py` derives its file list as siblings minus `onnx/`, `assets/`,
  dotfiles: 14 names, matching the 14 download records and the 14 files on disk.
- Re-hash probe (streamed 8 MB blocks) — all `OK SIZE_OK`:
  `1_Pooling/config.json a30548e8…`, `README.md a93b3965…`, `added_tokens.json c0284b58…`,
  `config.json f7865547…`, `configuration.py e914aa73…`, `merges.txt 8831e4f1…`,
  `model.safetensors 2c8d2f64…` (2,384,233,112 B), `modeling.py baf57b64…`,
  `modules.json 26a5eb7e…`, `special_tokens_map.json 3c624348…`,
  `st_quantize.py 320c54de…`, `tokenizer.json c6fb5c5b…`, `tokenizer_config.json 29282dae…`,
  `vocab.json ca10d7e9…`.
- Corroboration: root `MODEL_README.md` sha256 == `model/README.md` sha256
  (`a93b3965…`, `diff -q` exit 0). `weight_headers.txt` (HF redirect+object headers)
  shows `X-Repo-Commit: 2c4d510d…` (== pinned revision) and
  `X-Linked-ETag: "2c8d2f64…"` (== recorded safetensors sha256), `X-Linked-Size: 2384233112`.
- Safetensors header (first 8 LE bytes -> 33,424-byte JSON): 310 tensors, all `F32`;
  `embed_tokens.weight [151936, 1024]`; 28-layer shapes; `format: pt`. Matches
  `model/config.json` (`vocab_size 151936, hidden_size 1024, num_hidden_layers 28`,
  `model_type bidirectional_pplx_qwen3`).
- Tokenizer cross-check: `vocab.json` 151,643 entries + 26 added tokens (ids
  151643–151668) < `vocab_size` 151936 (padded, normal); `merges.txt` 151,387 rules;
  `1_Pooling/config.json` mean-only pooling (`pooling_mode_mean_tokens: true`, rest false);
  `modules.json` pipeline = Transformer -> Pooling -> `st_quantize.FlexibleQuantizer`.
- `modeling.py`: `PPLXQwen3Model(Qwen3Model)`, `post_init` sets `is_causal=False` on all
  layers (line 51), bidirectional mask via `create_causal_mask(... or_mask_function ...)`
  (lines 74–80) with version-tolerant signature probe (lines 12–20).
  `configuration.py` (4 lines) is a trivial `Qwen3Config` subclass.

### MP-02 — quantizer copy has zero deviation (LOW/pass)

- `diff model/st_quantize.py official_st_quantize.py` -> exit 0; both
  sha256 `320c54decc6a150bbfbef5eff4765291e66fb7506503ee65776809d99938faad` (3547 B).
  Key lines in both: `qmin/qmax` (41–42), `torch.round(soft * qmax)`+clamp (49–50),
  binary `torch.where(x >= 0, 1.0, -1.0)` (67), packed `np.where(x>=0)`+`packbits` (72–73).
- Torch probe (system python3, torch 2.14 CPU, `sentence_transformers` stubbed —
  package not installed, only its `Module` base was stubbed to import the file):
  on N(0,1) random 5x1024 f32, `pplx_scorer.official_int8` vs
  `Int8TanhQuantizer._hard_quantize` -> exact match (True); binary exact (True);
  packed exact (True, shape (5,128)); 1024-bit roundtrip True; masked-mean-pool vs
  manual mean max diff 5.96e-08 (FP32 rounding only).
- Near-zero semantics confirmed: x=-0.001 -> int8 `0` but binary `-1`, i.e. native BIN
  is sign of UNQUANTIZED pooled activations, not sign of INT8 (matches the test-suite
  fixture names `test_nearzero_counterexample`, `test_binary_uses_unquantized_sign`).
- Caveat (probe artifact, NOT a code deviation): comparing against the STE
  `forward()` float output with `.astype(np.int8)` truncation showed ~1.2% off-by-one
  (62/5120), because `hard.detach()+soft-soft.detach()` leaves ~1e-6 float residue
  (e.g. -15.999999). The project's save path (`encode_pplx.py` finalize + per-batch)
  uses `official_int8` (round-then-cast), which matches `_hard_quantize` exactly, so
  stored `int8` arrays are unaffected.

### MP-03 — no published number uses model/ (MED)

- `baseline/*.py` contains ZERO references to pplx/perplexity/AutoModel/safetensors;
  `baseline/REPORT.md` states cached FLOAT96 arms only, "no text/model inference",
  "PPLX/PCA/PQ model arms … labeled NOT RUN". Baseline reads
  `bench3/runs/b3b_perltqa/cache_*`, `regen/lme/cache_repr/*.pkl`,
  `bench3/runs/b3a_realtalk/rt_repr/RT*.pkl` (`run_top10.py` lines 44–49).
- `data/` (BM25/TFIDF) and `pq/` (Faiss PQ on cached FLOAT96) likewise never touch model/.
- Semantic PPLX side never finished: `semantic/progress.json` shows 120/9649 texts
  (RT01 docs partial); `progress_fast.json` (coordinator `encode_fast.py`, Sep 16) shows
  495 texts; `payloads/` holds ONLY `*_untrunc_len.npy` (+`tokenizer_stats.json`, all
  `trunc_gt1024: 0`); `checkpoints/` holds 15 RT01 shards (120 texts); and
  `per_query_pplx.jsonl` / `REPORT.md` / `SUMMARY.json` DO NOT EXIST in `semantic/`.
- Hence every published Top10-r1 number (baseline 9440, lexical 705, PQ 705) is
  PPLX-independent. Reports label this correctly, so nothing is wrong — but a reader
  equating baseline `sign96/float` arms with "the embedding model" would be mistaken:
  those are signs/cosines of OLD cached vectors, not of pplx-embed-v1-0.6b.

### MP-04 — scorer changed mid-flight, but contained (MED)

- No MODEL-weights switch: single revision `2c4d510d` in MODEL_SOURCE, MODEL_DOWNLOAD,
  download URLs, PROTOCOL.md line 8, and weight_headers; every loader
  (`semantic/encode_pplx.py:84-87`, `coordinator/encode_fast.py:55-57`,
  `diag_mask.py`, `diag_speed.py`) uses `local_files_only=True` against the same
  `ROOT/model` dir. Only other-model string in reports is declared NOT RUN
  ("8B Nemotron FP32", `baseline/REPORT.md:173`); remaining grep hits for `8b` are hex
  digests in `gates_top10.json` (false positives, verified by line inspection).
- The Python scorer/encoder DID change mid-project; a snapshot is preserved at
  `coordinator/semantic_before_fidelity_fix/` (16:17–16:20) vs current (16:26–16:27):
  (a) `official_int8` float64-numpy -> torch-FP32; (b) `masked_mean_pool` float64-numpy
  (zero-mask -> 0.0) -> torch-FP32 (`clamp(min=1e-9)` divisor); (c) resume
  `have[:]=True`-on-hash-match (old `encode_pplx.py:131-142`, the exact bug the
  coordinator notes flagged) -> fail-closed `load_checkpoint` (current).
- Containment: mtime order proves the 16:35–16:37 checkpoints + 16:37 progress.json
  were written by the CURRENT code; no per-archive payload (the only consumer of the
  resume path) was ever completed under either version; shard files are write-only
  (never read back by the encoder). Sampled drift old-vs-new on random data: int8
  0/20480 differ, pooling max abs diff 1.2e-07 — negligible, though LSB flips at exact
  .5 boundaries remain possible in principle (sampled only, not proven absent).

### MP-05 — publication-zip reproducibility gap (MED)

- Zip `/mnt/c/Users/MDP/dev/llmzip-work/LLMZIP_TWELVE_BYTE_PILOT_2026-09-16.zip`:
  821 entries, 47 MB uncompressed. Present: per-query files
  (`baseline/per_query_top10.jsonl.gz`, `pq/per_query.jsonl`, `data/RT*.json`),
  `MODEL_SOURCE.json`, `MODEL_DOWNLOAD.json`, `download_model.py`,
  `official_st_quantize.py`, `weight_headers.txt`, semantic code + `tokenizer_stats.json`.
- Absent: the ENTIRE `model/` dir (no `model.safetensors`, no `tokenizer.json`,
  `vocab.json`, `merges.txt`, no vendored `model/st_quantize.py` — only 3
  `.hf_modules` config/modeling cache copies) and ALL semantic embedding payloads.
- Consequence: no published number depends on a missing artifact (PPLX numbers don't
  exist; baseline/PQ aggregates recompute from zipped per-query rows), but the PRIMARY
  protocol endpoint (PPLX INT8/BIN/asym + PCA96 12B on RealTalk-705) is unreproducible
  from the package offline — it needs a 2.4 GB download (500 s observed once) plus a
  full CPU re-encode whose duration is uncertain (observed rates span 0.064 texts/s
  first-batch -> ~41 h, vs 1.82 texts/s fast-path -> ~1.5 h for 9649 texts). Source
  caches for baseline/PQ (`bench3/…`, `regen/…`) are likewise outside the zip.

### MP-06 / MP-07 — trivia (LOW)

- MP-06: `progress.json weight_bytes=2400127479` vs actual `model/` total 2400127792;
  the 313 B delta is exactly the subdirectory file `1_Pooling/config.json`, which the
  encoder's top-level-only sum (`encode_pplx.py:81-82`) skips. No finding beyond the
  undercount itself.
- MP-07: `semantic/.hf_modules/.../model/37bb1b653c423126/` holds only
  `configuration.py` (no `modeling.py`); both it and the full `f8498d62c9f3cb3a/`
  copy diff clean against `model/configuration.py` / `model/modeling.py`.
  Harmless transformers AutoConfig-resolution artifact.

## (4) What could NOT be checked and why

- Hub-side ground truth: NO internet per instructions, so `MODEL_SOURCE.json`'s
  revision/hash claims were corroborated only internally (download log URLs, ETags,
  on-disk hashes), NOT against huggingface.co. Would need: `git ls-remote` / Hub API
  for `perplexity-ai/pplx-embed-v1-0.6b @ 2c4d510d` plus fresh hash comparison.
- End-to-end inference fidelity (does `model.safetensors` through `modeling.py` +
  manual pooling reproduce official ST INT8/BIN on real text?): would require loading
  2.4 GB weights and a multi-hour CPU encode (each probe capped at 15 min); the
  installed env lacks `sentence_transformers`, so the official pipeline itself cannot
  run here — only the quantizer/pooling math above it was verified. Would need: the
  pinned env with ST installed + a completed encode + bit-compare vs a reference.
- Weight-tensor VALUES vs Hub: verified by sha256 (`2c8d2f64…`, matching ETag), not by
  semantic inspection; a conservatively-wrong file with the same hash is
  cryptographically infeasible, so this is noted for completeness only.
- Full-corpus drift of the pre-/post-fix scorer: sampled 20x1024 int8 + 4x9x32 pooling
  only; exhaustive proof would need the real pooled distribution (unavailable — no
  payloads exist).
- `audit_hard_r1/r2` texts were read-only context and were not re-audited; prior-round
  verdicts (e.g. the 705-query inductive collapse) were taken as given per the brief.
