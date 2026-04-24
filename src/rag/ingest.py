"""NIST AI RMF ingestion · Docling parse · 512-token chunks · embed · index."""
from __future__ import annotations
import asyncio
import hashlib
from pathlib import Path
import tiktoken
from src.config import get_settings
from src.models.embedding import EmbeddingClient

CHUNK_TOKENS = 512
CHUNK_OVERLAP = 50


def chunk_text(text: str, max_tokens: int = CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    ids = enc.encode(text)
    chunks: list[str] = []
    i = 0
    while i < len(ids):
        window = ids[i:i + max_tokens]
        chunks.append(enc.decode(window))
        if i + max_tokens >= len(ids):
            break
        i += max_tokens - overlap
    return chunks


def _chunk_id(doc_id: str, idx: int, text: str) -> str:
    return hashlib.sha1(f"{doc_id}:{idx}:{text[:64]}".encode()).hexdigest()[:16]


async def parse_pdf(path: Path) -> str:
    try:
        from docling.document_converter import DocumentConverter
        return DocumentConverter().convert(str(path)).document.export_to_markdown()
    except ImportError:
        from pypdf import PdfReader
        return "\n\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)


async def ingest(pdf_path: str, doc_id: str | None = None) -> int:
    s = get_settings()
    path = Path(pdf_path)
    doc_id = doc_id or path.stem
    text = await parse_pdf(path)
    chunks = chunk_text(text)
    vectors = await EmbeddingClient().embed(chunks)
    if s.mode == "azure":
        return await _index_azure(s, doc_id, chunks, vectors)
    return await _index_pgvector(s, doc_id, chunks, vectors)


async def _index_azure(s, doc_id, chunks, vectors):
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents.aio import SearchClient
    cred = DefaultAzureCredential()
    client = SearchClient(endpoint=s.search_endpoint, index_name=s.search_index_primary, credential=cred)
    docs = [{"id": _chunk_id(doc_id, i, t), "doc_id": doc_id, "chunk_id": i, "content": t, "vector": v}
            for i, (t, v) in enumerate(zip(chunks, vectors))]
    await client.upload_documents(documents=docs)
    await client.close()
    return len(docs)


async def _index_pgvector(s, doc_id, chunks, vectors):
    import asyncpg
    conn = await asyncpg.connect(s.pg_dsn)
    await conn.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY, doc_id TEXT, chunk_id INT, content TEXT, embedding vector(768)
        );
    """)
    for i, (text, vec) in enumerate(zip(chunks, vectors)):
        cid = _chunk_id(doc_id, i, text)
        await conn.execute(
            "INSERT INTO chunks(id, doc_id, chunk_id, content, embedding) VALUES ($1,$2,$3,$4,$5) ON CONFLICT(id) DO NOTHING",
            cid, doc_id, i, text, str(vec),
        )
    await conn.close()
    return len(chunks)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/nist-ai-rmf.pdf"
    print(f"Ingested {asyncio.run(ingest(path))} chunks from {path}")
