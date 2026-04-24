# Builder Brief · C · Delivery Pipeline

```
Brief ID     · BRIEF-C
Block        · C · Delivery Pipeline
Project      · project-00-ground-zero
Wave         · 2 (parallel with Brief D)
Dependencies · Brief A (OIDC federation) · Brief B (Bicep modules + runtime contract)
Deliver to   · Architect chat for review
```

---

## § 01 · Context · You are here

You are Builder-C. Self-contained Brief · architectural choices locked in Charter + ADRs. Seek clarification only on acceptance-criteria ambiguity.

You are the Delivery Pipeline block. Your job: author the seven GitHub Actions workflows, the `deploy.sh` master orchestrator, the teardown workflow, the ledger writer, the four stage gates (G1–G4) with fail-closed enforcement, and the demo-grade instrumentation (narrative names · `$GITHUB_STEP_SUMMARY` · PR comment bot) that makes the pipeline itself a portfolio demonstration surface per ADR-0011.

**You run in parallel with Brief D.** D builds the PCP; you build the pipeline that writes to the ledger the PCP reads. Your ledger schema contract is load-bearing for D.

Reads Brief A's `platform-contract.yml` for OIDC · reads Brief B's `runtime-contract.yml` and Bicep modules for deploy targets.

---

## § 02 · Goals

1. Author `scripts/deploy.sh` master orchestrator (idempotent · fan-out to 4 targets · ledger-writing)
2. Author `scripts/teardown-azure.sh` + `teardown-azure.yml` workflow (ephemeral Azure per ADR-0013)
3. Author 7 GitHub Actions workflows with narrative names per ADR-0011
4. Implement G1–G4 stage gates · fail-closed
5. Implement `$GITHUB_STEP_SUMMARY` dashboards on every workflow
6. Implement PR comment bot (gate-status summary on every PR)
7. Implement ledger writer (`as-built/ledger.jsonl` append-only) + JSON schema
8. Implement `metadata.json` validator (JSON Schema)
9. Generate README status badges
10. Document in `docs/05-runbook.md` §§ 7–9

---

## § 03 · Non-Goals

- ❌ Do NOT modify Brief A's or B's modules (only consume them)
- ❌ Do NOT author PCP pages (Block D)
- ❌ Do NOT implement the three `demo-fails-*` branches (Block E · they need working Hello AI to fail against)
- ❌ Do NOT build Hello AI logic (Block E)
- ❌ Do NOT deploy to Azure during Wave 2 authoring (Wave 4 activates deploy · Wave 2 is dry-run / `--what-if` only)

---

## § 04 · Deliverables (exhaustive)

### Deliverable 1 · `scripts/deploy.sh` master orchestrator

At repo root of `project-00-ground-zero/scripts/deploy.sh`:

**Interface**:

```
./deploy.sh --target=local     # docker compose up (default)
./deploy.sh --target=git       # git push origin main (triggers CI)
./deploy.sh --target=hf        # sync /src to HF Space, /models to HF Hub
./deploy.sh --target=azure     # bicep deploy via az CLI (local dev path)
./deploy.sh --all              # fan out to all 4 targets in sequence
./deploy.sh --teardown         # full teardown (Azure RG + HF Space)
./deploy.sh --what-if          # dry-run (no actual deploys)
./deploy.sh --help
```

**Behaviors**:
- Idempotent: safe to run N times · no side-effect duplication
- Every target run ends with a ledger entry via `scripts/ledger-write.sh`
- Exit codes: 0 success · 1 target failure · 2 precondition failure (e.g. missing `platform-contract.yml`)
- Colorized output (tput or simple ANSI) with gate-marker headers: `[G1]`, `[G2]`, `[G3]`, `[G4]`
- Runs G1 locally before any deploy (can't deploy with failing unit tests)
- Runs G2 pre-deploy (schema validation · Content Safety config check)
- Runs G3 post-deploy (smoke tests per target)
- Runs G4 post-all-targets (full guardrail + eval regression)

**Precondition checks** before any work:
- `platform-contract.yml` exists and parses
- `runtime-contract.yml` exists and parses
- `metadata.json` validates against schema
- Git working tree clean (if `--target=git` or `--all`)
- `az login` status OK (if `--target=azure` or `--all`)
- `huggingface-cli login` status OK (if `--target=hf` or `--all`)
- Docker running (if `--target=local` or `--all`)

### Deliverable 2 · `scripts/teardown-azure.sh`

```bash
#!/usr/bin/env bash
# Teardown Azure resources for project-00-ground-zero
# Implements ADR-0013 ephemeral pattern · typical post-interview cleanup

set -euo pipefail

RG=$(yq '.azure.resource_group' platform-contract.yml)
SUBSCRIPTION=$(yq '.azure.subscription_id' platform-contract.yml)

echo "About to delete resource group: $RG in subscription $SUBSCRIPTION"
read -p "Confirm (y/N): " ok
[[ "$ok" != "y" ]] && exit 0

az account set --subscription "$SUBSCRIPTION"
az group delete --name "$RG" --yes --no-wait

echo "Teardown initiated · async · verify with 'az group show --name $RG'"
bash scripts/ledger-write.sh teardown HEALTHY 0.00
```

Separate workflow `teardown-azure.yml` (see Deliverable 3) allows one-click teardown from GitHub UI.

### Deliverable 3 · Seven GitHub Actions workflows

All at `.github/workflows/` in `project-00-ground-zero`. Each workflow gets a **narrative name** per ADR-0011.

#### Workflow 1 · `ci.yml`

```yaml
name: "🧪 G1 · Unit + Lint + Type"

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  g1-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with: { version: "0.4.x" }
      - name: Install dependencies
        run: uv sync --frozen
      - name: Ruff lint
        run: uv run ruff check src/ tests/
      - name: Ruff format check
        run: uv run ruff format --check src/ tests/
      - name: Type check
        run: uv run mypy src/
      - name: Unit tests with coverage
        run: uv run pytest tests/unit -v --cov=src --cov-report=term --cov-report=xml --cov-fail-under=70
      - name: Write step summary
        if: always()
        run: |
          {
            echo "## 🧪 G1 · Unit + Lint + Type"
            echo ""
            echo "| Check | Status |"
            echo "|---|---|"
            echo "| Ruff lint | ${{ job.status == 'success' && '✅' || '❌' }} |"
            echo "| Type check | ${{ job.status == 'success' && '✅' || '❌' }} |"
            echo "| Unit coverage | $(grep -oP 'line-rate="\K[^"]+' coverage.xml | head -1 | awk '{printf "%.1f%%", $1*100}') |"
          } >> $GITHUB_STEP_SUMMARY
      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with: { name: coverage-report, path: coverage.xml }
```

#### Workflow 2 · `deploy-azure.yml`

```yaml
name: "🚀 G2-G3 · Deploy Azure · OIDC + Bicep + Smoke"

on:
  workflow_dispatch:   # manual per ADR-0013 ephemeral pattern
  # NO push trigger · Azure deploys are deliberate, not automatic

permissions:
  id-token: write      # required for OIDC
  contents: read

jobs:
  g2-precheck:
    runs-on: ubuntu-latest
    outputs:
      ready: ${{ steps.check.outputs.ready }}
    steps:
      - uses: actions/checkout@v4
      - id: check
        run: |
          # G2: schema validate metadata.json
          uv run python scripts/validate-metadata.py
          # G2: content safety config exists in Bicep
          grep -q "content-safety.bicep" infra/bicep/main.bicep || { echo "::error::Content Safety not wired"; exit 1; }
          echo "ready=true" >> $GITHUB_OUTPUT

  deploy:
    needs: g2-precheck
    if: needs.g2-precheck.outputs.ready == 'true'
    runs-on: ubuntu-latest
    environment: production   # GitHub environment · can require reviewer
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Bicep deploy
        run: |
          az deployment group create \
            --resource-group $(yq '.azure.resource_group' platform-contract.yml) \
            --template-file infra/bicep/main.bicep \
            --parameters @infra/bicep/parameters/prod.bicepparam
      - name: Capture endpoints
        id: endpoints
        run: |
          # Pull deployed endpoints from deployment output
          HELLO_URL=$(az deployment group show ... --query 'properties.outputs.helloAiUrl.value' -o tsv)
          echo "hello_url=$HELLO_URL" >> $GITHUB_OUTPUT
      - name: G3 Smoke test
        run: |
          for i in {1..10}; do
            curl -fsS --max-time 5 "${{ steps.endpoints.outputs.hello_url }}/health" && break
            echo "Waiting for endpoint to warm... ($i/10)"
            sleep 10
          done
      - name: Write ledger entry
        if: always()
        run: bash scripts/ledger-write.sh deploy-azure ${{ job.status == 'success' && 'HEALTHY' || 'REJECTED' }}
      - name: Write step summary
        if: always()
        run: |
          {
            echo "## 🚀 Deploy Azure · run #${{ github.run_number }}"
            echo ""
            echo "- **Commit**: ${{ github.sha }}"
            echo "- **Gate G2**: ${{ needs.g2-precheck.outputs.ready == 'true' && '✅' || '❌' }}"
            echo "- **Gate G3 Smoke**: ${{ job.status == 'success' && '✅' || '❌' }}"
            echo "- **Hello AI endpoint**: ${{ steps.endpoints.outputs.hello_url }}"
            echo "- **Ledger**: see as-built/ledger.jsonl"
          } >> $GITHUB_STEP_SUMMARY
```

#### Workflow 3 · `teardown-azure.yml`

```yaml
name: "🗑️ Teardown · Azure (ephemeral cleanup)"

on:
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  teardown:
    runs-on: ubuntu-latest
    environment: production   # same env protection as deploy
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Delete resource group
        run: |
          RG=$(yq '.azure.resource_group' platform-contract.yml)
          az group delete --name "$RG" --yes --no-wait
      - name: Write ledger entry
        run: bash scripts/ledger-write.sh teardown-azure HEALTHY 0.00
      - name: Write step summary
        run: |
          {
            echo "## 🗑️ Teardown · Azure"
            echo ""
            echo "Resource group deleted · async · ephemeral cycle complete"
          } >> $GITHUB_STEP_SUMMARY
```

#### Workflow 4 · `sync-hf-space.yml`

```yaml
name: "🤗 Sync · HuggingFace Space (Hello AI demo)"

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'spaces/**'
      - 'Dockerfile'
      - 'requirements-hf.txt'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { lfs: true }
      - name: Push to HF Space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          pip install huggingface_hub==0.26.*
          python scripts/sync-hf-space.py
      - name: Write ledger entry
        if: always()
        run: bash scripts/ledger-write.sh sync-hf-space ${{ job.status == 'success' && 'HEALTHY' || 'REJECTED' }}
      - name: Write step summary
        if: always()
        run: |
          {
            echo "## 🤗 HuggingFace Space sync"
            echo "- **Space URL**: https://huggingface.co/spaces/<user>/project-00-ground-zero"
            echo "- **Status**: ${{ job.status == 'success' && '✅ synced' || '❌ failed' }}"
          } >> $GITHUB_STEP_SUMMARY
```

#### Workflow 5 · `sync-hf-model.yml`

Same pattern, triggered on `/models/**` path changes. Mirrors fine-tuned model to HF Hub.

#### Workflow 6 · `eval-regression-nightly.yml`

```yaml
name: "📊 Nightly · Eval Regression (RAGAS + DeepEval)"

on:
  schedule:
    - cron: '0 2 * * *'   # 02:00 UTC daily
  workflow_dispatch:

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - name: Run RAGAS eval suite
        run: uv run pytest tests/eval -v --junit-xml=eval-results.xml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}   # RAGAS needs an LLM-as-judge
      - name: Parse metrics vs baseline
        id: metrics
        run: |
          uv run python scripts/eval-threshold-check.py \
            --results eval-results.xml \
            --baseline .baseline/eval-baseline.json \
            --tolerance 0.05 \
            --output $GITHUB_STEP_SUMMARY
      - name: Write ledger entry
        if: always()
        run: bash scripts/ledger-write.sh eval-regression ${{ job.status }}
      - name: Upload eval artifact
        if: always()
        uses: actions/upload-artifact@v4
        with: { name: eval-results-${{ github.run_number }}, path: eval-results.xml, retention-days: 90 }
```

#### Workflow 7 · `red-team-weekly.yml`

```yaml
name: "🔴 Weekly · Red-team (Garak + PyRIT)"

on:
  schedule:
    - cron: '0 3 * * 1'   # 03:00 UTC Monday
  workflow_dispatch:

jobs:
  red-team:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen --extra red-team
      - name: Run Garak probes
        run: |
          uv run garak \
            --model_type openai.OpenAIGenerator \
            --model_name gpt-4o-mini \
            --probes promptinject,jailbreak.AutoDAN \
            --generations 5 \
            --report_prefix red-team-$(date -u +%Y%m%d)
      - name: Run PyRIT adversarial
        run: uv run python tests/red-team/pyrit_orchestrator.py
      - name: Parse findings
        id: findings
        run: |
          python scripts/red-team-summarize.py \
            --garak-report red-team-*.jsonl \
            --pyrit-report pyrit-results.json \
            --output $GITHUB_STEP_SUMMARY
      - name: Fail if critical findings
        run: |
          CRIT=$(jq '.critical_count' red-team-summary.json)
          [[ "$CRIT" -gt 0 ]] && { echo "::error::$CRIT critical findings"; exit 1; } || echo "No criticals"
      - name: Write ledger
        if: always()
        run: bash scripts/ledger-write.sh red-team ${{ job.status }}
      - uses: actions/upload-artifact@v4
        with: { name: red-team-${{ github.run_number }}, path: "red-team-*.jsonl pyrit-results.json red-team-summary.json" }
```

#### Workflow 8 · `pcp-update.yml`

(Consumer-of-deploys per ADR-0005 — triggered by ledger changes, not deploys.)

```yaml
name: "🏛️ PCP · Rebuild on ledger change"

on:
  push:
    branches: [main]
    paths:
      - 'as-built/ledger.jsonl'
      - 'metadata.json'
      - 'control-plane/**'
  workflow_dispatch:

jobs:
  build-pcp:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd control-plane && npm ci && npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: control-plane/dist }
      - uses: actions/deploy-pages@v4
```

**Note**: `pcp-update.yml` is technically Brief D's deliverable · include as a stub here that D fills. Document boundary clearly.

### Deliverable 4 · G1–G4 stage gate enforcement

| Gate | Script | Location | Fail behavior |
|---|---|---|---|
| G1 | `scripts/gate-g1.sh` | Pre-commit · ci.yml | Block commit / block merge |
| G2 | `scripts/gate-g2.sh` | deploy-azure.yml precheck | Deploy script refuses to run |
| G3 | `scripts/gate-g3.sh` | deploy-azure.yml post-deploy | Ledger marks UNHEALTHY · no G4 |
| G4 | `scripts/gate-g4.sh` | deploy-azure.yml + eval-regression | Deploy REJECTED · ledger logs specific metric |

Each gate script:
- Exit code 0 = pass · non-zero = fail
- Writes machine-readable result to `out/gate-<id>.json`
- Writes human-readable summary to `GITHUB_STEP_SUMMARY` if running in Actions

### Deliverable 5 · Ledger writer

`scripts/ledger-write.sh`:

```bash
#!/usr/bin/env bash
# Append to as-built/ledger.jsonl
# Usage: ledger-write.sh <action> <status> [cost_usd]

set -euo pipefail

ACTION="$1"    # deploy-azure, sync-hf-space, eval-regression, red-team, teardown, ...
STATUS="$2"    # HEALTHY, UNHEALTHY, REJECTED
COST="${3:-0.00}"

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SHA=${GITHUB_SHA:-$(git rev-parse HEAD)}
RUN=${GITHUB_RUN_NUMBER:-local}
GATES="${GATES:-}"    # caller may set e.g. "G1G2G3G4" or "G1G2G3-G4fail"

jq -c -n \
  --arg ts "$TS" \
  --arg action "$ACTION" \
  --arg status "$STATUS" \
  --arg cost "$COST" \
  --arg sha "$SHA" \
  --arg run "$RUN" \
  --arg gates "$GATES" \
  '{timestamp: $ts, action: $action, status: $status, cost_usd: ($cost | tonumber), commit_sha: $sha, run_number: $run, gates: $gates}' \
  >> as-built/ledger.jsonl
```

Ledger schema (document at `docs/03-ADR/0005-ledger-schema.md`):

```json
{
  "timestamp": "ISO-8601 UTC",
  "action": "deploy-azure | sync-hf-space | sync-hf-model | eval-regression | red-team | teardown",
  "status": "HEALTHY | UNHEALTHY | REJECTED",
  "cost_usd": 0.00,
  "commit_sha": "git SHA",
  "run_number": "GitHub Actions run number or 'local'",
  "gates": "G1G2G3G4 | G1G2G3-G4fail · summary string",
  "notes": "optional free-text"
}
```

### Deliverable 6 · `metadata.json` validator

`scripts/validate-metadata.py`:

```python
#!/usr/bin/env python
"""Validate metadata.json against schema."""
import json, sys
from jsonschema import validate, ValidationError

SCHEMA = json.load(open("schemas/metadata.schema.json"))
data = json.load(open("metadata.json"))

try:
    validate(instance=data, schema=SCHEMA)
    print("✅ metadata.json valid")
except ValidationError as e:
    print(f"❌ {e.message}", file=sys.stderr)
    sys.exit(1)
```

Schema file at `schemas/metadata.schema.json` · author per Charter § 13 and Brief A § 04 Deliverable 7.

### Deliverable 7 · PR comment bot

Workflow addition (extend `ci.yml`): uses `actions/github-script@v7` to post a summary comment on every PR.

```yaml
- name: PR status comment
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      const comment = `## 🤖 Ground Zero CI
      
      | Gate | Status |
      |---|---|
      | G1 · Unit + Lint | ${{ steps.g1.outcome == 'success' && '✅' || '❌' }} |
      | Coverage | ${{ env.COVERAGE_PCT || 'n/a' }} |
      
      Full run: [link](${{ github.event.pull_request.html_url }}/checks)`;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

### Deliverable 8 · README status badges

In `README.md` of `project-00-ground-zero`:

```markdown
[![CI](https://github.com/<user>/project-00-ground-zero/actions/workflows/ci.yml/badge.svg)](...)
[![Deploy](https://github.com/<user>/project-00-ground-zero/actions/workflows/deploy-azure.yml/badge.svg)](...)
[![Eval](https://github.com/<user>/project-00-ground-zero/actions/workflows/eval-regression-nightly.yml/badge.svg)](...)
[![Red-team](https://github.com/<user>/project-00-ground-zero/actions/workflows/red-team-weekly.yml/badge.svg)](...)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Ground Zero](https://img.shields.io/badge/phase-ground--zero-orange)](docs/00-charter.md)
[![Azure](https://img.shields.io/badge/cloud-Azure-0078D4)](infra/bicep)
[![HF Space](https://img.shields.io/badge/🤗-HF%20Space-yellow)](...)
```

### Deliverable 9 · Runbook §§ 7–9

- § 7 · Pipeline overview (7 workflows · when each triggers)
- § 8 · Stage gates (G1–G4 · fail behaviors · debug steps)
- § 9 · Ephemeral Azure pattern (deploy · demo · teardown cycle with commands)

---

## § 05 · Interface Contracts

### Contract IN · From Brief A

- `platform-contract.yml` — read `azure.*`, `entra.*`, `github.*` fields
- OIDC federation must be configured · you set GH Secrets for `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`

### Contract IN · From Brief B

- `infra/bicep/modules/` — you import these in `main.bicep` (you author `main.bicep`)
- `runtime-contract.yml` — your workflows reference Hello AI health endpoints from this

### Contract OUT · To Brief D (PCP)

- `as-built/ledger.jsonl` — append-only · schema documented in ADR-0005 derivative
- `metadata.json` — validated against `schemas/metadata.schema.json`
- Workflow run URLs · stable format for PCP to deep-link

### Contract OUT · To Brief E (Hello AI)

- `scripts/deploy.sh --target=<x>` contract · Brief E's `src/` must be deployable via these targets
- Health endpoint contract · `/health` must return 200 for G3 smoke test

---

## § 06 · Step-by-Step Implementation Guidance

### Step 1 · Set GH Actions secrets

Using `gh` CLI (never via repo settings UI · leaves an audit trail):

```bash
# Read from platform-contract.yml
CLIENT_ID=$(yq '.entra.app_client_id' platform-contract.yml)
TENANT_ID=$(yq '.azure.tenant_id' platform-contract.yml)
SUB_ID=$(yq '.azure.subscription_id' platform-contract.yml)

gh secret set AZURE_CLIENT_ID --body "$CLIENT_ID"
gh secret set AZURE_TENANT_ID --body "$TENANT_ID"
gh secret set AZURE_SUBSCRIPTION_ID --body "$SUB_ID"
gh secret set HF_TOKEN --body "<read-from-user>"
gh secret set OPENAI_API_KEY --body "<read-from-user>"  # for RAGAS LLM-as-judge
```

### Step 2 · Create `production` environment

```bash
gh api --method PUT /repos/<user>/project-00-ground-zero/environments/production \
  -F 'deployment_branch_policy[protected_branches]=true' \
  -F 'deployment_branch_policy[custom_branch_policies]=false'
```

This gates `deploy-azure.yml` and `teardown-azure.yml` behind the `production` environment · optionally can require manual approval.

### Step 3 · Author `deploy.sh`

Start with skeleton · add targets one at a time · validate with `--what-if` mode before adding real deploys. Use `set -euo pipefail` at top.

### Step 4 · Author ledger-write.sh + schema

Author script + author `schemas/metadata.schema.json` + author `schemas/ledger-entry.schema.json`. Write a test entry manually:

```bash
bash scripts/ledger-write.sh deploy-local HEALTHY 0.00
cat as-built/ledger.jsonl | jq .
```

### Step 5 · Author 7 workflows

In order:
1. `ci.yml` (simplest · no auth needed)
2. `deploy-azure.yml` (OIDC-heavy · test with `--what-if` dispatch)
3. `teardown-azure.yml`
4. `sync-hf-space.yml`
5. `sync-hf-model.yml`
6. `eval-regression-nightly.yml` (schedule · test with manual dispatch)
7. `red-team-weekly.yml` (same)

For each workflow, after authoring:
```bash
gh workflow run <workflow-name>.yml
gh run watch
```

Verify step summaries render · verify ledger entries written · verify artifact uploads.

### Step 6 · Gate scripts

`scripts/gate-g1.sh` · `gate-g2.sh` · `gate-g3.sh` · `gate-g4.sh`. Each takes standardized inputs · exits 0 or non-zero · writes JSON output.

### Step 7 · PR comment bot

Extend `ci.yml` with the PR comment step. Test with a draft PR:

```bash
git checkout -b test-pr-bot
echo "# test" > test.md
git add test.md && git commit -m "test PR bot"
git push -u origin test-pr-bot
gh pr create --title "test PR bot" --body "test"
# Wait for CI · verify comment appears
```

### Step 8 · Badges in README

Author badge URLs · test that they render (they'll all show red initially until first successful run, which is expected).

### Step 9 · Runbook §§ 7–9

Author with actual command outputs captured from your test runs.

### Step 10 · Self-test

- [ ] All 7 workflows have narrative names with emoji + gate label
- [ ] All workflows write `$GITHUB_STEP_SUMMARY`
- [ ] `ci.yml` runs successfully on a test PR
- [ ] `deploy-azure.yml` `--what-if` mode runs cleanly (no actual deploy)
- [ ] `teardown-azure.yml` dispatches cleanly (no actual teardown — subscription not yet active)
- [ ] `sync-hf-space.yml` · `sync-hf-model.yml` · triggers configured but gated on Block E existence
- [ ] `eval-regression-nightly.yml` · `red-team-weekly.yml` · schedule valid
- [ ] `pcp-update.yml` stub committed for Brief D
- [ ] Ledger writer writes valid JSONL entries
- [ ] `metadata.json` validates against schema
- [ ] 8 README badges render (may show red/unknown initially)
- [ ] PR comment bot posts on test PR
- [ ] G1-G4 gate scripts written with exit-code contracts

---

## § 07 · Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| C-01 | 7 workflows with narrative names + emoji | File listing |
| C-02 | All workflows write `$GITHUB_STEP_SUMMARY` | File inspection |
| C-03 | `ci.yml` runs successfully on test PR | Workflow run URL |
| C-04 | `deploy-azure.yml` OIDC auth configured | Workflow YAML inspection |
| C-05 | `deploy-azure.yml` · `teardown-azure.yml` manual-dispatch only (no push trigger) | Workflow YAML |
| C-06 | Ledger writer produces valid JSONL with schema fields | `jq` validation |
| C-07 | `metadata.json` validator passes on current file | Validator run |
| C-08 | PR comment bot posts on test PR | Screenshot / comment URL |
| C-09 | 8 README badges render | Rendered README |
| C-10 | G1-G4 gate scripts written with 0/non-0 exit contracts | Shell script inspection |
| C-11 | GH Actions secrets set · no secrets in repo | `gh secret list` + repo scan |
| C-12 | Production environment configured | `gh api` output |
| C-13 | `deploy.sh --what-if` runs cleanly | Command output |
| C-14 | Runbook §§ 7–9 authored | File read |
| C-15 | No actual Azure resources deployed yet (Wave 4 gate) | `az resource list` |

---

## § 08 · Review Rubric (Architect's checks)

1. Trigger a draft PR · verify PR comment bot fires · verify `ci.yml` step summary
2. Manually dispatch `deploy-azure.yml` with `--what-if` flag · verify no actual deploy · verify step summary
3. Manually dispatch `red-team-weekly.yml` · verify workflow structure (will fail if no Hello AI deployed · expected)
4. Inspect `ledger-write.sh` with a test invocation · verify JSONL valid
5. Validate `metadata.json` via validator
6. Scan all workflows for hardcoded secrets (should find zero)
7. Check Actions tab Actions-tab-reads-like-story criterion · narrative names visible
8. Verify 3 demo-fails branches are flagged for Brief E (not created here · this is correct)

---

## § 09 · Risks & Your Mitigations

| Risk | Mitigation |
|---|---|
| OIDC federation misconfigured · deploy-azure.yml auth fails | Use `azure/login@v2` · test with `--what-if` before real deploy · fallback runbook for debug |
| Ledger write races in parallel workflows | JSONL append is atomic at the OS level for single-line writes · document line-length cap |
| Step summary too large (GitHub limit 1MB) | Use artifacts for large outputs · summary is narrative only |
| PR comment spam on repeated pushes | Use `actions/github-script` with issue-comment-upsert pattern (future · Wave 5 polish) |
| `red-team-weekly.yml` runs with no deployed endpoint during Ground Zero | Workflow tolerates missing endpoint in Wave 2 · real runs start Wave 4 |
| `eval-regression-nightly.yml` costs OpenAI API tokens (judge LLM) | Capped generations · budget alert at $5/month · can switch to Azure OpenAI judge when available |

---

## § 10 · Escalation Contract

Same format as Briefs A and B.

---

## § 11 · Expected Output Format

1. **Workflow files list** with one-line description each
2. **Test PR URL** showing `ci.yml` + PR bot in action
3. **Manual dispatch URLs** for `deploy-azure.yml --what-if` and `red-team-weekly.yml`
4. **Ledger entry example** (one HEALTHY · one REJECTED for gate-failure demo)
5. **Self-assessment** · 15 acceptance criteria with evidence
6. **Open escalations** (if any)

---

## § 12 · Closure

Brief C closes when Architect signs off. On closure:
- Brief D reads your ledger schema to render the As-Built zone
- Brief E's Hello AI must conform to `/health` endpoint contract for G3 smoke test
- Three `demo-fails-*` branches become Brief E's responsibility (can only exist once Hello AI does)
- Pipeline is deploy-ready · Azure activation in Wave 4 unblocks the actual deploys

---

**End of Builder Brief · C · Delivery Pipeline**

`Dammam · 2026-04-24 · Rev 1.0`
