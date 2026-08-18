from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.embeddings import EmbeddingProvider
from core.models import Repository, utcnow

from .embed import embed_repository
from .rules import build_repo_text, infer_labels
from .score import score_relevance


@dataclass(frozen=True)
class KnowledgeStats:
    processed: int
    rag: int
    rag_component: int
    not_rag: int


def build_knowledge(
    session: Session,
    embedder: EmbeddingProvider,
    *,
    limit: int | None = None,
) -> KnowledgeStats:
    statement = select(Repository).order_by(Repository.stars.desc())
    if limit is not None:
        statement = statement.limit(limit)

    counts = {"RAG": 0, "RAG_COMPONENT": 0, "NOT_RAG": 0}
    repositories = list(session.scalars(statement))

    for repository in repositories:
        text = build_repo_text(
            description=repository.description,
            readme=repository.readme,
            topics=repository.topics,
        )
        labels = infer_labels(text)
        relevance = score_relevance(text, repository.topics or [], labels.rag_types)

        repository.rag_types = labels.rag_types
        repository.use_cases = labels.use_cases
        repository.domains = labels.domains
        repository.relevance_label = relevance.label
        repository.relevance_score = relevance.score
        repository.embedding = (
            embed_repository(text, embedder)
            if relevance.label in {"RAG", "RAG_COMPONENT"}
            else None
        )
        repository.knowledge_updated_at = utcnow()
        counts[relevance.label] += 1

    session.commit()
    return KnowledgeStats(
        processed=len(repositories),
        rag=counts["RAG"],
        rag_component=counts["RAG_COMPONENT"],
        not_rag=counts["NOT_RAG"],
    )
