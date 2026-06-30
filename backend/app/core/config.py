from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Multi-Source Research Agent"
    app_version: str = "0.1.0"
    app_env: Literal["local", "development", "staging", "production"] = "local"
    api_v1_prefix: str = "/api/v1"
    enable_docs: bool = True
    log_level: str = "INFO"

    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-1.5-pro"
    gemini_embedding_model: str = "models/text-embedding-004"
    gemini_temperature: float = 0.1

    groq_api_key: SecretStr | None = None
    default_provider: str = "groq"
    default_model: str = "llama-3.3-70b-versatile"
    fallback_provider: str = "gemini"
    fallback_model: str = "gemini-2.5-flash"

    embedding_model: str = "BAAI/bge-base-en-v1.5"

    langsmith_tracing: bool = False
    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "multi-source-research-agent"

    qdrant_url: AnyHttpUrl | None = None
    qdrant_api_key: SecretStr | None = None
    qdrant_collection_name: str = "research_documents"
    qdrant_vector_size: int = 768
    qdrant_distance_metric: Literal["Cosine", "Dot", "Euclid"] = "Cosine"

    document_chunk_size: int = 1200
    document_chunk_overlap: int = 200
    document_retrieval_top_k: int = 8

    database_url: SecretStr | None = None
    sql_allowed_tables: list[str] = Field(default_factory=list)
    sql_default_table: str | None = None
    sql_result_limit: int = 25
    sql_statement_timeout_ms: int = 8000

    web_search_provider: Literal["tavily"] = "tavily"
    web_search_api_key: SecretStr | None = None
    web_search_top_k: int = 5
    web_search_timeout_seconds: float = 12.0

    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 8
    reranker_batch_size: int = 16
    reranker_fallback_enabled: bool = True

    synthesis_max_context_chars: int = 12000
    synthesis_require_citations: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("sql_allowed_tables", mode="before")
    @classmethod
    def parse_allowed_tables(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [table.strip() for table in value.split(",") if table.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
