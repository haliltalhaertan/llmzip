#!/bin/bash
# Bir denetim rolunu calistirir; kota/tasima hatalarinda yeniden dener.
# Kullanim: run_role.sh <rol>
export PATH="$HOME/.local/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
B=/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r3
R="$1"
P="$B/$R/$R.txt"
L="$B/$R/$R.log"
MIN=4000          # 4 KB alti = gercek rapor degil
MAX_TRY=4

test -s "$P" || { echo "PROMPT_MISSING:$R"; exit 2; }
cd "$B/$R" || exit 1

for try in $(seq 1 $MAX_TRY); do
  muse exec --disable-approval --trust-workspace --reasoning-effort xhigh \
      --prompt-file "$P" > "$L" 2>&1 &
  MPID=$!
  while kill -0 $MPID 2>/dev/null; do sleep 20; done
  SZ=$(wc -c < "$L" 2>/dev/null || echo 0)

  if [ "$SZ" -ge "$MIN" ]; then
    echo "ROLE_DONE:$R try=$try bytes=$SZ"
    exit 0
  fi

  cp "$L" "$B/$R/$R.fail$try.log" 2>/dev/null
  if grep -q "quota exhausted" "$L" 2>/dev/null; then
    echo "QUOTA_WAIT:$R try=$try"; sleep 900
  else
    echo "SHORT_LOG:$R try=$try bytes=$SZ"; sleep 60
  fi
done
echo "ROLE_FAILED:$R after $MAX_TRY tries"
exit 3
