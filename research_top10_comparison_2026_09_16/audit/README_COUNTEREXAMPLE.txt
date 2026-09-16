[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Audit counterexample for data/run_lexical.py expected_hit() bug.

Producer expected_hit() returns fractional expected Recall@10
  (exp_recall = E[|gold cap top10|]/|gold|),
NOT any-gold probability Hit@10
  (exp_hit = P(|gold cap top10| >= 1)).

REPORT.md falsely claims those equal ("Expected-Hit@10 equals Recall@10
to all digits"). They coincide only for single-gold queries or when no
boundary tie straddles rank 10. Multi-gold + boundary tie diverges.

Correct expectedHit (uniform within-bucket tiebreak, K=10):
  - let buckets be distinct scores descending, better = #docs strictly above
    current bucket, B = bucket size, G = #gold in bucket, s = K - better slots.
  - if any gold in a bucket fully inside top-K (better+B <= K) -> 1.0
  - else boundary bucket (better < K < better+B):
      if G == 0 -> 0.0
      else 1 - C(B-G, s)/C(B, s)  (0 when B-G < s, i.e. pigeonhole -> 1.0)
  - if loop ends with no gold seen -> 0.0

Run: $HOME/muse-work/ml-python test_expected_hit.py
  (stdlib only; imports producer file read-only for RED demonstration).
