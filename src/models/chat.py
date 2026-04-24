"""Azure OpenAI + Ollama chat · identical interface · MODE-switched."""
from __future__ import annotations
from typing import Any
import httpx
from src.config import get_settings


class ChatClient:
    def __init__(self) -> None:
        self.s = get_settings()

    async def complete(self, messages: list[dict[str, str]], **kw: Any) -> dict[str, Any]:
        if self.s.mode == "azure":
            return await self._azure(messages, **kw)
        return await self._ollama(messages, **kw)

    async def _azure(self, messages, **kw):
        from azure.identity.aio import DefaultAzureCredential
        from openai import AsyncAzureOpenAI
        cred = DefaultAzureCredential()
        token = (await cred.get_token("https://cognitiveservices.azure.com/.default")).token
        client = AsyncAzureOpenAI(azure_endpoint=self.s.aoai_endpoint, api_version=self.s.aoai_api_version, azure_ad_token=token)
        resp = await client.chat.completions.create(model=self.s.aoai_chat_deployment, messages=messages, **kw)
        return {"content": resp.choices[0].message.content, "tokens_in": resp.usage.prompt_tokens,
                "tokens_out": resp.usage.completion_tokens, "model": self.s.aoai_chat_deployment}

    async def _ollama(self, messages, **kw):
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{self.s.ollama_base_url}/api/chat",
                             json={"model": self.s.ollama_chat_model, "messages": messages, "stream": False})
            r.raise_for_status()
            j = r.json()
        return {"content": j["message"]["content"], "tokens_in": j.get("prompt_eval_count", 0),
                "tokens_out": j.get("eval_count", 0), "model": self.s.ollama_chat_model}
