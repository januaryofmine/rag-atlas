from evaluation.metrics import precision_at_k, recall_at_k, reciprocal_rank


def test_ir_metrics():
    relevant = ["a", "b"]
    retrieved = ["x", "a", "y", "b"]
    assert recall_at_k(relevant, retrieved, 2) == 0.5
    assert precision_at_k(relevant, retrieved, 2) == 0.5
    assert reciprocal_rank(relevant, retrieved) == 0.5
