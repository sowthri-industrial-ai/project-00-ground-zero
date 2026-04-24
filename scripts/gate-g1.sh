#!/usr/bin/env bash
# scripts/gate-g1.sh · G1 · Build gate
# Exit 0 if build artifacts valid OR content absent (Wave 2 skip)
set -euo pipefail

MODE="${1:-check}"
ARTIFACT="as-built/g1-result.json"
mkdir -p as-built

has_python_code() {
  [ -d src ] && find src -type f -name "*.py" ! -name "__init__.py" | grep -q .
}

if [ ! -f pyproject.toml ] && ! has_python_code; then
  cat > "$ARTIFACT" <<EOF
{"gate": "G1-build", "status": "SKIPPED", "reason": "no-pyproject no-python-files", "wave": "2"}
EOF
  echo "SKIPPED · G1 deferred to Wave 3"
  exit 0
fi

if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then
  if uv sync --frozen 2>/dev/null; then
    cat > "$ARTIFACT" <<EOF
{"gate": "G1-build", "status": "PASS", "reason": "uv-sync-ok"}
EOF
    echo "PASS · G1 build"
    exit 0
  fi
fi

cat > "$ARTIFACT" <<EOF
{"gate": "G1-build", "status": "FAIL", "reason": "build-failed"}
EOF
echo "FAIL · G1 build"
exit 1
