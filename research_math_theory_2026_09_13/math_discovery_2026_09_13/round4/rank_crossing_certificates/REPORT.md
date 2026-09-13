[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — exact rank-change / top-K stability certificates under the joint-scaling normalized law

## 0. The one result

Fix a coordinate group G. Scale **both** document and query group coordinates by
`t > 0`, put `z = t²`, and remove the common positive query norm. Then every
document's rank score is, for exact rationals `(a, b, u, v)` defined in §2,

> `f(z) = (a + b·z) / √(u + v·z)`, domain `u + v·z > 0`,

and the following is proved and machine-checked (49/49 exact checks, §8):

1. **Pairwise characterization (Theorem 1).** Equality `f_i(z) = f_j(z)` is
   decided by numerator signs first; squaring is valid only for shared strict
   signs, where equality is exactly the cubic
   `P_ij(z) = (a_i+b_i·z)²(u_j+v_j·z) − (a_j+b_j·z)²(u_i+v_i·z) = 0`.
   Opposite-sign and single-zero P-roots are spurious; `P ≡ 0` means
   `|f_i| ≡ |f_j|` (persistent tie on same-sign regions, persistent strict
   order on opposite-sign regions — never a root count).
2. **Constancy (Theorem 2).** Each pair's strict order is constant on open
   intervals between consecutive *genuine* equality points; a P-root may be a
   touch, not a reversal (witness §7: `P = (z−1)²`, verdicts `[+1, 0, +1]`).
3. **Top-K criterion (Theorem 3).** On a closed `J` inside the domain, strict
   top-K-set stability holds **iff** every inside/outside pair strictly favors
   the inside member on all of `J`; fixed-priority stability holds iff
   interiors favor inside and every listed tie favors inside by priority.
   Only `K·(n−K)` cross pairs are ever examined. Expected-tie recall is a
   **separate object** with its own formula; strict separation is sufficient
   but not necessary for it (counter-remark §6).
4. **Finite certificate procedure (§6)** for rational coefficients on bounded
   `J` (e.g. `z ∈ [1/16, 16]`, i.e. `t ∈ [1/4, 4]`): exact Sturm counts on
   sign-homogeneous subintervals plus exact rational-root splitting; honest
   `UNRESOLVED` output whenever a same-sign P-root cannot be isolated —
   `numpy.roots` is never called certified. Practical output is a certified
   safe-`t` interval (demo §7: LME gold/rival rival-above certified on
   `z ∈ [1/16, 1]`), not a codec.

## 1. Scope, budget, non-goals, governing corrections

Bounded first pass (~20 min target). Writes only in
`/home/mdp/muse-work/math4-rank-crossing-certificates`
(`STATUS.md`, `verify.py`, `results.json`, this file). All old sources
read-only; no benchmark sweeps, no new trained arms, no Git push/main edits,
no Task4F1 measurement, no installs/network/model APIs, Muse subscription
only. `threads=1`, `PYTHONDONTWRITEBYTECODE=1`, stdlib certificate path.
No infinite random searches: the only search (§7, 1+1-dim) is deterministic,
lexicographic, budget-capped (40000 evals, 18048 used, grid exhausted).

Corrections (govern all worker prose): gold numerator `1.02997959496` <
rival `1.04672119662` at `t = 4` yet cosine `.54573812 > .53902568` because
norms differ — numerator alone does NOT explain the flip; `t` vs `t²` alone
does not explain opposite Model-H dominance (monotone reparameterization
retains its crossover in the exact toy); query magnitude is NOT a proved
nuisance label; the +12pp LoCoMo claim is retracted (same-cache MC difference
+6.82838pp only); no literature novelty claim.

## 2. Setup, with full quantifiers

**Documents/query.** Arbitrary real vectors, arbitrary (unequal) norms.
For fixed group G write doc `C = (c, g)`, query `q = (qc, qg)`.
Joint scaling: `(c, t·g)`, `(qc, t·qg)`, `t > 0`.

**Definition.** With `z = t²`:
`a = qc·c`, `b = qg·g`, `u = ‖c‖² ≥ 0`, `v = ‖g‖² ≥ 0`.
Rank score `f(z) = N(z)/√D(z)`, `N(z) = a + b·z`, `D(z) = u + v·z`.
Raw cosine is `f(z)/‖q(t)‖`; the positive common factor `‖q(t)‖` never affects
ranking and is removed. Quantifiers: statements hold **for all** `z` in the
stated interval intersected with the domain
`𝒟 = {z > 0 : D_i(z) > 0 ∀i}`; coefficients are **exact rationals**
(`Fraction`s); §8's guarantees are about that exact reading.

**Ties: two separate objects.**
(a) *Fixed-priority top-K*: total order `(f_i(z), prio_i)` with
`prio: [n] → ℕ` injective and `z`-independent; top-K set `T_prio(z)` is always
a well-defined K-set.
(b) *Expected-tie recall*: for gold set `𝒢`, `E(z)` = expected #golds in top-K
under i.i.d. uniform random permutation inside each `f`-tie group (§6 formula).
These are different objects: (a) is a set, (b) a rational number depending on
tie-group composition. Never conflated below.

**Zero vocabulary.** `s = 0` is read as `N_i(z) = 0` (zero score; decided
without squaring). `r = 0` is read as `D_i(z) = 0` (norm-squared zero =
domain boundary; excluded from every closed certificate interval — see
half-open semantics next). If the task meant other symbols by `s`/`r`, the
cases below still exhaust the zero-measure degeneracies of this law.

**Boundary semantics.** Certificates are stated on closed `J = [L, R] ⊂ 𝒟`.
Since each `D_i` is linear, `D_i > 0` at both endpoints implies `D_i > 0` on
all of `J`; the procedure checks endpoints and returns `DOMAIN_FAIL`
otherwise. Points with `D_i = 0` are half-open exclusions: restrict `J` or
report failure — never silently evaluate through a pole. `z = 0` itself is
outside the positive domain (`t > 0`).

## 3. Theorem 1 — pairwise equality with sign discipline

**Theorem 1.** Fix `i, j` and `z ∈ 𝒟` (so `D_i(z), D_j(z) > 0`).
Let `s_i = sgn N_i(z)`, `s_j = sgn N_j(z)`. Then:
(i) if `s_i ≠ s_j`, `f_i(z) − f_j(z)` has sign `s_i − s_j` (strict unless both
zero — no squaring involved);
(ii) if `s_i = s_j = 0`, `f_i(z) = f_j(z) = 0` (genuine common-zero tie);
(iii) if `s_i = s_j = ±1`, then `f_i(z) = f_j(z)` iff `P_ij(z) = 0`, where
`P_ij(z) = N_i(z)²D_j(z) − N_j(z)²D_i(z)`, a polynomial of degree ≤ 3 with
leading coefficient `b_i²v_j − b_j²v_i`;
(iv) if `P_ij` is identically zero, `|f_i| ≡ |f_j|` on `𝒟`: ties exactly on
same-sign regions (including common zeros), strict order exactly on
opposite-sign regions;
(v) a root `z₀` of `P_ij` with `s_i(z₀) ≠ s_j(z₀)` (opposite signs) or exactly
one of `N_i(z₀), N_j(z₀)` zero is **spurious**: `f_i(z₀) ≠ f_j(z₀)`.

*Proof.* (i): `f` has the sign of `N` since `√D > 0`; distinct signs (with the
`0 vs ±1` cases) order the values directly. (ii): both values are `0`.
(iii): for shared strict sign `s`, `f_i = f_j ⟺ |f_i| = |f_j|`
(dividing by `s` preserves equality), and
`|f_i| = |f_j| ⟺ N_i²/D_i = N_j²/D_j ⟺ P_ij = 0` using `D_i, D_j > 0`.
Expansion of `(a+bz)²(u+vz)` gives degree ≤ 3. For ordering (not just
equality) under shared negative sign the squared comparison flips:
`f_i > f_j ⟺ N_i²D_j < N_j²D_i` (smaller magnitude = larger value).
(iv): `P ≡ 0` gives `N_i²D_j = N_j²D_i` as polynomials, hence `|f_i| = |f_j|`
wherever defined; signs decide tie vs strict per (i)–(ii).
(v): at such `z₀` the values have distinct signs or exactly one is nonzero,
hence are unequal, while `P(z₀) = 0` can still hold (squaring forgot signs).
∎

Consequences used everywhere: P-roots are *candidates*, at most 3 when
`P ≢ 0` (never a top-K change count — §6 examines only cross pairs); every
genuine equality is either a sign-filtered P-root or a common-zero tie (which
is itself a P-root, since both terms vanish). The comparator `cmp_rank`
implements (i)–(iii); `audit_cmp` re-implements it with integer-only
arithmetic and product denominators; `P_coeffs` (direct expansion) is checked
against `audit_P_coeffs` (Newton interpolation through `z = 0,1,2,3`) on every
pair the procedure touches.

## 4. Theorem 2 — constancy between genuine events

**Theorem 2.** Fix `i, j`. Let
`𝒢_ij = {z ∈ 𝒟 : f_i(z) = f_j(z)}` (genuine equalities only). On each connected
component (open interval) of `𝒟 ∖ 𝒢_ij`, the strict order of `f_i vs f_j` is
constant. In particular a `P_ij`-root outside `𝒢_ij` changes nothing, and a
multiple (tangent) root inside `𝒢_ij` may be a touch without reversal.

*Proof.* `h(z) = f_i(z) − f_j(z)` is continuous on `𝒟` (ratio of continuous
functions with nonvanishing denominator). Its zero set is exactly `𝒢_ij`.
A continuous real function keeps a constant strict sign on each connected
component of the complement of its zero set. Spurious P-roots are not zeros
of `h` (Theorem 1(v)), so they do not split components; a tangent zero is a
zero (it belongs to `𝒢_ij`) but `h` need not change sign there. ∎

## 5. Theorem 3 — top-K set stability (strict, priority, expected)

Fix docs `1..n`, `K`, closed `J = [L,R] ⊂ 𝒟`.

**Theorem 3a (strict, necessary and sufficient).** Let `z* ∈ J` be tie-free and
`In = T(z*)` (any tie-break; no ties at `z*`). Then the tie-free K-set is
well-defined (no tie across the cut) and equals `In` for all `z ∈ J`
**iff** for every cross pair `(p ∈ In, q ∉ In)`,
`f_p(z) > f_q(z)` strictly for all `z ∈ J`.
*Proof.* (⟸): at any `z`, the K members of `In` all strictly beat all `n − K`
outsiders, so no tie touches the cut and exactly `In` is on top. (⟹): if some
cross pair had `f_p(z₁) < f_q(z₁)`, the K-set at `z₁` cannot still be `In`:
top-K sets are downward-closed in any score-extending order, so
`p ∈ S₁ ∌ q` is impossible while `f_q > f_p` strictly. If instead
`f_p(z₁) = f_q(z₁)`, a tie straddles the cut and the tie-free K-set is not
even defined at `z₁`. Either way strict stability fails. ∎

**Theorem 3b (fixed priorities, necessary and sufficient).** With injective
`prio`, `T_prio(z) ≡ In` on `J` **iff** for every cross pair, interiors of
`J ∖ 𝒢` favor `p ∈ In` strictly and every listed tie point favors `p` by
priority (`prio_p < prio_q`).
*Proof.* Same sandwich argument with `≥_prio`: if all cross pairs favor `In`
in prio-order at `z`, the top-K prio-set is `In`; a violation at any point
changes the prio-set there. Persistent-tie pairs (`P ≡ 0`, tie intervals) are
decided by priority alone. ∎

**Expected-tie recall (separate object).** With tie groups
`G_1, G_2, …` best-first at `z`, let `F_{k} = Σ_{ℓ<k}|G_ℓ|`. The group
straddling rank K (if any) contributes fractionally:
`E(z) = Σ_{gold g strictly above cut} 1 + need·(gold-in-straddler/|straddler|)`,
`need = K − F_k`. *Sufficient* condition: strict separation of every cross
pair on `J` (Theorem 3a) implies no tie touches the cut, so `E(z)` equals the
constant deterministic gold count. This is **not necessary**: e.g. docs
`A = B = 1, C = 0` (tie `A = B > C`, golds `{A,B}`, `K = 1`) give `E = 1`,
same as strict `A > B > C` — the tie structure changed, `E` did not
(machine-checked: `S6-expectation-non-necessity`, `1 vs 1`). Boundary ties
*must* be listed explicitly because `E` jumps there: tangent demo
(`E1 ≥ E2`, tie only at `z = 1`, gold `{E2}`, `K = 1`) gives
`E = 0, 1/2, 0` at `z = 1/2, 1, 2` (machine-checked).

## 6. Certified finite procedure + complexity

**Input:** rational `(a_i, b_i, u_i, v_i)` for `n` docs, `K`, priorities,
closed `J = [L, R]` with `L < R` rationals.
**Output (per pair, then top-K):** `STRICT(d)`, `ISOLATED_TIES(d,list)`,
`PERSISTENT_TIE`, `VARIES` (certified piecewise order with a flip),
`UNRESOLVED`, or `DOMAIN_FAIL` — never a bare float verdict.

1. **Domain.** Check `D_i > 0` at `L, R` for all `i` (linearity extends to
   `J`); else `DOMAIN_FAIL` (the `r = 0` half-open case).
2. **Sample.** Try rational candidates (midpoint, endpoints, trisections) for
   a tie-free `z*`; `In` = top-K there. Two-point probe: prio-resolved top-K
   sets at `L, R` differing from `In` certify `CERTIFIED_UNSTABLE` immediately
   (exact, no root isolation).
3. **Per cross pair only** (`K·(n−K)` pairs; interior–interior crossings are
   provably irrelevant to the K-set): split `J` at exact numerator zeros
   (`s = 0` loci, `−a/b`), at exact rational P-roots (rational-root theorem;
   honestly skipped when coefficients exceed the enumeration budget), and
   evaluate the exact verdict at every split point (ties listed).
4. **Per open subinterval** (numerator signs constant inside): opposite or
   single-zero signs → no equality possible, certified; same strict signs →
   exact Sturm distinct-root count (endpoint roots deflated exactly; all split
   points rational): 0 → strict order certified constant; ≥ 1 →
   `UNRESOLVED` (touch or crossing — never guessed). `P ≡ 0` → persistent-tie
   / persistent-strict logic by signs (Theorem 1(iv)).
5. **Combine** via Theorems 3a/3b: `CERTIFIED_STABLE` / `TIES_PRESENT` /
   `PRIO_FLIPS_AT_TIE` / `CERTIFIED_UNSTABLE` / `UNRESOLVED`.

**Complexity.** Sorting at `z*`: `O(n log n)` exact comparisons. Per cross
pair: ≤ 7 split points, ≤ 6 subintervals, each `O(1)` exact ops (Sturm on
degree ≤ 3). Total `O(K·(n−K) + n log n)` exact operations; the global
`3·C(n,2)` P-root bound is never used as a change count. `numpy.roots` (or any
float root finder) is never on the certificate path.

**Rational vs BLAS.** All of the above is about the exact rational reading of
stored coefficients (`Fraction(float)` = binary-exact value). It transfers no
guarantee to floating-point BLAS evaluation order; §7–8 record an
*informational, uncertified* float-agreement spot-check kept strictly outside
the certificate.

## 7. Machine-checked witnesses (all dual-formulation audited)

| # | case | params `(a,b,u,v)` | exact fact |
|---|---|---|---|
| S1 | prior 2+2 nonmonotone | `(−3,4,5,10)` vs `(−2,2,2,10)` | verdicts at `z ∈ {1/64,1/16,1/4,1,4,16,64}`: `[+,−,−,+,+,+,+]`; `P` cubic, lead 120; at `z=1`, `N₂=0, N₁=1, P=12` (zero-discipline, decided without squaring) |
| S2 | persistent tie | `(2,2,4,4)` vs `(1,1,1,1)` | `P ≡ 0`, tie at `1/16, 1, 16` |
| S3 | opposite-sign fake root | `(1,1,1,10)` vs `(−1,−1,10,1)` | `P = 9(z+1)²(1−z)`, `P(1) = 0`, yet verdicts `[+,+,+]` — squaring's spurious root; companion `P ≡ 0` opposite-sign pair `(1,0,1,1)` vs `(−1,0,1,1)` never ties |
| S4 | tangent touch | `(1,1,0,4)` vs `(1,0,1,0)` | `P = (z−1)²`, verdicts at `1/4,1,4`: `[+,0,+]` — genuine root, no reversal; AM–GM: `(1+z)/√(4z) ≥ 1` |
| S5 | common-zero tie that crosses | `(−1,1,1,1)` vs `(−2,2,1,3)` | verdicts at `1/4,1,2`: `[+,0,−]` |
| S6a | top-1 stable *despite* P-root in J | fake pair + constant `−50`, `J = [1/16,16]`, `K = 1` | `CERTIFIED_STABLE` (strict + prio), 2 cross pairs; `P(1) = 0 ∈ J` causes zero top-K changes |
| S6b | top-1 unstable | S1 pair + constant `−100`, same `J` | `CERTIFIED_UNSTABLE` via endpoint probe sets `{C₂} → {C₁}` |
| S6c | boundary-tie semantics | tangent pair, `J = [1/4,4]`, `K = 1` | strict `TIES_PRESENT`; prio-E1-first `CERTIFIED_STABLE`, prio-E2-first `PRIO_FLIPS_AT_TIE`; `E = 0, 1/2, 0` |
| Neg | seeded broken variant | `naive_cmp` (squares, no sign discipline; `P = 0` read as tie) | claims tie at S3/`z = 1` where truth is strict → recorded `FAILS_AS_INTENDED` (for the intended reason, not incidentally) |
| S7 | fewer-dim (1+1) attempt | `c,g ∈ −3..3`, `qc,qg ∈ ±1,±2`, `a = qc·c, b = qg·g, u = c², v = g²` | grid exhausted (18048/18048 evals, budget 40000): **UNRESOLVED** — no witness in grid; no minimality claim in either direction |
| S8 | LME15745da0 post-hoc illustration | original cache (read-only), LOW48 by `lexsort(abs(q), index)`, gold 56 vs rival 368 | float reproduces coordinator cosines to < 1e-9; signs at `t = .25/1/4`: `[−,−,+]`; exact-rational reading: rival-above on `z ∈ [1/16,1]` **CERTIFIED STRICT** (Sturm 0); `(1,16)` **UNRESOLVED** (one same-sign P-root: touch-or-crossing unisolated); bracket flip itself certified by two exact endpoint verdicts. Post-hoc explanatory only — not out-of-sample prediction; numerator alone does not explain it (gold dot < rival dot at `t = 4`; normalization essential) |

## 8. Exact commands and results

```
cd /home/mdp/muse-work/math4-rank-crossing-certificates
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B verify.py
# checks=49 fail=0 / ALL PASS  (results.json written by the run)
```

`results.json` records every witness verdict, P coefficients, Sturm counts,
mutant control (`FAILS_AS_INTENDED`), search budget (`18048 ≤ 40000`,
`UNRESOLVED-in-grid`), LME floats vs coordinator reference, env
(`python 3.14.4`, threads `1/1`, bytecode `off`), and totals
(`n_checks 49, n_fail 0`). Proof arithmetic is dual-formulation throughout:
`cmp_rank` (Fraction path) vs `audit_cmp` (integer-only path) agree on every
evaluated point; `P_coeffs` (expansion) vs `audit_P_coeffs` (interpolation)
agree on every pair; Sturm is self-tested on 9 known polynomials + zero-poly
+ 3 rational-root cases (one honest over-budget skip). The seeded mutant
guards against green checks that encode the same mistake: it shares the
squaring step but drops the sign discipline, and fails exactly on the
fake-root point.

## 9. Limitations and saved counterexamples (not silently rewritten)

- Irrational P-roots are never isolated: same-sign interiors with Sturm ≥ 1
  return `UNRESOLVED` (e.g. LME `(1,16)`). `UNRESOLVED ≠ stable`.
- 1+1-dim nonmonotonicity is open (grid `UNRESOLVED`); the 2+2 witness is not
  dimension-minimal unless proved.
- Strict top-K certificates need a tie-free sample; fully tied families
  report `SAMPLE_TIED`.
- Expected-tie recall needs the tie-group formula, not just cross pairs; its
  strict-separation condition is sufficient, not necessary (§5 remark).
- All LME statements are post-hoc bracket-endpoint comparisons on one
  selected pair; no population rate, no prediction, no codec.
- Certificates cover the exact rational reading of coefficients, not BLAS
  float evaluation (kept as uncertified spot-check only).

