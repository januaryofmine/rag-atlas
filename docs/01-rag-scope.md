# 01 - RAG Scope

A repository is in scope when its

- description
- README
- topics

provide evidence that it implements retrieval-augmented generation or a RAG-specific component.

Note: this version does not read source code or dependency manifests.

## Labels

- `RAG`: explicit RAG purpose or named RAG architecture.
- `RAG_COMPONENT`: multiple retrieval/embedding/reranking signals but no explicit RAG claim.
- `NOT_RAG`: insufficient RAG evidence.

## Explicit RAG criteria

A repo is labelled `RAG` if at least one of the following holds:

1. It contains the phrase `retrieval augmented generation` or an unambiguous `RAG` token.
2. It matches a RAG type in the taxonomy.
3. Its GitHub topics include `rag`.

## Component signals

These are the signals:

```text
retriever
reranker
re-ranking
vector search
semantic search
embedding
vector database
context retrieval
```

If there is no explicit RAG evidence but >= 2 component signals are present → `RAG_COMPONENT`.
