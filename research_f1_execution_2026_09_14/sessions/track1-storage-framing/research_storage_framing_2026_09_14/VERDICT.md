[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# VERDICT — which side the evidence actually supports

PREPARED, NOT ACCEPTED. The assumption that would most damage this verdict: that the lexical+SVD projector is *common-mode* infrastructure both the 12-byte arms and the float baseline need (see §3) — if most of the 88 kB is common-mode, the MISLEADS case shrinks to the index-only shared state (~288 B/vector for OPQ, ~12.06 for SIGN96). I tested what I could without sealed access; the decisive measurement is named below.

## Verdict

**The evidence supports "the *unqualified* 12-byte framing misleads; the *marginal-qualified* 12-byte accounting is honest but incomplete."** These are different claims and the documents already split them:

1. Against the unqualified framing ("12 bytes vs 384 bytes" ≈ 32× saving): the bytes refute it. VERIFIED: cheapest measured total-footprint projector cost (f16+zlib, 30,769 B/vector minimum) is still ~80× the 384 B float payload; the headline float32 figure is ~230×. Break-even needs 1.4–3.7M vectors per projector vs 396–616 measured. The 32× inference is wrong in magnitude and, for the full pipeline, wrong in sign. **MISLEADS side wins on the question as originally posed (2026-09-09 draft §1).**
2. For the qualified marginal accounting (L-088 + revision): the definitions are written, the linearity `S(N)=a+bN` with slope exactly 12 is receipted by an exact cross-platform replay (CLAIM: `COMPARISON.json`, zero differing leaves), the overreach contrast was cancelled on the record, and effective costs are mandatory-reported. **HONEST side wins on the accounting *rules*.**
3. But the rules have not yet produced the complete number they promise: no arm has a measured *complete* package (index S0 + preprocessing + headers) in one receipt; the revision's §4 gate is explicitly unsatisfied. An honest rulebook with an empty scoreboard does not yet license practical conclusions. **Neither side wins on "what does 12-byte retrieval really cost to deploy" — that number does not exist in the bytes.**

## The single measurement-or-definition that would settle it decisively

**A Head Researcher definition ruling PLUS one complete-package measurement — but if forced to one: the definition ruling.** Specifically: HR must rule whether "the 12-byte result" as cited means (i) marginal code bytes only, (ii) index-package effective bytes/vector, or (iii) full-pipeline effective bytes/vector including query-time preprocessing state — and which denominator (per-archive N vs global N) applies. The arithmetic for all three is already computable from existing receipts; what is missing is not data but the *binding referent* of the quotable sentence. With that ruling, the existing numbers (12.06 / ~288 / ~88,886 for SIGN96-class at N≈500) immediately sort every past and future quotation into compliant or misleading, with no new experiment needed. The complementary measurement — one runner receipt giving the complete serialized package per arm per archive (the revision's §4 gate) — would then fill the one cell that is currently a lower bound.

## What would flip this verdict

- Flip toward fully-HONEST: a complete-package receipt showing full-pipeline effective cost within a small factor of marginal (requires refuting the 88 kB projector's per-archive necessity — e.g. a validated globally-shared or deterministic-regeneration projector, which the revision currently forbids assuming).
- Flip toward fully-MISLEADS: evidence that readers/consumers of the programme's claims (papers, handoffs) quote "12 bytes" without the marginal qualifier after L-088 — i.e. the qualification exists in the repo but not in the wild. I did not survey downstream quotations (out of scope, no network); that survey is an open question (see OPEN_QUESTIONS.md Q-6).
