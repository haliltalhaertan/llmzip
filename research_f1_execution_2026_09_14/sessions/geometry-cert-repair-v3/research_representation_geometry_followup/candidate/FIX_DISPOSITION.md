[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# FIX_DISPOSITION.md -- root-cause repair disposition for BULGU-1 (+BULGU-5).

Scope: additive repair of the BLOCKING finding against the published flawed
package `research_representation_geometry_2026_09_13/repairs/rank_cert/`
(which stays byte-identical with its REQUEST_CHANGES audit; manifest 73/73
re-verified, before/after full-tree hashes identical). All new files live
under `research_representation_geometry_followup/candidate/` (relative
paths below; absolute machine paths deliberately excluded from this
manifest). No other audit finding is closed by this report.

## 1. Root cause (BULGU-1), confirmed by execution

POC `p=(-100,100,0,10000)`, `q=(-200,200,70000,0)`, `J=[1,4]`: truth VARIES
(+1 on (1,7/4), tie 7/4, -1 on (7/4,4]); archived v2 certifies
ISOLATED_TIES direction -1 (receipt `receipts/red_vs_v2.txt`, exit 1, the
failure IS the wrong claim). Two coupled defects in
`certify_v2.py::certify_pair`:

(a) `rational_roots` budget skip (`certify_v2.py:263-264,372-375`): at K=100
    scaling the enumeration exceeds `limit` and silently drops the exact
    pre-cut at 7/4 (unscaled twin pre-cuts it and returns VARIES). Budget
    skip changes behavior under score-preserving scaling.
(b) Both isolator branches (`certify_v2.py:469-498` discriminator-fired and
    `505-539` same-sign) count crossings ONLY over bisection brackets
    (`n_cross`); bisection exact-hits (here 7/4) are logged as ties but
    never crossing/tangent-classified, and the flanking cells are never
    sampled. `n_cross=0` falls through to `dirs.add(vm)` -- ONE midpoint
    sample (5/2 -> -1) certifying the whole (1,4) interval with an
    unhandled crossing root inside.

## 2. Old -> new mapping

| # | Old (archived, untouched) | New (candidate/) | What changed |
|---|---|---|---|
| 1 | `certify_v2.py:469-498` + `505-539` (duplicated bracket-only classification, single-sample fallback) | `certify_v3.py:379-501` `_classify_isolated_roots`, called once from `certify_v3.py:503-689` for BOTH branches | ONE shared routine: every exact root sign-filtered via the actual comparator and crossing/tangent-classified from proven root-free neighbour cells; every cell proven root-free (Sturm 0) and sampled; bracket interiors skipped as root-holding by construction with endpoint-verdict evidence; any gap refuses (UNRESOLVED) |
| 2 | `certify_v2.py:372-375` skip note (pre-cut silently dropped) | `certify_v3.py` pre-cut block + isolator exact-hit/bracket path | Skip only logged; soundness never depends on the pre-cut (proven: K=1/7/100/1000 identical verdicts, `scale-*` checks) |
| 3 | `fuzz_rates.py:74-114` `validate_cert` (no order sampling for single-direction ISOLATED_TIES; passes the counterfeit) | `cert_validator_v3.py:191-384` `validate_cert_v3` | Independent module: own comparator/P-expansion/Sturm, never imports certify_v3 or archived code, never trusts claimed direction; interval/root COVERAGE proof (critical-point partition incl. independently recomputed numerator zeros; sign-decided vs proven-root-free cells); rejects the literal counterfeit |
| 4 | (none -- v2 refuses these silently or wrongly) | `certify_v3.py` guards | `L>=R` -> UNRESOLVED (v2 returned STRICT/0); zero-polynomial degenerate both-numerators-vanish -> UNRESOLVED; budget/precision exhaustion -> UNRESOLVED (never single-direction) |
| 5 | `certify_v2.py:1-15` contract prose ("never certifies something false" -- falsified) | `certify_v3.py:1-50` contract | Soundness rule spelled out (unknown stays unknown); same public surface (`P4`, `certify_pair`, `DomainError`, `Unresolved`, cert-dict keys incl. `xbrackets`/`disc_fired`) |

Exact-arithmetic core (comparators, P expansion + interpolation audit,
Sturm/deflation, rational enumeration, bisection isolator) carried over
from `certify_v2.py` with provenance noted in the module docstring; the
archived file itself is unmodified (TREE_IDENTICAL receipt).

## 3. Evidence, by kind (do not mix them)

EXECUTED REPRODUCTION (the bug exists; the repair holds on the POC):
- `receipts/red_vs_v2.txt` (exit 1): archived v2 -> ISOLATED_TIES/-1,
  independent truth gate {5/4:+1,3/2:+1,7/4:0,5/2:-1,4:-1}.
- `receipts/green_red_poc.txt` (exit 0): v3 -> ISOLATED_TIES/VARIES.
- `certify_v3.py` smoke (`__main__`, exit 0): tangent +1, witness VARIES,
  POC VARIES asserted.

PROOF ARGUMENT (why finite tests are not the whole story):
- Single-direction verdicts rest on: (i) numerator-sign constancy between
  cuts (structural: all linear numerator roots are cuts); (ii) Sturm-count-0
  root-freedom per cell (proven per interval, not sampled); (iii) every
  isolated root classified from neighbour-cell evidence; (iv) endpoint
  deflation accounting for endpoint-coincident/multiple roots; (v) actual
  comparator samples throughout, so numerator-negative reversal needs no
  special case and cannot invert a verdict. Refusal paths (UNRESOLVED) cover
  skips, caps, floors, mismatches, and degenerate inputs.

SAMPLE FUZZ EVIDENCE (supporting, NOT proof; falsification-grade):
- `receipts/green_fuzz.txt` (exit 0, 8.1 s): n=2000 synthetic small-int
  pairs (seed 20260914, J=[1/16,16], eff=1759+6?/1765 non-domain-fail):
  orig-unresolved 631 -> v3-unresolved 0 (recovered 631);
  agree_viol=0, mono_viol=0, valid_fail=0 (independent validator accepts
  every v3 verdict), countersign_fail=0 (65 probes), varies_witness_fail=0,
  tie_surprise=0. SOUNDNESS: HOLD.
- `receipts/green_vertical.txt` (exit 0): 80/80 checks (POC cells, scales,
  score-preserving transforms k=2/3/5, swaps, exhaustion, invalid
  intervals, DOMAIN_FAIL, 8 labeled examples, 6 orig-agreement cases).
- `receipts/green_validator.txt` (exit 0): 19/19 (counterfeit rejected,
  9 genuine v3 certs accepted incl. UNRESOLVED-refusal acceptance,
  5 mutation rejections, scan-vs-proof distinction).

INCOMPLETE / NOT CLAIMED:
- No 'certified safe generally': finite tests cannot prove absence of
  unsound verdicts outside the tested synthetic distribution (small ints,
  one J, one fuzz seed + fixed cases). The proof argument above is the
  generality carrier, and it is code reasoning, not a machine-checked proof.
- Fuzz distribution is narrow by design (seal: synthetic only); large
  numerators/denominators, deep bisection chains, and adversarial
  near-multiple roots are covered only by unit exhaustion tests.
- Validator and generator share the DEFINITION of order (unavoidable) but
  no code and no trust; a definitional misunderstanding would still be
  common-mode. The inline truth comparators in tests are a third writing
  of the same definition.

## 4. Test counts

- RED regression `test_red_poc.py`: 1 outcome assertion (FAIL on v2 with
  the wrong claim, PASS on v3 with VARIES). One command each way (see §7).
- Vertical `test_certify_v3.py`: 80 checks, 80 pass.
- Validator `test_validate_v3.py`: 19 checks, 19 pass.
- Fuzz `fuzz_v3.py`: 2000 cases, eff 1765; 0 soundness violations.
- Total committed checks: 80 + 19 + 1 (+ 2000 fuzz cases).

## 5. Remaining findings: OPEN / untouched

BULGU-2 (T5_EVIDENCE 1/2500->1/625), BULGU-3 (`>=` vs `==` lock),
BULGU-4 (rank_cover supersedes line refs), BULGU-6 (d=2 structural-tie
composition), BULGU-7 ("independent" wording), BULGU-8 (mutation drivers
unpackaged), and all measurement observations F-01..F-07: OPEN, no action
taken here, no blanket REQUEST_CHANGES closure claimed. This repair closes
BULGU-1 (repair) and BULGU-5 (validator) only, pending independent review.

## 6. New-file manifest (sha256 at commit time; workspace-relative paths)

- research_representation_geometry_followup/candidate/STATUS.md
  27e69d5d7b5a6da4d49e6530c325193ade0db2debe0034262edb8037cd5e69cd
- research_representation_geometry_followup/candidate/certify_v3.py
  b920737c6123622918e3931659131320f4dbe423ade5408bb21d074725dae592
- research_representation_geometry_followup/candidate/cert_validator_v3.py
  aa1fc12bbc79e6176246b3ce0d6354e610d6c0aab65675498de6e183223f4a8a
- research_representation_geometry_followup/candidate/test_red_poc.py
  7a586b9b8c8e972d9de04cf45ebeb5ed4c6cdd2bcc16e840c5d411a721d0262e
- research_representation_geometry_followup/candidate/test_certify_v3.py
  7fe3e0af481daa33463a9cfde6b8df8f4aea41cda217e9415c6a853a41168090bdb5865ab49
- research_representation_geometry_followup/candidate/test_validate_v3.py
  0cc7b10632e8d27065f88a2f9e19f991f85a3a37e62fd0351314a83bad89e60f
- research_representation_geometry_followup/candidate/fuzz_v3.py
  f210b99bda02df851ae29b9ae73ebdebd7c1a0f950accfe8525a0a5713c97f7a
- research_representation_geometry_followup/candidate/UNRESOLVED_RATE_V3.json
  (generated artifact of fuzz_v3.py; re-generated by re-running §7)
- research_representation_geometry_followup/candidate/receipts/red_vs_v2.txt
- research_representation_geometry_followup/candidate/receipts/green_red_poc.txt
- research_representation_geometry_followup/candidate/receipts/green_vertical.txt
- research_representation_geometry_followup/candidate/receipts/green_validator.txt
- research_representation_geometry_followup/candidate/receipts/green_fuzz.txt
- research_representation_geometry_followup/candidate/receipts/before_hashes.sha256
- research_representation_geometry_followup/candidate/receipts/after_hashes.sha256
  (before/after diff: empty -- published tree byte-identical)

## 7. Reviewer commands (from the worktree root; no installs, no network)

  PYTHONDONTWRITEBYTECODE=1 python3 -B research_representation_geometry_followup/candidate/test_red_poc.py
    # default CERT_DIR: archived v2 -> exits 1 with FALSE SINGLE-DIRECTION CERTIFICATE
  CERT_DIR=research_representation_geometry_followup/candidate CERT_MODULE=certify_v3 \
    PYTHONDONTWRITEBYTECODE=1 python3 -B research_representation_geometry_followup/candidate/test_red_poc.py
    # exits 0, SOUND OUTCOME .../VARIES
  PYTHONDONTWRITEBYTECODE=1 python3 -B research_representation_geometry_followup/candidate/test_certify_v3.py
  PYTHONDONTWRITEBYTECODE=1 python3 -B research_representation_geometry_followup/candidate/test_validate_v3.py
  PYTHONDONTWRITEBYTECODE=1 python3 -B research_representation_geometry_followup/candidate/fuzz_v3.py

Independence note: same model family as the producing sessions (no
different-family independence claim); cold-start repair from the published
package + audits only; no other worker branch/output read (cold comparison
preserved). Original USER POC returning exit 0 documents the BUG's
existence, not repair success; repair tests assert the sound outcome
(VARIES with per-cell evidence / conservative UNRESOLVED refusal).
