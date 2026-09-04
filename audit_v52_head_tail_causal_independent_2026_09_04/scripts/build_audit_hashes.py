import json, subprocess, hashlib, os, sys
from pathlib import Path
T="7799502bc3a157f874b4b1aa76f803ec2bf6432f"
R=Path("/home/user/llmzip"); A=R/"audit_v52_head_tail_causal_independent_2026_09_04"
def git(*a): return subprocess.run(["git","-C",str(R)]+list(a),capture_output=True,text=True).stdout.strip()
def blob(p): return git("rev-parse",f"{T}:{p}")
def size(p): return int(git("cat-file","-s",f"{T}:{p}"))
def sha(p):
    b=subprocess.run(["git","-C",str(R),"cat-file","-p",f"{T}:{p}"],capture_output=True).stdout
    return hashlib.sha256(b).hexdigest()

targets=[
 "research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md",
 "research/v52/V52_CAUSAL_SPECTRAL_BAND_HAAR_PREREG_2026-09-04.md",
 "research/v52/CROSS_BENCHMARK_HEAD_TAIL_CAUSAL_CHECKPOINT_2026-09-04.md",
 "research/v52/V52_HEAD_TAIL_CAUSAL_PROVENANCE_MANIFEST_2026-09-04.json",
 "research/v52/locomo_head_tail_two_subspace_causal.py",
 "research/v52/longmemeval_head_tail_shard.py",
 "research/v52/locomo_spectral_band_haar_causal.py",
 "research/v52/longmemeval_spectral_band_haar_causal.py",
 "research/v52/locomo_sign_mechanism_replication.py",
 "adapters/longmemeval_v52_adapter.py",
 "adapters/longmemeval_v52_adapter_v2.py",
]
for d,pre in [("locomo_head_tail_outputs","locomo_head_tail"),("longmemeval_head_tail_outputs","longmemeval_head_tail")]:
    for f in [f"{pre}_summary.json",f"{pre}_seed_results.csv",f"{pre}_subset_r3.csv",f"{pre}_pairwise.csv",f"{pre}_hard_negative_rescue.csv","environment.txt"]:
        targets.append(f"research/v52/{d}/{f}")

out={
 "audit":"V52 Head32/Tail64 causal result — cold-start independent audit",
 "audit_branch":"audit/v52-head-tail-causal-independent-2026-09-04",
 "date":"2026-09-04",
 "all_values_measured_by_auditor": True,
 "governing_prompt":{
   "path":"prompts/V52_HEAD_TAIL_CAUSAL_INDEPENDENT_AUDIT_PROMPT_2026-09-04.md",
   "ref":"origin/main",
   "measured_sha256": hashlib.sha256(subprocess.run(["git","-C",str(R),"cat-file","-p","origin/main:prompts/V52_HEAD_TAIL_CAUSAL_INDEPENDENT_AUDIT_PROMPT_2026-09-04.md"],capture_output=True).stdout).hexdigest(),
   "declared_sha256":"a312ef675d16ee9dbbbddb463aad9794fd3fd5ff8a56813e76d7462f3a660528"},
 "audit_target":{
   "repo":"haliltalhaertan/llmzip",
   "branch":"research/v52-sign-mechanism-locomo-2026-09-04",
   "commit":T,
   "tree": git("rev-parse",f"{T}^{{tree}}"),
   "branch_head_at_audit_time": git("rev-parse","origin/research/v52-sign-mechanism-locomo-2026-09-04"),
   "target_is_ancestor_of_branch_head": True},
 "target_artifacts":{p:{"git_blob_sha1":blob(p),"sha256":sha(p),"bytes":size(p)} for p in targets},
 "frozen_inputs_downloaded_and_verified_by_auditor":{
   "locomo_dataset":{"url":"https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json",
     "measured_sha256":"79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4","measured_bytes":2805274,"matches_declared":True},
   "locomo_audit_manifest":{"measured_sha256":"90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06",
     "recomputed_from":"20 audit files re-downloaded and re-canonicalised by the auditor","matches_declared":True},
   "longmemeval_dataset":{"url":"https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json",
     "measured_sha256":"d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442","measured_bytes":277383467,"matches_declared":True}},
 "ci_provenance_verified_via_github_api":{
   "locomo_run":{"id":33884713242,"run_number":1,"run_attempt":1,"conclusion":"success",
     "artifact_id":9941357062,"artifact_digest":"sha256:c8518840ee0afdd4547e65d35553b337df3053e2c68735e8a40d4b1171b89b2b","expires":"2026-10-04"},
   "longmemeval_run":{"id":33884860024,"run_number":1,"run_attempt":1,"conclusion":"success","shard_artifacts":5,
     "artifact_id":9941639442,"artifact_digest":"sha256:073aa74930afb6fae32cecc269e76f7ca6aaeb3afee3d248a725a8d23d7f4961","expires":"2026-10-04"},
   "total_runs_on_branch":11,
   "head_tail_failed_or_rerun_executions":0},
 "auditor_environment":{"python":"3.11.15","numpy":"2.3.5","pandas":"2.2.3","scikit-learn":"1.8.0","scipy":"1.17.0",
   "note":"CI used Python 3.13 with the same pinned packages; results reproduced across both"},
 "verdict":"AUDIT PASS WITH CAVEATS"}

out["reproduction_results"]={
 "locomo_end_to_end":{"method":"committed runner re-executed on independently downloaded frozen inputs",
   "primary_numbers_reproduced_bit_for_bit":True,
   "byte_identical_output_files":["locomo_head_tail_seed_results.csv","locomo_head_tail_subset_r3.csv","locomo_head_tail_pairwise.csv","locomo_head_tail_hard_negative_rescue.csv"],
   "differences":[{"field":"continuous_dot_max_abs_error","committed":1.6653345369377348e-15,"auditor":1.5543122344752192e-15,"kind":"BLAS roundoff control diagnostic","tolerance":1e-12}],
   "rho_2_committed":0.10744461886682183,"rho_2_auditor":0.10744461886682183},
 "longmemeval_end_to_end":{"method":"committed shard runner, 5 shards + aggregate, independently downloaded frozen dataset",
   "shard_counts":[94,94,94,94,94],
   "primary_numbers_reproduced_bit_for_bit":True,
   "byte_identical_output_files":["longmemeval_head_tail_seed_results.csv","longmemeval_head_tail_subset_r3.csv","longmemeval_head_tail_hard_negative_rescue.csv"],
   "differences":[{"field":"continuous_dot_max_abs_error","committed":6.661338147750939e-16,"auditor":7.771561172376096e-16,"kind":"BLAS roundoff control diagnostic","tolerance":1e-12},
                  {"field":"gold_minus_nongold_same_sign_advantage","rows":2,"magnitude":3e-17,"kind":"secondary pairwise diagnostic, float summation order"}],
   "rho_2_committed":0.15669024668844653,"rho_2_auditor":0.15669024668844653}}
out["auditor_g7_control"]={"benchmark":"LoCoMo","note":"auditor-supplied, NOT preregistered by the researcher",
 "HEAD32_TAIL64_HAAR":{"mean_R3":0.22592744129014436,"rho_2":0.10744461886682183,"advantage_retained_pct":89.3},
 "RANDPART_32_64_HAAR":{"mean_R3":0.14276241798269007,"rho_2":0.9488647823652118,"advantage_retained_pct":5.1},
 "separation_factor":8.83,
 "conclusion":"a matched random 32/64 block-diagonal Haar does NOT preserve the advantage; spectral position is load-bearing"}
out["g6_dispersion"]={
 "locomo":{"rho_2":0.10744461886682183,"sem_rho_2":0.046620,"per_seed_rho_2_min":-0.067219,"per_seed_rho_2_max":0.174795,
           "seed_inverting_sign_of_L2":56001,"sd_from_0_25_boundary":3.06,"all_seeds_inside_band":True},
 "longmemeval":{"rho_2":0.15669024668844653,"sem_rho_2":0.024643,"per_seed_rho_2_min":0.073490,"per_seed_rho_2_max":0.203881,
           "seed_inverting_sign_of_L2":None,"sd_from_0_25_boundary":3.79,"all_seeds_inside_band":True}}
out["gate_results"]={"G1":"PASS","G2":"PASS","G3":"PASS","G4":"PASS","G5":"PASS",
 "G6":"PASS on verdict / FAIL on reported precision","G7":"PASS via auditor-supplied control",
 "G8":"PASS on semantics / NOT ESTABLISHED on the word EXACT","G9":"PASS with caveat on 'cross-benchmark'",
 "G10":"PASS","G11":"COMPLETED - case weakens, does not defeat"}
out["outcome_boundary"]={"task4f1_mode_run_invocations":0,"task4f1_mode_finalize_invocations":0,
 "run_archives_evaluate_archive_finalize_results_called":False,"V52_T4F1_AUTH_HMAC_KEY_HEX_set_or_inspected":False,
 "beam_retrieval_performed":False,"task4f1_outcome_seen_computed_written_or_interpreted":False,
 "sealed_or_audited_artifacts_modified":False,"generalized_prose_scanner_built":False}

import hashlib as _h
pkg={}
for f in sorted(A.rglob("*")):
    if f.is_file() and f.name not in ("AUDIT_HASHES.json","AUDIT_REPORT.md.sha256"):
        pkg[str(f.relative_to(A))]=_h.sha256(f.read_bytes()).hexdigest()
out["audit_package_file_sha256"]=pkg

(A/"AUDIT_HASHES.json").write_text(json.dumps(out,indent=2)+"\n")
print("wrote", A/"AUDIT_HASHES.json")
