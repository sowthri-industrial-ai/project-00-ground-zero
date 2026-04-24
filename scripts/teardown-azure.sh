#!/usr/bin/env bash
# scripts/teardown-azure.sh · Delete the RG · Wave 4+ operation
set -euo pipefail

RG="${RESOURCE_GROUP:-rg-genai-portfolio-prod-swc}"

if ! command -v az >/dev/null 2>&1; then
  echo "⚠ az CLI not installed"
  exit 1
fi

echo "▸ Deleting resource group: $RG"
az group delete --name "$RG" --yes --no-wait
echo "✓ Teardown initiated (async)"
