# Builder Brief · A · Platform & Identity

```
Brief ID    · BRIEF-A
Block       · A · Platform & Identity
Project     · project-00-ground-zero
Wave        · 1 (parallel with Brief B)
Dependencies · None — foundation block
Deliver to  · Architect chat for review
```

---

## § 01 · Context · You are here

You are a **Builder** working in a separate Claude Code session. This Brief is self-contained. Do not seek architectural guidance on decisions already made — those are recorded in the Charter (`docs/00-charter.md`) and ADRs (`docs/03-ADR/0001..0010.md`). Seek clarification only on genuine ambiguity in acceptance criteria.

This Brief is part of **Project Ground Zero** — the architectural substrate for a GenAI Architect Portfolio. Your block (A · Platform & Identity) establishes the foundation every subsequent block depends on:

- Block B · Runtime Substrate (parallel to yours, depends on your RG + Entra outputs)
- Block C · Delivery Pipeline (depends on your OIDC federation)
- Block D · Portfolio Control Plane (depends on your repo scaffold)
- Block E · Hello AI Payload (depends on B + C)

**You are NOT building a use case.** You are building the foundation every use-case project will inherit. Optimize for reusability, clarity, and zero long-lived secrets. Do NOT optimize for scale, performance, or feature richness.

---

## § 02 · Goals

1. Create two GitHub repositories (public) with standardized scaffold
2. Prepare Azure subscription landing zone configuration (not yet deployed — Wave 4 activates Azure credit)
3. Configure Microsoft Entra ID app registration and OIDC workload identity federation
4. Author reusable Bicep modules (naming · tags · Key Vault · Managed Identity)
5. Mirror critical modules in Terraform (portability proof, not production-equivalent)
6. Configure pre-commit hooks, branch protection, and secret scanning
7. Author the `platform-contract.yml` that downstream Briefs will consume
8. Document everything in `docs/05-runbook.md` §§ 1–3

---

## § 03 · Non-Goals

- ❌ Do NOT deploy any Azure resources yet (Wave 4 gate)
- ❌ Do NOT deploy Azure OpenAI · Container Apps · storage (Block B)
- ❌ Do NOT configure GitHub Actions secrets or workflows (Block C)
- ❌ Do NOT build any PCP pages (Block D)
- ❌ Do NOT build any Hello AI code (Block E)
- ❌ Do NOT implement full test tiers beyond pre-commit checks (Block C + E distribute)
- ❌ Do NOT pick specific model deployments (Block B)

---

## § 04 · Deliverables (exhaustive)

### Deliverable 1 · GitHub repositories

**Repo 1 · `genai-portfolio-hub`** · public

```
genai-portfolio-hub/
├── README.md
├── LICENSE                          (MIT or Apache-2.0)
├── .gitignore                       (Python + Node + IDE standard)
├── .pre-commit-config.yaml
├── pyproject.toml                   (uv-managed)
├── uv.lock
├── .python-version                  (3.12)
├── platform-contract.yml            (template — values TBD for Wave 4)
├── .github/
│   ├── workflows/                   (empty · README placeholder)
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── charters/                        (empty placeholder)
├── docs/                            (empty placeholder)
├── control-plane/                   (empty · Brief D fills)
├── shared/                          (empty placeholder)
├── scripts/
│   └── bootstrap.sh                 (stub)
└── infra/
    ├── bicep/modules/               (populated — see below)
    └── terraform/                   (populated — see below)
```

**Repo 2 · `project-00-ground-zero`** · public

```
project-00-ground-zero/
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
├── .python-version
├── metadata.json                    (populated — see § 06)
├── platform-contract.yml            (template — values TBD for Wave 4)
├── Dockerfile                       (stub — Block E fills)
├── docker-compose.yml               (stub — Block E fills)
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── docs/
│   ├── 00-charter.md                (COMMIT THE CHARTER as first artifact)
│   ├── 01-HLD.md                    (placeholder · Block B/C/D/E add sections)
│   ├── 02-LLD.md                    (placeholder)
│   ├── 03-ADR/
│   │   ├── 0001-azure-region.md
│   │   ├── 0002-oidc-federation.md
│   │   ├── ...
│   │   └── 0010-astro-pcp.md
│   ├── 04-threat-model.md           (placeholder)
│   ├── 05-runbook.md                (§§ 1–3 populated by you)
│   ├── 06-tco.md                    (placeholder)
│   └── 07-poc-specifications/
│       └── brief-a-platform-identity.md  (THIS DOCUMENT — commit it)
├── html/                            (empty · Wave 5 fills)
├── src/                             (empty · Block E fills)
├── infra/
│   ├── bicep/                       (populated per this Brief)
│   └── terraform/                   (populated per this Brief)
├── spaces/ · models/ · datasets/    (empty · Block E fills)
├── as-built/
│   ├── ledger.jsonl                 (empty file created)
│   └── README.md                    (stub — Block C fills)
└── scripts/
    ├── deploy.sh                    (stub — Block C fills)
    ├── bootstrap.sh                 (stub)
    └── sync-hf.sh                   (stub)
```

### Deliverable 2 · Bicep modules

**`infra/bicep/modules/naming.bicep`** — parameter-based naming module enforcing `§ 17` convention:

```bicep
@description('Program slug')
param program string = 'genai-portfolio'

@description('Resource type short code (aoai, srch, cosmos, kv, mi, etc.)')
param resourceType string

@description('Sequence number')
param seq string = '01'

@description('Optional suffix for globally-unique resources (Key Vault, Storage)')
param uniqueSuffix string = ''

output resourceName string = empty(uniqueSuffix) 
  ? '${resourceType}-${program}-${seq}'
  : '${resourceType}-${program}-${seq}-${uniqueSuffix}'
```

**`infra/bicep/modules/tags.bicep`** — tag taxonomy:

```bicep
param program string = 'genai-portfolio'
param projectPhase string = 'ground-zero'
param environment string = 'prod'
param costCenter string = 'personal-portfolio'
param owner string
param pocId string
param managedBy string = 'bicep'

output tags object = {
  project: program
  'project-phase': projectPhase
  environment: environment
  'cost-center': costCenter
  owner: owner
  'poc-id': pocId
  'managed-by': managedBy
}
```

**`infra/bicep/modules/keyvault.bicep`** — Key Vault deployment:

```bicep
param location string = 'swedencentral'
param name string
param tags object
param tenantId string = subscription().tenantId
param enableRbac bool = true

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: enableRbac
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false  // ground zero only — allow teardown
    publicNetworkAccess: 'Enabled'  // portfolio demo
  }
}

output keyVaultId string = kv.id
output keyVaultName string = kv.name
output keyVaultUri string = kv.properties.vaultUri
```

**`infra/bicep/modules/managed-identity.bicep`** — user-assigned MI:

```bicep
param location string = 'swedencentral'
param name string
param tags object

resource mi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: tags
}

output identityId string = mi.id
output identityName string = mi.name
output principalId string = mi.properties.principalId
output clientId string = mi.properties.clientId
```

### Deliverable 3 · Terraform mirrors

`infra/terraform/keyvault.tf` and `infra/terraform/managed-identity.tf` — functional parity with the Bicep modules above, using `azurerm` provider. Not a full port — demonstrate that IaC choice is not lock-in.

### Deliverable 4 · Entra app registration & federation

Create (via `az ad app create` documented in runbook, OR via Terraform `azuread` provider — your call, document chosen path):

- **App name**: `genai-portfolio-github-oidc`
- **Federation credentials** (two, one per repo · branch):
  - Subject: `repo:<user>/genai-portfolio-hub:ref:refs/heads/main`
  - Subject: `repo:<user>/project-00-ground-zero:ref:refs/heads/main`
  - Issuer: `https://token.actions.githubusercontent.com`
  - Audience: `api://AzureADTokenExchange`
- **Role assignment**: Contributor on resource group (scoped — NOT subscription)

**Gate**: role assignment is prepared in Bicep/Terraform but NOT executed this Wave — Wave 4 activates Azure.

### Deliverable 5 · Pre-commit configuration

`.pre-commit-config.yaml` · both repos:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
      - id: detect-private-key
      - id: no-commit-to-branch
        args: [--branch, main]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.0
    hooks:
      - id: gitleaks
```

### Deliverable 6 · Repo settings

Via `gh` CLI or GitHub web UI (document in runbook):

- Branch protection on `main`:
  - Require PR before merge
  - Require status checks to pass (CI — activated by Brief C)
  - Require linear history
  - Do not allow bypass
- GitHub Actions: **Enabled** · `Read and write permissions` for `GITHUB_TOKEN`
- Secret scanning: **Enabled** · Push protection: **Enabled**

### Deliverable 7 · `metadata.json` for `project-00-ground-zero`

```json
{
  "project_id": "project-00-ground-zero",
  "name": "Ground Zero",
  "status": "in-progress",
  "phase": "ground-zero",
  "order": 0,
  "description": "Architectural substrate for the GenAI Architect Portfolio.",
  "urls": {
    "github": "https://github.com/<user>/project-00-ground-zero",
    "hf_space": null,
    "hf_model": null,
    "live_demo": null,
    "docs": "/projects/ground-zero"
  },
  "health": {
    "live_demo_status": "not-deployed",
    "last_checked": null,
    "uptime_30d": null
  },
  "sync": {
    "local_sha": null,
    "github_sha": null,
    "hf_sha": null,
    "drift": false
  },
  "cost": {
    "spent_usd": 0.00,
    "budget_usd": 25.00,
    "last_updated": null
  },
  "eval": {},
  "stack": ["azure", "bicep", "terraform", "github-actions", "entra-id", "oidc"]
}
```

### Deliverable 8 · `platform-contract.yml`

Template at repo root of both repos (values populated in Wave 4):

```yaml
# platform-contract.yml — produced by Brief A, consumed by Briefs B, C, D, E
# Rev 1.0 · 2026-04-24

azure:
  subscription_id: "<TBD-wave-4>"
  tenant_id: "<TBD-wave-4>"
  resource_group: rg-genai-portfolio-prod-swc
  region: swedencentral
  key_vault_name: kv-genai-portfolio-01
  managed_identity_name: mi-genai-portfolio-01

entra:
  app_display_name: genai-portfolio-github-oidc
  app_object_id: "<TBD-wave-4>"
  app_client_id: "<TBD-wave-4>"
  federation_subjects:
    - "repo:<user>/genai-portfolio-hub:ref:refs/heads/main"
    - "repo:<user>/project-00-ground-zero:ref:refs/heads/main"

naming:
  prefix_pattern: "<type>-genai-portfolio-<seq>"
  tag_keys: [project, project-phase, environment, cost-center, owner, poc-id, managed-by]

github:
  hub_repo: "https://github.com/<user>/genai-portfolio-hub"
  project_repo: "https://github.com/<user>/project-00-ground-zero"

contract:
  version: "1.0"
  produced_by: "brief-a"
  consumed_by: [brief-b, brief-c, brief-d, brief-e]
```

### Deliverable 9 · Runbook §§ 1–3

`docs/05-runbook.md` sections covering:
- § 1 · Prerequisites (tools, account access)
- § 2 · GitHub repo creation (step-by-step)
- § 3 · Azure prep (Entra, federation setup) — commands shown but **not executed** this Wave

---

## § 05 · Interface Contracts

### Contract OUT · What you hand to Briefs B, C, D, E

- `platform-contract.yml` at both repo roots · fields per § 04 Deliverable 8
- `infra/bicep/modules/*.bicep` · ready to be imported by Block B's deployment templates
- `infra/terraform/*.tf` · same
- `docs/05-runbook.md` §§ 1–3 · self-sufficient for reproducibility

### Contract IN · What you consume

- **Charter** (`docs/00-charter.md`) — committed with this Brief
- **ADRs** (`docs/03-ADR/0001..0010.md`) — committed with this Brief
- **Nothing else** — you are foundation

---

## § 06 · Step-by-Step Implementation Guidance

### Step 1 · Local environment

```bash
# macOS
brew install uv git pre-commit gitleaks azure-cli gh
# Linux — use your distro's package manager equivalent
# Windows — WSL2 recommended

# Verify
uv --version        # ≥ 0.4.0
az --version        # ≥ 2.60.0
gh --version        # ≥ 2.50.0
pre-commit --version
```

### Step 2 · Authenticate to GitHub

```bash
gh auth login
# Follow prompts · use HTTPS · login with browser
```

### Step 3 · Create hub repo

```bash
gh repo create <user>/genai-portfolio-hub \
  --public \
  --description "GenAI Architect Portfolio — hub + Portfolio Control Plane" \
  --clone
cd genai-portfolio-hub
```

### Step 4 · Scaffold hub

Create folder structure per § 04 Deliverable 1. Add placeholder `README.md` in each empty dir explaining what it will contain. Initial commit.

### Step 5 · Configure hub Python environment

```bash
uv init --python 3.12
# Add dev dependencies
uv add --dev pytest ruff pre-commit
uv lock
```

### Step 6 · Install pre-commit hooks

Write `.pre-commit-config.yaml` per § 04 Deliverable 5.

```bash
pre-commit install
pre-commit run --all-files     # should pass
```

### Step 7 · Create project-00 repo

```bash
cd ..
gh repo create <user>/project-00-ground-zero \
  --public \
  --description "Project Ground Zero · GenAI Architect Portfolio substrate" \
  --clone
cd project-00-ground-zero
```

### Step 8 · Scaffold project-00

Same pattern. Commit the Charter to `docs/00-charter.md` FIRST, then this Brief to `docs/07-poc-specifications/brief-a-platform-identity.md`.

### Step 9 · Author Bicep modules

Create `infra/bicep/modules/` and author four files per § 04 Deliverable 2. Validate with:

```bash
az bicep build --file infra/bicep/modules/naming.bicep
az bicep build --file infra/bicep/modules/tags.bicep
az bicep build --file infra/bicep/modules/keyvault.bicep
az bicep build --file infra/bicep/modules/managed-identity.bicep
```

All four must build clean.

### Step 10 · Author Terraform mirrors

`infra/terraform/keyvault.tf` and `infra/terraform/managed-identity.tf`. Validate:

```bash
cd infra/terraform
terraform fmt
terraform init
terraform validate
```

### Step 11 · Prepare Entra app registration (document only)

Document the exact `az ad app create` sequence in `docs/05-runbook.md` § 3. Do NOT execute — Wave 4 activates Azure.

### Step 12 · Configure branch protection

Via `gh` CLI on both repos:

```bash
gh api --method PUT \
  /repos/<user>/<repo>/branches/main/protection \
  -F required_pull_request_reviews.required_approving_review_count=0 \
  -F enforce_admins=false \
  -F required_status_checks.strict=true \
  -F required_status_checks.contexts='[]' \
  -F restrictions=null \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F required_linear_history=true
```

### Step 13 · Enable secret scanning & push protection

Both repos · Settings → Code security → Enable secret scanning + push protection. Document in runbook.

### Step 14 · Author `platform-contract.yml`

Template per § 04 Deliverable 8. Commit to both repos.

### Step 15 · Author runbook §§ 1–3

Write `docs/05-runbook.md` sections 1, 2, 3. Include screenshots / command output snippets where helpful. Another engineer must be able to follow it cold.

### Step 16 · Self-test

- [ ] Both repos public, clonable
- [ ] Pre-commit works on both — `pre-commit run --all-files` passes
- [ ] All 4 Bicep modules lint clean
- [ ] Both Terraform files lint clean
- [ ] Branch protection active on `main` both repos
- [ ] Secret scanning enabled both repos
- [ ] No Azure resources created (verify: `az resource list --resource-group rg-genai-portfolio-prod-swc` → empty or RG not found)
- [ ] Charter + ADRs + this Brief all committed
- [ ] `platform-contract.yml` templates committed
- [ ] Runbook §§ 1–3 readable cold

---

## § 07 · Acceptance Criteria

Each item binary pass/fail. Architect reviews against this list.

| # | Criterion | Evidence |
|---|---|---|
| A-01 | Both GitHub repos exist, public, CI enabled | Two repo URLs |
| A-02 | Pre-commit hooks configured and passing on both repos | `pre-commit run --all-files` output |
| A-03 | Secret scanner (gitleaks) active; verified against test credential | Test credential triggers block |
| A-04 | Branch protection on `main` both repos · PR required · linear history | Screenshot / `gh api` output |
| A-05 | Bicep modules (4) lint clean | `az bicep build` output for each |
| A-06 | Terraform mirrors (2) lint clean | `terraform validate` output |
| A-07 | Charter committed to `docs/00-charter.md` in project-00 | Commit SHA |
| A-08 | ADR-0001 through ADR-0010 committed MADR format | File listing |
| A-09 | `platform-contract.yml` template committed both repos | File listings |
| A-10 | `docs/05-runbook.md` §§ 1–3 authored | File reads clearly cold |
| A-11 | No Azure resources deployed yet (Wave 4 gate respected) | `az resource list` empty |
| A-12 | `metadata.json` populated in project-00 | File contents |

---

## § 08 · Review Rubric (Architect's checks)

When you return, Architect will:

1. Clone both repos fresh · run `pre-commit run --all-files` → must pass
2. Read `docs/05-runbook.md` cold, attempt to follow mentally → must be self-sufficient
3. Inspect ADR quality — trade-offs named, not just decisions stated
4. Lint Bicep and Terraform independently
5. Verify no Azure resources exist (`az resource list`)
6. Verify `platform-contract.yml` field completeness (values may be TBD but fields must be present)
7. Check tag taxonomy implementation in `tags.bicep`
8. Attempt to push a `.env` file → secret scanning must block it

---

## § 09 · Risks & Your Mitigations

| Risk | Mitigation you implement |
|---|---|
| Key Vault name collision (globally unique) | `naming.bicep` appends optional `uniqueSuffix` param |
| User lacks `gh` CLI | Runbook provides both `gh` and web-UI paths |
| User on Windows | Provide PowerShell equivalents alongside bash commands |
| Terraform vs Bicep version drift | Pin exact versions in runbook (Terraform ≥ 1.9 · Bicep ≥ 0.30) |
| Missing Entra permission (app registration) | Runbook lists required Azure AD role: `Application Administrator` or higher; escalation path documented |
| `uv` unfamiliar to reviewer | Runbook includes 5-line `uv` primer |

---

## § 10 · Escalation Contract

If you hit ambiguity you cannot resolve from Charter + ADRs + this Brief:

1. Do NOT invent architectural choices
2. Output structured questions:

```markdown
# Brief A · Escalations

## Q1 · <one-line summary>
- Context: <where you hit ambiguity>
- My options: <option A · option B · option C>
- My recommendation: <which and why>
- Blocks build: <yes/no>
```

3. Return to Architect chat for resolution, continue after.

---

## § 11 · Expected Output Format

When you return:

1. **Two repo URLs** (cloneable)
2. **Filled `platform-contract.yml`** (values TBD noted as `<TBD-wave-4>`)
3. **`runbook-delta.md`** · any deviation from this Brief
4. **Self-assessment** · 12 acceptance criteria (pass/fail + evidence)
5. **Open escalations** (if any)

Paste all five in your return message. Architect reviews against the rubric.

---

## § 12 · Closure

Brief A closes when Architect signs off against the acceptance rubric. On closure:

- Briefs B, C, D, E read your `platform-contract.yml` as their input
- `docs/05-runbook.md` §§ 1–3 become the canonical platform-setup reference
- You are done · Brief B has been running in parallel and may also be closing

---

**End of Builder Brief · A · Platform & Identity**

`Dammam · 2026-04-24 · Rev 1.0`
