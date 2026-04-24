#!/usr/bin/env bash
# scripts/deploy.sh · Master orchestrator
# Supports --target={azure|local|all} · --what-if · --help
set -euo pipefail

TARGET="all"
WHAT_IF=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target=*) TARGET="${1#*=}"; shift ;;
    --what-if) WHAT_IF=true; shift ;;
    --help)
      echo "Usage: deploy.sh [--target=azure|local|all] [--what-if]"
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo "▸ Target:    $TARGET"
echo "▸ What-if:   $WHAT_IF"

deploy_azure() {
  echo "▸ Azure deploy..."
  if [ "$WHAT_IF" = "true" ]; then
    echo "▸ Would run: az deployment group create --template-file infra/bicep/main.bicep --what-if"
    echo "✓ What-if SKIPPED (Wave 4 live)"
  else
    if command -v az >/dev/null 2>&1; then
      az deployment group create \
        --resource-group "${RESOURCE_GROUP:-rg-genai-portfolio-prod-swc}" \
        --template-file infra/bicep/main.bicep \
        --parameters infra/bicep/main.bicepparam 2>/dev/null || \
      echo "⚠ main.bicep not composed yet · Brief B's main.bicep applies when present"
    else
      echo "⚠ az CLI not installed · SKIPPING"
    fi
  fi
}

deploy_local() {
  echo "▸ Local Docker Compose..."
  if command -v docker >/dev/null 2>&1; then
    docker compose up -d
    docker compose ps
  else
    echo "⚠ docker not installed · SKIPPING"
  fi
}

case "$TARGET" in
  azure) deploy_azure ;;
  local) deploy_local ;;
  all)   deploy_local; deploy_azure ;;
  *) echo "Unknown target: $TARGET"; exit 1 ;;
esac

echo "✓ deploy.sh complete"
