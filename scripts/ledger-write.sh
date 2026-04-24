#!/usr/bin/env bash
# scripts/ledger-write.sh · Append an entry to as-built/ledger.jsonl
set -euo pipefail

ACTION=""
STATUS=""
ACTOR=""
SHA=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --action=*) ACTION="${1#*=}"; shift ;;
    --status=*) STATUS="${1#*=}"; shift ;;
    --actor=*)  ACTOR="${1#*=}"; shift ;;
    --sha=*)    SHA="${1#*=}"; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LEDGER="as-built/ledger.jsonl"
mkdir -p as-built

cat >> "$LEDGER" <<EOF
{"timestamp": "$TIMESTAMP", "action": "$ACTION", "status": "$STATUS", "actor": "$ACTOR", "sha": "$SHA"}
EOF

echo "✓ Ledger entry appended: $ACTION · $STATUS"
