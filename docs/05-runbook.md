# Runbook · Project Ground Zero

**Rev 1.1 · 2026-04-24 · Sections 1–3 authored by Brief A · Wave 1**

This runbook is the canonical source for standing up, operating, and tearing down Project Ground Zero. Sections 1–3 are authored by Brief A. Sections 4+ are filled by Briefs B, C, D, E.

Canonical state at start of § 2: both repos already exist on GitHub under `sowthri-industrial-ai` and have been seeded with Charter, Briefs, Coverage Matrix, TCO, and `architecture.html` via kickoff `setup.sh`.

---

## § 1 · Prerequisites

### 1.1 · Tooling

| Tool | Min | macOS | Linux |
|---|---|---|---|
| `uv` | 0.4 | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `git` | 2.40 | `brew install git` | apt/dnf |
| `pre-commit` | 4.0 | `brew install pre-commit` | `pip install pre-commit` |
| `gitleaks` | 8.21 | `brew install gitleaks` | GH releases |
| `azure-cli` | 2.60 | `brew install azure-cli` | apt/dnf |
| `gh` | 2.50 | `brew install gh` | apt/dnf |
| Bicep | 0.30 | `az bicep install` | `az bicep install` |
| Terraform | 1.9 | `brew install terraform` | HashiCorp repo |
| Python | 3.12 | `uv python install 3.12` | `uv python install 3.12` |

### 1.2 · Accounts

| Account | Role |
|---|---|
| GitHub | Write to `sowthri-industrial-ai/*` |
| Azure | Contributor (activated Wave 4) |
| Entra | Application Administrator (Wave 4) |

---

## § 2 · Repository governance (configure existing repos)

Assumes local clones at `~/dev/genai-portfolio/`.

### 2.1 · Install pre-commit hooks

```bash
cd ~/dev/genai-portfolio/project-00-ground-zero
uv sync
uv run pre-commit install
uv run pre-commit run --all-files

cd ../genai-portfolio-hub
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

### 2.2 · Gitleaks verification (acceptance A-03)

```bash
git switch -c test/gitleaks-block
AKID="AKIA$(LC_ALL=C tr -dc 'A-Z0-9' </dev/urandom | head -c 16)"
SECRET=$(LC_ALL=C tr -dc 'A-Za-z0-9/+' </dev/urandom | head -c 40)
echo "$AKID=$SECRET" > test-secret.env
git add test-secret.env
git commit -m "test gitleaks"  # expected: blocked
rm -f test-secret.env
git switch main
git branch -D test/gitleaks-block
```

### 2.3 · Branch protection on `main`

```bash
for REPO in sowthri-industrial-ai/genai-portfolio-hub \
            sowthri-industrial-ai/project-00-ground-zero; do
  gh api --method PUT /repos/$REPO/branches/main/protection \
    -F required_pull_request_reviews.required_approving_review_count=0 \
    -F enforce_admins=false \
    -F required_status_checks.strict=true \
    -F required_status_checks.contexts='[]' \
    -F restrictions=null \
    -F allow_force_pushes=false \
    -F allow_deletions=false \
    -F required_linear_history=true
done
```

### 2.4 · Secret scanning + push protection

Web UI per repo → Settings → Code security → enable: Secret scanning · Push protection · Dependabot.

### 2.5 · Actions permissions

Settings → Actions → General → Allow all actions · Read/write permissions · Allow PR creation.

---

## § 3 · Azure landing zone (Wave 4 execution · documented now)

### 3.1 · Subscription + RG

```bash
az login
az account set --subscription "<your-subscription-id>"
az group create --name rg-genai-portfolio-prod-swc --location swedencentral \
  --tags project=genai-portfolio project-phase=ground-zero environment=prod \
         cost-center=personal-portfolio owner=sowthri \
         poc-id=project-00-ground-zero managed-by=manual
```

### 3.2 · Entra app registration

```bash
APP_ID=$(az ad app create --display-name genai-portfolio-github-oidc --query appId -o tsv)
az ad sp create --id "$APP_ID"
SP_OBJECT_ID=$(az ad sp show --id "$APP_ID" --query id -o tsv)
SUB_ID=$(az account show --query id -o tsv)
az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role Contributor \
  --scope "/subscriptions/$SUB_ID/resourceGroups/rg-genai-portfolio-prod-swc"
```

### 3.3 · Federated credentials

```bash
for REPO in genai-portfolio-hub project-00-ground-zero; do
  az ad app federated-credential create --id "$APP_ID" --parameters "{
    \"name\": \"github-$REPO-main\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:sowthri-industrial-ai/$REPO:ref:refs/heads/main\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }"
done
```

### 3.4 · Populate platform-contract.yml

Replace 4 `<TBD-wave-4>` values in both repos with actual subscription_id, tenant_id, app_object_id, app_client_id. Commit to main.

### 3.5 · Wave-1 gate proof

```bash
az resource list --resource-group rg-genai-portfolio-prod-swc -o table
# Expected: empty or ResourceGroupNotFound
```

### 3.6 · Teardown (Wave 5+)

```bash
az group delete --name rg-genai-portfolio-prod-swc --yes
az ad app delete --id "$APP_ID"
```

---

> Sections 4+ authored by Briefs B (runtime) · C (pipeline) · D (PCP) · E (Hello AI).

---

## § 4 · Runtime Resource Overview

Each Bicep module in `infra/bicep/modules/` provisions one Azure resource class. All modules accept `name` + `tags` from Brief A and use Managed Identity for data-plane auth where Microsoft supports it.

| Module | Resource | Tier | Auth | Purpose |
|---|---|---|---|---|
| `aoai.bicep` | Azure OpenAI | S0 + 3 deployments | Entra (disableLocalAuth) | GPT-4o · GPT-4o-mini · text-embedding-3-small |
| `ai-search.bicep` | AI Search | Free | API key (Free tier constraint) | Hybrid retrieval · 1 index |
| `cosmos.bicep` | Cosmos DB | Serverless | Entra | Conversation memory · 1 database |
| `blob-storage.bicep` | Storage | Standard_LRS | Entra (no shared key) | Document + artifact storage |
| `content-safety.bicep` | Content Safety | F0 | Entra | Prompt Shields · groundedness |
| `app-insights.bicep` | App Insights + LA | PerGB2018 | N/A | Telemetry backbone |
| `container-apps-env.bicep` | Container Apps Env | Consumption | System MI | Runtime environment |
| `container-app.bicep` | Container App (generic) | Consumption | User MI | Reusable for any service |
| `container-registry.bicep` | ACR | Basic | Entra | Image hosting |
| `langfuse.bicep` | CA + Postgres Flex | B1ms | MI + password | Self-hosted tracing v3 |

### § 4.1 · TCO alignment

Brief B's modules own $8.58 of the $21.16 Ground Zero spend:
- AOAI deployments → $6.24 (see TCO sheet · row aoai tokens)
- Container Apps (Langfuse + Hello AI) → $2.34
- ACR Basic pro-rata → $1.32 (shared with Brief A)
- All other resources → free-tier or $0

### § 4.2 · AI Search Free-tier note

AI Search Free tier does NOT support API-key-less authentication. Module flips `authOptions.apiKeyOnly` to `aadOrApiKey` on any paid SKU. For Ground Zero we accept the Free-tier key-only auth trade-off and document the upgrade path here.

---

## § 5 · Docker Compose local dev

### § 5.1 · First start

```bash
cd ~/dev/genai-portfolio/project-00-ground-zero
docker compose up -d
docker compose ps
```

Expected · 4 services in `Up (healthy)` state within ~60s:
- postgres (Langfuse backend)
- pgvector (RAG store)
- langfuse (tracing UI on :3000)
- ollama (local LLM on :11434)

### § 5.2 · First-time Ollama model pull

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

~2GB download · completes in ~3 min on broadband. Skip if offline.

### § 5.3 · Hello AI payload (Brief E)

```bash
docker compose --profile payload up hello-ai
```

Profile-gated so payload doesn't start unless explicitly requested. Brief E owns the payload image contents.

### § 5.4 · Common commands

```bash
docker compose logs langfuse -f          # tail Langfuse logs
docker compose restart langfuse          # restart after config change
docker compose down                      # stop all (volumes preserved)
docker compose down -v                   # full teardown (volumes destroyed)
```

### § 5.5 · Troubleshooting

| Symptom | Fix |
|---|---|
| Langfuse won't start | Check postgres healthy first · `docker compose logs postgres` |
| Port 5432 conflict | Existing local postgres · stop it or change port mapping |
| Ollama pull fails | Check internet · retry · consider smaller model `llama3.2:1b` |
| `hello-ai` image build fails | Expected if `src/main.py` missing · Brief E fills |

---

## § 6 · Runtime contracts

`runtime-contract.yml` at repo root is the authoritative endpoint registry consumed by Brief E. All endpoints marked `<TBD-wave-4>` populate during Wave 4 post-deploy via Brief C's pipeline.

### § 6.1 · Auth modes

| Resource | Mode | Rationale |
|---|---|---|
| AOAI | Entra MI | `disableLocalAuth: true` · no API keys |
| Cosmos | Entra MI | `disableLocalAuth: true` |
| Blob | Entra MI | `allowSharedKeyAccess: false` |
| Content Safety | Entra MI | `disableLocalAuth: true` |
| AI Search | API key | Free-tier Microsoft constraint |
| App Insights | Connection string | Standard SDK pattern |
| Langfuse | HTTP + PK/SK | Open-source app-level |

### § 6.2 · Health check contract

Every service exposes:
- `GET /health` · 200 OK when downstream reachable
- `GET /ready` · 200 OK when warm (models loaded, caches primed)
- `GET /metrics` · Prometheus format (optional · Brief E implements)

Brief C's smoke tests assert against these paths.

### § 6.3 · Wave-1 vs Wave-4 state

| State | Wave 1 | Wave 4 |
|---|---|---|
| Bicep modules authored | ✅ | (same) |
| Modules deployed to Azure | ❌ | ✅ |
| `runtime-contract.yml` endpoints | `<TBD-wave-4>` | populated |
| Key Vault secrets | schema only | written post-deploy |
| Local Docker Compose | ✅ | ✅ (unchanged) |

---

## § 7 · Delivery Pipeline

Brief C authors 7 GitHub Actions workflows in `.github/workflows/` and shell scripts in `scripts/`. The pipeline enforces gates G1-G4 and produces a ledger that the PCP (Brief D) consumes.

### § 7.1 · Workflow inventory

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | push, PR | Ruff lint + pytest + Bicep build |
| `security-scan.yml` | PR, weekly | Gitleaks + dependency review |
| `deploy-azure.yml` | manual | OIDC-authed Azure deploy |
| `teardown-azure.yml` | manual | Delete RG (requires DELETE confirmation) |
| `eval-regression.yml` | PR on src/, manual | RAGAS + DeepEval scaffold |
| `red-team.yml` | weekly, manual | Garak + PyRIT scaffold |
| `pr-comment-bot.yml` | PR opened/sync | Upsert as-built summary comment |

### § 7.2 · Required GitHub Secrets (set before Wave 4)

```bash
gh secret set AZURE_CLIENT_ID       --body "<from platform-contract.yml>"
gh secret set AZURE_TENANT_ID       --body "<from platform-contract.yml>"
gh secret set AZURE_SUBSCRIPTION_ID --body "<from platform-contract.yml>"
```

### § 7.3 · Production environment

```bash
gh api -X PUT /repos/sowthri-industrial-ai/project-00-ground-zero/environments/production \
  -F wait_timer=0 \
  -F reviewers='[]' \
  -F deployment_branch_policy='{"protected_branches":true,"custom_branch_policies":false}'
```

---

## § 8 · Stage Gates · G1 through G4

Each gate is a standalone shell script with a defined exit contract. Workflows invoke gates sequentially and halt on any non-zero exit.

| Gate | Script | Purpose | Exit 0 conditions |
|---|---|---|---|
| G1 | `gate-g1.sh` | Build gate | uv sync succeeds OR no python code yet |
| G2 | `gate-g2.sh` | Safety wiring | content-safety.bicep present |
| G3 | `gate-g3.sh <url>` | Health probe | `/health` returns 200 OR no URL |
| G4 | `gate-g4.sh` | Eval regression | eval-results.xml within thresholds OR absent |

Each gate writes a JSON artifact to `as-built/g<N>-result.json`.

### § 8.1 · Deliberate failure branches (ADR-0011)

Three branches kept permanent to demonstrate gate behavior:
- `demo-fails-g1` — broken pyproject.toml
- `demo-fails-guardrail` — removed content-safety.bicep
- `demo-regresses-eval` — tanked eval thresholds

---

## § 9 · Ledger · as-built trail

`as-built/ledger.jsonl` · JSONL format · one entry per deploy/teardown event. Written by `scripts/ledger-write.sh` from workflow runs.

Schema: `schemas/ledger.schema.json`.

### § 9.1 · Example entries

```jsonl
{"timestamp": "2026-04-24T09:30:00Z", "action": "deploy-azure", "status": "success", "actor": "sowthri-industrial-ai", "sha": "a1b2c3d"}
{"timestamp": "2026-04-24T10:45:00Z", "action": "teardown-azure", "status": "success", "actor": "sowthri-industrial-ai", "sha": "a1b2c3d"}
```

### § 9.2 · PCP consumption

Brief D's Portfolio Control Plane fetches `ledger.jsonl` at build time and renders the timeline with newest-first ordering. REJECTED/failure entries stay visible (honesty principle).
