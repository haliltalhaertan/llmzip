[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# MASTER LEDGER — retrieval-quality numbers already measured

Inventory session 2026-09-16. Machine-readable companion: `ledger.csv`
(817 rows: 136 VERIFIED, 681 CLAIM, 0 RELAYED).
VERIFIED = re-derived this session from raw per-query data (counts below).
CLAIM = producer file inspected directly, not re-derived. Never averaged
across benchmarks. Values rounded for display; exact values in `ledger.csv`.

Re-derivation counts used: `baseline/per_query_top10.jsonl` 9440 rows
(PerLTQA 8265 / LME 470 / REALTALK 705); `audit/per_query_{bm25,tfidf}_corrected.jsonl`
705 rows each; `pq/per_query.jsonl` 705 rows. All re-derived means match the
producer reports at 4 decimals.

## 1. PerLTQA (n=8265)

Settled core (VERIFIED, Top10, deterministic SHA-tiebreak):
sign96 Hit .7568 / Rec .6182 / nDCG .4907; float_raw .8081/.7095/.5822;
float_std .8396/.7024/.5775; asym .8019/.6760/.5466. Tie-at-cut: sign96 0.7032,
asym 0.0005, floats 0.0000 — Hamming is the tie-sensitive arm, handled by exact
expected-Hit (exp .7576/.8081/.8396/.8019).
Settled: float_std is the strongest reference here; asym beats SIGN (+4.63pp FR@3)
but trails float_std; B8 adds nothing over asym (d=+0.00058, CI spans zero);
MAG8 adds nothing over SIGN_ONLY8 (d=+0.05pp, CI spans zero).
Also CLAIM: full hit@k/frac@k curves k=1..546 (KSWEEP+HIT10); qscale Hit@10 80.00
(coordinator-reproduced EXACTLY); HATA stage arms (centered 80.81, standardized
83.96, docbit+qstd 80.00); raw-text stage ladder (word TF-IDF 82.77, SVD96 drop
-3.47pp net on 364/77 queries); residual8 sections (events/mag8-base +0.70pp,
profile/social mag8-signonly8 negative).

## 2. LME (n=470)

Settled core (VERIFIED): sign96 .8638/.7626/.5914; float_raw .8255/.6895/.5095;
float_std .8830/.7955/.6207; asym .8574/.7338/.5559. Tie-at-cut sign96 0.6255.
Settled: float_std best; asym LOSES to SIGN here (d=-3.56pp FR@3); B8 loses to
asym (-2.44pp); MAG8 flat (-0.06pp). SIGN-vs-FLOAT sign flips vs PerLTQA, so no
pooled claim is licensed.
Also CLAIM: qscale Hit@10 88.51 (reproduced EXACTLY); HATA arms incl. centered
82.55 vs pre-center 82.77 (label fix, not a number change); 48-query raw-text
panel (SVD hit@10 flat but FR@3 51.28->38.26); LADDER 240-subset stages.

## 3. REALTALK (n=705 valid; 23 original empty-gold exclusions kept)

Settled core (VERIFIED): sign96 .4652/.3434/.2455; float_raw .3660/.2783/.2020;
float_std .4851/.3747/.2622; asym .4355/.3306/.2277. Lexical controls (VERIFIED):
BM25 .5418/.4316/.3428, TFIDF .5291/.4191/.3166 — both beat every 12-byte arm on
Hit@10 here. PQ12B (VERIFIED): .3305/.2439/.1734, per-archive 0.04..0.60
(RT06 0.054, RT08 0.043 collapse). Producer expected_hit column was mislabeled
(it equaled recall); corrected expected-Hit == hit mean (audit + this session).
Settled: lexical > float_std > sign96 > asym > float_raw > PQ12B on Hit@10;
no 12-byte arm is near lexical on this bench.
Also CLAIM: qscale Hit@10 49.65 (reproduced EXACTLY); qsign_dstd 50.35 claimed
but coordinator replay gives 49.50 (-0.85pp, NOT reproduced); RT09_q000 rank
inversion (gold rank 1 float-std vs 271 Hamming, diagnostic single case).

## 4. LoCoMo (transfer only, n=1531 per HIZ / 1535+5-skipped per LOCOMO.json — unresolved)

Only CLAIM, no VERIFIED rows, no historical float baseline. HIZ weighted(qstd)
Hit@10 57.22 vs hamming 52.64 (+4.58pp, 10-cluster bootstrap, exploratory);
LOCOMO.json sym Hit@10 43.84 / float_std 50.03 (different pipeline/gold: 156
audited corrections NOT applied, 5 no-gold skipped). Do NOT cite either as
unseen confirmation; do NOT mix the two LoCoMo numbers (different provenance).

## 5. Non-retrieval fixture studies (SmolLM2-135M, authored texts; CLAIM, compact)

KV ridge vs q4 (kv_repair, corrected alignment): ctx16 KL ridge 0.30-0.48 beats
zero/copy but loses to generic-4bit 0.02-0.03 everywhere; original negative dNLL
WITHDRAWN. Inverter: 0/12 + 0/4 under budget after JVP fix. Ledger L14 KV-only:
KL 0.00026. These are generation/compression probes, not Top10 evidence.

## 6. Gates and cross-checks (settled, do not re-run)

FR@3 SIGN/FLOAT replay PASS (maxdev 0.0, tol 1e-12) in baseline (VERIFIED this
session), asymmetric, B8, residual8 coordinators; 12/12 old-arm cells + qscale
reproduced EXACTLY by coordinator/verify_incoming.py; B8 S1 nDCG bug repaired
(FR untouched, maxerr 0.0); 510/510 payload integrity checks pass.
