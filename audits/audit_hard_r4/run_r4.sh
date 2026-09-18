#!/bin/bash
# R4: kota-korumali, SIRALI calisma. Haftalik kota %94 dolu -> ayni anda
# en fazla 1 ajan, aralarinda mola. 429 gorurse dener ve durur (kotayi yakmaz).
export PATH="$HOME/.local/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1
B=/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r4
MIN=4000
S="$B/STATUS.txt"

note(){ echo "[$(date '+%H:%M:%S')] $*" >> "$S"; }

# kota kontrolu: ucuz bir cagri
probe(){
  timeout 120 muse exec --disable-approval --reasoning-effort low "Reply exactly: OK" 2>&1 | tail -3
}

note "R4 basladi"
P=$(probe)
if echo "$P" | grep -q "quota exhausted"; then
  note "KOTA HALA DOLU - hicbir ajan baslatilmadi, is iptal"
  echo "QUOTA_STILL_EXHAUSTED"; exit 0
fi
note "kota acik, ajanlar sirayla kosacak"

for R in bench3_producer ladder_indep; do
  P="$B/$R/$R.txt"; L="$B/$R/$R.log"
  test -s "$P" || { note "$R: prompt yok, atlandi"; continue; }
  cd "$B/$R" || continue

  note "$R basliyor"
  muse exec --disable-approval --trust-workspace --reasoning-effort xhigh \
       --prompt-file "$P" > "$L" 2>&1 &
  MPID=$!
  while kill -0 $MPID 2>/dev/null; do sleep 30; done
  SZ=$(wc -c < "$L" 2>/dev/null || echo 0)

  if grep -q "quota exhausted" "$L" 2>/dev/null; then
    note "$R: KOTA BITTI (${SZ}B) - kalan roller iptal, kota korunuyor"
    echo "QUOTA_HIT_AT:$R"; exit 0
  fi
  if [ "$SZ" -ge "$MIN" ]; then
    note "$R: TAMAM (${SZ}B)"
  else
    note "$R: KISA LOG (${SZ}B) - tekrar denenmedi, kota korunuyor"
  fi
  sleep 60
done

note "R4 bitti"
echo "R4_DONE"
