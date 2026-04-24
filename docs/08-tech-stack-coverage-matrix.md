# Tech Stack Coverage Matrix

```
Document  · tech-stack-coverage-matrix
Revision  · 2.0
Date      · 2026-04-24
Owner     · Sowthri (Architect)
Purpose   · Explicit sequencing of tech stack across Ground Zero + Projects 1+
Status    · Companion to Charter-00 Rev 1.3
```

---

## Purpose

The GenAI Architect Portfolio commits to a specific tech stack as its architectural surface. This document makes explicit which components each project exercises — so a reviewer sees *deliberate sequencing*, not *accidental gaps*.

Rev 2.0 follows a scope re-evaluation: with the Ground Zero substrate already built, most deferred components proved lightweight to pull forward. Only **Next.js** stays deferred — not for effort reasons but as a principled architecture decision (ADR-0020).

---

## Coverage Matrix

| Stack Component | Ground Zero | Project 1 · Industrial RAG | Project 2 · Agentic OT/IT | Project 3 · Flagship |
|---|:---:|:---:|:---:|:---:|
| **Agent Orchestration** | | | | |
| LangGraph | ✅ primary | ✅ primary | ✅ primary | ✅ primary |
| Semantic Kernel | ✅ Brief E · Deliverable 4a | ⚪ optional | ✅ planner-heavy | ⚪ optional |
| MCP (Model Context Protocol) | ✅ Brief E · Supervisor↔Specialist | ✅ multi-server | ✅ heavy · OT/IT bridges | ✅ |
| **Foundation Models** | | | | |
| Azure OpenAI GPT-4o | ✅ reasoning demos | ✅ reasoning over docs | ✅ planning | ✅ |
| Azure OpenAI GPT-4o-mini | ✅ workhorse | ✅ workhorse | ✅ workhorse | ✅ workhorse |
| text-embedding-3-small | ✅ RAG | ✅ RAG | ⚪ | ⚪ |
| ALLaM (Azure AI Foundry) | ✅ **Brief E · Deliverable 4g · thin demo** | ⚪ | ⚪ | ✅ Arabic-primary use case |
| **Retrieval & Storage** | | | | |
| Azure AI Search (hybrid) | ✅ Free tier · 2 indexes | ✅ Basic · semantic ranker | ⚪ | ✅ |
| pgvector | ✅ local mode + ColPali embeddings | ⚪ | ⚪ | ⚪ |
| Cosmos DB | ✅ Brief E · conversation memory + cost rollups | ✅ document store | ✅ event store | ✅ |
| Azure Blob | ✅ free tier | ✅ corpus storage | ⚪ | ✅ |
| **Document Processing** | | | | |
| Docling | ✅ PDF parse | ⚪ fallback | ⚪ | ⚪ |
| Azure Document Intelligence | ✅ Brief E · Deliverable 4c · form extraction | ✅ heavy · invoices, forms | ⚪ | ⚪ |
| LlamaIndex | ✅ **Brief E · Deliverable 4d · alternative ingest** | ✅ routers · sub-question synthesis | ⚪ | ⚪ |
| ColPali | ✅ **Brief E · Deliverable 4e · 2-3 structure-rich pages** | ✅ P&IDs · equipment datasheets | ⚪ | ⚪ |
| **Safety & Guardrails** | | | | |
| NeMo Guardrails | ✅ Brief E | ✅ | ✅ | ✅ |
| Presidio (PII) | ✅ Brief E | ✅ | ✅ | ✅ |
| Azure Content Safety | ✅ Briefs B + E · Prompt Shields + groundedness | ✅ | ✅ | ✅ |
| **Evaluation & Observability** | | | | |
| RAGAS | ✅ Brief E · Tier 7 | ✅ | ⚪ | ✅ |
| DeepEval | ✅ Brief E · Tier 5 | ✅ | ✅ | ✅ |
| Giskard | ✅ Brief E · Tier 5 bias probes | ✅ | ✅ | ✅ |
| Langfuse | ✅ Briefs B + E | ✅ | ✅ | ✅ |
| Application Insights | ✅ Briefs B + E | ✅ | ✅ | ✅ |
| **Security Testing** | | | | |
| Garak | ✅ Brief C weekly workflow | ✅ | ✅ | ✅ |
| PyRIT | ✅ Brief C + E | ✅ | ✅ | ✅ |
| **Infrastructure** | | | | |
| Bicep | ✅ primary IaC | ✅ | ✅ | ✅ |
| Terraform | ✅ mirror | ⚪ | ✅ mirror | ⚪ |
| Azure Container Apps | ✅ Briefs B + E | ✅ | ✅ | ✅ |
| Azure Functions | ✅ **Brief E · Deliverable 4f · hourly cost aggregator** | ⚪ | ✅ heavy · event-driven OT/IT | ⚪ |
| Azure ML Pipeline | ✅ Brief E scaffold (no train) | ⚪ | ⚪ | ✅ fine-tune actually run |
| **Application** | | | | |
| FastAPI | ✅ Brief E | ✅ | ✅ | ✅ |
| Streamlit | ✅ Brief E UI | ✅ | ⚪ | ⚪ |
| Next.js | ⚪ **deferred by design · ADR-0020** | ⚪ | ⚪ | ✅ flagship UI (its correct placement) |
| **Language & Tooling** | | | | |
| Python 3.12 | ✅ all | ✅ | ✅ | ✅ |
| uv (package manager) | ✅ ADR-0009 | ✅ | ✅ | ✅ |
| OIDC federation GitHub↔Entra | ✅ ADR-0002 | ✅ inherited | ✅ inherited | ✅ inherited |

**Legend**: ✅ = actively exercised · ⚪ = not used

---

## Coverage summary by project · Rev 2.0

| Project | Components exercised | % of full stack |
|---|---|---|
| **Ground Zero** (with all amendments) | 29 of 30 | **~97%** |
| **Project 1 · Industrial RAG** (projected) | 23 of 30 | ~77% |
| **Project 2 · Agentic OT/IT** (projected) | 22 of 30 | ~73% |
| **Project 3 · Flagship** (projected) | 25 of 30 | ~83% |

**Cumulative portfolio coverage: 100%** — every committed tech stack component exercised in at least one project, with the 30th (Next.js) deliberately reserved for the flagship where its polished UI purpose fits.

---

## What changed in Rev 2.0

Four components moved from "deferred to Project 1+" → "Ground Zero Brief E":

| Component | Rev 1.0 placement | Rev 2.0 placement | Rationale |
|---|---|---|---|
| LlamaIndex | Project 1 | Brief E · 4d | Substrate built · alternative ingest ~2-3 hr · demonstrates polyglot retrieval without forcing use-case dependency |
| ColPali | Project 1 | Brief E · 4e | CPU inference viable for 2-3 pages · caches embeddings · no GPU cost · pattern portable to Project 1's fuller use case |
| Azure Functions | Project 2 | Brief E · 4f | Consumption plan 1M executions free · cost-aggregator cron is naturally serverless · no Container Apps stretch |
| ALLaM | Project 3 | Brief E · 4g | **Regional signal understated in Rev 1.0** · KSA panels recognize SDAIA + Vision 2030 instantly · ~$3 TCO · 2-3 hr · high-ROI |

One component confirmed deferred:

| Component | Placement | Rationale |
|---|---|---|
| Next.js | Project 3 (flagship) | Violates Charter § 04 Non-Goals · Streamlit sufficient for Hello AI · adding a parallel UI without use-case justification is architecture theater · ADR-0020 documents |

---

## TCO delta

Rev 2.0 additions affect TCO as follows:

| Addition | Incremental spend | Source |
|---|---|---|
| LlamaIndex | $0 | Library · uses existing AOAI tokens |
| ColPali | $0 | Local/HF-hosted model · no Azure compute |
| Azure Functions | $0 | Consumption plan free tier (1M executions/month; usage ~720) |
| ALLaM thin demo | ~$3 | Foundry managed endpoint · 1 hr ephemeral + ~50K tokens · **verify on activation** |
| **Total delta** | **~$3** | |

Ground Zero TCO: $19.63 → **~$22.63** · NFR-04 ceiling $25 · headroom $2.37 · **still PASS**.

See `docs/06-tco.xlsx` · Rev 2.0.

---

## Reviewer narrative · Rev 2.0

When a hiring reviewer asks *"where's X?"* the answer is now almost always *"right here in Ground Zero · specifically Brief E Deliverable 4x"* — with one exception:

> *"Next.js isn't in Ground Zero by design. It's reserved for the flagship project where polished custom UI is the actual purpose. Adding a parallel Next.js UI to Hello AI when Streamlit already works would be architecture theater — the point of Ground Zero is to prove the platform, not to enumerate every framework. The ADR at `docs/03-ADR/0020-nextjs-deferred-by-design.md` documents the reasoning. Next.js lands in Project 3 where flagship-quality React is the point."*

This is a **stronger signal** than "I used every tool in one project." It says: I know when to use what · and equally importantly · I know when NOT to use something.

---

## Change log

### Rev 2.0 · 2026-04-24
- Four components moved from deferred → Ground Zero per substrate-built scope reassessment
- Ground Zero coverage: 27/30 → 29/30 · ~90% → ~97%
- ADRs 0016 (LlamaIndex) · 0017 (ColPali) · 0018 (Functions) · 0019 (ALLaM) · 0020 (Next.js deferred) queued for Brief E authoring
- TCO delta ~$3 · ALLaM endpoint · fits in existing NFR-04 headroom · $22.63 / $25 · PASS
- Brief E rev 1.1 → 1.2

### Rev 1.0 · 2026-04-24
- Initial matrix · companion to Charter-00 Rev 1.2
- Ground Zero coverage ~75% → ~90% via three Brief E amendments (SK · Cosmos · Doc Intelligence)
- Deferrals: LlamaIndex · ColPali · Functions · Next.js · ALLaM

---

`Dammam · 2026-04-24 · Rev 2.0`
