from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Iterator

import httpx

from core.settings import get_settings


class GitHubAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitHubContributor:
    github_id: int
    login: str
    html_url: str
    avatar_url: str | None
    contributions: int


class GitHubClient:
    """Small synchronous GitHub REST client used only by offline jobs."""

    def __init__(self, token: str | None = None) -> None:
        settings = get_settings()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rag-atlas",
        }
        token = settings.github_token if token is None else token
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.Client(
            base_url=settings.github_api_url.rstrip("/"),
            headers=headers,
            timeout=30.0,
        )

    def __enter__(self) -> "GitHubClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.client.close()

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        response = self.client.get(path, params=params)
        if response.status_code in {204, 404}:
            return None
        if response.status_code >= 400:
            remaining = response.headers.get("x-ratelimit-remaining")
            reset = response.headers.get("x-ratelimit-reset")
            if remaining == "0":
                raise GitHubAPIError(f"GitHub rate limit exhausted; reset={reset}")
            raise GitHubAPIError(
                f"GitHub API {response.status_code}: {response.text[:300]}"
            )
        return response.json()

    def search_repositories(
        self, query: str, *, max_pages: int = 1, per_page: int = 50
    ) -> Iterator[dict[str, Any]]:
        for page in range(1, max_pages + 1):
            payload = self._get(
                "/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "page": page,
                    "per_page": min(per_page, 100),
                },
            )
            if not payload:
                return
            items = payload.get("items", [])
            yield from items
            if len(items) < per_page:
                return

    def get_repository(self, full_name: str) -> dict[str, Any] | None:
        return self._get(f"/repos/{full_name}")

    def get_readme(self, full_name: str) -> str | None:
        payload = self._get(f"/repos/{full_name}/readme")
        if not payload or not payload.get("content"):
            return None
        return base64.b64decode(payload["content"]).decode("utf-8", errors="replace")

    def get_languages(self, full_name: str) -> dict[str, int]:
        return self._get(f"/repos/{full_name}/languages") or {}

    def get_contributors(
        self, full_name: str, *, max_pages: int = 2, per_page: int = 100
    ) -> Iterator[GitHubContributor]:
        for page in range(1, max_pages + 1):
            payload = self._get(
                f"/repos/{full_name}/contributors",
                params={"page": page, "per_page": min(per_page, 100), "anon": "false"},
            )
            if not payload:
                return
            for item in payload:
                if not item.get("id") or not item.get("login"):
                    continue
                yield GitHubContributor(
                    github_id=int(item["id"]),
                    login=item["login"],
                    html_url=item.get("html_url") or f"https://github.com/{item['login']}",
                    avatar_url=item.get("avatar_url"),
                    contributions=int(item.get("contributions") or 0),
                )
            if len(payload) < per_page:
                return
