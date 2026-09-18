# MY_NUMBERS.md — frozen independent recomputation (STEP 1)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Status: FROZEN. Written 2026-09-14 before reading the audited code. DO NOT EDIT.
Independence note (honest): I am NOT fully independent — I was commissioned by the
party whose work I audit, and my brief quoted their numbers before I computed mine.
I wrote my own implementation from the method description only (my_axis.py in this
directory) and did not open their .py files before computing these.

Method (VERIFIED — my own code, locator: my_axis.py in this directory):
- Per archive, rank 96 axes by mean_i(C_ij^2) descending; TOP-m = first m.
- SIGN FR@3 = Hamming on (C>=0),(qC>=0) over TOP-m (lower better).
- FLOAT FR@3 = cosine on raw cached C over TOP-m (higher better).
- FR@3 = mean over queries of exact tie expectation
  E = (g_strict + g_tied * slots / bc) / |gold|, K=3.
- Caches used as-is (NO re-centering). Fractional recall (NOT all-in-top3).

Budget-matched Delta = sign − float, percentage points.

## LongMemEval (VERIFIED, n=470 queries; min N=396, min |gold|=1)

| m  | sign %    | float %   | Delta pp  |
|----|-----------|-----------|-----------|
| 8  | 9.031521  | 20.879433 | -11.847912 |
| 32 | 25.280733 | 31.581560 | -6.300827 |
| 48 | 35.205674 | 34.914894 | +0.290780 |
| 64 | 43.185185 | 39.507092 | +3.678093 |
| 96 | 54.213357 | 44.159574 | +10.053783 |

## PerLTQA (VERIFIED, n=8265 queries over 30 char archives; min arch N=293)

| m  | sign %    | float %   | Delta pp  |
|----|-----------|-----------|-----------|
| 8  | 14.520363 | 30.920997 | -16.400634 |
| 32 | 38.343936 | 50.045423 | -11.701487 |
| 48 | 41.882037 | 51.351704 | -9.469667 |
| 64 | 44.696544 | 52.963003 | -8.266459 |
| 96 | 48.894480 | 55.169207 | -6.274728 |

Controls (VERIFIED): m=96 Delta reproduces the frozen-headline controls quoted in my
brief to 6 decimals: LME +10.053783 (brief: +10.053783), PerLTQA −6.274728
(brief: −6.274728).

My zero-norm policy (decision recorded): cosine with zero denominator → NaN → ranked
last (equivalent to −inf). No zero denominators were encountered at m=96; subset-m
encounters (if any) rank those rows last. Their code reportedly uses nan_to_num(−2.0);
I did NOT copy that — ranking effect is identical (below the [−1,1] cosine range).
