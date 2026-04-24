"""RAG-as-tool for LangGraph."""
from __future__ import annotations
from langchain_core.tools import tool
from src.rag.retrieve import retrieve


@tool
async def rag_retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve top-k grounded chunks from the NIST AI RMF index."""
    chunks = await retrieve(query, top_k=top_k)
    return [{"id": c.id, "content": c.content, "score": c.score} for c in chunks]
