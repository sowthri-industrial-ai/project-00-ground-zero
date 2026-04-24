"""MCP client · connects Supervisor to Specialist · fallback if unreachable."""
from __future__ import annotations
import asyncio
import sys
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def specialist_session():
    params = StdioServerParameters(command=sys.executable, args=["-m", "src.multi_agent.retriever_specialist"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_retriever(query: str, top_k: int = 5) -> tuple[str, bool]:
    try:
        async with specialist_session() as s:
            result = await asyncio.wait_for(
                s.call_tool("retrieve_from_rag", {"query": query, "top_k": top_k}), timeout=15.0)
            return result.content[0].text, False
    except Exception as e:
        from src.rag.retrieve import retrieve
        chunks = await retrieve(query, top_k=top_k)
        return (f"[MCP fallback · {type(e).__name__}]\n" +
                "\n".join(f"[{c.id}] ({c.score:.2f}) {c.content}" for c in chunks)), True
