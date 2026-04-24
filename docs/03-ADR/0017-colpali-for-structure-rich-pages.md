# ADR-0017 · ColPali vision embedding for structure-rich pages

**Status**: Accepted · 2026-04-24

## Context
Text chunking destroys spatial structure of tables/diagrams. For documents where semantic content lives in visual layout, text retrieval systematically misses information.

## Decision
ColPali (patch-level vision embeddings over page images) for 2-3 NIST pages with tables/figures. Index in pgvector. Narrowly scoped — not the full corpus.

## Consequences
- Demonstrates multimodal retrieval pattern on CPU-feasible scale
- Pattern portable to Project 1's P&ID corpus where ColPali becomes primary
- Quantized weights (~1.5GB) on first run · cached · accepted
