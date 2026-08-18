from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models import DiscoveryEvent, Repository, utcnow

from .enrich import EnrichedRepo


def save_repository(session: Session, item: EnrichedRepo) -> tuple[Repository, bool]:
    """Upsert one canonical repository row by GitHub numeric ID."""

    repository = session.get(Repository, item.github_id)
    created = repository is None

    if repository is None:
        repository = Repository(
            github_id=item.github_id,
            full_name=item.full_name,
            owner_login=item.owner_login,
            name=item.name,
            html_url=item.html_url,
            discovered_at=utcnow(),
        )
        session.add(repository)

    repository.full_name = item.full_name
    repository.owner_login = item.owner_login
    repository.name = item.name
    repository.html_url = item.html_url
    repository.description = item.description
    repository.readme = item.readme
    repository.topics = item.topics
    repository.primary_language = item.primary_language
    repository.stars = item.stars
    repository.forks = item.forks
    repository.is_fork = item.is_fork
    repository.is_archived = item.is_archived
    repository.github_created_at = item.github_created_at
    repository.github_updated_at = item.github_updated_at
    repository.github_pushed_at = item.github_pushed_at

    session.flush()

    for query in item.discovery_queries:
        exists = session.scalar(
            select(DiscoveryEvent.id).where(
                DiscoveryEvent.repo_id == item.github_id,
                DiscoveryEvent.query == query,
            )
        )
        if exists is None:
            session.add(DiscoveryEvent(repo_id=item.github_id, query=query))

    return repository, created
