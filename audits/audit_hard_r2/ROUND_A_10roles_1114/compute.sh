#!/usr/bin/env bash
set -eu
BASE="$(cd "$(dirname "$0")" && pwd)"
exec flock -w 900 "$BASE/compute.lock" timeout 180 "$@"
