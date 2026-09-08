# Approved one-question gold exception and actual preflight

User explicitly approved the preceding proposal: only locomo_4_qa18 uses its six
historically resolvable references while preserving the accepted1535 cohort. This
is an author record of chat approval, not an independent signed decision.
Base72467979a794a89c44213687786fbb242863025b. Prior failed preflight preserved.

The exception is not a generic partial-gold option. It requires the exact target
question, absence of a correction record, the SHA256 of the seven normalized
references, SHA256 of the one missing reference, and SHA256 of the ordered680
archive IDs. Canonical digest input: UTF-8 json.dumps(value, ensure_ascii=True,
separators=(',', ':')). Those identities were derived from the hash-verified
pinned corpus before scoring; no answers, question text or ranking were used.

Only a copied effective evidence list changes. Original source, corrections,
cohort and archive mapping are unchanged. Original declared7/unresolved1 and
authorized omitted1 are retained explicitly in the result alongside effective6.
The unchanged source contract resolves every question afterward. Other missing
or empty gold still stops the complete call. Any mismatch to the narrow binding
also stops; the exception cannot be borrowed by another question.

preflight.py is an additive copy of the prior committed preflight, with the
exception wrapper substituted at gold resolution and explicit exception reporting.
Old namespaces, main, state and ledger are untouched.

Actual source preflight PASS WITH APPROVED EXCEPTION: ten correction-file
identities match,156 correction records parse, corpus identity matches,1535
questions resolve,155 selected questions have correction replacement. The target
question's historical exception is counted separately, not as an audit correction.
No representation fitting, ranking, scores, bootstrap, pilot, HMAC or seal.

Seven stdlib synthetic tests PASS under approved Python3.13.15 -B: exact exception,
no input mutation, other-question unresolved refusal, unexpected correction-record
refusal, changed seven-reference list refusal, changed archive-order refusal,
wrong missing-reference hash refusal, target-absent refusal (some share methods).
Tests substitute synthetic reference/archive hashes only with unittest patches;
there is no production override argument or environment setting for those pins.

A separate subagent statically reviewed exception.py and its preflight call-site,
found no confirmed scope leak/blocker, and verified preservation of original7/1
versus effective6 reporting. It did not rerun tests or verify runtime counts.
This is a parent-authored review summary, not a full independent acceptance.

This closes the specific observed LoCoMo gold gate. It does not mean the actual
membership experiment ran or the production driver/pre-run review is complete.
Existing user intent to execute remains recorded; no repeat run-intent approval
is required by this document. Separate BEAM Task4F1 is unaffected.
