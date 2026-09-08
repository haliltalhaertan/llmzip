# Actual source/gold preflight: stopped before experiment

The user explicitly requested the real membership experiment, twice, following
5820bc6f70aa41e0d3559e3797c83ab173be46e4. This author records that authorization
as covering necessary actual source/gold checks. It does not silently waive the
previously approved fail-closed unresolved-gold rule. Separate BEAM Task4F1 is not
being executed. Old candidate files and main/state/ledger remain unchanged.

Actual checks executed with approved Python3.13.15 -B against local source files:
work/locomo_reproduction_tmp_20260907/preflight_source_bytes/locomo10.json and
its audit/errors_conv_0.json through errors_conv_9.json. No download or external
model call. Source identities and accepted cohort loaded from committed Git.
Reader executed from SHA256-verified5a1dc16 source, gold contract from
SHA256-verified56e6701 source. No producer module was imported.

Results: all10 correction file identities match; strict parser accepts156 records;
raw corpus bytes/hash match; all1535 accepted IDs processed. Gold contract refuses
E-S-014. Diagnostic second pass identifies exactly one affected question:
locomo_4_qa18, no correct_evidence replacement, seven declared unique references,
six found in its own archive and one not found. All other1534 selected questions
have nonempty fully resolvable effective gold in this preflight.

Initial source preflight stopped E-S-014. A second source-only run added counts
and the canonical accepted question ID; it did not fit representations or produce
retrieval outputs. PREFLIGHT_RESULT.json records that run. Shell tool reported
nonzero exit1; the script's direct stop branch returns3. No successful run claim.

Historical semantics explain the mismatch: at692f599e,
research/v52/locomo_coordinate_scale.py calls base.gold_rows; that function is
research/v52/locomo_spectral_band_haar_causal.py lines70-71 and filters reference
IDs by membership in id_to_row. Thus the historical rule would retain this question
with six resolvable gold units. The newer explicitly approved contract instead
requires complete resolution and stops. This source-level comparison is not a
new retrieval result or a recomputation of the historical experiment.

A separate subagent independently verified the corpus and ten correction hashes,
then checked this question without reusing the parent's session-row construction.
It found680 distinct IDs and zero duplicate IDs across list-valued conversation
fields, six of seven reference IDs present, and zero correction records for this
question. It did not independently recheck the other1534 questions. This is the
parent's summary of its returned structural verification, not a signed full audit.

No resolution has been selected. Options require explicit scientific disposition:
retain the current hard stop, authorize a precisely documented question-specific
historical-six-reference exception, or revise the cohort and its reference binding.
Do not silently drop a reference or a question; do not pretend the new strict
contract and historical filtering are identical. No modified code or re-run after
such an exception has been authorized by this record.

No representation fitting, ranking, metrics, bootstrap, pilot, HMAC or seal.
This is a real-data preflight finding, NOT an experiment result. The production
driver/acceptance work remains incomplete in addition to this concrete data gate.
