# 03 - Data Model

## repositories

github_id PK
full_name
owner_login
name
html_url
description
readme
topics[]
primary_language
stars
forks
relevance_label
relevance_score
rag_types[]
use_cases[]
domains[]
embedding vector(384)

## discovery_events

id PK
repo_id FK -> repositories.github_id
query
discovered_at

UNIQUE(repo_id, query)

## developers

github_id PK
login
html_url
avatar_url
evidence_repo_count
evidence_score
rag_types[]
use_cases[]
domains[]

## repo_contributors

repo_id FK
developer_id FK
contributions
contribution_score
fetched_at

PK(repo_id, developer_id)
