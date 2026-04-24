# ADR-0016 · LlamaIndex ingestion alongside native Azure SDK

**Status**: Accepted · 2026-04-24

## Context
LlamaIndex offers higher-level orchestration abstraction. Native Azure SDK is more primitive but tighter to the service.

## Decision
Keep BOTH paths live. Native Azure SDK primary. LlamaIndex writes to `hello-ai-rag-llamaindex` for side-by-side comparison.

## Consequences
- Ground Zero's single-index simplicity doesn't exercise LlamaIndex differentiators · running it here is coverage signal
- Reviewers can benchmark retrieval identically
- 3-way UI toggle: Native · Docling+AI Search · LlamaIndex
