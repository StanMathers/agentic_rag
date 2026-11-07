from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INGESTION_")

    # Splitting
    chunk_size: int = 250
    chunk_overlap: int = 0

    # Embeddings
    embedding_model: str = "nomic-embed-text"

    # Vector store. If chroma_host is set, the Chroma server is used
    collection_name: str = "rag-chroma"
    persist_directory: str = "./.chroma"
    chroma_host: str | None = None
    chroma_port: int = 8000
