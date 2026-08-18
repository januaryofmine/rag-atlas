from __future__ import annotations

from pathlib import Path

import typer

from core.db import session_scope

from .collect import DEFAULT_SEED_FILE, discover_repositories, load_seed_queries
from .enrich import enrich_repository
from .github import GitHubClient
from .store import save_repository

app = typer.Typer(help="Phase 2: discover and store RAG repository candidates.")


@app.callback()
def main() -> None:
    """Crawler command group."""


@app.command("run")
def run(
    max_repos: int = typer.Option(50, min=1),
    max_pages_per_query: int = typer.Option(1, min=1),
    seed_file: Path = typer.Option(DEFAULT_SEED_FILE, exists=True, dir_okay=False),
) -> None:
    queries = load_seed_queries(seed_file)

    with GitHubClient() as github:
        discovered = discover_repositories(
            github,
            queries,
            max_repos=max_repos,
            max_pages_per_query=max_pages_per_query,
        )

        created = 0
        updated = 0
        with session_scope() as session:
            for candidate in discovered:
                enriched = enrich_repository(github, candidate)
                _, was_created = save_repository(session, enriched)
                created += int(was_created)
                updated += int(not was_created)

    typer.echo(
        f"queries={len(queries)} unique_repos={len(discovered)} "
        f"created={created} updated={updated}"
    )


if __name__ == "__main__":
    app()
