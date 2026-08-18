from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from core.models import Repository


def test_schema_is_postgres_pgvector_not_sqlite():
    ddl = str(CreateTable(Repository.__table__).compile(dialect=postgresql.dialect()))
    assert "vector(384)" in ddl
    assert "JSONB" in ddl


def test_vector_query_compiles_to_pgvector_cosine_operator():
    vector = [0.0] * 384
    distance = Repository.embedding.cosine_distance(vector)
    statement = select(Repository.github_id).order_by(distance.asc())
    sql = str(statement.compile(dialect=postgresql.dialect()))
    assert "<=>" in sql
