from core.config_files import load_config


def test_phase1_taxonomy_is_small_and_explicit():
    rag_types = load_config("rag-types.json")
    assert set(rag_types) == {
        "GRAPH_RAG",
        "AGENTIC_RAG",
        "SELF_RAG",
        "CORRECTIVE_RAG",
        "HYBRID_RETRIEVAL",
        "MULTIMODAL_RAG",
    }


def test_evidence_rules_are_machine_readable():
    rules = load_config("evidence-rules.json")
    assert rules["component_min_hits"] == 2
    assert "vector search" in rules["component_terms"]


def test_relevance_labels_are_explicit():
    labels = load_config("relevance-labels.json")
    assert set(labels) == {"RAG", "RAG_COMPONENT", "NOT_RAG"}
