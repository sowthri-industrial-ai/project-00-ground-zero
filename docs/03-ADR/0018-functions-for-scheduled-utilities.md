# ADR-0018 · Azure Functions for scheduled utilities

**Status**: Accepted · 2026-04-24

## Context
Request/response inference lives on Container Apps (ADR-0003). Scheduled/event-driven jobs are a different pattern.

## Decision
Azure Functions (Consumption plan) for scheduled crons, webhook receivers, queue-triggered processors. Ground Zero uses one: hourly cost aggregator Langfuse → Cosmos.

## Consequences
- Consumption 1M free executions/month · hourly cron = 720/month · $0
- Separate deployment target · separate Bicep module
- Separation of concerns: inference vs utility workloads
