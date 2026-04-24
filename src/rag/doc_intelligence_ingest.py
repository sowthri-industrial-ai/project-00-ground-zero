"""Azure Document Intelligence alternative ingest for structure-heavy PDFs."""
from __future__ import annotations
import asyncio
from pathlib import Path
from src.config import get_settings
from src.models.embedding import EmbeddingClient


async def ingest_form(pdf_path: str, doc_id: str | None = None) -> int:
    s = get_settings()
    path = Path(pdf_path)
    doc_id = doc_id or path.stem
    if s.mode == "azure":
        blocks = await _extract_azure(s, path)
    else:
        blocks = await _extract_local_fallback(path)
    texts = [b["text"] for b in blocks]
    vecs = await EmbeddingClient().embed(texts)
    return await _index(s, doc_id, blocks, vecs)


async def _extract_azure(s, path):
    from azure.identity.aio import DefaultAzureCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    cred = DefaultAzureCredential()
    client = DocumentIntelligenceClient(endpoint=s.docintel_endpoint, credential=cred)
    with open(path, "rb") as f:
        poller = await client.begin_analyze_document("prebuilt-layout", body=f)
    result = await poller.result()
    blocks = []
    for t in (result.tables or []):
        blocks.append({"type": "table", "text": _table_to_text(t)})
    for kv in (result.key_value_pairs or []):
        blocks.append({"type": "kv", "text": f"{kv.key.content}: {kv.value.content if kv.value else ''}"})
    for p in (result.paragraphs or []):
        blocks.append({"type": "para", "text": p.content})
    await client.close()
    return blocks


def _table_to_text(t):
    rows = {}
    for cell in t.cells:
        rows.setdefault(cell.row_index, {})[cell.column_index] = cell.content
    return "\n".join(" | ".join(rows[r].get(c, "") for c in sorted(rows[r])) for r in sorted(rows))


async def _extract_local_fallback(path):
    from pypdf import PdfReader
    return [{"type": "para", "text": (p.extract_text() or "").strip()} for p in PdfReader(str(path)).pages]


async def _index(s, doc_id, blocks, vectors):
    import asyncpg
    conn = await asyncpg.connect(s.pg_dsn)
    await conn.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE IF NOT EXISTS form_chunks (
            id SERIAL PRIMARY KEY, doc_id TEXT, block_type TEXT, content TEXT, embedding vector(768)
        );
    """)
    for b, v in zip(blocks, vectors):
        await conn.execute("INSERT INTO form_chunks(doc_id, block_type, content, embedding) VALUES($1,$2,$3,$4)",
                           doc_id, b["type"], b["text"], str(v))
    await conn.close()
    return len(blocks)


if __name__ == "__main__":
    import sys
    n = asyncio.run(ingest_form(sys.argv[1] if len(sys.argv) > 1 else "data/sample-form.pdf"))
    print(f"Ingested {n} blocks")
