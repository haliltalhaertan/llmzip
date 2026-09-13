[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Muse session — ADVERSARIAL DESIGN REVIEW of the axis-attack pilot

You are a fresh adversarial reviewer. Critique the DESIGN and CLAIMS of a local exploratory pilot
(not the arithmetic — a separate session recomputes the numbers). Read-only; scratch /tmp/pilotreview/.

## What to read

- pilot script: /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/pilot_axis_attack.py
- pilot results: /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/pilot_results.json
  (+ per_axis.csv, per_axis_matrices.npz in the same dir)
- frozen producer (protocol source of truth): /mnt/c/Users/MDP/dev/llmzip-work/drive/v52_t4c3_coordinate_axis_probe.py
- frozen reference outputs: /mnt/c/Users/MDP/dev/llmzip-work/drive/t4c3/*.csv
- benchmark context: /mnt/c/Users/MDP/dev/llmzip-work/reports/README context via
  /mnt/c/Users/MDP/dev/llmzip-work/TASK1_COMPLETION_RECEIPT.md (what the surrounding programme is)

## Questions to answer (each: FINDING / OK / CAVEAT with evidence)

1. **Protocol fidelity.** Compare the pilot's codes/distance/tie/ranking/metric implementation
   against the frozen producer's (evalq block and `met`/`rh` helpers). Any deviation — even
   benign — list it.
2. **Gate strength.** Is the E0 gate (per-question + aggregate reproduction) sufficient to trust
   the pipeline? What could still differ while the gate passes?
3. **Leakage audit.** For each experiment E1–E4: identify exactly what information was used to
   construct the codes/selection. Flag anything gold-informed and check it is *labeled* as
   analysis-only in the results JSON. E1's variance-prefix selection must be gold-free
   (verify). E2/E3 use gold — acceptable as analysis, but check the labels.
4. **Interpretation traps.** List the claims the pilot data does NOT support. Specifically:
   - "alone-FR" interpretation (tie-lottery effect: with a 1-bit distance, docs tie at d=0 en
     masse; FR ≈ 3/(tie-pool size) when gold agrees — the metric mostly measures agreement-set
     size, not "axis importance"). Is this handled in the results/labels?
   - E4 matched-vs-random pairing: what can and cannot be concluded from a same-rotations,
     different-order contrast?
   - E1 as "can we go below 96 bits": what is NOT shown (no alternative codecs, no
     learned selection, single benchmark, no multi-seed subsets except k∈{16,48}).
   - Any causal language that should be softened to descriptive.
5. **Frozen-NOES compliance.** The programme's earlier task listed what may NOT be done without a
   new preregistration (`NORES` list in the frozen producer: e.g. LoCoMo extension, alternate
   bit widths, learned thresholds, whitening, PCA rotations, variance reweighting, supervised
   rotation, reranking...). The pilot is explicitly labeled exploratory/local. Verify that:
   (a) nothing in the pilots directory claims citation-ready status; (b) the labels
   [LOCAL EXPLORATORY PILOT]/[NOT PREREGISTERED]/[NOT FOR CITATION]/[DISCLOSE-BEFORE-USE] are
   present in the results JSON and script; (c) list which NOES items the pilot approaches and
   what must be disclosed before any future preregistration.
6. **Missing cheap checks.** Identify any obvious control the pilot omitted that would materially
   strengthen or weaken the reading (e.g. duplicate-code statistics for the prefix arms,
   collision diagnostics; multiple random-subset seeds beyond 3; per-question win/tie/loss
   counts vs native). Rank by value.

## Report format

FINDINGS table (ID / area / verdict OK-CAVEAT-FAIL / one-line evidence), then:
- "Design verdict:" one paragraph (is the pilot sound AS an exploratory instrument, given labels).
- "Required corrections:" list (may be empty).
- "Before any preregistration:" list of disclosures/items the head researcher must carry over.
Read-only; no writes under /mnt/c; no network.
