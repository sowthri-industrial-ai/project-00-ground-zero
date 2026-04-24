"""ALLaM-2-7b-instruct · SDAIA · via Azure AI Foundry managed endpoint (ephemeral)."""
from __future__ import annotations
from typing import Any
import httpx
from src.config import get_settings


class ALLaMClient:
    def __init__(self) -> None:
        self.s = get_settings()

    async def complete(self, messages: list[dict[str, str]], **kw: Any) -> dict[str, Any]:
        if not self.s.allam_endpoint:
            raise RuntimeError("ALLAM_ENDPOINT not set · endpoint is ephemeral · activate for demo")
        from azure.identity.aio import DefaultAzureCredential
        cred = DefaultAzureCredential()
        token = (await cred.get_token("https://ml.azure.com/.default")).token
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                f"{self.s.allam_endpoint}/chat/completions",
                headers={"Authorization": f"Bearer {token}"},
                json={"model": self.s.allam_deployment, "messages": messages, **kw},
            )
            r.raise_for_status()
            j = r.json()
        return {"content": j["choices"][0]["message"]["content"],
                "tokens_in": j["usage"]["prompt_tokens"], "tokens_out": j["usage"]["completion_tokens"],
                "model": self.s.allam_deployment}
