[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 1 — Measurement provenance of the 88,886 bytes/vector figure

PREPARED, NOT ACCEPTED. Nothing here is sealed, ratified, or closed. Labels: VERIFIED = I ran/read the bytes; CLAIM = a document says it; RELAYED = second-hand.

## Headline

The figure "88,886 effective bytes/vector" is VERIFIED as the **median over 15 archives of (12 + shared_total/N_archive) for the float32+structured-vocab serialization of a declared re-fit** — i.e. it is a MEASUREMENT (of a re-fit, on real corpus text) combined with a MODEL OUTPUT (the choice of float32, structured vocab, median convention, per-archive sharing). It is not a property of a frozen production artifact: the pilot README states the frozen artifact's physical serialisation was never located (CLAIM, confirmed by re-read: `origin/findings/representation-geometry-2026-09-13:research_representation_geometry_2026_09_13/README.md`, "What these measurements are NOT" section).

## Where exactly it comes from

- Producer: `measure_projector.py` (`origin/findings/representation-geometry-2026-09-13:research_representation_geometry_2026_09_13/measurements/projector/measure_projector.py`), config `MARGINAL = 12`, `SVD_SEED = 5204`, `N_COMPONENTS = 96` (VERIFIED by reading the script head, lines ~50-58 region: `SVD_SEED = 5204`, `N_COMPONENTS = 96`, `MARGINAL = 12`).
- Data: first 15 archives of the frozen geometry order (`001be529` first; script exits 2 otherwise), N range 443–551 (VERIFIED: recomputed from `PROJECTOR_BYTES.json` per_archive Ns — min 443, max 551).
- Pipeline re-fit per archive: `fit_archive_representation(texts)` → hstack → `TruncatedSVD(96, random_state=5204)` → normalize → mu; only archive texts read, no labels (VERIFIED from script body).
- Inventory (7 items): word vocab + IDF, char vocab + IDF, `sv.components_` (32×word), `s96.components_` (96×combined), `mu` (96). Rationale: `TruncatedSVD.transform` uses only `components_` (source-checked by the auditor — CLAIM in `AUDIT_MEASUREMENTS_TR.md`, "Projector" section; I did not re-read sklearn source, so the source-check itself is RELAYED, the byte totals are VERIFIED below).
- Encoding of the quoted figure (format "a": raw float32 + structured vocab = index-order terms, each `uint32 LE length + UTF-8`): VERIFIED from `vocab_structured_bytes` in the script.
- Aggregation: median of the 15 per-archive `effective = 12 + shared_total/N` values = **88886.36234817814** (VERIFIED: independent median recomputation over `PROJECTOR_BYTES.json` per_archive matches to full float precision; report rounds to 88,886).

## Answers to the mandated questions

1. **Per-archive or shared projector? Per-archive.** The design fits one projector per archive and divides by that archive's N (VERIFIED: per_archive entries each carry their own totals; report states "paylaşılan durum yalnızca o arşivin N≈443–551 vektörü arasında paylaşılır, küresel değil" — global projector is a different, unmeasured configuration).
2. **Counted at float32? Yes for the headline.** The 88,886 figure is format (a) raw float32. Three cheaper formats are measured alongside: float16 raw → 45,614; zlib(float32) → 48,141; zlib(float16) → 34,453 (all VERIFIED medians recomputed from JSON: 45614.25, 48141.48, 34452.86). Native float64 reference median is 87,288,483 B total (VERIFIED from aggregate block).
3. **Median over how many, what spread? 15 archives; per-archive effective (float32) min 80,266.5, max 104,463.6** (VERIFIED recomputation; report table rounds to 80,267–104,464). So the headline ± spread is roughly −10%/+18%. Scope is 15 of 470 archives, one seed (CLAIM in pilot README; consistent with the 15-row tables).
4. **MEASUREMENT or MODEL OUTPUT? Both, layered.** Measured: component array shapes/sizes from real-corpus re-fits (byte-exact on 2 archives per the independent audit — CLAIM in audit report; the audit's byte equality `a=45050700` for `001be529` matches the JSON total I read, VERIFIED consistent). Modelled/assumed: float32 instead of native float64 (a cost-reducing choice — note the native f64 median total 87.29M B is ~2× the float32 44.22M B); structured vocab instead of delimiter form (delimiter lower bound also computed, slightly smaller); median-of-effective convention (see observation O-6); per-archive sharing denominator.
5. **Declared refit, not frozen artifact? YES — loudly.** Pilot README: "They are declared re-fits. The frozen production artifact's physical serialisation was never located" (CLAIM, read verbatim). Every JSON carries `_refit_notice` (VERIFIED: keys `_labels`, `_refit_notice` present in `PROJECTOR_BYTES.json` top level).

## The audit's observations (PASS WITH OBSERVATIONS) — all seven findings, and which weaken the figure

From `origin/findings/representation-geometry-2026-09-13:research_representation_geometry_2026_09_13/AUDIT/AUDIT_MEASUREMENTS_TR.md` (read in full; findings F-01..F-07):

- **F-01 (P1): the gate is shape-only, not pipeline identity.** Proven by execution: `sublinear_tf=False` reproduces the 4 gate integers exactly while moving σ by 0.44 (~5–8%); lexicon SVD seed change moves σ by 0.16 with identical gate. **Weakens the figure's pedigree, not its arithmetic**: assurance rests on code-identity review + independent re-derivation, not the gate. A wrong-but-gate-passing pipeline variant would shift all byte totals (vocab sizes change with vectorizer options).
- **F-02 (P1): `TRUNCATION.json` has no generating script in the package** (spectrum package, not projector). Does not touch the 88,886 figure directly; weakens package-level reproducibility discipline.
- **F-03 (P1): no `HASHES.json` for ties/roles.** Not projector; no effect on the figure.
- **F-04 (P2): unsourced "independent auditor reproduced" self-claim in spectrum scope.** Not projector; no effect on the figure, but it means the "independent" cross-checks cited near the headline number should be treated as RELAYED until the audit in hand (which does reproduce 2 archives byte-exact — CLAIM).
- **F-05 (P2): `REPRODUCE.md` lacks the re-fit declaration.** Documentation; no numeric effect — but directly relevant to the "say so loudly" requirement: one file in the package omits the declared-refit status.
- **F-06 (P2 observation): the "~7400×" ratio framing invites misreading as a cap test despite two disclaimers.** Directly relevant: the number most likely to be quoted (88,886 ≈ 7407×12) is arithmetically correct (VERIFIED: 88886.36/12 = 7407.2) and explicitly not a cap test (JSON contains no PASS/FAIL — CLAIM, consistent with keys I listed), yet reads like one. This is a framing weakness, not a numeric one.
- **F-07 (P2 observation): ties script recomputes a pool 5×.** Cosmetic; no effect.

## My own additional observations (adversarial additions)

- **O-A (convention sensitivity, VERIFIED): the quoted 88,886 is median-of-effective; ratio-of-medians gives 90,257** (44220235/490 + 12 = 90257.38). Gap ≈ 1,371 B (~1.5%). The cost-evidence package explicitly corrected the analogous mean-of-costs vs cost-at-mean error (1.07 B, `EVIDENCE.json` archive_cost); the projector pilot does not discuss its median convention at all. Small vs the 7400× headline, but a skeptic quoting the figure should know it is convention-dependent.
- **O-B (float32 is a choice, VERIFIED): native sklearn output is float64; the headline halves numeric bytes by assuming float32 with no retrieval-harm check** (harm check is Task4F1-sealed and was not done — CLAIM in report "Bakılmayanlar"). Cheapest measured format (f16+zlib, 34,453) is 2.6× smaller than the headline; the headline is therefore neither the cheapest defensible nor the native figure.
- **O-C (15-archive scope, VERIFIED N range 443–551 vs frozen 396–616):** the measured archives exclude both tails of the archive-size distribution. Direction of bias: larger N dilutes shared cost, so if anything the 15-archive median may *understate* small-archive costs — the direction that matters for the MISLEADS case is covered, not flattered.
- **O-D (component dominance, VERIFIED):** on median archive `078150f1`, s96.components_ = 85.11%, sv = 11.40%, vocab = 2.61%, IDFs ≈ 0.9%, mu ≈ 0%. The figure is essentially "one 96×~98k float32 matrix per ~500 vectors". Any attack on the figure must attack that matrix's necessity — the audit's inventory argument (transform needs only components_) defends its inclusion, and nothing in the bytes suggests double-counting.
