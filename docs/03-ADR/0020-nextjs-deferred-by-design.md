# ADR-0020 · Next.js deferred to flagship · Streamlit sufficient for Ground Zero

**Status**: Accepted · 2026-04-24

## Context
Charter § 04 commits to Streamlit for Ground Zero. Reviewers may ask "where's the React?" — this ADR documents why that's the right answer.

## Decision
No Next.js in Ground Zero. Streamlit is functionally sufficient for Hello AI demo (tabs, metric badges, session state, HITL buttons). Flagship project (Project 3) is where custom React UX earns its cost.

## Consequences
- Skipping parallel Next.js + Streamlit avoids architecture theater
- Review narrative: "Next.js lands where UX polish is the product"
- Project 3 brief calls Next.js the primary UI layer
