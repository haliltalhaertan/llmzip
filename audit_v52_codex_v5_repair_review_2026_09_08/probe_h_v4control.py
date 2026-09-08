"""Probe H -- ISOLATED original-v4 control for the two item-5 cases.

Run in its OWN process against the v4 base package only, so that no candidate
module of the same name can shadow it.
"""
import sys
from pathlib import Path
V4 = Path(sys.argv[1]).resolve()
CORE = Path(sys.argv[2]).resolve()
sys.path[:0] = [str(V4), str(CORE)]
import errors, membership_runner_v4 as R
print("PROVENANCE errors ->", Path(errors.__file__).resolve())
print("PROVENANCE runner ->", Path(R.__file__).resolve())
CANARY = "Where did Rashid park the blue van on the night of the storm?"
class IntSub(int):
    def __str__(self): return CANARY
    __repr__ = __str__
MAP = {"source_id": "s", "source_sha256": "0"*64, "benchmark": R.LOCOMO,
       "expected_cluster_ids": ["c0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "c0"}, "n_questions": 1}
for tag, val in [("exact int 5", 5), ("int SUBCLASS 5", IntSub(5)), ("str", CANARY)]:
    try:
        R.verify_source_identity(["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=val))
        print("  v4 %-18s -> returned" % tag)
    except BaseException as e:
        print("  v4 %-18s -> %s: %s" % (tag, type(e).__name__, str(e)[:150]))
        print("  v4 %-18s    canary: %s" % ("", CANARY in str(e)+repr(e)))
