from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from crawler.github import GitHubClient
from core.models import Developer, RepoContributor, Repository, utcnow

from .collect import collect_repo_contributors
from .score import aggregate_labels, evidence_score
from .store import replace_repo_contributors


@dataclass(frozen=True)
class DeveloperStats:
    repos_processed: int
    developers_seen: int
    edges_written: int


def refresh_contributors(
    session: Session,
    github: GitHubClient,
    *,
    repo_limit: int | None = None,
    contributor_pages: int = 2,
) -> tuple[int, set[int], int]:
    statement = (
        select(Repository)
        .where(Repository.relevance_label.in_(["RAG", "RAG_COMPONENT"]))
        .order_by(Repository.relevance_score.desc().nullslast(), Repository.stars.desc())
    )
    if repo_limit is not None:
        statement = statement.limit(repo_limit)

    repositories = list(session.scalars(statement))
    developer_ids: set[int] = set()
    edge_count = 0

    for repository in repositories:
        evidence = collect_repo_contributors(
            github, repository, max_pages=contributor_pages
        )
        developer_ids |= replace_repo_contributors(session, repository, evidence)
        edge_count += len(evidence)
        session.commit()

    return len(repositories), developer_ids, edge_count


def rebuild_developer_profiles(session: Session) -> None:
    """Steps 30–32: roll repo evidence up to developer-level expertise."""

    developers = list(session.scalars(select(Developer)))
    for developer in developers:
        rows = session.execute(
            select(RepoContributor, Repository)
            .join(Repository, Repository.github_id == RepoContributor.repo_id)
            .where(
                RepoContributor.developer_id == developer.github_id,
                Repository.relevance_label.in_(["RAG", "RAG_COMPONENT"]),
            )
        ).all()

        developer.evidence_repo_count = len(rows)
        developer.evidence_score = evidence_score(
            (repository.relevance_score or 0.0) * edge.contribution_score
            for edge, repository in rows
        )
        developer.rag_types = aggregate_labels(
            ((repository.rag_types or [], edge.contribution_score) for edge, repository in rows)
        )
        developer.use_cases = aggregate_labels(
            ((repository.use_cases or [], edge.contribution_score) for edge, repository in rows)
        )
        developer.domains = aggregate_labels(
            ((repository.domains or [], edge.contribution_score) for edge, repository in rows)
        )
        developer.profile_updated_at = utcnow()

    session.commit()


def build_developers(
    session: Session,
    github: GitHubClient,
    *,
    repo_limit: int | None = None,
    contributor_pages: int = 2,
) -> DeveloperStats:
    repos, developer_ids, edges = refresh_contributors(
        session,
        github,
        repo_limit=repo_limit,
        contributor_pages=contributor_pages,
    )
    rebuild_developer_profiles(session)
    return DeveloperStats(
        repos_processed=repos,
        developers_seen=len(developer_ids),
        edges_written=edges,
    )
