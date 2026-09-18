[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# KILLS.md -- attacks that damaged or killed programme claims (all VERIFIED this session)
1. KILL (headline framing): "12 bytes beat 384 bytes by 10pp." Per-axis-standardized cosine --
   same 384-byte storage, no leakage, computable from the same caches -- beats the published
   cosine baseline on all four benchmarks, significantly (LME +11.59pp [8.88,14.29], RT +5.66
   [3.69,7.62], LoCoMo +9.11 [7.49,10.74], PerLTQA +1.41 [0.78,2.03]). Against this fair float,
   sign wins on 0 of 4 benchmarks: LME -1.53pp n.s., RT -0.36pp n.s., LoCoMo -2.46pp significant,
   PerLTQA -7.68pp overwhelming. The +10.05pp is a baseline-choice effect, not a quantization triumph.
2. KILL (mechanism pointer): the residual "why" now points at variance-equalization, not
   quantization: sign gives each axis one vote; explicit equalization (zcos) matches/beats it;
   norm-preserving float variants (dot, raw Euclid) do NOT beat cosine. Any future mechanism hunt
   must beat zcos, not cosine.
3. DAMAGE (generality of "+10pp"): it is the maximum over K (peaks K=3-5; LME -1.71pp at K=20,
   RT +0.67pp at K=1) AND the value of a rising dimension curve sampled at the arbitrary endpoint
   96 (at m=32 float wins on all four benchmarks per CLAIM fact A). Two arbitrary choices (K=3,
   D=96) both sit near the effect's best angle.
4. DAMAGE (deployment): N<=1548 everywhere vs 100K-10M target (CLAIM G); at 10M docs the 97
   Hamming levels make top-3 a tie lottery with no VERIFIED evidence; "12 vs 384 bytes" omits
   embedder + centering vector + re-rank floats; CLAIM fact F's 33pp profile-vs-events swing on
   identical archives means no deployable per-method rule exists.
