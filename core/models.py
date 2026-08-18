from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .vector import VectorType

EMBEDDING_DIMENSIONS = 384


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Repository(Base):
    """Repository row populated by crawler, then enriched by knowledge."""

    __tablename__ = "repositories"

    # GitHub identity — Step 9 dedupe key.
    github_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    owner_login: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    html_url: Mapped[str] = mapped_column(Text)

    # Phase 2 crawler output.
    description: Mapped[str | None] = mapped_column(Text)
    readme: Mapped[str | None] = mapped_column(Text)
    topics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    primary_language: Mapped[str | None] = mapped_column(String(100))
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    is_fork: Mapped[bool] = mapped_column(default=False)
    is_archived: Mapped[bool] = mapped_column(default=False)
    github_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    github_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    github_pushed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Phase 3 knowledge output.
    relevance_label: Mapped[str | None] = mapped_column(String(32), index=True)
    relevance_score: Mapped[float | None] = mapped_column(Float)
    rag_types: Mapped[list[str]] = mapped_column(JSONB, default=list)
    use_cases: Mapped[list[str]] = mapped_column(JSONB, default=list)
    domains: Mapped[list[str]] = mapped_column(JSONB, default=list)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType(EMBEDDING_DIMENSIONS), nullable=True
    )
    knowledge_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    discoveries: Mapped[list["DiscoveryEvent"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )
    contributors: Mapped[list["RepoContributor"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )


class DiscoveryEvent(Base):
    """Step 8 provenance: which seed query discovered a repository."""

    __tablename__ = "discovery_events"
    __table_args__ = (
        UniqueConstraint("repo_id", "query", name="uq_discovery_repo_query"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("repositories.github_id", ondelete="CASCADE"),
        index=True,
    )
    query: Mapped[str] = mapped_column(Text)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    repository: Mapped[Repository] = relationship(back_populates="discoveries")


class Developer(Base):
    """Developer profile derived only from repository evidence."""

    __tablename__ = "developers"

    github_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    login: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    html_url: Mapped[str] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)

    evidence_repo_count: Mapped[int] = mapped_column(Integer, default=0)
    evidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    rag_types: Mapped[list[str]] = mapped_column(JSONB, default=list)
    use_cases: Mapped[list[str]] = mapped_column(JSONB, default=list)
    domains: Mapped[list[str]] = mapped_column(JSONB, default=list)
    profile_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    repositories: Mapped[list["RepoContributor"]] = relationship(
        back_populates="developer", cascade="all, delete-orphan"
    )


class RepoContributor(Base):
    """The evidence edge: developer contributed to repository."""

    __tablename__ = "repo_contributors"

    repo_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("repositories.github_id", ondelete="CASCADE"),
        primary_key=True,
    )
    developer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("developers.github_id", ondelete="CASCADE"),
        primary_key=True,
    )
    contributions: Mapped[int] = mapped_column(Integer, default=0)
    contribution_score: Mapped[float] = mapped_column(Float, default=0.0)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    repository: Mapped[Repository] = relationship(back_populates="contributors")
    developer: Mapped[Developer] = relationship(back_populates="repositories")


# Phase 7 search index. pgvector HNSW lives directly on repositories.embedding.
Index(
    "ix_repositories_embedding_hnsw",
    Repository.embedding,
    postgresql_using="hnsw",
    postgresql_ops={"embedding": "vector_cosine_ops"},
)
