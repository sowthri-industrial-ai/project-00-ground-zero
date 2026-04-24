# Charter — Project Ground Zero

```
Document    · Charter-00 · Project Ground Zero
Revision    · 1.3
Date        · 2026-04-24
Owner       · Sowthri (Architect)
Status      · Kick-off · Pre-build
Program     · GenAI Architect Portfolio
Location    · Dammam, KSA
```

---

## § 00 · Canonical Assertion

> *Project Ground Zero builds the platform before the payload. Every Charter that follows — for every subsequent project in the portfolio — inherits from this foundation without modification. The value of Ground Zero is not in what it does; it is in what it enables every subsequent project to do, faster and with zero architectural drift.*

---

## § 01 · Executive Summary

Ground Zero is the architectural substrate of the GenAI Architect Portfolio. Its mission is narrow and load-bearing: establish the full production stack — Azure landing zone, OIDC-secured GitHub↔Azure federation, sync pipeline (Local→Git→HF→Azure), deploy orchestrator with stage-gate enforcement, Portfolio Control Plane on GitHub Pages, seven-tier test harness, and a trivial **"Hello AI"** payload that exercises every layer end-to-end — and prove the platform is re-runnable from zero in under twenty minutes.

Ground Zero closes when a full teardown (`./deploy.sh --teardown`), followed by a single `./deploy.sh --all`, produces the same working system. That re-runnability proof is the deliverable; the Hello AI demo is incidental.

Ground Zero is scoped to **$25 of the $200 / 30-day Azure free-credit window**, deliberately leaving $175 for Project 1. It is built locally-first on Docker Compose, with Azure activation reserved for a concentrated validation sprint in Wave 4.

### Key numbers

| Metric | Value |
|---|---|
| Scope | 5 blocks · 5 Builder Briefs |
| Duration | 21 days (5 waves) |
| Azure budget | $25 of $200 ceiling |
| Test tiers | 7 (Unit · Smoke · Functional · AI Guardrail · Responsible AI · Red-team · Eval Regression) |
| Deploy targets | 4 (Local · Git · HF · Azure) |
| Definition of Done | 13 binary criteria |
| Re-runnability target | Fresh-start deploy < 20 min |

---

## § 02 · Strategic Context

### Why Ground Zero is its own project

Three arguments, ordered by strength:

1. **Separation of platform from payload.** OIDC federation, reusable IaC, multi-target deploy orchestrator, PCP, editorial HTML, seven-tier test harness, ledger discipline — this is the hard part of any GenAI portfolio. Bundled into a use-case project, infra consumes the content budget. Isolated, both get room.

2. **Every future project inherits, zero drift.** Charter #1 starts from proven foundation. Build time for Project 1 collapses to "build the interesting parts on top of working substrate." Cross-project consistency becomes structural, not aspirational.

3. **Architect-signal itself.** Senior architects build platforms before payloads. Real enterprise GenAI programs do this. Ground Zero in the portfolio signals that instinct — demonstrates the candidate does not conflate *demo* with *system*.

A practical fourth: the PCP demos from day one with Ground Zero live on it, not empty waiting for a real project.

### What Ground Zero is NOT

- Not a project with real use-case content
- Not a showcase of advanced agentic depth, fine-tuning rigor, or domain sophistication
- Not the "portfolio" a hiring panel sees — it is the substrate visible underneath every project
- Not infra completeness for its own sake — every block maps to a capability Project 1+ will exercise

---

## § 03 · Mission Statement

Prove the GenAI Architect Portfolio platform works end-to-end before any use-case content is built. Specifically:

**Ground Zero succeeds if, at closure:**

1. A hiring-panel reviewer can land on the PCP URL, see a live architecture visualization, click through to a working Hello AI demo, view the as-built ledger, and trust that what they see matches reality
2. The architect can scaffold a new project with `./scripts/new-project.sh <name>` and have CI, tests, deploy pipeline, and PCP integration work on first run
3. A fresh Azure subscription, GitHub org, and HF account reproduce the entire system in under 20 minutes

---

## § 04 · Goals & Non-Goals

### Goals

**Platform (Block A)**
- Azure landing zone · RG hierarchy · naming convention · tag taxonomy
- OIDC federation GitHub ↔ Entra ID — zero long-lived Azure credentials
- Key Vault + Managed Identity baseline
- Bicep + Terraform reusable module library

**Runtime (Block B)**
- Azure OpenAI (Sweden Central · Global Standard deployment)
- Azure AI Search Free tier index scaffold
- Cosmos DB · Azure Blob · Azure SQL (all free-tier provisioned)
- Azure Content Safety · Application Insights
- Langfuse self-hosted on Container Apps

**Pipeline (Block C)**
- `scripts/deploy.sh` orchestrator · idempotent · fan-out to 4 targets
- GitHub Actions workflow library (reusable across projects)
- Path-scoped sync pipeline routing commits to targets
- `as-built/ledger.jsonl` append-only writer
- `metadata.json` schema implemented and validated
- G1–G4 stage gates enforced with fail-closed behavior

**Control Plane (Block D)**
- Astro-based PCP with seven zones + TCO zone
- Ledger rendering (JSONL → HTML table)
- Markdown-as-source render pipeline
- Component-level deep-link generator
- Drift detection (Local vs Git vs HF SHAs)
- Custom domain + SSL · honest placeholder rendering

**Hello AI (Block E)**
- Minimal RAG (1 doc → hybrid retrieval → GPT-4o-mini generation)
- Minimal agent (LangGraph · 1 tool · 1 reflection · 1 HITL checkpoint)
- Minimal multi-agent (supervisor + 1 specialist via MCP)
- Minimal fine-tune scaffolding (Azure ML Pipeline skeleton + Model Registry entry)
- Deployed to all 4 targets
- Langfuse tracing wired · cost middleware active · Content Safety gate live

**Test Harness (distributed across C + E)**
- All 7 tiers implemented with at least one real test each
- G1–G4 gates enforce respective tiers
- Scheduled weekly red-team runs
- CI eval regression with thresholds

### Non-Goals

- Any real use-case content (deferred to Project 1+)
- Fine-tuning with real training data (scaffold only; training deferred to Colab)
- Multi-agent beyond supervisor + 1 specialist (proof of pattern, not breadth)
- Custom Next.js frontend (Streamlit sufficient for Hello AI)
- Production traffic volumes · HA architecture · multi-region
- Private endpoints / VNet integration (public endpoints sufficient)

---

## § 05 · Stakeholder & Role Model

| Role | Owner | Responsibility |
|---|---|---|
| Architect | Sowthri (Architect Claude chat) | Charter · Briefs · reviews · architectural decisions |
| Builder(s) | Separate Claude Code sessions, one per Brief | Implementation · tests · documentation |
| Orchestrator | `scripts/deploy.sh` + GitHub Actions | Packaging · deploy fan-out · ledger write |
| Reviewer | Architect | Review Builder output against acceptance criteria |

**Chat separation discipline**

- This Architect chat produces specifications and reviews outputs only
- Builder chats receive one self-contained Brief each, implement against it, return artifacts
- No Builder chat sees another Brief's output directly — only interface contracts
- All outputs return to Architect chat for review before integration

---

## § 06 · Timeline & Cadence

Parallel cadence per user selection: Blocks A+B parallel in Wave 1, C+D parallel in Wave 2, E solo in Wave 3.

| Wave | Days | Blocks | Activation state | Azure spend |
|---|---|---|---|---|
| 1 | 1–5 | A · Platform · B · Runtime (parallel) | Local only | $0 |
| 2 | 6–10 | C · Pipeline · D · PCP (parallel) | Local + Git + GitHub Pages | $0 |
| 3 | 11–14 | E · Hello AI | Local + HF | $0 |
| 4 | 15–18 | **Azure validation sprint** · integration · DoD tests · tear-down + re-run proof | **Azure credit activated** | ~$25 |
| 5 | 19–21 | Editorial HTML polish · runbook · close-out · Charter #1 handoff | Local + published | $0 |

**Azure activation gate.** Azure free credit is NOT activated until Wave 4. All prior work runs on Docker Compose, Ollama, local pgvector, and local Langfuse. This preserves the $200/30-day window for Project 1+, not Ground Zero.

---

## § 07 · High-Level Design

Ground Zero instantiates four concentric zones:

### Zone 1 · Portfolio Infrastructure (project-agnostic)
- GitHub org + `genai-portfolio-hub` repo + project-repo template
- Azure subscription + landing zone
- HuggingFace org/user namespace
- PCP domain on GitHub Pages

### Zone 2 · Runtime Substrate (shared across projects)
- Azure OpenAI (Sweden Central)
- Container Apps environment
- AI Search · Cosmos · Blob · SQL
- Content Safety · App Insights · Key Vault
- Langfuse

### Zone 3 · Delivery Pipeline
- `deploy.sh` orchestrator + GH Actions workflows
- OIDC federation
- Append-only ledger
- Stage gates G1–G4

### Zone 4 · Hello AI Payload
- Single repo `project-00-ground-zero/` with 5 block subfolders
- Streamlit demo
- HF Space mirror
- Azure live endpoint

The system diagram in editorial form ships as `html/architecture.html` (Wave 5).

---

## § 08 · Architectural Decision Records

Ten decisions captured in MADR format. Summary below; full text in `docs/03-ADR/`.

| ADR | Decision | Load-bearing rationale |
|---|---|---|
| **0001** | Azure region = Sweden Central · Global Standard deployment | Microsoft-recommended; broadest EU model availability; ~100ms from Dammam; UAE North disqualified (routes inference out); pricing parity |
| **0002** | OIDC federation GitHub ↔ Entra ID | Zero long-lived secrets; architect-signal for modern cloud security; scoped tokens per workflow |
| **0003** | PCP on GitHub Pages, not Azure SWA | Monitoring infrastructure must be independent of monitored infrastructure — PCP on Azure creates circular dependency during the exact outages PCP exists to report |
| **0004** | Polyrepo — hub + one repo per project | Hiring managers browse one repo at a time; independent CI/CD; each project sells on its own README |
| **0005** | `deploy.sh` is orchestrator · PCP is consumer of deploys | Failure isolation — broken site ≠ broken deploy |
| **0006** | Bicep primary · Terraform secondary | Azure-native speed + multi-cloud fluency signal |
| **0007** | Seven test tiers including Responsible AI + Red-team | AI Guardrail + Responsible AI are architect-signal differentiators; most portfolios omit them |
| **0008** | GitHub is source of truth · P-SelfDescribing principle | Eliminates the two-system problem causing doc sites to drift within weeks |
| **0009** | Python 3.12 + `uv` | Current stable · fastest modern package manager · `uv` adoption signals currency |
| **0010** | Astro for PCP | Markdown-native · zero-JS default · content collections map to project descriptors |
| **0011** | Deliberate failure-demo branches kept permanently (`demo-fails-g1` · `demo-fails-guardrail` · `demo-regresses-eval`) | Confidence-signal: showing known failure modes demonstrates you understand where the boundaries are. Most portfolios show happy-path only |
| **0012** | PCP URL = `<user>.github.io` (free tier · no custom domain) | $0 cost · portable later via CNAME · architect signal carried by content not URL polish |
| **0013** | Azure endpoint is ephemeral by design — spun up per interview, torn down after | Burn rate ~$0.50/demo vs $200/2-weeks if always-on. Doubles as re-runnability proof for DoD #10 |

---

## § 09 · Non-Functional Requirements

| # | Requirement | Target | Measured by |
|---|---|---|---|
| NFR-01 | Fresh-start deploy time | < 20 min wall-clock | DoD #10 |
| NFR-02 | PCP rebuild (ledger → live) | < 5 min | GH Actions duration log |
| NFR-03 | Local dev stack | Fully runnable offline via Docker Compose | `docker compose up` starts Langfuse + Ollama + pgvector |
| NFR-04 | Ground Zero Azure spend | ≤ $25 of $200 | Azure Cost Management export |
| NFR-05 | Long-lived secrets | Zero | Repo scan + GitHub secret-scanning |
| NFR-06 | PCP uptime | > 99% | GH Pages SLA + scheduled health check |
| NFR-07 | `deploy.sh` idempotency | Safe N times | Integration test |
| NFR-08 | Teardown completeness | No orphaned resources | Post-teardown RG listing |
| NFR-09 | Test execution time | Unit < 30s · Smoke < 2m · Functional < 10m | CI workflow duration |
| NFR-10 | Cost telemetry latency | Token cost visible in Langfuse < 10s of request | Middleware instrumentation |

---

## § 10 · Threat Model (STRIDE-lite)

| Threat | Risk | Mitigation |
|---|---|---|
| **Spoofing** — stolen GH token impersonates Architect | Medium | OIDC federation; signed commits (recommended); protected `main` |
| **Tampering** — ledger entries altered | Low | Append-only contract; Git commit history; PR review on ledger touches |
| **Repudiation** — deploy made, no record | Low | Ledger mandatory at G4; `deploy.sh` writes before returning success |
| **Information Disclosure** — secrets in repo | Medium | Key Vault for runtime secrets; OIDC for CI auth; GH secret scanning; `.env.example` pattern; pre-commit blocks `.env` |
| **Denial of Service** — portfolio attacked | Low | PCP static (GH Pages CDN); API Management rate limits; Content Safety rejects abuse |
| **Elevation of Privilege** — service escalates | Medium | Least-privilege Managed Identities per service; scoped Entra apps; no admin roles in CI |
| **Prompt Injection** — user input manipulates agent | High | NeMo Guardrails input filters; Content Safety Prompt Shields; agent tool authorization; Garak/PyRIT weekly |
| **Data Exfiltration via Agent** — agent returns sensitive data | High | Presidio PII redaction on output; Content Safety groundedness; Pydantic output schema |

---

## § 11 · Test Architecture — Seven Tiers

Every tier is first-class at Ground Zero. Every future project inherits.

### Tier 1 · Unit
- **Tests**: Component-level pure logic; dependencies mocked
- **Runs**: Pre-commit hook + CI G1
- **Framework**: pytest + pytest-asyncio + pytest-mock
- **Pass**: 100% declared tests pass; coverage ≥ 70% on `src/`
- **Fail action**: Block commit / block G1 gate

### Tier 2 · Smoke
- **Tests**: Post-deploy health per target
- **Runs**: CI G3 (post-deploy)
- **Framework**: bash + httpx
- **Pass**: All 4 endpoints respond 200 within timeout
- **Fail action**: Deploy unhealthy in ledger; no G4 progression

### Tier 3 · Functional
- **Tests**: End-to-end scenarios against deployed Hello AI
- **Runs**: CI G4 (post all targets)
- **Framework**: pytest + httpx + Playwright (Streamlit UI)
- **Pass**: All scenarios pass within latency NFR
- **Fail action**: Deploy REJECTED; ledger records gate failure

### Tier 4 · AI Guardrail
- **Tests**: Runtime safety boundary actually fires
- **Runs**: CI G4 + scheduled daily
- **Framework**: NeMo Guardrails harness + Presidio fixtures + Content Safety API
- **Scenarios**:
  - Prompt injection rejected
  - PII in output redacted
  - Jailbreak blocked
  - Groundedness fails on hallucination
- **Pass**: All guardrails behave as specified (block/redact)
- **Fail action**: Deploy REJECTED

### Tier 5 · Responsible AI
- **Tests**: Bias · fairness · toxicity · hallucination · transparency · PII-leakage
- **Runs**: CI G4 (threshold gate) + weekly regression
- **Framework**: Giskard + DeepEval + custom bias-probe + RAGAS faithfulness
- **Thresholds**:
  - Toxicity < 0.1
  - Hallucination rate < 5%
  - RAGAS faithfulness > 0.85
  - Groundedness > 0.85
  - Bias variance across demographic probes < 5%
- **Pass**: All thresholds met
- **Fail action**: Deploy REJECTED with metric failure logged to ledger

### Tier 6 · Red-team
- **Tests**: Adversarial — injection · jailbreak · data exfil · persistent manipulation
- **Runs**: Scheduled weekly + pre-release (tagged release)
- **Framework**: Garak + PyRIT
- **Pass**: ≥ 80% Garak probe coverage; zero critical findings unresolved
- **Fail action**: Critical findings block release; ledger logs

### Tier 7 · Eval Regression
- **Tests**: Quantitative retrieval + generation quality cannot degrade
- **Runs**: CI G4 threshold gate + nightly
- **Framework**: RAGAS + DeepEval + Promptfoo CI
- **Metrics**:
  - RAGAS context precision > 0.80
  - RAGAS answer relevancy > 0.85
  - RAGAS faithfulness > 0.85
  - Latency P95 < 5s
- **Pass**: No metric regresses > 5% from main branch baseline
- **Fail action**: CI red; PR blocked until restored

---

## § 12 · TCO Summary

Full calculation logic: `docs/06-tco.xlsx` Rev 2.0. Summary reconciles to the workbook's computed values — **Charter ceiling $25 · TCO actual $21.16 · headroom $3.84**.

| Component | Wave | Est. USD |
|---|---|---|
| Azure OpenAI tokens — 29.6M (GPT-4o-mini + GPT-4o + embeddings) | 4 | $6.24 |
| Container Apps — 3-day pulse · 0.5 vCPU · 1 GiB | 4 | $2.34 |
| Azure ML NC6 GPU — 2 hours (LoRA demo) | 4 | $1.80 |
| AOAI fine-tune Online Endpoint — 1 hour ephemeral | 4 | $1.70 |
| AI Search · Cosmos · Blob · Content Safety · Doc Intelligence · egress — all free-tier | 4 | $0.00 |
| Key Vault ops · Container Registry Basic 7-day pro-rated | 4 | $1.32 |
| **ALLaM managed endpoint — 1 hour ephemeral + 50K tokens (Brief E Deliverable 4g)** | 4 | $1.56 |
| Buffer (unplanned / re-run) | 4 | $6.00 |
| **Ground Zero actual spend (TCO Rev 2.0)** | | **$21.16** |
| Headroom vs NFR-04 ceiling ($25) | | $3.84 |
| Reserved for Project 1+ ($200 − $21.16) | 1+ | $178.84 |
| **$200 ceiling** | | **$200.00** |

All rates linked to `Pricing Reference` sheet · all quantities sourced from Block E specifications · zero illustrative values.

Components delivered at $0 incremental cost despite being added in Rev 2.0: LlamaIndex (library) · ColPali (CPU-hosted model) · Azure Functions (Consumption plan under free-tier cap).

---

## § 13 · Deliverables Manifest

### Repositories
- `genai-portfolio-hub` — public · hub-level scaffold
- `project-00-ground-zero` — public · project-level scaffold

### Documentation
- `docs/00-charter.md` (this document)
- `docs/01-HLD.md` + `docs/02-LLD.md`
- `docs/03-ADR/0001..0020.md` (MADR format · includes ADRs 0014–0020 per Brief E stack-coverage amendments)
- `docs/04-threat-model.md`
- `docs/05-runbook.md` (fresh-start provisioning)
- `docs/06-tco.xlsx` + `docs/06-tco.md`
- `docs/07-poc-specifications/brief-a..e.md` (five Builder Briefs)
- `docs/08-tech-stack-coverage-matrix.md` (cross-project stack sequencing · Rev 2.0)

### HTML references
- `html/architecture.html` — Ground Zero system visualization (editorial)
- `html/charter.html` — charter rendered
- `html/review.html` — post-close as-built narrative

### Code
- `src/` — minimal Hello AI app
- `infra/bicep/` + `infra/terraform/` — reusable module library
- `scripts/deploy.sh` · `scripts/bootstrap.sh` · `scripts/new-project.sh`
- `tests/unit|smoke|functional|guardrail|responsible-ai|red-team|eval/`

### CI workflows
- `.github/workflows/`: `ci.yml` · `sync-hf-space.yml` · `sync-hf-model.yml` · `deploy-azure.yml` · `pcp-update.yml` · `red-team-weekly.yml` · `eval-regression-nightly.yml`

### PCP
- `genai-portfolio-hub/control-plane/` — Astro site
- Custom domain configured · SSL issued · DNS pointed

### Ledger
- `as-built/ledger.jsonl` with ≥ 1 entry (Ground Zero close)
- `as-built/README.md` auto-rendered

---

## § 14 · Definition of Done

Ground Zero closes only when all 13 are true. Binary, no grey.

| # | Criterion |
|---|---|
| 1 | `genai-portfolio-hub` + `project-00-ground-zero` repos public on GitHub |
| 2 | Azure subscription active; OIDC working; Bicep deploys from empty subscription in < 20 min |
| 3 | PCP live at `<user>.github.io` (free tier); Ground Zero status rendered from ledger |
| 4 | Hello AI deployed to Local + Git + HF Space + Azure; all four URLs reachable during Wave 4 validation · Azure endpoint may be spun down after validation (ephemeral pattern per ADR-0013) |
| 5 | All 7 test tiers implemented with passing tests on fresh deploy |
| 6 | G1–G4 gates enforced; one documented test proves each gate fails closed |
| 7 | Ledger contains entries for every deploy; rendered on PCP As-Built zone |
| 8 | `metadata.json` populated; PCP reads it correctly |
| 9 | `deploy.sh --teardown` works; no orphaned resources |
| 10 | **Full fresh-start reproduction**: delete Azure RG, re-run from scratch, everything works |
| 11 | `architecture.html` + `charter.html` + `review.html` published in editorial aesthetic |
| 12 | Runbook + threat model + TCO workbook committed |
| 13 | `scripts/new-project.sh` scaffolds Project 1 repo cleanly; CI green on first run |

**Criterion 10 is the platform-proof.** Nothing closes until it passes.

---

## § 15 · Risk Register

| ID | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| R-01 | OIDC federation setup delays Wave 1 | Medium | Medium | Step-by-step runbook; `azure/login` action with federation; test with `az login --federated-token` before real use |
| R-02 | $200 credit burned too fast | High | Medium | Azure activation gated to Wave 4; ephemeral resources torn down immediately; budget alerts at 50%/80%/100% |
| R-03 | Tests flaky due to LLM nondeterminism | Medium | High | Retry cap at 3; isolate network-dependent tests; recorded fixtures for eval regression where possible; tolerance bands |
| R-04 | PCP empty reads as "not started" | Low | Low | Honest placeholders; Hello AI demo visible; Ground Zero status live |
| R-05 | Builder chats misinterpret Briefs | Medium | Medium | Acceptance criteria + review rubric in every Brief; interface contracts explicit; example output scaffolds; Architect review cycle |
| R-06 | Responsible AI thresholds too aggressive · blocks legit deploys | Low | Medium | Thresholds calibrated against Hello AI baseline; gate warns Wave 1-3, blocks Wave 4+ |
| R-07 | Fresh-start proof fails at minute 21 | High | Medium | Dry-run teardown/redeploy in Wave 4 before final close; iterate to < 20min |
| R-08 | ALLaM / Arabic model unavailable Sweden Central | Low | High | Not needed for Ground Zero; deferred to Project 1+ if relevant |

---

## § 16 · Builder Brief Index

Five Briefs handed off in cadence order.

| Brief | Scope | Handoff Wave | Dependencies |
|---|---|---|---|
| **A** | Platform & Identity | Wave 1 | None |
| **B** | Runtime Substrate | Wave 1 (parallel) | A's Entra + RG |
| **C** | Delivery Pipeline | Wave 2 | A (OIDC) · B (resources) |
| **D** | Portfolio Control Plane | Wave 2 (parallel) | A (repo structure) |
| **E** | Hello AI Payload | Wave 3 | B (runtime) · C (pipeline) |

Uniform contract per Brief: context · goals · non-goals · deliverables · interface contracts · step-by-step · acceptance criteria · review rubric · risks · escalation contract.

**Brief A ships with this charter.** Briefs B–E ship before their respective handoff waves.

---

## § 17 · Appendix A · Naming & Tagging

### Resource-group naming
`rg-<program>-<env>-<region-short>`
Example: `rg-genai-portfolio-prod-swc` (Sweden Central = swc)

### Resource naming
`<prefix>-<program>-<seq>`
- `aoai-genai-portfolio-01` — Azure OpenAI
- `srch-genai-portfolio-01` — AI Search
- `cosmos-genai-portfolio-01`
- `cae-genai-portfolio-01` — Container Apps Environment
- `kv-genai-portfolio-01` — Key Vault (append random suffix if collision)
- `mi-genai-portfolio-01` — Managed Identity

### Tag taxonomy (mandatory on every resource)

| Tag | Value pattern | Example |
|---|---|---|
| `project` | program slug | `genai-portfolio` |
| `project-phase` | `ground-zero` / `p1` / `p2`... | `ground-zero` |
| `environment` | `dev` / `staging` / `prod` | `prod` |
| `cost-center` | owner cost tag | `personal-portfolio` |
| `owner` | email or handle | `ssomasundaram` |
| `poc-id` | `brief-a` / `brief-b` / ... | `brief-a` |
| `managed-by` | `bicep` / `terraform` / `manual` | `bicep` |

---

## § 18 · Acceptance & Closure

Ground Zero is signed off by the Architect when all 13 DoD criteria show ✅ in the close-out `review.html`.

On signature:
1. `scripts/new-project.sh project-01-<name>` executes cleanly
2. Charter #1 drafts with Ground Zero as assumed substrate
3. `project-00-ground-zero` repo remains public; referenced from every subsequent project's README

---

**End of Charter-00 · Project Ground Zero · Rev 1.3**

`Dammam · 2026-04-24`

---

## § 19 · Change Log

### Rev 1.3 · 2026-04-24

| Change | § | Driver |
|---|---|---|
| Tech stack coverage re-evaluation · Ground Zero lifted from ~90% to ~97% | § 16 (ref) | Substrate-built principle: additions are lightweight once platform exists. User challenge "why defer the rest" prompted honest reassessment |
| Brief E rev 1.1 → 1.2 · four new deliverables (4d LlamaIndex · 4e ColPali · 4f Azure Functions · 4g ALLaM) | § 16 | Four of five previously-deferred components pulled into Ground Zero · each with TCO-consistent cost |
| Next.js confirmed deferred with explicit ADR | § 08 | ADR-0020 documents why Next.js stays out · Streamlit sufficient · avoiding architecture theater · flagship is correct placement |
| ADRs 0016–0020 queued for Brief E authoring | § 08 | LlamaIndex · ColPali · Functions · ALLaM · Next.js-deferred — each a decision artifact |
| TCO Rev 1.0 → 2.0 · actual $19.63 → $21.16 · ALLaM managed endpoint line added · NFR-04 still PASS with $3.84 headroom | § 12 | ALLaM thin demo costs ~$1.56 · other three additions are $0 incremental (library · CPU inference · consumption free tier) |
| Coverage matrix Rev 1.0 → 2.0 | § 13 | Reflects new ✅ marks for 4 components · Next.js deferral reasoning |

### Rev 1.2 · 2026-04-24

| Change | § | Driver |
|---|---|---|
| `docs/08-tech-stack-coverage-matrix.md` added to manifest | § 13 | Explicit sequencing of 30 stack components across Ground Zero + Projects 1–3. Ground Zero lifted from ~75% → ~90% coverage |
| Brief E amended · Semantic Kernel · Cosmos DB · Document Intelligence added | § 16 (reference) | Three provisioned-but-unused components become exercised · ~5 hours added to Brief E scope · no cadence impact |
| ADRs 0014 (SK vs LangGraph) · 0015 (Docling vs Doc Intelligence) to be authored during Brief E | § 08 | Documents the framework-choice reasoning · architect signal |
| Reinforced: all repos public (ADR-0004 unchanged) · no private code in portfolio ever | § 04 · DoD #1 | Reviewer auditability · free-tier GH features depend on public |

### Rev 1.1 · 2026-04-24

| Change | § | Driver |
|---|---|---|
| TCO § 12 reconciled to computed $19.63 actual · $25 ceiling preserved as NFR-04 | § 12 | Caught Charter↔TCO inconsistency during TCO build (AI Search Basic vs Free tier mismatch). Deloitte consistency preference |
| ADR-0011 added · deliberate failure-demo branches kept permanently | § 08 | Demonstrates the pipeline's gate behavior live; differentiator vs happy-path-only portfolios |
| ADR-0012 added · PCP URL = `<user>.github.io` (free tier) | § 08 | User decision: skip paid `.dev` domain · content carries signal · portable later via CNAME |
| ADR-0013 added · Azure endpoint is ephemeral by design | § 08 | $200 credit preservation; spin-up-per-interview pattern · burn ~$0.50/demo vs $200/2wk always-on. Doubles as DoD #10 re-runnability proof |
| DoD #3 updated to reference free GH Pages URL | § 14 | Consistent with ADR-0012 |
| DoD #4 updated to acknowledge ephemeral pattern | § 14 | Consistent with ADR-0013 |

### Rev 1.0 · 2026-04-24

Initial Charter · Kick-off baseline
