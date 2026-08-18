## Phase 1: Define RAG

### 1. RAG Scope

- [x] RAG scope & criteria: `docs/01-rag-scope.md`

### 2. RAG Type

- [x] RAG Types: `config/rag-types.json`

### 3. Repo Relevance Labels

- [x] Relevance Labels: `config/relevance-labels.json`

### 4. Evidence Rules

- [x] Evidence Rules: `config/evidence-rules.json`

### 5. Seed Query Families

- [x] Reasoning: `docs/02-query-space.md`
- [x] Seed Query: `crawler/config/seed-queries.json`

## Phase 2: Data Schema

### 6. Define Schema

- [x] Define PostgreSQL tables: `docs/03-data-model.md`
- [x] Implement ORM schema: `core/models.py`

### 7. Data Flow

- [x] Define flow: `docs/04-data-flow.md`

## Phase 3: Github Crawler

### 8. GitHub Repo Collector

- [x] `crawler/github.py`: GitHub REST client
- [x] `crawler/collect.py`: search candidates

### 9. Store Discovery

- [x] `crawler/store.py`

### 10. Deduplicate Repository Candidates

- [x] `crawler/collect.py`: GitHub numeric repository ID

### 11. Enrich Repo Metadata

- [x] `crawler/enrich.py`

## Phase 4: Knowledge Base

### 12. Infer RAG types, use cases, domains

- [x] `knowledge/rules.py`

### 13. Semantic representation

- [x] `knowledge/embed.py`

### 14. Relevance score

- [x] `knowledge/score.py`: deterministic score

## Phase 5: Developer Extraction

### 15. Extract contributors

- [x] `developers/collect.py`

### 16. Repo & Developer Graph

- [x] `developers/store.py`: PostgreSQL relation table `repo_contributors`

### 17. Contribution strength

- [x] `developers/score.py`

### 18. Aggregate developer evidence

- [x] `developers/build.py`

## Phase 6: Search & matching API

### 19. Retrieve matching RAG repos

- [x] Parse product description
- [x] `search/query.py`

### 20. Developer matching/ranking

- [x] `search/rank.py`
- [x] `search/service.py`

## Phase 7: Evaluation

### 21. Evaluation set

- [x] `evaluation/data/queries.example.json`

### 22. Recall / ranking metrics

- [x] `evaluation/metrics.py`
- [x] `evaluation/run.py`

## Phase 8: Serve

### 23. Search index

- [x] PostgreSQL + pgvector HNSW index

### 24. Search API

- [x] `search/api.py`

### 25. UI

- [x] `app/`
