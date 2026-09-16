[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERIFY QUEUE — sources the coordinator should fetch (web access required)

Ranked most decision-relevant first. Every item below is RECALLED-FROM-MEMORY:
I have NOT verified from disk that it exists under the stated
authors/venue/year, and no number, quote, or finding is asserted. One line per
item states what fetching it would settle. Do not cite any of these until the
fetch confirms the bibliographic details AND the claimed content.

1. Husbands / Simon / Ding — "Term norm distribution and its effects on LSI"
   (recalled: ~2005). — Settles whether our IDF^p arm has direct prior art and
   whether any stated limit on rare-term emphasis predicts our RealTalk-gain /
   PerLTQA-loss reversal (Q3; S1).
2. ITQ original — Iterative Quantization (recalled: Gong et al., CVPR ~2013;
   UNVERIFIED). — Settles ITQ's true objective, eval datasets/metrics, and
   whether any sparse/text or negative regime is reported (Q1 candidates
   b + d; decides if our rotation catastrophe is novel).
3. "All-but-the-top" postprocessing (recalled: Mu / Bhat / Viswanath, ICLR
   ~2018; UNVERIFIED). — Settles what ABTT is applied to, what operation it
   performs, and whether any cross-dataset sign reversal is reported (Q2).
4. ScaNN anisotropic quantization (recalled: Guo et al., ICML 2020;
   UNVERIFIED). — Settles the retrieval-optimal-vs-reconstruction-optimal
   precedent: exact loss, comparison, and dense-only scope (Q1 candidate b; S3).
5. Ando & Lee — "Iterative Residual Rescaling" (recalled: SIGIR 2001;
   UNVERIFIED). — Settles problem setup (global vs per-subset SVD), remedy,
   and whether benchmark-dependent effects are reported (Q3 distortion side; S2).
6. Drineas et al. leverage scores (recalled: JMLR 2012; UNVERIFIED). —
   Settles attribution of rho_i = sum_j U_ij^2 only; changes no number, lowest
   decision weight among the four starters (S4).
7. RRF original (recalled: Cormack / Clarke / Buettcher, SIGIR ~2009;
   UNVERIFIED) + per-paper storage audit of 2–3 hybrid baselines the programme
   actually compares against. — Settles the fusion formula/k=60 claim AND the
   honest-accounting question: does each compared paper charge itself for its
   inverted index (Q4; do not generalize beyond audited papers)?
8. BM25 saturation + pivoted length normalization primaries (recalled: Robertson
   et al.; Singhal et al.; UNVERIFIED). — Settles the institutionalized "how
   far to push rarity" answer: TF saturation and length-norm as the field's
   backfire guard (Q3).
9. Spectral Hashing (recalled: Weiss et al.) + any "bit-balance critique"
   follow-up. — Settles whether balance/variance-equalization is ITQ's
   inherited design goal and whether anyone reported balance hurting retrieval
   (Q1 candidate c).
10. Targeted search: rate-distortion / hashing-lower-bound / "bits vs recall"
    results for retrieval (no recalled candidate — this is a search, not a
    fetch). — Settles Q5 positively (a real theorem with stated distortion
    measure) or as a documented null with recorded search strategy; do not
    accept "no bound exists" without that record.
11. LSI-weighting comparisons (recalled: log-entropy vs TF-IDF on TREC;
    UNVERIFIED). — Secondary support for Q3: does any weighting study state a
    rarity backfire point on small collections?

Stop rule: items 1–4 decide the rediscovery question for our three live arms
(IDF^p, SHIFT, rotation). Items 5–6 are attribution hygiene. Items 7–11 each
settle one open half-question. Nothing here justifies re-fetching anything in
`../../inventory/literature/DO_NOT_RESCAN.md`.
