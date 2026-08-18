from __future__ import annotations

from dataclasses import dataclass

from core.config_files import load_config
from core.embeddings import EmbeddingProvider

USE_CASES: dict[str, list[str]] = load_config("use-cases.json")
DOMAINS: dict[str, list[str]] = load_config("domains.json")
RAG_TYPES: dict[str, list[str]] = load_config("rag-types.json")


@dataclass(frozen=True)
class SearchQuery:
    text: str
    vector: list[float]
    use_cases: list[str]
    domains: list[str]
    rag_types: list[str]


def _match(text: str, mapping: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    return [
        label
        for label, terms in mapping.items()
        if any(term.lower() in lowered for term in terms)
    ]


def parse_query(
    product_description: str,
    requested_rag_types: list[str],
    embedder: EmbeddingProvider,
) -> SearchQuery:
    """Step 34.

    Business semantics may be inferred from the product description.
    RAG types are NOT inferred (Step 35 is skipped); they come from the UI select.
    """

    unknown = sorted(set(requested_rag_types) - set(RAG_TYPES))
    if unknown:
        raise ValueError(f"unknown RAG types: {', '.join(unknown)}")

    domains = _match(product_description, DOMAINS) or ["GENERAL"]
    return SearchQuery(
        text=product_description,
        vector=embedder.embed(product_description),
        use_cases=_match(product_description, USE_CASES),
        domains=domains,
        rag_types=requested_rag_types,
    )
