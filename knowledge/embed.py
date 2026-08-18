from __future__ import annotations

from core.embeddings import EmbeddingProvider


def embed_repository(text: str, embedder: EmbeddingProvider) -> list[float]:
    return embedder.embed(text)
