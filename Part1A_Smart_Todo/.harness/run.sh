#!/usr/bin/env sh
set -u

cd "$(dirname "$0")/.." || exit 1
exec python3 .harness/run_harness.py
