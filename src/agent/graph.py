"""LangGraph 4-node agent · plan → rag → reflect → [hitl] → respond."""
from __future__ import annotations
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.agent.hitl import is_risky
from src.agent.memory import ConversationMemory
from src.agent.reflection import score_groundedness
from src.agent.tools import rag_retrieve
from src.models.chat import ChatClient


class AgentState(TypedDict, total=False):
    query: str
    session_id: str
    plan_intent: str
    chunks: list[dict]
    draft: str
    groundedness: float
    reflect_count: int
    final: str
    risky: bool


async def plan_node(state):
    messages = [
        {"role": "system", "content": "Classify intent: 'rag' or 'direct'. Return only the word."},
        {"role": "user", "content": state["query"]},
    ]
    r = await ChatClient().complete(messages, temperature=0.0)
    return {"plan_intent": r["content"].strip().lower(), "risky": is_risky(state["query"])}


async def rag_tool_node(state):
    chunks = await rag_retrieve.ainvoke({"query": state["query"], "top_k": 5})
    return {"chunks": chunks}


async def reflect_node(state):
    draft = state.get("draft", "")
    if not draft:
        ctx = "\n".join(f"[{c['id']}] {c['content']}" for c in state.get("chunks", []))
        messages = [
            {"role": "system", "content": "Answer using ONLY the chunks. Cite as [chunk-id]."},
            {"role": "user", "content": f"Chunks:\n{ctx}\n\nQ: {state['query']}"},
        ]
        r = await ChatClient().complete(messages, temperature=0.2)
        draft = r["content"]
    score = await score_groundedness(draft, state.get("chunks", []))
    return {"draft": draft, "groundedness": score, "reflect_count": state.get("reflect_count", 0) + 1}


async def hitl_node(state):
    decision = interrupt({"reason": "risky_query", "query": state["query"], "draft": state.get("draft", "")})
    if decision == "approve":
        return {}
    return {"final": "Response withheld pending human review."}


async def respond_node(state):
    if state.get("final"):
        return {}
    return {"final": state.get("draft", "")}


def route_after_reflect(state):
    if state.get("groundedness", 1.0) < 0.7 and state.get("reflect_count", 0) < 2:
        return "use_rag_tool"
    if state.get("risky"):
        return "hitl_checkpoint"
    return "respond"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("plan", plan_node)
    g.add_node("use_rag_tool", rag_tool_node)
    g.add_node("reflect", reflect_node)
    g.add_node("hitl_checkpoint", hitl_node)
    g.add_node("respond", respond_node)
    g.add_edge(START, "plan")
    g.add_edge("plan", "use_rag_tool")
    g.add_edge("use_rag_tool", "reflect")
    g.add_conditional_edges("reflect", route_after_reflect,
                            {"use_rag_tool": "use_rag_tool", "hitl_checkpoint": "hitl_checkpoint", "respond": "respond"})
    g.add_edge("hitl_checkpoint", "respond")
    g.add_edge("respond", END)
    return g.compile()


async def run_agent(query: str, session_id: str = "default") -> dict:
    mem = ConversationMemory()
    history = await mem.load(session_id, limit=5)
    graph = build_graph()
    result = await graph.ainvoke({"query": query, "session_id": session_id, "reflect_count": 0})
    await mem.save(session_id, "user", query)
    await mem.save(session_id, "assistant", result.get("final", ""))
    return {"final": result.get("final", ""), "groundedness": result.get("groundedness", 0.0),
            "chunks": result.get("chunks", []), "reflect_count": result.get("reflect_count", 0),
            "risky": result.get("risky", False), "history": history}
