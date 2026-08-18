# 04 - End-to-End Data Flow

## Flow 1: Build knowledge base

```text
crawler/config/seed-queries.json
              ↓
        crawler/github.py
              ↓
        crawler/collect.py
      search + dedupe + provenance
              ↓
        crawler/enrich.py
   metadata + README + topics
              ↓
         crawler/store.py
              ↓
           PostgreSQL
              ↓
       knowledge/rules.py
 RAG types + use case + domain
              ↓
       knowledge/score.py
         relevance score
              ↓
       knowledge/embed.py
         repo embedding
              ↓
      PostgreSQL + pgvector
              ↓
      developers/collect.py
        GitHub contributors
              ↓
       developers/score.py
       contribution strength
              ↓
       developers/build.py
 aggregate developer evidence
              ↓
           PostgreSQL
```

## Flow 2: User search

```text
User
 ↓
app
 ↓
POST /v1/search
 ↓
search/query.py
embed raw product description
 ↓
search/retrieve.py
pgvector -> matching repos
 ↓
search/rank.py
repo score -> contributor evidence -> developer score
 ↓
Top developers + evidence repos
```

## Evaluation

```text
evaluation/data/queries.json
          ↓
     search/service.py
          ↓
    evaluation/run.py
          ↓
Recall@K / Precision@K / MRR
```
