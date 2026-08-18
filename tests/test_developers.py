from developers.score import aggregate_labels, evidence_score, normalize_contributions


def test_contribution_normalization():
    assert normalize_contributions([10, 5, 1]) == [1.0, 0.5, 0.1]


def test_developer_label_aggregation_uses_contribution_weights():
    labels = aggregate_labels([
        (["GRAPH_RAG"], 1.0),
        (["AGENTIC_RAG"], 0.1),
    ])
    assert labels == ["GRAPH_RAG"]


def test_evidence_score_uses_strongest_repos():
    assert evidence_score([0.9, 0.6, 0.3, 0.1], top_k=3) == 0.6
