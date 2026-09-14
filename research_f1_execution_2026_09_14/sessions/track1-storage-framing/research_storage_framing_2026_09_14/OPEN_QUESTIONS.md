[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 4 — Open questions

PREPARED, NOT ACCEPTED. Each item says what would settle it and whether it is UNAVAILABLE-UNDER-SEAL or merely not-done.

## Q-1. Common-mode projector cost for the float reference (the verdict's load-bearing gap)

- Question: how much of the ~88 kB/archive projector is needed to encode *queries* for the FLOAT96 arm too? If most of it is common-mode, the MISLEADS sign-inversion overstates SIGN96-specific overhead.
- Settles by: a per-arm complete-package inventory (the revision's §4 gate) that reports preprocessing state separately for SIGN96-class and FLOAT96 arms. Definition input from HR on what counts as "arm-specific" vs "common infrastructure."
- Status: merely not done. No seal involved — it needs the runner + implementations, which are unbuilt/ungated, not sealed.

## Q-2. Complete serialized package per arm (index S0 + preprocessing + headers)

- Question: what is the true effective bytes/vector per arm per archive, measured as one serialized package?
- Settles by: executing the revision's §4 storage gate (synthetic S0/S(n) identities + archive-specific validation after authorized fitting). Historical faiss replay (R1) explicitly cannot close this; it needs the future runner (gate I1, OPEN per UNRESOLVED_DECISIONS.md).
- Status: merely not done (gates R1-closed/I1-open recorded in CURRENT_STATE.json `twelve_byte_prereg_revision_2026_09_12`).

## Q-3. Whether float16 (or zlib) storage preserves retrieval behavior

- Question: the cheapest projector format (34,453 B/vector) assumes float16 numerics; does retrieval survive the precision drop?
- Settles by: retrieval-quality measurement under Task4F1 authorization — gold labels + recall. That is the sealed experiment.
- Status: UNAVAILABLE-UNDER-SEAL. Blocked until Task4F1 runs; must not be probed by pilot. (The projector report correctly lists it as "bakılmadı.")

## Q-4. Frozen production artifact size

- Question: what did the actually-deployed/frozen projector weigh, as serialized?
- Settles by: locating the frozen artifact's physical serialisation — the pilot states it was never found. If unfindable in principle, the re-fit remains the best available proxy and its re-fit status must travel with every quotation (F-05 shows one file already drops it).
- Status: merely not done (possibly undoable). Not seal-blocked; it is a provenance search.

## Q-5. Median-convention ruling for quotable figures

- Question: median-of-effective (88,886) vs ratio-of-medians (90,257) vs mean-of-costs — which is the programme's quotable convention for shared-state figures?
- Settles by: an HR definition ruling (one sentence). The cost package already ruled mean-of-costs for the OPQ panel; the projector figure needs the same treatment.
- Status: merely not done. No experiment needed.

## Q-6. Downstream-quotation survey: does "12 bytes" travel without its qualifier?

- Question: do papers, handoffs, or talks quote the 12-byte figure where readers infer total footprint, despite L-088?
- Settles by: a text survey of downstream artifacts (no network needed for in-repo; network for external — currently unavailable to me).
- Status: merely not done. Would flip the verdict toward fully-MISLEADS if the qualifier is routinely dropped in the wild.

## Q-7. Per-query shared-state read cost (latency/RAM), not just bytes

- Question: the HONEST side's "marginal is operationally relevant" assumes shared state is read-once and cheap at query time. Is it?
- Settles by: a latency/RAM measurement of query scoring with shared state resident vs per-vector payload — needs the runner, not the seal (synthetic + timing suffices; no gold needed).
- Status: merely not done.

## Q-8. Global-projector deployment properties

- Question: the revision declares global sharing "different, untested." Would a single global projector even preserve the frozen geometry (gate) and retrieval behavior?
- Settles by: (a) gate check of a globally-fit projector (descriptive stats only — no seal needed); (b) retrieval comparison (sealed). Note Attack 4 already shows it would not reach 12 B/vector anyway, so (b) is moot for the budget question but live for the science question.
- Status: (a) merely not done; (b) UNAVAILABLE-UNDER-SEAL.

## Explicit seal-compliance record

No step of this work opened corpora beyond descriptive re-fit byte JSONs and the archive-cardinality column, no queries/gold/labels/embeddings, no retrieval IDs/distances/recall/metrics, no `run_archives`/`evaluate_archive`/`finalize_results`, no HMAC key, no authorization constructed, no BEAM contact. The one boundary-adjacent input — `V52_T4C2_feature_geometry.csv` N_archive column — is the same non-outcome input the sealed-exempt cost script uses, and only cardinalities were read. If any future step above marked "merely not done" would cross into gold/recall/ranking, it must STOP and await Task4F1 authorization.
