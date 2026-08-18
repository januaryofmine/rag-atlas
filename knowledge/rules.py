from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.config_files import load_config

RAG_TYPES: dict[str, list[str]] = load_config("rag-types.json")
USE_CASES: dict[str, list[str]] = load_config("use-cases.json")
DOMAINS: dict[str, list[str]] = load_config("domains.json")
EVIDENCE_RULES: dict = load_config("evidence-rules.json")


@dataclass(frozen=True)
class RepoLabels:
    rag_types: list[str]
    use_cases: list[str]
    domains: list[str]


def build_repo_text(
    *, description: str | None, readme: str | None, topics: Iterable[str] | None
) -> str:
    return "\n".join(
        part
        for part in (
            description or "",
            " ".join(topics or []),
            readme or "",
        )
        if part
    )


def match_labels(text: str, mapping: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    return [
        label
        for label, terms in mapping.items()
        if any(term.lower() in lowered for term in terms)
    ]


def infer_rag_types(text: str) -> list[str]:
    return match_labels(text, RAG_TYPES)


def infer_use_cases(text: str) -> list[str]:
    return match_labels(text, USE_CASES)


def infer_domains(text: str) -> list[str]:
    values = match_labels(text, DOMAINS)
    return values or ["GENERAL"]


def infer_labels(text: str) -> RepoLabels:
    return RepoLabels(
        rag_types=infer_rag_types(text),
        use_cases=infer_use_cases(text),
        domains=infer_domains(text),
    )
