#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 "$DIR/run-skill-tests.py" "$(cd "$DIR/.." && pwd)" en-US
elif command -v python >/dev/null 2>&1; then
  python "$DIR/run-skill-tests.py" "$(cd "$DIR/.." && pwd)" en-US
elif command -v node >/dev/null 2>&1; then
  node "$DIR/run-skill.mjs"
else
  echo "No supported runtime found (python3/python/node)." >&2
  exit 1
fi
