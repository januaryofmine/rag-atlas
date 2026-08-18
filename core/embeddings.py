from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache
from typing import Protocol

from .settings import get_settings

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_+.-]*", re.IGNORECASE)


class EmbeddingProvider(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]: ...


class HashingEmbeddingProvider:
    """Deterministic no-download baseline for local runs and tests."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        tokens = [token.lower() for token in _TOKEN_RE.findall(text)]
        features = tokens + [f"{a}::{b}" for a, b in zip(tokens, tokens[1:])]
        vector = [0.0] * self.dimensions

        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            sign = 1.0 if digest[0] & 1 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        return vector if norm == 0.0 else [value / norm for value in vector]


class SentenceTransformerEmbeddingProvider:
    """Optional real semantic model; keeps the same 384-d vector boundary."""

    def __init__(self, model_name: str, dimensions: int = 384) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Install sentence-transformers to use this embedding provider."
            ) from exc
        self.model = SentenceTransformer(model_name)
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:  # pragma: no cover
        values = [
            float(value)
            for value in self.model.encode(text, normalize_embeddings=True).tolist()
        ]
        if len(values) != self.dimensions:
            raise ValueError(
                f"model returned {len(values)} dimensions; expected {self.dimensions}"
            )
        return values


@lru_cache(maxsize=4)
def build_embedding_provider(
    provider_name: str | None = None,
    model_name: str | None = None,
    dimensions: int | None = None,
) -> EmbeddingProvider:
    settings = get_settings()
    provider = (provider_name or settings.embedding_provider).strip().lower()
    dims = dimensions or settings.embedding_dimensions

    if provider == "hashing":
        return HashingEmbeddingProvider(dims)
    if provider in {"sentence-transformers", "sentence_transformers", "sbert"}:
        return SentenceTransformerEmbeddingProvider(
            model_name or settings.embedding_model, dims
        )
    raise ValueError(f"unknown embedding provider: {provider}")
