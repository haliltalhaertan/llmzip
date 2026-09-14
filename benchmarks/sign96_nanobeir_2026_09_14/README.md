# SIGN96 NanoBEIR 13-task generalization sweep

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Purpose: test whether the unusual V52 observation — a 96-bit centered sign code sometimes outperforming its exact continuous 96D parent — generalizes outside conversational-memory benchmarks.

This branch starts from `findings/f1-execution-2026-09-14 @ ccedd5613c337e455a91043fd971c36360aa2fda`.

## Frozen method identity

The runner refuses to execute unless these inherited sources are byte-exact:

- `adapters/longmemeval_v52_adapter.py`
  - SHA256 `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- `docs/v52/task4c2/v52_t4c2_centering_geometry.py`
  - SHA256 `3bb1126090ab619c061d10d0f1a5c20db1372c5e2cd66b5158905a65f460061b`

The archive representation follows T4C2:

1. fit word + char TF-IDF and lexical SVD on corpus documents only;
2. concatenate `[Xl, Xw, Xc]`;
3. `TruncatedSVD(96, random_state=5204)`;
4. row-normalize to `Y96`;
5. center by corpus mean `mu`;
6. FLOAT96 ranks with exact cosine on `Y96-mu`;
7. SIGN96 uses the signs of the **same** centered coordinates and integer Hamming distance.

No query, qrel, answer label, or relevance information enters fitting.

## Outcome-blind ordering

For every NanoBEIR task:

1. dataset revision is resolved;
2. only `corpus` and `queries` are loaded;
3. representation is fit;
4. top-100 FLOAT96/SIGN96 rankings are computed for 20 deterministic relevance-independent tie trials;
5. **only then** is the `qrels` subset loaded and metrics computed.

Primary crosswalk to the original memory experiments: `Recall@3`.
Standard IR primary: `nDCG@10`.
Also recorded: Accuracy/Recall/Precision @1/3/5/10, MRR@10, MAP@100, paired query bootstrap intervals, W/T/L, and Hamming boundary ties.

## 13 tasks

NanoArguAna, NanoClimateFEVER, NanoDBPedia, NanoFEVER, NanoFiQA2018, NanoHotpotQA, NanoMSMARCO, NanoNFCorpus, NanoNQ, NanoQuoraRetrieval, NanoSCIDOCS, NanoSciFact, NanoTouche2020.

## Important limit

`SIGN96 = 96 bits = 12 active code bytes`.

This experiment **does not** claim the whole retrieval system costs 12 bytes/vector. Shared TF-IDF vocabularies, IDF arrays, SVD/projector state, index overhead and serialization/storage accounting are deliberately outside this benchmark and remain separate static-storage questions.

## Interpretation

A broad SIGN win would show cross-domain generalization of the phenomenon, not explain its cause.
A broad loss would be equally valuable: it would localize the phenomenon to memory/conversation-style archives.
Mixed signs would motivate predicting the regime from pre-outcome geometry.
