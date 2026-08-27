# V52 Task 3A.1 — Protocol Patch

Memory ID is `question_id::s<session_position>::session_id::t<turn_index>` with 0-based session_position. session_position is identity-only and excluded from memory text, feature fitting, distance, and tie priority.

Primary retrieval-recall cohort is exactly the 470 non-`_abs` questions. All 30 `_abs` questions are excluded from primary ANY/ALL/Fractional Evidence Recall, including the 9 questions carrying 10 residual positive turns; annotations are preserved.

Non-abstention zero-gold count: 0.

Dependency graph: 1 component(s), largest=470/470. question-level bootstrap cannot be interpreted as independent underlying-memory population inference.

No full96/M32/M64 comparative recall was computed.
