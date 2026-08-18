from __future__ import annotations

from dataclasses import dataclass
import re

from .rules import EVIDENCE_RULES


@dataclass(frozen=True)
class Relevance:
    label: str
    score: float
    explicit_rag: bool
    rag_topic: bool
    component_hits: int


def score_relevance(text: str, topics: list[str], rag_types: list[str]) -> Relevance:
    lowered = text.lower()
    patterns: list[str] = EVIDENCE_RULES["explicit_rag_patterns"]
    component_terms: list[str] = EVIDENCE_RULES["component_terms"]
    weights: dict[str, float | int] = EVIDENCE_RULES["weights"]

    # Avoid treating "rag" as an arbitrary substring such as "storage".
    explicit_rag = any(
        (pattern.lower() in lowered if pattern.lower() != "rag" else bool(re.search(r"\brag\b", lowered)))
        for pattern in patterns
    )
    def is_rag_topic(topic: str) -> bool:
        value = topic.lower().strip()
        return value == "rag" or value.endswith("rag") or value.startswith("rag-") or "-rag-" in value

    rag_topic = any(is_rag_topic(topic) for topic in topics)
    component_hits = sum(term.lower() in lowered for term in component_terms)

    score = 0.0
    score += float(weights["explicit_rag"]) if explicit_rag else 0.0
    score += float(weights["rag_type"]) if rag_types else 0.0
    score += float(weights["rag_topic"]) if rag_topic else 0.0
    score += min(component_hits, int(weights["max_component_hits"])) * float(
        weights["component_hit"]
    )
    score = min(score, 1.0)

    if explicit_rag or rag_types or rag_topic:
        label = "RAG"
    elif component_hits >= int(EVIDENCE_RULES["component_min_hits"]):
        label = "RAG_COMPONENT"
    else:
        label = "NOT_RAG"

    return Relevance(
        label=label,
        score=score,
        explicit_rag=explicit_rag,
        rag_topic=rag_topic,
        component_hits=component_hits,
    )
