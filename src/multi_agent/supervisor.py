"""Multi-agent supervisor · routes via MCP · synthesises final answer."""
from __future__ import annotations
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from src.models.chat import ChatClient
from src.multi_agent.mcp_client import call_retriever


class MAState(TypedDict, total=False):
    query: str
    needs_retrieval: bool
    specialist_result: str
    used_fallback: bool
    final: str


async def route_node(state):
    messages = [
        {"role": "system", "content": "Answer yes/no: does this query require document retrieval?"},
        {"role": "user", "content": state["query"]},
    ]
    r = await ChatClient().complete(messages, temperature=0.0)
    return {"needs_retrieval": r["content"].strip().lower().startswith("y")}


async def specialist_node(state):
    payload, fallback = await call_retriever(state["query"])
    return {"specialist_result": payload, "used_fallback": fallback}


async def synthesise_node(state):
    context = state.get("specialist_result", "")
    messages = [
        {"role": "system", "content": "Synthesise a grounded answer. Cite as [chunk-id]."},
        {"role": "user", "content": f"Specialist output:\n{context}\n\nQuestion: {state['query']}"},
    ]
    r = await ChatClient().complete(messages, temperature=0.2)
    return {"final": r["content"]}


def route_after_plan(state):
    return "specialist" if state.get("needs_retrieval") else "synthesise"


def build_ma_graph():
    g = StateGraph(MAState)
    g.add_node("route", route_node)
    g.add_node("specialist", specialist_node)
    g.add_node("synthesise", synthesise_node)
    g.add_edge(START, "route")
    g.add_conditional_edges("route", route_after_plan, {"specialist": "specialist", "synthesise": "synthesise"})
    g.add_edge("specialist", "synthesise")
    g.add_edge("synthesise", END)
    return g.compile()


async def run_multi_agent(query: str) -> dict:
    from src.multi_agent.sk_planner import plan as sk_plan
    sk_result = await sk_plan(query)
    graph = build_ma_graph()
    result = await graph.ainvoke({"query": query})
    return {**result, "sk_plan": sk_result}
