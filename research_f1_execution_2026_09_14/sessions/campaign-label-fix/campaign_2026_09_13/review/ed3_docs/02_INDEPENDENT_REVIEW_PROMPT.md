[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# 02 — INDEPENDENT REVIEW PROMPT (copy this block into the reviewer LLM's session)

---

**You are an independent reviewer.** A research programme ran an exploratory pilot ("axis attack")
on a frozen retrieval benchmark and claims a set of benchmark-scoped findings. Your job: **verify or
falsify the claims from the artifacts in this bundle**, with no access to the producing session's
reasoning. Everything you need is local; no network required.

**Stance:** adversarial but fair. Trust nothing the bundle does not demonstrate. Prefer runnable
checks over prose. When something is claimed but not checkable from the bundle, say so explicitly —
do NOT assume it true, do NOT assume it false.

**Read first (in order):**
1. `00_READ_ME_FIRST.md` — orientation + headline table.
2. `01_CANONICAL_STATUS.md` — full numbers, verification records, limits, NOES.
3. `pilots/axis_attack_2026-09-12/REPORT.md` — the pilot's own full report.

**Then perform these checks (each: PASS / FAIL / CAVEAT + evidence you produced):**

1. **Integrity.** Run both hash manifests (see `03_VERIFY_COMMANDS.md`). Every entry must verify.
   Report any mismatch verbatim.
2. **Consistency (stdlib).** Run `python3 verify_pilot.py`. It re-derives, from the shipped files:
   the 470-question gate (per-question map vs frozen CSV, aggregate recompute), the per-axis
   drop/`alone` identities, the E4 gap arithmetic and ordering (matched < random < antimatched),
   the corrections tags, and a set of claim greps into REPORT.md. Any FAIL = finding.
3. **NumPy spot-recomputation (optional but recommended).** Run `python3 verify_sample_numpy.py`
   against the 32 shipped matrices: per-question native FR must reproduce the stored values
   exactly; the two 32-sample arm means are informational (compare to the full-470 values in
   `01_CANONICAL_STATUS.md` §B and state the deviation).
4. **Claim-vs-file agreement.** Walk the headline table in `00` and §B–§E of `01`; for each number,
   find the file+field that backs it (`pilot_results.json`, `pilot_results_corrections.json`,
   `per_axis*.csv`, `diagnostics*.json`, `extra_arms.json`, `probe48.json`). Any unbacked number =
   finding.
5. **Overclaim hunt.** Read §G limits of `01` and §5 of REPORT.md. Then search all documents for
   any statement *stronger* than the limits permit — e.g. cross-benchmark generalizations
   ("retrieval depends on…" without "in this benchmark"), causal language about the mechanism,
   "verified" claims that are sample-level, unreported seed scatter. List every instance with file
   + line context.
6. **Corrections-landed check.** The pilot went through an adversarial design review whose 2 defects
   and 6 caveats were claimed fixed. Verify at least: (a) gold-informed fields are tagged in
   `pilot_results_corrections.json`; (b) no arm labeled `IDXSTRIDE64` is used as a 64-bit arm
   anywhere (the old mislabeled arm must be gone/annotated); (c) tie-pool normalization exists
   (`per_axis_v2.csv` columns) with the correlation caveat; (d) seed-scatter ranges appear wherever
   random-arm means appear in REPORT.md; (e) E4 uses 5 seeds × 3 arms.
7. **Free hunt.** Anything else misleading, unsupported, or internally inconsistent. Also state
   what the bundle CANNOT demonstrate (full-470 recomputation, byte-provenance of the matrices, the
   frozen programme's acceptance state) without calling it a defect.

**EDITION 3 supplement — additional checks for round 3 (all local):**

8. **Round-3 consistency (stdlib).** Run `python3 verify_round3.py` (bundle root). It re-derives
   from the shipped round-3 JSONs: the kill arithmetic and all three triggers; per-split gap
   recomputation from stored per-question arrays (incl. seed-literal formulas); SPREAD eff_k;
   LoCoMo counts; errata/banner presence; the F3 recheck log.
9. **Round-3 integrity.** `sha256sum -c pilots/axis_attack_2026-09-12/round3/HASHES_ROUND3_BUNDLE.txt`
   (38 entries; paths remapped for this bundle — the harness scripts live under `round3_sources/`).
10. **Round-3 claim-vs-file list** (spot each against the JSONs/reports in `round3/`): kill
    triggers (−1.25 pp / 2/10 / −0.15 pp); D2 AUCs (0.798 / 0.686); D3 Spearman (~0.097/0.075);
    c2 gains (+3.09 / +1.48 pp; random +1.83 / +1.14); D4 separations (LoCoMo 0.22966 > 0.21848 >
    0.20732). Also: every FAIL/C-numbered D5 finding has a disposition in `ERRATA_ROUND3_D5.md`.

**Known and resolved (verify but do not re-report as new):** D5's F1–F3 + C1–C9 (dispositioned in
ERRATA + per-session banners); D1V's two initial false "cannot-check" items (filled by
`round3/muse_sessions/d5/f3_rechecks.txt`); the SPREAD stride-2 cap artifact from round 2
(repaired in round 3; eff_k asserts in the shipped manifest/checker); round-3's two pre-declared
gate provenance notes (kill rule quoted in DENEY1_REPORT.md §HÜKÜM).

**Output format (reply with exactly this structure):**
1. `INTEGRITY:` one line (n/n checks, or failures verbatim).
2. `FINDINGS:` table — ID | check | verdict (PASS/FAIL/CAVEAT) | evidence (command + result) |
   severity (cosmetic/wording/coverage/substantive).
3. `UNSUPPORTED CLAIMS:` list (may be empty).
4. `NOT CHECKABLE FROM BUNDLE:` list with what would be needed.
5. `VERDICT:` one paragraph — do the artifacts support the headline findings, yes/no/partially, and
   the single most important thing a head researcher should know before using these numbers.

**Rules:** read-only; do not modify the bundle; answer in your working language (Turkish if the
request is in Turkish, English otherwise); tie every claim to file paths + fields.
