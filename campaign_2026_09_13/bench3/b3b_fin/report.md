[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# BENCH-3B FINISH — PerLTQA port (killed-run salvage + verification)

Labels: [LOCAL EXPLORATORY PILOT]. License of source data: CC BY-NC 4.0 (non-commercial research).

A previous session ported the frozen SIGN96 pipeline to PerLTQA and was SIGTERM-killed
after STEP 0–2 computation but before writing its report. This session salvaged the
artifacts in `/tmp/b3b/` (byte-identical to the read-only copy at
`/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/`, verified by sha256 on all
19 files), verified every headline claim independently, and writes the missing report here
(`/tmp/b3b_fin/`; originals untouched). Interpreter: `$HOME/muse-work/ml-python`
(numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1).

## 0. Port fidelity gate — PASS (salvaged, 6 samples)

`port_gate.json`: gate PASS, n_sampled=6, threshold 1e-10, producer/adapter hashes match
expected. Max |C−C_ref| ≤ 7.38e-12, max |qC−qC_ref| ≤ 8.37e-13 across the 6 LME qids;
sign codes identical; gold identical. (Gate artifact accepted as-is; not re-run — it
requires the LME regen caches and producer file, and its JSON is complete and PASS.)

## 1. Unit reconciliation — DOCUMENTED DIFF (coordinator error, not run error) — VERIFIED

The brief said "1905 QA total (357/294/628/626)". That is a **top-level-keys miscount**:
profile QAs are flat dicts (count == keys), but social/events/dialogues QAs are nested
under group keys, so counting top-level keys undercounts them. Direct expansion of
`perltqa_en_v2.json` (this session, independent count) gives:

| layer | profile | social | events | dialogues | total |
|---|---|---|---|---|---|
| expanded QAs in file (32 chars) | 357 | 897 | 4501 | 2838 | **8593** |
| resolved (resolution.json) | 345 | 867 | 4349 | 2744 | **8305** |
| evaluated (cache_q_eval, n=8265 rows) | 333 | 844 | 4346 | 2742 | **8265** |

Reconciliation, all verified this session from the dataset file + resolution.json +
exclusions.json + cache_q_eval.pkl:

- 8593 − 8305 = 288 unresolved = 11 keymiss (events 7 + social 4) + 277 nobank
  (profile 12 + social 26 + events 145 + dialogues 94). The 277 nobank QAs are exactly
  the QA counts of the one bankless character "dragon beautiful" (12/26/145/94 = 277 —
  confirmed by direct per-char count). No other character lacks a bank (141 mem chars ⊇
  31 of 32 QA chars).
- 8305 − 8265 = 40 = exactly the Chen Zhi file counts (profile 12 + social 23 +
  events 3 + dialogues 2 = 40 — confirmed by direct count), dropped by the frozen-support
  exclusion (below).
- 32 chars → 31 archives → 30 evaluated archives: "dragon beautiful" has no bank in
  `perltmem_en_v2.json` (→ no archive built, its 277 QAs are the nobank unresolved);
  Chen Zhi built an archive with N=35 whose C came out (35, 35) — TruncatedSVD(96)
  silently capped at N samples with no warning — and was excluded per the port rule
  "do not silently shrink" (`exclusions.json`, reason recorded). Both confirmed:
  QA chars missing from `cache_arch_eval.pkl` = {Chen Zhi, dragon beautiful} exactly;
  `cache_arch.pkl` (pre-exclusion) has 31 (all but dragon beautiful). **32 → 30 reconciled.**

### What ONE evaluated unit is (read from step1/step2 sources, exact)

One evaluated unit = one **resolved QA record**: `(qid, char, section, question,
gold_idx_list)` with non-empty gold, where `gold_idx_list` is a sorted list of integer
archive-item indices, scored as **fractional R@3** = mean over NT=20 tie-draws of
|top-3 ∩ gold| / |gold| (plus any/all variants per QA). n = 8265.

Every itemization choice (from `step2_build.py`, applied uniformly):

- Archive = one character's memory bank. Items: profile → **one item per bank field**
  (`[profile] {field}: {value}`, build lines 27–28) **plus one profile_description item**
  (`[profile_description] {...}`, line 29); social → **one item per entry, sorted keys**
  (`[social {k}] ...`, lines 30–34); events → **one item per event narrative, sorted
  keys** (`[event {k}] {content}`, lines 35–38); dialogues → **per-TURN granularity:
  one item per turn** (`[dialogue {k} @ {ts}] {turn}`, sorted dialogue/ts order,
  lines 39–44). Per-turn (not per-dialogue) was required so anchors/refs can map to
  turns; profile_description kept as ONE item (not sentence-split).
- `memory_id` = `PQ{ord:03d}_{SEC}_{idx:03d}` (SEC ∈ PRF/DSC/SOC/EVE/DLG, ord = lexical
  ordinal over the 31 banked chars); `qid` = `PQ{ord:03d}_{SEC}_q{idx:03d}` with
  **per-section running index** across groups (profile flat; social/events/dialogues
  qi increments across all groups in file order — NOT per-group, NOT global).
- Gold mapping (`step2_build.py` lines 109–139): profile by **Reference Memory field
  name** → field index (miss → unresolved:keymiss); social/events by **group key** →
  that entry's item (miss → keymiss; the 11 keymisses are Cao Lili events [7 QAs under
  keys absent from bank] and Yang Wei social [4 QAs]); dialogues by **group key → all
  turn idxs of that dialogue, narrowed to anchor-substring hits when ≥1 numeric anchor
  text matches a turn case-insensitively, else fallback to the full dialogue turn list**.
  Split outcome (`dialogue_gold_split.json`): anchor-hit 1632 QAs (mean gold 5.69,
  range 1–21) vs fallback-full-dialogue 1112 QAs (mean gold 16.13, range 10–30).
- Fit: producer-verbatim Tfidf [latent32|word|char] → SVD96 seed 5204 → Y96 → C=Y−mu
  (float64); query transformed post-fit through the same fitted vectorizers/SVDs.
  (One deviation from the producer's adapter path: latent dim uses
  d=min(32, Xw.samples−1, Xw.features−1) rather than fixed 32 — forced by small banks;
  the SVD96 stage itself is verbatim including seed.)

## 2. Headline under suspicion — NOT A BUG (three independent verifications)

- Salvaged `results.json` (sha ec9b8b2c…): **native SIGN96 FR@3 = 0.48894 vs float96 =
  0.55169, delta = −6.275pp, n = 8265.** (native_any 0.59050 / float_any 0.64682;
  native_all 0.46967 / float_all 0.52886.)
- (a) **Verbatim rerun** (`step2_eval.py`, OUT=/tmp/b3b_fin/results_rerun.json, 4m18s):
  **byte-identical** (sha ec9b8b2c…, 9,402,513 bytes, `cmp` clean). Determinism confirmed;
  nonfinite-cos QAs = 0.
- (b) **Independent spot-check**: 5 QAs across all 4 sections recomputed via a
  pure-python `sorted()` path (no lexsort): all 10 values (native+float) match stored
  per-q to ≤5.6e-17 (tolerance 1e-12). All OK.
- (c) Code proof (`step2_eval.py`): native = Hamming on sign(C) over **ALL 96 cols** —
  line 30 `D0 = C >= 0`, line 55 `Q0 = qC >= 0`, line 56
  `d0 = count_nonzero(D0 != Q0)`; ranking line 20 `rh = lexsort((p, d))` (distance
  primary, random tiebreak). Float = cosine on **CENTERED C** — line 22–24
  `cos(C,q) = (C@q)/(||C||·||q||)` where C is the centered matrix from the build
  (step2_build line 64 `C = Y − mu`), line 21 `rf = lexsort((p, −s))`. Arms use Hamming
  on column subsets of the same sign codes (line 75). No inversion, no uncentered path,
  no column mix-up: the sign loss is real.
- (d) Eyeball top-5s (3 QAs): e.g. PQ026_PRF_q012 (Zhang Xiaohong, gold idx 13) native
  ranks gold 4th (d=34, misses top-3 → 0.0) while float ranks it 2nd (cos 0.8622 → 1.0);
  PQ026_PRF_q006 reverses (native 1.0 / float 0.0); PQ000_DLG_q000 (gold size 10) shows
  both arms retrieving a mix of gold turns and the sibling event item. Both orderings
  look sane — neither is degenerate.

**Verdict: the −6.275pp sign loss is genuine, not a scoring bug.**

## 3. Structure probes — where the negative delta concentrates (from stored per_q, n=8265)

Per-section native − float (fractional R@3 means):

- profile: native 0.50766 vs float 0.30330 → **+20.44pp** (n=333). ONLY section where
  sign wins — and wins big. (All gold_size=1.)
- social_relationship: 0.74905 vs 0.75711 → −0.81pp (n=844). Near-parity at high level.
- events: 0.69158 vs 0.81569 → **−12.41pp** (n=4346, 52.6% of evaluated QAs).
  **This section alone drives the headline.**
- dialogues: 0.08543 vs 0.10020 → −1.48pp (n=2742), both near floor (mean gold
  size 9.92; fractional recall of ~10–30 gold turns with K=3 is inherently tiny).

Per-character delta (30 archives): **29 of 30 negative**; only Cao Lili positive
(+1.53pp, N=377, n=302). Worst: Kong Tingting −13.46pp (N=293, smallest archive),
Han Gang −13.31pp (N=448), Tayo −10.40pp, Xia Tong −10.52pp. Corr(N, delta) = +0.18
(weak; larger-N archives lose slightly less, but there is no small-N instability —
all N ≥ 293, and the second-smallest archive Zhu Xiaolong N=343 loses only −3.09pp).

Gold-size vs delta: gold_size=1 (n=5943: all profile/social/events QAs) carries
−8.20pp; multi-gold dialogue bins sit at −0.3 to −3.2pp on much lower absolute recall
(e.g. gs=10: n=331, native 0.0606, delta −2.16pp; gs=20: n=408, native 0.0378,
delta −0.30pp). The sign deficit is a **single-gold precision phenomenon**, not a
multi-gold artifact.

Win-rate over QAs: native>float 9.2% (757), exact tie 73.0%, float>native 17.8%.
Median per-QA delta = 0.0; mean |delta| = 0.166.

Tie diagnostics: native boundary-tie rate 29.20% (2413/8265), mean tail gap 1.564
Hamming units; float tie rate 0.0% (continuous cosine never exactly ties at the
top-3 boundary), mean score gap 0.0333. The discrete 96-bit Hamming space ties an
order of magnitude more often — expected, and handled by the 20-draw tie protocol.

## 4. Convention audit — as-run matches deney1 split-0 verbatim; REALTALK deviated

`step2_eval.py` uses: RANDOM seeds **91000+j, j=0..9** (line 41); tie priorities
**5_100_000 + ORD[char]·100_000 + t·100 + 99** (line 43, ORD = lexical ordinal over
banked chars); SPREAD = `round(linspace(0,95,k))` over descending-variance order
(lines 37–39, distinctness asserted). The harness files confirm this is deney1
verbatim: `deney1_lme.py` line 32 `91000 + split*10 + j` (split-0 = 91000+j), line 90
the identical 5_100_000 priority formula, lines 150–151 the identical SPREAD
construction; `deney1_loco.py` matches. **Zero deviation: primary = as-run is
deney1 split-0.**

The REALTALK port (`bench3/runs/b3a_realtalk/details.json` protocol string) instead
used **global 93000-series** RANDOM arms. Sensitivity analysis this session (no rerun
of the full 41-arm eval needed — headline arms don't touch RANDOM seeds):

- RANDOM64 recomputed with 93000+j: mean 0.42591 vs as-run 91000-series 0.42196
  (+0.40pp, well within the 10-seed scatter sd=0.0141). SPREAD64 (0.42778) ≈ RANDOM64
  under either series. Conclusion (3) below is seed-robust.
- Tie-priority shift (+7919 on all 20 draws, native+float recomputed over all 8265
  QAs): native 0.48913 vs 0.48894 (+0.02pp), float 0.55169 identical, delta −6.256pp
  vs −6.275pp. **Headline robust to tie-breaking.**
- The 91000-series recomputation reproduced the stored RANDOM64 mean exactly
  (0.42196), further validating the stored numbers.

No full 93000-series 41-arm rerun was performed (would have re-spent ~4.5 min to
leave native/float bit-identical by construction); the two targeted sensitivities
above cover what a full rerun could have moved. Disclosed, not hidden.

## 5. Size flags — per-character N (cache_arch_eval, all C verified (N, 96))

Range 293–546, median 407. No small-N instability expected beyond excluded Chen Zhi
(N=35, C (35,35)). Full table:

Kong Tingting 293 (n=216) | Zhu Xiaolong 343 (323) | Xu Hui 359 (281) |
Xu Jia 371 (205) | Xiao Ming 376 (301) | Cao Lili 377 (302) | Xia Tong 380 (290) |
Madan 381 (299) | Zheng Yong 385 (278) | Zhang Xiaohong 391 (202) |
Lin Wen 392 (272) | Lu Yun 392 (288) | Liu Liang 401 (231) | Qin Meng 402 (314) |
Sun Xiaoming 406 (210) | Wang Ming 408 (219) | Xiong Fei 412 (362) |
Yang Wei 416 (233) | Huang Xin 418 (256) | Zhou Ting 421 (214) |
Li Hua 422 (224) | Feng Wei 422 (324) | Tayo 437 (283) | Wang Xiaoming 438 (242) |
He Feng 442 (311) | Han Gang 448 (259) | Cai Xiuying 459 (409) | Peng Jie 459 (284) |
Zhao Li 491 (239) | Liang Xin 546 (394). (n = evaluated QAs per archive.)

Effective-M caps: none bind — all archives support full SVD96 (min N=293 > 96+1), and
all ladder k (80/64/48) < min N. No cap effect to report.

## 6. Pattern checklist vs LME / LoCoMo / REALTALK (harsh honesty)

1. sign96 vs float96 — **FAIL (negative): −6.275pp** (0.48894 vs 0.55169, n=8265).
   Reverses LME +10.0 / LoCoMo +12.0 / REALTALK +5.2. Verified not-a-bug (§2). The
   reversal concentrates in events (−12.41pp, 52.6% of QAs); profile counter-wins
   (+20.44pp, n=333) but is outvoted 13:1.
2. Ladder costs (aggregate): 80b: TOP 0.47306 / SPREAD 0.46444 / RANDOM 0.46413±0.008 /
   BOT 0.40397; 64b: 0.44706 / 0.42778 / 0.42196±0.014 / 0.33301; 48b: 0.41865 /
   0.37552 / 0.37003±0.020 / 0.29135. Monotone cost of dropping bits; native96
   (0.48894) beats every 80b arm (float excepted).
3. SPREAD ≈ RANDOM vs TOP — **HOLDS in aggregate** (SPREAD80 0.46444 vs RANDOM80
   0.46413; SPREAD64 0.42778 vs 0.42196; SPREAD48 0.37552 vs 0.37003; TOP above both
   at every k). BUT with a section anomaly: in **profile, the order inverts —
   BOT64 (0.4883) > SPREAD64 (0.4294) > TOP64 (0.3059)**, i.e. high-variance cols
   HURT profile retrieval. Social/events show the normal TOP-best order; dialogues
   flat (~0.06–0.09 all arms).
4. BOT — worst at every k in aggregate (0.404/0.333/0.291), as usual; except the
   profile inversion just noted (BOT64 is profile's best 64b arm and near-native).
5. Section profile — anomalous vs prior ports: previously sign won broadly; here
   sign wins ONLY profile (+20.44) while losing events hard (−12.41). Social is parity
   (−0.81). Dialogues is a floor effect (both ≤0.10) driven by gold sizes 10–30 vs K=3.
6. Anomalies / limits:
   - The headline reversal itself (see "what this means" below).
   - Profile ladder inversion (BOT64 best) — suggests profile-field discrimination
     lives in LOW-variance directions of these per-character archives; variance-order
     arm semantics may not transfer across itemization regimes.
   - Dialogue floor: fractional R@3 with mean gold 9.92 (fallback mean 16.13) vs K=3
     compresses all arms to ≤0.10; this section contributes noise, not signal, to the
     headline (its delta is only −1.48pp).
   - 29.2% native boundary ties (vs 0% float) — the Hamming space is coarse at N≈400;
     the 20-draw protocol handles it, and tie-shift sensitivity is ±0.02pp.
   - Itemization sensitivity untested: per-turn dialogue + single-item
     profile_description + min(32,·) latent dim are one reasonable choice, not the only
     one; the sign>float question may interact with them (especially the
     anchor-substring narrowing, which decides gold sizes 1–21 vs 10–30).
   - Single benchmark, 30 archives, one seed family for SVD (5204) — no claim beyond
     PerLTQA-en_v2 as itemized here.

### What this means for generalization

One benchmark now fails the sign>float pattern — on 8,265 evaluated QAs with a
bit-identical determinism rerun, an independent 1e-12 spot-check, and tie-seed
robustness (±0.02pp). The failure is not uniform: sign still wins profile by +20pp,
but events (−12.4pp, the majority section) overturn it. That heterogeneity is the
finding: **the SIGN96 advantage does not generalize unconditionally across memory
regimes.** Plausible mechanism (not proven): per-character PerLTQA archives mix
short factual items (profile/social/event one-liners) with long dialogue turns in one
fit, so the top-variance SVD directions — which the sign code must quantize — get
dominated by dialogue/event-narrative verbiage while single-gold factual retrieval
needs fine-grained distinctions that binarization destroys but cosine preserves
(the profile BOT64 inversion points the same way: discriminative signal living in
low-variance cols). Whatever the mechanism, a program claiming sign≥float as a
general property must now either bound its domain (excluding PerLTQA-style
mixed-granularity per-character archives as itemized here) or explain the events
section. Do not average this away: the negative is section-concentrated,
seed-robust, and methodologically clean — it is evidence, not error.

## Provenance

- Salvage hashes: all 19 /tmp/b3b files sha256-identical to the read-only run copy.
- Rerun: /tmp/b3b_fin/results_rerun.json sha256 ec9b8b2c… == salvaged results.json.
- This report: /tmp/b3b_fin/report.md; numbers machine-readable in
  /tmp/b3b_fin/summary.json (same directory).
