"""Retriever specialist · MCP server · stdio transport."""
from __future__ import annotations
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from src.rag.retrieve import retrieve

server = Server("retriever-specialist")


@server.list_tools()
async def list_tools():
    return [Tool(
        name="retrieve_from_rag",
        description="Retrieve top-k grounded chunks from the NIST AI RMF index.",
        inputSchema={
            "type": "object",
            "properties": {"query": {"type": "string"}, "top_k": {"type": "integer", "default": 5}},
            "required": ["query"],
        },
    )]


@server.call_tool()
async def call_tool(name, arguments):
    if name != "retrieve_from_rag":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    chunks = await retrieve(arguments["query"], top_k=arguments.get("top_k", 5))
    return [TextContent(type="text", text="\n".join(f"[{c.id}] ({c.score:.2f}) {c.content}" for c in chunks))]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
