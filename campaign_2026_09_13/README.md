# Campaign 2026-09-13 — local findings snapshot (review surface)

**Labels:** [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
**Base:** `main` @ `5ec3db6` (this branch does not touch main). **Source:** local work area
`C:\Users\MDP\dev\llmzip-work` snapshot, 2026-09-13 ~15:30 UTC+3.

**TR özet:** Bu dal, 2026-09-13 yerel kampanyasının inceleme yüzeyidir: Task-1 sertifikasyonu,
eksen-saldırı pilotları (round 3), mühürlü "12-byte yarışı" (kalibrasyon → koşucular → sertifika →
bağımsız RACE-V → resmi koşu → analiz), BENCH-3 portları (REALTALK +5.22pp; PerLTQA doğrulanmış
negatif −6.27pp), denetimler (centering/binarization ayrıştırması; tie-robustluk; provenans),
literatür taraması, strateji ve Muse oturum prompt'ları. Büyük veri/önbellek dosyaları repo
konvansiyonu gereği dışarıda tutuldu (bkz. Exclusions).

## Headline results (independently recomputed or hand-verified)

| # | claim | number | evidence in this tree |
|---|---|---|---|
| 1 | Native SIGN96 (12 B) beats float96 (384 B) on LongMemEval | +10.04pp (54.198% vs 44.160%), n=470 | `audits/audit1/taskB_numbers.json` |
| 2 | The separation is BINARIZATION, not centering | binarization +10.038pp; centering +0.149pp | `audits/` |
| 3 | Twelve-byte race verdict (sealed) | HOLD-parity: SIGN − best rival +1.67pp LME (CI95 [−0.60,+2.12]); +0.11pp LoCoMo (CI95 [−0.91,+1.02]) | `race/analysis/`, `race/RACE_REPORT.md` |
| 4 | Race robust to tie-convention | pess/exp/opt: LME +1.369/+1.717/+2.188pp; LoCoMo +0.089/+0.131/+0.193pp | `audits/audit1_cont/` |
| 5 | Certified loss bounds (95% one-sided) | LME 10B ≤3.28pp / 8B ≤6.06 / 6B ≤10.83; LoCoMo ≤0.95 / ≤3.00 / ≤6.84 | `race/cert/` |
| 6 | REALTALK port | sign − float = **+5.2241pp**, n=705; port gate PASS 5/5 | `bench3/b3a_realtalk/` |
| 7 | PerLTQA port — FIRST reversal (verified, not a bug) | sign − float = **−6.275pp**, n=8265 (events −12.41 / profile +20.44); byte-identical rerun | `bench3/b3b_perltqa/`, `bench3/b3b_fin/` |
| 8 | Coordinate mixing destroys the signal | Haar96 −15.93pp LME / −9.88pp LoCoMo; effective coords 48.3→93.9 | `pilots_round3/` + `race/` refs |
| 9 | RACE-V independent recomputation | 26/26 checks EXACT, zero undisclosed diffs | `race/racev/` |

## Folder map

- `task1/` — Task-1 rederivation & certification surface (receipt, 60-entry hash ledger, TR summary).
- `harness/` — derivation/eval scripts holding the frozen conventions (e.g. `deney1_lme.py`,
  `lme_regen.py`, `code_cert_v2.py`).
- `pilots_round3/` — axis-attack round-3 reports, per-question details, Muse session slips (d1v…d5, c2).
- `race/` — sealed twelve-byte race: `rb1/` calibration, `rb2/` sign runner, `rb3/` FAISS runner,
  `cert/` certificates, `racev/` independent verification, `official_run/` sealed outputs,
  `analysis/` verdict, `RACE_REPORT.md`, `CAMPAIGN.md`.
- `prereg/` — prereg-shaped drafts (v1/v2) + pre1/pre2/math1/math2.
- `bench3/b3a_realtalk/` — REALTALK port (report, per-QA details, scripts, determinism hashes).
- `bench3/b3b_perltqa/` — PerLTQA port (scripts, unit resolution, exclusions, per-QA `results.json`).
- `bench3/b3b_fin/` — salvage-verification report of the killed run (byte-identical rerun sha `ec9b8b2c…`).
- `audits/` — AUDIT-1: centering/binarization decomposition + tie-convention robustness + anchor provenance.
- `lit_scan/` — literature sweep (coordinate-heterogeneity theory line + saved sources).
- `strategy/` — roadmap / strategy notes.
- `muse_prompts/` — the 38 session briefs used to drive the campaign (method provenance).
- `review/` — external-LLM handoff prompt (v1.1) + ED3 review docs.
- `MANIFEST.sha256` — sha256 for every included file.

## Exclusions (per `DATASETS_AND_LARGE_ARTIFACTS.md` conventions)

Not in this branch (remain local / Drive): raw datasets (`bench3/REALTALK`, `bench3/PerLTQA`;
canonical LongMemEval already documented in the repo), binary caches (`*.pkl` incl. `rt_repr/`
and `regen/` caches), `review_transfer` zip bundles, Muse run logs / `session.jsonl` transcripts,
`drive/` frozen originals (several already committed under `docs/v52/`), virtualenvs.
Rebuild paths live in `harness/` and `bench3/*/*.py`.

## Provenance

- Snapshot taken from `C:\Users\MDP\dev\llmzip-work` on 2026-09-13; branch
  `findings/campaign-2026-09-13` created from `main` @ `5ec3db6`; main untouched.
- Session transcripts: excerpts under `pilots_round3/muse_sessions/`; full run logs remain local.
- Numbers carry the gates recorded in their own reports; this tree adds no new claims.