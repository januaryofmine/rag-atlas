from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def normalize_contributions(values: Iterable[int]) -> list[float]:
    """Step 29: normalize contributions within one repository."""
    items = [max(0, int(value)) for value in values]
    maximum = max(items, default=0)
    if maximum == 0:
        return [0.0 for _ in items]
    return [value / maximum for value in items]


def aggregate_labels(
    rows: Iterable[tuple[list[str], float]], *, min_score: float = 0.20
) -> list[str]:
    """Propagate repo labels to a developer using contribution weights."""
    totals: dict[str, float] = defaultdict(float)
    for labels, weight in rows:
        for label in labels:
            totals[label] += max(0.0, weight)
    if not totals:
        return []
    maximum = max(totals.values())
    return sorted(
        label for label, value in totals.items() if value / maximum >= min_score
    )


def evidence_score(values: Iterable[float], *, top_k: int = 3) -> float:
    """Average the strongest few repo evidence edges."""
    selected = sorted(
        (max(0.0, min(1.0, value)) for value in values), reverse=True
    )[:top_k]
    return 0.0 if not selected else sum(selected) / len(selected)
