# 03 — VERIFY COMMANDS (run from this bundle's root)

All checks are local. No network. Three levels:

## 1. Integrity (hash manifests)

```bash
# pilot directory manifest (18 entries; paths are relative to this bundle root)
sha256sum -c pilots/axis_attack_2026-09-12/HASHES_AXIS_PILOT.txt

# bundle additions (docs, protocol sources, sample matrices, transcripts, checkers)
sha256sum -c SUPPLEMENTARY_PILOT_HASHES.txt
```

## 2. Consistency (stdlib only)

```bash
python3 verify_pilot.py
# expected: all checks PASS, exit 0

# round-2 additions (edition 2)
sha256sum -c pilots/axis_attack_2026-09-12/round2/HASHES_AXIS_PILOT_R2.txt
python3 pilots/axis_attack_2026-09-12/round2/verify_round2.py
# expected: ALL ROUND-2 CHECKS PASS
```

It re-derives from the shipped files: the 470-question gate (aggregate recompute from the
per-question map; per-question values vs the frozen CSV), the per-axis identities
(`drop_FR + drop_loss == native mean`; `alone_fr_norm == alone_FR × pool / 3`), the E4 arithmetic
and the monotone ordering (matched < random < antimatched), the corrections tags, and key claim
greps into REPORT.md.

## 3. NumPy spot-recomputation (optional; needs `numpy`)

```bash
python3 verify_sample_numpy.py
# recomputes per-question native FR @3 for the 32 shipped matrices; must match stored values exactly
# (it also prints two 32-sample arm means, informational vs the full-470 values in 01 §B)
```

Protocol formulas you need if you write your own recomputation (all verbatim from the frozen
producer in `protocol_sources/`):

```text
codes:   D = (C >= 0); Q = (qC >= 0)              # C: (N,96) float64; qC: (96,)
dist:    d = np.count_nonzero(D != Q[None,:], axis=1)
lex:     ordinal of question_id in sorted(qids_500_sorted.json)
trials:  for t in 0..19: prio_t = np.random.default_rng(5_100_000 + lex*100_000 + t*100 + 99).random(N)
rank:    order = np.lexsort((prio_t, d)); top3 = order[:3]
metric:  Fractional Evidence Recall@3 = |top3 ∩ gold| / |gold| ; per-question = mean over 20 trials
```

## 4. What CANNOT be checked from this bundle (state it, don't treat it as a defect)

- **Full 470-question recomputation** — needs the complete 172 MB matrix cache; only 32 matrices
  are shipped (`sample_data/`). The full cache's byte-provenance lives in the companion Task1
  bundle (`certification_report.json` → `pkl_sha256_manifest`, 470 entries).
- **Byte-provenance of the matrices vs the historical originals** — impossible in principle for
  hidden float bytes (see the companion bundle's red-team record); what IS certified: all published
  functionals reproduce (0.0/≤1e-12) and all consumed codes are bit-identical.
- **Per-question raw values for the E1/E4 arms** — only aggregates (+ per-question native FR and the
  per-axis matrices `per_axis_matrices.npz`) were saved; per-question arm tables would need the full
  cache and a rerun.
- **Frozen programme state** (seals, ledgers, Task 4F1 boundary) — separate governance layer; only
  the companion bundle's summary applies here.

## 5. Round-3 additions (EDITION 3)

```bash
# round-3 bundle manifest (38 entries; paths remapped for this bundle)
sha256sum -c pilots/axis_attack_2026-09-12/round3/HASHES_ROUND3_BUNDLE.txt

# round-3 consistency (stdlib-only)
python3 verify_round3.py
# expected: ROUND-3 ALL CHECKS PASS (exit 0)
```

Round-3 protocol notes: the Deney-1 arms use the same frozen tie protocol as rounds 1–2; splits are
salted-stratified (rules in `round3_sources/harness/deney1_lme.py` / `deney1_loco.py`); the kill
rule was pre-declared at session level (roadmap; quoted verbatim in `round3/DENEY1_REPORT.md`);
D2/D4/c2 session code ships under `round3/muse_sessions/*/`. The LoCoMo per-axis arrays are shipped
as `round3/deney1_loco_peraxis.npz` for independent re-analysis.
