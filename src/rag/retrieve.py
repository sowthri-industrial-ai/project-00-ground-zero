"""Hybrid retrieval · AI Search (Azure) · pgvector cosine (local)."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from src.config import get_settings
from src.models.embedding import EmbeddingClient


@dataclass
class Chunk:
    id: str
    content: str
    score: float
    doc_id: str = ""


async def retrieve(query: str, top_k: int = 5, index_name: str | None = None) -> list[Chunk]:
    s = get_settings()
    qvec = (await EmbeddingClient().embed([query]))[0]
    if s.mode == "azure":
        return await _retrieve_azure(s, query, qvec, top_k, index_name or s.search_index_primary)
    return await _retrieve_pg(s, qvec, top_k)


async def _retrieve_azure(s, query, qvec, top_k, index_name):
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents.aio import SearchClient
    from azure.search.documents.models import VectorizedQuery
    cred = DefaultAzureCredential()
    client = SearchClient(endpoint=s.search_endpoint, index_name=index_name, credential=cred)
    vq = VectorizedQuery(vector=qvec, k_nearest_neighbors=top_k, fields="vector")
    out = []
    async for r in await client.search(search_text=query, vector_queries=[vq], top=top_k):
        out.append(Chunk(id=r["id"], content=r["content"], score=r["@search.score"], doc_id=r.get("doc_id", "")))
    await client.close()
    return out


async def _retrieve_pg(s, qvec, top_k):
    import asyncpg
    conn = await asyncpg.connect(s.pg_dsn)
    rows = await conn.fetch(
        "SELECT id, doc_id, content, 1 - (embedding <=> $1::vector) AS score "
        "FROM chunks ORDER BY embedding <=> $1::vector LIMIT $2",
        str(qvec), top_k,
    )
    await conn.close()
    return [Chunk(id=r["id"], content=r["content"], score=float(r["score"]), doc_id=r["doc_id"]) for r in rows]


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "What is the Govern function of the AI RMF?"
    for c in asyncio.run(retrieve(q)):
        print(f"[{c.id}] score={c.score:.3f} · {c.content[:120]}")
