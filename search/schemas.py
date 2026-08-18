from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from core.config_files import load_config

RAG_TYPES: dict[str, list[str]] = load_config("rag-types.json")


class SearchRequest(BaseModel):
    product_description: str = Field(min_length=3, max_length=4000)
    rag_types: list[str] = Field(default_factory=list, max_length=6)
    limit: int = Field(default=10, ge=1, le=50)

    @field_validator("rag_types")
    @classmethod
    def validate_rag_types(cls, values: list[str]) -> list[str]:
        normalized = [value.strip().upper() for value in values if value.strip()]
        unknown = sorted(set(normalized) - set(RAG_TYPES))
        if unknown:
            raise ValueError(f"unknown RAG types: {', '.join(unknown)}")
        return list(dict.fromkeys(normalized))


class EvidenceRepo(BaseModel):
    full_name: str
    github_url: str
    match_score: float
    contribution_score: float
    rag_types: list[str]
    use_cases: list[str]
    domains: list[str]


class DeveloperResult(BaseModel):
    github_id: int
    login: str
    github_url: str
    avatar_url: str | None
    match_score: float
    profile_evidence_score: float
    rag_types: list[str]
    use_cases: list[str]
    domains: list[str]
    evidence_repos: list[EvidenceRepo]


class SearchResponse(BaseModel):
    query: str
    rag_types: list[str]
    repo_candidates: int
    results: list[DeveloperResult]
    elapsed_ms: float
