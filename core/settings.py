from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings shared by the six blocks.

    Business rules do not live here. This module only owns infrastructure
    configuration such as PostgreSQL, GitHub, embeddings and serving limits.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://rag_atlas:rag_atlas@localhost:5432/rag_atlas"

    github_token: str | None = None
    github_api_url: str = "https://api.github.com"

    embedding_provider: str = "hashing"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384

    search_repo_candidates: int = 30
    rag_type_boost: float = 0.10
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
