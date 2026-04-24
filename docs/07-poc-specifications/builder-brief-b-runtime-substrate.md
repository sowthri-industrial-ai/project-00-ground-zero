# Builder Brief · B · Runtime Substrate

```
Brief ID     · BRIEF-B
Block        · B · Runtime Substrate
Project      · project-00-ground-zero
Wave         · 1 (parallel with Brief A)
Dependencies · Brief A must be in progress · reads A's contracts when available
Deliver to   · Architect chat for review
```

---

## § 01 · Context · You are here

You are Builder-B. This Brief is self-contained. Architectural choices are already made in the Charter (`docs/00-charter.md`) and ADRs (`docs/03-ADR/`). Seek clarification only on genuine ambiguity in acceptance criteria.

You are the Runtime Substrate block. Your job: author the Bicep + Terraform modules for every Azure runtime resource the portfolio will use, author the Docker Compose stack for local development, and author the Hello AI container scaffolding that Block E will later fill.

**You do NOT deploy to Azure.** Deploy happens in Wave 4 via Brief C's pipeline. You author and validate.

**You run in parallel with Brief A.** A creates the RG and OIDC federation; you author the resources that will land in that RG. Your Bicep modules reference A's outputs via parameter injection, not hardcoded values.

---

## § 02 · Goals

1. Author Bicep modules for runtime resources (9 resource types)
2. Mirror critical modules in Terraform (3 resource types)
3. Author `docker-compose.yml` for local dev stack (Langfuse + Ollama + pgvector + Postgres)
4. Scaffold `Dockerfile` for Hello AI (stub — Block E fills business logic)
5. Author `runtime-contract.yml` — the interface your resources expose to Block E
6. Author AOAI model-deployment manifest (GPT-4o · GPT-4o-mini · text-embedding-3-small)
7. Environment variable schema for local vs Azure runtime parity
8. Health-check contract specifications (every resource exposes a probe)
9. Document in `docs/05-runbook.md` §§ 4–6

---

## § 03 · Non-Goals

- ❌ Do NOT deploy resources to Azure (Wave 4 gate)
- ❌ Do NOT author GitHub Actions workflows (Block C)
- ❌ Do NOT build Hello AI application logic (Block E)
- ❌ Do NOT build PCP (Block D)
- ❌ Do NOT implement retrieval, agents, or generation (Block E)
- ❌ Do NOT configure domain-specific model fine-tunes (Block E scaffold only)

---

## § 04 · Deliverables (exhaustive)

### Deliverable 1 · Bicep runtime modules

Author in `infra/bicep/modules/`:

| Module | Resource | Key parameters |
|---|---|---|
| `aoai.bicep` | Azure OpenAI resource + 3 model deployments | region · deployment type · model capacities |
| `ai-search.bicep` | AI Search service (Free tier) | region · sku=`free` |
| `cosmos.bicep` | Cosmos DB (serverless · 1000 RU/s free) | region · database name |
| `blob-storage.bicep` | Azure Storage (Blob · free tier) | region · sku · containers |
| `container-apps-env.bicep` | Container Apps Environment | region · log analytics link |
| `container-app.bicep` | Generic Container App (reusable) | image · env vars · ingress · MI |
| `container-registry.bicep` | ACR Basic | region · sku=`basic` |
| `content-safety.bicep` | Content Safety F0 | region · sku=`F0` |
| `app-insights.bicep` | Application Insights + Log Analytics Workspace | region · retention-days |
| `langfuse.bicep` | Langfuse self-host on Container App | composite module (pulls container-app + postgres) |

**Shared requirements on every module**:
- Accept `tags` parameter of type `object` (from Brief A's `tags.bicep`)
- Accept `name` parameter derived from Brief A's `naming.bicep`
- Output resource ID, name, and any secrets written to Key Vault
- Use Managed Identity (passed in as parameter) for Azure OpenAI · Cosmos · Storage access
- Public endpoints OK (portfolio scope) but document where private endpoints would slot in

### Deliverable 2 · AOAI model deployments

In `aoai.bicep`, declare three deployments:

```bicep
resource aoai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: name  // required for Entra auth
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true  // force Entra-only auth (architect signal)
  }
}

resource gpt4oMini 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'gpt-4o-mini'
  sku: { name: 'GlobalStandard', capacity: 50 }  // low TPM for GZ · scale later
  properties: {
    model: { format: 'OpenAI', name: 'gpt-4o-mini', version: '2024-07-18' }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

resource gpt4o 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'gpt-4o'
  sku: { name: 'GlobalStandard', capacity: 10 }  // minimal for reasoning demos
  properties: {
    model: { format: 'OpenAI', name: 'gpt-4o', version: '2024-11-20' }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
  dependsOn: [ gpt4oMini ]  // deployments can't create in parallel
}

resource embed 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'text-embedding-3-small'
  sku: { name: 'Standard', capacity: 50 }
  properties: {
    model: { format: 'OpenAI', name: 'text-embedding-3-small', version: '1' }
  }
  dependsOn: [ gpt4o ]
}
```

Three notes:
- `disableLocalAuth: true` — forces Entra ID auth, no API keys. Architect signal.
- `versionUpgradeOption: OnceNewDefaultVersionAvailable` — auto-upgrade to stable releases when Microsoft changes default. Minimizes staleness.
- Sequential `dependsOn` on deployments is Azure's constraint, not a choice — model deployments can't parallel-create on the same account.

### Deliverable 3 · Terraform mirrors

Mirror three modules in `infra/terraform/`:
- `aoai.tf` — matches `aoai.bicep`
- `ai-search.tf`
- `container-apps-env.tf`

Not a full port · demonstrate parity on the non-trivial resources.

### Deliverable 4 · Docker Compose local stack

`docker-compose.yml` at repo root of `project-00-ground-zero`:

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse
      POSTGRES_DB: langfuse
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U langfuse"]
      interval: 10s
    ports: ["5432:5432"]

  pgvector:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: rag
      POSTGRES_PASSWORD: rag
      POSTGRES_DB: rag
    volumes:
      - pgvector_data:/var/lib/postgresql/data
    ports: ["5433:5432"]  # avoid collision with langfuse postgres

  langfuse:
    image: langfuse/langfuse:3
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://langfuse:langfuse@postgres:5432/langfuse
      NEXTAUTH_SECRET: local-dev-only-not-for-prod
      SALT: local-dev-only-not-for-prod
      NEXTAUTH_URL: http://localhost:3000
    ports: ["3000:3000"]

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports: ["11434:11434"]
    # Pull a small model on first run:
    # docker exec -it <container> ollama pull llama3.2:3b

  hello-ai:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - langfuse
      - pgvector
      - ollama
    environment:
      MODE: local
      LANGFUSE_HOST: http://langfuse:3000
      OLLAMA_HOST: http://ollama:11434
      PGVECTOR_DSN: postgresql://rag:rag@pgvector:5432/rag
    ports: ["8080:8080"]

volumes:
  postgres_data:
  pgvector_data:
  ollama_data:
```

**Design rationale**:
- Ports chosen to avoid collisions (Postgres 5432 vs pgvector on 5433)
- Healthchecks on Postgres ensure Langfuse doesn't race — Block E will add healthchecks for hello-ai
- Ollama as local LLM substitute for Azure OpenAI in local mode · NFR-03 satisfaction
- `MODE: local` env switches Hello AI runtime between local (Ollama) and Azure (AOAI)
- Everything on default bridge network · `service_name` resolves via DNS

### Deliverable 5 · Hello AI Dockerfile stub

`Dockerfile` at repo root of `project-00-ground-zero`:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install uv (dependency manager per ADR-0009)
RUN pip install uv==0.4.*

# Copy manifests first for layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source (Block E fills /app/src)
COPY src/ ./src/

# Health check (Block E implements actual endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=3)" || exit 1

EXPOSE 8080
CMD ["uv", "run", "python", "-m", "src.main"]
```

### Deliverable 6 · `runtime-contract.yml`

Companion to Brief A's `platform-contract.yml`. Written by you, read by Block E.

```yaml
# runtime-contract.yml — produced by Brief B, consumed by Brief E
# Rev 1.0 · 2026-04-24

aoai:
  endpoint: "https://aoai-genai-portfolio-01.openai.azure.com"
  auth_mode: "entra_managed_identity"  # no API keys
  deployments:
    chat_small: "gpt-4o-mini"
    chat_large: "gpt-4o"
    embedding:  "text-embedding-3-small"
  api_version: "2024-10-21"

ai_search:
  endpoint: "https://srch-genai-portfolio-01.search.windows.net"
  auth_mode: "entra_managed_identity"
  index_name: "hello-ai-rag"
  tier: "free"
  semantic_enabled: false  # not available on free tier

cosmos:
  endpoint: "https://cosmos-genai-portfolio-01.documents.azure.com"
  auth_mode: "entra_managed_identity"
  database: "hello-ai"
  containers:
    - name: "conversations"
      partition_key: "/session_id"

blob_storage:
  endpoint: "https://stgenaiportfolio01.blob.core.windows.net"
  auth_mode: "entra_managed_identity"
  containers:
    - name: "documents"
    - name: "artifacts"

container_apps:
  environment_name: "cae-genai-portfolio-01"
  managed_identity_client_id: "<from-platform-contract>"

content_safety:
  endpoint: "https://cs-genai-portfolio-01.cognitiveservices.azure.com"
  auth_mode: "entra_managed_identity"
  tier: "F0"
  prompt_shield_enabled: true
  groundedness_check_enabled: true

observability:
  langfuse:
    azure_url: "https://langfuse-genai-portfolio-01.<env>.azurecontainerapps.io"
    local_url: "http://localhost:3000"
  app_insights:
    instrumentation_key_secret_uri: "<keyvault-secret-uri>"

local_runtime:
  compose_file: "docker-compose.yml"
  services_url:
    langfuse: "http://localhost:3000"
    ollama:   "http://localhost:11434"
    pgvector: "postgresql://rag:rag@localhost:5433/rag"

contract:
  version: "1.0"
  produced_by: "brief-b"
  consumed_by: ["brief-e"]
```

### Deliverable 7 · Environment variable schema

`.env.example` at repo root:

```bash
# Mode switch — local | azure
MODE=local

# === LOCAL MODE (Docker Compose) ===
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=pk-lf-local-dev
LANGFUSE_SECRET_KEY=sk-lf-local-dev

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

PGVECTOR_DSN=postgresql://rag:rag@localhost:5433/rag

# === AZURE MODE (populated by deploy.sh from Key Vault) ===
# These are pulled at container start · not stored in repo
# AOAI_ENDPOINT=<from-keyvault>
# AOAI_DEPLOYMENT_CHAT_SMALL=gpt-4o-mini
# AOAI_DEPLOYMENT_CHAT_LARGE=gpt-4o
# AOAI_DEPLOYMENT_EMBEDDING=text-embedding-3-small
# AZURE_SEARCH_ENDPOINT=<from-keyvault>
# AZURE_SEARCH_INDEX=hello-ai-rag
# COSMOS_ENDPOINT=<from-keyvault>
# BLOB_ENDPOINT=<from-keyvault>
# CONTENT_SAFETY_ENDPOINT=<from-keyvault>
# APPLICATIONINSIGHTS_CONNECTION_STRING=<from-keyvault>
```

**Never commit `.env`**. Pre-commit (from Brief A) blocks it.

### Deliverable 8 · Health-check contract

Every runtime service in the Hello AI payload exposes:
- `GET /health` → 200 OK with `{"status": "healthy", "dependencies": {...}}` when all downstream reachable
- `GET /ready` → 200 OK only when model is warm and caches populated
- `GET /metrics` → Prometheus-format metrics (optional · Block E fills)

Document this in `docs/05-runbook.md` § 6 as the contract Block C's smoke tests will assert against.

### Deliverable 9 · Runbook §§ 4–6

- § 4 · Runtime resource overview (what each module provisions and why)
- § 5 · Docker Compose local dev (setup, common commands, troubleshooting)
- § 6 · Runtime contracts (auth modes · endpoints · health checks)

---

## § 05 · Interface Contracts

### Contract IN · From Brief A

Read these fields from `platform-contract.yml`:
- `azure.subscription_id` · `azure.tenant_id` · `azure.resource_group` · `azure.region`
- `azure.key_vault_name` · `azure.managed_identity_name`
- `naming.prefix_pattern`

Your Bicep modules accept these as parameters — never hardcode.

### Contract OUT · To Brief E (primarily) · Brief C (deployment orchestration)

- `runtime-contract.yml` at repo root — the authoritative endpoint + auth registry
- `infra/bicep/modules/` — Brief C imports these in `deploy-azure.yml`
- `docker-compose.yml` — Brief E's Hello AI joins this stack for local dev
- `Dockerfile` — Brief E fills `src/`
- `.env.example` — Block E adds service-specific vars; schema is yours

---

## § 06 · Step-by-Step Implementation Guidance

### Step 1 · Read Brief A's output

Verify `platform-contract.yml` exists in `project-00-ground-zero/` root. Note field names — your parameters will reference these.

### Step 2 · Author `aoai.bicep`

Start with the AOAI module · it's the most complex. Use code from § 04 Deliverable 2 as starting point. Validate:

```bash
az bicep build --file infra/bicep/modules/aoai.bicep
```

### Step 3 · Author remaining Bicep modules

In order of increasing complexity:
1. `content-safety.bicep` · simplest (single resource)
2. `blob-storage.bicep`
3. `cosmos.bicep`
4. `ai-search.bicep`
5. `container-registry.bicep`
6. `app-insights.bicep`
7. `container-apps-env.bicep` · depends on app-insights
8. `container-app.bicep` · generic reusable module
9. `langfuse.bicep` · composite · depends on container-app + a Postgres option

Build each with `az bicep build`. All must lint clean.

### Step 4 · Terraform mirrors

Three modules in `infra/terraform/`:
1. `aoai.tf`
2. `ai-search.tf`
3. `container-apps-env.tf`

Validate:

```bash
cd infra/terraform
terraform fmt && terraform init && terraform validate
```

### Step 5 · Docker Compose stack

Author `docker-compose.yml` per § 04 Deliverable 4. Test locally:

```bash
docker compose up -d
docker compose ps          # all services running
curl http://localhost:3000 # Langfuse UI
curl http://localhost:11434/api/tags  # Ollama API
docker compose down
```

### Step 6 · Dockerfile stub

Author `Dockerfile` per § 04 Deliverable 5. Build:

```bash
docker build -t hello-ai:stub .
# Container will fail to start because src/main.py doesn't exist yet — expected
# Verify image builds to the CMD step
```

### Step 7 · `runtime-contract.yml`

Author per § 04 Deliverable 6. Reference Brief A's `platform-contract.yml` for field naming consistency.

### Step 8 · `.env.example`

Author per § 04 Deliverable 7. Do NOT create `.env` (pre-commit blocks it).

### Step 9 · Runbook §§ 4–6

Author in `docs/05-runbook.md`. Include:
- Actual commands the architect will run
- Expected output for verification
- Common failure modes and fixes

### Step 10 · Self-test

- [ ] All 10 Bicep modules lint clean (`az bicep build`)
- [ ] All 3 Terraform mirrors validate clean
- [ ] `docker compose up` starts all 4 local services (Langfuse · Postgres · pgvector · Ollama)
- [ ] Langfuse UI loads at `http://localhost:3000`
- [ ] Dockerfile builds successfully
- [ ] `runtime-contract.yml` has all fields populated (endpoints as TBD-until-deployment)
- [ ] `.env.example` committed · `.env` absent (pre-commit would block)
- [ ] No Azure resources exist yet (`az resource list` empty or not-yet-authenticated)
- [ ] Runbook §§ 4–6 self-sufficient cold-read

---

## § 07 · Acceptance Criteria

Each binary pass/fail.

| # | Criterion | Evidence |
|---|---|---|
| B-01 | 10 Bicep modules lint clean | `az bicep build` output per module |
| B-02 | 3 Terraform modules validate clean | `terraform validate` output |
| B-03 | `disableLocalAuth: true` set on AOAI | File inspection |
| B-04 | All 3 AOAI deployments declared (4o-mini · 4o · embedding) | `aoai.bicep` inspection |
| B-05 | Managed Identity auth used for Cosmos · Blob · AI Search access | Module parameters |
| B-06 | `docker compose up` starts all 4 services healthy | `docker compose ps` output |
| B-07 | Langfuse UI loads at `localhost:3000` | Browser / curl verification |
| B-08 | Ollama responds on `localhost:11434` | `curl http://localhost:11434/api/tags` |
| B-09 | Dockerfile builds to CMD step cleanly | `docker build` output |
| B-10 | `runtime-contract.yml` committed with all fields | File read |
| B-11 | `.env.example` committed · `.env` absent | Repo listing |
| B-12 | Runbook §§ 4–6 authored | File read |
| B-13 | No Azure resources deployed (Wave 4 gate respected) | `az resource list` |

---

## § 08 · Review Rubric (Architect's checks)

1. Clone fresh · `docker compose up` · verify all services healthy in < 2 min
2. Inspect `aoai.bicep` — Entra-only auth? Three deployments? Version pinning sensible?
3. Inspect `container-apps-env.bicep` — linked to Log Analytics? Managed environment spec?
4. Inspect `runtime-contract.yml` — all fields present? auth modes explicit?
5. Read runbook §§ 4–6 cold — follow mentally, note gaps
6. Verify Docker Compose services can be brought down cleanly (`docker compose down -v`)
7. Terraform mirrors — functional parity demonstrable (not necessarily identical)
8. Attempt to deploy one Bicep module to Azure as a dry-run check (`--what-if`) if subscription available

---

## § 09 · Risks & Your Mitigations

| Risk | Mitigation |
|---|---|
| AOAI model version drift (version pinned becomes deprecated) | `versionUpgradeOption: OnceNewDefaultVersionAvailable` · auto-moves to stable |
| Langfuse v3 breaking config changes | Pin `langfuse/langfuse:3` tag · upgrade intentional |
| Port collision on local (Postgres, pgvector both default 5432) | Explicit port mapping · 5432 Langfuse · 5433 pgvector |
| Ollama model download too large for initial run | Recommend `llama3.2:3b` (~2GB) in runbook · not 70B variants |
| `disableLocalAuth` breaks legacy SDKs expecting API keys | Architect signal · Block E uses `AzureDefaultCredential` for MI |
| AI Search Free tier limits (3 indexes · 50MB) | Ground Zero needs 1 index · fits easily · documented in runbook § 4 |

---

## § 10 · Escalation Contract

Same format as Brief A:

```markdown
# Brief B · Escalations

## Q1 · <summary>
- Context:
- My options:
- My recommendation:
- Blocks: <yes/no>
```

Return to Architect chat for resolution.

---

## § 11 · Expected Output Format

When you return:

1. **File listing** of all Bicep + Terraform + Compose + Dockerfile + contracts
2. **`az bicep build` output** for each module (paste)
3. **`docker compose ps` output** showing all services healthy
4. **Self-assessment** · 13 acceptance criteria with evidence
5. **Open escalations** (if any)

---

## § 12 · Closure

Brief B closes when Architect signs off. On closure:
- Brief C reads your `infra/bicep/modules/` to build `deploy-azure.yml`
- Brief E reads your `runtime-contract.yml` as the endpoint registry
- `docker-compose.yml` becomes the local dev stack for all subsequent projects

---

**End of Builder Brief · B · Runtime Substrate**

`Dammam · 2026-04-24 · Rev 1.0`
