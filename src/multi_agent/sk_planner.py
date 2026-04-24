"""Semantic Kernel planner · one-step before LangGraph Supervisor."""
from __future__ import annotations
from typing import Any


async def plan(query: str) -> dict[str, Any]:
    try:
        from semantic_kernel import Kernel
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        from semantic_kernel.functions import kernel_function
        from src.config import get_settings

        s = get_settings()
        kernel = Kernel()
        if s.mode == "azure":
            kernel.add_service(AzureChatCompletion(
                deployment_name=s.aoai_chat_deployment, endpoint=s.aoai_endpoint,
                api_version=s.aoai_api_version,
            ))

        class PlannerPlugin:
            @kernel_function(name="decompose_query", description="Split query into sub-tasks")
            async def decompose_query(self, query: str) -> str:
                return f"[sub-task] {query}"

            @kernel_function(name="classify_intent", description="Classify as rag|direct")
            async def classify_intent(self, query: str) -> str:
                return "rag"

        kernel.add_plugin(PlannerPlugin(), plugin_name="planner")
        decomposed = await kernel.invoke(plugin_name="planner", function_name="decompose_query", query=query)
        intent = await kernel.invoke(plugin_name="planner", function_name="classify_intent", query=query)
        return {"planner": "semantic-kernel", "sub_tasks": [str(decomposed)], "intent": str(intent)}
    except ImportError:
        return {"planner": "semantic-kernel", "sub_tasks": [query], "intent": "rag", "note": "SK not installed"}
