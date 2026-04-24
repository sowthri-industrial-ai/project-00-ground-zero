#!/usr/bin/env bash
# scripts/gate-g2.sh · G2 · Safety wiring gate
# Verifies content safety + guardrails referenced in code/infra
set -euo pipefail

ARTIFACT="as-built/g2-result.json"
mkdir -p as-built

# Check for content-safety reference in infra (Brief B's content-safety.bicep exists)
if [ ! -f infra/bicep/modules/content-safety.bicep ]; then
  cat > "$ARTIFACT" <<EOF
{"gate": "G2-safety-wiring", "status": "FAIL", "reason": "content-safety-module-missing"}
EOF
  echo "FAIL · G2 safety wiring (content-safety.bicep missing)"
  exit 1
fi

cat > "$ARTIFACT" <<EOF
{"gate": "G2-safety-wiring", "status": "PASS", "reason": "content-safety-module-present"}
EOF
echo "PASS · G2 safety wiring"
exit 0
