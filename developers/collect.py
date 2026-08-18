from __future__ import annotations

from dataclasses import dataclass

from crawler.github import GitHubClient, GitHubContributor
from core.models import Repository

from .score import normalize_contributions


@dataclass(frozen=True)
class ContributorEvidence:
    contributor: GitHubContributor
    contribution_score: float


def collect_repo_contributors(
    github: GitHubClient,
    repository: Repository,
    *,
    max_pages: int = 2,
) -> list[ContributorEvidence]:
    """Step 26: fetch human GitHub contributors for one relevant repository."""
    contributors = [
        item
        for item in github.get_contributors(repository.full_name, max_pages=max_pages)
        if not item.login.endswith("[bot]")
    ]
    scores = normalize_contributions(item.contributions for item in contributors)
    return [
        ContributorEvidence(contributor=item, contribution_score=score)
        for item, score in zip(contributors, scores)
    ]
