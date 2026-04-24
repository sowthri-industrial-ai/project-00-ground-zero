# Builder Brief · E · Hello AI Payload

```
Brief ID     · BRIEF-E
Block        · E · Hello AI Payload
Project      · project-00-ground-zero
Wave         · 3 (solo — no parallel)
Dependencies · Brief A (platform) · Brief B (runtime) · Brief C (pipeline) must be closed
Deliver to   · Architect chat for review
```

---

## § 01 · Context · You are here

You are Builder-E. Self-contained Brief · architectural choices locked in Charter + ADRs.

You are the final block — the payload that exercises every layer the prior blocks built. Your job: build a minimal-but-honest Hello AI application that demonstrates the four GenAI pillars (RAG · Agent · Multi-Agent · Fine-tune scaffold), instrument it with the full observability + safety stack, deploy it to all four targets, and create the three deliberate failure-demo branches per ADR-0011.

**"Minimal" is the hard constraint.** You are not building a production app. Each pillar gets the smallest working implementation that still reads as architecturally complete — one document in RAG, one tool in the agent, two agents in the multi-agent graph, one pipeline in the fine-tune scaffold. The richness is in the *integration*, not the breadth.

You are also the block that gets to break things on purpose — the three `demo-fails-*` branches are Ground Zero's most distinctive portfolio signal.

---

## § 02 · Goals

1. Minimal RAG · 1 document · AI Search hybrid retrieval (Azure) · pgvector (local) · GPT-4o-mini generation
2. Minimal LangGraph agent · RAG-as-tool · 1 reflection step · 1 HITL checkpoint
3. Minimal multi-agent · Supervisor + 1 Specialist (Retriever) connected via MCP
4. **Semantic Kernel planner** · alternative plan step before LangGraph routes · demonstrates framework polyglot
5. **Cosmos DB conversation memory** · session-keyed persistence · loaded at agent start · saved at end
6. **Document Intelligence second-ingest path** · one structured document (form/invoice) processed via Doc Intelligence alongside Docling
7. **LlamaIndex alternative ingestion** · demonstrates polyglot retrieval · index NIST doc via LlamaIndex `VectorStoreIndex` alongside native Azure AI Search path
8. **ColPali multimodal embedding** · 2-3 structure-rich pages indexed via ColPali (CPU) · visual-similarity retrieval on charts/tables
9. **Azure Functions serverless utility** · one Function App running hourly cost-aggregator cron · consumption plan free tier
10. **ALLaM thin demo** · SDAIA's Arabic-English model via Azure AI Foundry · one bilingual query path · regional signal
11. Fine-tune scaffold · Azure ML Pipeline YAML + Model Registry entry · NO actual training
12. Streamlit UI — three tabs · one per pillar above (fine-tune shown as artifact, not interactive)
13. Full safety stack · Content Safety (input + output gates) · NeMo Guardrails · Presidio PII redaction
14. Full observability · Langfuse tracing · cost middleware · App Insights
15. Deploy to all 4 targets via Brief C's `deploy.sh`
16. Three `demo-fails-*` branches per ADR-0011
17. Tests implementing all 7 tiers with at least one real assertion each
18. Document in `docs/05-runbook.md` §§ 13–15

---

## § 03 · Non-Goals

- ❌ Do NOT build a production-grade RAG (no re-ranking sophistication · no query rewriting · no HyDE)
- ❌ Do NOT build a deep agentic system (1 tool · 1 reflection · 1 HITL is the ceiling)
- ❌ Do NOT train an actual fine-tune model (scaffold only · actual LoRA training deferred to Project 1+)
- ❌ Do NOT build domain-specific logic (generic Hello AI — use public-domain document as corpus)
- ❌ Do NOT build custom UI components (Streamlit defaults · no Next.js · per ADR/Charter § 04)
- ❌ Do NOT modify prior Briefs' contracts (consume only)
- ❌ Do NOT wire the 3 demo-fails branches into main CI (they must live on branches · not pollute main)

---

## § 04 · Deliverables (exhaustive)

### Deliverable 1 · Project structure (populate `src/`)

```
src/
├── __init__.py
├── main.py                      # FastAPI entrypoint · /health, /ready, /chat, /metrics
├── config.py                    # Pydantic Settings · reads .env or Key Vault
├── models/                      # Azure OpenAI client wrappers
│   ├── __init__.py
│   ├── chat.py                  # AzureOpenAI chat (MI auth)
│   ├── embedding.py             # text-embedding-3-small
│   └── local_llm.py             # Ollama fallback for MODE=local
├── rag/
│   ├── __init__.py
│   ├── ingest.py                # 1 doc → chunks → embeddings → index (via Docling)
│   ├── doc_intelligence_ingest.py  # Azure Doc Intelligence · structured extraction (alt path)
│   ├── retrieve.py              # Hybrid retrieval (AI Search) or pgvector (local)
│   ├── generate.py              # RAG generation with cited sources
│   └── eval.py                  # RAGAS wrapper
├── agent/
│   ├── __init__.py
│   ├── graph.py                 # LangGraph state machine
│   ├── tools.py                 # RAG-as-tool definition
│   ├── reflection.py            # Self-critique node
│   ├── hitl.py                  # Human-in-the-loop interrupt logic
│   └── memory.py                # Cosmos DB conversation persistence (session-keyed)
├── multi_agent/
│   ├── __init__.py
│   ├── supervisor.py            # Routing supervisor (LangGraph)
│   ├── retriever_specialist.py  # RAG specialist as MCP server
│   ├── mcp_client.py            # MCP protocol client
│   └── sk_planner.py            # Semantic Kernel planner (alternative to LangGraph plan node)
├── fine_tune/
│   ├── __init__.py
│   ├── pipeline.yml             # Azure ML Pipeline definition (no actual run)
│   ├── register_model.py        # Model Registry entry stub
│   └── prepare_dataset.py       # Dataset prep (shows the pattern · no real training)
├── guardrails/
│   ├── __init__.py
│   ├── nemo_config.yml          # NeMo Guardrails rails
│   ├── content_safety.py        # Azure Content Safety input/output gates
│   └── presidio_redactor.py     # PII redaction
├── observability/
│   ├── __init__.py
│   ├── langfuse_tracer.py       # Langfuse integration
│   ├── cost_middleware.py       # Per-request token cost
│   └── app_insights.py          # App Insights metrics
└── ui/
    └── streamlit_app.py         # Streamlit UI with 3 tabs
```

### Deliverable 2 · Minimal RAG

**Corpus**: Single public-domain document (recommend: NIST AI RMF 1.0 PDF — ~80 pages · technical enough to showcase retrieval · public-domain · topically aligned with Responsible AI story). Ship in `data/nist-ai-rmf.pdf`.

**Ingestion flow** (`src/rag/ingest.py`):
1. Load PDF with Docling (structure-preserving parse · not raw `pypdf`)
2. Chunk: semantic chunking at 512 tokens · 50 token overlap
3. Embed via `text-embedding-3-small` (Azure in MODE=azure · Ollama `nomic-embed-text` in MODE=local)
4. Index:
   - **Azure mode**: Upsert to AI Search index `hello-ai-rag` with hybrid (vector + BM25)
   - **Local mode**: Upsert to pgvector table `chunks`

**Retrieval** (`src/rag/retrieve.py`): 
- Azure: hybrid retrieval via AI Search SDK · top-k=5 · no semantic reranking (Free tier doesn't support it · documented in Brief B)
- Local: cosine similarity on pgvector · top-k=5

**Generation** (`src/rag/generate.py`):
- System prompt instructs grounded answering + citation format `[chunk-id]`
- Citations visible in response · clickable to show source text
- Reject query if no chunks retrieved (don't hallucinate "I don't know" without grounding)

### Deliverable 3 · Minimal LangGraph agent

State machine with 4 nodes:

```
START → plan → use_rag_tool → reflect → (hitl_checkpoint if risky) → respond → END
```

**Node details**:
- `plan`: GPT-4o mini classifies query intent · decides whether RAG is needed
- `use_rag_tool`: Calls `src/rag/retrieve.py` as a tool
- `reflect`: Self-critique step · GPT-4o-mini scores its own draft response on groundedness · if < 0.7, loops back to `use_rag_tool` once max
- `hitl_checkpoint`: If query is flagged `risky` (keyword match on compliance/legal terms), pause graph · write to Langfuse · await human approval in Streamlit UI (for demo: a button)
- `respond`: Final formatted response · citations · Langfuse span closed

Use LangGraph's built-in interrupt pattern for HITL · state is serializable (for HF Space persistence).

### Deliverable 4 · Minimal multi-agent with MCP

**Supervisor** (`src/multi_agent/supervisor.py`):
- LangGraph with conditional routing
- Accepts user query · decides whether to invoke the Retriever specialist
- Handles final synthesis

**Retriever Specialist** (`src/multi_agent/retriever_specialist.py`):
- Standalone MCP server exposing one tool: `retrieve_from_rag(query, top_k)`
- Runs as a separate process (locally: background thread · Azure: separate Container App)
- Uses official MCP Python SDK

**MCP client** (`src/multi_agent/mcp_client.py`):
- Connects Supervisor to Specialist via MCP protocol (stdio or SSE transport)
- Graceful degradation if specialist unreachable → falls back to direct RAG call

**Why MCP here** (document in runbook § 13): demonstrates inter-agent tool sharing over a standard protocol · not a proprietary function-call pattern. Architect signal: the multi-agent boundary is an MCP boundary · not a Python import boundary · portable to non-Python tools later.

### Deliverable 4a · Semantic Kernel planner (stack-coverage amendment)

**`src/multi_agent/sk_planner.py`** — a Semantic Kernel-based planner that runs ONE step before the LangGraph Supervisor takes over. Flow:

```
user query → SK planner (decomposes into sub-tasks) → LangGraph Supervisor (routes) → MCP Specialist → response
```

Requirements:
- Use `semantic-kernel` Python SDK (pin version in `pyproject.toml`)
- Define 2 SK plugins: `decompose_query` · `classify_intent`
- Use SK's native function-calling pattern · NOT a LangGraph ToolNode wrapper (point is showing both idioms)
- Result feeds into LangGraph Supervisor as initial state
- Langfuse trace tags this as `planner=semantic-kernel` · `router=langgraph` for clear attribution

Add one ADR during authoring · `docs/03-ADR/0014-sk-vs-langgraph.md` · documents: "LangGraph primary for stateful agent graphs · Semantic Kernel for plugin-composition planning where SK's native patterns are more concise."

### Deliverable 4b · Cosmos DB conversation memory (stack-coverage amendment)

**`src/agent/memory.py`** — session-keyed conversation persistence. Flow:
- At agent run start · read conversation history by `session_id` from Cosmos container `conversations`
- Inject history into LangGraph initial state
- At agent run end · append new turns to Cosmos

Cosmos schema (container `conversations` · partition key `/session_id`):
```json
{
  "id": "<uuid>",
  "session_id": "<session-key>",
  "timestamp": "ISO-8601",
  "role": "user | assistant",
  "content": "<text>",
  "trace_id": "<langfuse-trace-id>",
  "tokens": { "in": 0, "out": 0 },
  "cost_usd": 0.000
}
```

Local mode: use Cosmos DB Emulator in Docker Compose · OR fallback to a simple SQLite table (both patterns acceptable · document which chosen in runbook).

Streamlit UI tab addition · "Memory" view shows last 5 turns of conversation for current session. Clearing session starts fresh.

### Deliverable 4c · Azure Document Intelligence second ingest (stack-coverage amendment)

**`src/rag/doc_intelligence_ingest.py`** — alternative ingest path using Azure Document Intelligence Read + Layout models.

Requirements:
- Ship one sample document at `data/sample-form.pdf` (recommend: synthetic invoice or form · generate with ReportLab · ~1 page)
- Process via Document Intelligence `prebuilt-layout` model · extract:
  - Text regions with bounding boxes
  - Tables as structured rows/columns
  - Key-value pairs
- Index extracted structure into AI Search as separate index `hello-ai-forms` (1 index allowed on Free tier · we already have `hello-ai-rag` · so this index creation is gated to Azure mode only · or uses pgvector in local)
- Streamlit RAG tab gains a toggle · "Corpus: NIST doc (Docling) | Sample form (Doc Intelligence)"
- Demonstrates architectural trade-off · Docling for text-heavy · Doc Intelligence for structure-heavy

Add to ADR `docs/03-ADR/0015-docling-vs-doc-intelligence.md`: "Docling primary for clean-text PDFs where parse fidelity is sufficient. Document Intelligence when structure (tables, forms, layout) is semantically meaningful. Not either/or — picked per document class."

### Deliverable 4d · LlamaIndex alternative ingestion (stack-coverage amendment)

**`src/rag/llamaindex_ingest.py`** — alternative ingestion path using LlamaIndex idioms alongside the native Azure AI Search path.

Requirements:
- Use `llama-index-core` + `llama-index-vector-stores-azureaisearch` (pin versions)
- Index the NIST doc via LlamaIndex's `VectorStoreIndex` with AzureAISearchVectorStore backend
- Resulting index shares the same AI Search service but writes to a separate index name (`hello-ai-rag-llamaindex`) — gated to Azure mode · local mode uses pgvector
- Streamlit RAG tab gains a 3-way toggle: "Native (Azure SDK) | Docling+AI Search | LlamaIndex" — shows same corpus, different orchestration layers, retrieves identically
- Langfuse trace tags retrieval path: `retrieval=native | retrieval=llamaindex`

ADR `docs/03-ADR/0016-llamaindex-alongside-native.md`: "LlamaIndex demonstrates the orchestration abstraction for retrieval. Native Azure SDK remains primary because Ground Zero's single-index simplicity doesn't exercise LlamaIndex's differentiators (routers, sub-question synthesis). Keeping both paths live gives reviewers a comparable benchmark."

### Deliverable 4e · ColPali multimodal embedding (stack-coverage amendment)

**`src/rag/colpali_ingest.py`** — vision-based document embedding for 2-3 structure-rich pages.

Requirements:
- Install `colpali-engine` (pinned version) · model weights downloaded from HuggingFace on first run · quantized variant for CPU-feasibility
- Select 2-3 pages from NIST doc that have tables/figures (e.g., Core functions diagram, profile tables)
- Process via ColPali: page-image → ColPali → patch-level embeddings
- Store embeddings in pgvector table `colpali_chunks` (schema: page_id, patch_id, vector, page_image_path)
- Ingestion is slow (~1-2 min per page on CPU) · run once · cache results
- Retrieval is fast (cosine over patches)
- Streamlit RAG tab gains a "Vision retrieval" toggle: when enabled, demo a query like *"show me the table describing the Govern function"* · ColPali returns the page image with relevant patches highlighted
- Comparison demo: same query via text retrieval misses the table structure · vision retrieval surfaces it

ADR `docs/03-ADR/0017-colpali-for-structure-rich-pages.md`: "ColPali for pages where semantic content lives in visual structure (tables, diagrams). Text chunking destroys that structure. Scoped narrowly — only structure-rich pages, not the full corpus. Pattern is portable to Project 1's P&ID corpus where ColPali becomes primary."

### Deliverable 4f · Azure Functions serverless utility (stack-coverage amendment)

**`src/functions/cost_aggregator/`** — Azure Function App running on Consumption plan.

Requirements:
- One timer-triggered function: runs hourly · cron `0 */1 * * * *`
- Queries Langfuse API for traces in last hour · aggregates `cost_usd` metadata · writes daily rollup to Cosmos container `cost_rollups`
- Demonstrates serverless idiom · Python Functions worker · MI authentication to Langfuse API via Key Vault secret
- Deployed via Bicep module `infra/bicep/modules/function-app.bicep` (Brief B extends · OR authored fresh here)
- Function emits metric to App Insights: `portfolio.cost.hourly_aggregate`
- Consumption plan: first 1M executions free · hourly cron = 720 executions/month · well under free tier · $0

Streamlit sidebar shows "Last cost rollup" pulled from Cosmos · demonstrates the end-to-end serverless data flow visibly.

ADR `docs/03-ADR/0018-functions-for-scheduled-utilities.md`: "Container Apps for request/response inference · Functions for event-driven utilities (scheduled, webhook, queue-triggered). Separation respects compute-pattern fit. Ground Zero uses Functions only for the cost aggregator · future projects will use it for OT telemetry ingestion and GitHub webhook receivers."

### Deliverable 4g · ALLaM thin demo (stack-coverage amendment)

**`src/models/allam_client.py`** — client for SDAIA's ALLaM-2-7b-instruct via Azure AI Foundry.

Requirements:
- Deploy ALLaM via Azure AI Foundry managed endpoint (Bicep module `infra/bicep/modules/foundry-allam.bicep`)
- Endpoint is **ephemeral** per ADR-0013 · spun up for Wave 4 validation + demo sessions only
- Add to Streamlit sidebar: language toggle "English (GPT-4o-mini) | Arabic (ALLaM)"
- When Arabic mode active: RAG queries route to ALLaM · NIST corpus does NOT have Arabic content · use a second small corpus at `data/saudi-vision-2030-bilingual.pdf` (public Saudi Vision 2030 document · officially bilingual) as Arabic-query target
- Demo one query in Arabic · one in English · show both render cleanly · grounded citations work in both
- Content Safety + groundedness check must fire on Arabic path (Content Safety supports Arabic)

ADR `docs/03-ADR/0019-allam-for-regional-signal.md`: "ALLaM demonstrates regional AI landscape awareness (KSA · SDAIA · Vision 2030). Thin demo in Ground Zero proves the deployment pattern. Arabic-primary projects land in Project 3 (flagship) where the corpus + use case justify full ALLaM integration."

ADR `docs/03-ADR/0020-nextjs-deferred-by-design.md`: "Next.js NOT in Ground Zero. Streamlit is functionally sufficient for the Hello AI demo surface. Adding a parallel Next.js UI without use-case justification is architecture theater. Flagship project (Project 3) is the correct placement — custom React where polished interactive UX is the purpose, not a parallel demo of 'I can use React too.'"

### Deliverable 5 · Fine-tune scaffold

**`src/fine_tune/pipeline.yml`** — Azure ML Pipeline YAML declaring:
- Input: `data/fine-tune-corpus.jsonl` (small synthetic instruction dataset · maybe 50 examples)
- Components:
  1. `prepare_dataset` — tokenization · train/val split · upload to Azure ML datastore
  2. `run_finetune` — **marked as manual approval** · would run LoRA training on NC6 GPU · currently a no-op returning mock metrics
  3. `register_model` — registers a placeholder in Model Registry with `stage=dev` · name `hello-ai-finetune-v1`
- Outputs: model artifact URI · eval metrics JSON

**`src/fine_tune/register_model.py`** — demonstrates registering a model with metadata (tags · metrics · dataset lineage). Called standalone for the demo.

**Ground Zero intent**: show the architectural pattern · not the ML. The Azure ML Pipeline graph is visible in Azure portal · Model Registry entry is visible · cost is near-zero (no training runs).

### Deliverable 6 · Safety stack

**Input gate** (Content Safety + Presidio):
```python
# src/guardrails/content_safety.py
async def input_gate(user_query: str) -> GateResult:
    # 1. Prompt Shields · detects jailbreak + prompt injection
    shield_result = await content_safety_client.analyze_prompt(user_query)
    if shield_result.attack_detected:
        return GateResult(pass_=False, reason="prompt_injection_detected")
    # 2. Categorical toxicity
    text_result = await content_safety_client.analyze_text(user_query)
    if any(cat.severity >= 4 for cat in text_result.categories):
        return GateResult(pass_=False, reason="unsafe_input")
    return GateResult(pass_=True)
```

**Output gate**: same pattern · also runs Presidio PII redaction · returns redacted output or blocks if critical PII (SSN · credit card) detected.

**NeMo Guardrails** (`src/guardrails/nemo_config.yml`): declarative rails for off-topic questions (reject anything not about the NIST doc) + refusal patterns for unsafe asks.

**Groundedness check**: Content Safety Groundedness API called after generation · if score < 0.85 · response flagged in Langfuse trace · UI shows "⚠️ low groundedness" banner.

### Deliverable 7 · Observability stack

**Langfuse** (`src/observability/langfuse_tracer.py`):
- Wrapper around LangChain/LangGraph Langfuse callback
- Every chat/agent/multi-agent invocation creates a trace
- Traces visible in both local Langfuse (`localhost:3000`) and Azure-deployed Langfuse
- Tags: `pillar=rag|agent|multi-agent` · `mode=local|azure` · `gate_result=pass|fail`

**Cost middleware** (`src/observability/cost_middleware.py`):
- FastAPI middleware · captures `X-Tokens-Input`, `X-Tokens-Output` headers from AOAI responses
- Computes USD cost using pricing table from `pricing.yml` (sourced from TCO Pricing Reference sheet — same numbers)
- Writes to Langfuse trace metadata · also logs to App Insights custom metric `request_cost_usd`

**App Insights** (`src/observability/app_insights.py`):
- OpenTelemetry-based · auto-instrumentation for FastAPI
- Custom metrics: request latency P95 · cost per request · gate rejection rate · groundedness score distribution

### Deliverable 8 · Streamlit UI

`src/ui/streamlit_app.py` with **three tabs** (Streamlit's `st.tabs`):

| Tab | Content |
|---|---|
| **🔍 RAG** | Query input · top-k slider · response with inline citations · click citation to show source text · groundedness score badge · cost badge · latency badge |
| **🤖 Agent** | Query input · "Run agent" button · shows graph execution trace (nodes traversed) · HITL-checkpoint resolution UI when interrupt fires · reflection loop count · final response |
| **👥 Multi-Agent** | Query input · shows Supervisor routing decision · Specialist tool call via MCP · combined response · MCP transport indicator (stdio/SSE) |

Sidebar shows:
- Mode toggle: Local / Azure
- Model selector: GPT-4o-mini / GPT-4o (large is opt-in — costs more)
- Langfuse link (opens traces for current session)

**Fine-tune not interactive** — link in sidebar to Azure ML Studio page showing the Pipeline + Registry entry.

### Deliverable 9 · Three `demo-fails-*` branches (ADR-0011)

Branch from `main` · each contains one intentional break:

| Branch | What breaks | Gate that catches | Demo narrative |
|---|---|---|---|
| `demo-fails-g1` | Import a non-existent module in `src/main.py` OR introduce type error in `src/rag/generate.py` | G1 · unit + mypy | "Here's what happens on bad code — G1 blocks the PR" |
| `demo-fails-guardrail` | Remove the `content_safety.input_gate` call in `src/main.py` + add test that sends known prompt injection payload | G4 · AI Guardrail tier | "Here's what happens when a safety check is bypassed — G4 rejects deploy" |
| `demo-regresses-eval` | Swap `text-embedding-3-small` for random-vector noise in `src/rag/retrieve.py` — retrieval quality drops | G4 · Eval Regression · RAGAS context precision crashes | "Here's what happens when retrieval regresses — nightly eval fires red" |

Each branch has:
- Clear commit message: `demo: intentional <x> failure to demonstrate <gate>`
- README badge on the branch explaining what it's showing
- **NEVER merged to main** · branches are permanent fixtures · documented as such in `docs/05-runbook.md` § 15

### Deliverable 10 · Seven-tier test implementation

| Tier | Location | One real assertion |
|---|---|---|
| 1 · Unit | `tests/unit/` | `test_rag_chunker_respects_token_cap()` — chunker never produces > 512-token chunks |
| 2 · Smoke | `tests/smoke/` | `test_health_endpoint_returns_200()` — live `/health` ping per target |
| 3 · Functional | `tests/functional/` | `test_rag_end_to_end_with_citation()` — query returns answer with ≥ 1 citation · citation text exists in corpus |
| 4 · AI Guardrail | `tests/guardrail/` | `test_prompt_injection_blocked()` — known DAN prompt returns gate-rejection |
| 5 · Responsible AI | `tests/responsible-ai/` | `test_bias_variance_across_demographic_probes()` — variance < 5% across name-swap probes · uses Giskard |
| 6 · Red-team | `tests/red-team/` | `test_garak_promptinject_probes()` — Garak probe suite runs · no critical findings |
| 7 · Eval Regression | `tests/eval/` | `test_ragas_faithfulness_above_baseline()` — RAGAS faithfulness ≥ 0.85 against golden set |

Golden set (`tests/eval/golden.jsonl`): 20 questions with reference answers · sourced from NIST doc · hand-curated.

### Deliverable 11 · Runbook §§ 13–15

- § 13 · Hello AI architecture · 4 pillars · safety + observability integration points
- § 14 · Running locally · `docker compose up` + `streamlit run src/ui/streamlit_app.py`
- § 15 · Deploying to all 4 targets + the three demo-fails branches · what each demonstrates

---

## § 05 · Interface Contracts

### Contract IN · From Brief A

- `platform-contract.yml` — auth config
- Pre-commit hooks active

### Contract IN · From Brief B

- `runtime-contract.yml` — endpoint registry
- `infra/bicep/modules/` — Bicep modules for your Container App wiring
- `docker-compose.yml` — local stack you join
- `Dockerfile` — stub you fill

### Contract IN · From Brief C

- `scripts/deploy.sh --target=<x>` — your deploy path
- Ledger schema — your workflow runs write entries via `scripts/ledger-write.sh`
- `/health` · `/ready` endpoint contract — you implement
- G1–G4 gate contracts — your tests hook in

### Contract OUT · To reviewers (and future you)

- Live demo URLs (HF Space always-on · Azure ephemeral per ADR-0013)
- Three demo-fails branches demonstrable on demand
- Full Langfuse trace history showing instrumentation across all pillars

---

## § 06 · Step-by-Step Implementation Guidance

### Step 1 · Local stack up · verify prior blocks

```bash
cd project-00-ground-zero
docker compose up -d
curl http://localhost:3000         # Langfuse UI
curl http://localhost:11434/api/tags  # Ollama
psql -h localhost -p 5433 -U rag -d rag -c '\dt'  # pgvector
```

Pull an Ollama model for local mode:
```bash
docker exec -it project-00-ground-zero-ollama-1 ollama pull llama3.2:3b
docker exec -it project-00-ground-zero-ollama-1 ollama pull nomic-embed-text
```

### Step 2 · Author `config.py` and `models/`

Pydantic Settings-based config · reads `.env` locally · reads Key Vault in Azure. Wrappers for AzureOpenAI and Ollama with identical interface (so calling code doesn't care about MODE).

### Step 3 · RAG · ingestion + retrieval + generation

Ingest the NIST PDF. Verify against local pgvector first · then add Azure AI Search path behind `MODE` switch. Generation prompt with citation format.

Run standalone:
```bash
uv run python -m src.rag.ingest data/nist-ai-rmf.pdf
uv run python -m src.rag.retrieve "What is the Govern function of the AI RMF?"
```

### Step 4 · Agent · LangGraph state machine

Author the 4-node graph. Test with and without HITL interrupts. Verify traces appear in Langfuse.

### Step 5 · Multi-agent · MCP

Author Retriever Specialist as MCP server · Supervisor as MCP client. Run specialist in separate terminal locally · verify Supervisor connects.

### Step 6 · Fine-tune scaffold

Author YAML pipeline + registration script. Register a placeholder model entry in local dev · confirm pattern works. Actual Azure ML Pipeline submission gated to Wave 4.

### Step 7 · Safety stack

Content Safety client setup (uses MI in Azure · local mode skips or uses Azure endpoint from your personal free tier). NeMo rails. Presidio redactor. Wire input gate → generation → output gate.

### Step 8 · Observability

Langfuse callback on LangChain/LangGraph. Cost middleware in FastAPI. App Insights OpenTelemetry.

### Step 9 · Streamlit UI

Three tabs. Wire each to the corresponding pillar. Test interrupts on Agent tab.

### Step 10 · Tests · all 7 tiers

Author at least one real test per tier. Wire to pytest markers:
```python
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit", "smoke", "functional", "guardrail",
    "responsible_ai", "red_team", "eval"
]
```

Run each tier:
```bash
uv run pytest tests/unit -m unit
uv run pytest tests/responsible-ai -m responsible_ai
# ... etc
```

### Step 11 · Demo-fails branches

From clean main:
```bash
# Branch 1
git checkout -b demo-fails-g1
# Introduce type error in src/rag/generate.py
echo "def bad_func() -> int: return 'string'" >> src/rag/generate.py
git add -A && git commit -m "demo: intentional type error to demonstrate G1 gate"
git push -u origin demo-fails-g1
# Do NOT merge · branch lives permanently

git checkout main
# Branch 2
git checkout -b demo-fails-guardrail
# Bypass input gate in src/main.py
# ... (sed out the line calling input_gate)
git add -A && git commit -m "demo: bypass content safety to demonstrate G4 Guardrail gate"
git push -u origin demo-fails-guardrail

git checkout main
# Branch 3
git checkout -b demo-regresses-eval
# Swap retrieval to random vectors in src/rag/retrieve.py
git add -A && git commit -m "demo: retrieval regression to demonstrate G4 Eval Regression gate"
git push -u origin demo-regresses-eval

git checkout main
```

On each branch: file a PR against main to surface the failing CI · label PR `demo-fails` · **do NOT merge**.

### Step 12 · Deploy to all 4 targets

```bash
./scripts/deploy.sh --target=local  # docker compose up with hello-ai built
./scripts/deploy.sh --target=git    # triggers CI
./scripts/deploy.sh --target=hf     # pushes src/ to HF Space
# Azure is gated to Wave 4 · test with --what-if
./scripts/deploy.sh --target=azure --what-if
```

### Step 13 · Runbook §§ 13–15

Author with screenshots of each pillar working · link to demo-fails PRs · link to HF Space.

### Step 14 · Self-test

- [ ] `docker compose up` includes running Hello AI · Streamlit accessible on 8501
- [ ] 3 tabs in Streamlit · each pillar functional in local mode
- [ ] RAG returns answer with citation · citation verifiable against corpus
- [ ] Agent graph renders · HITL interrupt pauses execution
- [ ] Multi-agent: Supervisor calls Retriever Specialist via MCP · response combines both
- [ ] Fine-tune scaffold: pipeline.yml valid · register_model.py runs standalone
- [ ] Input gate rejects known prompt injection test fixture
- [ ] Output gate redacts PII from synthetic test response
- [ ] Langfuse shows traces for RAG · Agent · Multi-Agent with tags
- [ ] Cost middleware populates `request_cost_usd` metric
- [ ] All 7 test tiers run with at least one real test each · all pass on main
- [ ] Three `demo-fails-*` branches exist on remote · PRs filed against main · CI red
- [ ] 4-target deploy: local works · git triggers CI · HF Space syncs · Azure `--what-if` passes
- [ ] Runbook §§ 13–15 authored

---

## § 07 · Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| E-01 | RAG returns cited answer against NIST corpus | UI screenshot + trace |
| E-02 | Citations clickable · source text verifiable | UI walkthrough |
| E-03 | LangGraph agent renders 4-node graph · HITL interrupt working | Langfuse trace + UI |
| E-04 | Multi-agent uses MCP protocol (not direct function calls) | Code inspection + trace |
| E-05 | Fine-tune scaffold has valid Azure ML Pipeline YAML + Model Registry script | Files + registry entry |
| E-06 | Content Safety input gate active · blocks prompt injection | Test run |
| E-07 | Presidio PII redaction active on output | Test run with PII input |
| E-08 | NeMo Guardrails rails configured | Config file |
| E-09 | Langfuse traces every pillar with structured tags | Langfuse UI |
| E-10 | Cost middleware writes USD to every trace | Langfuse trace |
| E-11 | Streamlit UI has 3 tabs · all working locally | UI walkthrough |
| E-12 | All 7 test tiers implemented with real assertions | Pytest output per tier |
| E-13 | 3 `demo-fails-*` branches exist · PRs filed · CI red on each | Branch + PR list |
| E-14 | 4-target deploy completes successfully (Azure may be `--what-if` until Wave 4) | Ledger + target URLs |
| E-15 | Langfuse Azure deployment accessible (deferred to Wave 4 for actual deploy) | Deploy log |
| E-16 | Runbook §§ 13–15 authored with screenshots | File read |
| E-17 | No direct function calls bypassing safety stack | Code audit |
| E-18 | Semantic Kernel planner runs · Langfuse trace shows `planner=semantic-kernel` tag | Trace URL |
| E-19 | Cosmos DB conversation memory · multi-turn context preserved · visible in Streamlit Memory tab | UI walkthrough |
| E-20 | Azure Document Intelligence ingests sample form · structured extraction visible in RAG tab toggle | UI walkthrough |
| E-21 | LlamaIndex ingestion path produces `hello-ai-rag-llamaindex` index · 3-way retrieval toggle works in UI | UI walkthrough + index list |
| E-22 | ColPali processes 2-3 pages · vision-retrieval surfaces table/figure structure that text retrieval misses | UI walkthrough with side-by-side comparison |
| E-23 | Azure Functions cost-aggregator Function App deployed · hourly cron firing · rollup visible in Streamlit sidebar | Deploy log + UI |
| E-24 | ALLaM endpoint deployable · Arabic query renders bilingual response · groundedness fires on Arabic path | Screenshot · trace URL |

---

## § 08 · Review Rubric (Architect's checks)

1. Clone fresh · `docker compose up` · `streamlit run src/ui/streamlit_app.py` · test all 3 tabs work within 5 minutes
2. Submit known-bad prompt injection payload · verify UI shows rejection · verify Langfuse trace labeled `gate_result=fail`
3. Run agent with a compliance-flagged question · verify HITL interrupt fires · resume via UI button
4. Run multi-agent with Retriever running · kill specialist process · verify graceful fallback with warning
5. Inspect fine-tune pipeline.yml · verify Azure ML Pipeline schema valid (Azure ML SDK validator)
6. Open each demo-fails-* PR · verify CI red · verify failure message is clear and educational
7. Run `pytest tests/ -v` · verify all tiers run · no flakes
8. Check Langfuse trace tags — `pillar`, `mode`, `gate_result` all populated
9. Verify no API keys in repo (gitleaks pre-commit)
10. Read runbook § 15 cold · walk through the demo-fails narrative mentally · does it land?

---

## § 09 · Risks & Your Mitigations

| Risk | Mitigation |
|---|---|
| RAGAS eval requires an LLM judge · costs tokens · introduces nondeterminism | Cache golden-set results · use GPT-4o-mini as judge (cheaper) · tolerance bands ±5% on thresholds |
| MCP SDK churn · protocol still evolving | Pin SDK version · document in `pyproject.toml` · note in runbook that MCP may rev |
| Content Safety Groundedness API regional availability | Verify Sweden Central supports it · fallback to custom groundedness check using embedding similarity |
| NeMo Guardrails can be verbose in traces | Configure at `verbose=False` in production · keep DEBUG for local |
| Streamlit session state + HITL interrupt state conflicts | Use LangGraph checkpoint serialization · Streamlit session only holds resume tokens |
| Demo-fails branches accidentally merged | Branch protection on each demo-fails branch · README banner says "DO NOT MERGE" |
| HF Space 16GB disk limit · NIST PDF embeddings could bloat | Store embeddings as int8 quantized · or use smaller embedding dims (truncate 1536 → 512) |
| Fine-tune pipeline YAML becomes outdated vs Azure ML SDK | Pin SDK version · runbook notes validation command |

---

## § 10 · Escalation Contract

Same format as prior Briefs.

---

## § 11 · Expected Output Format

1. **Repository state** · `src/` fully populated · three demo-fails branches pushed
2. **4 deploy URLs** · Local (`localhost:8501`) · Git (repo) · HF Space URL · Azure (`--what-if` output until Wave 4)
3. **Langfuse traces** · one example URL per pillar (RAG · Agent · Multi-Agent)
4. **Three demo-fails PR URLs** with failing CI badges visible
5. **Test run output** · `pytest tests/ -v --tb=short` showing all 7 tiers pass on main
6. **Self-assessment** · 17 acceptance criteria with evidence
7. **Open escalations** (if any)

---

## § 12 · Closure

Brief E closes when Architect signs off. On closure:
- Project Ground Zero is functionally complete · enters Wave 4 validation sprint
- DoD criterion 4 (Hello AI deployed to 4 targets) achievable when Azure activates
- DoD criterion 5 (all 7 test tiers) achievable · real tests exist
- DoD criterion 10 (fresh-start reproduction < 20min) is the remaining platform-proof
- Project 1 can be drafted · Ground Zero substrate proven

---

**End of Builder Brief · E · Hello AI Payload**

`Dammam · 2026-04-24 · Rev 1.2 · expanded stack coverage · 97% total`
