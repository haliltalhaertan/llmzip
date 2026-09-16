# CASE AGAINST continuing llmzip as a retrieval-code programme

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Claim-tag legend (used on every claim below): [BRIEF] = taken from the 2026-09-16
decision brief without independent re-execution; [CHECKED] = I recomputed it by
re-doing the arithmetic on the brief's own numbers in this session (method cited);
[RECALLED] = memory of literature with stated confidence, no web access;
[CONJECTURE] = my hypothesis plus its falsifier. I ran no benchmarks and no
re-executions of programme code [CHECKED — only `python3` subtraction on brief
numbers; source `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/decision_r1/kill.txt`].

## Recommendation: STOP the programme

The original claim was "a 12-byte-per-document code gives competitive retrieval"
[BRIEF — kill.txt line 18]. That claim is dead on current evidence, and none of the
rescue readings survives contact with the fair baseline [CONJECTURE — falsifier: a
prespecified fair-baseline comparison in which any code at any byte budget beats fair
BM25 on both RealTalk and PerLTQA simultaneously; see Options]. The honest move is to
stop all retrieval-optimization work, publish the negative results and the two traps
(rank-overflow, coarse-baseline inflation) as the deliverable, and spend zero further
CPU-hours chasing a competitive 12-byte code [CONJECTURE — falsifier: same as above].

## 1. The premise has no surviving win

**Fact C — every historical "we beat BM25" used a handicapped baseline.**
[BRIEF — kill.txt lines 52–59]. Giving BM25 our own frozen tokenizer is worth +6.38 pp
Hit@10 on RealTalk (55.32 → 61.70) [CHECKED — recomputed 61.70−55.32=6.38 from brief
numbers, kill.txt lines 53–54]. Against the coarse baseline our 48-byte code wins by
+2.55 pp (57.87 vs 55.32) [CHECKED — 57.87−55.32=2.55, kill.txt lines 57–58]; against
the fair baseline it loses by −3.83 pp (57.87 vs 61.70) [CHECKED — 57.87−61.70=−3.83,
kill.txt lines 57–58]. The tokenizer gain (+6.38) is larger than the entire 12→48-byte
ladder gain (+8.22: 49.65 → 57.87) [CHECKED — 57.87−49.65=8.22 from kill.txt lines
24–27; comparison of the two deltas is my arithmetic]. So the programme's headline
result was a tokenizer artifact, not a compression result [CONJECTURE — falsifier: show
any byte budget at which the code beats the fair-tokenizer BM25 on the same queries].
What survives if every comparison is re-run fairly: on current numbers, nothing at 48
bytes, and a fortiori nothing at the claimed 12 bytes (49.65 vs fair 61.70 = −12.05 pp)
[CHECKED — 49.65−61.70=−12.05 from kill.txt lines 24–27 and 53–54]. A defender must
argue the fair tokenizer is somehow unfair to the code — but it is the code's own
tokenizer, so that defense concedes the code was previously evaluated against a
crippled opponent [CONJECTURE — falsifier: a written justification, prespecified before
re-running, for why the coarse tokenizer is the correct opponent].

**Fact E — reranking dissolves first-stage quality.** [BRIEF — kill.txt lines 69–75].
The worse LME first stage (hamming96 FR@3 53.86) ends better after the same BM25 text
reranker (58.23) than the better first stage (qscale96 54.27 → 57.70)
[BRIEF — kill.txt lines 71–72]. I verify the inversion arithmetically: hamming gains
+4.37 under rerank, qscale +3.43, so a −0.41 first-stage deficit becomes a +0.53
post-rerank lead [CHECKED — 58.23−53.86=4.37; 57.70−54.27=3.43; from kill.txt lines
71–72]. The code's net contribution over plain BM25 alone is −0.33 / +0.33 / +1.07 pp
[BRIEF — kill.txt line 73], i.e. noise around zero at the cost of raw text at 76× the
code plus an index at 0.9–1.5× the text again, and 14.9→17.6 ms latency vs 0.14 ms for
a plain inverted index [BRIEF — kill.txt lines 74–75]. Is there any reading of E that
leaves the premise intact? Only the latency reading: the code is ~100× faster than the
reranked pipeline per query [CONJECTURE — falsifier: a deployment where sub-millisecond
first-stage latency without text access is worth −3.83 pp of accuracy — but no such
deployment has been named in this programme, and the reranked system needs the text
anyway, which erases the storage premise]. If the end system needs raw text to be
competitive, optimizing a compact first-stage code is optimizing a component whose
output the reranker overwrites [CONJECTURE — falsifier: a first-stage-quality vs
post-rerank-quality correlation study across many first stages showing rank
preservation; E is currently one inversion, so this demands new data].

**Fact D — we tuned the wrong layer for months.** [BRIEF — kill.txt lines 61–67].
Word-channel-only float cosine with NO projection reaches Hit@10 56.03, while the full
Z (LSA+word+char) reaches 47.80 — the char+LSA mix costs 8.23 pp
[CHECKED — 56.03−47.80=8.23, kill.txt lines 63–64]. The 12→48-byte compression ladder
on RealTalk gains +8.22 pp total [CHECKED — 57.87−49.65=8.22, kill.txt lines 24–27],
so the feature-mix loss (8.23) fully cancels the entire compression budget's gain
(8.22) [CHECKED — comparison of the two recomputed deltas]. Worse: word-only with no
projection at all (56.03) beats our 24-byte code (55.32) outright by +0.71 pp
[CHECKED — 56.03−55.32=0.71, kill.txt lines 63–67]. Months of quantization-layer work
(ITQ, rotations, penalties) fought over single-digit deltas while an 8-point loss sat
one layer down, unaddressed [CONJECTURE — falsifier: a log showing the feature-mix
ablation was run before the quantization work began]. Any continuation that does not
start by deleting or justifying the char+LSA channels is indefensible
[CONJECTURE — falsifier: a prespecified ablation in which full Z beats word-only on
both benchmarks].

**Fact F — no arm has EVER won on both benchmarks simultaneously.**
[BRIEF — kill.txt lines 77–90]. IDF^p helps RealTalk rare (+4.78 pp SIG) and hurts
PerLTQA (−1.76); component shift helps PerLTQA (+1.58 SIG) and hurts RealTalk
[BRIEF — kill.txt lines 88–89]. ITQ loses to random rotation on both (−2.27 RealTalk,
−0.13 PerLTQA) [BRIEF — kill.txt lines 78–81]. At some point "it depends on the
archive" stops being a finding and becomes the signature of per-archive fitting on
300–1500 documents: with n≈300–400 and k up to 384, there is barely one observation
per fitted direction, so archive-specific winners are expected under pure noise
[CONJECTURE — falsifier: a prespecified arm that wins on RealTalk AND PerLTQA
simultaneously with CIs excluding zero on both]. The honest rule from Fact B (k<n per
archive; fixed global k is wrong for heterogeneous archives) [BRIEF — kill.txt lines
45–50] cuts against the programme, not for it: a code whose dimensionality must be
hand-tuned per archive, with 8 of 30 PerLTQA archives holding fewer than 384 documents
[BRIEF — kill.txt lines 45–46], is not a general 12-byte code but a per-archive
bespoke fit [CONJECTURE — falsifier: a single fixed-k code that satisfies k<n on every
archive in a heterogeneous collection and still wins].

**Fact G — four headline claims retracted in one week, all toward over-claiming.**
[BRIEF — kill.txt lines 92–102]. The false "no better 96 directions exist" rested on a
mean-vs-individual confusion about sum_i rho_i (counterexample: 96 coordinate axes,
rho=1.0/0.0, mean 0.1920) [BRIEF — kill.txt lines 93–95]; "12 bytes isn't enough, 48
is" confused dimensions with bytes on top of the rank-overflow artifact
[BRIEF — kill.txt lines 96–97]; the SVD-rare-terms and common-band stories were
overstated and degenerate respectively (rare terms survive at 0.94× null; BM25 scores
exactly zero on 97.8–100% of the common bucket by construction)
[BRIEF — kill.txt lines 98–102]. Four retractions in one direction is not bad luck; it
is evidence of a systematic optimism bias in programme-internal analysis, caught only
by external review [CONJECTURE — falsifier: a list of programme-internal analyses this
month that concluded against the programme's claims without external prompting]. What
remains (the RealTalk ladder, the LME rise) was produced by the same pipeline and the
same analysts, so its credibility discount should be nonzero
[CONJECTURE — falsifier: an independent re-derivation of the RealTalk ladder from raw
artifacts by a party that has not previously produced programme numbers].

**Fact H — BEIR predicts exactly our result.** [BRIEF — kill.txt lines 104–116].
Dense models without in-domain training routinely lose to BM25 zero-shot (Thakur et
al. 2021), and our per-archive SVD has no cross-archive training, placing us squarely
where BM25 is expected to win [BRIEF — kill.txt lines 109–111; citation recalled by
round-2 workers and coordinator-verified with web access per the brief — I have no web
access and did not re-verify it: treat as RECALLED with medium-high confidence, exact
wording unverified]. No recalled source bounds gold Hit@K from bits/doc or reports
gold Hit@10 at K=10 from ≤12–16 B/doc codes, and our few-hundred-document regime
appears unstudied [BRIEF — kill.txt lines 112–114; RECALLED with medium confidence,
no web access]. Spending owner-paid compute to rediscover "untrained dense loses to
BM25" is not research; the genuinely novel bits (ITQ ≤ random rotation, rotation
damage scaling with archive size r=−0.78, bit-balance anti-correlating with retrieval)
[BRIEF — kill.txt lines 77–81, 115–116] are negative results about our own pipeline,
publishable once, not a basis for continued optimization [CONJECTURE — falsifier: a
named recalled source showing per-archive unsupervised sign codes beating tuned BM25
on gold retrieval at ≤48 B/doc].

## 2. What about the ladders (A) and the rank-overflow fix (B)?

Steel-manning the other side: RealTalk rises monotonically 49.65 → 55.32 (+5.67) →
57.87 (+2.55) Hit@10, FR@3 22.41 → 29.75 → 32.79 [CHECKED — 55.32−49.65=5.67;
57.87−55.32=2.55; 29.75−22.41=7.34; 32.79−29.75=3.04; kill.txt lines 24–27], with a
0-of-858,624-bit fidelity gate and k=96 anchor reproduction to −0.0000
[BRIEF — kill.txt lines 21–22]. LME FR@3 rises 52.47 → 61.48 (+9.01) → 61.75 (+0.27)
[CHECKED — recomputed from kill.txt line 33]. Diminishing but not exhausted, says the
brief [BRIEF — kill.txt line 28]. True — and irrelevant: the entire RealTalk ladder
tops out at 57.87, still −3.83 below fair BM25's 61.70 [CHECKED — same subtraction as
Fact C]. A rising ladder that never reaches the opponent is an argument for stopping,
not for climbing [CONJECTURE — falsifier: extrapolate the ladder's diminishing steps
(+5.67, +2.55, …) to any byte budget and show it crossing 61.70 before the storage
premise becomes absurd]. Fact B's rank-overflow diagnosis (surplus constant-filled
dimensions with σ≈0 poison standardized scorers; unstandardized arms rise: asym
53.71→57.30→58.03, float_raw 55.03→58.55→60.43) [BRIEF — kill.txt lines 37–50] is real
debugging value — but it downgrades the programme's past conclusions (the "bits beyond
24 B do not help" reading was measured under a defect, not a law)
[BRIEF — kill.txt line 49] rather than rescuing the premise: the fixed 48-byte code
still charges full bytes for zero-information constant dimensions on 26.8% of PerLTQA
queries [BRIEF — kill.txt lines 45–48], i.e. the product as specified wastes a quarter
of its budget by construction [CONJECTURE — falsifier: a per-archive adaptive-k
implementation with prespecified k(n) rule that beats fair BM25 — which is a new
programme, not the 12-byte-code programme].

## 3. Options — each with next action, prespecified success criterion, honest cost, and strongest reason it fails

**Option 1 (recommended): STOP optimization; publish the salvage note.**
Next action: freeze all retrieval-optimization branches; write up the committed
RealTalk ladder, audits, and negative results as a negative-results/traps note; leave
main untouched [BRIEF — current state, kill.txt lines 118–121]. Success criterion
(decided now, before writing): the note states the fair-baseline gap (−3.83 pp at 48
B), the rank-overflow trap (k<n rule), and the abandon list, with every number
traceable to committed artifacts — done when an independent reader can reproduce the
three headline subtractions from the note alone. Honest cost: ~1–3 days of writing,
near-zero compute [CONJECTURE — cost estimate from the fact that all numbers already
exist in-branch; falsifier: the draft takes longer than a week]. Strongest reason it
fails: the salvage note may be unpublishable/uninteresting ("untrained method loses to
BM25" is BEIR-expected), leaving the owner with sunk cost and no asset beyond internal
cautionary value [CONJECTURE — falsifier: a venue or internal consumer that explicitly
wants the negative result].

**Option 2: narrow finish — traps-only note (rank-overflow + coarse-baseline inflation).**
Next action: publish just Facts B and C as a two-trap methods note; abandon everything
else. Success criterion (prespecified): a reader holding only the note can (a) state
the k<n rule and (b) reproduce the +6.38 tokenizer swing and −3.83 fair gap from the
note's own tables. Honest cost: hours of writing, zero compute [CONJECTURE —
falsifier: it requires new runs]. Strongest reason it fails: two traps do not make a
paper or a product, and the same optimism-bias concern (Fact G) taints even this —
the traps were found by the same process that set them [CONJECTURE — falsifier:
external confirmation that either trap was previously unknown and useful].

**Option 3: fair-baseline re-run of every historical comparison, then decide.**
Next action: re-score all code-vs-BM25 claims with the frozen fair tokenizer and
textbook-vs-tuned BM25 variants before any further code work. Success criterion
(prespecified, binding): continue ONLY if some code at ≤48 B/doc beats fair BM25 on
RealTalk AND PerLTQA simultaneously with CIs excluding zero; otherwise stop
permanently. Honest cost: small-to-moderate compute (re-scoring, no new codes) plus
the temptation to keep moving goalposts [CONJECTURE — falsifier: the re-run costs
more than budgeted]. Strongest reason it fails: the answer is already known on
RealTalk (−3.83 at 48 B), so this spends compute to confirm a stop; and the losing
side will demand "just one more tokenizer variant" indefinitely [CONJECTURE —
falsifier: the re-run changes the sign of the RealTalk gap].

**Option 4: continue the 12-byte-code programme (reject my case).**
Next action: propose the next optimization (new rotation, new penalty, new split) with
a prespecified two-benchmark win criterion. Success criterion (prespecified): the new
arm beats fair BM25 AND float on both RealTalk and PerLTQA. Honest cost: open-ended
owner-paid compute with a 0-for-history base rate (4/4 quantization attempts failed;
no arm ever won on both benchmarks) [BRIEF — kill.txt lines 77–90]. Strongest reason
it fails: every structural fact (fair baseline ahead by 3.83, feature mix −8.23,
rerank dissolution, BEIR expectation, optimism bias) points the same way, so this is
buying lottery tickets with the owner's money [CONJECTURE — falsifier: Option 4's
champion posts a bond — names the single next experiment and agrees to stop if its
prespecified criterion fails].

## 4. Honest salvage plan (if we stop): what is the deliverable and its real value?

The deliverable is a short negative-results and traps note from work already committed
(RealTalk ladder, lit maps, incoming audits on branch
findings/top10-comparison-2026-09-15, main untouched) [BRIEF — kill.txt lines
118–120]. Contents: (1) the fair-baseline correction (−3.83 pp at 48 B; +6.38
tokenizer swing) with the rule "never report code-vs-BM25 without the code's own
tokenizer on both sides"; (2) the rank-overflow trap (k<n per archive; 8/30 PerLTQA
archives below 384 docs; constant dims + σ≈0 + qscale = poison; unstandardized arms
immune) with the rule "charge bytes only for effective rank"; (3) the quantization
negative results (ITQ ≤ random rotation; rotation damage r=−0.78 with archive size;
rotation costs 3.4–7.5× the payload it fails to improve; sign(C/σ)==sign(C) exactly,
0 of 63,552 bits change) [BRIEF — kill.txt lines 77–90]; (4) the rerank dissolution
(inversion numbers + net −0.33/+0.33/+1.07) as a scope warning; (5) the four
retractions as an honesty appendix [BRIEF — kill.txt lines 92–102]. Real value, stated
without inflation: internal — it stops the owner spending more compute and prevents
the next team from re-setting both traps; external — the rotation-damage scaling and
bit-balance anti-correlation are claimed as genuinely ours (nothing recalled covers
them) [BRIEF — kill.txt lines 115–116] and may be worth one workshop-grade negative
result, though BEIR-expectedness caps its novelty [CONJECTURE — falsifier: a reviewer
who finds the traps already documented]. Cost to finish: writing only; the one
in-flight item (LME channel ablation, 322/470) [BRIEF — kill.txt line 120] should be
allowed to finish ONLY because it is already paid for, then frozen — no follow-ups
[CONJECTURE — falsifier: finishing it requires significant new spend].

## 5. Explicit abandon list — directions that should never get another CPU-hour

1. Any further rotation learning (ITQ or variants) on per-archive sign codes: 4/4
   failed, loses to random rotation, damage scales with small archives, costs
   3.4–7.5× the payload [BRIEF — kill.txt lines 77–81]. Dead.
2. Per-axis rescaling as a bit-changing intervention: mathematically incapable
   (sign(C/σ)==sign(C), 0/63,552 change); only rotation or shifted thresholds can
   change bits [BRIEF — kill.txt lines 82–83]. Dead by proof.
3. Budget-splitting (SVD dims + rare-term Bloom sketch): failed at every ratio
   [BRIEF — kill.txt line 84]. Dead.
4. Constrained additive penalty Z′Z+λD: safety gates passed, retrieval did not
   improve; CI includes zero vs production, loses to BM25 and float everywhere
   [BRIEF — kill.txt lines 85–87]. Dead.
5. Fixed-global-k codes on heterogeneous archives: violates k<n on 8/30 PerLTQA
   archives, charges bytes for constant dims [BRIEF — kill.txt lines 45–50]. Dead as
   specified; any revival must be a per-archive adaptive-k programme with a
   prespecified k(n) rule, judged under Option 3's criterion.
6. Any new code-vs-BM25 claim using the coarse baseline or textbook k1=1.2/b=0.75
   without reporting the fair-tokenizer and tuned variants: the +6.38 swing and the
   k1→0,b=0 finding (42.11 vs 37.67 on LoCoMo) [BRIEF — kill.txt lines 52–56] prove
   the old protocol manufactures wins. Dead protocol.
7. First-stage-code optimization justified by end-to-end retrieval while the
   deployed path contains a text reranker: Fact E shows the reranker dissolves the
   optimized quantity [BRIEF — kill.txt lines 69–75]. Dead unless the latency-without-
   text deployment is named and its accuracy price (−3.83 pp or worse) is accepted in
   writing beforehand [CONJECTURE — falsifier: such a signed deployment requirement].
8. Char+LSA feature-mix tuning before the word-only ablation is resolved: the mix
   costs 8.23 pp and word-only-no-projection beats the 24-byte code
   [CHECKED — both deltas recomputed above from kill.txt lines 61–67]. No compression
   work until the feature layer is justified or deleted.

## 6. The strongest point against my own case

The honest objection: RealTalk's ladder is clean (0/858,624-bit fidelity gate, anchor
reproduction to −0.0000) [BRIEF — kill.txt lines 21–22], monotone, and not yet
flattened (+2.55 on the last doubling; LME still rises to 44.15 on LoCoMo and 61.75 on
LME-FR@3) [BRIEF — kill.txt lines 23–35; last-step deltas CHECKED above], and Fact B
shows the PerLTQA decline was a scorer defect, meaning the "scaling stops at 24 B"
ceiling was false — the unstandardized arms keep rising to 58.03/60.43
[BRIEF — kill.txt lines 42–50]. A fair-minded owner could read this as "the
programme's measurement was broken, not its premise; fix k<n, drop the char channel,
use the fair baseline on both sides, and the unbroken scaling curve plus a repaired
feature layer might yet cross BM25." [CONJECTURE — this is the keep-side hypothesis;
falsifier: the prespecified Option 3 re-run]. My reply: "might yet cross" has been the
programme's position through 4/4 failed quantization attempts and zero two-benchmark
wins, against a −3.83 pp deficit at 4× the claimed budget and a −12.05 pp deficit at
the claimed 12 bytes [CHECKED — both recomputed above], in a regime where the
literature expects BM25 to win [RECALLED — BEIR, medium-high confidence, unverified
by me]. Hope is not a plan; the keep side should accept Option 3's binding criterion,
and until it passes, the CPU stays off.

---
*Method note: all [CHECKED] items are same-session `python3` subtractions on the
brief's printed numbers (e.g. 57.87−61.70=−3.83), cited to kill.txt line ranges, not
independent benchmark re-executions; no long benchmark was launched and no repo code
was executed [CHECKED — procedure described; source kill.txt].*
