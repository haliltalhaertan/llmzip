# HANDOFF PROMPT — llmzip programme: everything done from the beginning
**For an external LLM (review / continuation / Q&A).** Version 1.1 — 2026-09-13 ~15:00 UTC+3 (B3B verification + tie-robustness audit folded in; see §2 row, §5, §6).
All content is [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE].

> How to use: give this entire text to another LLM as its brief. If it has access to the local
> work area (a Windows/macOS/Linux filesystem or an uploaded archive), point it at the artifact
> map in §7 — raw files override this brief everywhere; it must report any conflict it finds.

---

You are reviewing (or continuing) a private, local research programme called **llmzip**. This
brief is self-contained. Treat every number below as a CLAIM to be checked against raw artifacts
where you have access — not as ground truth. Your single most valuable output is honest,
adversarial scrutiny; silence on a defect you noticed is the only real failure.

## 1. The research question

LLM agents need long-term memory: candidate text chunks are embedded as vectors and the agent
retrieves the top few for the answering model. Retrieval quality therefore gates answer quality.
The programme asks: **how small can a retrieval code be while preserving (or improving) retrieval
quality?**

Frozen pipeline (local, deterministic, no neural embedder):
- Each archive (a set of memory items) is embedded by: TF-IDF/SVD over `[latent32|word|char]`
  feature blocks → SVD96 (seed 5204) → L2-normalize → `Y96` (96-dim float64). Archive mean `mu96`
  is computed from the archive; `C96 = Y96 − mu96` (centered). Sha256 of the producer script:
  `8dce37b1611ba6257570b…` (frozen; all ports must import it, never reimplement).
- **Native code = SIGN96 = sign(C96) = 96 bits = 12 bytes.** Retrieval = Hamming top-3.
- Baseline = **float96** = the same vectors as floats (384 bytes) — NOW KNOWN to be the CENTERED
  floats ranked by cosine (see §6.1; this was only established by audit on 2026-09-13).
- Primary metric = **fractional Evidence Recall@3 (FR@3)**: gold evidence items (e.g. `dia_id`s)
  counted fractionally when in the top-3, averaged over 20 random tie-order draws (K=3, expected
  value over ties). "1pp" ≈ 4–5 of 470 LongMemEval questions.
- Headline anomaly: **12-byte SIGN96 beats 384-byte float96** (+10.04pp on LongMemEval,
  ≈+12.0pp on LoCoMo, +5.22pp on REALTALK; a NEGATIVE result on PerLTQA is under verification).

## 2. Frozen anchors (verify from raw files; bit-exactness is the programme's fetish)

| anchor | value | source |
|---|---|---|
| LME native SIGN96 (n=470) | `0.5419751773049645` | V52_T4C2 question-level CSV; reproduced exactly in every session |
| LME float96 = centered floats (n=470) | `0.4415957446808511` | same CSV (AUDIT-1 Task B, 2026-09-13) |
| LME uncentered float `Y96` (n=470) | `0.4401063829787234` | same (auxiliary) |
| LME ITQ96 | `0.3761411347517731` | same |
| LME Haar96 (5 seeds, mean) | `0.38271666666667` → D = **−15.926pp** | T4C3 compute report |
| LoCoMo native (n=1535) | `0.23654714666441054` | T4D report |
| LoCoMo Haar mean | `0.13770827054136` → D = **−9.884pp** | T4D report |
| LoCoMo float96 delta | ≈ +12.0pp vs Sign (programme-reported; not re-derived) | V52 docs |
| Budget ladder, best naive arms (LME / LoCoMo costs vs native) | 10B ≈ −2.7 / −0.1 · 8B ≈ −5.9 / −1.9 · 6B ≈ −9.2 / −5.5 · 4B ≈ −17 / −9.6 · 2B ≈ −34 | round-2 pilots |
| Race verdict (sealed) | HOLD-parity: LME SIGN − best rival = **+1.6716pp** vs SPREAD80, CI95 [−0.60, +2.12]; LoCoMo **+0.1086pp** vs BOT80, CI95 [−0.91, +1.02] | analysis of official run |
| Race kill/promote lines (frozen pre-run) | KILL −6.4pp LME / −3.7pp LoCoMo · PROMOTE +2.0pp; premium needed +3.1 / +1.8pp (80% power +4.4/+2.6); calibrated null: LME −3.14 sd 1.60, LoCoMo −1.82 sd 0.93 | RB1 calibration |
| Certificate table (95% one-sided; per-comparison / Bonferroni-18) | LME 10B ≤3.28/4.28 (SPREAD), 8B ≤6.06/7.40 (BOT), 6B ≤10.83/11.96 (RANDavg); LoCoMo 10B ≤0.95/1.55, 8B ≤3.00/3.73, 6B ≤6.84/7.70 (all BOT) | CERT report |
| Rotation probes | effective-coordinate count 48.3 native → 93.9 Haar; variance-CV 0.994 → 0.150; signed-permutation invariance EXACT | T4C3 |
| REALTALK port (n=705/728) | native `0.22477507598784194` vs float `0.17253405381064957` → **+5.2241pp**; W/T/L 104/558/43; BOT is the best ladder arm at 80/64 | B3A report; coordinator hand-verified all headline numbers from raw per-QA rows + hashes |
| PerLTQA port (n=8265; VERIFIED — genuine negative) | native `0.4889419949` vs float `0.5516920745` → **−6.275pp (sign LOSES — not a bug)**: byte-identical rerun (sha `ec9b8b2c…`), spot-check ≤5.6e-17, tie-shift robust (−6.256pp); sections: profile +20.4pp native, social −0.8, events −12.4 (n=4346), dialogues −1.5; 29/30 archives negative | b3b_fin/report.md + summary.json |

## 3. Chronology — what was done, from the beginning

- **Phase −1 (pre-history):** the original V52 pilot series built the frozen pipeline and probe
  codes (native/float/ITQ/Haar) inside repo `haliltalhaertan/llmzip`. Its archived outputs live in
  `drive/` with hashes (T4C2/T4C3/T4D reports & scripts).
- **Phase 0 — Task-1 rederivation & certification:** original result pickles were lost; instead of
  trusting summaries, every archived result was RE-DERIVED with the deterministic producer +
  canonical datasets: published CSVs reproduced to the last printed digit (validation gates 0.0
  deviation), a 60-entry hash ledger (`HASHES_TASK1.txt`). Red-team proved byte-exact provenance of
  original artifacts is impossible; scope is **rederivation vs published summaries/codes**.
- **Phase 1 — axis-attack pilots (rounds 1–3):** systematic perturbations of the frozen codes:
  (i) coordinate mixing (Haar rotation) destroys retrieval (−15.9pp LME / −9.9pp LoCoMo) while
  signed permutations are exactly invariant; (ii) variance-ordered axis selection is a TRAP (top-
  variance subsets lose; spread ≈ random ≈ best; bottom sometimes best); (iii) top-3-boundary TIES
  dominate outcomes (losers have 5.5× more strictly-closer rivals vs 0.55 for winners; tie-mass
  feature AUC 0.798 vs 0.686 for mean distance); (iv) an exact probability model reproduces every
  panel from per-question distance distributions alone (r ≥ 0.997), including the TOP48 collapse.
- **Phase 2 — the twelve-byte RACE (sealed campaign, 2026-09-13):** a prereg-shaped race for "what
  beats 12 bytes at ≤12 marginal bytes": **RB1 calibration** (kill/promote lines above; null from
  2M draws, seed 94301; the 30 random-seed arms counted as competitors makes the null a
  max-statistic over a 40/41-arm set); **RB2** sign-arm runner (SIGN champion + budget ladder +
  TOP-variance control + MATH-1 model column); **RB3** FAISS runner — external codecs at 12 bytes:
  RaBitQ (A4, 32-axis config; note its natural config needs ~20B so it is a handicapped-but-fair
  ≤12B arm) 0.294–0.312 LME; PQ (A6) 0.431 LME; wrapper (A5) 0.338 — ALL lose vs native 0.542.
  Byte-replay asserts exact (20/12/12/44 B); PQ mask policy never fired. Pre-run SEAL of runner
  hashes + literals → single OFFICIAL RUN → **RACE-V independent recomputation: 26/26 checks
  EXACT, zero undisclosed diffs** → official analysis above.
- **Phase 3 — certification:** distribution-free paired-bootstrap certificate table (§2); a
  model-conditional lemma (spike+bulk class; retrievable-mass bounds and monotonicity of f(S,T)
  PROVED; the class membership itself a conjecture); honest verdicts: bit-exact reconstruction,
  model-free lower bounds and a universal floor are all OUT of reach; only finite-sample
  quality-equivalence is certifiable; ε=0 now/here certified nowhere.
- **Phase 4 — generalization (BENCH-3):** ports to two unseen benchmarks behind a **Port-Fidelity
  Gate** (a port may not be scored until it reproduces LME C96 bit-exactly ≤1e-10 via the frozen
  producer): REALTALK (10 real chats, 728 QA, evidence = message ids) → **+5.2241pp, gate PASS 5/5,
  hand-verified**; PerLTQA en_v2 (32 character memory banks: profile/social/events/dialogues QAs,
  expansions: 8593 QA → 8305 resolved → 8265 evaluated on 30 archives) → **−6.275pp (VERIFIED)** — the first
  REVERSAL of the sign>float pattern (byte-identical rerun + spot checks + tie-shift robust; section-split shows a structural,
  not random, effect).
- **Phase 5 — literature sweep:** found the "coordinate heterogeneity" theory (arXiv 2605.17524)
  that PREDICTS and EXPLAINS our rotation result and predicts value in magnitude bits (untested);
  the TurboQuant / "MSE ≠ recall" industry controversy (external version of our sign>float class);
  neighbor systems (RaBitQ, QuIVer, MRC/MHR, Hippocampus = binary-signature memory, IKE); new
  benchmark candidates (MemoryAgentBench, MemTrack). Planned: E1 heterogeneity diagnostics on C96,
  E2 same-budget bit-allocation sweep (96×1 vs 48×2 vs 64×1.5).
- **Phase 6 — audits (COMPLETED 2026-09-13):** AUDIT-1 resolved the "+10pp might be centering, not
  binarization" suspicion — see §6.1; tie-convention robustness (pessimistic / expected /
  optimistic tie resolutions) and full PerLTQA verification are COMPLETE: race gaps stay positive under pessimistic ties (LME +1.369/+1.717/+2.188pp; LoCoMo +0.089/+0.131/+0.193pp, monotone pess<exp<opt — the convention does not carry the results).

## 4. Governance rules this programme holds itself to (keep them if you continue)

- Labels on every output: `[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
  [DISCLOSE-BEFORE-USE]`.
- **Nothing is ever pushed** to GitHub; main is untouched; all work is local.
- Rules and thresholds are frozen BEFORE official runs (seals of runner hashes + literals +
  calibration); one official run; independent recomputation afterwards; findings filed as errata
  when later audits contradict earlier text.
- Two independent agent sessions per attack round where feasible (one computes, one reviews
  adversarially). NOTE: this "independence" is cross-session, same model family — NOT institutional.
- The operator works on Windows 10; the work area is `C:\Users\MDP\dev\llmzip-work` (writable) and
  a repo checkout `C:\Users\MDP\dev\llmzip` (main @ `5ec3db6`). Operator constraints for automated
  agents: no paid APIs (use the local Muse CLI in WSL for agent work), no git pushes, local-only.
- The operator speaks Turkish; answer in the language they use.

## 5. Current live state (2026-09-13 ~15:00)

- SETTLED: LME/LoCoMo race complete, sealed, verified, analysed (HOLD-parity); certification table
  delivered; Task-1 rederivation complete; REALTALK port complete (hand-verified); **PerLTQA port verified (genuine negative)**; **both audits complete** (centering decomposition §6.1 + tie-robustness §6).
- COMPLETED (v1.1 update — both finished cleanly after the kill incident): **B3B-FIN** (PerLTQA negative-result verification: determinism
  re-run, 5 spot checks, code-line evidence, convention audit, report) and **AUDIT1-CONT**
  (tie-convention robustness on real race arms for LME/LoCoMo + provenance of anchor numbers).
  Both were relaunched after an unexplained simultaneous external SIGTERM killed their predecessors
  mid-writing (outputs survived; both sessions later completed and were harvested). No sessions are running now.
- PENDING: ED4 transfer bundle (race sources + RACE-V + analysis) not yet assembled; E1/E2
  experiments not started; a "B3-V" independent verification of the two new ports not started;
  the 1M-scale test (4F1) remains untouched.

## 6. Declared weak spots — START HERE if your job is review

1. **Significance margins:** the LME race margin (+1.67pp) has a CI that includes 0; "moderate,
   not proven". The null counted every random seed arm as a competitor (conservative choice).
2. **Tie-convention dependence — RESOLVED 2026-09-13 (was: under audit):** all margins live in a fractional-R@3 world with a
   specific tie rule; pessimistic/optimistic re-resolutions done — gaps stay positive in the same MID zone (LME +1.369/+1.717/+2.188pp; LoCoMo +0.089/+0.131/+0.193pp, monotone pess<exp<opt); the convention does not carry the results.
3. **Cross-session ≠ institutional independence** of RACE-V/D1V verifications.
4. **Reproducibility ≠ validity:** bit-exact reruns verify arithmetic, not definitions. The
   weakest layer is definitional (tie rule, metric, question validity), not numeric.
5. **Centering vs binarization — RESOLVED 2026-09-13 (§6.1).**
6. **Scope:** 2+2 benchmarks, one feature family, modest scale; the +10pp claim is not a law of
   nature. The PerLTQA reversal (now VERIFIED; events −12.4pp vs profile +20.4pp) is the live example.
7. **Wording traps already identified:** "learned selection is dead" should read "the tested
   learned selectors (drop/alone family) did not beat best-of-random"; "SIGN96 unbeaten" should
   read "unbeaten at ≤12 bytes across the tested configurations on these benchmarks".
8. **Provenance items:** the −15.9pp Haar figure's source lives in `drive/` T4C3/T4D reports (not
   in the round-3 bundle where an auditor first looked); per-archive code bytes were not persisted
   (only aggregate `codes_sha256`); manifest `.py` entries not shipped in the official-run folder.

### 6.1 the resolved audit (template for how findings must be stated)
Suspicion: "+10pp might be centering (subtract archive mean), not binarization." Verdict (audit,
n=470, from the frozen question-level CSV, reproduced by the audit session and hand-checked):
uncentered float 44.011% → centered float 44.160% (centering = **+0.149pp**) → sign 54.198%
(binarization = **+10.038pp**); total vs uncentered = +10.187pp; paired W/T/L sign-vs-centered-float
122/304/44. Conclusion: the anomaly is BINARIZATION, and the original float96 anchor was already
centered (the comparison was fair all along). Deliverable of that audit: `taskB_numbers.json`.

## 7. Artifact map (local, `C:\Users\MDP\dev\llmzip-work\…`; all read-only-safe for reviewers)

- `harness/` — runners & regen scripts (`deney1_lme.py`, `deney1_loco.py`, `lme_regen.py`,
  `locomo_regen.py`, `task1_extend_lme.py`, `code_cert_v2.py`, …)
- `regen/` — re-derived caches (`lme/cache_repr/*.pkl`: per-qid C/qC/gold; `task1_RESULTS_extended.json`)
- `pilots/axis_attack_2026-09-12/round3/` — pilot reports + `DENEY1_REPORT.md`, `ROUND3_REPORT.md`,
  `HASHES_ROUND3.txt`, `deney1_*_details.json`, `muse_sessions/`, `missing_analyses/`
- `race_2026-09-13/` — `CAMPAIGN.md`, `RACE_REPORT.md`, `analysis/{analysis.py,ANALYSIS.md}`,
  `rb1|rb2|rb3|cert|racev/` (each with report + details JSON + scripts), `official_run/`
  (`PRE_RUN_SEAL_local.json`, `OFFICIAL_RUN.md`, sealed outputs)
- `prereg_race_2026-09-13/` — `DRAFT_v2.md` + `pre1/ pre2/ math1/ math2/`; root
  `DRAFT_PREREG_TWELVE_BYTE_RACE(.v2).md`
- `review_transfer/` — external-review bundles (ED2, ED3 FULL/LITE with verify scripts) + THIS file
- `strategy/roadmap_2026-09-13/` — roadmap docs (incl. "why does sign beat float?" probe list)
- `bench3/` — datasets (REALTALK, PerLTQA) + `runs/b3a_realtalk/` (complete, hand-verified) and
  `runs/b3b_perltqa/` (salvage: results.json, port_gate.json PASS, step0–2 scripts, caches)
- `audit_2026-09-13/` — audit scope + AUDIT-1 partial artifacts (`taskB_numbers.json` = §6.1)
- `lit_scan_2026-09-13/` — literature report + saved source texts
- `drive/` — FROZEN originals: producer scripts, T4C2/T4C3/T4D reports & CSVs, datasets, hashes
- Task-1 surface: `TASK1_COMPLETION_RECEIPT.md`, `HASHES_TASK1.txt` (60 entries), `OZET_TASK1_TR.md`
- Muse session logs (WSL): `~/muse-work/run_*.log` (transcripts of every agent session)

Entry-point checks a reviewer with filesystem access can run: `sha256sum -c HASHES_ROUND3.txt`;
replay `race_2026-09-13/analysis/analysis.py` against `official_run/` JSONs; re-derive §2 anchors
from `drive/` CSVs; re-run `bench3/runs/b3a_realtalk/run_realtalk.py` and bit-compare `details.json`
(`8bae1d38…`).

## 8. What we want from you (pick per the operator's actual ask)

- **(A) REVIEW** — hunt for errors in claims, definitions, statistics, provenance. Start from §6.
  For each suspected defect: state severity, the exact check that would confirm/refute it, and the
  evidence you used. Do not pad with praise; a clean bill of health must itself be justified.
- **(B) CONTINUATION** — rank the next experiments. Candidates on the table: finish/verify the
  PerLTQA reversal (is it real, structural, or a port artifact?); tie-convention robustness; E1/E2;
  independent re-verification of the ports (B3-V); ED4 bundle; a 5th benchmark; 1M-scale test;
  MHR-style learned codes. Say what you would do first and why, with pass/fail criteria.
- **(C) Q&A / TEACHING** — explain any part of the programme in plain language.

If this brief and the raw files disagree, **the raw files win** — report the conflict explicitly
with file+line evidence.