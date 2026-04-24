"""Cosmos DB conversation memory · SQLite fallback for local."""
from __future__ import annotations
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any
from src.config import get_settings

SQLITE_PATH = ".memory.sqlite"


class ConversationMemory:
    def __init__(self) -> None:
        self.s = get_settings()
        if self.s.mode == "local":
            self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(SQLITE_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations(
                id TEXT PRIMARY KEY, session_id TEXT, timestamp TEXT, role TEXT, content TEXT,
                trace_id TEXT, tokens_in INT, tokens_out INT, cost_usd REAL
            )
        """)
        conn.commit()
        conn.close()

    async def load(self, session_id: str, limit: int = 10) -> list[dict]:
        if self.s.mode == "azure":
            return await self._load_cosmos(session_id, limit)
        return self._load_sqlite(session_id, limit)

    async def save(self, session_id, role, content, trace_id="", tokens_in=0, tokens_out=0, cost_usd=0.0):
        rec = {
            "id": str(uuid.uuid4()), "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role, "content": content, "trace_id": trace_id,
            "tokens": {"in": tokens_in, "out": tokens_out}, "cost_usd": cost_usd,
        }
        if self.s.mode == "azure":
            await self._save_cosmos(rec)
        else:
            self._save_sqlite(rec)

    def _load_sqlite(self, session_id, limit):
        conn = sqlite3.connect(SQLITE_PATH)
        rows = conn.execute(
            "SELECT role, content, timestamp FROM conversations WHERE session_id=? "
            "ORDER BY timestamp DESC LIMIT ?", (session_id, limit)
        ).fetchall()
        conn.close()
        return [{"role": r, "content": c, "timestamp": t} for r, c, t in reversed(rows)]

    def _save_sqlite(self, rec):
        conn = sqlite3.connect(SQLITE_PATH)
        conn.execute(
            "INSERT INTO conversations VALUES(?,?,?,?,?,?,?,?,?)",
            (rec["id"], rec["session_id"], rec["timestamp"], rec["role"], rec["content"],
             rec["trace_id"], rec["tokens"]["in"], rec["tokens"]["out"], rec["cost_usd"]),
        )
        conn.commit()
        conn.close()

    async def _load_cosmos(self, session_id, limit):
        from azure.cosmos.aio import CosmosClient
        from azure.identity.aio import DefaultAzureCredential
        cred = DefaultAzureCredential()
        client = CosmosClient(self.s.cosmos_endpoint, credential=cred)
        db = client.get_database_client(self.s.cosmos_db)
        container = db.get_container_client(self.s.cosmos_container_conv)
        q = "SELECT c.role, c.content, c.timestamp FROM c WHERE c.session_id=@sid ORDER BY c.timestamp DESC"
        items = []
        async for item in container.query_items(q, parameters=[{"name": "@sid", "value": session_id}]):
            items.append({"role": item["role"], "content": item["content"], "timestamp": item["timestamp"]})
            if len(items) >= limit:
                break
        await client.close()
        return list(reversed(items))

    async def _save_cosmos(self, rec):
        from azure.cosmos.aio import CosmosClient
        from azure.identity.aio import DefaultAzureCredential
        cred = DefaultAzureCredential()
        client = CosmosClient(self.s.cosmos_endpoint, credential=cred)
        db = client.get_database_client(self.s.cosmos_db)
        container = db.get_container_client(self.s.cosmos_container_conv)
        await container.upsert_item(rec)
        await client.close()
