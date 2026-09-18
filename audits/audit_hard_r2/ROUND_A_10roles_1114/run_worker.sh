#!/usr/bin/env bash
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
ROLE="$1"
export PATH="$HOME/.local/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd "$BASE/$ROLE" || exit 2
test -s prompt.txt || exit 3
printf '%s
' "$$" > wrapper.pid
timeout 2400 muse exec --disable-approval --trust-workspace --reasoning-effort xhigh --prompt-file "$BASE/$ROLE/prompt.txt" > "$BASE/$ROLE/run.log" 2>&1 &
MPID=$!
printf '%s
' "$MPID" > runner.pid
wait "$MPID"
RC=$?
printf '%s
' "$RC" > exit_code.txt
printf '%s MUSE_EXIT:%s
' "$ROLE" "$RC"
exit "$RC"
