# E1 V2 RAW-CACHE R2 — EXECUTOR PROMPT

You are the execution worker for one narrowly defined repair. Do not invent new hypotheses or modify frozen definitions.

## Repository targets

Repository: `haliltalhaertan/llmzip`

R1 recovery target:
`d5441698fa8fb8404873af47233569803b887376`

Independent audit:
`010bcbbe0ade15ed1dc501ce6d2f4e2e5ccd89b7`
verdict `REQUEST_CHANGES`.

R2 repair branch:
`research/e1-v2-raw-cache-recovery-r2-2026-09-13`

Frozen E1 V2 design:
`775a09c1ba6fd8c28f1e98ec1826d31a7f2c3484`

Read first:
- `campaign_2026_09_13/e1_v2_raw_recovery_r2_2026_09_13/AUDIT_FINDINGS_DISPOSITION_R2.md`
- `R2_COMPETITION_RERUN_CONTRACT.md`
- `E1_V2_COMPETITION_CORRECTED_RESULT.json`
- independent audit report at `010bcbbe...`.

## Drive inputs

Use the already-bound heavy-backup files, not regenerated representations:

`03_regen_caches.tar.gz`
Drive id `1H_k_y--a-QFvdrL5riEFC9ysCcyg2HFG`
SHA256 `a16bdf95d3a96cb964fd6fd614d3b49d22bb9329c5afaf81cd692214d50f8aad`

`04_bench3_runs_caches.tar.gz`
Drive id `1tfR3IC0BlJCxp90nDohT9I_qt8QPHzUg`
SHA256 `87d6312ef6c195ac6c161a8693ab635c447074c969f6573a0d0b0ca994219ae4`

`07_drive_frozen.tar.gz`
Drive id `1U-2yC7Yr55ljVoSFE5Qgmx_b3OX-rsU2`
SHA256 `370ea40962b078fc2fc09ab5319942b242f1559adeb62765e271f90cc21a9f59`

Original R1 package:
Drive id `1qP5ZtCnC-seOQIWDPkEYEGdISQooT0r0`
SHA256 `b6b7923f2e9623f5e1d46dda523f8f4a2919b62f69e82ba5b2bb679ad9771ae8`

Independent audit package folder supplied by coordinator:
`https://drive.google.com/drive/folders/1_aV9mhfAXm1y0DXfQ9UQ4SwsVpINAawE`

## Forbidden actions

- no representation refit;
- no evidence remapping;
- no new text preprocessing;
- no new threshold/metric selection after seeing results;
- no E2/new codec work;
- no Task4F1 access;
- no change to main/frozen branches;
- do not reuse R1 min-gold competition rows as corrected output.

Task4F1 remains:
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

## Mandatory byte gates

Before computation, SHA256 all four Drive inputs above. Abort on any mismatch.

Inventory must reproduce at minimum:
- LME cache_repr: 470 pickle files;
- LoCoMo: 10 representation pickles;
- REALTALK: 10 RT representation pickles;
- PerLTQA: archive/query evaluation caches present.

## Headline gates before competition analysis

Reproduce:
- LME SIGN `0.5419751773049645`; float `0.4415957446808511`.
- REALTALK SIGN `0.22477507598784194`; float `0.17253405381064954`.
- PerLTQA SIGN `0.488941994930817`; float `0.551692074528853`.
- LoCoMo SIGN `0.23654714666441054`; frozen-cache centered float `0.16826334541318252`.

If any accepted gate differs by >1e-12 where it is an accepted exact anchor, abort. LoCoMo centered float is an exploratory frozen-cache candidate rather than an old accepted anchor; independently derive and report it.

## Only repair to execute

For every query, build TOP64/BOT64 from stable descending archive-side `mean(C^2)`.

For every gold row g SEPARATELY compute TOP64 and BOT64 ranking competition. Never collapse to `min(distance[gold])`.

Primary per-gold all-row metrics:
- count rows strictly closer than each gold's distance;
- count rows tied at each gold's distance;
- arithmetic mean over gold rows within the query;
- gap = TOP64 minus BOT64.

Also compute the mandatory non-gold-only sensitivity variant.

Use average-rank Spearman.

Expected primary point coefficients:
- LME strict `0.14168629605302735`; tie `0.14045379360271315`.
- REALTALK strict `0.097939128891117`; tie `0.12281952421315011`.
- PerLTQA strict `0.25416826537535475`; tie `0.2797878341571222`.
- LoCoMo strict `0.09491957131277647`; tie `0.10376015063205302`.

Expected multi-gold counts:
- LME 296/470
- REALTALK 386/705
- PerLTQA 2322/8265
- LoCoMo 432/1535

PerLTQA sections must reproduce:
- dialogues strict `0.13054126734088975`; tie `0.11123087254360414`
- events strict `0.39790634780463613`; tie `0.38922832069574037`
- profile strict `0.0573253028779693`; tie `0.018738683422868593`
- social_relationship strict `0.30428515802019`; tie `0.2993013213223269`

A mismatch is a stop condition; do not tune definitions to hit expected values.

## Bootstrap

Regenerate from corrected rows only:
- B=2000
- seed=96013
- cluster resampling by archive/conversation where multiple queries share a cluster
- recompute average-rank Spearman per replicate
- percentile 2.5% / 97.5%
- record attempted/valid/invalid replicate counts and invalid reasons
- label all intervals descriptive/post-hoc.

## Persist exact outputs

Create a new output folder, preferably under the coordinator-provided audit folder, named:
`E1_V2_RAW_CACHE_RECOVERY_R2_2026-09-13`

Persist:
1. `E1_V2_COMPETITION_PER_QUERY_R2.json.gz`
2. `E1_V2_COMPETITION_SUMMARY_R2.json`
3. `E1_V2_COMPETITION_BOOTSTRAP_R2.json`
4. `INPUT_HASHES.json`
5. executable script(s)
6. `EXECUTION_LOG.txt`
7. `HASHES.json`
8. `HASHES.json.sha256`
9. one immutable ZIP of the folder.

Then add only the compact review/provenance surface to a NEW additive GitHub commit on the R2 branch. Large per-query payload stays SHA-bound in Drive.

Do not overwrite R1 or independent-audit artifacts.

## Required final state

Report:
- exact GitHub R2 final commit;
- Drive folder/file IDs;
- ZIP SHA256;
- corrected point estimates and bootstrap intervals;
- any mismatch/failure;
- `main unchanged`;
- `Task4F1 unchanged`.

Do not call the result PASS. It remains a repair candidate until a separate cold-start independent re-audit.
