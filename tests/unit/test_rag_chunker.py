"""Tier 1 · Unit · chunker respects 512-token cap."""
import pytest
from src.rag.ingest import chunk_text, CHUNK_TOKENS
import tiktoken


@pytest.mark.unit
def test_rag_chunker_respects_token_cap():
    text = " ".join(["word"] * 5000)
    chunks = chunk_text(text)
    enc = tiktoken.get_encoding("cl100k_base")
    assert chunks
    for c in chunks:
        assert len(enc.encode(c)) <= CHUNK_TOKENS
