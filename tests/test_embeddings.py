import math

from core.embeddings import HashingEmbeddingProvider


def test_hashing_embedding_has_fixed_dimension_and_norm():
    provider = HashingEmbeddingProvider(384)
    vector = provider.embed("legal contract retrieval augmented generation")
    assert len(vector) == 384
    assert math.isclose(sum(value * value for value in vector), 1.0, rel_tol=1e-6)


def test_hashing_embedding_is_deterministic():
    provider = HashingEmbeddingProvider(32)
    assert provider.embed("same text") == provider.embed("same text")
