[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — math-sign-mechanism (checkpoint)

Target: smallest explicit model separating angular/sign-relevant signal from
magnitude/nuisance; sufficient condition for sign > centered-cosine pairwise
AND a contrasting regime where sign loses; pairwise vs top-3 separated;
variance-selection counterexample fresh (not MATH-1 repeat); PerLTQA section
pattern tied to TESTABLE hypotheses only.

Plan (forward generative micro-model, stdlib exact rational arithmetic):
- E1 (d=3, strict): sign correct + cosine wrong. E2 (d=3, strict): reverse.
- Model H (1 signal + 2 nuisance coords, Rademacher nuisance signs, shared
  nuisance scale t>0): P_sign = 13/16 for ALL t (magnitude-blindness);
  P_cos(0.5) = 31/32 (lose), P_cos(10) = 11/16 (win), random-tiebreak.
  Strict-win masses coincide (11/16); the gap is pure tie conversion.
- Transport lemma: single-gold exchangeable non-golds, exact E[FR@3] from
  pairwise (u,v) for N in {6,10}; direction must survive (else disclose).
- Variance-selection micro-model V: fresh 4-doc synthetic archive where
  TOP-variance subset ~ chance and BOT-variance subset perfect.
- Failed attempts recorded (d=2 symmetric always-cosine-correct proof;
  sigma=0 large-tau limit where cosine still wins).

Progress: context read (handoff brief, CERT, AUDIT1-CONT, B3B-FIN, LIT scan,
ROUND3, MATH-1, MATH-2). verify.py next; REPORT.md only after executed numbers.
No benchmark recompute; no frozen artifacts touched; sources outside
/home/mdp/muse-work read-only.
