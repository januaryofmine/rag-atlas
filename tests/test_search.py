from types import SimpleNamespace

from core.embeddings import HashingEmbeddingProvider
from search.query import parse_query
from search.rank import developer_score, rank_repository
from search.retrieve import RepoCandidate


def test_query_does_not_infer_hidden_rag_types():
    query = parse_query(
        "GraphRAG legal contract review",
        [],
        HashingEmbeddingProvider(384),
    )
    assert query.rag_types == []
    assert "LEGAL_REVIEW" in query.use_cases


def test_rag_type_is_soft_boost_not_filter():
    query = parse_query(
        "legal contract review",
        ["GRAPH_RAG"],
        HashingEmbeddingProvider(384),
    )
    repository = SimpleNamespace(
        use_cases=["LEGAL_REVIEW"],
        domains=["LEGAL"],
        rag_types=["GRAPH_RAG"],
        relevance_score=0.9,
    )
    ranked = rank_repository(
        query,
        RepoCandidate(repository=repository, semantic_score=0.8),
        rag_type_boost=0.1,
    )
    assert ranked.soft_boost == 0.1
    assert ranked.match_score > 0.8


def test_multiple_strong_evidence_repos_help_developer_score():
    assert developer_score([0.9, 0.9]) > developer_score([0.9])
