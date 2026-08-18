from __future__ import annotations

import typer

from core.db import session_scope
from core.embeddings import build_embedding_provider

from .build import build_knowledge

app = typer.Typer(help="Phase 3: turn crawled repositories into RAG knowledge.")


@app.callback()
def main() -> None:
    """Knowledge command group."""


@app.command("run")
def run(limit: int | None = typer.Option(None, min=1)) -> None:
    embedder = build_embedding_provider()
    with session_scope() as session:
        stats = build_knowledge(session, embedder, limit=limit)
    typer.echo(
        f"processed={stats.processed} rag={stats.rag} "
        f"components={stats.rag_component} not_rag={stats.not_rag}"
    )


if __name__ == "__main__":
    app()
