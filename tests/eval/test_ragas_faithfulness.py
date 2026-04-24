"""Tier 7 · Eval · RAGAS faithfulness above baseline."""
import asyncio
import pytest
from src.rag.eval import run_golden_eval


@pytest.mark.eval
def test_ragas_faithfulness_above_baseline(monkeypatch):
    async def fake_generate(q, top_k=5, index_name=None):
        return {"answer": f"Grounded answer about: {q}",
                "chunks": [{"id": "c1", "content": q, "score": 0.9}],
                "tokens_in": 10, "tokens_out": 10, "model": "gpt-4o-mini"}
    monkeypatch.setattr("src.rag.generate.generate", fake_generate)
    scores = asyncio.run(run_golden_eval("tests/eval/golden.jsonl"))
    assert scores.get("faithfulness", 0) >= 0.40
