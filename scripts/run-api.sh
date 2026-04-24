#!/usr/bin/env bash
# Launch FastAPI with correct PYTHONPATH
# Usage: bash scripts/run-api.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
exec uvicorn src.main:app --reload --port 8000
