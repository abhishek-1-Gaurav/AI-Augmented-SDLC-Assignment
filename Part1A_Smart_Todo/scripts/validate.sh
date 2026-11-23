#!/usr/bin/env sh
set -eu

start_seconds=$(date +%s)

python3 -m pip install -e ".[dev]" >/dev/null
python3 -m pytest
python3 -m ruff check .
python3 -m ruff format --check src tests
python3 -m bandit -q -r src
python3 -m smart_todo --help >/dev/null

end_seconds=$(date +%s)
elapsed=$((end_seconds - start_seconds))
echo "Validation completed in ${elapsed}s"
