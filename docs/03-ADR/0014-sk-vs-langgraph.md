# ADR-0014 · Semantic Kernel alongside LangGraph

**Status**: Accepted · 2026-04-24
**Relates to**: ADR-0005 (agent framework selection)

## Context
Brief E requires framework polyglot in the agentic layer.

## Decision
LangGraph primary for stateful agent graphs (supervisor routing, reflection loops, HITL interrupts). Semantic Kernel runs ONE planner step before LangGraph's Supervisor when plugin-composition is the natural idiom. SK planner feeds decomposed sub-tasks into LangGraph's initial state.

## Consequences
- Single source-of-truth for agent state remains LangGraph
- SK demonstrates plugin+kernel_function patterns Microsoft-shop reviewers expect
- Langfuse tags distinguish: `planner=semantic-kernel` · `router=langgraph`
- Two framework SDKs in the dependency tree · accepted cost
