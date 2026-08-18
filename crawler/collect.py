from __future__ import annotations

import json
from importlib.resources import files
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .github import GitHubClient

DEFAULT_SEED_FILE = Path(__file__).parent / "config" / "seed-queries.json"


@dataclass
class DiscoveredRepo:
    github_id: int
    full_name: str
    search_payload: dict[str, Any]
    queries: list[str] = field(default_factory=list)


def load_seed_queries(path: Path = DEFAULT_SEED_FILE) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("seed query file must be a JSON list of strings")
    return [item.strip() for item in payload if item.strip()]


def discover_repositories(
    github: GitHubClient,
    queries: Iterable[str],
    *,
    max_repos: int = 50,
    max_pages_per_query: int = 1,
) -> list[DiscoveredRepo]:
    by_id: dict[int, DiscoveredRepo] = {}

    for query in queries:
        for payload in github.search_repositories(query, max_pages=max_pages_per_query):
            github_id = int(payload["id"])
            existing = by_id.get(github_id)
            if existing is not None:
                if query not in existing.queries:
                    existing.queries.append(query)
                continue

            if len(by_id) >= max_repos:
                return list(by_id.values())

            by_id[github_id] = DiscoveredRepo(
                github_id=github_id,
                full_name=payload["full_name"],
                search_payload=payload,
                queries=[query],
            )

    return list(by_id.values())
