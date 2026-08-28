# V52 Task 4C3 — Independent Hash Verification Log

Audit date: 2026-08-28  
Pinned compute commit: `7959c1df46b09f48bdbd1d1922bf62715e119839`

## Direct canonical Drive bytes

| Artifact | Independent SHA256 | Result |
|---|---|---|
| `V52_T4C3_PRE_RUN_SEAL.json` | `c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97` | PASS |
| `v52_t4c3_coordinate_axis_probe.py` | `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996` | PASS |
| `V52_T4C3_POST_RUN_MANIFEST.json` | `7bfeae589ffdf86012c04eec02017918cae92c3fa20a699c8d342f4baa39c00c` | recorded independently |

Post-run manifest binding:
- `pre_run_seal_sha256` matches the independently hashed seal.
- `pre_run_script_sha256` matches the independently hashed sealed script.
- `final_script_sha256` equals `pre_run_script_sha256`.

## Manifest-declared output hashes

The canonical `V52_T4C3_ALL_OUTPUTS.zip` was fetched and extracted. Every manifest-declared output was independently SHA256-hashed.

**Result: 26/26 PASS, 0 mismatch.**

| Artifact | Expected SHA256 | Result |
|---|---|---|
| `V52_T4C3_PRE_RUN_SEAL.json` | `c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97` | PASS |
| `v52_t4c3_coordinate_axis_probe.py` | `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996` | PASS |
| `V52_T4C3_INPUT_CHECKS.json` | `483323b059642cc49db06c3b2765a75bc924edf1b695f3f94e34f62098d9907b` | PASS |
| `V52_T4C3_trial_results.csv` | `22abc1447a362b36ecbb8bebb2cfa0ca2fbdf5480e50d8e2d8305e62e925337e` | PASS |
| `V52_T4C3_question_level.csv` | `51b8ee69126c0478649728a64891ccff0ffade0bb7d428940a1759a785ccc933` | PASS |
| `V52_T4C3_aggregate.csv` | `ab8b7233ae390c9aa977621093027a4ad1b6f63833bd33b5eec40acad02f39fe` | PASS |
| `V52_T4C3_rotation_seed_results.csv` | `bc6919e65f47a58bd87ffc8a8dc554eb7ef3a97ddcce5976396cc10fcc3ff4ea` | PASS |
| `V52_T4C3_block_gradient.csv` | `234cb0e3a2108ee3a93ef1011904cac99ad359a7a540b396ea153eaaaf748001` | PASS |
| `V52_T4C3_continuous_invariance.csv` | `7d46f435b10297e229c9c7516700a42c3123907c18fe76a6ae581a3db6818da2` | PASS |
| `V52_T4C3_signed_permutation_control.csv` | `e6bcf1f797fef1d44d83fbe97bc73e8312ff56a331bbf45494ff2b459bed5fca` | PASS |
| `V52_T4C3_native_heterogeneity.csv` | `148ae5b727ce1aedc6c84ee9c00727f1454b0e0710d100ac8154fdf8d00924cb` | PASS |
| `V52_T4C3_rotated_heterogeneity.csv` | `2651fe7d2074a4a780e2038fcbb484241e0b785dcd69876247352d3f150d59d4` | PASS |
| `V52_T4C3_heterogeneity_quintiles.csv` | `bd97eefda47aa502ec7bf02d4c1b0bad5c250b0527dab28bf84ed7442c253f2a` | PASS |
| `V52_T4C3_heterogeneity_alignment.csv` | `e820f758073cfffde6fe6a69812daea0f411cd8eb5742d2043db80e4b4d5745f` | PASS |
| `V52_T4C3_rank_geometry.csv` | `b3b2d52c775c0a2a033b0690918c523b7879af3d7c3c3fcb6237b8285af6731b` | PASS |
| `V52_T4C3_collision_diagnostics.csv` | `57a6575f50c619d3f5b696ab918aa22d56db95002ad9da793431b2613d2f6220` | PASS |
| `V52_T4C3_tie_diagnostics.csv` | `64e2892c9498d66e6bc7d0d46197c2929f876ab786eef8f8d3516317a7177637` | PASS |
| `V52_T4C3_ITQ_HAAR_ENVELOPE.csv` | `a99d49f54f0ef0a19946f62404abbc3691562584c9ee6b13a4206ec58c45c40b` | PASS |
| `V52_T4C3_question_type.csv` | `faded323e1da0beaafcad1961a4a96a340333343947a92e100d633fdd478b82c` | PASS |
| `V52_T4C3_gold_cardinality.csv` | `0a3f2b36624502450ff0c96b8f9c9c18a72607eb10532fb032aa3a305393e7ad` | PASS |
| `V52_T4C3_archive_size.csv` | `a62018f177711adadf89b0840318e8f0082c38fed7d3f52bcf3c8779f62dc748` | PASS |
| `V52_T4C3_reuse.csv` | `20a07f039cf1afea90303102a39b8c44daf5849d556b0278aa3116faf17e31b5` | PASS |
| `V52_T4C3_sanity_checks.csv` | `9223ff38ece351b3b2dc42e872ca6fbedc9140d7a17b53b0edfac642fe4745de` | PASS |
| `V52_T4C3_leakage_audit.csv` | `63e45c74e5afef617e7cd28423c6278f20f13c2e685ce502990e346e0241cb6a` | PASS |
| `V52_T4C3_COMPUTE_REPORT.md` | `610ba1dcd181cbf921209fa16dde246dda1c1f0619a3afd8c732963e581ecdef` | PASS |
| `V52_T4C3_HEAD_RESEARCHER_HANDOFF.txt` | `f1c05463436e202dfd06c13d29385fd10dc7106c5ae72ba55a17a6879187e95b` | PASS |

## Bounded provenance conditions

Dataset expected SHA256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`; expected size: `277383467` bytes. The sealed Task 4C3 runtime input gate records a match, but this audit environment did not independently download and re-hash the full dataset.

Adapter expected SHA256 values:
- v1: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- v2: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`

Both adapter source files were independently inspected at the pinned Git commit. The sealed runtime input gate records exact SHA matches, but this audit environment did not independently compute SHA256 from separately downloaded GitHub raw adapter bytes.

## Governance observation

`CHAIN_OF_CUSTODY.md` and `tools/verify_frozen_artifacts.py` still contain stale Task 4C2-era statements/coverage. This should be repaired separately. It is not a mismatch in the frozen Task 4C3 bytes and has quantified effect `0.000 pp` on `D96`.
