[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DELIVER 4 — How independent were these audits? (PREPARED, NOT ACCEPTED)

Programme bar (CLAIM — task statement of `docs/CONTINUITY_PROTOCOL.md:31-34`, confirmed
by my read of the "Parallel work" section in `docs/CONTINUITY_PROTOCOL.md` (VERIFIED:
the cold-start bullet reads "An independent auditor must be cold-start: it may read
committed artifacts and the audit prompt, but not another agent's claimed verdict or
private chat reasoning," and "The Head Researcher cannot call its own implementation
work an independent audit."): a cold-start auditor may read committed artifacts + the
audit prompt, but not another agent's claimed verdict or private reasoning; the
preparer cannot audit its own work. This document is PREPARED, NOT ACCEPTED.

## Audit 1 (raw-cache recovery, `010bcbb`, REQUEST_CHANGES) — strong recomputation, imperfect blinding

- **Re-derived numbers from raw inputs? YES (VERIFIED).** Three heavy archives + analysis
  ZIP hash-verified first (`match=True`, EXECUTION_LOG.txt), then headlines recomputed
  from the raw C96/qC caches — including a LoCoMo centered float (`0.16826334541318252`)
  the lead had never produced. Non-competition rows matched the lead exactly at
  `max_abs_diff 0`, which is convergence, not copying: the mismatch counts on
  competition rows (265/425/2315/385) prove a separately computed table.
- **Ran its own code? YES (VERIFIED).** `competition_variants.py` (95 lines) and
  `locomo_variants.py` (60 lines) are auditor-authored recomputation, not reruns of
  lead scripts.
- **Same-model-family limitation disclosed? NO — nothing found (VERIFIED search).**
  `git grep -iE "model|claude|codex|gpt|opus|sonnet"` over the audit namespace returns
  zero hits: no statement of which model executed, whether it differs from the lead's,
  or whether the session was zero-context. Independence therefore rests on bytes +
  method, not on executor separation.
- **Cold-start bar? PARTIAL, by the auditor's own disclosure (VERIFIED).** The mandatory
  Git scope query exposed target diff prose before the Stage-1 freeze (FINDINGS.json F6,
  status DISCLOSED). The auditor asserts no result JSON/derived output was intentionally
  inspected pre-freeze and froze+hashed its raw table first — credible, but the letter
  of "not another agent's claimed verdict" is bent: lead prose (which contains
  interpretations, if not the verdict string) was seen. The auditor labels itself
  "independently recomputed, not perfectly blind" — the honest rating, and mine too.

## Audit 2 (mechanism checkpoint, `ec40dc3`, PASS_WITH_FINDINGS) — strong reproduction + adversarial analysis, weaker re-derivation

- **Re-derived numbers from raw inputs? MIXED (VERIFIED).** The core act is *reproduction*:
  all 10 lead scripts rerun on a clean GitHub Actions runner (`34764744784`, SUCCESS
  after two infra-fails — VERIFIED in EXECUTION_LOG.txt) with committed-vs-fresh
  agreement ≤1e-12. That verifies the scripts do what they claim, not that the claims
  follow from independent reasoning. The genuinely independent layer is
  `independent_diagnostics.py` (260 lines, VERIFIED): exact-join checks,
  leave-one-type/character/chat-out attacks, dense-vs-average-rank variants, same-archive
  verification — which produced the report's adversarial findings (e.g. REALTALK
  dense-rank `+0.1266` vs average-rank `+0.0746`; category-3 LOO crossing zero).
- **Ran its own code? PARTLY (VERIFIED).** Own diagnostics: yes. But the 10 headline
  reruns execute the *lead's* scripts — a reproduction gate, weaker than Audit 1's
  from-raw-cache recomputation. The workflow (`.github/workflows/independent_e1_mechanism_audit.yml`,
  VERIFIED: ancestry/additive-scope gate, `contents: read`, numpy install, artifact
  hashing) is well-constructed for integrity but cannot detect a bug shared by the
  lead's scripts and the auditor's reading of them.
- **Same-model-family limitation disclosed? NO — nothing found (VERIFIED search).**
  Same zero-hit grep result as Audit 1. No executor/model/launch-context statement.
- **Cold-start bar? LETTER-OK, SPIRIT-UNCLEAR (my judgement on VERIFIED facts).** The
  branch was cut from the frozen target with an additive-scope gate (report §1,
  workflow-verified), and everything the auditor cites (checkpoint doc, result JSONs,
  source CSVs/NPZs) is a committed artifact — permitted. I found no evidence it saw
  another agent's verdict or private reasoning (the checkpoint doc carries a
  "CHECKPOINT CANDIDATE" status, not a verdict — VERIFIED). But I also found no
  affirmative evidence of a zero-context launch (no audit prompt pinned in the audit
  namespace; the `muse_prompts/` files on the branch are the campaign's lead prompts),
  so "cold-start" is assumed, not demonstrated. The auditor's own framing is careful —
  "mechanically reproducible enough to guide the next mechanism experiment" — which is
  the right size for a reproduction-plus-adversarial-analysis, and it explicitly refuses
  causal/confirmatory/deployable/Task4F1 upgrade.

## Plain verdict on the bar

Neither audit fully meets a strict cold-start standard *as demonstrated in the bytes*:
both lack any executor-separation or model-diversity statement, Audit 1 discloses a
blinding imperfection, and Audit 2's core is reproduction of the lead's own scripts
rather than independent re-derivation. Against what matters most, they are
complementary, not redundant: Audit 1 re-derived from raw bytes with its own code
(the stronger independence, honestly caveated); Audit 2 reproduced execution in a
clean room and attacked the conclusions adversarially (the stronger skepticism,
weaker independence of method). A future audit meeting the programme bar should pin,
in-namespace: the audit prompt's hash, the launcher's zero-context statement, the
executor model identity relative to the lead's, and a pre-freeze access log —
precisely the points both current audits leave to trust.
