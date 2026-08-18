from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from core.models import Developer, RepoContributor, Repository, utcnow

from .collect import ContributorEvidence


def replace_repo_contributors(
    session: Session,
    repository: Repository,
    evidence: list[ContributorEvidence],
) -> set[int]:
    """Step 27: replace one repo's evidence edges idempotently."""

    session.execute(
        delete(RepoContributor).where(RepoContributor.repo_id == repository.github_id)
    )

    developer_ids: set[int] = set()
    for item in evidence:
        raw = item.contributor
        developer = session.get(Developer, raw.github_id)
        if developer is None:
            developer = Developer(
                github_id=raw.github_id,
                login=raw.login,
                html_url=raw.html_url,
                avatar_url=raw.avatar_url,
            )
            session.add(developer)
        else:
            developer.login = raw.login
            developer.html_url = raw.html_url
            developer.avatar_url = raw.avatar_url

        session.flush()
        session.add(
            RepoContributor(
                repo_id=repository.github_id,
                developer_id=raw.github_id,
                contributions=raw.contributions,
                contribution_score=item.contribution_score,
                fetched_at=utcnow(),
            )
        )
        developer_ids.add(raw.github_id)

    return developer_ids
