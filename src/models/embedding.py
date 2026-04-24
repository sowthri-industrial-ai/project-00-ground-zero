"""Embedding client · Azure text-embedding-3-small · Ollama nomic-embed-text."""
from __future__ import annotations
import httpx
from src.config import get_settings


class EmbeddingClient:
    def __init__(self) -> None:
        self.s = get_settings()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self.s.mode == "azure":
            return await self._azure(texts)
        return await self._ollama(texts)

    async def _azure(self, texts):
        from azure.identity.aio import DefaultAzureCredential
        from openai import AsyncAzureOpenAI
        cred = DefaultAzureCredential()
        token = (await cred.get_token("https://cognitiveservices.azure.com/.default")).token
        client = AsyncAzureOpenAI(azure_endpoint=self.s.aoai_endpoint, api_version=self.s.aoai_api_version, azure_ad_token=token)
        resp = await client.embeddings.create(model=self.s.aoai_embed_deployment, input=texts)
        return [d.embedding for d in resp.data]

    async def _ollama(self, texts):
        out = []
        async with httpx.AsyncClient(timeout=60) as c:
            for t in texts:
                r = await c.post(f"{self.s.ollama_base_url}/api/embeddings",
                                 json={"model": self.s.ollama_embed_model, "prompt": t})
                r.raise_for_status()
                out.append(r.json()["embedding"])
        return out
