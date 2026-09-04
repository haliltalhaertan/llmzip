#!/usr/bin/env bash
# Re-verify every identity this audit binds to. Run from the repo root.
# Prints MATCH/MISMATCH per item. Exit 1 if anything mismatches.
set -uo pipefail
T=7799502bc3a157f874b4b1aa76f803ec2bf6432f
rc=0
chk(){ if [ "$2" = "$3" ]; then echo "MATCH    $1"; else echo "MISMATCH $1"; echo "   expected $3"; echo "   measured $2"; rc=1; fi; }

echo "== git blob ids at $T =="
b(){ git rev-parse "$T:$1"; }
chk "prereg (head/tail)"        "$(b research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md)" 0d34207be55a75194b585789c7139cbc8aeb264d
chk "prereg (spectral band)"    "$(b research/v52/V52_CAUSAL_SPECTRAL_BAND_HAAR_PREREG_2026-09-04.md)"          02aa91a12b4052bbb2f0a6617167c8851e4f71f7
chk "LoCoMo summary"            "$(b research/v52/locomo_head_tail_outputs/locomo_head_tail_summary.json)"      228f756447e70c73f40b6074a44f13acabdabc08
chk "LongMemEval summary"       "$(b research/v52/longmemeval_head_tail_outputs/longmemeval_head_tail_summary.json)" 86b3718a9af1d6f86a0a3478ad0b83bf6dd0caf8
chk "cross-benchmark checkpoint" "$(b research/v52/CROSS_BENCHMARK_HEAD_TAIL_CAUSAL_CHECKPOINT_2026-09-04.md)"  9923c5284c04dd9b2acb345dcb7f0c92e4584b06
chk "LoCoMo runner"             "$(b research/v52/locomo_head_tail_two_subspace_causal.py)"                     cb16d4136c6280875b7c5875ffd89f9fc01cb810
chk "LongMemEval shard runner"  "$(b research/v52/longmemeval_head_tail_shard.py)"                              184a8a4bbb7d991c875ee1dcb92aa85b5e718074
chk "LoCoMo base module"        "$(b research/v52/locomo_spectral_band_haar_causal.py)"                         7c4140252fb7f846d617189925cdf534515743f4
chk "LongMemEval base module"   "$(b research/v52/longmemeval_spectral_band_haar_causal.py)"                    79dd4a5ec462102da5d82530088a4b7e89bef437

echo "== SHA-256 of file contents at $T =="
s(){ git cat-file -p "$T:$1" | sha256sum | cut -d' ' -f1; }
chk "prereg sha256"             "$(s research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md)" 6830c91b01d5df1a87b1a76f25b0101049b47c292c6ea867f48988998aa5ff05
chk "checkpoint sha256"         "$(s research/v52/CROSS_BENCHMARK_HEAD_TAIL_CAUSAL_CHECKPOINT_2026-09-04.md)"   9cc773d9153c3dbb6431044e4123c026a15aa6000a7796060590f8e18bc2b9c3
chk "adapter v1 sha256"         "$(s adapters/longmemeval_v52_adapter.py)"                                      0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722
chk "adapter v2 sha256"         "$(s adapters/longmemeval_v52_adapter_v2.py)"                                   643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218

echo "== byte counts =="
n(){ git cat-file -s "$T:$1"; }
chk "prereg bytes"     "$(n research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md)" 6624
chk "checkpoint bytes" "$(n research/v52/CROSS_BENCHMARK_HEAD_TAIL_CAUSAL_CHECKPOINT_2026-09-04.md)"   5190

echo "== governing audit prompt on origin/main =="
chk "audit prompt sha256" "$(git cat-file -p origin/main:prompts/V52_HEAD_TAIL_CAUSAL_INDEPENDENT_AUDIT_PROMPT_2026-09-04.md | sha256sum | cut -d' ' -f1)" a312ef675d16ee9dbbbddb463aad9794fd3fd5ff8a56813e76d7462f3a660528
exit $rc
