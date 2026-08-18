from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
from sqlalchemy.orm import Session

from core.db import session_scope
from search.service import SearchService

from .metrics import mean, precision_at_k, recall_at_k, reciprocal_rank


@dataclass(frozen=True)
class EvaluationQuery:
    id: str
    query: str
    rag_types: list[str]
    relevant_repos: list[str]
    relevant_developers: list[str]


def load_queries(path: Path) -> list[EvaluationQuery]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        EvaluationQuery(
            id=item["id"],
            query=item["query"],
            rag_types=item.get("rag_types") or [],
            relevant_repos=item.get("relevant_repos") or [],
            relevant_developers=item.get("relevant_developers") or [],
        )
        for item in payload
    ]


def evaluate(
    session: Session,
    queries: list[EvaluationQuery],
    *,
    repo_k: int = 20,
    developer_k: int = 10,
) -> dict[str, Any]:
    search = SearchService(session)
    rows: list[dict[str, Any]] = []
    repo_recalls: list[float] = []
    developer_recalls: list[float] = []
    developer_precisions: list[float] = []
    developer_rrs: list[float] = []

    for item in queries:
        trace = search.search_with_trace(
            item.query, rag_types=item.rag_types, limit=developer_k
        )
        row: dict[str, Any] = {
            "id": item.id,
            "retrieved_repos": trace.retrieved_repo_names[:repo_k],
            "retrieved_developers": trace.retrieved_developer_logins[:developer_k],
        }

        if item.relevant_repos:
            value = recall_at_k(item.relevant_repos, trace.retrieved_repo_names, repo_k)
            row[f"repo_recall@{repo_k}"] = value
            repo_recalls.append(value)

        if item.relevant_developers:
            recall = recall_at_k(
                item.relevant_developers,
                trace.retrieved_developer_logins,
                developer_k,
            )
            precision = precision_at_k(
                item.relevant_developers,
                trace.retrieved_developer_logins,
                developer_k,
            )
            rr = reciprocal_rank(
                item.relevant_developers, trace.retrieved_developer_logins
            )
            row[f"developer_recall@{developer_k}"] = recall
            row[f"developer_precision@{developer_k}"] = precision
            row["developer_rr"] = rr
            developer_recalls.append(recall)
            developer_precisions.append(precision)
            developer_rrs.append(rr)

        rows.append(row)

    return {
        "queries": rows,
        "summary": {
            f"repo_recall@{repo_k}": mean(repo_recalls),
            f"developer_recall@{developer_k}": mean(developer_recalls),
            f"developer_precision@{developer_k}": mean(developer_precisions),
            "developer_mrr": mean(developer_rrs),
        },
    }


app = typer.Typer(help="Phase 6: offline search evaluation.")


@app.callback()
def main() -> None:
    """Evaluation command group."""


@app.command("run")
def run_cli(
    file: Path = typer.Option(..., exists=True, dir_okay=False),
    repo_k: int = typer.Option(20, min=1),
    developer_k: int = typer.Option(10, min=1),
) -> None:
    with session_scope() as session:
        report = evaluate(
            session,
            load_queries(file),
            repo_k=repo_k,
            developer_k=developer_k,
        )
    typer.echo(json.dumps(report, indent=2))


if __name__ == "__main__":
    app()
