from __future__ import annotations


def recall_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    return len(relevant_set & set(retrieved[:k])) / len(relevant_set)


def precision_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    selected = retrieved[:k]
    if not selected:
        return 0.0
    relevant_set = set(relevant)
    return sum(item in relevant_set for item in selected) / k


def reciprocal_rank(relevant: list[str], retrieved: list[str]) -> float:
    relevant_set = set(relevant)
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant_set:
            return 1.0 / rank
    return 0.0


def mean(values: list[float]) -> float | None:
    return None if not values else sum(values) / len(values)
