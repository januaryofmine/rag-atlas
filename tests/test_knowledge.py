from knowledge.rules import infer_labels
from knowledge.score import score_relevance


def test_repo_inference_is_multilabel_and_explainable():
    text = "GraphRAG legal contract review with hybrid search and vector retrieval"
    labels = infer_labels(text)
    relevance = score_relevance(text, ["rag", "legal"], labels.rag_types)

    assert "GRAPH_RAG" in labels.rag_types
    assert "HYBRID_RETRIEVAL" in labels.rag_types
    assert "LEGAL_REVIEW" in labels.use_cases
    assert "LEGAL" in labels.domains
    assert relevance.label == "RAG"
    assert relevance.score >= 0.35


def test_component_repo_needs_multiple_component_signals():
    text = "A vector search retriever for semantic search"
    labels = infer_labels(text)
    relevance = score_relevance(text, [], labels.rag_types)
    assert relevance.label == "RAG_COMPONENT"
