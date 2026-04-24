"""Tier 3 · Functional · RAG returns cited answer, citation present in corpus."""
import asyncio
import re
import pytest


@pytest.mark.functional
def test_rag_end_to_end_with_citation(monkeypatch):
    async def fake_retrieve(q, top_k=5, index_name=None):
        from src.rag.retrieve import Chunk
        return [Chunk(id="abc123", content="The Govern function establishes risk management culture.", score=0.9, doc_id="nist")]

    async def fake_complete(self, messages, **kw):
        return {"content": "The Govern function establishes a risk management culture [abc123].",
                "tokens_in": 10, "tokens_out": 12, "model": "gpt-4o-mini"}

    monkeypatch.setattr("src.rag.generate.retrieve", fake_retrieve)
    monkeypatch.setattr("src.models.chat.ChatClient.complete", fake_complete)

    from src.rag.generate import generate
    result = asyncio.run(generate("What is Govern?"))
    assert re.search(r"\[[\w-]+\]", result["answer"])
    assert any(c["id"] in result["answer"] for c in result["chunks"])
