# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# GENERATOR.md — synthetic (documents, queries, gold) generator: design + rationale
# Code: synth.py (generator + dial sweeps), cm_test.py (common-mode follow-up), control.py (metric control).

## 1. What the generator is
A sampler for one archive: an (N,96) document matrix C, a set of queries qC with
KNOWN gold rows, and nothing else. Both retrieval arms run exactly as in the programme
(VERIFIED: control.py reproduces the frozen LongMemEval headline
SIGN=0.542134 FLOAT=0.441596 Delta=+10.053783 exactly):
sign arm = Hamming distance between (C>=0) and (qC>=0);
float arm = cosine similarity on raw C;
score = FR@3 with the exact tie expectation E[FR@K] = (g_strict + g_tied*slots/bc)/|gold|.

## 2. Generative model
- Spectrum: per-axis scales s_j with s_j^2 proportional to j^-alpha, normalized so total
  variance = 96 (mean per-axis variance 1, comparable across alpha). alpha=0 flat … 2.5 steep.
- Documents: C = Z*diag(s), Z iid from the shape dial (gauss / heavy Student-t3 unit-variance
  / skew centered-exponential). Zero-mean by construction, mirroring the cached pre-centered C.
- Query with gold set G: q = beta*(w ⊙ mean_{g in G} C[g]) + sigma*(eps ⊙ s),
  eps fresh from the same shape family. w = signal-locus mask (top16/mid16/bot16/rand16/broad
  highest-variance axes). Noise is spectrum-matched (eps⊙s): the query lives in the same
  anisotropic space as the documents.
- THE MECHANISM UNDER TEST: cosine weights axes by magnitude, so it over-trusts noisy
  high-variance axes; sign gives every axis one vote. When discriminative signal sits on
  low-variance axes, cosine wastes its weight and sign should win; reversed when signal is
  top-loaded. The generator exists to test exactly this, with everything else held fixed.

## 3. Decisions taken and why (recorded so a later session can challenge them)
- D1 signal-power normalization: w is scaled so sum(w*s^2)=1, i.e. EQUAL total signal power
  across loci. Without this, "top16" trivially carries more signal and the dial confounds
  WHERE with HOW MUCH. Consequence: any locus effect is purely positional. (CLAIM: this is the
  right normalization; an un-normalized variant is listed in MENU.md as a 10-minute check.)
- D2 matched query noise (eps⊙s) rather than isotropic: a query embedding from the same model
  should share the archive's anisotropy. Isotropic noise is a listed follow-up, not tested.
- D3 diagonal covariance (independent axes): required to isolate the locus dial. Standing result
  (C) says real axes matter; correlated covariance is a listed amplifier candidate (not tested).
- D4 base operating point N=500, nq=400/archive, 5 seeds, beta=sigma=1: N=500 sits inside the real
  regime (293–1548); 400 queries give per-cell se ≈ 0.3–0.7pp (observed), enough to resolve flips.
- D5 multi-gold queries average gold rows: the simplest "shared topic" model; acknowledged crude.

## 4. Dials (each varied singly from BASE = N500/alpha1.0/gauss/broad/ng1/sigma1.0)
A spectrum alpha {0,.5,1,1.5,2,2.5}; B locus×alpha grid {top,mid,bot,rand16,broad}×{.5,1,2};
C shape {gauss,heavy,skew} at broad and bot16; D N {100,400,1500,5000}; E ngold {1,2,4};
F sigma {.5,1,2}; plus dimension-matched budget curves (programme convention: top-m axes,
both arms) and the cm_test.py common-mode-background dial (shared top-16 direction, gamma 0–3).

## 5. Limitations (VERIFIED gaps, not modesty)
- L1 magnitudes: at real-regime alpha≈0.9 the synthetic locus gap is ~2.4pp vs real ±5–12pp.
  The generator flips the SIGN but underpredicts the SIZE. An amplifier variable is missing.
- L2 budget curve: synthetic dimension-matched curves are FLAT (hover near 0); the real rising
  curve (A: −12→+10 across m) is NOT reproduced. The generator lacks whatever makes real
  low-variance axes cumulatively valuable.
- L3 one killed amplifier: a shared background direction on top-16 axes (gamma 0→3) moved Delta
  by <0.5pp in all three loci tested. Common-mode-as-implemented is dead; do not resurrect it
  in this form (correlated per-axis noise or spike spectra remain untested).
- L4 no inter-axis correlation, no topic/cluster structure, no query-side linguistic structure.
