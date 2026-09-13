# Muse session — RACE-2: SIGN-ARM race runner (implement + smoke)

You are implementing the race runner for the SIGN-ARM family, per the v2 prereg draft. Write code
+ run it (this is the build phase; the official one-shot happens after seal — but your run here IS
the smoke + the frozen outputs candidate). Read-only /mnt/c; write ONLY /tmp/rb2/. No network.
numpy only (no faiss needed for this session).

## Spec (from DRAFT_PREREG_TWELVE_BYTE_RACE_v2.md — read it first; paths in the draft)

Benchmarks: LME-470 + LoCoMo-1535 (same loaders/protocol as pilots: regen/lme/cache_repr/*.pkl;
regen/locomo/*.pkl + drive/audit_layer corrections; tie priorities `5_100_000+lex*100_000+t*100+99`
and `stable_archive_seed(ci,t)+99`; 20 trials; K=3; fractional R@3; per-question then aggregate;
anchors 0.5419751773049645 / 0.23654714666441054 with ≤1e-12 abort).

Arms (sign family):
- NATIVE96.
- SPREAD_k, TOP_k, BOT_k for k in {80, 64, 48} — **per-archive variance construction** (R2C/pilot
  convention: order_desc = argsort(var)[::-1]; TOP=order_desc[:k]; BOT=order_desc[-k:];
  SPREAD=order_desc[round(linspace(0,95,k))]); assert eff_k==k, log counts; ALSO a global-ordering
  SPREAD64 sensitivity variant (axes ranked by mean per-archive rank across the benchmark).
- RANDOM panels: 10 seeds/width, literals `93000+10*width_idx+j` (j=0..9; width_idx {0:48,1:64,2:80}).
- TOP-variance negative control: k=48 (k=64 LME optional) — prespecified: loses to random-mean by
  ≥5pp expected; if it wins → validity FAIL flag.
- A3 learned arm: EXCLUDED (record only).
- Per arm: per-question FR arrays persisted; mean/median; W/T/L vs SIGN (tol 1e-12) + tie fraction;
  model-predicted FR column using the MATH-1 exact identity P(top3)=f(S,T) (per question, per arm;
  descriptive annex — include it in the JSON).
- Per-type (LME 6 types) / per-Cat (LoCoMo 4) descriptive means; per-seed records.
- Bootstrap: B=5000, seed 94301 — but you may STOP at producing per-question arrays + aggregates;
  bootstrap machinery can ship as a separate analysis step (state what you produced).

Smokes to execute + log (subset for this session): S1 (both anchors in THIS runner, abort demo),
S6 (tie rule: 20 priorities as lexsort(distance, priority), per-question persistence demo on one
archive), S8 (construction asserts + one BROKEN-construction negative control showing the abort
fires), S10 (no C:/ hardcodes in runner — use env/relative; threads=1 pins recorded), S9-lite
(dry-run manifest hashing of its own outputs).
Gates: anchors ≤1e-12; reproduce pilot spot aggregates under matching definitions: LME TOP48
≈0.34949468 (per-archive convention — verify against R2A defs in round2/session_scripts/r2a.py:
read it and MATCH its construction exactly for this gate), RAND48_s0 12000 ≈0.4729255, BOT48
≈0.4284574; LoCoMo native etc. State any definitional mismatch found and how resolved.

## Outputs

/tmp/rb2/race_sign.py (single constants block at top), race_sign_details.json (per-q arrays, cols,
per-seed records, aggregates, model column, descriptives), smoke_log.txt, hash manifest of outputs.
Print RB2_VERDICT: <gates; arm aggregate table; TOP-control verdict; asserts status>. ~2-3 hours.
