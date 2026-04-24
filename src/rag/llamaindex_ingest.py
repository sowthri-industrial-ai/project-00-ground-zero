"""LlamaIndex alternative ingestion · same corpus · different orchestration."""
from __future__ import annotations
from src.config import get_settings


def ingest(pdf_path: str) -> int:
    s = get_settings()
    try:
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings as LISettings
        LISettings.chunk_size = 512
        LISettings.chunk_overlap = 50
        if s.mode == "azure":
            from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
            from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore
            from azure.identity import DefaultAzureCredential
            from azure.search.documents.indexes import SearchIndexClient
            cred = DefaultAzureCredential()
            index_client = SearchIndexClient(endpoint=s.search_endpoint, credential=cred)
            vs = AzureAISearchVectorStore(
                search_or_index_client=index_client,
                index_name=s.search_index_llamaindex,
                id_field_key="id", chunk_field_key="content",
                embedding_field_key="embedding", metadata_string_field_key="metadata",
                doc_id_field_key="doc_id",
            )
            LISettings.embed_model = AzureOpenAIEmbedding(
                deployment_name=s.aoai_embed_deployment, azure_endpoint=s.aoai_endpoint,
                api_version=s.aoai_api_version,
            )
        else:
            from llama_index.embeddings.ollama import OllamaEmbedding
            from llama_index.core.vector_stores.simple import SimpleVectorStore
            vs = SimpleVectorStore()
            LISettings.embed_model = OllamaEmbedding(model_name=s.ollama_embed_model, base_url=s.ollama_base_url)
        storage = StorageContext.from_defaults(vector_store=vs)
        docs = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
        index = VectorStoreIndex.from_documents(docs, storage_context=storage)
        index.storage_context.persist("./.llamaindex_store")
        return len(docs)
    except ImportError:
        print("llama-index not installed · scaffold only · install via requirements-brief-e.txt")
        return 0


if __name__ == "__main__":
    import sys
    n = ingest(sys.argv[1] if len(sys.argv) > 1 else "data/nist-ai-rmf.pdf")
    print(f"Indexed {n} docs via LlamaIndex")
