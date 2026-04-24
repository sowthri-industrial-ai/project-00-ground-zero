"""Grounded RAG generation with citation format [chunk-id]."""
from __future__ import annotations
from src.models.chat import ChatClient
from src.rag.retrieve import retrieve

SYSTEM_PROMPT = """You answer questions using ONLY the provided context chunks.
Cite every factual claim inline using the chunk id in square brackets: [chunk-id].
If the context is insufficient, reply exactly: "Insufficient context to answer."
Never invent citations. Never answer from prior knowledge."""


async def generate(query: str, top_k: int = 5, index_name: str | None = None) -> dict:
    chunks = await retrieve(query, top_k=top_k, index_name=index_name)
    if not chunks:
        return {"answer": "No chunks retrieved.", "chunks": [], "tokens_in": 0, "tokens_out": 0}
    context = "\n\n".join(f"[{c.id}] {c.content}" for c in chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    resp = await ChatClient().complete(messages, temperature=0.2)
    return {
        "answer": resp["content"],
        "chunks": [{"id": c.id, "content": c.content, "score": c.score} for c in chunks],
        "tokens_in": resp["tokens_in"], "tokens_out": resp["tokens_out"],
        "model": resp["model"],
    }
