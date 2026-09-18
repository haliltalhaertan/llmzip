[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — storage accounting pilot (PREPARED, NOT ACCEPTED)

- Namespace: `research_storage_accounting_2026_09_14/`
- Branch (own): `muse/track1-storage-cost` (base `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`) — VERIFIED (`git log --oneline -3`, 2026-09-14 session)
- Task4F1 SEAL: IN FORCE. No `--mode run/finalize`, no `run_archives`/`evaluate_archive`/`finalize_results` on real data, no `V52_T4F1_AUTH_HMAC_KEY_HEX`, no authorization construction, no retrieval IDs/distances/recall/metrics/arm outcomes, no corpora/queries/labels/embeddings opened. 804MB BEAM corpus absent, will NOT be fetched.
- Pure-additive rule: only new files under this namespace will be created. No existing file modified.
- Plan:
  1. STATUS.md (this file) — DONE
  2. Read projector pilot + audit + budget decision/finding + prereg branches + runtime replay + preseal cost worker (all via `git show origin/<branch>:<path>`, no checkout)
  3. COST_MODEL.md (formula + instantiation + break-evens)
  4. RECONCILIATION.md (12 B vs 88,886 B verdict)
  5. verify_cost.py + evidence/cost_results.json (stdlib-only recompute + sensitivity)
  6. IMPLICATIONS.md (symmetric, re-wording list with locators)
  7. REPORT.md + commit to own branch only
- Skeptic pre-commitment: headline assumption most damaging to conclusion = projector is SHARED across archives (amortized ~0) rather than PER-ARCHIVE. Sensitivity analysis will test exactly this.
- Receipt log:
  - 2026-09-14: namespace created; branch confirmed `muse/track1-storage-cost`.
  - Sources read via `git show` only (no checkout): projector JSON+report,
    audit TR, CURRENT_STATE budget keys, EVIDENCE.json + OPEN_ITEMS_CLOSED
    (`8217704`), REPLAY/ENV/COMPARISON/SUPPLEMENTARY (`9cd3f54`), Task2
    RESULTS/NOTES (`44ae95a`), prereg draft (`d2cfbaa` L41-42, L89),
    prereg revision §§1-4 (`a73393a`), ledger race sentences (main).
  - Seal receipts: no `--mode run/finalize`, no runner invocation, no HMAC key,
    no corpus/query/gold/embedding/metric bytes opened; BEAM corpus not fetched;
    no network, no installs. Pure-additive: `git status` shows only the new
    namespace (checked at commit time).
  - verify_cost.py: 9/9 PASS; evidence/cost_results.json written by the script.
