from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean

from core.models import RepoContributor

from .query import SearchQuery
from .retrieve import RepoCandidate


def overlap_score(query_labels: list[str], candidate_labels: list[str]) -> float:
    if not query_labels:
        return 0.0
    query = set(query_labels)
    return len(query & set(candidate_labels)) / len(query)


def business_similarity(query: SearchQuery, candidate: RepoCandidate) -> float:
    repository = candidate.repository
    scores: list[float] = []

    if query.use_cases:
        scores.append(overlap_score(query.use_cases, repository.use_cases or []))

    meaningful_domains = [item for item in query.domains if item != "GENERAL"]
    if meaningful_domains:
        scores.append(overlap_score(meaningful_domains, repository.domains or []))

    return fmean(scores) if scores else 0.0


@dataclass(frozen=True)
class RankedRepo:
    candidate: RepoCandidate
    business_score: float
    rag_type_score: float
    soft_boost: float
    match_score: float


def rank_repository(
    query: SearchQuery,
    candidate: RepoCandidate,
    *,
    rag_type_boost: float,
) -> RankedRepo:
    """Steps 38–41: combine business + RAG/relevance signals."""

    business = business_similarity(query, candidate)
    type_overlap = overlap_score(query.rag_types, candidate.repository.rag_types or [])
    relevance = candidate.repository.relevance_score or 0.0

    # Weights are intentionally explicit instead of hidden inside a model.
    base = (
        0.60 * candidate.semantic_score
        + 0.20 * business
        + 0.10 * relevance
        + 0.10 * type_overlap
    )
    boost = rag_type_boost * type_overlap
    total = min(1.0, base + boost)

    return RankedRepo(
        candidate=candidate,
        business_score=business,
        rag_type_score=type_overlap,
        soft_boost=boost,
        match_score=total,
    )


def evidence_score(repo_match_score: float, edge: RepoContributor) -> float:
    """Step 42: repo match is primary; contribution strength adjusts confidence."""
    contribution = max(0.0, min(1.0, edge.contribution_score))
    return repo_match_score * (0.70 + 0.30 * contribution)


def developer_score(evidence_scores: list[float]) -> float:
    """Step 43: best repo dominates; extra strong evidence gives a small bonus."""
    if not evidence_scores:
        return 0.0
    top = sorted(evidence_scores, reverse=True)[:3]
    best = top[0]
    support_bonus = 0.05 * sum(top[1:])
    return min(1.0, best + support_bonus)
