from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .collect import DiscoveredRepo
from .github import GitHubClient


@dataclass(frozen=True)
class EnrichedRepo:
    github_id: int
    full_name: str
    owner_login: str
    name: str
    html_url: str
    description: str | None
    readme: str | None
    topics: list[str]
    primary_language: str | None
    stars: int
    forks: int
    is_fork: bool
    is_archived: bool
    github_created_at: datetime | None
    github_updated_at: datetime | None
    github_pushed_at: datetime | None
    discovery_queries: list[str]


def _datetime(value: str | None) -> datetime | None:
    return None if not value else datetime.fromisoformat(value.replace("Z", "+00:00"))


def _primary_language(languages: dict[str, int], fallback: str | None) -> str | None:
    if not languages:
        return fallback
    return max(languages.items(), key=lambda item: item[1])[0]


def enrich_repository(github: GitHubClient, discovered: DiscoveredRepo) -> EnrichedRepo:
    """Steps 10–11: fetch detail, README, topics and primary language."""

    payload = github.get_repository(discovered.full_name) or discovered.search_payload
    owner = payload.get("owner") or {}
    languages = github.get_languages(discovered.full_name)

    return EnrichedRepo(
        github_id=discovered.github_id,
        full_name=payload["full_name"],
        owner_login=owner.get("login") or payload["full_name"].split("/", 1)[0],
        name=payload["name"],
        html_url=payload.get("html_url") or f"https://github.com/{payload['full_name']}",
        description=payload.get("description"),
        readme=github.get_readme(discovered.full_name),
        topics=payload.get("topics") or [],
        primary_language=_primary_language(languages, payload.get("language")),
        stars=int(payload.get("stargazers_count") or 0),
        forks=int(payload.get("forks_count") or 0),
        is_fork=bool(payload.get("fork")),
        is_archived=bool(payload.get("archived")),
        github_created_at=_datetime(payload.get("created_at")),
        github_updated_at=_datetime(payload.get("updated_at")),
        github_pushed_at=_datetime(payload.get("pushed_at")),
        discovery_queries=discovered.queries,
    )
