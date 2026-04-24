# ADR-0015 · Docling for text-heavy · Document Intelligence for structure-heavy

**Status**: Accepted · 2026-04-24

## Context
PDF ingestion has two dominant patterns: layout-preserving text extraction (Docling) and structure-aware semantic extraction (Azure Document Intelligence). NOT competing — they serve different document classes.

## Decision
- **Docling**: primary for narrative/text-heavy PDFs (NIST AI RMF is this class)
- **Document Intelligence**: when tables/forms/KV-pairs carry semantic weight (sample form)
- Picked per document class at ingestion time

## Consequences
- Two ingestion modules · two AI Search indices
- UI toggle surfaces the trade-off for reviewers
