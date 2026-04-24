#!/usr/bin/env bash
# Launch Streamlit UI with correct PYTHONPATH
# Usage: bash scripts/run-ui.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
exec streamlit run src/ui/streamlit_app.py "$@"
