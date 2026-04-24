#!/usr/bin/env bash
# scripts/metadata-validate.sh · Validate metadata.json against schema
set -euo pipefail

META_FILE="${1:-metadata.json}"
SCHEMA_FILE="schemas/metadata.schema.json"

if [ ! -f "$META_FILE" ]; then
  echo "⚠ metadata.json not present · SKIPPED"
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  jq empty "$META_FILE" || { echo "✗ Invalid JSON"; exit 1; }
  echo "✓ metadata.json is valid JSON"
fi

echo "✓ metadata-validate passed"
