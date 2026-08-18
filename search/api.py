from __future__ import annotations

from collections.abc import Iterator

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.db import get_session_factory
from core.settings import get_settings

from .schemas import SearchRequest, SearchResponse
from .service import SearchService

settings = get_settings()
app = FastAPI(
    title="RAG Atlas API",
    version="0.2.0",
    description="Repo-first evidence-backed RAG engineer search.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_session() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/search", response_model=SearchResponse)
def search(request: SearchRequest, session: Session = Depends(get_session)) -> SearchResponse:
    return SearchService(session).search(
        request.product_description,
        rag_types=request.rag_types,
        limit=request.limit,
    )


def run() -> None:
    uvicorn.run("search.api:app", host="0.0.0.0", port=8000, reload=False)
