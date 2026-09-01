# V52 Task 4F1 — V3 Candidate Outcome-Free Preparation Report

Date: 2026-09-01  
Role: Head Researcher preparation only  
Status: `PASS — READY FOR FRESH COLD-START INDEPENDENT V3 AUDIT`

This preparation does not seal, preregister or authorize Task 4F1. No real BEAM ranking or Native, signed-permutation, Haar or ITQ retrieval-quality outcome was computed, opened or interpreted.

## Governance disposition

V2 and its independent BLOCKED audit remain byte-preserved. The V2 audit package was independently re-hashed 11/11 before remediation. Its three sealing blockers B1–B3 are accepted as valid and are bound into the V3 preparation seal.

Current boundary:

- `TASK 4F1 PREREGISTRATION = BLOCKED`
- `TASK 4F1 RUN = BLOCKED`
- `RETRIEVAL-QUALITY OUTCOME ACCESS = FORBIDDEN`

## Exact V3 bindings

- implementation: 59,110 bytes; SHA256 `0c1c1cc2bcf23296f0559daa98d936ed605fd7068ef376aa26bed69f6e66b07c`
- recursive payload inventory: 1,180 bytes; SHA256 `c7b53e55aff9206be8f70779bb781813e2c177120db1a4fb2826dde699df4199`
- candidate execution seal: 6,598 bytes; SHA256 `9d35192ecc20fbe0a01254278857f656027b71e1f04947267c67e4d379a868de`
- sealed cohort: SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`
- V2 blocking audit manifest: SHA256 `9942a531647b95d3ded7ca069a13ca70f51ab51868ad6835321e59601ba05395`

## B1 remediation — no silent finalization overwrite

Finalization reserves the three derived CSV paths, their `.tmp` paths, the post-run manifest and its `.tmp` path before reading/aggregating checkpoints. Any pre-existing reserved path blocks immediately.

Derived CSV and manifest commits use an exclusively created temporary file followed by an atomic same-directory hard link. An existing destination cannot be replaced. A failure leaves evidence that blocks a blind retry.

Synthetic regression confirmed:

- a pre-existing derived CSV blocked and its sentinel bytes remained unchanged;
- a crash-left `.tmp` path blocked and its sentinel bytes remained unchanged;
- a clean synthetic finalization produced all three CSVs and the manifest.

## B2 remediation — metric recomputation from frozen gold

For every trial cell, finalization canonicalizes all retrieved IDs and the frozen `gold_source_ids_parsed`, independently recomputes Fractional Source Evidence Recall@3, ANY@3 and ALL@3 with `metrics_at_3`, and requires exact equality to the stored fields.

Synthetic regression rejected both:

- retrieved IDs `9,8,7` carrying false `.75/1/0` metrics against frozen gold `1,2,3,4`;
- correct retrieved IDs with a deliberately wrong stored fractional metric.

## B3 remediation — exact Native/signed-control revalidation

Finalization stores the parsed ordered top-three IDs and ordered distances for every question/method/seed/trial cell. Each signed-permutation cell must exactly equal the matching Native cell for both IDs and distances. Trial replication identity now covers distances as well as IDs.

Synthetic regression rejected:

- signed-control top-three order divergence with unchanged metrics;
- signed-control distance divergence with unchanged IDs and metrics;
- a trial-only distance divergence under fixed priority.

## Preserved gates

The V2-to-V3 source diff leaves archive representation, query transformation, ranking, signed-permutation generation, Haar, ITQ, tie priority, archive evaluation and aggregation formulas unchanged. Changes are confined to V3 schema bindings, finalization validation and no-replace output commit behavior.

Locked outcome-free runner preflight passed again:

- Python 3.12.13 / NumPy 2.3.2 / SciPy 1.16.1 / scikit-learn 1.7.1 / psutil 7.0.0;
- all five thread controls;
- 2,000 total rows / 1,712 eligible / 96 archives;
- 192/192 pinned corpus files;
- synthetic representation/method gates;
- outcome-free `100K::12` archive and fixed-query canary digests.

The structurally complete negative V3 authorization was tested only by directly calling `verify_run_authorization`; it blocked on the unsealed Head Researcher key commitment. The HMAC environment variable remained unset and no output directory was created. CLI `run` and `finalize` invocation counts were both zero.

## Required next gate

A fresh cold-start independent auditor must re-hash and audit these exact V3 bytes. The audit must reproduce B1–B3 fixes with synthetic fixtures and actively search for related semantic-substitution, partial-output, checkpoint and finalization bypasses. It must not invoke CLI `run` or `finalize`, set the HMAC key, construct a valid authorization, rank a real query or inspect retrieval quality.

Even a clean PASS authorizes only a later Head Researcher sealing decision. Preregistration, key commitment, execution and interpretation remain separate blocked stages.
