from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.embeddings import EmbeddingProvider, build_embedding_provider
from core.models import Developer, RepoContributor
from core.settings import Settings, get_settings

from .query import parse_query
from .rank import RankedRepo, developer_score, evidence_score, rank_repository
from .retrieve import retrieve_repositories
from .schemas import DeveloperResult, EvidenceRepo, SearchResponse


@dataclass(frozen=True)
class SearchTrace:
    response: SearchResponse
    retrieved_repo_names: list[str]
    retrieved_developer_logins: list[str]


class SearchService:
    """Thin orchestrator for the online query path."""

    def __init__(
        self,
        session: Session,
        *,
        embedder: EmbeddingProvider | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.embedder = embedder or build_embedding_provider()

    def search_with_trace(
        self,
        product_description: str,
        *,
        rag_types: list[str] | None = None,
        limit: int = 10,
    ) -> SearchTrace:
        started = perf_counter()
        query = parse_query(product_description, rag_types or [], self.embedder)

        candidates = retrieve_repositories(
            self.session,
            query,
            limit=self.settings.search_repo_candidates,
        )
        ranked_repos = [
            rank_repository(
                query,
                candidate,
                rag_type_boost=self.settings.rag_type_boost,
            )
            for candidate in candidates
        ]
        ranked_repos.sort(key=lambda item: item.match_score, reverse=True)

        ranked_by_id: dict[int, RankedRepo] = {
            item.candidate.repository.github_id: item for item in ranked_repos
        }
        repo_ids = list(ranked_by_id)

        evidence_by_developer: dict[
            int, list[tuple[RepoContributor, RankedRepo]]
        ] = defaultdict(list)
        developers: dict[int, Developer] = {}

        if repo_ids:
            rows = self.session.execute(
                select(RepoContributor, Developer)
                .join(Developer, Developer.github_id == RepoContributor.developer_id)
                .where(RepoContributor.repo_id.in_(repo_ids))
            ).all()
            for edge, developer in rows:
                developers[developer.github_id] = developer
                evidence_by_developer[developer.github_id].append(
                    (edge, ranked_by_id[edge.repo_id])
                )

        results: list[DeveloperResult] = []
        for developer_id, evidence_rows in evidence_by_developer.items():
            developer = developers[developer_id]
            scored = [
                (evidence_score(repo.match_score, edge), edge, repo)
                for edge, repo in evidence_rows
            ]
            scored.sort(key=lambda row: row[0], reverse=True)

            results.append(
                DeveloperResult(
                    github_id=developer.github_id,
                    login=developer.login,
                    github_url=developer.html_url,
                    avatar_url=developer.avatar_url,
                    match_score=round(developer_score([row[0] for row in scored]), 4),
                    profile_evidence_score=round(developer.evidence_score or 0.0, 4),
                    rag_types=developer.rag_types or [],
                    use_cases=developer.use_cases or [],
                    domains=developer.domains or [],
                    evidence_repos=[
                        EvidenceRepo(
                            full_name=row[2].candidate.repository.full_name,
                            github_url=row[2].candidate.repository.html_url,
                            match_score=round(row[2].match_score, 4),
                            contribution_score=round(row[1].contribution_score, 4),
                            rag_types=row[2].candidate.repository.rag_types or [],
                            use_cases=row[2].candidate.repository.use_cases or [],
                            domains=row[2].candidate.repository.domains or [],
                        )
                        for row in scored[:3]
                    ],
                )
            )

        results.sort(key=lambda item: item.match_score, reverse=True)
        results = results[:limit]

        response = SearchResponse(
            query=product_description,
            rag_types=query.rag_types,
            repo_candidates=len(ranked_repos),
            results=results,
            elapsed_ms=round((perf_counter() - started) * 1000, 2),
        )
        return SearchTrace(
            response=response,
            retrieved_repo_names=[
                item.candidate.repository.full_name for item in ranked_repos
            ],
            retrieved_developer_logins=[item.login for item in results],
        )

    def search(
        self,
        product_description: str,
        *,
        rag_types: list[str] | None = None,
        limit: int = 10,
    ) -> SearchResponse:
        return self.search_with_trace(
            product_description, rag_types=rag_types, limit=limit
        ).response
