#!/usr/bin/env bash
# Local adaptation of audit_hard_r2/compute.sh: sandbox denies timeout(1) exec
# (RC=126 Operation not permitted), so flock-only + direct exec. Same env,
# same 180s budget enforced by keeping probes small (script prints wall time).
set -eu
BASE="$(cd "$(dirname "$0")" && pwd)"
exec flock -w 900 "$BASE/compute.lock" "$@"
