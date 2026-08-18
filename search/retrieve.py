from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models import Repository

from .query import SearchQuery


@dataclass(frozen=True)
class RepoCandidate:
    repository: Repository
    semantic_score: float


def retrieve_repositories(
    session: Session,
    query: SearchQuery,
    *,
    limit: int = 30,
) -> list[RepoCandidate]:
    """Step 36: pgvector candidate generation over relevant RAG repos."""

    distance = Repository.embedding.cosine_distance(query.vector).label("distance")
    statement = (
        select(Repository, distance)
        .where(
            Repository.embedding.is_not(None),
            Repository.relevance_label.in_(["RAG", "RAG_COMPONENT"]),
        )
        .order_by(distance.asc())
        .limit(limit)
    )

    candidates: list[RepoCandidate] = []
    for repository, raw_distance in session.execute(statement):
        semantic = max(0.0, min(1.0, 1.0 - float(raw_distance)))
        candidates.append(RepoCandidate(repository=repository, semantic_score=semantic))
    return candidates
