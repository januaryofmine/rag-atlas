from __future__ import annotations

import typer

from .db import create_tables

app = typer.Typer(help="RAG Atlas PostgreSQL schema commands.")


@app.callback()
def main() -> None:
    """Database command group."""


@app.command("init")
def init() -> None:
    create_tables()
    typer.echo("PostgreSQL schema created.")


if __name__ == "__main__":
    app()
