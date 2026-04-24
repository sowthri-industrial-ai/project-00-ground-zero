"""Pydantic Settings · reads .env locally · Key Vault in Azure."""
from __future__ import annotations
from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mode: Literal["local", "azure"] = Field(default="local", alias="MODE")

    aoai_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    aoai_api_version: str = Field(default="2024-10-21", alias="AZURE_OPENAI_API_VERSION")
    aoai_chat_deployment: str = Field(default="gpt-4o-mini", alias="AZURE_OPENAI_CHAT_DEPLOYMENT")
    aoai_embed_deployment: str = Field(default="text-embedding-3-small", alias="AZURE_OPENAI_EMBED_DEPLOYMENT")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field(default="llama3.2:3b", alias="OLLAMA_CHAT_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")

    search_endpoint: str = Field(default="", alias="AZURE_SEARCH_ENDPOINT")
    search_index_primary: str = Field(default="hello-ai-rag", alias="AZURE_SEARCH_INDEX_PRIMARY")
    search_index_forms: str = Field(default="hello-ai-forms", alias="AZURE_SEARCH_INDEX_FORMS")
    search_index_llamaindex: str = Field(default="hello-ai-rag-llamaindex", alias="AZURE_SEARCH_INDEX_LLAMAINDEX")

    pg_dsn: str = Field(default="postgresql://rag:rag@localhost:5433/rag", alias="PG_DSN")

    cosmos_endpoint: str = Field(default="", alias="COSMOS_ENDPOINT")
    cosmos_db: str = Field(default="hello-ai", alias="COSMOS_DB")
    cosmos_container_conv: str = Field(default="conversations", alias="COSMOS_CONTAINER_CONV")
    cosmos_container_cost: str = Field(default="cost_rollups", alias="COSMOS_CONTAINER_COST")

    docintel_endpoint: str = Field(default="", alias="DOCINTEL_ENDPOINT")
    contentsafety_endpoint: str = Field(default="", alias="CONTENTSAFETY_ENDPOINT")

    langfuse_host: str = Field(default="http://localhost:3000", alias="LANGFUSE_HOST")
    langfuse_public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", alias="LANGFUSE_SECRET_KEY")

    appinsights_connection_string: str = Field(default="", alias="APPLICATIONINSIGHTS_CONNECTION_STRING")

    allam_endpoint: str = Field(default="", alias="ALLAM_ENDPOINT")
    allam_deployment: str = Field(default="allam-2-7b-instruct", alias="ALLAM_DEPLOYMENT")

    risky_keywords: tuple[str, ...] = ("compliance", "legal", "regulatory", "gdpr", "hipaa")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
