[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Representation geometry measurements and round4 repair packages — 2026-09-13

Additive research branch. `main` is untouched at `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`; nothing here is merged, and no frozen artifact is rewritten.

This directory holds two kinds of work, both independently audited, with the audit verdicts included:

1. **Five descriptive measurements** on the real LongMemEval corpus, under an explicit Head Researcher grant, answering questions the programme had left open.
2. **Four additive repair packages** correcting defects found in the frozen `round4` mathematics at `1021083d4f2faebda760546e1217b4de1eef87ea`.

## Status — read this before using anything here

| Package | Audit verdict | Usable? |
|---|---|---|
| `measurements/` (all five) | **PASS WITH OBSERVATIONS** | Yes, within the stated scope |
| `repairs/norm_math` | PASS (within the repairs audit) | Yes |
| `repairs/norm_tests` | PASS with two documentation defects | Yes, after the two text fixes |
| `repairs/rank_cover` | PASS with one governance defect | Yes, after the supersedes table is completed |
| `repairs/rank_cert` | **REQUEST_CHANGES — BLOCKING** | **NO. Do not use `certify_v2.py` to certify anything.** |

### The blocking finding

`repairs/rank_cert/certify_v2.py` **certifies a false result**. Reproduced independently by two parties with `AUDIT/poc_bulgu1.py`:

```
input : p=(-100,100,0,10000), q=(-200,200,70000,0), J=[1,4]
truth : verdicts {5/4:+1, 3/2:+1, 7/4:0, 5/2:-1, 4:-1}  -> the order VARIES
v2    : ISOLATED_TIES, direction -1                      -> WRONG
orig  : UNRESOLVED                                       -> honest
```

The original procedure correctly refused this case. The repair traded conservatism for a wrong answer, which is the one failure mode a certificate may never have. Root cause: exact roots are not classified as crossing vs tangency, and `rational_roots` has no pre-cut on budget overrun. The measured resolution rates elsewhere in that package are unaffected and reproduce exactly, but the claim "it never certifies something false" is **false as written**.

This package is preserved here byte-unchanged, with its audit, as the programme's convention requires. It is not fixed.

## Measurements — what was found

All five passed a gate reproducing the frozen feature geometry (`N_archive`, `word_columns`, `char_columns`, `combined_columns`) exactly on 15 archives.

- **`spectrum/`** — raw SVD decay `p_A = 0.478` (median), first-12 share `f12_A = 41.7%`. The variance the method actually thresholds decays differently: `p_B = 0.861`, `f12_B = 35.7%`. Row normalisation after the SVD means `Var(C)` cannot be derived from the singular values and must be measured directly. Sign balance: essentially no coordinate is collapsed (median 11 of 96 outside [0.45,0.55], 0 outside [0.30,0.70]). Truncation sweep: the variance tail is **not** flat at 96 — the last 32 coordinates carry ~9.9%.
- **`projector/`** — the shared projector's byte cost, open since the programme's earliest handoffs. Median **88,886 effective bytes per vector** against the 12-byte marginal budget, dominated by `s96.components_` (85%). Break-even: ~3.7M vectors (float32) or ~1.4M (float16+zlib) would have to share one projector for the shared cost to fall to 12 B/vector. Archives hold ~500.
- **`ties/`** — boundary-tie multiplicity at top-3 is median 1; 74% of probes have no tie at all. Ties **decrease** as N grows. Continuous-query rescoring resolves 99.4% of the ties that exist; the residue is identical ±1 codes, which nothing can separate.
- **`roles/`** — adjacent assistant→user pairs are much closer than random (Hamming 28 vs 48, AUC 0.955), but they are **not** near-duplicates: pairs within 16 bits are 0.14% of all pairs, and 84% of those are not adjacent pairs. Role asymmetry is ~1 bit.
- **`tails/`** — a proposed mechanism (heavy tails + hubness, asserted kurtosis 9.71 / skewness 1.58) is **refuted**: measured per-coordinate median kurtosis 1.10, skewness 0.09. Hubness is moderate and similar under raw float, clipped float and sign scoring; at k=10 the sign score's hub skew is *higher* than raw float, the opposite of the prediction.

## What these measurements are NOT

They are **declared re-fits**. The frozen production artifact's physical serialisation was never located; these are the statistics of a faithful re-fit of the same pipeline, and every document says so.

**Variance loss from discarding coordinates is measured. Retrieval harm is not, and could not be** — that requires gold labels and recall, which are inside the sealed Task4F1 boundary and were not touched. No document here may be read as evidence about retrieval quality.

Scope: 15 of 470 archives, one seed. The power-law fits are imperfect (R² ≈ 0.87 and 0.78), so the exponents are summaries, not laws.

## Independence limitation

The repair packages and the measurements were produced by sessions of one model family; the audits were produced by cold-start sessions of the same family, with no memory of the work and an adversarial brief. Both audit reports state this themselves. **This is partial independence, not full independence.** A genuinely independent review has not been performed.

## Boundary compliance

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`. No gold or evidence label was opened; no recall, accuracy, ranking correctness or benchmark was computed; no seal, HMAC or finalize was performed. The corpus and the representation pipeline were opened only to read descriptive statistics, under explicit grant, and every such document is labelled a declared re-fit.

`main`, the continuity ledger and `ops/CURRENT_STATE.json` are untouched. The frozen `round4` archive is byte-unchanged; all corrections are additive and carry supersedes notes.
