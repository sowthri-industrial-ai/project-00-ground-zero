#!/usr/bin/env bash
# scripts/gate-g3.sh · G3 · Health probe gate
# Exit 0 if endpoint healthy OR not deployed yet (Wave 4 activates)
set -euo pipefail

URL="${1:-}"
ARTIFACT="as-built/g3-result.json"
mkdir -p as-built

if [ -z "$URL" ]; then
  cat > "$ARTIFACT" <<EOF
{"gate": "G3-health-probe", "status": "SKIPPED", "reason": "no-url-provided"}
EOF
  echo "SKIPPED · G3 (no URL · Wave 4 activates)"
  exit 0
fi

if curl -sfL --max-time 5 "$URL/health" >/dev/null 2>&1; then
  cat > "$ARTIFACT" <<EOF
{"gate": "G3-health-probe", "status": "PASS", "url": "$URL"}
EOF
  echo "PASS · G3 health probe"
  exit 0
fi

cat > "$ARTIFACT" <<EOF
{"gate": "G3-health-probe", "status": "FAIL", "url": "$URL", "reason": "unreachable-or-unhealthy"}
EOF
echo "FAIL · G3 health probe"
exit 1
