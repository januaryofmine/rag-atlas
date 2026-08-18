# 02 - Build Query Space

## Reasoning

Once "what counts as RAG" is settled, the crawler needs a small vocabulary to find candidate repositories.

```text
RAG scope
  ↓
RAG vocabulary
  ↓
RAG type vocabulary
  ↓
common product/use-case phrases
  ↓
GitHub seed queries
```

## Query families

### A. Generic RAG

```text
"retrieval augmented generation"
RAG LLM
```

### B. RAG types

```text
GraphRAG
"agentic RAG"
"self RAG"
"corrective RAG"
"hybrid retrieval" RAG
"multimodal RAG"
```

### C. Common RAG products

```text
"chat with PDF" RAG
"document question answering" RAG
"knowledge base assistant" RAG
```

## Deliberate limitation

The query list is a **fixed seed list**.

There is not yet any:

- adaptive partitioning;
- query expansion;
- semantic neighbor discovery;
- graph neighbor discovery;
- saturation estimation.

## Source of truth

`crawler/config/seed-queries.json`
