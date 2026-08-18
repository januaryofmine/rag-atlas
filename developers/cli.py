from __future__ import annotations

import typer

from core.db import session_scope
from crawler.github import GitHubClient

from .build import build_developers

app = typer.Typer(help="Phase 4: build repository-backed developer evidence.")


@app.callback()
def main() -> None:
    """Developer command group."""


@app.command("run")
def run(
    repo_limit: int | None = typer.Option(None, min=1),
    contributor_pages: int = typer.Option(2, min=1),
) -> None:
    with GitHubClient() as github, session_scope() as session:
        stats = build_developers(
            session,
            github,
            repo_limit=repo_limit,
            contributor_pages=contributor_pages,
        )
    typer.echo(
        f"repos={stats.repos_processed} developers={stats.developers_seen} "
        f"edges={stats.edges_written}"
    )


if __name__ == "__main__":
    app()
