# SIGN96 vs FLOAT96 — NanoBEIR 13-task post-run report

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This is a post-run reporting artifact only. It does not modify the benchmark code, dataset, rankings, qrels, or result artifacts.

## Provenance

- GitHub Actions run: `34866074513`
- Run head: `a9ffad8e1ee146368c0a522f71aee9cdd67cedbc`
- Branch: `bench/sign96-nanobeir-sweep-2026-09-14`
- Workflow: `.github/workflows/sign96-nanobeir-sweep.yml`
- Run conclusion: `success`
- Summary artifact: `sign96-nanobeir-summary`, artifact ID `10357626222`
- Summary artifact digest: `sha256:68cb5e8a00e00b82c4bc776bef3026242675a9c61de55f4f5ff86a19599ae8b2`
- 13 NanoBEIR tasks, 649 queries, 56,723 corpus documents.

## Protocol boundary

The representation was fit from corpus documents only. Queries were transformed with the fitted representation. FLOAT96 and SIGN96 rankings were produced before qrels were loaded. Qrels were loaded only after top-100 rankings had been frozen in memory. Binary ties used 20 deterministic relevance-independent SHA-256 nuisance priorities.

FLOAT96 and SIGN96 use the same centered 96-dimensional representation. FLOAT96 ranks by centered cosine; SIGN96 takes the sign of those same 96 centered coordinates and ranks by integer Hamming distance.

`96 bits = 12 active code bytes` is **not** a whole-system storage-cost claim. Shared TF-IDF vocabulary/IDF/SVD/projector/index state is excluded from that number.

## Aggregate result

| Metric | SIGN96 wins | ties | losses | Macro delta | Median delta |
|---|---:|---:|---:|---:|---:|
| Recall@3 | 8 | 0 | 5 | **+2.472 pp** | **+0.640 pp** |
| nDCG@10 | 8 | 0 | 5 | **+1.770 pp** | **+0.647 pp** |

## Per-task deltas

| Task | Delta Recall@3 (pp) | Delta nDCG@10 (pp) |
|---|---:|---:|
| NanoArguAna | -5.700 | +0.647 |
| NanoClimateFEVER | -1.767 | -3.081 |
| NanoDBPedia | +1.203 | +0.520 |
| NanoFEVER | +4.033 | +3.498 |
| NanoFiQA2018 | +2.981 | +1.131 |
| NanoHotpotQA | +7.200 | +7.218 |
| NanoMSMARCO | +0.400 | -2.239 |
| NanoNFCorpus | -0.685 | -2.502 |
| NanoNQ | -3.000 | -0.458 |
| NanoQuoraRetrieval | +9.033 | +1.718 |
| NanoSCIDOCS | -0.300 | -0.075 |
| NanoSciFact | **+18.100** | **+14.627** |
| NanoTouche2020 | +0.640 | +2.009 |

## Strongest observations

- NanoSciFact: FLOAT Recall@3 `0.265`, SIGN Recall@3 `0.446`, delta **+18.1 pp**; nDCG@10 delta **+14.627 pp**.
- NanoQuoraRetrieval: Recall@3 delta **+9.033 pp**.
- NanoHotpotQA: Recall@3 delta **+7.2 pp** and nDCG@10 delta **+7.218 pp**.
- NanoFEVER: Recall@3 delta **+4.033 pp**.
- Clear counterexamples remain: NanoArguAna Recall@3 **-5.7 pp**, NanoNQ **-3.0 pp**, NanoClimateFEVER **-1.767 pp**.

## Licensed interpretation

This run materially weakens the hypothesis that the SIGN96-vs-FLOAT96 effect is unique to LongMemEval or conversational-memory benchmarks: large positive deltas appeared on independent retrieval task families including scientific fact retrieval, duplicate-question retrieval, multi-hop QA, and fact verification.

It does **not** establish that SIGN96 is universally better. The sign reversals are real and are scientifically important. The current evidence supports a regime-dependent phenomenon: binarization of the same centered 96D representation can improve or harm retrieval depending on the task/data geometry.

This run does not identify the causal mechanism, does not prove full-system 12-byte storage, and is not an external independent reproduction. A separate implementation and independent researcher should reproduce the headline results before publication-level claims are made.
