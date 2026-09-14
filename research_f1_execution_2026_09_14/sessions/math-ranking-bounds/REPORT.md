# Ranking stability under bit removal/quantization: perturbation bounds, exact top-k invariance, tie math, and an honest impossibility result

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 0. One useful result (and one honest negative)

**Positive (new, proved, machine-checked on 122k+ configurations):** for coordinate-subset
codes (keep S of b bits, drop r = b − |S|), the FULL-code distance profile plus the single
integer r already yields (i) a tight pairwise perturbation bound, (ii) a sufficient exact
top-K *set*-invariance condition with a sharp integer refinement (gap > r preserves order;
gap = r can tie but never strictly reverse; gap < r can strictly reverse), (iii) per-gold
"deeply free / deeply buried" survival conditions, and (iv) an array-specific sandwich bounding
subset-code expected fractional recall — all without any distributional assumption and with
ties handled exactly (pessimistic / expected / optimistic + hypergeometric joint law).

**Negative (proved, with explicit quantifiers):** there is NO nontrivial distribution-free
guarantee: for EVERY retained set S with r ≥ 1 removed bits there EXISTS a tiny archive+query
(n = 2) on which full-code expected recall is 1 but subset-code expected recall is 1/2
(pessimistic 1 → 0). So any claim of the form "dropping to k < 96 bits preserves retrieval"
must condition on the array's margins (as T2–T4 do) — it can never hold uniformly. This bounds
only coordinate-projection codes against an adversarial (archive, query) pair; it is NOT a
universal bound on all codecs (heterogeneous multi-bit, learned, or recoded families are
explicitly out of scope).

Net: the certificate in `race_2026-09-13/cert/` (paired-bootstrap quality-equivalence) and the
MATH-1 exact tie identity remain the right tools for real data; what is added here is the
deterministic, per-array perturbation calculus that sits *underneath* them, plus a proof that
nothing stronger-but-still-distribution-free exists.

## 1. Setup and relation to prior work

### 1.1 Frozen protocol (shared with the programme)

One question: n docs with centered float vectors C_i and query qC (see
`race_2026-09-13/cert/cert_compute.py:60-66` for the construction `D0=(C>=0)`,
`Q0=(qC>=0)`). Sign codes D_i, Q ∈ {0,1}^96. Full Hamming distances
d_i = |{j : D_i[j] ≠ Q[j]}|. Retrieval = top-K (K = 3) by (d_i, priority) lexsort with
frozen iid continuous priorities (20 trials). Per-gold profile (MATH-1 identity, proved in
`prereg_race_2026-09-13/math1/math1_report.md:§1a`, reused here as a DEFINITION):
S_g = #{i : d_i < d_g}, T_g = #{i : d_i = d_g} (gold included),
f(S,T) = 0 if S ≥ K; 1 if S+T ≤ K; (K−S)/T otherwise, and
E[fractional-R@K] = (1/m)Σ_g f(S_g,T_g) over the m golds.
Pessimistic FR_pess = 1{S+T ≤ K}; optimistic FR_opt = 1{S < K}; always FR_pess ≤ E ≤ FR_opt.

### 1.2 What this adds over the cert theorem and MATH-1/MATH-2

- The cert report (`race_2026-09-13/cert/cert_report.md:§1-3`) proves *statistical*
  quality-equivalence (paired bootstrap, benchmark-conditional) and explicitly declines
  universal losslessness (§1a, §1d: counting/Kolmogorov/distribution objections).
- MATH-1 (`prereg_race_2026-09-13/math1/math1_report.md`) proves the exact tie identity and
  the pairing→width→burial chain; its spike+bulk lemma (cert report §4) needs the empirical
  premise P(C). MATH-2 (`prereg_race_2026-09-13/math2/math2_report.md`) surveys frameworks
  (T1–T7), warns that JL→retrieval transfer is a category error (T3), and conjectures an
  S2 tie-mass floor with a Binomial shell.
- This report is distinct from all three: deterministic per-array perturbation bounds for
  the subset (bit-removal) code family, with NO Binomial/independence shell (so it does not
  inherit the MATH-1 §2c rejection of A1/A2), plus a matching impossibility proof. It does
  not restate the bootstrap certificates or the pairing→covariance chain.

### 1.3 Notation for bit removal

Full width b (frozen b = 96). Retained set S ⊆ [b], |S| = s, removed R = [b]\S, r = b − s ≥ 1.
For doc i: d_i = d^S_i + d^R_i (retained + removed Hamming parts). Subset code ranks by d^S;
(S′_g, T′_g), f′, E′_sub denote the subset-code analogues. "Top-K set" means the K docs with
smallest distances (well-defined as a set iff the K-th order-statistic boundary is strict).

## 2. THEOREMS (full proofs, explicit assumptions)

Assumptions for T1–T4: NONE beyond the definitions above (arbitrary binary codebook,
arbitrary query, arbitrary gold set; duplicates allowed, as in real archives with
near-duplicate clusters — cf. MATH-1 §2c). K is general (frozen K = 3 is a special case).

> **T1 — Pairwise perturbation bound (tight).** For all docs i, j:
> |(d_i − d_j) − (d^S_i − d^S_j)| = |d^R_i − d^R_j| ≤ r.
> *Corollary:* d_j − d_i > r ⟹ d^S_j > d^S_i (strict pairwise order preserved).
> *Proof.* d_i − d_j = (d^S_i − d^S_j) + (d^R_i − d^R_j); rearrange and use
> 0 ≤ d^R ≤ r. ∎
> *Tightness:* equality |d^R_i − d^R_j| = r is attained whenever two docs agree with the
> query identically on S and differ maximally on R (exhaustion: 119,264 tight
> configurations in scope; witness W1 §4). No JL or distance-preservation machinery is
> used — and none is needed (cf. MATH-2 T3 warning).

> **T1′ — Integer refinement (sharp trichotomy).** Let γ = d_j − d_i > 0 (integer gap).
> Then (a) γ > r ⟹ subset order preserved (T1 corollary); (b) γ = r ⟹ subset order can
> tie (d^S_j = d^S_i) but can NEVER strictly reverse; (c) γ < r ⟹ strict reversal is
> possible. *Proof.* d^S_j − d^S_i = γ − ρ with ρ = d^R_j − d^R_i,
> |ρ| ≤ r. (b): γ − ρ ≥ γ − r = 0. (c): ρ = r gives γ − r < 0; realizable (W2-style
> construction §4). ∎
> This refines the naive "margin > perturbation" slogan: at exactly margin = r the damage
> is tie-creation only — which still costs expected recall (1 → (K−S)/T) and pessimistic
> recall, but not optimistic recall from strictly-behind docs (see corrected boundary §5).

> **T2 — Exact top-K set invariance (sufficient, gap condition).** Let
> d_(1) ≤ … ≤ d_(n) be sorted full distances and Γ = d_(K+1) − d_(K) (need K < n).
> If Γ > r, the subset-code top-K SET equals the full-code top-K set, and both
> boundaries are strict. *Proof.* Any full-top-K doc i and outsider j satisfy
> d_j − d_i ≥ Γ > r, so d^S_j > d^S_i by T1: all K insiders beat all outsiders in the
> subset code too; both gaps are ≥ Γ − r > 0 on the subset side. ∎
> *Sufficient, NOT necessary:* fails to fire whenever removed bits are near-constant
> across docs (uniform shift preserves order at Γ = 0) — found routinely in scope
> (premise fires on only 9,856/122,368 applicable checks; equality of top-K sets holds far
> more often). *Sharpness:* Γ = r does not suffice — 11,072 scope instances have a
> subset-code boundary tie there (example §4, T2_sharp_example).

> **T3 — Per-gold survival (array-specific, checkable from full profile + r alone).**
> For gold g let H_g = #{i : d_i ≤ d_g + r} and L_g = #{i : d_i < d_g − r}.
> (a) *Deeply free:* H_g ≤ K ⟹ f′_g = 1 (gold stays fully retrieved).
> (b) *Deeply buried:* L_g ≥ K ⟹ f′_g = 0 (gold stays unretrieved).
> *Proof.* (a): d_i > d_g + r ⟹ d^S_i > d^S_g (T1), so
> {i : d^S_i ≤ d^S_g} ⊆ {i : d_i ≤ d_g + r}, of size ≤ K, i.e. S′ + T′ ≤ K.
> (b): d_i < d_g − r ⟹ d^S_i < d^S_g, so S′_g ≥ L_g ≥ K. ∎
> Note (a) implies full-code freedom too (S + T ≤ H_g ≤ K), so it reads: "free with no
> doc within r above ⟹ stays free." Both premises use only full distances + r — the
> subset geometry is never consulted.

> **T4 — Array-specific loss sandwich.** Let E = full-code expected FR, E′ = subset-code
> expected FR over the question's m golds. Then
> (1/m)|{g : H_g ≤ K}| ≤ E′ ≤ (1/m)|{g : L_g < K}|,
> hence loss L := E − E′ ≤ (1/m)Σ_g (f_g − 1{H_g ≤ K}).
> *Proof.* Average T3 over golds (f′_g ≥ 1{H_g≤K}; f′_g ≤ 1{L_g<K}). ∎
> *Honest vacuity warning:* when margins are thin the lower bound is 0 (it is vacuous in
> 393,504/424,448 ≈ 92.7% of small exhaustive cases — small random codebooks rarely have
> deep margins; real 96-bit profiles are kinder, but that is an empirical claim, not
> proved here). The bound is an upper envelope on what full-profile geometry alone can
> promise — exactly the gap the impossibility result (T6) shows cannot be closed
> distribution-free.

> **T5 — Tie-randomization law (hypergeometric, with variance).** Fix a trial. Only the
> boundary distance bucket is contested: if gold g's bucket holds T tied docs competing
> for t = K − S > 0 slots (0 < t < T), each tied doc is included w.p. t/T (uniform random
> permutation from the frozen continuous priorities — same conditional-uniformity argument
> as MATH-1 §1a). Jointly: if the bucket contains c golds, # retrieved golds ∼
> Hypergeometric(T, c, t): P(=v) = C(c,v)C(T−c,t−v)/C(T,t), mean ct/T,
> Var = t(c/T)(1 − c/T)(T−t)/(T−1). Golds at different distances from the boundary bucket
> are deterministic (0/1); at most one bucket per question is stochastic. NT-trial mean
> variance = single-trial variance / NT. *Proof.* Symmetry of the uniform permutation over
> the tied block; sampling without replacement. Verified by brute-force permutation
> enumeration (171 distribution checks, 1,372 permutations, exact rational equality). ∎
> This replaces "pessimistic vs optimistic prose" with the exact sampling law the frozen
> 20-trial MC estimates.

> **T6 — Distribution-free impossibility (explicit quantifiers, honest negative).**
> Fix ANY retained set S ⊆ [96] with r = 96 − |S| ≥ 1 (data-oblivious or data-dependent —
> the adversary sees S). Then ∃ an archive (n = 2, duplicate-free) and query over 96-bit
> sign vectors with full-code E[FR] = 1 but subset-code E[FR] = 1/2 (pessimistic 1 → 0).
> *Proof.* Padding/lifting: it suffices to exhibit this for small width b₀ (append
> 96 − b₀ coordinates on which both docs and query agree; all distances and gaps are
> unchanged, retained/removed status of padding arbitrary). Take b₀ = 2, S₀ = {bit0},
> q = 00, docs A = 00, B = 10 (differ only on the removed bit): full d = (0,1), gold A has
> (S,T) = (0,1), f = 1 (K = 1); subset d^S = (0,0), (S′,T′) = (0,2), f′ = 1/2,
> pess 1 → 0. ∎
> *Scope fence:* quantifiers are ∀S (coordinate subsets) ∃(archive, query) — an
> adversarial pair for the SUBSET code family only. NOT a bound on all codecs
> (48×2-bit, recoded/rotated, or learned families can behave differently), NOT a claim
> about typical arrays (T2–T4 govern those), and NOT a retrieval lower bound derived
> from distance preservation (no JL content anywhere in this report).

**Reversibility ≠ retrieval (remark).** A global bit-complement / coordinate permutation is
bijective on codes yet preserves every Hamming distance exactly (hence all retrieval —
the signed-permutation invariance re-derived in pilots-round-2 and re-checked as W3);
conversely subset projection is non-injective yet preserves retrieval exactly on
large-margin arrays (T2). Do not use "lossy"/"lossless" of the CODE as a proxy for
retrieval preservation — the programme's cert report §1a makes the same point for
reconstruction; T2/T6 make it for ranking.

## 3. EMPIRICAL OBSERVATIONS (synthetic scope only — NOT benchmark output)

Exhaustion ranges (exact): A: b=3,n=3,K∈{1,2}: all 8⁴=4,096 (docs,q) × 7 proper subsets;
B: b=3,n=2,K=1: all 8³=512 × 7; C: b=4,n=2,K=1: all 16³=4,096 × 15. Gold sets: all
singletons + full set. (K < n is required for T2; frozen K=3 theorems are parametric in K,
so K∈{1,2} checks the same statements.) T5: T=1..5, K=1..3, all S≤K, all c=1..T, full
permutation enumeration. All arithmetic exact (integers/Fractions).

- T1: 122,368 checks, 0 violations; bound tight 119,264 times.
- T2: 122,368 applicable; premise Γ>r fired 9,856× (0 violations of set equality);
  11,072 Γ=r subset-tie instances (sharpness).
- T3: 604,160 per-gold checks, 0 violations (32,384 free-fires + 32,384 buried-fires).
- T4: 424,448 question checks, 0 violations; lower bound vacuous (0) in 92.7%,
  both bounds attained 104,064× each.
- T5: 171/171 distribution checks exact over 1,372 permutations.
- r=1 boundary: restricted entry holds everywhere (0 violations); optimistic recall still
  breaks via tied-doc entry in 6,720/71,264 cases (counterexample C1 §4).

## 4. COUNTEREXAMPLES (all lift to 96 bits by agreeing-coordinate padding)

- **W1 (T6 witness, r=1):** b=2, sub={bit0}, q=00, docs A=00, B=10. Full d=(0,1) → E=1;
  subset d^S=(0,0) → E′=1/2, pess 1→0, opt stays 1. Minimal proof that one removed bit
  already forbids a uniform preservation guarantee.
- **C1 (r=1 optimistic break via tied entry):** b=2, sub={bit0}, q=00, docs g=01, x=10.
  Full d=(1,1) (tie; opt=1); subset d^S=(1,0) → x strictly closer, opt′=0. Mechanism:
  the removed bit broke the tie asymmetrically. (This killed the author's first-draft
  "r=1 preserves opt" lemma — see §5.)
- **W2 (r=2 optimistic kill from strictly behind):** b=3, sub={bit0}, K=3, q=000,
  gold g=001 (d=1), three intruders x=110 (d=2, d^S=0 < d^S_g=1). Full f=opt=1;
  subset S′=3 → f′=opt′=0. Triplicated intruder = the duplicate-cluster pattern MATH-1
  §2c found in real data (spike mass), here weaponized by the adversary.
- **T2-sharp (Γ=r ties):** b=3,n=3,K=1, docs=(0,0,1), q=1, sub=110: full d=(1,1,0),
  Γ=1=r; subset ds=(0,0,0) three-way tie — the top-1 set is tie-draw-dependent.

## 5. FAILED ATTEMPTS (recorded, not hidden)

1. **"Single-bit removal preserves optimistic recall" — FALSE.** First draft claimed
   S′_g ≤ S_g for r=1 (docs behind cannot enter). The sweep falsified it before anything
   was written down: tied docs (γ=0) with removed-bit asymmetry enter S′ (C1). Salvaged
   true core = restricted-entry lemma: for r=1, {i:d^S_i<d^S_g} ⊆ {i:d_i≤d_g} (docs
   STRICTLY behind cannot enter; 0 violations in scope). General-r version is already
   inside T3's proof ({d^S<d^S_g} ⊆ {d ≤ d_g+r}).
2. **"Necessary-and-sufficient top-K condition from full profile alone" — ABANDONED.**
   Sufficiency (T2) is clean; necessity fails (uniform-shift orders survive at Γ=0), and
   any exact necessity statement needs the subset profile, making it circular for
   pre-hoc certification. T4's sandwich is the usable substitute.
3. **"Distribution-free expected-loss bound < 1/2 for r≥1" — REFUTED by W1.** The
   worst case over (archive, query) saturates at 1/2 loss (K=1, n=2) and at 1 (W2-style
   burial for larger r/n). Only margin-conditional bounds (T4) survive.

## 6. What is NOT proven / scope & novelty limits

- Nothing here is evaluated on LME/LoCoMo/REALTALK/PerLTQA (frozen benchmark artifacts
  untouched per instructions; T2–T4 are checkable on real profiles — that computation is
  future work, one session, read-only).
- T2–T4 premises may fire rarely on real 96-bit data (margins at the top-3 boundary are
  thin — the pilot tie-mass results, ROUND3 §2/AUDIT-1 §Task-C, suggest exactly that);
  the theorems are valid regardless, but their PRACTICAL bite (fraction of questions with
  H_g ≤ 3 at r = 16/32/48) is unmeasured. Do not cite these as "48-bit safety."
- No priority/literature claim: MATH-2's T2/T4/T6 pointers (order statistics, ranking
  losses, tie-breaking) and the heterogeneity paper (arXiv 2605.17524, see
  `lit_scan_2026-09-13/LITERATUR_TARAMASI.md:§1`) cover adjacent ground; whether the
  T1′ trichotomy or T3's H_g/L_g formulation appears there was NOT checked (no web
  access per instructions) — treat novelty as "new relative to the programme's own
  cert/MATH-1/MATH-2 artifacts," not as literature priority.
- Finite exhaustive checks (b≤4, n≤4) are evidence for implementation correctness, NOT
  universal proofs — the proofs in §2 stand on their own; the sweep's role is
  falsification (it caught the §5.1 error) and tightness demonstration.
- Learned selection / adaptive routing stay closed (ROUND3 §§1,5 + m2/m3 gates); nothing
  here revives them (all S are fixed before seeing the array in T2–T4; T6 lets the
  adversary see S, which only strengthens the negative).
- Centering is not revisited (AUDIT-1 verdict: binarization carries +10.04pp, centering
  +0.15pp — `audit_2026-09-13/audit1_cont/report.md:Task-B`); sign-vs-float quality
  direction is benchmark-local (PerLTQA reversal, `bench3/runs/b3b_fin/report.md:§6`).

## 7. Reproduction (exact commands & output)

Environment: system python3 (3.14.4), stdlib only — no ml-python import needed
(verified `which python3`; nothing installed).

```
$ cd /home/mdp/muse-work/math-ranking-bounds
$ python3 verify.py results.json
T1_checks=122368 tight_hits=119264
T2_applicable=122368 premise_hits=9856 sharp_instances=11072
T2_sharp_example={'b': 3, 'n': 3, 'K': 1, 'docs': [0, 0, 1], 'q': 1, 'sub': 6, 'd': [1, 1, 0], 'ds': [0, 0, 0]}
T3_checks=604160 free_hits=32384 buried_hits=32384
T4_checks=424448 vacuous_lo=393504 lo_attained=104064 hi_attained=104064
T5_checks=171 perm_count=1372
opt_r1: cases=71264 kills=6720
W1={'docs': [0, 2], 'q': 0, 'b': 2, 'K': 1, 'sub': 1, 'full_f': '1', 'sub_f': '1/2', 'pess': '1->0', 'opt': '1->1'}
W2={'docs': [1, 6, 6, 6], 'q': 0, 'b': 3, 'K': 3, 'sub': 1, 'd': [1, 2, 2, 2], 'ds': [1, 0, 0, 0], 'opt': '1->0'}
DONE ALL THEOREM CHECKS PASSED: T1 bound+corollary, T2 set invariance under gap>r, T3 deep-free/buried, T4 sandwich, T5 hypergeometric, W1/W2/C1 impossibility witnesses, r=1 restricted-entry (opt CAN break via tied docs).
wrote results.json
```

Files in this workspace: `REPORT.md` (this file), `verify.py` (stdlib, runnable),
`results.json` (raw deterministic counts + witnesses), `STATUS.md` (checkpoint log).
verify.py was actually executed (output above); report claims match `results.json` keys.

## 8. Suggested next step (not started)

Apply T3/T4 read-only to frozen LME-470 profiles (`regen/lme/cache_repr/*.pkl`):
for r ∈ {16, 32, 48} with SPREAD/BOT/RAND subsets, report the share of questions with
H_g ≤ 3 per gold and the T4 lower bound vs the measured cert gaps
(`race_2026-09-13/cert/cert_details.json`). Prediction: T4 lower bounds sit far below
measured means (thin real margins) — which would localize exactly how much of the
ladder's loss the margin-conditional theory leaves unexplained, i.e. the room a
spike-aware (MATH-1 P(C)-style) premise must fill. One read-only session; no frozen
artifact touched.
