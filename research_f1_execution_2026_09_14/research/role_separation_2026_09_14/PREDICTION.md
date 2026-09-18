[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# PREDICTION.md — written BEFORE step 2 (distributions) was run. NEVER EDITED.

Timestamp of writing: after step 1 (mapping proof) completed, before any Hamming/cosine/AUC/retrieval
number was computed. Corrections, if any, go in VERDICT.md §"Corrections to PREDICTION", not here.

## What was already known at the time of writing (VERIFIED, step 1 only)

- VERIFIED `build_archive` in `HEAD:adapters/longmemeval_v52_adapter.py:64-107` indexes EVERY turn of
  every haystack session. The only role logic is a validation branch
  (`if role not in {"user","assistant"}: issues.append({"code":"INVALID_ROLE",...})`) at line ~78,
  which records an issue and then **falls through and appends the record anyway**. There is no
  `continue`/`skip` on role. Same in `HEAD:adapters/longmemeval_v52_adapter_v2.py:19-48`.
  => The "no role filter" claim is CONFIRMED by reading. Both roles are indexed.
- VERIFIED LME row<->turn mapping: flatten `haystack_sessions` session-major, turn-minor.
  470/470 items have `C.shape[0] == sum(len(session))`, AND the cached `gold` row indices equal
  exactly the flattened positions of `has_answer==True` turns for 470/470 items (886 gold rows).
- VERIFIED LoCoMo: `id_to_row` maps "D<session>:<turn>" -> contiguous 0..N-1 in all 10 files.
- VERIFIED caches are already centered (LME col-mean absmax 1.55e-16). Do not re-center.

## Predictions (stated before measurement)

### P1 — Adjacency signal exists but is moderate, not "near-copy"
I predict adjacent turn pairs (i, i+1 within the same session) are measurably closer than random
pairs, but nowhere near duplicate. Concretely I predict mean Hamming for adjacent pairs in the range
**30–40 of 96**, random pairs at **~48 (chance)**, and AUC in the range **0.75–0.93**.

I specifically predict the relayed figures are TOO EXTREME: relayed Hamming 28 / AUC 0.955 /
cosine 0.77. A mean cosine of 0.77 between adjacent turns in a 96-D *centered* TF-IDF/SVD/ITQ-style
space would be an enormous amount of shared signal. My prediction is adjacent cosine lands
**0.35–0.65**, random cosine near **-1/(N-1) ≈ 0** (forced negative by centering).
REASON for expecting mismatch: the relayed numbers may have come from a different corpus (LoCoMo,
where a "turn" is a whole dialogue utterance with speaker-name prefixes) or from an uncentered
matrix. If LoCoMo and LME disagree, that is the finding.

### P2 — "Near-copy is FALSE" will REPLICATE
I predict the ≤16-bit tail is a very small fraction of all pairs (**< 1%**), and that a large
majority of that tail is NOT adjacent pairs. Rationale: a 96-bit code over an archive of ~500 rows
has ~125k pairs; the binomial null already puts almost no mass ≤16, so any mass there is structural,
but archives contain many topically-repeated turns that are not adjacent (same session, same topic,
recurring assistant boilerplate like list formatting and "Here are some tips"). Assistant
boilerplate, not speaker-pairing, is my favoured explanation for the ≤16 tail.

### P3 — Role asymmetry is small but I expect it to be LARGER than the relayed ~1 bit
I predict the two directions (user_i -> assistant_{i+1}, assistant_i -> user_{i+1}) differ by
**1–4 bits**, with the **user->assistant direction being CLOSER** (smaller Hamming). Reason: an
assistant reply restates and expands the user's question vocabulary, so the reply inherits the
user's content words; the following user turn more often introduces a new topic or a short
acknowledgement. I am not confident; if it comes out ~1 bit the relayed claim stands.

### P4 — Gold rows will NOT be disproportionately adjacent to other gold rows... weakly
This one I split. In LongMemEval, `has_answer` is annotated per turn and answers often span a
user question + the assistant answer, so I predict gold-gold adjacency IS enriched relative to
chance, by a large relative factor (**>5x chance**) though on small absolute numbers. This is a
prediction that the *annotation* is pair-structured, not that the *geometry* is.

### P5 — THE ONE THAT MATTERS: near-duplicate neighbours will NOT explain the sign-vs-float effect
This is the falsifiable core. The mechanism hypothesis under test is:
  "sign quantization confuses near-duplicate pairs, so queries whose gold row has a close non-gold
   neighbour should do WORSE under sign than under float."

I predict **NO such effect, or an effect of the wrong sign**, on LongMemEval.
Rationale: LongMemEval is the benchmark where SIGN *WINS* by +10.04 pp. If near-duplicate
confusion were the operative mechanism it would be a cost, and a cost cannot produce the largest
positive delta in the programme. For the hypothesis to explain the headline it would have to
predict that LME has FEWER near-duplicates than PerLTQA (where sign loses 6.28 pp) — a specific,
checkable corollary that I also doubt.

Quantitatively I predict: regressing per-query (FR@3_sign − FR@3_float) on the gold row's minimum
Hamming distance to a non-gold row yields a slope whose sign is **positive or indistinguishable
from zero** (i.e. having a close non-gold neighbour does NOT hurt sign more than float), with
|effect| < 3 pp across the tail-vs-bulk contrast, and that whatever raw effect appears does NOT
survive controlling for archive.

I ALSO pre-register the honest alternative: if near-duplicate gold neighbours turn out to HELP the
sign arm (delta increases when a near-duplicate is present), that is a real and interesting finding
and I will report it as such rather than as noise.

### P6 — Control
The FR@3 expectation formula will reproduce at least one frozen headline to <0.05 pp
(LME target +10.037943 pp frozen / +10.053783 pp expectation). If it does not, every downstream
number is suspect and I will say so.

## What would kill the "near-duplicate" story
- ≤16-bit tail is tiny AND mostly non-adjacent (P2 holds) => the "both speakers indexed creates
  near-copies" story is dead as stated, regardless of everything else.
- No sign-specific penalty for close-neighboured golds (P5 holds) => near-duplicates are not the
  mechanism, and candidate explanation #6 joins the five already dead.

## What would rescue it
- A close non-gold neighbour costs the sign arm >5 pp more than the float arm, surviving archive
  control, AND PerLTQA having more such cases than LME. I consider this unlikely but it is the
  thing I am looking for.
