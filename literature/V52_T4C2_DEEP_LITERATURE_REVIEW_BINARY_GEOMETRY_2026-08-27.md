# V52 TASK 4C2 — DEEP LITERATURE REVIEW: BINARY GEOMETRY, SIGN/HAMMING, ROTATION AND LONG-TERM MEMORY
Date: 2026-08-27
Status: PRIOR-ART / MECHANISM REVIEW — NOT A PERFORMANCE CLAIM

## Executive conclusion

The Task 4C2 observation — coordinate-preserving SIGN/Hamming strongly outperforming an archive-fitted ITQ rotation on the same centered 96D representation — has a very close 2026 theoretical prior-art analogue. Wenxuan Xiao, “Coordinate Heterogeneity Governs Binary Quantization: From InfoNCE to Recall” (arXiv:2605.17524, May 2026), argues that non-uniform per-coordinate variance and full covariance structure can be useful signal for binary quantization; a rotation can uniformize coordinate variances and destroy the implicit coordinate weighting exploited by coordinate-preserving Hamming. The paper explicitly frames a rotation paradox between coordinate-preserving BQ and rotation-based BQ, and reports datasets where rotation harms Hamming BQ. Therefore, we must NOT claim that “rotation destroys useful coordinate heterogeneity” is a novel mechanism discovered by this project.

The project still has a meaningful empirical extension: archive-local no-QA/gold fitting, a fixed mixed text representation, exact evidence-level R@3 on conversational long-term memory, and an unusually large identity-sign vs learned-ITQ gap on LongMemEval under frozen same-input controls. Algorithmic novelty of SIGN96 itself is not supported.

## 1. Most direct prior art: coordinate heterogeneity

Wenxuan Xiao (2026), arXiv:2605.17524.
Core claim: coordinate heterogeneity (non-uniform per-coordinate variances) governs important aspects of binary-quantization fidelity. The full covariance matrix matters, not only dimension or angle. The paper derives a rotation–fidelity duality: random orthogonal rotation approximately uniformizes coordinate variances. This can hurt coordinate-preserving BQ because Hamming implicitly weights dimensions according to the representation’s native variance/covariance structure, while rotation can help methods that require isotropy for linear correction.

This is strikingly aligned with the mechanism suggested by Task 4C2, but there are important differences. Their main theorem concerns Haar-random rotation, whereas Task 4C2 compares identity SIGN to an archive-fitted ITQ rotation. ITQ is optimized to reduce binary quantization error, not sampled Haar-randomly. Their theory also assumes an approximate Gaussian / contrastive-embedding regime; our representation is a mixed archive-local SVD construction and must be tested rather than assumed to satisfy those conditions.

The paper’s experiments demonstrate that rotation is dataset-dependent, not universally good or bad. In one reported Hamming-BQ comparison, Cohere recall falls from approximately 0.440 to 0.381 after rotation; BGE-M3 is slightly harmed, while GIST benefits dramatically. This is precisely why a one-size-fits-all “rotation improves binarization” claim is unsafe.

**Novelty status:**
- `[KNOWN MECHANISM PRIOR ART]` coordinate heterogeneity can make coordinate-preserving BQ preferable to rotated BQ.
- `[OPEN EMPIRICAL EXTENSION]` whether the exact LongMemEval Task 4C2 gap is explained quantitatively by that mechanism.

## 2. QuIVer — coordinate-preserving training-free binary quantization

W. Xiao, Z. Wang, C. Li, “QuIVer: Rethinking ANN Graph Topology via Training-Free Binary Quantization” (arXiv:2605.02171, 2026).
QuIVer builds ANN graph topology directly in a 2-bit sign-magnitude binary metric and deliberately preserves coordinate axes. It reports strong recall on compatible cosine-native embeddings and carefully documents failure boundaries on other distributions. This establishes that training-free, coordinate-preserving binary retrieval is already an active modern design paradigm.

**Novelty status:** `[KNOWN]` coordinate-preserving binary quantization can be a deliberate retrieval design. Task 4C2 remains different: QuIVer is an ANN graph system with 2-bit sign+magnitude and final float rerank; Task 4C2 is symmetric 1-bit sign/Hamming global retrieval in conversational memory.

## 3. Learning-free binary LLM embeddings

Z. Zhang, Y. Xu, K. M. Ting, C.-T. Nguyen, “LLMs Meet Isolation Kernel: Lightweight, Learning-free Binary Embeddings for Fast Retrieval,” Findings of ACL 2026.
The paper proposes Isolation Kernel Embedding, a learning-free binary transformation of LLM embeddings. It reports up to 16.7x faster retrieval and 16x lower memory while maintaining comparable accuracy on multiple text-retrieval datasets.

**Novelty status:** `[KNOWN]` learning-free binary transformations of LLM embeddings for efficient retrieval.

## 4. Hippocampus — binary agent memory on LoCoMo/LongMemEval

Y. Li et al., “Hippocampus: An Efficient and Scalable Memory Module for Agentic AI,” MLSys 2026 / arXiv:2602.13594.
Hippocampus uses compact binary signatures for semantic search and compressed token streams for memory content. It evaluates on LoCoMo and LongMemEval and reports substantial retrieval-latency and token-footprint savings while maintaining competitive task accuracy.

**Novelty status:** `[KNOWN — DIRECT BENCHMARK PRIOR ART]` binary signatures for agentic memory on LoCoMo and LongMemEval. No future paper from this project should claim “binary memory retrieval on LongMemEval/LoCoMo” as new.

## 5. Simple zero-threshold binary quantization is standard practice

SentenceTransformers documentation describes binary quantization by thresholding normalized float embeddings at zero and retrieving with Hamming distance. Production/vector-database systems also use binary quantization plus oversampling/rescoring.

**Novelty status:** `[KNOWN]` sign(x) / zero-threshold binary encoding plus Hamming retrieval. SIMPLE_SIGN96 is not an algorithmic novelty.

## 6. Binary representations can match or sometimes outperform continuous retrieval

Salakhutdinov & Hinton, “Semantic Hashing” (2009) showed compact binary document codes and reported that binary prefiltering followed by TF-IDF could improve accuracy over applying TF-IDF globally.

Shen et al., ACL 2019, “Learning Compressed Sentence Representations for On-Device Text Processing,” demonstrated binary sentence embeddings with only modest degradation across tasks and very large storage savings. Consequently, the generic statement “binary can beat continuous retrieval” is not novel. What matters is our exact controlled phenomenon: same representation, frozen evidence-level benchmark, centered continuous cosine vs identity-sign Hamming, with a large fixed-benchmark gap.

## 7. ITQ and why lower quantization error need not mean better ranking

Gong & Lazebnik, “Iterative Quantization: A Procrustean Approach to Learning Binary Codes,” CVPR 2011. ITQ rotates zero-centered data to minimize quantization error to vertices of a zero-centered binary hypercube using an orthogonal Procrustes alternating optimization.

Task 4C2’s result should therefore be phrased carefully: ITQ may be doing exactly what its objective asks — reducing quantization error / producing balanced codes — while still giving worse evidence retrieval ranking for this representation. The 2026 coordinate-heterogeneity theory provides a plausible reason why a rotation that is good for one geometric objective can be bad for a ranking objective that benefits from native coordinate structure.

## 8. Opposing modern evidence: rotation can help

Hashing-Baseline (Moummad et al., ICASSP 2026; arXiv:2509.14427) combines frozen pretrained embeddings, PCA, random orthogonal projection, threshold binarization, and asymmetric Hamming retrieval. Their ablation reports PCA and random orthogonal projection as complementary; removing the random projection harms performance on their image/audio retrieval benchmarks.

RaBitQ (Gao & Long, SIGMOD 2024) uses randomized quantization / rotation and correction machinery to obtain a D-bit representation with a theoretical distance-estimation error bound.

Super-Bit LSH (Ji et al., NeurIPS 2012) orthogonalizes random hyperplanes to reduce angular-estimation variance relative to ordinary sign random projections.

This opposing evidence is scientifically useful. Rotation is not intrinsically bad; its effect depends on data distribution, quantizer, distance estimator, and downstream ranking objective. Any Task 4C3 mechanism claim must explain why our representation lies in the coordinate-preserving regime rather than merely observe that SIGN wins.

## 9. Classical foundation

Charikar (STOC 2002) formalized sign/random-hyperplane locality-sensitive hashing for angular similarity. Spectral Hashing (Weiss, Torralba, Fergus, NeurIPS 2008), Binary Reconstructive Embeddings (Kulis & Darrell, NeurIPS 2009), Hamming Distance Metric Learning (Norouzi, Fleet, Salakhutdinov, NeurIPS 2012), and rank-preserving hashing lines establish a broad historical literature on constructing binary codes to preserve similarity/ranking.

Two-Stage Hashing for Fast Document Retrieval (ACL 2014) explicitly combines LSH candidate pruning and ITQ reranking. Binary Passage Retriever (ACL 2021) combines compact binary candidate generation with continuous reranking. These works close off broad novelty claims about hashing, Hamming retrieval, learned rotations, two-stage binary retrieval, or binary QA retrieval.

## 10. Very recent adjacent work

“Quantization Beyond Uniform Bit Allocation” (arXiv:2608.19388, Aug 2026) shows that modern embeddings can have structured non-uniform information across dimensions and that non-uniform bit allocation can improve recall at the same budget, especially at low bitrates.

“BinaryPC: Training-Free Hashing-Based Attention via Binary Principal Components” (arXiv:2608.04405, Aug 2026) applies data-aware binary hashing to sparse attention / KV-cache retrieval. It is conceptually adjacent but operates inside transformer attention, not external conversational long-term memory.

## 11. Revised novelty map

**Not novel / known:** zero-threshold sign codes + Hamming, binary semantic/text/LLM retrieval, binary candidate retrieval + richer reranking, binary agent memory on LoCoMo/LongMemEval, ITQ/orthogonal rotation, coordinate-preserving BQ, the general proposition that rotation can erase useful coordinate heterogeneity, and the generic observation that binary retrieval can sometimes equal or beat a continuous baseline.

**Empirical extension:** archive-local mixed-SVD representation fitted without QA/gold/evidence labels; clean same-input identity-SIGN vs archive-fitted ITQ on LongMemEval; exact evidence-level R@3; frozen nuisance/tie semantics and chain-of-custody; unusually large SIGN-vs-ITQ and SIGN-vs-centered-float gap.

**Potentially contributive if cross-benchmark audited:** a pre-registered evidence-level bit–geometry–quality–cost study for conversational long-term memory, with archive-local unsupervised fitting and identical protocol across LongMemEval and LoCoMo, plus a mechanistic test of when native coordinate geometry should be preserved versus rotated.

## 12. Best next mechanistic test after the 4C2 audit

Do NOT start before independent 4C2 audit.

Instead of vaguely testing “collisions cause the improvement,” pre-register a coordinate-heterogeneity mechanism test:

A. Measure exact C96 per-coordinate variance distribution before sign/ITQ.  
B. Report CV / dispersion of coordinate standard deviations, covariance off-diagonal energy, effective rank, coordinate sign entropy, and if feasible Gaussianity diagnostics.  
C. Measure how ITQ changes those quantities, particularly variance dispersion and covariance structure.  
D. Ask whether per-question / per-archive SIGN advantage is predicted by pre-existing, label-free heterogeneity statistics.  
E. Freeze the predictor/statistic before performance association is inspected. Do not optimize a threshold on recall labels.  
F. Treat collision/tie changes as downstream diagnostics, not causal proof.

The strongest falsification would be: if C96 is nearly isotropic/homogeneous or if heterogeneity statistics do not align at all with SIGN-vs-ITQ ranking differences, the Xiao-2026 mechanism does not explain our result even though it is plausible prior art.

## 13. Claim ceiling

Even if Task 4C2 passes audit, the safe claim is:

> On the frozen LongMemEval evidence-retrieval protocol, identity sign/Hamming on a shared centered 96D archive representation substantially outperforms both centered continuous cosine and archive-fitted ITQ/Hamming. Existing 2026 binary-quantization theory suggests native coordinate heterogeneity as a plausible mechanism; this mechanism is prior art and remains to be tested in our representation.

Do NOT claim a new hashing algorithm, a new theory of binary quantization, or general superiority of sign/Hamming.

## Key references

- Xiao, W. Coordinate Heterogeneity Governs Binary Quantization: From InfoNCE to Recall. arXiv:2605.17524 (2026).
- Xiao, W.; Wang, Z.; Li, C. QuIVer. arXiv:2605.02171 (2026).
- Zhang, Z.; Xu, Y.; Ting, K.M.; Nguyen, C.-T. LLMs Meet Isolation Kernel. Findings ACL 2026.
- Li, Y. et al. Hippocampus. MLSys 2026.
- Moummad, I. et al. Hashing-Baseline. ICASSP 2026 / arXiv:2509.14427.
- Gao, J.; Long, C. RaBitQ. SIGMOD 2024.
- Gong, Y.; Lazebnik, S. Iterative Quantization. CVPR 2011.
- Ji, J. et al. Super-Bit LSH. NeurIPS 2012.
- Charikar, M. Similarity Estimation Techniques from Rounding Algorithms. STOC 2002.
- Weiss, Y.; Torralba, A.; Fergus, R. Spectral Hashing. NeurIPS 2008.
- Salakhutdinov, R.; Hinton, G. Semantic Hashing. IJAR 2009.
- Kulis, B.; Darrell, T. Binary Reconstructive Embeddings. NeurIPS 2009.
- Norouzi, M.; Fleet, D.J.; Salakhutdinov, R. Hamming Distance Metric Learning. NeurIPS 2012.
- Li, H.; Liu, W.; Ji, H. Two-Stage Hashing for Fast Document Retrieval. ACL 2014.
- Shen, D. et al. Learning Compressed Sentence Representations for On-Device Text Processing. ACL 2019.
- Yamada, I.; Asai, A.; Hajishirzi, H. Efficient Passage Retrieval with Hashing for Open-domain QA. ACL 2021.
- Sreeramji, K.S. et al. Quantization Beyond Uniform Bit Allocation. arXiv:2608.19388 (2026).
- Yu, D. et al. BinaryPC. arXiv:2608.04405 (2026).
