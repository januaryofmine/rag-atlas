.PHONY: install test db pipeline api app

install:
	pip install -e '.[dev]'

test:
	pytest -q

db:
	rag-atlas-db init

pipeline:
	rag-atlas-crawler run --max-repos 50
	rag-atlas-knowledge run
	rag-atlas-developers run

api:
	rag-atlas-api

app:
	cd app && npm install && npm run dev
