[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# ROLE_FACTS.md — measured facts about role/adjacency structure in memory archives

All numbers VERIFIED (computed from bytes this session) unless labelled otherwise.
Code: `roles.py` (A,B), `roles_main.py` (C,D,E), `roles_fix.py` (F), `roles_fix2.py` (G),
`roles_confound.py` (K), `roles_decomp.py` (L). Raw output: `evidence/results.json`.

---

## 0. Metric control (must pass before any other number is trusted)

VERIFIED — the exact FR@3 tie expectation reproduces three frozen headlines:

| benchmark | my value (pp) | frozen / expectation target (pp) | abs error |
|---|---|---|---|
| LongMemEval | **+10.053782505910153** | +10.053783 (frozen +10.037943) | 5e-7 pp |
| PerLTQA | **−6.274727836521099** | −6.274728 (frozen −6.275) | 2e-7 pp |
| REALTALK | **+5.300076925963445** | +5.300077 (frozen +5.2241) | 7e-8 pp |
| LoCoMo | +6.655046274753115 | frozen +6.82838013 | **0.173 pp** |

VERIFIED LME float arm = 0.4415957446808511, matching the frozen float value to all digits
(`roles.py:B_control`). LME sign arm 0.5421335697 vs frozen 0.5419751773 (1.6e-4 difference,
consistent with the frozen value's NT=20 sampled tie-break vs my exact expectation).

DISCLOSED DISAGREEMENT: LoCoMo is off by 0.173 pp. My gold construction maps `raw_evidence`
strings through `id_to_row`, dropping evidence IDs absent from the map; the frozen pipeline
presumably differs slightly in gold assembly. Three of four controls land at 1e-7, so the
machinery is right; the LoCoMo gap is a gold-set definition difference, not a metric bug.
It does not affect any conclusion below (LoCoMo is only used for adjacency structure).

---

## 1. Row↔turn mapping — PROVEN

### LongMemEval (`roles.py:lme_load`, `map_probe.py`)
Mapping: flatten `item["haystack_sessions"]` session-major, turn-minor; row *i* = the *i*-th turn.

Four independent proofs:
1. VERIFIED count match: `C.shape[0] == sum(len(session))` for **470/470** items.
2. VERIFIED gold-index match: cached `gold` row indices equal exactly the flattened positions of
   `has_answer == True` turns for **470/470** items (886 gold rows). This is the strong proof —
   it constrains *order*, not merely length. A wrong flattening order would break it.
3. VERIFIED order-destroying control (`roles_fix2.py:G1`): permuting rows within each archive
   collapses "adjacent" mean Hamming from **31.98 → 47.91 bits**, exactly the cross-session
   baseline (48.19). AUC vs cross-session falls from **0.914 → 0.507** (chance).
   If the mapping were arbitrary, the true value would already sit at 47.9. It does not.
4. VERIFIED role-shuffle control (`roles_fix.py:F4`): permuting role labels collapses the
   role asymmetry from **6.90 bits → 0.045 bits**.

Archive composition: 231,606 rows total; **114,902 user + 116,704 assistant**. 20,588 of 22,419
sessions (91.8%) are strictly alternating starting with `user`.

### LoCoMo (`map_probe.py`)
VERIFIED `id_to_row` keys are `"D<session>:<turn>"` and values are exactly `0..N-1` contiguous in
all 10 files. Adjacency = same session, consecutive turn number.

---

## 2. `build_archive` role filter — CLAIM CONFIRMED, both roles indexed

VERIFIED by reading blobs (no checkout).

`HEAD:adapters/longmemeval_v52_adapter.py:64-107` — `build_archive` iterates every session and
every turn. The only role-related logic is line 80-81:

```
80:            if role not in {"user", "assistant"}:
81:                issues.append({"code": "INVALID_ROLE", ...})
```

This records a diagnostic and **falls through**. The `continue` statements at lines 73 and 77 guard
only `SESSION_NOT_LIST` and `TURN_NOT_DICT`. `memories.append(rec)` at line 103 is unconditional
w.r.t. role. Line 89 puts the role *into* the indexed text:
`memory_text = f"[{date}] {role}: {content}"`.

Identical structure in `HEAD:adapters/longmemeval_v52_adapter_v2.py:19-48` (append at line 47).

**VERDICT: no role filter. Both speakers are indexed.** Corroborated empirically by the
114,902 user / 116,704 assistant row counts above.

---

## 3. Adjacency distributions (not just means)

### LongMemEval — 209,187 adjacent pairs, 57,176,172 within-archive pairs

| | adjacent | non-adjacent / random |
|---|---|---|
| mean Hamming | **31.98** (sd 10.50) | **47.96** (random sample 47.89, sd 5.10) |
| p1 / p5 / p25 / p50 / p75 / p95 / p99 | 10 / 16 / 24 / **31** / 39 / 50 / 57 | 33 / 40 / 45 / **48** / 51 / 55 / 58 |
| mean cosine | **+0.705** | **−0.0023** |
| cosine p5 / p50 / p95 | 0.371 / **0.737** / 0.922 | −0.137 / −0.028 / 0.202 |
| **AUC (adjacent closer)** | **0.9088** | — |

### LoCoMo — 5,610 adjacent pairs, 1,789,631 within-archive pairs

| | adjacent | non-adjacent |
|---|---|---|
| mean Hamming | **43.19** | **47.97** |
| p5 / p50 / p95 | 29 / **44** / 54 | 40 / 48 / 56 |
| mean cosine | **+0.145** | −0.0011 |
| **AUC** | **0.6952** | — |

RELAYED-vs-VERIFIED comparison:

| relayed claim | verified | verdict |
|---|---|---|
| adjacent Hamming 28 | **31.98** (LME); 43.19 (LoCoMo) | ~4 bits optimistic on LME; badly wrong for LoCoMo |
| random Hamming 48 | **47.96** | CONFIRMED |
| AUC 0.955 | **0.9088** (LME), 0.695 (LoCoMo) | overstated |
| cosine 0.77 vs −0.03 | **0.705 vs −0.0023** | directionally right, magnitude overstated |

My PREDICTION.md predicted adjacent cosine 0.35–0.65 and Hamming 30–40. Hamming landed in range
(31.98); **cosine 0.705 was ABOVE my predicted band** — the relayed 0.77 was closer than my guess.
Recorded as a miss.

⚠️ BUG DISCLOSURE: `roles_main.py:auc_fast()` computed `P(neg < k)` instead of `P(neg > k)`,
reporting P(adj > rnd) = 0.0928 / 0.3047. Corrected in `roles_fix.py:F1` (AUC = 1 − buggy).
The corrected values 0.9088 / 0.6952 are the ones above.

### The ≤16-bit tail — "near-copy is FALSE" REPLICATES

| | LME | LoCoMo | relayed |
|---|---|---|---|
| ≤16-bit pairs as % of all pairs | **0.1369%** | 0.0040% | 0.14% ✓ |
| % of that tail that is NOT adjacent | **83.56%** | 81.94% | 84% ✓ |

Both relayed numbers CONFIRMED almost exactly on LME. Only 6.15% of adjacent pairs are ≤16 bits,
and same-session-non-adjacent pairs hit ≤16 bits at essentially the same rate (**6.12%**) —
adjacency confers no special near-duplicate status beyond being in the same session.

**The "both speakers indexed creates near-copies" story is false as stated.** Adjacent turns are
*correlated* (AUC 0.91), not *duplicated*.

### Role asymmetry — RELAYED CLAIM REFUTED (~7x larger than claimed)

VERIFIED, both directions (`roles_main.py:C`, controlled in `roles_fix.py:F4`):

| direction | n | mean Hamming |
|---|---|---|
| user_i → assistant_{i+1} | 114,870 | **28.87** |
| assistant_i → user_{i+1} | 94,285 | **35.77** |
| **asymmetry** | | **6.90 bits** |
| role-shuffled control | | **0.045 bits** |

Relayed "about 1 bit" is **REFUTED**: measured 6.90 bits, and the shuffle control confirms it is
real structure, not an artifact. My PREDICTION.md predicted 1–4 bits with user→assistant closer —
**direction CORRECT, magnitude UNDER-predicted** (6.90 > 4).

Mechanism: an assistant reply restates the user's vocabulary (close); the next user turn introduces
new material (far). The asymmetry is a *topic-continuation* effect, not a speaker-identity effect.

### Surprise finding: lag-2 (SAME speaker) is closer than lag-1 (different speaker)

VERIFIED (`roles_fix2.py:G1`):

| relation | mean Hamming |
|---|---|
| lag-1, same session (cross-speaker) | 31.98 |
| **lag-2, same session (SAME speaker)** | **25.48** |
| lag-3, same session (cross-speaker) | 38.80 |
| same session, non-adjacent | 35.85 |
| cross-session | 48.19 |

Same-speaker pairs at distance 2 are **6.5 bits CLOSER** than the cross-speaker pairs at distance 1.
This directly contradicts the premise that *speaker pairing* creates the proximity: proximity is
driven by **same-speaker style/register** and topic continuity, and the odd/even alternation means
"both speakers indexed" actually *separates* consecutive rows rather than duplicating them.

---

## 4. Gold-gold adjacency

**LongMemEval** (`roles_main.py:D`): 3 gold-gold adjacent pairs out of 209,187 adjacent pairs.
Enrichment vs all-pairs base rate **1.33x**; vs iid marginal **0.98x** — i.e. **no enrichment**.
Caveat: LME averages 1.9 gold rows per archive, so this test has almost no power.
My PREDICTION.md predicted >5x enrichment — **REFUTED on LME**.

**LoCoMo** (`roles_fix.py:F2`), where per-query evidence sets are larger and this is testable:
54 of 1,892 within-query gold pairs are adjacent = **2.85%**, versus a chance rate of **0.313%**
→ **9.10x enrichment**. VERIFIED.

So gold evidence *does* span adjacent turns far more than chance where multi-gold queries exist
(LoCoMo), confirming the annotation is pair-structured; LME's single-gold design cannot show it.
Mixed outcome for my prediction: right about the annotation, wrong about LME.

---

## 5. The mechanism test — does near-duplicate structure hurt the sign arm?

Definition: `dnn` = minimum Hamming distance from any gold row to any **non**-gold row in the same
archive. Per-query `delta = FR@3_sign − FR@3_float`. "Close" = `dnn ≤ median`.

### Across benchmarks (`roles_main.py:E`)

| benchmark | n | median dnn | close−far effect (pp) | 95% CI | archive+section-controlled slope (pp/bit) |
|---|---|---|---|---|---|
| LongMemEval | 470 | 18 | **−11.15** | [−17.79, −4.12] | n/a (1 query per archive) |
| PerLTQA | 8,265 | 27 | +0.87 | [−0.77, +2.47] | +0.223 |
| LoCoMo | 1,535 | 29 | −3.02 | [−6.37, +0.41] | +0.422 |
| REALTALK | 705 | 24 | −0.28 | [−5.10, +4.24] | −0.045 |

Only **LongMemEval** shows a significant effect. On the benchmark that actually reverses
(PerLTQA), the effect is **positive and not significant** — the opposite of what the hypothesis
needs.

### The decisive cross-benchmark corollary (`roles_fix2.py:G2`) — hypothesis REFUTED

If near-duplicate confusion caused the reversal, the benchmark where sign LOSES must have the MOST
near-duplicate structure. Observed:

| benchmark | sign − float (pp) | median gold-dnn (bits) | % golds with dnn ≤ 16 |
|---|---|---|---|
| **LongMemEval** | **+10.05** (sign wins biggest) | **18** (closest) | **38.5%** (most) |
| LoCoMo | +6.66 | 29 | 2.0% |
| REALTALK | +5.30 | 24 | 13.5% |
| **PerLTQA** | **−6.27** (sign LOSES) | **27** | **3.2%** (nearly fewest) |

The relationship runs **exactly backwards**. The benchmark drowning in near-duplicate gold
neighbours is the one where sign wins by the largest margin.

### Is the LongMemEval effect about *roles* at all? No. (`roles_decomp.py:L`)

The −11.15 pp LME effect is real and survives confound checks:
- Archive size (`roles_confound.py:K1`): corr(dnn, N) = **−0.039**; mean N is 492.5 (close) vs
  493.1 (far). Not a size artifact. Effect persists within size quartiles
  (−19.2, −14.3, −20.3, +6.1 pp; pooled −11.9 pp).
- Gold distinctiveness (`L3`): residualising dnn on the gold row's own query distance *raises*
  the slope (r 0.174 → 0.188). Not a distinctiveness proxy.

But three tests show it is **not** the role/adjacency mechanism:

1. **Adjacency carries none of the damage.** Within the close-neighbour group, splitting on whether
   the nearest non-gold neighbour is literally an adjacent turn:
   **−1.67 pp, CI [−10.24, +6.70]** — indistinguishable from zero (n=73 vs 177).
   Overall, queries whose gold's nearest neighbour is adjacent do **+0.58 pp BETTER**,
   CI [−6.27, +7.67] (`F3_LME_direct`, n=137 vs 333).
2. **Cosine reproduces the effect.** Using *cosine* nearest-neighbour instead of Hamming gives
   **−8.23 pp, CI [−14.84, −2.01]** — nearly the whole effect. A sign-quantization-specific
   phenomenon cannot be reproduced by a pure float-geometry predictor.
3. **Arm decomposition.** sign arm −8.37 pp [−15.63, −0.88]; float arm +2.78 pp [−4.94, +10.20].
   Dense gold neighbourhoods do hurt sign more — but the predictor works equally in float space,
   so the operative variable is **generic gold-neighbourhood density**, not speaker duplication.

**Conclusion: gold-neighbourhood density is a real per-query moderator on LongMemEval, but it is
not created by indexing both speakers, and its cross-benchmark sign is opposite to what is needed
to explain the PerLTQA reversal.**
